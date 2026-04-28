from typing import Any

"""Integration tests for MLX model operations."""

import pytest
from infrastructure.mlx_integration import EmbeddingManager, MLXModelManager


class TestMLXIntegration:
    """Test MLX integration."""

    @pytest.fixture
    def mlx_manager(self) -> None:
        """Create MLX manager."""
        return MLXModelManager()

    def test_mlx_manager_initialization(self, mlx_manager: Any) -> None:
        """Test MLX manager initialization."""
        assert mlx_manager is not None
        assert mlx_manager.model_name == "katanemo/Arch-Router-1.5B"
        assert mlx_manager.model is None

    def test_mlx_manager_stats(self, mlx_manager: Any) -> None:
        """Test MLX manager statistics."""
        stats = mlx_manager.get_stats()
        assert "model_name" in stats
        assert "loaded" in stats
        assert stats["loaded"] is False

    @pytest.mark.skip(reason="Requires MLX installation and model download")
    def test_mlx_model_loading(self, mlx_manager: Any) -> None:
        """Test MLX model loading."""
        model, tokenizer = mlx_manager.load()
        assert model is not None
        assert tokenizer is not None
        assert mlx_manager.load_time is not None

    @pytest.mark.skip(reason="Requires MLX installation and model download")
    def test_mlx_inference(self, mlx_manager: Any) -> None:
        """Test MLX inference."""
        response = mlx_manager.infer(
            prompt="Select the best route for: process CSV data",
            max_tokens=10,
        )
        assert isinstance(response, str)
        assert len(response) > 0


class TestEmbeddingManager:
    """Test embedding manager."""

    @pytest.fixture
    def embedding_manager(self) -> None:
        """Create embedding manager."""
        return EmbeddingManager()

    def test_embedding_manager_initialization(self, embedding_manager: Any) -> None:
        """Test embedding manager initialization."""
        assert embedding_manager is not None
        assert embedding_manager.api_key is None

    @pytest.mark.skip(reason="Requires OpenAI API key")
    def test_embedding_generation(self, embedding_manager: Any) -> None:
        """Test embedding generation."""
        embedding_manager.api_key = "test-key"

        embedding = embedding_manager.generate_embedding("test text")
        assert isinstance(embedding, list)
        assert len(embedding) == 1536  # OpenAI embedding size

    @pytest.mark.skip(reason="Requires OpenAI API key")
    def test_batch_embedding_generation(self, embedding_manager: Any) -> None:
        """Test batch embedding generation."""
        embedding_manager.api_key = "test-key"

        texts = ["text1", "text2", "text3"]
        embeddings = embedding_manager.generate_embeddings_batch(texts)

        assert len(embeddings) == 3
        assert all(len(e) == 1536 for e in embeddings)
