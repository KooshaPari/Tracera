from pheno.llm.optimization import (
    ProviderOption,
    ProviderSelector,
    QuantizationLevel,
    build_preference_payload,
)


def test_selector_prioritises_better_quantisation_over_minor_throughput_gain() -> None:
    selector = ProviderSelector()

    options = [
        ProviderOption(
            slug="openrouter/provider-bf16",
            prompt_price_per_1k=2.0,
            completion_price_per_1k=2.0,
            throughput_tokens_per_s=230.0,
            quantization=QuantizationLevel.BF16,
        ),
        ProviderOption(
            slug="openrouter/provider-fp8",
            prompt_price_per_1k=1.0,
            completion_price_per_1k=1.0,
            throughput_tokens_per_s=220.0,
            quantization=QuantizationLevel.FP8,
        ),
    ]

    scores = selector.score_options(options)

    assert scores[0].option.slug == "openrouter/provider-fp8"
    assert scores[0].composite > scores[1].composite


def test_selector_uses_quality_overrides() -> None:
    selector = ProviderSelector()

    options = [
        ProviderOption(
            slug="openrouter/fp8",
            prompt_price_per_1k=0.9,
            completion_price_per_1k=0.9,
            throughput_tokens_per_s=250.0,
            quantization=QuantizationLevel.FP8,
            reliability_score=0.9,
        ),
        ProviderOption(
            slug="openrouter/int4",
            prompt_price_per_1k=0.8,
            completion_price_per_1k=0.8,
            throughput_tokens_per_s=260.0,
            quantization=QuantizationLevel.INT4,
        ),
    ]

    scores = selector.score_options(
        options,
        predicted_quality={
            "openrouter/int4": 0.6,  # penalise due to poor hallucination rate
        },
    )

    assert scores[0].option.slug == "openrouter/fp8"
    assert scores[0].composite > scores[1].composite


def test_build_preference_payload_includes_quantisation_and_limits() -> None:
    selector = ProviderSelector()
    options = [
        ProviderOption(
            slug="provider/a",
            prompt_price_per_1k=0.5,
            completion_price_per_1k=0.5,
            throughput_tokens_per_s=400.0,
            quantization=QuantizationLevel.FP8,
        ),
        ProviderOption(
            slug="provider/b",
            prompt_price_per_1k=0.7,
            completion_price_per_1k=0.7,
            throughput_tokens_per_s=500.0,
            quantization=QuantizationLevel.FP16,
        ),
    ]

    scores = selector.score_options(options)
    preference = build_preference_payload(scores)
    payload = preference.as_dict()

    assert payload["order"][0] == "provider/a"
    assert payload["quantizations"] == ["fp8", "fp16"]
    assert payload["max_price"]["prompt"] == 0.5
    assert payload["sort"] == "price"
