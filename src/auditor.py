import os
import re
import sys
import time
from openpyxl import Workbook


## progress display - fire walk with me

_FIRE_FRAMES = [
    "   (  )   (   )  (  )   ",
    "  (   )  ) ^ (  (   )  ",
    "   ) (  (  ^ ) )  ) (  ",
    "  ( (  ) ) ^ ( (  ) )  ",
    "   ) ) (  ^^^  ) ( (   ",
    "  ( (  ) )^^^^(  ) )   ",
    "   ) (   )^^^^^ ) (    ",
    "  (   ) (^^^^^^^) (    ",
]

_STATUS_MESSAGES = [
    "☕️ A damn fine scan ☕️",
    "🦉 Hoooooot Hoooooooot 🦉",
    "🎤  Diane, here's something we haven't seen before: a mounted disk 🎤",
    "🫧  Those GBs you like are going to come back in style 🫧",
    "🐟 There's a file in the percolator 🐟",
    "🔴 This path is not what it seems 🔴",
    "🌲 Scanning the woods 🌲",
    "🔥 File walk with me 🔥",
    "🪵  My log has something to say about your versioning patterns 🪵",
    "🩶  The directory is wrapped in plastic 🩶",
    "🪺  We live inside a nested folder 🪺",
    "🕳️  Entering the Black Lodge 🕳️",
    "📼  Diane, the shared drive is haunted 📼",
    "🎞️  Meanwhile... 🎞️",
]

_BAR_WIDTH = 30


class _Progress:
    def __init__(self):
        self._frame = 0
        self._message_idx = 0
        self._current_message = _STATUS_MESSAGES[0]
        self._last_message_change = 0.0
        self._display_initialized = False

    def _next_frame(self):
        f = _FIRE_FRAMES[self._frame % len(_FIRE_FRAMES)]
        self._frame += 1
        return f

    def _update_message(self):
        now = time.time()

        if self._last_message_change == 0:
            self._last_message_change = now
            self._current_message = _STATUS_MESSAGES[self._message_idx]
            return

        if now - self._last_message_change >= 4:
            self._message_idx = (self._message_idx + 1) % len(_STATUS_MESSAGES)
            self._current_message = _STATUS_MESSAGES[self._message_idx]
            self._last_message_change = now

    def _init_display(self):
        if not self._display_initialized:
            sys.stdout.write("\n\n\n")
            sys.stdout.flush()
            self._display_initialized = True

    def _redraw_display(self, line1, line2, line3):
        self._init_display()
        sys.stdout.write("\033[3F\033[J")
        sys.stdout.write(f"{line1}\n{line2}\n{line3}\n")
        sys.stdout.flush()

    def header(self):
        print()
        print("  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("    📂 🔥 F i l e   W a l k   W i t h   M e 📂 🔥")
        print("  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print()

    def spinning(self, count):
        ## animates while counting files (no total yet)
        f = self._next_frame()
        self._update_message()
        self._redraw_display(
            f,
            self._current_message,
            f"{count:,} files counted..."
        )

    def bar(self, current, total):
        f = self._next_frame()
        ## progress bar with percentage
        self._update_message()

        pct = current / total if total > 0 else 0
        filled = int(_BAR_WIDTH * pct)
        bar = "#" * filled + "-" * (_BAR_WIDTH - filled)

        self._redraw_display(
            f,
            self._current_message,
            f"[{bar}]  {pct * 100:3.0f}%  |  {current:,} / {total:,}"
        )

    def done(self, total):
        bar = "#" * _BAR_WIDTH
        self._redraw_display(
            "  ( o,o )  ( o,o )  ( o,o )",
            "✅ Audit complete",
            f"[{bar}]  100%  |  {total:,} / {total:,}"
        )
        sys.stdout.write("\n")
        sys.stdout.flush()

    def clear(self):
        if self._display_initialized:
            sys.stdout.write("\033[3F\033[J")
            sys.stdout.flush()
            self._display_initialized = False


def get_depth(filepath, root_path):
    ## depth relative to the scan root
    ## file directly in root = 0, each additonal folder level adds 1

    relative = os.path.relpath(filepath, root_path)
    parts = relative.replace("\\", "/").split("/")
    ## parts[-1] is the filename - everything before it is folders
    return len(parts) - 1


def get_status(filepath):
    ## checks folder names anywhere in the path for versioning suffixes
    ## order matters - check specific patterns before -00 or it catches -001 etc
    normalized = filepath.replace("\\", "/")

    if re.search(r"-02\s*\(working\s+on\)", normalized, re.IGNORECASE):
        return "working on"
    elif re.search(r"-01\s*-\s*\(current\)", normalized, re.IGNORECASE):
        return "current"
    elif re.search(r"-00(?!\d)", normalized, re.IGNORECASE):
        return "00"
    else:
        return "unversioned"


def collect_paths(root_path, progress):
    ## fast first pass, just grabs paths - no stat calls yet
    paths = []
    for dirpath, _, filenames in os.walk(root_path):
        for filename in filenames:
            paths.append(os.path.join(dirpath, filename))
            if len(paths) % 10 == 0:
                progress.spinning(len(paths))

    progress.spinning(len(paths))
    return paths


def scan_directory(root_path, paths, progress):
    ## does the actual work - stat calls, depth, status
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
            "extension": ext if ext else "(no ext)",
            "filename": filename,
            "filepath": filepath,
            "size_mb": size_mb,
            "depth": get_depth(filepath, abs_root),
            "status": get_status(filepath)
        })

        if (i + 1) % 10 == 0 or (i + 1) == total:
            progress.bar(i + 1, total)

    return files


def create_excel(files, output_path):
    ## writes to xlsx
    wb = Workbook()
    ws = wb.active
    ws.title = "Files"

    ## Add Headers
    ws["A1"] = "File Type"
    ws["B1"] = "File Name"
    ws["C1"] = "File Path"
    ws["D1"] = "Size (MB)"
    ws["E1"] = "Depth"
    ws["F1"] = "Status"

    ## Add file data
    for idx, file in enumerate(files, start=2):
        ws[f"A{idx}"] = file["extension"]
        ws[f"B{idx}"] = file["filename"]
        ws[f"C{idx}"] = file["filepath"]
        ws[f"D{idx}"] = file["size_mb"]
        ws[f"E{idx}"] = file["depth"]
        ws[f"F{idx}"] = file["status"]

    ## Adjust column widths, we aren't animals here
    ws.column_dimensions["A"].width = 15
    ws.column_dimensions["B"].width = 25
    ws.column_dimensions["C"].width = 50
    ws.column_dimensions["D"].width = 12
    ws.column_dimensions["E"].width = 10
    ws.column_dimensions["F"].width = 15

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
        print(f"  Scanning: {target_dir}")
        print()
        print("  Counting files...")

        ## first pass, get the paths
        paths = collect_paths(target_dir, progress)
        progress.clear()

        print("  Processing files...")

        ## second pass, do the actual work
        files = scan_directory(target_dir, paths, progress)
        progress.done(len(files))

        print(f"✅ Found {len(files):,} files")
        print(f"💾 Report saved to {output_file}")
        print("📝 Creating Excel report...")
        print()

        create_excel(files, output_file)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()