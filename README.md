# 📁 🔥 File Walk With Me


A lightweight command-line utility that scans a directory tree and generates a report with file metadata, including nesting depth and versioning status.

Available in two forms:
- **Python** → outputs `.xlsx` (Excel workbook)
- **Bash** → outputs `.csv` (works in restricted environments where package installs are not possible, and on macOS Terminal out of the box)

<br>

## 🕵🏻‍♀️ Why I built this

I work in municipal government, where IT restrictions are a constant reality: Overnight OneDrive syncs you didn't ask for, VS Code Marketplace blocked, `C://` access randomly revoked, and having to justify why Git is necessary on a software project. Standard stuff  if you've worked in a locked-down Windows environment.

I was leading a file migration across a shared drive where versioning was done manually: authors named their folders things like `current-00`, `working-01`, `approved-02`, `approved-final`, `approved-final-final`, mixed into a reusable media repository with no naming conventions and nesting up to 22 levels deep. I needed to know what we actually had before I could tell my team how to move it. The bottleneck was known all the way up to Director level. The usual routes weren't moving.

I wrote a Python script on my Mac. It worked. Then I tried to run it at work in the Microsoft environment... To no one's surprise, every restriction at once. 🙅🏻‍♀️ 

Rather than wait on a 2-3 month IT ticket, I remembered that VS Code's integrated terminal ships with Git for Windows, which includes bash. No install, no admin rights, nothing outside policy. I rewrote the logic as a bash script using only built-in shell tools, and it ran fine.

Both versions are in this repo. The Python script is the full one. The bash version exists because sometimes you work with what you've got.


<br>

## ⛓️ What it does

**Point it at a folder, and it creates a report with:**

| Column | Description |
|--------|-------------|
| File Type | Extension (`.txt`, `.pdf`, `.jpeg`, etc.) |
| File Name | Just the filename |
| File Path | Full path on disk |
| Size (MB) | Human-readable size |
| Depth | Folder levels deep from your scan root |
| Status | Versioning label based on folder name suffix |

**Useful for:**

- Auditing shared drives and B: drives
- Content migration planning (filter by Status to skip non-current versions)
- Finding large files and understanding nesting depth
- Untangling multi-nested empty folders
- Duplicated folders

<br>

## 🗂️ Status Column

The **Status** column detects a manual folder versioning convention used in many organizations:

| Folder suffix | Status value | Meaning |
|---------------|--------------|---------|
| `-00` | `00` | Archived / old — do not migrate |
| `-01- (current)` | `current` | Ready to migrate |
| `-02 (working on)` | `working on` | In progress — do not migrate |
| *(none found)* | `unversioned` | No versioning folder in this path |

The check scans **all folder names** in the full path, so a deeply nested file still picks up the status of its versioned parent folder.

**Example paths:**
```
B:\Projects\Design-01- (current)\assets\logo.png   → current
B:\Projects\Design-00\archive\old_logo.png         → 00
B:\Projects\Design-02 (working on)\draft.ai        → working on
B:\README.txt                                       → unversioned
```

<br>

## 💾 Installation

### Python version
```bash
git clone https://github.com/kr1st1n4gr03g3r/file-walk-with-me.git
cd file-walk-with-me
python3 -m venv venv
source venv/bin/activate        # Windows Git Bash: source venv/Scripts/activate
pip install -r requirements.txt
```

### Bash version
No installation needed. The script uses only standard shell tools (`find`, `awk`, `grep`, `stat`).

<br>

## 𖣠 Usage

### Python (outputs `.xlsx`)

Make sure your virtual environment is activated:
```bash
source venv/bin/activate
```

Then run:
```bash
python3 src/auditor.py <directory_path> [output_file.xlsx]
```

### Bash (outputs `.csv`)

```bash
bash scripts/audit.sh <directory_path> [output.csv]
```

<br>

## 🍖 Examples

### Python
```bash
# Scan B: drive, create default report
python3 src/auditor.py "B:/"

# Scan with custom output name
python3 src/auditor.py "B:/shared_drive" b_drive_audit.xlsx

# Works on Windows, Mac, Linux
python3 src/auditor.py "/Volumes/shared/files"
```

### Bash (Git Bash on Windows)
```bash
# B: drive is /b/ in Git Bash
bash scripts/audit.sh "/b/"

# Custom output name
bash scripts/audit.sh "/b/shared_drive" b_drive_audit.csv

# Scan a specific subfolder
bash scripts/audit.sh "/b/departments/finance" finance_audit.csv
```

### Bash (macOS Terminal)
```bash
# Scan a local folder
bash scripts/audit.sh "/Users/yourname/Documents"

# Scan a mounted network drive or external volume
bash scripts/audit.sh "/Volumes/SharedDrive" shared_drive_audit.csv

# Custom output name
bash scripts/audit.sh "/Users/yourname/Projects" projects_audit.csv
```

<br>

## 🪐 Output

### Excel (Python)
```
| File Type | File Name  | File Path                              | Size (MB) | Depth | Status  |
|-----------|------------|----------------------------------------|-----------|-------|---------|
| .pdf      | report.pdf | B:\Projects\Design-01- (current)\...  | 2.45      | 3     | current |
| .xlsx     | data.xlsx  | B:\Projects\Design-00\data.xlsx        | 0.85      | 2     | 00      |
```

