import re
from pathlib import Path


def get_git_root(start_path: Path) -> Path:
    """指定されたパスから親ディレクトリに向かって探索し、Gitリポジトリのルート（.gitが存在する場所）を特定する。"""
    curr = start_path.resolve()
    while curr != curr.parent:
        if (curr / ".git").is_dir():
            return curr
        curr = curr.parent
    return None


def get_remote_url(git_root: Path) -> str:
    """gitコマンドを使用せずに .git/config から直接 origin リモートのURLを取得する。"""
    config_path = git_root / ".git" / "config"
    if not config_path.exists():
        return None

    with open(config_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # セクション [remote "origin"] 内の url 属性を探す
    match = re.search(
        r'\[remote\s+"?origin"?\][^\[]*url\s*=\s*(\S+)', content, re.MULTILINE
    )
    if match:
        url = match.group(1)
        return url
    return None


def get_current_branch(git_root: Path) -> str:
    """gitコマンドを使用せずに .git/HEAD から現在のブランチ名を取得する。"""
    head_path = git_root / ".git" / "HEAD"
    if not head_path.exists():
        return None

    with open(head_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read().strip()

    if content.startswith("ref: "):
        # 'ref: refs/heads/master' 形式からブランチ名のみを取り出す
        ref_prefix = "refs/heads/"
        if ref_prefix in content:
            return content[content.find(ref_prefix) + len(ref_prefix) :].strip()
        return content[len("ref: ") :].strip()
    # デタッチドHEAD状態などの場合はコミットハッシュが直接書かれている
    return content


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
    """リモートリポジトリ（GitHub/Bitbucket等）のWebビューでファイルを表示するためのURLを構築する。"""
    if not remote_url or not branch:
        return ""

    base_url = sanitize_remote_url(remote_url)

    # プロバイダーごとのパス形式の違いを吸収する
    if "github.com" in base_url or "gitlab.com" in base_url:
        return f"{base_url}/blob/{branch}/{relative_path}"
    elif "bitbucket.org" in base_url:
        return f"{base_url}/src/{branch}/{relative_path}"
    else:
        # 未知のプロバイダーについては、GitHubに多い blob 形式をデフォルトとする
        return f"{base_url}/blob/{branch}/{relative_path}"


def parse_repo_info(url: str):
    """リモートURLから、命名に使用するプロジェクト名（キー）とリポジトリ名を抽出する。"""
    if not url:
        return None, None

    # 末尾のスラッシュを削除し、.git サフィックスを除去
    url = url.rstrip("/")
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
