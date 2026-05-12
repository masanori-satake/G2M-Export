import argparse
import yaml
from pathlib import Path
from .git_utils import get_git_root, get_remote_url, get_current_branch
from .scanner import scan_files
from .markdown_writer import generate_markdown, write_to_file

def load_config(config_path: Path):
    if config_path.exists():
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
            return config if config is not None else {}
    return {}

def main():
    parser = argparse.ArgumentParser(description="G2M-Export: Export Git repository to a single Markdown file.")
    parser.add_argument("src_dir", nargs="?", default=".", help="Source directory to scan (default: current directory)")
    parser.add_argument("--config", default=".g2m_export.yaml", help="Path to config file")
    parser.add_argument("--output", help="Output Markdown file path")

    args = parser.parse_args()

    src_dir = Path(args.src_dir).resolve()

    # Try specified config path, or look for default in src_dir
    config_path = Path(args.config)
    if not config_path.exists() and args.config == ".g2m_export.yaml":
        config_path = src_dir / ".g2m_export.yaml"

    config = load_config(config_path)
    ignore_patterns = config.get("ignore_patterns", [])

    git_root = get_git_root(src_dir)
    remote_url = ""
    branch = ""
    if git_root:
        remote_url = get_remote_url(git_root)
        branch = get_current_branch(git_root)

    print(f"Scanning {src_dir}...")
    files = list(scan_files(src_dir, ignore_patterns))
    print(f"Found {len(files)} files.")

    markdown_content = generate_markdown(src_dir, files, remote_url, branch)

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = Path(f"【Repo】 {src_dir.name}.md")

    write_to_file(output_path, markdown_content)
    print(f"Exported to {output_path}")

if __name__ == "__main__":
    main()
