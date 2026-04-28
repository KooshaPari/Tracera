import pytest


@pytest.mark.asyncio
async def test_sentence_transformers_provider(monkeypatch):
    from pheno.vector.providers import factory
    from pheno.vector.providers import sentence_transformers as st_module

    class FakeModel:
        def __init__(self, *args, **kwargs):
            pass

        def get_sentence_embedding_dimension(self):
            return 3

        def encode(self, texts, **kwargs):
            if isinstance(texts, str):
                return [0.1, 0.2, 0.3]
            return [[0.1, 0.2, 0.3] for _ in texts]

    monkeypatch.setattr(st_module, "SentenceTransformer", FakeModel, raising=False)

    service = factory.get_embedding_service("sentence-transformers", model_name="fake-model")
    result = await service.generate_embedding("hello world")

    assert pytest.approx(result.embedding) == [0.1, 0.2, 0.3]
    assert result.model.startswith("sentence-transformers")

    batch = await service.generate_batch_embeddings(["a", "b"])
    assert len(batch.embeddings) == 2
    assert batch.embeddings[0] == [0.1, 0.2, 0.3]


def test_sentence_transformers_missing(monkeypatch):
    from pheno.vector.providers import factory
    from pheno.vector.providers import sentence_transformers as st_module

    monkeypatch.setattr(st_module, "SentenceTransformer", None, raising=False)

    with pytest.raises(RuntimeError):
        factory.get_embedding_service("sentence-transformers")


@pytest.mark.asyncio
async def test_litellm_provider(monkeypatch):
    from pheno.vector.providers import factory
    from pheno.vector.providers import litellm_provider as llm_module

    class FakeResponse:
        def __init__(self, embeddings):
            self.data = [{"embedding": emb} for emb in embeddings]

    class FakeLiteLLM:
        async def aembedding(self, **payload):
            texts = payload.get("input", [])
            embeddings = [[float(i + 1) for _ in range(2)] for i in range(len(texts))]
            return FakeResponse(embeddings)

    fake = FakeLiteLLM()
    monkeypatch.setattr(llm_module, "litellm", fake, raising=False)
    monkeypatch.setattr(factory, "litellm", fake, raising=False)

    service = factory.get_embedding_service("litellm", model="unit-test-embedding")
    single = await service.generate_embedding("hello")
    assert single.embedding == [1.0, 1.0]
    assert single.model == "unit-test-embedding"

    batch = await service.generate_batch_embeddings(["a", "b", "c"])
    assert len(batch.embeddings) == 3
    assert batch.embeddings[2] == [3.0, 3.0]


def test_litellm_missing(monkeypatch):
    from pheno.vector.providers import factory
    from pheno.vector.providers import litellm_provider as llm_module

    monkeypatch.setattr(llm_module, "litellm", None, raising=False)
    monkeypatch.setattr(factory, "litellm", None, raising=False)

    with pytest.raises(RuntimeError):
        factory.get_embedding_service("litellm", model="test")
