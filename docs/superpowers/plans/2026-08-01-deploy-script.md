# Deploy Script Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an executable `./deploy.sh` command that stages every repository change, creates a fixed-message commit when needed, and pushes the current branch to `origin`.

**Architecture:** A shell launcher resolves the project root and invokes a standard-library Python program. The Python program validates repository state, runs Git commands without shell interpolation, skips empty commits, and pushes the active branch. Integration tests use temporary working repositories and local bare remotes, so they exercise real Git behavior without network access.

**Tech Stack:** POSIX shell, Python 3 standard library (`subprocess`, `pathlib`, `unittest`, `tempfile`), Git

## Global Constraints

- Stage additions, modifications, and deletions with `git add -A`.
- Use the fixed commit message `chore: update project`.
- Skip commit creation when the index has no changes, but still push.
- Push the current branch with `git push -u origin <branch>`.
- Never pull, switch branches, rewrite commits, or force push.
- Stop with a non-zero status when validation or a Git command fails.

---

### Task 1: Publish Changed Repositories

**Files:**
- Create: `scripts/deploy.py`
- Create: `tests/test_deploy.py`

**Interfaces:**
- Consumes: Git CLI available as `git` on `PATH`; current working directory inside the repository to publish.
- Produces: `scripts/deploy.py` with `COMMIT_MESSAGE: str`, `git_query(*args: str) -> str`, `git_run(*args: str) -> None`, and `main() -> int`.

- [ ] **Step 1: Write the failing integration test**

Create test helpers that initialize a temporary repository and bare `origin`, configure a local Git identity, and invoke `scripts/deploy.py` with `sys.executable`. Add this test:

```python
def test_publishes_all_changes_with_fixed_commit_message(self):
    repo, remote = self.make_repository()
    (repo / "tracked.txt").write_text("updated\n", encoding="utf-8")
    (repo / "deleted.txt").unlink()
    (repo / "new.txt").write_text("new\n", encoding="utf-8")

    result = self.run_deploy(repo)

    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertEqual(git(repo, "log", "-1", "--format=%s"), "chore: update project")
    self.assertEqual(git(repo, "status", "--porcelain"), "")
    self.assertEqual(git_dir(remote, "show", "main:tracked.txt"), "updated")
    self.assertEqual(git_dir(remote, "show", "main:new.txt"), "new")
    deleted = git_dir_result(remote, "cat-file", "-e", "main:deleted.txt")
    self.assertNotEqual(deleted.returncode, 0)
    self.assertEqual(git(repo, "rev-parse", "--abbrev-ref", "@{upstream}"), "origin/main")
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python3 -m unittest tests.test_deploy.DeployScriptTests.test_publishes_all_changes_with_fixed_commit_message -v`

Expected: FAIL because `scripts/deploy.py` does not exist.

- [ ] **Step 3: Implement the minimal Python publisher**

Implement command execution without `shell=True`:

```python
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
    staged = subprocess.run(["git", "diff", "--cached", "--quiet").returncode
    if staged == 1:
        git_run("commit", "-m", COMMIT_MESSAGE)
    elif staged != 0:
        return staged
    git_run("push", "-u", "origin", branch)
    return 0
```

Use `raise SystemExit(main())` as the module entry point.

- [ ] **Step 4: Run the focused test to verify it passes**

Run: `python3 -m unittest tests.test_deploy.DeployScriptTests.test_publishes_all_changes_with_fixed_commit_message -v`

Expected: PASS with one new commit on both the working repository and bare remote.

- [ ] **Step 5: Commit the working publisher**

```bash
git add scripts/deploy.py tests/test_deploy.py
git commit -m "Add Python deploy publisher"
```

---

### Task 2: No-Change And Validation Paths

**Files:**
- Modify: `scripts/deploy.py`
- Modify: `tests/test_deploy.py`

**Interfaces:**
- Consumes: Task 1's `git_query`, `git_run`, and `main` functions.
- Produces: `validate_repository() -> str`, returning the active branch or raising `DeployError`; `DeployError`, a user-facing validation exception.

- [ ] **Step 1: Write failing tests for no changes and invalid repository state**

