import os
import sys
from openpyxl import Workbook


def scan_directory(path):
    """Walk through directory and collect file info."""
    files = []

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
                'size_mb': size_mb
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

    ## Add file data
    for idx, file in enumerate(files, start=2):
        ws[f'A{idx}'] = file['extension']
        ws[f'B{idx}'] = file['filename']
        ws[f'C{idx}'] = file['filepath']
        ws[f'D{idx}'] = file['size_mb']

    ## Adjust column widths, we aren't animals here
    ws.column_dimensions['A'].width = 15
    ws.column_dimensions['B'].width = 25
    ws.column_dimensions['C'].width = 50
    ws.column_dimensions['D'].width = 12

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