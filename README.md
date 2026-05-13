# Git to Markdown Exporter (G2M-Export)

ローカルの Git リポジトリをスキャンし、AIが理解しやすい「1ファイル統合 Markdown」へエクスポートするツールです。各ファイルがリモート（GitHub/Bitbucket等）のどこに存在するかを示すURLを自動付与します。

## 特徴

- ローカル Git リポジトリを再帰的にスキャンし、1つの Markdown ファイルに統合
- `.git` ディレクトリから「リモートURL」と「カレントブランチ名」を直接取得（`git` コマンド不要）
- 各ファイルのセクションに [View on Remote](URL) 形式のリンクを挿入
- 設定ファイル (`.g2m_export.yaml`) による柔軟な除外設定 (`ignore_patterns`)
- ディレクトリ深さに応じた見出しレベル (`#`, `##`, ...) の動的変更
- バイナリファイルの自動判定と除外

## セットアップ

Python 3.8以上が必要です。

```bash
# 依存関係のインストール
pip install -r requirements.txt
```

## 実行方法

### 1. 設定ファイルの準備（任意）

プロジェクトルートまたはスキャン対象ディレクトリに `.g2m_export.yaml` を作成し、除外パターンを指定できます。

```yaml
ignore_patterns:
  - "*.log"
  - "node_modules/*"
  - ".pytest_cache/*"
```

### 2. 実行

最も簡単な実行方法（カレントディレクトリをスキャン）:

```bash
python -m g2m_export.cli
```

スキャン対象のディレクトリを指定して実行:

```bash
python -m g2m_export.cli /path/to/your/repo
```

出力先ディレクトリを指定して実行（既定値: `output`）:

```bash
python -m g2m_export.cli . --output-dir my_output
```

出力ファイル名を指定して実行:

```bash
python -m g2m_export.cli . --output my_repo.md
```

## パラメータ

- `src_dir`: スキャン対象のディレクトリ (既定: カレントディレクトリ)
- `--config`: 設定ファイルのパス (既定: `.g2m_export.yaml`)
- `--output`: 出力する Markdown ファイル名またはパス
- `--output-dir`: 出力先のディレクトリ (既定: `output`)

## デフォルトの出力ファイル名

- Git リポジトリの場合: `【Repo】 <リポジトリ名>.md`
  - Bitbucket 等でプロジェクトキーが取得可能な場合: `【Repo】 <プロジェクトキー>_<リポジトリ名>.md`
- それ以外の場合: `【Dir】 <ディレクトリ名>.md`

## 開発者向け

### テストの実行

```bash
pip install -r requirements-dev.txt
PYTHONPATH=. pytest tests/
```

### pre-commit の利用

```bash
pip install pre-commit
pre-commit install
```

## ライセンス

[MIT License](LICENSE)
