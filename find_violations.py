import pathlib

allowlist = {}
with pathlib.Path("config/loc-allowlist.txt").open("r") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) == 2:
            allowlist[parts[0]] = int(parts[1])

violations = []
for file_path, limit in allowlist.items():
    if pathlib.Path(file_path).exists():
        try:
            with pathlib.Path(file_path).open("r", errors="ignore") as f:
                lines = f.readlines()
                count = len(lines)
                if count > limit:
                    violations.append((file_path, count, limit))
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

violations.sort(key=lambda x: x[1] - x[2], reverse=True)
for v in violations:
    print(f"{v[0]}: {v[1]} > {v[2]} (diff: {v[1] - v[2]})")
