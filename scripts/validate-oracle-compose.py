#!/usr/bin/env python3
"""Validate a disposable rich-dashboard oracle checkout before Compose launch.

This is intentionally dependency-free and read-only.  It does not invoke Docker
or parse/modify a Compose file; it gates the two hazards found during recovery:
missing nginx assets and accidental publication on Grapheon's port 8080.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

RESERVED_HOST_PORT = 8080
PORT_RE = re.compile(r"(?:^|[\"'\s-])(?:127\.0\.0\.1:)?(\d{2,5}):\d{1,5}(?:[\"'\s]|$)")
PUBLISHED_PORT_RE = re.compile(
    r"^[\s-]*[\"'](?:(?P<host>[^:\"']+):)?(?P<port>\d{2,5}):\d{1,5}[\"']\s*$",
    re.MULTILINE,
)
CONTAINER_NAME_RE = re.compile(r"^\s*container_name:\s*([^#\s]+)", re.MULTILINE)
SERVICE_RE = re.compile(r"^  ([a-zA-Z0-9_.-]+):\s*$", re.MULTILINE)
BUILD_CONTEXT_RE = re.compile(r"^\s*context:\s*([^#\s]+)", re.MULTILINE)
BUILD_DOCKERFILE_RE = re.compile(r"^\s*dockerfile:\s*([^#\s]+)", re.MULTILINE)
SERVICE_BLOCK_RE = re.compile(r"^  ([a-zA-Z0-9_.-]+):\s*$([\s\S]*?)(?=^  [a-zA-Z0-9_.-]+:\s*$|\Z)", re.MULTILINE)
UPSTREAM_RE = re.compile(r"^\s*upstream\s+([a-zA-Z0-9_.-]+)\s*\{", re.MULTILINE)
UPSTREAM_SERVER_RE = re.compile(r"^\s*server\s+([a-zA-Z0-9_.-]+):\d+", re.MULTILINE)
NETWORK_ALIAS_RE = re.compile(r"^\s*-\s+([a-zA-Z0-9_.-]+)\s*$", re.MULTILINE)


def validate_checkout(
    root: Path,
    compose: Path,
    *,
    http_only: bool = False,
    nginx_config: Path | None = None,
    project_root: Path | None = None,
    require_internal_network: bool = False,
) -> tuple[list[str], list[str]]:
    """Return (errors, observations) for *root* and its Compose text."""
    errors: list[str] = []
    observations: list[str] = []

    # Accept either a conventional nginx/ tree or the isolated artifact's
    # flat layout.  The latter keeps the evidence-copied configs immutable and
    # makes Compose mounts explicit relative to the override file.
    project_base = project_root or root
    nginx_root = nginx_config.parent if nginx_config else project_base
    nginx_conf = nginx_root / "nginx" / "nginx.conf"
    nginx_conf_d = nginx_root / "nginx" / "conf.d"
    if not nginx_conf.is_file():
        nginx_conf = nginx_root / "nginx.conf"
        nginx_conf_d = nginx_root / "conf.d"
    if not nginx_conf.is_file():
        errors.append(f"missing required nginx config: {nginx_conf}")
    if not nginx_conf_d.is_dir():
        errors.append(f"missing required nginx include directory: {nginx_conf_d}")

    if not compose.is_file():
        errors.append(f"Compose file not found: {compose}")
        return errors, observations

    text = compose.read_text(encoding="utf-8")
    if require_internal_network:
        if not re.search(r"^\s*internal:\s*true\s*$", text, re.MULTILINE):
            errors.append("required internal backend network is not declared")
        if not re.search(r"(?m)^\s*nginx:\s*$[\s\S]{0,400}?\bedge\b", text):
            errors.append("nginx service is not attached to the edge network")
        for service in ("go-backend", "python-backend"):
            if not re.search(
                rf"(?m)^\s*{re.escape(service)}:\s*$[\s\S]{{0,400}}?\bbackend\b",
                text,
            ):
                errors.append(f"{service} is not attached to the internal backend network")
    services = set(SERVICE_RE.findall(text))
    # Validate build inputs before launch. Compose reports these late and with
    # opaque errors; this gate makes an incomplete stable ref explicit.
    contexts = BUILD_CONTEXT_RE.findall(text)
    for context in contexts:
        context_path = (project_base / context).resolve()
        if not context_path.is_dir():
            errors.append(f"missing build context: {context} ({context_path})")
    build_contexts_checked = 0
    for _service, block in SERVICE_BLOCK_RE.findall(text):
        context_match = BUILD_CONTEXT_RE.search(block)
        if not context_match:
            continue
        context = context_match.group(1)
        dockerfile_match = BUILD_DOCKERFILE_RE.search(block)
        dockerfile = dockerfile_match.group(1) if dockerfile_match else "Dockerfile"
        dockerfile_path = (project_base / context / dockerfile).resolve()
        if not dockerfile_path.is_file():
            errors.append(f"missing build Dockerfile: {dockerfile} ({dockerfile_path})")
        else:
            ignore_file = (project_base / context / ".dockerignore").resolve()
            if ignore_file.is_file():
                ignored = ignore_file.read_text(encoding="utf-8", errors="replace")
                dockerfile_text = dockerfile_path.read_text(encoding="utf-8", errors="replace")
                for copy_line in re.findall(r"^COPY\s+(.+)$", dockerfile_text, re.MULTILINE):
                    sources = copy_line.split()[:-1]
                    for source in sources:
                        if source.startswith("--") or source.startswith("$"):
                            continue
                        if re.search(rf"(?m)^\s*{re.escape(source)}\s*$", ignored):
                            errors.append(
                                f"Dockerfile COPY source excluded by .dockerignore: {source}"
                            )
        build_contexts_checked += 1
    if contexts:
        observations.append(f"build contexts checked: {build_contexts_checked}")

    gateway = nginx_config or nginx_conf
    if gateway.is_file():
        gateway_text = gateway.read_text(encoding="utf-8")
        nginx_sources = [gateway_text]
        # nginx.conf includes conf.d at runtime. Validate mounted fragments so
        # a valid main file cannot mask an unresolvable upstream host.
        if nginx_conf_d.is_dir():
            nginx_sources.extend(
                path.read_text(encoding="utf-8", errors="replace")
                for path in sorted(nginx_conf_d.glob("*.conf"))
            )
        nginx_text = "\n".join(nginx_sources)
        upstreams = set(UPSTREAM_RE.findall(nginx_text))
        upstream_servers = set(UPSTREAM_SERVER_RE.findall(nginx_text))
        network_aliases = set()
        for _, block in SERVICE_BLOCK_RE.findall(text):
            network_aliases.update(NETWORK_ALIAS_RE.findall(block))
        missing_upstreams = sorted(upstream_servers - services - network_aliases)
        if missing_upstreams:
            errors.append(
                "nginx upstream hosts absent from Compose services or network aliases: "
                + ", ".join(missing_upstreams)
            )
        if upstreams:
            observations.append("nginx upstreams: " + ", ".join(sorted(upstreams)))
        if upstream_servers:
            observations.append("nginx upstream hosts: " + ", ".join(sorted(upstream_servers)))
        if http_only and re.search(r"(?:ssl_certificate|listen\s+443\s+ssl)", gateway_text):
            errors.append("HTTP-only mode cannot include TLS certificate or HTTPS directives")
        if http_only and re.search(r"/etc/nginx/certs|conf\.d/ssl", gateway_text):
            errors.append("HTTP-only mode cannot require an nginx cert mount")
    host_ports = [int(match.group(1)) for match in PORT_RE.finditer(text)]
    for match in PUBLISHED_PORT_RE.finditer(text):
        host = match.group("host")
        if host not in (None, "127.0.0.1"):
            errors.append(
                f"published host must be loopback, found {host}:{match.group('port')}"
            )
        if host is None:
            errors.append(f"published port must bind loopback: {match.group('port')}")
    if RESERVED_HOST_PORT in host_ports:
        errors.append("host port 8080 is reserved for Grapheon and must not be published")
    observations.append(
        "host ports: " + (", ".join(map(str, host_ports)) if host_ports else "none published")
    )

    names = CONTAINER_NAME_RE.findall(text)
    if names:
        observations.append("fixed container_name values: " + ", ".join(names))
        observations.append("fixed container names require an isolated project/container prefix")
    else:
        observations.append("fixed container_name values: none")
    return errors, observations


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkout", type=Path, help="oracle checkout to inspect")
    parser.add_argument(
        "--compose",
        type=Path,
        default=None,
        help="Compose file relative to checkout (default: docker-compose.yml)",
    )
    parser.add_argument(
        "--http-only",
        action="store_true",
        help="reject TLS directives/cert mounts; intended for disposable local smoke stacks",
    )
    parser.add_argument(
        "--nginx-config",
        type=Path,
        default=None,
        help="nginx config to inspect (default: checkout nginx config)",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Compose project root for relative build contexts and nginx assets",
    )
    parser.add_argument(
        "--require-internal-network",
        action="store_true",
        help="Require an internal backend network and edge-attached gateway",
    )
    args = parser.parse_args()
    root = args.checkout.resolve()
    compose = (args.compose or (root / "docker-compose.yml")).resolve()
    project_root = args.project_root.resolve() if args.project_root else root
    gateway = args.nginx_config.resolve() if args.nginx_config else None
    errors, observations = validate_checkout(
        root,
        compose,
        http_only=args.http_only,
        nginx_config=gateway,
        project_root=project_root,
        require_internal_network=args.require_internal_network,
    )
    for observation in observations:
        print(f"INFO: {observation}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 2
    print("OK: oracle checkout passes Compose safety gate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
