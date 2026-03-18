import os
import re
import sys
from openpyxl import Workbook


def get_depth(filepath, root_path):
    """Calculate folder depth of a file relative to the root scan path.

    A file directly inside root_path has depth 0.
    Each additional nested folder adds 1.
    """
    relative = os.path.relpath(filepath, root_path)
    parts = relative.replace('\\', '/').split('/')
    ## parts[-1] is the filename — everything before it is folders
    return len(parts) - 1


def get_status(filepath):
    """Detect versioning status from folder names anywhere in the file path.

    Matches the manual versioning convention:
      -00             → '00'           (archived / old)
      -01- (current)  → 'current'      (ready to migrate)
      -02 (working on)→ 'working on'   (in progress, skip migration)

    Files not inside any versioned folder → 'unversioned'
    """
    normalized = filepath.replace('\\', '/')

    if re.search(r'-02\s*\(working\s+on\)', normalized, re.IGNORECASE):
        return 'working on'
    elif re.search(r'-01\s*-\s*\(current\)', normalized, re.IGNORECASE):
        return 'current'
    elif re.search(r'-00(?!\d)', normalized, re.IGNORECASE):
        return '00'
    else:
        return 'unversioned'


def scan_directory(path):
    """Walk through directory and collect file info."""
    files = []
    root_path = os.path.abspath(path)

    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)

            ## Get file extension
            _, ext = os.path.splitext(filename)

            ## Get file size in MB
            size_bytes = os.path.getsize(filepath)
            size_mb = round(size_bytes / (1024 * 1024), 2)

            files.append({
                'extension': ext if ext else '(no ext)',
                'filename': filename,
                'filepath': filepath,
                'size_mb': size_mb,
                'depth': get_depth(filepath, root_path),
                'status': get_status(filepath)
            })

    return files


def create_excel(files, output_path):
    """Create Excel file with file data."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Files"

    ## Add Headers
    ws['A1'] = 'File Type'
    ws['B1'] = 'File Name'
    ws['C1'] = 'File Path'
    ws['D1'] = 'Size (MB)'
    ws['E1'] = 'Depth'
    ws['F1'] = 'Status'

    ## Add file data
    for idx, file in enumerate(files, start=2):
        ws[f'A{idx}'] = file['extension']
        ws[f'B{idx}'] = file['filename']
        ws[f'C{idx}'] = file['filepath']
        ws[f'D{idx}'] = file['size_mb']
        ws[f'E{idx}'] = file['depth']
        ws[f'F{idx}'] = file['status']

    ## Adjust column widths, we aren't animals here
    ws.column_dimensions['A'].width = 15
    ws.column_dimensions['B'].width = 25
    ws.column_dimensions['C'].width = 50
    ws.column_dimensions['D'].width = 12
    ws.column_dimensions['E'].width = 10
    ws.column_dimensions['F'].width = 15

    wb.save(output_path)
    print(f"✅ Report saved to {output_path}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python auditor.py <directory_path> [output_file.xlsx]")
        print("Example: python auditor.py /Users/kristinagroeger/Documents")
        sys.exit(1)

    target_dir = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "file_audit_report.xlsx"

    if not os.path.isdir(target_dir):
        print(f"Error: {target_dir} is not a valid directory")
        sys.exit(1)

    try:
        print(f"📁 Scanning {target_dir}...\n")
        files = scan_directory(target_dir)

        print(f"✅ Found {len(files)} files")
        print(f"📝 Creating Excel report...\n")

        create_excel(files, output_file)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
