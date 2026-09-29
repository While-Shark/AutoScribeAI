# 三份公开项目样例手册

这些样例通过 AutoScribeAI 的 `autoscribe-project-analyzer`、`autoscribe-manual-writer`、`autoscribe-manual-verifier` 工作流制作，并从同一份 `manual.json` 导出 HTML、DOCX 和 Markdown ZIP。每个项目固定到下表的 Git commit，源码位置可从各样例的 `inventory.json` 和手册步骤直接追溯。

| 项目 | 手册语言 | 固定源码版本 | 许可证 | 示例内容 |
| --- | --- | --- | --- | --- |
| [Uptime Kuma](uptime-kuma/README.md) | 简体中文 | [`e7420f8`](https://github.com/louislam/uptime-kuma/commit/e7420f8fa546a8baa7ac4bf9d10a32545d4346e0) | MIT | HTTP 监控、通知渠道、状态页 |
| [changedetection.io](changedetection/README.md) | 日本語 | [`0e05667`](https://github.com/dgtlmoon/changedetection.io/commit/0e0566721b1c483dcf7ae548210ee10532d9b181) | Apache-2.0 | 监控对象、内容选择、Browser Steps |
| [IT Tools](it-tools/README.md) | 한국어 | [`d505845`](https://github.com/CorentinTh/it-tools/commit/d505845f918e946ec300af7b36efc107e2f66e9e) | GPL-3.0 | JSON 转 YAML、文本哈希、二维码 |

## 查看导出结果

每个项目目录都有 HTML、Word、Markdown 压缩包、统一内容模型和质量报告。点击项目名进入该样例，然后打开 `output/` 中对应文件。HTML 是独立离线页面；Markdown ZIP 解压后查看 `README.md`。

所有流程都明确标记为“未验证”，质量报告为 `ready: false`，因为这次只分析了对应 commit 的公开源码，没有启动或登录这三个项目，也没有浏览器操作和截图。`run/manifest.json` 记录了跳过的界面探索阶段，`run/coverage.json` 显示每份 0/3 个已验证流程。阅读时请把步骤视为待核验候选，而非现场操作记录。

每个样例保留了配置、源码清单、手册、覆盖计划和运行状态，便于查看技能输入如何映射到最终导出。由于上游项目许可证不同，仓库中只保存归纳后的操作指引，不复制项目源码或界面截图；请参阅各上游仓库中的许可证全文。
