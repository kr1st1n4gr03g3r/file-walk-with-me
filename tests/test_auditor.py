import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.auditor import scan_directory, get_depth, get_status


def test_scan_directory():
    """Test that scan_directory finds files correctly."""

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        Path(tmpdir, "test1.txt").write_text("hello")
        Path(tmpdir, "test2.pdf").write_text("world")

        # Create subdirectory with file
        subdir = Path(tmpdir, "subdir")
        subdir.mkdir()
        Path(subdir, "test3.csv").write_text("data")

        # Scan the directory
        files = scan_directory(tmpdir)

        # Debug: print what we found
        print(f"Found {len(files)} files:")
        for f in files:
            print(f"  - {f['filename']} ({f['extension']}) depth={f['depth']} status={f['status']}")

        # Assertions
        assert len(files) == 3, f"Expected 3 files, found {len(files)}"

        extensions = {f['extension'] for f in files}
        assert '.txt' in extensions, "Should find .txt files"
        assert '.pdf' in extensions, "Should find .pdf files"
        assert '.csv' in extensions, "Should find .csv files in subdirs"

        print("✓ scan_directory: all files found")


def test_get_depth():
    """Test that folder depth is calculated correctly from the scan root."""

    with tempfile.TemporaryDirectory() as tmpdir:
        # depth 0 — file directly in root
        root_file = Path(tmpdir, "root_file.txt")
        root_file.write_text("root")

        # depth 1 — one folder deep
        level1 = Path(tmpdir, "level1")
        level1.mkdir()
        file_l1 = level1 / "file.txt"
        file_l1.write_text("l1")

        # depth 2 — two folders deep
        level2 = level1 / "level2"
        level2.mkdir()
        file_l2 = level2 / "file.txt"
        file_l2.write_text("l2")

        assert get_depth(str(root_file), tmpdir) == 0, "Root file should have depth 0"
        assert get_depth(str(file_l1), tmpdir) == 1, "One level deep should have depth 1"
        assert get_depth(str(file_l2), tmpdir) == 2, "Two levels deep should have depth 2"

        print("✓ get_depth: depth calculations correct")


def test_get_status():
    """Test that versioning status is detected from folder names in the path."""

    # Current (-01- (current))
    assert get_status("/b/Projects/Design-01- (current)/report.pdf") == "current"
    assert get_status("/b/Projects/Design-01-(current)/report.pdf") == "current"

    # Working on (-02 (working on))
    assert get_status("/b/Projects/Design-02 (working on)/draft.docx") == "working on"
    assert get_status("/b/Projects/Design-02(working on)/draft.docx") == "working on"

    # Archived (-00)
    assert get_status("/b/Projects/Design-00/old.pdf") == "00"

    # Unversioned — no matching folder in path
    assert get_status("/b/Projects/Shared/generic_file.txt") == "unversioned"

    # Status detected from a deeply nested path
    assert get_status("/b/dept/sub/Design-01- (current)/2024/Q1/report.pdf") == "current"

    # -002 should NOT match -00 (would be a false positive without the (?!\d) guard)
    assert get_status("/b/Projects/report-002.pdf") == "unversioned"

    print("✓ get_status: all status patterns detected correctly")


def test_scan_directory_status_and_depth():
    """Integration test: scan a versioned folder structure and verify status + depth."""

    with tempfile.TemporaryDirectory() as tmpdir:
        # Simulate versioned folder structure
        current_dir = Path(tmpdir, "Project-01- (current)")
        current_dir.mkdir()
        Path(current_dir, "final.pdf").write_text("final")

        archived_dir = Path(tmpdir, "Project-00")
        archived_dir.mkdir()
        Path(archived_dir, "old.pdf").write_text("old")

        working_dir = Path(tmpdir, "Project-02 (working on)")
        working_dir.mkdir()
        Path(working_dir, "draft.docx").write_text("draft")

        # File with no versioning
        Path(tmpdir, "readme.txt").write_text("readme")

        files = scan_directory(tmpdir)
        by_name = {f['filename']: f for f in files}

        assert by_name['final.pdf']['status'] == 'current'
        assert by_name['old.pdf']['status'] == '00'
        assert by_name['draft.docx']['status'] == 'working on'
        assert by_name['readme.txt']['status'] == 'unversioned'

        # All versioned files are one level deep; readme is at depth 0
        assert by_name['final.pdf']['depth'] == 1
        assert by_name['readme.txt']['depth'] == 0

        print("✓ Integration: status and depth both correct in scan output")


if __name__ == '__main__':
    test_scan_directory()
    test_get_depth()
    test_get_status()
    test_scan_directory_status_and_depth()
    print("\n✅ All tests passed!")
