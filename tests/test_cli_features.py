import pytest
import shutil
import tempfile
from pathlib import Path
from g2m_export.cli import main
import sys
from unittest.mock import patch


@pytest.fixture
def temp_dir():
    d = tempfile.mkdtemp()
    yield Path(d)
    shutil.rmtree(d)


def test_cli_splitting(temp_dir, capsys):
    src = temp_dir / "src"
    src.mkdir()
    # Create multiple files to trigger splitting
    # Each file will be around 0.5MB, and we set max-mb to 0.1 to force split
    content = "A" * (1024 * 512)  # 0.5MB
    (src / "file1.txt").write_text(content)
    (src / "file2.txt").write_text(content)

    output_dir = temp_dir / "output"

    # Mock sys.argv
    test_args = [
        "g2m_export.cli",
        str(src),
        "--output-dir",
        str(output_dir),
        "--max-mb",
        "0.1",
        "--overwrite",
    ]

    with patch.object(sys, "argv", test_args):
        main()

    # Check if two files are created
    # base name will be 【Dir】 src.md
    out_files = list(output_dir.glob("*.md"))
    filenames = [f.name for f in out_files]
    assert "【Dir】 src.md" in filenames
    assert "【Dir】 src_2.md" in filenames
    assert len(out_files) == 2


def test_cli_stop_threshold(temp_dir, capsys):
    src = temp_dir / "src"
    src.mkdir()
    content = "A" * (1024 * 512)  # 0.5MB
    (src / "file1.txt").write_text(content)
    (src / "file2.txt").write_text(content)
    (src / "file3.txt").write_text(content)

    output_dir = temp_dir / "output"

    # Set stop-threshold-mb to 0.7MB.
    # file1 (0.5) + header < 0.7 (OK)
    # file2 (0.5) -> total (1.0+) > 0.7 (STOP)
    test_args = [
        "g2m_export.cli",
        str(src),
        "--output-dir",
        str(output_dir),
        "--stop-threshold-mb",
        "0.7",
        "--overwrite",
    ]

    with patch.object(sys, "argv", test_args):
        main()

    out_files = list(output_dir.glob("*.md"))
    # Only the first file should be fully processed and written
    assert len(out_files) == 1

    captured = capsys.readouterr()
    assert (
        "全体サイズ制限 (0.7 MB) を超えるため、スキャンを中断します。" in captured.out
    )


def test_cli_overwrite_with_suffix(temp_dir):
    src = temp_dir / "src"
    src.mkdir()
    (src / "file1.txt").write_text("hello")

    output_dir = temp_dir / "output"
    output_dir.mkdir()

    # Pre-create a file that would match the base name
    (output_dir / "【Dir】 src.md").write_text("existing")

    # Run WITHOUT overwrite. Should create a file with timestamp suffix.
    test_args = [
        "g2m_export.cli",
        str(src),
        "--output-dir",
        str(output_dir),
        "--no-overwrite",
    ]

    with patch.object(sys, "argv", test_args):
        main()

    out_files = list(output_dir.glob("*.md"))
    # Should have the original and the new one with suffix
    assert len(out_files) == 2
    filenames = [f.name for f in out_files]
    assert any("_" in f for f in filenames if f != "【Dir】 src.md")


def test_cli_overwrite_enabled(temp_dir):
    src = temp_dir / "src"
    src.mkdir()
    (src / "file1.txt").write_text("hello")

    output_dir = temp_dir / "output"
    output_dir.mkdir()

    existing_file = output_dir / "【Dir】 src.md"
    existing_file.write_text("existing")

    # Run WITH overwrite.
    test_args = [
        "g2m_export.cli",
        str(src),
        "--output-dir",
        str(output_dir),
        "--overwrite",
    ]

    with patch.object(sys, "argv", test_args):
        main()

    out_files = list(output_dir.glob("*.md"))
    assert len(out_files) == 1
    assert existing_file.read_text() != "existing"
    assert "hello" in existing_file.read_text()
