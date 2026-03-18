import os
import re
import sys
from openpyxl import Workbook


## progress display — fire walk with me

_FIRE_FRAMES = [
    "  ) )  ( (  ) )  ( ( ",
    " ) )  ( (  ) )  ( (  ",
    ") )  ( (  ) )  ( (   ",
    " )  ( (  ) )  ( (  ) ",
    "  ( (  ) )  ( (  ) ) ",
    " ( (  ) )  ( (  ) )  ",
    "( (  ) )  ( (  ) )   ",
    " (  ) )  ( (  ) )  ( ",
]

_BAR_WIDTH = 30
_LINE_WIDTH = 90


class _Progress:
    def __init__(self):
        self._frame = 0

    def _next_frame(self):
        f = _FIRE_FRAMES[self._frame % len(_FIRE_FRAMES)]
        self._frame += 1
        return f

    def header(self):
        print()
        print("  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("    📂 🔥 f i l e   w a l k   w i t h   m e")
        print("  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print()

    def spinning(self, count):
        ## animates while counting files (no total yet)
        f = self._next_frame()
        line = f"\r  {f}  The owls are counting...  {count:,}"
        sys.stdout.write(line.ljust(_LINE_WIDTH))
        sys.stdout.flush()

    def bar(self, current, total):
        ## progress bar with percentage
        f = self._next_frame()
        pct = current / total if total > 0 else 0
        filled = int(_BAR_WIDTH * pct)
        bar = '#' * filled + '-' * (_BAR_WIDTH - filled)
        line = f"\r  {f}  [{bar}] {pct*100:3.0f}%  |  {current:,} / {total:,}"
        sys.stdout.write(line.ljust(_LINE_WIDTH))
        sys.stdout.flush()

    def done(self, total):
        bar = '#' * _BAR_WIDTH
        owls = "  ( o,o )  ( o,o )  ( o,o )  "
        line = f"\r  {owls}  [{bar}] 100%  |  {total:,} / {total:,}"
        sys.stdout.write(line.ljust(_LINE_WIDTH) + '\n\n')
        sys.stdout.flush()

    def clear(self):
        sys.stdout.write('\r' + ' ' * _LINE_WIDTH + '\r')
        sys.stdout.flush()


def get_depth(filepath, root_path):
    ## depth relative to the scan root
    ## file directly in root = 0, each additonal folder level adds 1
    relative = os.path.relpath(filepath, root_path)
    parts = relative.replace('\\', '/').split('/')
    ## parts[-1] is the filename — everything before it is folders
    return len(parts) - 1


def get_status(filepath):
    ## checks folder names anywhere in the path for versioning suffixes
    ## order matters — check specific patterns before -00 or it catches -001 etc
    normalized = filepath.replace('\\', '/')

    if re.search(r'-02\s*\(working\s+on\)', normalized, re.IGNORECASE):
        return 'working on'
    elif re.search(r'-01\s*-\s*\(current\)', normalized, re.IGNORECASE):
        return 'current'
    elif re.search(r'-00(?!\d)', normalized, re.IGNORECASE):
        return '00'
    else:
        return 'unversioned'


def collect_paths(root_path, progress):
    ## fast first pass, just grabs paths — no stat calls yet
    paths = []
    for dirpath, _, filenames in os.walk(root_path):
        for filename in filenames:
            paths.append(os.path.join(dirpath, filename))
            if len(paths) % 200 == 0:
                progress.spinning(len(paths))
    progress.spinning(len(paths))
    return paths


def scan_directory(root_path, paths, progress):
    ## does the actual work — stat calls, depth, status
    ## kept seperate from collect_paths so we can show a real progress bar
    files = []
    abs_root = os.path.abspath(root_path)
    total = len(paths)

    for i, filepath in enumerate(paths):
        filename = os.path.basename(filepath)
        _, ext = os.path.splitext(filename)

        size_bytes = os.path.getsize(filepath)
        size_mb = round(size_bytes / (1024 * 1024), 2)

        files.append({
            'extension': ext if ext else '(no ext)',
            'filename': filename,
            'filepath': filepath,
            'size_mb': size_mb,
            'depth': get_depth(filepath, abs_root),
            'status': get_status(filepath)
        })

        if (i + 1) % 50 == 0 or (i + 1) == total:
            progress.bar(i + 1, total)

    return files


def create_excel(files, output_path):
    ## writes to xlsx
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
        progress = _Progress()
        progress.header()
        print(f"  Scanning: {target_dir}\n")

        ## first pass, get the paths
        paths = collect_paths(target_dir, progress)
        progress.clear()

        ## second pass, do the actual work
        files = scan_directory(target_dir, paths, progress)
        progress.done(len(files))

        print(f"✅ Found {len(files):,} files")
        print(f"📝 Creating Excel report...\n")

        create_excel(files, output_file)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
