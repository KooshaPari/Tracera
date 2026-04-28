from __future__ import annotations

from typing import TYPE_CHECKING

from ..entities.tunnel import Tunnel
from ..events.tunnel_events import TunnelClosed, TunnelEstablished

if TYPE_CHECKING:
    from ..entities.service import Service
    from ..value_objects.port_number import PortNumber


class TunnelPlanner:
    """
    Coordinates tunnel lifecycle relative to a service.
    """

    @staticmethod
    def establish(
        service: Service,
        tunnel_id: str,
        source_port: PortNumber,
        target_host: str,
        target_port: PortNumber,
        description: str = "",
    ) -> tuple[Tunnel, TunnelEstablished]:
        if service.tunnel(tunnel_id):
            raise ValueError(f"Tunnel {tunnel_id} already exists")

        if not service.port(source_port):
            raise ValueError(
                f"Source port {int(source_port)} must be reserved before establishing a tunnel",
            )

        tunnel = Tunnel(
            tunnel_id=tunnel_id,
            service_id=service.service_id,
            source_port=source_port,
            target_host=target_host,
            target_port=target_port,
            description=description,
        )
        tunnel.activate()
        service.track_tunnel(tunnel)

        event = TunnelEstablished(
            service_id=service.service_id,
            tunnel_id=tunnel_id,
            source_port=source_port,
            target_host=target_host,
            target_port=target_port,
        )
        return tunnel, event

    @staticmethod
    def close(
        service: Service,
        tunnel_id: str,
        reason: str | None = None,
    ) -> TunnelClosed:
        tunnel = service.remove_tunnel(tunnel_id)
        tunnel.deactivate()
        return TunnelClosed(
            service_id=service.service_id,
            tunnel_id=tunnel.tunnel_id,
            reason=reason,
        )
