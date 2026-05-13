import argparse
import yaml
from pathlib import Path
from .git_utils import (
    get_git_root,
    get_remote_url,
    get_current_branch,
    parse_repo_info,
)
from .scanner import scan_files
from .markdown_writer import generate_markdown, write_to_file


def load_config(config_path: Path):
    """設定ファイルを読み込む。"""
    if config_path.exists():
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
            return config if config is not None else {}
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
        "--config", default=".g2m_export.yaml", help="設定ファイルのパス"
    )
    parser.add_argument("--output", help="出力するMarkdownファイルのパス")
    parser.add_argument("--output-dir", help="出力先のディレクトリ")

    args = parser.parse_args()

    src_dir = Path(args.src_dir).resolve()

    # 指定された設定パスを試すか、src_dir 内の既定ファイルを探す
    config_path = Path(args.config)
    if not config_path.exists() and args.config == ".g2m_export.yaml":
        config_path = src_dir / ".g2m_export.yaml"

    config = load_config(config_path)
    ignore_patterns = config.get("ignore_patterns", [])
    binary_extensions = config.get("binary_extensions", [])
    output_dir_config = config.get("output_dir", "output")

    # 出力ディレクトリの決定
    output_dir = Path(args.output_dir or output_dir_config)
    if not output_dir.is_absolute():
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
            # 相対パスの場合は output_dir を基準とする
            output_path = output_dir / output_path
    else:
        # デフォルトファイル名の決定
        if git_root:
            proj_key, repo_name = parse_repo_info(remote_url)
            if not repo_name:
                repo_name = git_root.name

            if proj_key:
                filename = f"【Repo】 {proj_key}_{repo_name}.md"
            else:
                filename = f"【Repo】 {repo_name}.md"
        else:
            filename = f"【Dir】 {src_dir.name}.md"

        output_path = output_dir / filename

    # 出力ディレクトリの作成
    output_path.parent.mkdir(parents=True, exist_ok=True)

    write_to_file(output_path, markdown_content)
    print(f"{output_path} にエクスポートされました。")


if __name__ == "__main__":
    main()
