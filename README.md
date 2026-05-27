# Git to Markdown Exporter (G2M-Export)

ローカルの Git リポジトリをスキャンし、AIが理解しやすい「1ファイル統合 Markdown」へエクスポートするツールです。各ファイルがリモート（GitHub/Bitbucket等）のどこに存在するかを示すURLを自動付与します。

## 特徴

- ローカル Git リポジトリを再帰的にスキャンし、1つの Markdown ファイルに統合
- `.git` ディレクトリから「リモートURL」と「カレントブランチ名」を直接取得（`git` コマンド不要）
- 各ファイルのセクションに [View on Remote](URL) 形式のリンクを挿入
- 設定ファイル (`g2m_config.yaml`) による柔軟な除外設定 (`ignore_patterns`)
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

必要に応じて、プロジェクトルートまたはスキャン対象ディレクトリに `g2m_config.yaml` を用意し、除外パターンを指定できます。
リポジトリにある `g2m_config_sample.yaml` を `g2m_config.yaml` にコピーして、必要であれば除外対象を追加/修正してください。

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

既存の出力ファイルを上書きして実行:

```bash
python -m g2m_export.cli . --overwrite
```

## パラメータ

- `src_dir`: スキャン対象のディレクトリ (既定: カレントディレクトリ)
- `--config`: 設定ファイルのパス (既定: `g2m_config.yaml`)
- `--output`: 出力する Markdown ファイル名またはパス (指定時は後述の Suffix は付与されません)
- `--output-dir`: 出力先のディレクトリ (既定: `output`)
- `--max-mb`: 1ファイルあたりの最大サイズ(MB) (既定: 95.0)
- `--stop-threshold-mb`: 実行全体での処理合計サイズ上限(MB) (既定: 950.0)
- `--overwrite`: 同名ファイルが存在する場合に上書きします（指定しない場合はSuffixが付与されます）。
- `--no-overwrite`: 同名ファイルが存在する場合に上書きせず、エラーとします（既定）。

## デフォルトの出力ファイル名

出力先 (`--output`) が指定されていない場合、以下の規則に従ってファイル名が自動生成されます。

- Git リポジトリの場合: `【Repo】 <リポジトリ名>.md`
  - Bitbucket 等でプロジェクトキーが取得可能な場合: `【Repo】 <プロジェクトキー>_<リポジトリ名>.md`
- それ以外の場合: `【Dir】 <ディレクトリ名>.md`

### Suffix (年月日時分秒) および Index の付与

上書き設定が OFF（デフォルト）かつ、出力先を自動生成する場合、ファイル名の末尾に実行時のタイムスタンプが Suffix として付与されます。
例: `2026年5月3日 16時5分02秒` に実行した場合、`_260503_160502` が付与されます。

ファイルサイズ制限により分割された場合、2つ目以降のファイル名に `_2`, `_3` ... と Index が付与されます。

`--output` でパスを明示的に指定した場合は、上書き設定に関わらず Suffix は付与されません。この場合、同名ファイルが存在し上書き設定が OFF であればエラーとなります。

## サイズ制限の挙動

- **1ファイルあたりの制限 (--max-mb)**: 出力される1ファイルあたりのサイズがこの値（既定 95.0MB）を超えないように制御します。超える場合は新しいファイルに分割されます。
- **実行全体の制限 (--stop-threshold-mb)**: 全出力ファイルの合計サイズがこの値（既定 950.0MB）を超える見込みになった時点で、スキャンと出力を停止し、処理を終了します。

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
