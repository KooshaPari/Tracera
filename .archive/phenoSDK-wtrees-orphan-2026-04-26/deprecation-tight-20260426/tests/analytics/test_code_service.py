from pathlib import Path

import pytest

from pheno.analytics import CodeAnalyticsOptions, analyze_codebase

TEST_DATA = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "sample_project"


@pytest.mark.asyncio
async def test_analyze_codebase_smoke(tmp_path):
    report = await analyze_codebase(
        TEST_DATA,
        options=CodeAnalyticsOptions(
            include_patterns=("*.py",),
        ),
    )

    assert report.complexity.total_lines > 0
    assert report.dependencies.external_packages is not None
    assert report.dependencies.dependency_graph is not None
