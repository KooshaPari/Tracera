import socket
import unittest

import aiohttp
from aiohttp import web

from pheno.infra.fallback_site import FallbackServer
from pheno.infra.proxy_gateway import ProxyServer


def get_free_port() -> int:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


async def start_dummy_upstream(port: int):
    app = web.Application()

    async def handle_hello(request):
        return web.Response(text="OK")

    app.router.add_get("/hello", handle_hello)
    app.router.add_get("/t/hello", handle_hello)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", port)
    await site.start()
    return runner, site


class TestProxyRouting(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.fallback_port = get_free_port()
        self.proxy_port = get_free_port()
        self.upstream_port = get_free_port()

        self.fallback = FallbackServer(port=self.fallback_port)
        await self.fallback.start()
        self.proxy = ProxyServer(
            proxy_port=self.proxy_port,
            fallback_port=self.fallback_port,
            fallback_server=self.fallback,
        )
        await self.proxy.start()
        self.up_runner, self.up_site = await start_dummy_upstream(self.upstream_port)

    async def asyncTearDown(self):
        await self.proxy.stop()
        await self.fallback.stop()
        await self.up_runner.cleanup()

    async def test_routing_to_upstream_and_fallback(self):
        async with aiohttp.ClientSession() as session:
            # Add upstream at /t
            url_admin = f"http://127.0.0.1:{self.proxy_port}/__admin__/tenant/upstream"
            async with session.post(
                url_admin,
                json={
                    "path_prefix": "/t",
                    "port": self.upstream_port,
                    "host": "127.0.0.1",
                    "tenant": "tt",
                },
            ) as r:
                res = await r.json()
                self.assertTrue(res.get("ok"))
            # Mark healthy immediately to bypass initial health gate
            self.assertIsNotNone(self.proxy.middleware.health_check)
            self.proxy.middleware.health_check.service_health["t"] = True

            # Should route to upstream
            url = f"http://127.0.0.1:{self.proxy_port}/t/hello"
            async with session.get(url) as r:
                txt = await r.text()
                self.assertEqual(r.status, 200)
                self.assertEqual(txt, "OK")

            # Remove upstream
            async with session.delete(url_admin, json={"path_prefix": "/t"}) as r:
                _ = await r.json()

            # Now same URL should be served by fallback (HTML)
            async with session.get(url) as r:
                txt = await r.text()
                self.assertIn(r.status, (200, 404, 503))
                self.assertIn("<html", txt.lower())
