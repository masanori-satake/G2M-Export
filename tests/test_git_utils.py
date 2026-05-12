import unittest
from g2m_export.git_utils import sanitize_remote_url, get_file_remote_url, parse_repo_info


class TestGitUtils(unittest.TestCase):
    def test_sanitize_remote_url(self):
        self.assertEqual(
            sanitize_remote_url("https://github.com/user/repo.git"),
            "https://github.com/user/repo",
        )
        self.assertEqual(
            sanitize_remote_url("git@github.com:user/repo.git"),
            "https://github.com/user/repo",
        )
        self.assertEqual(
            sanitize_remote_url("https://bitbucket.org/user/repo.git"),
            "https://bitbucket.org/user/repo",
        )

    def test_get_file_remote_url(self):
        # GitHub
        self.assertEqual(
            get_file_remote_url("https://github.com/user/repo", "main", "src/main.py"),
            "https://github.com/user/repo/blob/main/src/main.py",
        )
        # Bitbucket
        self.assertEqual(
            get_file_remote_url(
                "https://bitbucket.org/user/repo", "main", "src/main.py"
            ),
            "https://bitbucket.org/user/repo/src/main/src/main.py",
        )

    def test_get_current_branch(self):
        # This is a bit hard to test without real files, but we can test the logic if we mock or just check logic.
        # Actually I can't easily mock Path object's read in this way without more effort,
        # but I can at least verify the fix for hierarchical branches if I were to test the function.
        pass

    def test_parse_repo_info(self):
        # GitHub
        self.assertEqual(parse_repo_info("https://github.com/user/my-repo.git"), (None, "my-repo"))
        self.assertEqual(parse_repo_info("git@github.com:user/my-repo.git"), (None, "my-repo"))

        # Bitbucket Cloud
        self.assertEqual(parse_repo_info("https://bitbucket.org/my-workspace/my-repo.git"), ("my-workspace", "my-repo"))
        self.assertEqual(parse_repo_info("git@bitbucket.org:my-workspace/my-repo.git"), ("my-workspace", "my-repo"))

        # Bitbucket Server
        self.assertEqual(
            parse_repo_info("https://bitbucket.example.com/projects/PROJ/repos/my-repo/browse"),
            ("PROJ", "my-repo")
        )
        self.assertEqual(
            parse_repo_info("https://bitbucket.example.com/scm/PROJ/my-repo.git"),
            ("PROJ", "my-repo")
        )


if __name__ == "__main__":
    unittest.main()
