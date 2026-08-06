# 用語集（Glossary）

プロジェクトで使用する用語を統一するための定義集。

---

## 業務用語

| 用語 | 定義 | 出典 |
|------|------|------|
| 1ファイル統合 Markdown | リポジトリ全体を1つの Markdown に統合した出力物 | README |
| スキャン | 対象ディレクトリ内のファイルを再帰的に列挙する処理 | コード・README |
| エクスポート | スキャン結果を Markdown ファイルとして書き出す処理 | README |
| 除外パターン | `ignore_patterns` で指定する、スキャン対象外のファイルパターン | コード・設定ファイル |

## 技術用語

| 用語 | 定義 | 出典 |
|------|------|------|
| Git ルート | `.git` ディレクトリが存在する最も近い祖先ディレクトリ | コード (`get_git_root`) |
| リモート URL | `.git/config` 内の `[remote "origin"]` セクションの `url` 値 | コード (`get_remote_url`) |
| プロジェクトキー | Bitbucket Server の `/projects/KEY/repos/NAME` 形式から抽出されるキー | コード (`parse_repo_info`) |
| バイナリ判定 | 拡張子チェック + 内容ベース（ヌルバイト/UTF-8デコード失敗）の二段階判定 | コード (`is_binary`) |
| 分割出力 | `max_mb` を超えた場合に `_2.md`, `_3.md` と番号付きで分割する仕組み | コード (`flush_content`) |
| Suffix | 上書き禁止時にファイル名末尾に付与されるタイムスタンプ（例: `_260503_160502`） | コード・README |

## プロバイダ関連

| 用語 | 定義 | 備考 |
|------|------|------|
| Bitbucket Server (Data Center) | `/projects/KEY/repos/NAME` または `/scm/KEY/NAME` 形式の URL を持つ | 現在の主対象 |
| Bitbucket Cloud | `bitbucket.org/WORKSPACE/REPO` 形式 | コードに実装あり、ドキュメントでは将来計画（不整合） |
| GitHub | `github.com/USER/REPO` 形式、`/blob/BRANCH/PATH` で Web ビュー | 対応済み |
| GitLab | `gitlab.com/USER/REPO` 形式、`/blob/BRANCH/PATH` で Web ビュー | 対応済み |

## Spec 関連用語

| 用語 | 定義 |
|------|------|
| Requirements | 「何を実現するか」を定義するフェーズ／ドキュメント |
| Design | 「どう実現するか」を定義するフェーズ／ドキュメント |
| Tasks | 実装タスクの一覧と順序を定義するフェーズ／ドキュメント |
| Open Questions | 未確定・曖昧な事項のリスト。無理に確定させず記録する |
| Correctness Properties | ソフトウェアが満たすべき正しさの性質（PBT で検証） |
