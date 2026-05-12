from pathlib import Path
from typing import List
from .git_utils import get_file_remote_url

def generate_markdown(root_dir: Path, files: List[Path], remote_url: str, branch: str) -> str:
    """Generate a single Markdown content from listed files."""
    lines = []
    repo_name = root_dir.name
    lines.append(f"# 【Repo】 {repo_name}\n")

    # Sort files to ensure consistent output
    for file_path in sorted(files):
        rel_path = file_path.relative_to(root_dir)
        depth = len(rel_path.parts)
        heading_level = "#" * (depth + 1)

        lines.append(f"{heading_level} {rel_path}")

        file_remote_url = get_file_remote_url(remote_url, branch, str(rel_path))
        if file_remote_url:
            lines.append(f"Source URL: [View on Remote]({file_remote_url})")

        lines.append("\n```")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines.append(content)
        except Exception as e:
            lines.append(f"Error reading file: {e}")
        lines.append("```\n")

    return "\n".join(lines)

def write_to_file(output_path: Path, content: str):
    """Write the generated content to the output file."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
