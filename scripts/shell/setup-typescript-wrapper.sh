#!/bin/bash

# Setup TypeScript 7 native preview wrapper for backward compatibility
# This script creates a tsc.js wrapper that calls tsgo (the native TypeScript compiler)

set -e

echo "Setting up TypeScript 7 native preview wrappers..."

# Function to create tsc wrapper
create_tsc_wrapper() {
    local ts_dir=$1

    if [ ! -d "$ts_dir/bin" ]; then
        return
    fi

    if [ ! -f "$ts_dir/bin/tsgo.js" ]; then
        return
    fi

    echo "Creating tsc wrapper in $ts_dir/bin"

    cat > "$ts_dir/bin/tsc.js" << 'EOF'
#!/usr/bin/env node

import getExePath from "#getExePath";
import { execFileSync } from "node:child_process";

const exe = getExePath();

try {
    execFileSync(exe, process.argv.slice(2), { stdio: "inherit" });
}
catch (e) {
    if (e.status) {
        process.exitCode = e.status;
    }
    else {
        throw e;
    }
}
EOF

    chmod +x "$ts_dir/bin/tsc.js"

    # Update package.json to include tsc and tsserver bins
    if [ -f "$ts_dir/package.json" ]; then
        node -e "
            const fs = require('fs');
            const path = '$ts_dir/package.json';
            const pkg = JSON.parse(fs.readFileSync(path, 'utf8'));
            pkg.bin = pkg.bin || {};
            pkg.bin.tsc = './bin/tsc.js';
            pkg.bin.tsserver = './bin/tsc.js';
            fs.writeFileSync(path, JSON.stringify(pkg, null, 4));
        " 2>/dev/null || true
    fi
}

# Find all typescript installations
find . -name "typescript" -type d -path "*/node_modules/typescript" ! -path "*/node_modules/typescript/node_modules/*" 2>/dev/null | while read -r ts_dir; do
    create_tsc_wrapper "$ts_dir"
done

echo "TypeScript 7 native preview wrappers setup complete!"
