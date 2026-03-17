# 📁 File Walk With Me

```                                                                 
....%@@@@@@@@+=@@@@@@@@@.........#@@@@@@@@#.@@@@@@@@@-........+@@@@@@@@@=@@@@@@@@@=.........@@@
..%@@@@@@@@+....=@@@@@@@@@.....#@@@@@@@@%.....@@@@@@@@@-....*@@@@@@@@@.....@@@@@@@@@=.....@@@@@
%@@@@@@@@*........+@@@@@@@@@.#@@@@@@@@%.........@@@@@@@@@-=@@@@@@@@@.........@@@@@@@@@-.@@@@@@@
@@@@@@@*............*@@@@@@@@@@@@@@@%............:@@@@@@@@@@@@@@@@:............@@@@@@@@@@@@@@@@
@@@@@#................*@@@@@@@@@@@@................-@@@@@@@@@@@@-...............:@@@@@@@@@@@@*.
@@@%....................#@@@@@@@@....................=@@@@@@@@-...................-@@@@@@@@*...
@%..........:@@-..........#@@@@...........%@*..........=@@@@-..........*@*..........=@@@@*.....
...........@@@@@@-..........*...........%@@@@@+..........+=..........*@@@@@*..........+*.......
.........@@@@@@@@@@:..................%@@@@@@@@@+..................*@@@@@@@@@+.................
.......@@@@@@@@@@@@@@:..............@@@@@@@@@@@@@@+..............+@@@@@@@@@@@@@*..............:
.....@@@@@@@@@@@@@@@@@@...........%@@@@@@@@@@@@@@@@@=..........+@@@@@@@@@@@@@@@@@+...........@@
...@@@@@@@@@*..+@@@@@@@@@.......#@@@@@@@@%...@@@@@@@@@-......=@@@@@@@@@...@@@@@@@@@=.......@@@@
.@@@@@@@@@*......*@@@@@@@@@...*@@@@@@@@%......:@@@@@@@@@:..-@@@@@@@@@.......@@@@@@@@@=...@@@@@@
@@@@@@@@%..........*@@@@@@@@@@@@@@@@@@..........-@@@@@@@@@@@@@@@@@@..........:@@@@@@@@@@@@@@@@@
@@@@@@#..............+@@@@@@@@@@@@@@..............:@@@@@@@@@@@@@@...............@@@@@@@@@@@@@@=
@@@@#..................*@@@@@@@@@@..................-@@@@@@@@@@:.................:@@@@@@@@@@+..
@@#..........:-..........#@@@@@@...........*..........-@@@@@@-..........+..........:@@@@@@*....
#...........@@@@:..........#@@...........%@@@+..........+@@=..........*@@@*..........-@@#......
```

A lightweight command-line utility that scans a directory tree and generates an Excel report with file metadata.

<br>

## ⛓️ What it does

**Point it at a folder, and it creates an `xlsx` file with:**

- File Type - Extension (.txt, .pdf, .jpeg, etc.)
- File Name - Just the filename
- File Path - full path on diesk
- Size (MB) - human-readable size

**Useful for:**

- Auditing shared drives
- Finding large files
- Untangling multi-nested empty folders
- Understanding what's taking up space
- Duplicated folders

<br>

## 💾 Installation

```bash
git clone https://github.com/kr1st1n4gr03g3r/file-walk-with-me.git
cd file-walk-with-me
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

<br>

## 𖣠 Usage

Make sure your virtual environment is activated:
```bash
source venv/bin/activate
```

Then run:
```bash
python3 src/auditor.py  [output_file.xlsx]
```

<br>

## 🍖 Examples

```bash
# Scan a folder, create default report
python src/auditor.py "B:\shared_drive"

# Scan and save with custom filename
python src/auditor.py "/home/user/documents" my_audit.xls

# Works on Windows, Mac, Linux
python src/auditor.py "/Volumes/shared/files"

```
<br>

## 🪐 Output

The script creates an Excel file with columns:
| File Type | File Name | File Path | Size (MB) |
|-----------|-----------|-----------|-----------|
| .pdf | report.pdf | C:\docs\report.pdf | 2.45 |
| .xlsx | data.xlsx | C:\docs\data.xlsx | 0.85 |

<br>

## 🐛 Requirements

- Python 3.7+
- openpyxl (for Excel file creation)

```
pip install openpyxl
```

🔗 [openpyxl Docs](https://openpyxl.readthedocs.io/en/stable/)

<br>

## 🚗 How it Works
1. `scan_directory(path)` - Recursively walks the directory tree using `os.walk()`
2. Collects filename, extension, fullpath, and size for each file
3. Converts bytes to megabytes for readibility
4. `create_excel(files, output_path)` - Writes results to an `.xlsx` file
5. Sets Column widths for professional appearance

<br>

## ⬇️ Future Iterations

[ ] Filter by extension  
[ ] Find duplicate files by hash  
[ ] Generate summary statistics (total size, oldest / newest files)  
[ ] Progress bar for large scans  
[ ] Command prompt choices to choose folder, create alias command, and make it executable `chmod`  
[ ] Generate a column with nesting depth level  
[ ] Find duplicate files in file system despite their locations  
[ ] Explore further metadata capabilities  
[ ] Export to `CSV` (not just Excel)  
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
