import fnmatch
from pathlib import Path
from typing import List, Iterator

def is_binary(file_path: Path) -> bool:
    """Detect if a file is binary by checking for null bytes or decoding failure."""
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(1024)
            if b'\x00' in chunk:
                return True
            # Try decoding as utf-8
            chunk.decode('utf-8')
            return False
    except UnicodeDecodeError:
        return True
    except Exception:
        return True

def should_ignore(path: Path, root: Path, ignore_patterns: List[str]) -> bool:
    """Check if the path should be ignored based on patterns."""
    rel_path = str(path.relative_to(root))

    # Always ignore .git directory
    if ".git" in path.parts:
        return True

    for pattern in ignore_patterns:
        if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(path.name, pattern):
            return True
        # Support directory-specific patterns like "node_modules/*"
        if any(fnmatch.fnmatch(part, pattern.rstrip('/')) for part in path.parts):
             return True

    return False

def scan_files(root_dir: Path, ignore_patterns: List[str]) -> Iterator[Path]:
    """Recursively scan files in root_dir, filtering by ignore_patterns and binary check."""
    for path in root_dir.rglob("*"):
        if path.is_file():
            if not should_ignore(path, root_dir, ignore_patterns):
                if not is_binary(path):
                    yield path
