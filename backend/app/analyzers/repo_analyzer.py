from pathlib import Path
from git import Repo
import json


def analyze_repo(repo_path):
    result = {
        "readme": "",
        "frameworks": [],
        "important_files": [],
        "folders": [],
        "dependencies": [],
        "git_history": "",
        "contributors": [],
        "recent_changes": "",
        "merge_commits": "",
    }

    # --- README ---
    readme = Path(repo_path) / "README.md"
    if readme.exists():
        try:
            result["readme"] = readme.read_text(encoding="utf-8", errors="replace")[:5000]
        except Exception:
            result["readme"] = "(could not read README)"

    # --- Dependencies ---
    # Node.js
    package_json = Path(repo_path) / "package.json"
    if package_json.exists():
        try:
            data = json.loads(package_json.read_text(encoding="utf-8"))
            deps = data.get("dependencies", {})
            dev_deps = data.get("devDependencies", {})
            result["dependencies"] = list(deps.keys()) + list(dev_deps.keys())
        except Exception:
            pass

    # Python
    requirements_txt = Path(repo_path) / "requirements.txt"
    if requirements_txt.exists():
        try:
            lines = requirements_txt.read_text(encoding="utf-8", errors="replace").splitlines()
            for line in lines:
                line = line.strip()
                if line and not line.startswith("#"):
                    pkg = line.split("==")[0].split(">=")[0].split("<=")[0].split("[")[0].strip()
                    if pkg:
                        result["dependencies"].append(pkg)
        except Exception:
            pass

    # pyproject.toml / setup.py
    if (Path(repo_path) / "pyproject.toml").exists():
        result["frameworks"].append("Python (pyproject.toml)")
    if (Path(repo_path) / "setup.py").exists():
        result["frameworks"].append("Python (setup.py)")

    # --- Folders ---
    for item in Path(repo_path).iterdir():
        if item.is_dir() and not item.name.startswith("."):
            result["folders"].append(item.name)

    # --- Important files ---
    important = [
        "main.py", "app.py", "server.js", "index.ts", "index.js",
        "routes.py", "manage.py", "wsgi.py", "asgi.py",
        "Dockerfile", "docker-compose.yml", "Makefile",
        "setup.py", "pyproject.toml", "CONTRIBUTING.md", "CHANGELOG.md",
    ]
    for path in Path(repo_path).rglob("*"):
        if path.name in important:
            try:
                rel = path.relative_to(repo_path)
                result["important_files"].append(str(rel))
            except ValueError:
                result["important_files"].append(path.name)

    # --- Framework detection ---
    dep_set = set(d.lower() for d in result["dependencies"])
    framework_map = {
        "next": "Next.js", "react": "React", "express": "Express.js",
        "flask": "Flask", "django": "Django", "fastapi": "FastAPI",
        "celery": "Celery", "redis": "Redis", "sqlalchemy": "SQLAlchemy",
        "prisma": "Prisma", "mongoose": "Mongoose", "vue": "Vue.js",
        "angular": "Angular", "svelte": "Svelte",
        "@nestjs/core": "NestJS",
    }
    for dep, name in framework_map.items():
        if dep in dep_set and name not in result["frameworks"]:
            result["frameworks"].append(name)

    # ============================================================
    # GIT HISTORY - the real institutional memory
    # This is what the last engineer knew: decisions, patterns,
    # who worked on what, what changed recently, merge context
    # ============================================================
    try:
        repo = Repo(repo_path)

        # Need to unshallow if cloned with depth=1
        try:
            repo.git.fetch("--unshallow")
        except Exception:
            pass  # Already full or can't unshallow - that's fine

        # --- Last 100 commit messages ---
        # Captures WHAT was done and often WHY
        commits = list(repo.iter_commits("HEAD", max_count=100))
        commit_lines = []
        for c in commits:
            date = c.committed_datetime.strftime("%Y-%m-%d")
            author = c.author.name if c.author else "unknown"
            msg = c.message.strip().split("\n")[0][:200]
            commit_lines.append(f"[{date}] {author}: {msg}")

        result["git_history"] = "\n".join(commit_lines)

        # --- Contributors (who knows what) ---
        author_counts = {}
        for c in commits:
            name = c.author.name if c.author else "unknown"
            author_counts[name] = author_counts.get(name, 0) + 1

        result["contributors"] = [
            {"name": name, "commits": count}
            for name, count in sorted(author_counts.items(), key=lambda x: -x[1])
        ][:15]

        # --- Merge commits / PR merges = engineering decisions ---
        merge_lines = []
        for c in commits:
            msg = c.message.strip()
            if any(p in msg.lower() for p in [
                "merge pull request", "merge branch", "merged",
                "fix #", "closes #", "resolves #", "breaking change",
                "deprecate", "migrate", "refactor", "revert",
            ]):
                date = c.committed_datetime.strftime("%Y-%m-%d")
                author = c.author.name if c.author else "unknown"
                full_msg = msg[:500]
                merge_lines.append(f"[{date}] {author}: {full_msg}")

        result["merge_commits"] = "\n".join(merge_lines[:30])

        # --- Recently active areas ---
        recent = list(repo.iter_commits("HEAD", max_count=20))
        changed_files = {}
        for c in recent:
            try:
                if c.parents:
                    for diff in c.diff(c.parents[0]):
                        path = diff.a_path or diff.b_path or ""
                        if path:
                            top = path.split("/")[0] if "/" in path else path
                            changed_files[top] = changed_files.get(top, 0) + 1
            except Exception:
                pass

        active_areas = sorted(changed_files.items(), key=lambda x: -x[1])[:10]
        result["recent_changes"] = "\n".join(
            [f"- {area}: {count} recent changes" for area, count in active_areas]
        )

    except Exception as e:
        result["git_history"] = f"(could not read git history: {e})"

    return result