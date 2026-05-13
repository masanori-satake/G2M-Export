from pathlib import Path
from typing import List
from .git_utils import get_file_remote_url


def generate_markdown(
    root_dir: Path, files: List[Path], remote_url: str, branch: str
) -> str:
    """スキャンされたファイル群の内容を統合し、単一の Markdown 文字列を生成する。"""
    lines = []
    repo_name = root_dir.name
    lines.append(f"# 【Repo】 {repo_name}\n")

    # ファイルパス順にソートすることで、ディレクトリ構造が整理された状態で出力される
    for file_path in sorted(files):
        rel_path = file_path.relative_to(root_dir)
        # ディレクトリの深さに応じて見出しレベル（#の数）を動的に調整する
        depth = len(rel_path.parts)
        heading_level = "#" * (depth + 1)

        lines.append(f"{heading_level} {rel_path.as_posix()}")

        # リモートURLが存在する場合、該当ファイルへの直リンクを挿入する
        file_remote_url = get_file_remote_url(remote_url, branch, rel_path.as_posix())
        if file_remote_url:
            lines.append(f"Source URL: [View on Remote]({file_remote_url})")

        lines.append("\n```")
        try:
            # UTF-8 での読み込みを試みる。Scanner でのチェックを通過している前提
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines.append(content)
        except Exception as e:
            lines.append(f"ファイルの読み込みエラー: {e}")
        lines.append("```\n")

    return "\n".join(lines)


def write_to_file(output_path: Path, content: str):
    """生成された Markdown 文字列を指定されたパスに保存する。"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
