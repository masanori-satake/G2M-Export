from pathlib import Path

from .git_utils import get_file_remote_url


def generate_header(repo_name: str) -> str:
    """リポジトリ名を含む Markdown ヘッダーを生成する。"""
    return f"# 【Repo】 {repo_name}\n"


def generate_file_section(
    root_dir: Path, file_path: Path, remote_url: str, branch: str
) -> str:
    """1つのファイルに対する Markdown セクションを生成する。"""
    lines = []
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
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            lines.append(content)
    except OSError as e:
        lines.append(
            f"ファイルの読み込みに失敗しました（現象）。ファイルが途中で削除されたか、権限がない可能性があります（対処方法）。詳細: {e}（原因）"
        )
    lines.append("```\n")

    return "\n".join(lines)


def generate_markdown(
    root_dir: Path, files: list[Path], remote_url: str, branch: str
) -> str:
    """スキャンされたファイル群の内容を統合し、単一の Markdown 文字列を生成する。"""
    sections = []
    repo_name = root_dir.name
    sections.append(generate_header(repo_name))

    # ファイルパス順にソートすることで、ディレクトリ構造が整理された状態で出力される
    for file_path in sorted(files):
        sections.append(generate_file_section(root_dir, file_path, remote_url, branch))

    return "\n".join(sections)


def write_to_file(output_path: Path, content: str):
    """生成された Markdown 文字列を指定されたパスに保存する。"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
