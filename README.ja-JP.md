# AutoScribeAI

[English](README.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja-JP.md) · [한국어](README.ko-KR.md)

> ソフトウェアプロジェクトを AI に渡して、実スクリーンショット付きの操作マニュアルを生成します。

**Live Demo:** https://auto-scribe-ai-tau.vercel.app/?lang=ja

AutoScribeAI は、プロジェクト解析、許可された UI 操作、スクリーンショット取得、実結果の記録を行い、**HTML、Word / DOCX、Markdown** を出力するポータブル Skill Pack です。

AutoScribeAI 専用バックエンドは不要です。

## まず結果を見る

Live Demo には 3 つの実サンプルがあります。

| Project | Language | Verified |
| --- | --- | --- |
| Uptime Kuma | 简体中文 | **3/3** |
| changedetection.io | 日本語 | **0/3**。ブロッカーを保持し、未実行手順を生成しません |
| IT Tools | 한국어 | **1/3**。実測とソース由来候補を分離 |

**[Open Live Demo →](https://auto-scribe-ai-tau.vercel.app/?lang=ja)**

HTML マニュアル、生成済み Word、実スクリーンショット、検証状態を直接確認できます。

## 出力

- **Offline HTML**：検索と画像表示に対応し、単一ファイルでも共有できます。
- **Word / DOCX**
- **Markdown**
- **PDF（任意）**：LibreOffice があれば固定レイアウトで出力できます。
- **Coverage / Quality report**
- **確認ツール**：役割別の閲覧、中断した作業の再開、版の差分確認、出力リンクの検査。

実際の操作結果と証拠がないワークフローは verified になりません。

## 使い方

```bash
git clone https://github.com/While-Shark/AutoScribeAI.git
cd AutoScribeAI
python -m pip install -r requirements.txt
```

AI Agent をこのディレクトリで起動し、次のように指示します。

```text
Read skills/autoscribe/SKILL.md and use AutoScribeAI
to generate a complete illustrated user manual.
```

<details>
<summary><strong>Codex</strong></summary>

AutoScribeAI ルートで `codex` を起動し、`skills/autoscribe/SKILL.md` を読むよう指示します。

</details>

<details>
<summary><strong>Claude Code</strong></summary>

AutoScribeAI ルートで `claude` を起動し、`skills/autoscribe/SKILL.md` を読むよう指示します。

Claude Code は native Skills をサポートしますが、AutoScribeAI は共有 scripts / schemas / references を利用するため、完全なリポジトリを保持する方法を推奨します。

</details>

<details>
<summary><strong>Pi</strong></summary>

AutoScribeAI ルートで Pi を起動し、`skills/autoscribe/SKILL.md` を読み込ませます。Pi は Agent Skills / `SKILL.md` をサポートします。

</details>

<details>
<summary><strong>Agy / Google Antigravity</strong></summary>

AutoScribeAI ルートで `agy` を起動し、`skills/autoscribe/SKILL.md` を読み込ませます。Antigravity は Agent Skills をネイティブサポートします。

</details>

<details>
<summary><strong>OpenCode</strong></summary>

AutoScribeAI ルートで OpenCode を起動し、`skills/autoscribe/SKILL.md` を読み込ませます。OpenCode は `SKILL.md` と Agent Skills をサポートします。

</details>

<details>
<summary><strong>Other agents</strong></summary>

Cursor、Cline、Roo Code、Gemini CLI などでも、ファイル読み取りとコマンド実行が可能なら利用できます。

完全な AutoScribeAI ディレクトリをワークスペースとして開き、autoscribe Skill を読むよう指示してください。

</details>

## Languages

- **English — `en-US` (default)**
- 简体中文 — `zh-CN`
- 日本語 — `ja-JP`
- 한국어 — `ko-KR`

## Links

- [Live Demo](https://auto-scribe-ai-tau.vercel.app/?lang=ja)
- [Samples](tests/manual_samples/README.md)
- [Installation](docs/INSTALLATION.md)
- [Technical design](docs/TECHNICAL_DESIGN.md)
