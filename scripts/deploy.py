import subprocess


COMMIT_MESSAGE = "chore: update project"


def git_query(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], text=True, capture_output=True, check=True
    )
    return result.stdout.strip()


def git_run(*args: str) -> None:
    subprocess.run(["git", *args], check=True)


def main() -> int:
    branch = git_query("symbolic-ref", "--quiet", "--short", "HEAD")
    git_run("add", "-A")
    staged = subprocess.run(["git", "diff", "--cached", "--quiet"]).returncode
    if staged == 1:
        git_run("commit", "-m", COMMIT_MESSAGE)
    elif staged != 0:
        return staged
    git_run("push", "-u", "origin", branch)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
