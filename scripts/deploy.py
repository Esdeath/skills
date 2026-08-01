import subprocess
import sys


COMMIT_MESSAGE = "chore: update project"


class DeployError(RuntimeError):
    pass


def git_query(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], text=True, capture_output=True, check=True
    )
    return result.stdout.strip()


def git_run(*args: str) -> None:
    subprocess.run(["git", *args], check=True)


def validate_repository() -> str:
    try:
        if git_query("rev-parse", "--is-inside-work-tree") != "true":
            raise DeployError("current directory is not a Git worktree")
    except subprocess.CalledProcessError as error:
        raise DeployError("current directory is not a Git worktree") from error

    try:
        git_query("remote", "get-url", "origin")
    except subprocess.CalledProcessError as error:
        raise DeployError("origin remote is not configured") from error

    try:
        return git_query("symbolic-ref", "--quiet", "--short", "HEAD")
    except subprocess.CalledProcessError as error:
        raise DeployError("cannot deploy from detached HEAD") from error


def main() -> int:
    branch = validate_repository()
    git_run("add", "-A")
    staged = subprocess.run(["git", "diff", "--cached", "--quiet"]).returncode
    if staged == 1:
        git_run("commit", "-m", COMMIT_MESSAGE)
    elif staged == 0:
        print("No changes to commit.")
    else:
        return staged
    git_run("push", "-u", "origin", branch)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except DeployError as error:
        print(f"deploy: {error}", file=sys.stderr)
        raise SystemExit(1)
