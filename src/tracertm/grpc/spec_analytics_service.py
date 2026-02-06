"""gRPC SpecAnalytics service implementation."""

from __future__ import annotations

import asyncio
from typing import Any

import grpc

from tracertm.proto.tracertm.v1 import tracertm_pb2, tracertm_pb2_grpc
from tracertm.services import spec_analytics_service

ISO_29148_COMPLIANCE_THRESHOLD = 0.80


def _build_ears_patterns(ears_analysis: dict[str, Any]) -> list[tracertm_pb2.EARSPattern]:
    pattern_type = str(ears_analysis.get("pattern_type", "") or "")
    confidence = float(ears_analysis.get("confidence", 0.0) or 0.0)
    matched = bool(ears_analysis.get("is_valid", False))
    if not pattern_type:
        return []
    return [
        tracertm_pb2.EARSPattern(
            type=pattern_type,
            matched=matched,
            confidence=confidence,
        )
    ]


def _build_odc_classification(requirement_text: str) -> tracertm_pb2.ODCClassification:
    classification = spec_analytics_service.spec_analytics_service.classify_defect(requirement_text)
    return tracertm_pb2.ODCClassification(
        defect_type=str(classification.defect_type),
        trigger=str(classification.trigger),
        impact=str(classification.impact),
        qualifier=classification.qualifier or "",
        age=classification.age or "",
        source=classification.source or "",
        confidence=float(classification.confidence),
    )


def _build_spec_analysis_result(
    spec_id: str,
    requirement_text: str,
    analysis: dict[str, Any],
) -> tracertm_pb2.SpecAnalysisResult:
    quality_analysis = analysis.get("quality_analysis", {}) or {}
    ears_analysis = analysis.get("ears_analysis", {}) or {}
    quality_score = float(quality_analysis.get("overall_score", 0.0) or 0.0)
    quality_grade = str(quality_analysis.get("grade", "") or "")
    recommendations = list(quality_analysis.get("improvement_priority", []) or [])

    return tracertm_pb2.SpecAnalysisResult(
        spec_id=spec_id,
        compliant_with_iso=quality_score >= ISO_29148_COMPLIANCE_THRESHOLD,
        ears_patterns=_build_ears_patterns(ears_analysis),
        odc_classification=_build_odc_classification(requirement_text),
        formal_verification=tracertm_pb2.FormalVerificationResult(
            is_verifiable=False,
            logical_formula="",
            contradictions=[],
            ambiguities=[],
        ),
        recommendations=recommendations,
        quality_score=quality_score,
        quality_grade=quality_grade,
    )


class SpecAnalyticsService(tracertm_pb2_grpc.SpecAnalyticsServiceServicer):
    """Spec analytics gRPC service backed by spec_analytics_service."""

    async def AnalyzeSpec(
        self,
        request: tracertm_pb2.AnalyzeSpecRequest,
        context: grpc.aio.ServicerContext,
    ) -> tracertm_pb2.AnalyzeSpecResponse:
        if not request.content:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "content is required")

        analysis = await asyncio.to_thread(spec_analytics_service.analyze_requirement, request.content)
        result = _build_spec_analysis_result(request.spec_id, request.content, analysis)
        return tracertm_pb2.AnalyzeSpecResponse(result=result)

    async def BatchAnalyzeSpecs(
        self,
        request: tracertm_pb2.BatchAnalyzeSpecsRequest,
        context: grpc.aio.ServicerContext,
    ) -> tracertm_pb2.BatchAnalyzeSpecsResponse:
        if not request.requests:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "requests is required")

        results: list[tracertm_pb2.SpecAnalysisResult] = []
        for req in request.requests:
            if not req.content:
                await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "content is required")
            analysis = await asyncio.to_thread(spec_analytics_service.analyze_requirement, req.content)
            results.append(_build_spec_analysis_result(req.spec_id, req.content, analysis))

        return tracertm_pb2.BatchAnalyzeSpecsResponse(results=results)

    async def ValidateISO29148(
        self,
        request: tracertm_pb2.ValidateISO29148Request,
        context: grpc.aio.ServicerContext,
    ) -> tracertm_pb2.ValidateISO29148Response:
        if not request.content:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "content is required")

        analysis = await asyncio.to_thread(spec_analytics_service.analyze_requirement, request.content)
        quality_analysis = analysis.get("quality_analysis", {}) or {}
        quality_score = float(quality_analysis.get("overall_score", 0.0) or 0.0)
        recommendations = list(quality_analysis.get("improvement_priority", []) or [])
        return tracertm_pb2.ValidateISO29148Response(
            compliant_with_iso=quality_score >= ISO_29148_COMPLIANCE_THRESHOLD,
            recommendations=recommendations,
        )

    async def GetEARSPatterns(
        self,
        request: tracertm_pb2.GetEARSPatternsRequest,
        context: grpc.aio.ServicerContext,
    ) -> tracertm_pb2.GetEARSPatternsResponse:
        if not request.content:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "content is required")

        analysis = await asyncio.to_thread(spec_analytics_service.analyze_requirement, request.content)
        ears_analysis = analysis.get("ears_analysis", {}) or {}
        patterns = _build_ears_patterns(ears_analysis)
        return tracertm_pb2.GetEARSPatternsResponse(ears_patterns=patterns)
