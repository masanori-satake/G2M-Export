# Spec 命名規則

## ディレクトリ命名

Spec ディレクトリは `.kiro/specs/` 配下に作成し、先頭に4桁のインクリメント番号を付与する。

形式: `{番号}_{feature-name}`

例:
- `0001_user-authentication`
- `0002_file-export-optimization`
- `0003_bitbucket-cloud-support`

## 番号の採番ルール

- 新規作成時は、既存の最大番号 + 1 を使用する
- `.kiro/specs/` 内にまだディレクトリがない場合は `0001` から開始する
- 番号は常に4桁のゼロ埋め（例: `0001`, `0012`, `0100`）
