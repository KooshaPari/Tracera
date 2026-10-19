"""Disposable non-secret fixtures. Fake docker permits only version/ps/up argv."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

binary = Path(sys.argv[1]).resolve()
results = []
with tempfile.TemporaryDirectory(prefix="tracera-d04-") as scratch:
    base = Path(scratch)
    tools = base / "tools"
    tools.mkdir()
    docker = tools / "docker"
    docker.write_text(
        "#!/bin/sh\nprintf '%s\\n' \"$*\" >> \"$FIXTURE_CALLS\"\ncase \"$*\" in\n'compose version'|*' ps'|*' up -d') exit 0;;\n*) exit 97;;\nesac\n"
    )
    docker.chmod(0o700)
    for case, body in [
        ("valid", "POSTGRES_PASSWORD=nonsecret-sentinel\nCUSTOM=keep\n"),
        ("invalid", "CUSTOM=nonsecret-sentinel\n"),
        ("absent", None),
        ("empty", 'POSTGRES_PASSWORD=""\n'),
    ]:
        root = base / case
        root.mkdir()
        (root / "docker-compose.local.yml").write_text("services: {}\n")
        envfile = root / ".env.local"
        if body is not None:
            envfile.write_text(body)
        calls = root / "calls"
        home = root / "home"
        home.mkdir()
        env = {"PATH": str(tools), "HOME": str(home), "FIXTURE_CALLS": str(calls)}
        run = subprocess.run(
            [str(binary), "--root", str(root), "--backend", "docker", "status"],
            cwd=root,
            env=env,
            capture_output=True,
            text=True,
        )
        assert run.returncode == (0 if case == "valid" else 1), (case, run.returncode)
        assert envfile.exists() == (body is not None)
        if body is not None:
            assert envfile.read_text() == body
        assert not any(home.iterdir())
        assert "nonsecret-sentinel" not in run.stdout + run.stderr
        assert calls.exists() == (case == "valid")
        results.append(
            {"case": case, "status": "PASS", "backend_invoked": calls.exists()}
        )
    # Invalid up must fail before backend execution and preserve the bytes.
    root = base / "invalid"
    calls = root / "calls"
    run = subprocess.run(
        [str(binary), "--root", str(root), "--backend", "docker", "up", "--no-wait"],
        cwd=root,
        env=env | {"FIXTURE_CALLS": str(calls)},
        capture_output=True,
        text=True,
    )
    assert run.returncode == 1 and not calls.exists()
    assert (root / ".env.local").read_text() == "CUSTOM=nonsecret-sentinel\n"
    results.append({"case": "invalid-up-preserved", "status": "PASS"})
    # Bundle layout resolution must not create application data directories.
    root = base / "bundled"
    bundle = root / "tracera-bundle"
    bundle.mkdir(parents=True)
    (bundle / "docker-compose.bundle.yml").write_text("services: {}\n")
    home = root / "home"
    home.mkdir()
    run = subprocess.run(
        [str(binary), "--root", str(root), "--backend", "docker", "status"],
        cwd=root,
        env=env | {"HOME": str(home)},
        capture_output=True,
        text=True,
    )
    assert run.returncode == 1 and not any(home.iterdir())
    assert not (bundle / ".env.local").exists()
    results.append({"case": "bundle-status-no-writes", "status": "PASS"})
    # Up validates without replacing the operator's standalone symlink.
    root = base / "valid"
    envfile = root / ".env.local"
    target = root / "external"
    envfile.rename(target)
    envfile.symlink_to(target)
    run = subprocess.run(
        [str(binary), "--root", str(root), "--backend", "docker", "up", "--no-wait"],
        cwd=root,
        env=env | {"FIXTURE_CALLS": str(root / "calls")},
        capture_output=True,
        text=True,
    )
    assert run.returncode == 0
    assert envfile.is_symlink() and envfile.readlink() == target
    results.append(
        {"case": "standalone-up-symlink", "status": "PASS", "backend": "fake-only"}
    )
print(json.dumps(results, indent=2))
