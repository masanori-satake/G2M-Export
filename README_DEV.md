# G2M-Export 開発者向けドキュメント

このドキュメントは、G2M-Export の内部構造、アルゴリズム、および開発プロセスについて説明します。

## システム構成図

ツールの全体的なコンポーネント構成とデータの流れを以下に示します。

```mermaid
graph TD
    User([ユーザー]) --> CLI[CLI / cli.py]
    CLI --> Config[設定読み込み / yaml]
    CLI --> Scanner[Scanner / scanner.py]
    CLI --> GitUtils[Git Utils / git_utils.py]
    CLI --> MarkdownWriter[Markdown Writer / markdown_writer.py]
    Scanner --> FS[(ファイルシステム)]
    GitUtils --> GitDir[.git ディレクトリ]
    MarkdownWriter --> OutputFile[Markdown ファイル]
```

## クラス/モジュール構造

主なモジュールとその役割は以下の通りです。

```mermaid
classDiagram
    class CLI {
        +main() CLIの起点。引数解析と全体制御
        +load_config() .g2m_export.yamlの読み込み
    }
    class Scanner {
        +scan_files() ファイルの再帰的走査
        +should_ignore() 除外パターン判定
        +is_binary() 内容ベースのバイナリ判定
    }
    class GitUtils {
        +get_git_root() .gitディレクトリの探索
        +get_remote_url() リモートURLの抽出
        +get_current_branch() 現在のブランチ名取得
        +get_file_remote_url() ファイル単位のURL生成
        +parse_repo_info() リポジトリ名やプロジェクトキーの解析
    }
    class MarkdownWriter {
        +generate_markdown() Markdownコンテンツの構築
        +write_to_file() ファイルへの保存
    }
    CLI ..> Scanner
    CLI ..> GitUtils
    CLI ..> MarkdownWriter
    MarkdownWriter ..> GitUtils
```

## 処理シーケンス

CLI を実行してから Markdown ファイルが出力されるまでの流れです。

```mermaid
sequenceDiagram
    actor User
    User->>CLI: コマンド実行 (src_dir, options)
    CLI->>CLI: 設定の読み込み (.g2m_export.yaml)
    CLI->>GitUtils: Gitルート、リモートURL、ブランチの取得
    GitUtils-->>CLI: Git情報
    CLI->>Scanner: ファイルスキャン (ignore_patterns, binary_extensions)
    Scanner->>Scanner: 除外パターンとバイナリの判定
    Scanner-->>CLI: ファイルリスト
    CLI->>MarkdownWriter: Markdown生成 (files, remote_url, branch)
    MarkdownWriter->>GitUtils: ファイルごとのリモートURL生成
    GitUtils-->>MarkdownWriter: URL
    MarkdownWriter->>MarkdownWriter: コンテンツの統合
    MarkdownWriter-->>CLI: Markdownコンテンツ
    CLI->>MarkdownWriter: ファイル書き出し
    CLI->>User: 完了メッセージ
```

## ファイルスキャン・アルゴリズム

ファイルのスキャンとフィルタリングのプロセスです。バイナリ判定は拡張子と内容の両面で行われます。

```mermaid
flowchart TD
    Start([スキャン開始]) --> NextPath{次のパスがあるか?}
    NextPath -- Yes --> IsFile{ファイルか?}
    IsFile -- No --> NextPath
    IsFile -- Yes --> IsGit{ .git 内のファイル?}
    IsGit -- Yes --> NextPath
    IsGit -- No --> BinaryExt{バイナリ拡張子か?}
    BinaryExt -- Yes --> NextPath
    BinaryExt -- No --> IgnorePattern{除外パターンに一致?}
    IgnorePattern -- Yes --> NextPath
    IgnorePattern -- No --> IsBinaryContent{バイナリ内容か?}
    IsBinaryContent -- Yes --> NextPath
    IsBinaryContent -- No --> AddList[リストに追加]
    AddList --> NextPath
    NextPath -- No --> End([スキャン終了])
```

## テスト方法

品質管理のために、pytest を使用した自動テストを実施しています。

### テストの実行

開発用依存関係をインストールした後、プロジェクトルートで以下のコマンドを実行します。

```bash
# 依存関係のインストール
pip install -r requirements-dev.txt

# テストの実行
PYTHONPATH=. pytest tests/
```

### テスト構成

- `tests/test_git_utils.py`: Git情報の取得やURLパースのロジックをテストします。
- `tests/test_scanner.py`: ファイルのフィルタリング、除外パターン、バイナリ判定をテストします。

### カバレッジの確認 (任意)

`pytest-cov` を使用してカバレッジを確認できます。

```bash
pip install pytest-cov
PYTHONPATH=. pytest --cov=g2m_export tests/
```

## コーディング規約

- Python 3.8 以上を対象とします。
- `pre-commit` を使用して、コミット前に `ruff` による Lint/Format や型チェック（将来導入予定）が行われるように設定されています。
- コメントやドキュメントは日本語で記載します。
