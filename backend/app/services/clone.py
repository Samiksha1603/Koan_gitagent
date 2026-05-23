from git import Repo
from pathlib import Path
import shutil
import time
import os


def remove_readonly(func, path, _):
    """Handle Windows read-only files during rmtree."""
    os.chmod(path, 0o777)
    func(path)


def clone_repo(repo_url: str):
    repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")

    base = Path.cwd() / "repos"
    base.mkdir(exist_ok=True)

    target = base / repo_name

    if target.exists():
        # Give Windows a moment to release file handles
        time.sleep(1)
        try:
            shutil.rmtree(target, onerror=remove_readonly)
        except Exception as e:
            print(f"Warning: could not clean {target}: {e}")
            # Try with a timestamped name instead
            import datetime
            ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            target = base / f"{repo_name}-{ts}"

    Repo.clone_from(
        repo_url,
        str(target),
        depth=1,
    )

    return target