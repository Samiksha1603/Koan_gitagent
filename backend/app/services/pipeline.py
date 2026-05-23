from pathlib import Path
from app.services.clone import clone_repo
from app.analyzers.repo_analyzer import analyze_repo
from app.generators.memory_generator import generate_memories
from app.generators.gitagent_generator import (
    build_agent_yaml,
    build_soul,
    build_rules,
)


def run_pipeline(repo_url, description):
    repo_path = clone_repo(repo_url)

    analysis = analyze_repo(repo_path)

    repo_name = repo_path.name

    output = Path("generated_agents") / repo_name

    output.mkdir(parents=True, exist_ok=True)

    (output / "memory").mkdir(exist_ok=True)

    memories = generate_memories(analysis)

    # FIX: encoding="utf-8" on ALL write_text calls (Windows defaults to cp1252
    # which can't handle the macron in "Koan" and other unicode characters)
    (output / "memory" / "onboarding.md").write_text(
        memories, encoding="utf-8"
    )

    (output / "agent.yaml").write_text(
        build_agent_yaml(repo_name), encoding="utf-8"
    )

    (output / "SOUL.md").write_text(
        build_soul(description), encoding="utf-8"
    )

    (output / "RULES.md").write_text(
        build_rules(), encoding="utf-8"
    )

    return {
        "status": "success",
        "agent": repo_name,
        "analysis": analysis,
        "memory": memories,
        "agent_path": str(output),
    }