### CSV (Bash)
Same columns, saved as `.csv`. Open directly in Excel with **File → Open**.

<br>

## 🔒 Running in Restricted Environments

If you work in an environment where:
- Package managers (`pip`, `npm`) are blocked or unreliable
- `PATH` settings reset periodically
- PowerShell or Command Prompt access is unavailable

**Use the Bash script** via the VS Code integrated terminal:

1. Open VS Code
2. Open the integrated terminal (`Ctrl + \``)
3. Run:
   ```bash
   bash scripts/audit.sh "/b/your/folder" report.csv
   ```
4. Open `report.csv` directly in Excel

No Python, no `pip`, no virtual environment needed. The Bash script uses only built-in shell tools that ship with Git for Windows.

<br>

## 🐛 Requirements

### Python version
- Python 3.7+
- `openpyxl` (for Excel file creation)

```bash
pip install openpyxl
```

🔗 [openpyxl Docs](https://openpyxl.readthedocs.io/en/stable/)

### Bash version
- Bash (Git Bash, WSL, macOS Terminal, Linux)
- Standard tools: `find`, `awk`, `grep`, `stat` — all included with Git for Windows

<br>

## 🚗 How it Works

### Python
1. `scan_directory(path)` — Recursively walks the directory tree using `os.walk()`
2. For each file: collects filename, extension, full path, size, depth, and status
3. `get_depth(filepath, root)` — Counts folder levels using `os.path.relpath()`
4. `get_status(filepath)` — Regex-matches versioning suffixes anywhere in the full path
5. Converts bytes to megabytes for readability
6. `create_excel(files, output_path)` — Writes results to an `.xlsx` file with formatted columns

### Bash
1. `find "$ROOT_DIR" -type f -print0` — Null-delimited recursive file list
2. For each file: extracts extension, computes size via `stat`, depth via slash-counting, status via `grep -E`
3. Writes a properly escaped CSV row per file

<br>

## ⬇️ Future Iterations

[x] Generate a column with nesting depth level
[x] Export to `CSV` (Bash fallback for restricted environments)
[ ] Filter by extension
[ ] Find duplicate files by hash
[ ] Generate summary statistics (total size, oldest / newest files)
[x] Progress bar for large scans
[ ] Command prompt choices to choose folder, create alias command, and make it executable `chmod`
[ ] Find duplicate files in file system despite their locations
[ ] Explore further metadata capabilities
[ ] Sort/filter results in Excel (add AutoFilter)
[ ] Exclude folders (like `node_modules`, `.git`, `venv`)
[ ] File age calculation (days since modified)
[ ] Permission checks (read-only files, access denied logging)
[ ] Parallel scanning for faster processing on large drives
[ ] Config file support (remember last scanned path)
[ ] Recursive depth limit (scan only N levels deep)
[ ] Generate HTML report alternative
[ ] Integration with system file explorer (right-click → audit this folder)

<br>

## License

MIT

```
..%@@@@@@@@+=@@@@@@@@@.........#@@@@@@@@#.@@@@@@@@@-........+@@@@@@@@@=@@@@@@@@@=.........@
%@@@@@@@@+....=@@@@@@@@@.....#@@@@@@@@%.....@@@@@@@@@-....*@@@@@@@@@.....@@@@@@@@@=.....@@@
@@@@@@@*........+@@@@@@@@@.#@@@@@@@@%.........@@@@@@@@@-=@@@@@@@@@.........@@@@@@@@@-.@@@@@
@@@@@*............*@@@@@@@@@@@@@@@%............:@@@@@@@@@@@@@@@@:............@@@@@@@@@@@@@@
@@@#................*@@@@@@@@@@@@................-@@@@@@@@@@@@-...............:@@@@@@@@@@@@
@%....................#@@@@@@@@....................=@@@@@@@@-...................-@@@@@@@@*.
..........:@@-..........#@@@@...........%@*..........=@@@@-..........*@*..........=@@@@*...
.........@@@@@@-..........*...........%@@@@@+..........+=..........*@@@@@*..........+*.....
.......@@@@@@@@@@:..................%@@@@@@@@@+..................*@@@@@@@@@+...............
.....@@@@@@@@@@@@@@:..............@@@@@@@@@@@@@@+..............+@@@@@@@@@@@@@*.............
...@@@@@@@@@@@@@@@@@@...........%@@@@@@@@@@@@@@@@@=..........+@@@@@@@@@@@@@@@@@+...........
.@@@@@@@@@*..+@@@@@@@@@.......#@@@@@@@@%...@@@@@@@@@-......=@@@@@@@@@...@@@@@@@@@=.......@@
@@@@@@@@*......*@@@@@@@@@...*@@@@@@@@%......:@@@@@@@@@:..-@@@@@@@@@.......@@@@@@@@@=...@@@@
@@@@@@%..........*@@@@@@@@@@@@@@@@@@..........-@@@@@@@@@@@@@@@@@@..........:@@@@@@@@@@@@@@@
@@@@#..............+@@@@@@@@@@@@@@..............:@@@@@@@@@@@@@@...............@@@@@@@@@@@@@
@@#..................*@@@@@@@@@@..................-@@@@@@@@@@:.................:@@@@@@@@@@+
#..........:-..........#@@@@@@...........*..........-@@@@@@-..........+..........:@@@@@@*..
..........@@@@:..........#@@...........%@@@+..........+@@=..........*@@@*..........-@@#....
```
