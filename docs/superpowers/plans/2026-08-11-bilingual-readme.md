# Bilingual README Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add equivalent Chinese and English root READMEs that let a public GitHub visitor install, invoke, understand, test, and safely maintain the repository.

**Architecture:** `README.md` is the default Chinese entry point and `README.en.md` is its English counterpart. Both documents use the same section order, commands, relative links, behavioral claims, and deployment warning; only the explanatory language differs.

**Tech Stack:** GitHub-Flavored Markdown, POSIX shell commands, Python 3 `unittest`, Git

## Global Constraints

- Write `README.md` in concise Chinese and `README.en.md` in natural English.
- Keep commands, paths, filenames, identifiers, warnings, and factual claims equivalent.
- Document only behavior present in this repository or confirmed by official OpenAI documentation.
- Do not add badges, screenshots, a license, a contribution process, releases, or support promises.
- State that `./deploy.sh` stages all changes, commits with `chore: update project` when needed, and pushes the active branch to `origin`.

---

### Task 1: Create The Bilingual Public Entry Points

**Files:**
- Create: `README.md`
- Create: `README.en.md`

**Interfaces:**
- Consumes: `star-value-snapshot/SKILL.md`, `star-value-snapshot/references/data-api.md`, `scripts/deploy.py`, `tests/test_deploy.py`, and the official OpenAI skill documentation.
- Produces: two GitHub-renderable documents with reciprocal language links and identical user workflows.

- [ ] **Step 1: Draft the Chinese README**

Create `README.md` with this exact section order:

```markdown
[English](README.en.md)
# Codex Skills
## 可用技能
## 快速开始
### 前置条件
### 安装
### 使用
## 输出与原则
## 项目结构
## 测试
## 发布
## 参考资料
```

Describe `star-value-snapshot`, show installation through `$skill-installer` and `$HOME/.agents/skills`, provide explicit and natural-language prompt examples, list the HTML and Markdown output names, summarize the fact-only/data-source rules, and mark publishing as a maintainer workflow.

- [ ] **Step 2: Draft the equivalent English README**

Create `README.en.md` with the reciprocal `[中文](README.md)` link and this matching section order:

```markdown
[中文](README.md)
# Codex Skills
## Available Skill
## Quick Start
### Prerequisites
### Installation
### Usage
## Output And Principles
## Repository Layout
## Tests
## Publishing
## References
```

Use natural English rather than literal translation while preserving every command, path, example intent, output filename, limitation, and warning from `README.md`.

- [ ] **Step 3: Validate paths, links, and bilingual parity**

Run:

```bash
test -f README.md
test -f README.en.md
test -f star-value-snapshot/SKILL.md
test -f star-value-snapshot/assets/template.html
test -f star-value-snapshot/assets/template.md
test -f star-value-snapshot/references/data-api.md
test -f deploy.sh
test -f scripts/deploy.py
python3 - <<'PY'
from pathlib import Path

zh = Path("README.md").read_text(encoding="utf-8")
en = Path("README.en.md").read_text(encoding="utf-8")
shared = [
    "$skill-installer",
    "$HOME/.agents/skills",
    "star-value-snapshot",
    "python3 -m unittest discover -s tests -v",
    "./deploy.sh",
    "chore: update project",
]
for value in shared:
    assert value in zh, ("README.md", value)
    assert value in en, ("README.en.md", value)
assert "[English](README.en.md)" in zh
assert "[中文](README.md)" in en
PY
```

Expected: every command exits with status 0 and prints no assertion failure.

- [ ] **Step 4: Commit the two entry points**

```bash
git add README.md README.en.md
git commit -m "Add bilingual project README"
```

---

### Task 2: Verify The Documentation As A Reader

**Files:**
- Modify if needed: `README.md`
- Modify if needed: `README.en.md`

**Interfaces:**
- Consumes: the two documents from Task 1.
- Produces: verified documents with no broken repository references, unsupported claims, unclear setup steps, or bilingual drift.

- [ ] **Step 1: Run repository tests**

Run:

```bash
python3 -m unittest discover -s tests -v
```

Expected: all deploy integration tests pass.

- [ ] **Step 2: Run documentation hygiene checks**

Run:

```bash
if rg -n 'TBD|TODO|FIXME|\[To be written\]|localhost|example\.com' README.md README.en.md; then exit 1; fi
git diff --check HEAD~1 -- README.md README.en.md
```

Expected: `rg` finds nothing and `git diff --check` reports no whitespace errors.

- [ ] **Step 3: Perform context-free reader testing**

Give only the two README files to a fresh reader agent and ask it to answer:

1. What does this repository provide?
2. How can a Codex user install and invoke the skill?
3. What files does the skill generate?
4. What does the publishing script change and push?
5. Which statements are ambiguous, unsupported, or inconsistent across languages?

Revise both documents together if any answer is missing or inconsistent.

- [ ] **Step 4: Re-run parity, tests, and diff checks**

Repeat Task 1 Step 3, then run:

```bash
python3 -m unittest discover -s tests -v
git diff --check
git status --short
```

Expected: parity assertions and tests pass, the diff check is empty, and status lists only intentional README revisions if reader testing required changes.

- [ ] **Step 5: Commit reader-test revisions if present**

```bash
git add README.md README.en.md
git commit -m "Clarify bilingual README guidance"
```

Skip this commit when reader testing requires no revisions.
