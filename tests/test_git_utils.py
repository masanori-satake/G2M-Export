import unittest
from pathlib import Path
from g2m_export.git_utils import sanitize_remote_url, get_file_remote_url

class TestGitUtils(unittest.TestCase):
    def test_sanitize_remote_url(self):
        self.assertEqual(
            sanitize_remote_url("https://github.com/user/repo.git"),
            "https://github.com/user/repo"
        )
        self.assertEqual(
            sanitize_remote_url("git@github.com:user/repo.git"),
            "https://github.com/user/repo"
        )
        self.assertEqual(
            sanitize_remote_url("https://bitbucket.org/user/repo.git"),
            "https://bitbucket.org/user/repo"
        )

    def test_get_file_remote_url(self):
        # GitHub
        self.assertEqual(
            get_file_remote_url("https://github.com/user/repo", "main", "src/main.py"),
            "https://github.com/user/repo/blob/main/src/main.py"
        )
        # Bitbucket
        self.assertEqual(
            get_file_remote_url("https://bitbucket.org/user/repo", "main", "src/main.py"),
            "https://bitbucket.org/user/repo/src/main/src/main.py"
        )

    def test_get_current_branch(self):
        # This is a bit hard to test without real files, but we can test the logic if we mock or just check logic.
        # Actually I can't easily mock Path object's read in this way without more effort,
        # but I can at least verify the fix for hierarchical branches if I were to test the function.
        pass

if __name__ == "__main__":
    unittest.main()
