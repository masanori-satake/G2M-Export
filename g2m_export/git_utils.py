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

    # [remote "origin"] の url を抽出する正規表現（引用符の有無に対応）
    match = re.search(
        r'\[remote\s+"?origin"?\][^\[]*url\s*=\s*(\S+)', content, re.MULTILINE
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
        # refs/heads/ 以降を抽出
        ref_prefix = "refs/heads/"
        if ref_prefix in content:
            return content[content.find(ref_prefix) + len(ref_prefix) :].strip()
        # refs/heads/ が含まれない場合は ref: 以降をそのまま返す
        return content[len("ref: ") :].strip()
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


def parse_repo_info(url: str):
    """リモートURLからプロジェクトキーとリポジトリ名を取得する。"""
    if not url:
        return None, None

    # .git サフィックスを除去
    if url.endswith(".git"):
        url = url[:-4]

    # Bitbucket Server (projects/KEY/repos/NAME)
    match = re.search(r"/projects/([^/]+)/repos/([^/]+)", url)
    if match:
        return match.group(1), match.group(2)

    # Bitbucket Server (scm/KEY/NAME)
    match = re.search(r"/scm/([^/]+)/([^/]+)", url)
    if match:
        return match.group(1), match.group(2)

    # Bitbucket Cloud (bitbucket.org/WORKSPACE/REPO)
    if "bitbucket.org" in url:
        # プロトコルとホストを除去
        path = re.sub(r"^.*bitbucket\.org[:/]", "", url)
        parts = path.strip("/").split("/")
        if len(parts) >= 2:
            return parts[0], parts[1]

    # GitHub or others: 最後のスラッシュ以降をリポジトリ名とする
    # git@github.com:user/repo -> repo
    # https://github.com/user/repo -> repo
    repo_name = url.split("/")[-1].split(":")[-1]
    return None, repo_name
