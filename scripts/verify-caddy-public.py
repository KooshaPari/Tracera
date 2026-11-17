#!/usr/bin/env python3
"""Conservative static check of the repository's single-site Caddy template.

Complex/imported configurations require a separate review, not a guessed pass.
This proves configuration intent only, not certificate issuance or live reachability.
"""
import os
import re
import shlex
from pathlib import Path


def check(text, hostname):
    text = text.replace('{$TRACERA_PUBLIC_HOSTNAME}', hostname)
    # Strip quoted strings/comments before counting braces. No arbitrary env expansion.
    lines = []
    for line in text.splitlines():
        parts = shlex.split(line, comments=True)
        if parts:
            lines.append(parts)
    depth = 0
    sites = []
    auth = proxy = headers = False
    for parts in lines:
        if parts[0] in {'import', 'auto_https'} or parts[:2] == ['tls', 'off']:
            raise ValueError('imports, auto_https overrides and tls off require review')
        if depth == 0:
            if parts[-1:] != ['{']:
                raise ValueError('expected one explicit HTTPS site block')
            addresses = ''.join(parts[:-1]).split(',')
            allowed = {hostname, hostname + ':443', 'https://' + hostname, 'https://' + hostname + ':443'}
            if not addresses or any(a not in allowed for a in addresses):
                raise ValueError('site must name the requested hostname using HTTPS/443 only')
            sites.append(addresses)
        elif depth == 1:
            auth |= parts[0] in {'forward_auth', 'basic_auth', 'jwt'}
            proxy |= parts[:2] == ['reverse_proxy', 'tracera-server:8080']
            headers |= parts[:2] == ['header', '{']
        depth += parts.count('{') - parts.count('}')
        if depth < 0:
            raise ValueError('unbalanced Caddy blocks')
    if depth or len(sites) != 1 or not (auth and proxy and headers):
        raise ValueError('require one balanced HTTPS site with site-wide auth, headers and backend proxy')


if __name__ == '__main__':
    import sys
    try:
        check((Path(__file__).resolve().parent.parent / 'deploy/selfhost/Caddyfile').read_text(), os.environ['TRACERA_PUBLIC_HOSTNAME'])
    except (ValueError, KeyError) as exc:
        print('Caddy public HTTPS validation failed: ' + str(exc), file=sys.stderr)
        raise SystemExit(1)
    print('Caddy public HTTPS/auth configuration validated (not a live probe)')
