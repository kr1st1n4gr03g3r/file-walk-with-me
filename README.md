# 📁 File Walk With Me
A lightweight command-line utility that scans a directory tree and generates an Excel report with file metadata.

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

## 💾 Installation

```
git clone https://github.com/kr1st1n4gr03g3r/file-walk-with-me.git
cd file-walk-with-me
pip install openpyxl
```

## 𖣠 Useage

```
python src/auditor.py <directory_path> [output_file.xlsx]
```

## 🍖 Examples

```
# Scan a folder, create default report
python src/auditor.py "B:\shared_drive"

# Scan and save with custom filename
python src/auditor.py "/home/user/documents" my_audit.xls

# Works on Windows, Mac, Linux
python src/auditor.py "/Volumes/shared/files"

```

## 🪐 Output

The script creates an Excel file with columns:
| File Type | File Name | File Path | Size (MB) |
|-----------|-----------|-----------|-----------|
| .pdf | report.pdf | C:\docs\report.pdf | 2.45 |
| .xlsx | data.xlsx | C:\docs\data.xlsx | 0.85 |

## 🐛 Requirements

- Python 3.7+
- openpyxl (for Excel file creation)

```
pip install openpyxl
```

## 🚗 How it Works
1. `scan_directory(path)` - Recursively walks the directory tree using `os.walk()`
2. Collects filename, extension, fullpath, and size for each file
3. Converts bytes to megabytes for readibility
4. `create_excel(files, output_path)` - Writes results to an `.xlsx` file
5. Sets Colum widths for professional appearance


## ⬇️ Future Iterations

[ ] Filter by extension
[ ] Find duplicate files by hash
[ ] Generate summary statistics (total size, oldest / newest files)
[ ] Progress bar for large scans
[ ]

## License

MIT