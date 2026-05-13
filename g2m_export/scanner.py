import fnmatch
from pathlib import Path
from typing import List, Iterator


def is_binary(file_path: Path) -> bool:
    """ファイルの内容を確認し、テキストファイルかバイナリファイルかを判定する。

    先頭1024バイトにヌルバイトが含まれているか、UTF-8としてデコードできない場合はバイナリとみなす。
    """
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(1024)
            if b"\x00" in chunk:
                return True
            chunk.decode("utf-8")
            return False
    except UnicodeDecodeError:
        return True
    except Exception:
        return True


def should_ignore(path: Path, root: Path, ignore_patterns: List[str]) -> bool:
    """設定された除外パターンに基づき、対象パスを処理から外すべきか判定する。"""
    rel_path_obj = path.relative_to(root)
    rel_path = str(rel_path_obj)

    # Gitの内部管理ディレクトリは常に除外対象とする
    if ".git" in rel_path_obj.parts:
        return True

    for pattern in ignore_patterns:
        # ファイル名単体、またはルートからの相対パスでパターンマッチングを行う
        if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(path.name, pattern):
            return True
        # ディレクトリ構造のいずれかのパーツがパターンに合致する場合も除外（例: node_modules）
        if any(
            fnmatch.fnmatch(part, pattern.rstrip("/")) for part in rel_path_obj.parts
        ):
            return True

    return False


def scan_files(
    root_dir: Path, ignore_patterns: List[str], binary_extensions: List[str] = None
) -> Iterator[Path]:
    """指定されたディレクトリを再帰的に走査し、有効なテキストファイルのみを列挙する。"""
    if binary_extensions is None:
        binary_extensions = []

    for path in root_dir.rglob("*"):
        if path.is_file():
            # 拡張子によるバイナリ判定
            if any(
                path.suffix == ext if ext.startswith(".") else f".{ext}" == path.suffix
                for ext in binary_extensions
            ):
                continue

            if not should_ignore(path, root_dir, ignore_patterns):
                if not is_binary(path):
                    yield path
