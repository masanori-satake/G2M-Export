# 既存システム概要

既存コードとドキュメントの実態を整理し、差異や不明点を可視化する。

---

## コードから読み取れる事実

- CLI エントリポイント: `g2m_export/cli.py` の `main()` 関数
- 設定読み込み: `load_config()` で YAML を `yaml.safe_load` で読み込み
- 設定の優先順位: CLI 引数 > 設定ファイル値 > ハードコードのデフォルト
- スキャン: `scanner.py` の `scan_files()` がジェネレータで `Path.rglob("*")` を再帰走査
- バイナリ判定: 拡張子チェック → 先頭1024バイトのヌルバイト/UTF-8デコード失敗
- 除外判定: `fnmatch` によるパターンマッチ（ファイル名・相対パス・パーツ単位）
- Git 情報取得: `.git/config` を正規表現で parse、`.git/HEAD` を直接読み取り
- SSH→HTTPS 変換: `git@` を `https://` に単純置換（`:` を `/` に変換）
- プロバイダ判定: URL 文字列に `github.com`, `gitlab.com`, `bitbucket.org` を含むかで分岐
- Bitbucket Server: `/projects/KEY/repos/NAME` と `/scm/KEY/NAME` の2パターンを認識
- ファイル分割: `max_mb` 超過時に `_{index}` サフィックスで分割出力
- 全体制限: `stop_threshold_mb` 超過見込みでスキャン中断
- 上書き制御: `--overwrite` 時に旧分割ファイル（`_2.md` 等）を事前削除

## ドキュメントからの記述

- AGENTS.md: Bitbucket Cloud 対応は「将来計画」と明記
- AGENTS.md: `Scanner` を「クラス」と記述
- README_DEV.md: `Scanner` クラスとして classDiagram に記載
- README.md: `binary_extensions` 設定については未記載（サンプルにも未記載）
- AGENTS.md: エラーメッセージ構成を「現象・原因・対処方法」と定義

## 差異・不整合

| 項目 | コードの実態 | ドキュメントの記述 | 分類 |
|------|-------------|-------------------|------|
| Scanner の構造 | 関数群（クラスではない） | 「Scanner クラス」と記述 | 差異 |
| `binary_extensions` | コード上で機能する | README/サンプルに記載なし | 差異 |
| `output_dir` 設定 | YAML から `output_dir` キーを読む | README に設定キーとして未記載 | 差異 |
| Bitbucket Cloud | `parse_repo_info` に実装あり | AGENTS.md では「将来計画」 | 差異 |

## 推定される設計意図

- J2M-Export のアーキテクチャを踏襲し、同じ分割・上書きロジックを移植した（推定）
- `git` コマンド非依存はポータビリティ確保のため（推定: CI 環境や git 未インストール環境への配慮）
- プロバイダ別 URL 構築は、出力 Markdown の可読性向上が目的（推定）

## Open Questions

- [ ] `Scanner` はクラス化すべきか、現状の関数群のままで良いか？
- [ ] `binary_extensions` のデフォルト値をコードに持たせるべきか？
- [ ] Bitbucket Cloud 対応は現時点でどの程度動作するか（テスト未確認）
- [ ] SSH URL 変換の `git@host:path` → `https://host/path` は全ケースで正しいか？（ポート指定ありの場合等）
- [ ] `generate_markdown()` 関数が存在するが `cli.py` からは呼ばれていない（レガシー？）
