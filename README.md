[English](README.en.md)

# Codex Skills

这个仓库收录可复用的 Codex 技能。当前提供 `star-value-snapshot`，用于为港股上市公司生成基于公开数据的价值投资快照。

## 可用技能

### [`star-value-snapshot`](star-value-snapshot/SKILL.md)

为指定港股生成一份 HTML 快照和一份 Markdown 底稿。技能会读取东方财富港股 F10 财务数据与腾讯行情，核对币种、历史股本、股息字段、上市前会计失真和行情日期，再用 Python 计算页面中的衍生指标。

它只整理已披露数据及其直接运算，不提供预测、目标价、评级或跨公司比较。分析结构包括入口检验、五步扫描、5 秒心算和五问清单。

## 快速开始

### 前置条件

- 支持本地技能的 Codex
- Git
- Python 3
- 可访问东方财富与腾讯行情接口的网络环境

### 安装

推荐在 Codex 中调用内置的 `$skill-installer`：

```text
$skill-installer install the star-value-snapshot skill from https://github.com/Esdeath/skills
```

也可以手动安装到用户级技能目录：

```bash
git clone https://github.com/Esdeath/skills.git
mkdir -p "$HOME/.agents/skills"
cp -R skills/star-value-snapshot "$HOME/.agents/skills/"
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

## 输出与原则

每次运行会在当前项目根目录生成两个内容一致的文件：

```text
HK_{公司简称}({5位代码}).html
HK_{公司简称}({5位代码}).md
```

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

> 此命令供仓库维护者使用。运行前请检查当前分支和工作区中的全部变更。

```bash
./deploy.sh
```

脚本会执行相当于 `git add -A` 的操作，暂存新增、修改和删除的文件；如果存在待提交内容，它会使用固定提交信息 `chore: update project` 创建提交，随后把当前分支推送到 `origin` 并设置上游分支。没有文件变更时，脚本仍会推送已有的本地提交。

脚本要求当前目录属于 Git 工作树、已配置 `origin`，并且 `HEAD` 指向分支；它不会拉取远端、更换分支、改写提交或强制推送。

## 参考资料

- [OpenAI：Build skills](https://learn.chatgpt.com/docs/build-skills)
- [`star-value-snapshot` 完整说明](star-value-snapshot/SKILL.md)
