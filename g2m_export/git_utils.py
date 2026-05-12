import re
from pathlib import Path


def get_git_root(start_path: Path) -> Path:
    """開始パスから親ディレクトリへ遡り、.gitディレクトリを探す。"""
    curr = start_path.resolve()
    while curr != curr.parent:
        if (curr / ".git").is_dir():
            return curr
        curr = curr.parent
    return None


def get_remote_url(git_root: Path) -> str:
    """.git/config を読み取り、origin リモートのURLを取得する。"""
    config_path = git_root / ".git" / "config"
    if not config_path.exists():
        return None

    with open(config_path, "r") as f:
        content = f.read()

    # [remote "origin"] の url を抽出する正規表現
    match = re.search(
        r'\[remote "origin"\][^\[]*url\s*=\s*(\S+)', content, re.MULTILINE
    )
    if match:
        url = match.group(1)
        return url
    return None


def get_current_branch(git_root: Path) -> str:
    """.git/HEAD を読み取り、現在のブランチ名を取得する。"""
    head_path = git_root / ".git" / "HEAD"
    if not head_path.exists():
        return None

    with open(head_path, "r") as f:
        content = f.read().strip()

    if content.startswith("ref: "):
        # 例: "ref: refs/heads/feature/login" -> "feature/login"
        return content[len("ref: refs/heads/") :].strip()
    return content  # ハッシュ値の場合がある


def sanitize_remote_url(url: str) -> str:
    """SSH形式のURLをHTTPS形式に変換し、.gitサフィックスを削除する。"""
    if not url:
        return ""

    # SSH: git@github.com:user/repo.git -> https://github.com/user/repo
    if url.startswith("git@"):
        url = url.replace(":", "/").replace("git@", "https://")

    if url.endswith(".git"):
        url = url[:-4]

    return url


def get_file_remote_url(remote_url: str, branch: str, relative_path: str) -> str:
    """リモートリポジトリ上のファイルのURLを生成する。"""
    if not remote_url or not branch:
        return ""

    base_url = sanitize_remote_url(remote_url)

    # GitHub, GitLab, Bitbucket のサポート
    if "github.com" in base_url or "gitlab.com" in base_url:
        return f"{base_url}/blob/{branch}/{relative_path}"
    elif "bitbucket.org" in base_url:
        return f"{base_url}/src/{branch}/{relative_path}"
    else:
        # デフォルトは GitHub ライクな形式
        return f"{base_url}/blob/{branch}/{relative_path}"
