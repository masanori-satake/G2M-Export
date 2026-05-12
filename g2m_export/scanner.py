import fnmatch
from pathlib import Path
from typing import List, Iterator

def is_binary(file_path: Path) -> bool:
    """ヌルバイトの有無またはデコード失敗により、ファイルがバイナリかどうかを判定する。"""
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(1024)
            if b'\x00' in chunk:
                return True
            # utf-8 としてデコードを試みる
            chunk.decode('utf-8')
            return False
    except UnicodeDecodeError:
        return True
    except Exception:
        return True

def should_ignore(path: Path, root: Path, ignore_patterns: List[str]) -> bool:
    """パターンに基づき、パスを除外すべきかどうかを判定する。"""
    rel_path_obj = path.relative_to(root)
    rel_path = str(rel_path_obj)

    # .git ディレクトリは常に除外
    if ".git" in rel_path_obj.parts:
        return True

    for pattern in ignore_patterns:
        if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(path.name, pattern):
            return True
        # "node_modules/*" のようなディレクトリ固有のパターンをサポート
        if any(fnmatch.fnmatch(part, pattern.rstrip('/')) for part in rel_path_obj.parts):
             return True

    return False

def scan_files(root_dir: Path, ignore_patterns: List[str], binary_extensions: List[str] = None) -> Iterator[Path]:
    """root_dir 内のファイルを再帰的にスキャンし、除外パターンとバイナリチェックでフィルタリングする。"""
    if binary_extensions is None:
        binary_extensions = []

    for path in root_dir.rglob("*"):
        if path.is_file():
            # 拡張子によるバイナリ判定
            if any(path.suffix == ext if ext.startswith('.') else f".{ext}" == path.suffix for ext in binary_extensions):
                continue

            if not should_ignore(path, root_dir, ignore_patterns):
                if not is_binary(path):
                    yield path
