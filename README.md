# Infographic Skill for Claude Code

Claude Code のスキル / プラグインとして動作するインフォグラフィック画像生成ツール。
Google Gemini API を使って、テキストプロンプトからスライド画像やイラスト素材を生成します。

| Graphic Recording Style | Consulting Style |
|:-:|:-:|
| ![Graphic Recording](docs/hero.png) | ![Consulting](docs/sample-consulting.png) |

## Features

- **5つの構成タイプ** — プレゼン用スライド / ビジネス資料 / ドキュメント用図解 / モチーフ素材 / カスタム
- **2つのスタイル** — IDEO/McKinsey コンサル風 / グラフィックレコーディング風（カスタムも可）
- **アスペクト比指定** — 16:9（スライド）、1:1（モチーフ）、4:3、9:16 等をサポート
- **プリセットシステム** — 構成 × スタイルの組み合わせで最適なプロンプトを自動設計
- **複数モデル対応** — Gemini 3 Pro（高品質）/ Gemini 3.1 Flash（低コスト）/ Imagen 4（写実的）
- **外部依存なし** — Python 標準ライブラリのみで動作（pip install 不要）

## Requirements

- Python 3.10+
- Google Gemini API key ([取得はこちら](https://aistudio.google.com/apikey))
- 外部パッケージ不要（Python 標準ライブラリのみ）

## Setup

### Option A: プラグインとしてインストール（推奨）

Claude Code 内で以下を実行：

```
/plugin marketplace add kseriri/infographic-skill
/plugin install infographic@infographic-skill
```

インストール後、API キーを設定：

```bash
export Google_Image_API="your-api-key-here"
```

またはプラグインのインストール先に `.env` を配置（スクリプトが自動検出します）。

### Option B: リポジトリをクローン

```bash
git clone https://github.com/kseriri/infographic-skill.git
cd infographic-skill
cp .env.example .env
# .env を編集して API キーを設定
```

Claude Code を起動すると `.claude/skills/infographic/SKILL.md` が自動認識されます。

### Option C: 既存プロジェクトにコピー

```bash
# スキル定義をコピー
cp -r .claude/skills/infographic /path/to/your-project/.claude/skills/

# スクリプトをコピー
cp -r scripts/ /path/to/your-project/scripts/

# .env をコピー（APIキーを設定済みの場合）
cp .env /path/to/your-project/.env
```

### API キーの取得

[Google AI Studio](https://aistudio.google.com/apikey) でAPIキーを取得してください。

## Usage（Claude Code）

Claude Code に話しかけるだけ：

- 「インフォグラフィック作って」
- 「図解を生成して」
- 「スライド画像を作って」
- 「モチーフ作って」

スキルが自動的に起動し、プロンプト設計 → 生成 → レビューのフローを実行します。

## CLI（Claude Code なしでも動作）

```bash
# スライド（16:9、デフォルトスタイル）
python3 scripts/generate-image.py \
  --prompt "フロー図を描いてください" \
  --default-style --aspect 16:9 \
  --output output/flow.png

# モチーフ（1:1、スタイルなし）
python3 scripts/generate-image.py \
  --prompt "フラットデザインのアイコン。走る人。オレンジ。白背景。テキストなし。" \
  --aspect 1:1 \
  --output output/motif-runner.png

# 複数枚生成
python3 scripts/generate-image.py \
  --prompt "アイコンイラスト" \
  --num 3 --output-dir output/ --name icon

# 低コストモデル
python3 scripts/generate-image.py \
  --model gemini-3.1-flash-image-preview \
  --prompt "ドラフト用の図解" \
  --output output/draft.png

# プロンプトファイルから
python3 scripts/generate-image.py \
  --prompt-file prompts/my-slide.txt \
  --default-style --output output/slide.png
```

### CLI Options

| Option | Short | Description |
|--------|-------|-------------|
| `--prompt` | `-p` | プロンプトテキスト（直接指定） |
| `--prompt-file` | `-f` | プロンプトファイルのパス |
| `--output` | `-o` | 出力ファイルパス |
| `--output-dir` | `-d` | 出力ディレクトリ（デフォルト: `output/`） |
| `--name` | `-n` | ファイル名のベース（拡張子なし） |
| `--aspect` | `-a` | アスペクト比: `1:1`, `16:9`, `9:16`, `4:3`, `3:4`, `3:2`, `2:3` |
| `--style-prefix` | | スタイル指示テキスト |
| `--style-file` | | スタイル指示ファイルのパス |
| `--default-style` | | デフォルトスタイル（IDEO/McKinsey風）を使用 |
| `--num` | `-N` | 生成枚数（デフォルト: 1） |
| `--model` | `-m` | モデル名（デフォルト: `gemini-3-pro-image-preview`） |

## Models

| Model | ID | Quality | Use case |
|-------|-----|---------|----------|
| Gemini 3 Pro | `gemini-3-pro-image-preview` | Best | デフォルト。正式な資料用 |
| Gemini 3.1 Flash | `gemini-3.1-flash-image-preview` | Good | ドラフト・大量生成 |
| Imagen 4 | `imagen-4.0-generate-001` | Photorealistic | 写真風ビジュアル |

## License

MIT
