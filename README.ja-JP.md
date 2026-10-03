# AutoScribeAI

[English](README.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja-JP.md) | [한국어](README.ko-KR.md)

## AI にプロジェクトを渡して、実際に使える画像付き操作マニュアルを生成

プロジェクト、アクセス可能なテスト環境、対象ワークフローを AI に渡すと、AutoScribeAI がモジュール分析、許可された UI の実操作、スクリーンショット収集、実結果の記録、マニュアル出力までをガイドします。

**AutoScribeAI 用の常駐バックエンドは不要です。1 回の実行から Offline HTML、Word / DOCX、Markdown、カバレッジレポートを生成できます。**

プロジェクト納品、オンボーディング、社内システム、OSS ドキュメント、研修、受入資料、リリース後のマニュアル更新に実用的です。

### Demo Gallery

3 つの実サンプルを 1 ページにまとめた Vercel-ready Gallery を追加しました。生成済み HTML マニュアルと実際の Word 文書をそのまま確認できます。

- Uptime Kuma — 简体中文 — **3/3 verified**
- changedetection.io — 日本語 — **0/3 verified**。有料フローで止まった事実をそのまま記録
- IT Tools — 한국어 — **1/3 verified**。実測とソース由来候補を明確に分離

Gallery: [`demo/`](demo/) · Vercel: [`vercel.json`](vercel.json) · Samples: [`tests/manual_samples`](tests/manual_samples/README.md)
## 設計のポイント

- HTML を主要な閲覧形式として使用
- `manual.json` を単一の信頼できるデータ源として使用
- 実操作とスクリーンショット証拠がある場合のみ「検証済み」とする
- 常駐サービスは不要。5 つの Skills とローカルスクリプトで構成
- チェックポイントにより中断した実行を安全に再開

## Skills

- `autoscribe-orchestrator` — 実行計画、開始、再開、全体調整
- `autoscribe-project-analyzer` — モジュール、機能、ロール、候補ワークフローの分析
- `autoscribe-software-explorer` — 実 UI の操作と証拠収集
- `autoscribe-manual-writer` — 証拠から `manual.json` を生成
- `autoscribe-manual-verifier` — 出典、参照、カバレッジ、品質を検証

## 言語

- English — `en-US` **既定**
- 简体中文 — `zh-CN`
- 日本語 — `ja-JP`
- 한국어 — `ko-KR`

`language` を省略すると `en-US` が使用されます。他の BCP-47 言語も本文生成に使用できますが、固定テンプレートのラベルは英語にフォールバックします。

## クイックスタート

```bash
python -m pip install -r requirements.txt
python scripts/package_skills.py --output dist/autoscribeai-skills.zip
```

AI には `skills/autoscribe-orchestrator/SKILL.md` から開始するよう指示してください。実スクリーンショットを取得するには、AI ホスト側に許可済みブラウザまたは Computer Use 機能が必要です。

実例は [tests/manual_samples](tests/manual_samples/README.md)、詳細は [Installation](docs/INSTALLATION.md) を参照してください。
