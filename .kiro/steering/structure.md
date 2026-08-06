# プロジェクト構造

```
G2M-Export/
├── g2m_export/            # メインパッケージ
│   ├── __init__.py
│   ├── cli.py             # CLI エントリポイント（argparse、全体制御、分割出力）
│   ├── scanner.py         # ファイル走査、除外判定、バイナリ判定
│   ├── git_utils.py       # .git 直接読み取りによる Git 情報取得・URL 生成
│   └── markdown_writer.py # Markdown 生成・ファイル書き出し
├── tests/                 # pytest テスト
│   ├── test_cli_features.py
│   ├── test_git_utils.py
│   └── test_scanner.py
├── output/                # デフォルト出力先（生成された Markdown）
├── g2m_config.yaml        # ユーザー設定（gitignore 対象）
├── g2m_config_sample.yaml # 設定テンプレート
├── requirements.txt       # ランタイム依存
├── requirements-dev.txt   # 開発依存
├── .pre-commit-config.yaml
└── AGENTS.md              # エージェント向け指示書
```

## モジュール責務

| モジュール | 責務 |
|---|---|
| `cli.py` | 引数解析、設定読み込み、スキャン〜出力の全体フロー制御、ファイル分割ロジック |
| `scanner.py` | ディレクトリ再帰走査、`ignore_patterns` による除外、拡張子/内容ベースのバイナリ判定 |
| `git_utils.py` | `.git/config` からリモート URL 取得、`.git/HEAD` からブランチ取得、SSH→HTTPS 変換、プロバイダ別 URL 構築 |
| `markdown_writer.py` | ヘッダー生成、ファイルセクション生成（深さ対応見出し）、ファイル書き出し |

## 重要な設計制約

- `git` コマンドラインバイナリに依存しない（`.git` ディレクトリを直接読み取る）
- `.git` ディレクトリ配下は常にスキャン対象外
- 設定ファイル検索順: `--config` 指定 → `src_dir` 直下 → カレントディレクトリ
