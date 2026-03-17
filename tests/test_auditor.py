import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.auditor import scan_directory


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
            print(f"  - {f['filename']} ({f['extension']})")
        
        # Assertions
        assert len(files) == 3, f"Expected 3 files, found {len(files)}"
        
        extensions = {f['extension'] for f in files}
        assert '.txt' in extensions, "Should find .txt files"
        assert '.pdf' in extensions, "Should find .pdf files"
        assert '.csv' in extensions, "Should find .csv files in subdirs"
        
        print("✓ All tests passed!")


if __name__ == '__main__':
    test_scan_directory()