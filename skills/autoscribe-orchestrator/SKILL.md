---
name: autoscribe-orchestrator
description: 为软件项目规划、启动和恢复带真实截图的操作手册任务。用户提供源码、项目地址或要求继续 AutoScribeAI 任务时使用；协调分析、探索、写作与核验。
---

# 组织手册任务

读取 [运行约定](../../references/RUN_PROTOCOL.md)。保留整个仓库目录；命令中的 `<repo>` 指本文件上两级目录。当前为 M0 基础版本：可以预检、校验和保存状态，尚无截图采集适配器或导出器。不得声称完整手册已自动生成。

1. 收集项目来源、版本、环境、角色、范围、输出语言、格式和允许动作。参考 `examples/project.json`。使用宿主安全登录；不要索取写入配置的密码。
2. 检查终端和文件能力；通过宿主实际可用工具验证浏览器及截图能力。创建 `host.json`，未知时保留 unknown。不要启动或探测未获授权的网站。
3. 执行 `python <repo>/scripts/autoscribe_cli.py init <config> --run-dir <new-directory> --host <host.json>`。读取降级原因；源码模式不算已验证界面。
4. 按 analyze → explore → write → export → verify 顺序调用同级专项技能；交接产物路径与缺口，不重复运行完成的阶段。每次只有一个任务写入状态。按照运行约定更新阶段；标记完成只说明此阶段产物已人工检查，不等同于质量验收。
5. 使用 `resume <run-directory> --config <config> --host <fresh-host.json>` 恢复。先核对版本、登录、证据和已有写入结果。任何被中断的运行阶段都会变为 blocked；确认后才能转 running。不要自动重放提交动作。
6. 若缺少导出器或必要工具，记录 blocked 及原因并交付已有产物和剩余任务，不伪造下载链接、不把跳过当作完成。

分工：分析交给 `autoscribe-project-analyzer`；界面操作交给 `autoscribe-software-explorer`；内容整理交给 `autoscribe-manual-writer`；质量检查交给 `autoscribe-manual-verifier`。不要求启动子智能体。
