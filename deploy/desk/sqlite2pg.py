#!/usr/bin/env python3
"""Copy Tracera data from a sqlite file into Postgres (same table names, shared columns).
Usage: sqlite2pg.py <sqlite.db> <postgres-container> <database>  (credentials are read from the container env)
Truncates target tables first (staging use), copies via COPY, prints row counts both sides."""
import sqlite3, subprocess, sys, csv, io
db, ctr, pgdb = sys.argv[1], sys.argv[2], sys.argv[3]
def psql(sql, stdin=None):
    cmd = ["podman","exec","-i",ctr,"sh","-c",f'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d {pgdb} -Atc "$0"', sql]
    r = subprocess.run(cmd, input=stdin, capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr)
    return r.stdout.strip()
def copy_in(table, cols, data):
    cmd = ["podman","exec","-i",ctr,"sh","-c",
      f'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d {pgdb} -c "COPY {table} ({",".join(cols)}) FROM STDIN WITH (FORMAT csv, NULL \'\\N\')"']
    r = subprocess.run(cmd, input=data, capture_output=True, text=True)
    if r.returncode: raise SystemExit(f"{table}: {r.stderr}")
s = sqlite3.connect(db)
pgt = psql("select table_name from information_schema.tables where table_schema='public' and table_type='BASE TABLE'").split("\n")
st = {r[0] for r in s.execute("select name from sqlite_master where type='table'")}
tabs = [t for t in pgt if t in st and t != "_sqlx_migrations"]
order = ["canonical_projects","canonical_items","canonical_links"]
tabs.sort(key=lambda t: order.index(t) if t in order else -1)
psql("TRUNCATE " + ",".join(tabs) + " CASCADE")
ok = True
for t in tabs:
    pcols = psql(f"select column_name from information_schema.columns where table_name='{t}' and table_schema='public' order by ordinal_position").split("\n")
    scols = [r[1] for r in s.execute(f"pragma table_info({t})")]
    cols = [c for c in pcols if c in scols]
    buf = io.StringIO(); w = csv.writer(buf)
    n = 0
    extra = []
    if t == "teams" and "slug" in pcols and "slug" not in scols:
        extra = ["slug"]  # sqlite has no slug; derive from name (documented drift)
    for row in s.execute(f"select {','.join(cols)} from {t}"):
        row = [r"\N" if v is None else v for v in row]
        if extra:
            nm = row[cols.index("name")]
            row.append("-".join("".join(ch if ch.isalnum() else " " for ch in nm.lower()).split()))
        w.writerow(row); n += 1
    cols = cols + extra
    if n: copy_in(t, cols, buf.getvalue())
    pn = psql(f"select count(*) from {t}")
    flag = "OK" if int(pn) == n else "MISMATCH"
    ok &= flag == "OK"
    print(f"{t:28} sqlite={n:6} pg={pn:6} {flag}  (cols dropped: {sorted(set(scols)-set(pcols))})")
print("RESULT", "PASS" if ok else "FAIL")