Add three focused tests:

```python
def test_skips_commit_when_there_are_no_changes_and_still_pushes(self):
    repo, _ = self.make_repository()
    before = git(repo, "rev-list", "--count", "HEAD")
    result = self.run_deploy(repo)
    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertIn("No changes to commit.", result.stdout)
    self.assertEqual(git(repo, "rev-list", "--count", "HEAD"), before)

def test_fails_clearly_when_origin_is_missing(self):
    repo = self.make_repository(with_remote=False)[0]
    result = self.run_deploy(repo)
    self.assertNotEqual(result.returncode, 0)
    self.assertIn("origin remote is not configured", result.stderr)

def test_fails_clearly_in_detached_head_state(self):
    repo, _ = self.make_repository()
    git(repo, "checkout", "--detach", capture=False)
    result = self.run_deploy(repo)
    self.assertNotEqual(result.returncode, 0)
    self.assertIn("detached HEAD", result.stderr)
```

- [ ] **Step 2: Run the new tests to verify they fail**

Run: `python3 -m unittest tests.test_deploy.DeployScriptTests.test_skips_commit_when_there_are_no_changes_and_still_pushes tests.test_deploy.DeployScriptTests.test_fails_clearly_when_origin_is_missing tests.test_deploy.DeployScriptTests.test_fails_clearly_in_detached_head_state -v`

Expected: FAIL because the no-change message and explicit validation errors are not implemented.

- [ ] **Step 3: Add validation and graceful no-change handling**

Add a small exception and validation function:

```python
class DeployError(RuntimeError):
    pass


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
```

Call `validate_repository()` before staging. Print `No changes to commit.` when `git diff --cached --quiet` returns zero. Catch `DeployError` in the entry point, print `deploy: <message>` to stderr, and exit with status 1. Allow failed operational Git commands such as commit and push to retain their native output and non-zero exit status.

- [ ] **Step 4: Run the full Python test suite**

Run: `python3 -m unittest tests.test_deploy -v`

Expected: all four tests PASS with no tracebacks or warnings.

- [ ] **Step 5: Commit validation behavior**

```bash
git add scripts/deploy.py tests/test_deploy.py
git commit -m "Handle deploy validation and empty changes"
```

---

### Task 3: Executable Launcher

**Files:**
- Create: `deploy.sh`
- Modify: `tests/test_deploy.py`

**Interfaces:**
- Consumes: Task 2's `scripts/deploy.py` command-line entry point.
- Produces: executable `./deploy.sh` entry point that can be invoked from any working directory.

- [ ] **Step 1: Write a failing launcher integration test**

Extend the repository fixture to copy `deploy.sh` and `scripts/deploy.py` into the temporary repository. Add:

```python
def test_launcher_publishes_from_outside_repository(self):
    repo, _ = self.make_repository()
    (repo / "new.txt").write_text("via launcher\n", encoding="utf-8")
    result = subprocess.run(
        [str(repo / "deploy.sh")],
        cwd=repo.parent,
        text=True,
        capture_output=True,
    )
    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertEqual(git(repo, "log", "-1", "--format=%s"), "chore: update project")
```

- [ ] **Step 2: Run the launcher test to verify it fails**

Run: `python3 -m unittest tests.test_deploy.DeployScriptTests.test_launcher_publishes_from_outside_repository -v`

Expected: FAIL because `deploy.sh` does not exist.

- [ ] **Step 3: Add the shell launcher**

Create `deploy.sh` with:

```sh
#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$SCRIPT_DIR"
exec python3 "$SCRIPT_DIR/scripts/deploy.py"
```

Run `chmod +x deploy.sh` so Git records executable mode `100755`.

- [ ] **Step 4: Run all verification checks**

Run:

```bash
python3 -m unittest discover -s tests -v
sh -n deploy.sh
python3 -m py_compile scripts/deploy.py tests/test_deploy.py
git diff --check
```

Expected: five tests PASS; shell syntax, Python compilation, and whitespace checks exit zero.

- [ ] **Step 5: Commit the launcher**

```bash
git add deploy.sh tests/test_deploy.py
git commit -m "Add deploy command launcher"
```
