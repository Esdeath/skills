---
name: git-commit
description: "Git 提交与推送通用规程：先弄清改动归属，按任务隔离分批提交（每个任务一个 commit），推送前自动变基。当用户要求提交/推送 git、编写提交说明、处理涉及多文件/多任务的提交、或需要变基/解决变基冲突时调用。"
whenToUse: "适用于任意 Git 仓库的提交与推送场景：用户要求提交/推送 git、编写提交说明、对多文件/多任务改动分批提交、变基或解决变基冲突。"
---

# Git 提交与推送（通用）

> 本技能适用于任意 Git 仓库。执行前先确定仓库根目录（`git rev-parse --show-toplevel`），后续命令均在该目录执行。

## 铁律（先于一切）

1. **不自动提交**：仅当用户明确要求「提交/推送到 git」时才执行；任务完成默认只汇报改动清单。
2. **禁止 force-push**：任何情况下不执行 `git push --force`、`--force-with-lease` 或任何等价写法；推送被拒、冲突无法解决时停下向用户报告。
3. **提交前必须弄清改动**：先 `git status` + `git diff --stat`，必要时 `git diff` 看内容，判断每个文件属于哪个任务，**禁止盲提交**。
4. **禁止盲暂存**：只 `git add <明确路径>`，不用 `git add -A`、`git add .`、`git commit -a`，避免把无关改动、构建产物或他人改动裹进提交。
5. **尊重仓库既有惯例**：提交信息风格、分支策略以当前仓库为准；不确定时先看 `git log --oneline -10` 归纳惯例，仍拿不准就询问用户。

## 第 0 步：弄清仓库上下文

```bash
git rev-parse --show-toplevel             # 仓库根目录
git remote -v                             # 远程地址（origin 为主）
git symbolic-ref --short HEAD             # 当前分支
git rev-parse --abbrev-ref origin/HEAD    # 远程默认分支（可能取不到）
git status -sb                            # 当前分支与上游的 ahead/behind 关系
git log --oneline -10                     # 近期提交信息风格
```

- 默认分支不写死：优先读 `origin/HEAD`；部分克隆里该引用不存在（报 `ref refs/remotes/origin/HEAD is not a symbolic ref` 属正常现象），
  此时改用 `git ls-remote --symref origin HEAD | head -1` 或 `git remote show origin` 判断 `master`/`main`，仍不确定时询问用户。
- 当前分支若无上游（`git rev-parse --abbrev-ref '@{upstream}'` 报错）或不是默认分支，提交后是否推送、推送到哪，先与用户确认。

## 第 1 步：摸底

```bash
git status          # 改动文件清单（含 ?? 未跟踪文件，注意甄别）
git diff --stat     # 每个文件改动量
git diff            # 有疑问时看具体内容，判断文件归属
```

## 第 2 步：按任务切割

- 按**路径/业务域/改动内容**聚类：同一功能的文件属于同一任务（如「文案修复」= 多个页面文案文件；「工具链」= `package.json` + lock + 类型修复）。
- 摸不清某个文件属于哪个任务时，停下来向用户说明，不擅自归并。

## 第 3 步：逐个任务提交（一个任务一个 commit）

```bash
git add <任务A的文件…>       # 只 add 该任务的文件
git diff --cached --stat     # 核对暂存区只包含任务 A
git commit -m "type(scope): 任务A标题" -m "- 要点1" -m "- 要点2"
# …任务 B、C 重复以上三步（每个任务独立 commit，历史清晰）
```

- 标题风格优先遵循当前仓库惯例（从 `git log` 归纳）；无明确惯例时用 Conventional Commits：`type ∈ feat / fix / chore / docs / refactor / style / test / perf / build / ci`，`scope` 用模块或目录名（如 `site`、`admin`、`api`、`web`），要点用多个 `-m` 追加。

## 第 4 步：推送前自动变基

变基目标取决于当前分支是否已有上游（即是否已推送过），先判断：

```bash
git fetch origin
git rev-parse --abbrev-ref '@{upstream}'   # 报错说明当前分支还没有上游
```

- **已有上游（分支已推送过）**：变基到自己的上游，保持快进推送，不改写已公开历史：

```bash
git rebase '@{upstream}'
git push
```

- **还没有上游（新分支）**：先变基到最新的默认分支，再首次推送并设置上游：

```bash
git rebase origin/<默认分支>
git push -u origin <当前分支>
```

- 变基后推送仍被拒（`non-fast-forward`）说明远端有本地没有的提交：**停下报告**，不要 force-push。
  已在上游发布过的分支不要变基到默认分支——那会改写已公开的历史，与铁律 2 冲突。

## 第 5 步：收尾确认

```bash
git status -sb                      # 与上游同步（无 ahead/behind）
git log --oneline -1                # 本地最新提交
git log --oneline -1 '@{upstream}'  # 上游最新提交：两者 hash 一致才算推送成功
```

## 变基冲突处理

```bash
git status                    # 查看冲突文件
# 手动解决冲突后：
git add <已解决的文件>
git rebase --continue         # 继续变基；再冲突则重复上述两步
git push                      # 已有上游时；新分支用 git push -u origin <当前分支>
```

拿不准时可用 `git rebase --abort` 整体放弃本次变基，回到变基前状态。无法解决的问题（如语义冲突拿不准）立刻停下，向用户说明冲突内容与选项，**不要 force-push、不要乱改他人代码**。

## 注意事项

- **不要提交的内容**：临时/构建产物目录（如 `.temp/`、`dist/`、`stats.html` 等）、密钥与凭据（`.env`、`*.pem`、token 文件）、本地工具配置（`.dsh/`、`.agents/` 等技能目录，视仓库跟踪状态而定，一般不入仓）、被 .gitignore 忽略的规则文件（如 `AGENTS.md`）。拿不准时用 `git check-ignore <path>` 确认。
- 命令按 POSIX shell（sh/zsh/bash）书写，可用 `&&` 串联；在 Windows PowerShell 中执行时改用 `;` 分隔，PowerShell 不支持 `&&`。
- 在 PowerShell 中，远程为未加密 HTTP 时 git 会打印 warning（`use of unencrypted HTTP remote URLs`）并可能让 `git push` 返回 exit 1。判断推送是否成功一律以输出中的 `<旧hash>..<新hash>  <分支> -> <分支>` 行为准，不要只看退出码；该 warning 属正常提示，不影响推送结果。
- 提交前如改动涉及代码/前端，建议先跑项目已有的静态检查（类型检查 / lint / 测试）再提交。
- 提交完成后检查是否有构建产物或临时文件被误 add：若出现，`git rm --cached` 后重新提交对应任务。

## 交付汇报模板

提交完成后向用户汇报：提交清单（每个 commit 的 hash + 标题 + 涉及文件数/路径归组）、是否推送成功、与远端对应分支（上游）的同步状态。未推送则明确告知「已提交未推送」。
