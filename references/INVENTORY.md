# 项目清单与覆盖报告

使用 `schemas/inventory.schema.json` 编写分析清单。清单来自源码/说明的分析者；当前工具不会自动识别任意前端路由框架。静态推断填写 `source`，实际页面观察填写 `observed`，人工提供填写 `human`。`projectVersion` 使用明确提交 SHA、版本号或其他稳定标识。模块、功能及每条候选流程的 `location` 均应指向最具体的可复核文件、符号、路由或页面；流程位置可定位对应代码入口。

每个 workflow 说明 role、goal、preconditions、successCriteria；它是覆盖分母中的一项。每个原始 `scope` 字符串在 `scopeItems` 中必须恰好映射一次。scope 可以对应多条流程；每条流程也应至少归属一个范围。若某项范围找不到候选流程，workflowIds 可留空，但必须写明 reason，报告会显示无适用计划流程，而不会虚构覆盖。

```bash
python scripts/autoscribe_cli.py validate inventory examples/inventory.json
python scripts/autoscribe_cli.py analyze \
  --config examples/project.json --inventory examples/inventory.json \
  --manual-out runs/demo/manual.json --plan-out runs/demo/coverage-plan.json
python scripts/autoscribe_cli.py coverage \
  --plan runs/demo/coverage-plan.json --inventory examples/inventory.json \
  --config examples/project.json --manual runs/demo/manual.json \
  --out runs/demo/coverage.json
```

`coverage-plan.json` 保存每个模块、功能、流程 ID、原始范围和 inventory SHA-256。报告会核对清单文件摘要、配置范围、项目 ID/版本，以及 manual 中计划项目集合。编辑 inventory 或改变 scope 后，应复核新清单并显式重建计划；不要覆盖旧计划来隐藏未完成项。

覆盖率 = `verified / planned`。planned 包含范围内所有候选流程，不因 blocked、pending、unverified 而扣除；分母为零时显示“不适用”，而非 100%。范围清单中的每个模块与 scope 项都单独展示。将流程标为 verified 仍需完整步骤、实际结果和截图证据，并由人工检查内容真实性。
