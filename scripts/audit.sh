#!/usr/bin/env bash
# =============================================================================
# file-walk-with-me — Bash fallback for restricted Windows environments
# =============================================================================
#
# Outputs a CSV report instead of .xlsx. Excel can open CSV files directly.
#
# USAGE
#   bash scripts/audit.sh <directory_path> [output.csv]
#
# EXAMPLES
#   bash scripts/audit.sh "/b/shared_drive"
#   bash scripts/audit.sh "/b/shared_drive" b_drive_audit.csv
#
# WINDOWS (Git Bash via VS Code terminal)
#   The B: drive is accessed as /b/ in Git Bash:
#     bash scripts/audit.sh "/b/"
#
#   If Git Bash maps drives differently on your machine, try:
#     bash scripts/audit.sh "B:/"
#
# STATUS COLUMN — manual versioning detection
#   Scans all folder names in the full path for the team's version suffixes:
#     -00              → 00           (archived, do not migrate)
#     -01- (current)   → current      (ready to migrate)
#     -02 (working on) → working on   (in progress, do not migrate)
#     (none found)     → unversioned
#
# DEPTH COLUMN
#   Number of folder levels from your scan root.
#   A file directly inside the root directory has depth 0.
# =============================================================================

set -euo pipefail

ROOT_DIR="${1:?Error: directory path required. Usage: bash scripts/audit.sh <path> [output.csv]}"
OUTPUT="${2:-file_audit_report.csv}"

# Normalize: strip trailing slash
ROOT_DIR="${ROOT_DIR%/}"

if [ ! -d "$ROOT_DIR" ]; then
    echo "Error: '$ROOT_DIR' is not a valid directory" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# get_size_bytes <file>
# Returns file size in bytes. Tries GNU stat (Git Bash / Linux / WSL) first,
# then BSD stat (macOS), then falls back to wc.
# ---------------------------------------------------------------------------
get_size_bytes() {
    local file="$1"
    stat -c "%s" "$file" 2>/dev/null \
        || stat -f "%z" "$file" 2>/dev/null \
        || wc -c < "$file" 2>/dev/null \
        || echo 0
}

# ---------------------------------------------------------------------------
# get_depth <filepath>
# Counts folder levels between ROOT_DIR and the file.
# ---------------------------------------------------------------------------
get_depth() {
    local filepath="$1"
    local relative="${filepath#${ROOT_DIR}/}"
    # If root didn't have a trailing slash in the path, strip the leading /
    relative="${relative#/}"
    # Count the number of / separators = number of folder levels
    local slashes
    slashes=$(printf '%s' "$relative" | tr -cd '/' | wc -c | tr -d ' ')
    echo "$slashes"
}

# ---------------------------------------------------------------------------
# get_status <filepath>
# Detects manual version-control suffix in any folder name along the path.
# Order matters: check most specific patterns before -00.
# ---------------------------------------------------------------------------
get_status() {
    local filepath="$1"
    if printf '%s' "$filepath" | grep -qiE -- '-02[[:space:]]*\(working[[:space:]]+on\)'; then
        echo "working on"
    elif printf '%s' "$filepath" | grep -qiE -- '-01[[:space:]]*-[[:space:]]*\(current\)'; then
        echo "current"
    elif printf '%s' "$filepath" | grep -qiE -- '-00([^0-9]|$)'; then
        echo "00"
    else
        echo "unversioned"
    fi
}

# ---------------------------------------------------------------------------
# csv_escape <value>
# Wraps value in double quotes and escapes any internal double quotes.
# ---------------------------------------------------------------------------
csv_escape() {
    local val="$1"
    # Replace every " with "" then wrap in outer quotes
    printf '"%s"' "${val//\"/\"\"}"
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
echo "Scanning $ROOT_DIR ..."

# Write CSV header
printf 'File Type,File Name,File Path,Size (MB),Depth,Status\n' > "$OUTPUT"

file_count=0

while IFS= read -r -d '' filepath; do
    filename=$(basename "$filepath")

    # Extension
    extension="${filename##*.}"
    if [ "$extension" = "$filename" ]; then
        extension="(no ext)"
    else
        extension=".${extension}"
    fi

    # Size in MB (2 decimal places)
    size_bytes=$(get_size_bytes "$filepath")
    size_mb=$(awk "BEGIN { printf \"%.2f\", ${size_bytes:-0} / 1048576 }")

    # Depth from root
    depth=$(get_depth "$filepath")

    # Versioning status
    status=$(get_status "$filepath")

    # Write one CSV row
    printf '%s,%s,%s,%s,%s,%s\n' \
        "$(csv_escape "$extension")" \
        "$(csv_escape "$filename")" \
        "$(csv_escape "$filepath")" \
        "$size_mb" \
        "$depth" \
        "$(csv_escape "$status")" >> "$OUTPUT"

    file_count=$((file_count + 1))
done < <(find "$ROOT_DIR" -type f -print0)

echo "Found $file_count files"
echo "Report saved to $OUTPUT"
