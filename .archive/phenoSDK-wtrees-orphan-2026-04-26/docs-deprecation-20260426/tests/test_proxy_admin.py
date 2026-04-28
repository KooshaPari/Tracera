import socket
import unittest

import aiohttp

from pheno.infra.proxy_gateway import ProxyServer


def get_free_port() -> int:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


class TestProxyAdmin(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.proxy_port = get_free_port()
        self.server = ProxyServer(proxy_port=self.proxy_port)
        await self.server.start()

    async def asyncTearDown(self):
        await self.server.stop()

    async def test_add_list_remove_deregister(self):
        async with aiohttp.ClientSession() as session:
            # Add upstream for tenant
            url = f"http://127.0.0.1:{self.proxy_port}/__admin__/tenant/upstream"
            async with session.post(
                url, json={"path_prefix": "/api", "port": 8080, "host": "localhost", "tenant": "t1"},
            ) as r:
                res = await r.json()
                self.assertTrue(res.get("ok"))

            # List upstreams for tenant
            url_list = f"http://127.0.0.1:{self.proxy_port}/__admin__/tenant/upstreams?tenant=t1"
            async with session.get(url_list) as r:
                listed = await r.json()
                self.assertTrue(listed.get("ok"))
                ups = listed.get("upstreams", [])
                self.assertTrue(
                    any(u.get("path_prefix") == "/api" and u.get("tenant") == "t1" for u in ups),
                )

            # Remove upstream
            async with session.delete(url, json={"path_prefix": "/api"}) as r:
                del_res = await r.json()
                self.assertTrue(del_res.get("ok"))

            # Add two upstreams then deregister tenant
            async with session.post(
                url, json={"path_prefix": "/a", "port": 8081, "tenant": "t1"},
            ) as r:
                await r.json()
            async with session.post(
                url, json={"path_prefix": "/b", "port": 8082, "tenant": "t1"},
            ) as r:
                await r.json()
            url_dereg = f"http://127.0.0.1:{self.proxy_port}/__admin__/tenant/deregister"
            async with session.post(url_dereg, json={"tenant": "t1"}) as r:
                dres = await r.json()
                self.assertTrue(dres.get("ok"))
                removed = dres.get("removed", [])
                self.assertTrue(set(removed) >= {"/a", "/b"})


if __name__ == "__main__":
    unittest.main()
