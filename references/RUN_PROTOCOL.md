# 运行约定（M0）

采用 Python 3.10+ 和 JSON Schema 2020-12；安装 `requirements.txt`。所有命令都可使用脚本绝对路径运行。完整仓库是当前技能资源单元，不能只复制 SKILL.md；尚未提供自动安装包。

## 命令

```bash
python scripts/autoscribe_cli.py validate project examples/project.json
python scripts/autoscribe_cli.py init examples/project.json --run-dir runs/demo --host examples/host.json
python scripts/autoscribe_cli.py stage runs/demo analyze running
python scripts/autoscribe_cli.py stage runs/demo analyze completed
python scripts/autoscribe_cli.py resume runs/demo --config examples/project.json --host examples/host.json
python scripts/autoscribe_cli.py status runs/demo
```

`source.path` 相对配置文件解析；初始化时转换为绝对路径。目标版本在 project.version 中填写提交 SHA/产品版本；当前不会自动探测代码或线上部署版本，恢复者必须核对。未填写版本时尤须人工复核。

`host.json` 由宿主观察实际工具后填写。available 表示当前可使用的工具，不代表已登录、目标可达或拥有指定角色。未声明或 resume 时没有重新提供 host，浏览器恢复为 unknown。终端/文件能力由脚本实际执行和临时写入检查；docxDependency 只表示依赖存在，不代表导出实现可用。

源码可访问时允许 source-only 模式继续分析；没有 URL/浏览器截图能力不能进入 explore。没有可访问输入时 preflight=blocked。浏览器与 URL 具备时仍需在探索阶段核对访问、登录、角色。

## 状态与恢复

manifest.json 是唯一权威状态；checkpoint.json 是可修复投影。每次先原子替换 manifest，再更新 checkpoint；中途断电可能使投影滞后，resume 从 manifest 重建。不承诺网络文件系统/硬件断电的目录持久性。任务目录需位于可信本地磁盘。

阶段：preflight → analyze → explore → write → export → verify。

- pending → running / blocked / skipped
- running → completed / blocked / failed
- blocked / failed → running / skipped
- completed / skipped 为终态；变更输入时建立新运行并复核证据。

进入 running 前，前置阶段必须 completed 或 skipped。blocked、failed、skipped 必须有原因。跳过允许降级，但不等于验收通过。阶段 completed 是调用者检查产物后的声明；M0 不强制检查各阶段产物，尚无自动执行引擎。

resume 将中断的 running 改为 blocked，返回复核清单；它不会调用浏览器或重放任何操作。对登录、目标版本、截图有效性和有副作用操作，宿主必须自行复核。仅实现阶段级恢复，步骤级幂等和执行日志在 T12 中实现。

`.state.lock` 拒绝并发写入。进程被强杀时可能遗留锁；确认没有写入进程后才人工移除。不要根据时间自动删除锁。

## 信息处理

配置只存项目来源、角色、范围、允许动作及测试数据规则。不存密码、Cookie、API 密钥。文本检测只覆盖常见敏感字段/赋值和 URL 凭据；不能识别所有秘密或个人信息。URL 应使用无查询参数及片段的脱敏入口，哈希路由的具体位置写入步骤 location。

错误输出不回显非法字段的值。默认 runs/ 已排除版本控制；不要将真实任务状态、截图和账号数据提交仓库。
