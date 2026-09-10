[English](README.en.md)

# Codex Skills

这个仓库收录可复用的 Codex 技能。当前提供 `star-value-snapshot`（为港股上市公司生成基于公开数据的价值投资快照）与 `git-commit`（Git 提交与推送通用规程）。

## 可用技能

### [`star-value-snapshot`](star-value-snapshot/SKILL.md)

为指定港股生成一份 HTML 快照和一份 Markdown 底稿。技能会读取东方财富港股 F10 财务数据与腾讯行情，核对币种、历史股本、股息字段、上市前会计失真和行情日期，再用 Python 计算页面中的所有衍生指标。

它只整理已披露数据及其直接运算，不提供预测、目标价、评级或跨公司比较。分析结构包括入口检验、五步扫描、5 秒心算和五问清单。

### [`git-commit`](git-commit/SKILL.md)

约束 Git 提交与推送的通用规程：先弄清每处改动的归属，按任务隔离分批暂存（一个任务一个 commit），推送前变基到上游，并禁止盲暂存与 force-push。适用于任意 Git 仓库，也可直接用来编写提交说明或处理变基冲突。

## 快速开始

### 前置条件

- 支持本地技能的 Codex
- Git
- Python 3
- 可访问东方财富与腾讯行情接口的网络环境

### 安装

推荐在 Codex 中让 `$skill-installer` 从 GitHub 仓库安装技能：

```text
$skill-installer install the star-value-snapshot skill from https://github.com/Esdeath/skills
```

在 macOS 或 Linux 上，也可以手动安装到用户级技能目录：

```bash
git clone https://github.com/Esdeath/skills.git
mkdir -p "$HOME/.agents/skills"
cp -R skills/star-value-snapshot skills/git-commit "$HOME/.agents/skills/"
```

Codex 通常会自动识别新技能；如果技能没有出现，请重启 Codex。Codex 也支持把技能放在仓库内的 `.agents/skills` 目录中，详见 [OpenAI 技能文档](https://learn.chatgpt.com/docs/build-skills)。

### 使用

显式调用技能：

```text
$star-value-snapshot 为 09992 泡泡玛特生成企业快照
```

也可以直接描述任务，让 Codex 根据技能说明自动匹配：

```text
为 00700 腾讯生成价值线企业快照版
```

`git-commit` 可以显式调用，也会在你要求提交或推送代码时自动匹配：

```text
$git-commit 把当前改动按任务分批提交并推送到远端
```

## 输出与原则

每次运行会在 Codex 当前处理的项目根目录生成两个文件；它们用不同格式承载同一组事实和判定：

```text
HK_{公司简称}({5位代码}).html
HK_{公司简称}({5位代码}).md
```

其中，`公司简称` 是公司的中文简称，`5位代码` 是五位港股代码。

- HTML 使用 [`assets/template.html`](star-value-snapshot/assets/template.html) 渲染，适合浏览和打印。
- Markdown 使用 [`assets/template.md`](star-value-snapshot/assets/template.md) 渲染，适合发布、版本管理和保留决策记录。
- 数据接口、字段解释和备选取数方式记录在 [`references/data-api.md`](star-value-snapshot/references/data-api.md)。
- 财报数据以人民币为主，股价与股息以港元为主；技能会在结果中标明换算口径与行情日期。
- 接口失败或关键数据缺失时，技能应说明缺失内容，不编造数字。

## 项目结构

```text
.
├── README.md
├── README.en.md
├── git-commit/
│   └── SKILL.md
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

## 测试

部署脚本的测试使用临时 Git 仓库和本地裸仓库，不会访问真实远端：

```bash
python3 -m unittest discover -s tests -v
```

## 发布

> 此命令供仓库维护者使用。它会提交仓库中的全部变更，包括运行前已暂存的内容；请勿用它发布部分文件。

```bash
./deploy.sh
```

[`scripts/deploy.py`](scripts/deploy.py) 会执行相当于 `git add -A` 的操作，暂存新增、修改、删除以及运行前已暂存的内容；如果存在待提交内容，它会使用固定提交信息 `chore: update project` 创建提交，随后把当前分支推送到 `origin` 并设置上游分支。没有文件变更时，脚本仍会推送已有的本地提交。

脚本要求当前目录属于 Git 工作树、已配置 `origin`，并且 `HEAD` 指向分支；它不会自动运行测试、拉取远端、更换分支、改写提交或强制推送。

## 参考资料

- [OpenAI：Build skills](https://learn.chatgpt.com/docs/build-skills)
- [`star-value-snapshot` 完整说明](star-value-snapshot/SKILL.md)
- [`git-commit` 完整说明](git-commit/SKILL.md)
