import argparse
import sys
import yaml
from datetime import datetime
from pathlib import Path
from .git_utils import (
    get_git_root,
    get_remote_url,
    get_current_branch,
    parse_repo_info,
)
from .scanner import scan_files
from .markdown_writer import generate_markdown, write_to_file


def load_config(config_path: Path) -> dict:
    """指定されたパスからYAML形式の設定ファイルを読み込む。

    ファイルが存在しない、または内容が空の場合は空の辞書を返す。
    読み込みに失敗した場合は、エラーメッセージを表示し空の辞書を返す。
    """
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                return config if config is not None else {}
        except yaml.YAMLError as e:
            print(
                f"設定ファイルの解析に失敗しました（現象）。{config_path} の内容が正しいYAML形式か確認してください（対処方法）。詳細: {e}（原因）"
            )
            return {}
        except OSError as e:
            print(
                f"設定ファイルの読み込みに失敗しました（現象）。{config_path} のアクセス権限などを確認してください（対処方法）。詳細: {e}（原因）"
            )
            return {}
    return {}


def main():
    parser = argparse.ArgumentParser(
        description="G2M-Export: Gitリポジトリを単一のMarkdownファイルにエクスポートします。"
    )
    parser.add_argument(
        "src_dir",
        nargs="?",
        default=".",
        help="スキャン対象のディレクトリ (既定: カレントディレクトリ)",
    )
    parser.add_argument(
        "--config", default="g2m_config.yaml", help="設定ファイルのパス"
    )
    parser.add_argument("--output", help="出力するMarkdownファイルのパス")
    parser.add_argument("--output-dir", help="出力先のディレクトリ")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=None,
        help="既存の出力ファイルを上書きする",
    )
    parser.add_argument(
        "--no-overwrite",
        action="store_false",
        dest="overwrite",
        help="既存の出力ファイルを上書きしない (既定)",
    )

    args = parser.parse_args()

    # 実行時点のタイムスタンプを取得 (Suffix用)
    now = datetime.now()
    suffix = now.strftime("_%y%m%d_%H%M%S")

    src_dir = Path(args.src_dir).resolve()

    config_path = Path(args.config)
    # 明示的に指定されていない場合、スキャン対象ディレクトリ直下の設定ファイルを優先的に探す
    if args.config == "g2m_config.yaml":
        src_config = src_dir / "g2m_config.yaml"
        if src_config.exists():
            config_path = src_config

    config = load_config(config_path)
    ignore_patterns = config.get("ignore_patterns", [])
    binary_extensions = config.get("binary_extensions", [])
    output_dir_config = config.get("output_dir", "output")
    overwrite_config = config.get("overwrite", False)

    # 上書き設定の優先順位: コマンドライン引数 > 設定ファイル > デフォルト(False)
    overwrite = overwrite_config
    if args.overwrite is not None:
        overwrite = args.overwrite

    output_dir = Path(args.output_dir or output_dir_config)
    if not output_dir.is_absolute():
        # 出力ディレクトリが相対パスで指定された場合、カレントディレクトリを基準に解決する
        output_dir = Path.cwd() / output_dir

    git_root = get_git_root(src_dir)
    remote_url = ""
    branch = ""
    if git_root:
        remote_url = get_remote_url(git_root)
        branch = get_current_branch(git_root)

    print(f"{src_dir} をスキャン中...")
    files = list(scan_files(src_dir, ignore_patterns, binary_extensions))
    print(f"{len(files)} 個のファイルが見つかりました。")

    markdown_content = generate_markdown(src_dir, files, remote_url, branch)

    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = output_dir / output_path
    else:
        # 出力先が指定されていない場合、Gitリポジトリ名やディレクトリ名に基づいたファイル名を自動生成する
        if git_root:
            proj_key, repo_name = parse_repo_info(remote_url)
            if not repo_name:
                repo_name = git_root.name

            if proj_key:
                base_name = f"【Repo】 {proj_key}_{repo_name}"
            else:
                base_name = f"【Repo】 {repo_name}"
        else:
            base_name = f"【Dir】 {src_dir.name}"

        if not overwrite:
            filename = f"{base_name}{suffix}.md"
        else:
            filename = f"{base_name}.md"

        output_path = output_dir / filename

    # 上書き不許可時にファイルが既に存在する場合、エラーとする
    if not overwrite and output_path.exists():
        print(
            f"出力ファイルが既に存在します（現象）。既存のファイルを移動するか、--overwrite オプションを指定してください（対処方法）。詳細: {output_path} が既に存在します（原因）"
        )
        sys.exit(1)

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        write_to_file(output_path, markdown_content)
        print(f"{output_path} にエクスポートされました。")
    except OSError as e:
        print(
            f"ファイルの書き出しに失敗しました（現象）。出力先ディレクトリの権限やディスク容量を確認してください（対処方法）。詳細: {e}（原因）"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
