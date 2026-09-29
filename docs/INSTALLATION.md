# 安装与使用 AutoScribeAI Skills

AutoScribeAI 不需要部署服务。技能指引 AI 分析项目并操作受授权的界面；本地 Python 命令负责校验、证据处理和生成 HTML、DOCX、Markdown。要保留完整目录结构，因为各技能会调用同一份 `scripts/`、`schemas/` 和 `references/`。

## 准备技能包

从仓库根目录执行：

```bash
python scripts/package_skills.py --output dist/autoscribeai-skills.zip
```

将 ZIP 解压到一个稳定目录，并保持其中的 `AutoScribeAI/` 根目录。不要只复制某个 `SKILL.md`：那样会缺少 CLI、校验 schema 和操作约定。若使用 GitHub 下载的源码 ZIP，也可直接保留整个仓库，不必额外制作技能包。

打包器默认拒绝覆盖已有 ZIP；重复生成时请指定新的输出文件名，确认旧包不再需要后再自行清理。

## 安装运行依赖

需要 Python 3.10 或更新版本。建议在技能包目录创建虚拟环境：

```bash
cd AutoScribeAI
python -m venv .venv
```

Linux/macOS：

```bash
. .venv/bin/activate
python -m pip install -r requirements.txt
```

Windows PowerShell：

```powershell
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

HTML、截图和 Markdown ZIP 使用 Pillow 与标准库；Word 导出还需要 `python-docx`，已包含在 requirements.txt。

## 让 AI 使用技能

把 `AutoScribeAI/skills/` 下的五个技能目录提供给支持本地 Skills 的 AI 宿主，并在说明中指出完整仓库根目录路径。若宿主只支持单文件技能导入，先保留整个 `AutoScribeAI/` 目录可供 AI 和终端访问，再在任务中要求它从 `skills/autoscribe-orchestrator/SKILL.md` 开始；其余四个技能作为专项流程按需读取。

项目配置中的 `language` 决定手册正文及导出模板的语言。当前内置模板支持 `zh-CN`（简体中文）、`en-US`（英语）、`ja-JP`（日语）和 `ko-KR`（韩语）；`zh`、`en`、`ja`、`ko` 等语言前缀也会自动匹配。其他 BCP-47 语言代码仍可用于 AI 撰写正文，固定模板标签暂时回退为英语。菜单、按钮等产品原始名称建议保留，并用目标语言解释。

当前技能包不自动安装到某个 AI 产品的全局目录，也不替宿主配置登录或浏览器。宿主必须提供可用的终端、文件读写；真实界面验证还需要已授权的浏览器和截图能力。登录凭据通过宿主安全能力提供，不写进项目配置或运行日志。

## 最小运行流程

从 `AutoScribeAI/` 目录开始，在项目副本中准备配置。可复制 `examples/project.json` 作为结构示例，填写项目来源、版本、角色、范围、输出语言与允许操作。示例值只用于演示，不代表任何目标网站已经验证。

```bash
python scripts/autoscribe_cli.py validate project path/to/project.json
python scripts/autoscribe_cli.py init path/to/project.json --run-dir path/to/runs/manual --host path/to/host.json
python scripts/autoscribe_cli.py analyze --config path/to/project.json --inventory path/to/inventory.json --manual-out path/to/runs/manual/manual.json --plan-out path/to/runs/manual/coverage-plan.json
python scripts/autoscribe_cli.py coverage --plan path/to/runs/manual/coverage-plan.json --inventory path/to/inventory.json --config path/to/project.json --manual path/to/runs/manual/manual.json --out path/to/runs/manual/coverage.json
python scripts/autoscribe_cli.py render-html --manual path/to/runs/manual/manual.json --coverage path/to/runs/manual/coverage.json --out-dir path/to/runs/manual/output
```

`analyze` 生成未验证手册骨架；只有 AI 使用真实界面完成流程、记录结果并关联经过检查的截图后，才能将流程标为 verified。输出目录包含离线 HTML、DOCX、Markdown ZIP 和质量报告。报告 `ready=false` 时应保留并说明所有缺口。

真实浏览器探索尚无通用自动化适配器，由 AI 宿主支持的浏览器能力执行。没有目标网站、账号角色或授权范围时，只运行源码盘点，不虚构操作记录或截图。
