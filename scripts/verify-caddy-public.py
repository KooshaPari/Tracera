#!/usr/bin/env python3
"""Conservative single-site static check, not a live TLS or authentication probe.

Complex/imported configurations require review rather than a guessed pass.
"""

import os
import shlex
from pathlib import Path


def site_addresses(parts, hostname):
    if parts[-1:] != ["{"]:
        raise ValueError("expected one explicit HTTPS site block")
    addresses = "".join(parts[:-1]).split(",")
    allowed = {
        hostname,
        hostname + ":443",
        "https://" + hostname,
        "https://" + hostname + ":443",
    }
    if not addresses or any(a not in allowed for a in addresses):
        raise ValueError("site must name the requested hostname using HTTPS/443 only")
    return addresses


def site_wide_auth(parts):
    # Only known unqualified forms count. Named/path matchers and unknown forms
    # fail closed, even if the directive appears directly inside the site block.
    if parts[0] == "basic_auth":
        return parts in (
            ["basic_auth", "{"],
            ["basic_auth", "bcrypt", "{"],
            ["basic_auth", "argon2id", "{"],
        )
    if parts[0] == "jwt":
        return parts == ["jwt", "{"]
    if parts[0] != "forward_auth" or len(parts) != 3 or parts[-1] != "{":
        return False
    return not parts[1].startswith(("/", "@", "*"))


def directives(text, hostname):
    for line in text.replace("{$TRACERA_PUBLIC_HOSTNAME}", hostname).splitlines():
        parts = shlex.split(line, comments=True)
        if not parts:
            continue
        if parts[0] in {"import", "auto_https"} or parts[:2] == ["tls", "off"]:
            raise ValueError("imports, auto_https overrides and tls off require review")
        yield parts


def check(text, hostname):
    depth = sites = 0
    found = set()
    for parts in directives(text, hostname):
        if depth == 0:
            site_addresses(parts, hostname)
            sites += 1
        elif depth == 1:
            found.update(site_features(parts))
        depth += parts.count("{") - parts.count("}")
        if depth < 0:
            raise ValueError("unbalanced Caddy blocks")
    if depth or sites != 1 or found != {"auth", "proxy", "headers"}:
        raise ValueError(
            "require one balanced HTTPS site with site-wide auth, headers and backend proxy"
        )


def site_features(parts):
    if site_wide_auth(parts):
        yield "auth"
    if parts[:2] == ["reverse_proxy", "tracera-server:8080"]:
        yield "proxy"
    if parts[:2] == ["header", "{"]:
        yield "headers"


if __name__ == "__main__":
    import sys

    try:
        check(
            (
                Path(__file__).resolve().parent.parent / "deploy/selfhost/Caddyfile"
            ).read_text(),
            os.environ["TRACERA_PUBLIC_HOSTNAME"],
        )
    except (ValueError, KeyError) as exc:
        print("Caddy public HTTPS validation failed: " + str(exc), file=sys.stderr)
        raise SystemExit(1) from exc
    print("Caddy public HTTPS/auth configuration validated (not a live probe)")
