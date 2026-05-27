"""Tests for traceability matrix CSV export API."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from tests.test_constants import HTTP_OK
from tracertm.api.deps import auth_guard, get_db
from tracertm.api.main import app

client = TestClient(app)


class TestTraceMatrixExport:
    """Test traceability matrix CSV export endpoint."""

    @patch("tracertm.api.routers.analysis.ensure_project_access")
    @patch("tracertm.api.routers.analysis.enforce_rate_limit")
    def test_export_trace_matrix_csv(self, _mock_rate: object, _mock_access: object) -> None:
        """CSV export returns attachment with matrix content."""
        mock_session = AsyncMock()

        async def override_db() -> AsyncMock:
            return mock_session

        def override_auth() -> dict[str, str]:
            return {"role": "user", "sub": "user123"}

        app.dependency_overrides[get_db] = override_db
        app.dependency_overrides[auth_guard] = override_auth

        mock_matrix = MagicMock()

        try:
            with patch(
                "tracertm.api.routers.analysis.traceability_matrix_service.TraceabilityMatrixService",
            ) as mock_service_class:
                mock_service = MagicMock()
                mock_service.generate_matrix = AsyncMock(return_value=mock_matrix)
                mock_service.export_matrix_csv = AsyncMock(
                    return_value='"Source","Feature A"\n"Req 1","traces_to"',
                )
                mock_service_class.return_value = mock_service

                response = client.get("/api/v1/analysis/trace-matrix/export?project_id=proj1")
                assert response.status_code == HTTP_OK
                assert response.headers["content-type"].startswith("text/csv")
                disposition = response.headers.get("content-disposition", "")
                assert "attachment" in disposition
                assert "tracera-matrix" in disposition
                assert "Req 1" in response.text
        finally:
            app.dependency_overrides.clear()
