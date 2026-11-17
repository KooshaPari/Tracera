#!/usr/bin/env python3
"""Local fixtures only: no server, container, network or Cloudflare calls."""

import importlib.util
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location(
    "validator", ROOT / "scripts/verify-caddy-public.py"
)
if spec is None or spec.loader is None:
    raise ImportError("cannot load the Caddy validator fixture")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)
HOST = "tracera.pheno.studio"
SITE = """%s {
 basic_auth {
 user fakehash
 }
 header {
 X-Frame-Options DENY
 }
 reverse_proxy tracera-server:8080
}
"""


class ReviewTests(unittest.TestCase):
    def test_https_forms(self):
        for address in [
            HOST,
            HOST + ":443",
            "https://" + HOST,
            "https://" + HOST + ":443",
            "{$TRACERA_PUBLIC_HOSTNAME}",
        ]:
            validator.check(SITE % address, HOST)

    def test_http_or_other_listener_rejected(self):
        for address in [
            "http://" + HOST,
            HOST + ":80",
            ":443",
            "https://other.invalid",
            HOST + ",http://" + HOST,
        ]:
            with self.assertRaises(ValueError, msg=address):
                validator.check(SITE % address, HOST)

    def test_unrelated_or_disabled_auth_rejected(self):
        for text in [
            (SITE % HOST).replace(" basic_auth", " # basic_auth"),
            SITE % ("http://" + HOST) + SITE % HOST,
            (SITE % HOST)
            .replace(" basic_auth", " handle /admin {\n basic_auth")
            .replace(" header {", " }\n header {"),
            (SITE % HOST).replace(" basic_auth", " tls off\n basic_auth"),
            "{\n auto_https off\n}\n" + SITE % HOST,
        ]:
            with self.assertRaises(ValueError):
                validator.check(text, HOST)

    def test_restricted_auth_matchers_rejected(self):
        for directive in [
            "basic_auth /admin/*",
            "basic_auth @private",
            "forward_auth /admin/* auth:9090",
            "forward_auth @private auth:9090",
            "jwt /admin/*",
        ]:
            with self.assertRaises(ValueError, msg=directive):
                validator.check((SITE % HOST).replace("basic_auth", directive), HOST)

    def test_unqualified_auth_forms(self):
        for directive in [
            "basic_auth bcrypt",
            "basic_auth argon2id",
            "forward_auth auth:9090",
            "jwt",
        ]:
            validator.check((SITE % HOST).replace("basic_auth", directive), HOST)

    def test_prod_order_and_no_post_exit_success(self):
        makefile = (ROOT / "Makefile").read_text()
        a = makefile.index("task-prod:")
        recipe = makefile[a : makefile.index("\n\n", a)]
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "Makefile"
            p.write_text(
                ".PHONY: task-prod stack task-tunnel-status task-run-server\n"
                + recipe
                + """
stack:
	@echo MOCK_STACK
task-tunnel-status:
	@echo MOCK_STATUS
task-run-server:
	@echo MOCK_SERVER_EXIT
	@exit $(CODE)
"""
            )
            for code in [0, 7]:
                result = subprocess.run(
                    [
                        "make",
                        "--no-print-directory",
                        "-f",
                        str(p),
                        "task-prod",
                        "CODE=" + str(code),
                    ],
                    text=True,
                    capture_output=True,
                    cwd=d,
                )
                self.assertEqual(result.returncode == 0, code == 0)
                out = result.stdout
                self.assertLess(out.index("MOCK_STACK"), out.index("MOCK_STATUS"))
                self.assertLess(
                    out.index("MOCK_STATUS"), out.index("starting tracera-server")
                )
                self.assertLess(
                    out.index("starting tracera-server"), out.index("MOCK_SERVER_EXIT")
                )
                self.assertNotIn("are up", out)
                self.assertEqual(out.splitlines()[-1], "MOCK_SERVER_EXIT")


if __name__ == "__main__":
    unittest.main()
