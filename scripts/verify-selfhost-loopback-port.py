#!/usr/bin/env python3
"""Fail closed unless tracera-server publishes exactly one safe loopback port."""

from __future__ import annotations

import re
import sys
from pathlib import Path


def die(message: str) -> "NoReturn":
    print(f"self-host loopback validation failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


if len(sys.argv) != 2:
    die("usage: verify-selfhost-loopback-port.py <compose-file>")

path = Path(sys.argv[1])
lines = path.read_text(encoding="utf-8").splitlines()

starts = [i for i, line in enumerate(lines) if line.rstrip() == "  tracera-server:"]
if len(starts) != 1:
    die(f"expected exactly one tracera-server service, found {len(starts)}")

start = starts[0] + 1
end = len(lines)
for i in range(start, len(lines)):
    line = lines[i]
    if not line.strip() or line.lstrip().startswith("#"):
        continue
    if indent(line) <= 2:
        end = i
        break

service = lines[start:end]
port_headers = [
    i
    for i, line in enumerate(service)
    if indent(line) == 4 and line.strip() == "ports:"
]
if len(port_headers) != 1:
    die(f"expected exactly one ports block in tracera-server, found {len(port_headers)}")

ports_start = port_headers[0] + 1
ports_end = len(service)
for i in range(ports_start, len(service)):
    line = service[i]
    if not line.strip() or line.lstrip().startswith("#"):
        continue
    if indent(line) <= 4:
        ports_end = i
        break

entries = [
    line.strip()
    for line in service[ports_start:ports_end]
    if line.strip() and not line.lstrip().startswith("#")
]

if len(entries) != 1:
    die(f"expected exactly one published port entry, found {len(entries)}: {entries!r}")

entry = entries[0]
if not entry.startswith("- "):
    die(f"ports entry must use single short-form list syntax, got {entry!r}")

value = entry[2:].strip()
if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
    value = value[1:-1]

if value != "127.0.0.1:8080:8080":
    die(
        "only 127.0.0.1:8080:8080 is allowed; "
        f"got {value!r}. Extra IPs, long-form mappings, and broad binds are rejected."
    )

# Reject a second ports key hidden deeper in the same service.
if sum(1 for line in service if re.match(r"^\s+ports:\s*$", line)) != 1:
    die("multiple ports keys are not allowed in tracera-server")

print("self-host loopback publication validated")
