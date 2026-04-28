from __future__ import annotations

from types import SimpleNamespace

import pytest

from pheno.infra import project_context as project_ctx_module


class DummyServiceInfo:
    def __init__(
        self,
        *,
        project: str,
        assigned_port: int,
        service_type: str,
        scope: str,
        resource_type: str,
        metadata: dict | None = None,
    ):
        self.project = project
        self.assigned_port = assigned_port
        self.service_type = service_type
        self.scope = scope
        self.resource_type = resource_type
        self.metadata = metadata or {}
        self.tunnel_hostname: str | None = None


class DummyRegistry:
    def __init__(self) -> None:
        self._services: dict[str, DummyServiceInfo] = {}

    def get_all_services(self) -> dict[str, DummyServiceInfo]:
        return dict(self._services)

    def get_service(self, service_name: str) -> DummyServiceInfo | None:
        return self._services.get(service_name)

    def update_service(self, service_name: str, metadata: dict | None = None) -> None:
        info = self._services.get(service_name)
        if info and metadata:
            info.metadata.update(metadata)


class DummyTunnelManager:
    def __init__(self, registry: DummyRegistry) -> None:
        self._registry = registry

    def start_tunnel(self, scoped_name: str, port: int, *, domain: str | None = None):
        hostname = f"{scoped_name}.test"
        info = self._registry.get_service(scoped_name)
        if info:
            info.tunnel_hostname = hostname
        return SimpleNamespace(hostname=hostname, port=port, domain=domain)


class DummyServiceInfraManager:
    def __init__(self, *, domain: str | None = None, config_dir: str | None = None) -> None:
        self.domain = domain
        self.config_dir = config_dir
        self.registry = DummyRegistry()
        self.allocator = SimpleNamespace(registry=self.registry)
        self.tunnel_manager = DummyTunnelManager(self.registry)
        self._next_port = 5000

    def allocate_port(
        self,
        service_name: str,
        *,
        preferred_port: int | None = None,
        project: str,
        service_type: str,
        scope: str | None,
        resource_type: str,
        metadata: dict | None = None,
    ) -> int:
        port = preferred_port or self._next_port
        if preferred_port is None:
            self._next_port += 1
        info = DummyServiceInfo(
            project=project,
            assigned_port=port,
            service_type=service_type,
            scope=scope or ("project" if project else "local"),
            resource_type=resource_type,
            metadata=metadata,
        )
        self.registry._services[service_name] = info
        return port

    def cleanup(self, service_name: str) -> None:
        self.registry._services.pop(service_name, None)


class DummyResourceCoordinator:
    def __init__(self, *args, **kwargs) -> None:
        self._policies = {}

    async def initialize(self) -> None:
        return None

    async def shutdown(self) -> None:
        return None

    def set_resource_policy(self, policy) -> None:  # pragma: no cover - unused in tests
        self._policies[policy.resource_type] = policy

    async def request_resource(self, *args, **kwargs):  # pragma: no cover - unused in tests
        return True, {}

    def release_resource(self, *args, **kwargs) -> bool:  # pragma: no cover - unused in tests
        return True

    async def get_project_resources(self) -> list[dict]:
        return []

    async def get_resource_status(self, *args, **kwargs):  # pragma: no cover - unused in tests
        return {}

    async def validate_project_dependencies(self) -> tuple[bool, list[str]]:
        return True, []

    async def get_coordination_status(self) -> dict:
        return {}


class DummyProxyServer:
    def __init__(self, *, proxy_port: int, fallback_port: int) -> None:
        self.proxy_port = proxy_port
        self.fallback_port = fallback_port
        self.routes: dict[str, dict[str, object]] = {}
        self.started = False

    async def start(self) -> None:
        self.started = True

    async def stop(self) -> None:
        self.started = False

    def add_upstream(
        self,
        path_prefix: str,
        *,
        port: int,
        host: str = "localhost",
        service_name: str | None = None,
        tenant: str | None = None,
    ) -> None:
        self.routes[path_prefix] = {
            "port": port,
            "host": host,
            "service_name": service_name,
            "tenant": tenant,
        }

    def remove_upstream(self, path_prefix: str) -> bool:
        return self.routes.pop(path_prefix, None) is not None


@pytest.fixture(autouse=True)
def patch_project_context(monkeypatch):
    monkeypatch.setattr(project_ctx_module, "ServiceInfraManager", DummyServiceInfraManager)
    monkeypatch.setattr(project_ctx_module, "ResourceCoordinator", DummyResourceCoordinator)
    monkeypatch.setattr(project_ctx_module, "ProxyServer", DummyProxyServer)
    yield


def test_allocate_and_tunnel_registers_default_route():
    ctx = project_ctx_module.ProjectInfraContext("demo", enable_proxy=True)

    result = ctx.allocate_and_tunnel("api")

    assert result["port"] == 5000
    assert ctx.proxy_server is not None
    assert "/demo/api" in ctx.proxy_server.routes
    route = ctx.proxy_server.routes["/demo/api"]
    assert route["host"] == "localhost"
    assert route["tenant"] == "demo"
    assert route["service_name"] == "demo-api"
    assert ctx._auto_registered_routes["api"] == "/demo/api"


def test_manual_route_can_disable_default_registration():
    ctx = project_ctx_module.ProjectInfraContext("demo", enable_proxy=True)
    ctx.allocate_and_tunnel("api")

    assert "/demo/api" in ctx.proxy_server.routes  # type: ignore[union-attr]

    ctx.register_proxy_route(
        path_prefix="/custom/api",
        port=7001,
        host="127.0.0.1",
        service_name="api",
        disable_default_route=True,
    )

    assert "/demo/api" not in ctx.proxy_server.routes  # type: ignore[union-attr]
    assert ctx._auto_registered_routes.get("api") is None
    assert ctx._auto_route_disabled_services == {"api"}
    assert ctx.proxy_server.routes["/custom/api"]["port"] == 7001  # type: ignore[index]

    # Trigger another allocation; default route should remain disabled.
    ctx.allocate_and_tunnel("api")
    assert "/demo/api" not in ctx.proxy_server.routes  # type: ignore[union-attr]


def test_register_default_helpers_use_template():
    ctx = project_ctx_module.ProjectInfraContext(
        "demo",
        enable_proxy=True,
        routing_template={"host": "127.0.0.1", "path_template": "/svc/{service}"},
    )

    port_a = ctx.allocate_port("alpha")
    port_b = ctx.allocate_port("beta")

    ctx.register_default_routes(["alpha", "beta"])

    assert ctx.proxy_server.routes["/svc/alpha"]["port"] == port_a  # type: ignore[index]
    assert ctx.proxy_server.routes["/svc/beta"]["port"] == port_b  # type: ignore[index]
    assert ctx.proxy_server.routes["/svc/alpha"]["host"] == "127.0.0.1"  # type: ignore[index]

    ctx.register_service_route("gamma", port=9001)
    assert ctx.proxy_server.routes["/demo/gamma"]["port"] == 9001  # type: ignore[index]
