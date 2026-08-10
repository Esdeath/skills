[中文](README.md)

# Codex Skills

This repository contains reusable skills for Codex. It currently provides `star-value-snapshot`, which creates public-data investment snapshots for companies listed in Hong Kong.

## Available Skill

### [`star-value-snapshot`](star-value-snapshot/SKILL.md)

The skill produces an HTML snapshot and a Markdown source document for a specified Hong Kong stock. It reads financial data from Eastmoney's Hong Kong F10 endpoint and quotes from Tencent, checks currency boundaries, historical share counts, dividend fields, pre-IPO accounting distortions, and quote dates, then uses Python to calculate every derived metric shown in the output.

It uses disclosed facts and direct arithmetic only. It does not provide forecasts, target prices, ratings, or cross-company comparisons. The analysis covers an entry screen, a five-step scan, quick mental checks, and a five-question checklist.

## Quick Start

### Prerequisites

- A Codex environment that supports local skills
- Git
- Python 3
- Network access to the Eastmoney and Tencent quote endpoints

### Installation

The recommended route is Codex's built-in `$skill-installer`:

```text
$skill-installer install the star-value-snapshot skill from https://github.com/Esdeath/skills
```

You can also install the skill manually in your user-level skill directory:

```bash
git clone https://github.com/Esdeath/skills.git
mkdir -p "$HOME/.agents/skills"
cp -R skills/star-value-snapshot "$HOME/.agents/skills/"
```

Codex usually detects a newly installed skill automatically. Restart Codex if it does not appear. You can also keep repository-scoped skills under `.agents/skills`; see the [OpenAI skills documentation](https://learn.chatgpt.com/docs/build-skills) for the supported locations.

### Usage

Invoke the skill explicitly:

```text
$star-value-snapshot Generate a company snapshot for Pop Mart (HKEX: 09992).
```

You can also describe the task and let Codex match the skill from its description:

```text
Create a Value Line company snapshot for Tencent (HKEX: 00700).
```

## Output And Principles

Each run writes two equivalent files to the current project root:

```text
HK_{公司简称}({5位代码}).html
HK_{公司简称}({5位代码}).md
```

Here, `公司简称` is the company's short Chinese name and `5位代码` is its five-digit Hong Kong stock code.

- The HTML output uses [`assets/template.html`](star-value-snapshot/assets/template.html) and is suited to browsing or printing.
- The Markdown output uses [`assets/template.md`](star-value-snapshot/assets/template.md) and is suited to publishing, version control, and keeping a decision record.
- Endpoint details, field definitions, and fallback sources live in [`references/data-api.md`](star-value-snapshot/references/data-api.md).
- Financial statements primarily use RMB, while share prices and dividends use HKD. The output states its conversion basis and quote date.
- When an endpoint fails or required data is missing, the skill should identify the gap instead of inventing a value.

## Repository Layout

```text
.
├── README.md
├── README.en.md
├── star-value-snapshot/
│   ├── SKILL.md
│   ├── assets/
│   │   ├── template.html
│   │   └── template.md
│   └── references/
│       └── data-api.md
├── scripts/
│   └── deploy.py
├── tests/
│   └── test_deploy.py
└── deploy.sh
```

## Tests

The deployment tests use temporary Git repositories and local bare remotes. They do not contact the configured remote:

```bash
python3 -m unittest discover -s tests -v
```

## Publishing

> This command is for repository maintainers. Review the active branch and every working-tree change before running it.

```bash
./deploy.sh
```

The script performs the equivalent of `git add -A`, staging additions, modifications, and deletions. When the index contains changes, it creates a commit with the fixed message `chore: update project`, then pushes the active branch to `origin` and configures its upstream. With no file changes, it still pushes any existing local commits.

The script requires a Git worktree, a configured `origin`, and a branch-attached `HEAD`. It does not pull, switch branches, rewrite commits, or force-push.

## References

- [OpenAI: Build skills](https://learn.chatgpt.com/docs/build-skills)
- [Full `star-value-snapshot` instructions](star-value-snapshot/SKILL.md)
