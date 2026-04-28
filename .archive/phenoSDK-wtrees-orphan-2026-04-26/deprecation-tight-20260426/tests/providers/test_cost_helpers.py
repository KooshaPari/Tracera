
import pytest

from pheno.providers import cost


def test_estimate_tokens_without_tiktoken(monkeypatch):
    monkeypatch.setattr(cost, "tiktoken", None)
    tokens = cost.estimate_tokens("hello world")
    assert tokens >= 1


def test_estimate_tokens_with_mock(monkeypatch):
    class MockEnc:
        def encode(self, text):
            return list(text)

    class MockModule:
        def encoding_for_model(self, model):
            return MockEnc()

        def get_encoding(self, name):
            return MockEnc()

    monkeypatch.setattr(cost, "tiktoken", MockModule())
    assert cost.estimate_tokens("ab") == 2


def test_estimate_completion_cost_without_litellm(monkeypatch):
    monkeypatch.setattr(cost, "completion_cost", None)
    assert cost.estimate_completion_cost("model", 10, 5) == 0.0


def test_estimate_completion_cost_with_mock(monkeypatch):
    monkeypatch.setattr(cost, "completion_cost", lambda **kwargs: 0.123)
    assert cost.estimate_completion_cost("model", 5, 5) == pytest.approx(0.123)
