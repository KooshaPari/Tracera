import subprocess, json, os, re
ANSI = re.compile(rb'\x1b\[[0-9;]*[A-Za-z]')
cmd = ["gh", "api", "repos/KooshaPari/Tracera/git/ref/heads/main"]
r = subprocess.run(cmd, capture_output=True, timeout=60)
print("RC:", r.returncode)
clean = ANSI.sub(b'', r.stdout).decode("utf-8", "replace")
data = json.loads(clean)
print("PARSED:", data["object"]["sha"])
