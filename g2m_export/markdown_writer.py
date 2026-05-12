from pathlib import Path
from typing import List
from .git_utils import get_file_remote_url

def generate_markdown(root_dir: Path, files: List[Path], remote_url: str, branch: str) -> str:
    """リストされたファイルから単一の Markdown コンテンツを生成する。"""
    lines = []
    repo_name = root_dir.name
    lines.append(f"# 【Repo】 {repo_name}\n")

    # 出力の一貫性を保つためにファイルをソート
    for file_path in sorted(files):
        rel_path = file_path.relative_to(root_dir)
        depth = len(rel_path.parts)
        heading_level = "#" * (depth + 1)

        lines.append(f"{heading_level} {rel_path}")

        # URLにはPOSIX形式（スラッシュ）を使用
        file_remote_url = get_file_remote_url(remote_url, branch, rel_path.as_posix())
        if file_remote_url:
            lines.append(f"Source URL: [View on Remote]({file_remote_url})")

        lines.append("\n```")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines.append(content)
        except Exception as e:
            lines.append(f"ファイルの読み込みエラー: {e}")
        lines.append("```\n")

    return "\n".join(lines)

def write_to_file(output_path: Path, content: str):
    """生成されたコンテンツを出力ファイルに書き込む。"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
