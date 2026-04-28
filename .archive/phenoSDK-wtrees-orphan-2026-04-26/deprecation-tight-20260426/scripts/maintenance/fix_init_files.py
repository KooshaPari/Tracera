#!/usr/bin/env python3
import os
import re


def fix_file(filepath):
    try:
        with open(filepath) as f:
            content = f.read().strip()

        # Simple pattern to match and replace
        if content.startswith('""" \\') and r' module. \ """' in content:
            # Extract module name between backslash and space
            pattern = r'""" \\([a-zA-Z_][a-zA-Z0-9_]*) module\\. \\ """'
            match = re.search(pattern, content)
            if match:
                module_name = match.group(1)
                new_content = f'"""{module_name.title()} module."""\n\n'

                with open(filepath, "w") as f:
                    f.write(new_content)

                print(f"Fixed: {filepath} -> {module_name}")
                return True
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
    return False


def main():
    # Find and fix all files
    fixed_count = 0
    for root, dirs, files in os.walk("src"):
        for file in files:
            if file == "__init__.py":
                filepath = os.path.join(root, file)
                if fix_file(filepath):
                    fixed_count += 1

    print(f"Fixed {fixed_count} files")


if __name__ == "__main__":
    main()
