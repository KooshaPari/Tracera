import tempfile
import unittest
from pathlib import Path

from pheno.infra.port_registry import PortRegistry


class TestPortRegistry(unittest.TestCase):
    def setUp(self):
        # Use a temp directory for registry to avoid touching user home
        self.tmpdir = tempfile.TemporaryDirectory()
        self.registry = PortRegistry(config_dir=Path(self.tmpdir.name))

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_register_and_lookup(self):
        self.registry.register_service("svc-a", 12345, pid=111)
        self.assertEqual(self.registry.is_port_registered(12345), "svc-a")
        self.assertEqual(self.registry.get_canonical_port("svc-a"), 12345)

    def test_unregister(self):
        self.registry.register_service("svc-b", 20000, pid=222)
        ok = self.registry.unregister_service("svc-b")
        self.assertTrue(ok)
        self.assertIsNone(self.registry.is_port_registered(20000))


if __name__ == "__main__":
    unittest.main()
