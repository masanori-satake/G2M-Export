import re
from pathlib import Path

def get_git_root(start_path: Path) -> Path:
    """Find the .git directory by walking up from start_path."""
    curr = start_path.resolve()
    while curr != curr.parent:
        if (curr / ".git").is_dir():
            return curr
        curr = curr.parent
    return None

def get_remote_url(git_root: Path) -> str:
    """Read .git/config to find the origin remote URL."""
    config_path = git_root / ".git" / "config"
    if not config_path.exists():
        return None

    with open(config_path, "r") as f:
        content = f.read()

    # Simple regex to find [remote "origin"] url
    # [remote "origin"]
    #     url = ...
    match = re.search(r'\[remote "origin"\][^\[]*url\s*=\s*(\S+)', content, re.MULTILINE)
    if match:
        url = match.group(1)
        return url
    return None

def get_current_branch(git_root: Path) -> str:
    """Read .git/HEAD to find the current branch."""
    head_path = git_root / ".git" / "HEAD"
    if not head_path.exists():
        return None

    with open(head_path, "r") as f:
        content = f.read().strip()

    if content.startswith("ref: "):
        # e.g., "ref: refs/heads/feature/login" -> "feature/login"
        return content[len("ref: refs/heads/"):].strip()
    return content  # Might be a hash

def sanitize_remote_url(url: str) -> str:
    """Convert SSH URL to HTTPS and remove .git suffix."""
    if not url:
        return ""

    # SSH: git@github.com:user/repo.git -> https://github.com/user/repo
    if url.startswith("git@"):
        url = url.replace(":", "/").replace("git@", "https://")

    if url.endswith(".git"):
        url = url[:-4]

    return url

def get_file_remote_url(remote_url: str, branch: str, relative_path: str) -> str:
    """Generate the URL for a file on the remote repository."""
    if not remote_url or not branch:
        return ""

    base_url = sanitize_remote_url(remote_url)

    # Support GitHub, GitLab, Bitbucket
    if "github.com" in base_url or "gitlab.com" in base_url:
        return f"{base_url}/blob/{branch}/{relative_path}"
    elif "bitbucket.org" in base_url:
        return f"{base_url}/src/{branch}/{relative_path}"
    else:
        # Default to GitHub-like format
        return f"{base_url}/blob/{branch}/{relative_path}"
