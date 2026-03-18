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
# STATUS COLUMN
#   -00              → 00           (archived, do not migrate)
#   -01- (current)   → current      (ready to migrate)
#   -02 (working on) → working on   (in progress, do not migrate)
#   (none found)     → unversioned
#
# DEPTH COLUMN
#   Number of folder levels from your scan root.
#   A file directly inside the root directory has depth 0.
# =============================================================================

set -euo pipefail

ROOT_DIR="${1:?Error: directory path required. Usage: bash scripts/audit.sh <path> [output.csv]}"
OUTPUT="${2:-file_audit_report.csv}"

# strip trailing slash
ROOT_DIR="${ROOT_DIR%/}"

if [ ! -d "$ROOT_DIR" ]; then
    echo "Error: '$ROOT_DIR' is not a valid directory" >&2
    exit 1
fi

# progress display

FIRE_FRAMES=(
    "  ) )  ( (  ) )  ( ( "
    " ) )  ( (  ) )  ( (  "
    ") )  ( (  ) )  ( (   "
    " )  ( (  ) )  ( (  ) "
    "  ( (  ) )  ( (  ) ) "
    " ( (  ) )  ( (  ) )  "
    "( (  ) )  ( (  ) )   "
    " (  ) )  ( (  ) )  ( "
)

BAR_WIDTH=30
LINE_WIDTH=90
FRAME_IDX=0
CURRENT_FRAME=""

print_header() {
    echo ""
    echo "  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    echo "    📂 🔥 f i l e   w a l k   w i t h   m e"
    echo "  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    echo ""
}

next_frame() {
    CURRENT_FRAME="${FIRE_FRAMES[$((FRAME_IDX % ${#FIRE_FRAMES[@]}))]}"
    FRAME_IDX=$((FRAME_IDX + 1))
}

show_spinner() {
    local count="$1"
    next_frame
    printf "\r  %s  The owls are counting...  %d" "$CURRENT_FRAME" "$count"
}

show_bar() {
    local current="$1"
    local total="$2"
    next_frame

    local pct=0
    local filled=0
    if [ "$total" -gt 0 ]; then
        pct=$((current * 100 / total))
        filled=$((current * BAR_WIDTH / total))
    fi

    local bar=""
    local i=0
    while [ "$i" -lt "$filled" ]; do
        bar="${bar}#"
        i=$((i + 1))
    done
    while [ "$i" -lt "$BAR_WIDTH" ]; do
        bar="${bar}-"
        i=$((i + 1))
    done

    printf "\r  %s  [%s] %3d%%  |  %d / %d" "$CURRENT_FRAME" "$bar" "$pct" "$current" "$total"
}

show_done() {
    local total="$1"
    local bar=""
    local i=0
    while [ "$i" -lt "$BAR_WIDTH" ]; do
        bar="${bar}#"
        i=$((i + 1))
    done
    printf "\r  ( o,o )  ( o,o )  ( o,o )    [%s] 100%%  |  %d / %d\n\n" \
        "$bar" "$total" "$total"
}

clear_line() {
    printf "\r%${LINE_WIDTH}s\r" ""
}

# returns file size in bytes
# tries GNU stat first (git bash / linux), then BSD stat (macos), then wc fallback
get_size_bytes() {
    local file="$1"
    stat -c "%s" "$file" 2>/dev/null \
        || stat -f "%z" "$file" 2>/dev/null \
        || wc -c < "$file" 2>/dev/null \
        || echo 0
}

# counts folder levels between ROOT_DIR and the file
get_depth() {
    local filepath="$1"
    local relative="${filepath#${ROOT_DIR}/}"
    relative="${relative#/}"
    # count / separators = number of folder levels
    local slashes
    slashes=$(printf '%s' "$relative" | tr -cd '/' | wc -c | tr -d ' ')
    echo "$slashes"
}

# detects versioning suffix anywhere in the path
# order matters - check specific patterns before -00 or it'll match -001 etc
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

# wraps value in double quotes, escapes internal double quotes
csv_escape() {
    local val="$1"
    printf '"%s"' "${val//\"/\"\"}"
}

# main

print_header
echo "  Scanning: $ROOT_DIR"
echo ""
echo "  Counting files..."

# pass 1 - count total files so we can show a real progress bar
total_files=0
spinner_tick=0
while IFS= read -r -d '' filepath; do
    total_files=$((total_files + 1))
    spinner_tick=$((spinner_tick + 1))
    if [ "$((spinner_tick % 10))" -eq 0 ]; then
        show_spinner "$total_files"
    fi
done < <(find "$ROOT_DIR" -type f -print0)

clear_line
echo "  Processing files..."

# write CSV header
printf 'File Type,File Name,File Path,Size (MB),Depth,Status\n' > "$OUTPUT"

# pass 2 - process files
file_count=0

while IFS= read -r -d '' filepath; do
    filename=$(basename "$filepath")

    extension="${filename##*.}"
    if [ "$extension" = "$filename" ]; then
        extension="(no ext)"
    else
        extension=".${extension}"
    fi

    size_bytes=$(get_size_bytes "$filepath")
    size_mb=$(awk "BEGIN { printf \"%.2f\", ${size_bytes:-0} / 1048576 }")

    depth=$(get_depth "$filepath")
    status=$(get_status "$filepath")

    printf '%s,%s,%s,%s,%s,%s\n' \
        "$(csv_escape "$extension")" \
        "$(csv_escape "$filename")" \
        "$(csv_escape "$filepath")" \
        "$size_mb" \
        "$depth" \
        "$(csv_escape "$status")" >> "$OUTPUT"

    file_count=$((file_count + 1))

    if [ "$((file_count % 10))" -eq 0 ]; then
        show_bar "$file_count" "$total_files"
    fi

done < <(find "$ROOT_DIR" -type f -print0)

show_done "$file_count"

echo "Found $file_count files"
echo "Report saved to $OUTPUT"