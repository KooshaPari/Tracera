import socket
import unittest

import aiohttp

from pheno.infra.fallback_site import FallbackServer


def get_free_port() -> int:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


class TestFallbackAdmin(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.port = get_free_port()
        self.server = FallbackServer(port=self.port)
        await self.server.start()

    async def asyncTearDown(self):
        await self.server.stop()

    async def test_update_list_delete(self):
        async with aiohttp.ClientSession() as session:
            # Update status for tenant/service
            url = f"http://127.0.0.1:{self.port}/__admin__/tenant/status"
            async with session.post(
                url,
                json={
                    "tenant": "t1",
                    "service_name": "svcA",
                    "status_message": "Downloading",
                    "state": "starting",
                },
            ) as r:
                res = await r.json()
                self.assertTrue(res.get("ok"))

            # List for tenant should include t1:svcA
            url_list = f"http://127.0.0.1:{self.port}/__admin__/tenant/status?tenant=t1"
            async with session.get(url_list) as r:
                listed = await r.json()
                services = listed.get("services", {})
                self.assertIn("t1:svcA", services)
                self.assertEqual(services["t1:svcA"].get("status_message"), "Downloading")

            # Delete specific service row
            async with session.delete(url, json={"tenant": "t1", "service_name": "svcA"}) as r:
                del_res = await r.json()
                self.assertTrue(del_res.get("ok"))

            # Now shouldn't be present
            async with session.get(url_list) as r:
                listed2 = await r.json()
                self.assertNotIn("t1:svcA", listed2.get("services", {}))


if __name__ == "__main__":
    unittest.main()
