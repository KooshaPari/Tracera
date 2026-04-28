import socket
import unittest
from collections import deque
from unittest import mock

import aiohttp

from pheno.infra.fallback_site import FallbackServer
from pheno.infra.proxy_gateway import ProxyServer


def get_free_port() -> int:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


class TestProxySteps(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.fallback = None
        self.proxy = None
        try:
            self.fallback_port = get_free_port()
            self.proxy_port = get_free_port()
        except OSError as exc:  # pragma: no cover - environment dependent
            self.skipTest(f"Socket allocation not permitted: {exc}")

        self.fallback = FallbackServer(port=self.fallback_port)
        try:
            await self.fallback.start()
        except OSError as exc:  # pragma: no cover - environment dependent
            await self.fallback.stop()
            self.skipTest(f"Fallback server cannot start in sandbox: {exc}")

        self.proxy = ProxyServer(
            proxy_port=self.proxy_port,
            fallback_port=self.fallback_port,
            fallback_server=self.fallback,
        )
        try:
            await self.proxy.start()
        except OSError as exc:  # pragma: no cover - environment dependent
            await self.fallback.stop()
            self.skipTest(f"Proxy server cannot start in sandbox: {exc}")

    async def asyncTearDown(self):
        if getattr(self, "proxy", None):
            await self.proxy.stop()  # type: ignore[func-returns-value]
        if getattr(self, "fallback", None):
            await self.fallback.stop()  # type: ignore[func-returns-value]

    async def test_proxy_routes_to_fallback_with_steps_before_upstream_ready(self):
        # Emit a step via fallback admin endpoint
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

            # Before any upstream is added, request a path on proxy; should render fallback HTML with step
            url = f"http://127.0.0.1:{self.proxy_port}/svcA/anything"
            async with session.get(url) as r:
                html = await r.text()
                self.assertIn(r.status, (200, 404, 503))
                self.assertIn(step_text, html)


class DummyFallback:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def update_service_status(self, **payload):
        self.calls.append(payload)


class TestProxyHealthVisibility(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.fallback = DummyFallback()
        self.proxy = ProxyServer(fallback_server=self.fallback)
        self.monitor = self.proxy._health_monitor
        self.registry = self.proxy._registry

        self._health_results = deque()
        self._last_health = False

        def fake_check(host, port, timeout):
            if self._health_results:
                self._last_health = self._health_results.popleft()
            return self._last_health

        patcher = mock.patch(
            "pheno.infra.proxy_gateway.server.health.check_tcp_health",
            side_effect=fake_check,
        )
        self._check_patch = patcher
        patcher.start()

    async def asyncTearDown(self) -> None:
        self._check_patch.stop()

    async def test_snapshot_and_event_logging(self) -> None:
        self.proxy.add_upstream(
            "/svc",
            port=1234,
            host="127.0.0.1",
            service_name="svcA",
            tenant="tenantA",
        )

        self._health_results.extend([True, False])

        with mock.patch("pheno.infra.proxy_gateway.server.events.event_logger.info") as info_mock:
            await self.monitor._poll_upstreams()
            await self.monitor._poll_upstreams()

        snapshot = self.proxy.health_snapshot
        upstreams = snapshot["upstreams"]
        self.assertEqual(len(upstreams), 1)
        state = upstreams[0]
        self.assertEqual(state["tenant"], "tenantA")
        self.assertEqual(state["service"], "svcA")
        self.assertFalse(state["healthy"])
        self.assertGreater(state["last_checked"], 0)
        self.assertEqual(state["last_checked"], state["last_changed"])

        # Event logger receives structured payloads for each transition.
        self.assertGreaterEqual(info_mock.call_count, 2)
        first_call = info_mock.call_args_list[0]
        second_call = info_mock.call_args_list[1]
        self.assertEqual(first_call.args[0], "proxy.health_transition")
        self.assertTrue(first_call.kwargs["healthy"])
        self.assertFalse(first_call.kwargs["previous_healthy"])
        self.assertEqual(second_call.args[0], "proxy.health_transition")
        self.assertFalse(second_call.kwargs["healthy"])
        self.assertTrue(second_call.kwargs["previous_healthy"])

        # Fallback status updates are issued on transitions.
        self.assertEqual(len(self.fallback.calls), 2)
        self.assertEqual(self.fallback.calls[-1]["health_status"], "Unhealthy")


if __name__ == "__main__":
    unittest.main()
