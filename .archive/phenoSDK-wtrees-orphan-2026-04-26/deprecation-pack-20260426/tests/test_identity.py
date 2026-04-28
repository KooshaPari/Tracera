import os
import unittest

from pheno.infra.utils.identity import (
    base_ports_from_env,
    get_project_id,
    stable_offset,
)


class TestIdentity(unittest.TestCase):
    def test_get_project_id_default(self):
        default = get_project_id("default-project")
        self.assertIsInstance(default, str)
        self.assertTrue(default)

    def test_stable_offset_deterministic(self):
        pid = "example-project"
        o1 = stable_offset(pid)
        o2 = stable_offset(pid)
        self.assertEqual(o1, o2)
        self.assertTrue(0 <= o1 < 50)

    def test_base_ports_from_env(self):
        orig_fb = os.environ.get("KINFRA_BASE_FALLBACK_PORT")
        orig_px = os.environ.get("KINFRA_BASE_PROXY_PORT")
        try:
            os.environ["KINFRA_BASE_FALLBACK_PORT"] = "9050"
            os.environ["KINFRA_BASE_PROXY_PORT"] = "9150"
            fb, px = base_ports_from_env()
            self.assertEqual(fb, 9050)
            self.assertEqual(px, 9150)
        finally:
            if orig_fb is None:
                os.environ.pop("KINFRA_BASE_FALLBACK_PORT", None)
            else:
                os.environ["KINFRA_BASE_FALLBACK_PORT"] = orig_fb
            if orig_px is None:
                os.environ.pop("KINFRA_BASE_PROXY_PORT", None)
            else:
                os.environ["KINFRA_BASE_PROXY_PORT"] = orig_px


if __name__ == "__main__":
    unittest.main()
