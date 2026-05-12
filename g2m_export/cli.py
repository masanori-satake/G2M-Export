import argparse
import yaml
from pathlib import Path
from .git_utils import get_git_root, get_remote_url, get_current_branch
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
    parser = argparse.ArgumentParser(description="G2M-Export: Gitリポジトリを単一のMarkdownファイルにエクスポートします。")
    parser.add_argument("src_dir", nargs="?", default=".", help="スキャン対象のディレクトリ (既定: カレントディレクトリ)")
    parser.add_argument("--config", default=".g2m_export.yaml", help="設定ファイルのパス")
    parser.add_argument("--output", help="出力するMarkdownファイルのパス")

    args = parser.parse_args()

    src_dir = Path(args.src_dir).resolve()

    # 指定された設定パスを試すか、src_dir 内の既定ファイルを探す
    config_path = Path(args.config)
    if not config_path.exists() and args.config == ".g2m_export.yaml":
        config_path = src_dir / ".g2m_export.yaml"

    config = load_config(config_path)
    ignore_patterns = config.get("ignore_patterns", [])
    binary_extensions = config.get("binary_extensions", [])

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
    else:
        output_path = Path(f"【Repo】 {src_dir.name}.md")

    write_to_file(output_path, markdown_content)
    print(f"{output_path} にエクスポートされました。")

if __name__ == "__main__":
    main()
