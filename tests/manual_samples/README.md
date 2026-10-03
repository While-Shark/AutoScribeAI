# 三份公开项目样例手册

**在线 Demo Gallery：** [https://auto-scribe-ai-tau.vercel.app](https://auto-scribe-ai-tau.vercel.app)

这些样例通过 AutoScribeAI 的项目分析、手册编写、流程核验技能制作，并从 `manual.json` 导出 HTML、DOCX 和 Markdown ZIP。每个项目固定到下表的 Git commit。

| 项目 | 手册语言 | 固定源码版本 | 许可证 | 实测截图 | 流程覆盖 |
| --- | --- | --- | --- | --- | --- |
| [Uptime Kuma](uptime-kuma/README.md) | 简体中文 | [`e7420f8`](https://github.com/louislam/uptime-kuma/commit/e7420f8fa546a8baa7ac4bf9d10a32545d4346e0) | MIT | [监控](uptime-kuma/screenshots/monitor-created-dashboard.jpg)、[通知](uptime-kuma/screenshots/notification-saved.jpg)、[状态页](uptime-kuma/screenshots/status-page-public.jpg) | 3/3；官方临时实例实测 |
| [changedetection.io](changedetection/README.md) | 日本語 | [`0e05667`](https://github.com/dgtlmoon/changedetection.io/commit/0e0566721b1c483dcf7ae548210ee10532d9b181) | Apache-2.0 | [官方公开页面](changedetection/screenshots/changedetection-public-homepage.jpg) | 0/3；公开页面转入付费订阅 |
| [IT Tools](it-tools/README.md) | 한국어 | [`d505845`](https://github.com/CorentinTh/it-tools/commit/d505845f918e946ec300af7b36efc107e2f66e9e) | GPL-3.0 | [JSON→YAML 实测截图](it-tools/output/evidence/ev-it-tools-json-yaml.jpg) | 1/3；JSON→YAML 已验证 |

## 查看导出结果

每个项目目录都有离线 HTML、Word、Markdown 压缩包、结构化手册和质量报告。打开样例目录中的 `output/` 即可查看。HTML 和 DOCX 已嵌入关联的实测截图；Markdown ZIP 也包含图片资源。Uptime Kuma 在官方临时演示实例完成了监控、通知配置和状态页流程。Webhook 使用 `example.invalid` 占位地址且未发送测试消息，实例运行版本也未与固定源码提交核对，因此质量报告保留限制说明。changedetection.io 的截图显示官方公开站点的付费订阅入口，没有提交 URL 或付款，其功能流程保持未验证。

IT Tools 的 JSON→YAML 操作已在公开部署页面输入合成样例并观察转换结果。源码索引固定版本与公开部署版本未对齐；手册明确记录该限制。文本哈希与 QR 码仍未实测。Uptime Kuma 与 changedetection.io 的质量报告为 `ready: false`，分别因为演示版本/通知投递限制及付费流程未验证；IT Tools 仍保留公开部署版本与固定源码版本未对齐的说明。

每个样例保留配置、源码清单、手册、覆盖计划和运行状态，便于查看技能输入如何映射到导出。项目源码未复制进本目录；截图为本次浏览器实测页面。
