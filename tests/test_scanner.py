import unittest
from pathlib import Path
import tempfile
import shutil
from g2m_export.scanner import should_ignore, is_binary


class TestScanner(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_should_ignore(self):
        root = self.test_dir
        ignore_patterns = ["*.log", "node_modules/"]

        # Test basic pattern
        path1 = root / "test.log"
        self.assertTrue(should_ignore(path1, root, ignore_patterns))

        # Test no ignore
        path2 = root / "test.txt"
        self.assertFalse(should_ignore(path2, root, ignore_patterns))

        # Test directory pattern
        path3 = root / "node_modules" / "pkg" / "index.js"
        self.assertTrue(should_ignore(path3, root, ignore_patterns))

        # Test .git ignore
        path4 = root / ".git" / "config"
        self.assertTrue(should_ignore(path4, root, ignore_patterns))

    def test_is_binary(self):
        root = self.test_dir

        # Text file
        txt_file = root / "test.txt"
        with open(txt_file, "w", encoding="utf-8") as f:
            f.write("Hello World")
        self.assertFalse(is_binary(txt_file))

        # Binary file
        bin_file = root / "test.bin"
        with open(bin_file, "wb") as f:
            f.write(b"\x00\x01\x02")
        self.assertTrue(is_binary(bin_file))


if __name__ == "__main__":
    unittest.main()
