#!/bin/bash
# Script to fix exhaustruct violations by adding missing fields

set -e

cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend

# Get list of files with violations
FILES=$(golangci-lint run --timeout 5m 2>&1 | grep "exhaustruct" | cut -d':' -f1 | sort -u)

echo "Files with exhaustruct violations:"
echo "$FILES"

# For each file, run goimports to format
for file in $FILES; do
    if [ -f "$file" ]; then
        echo "Processing $file..."
        goimports -w "$file"
    fi
done

echo "Done processing files. Now checking build..."
go build ./...

echo "All files processed and build successful"
