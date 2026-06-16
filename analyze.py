import os, re, json

# 1. Extract requirement IDs from spec docs
spec_files = [
    "FUNCTIONAL_REQUIREMENTS.md",
    "docs/FUNCTIONAL_REQUIREMENTS.md",
    "docs/05-requirements/FUNCTIONAL_REQUIREMENTS.md",
    "docs/unified-plan/04-REQUIREMENTS.md",
]
ids = set()
for path in spec_files:
    if not os.path.exists(path):
        continue
    c = open(path, "r", encoding="utf-8").read()
    for m in re.finditer(r"FR-[A-Z]+-\d+", c):
        ids.add(m.group(0))
    for m in re.finditer(r"FR-\d+\.\d+", c):
        ids.add(m.group(0))
    for m in re.finditer(r"NFR-\d+", c):
        ids.add(m.group(0))
ids = sorted(ids)
print(f"Total spec IDs: {len(ids)}")

# 2. Search codebase for references
found_ids = set()
roots = ["src", "backend", "frontend", "tests", "crates"]
for root in roots:
    if not os.path.exists(root):
        continue
    for dirpath, dirnames, filenames in os.walk(root):
        for fname in filenames:
            if not (fname.endswith(".py") or fname.endswith(".go") or fname.endswith(".ts") or fname.endswith(".tsx") or fname.endswith(".js") or fname.endswith(".jsx") or fname.endswith(".rs") or fname.endswith(".md")):
                continue
            fpath = os.path.join(dirpath, fname)
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as fh:
                    text = fh.read()
                for m in re.finditer(r"FR-[A-Z]+-\d+", text):
                    found_ids.add(m.group(0))
                for m in re.finditer(r"FR-\d+\.\d+", text):
                    found_ids.add(m.group(0))
                for m in re.finditer(r"NFR-\d+", text):
                    found_ids.add(m.group(0))
            except Exception:
                pass

print(f"Total found in codebase: {len(found_ids)}")

# 3. Determine gaps
zero_refs = [req_id for req_id in ids if req_id not in found_ids]
print(f"\nZero reference IDs: {len(zero_refs)}")
for z in zero_refs:
    print(z)

# 4. Write detailed report
results = {}
for req_id in ids:
    results[req_id] = {"found": req_id in found_ids}
with open("tmp_results.json", "w", encoding="utf-8") as fh:
    json.dump(results, fh, indent=2)
