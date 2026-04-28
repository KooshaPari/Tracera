import socket
import unittest

import aiohttp

from pheno.infra.fallback_site import FallbackServer
from pheno.infra.proxy_gateway import ProxyServer


def get_free_port() -> int:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


class TestFallbackSteps(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.fallback_port = get_free_port()
        self.proxy_port = get_free_port()
        self.fallback = FallbackServer(port=self.fallback_port)
        await self.fallback.start()
        self.proxy = ProxyServer(
            proxy_port=self.proxy_port,
            fallback_port=self.fallback_port,
            fallback_server=self.fallback,
        )
        await self.proxy.start()

    async def asyncTearDown(self):
        await self.proxy.stop()
        await self.fallback.stop()

    async def test_emitted_steps_render_in_fallback_html(self):
        # Emit a step via admin endpoint (async to avoid blocking event loop)
        step_text = "Building service"
        async with aiohttp.ClientSession() as session:
            admin_url = f"http://127.0.0.1:{self.fallback_port}/__admin__/tenant/status"
            async with session.post(
                admin_url,
                json={
                    "tenant": "tt",
                    "service_name": "svcA",
                    "steps": [{"text": step_text, "status": "active"}],
                    "status_message": step_text,
                },
            ) as r:
                res = await r.json()
                self.assertTrue(res.get("ok"))

            # Request fallback root; the page should include the emitted step text
            url = f"http://127.0.0.1:{self.fallback_port}/"
            async with session.get(url) as r:
                html = await r.text()
                self.assertIn(r.status, (200, 503))
                self.assertIn(step_text, html)


if __name__ == "__main__":
    unittest.main()
