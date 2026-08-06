# 技術スタック

## 言語・ランタイム

- Python 3.8 以上
- 外部依存: `pyyaml` のみ

## パッケージ管理

- `pip` によるパッケージ管理
- `requirements.txt`: ランタイム依存
- `requirements-dev.txt`: 開発用依存（pytest）

## テスト

- フレームワーク: pytest
- 実行コマンド（Linux/Mac）:

  ```bash
  PYTHONPATH=. python -m pytest tests/
  ```

- 実行コマンド（Windows）:

  ```cmd
  set PYTHONPATH=. && python -m pytest tests/
  ```

## コード品質

- リンター/フォーマッター: Ruff（`ruff --fix` + `ruff-format`）
- pre-commit フック: trailing-whitespace, end-of-file-fixer, check-yaml, check-added-large-files, ruff
- CI: `.pre-commit-ci.yml` による自動チェック

## 実行方法

```bash
python -m g2m_export.cli [src_dir] [--config パス] [--output パス] [--output-dir ディレクトリ] [--max-mb 数値] [--stop-threshold-mb 数値] [--overwrite]
```

## 環境セットアップ

```bash
pip install -r requirements.txt -r requirements-dev.txt
pre-commit install
```
