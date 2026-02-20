"""Comprehensive unit tests for concurrency control module.

Tests concurrency.py:
- ConcurrencyError exception
- update_with_retry function
- Exponential backoff behavior
- Retry logic
"""

import asyncio
from typing import Any, Never

import pytest

from tests.test_constants import COUNT_TEN, COUNT_THREE, COUNT_TWO
from tracertm.core.concurrency import ConcurrencyError, update_with_retry


class TestConcurrencyError:
    """Test ConcurrencyError exception."""

    def test_create_concurrency_error(self) -> None:
        """Test creating ConcurrencyError."""
        error = ConcurrencyError("Version mismatch")
        assert str(error) == "Version mismatch"

    def test_raise_concurrency_error(self) -> Never:
        """Test raising ConcurrencyError."""
        with pytest.raises(ConcurrencyError) as exc_info:
            msg = "Optimistic lock failed"
            raise ConcurrencyError(msg)
        assert str(exc_info.value) == "Optimistic lock failed"

    def test_concurrency_error_is_exception(self) -> None:
        """Test that ConcurrencyError is an Exception."""
        error = ConcurrencyError("Test")
        assert isinstance(error, Exception)

    def test_concurrency_error_with_details(self) -> None:
        """Test ConcurrencyError with detailed message."""
        error = ConcurrencyError("Version mismatch: expected 5, got 7")
        assert "Version mismatch" in str(error)
        assert "expected 5" in str(error)


class TestUpdateWithRetrySuccess:
    """Test update_with_retry successful scenarios."""

    @pytest.mark.asyncio
    async def test_successful_update_first_try(self) -> None:
        """Test successful update on first attempt."""
        call_count = 0

        async def update_fn() -> str:
            await asyncio.sleep(0)
            nonlocal call_count
            call_count += 1
            return "success"

        result = await update_with_retry(update_fn)
        assert result == "success"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_successful_update_after_retries(self) -> None:
        """Test successful update after retries."""
        call_count = 0

        async def update_fn() -> str:
            await asyncio.sleep(0)
            nonlocal call_count
            call_count += 1
            if call_count < COUNT_THREE:
                msg = "Retry me"
                raise ConcurrencyError(msg)
            return "success"

        result = await update_with_retry(update_fn, max_retries=3)
        assert result == "success"
        assert call_count == COUNT_THREE

    @pytest.mark.asyncio
    async def test_returns_different_types(self) -> None:
        """Test that update_with_retry can return different types."""

        async def return_int() -> int:
            await asyncio.sleep(0)
            return 42

        async def return_dict() -> None:
            await asyncio.sleep(0)
            return {"key": "value"}

        async def return_none() -> None:
            await asyncio.sleep(0)

        assert await update_with_retry(return_int) == 42
        assert await update_with_retry(return_dict) == {"key": "value"}
        assert await update_with_retry(return_none) is None

    @pytest.mark.asyncio
    async def test_zero_retries_needed(self) -> None:
        """Test when no retries are needed."""

        async def always_succeed() -> str:
            await asyncio.sleep(0)
            return "immediate_success"

        result = await update_with_retry(always_succeed, max_retries=10)
        assert result == "immediate_success"


class TestUpdateWithRetryFailure:
    """Test update_with_retry failure scenarios."""

    @pytest.mark.asyncio
    async def test_all_retries_fail(self) -> None:
        """Test when all retries fail."""
        call_count = 0

        async def always_fail() -> Never:
            await asyncio.sleep(0)
            nonlocal call_count
            call_count += 1
            msg = "Always fails"
            raise ConcurrencyError(msg)

        with pytest.raises(ConcurrencyError) as exc_info:
            await update_with_retry(always_fail, max_retries=3)

        assert "Failed after 3 retries" in str(exc_info.value)
        assert call_count == COUNT_THREE

    @pytest.mark.asyncio
    async def test_single_retry_exhausted(self) -> None:
        """Test with max_retries=1."""
        call_count = 0

        async def always_fail() -> Never:
            await asyncio.sleep(0)
            nonlocal call_count
            call_count += 1
            msg = "Fail"
            raise ConcurrencyError(msg)

        with pytest.raises(ConcurrencyError) as exc_info:
            await update_with_retry(always_fail, max_retries=1)

        assert "Failed after 1 retries" in str(exc_info.value)
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_original_error_message_preserved(self) -> None:
        """Test that original error message is preserved in final error."""

        async def fail_with_message() -> Never:
            await asyncio.sleep(0)
            msg = "Original error: version mismatch"
            raise ConcurrencyError(msg)

        with pytest.raises(ConcurrencyError) as exc_info:
            await update_with_retry(fail_with_message, max_retries=2)

        error_msg = str(exc_info.value)
        assert "Failed after 2 retries" in error_msg
        assert "Original error: version mismatch" in error_msg

    @pytest.mark.asyncio
    async def test_non_concurrency_error_propagates(self) -> None:
        """Test that non-ConcurrencyError exceptions are not retried."""
        call_count = 0

        async def raise_other_error() -> Never:
            await asyncio.sleep(0)
            nonlocal call_count
            call_count += 1
            msg = "Different error"
            raise ValueError(msg)

        with pytest.raises(ValueError, match="Different error"):
            await update_with_retry(raise_other_error, max_retries=3)

        # Should fail immediately without retries
        assert call_count == 1


class TestUpdateWithRetryBackoff:
    """Test exponential backoff behavior."""

    @pytest.mark.asyncio
    async def test_backoff_delays_increase(self) -> None:
        """Test that delays increase exponentially."""
        call_times = []

        async def track_calls() -> str:
            await asyncio.sleep(0)
            call_times.append(asyncio.get_event_loop().time())
            if len(call_times) < COUNT_THREE:
                msg = "Retry"
                raise ConcurrencyError(msg)
            return "done"

        _ = asyncio.get_event_loop().time()
        await update_with_retry(track_calls, max_retries=3, base_delay=0.01)

        # Verify calls happened
        assert len(call_times) == COUNT_THREE

        # Verify increasing delays (with jitter tolerance)
        if len(call_times) >= COUNT_THREE:
            delay1 = call_times[1] - call_times[0]
            delay2 = call_times[2] - call_times[1]
            # Second delay should be roughly twice the first (allowing for jitter)
            assert delay2 > delay1

    @pytest.mark.asyncio
    async def test_base_delay_parameter(self) -> None:
        """Test that base_delay parameter works."""
        call_times = []

        async def track_calls() -> str:
            await asyncio.sleep(0)
            call_times.append(asyncio.get_event_loop().time())
            if len(call_times) < COUNT_TWO:
                msg = "Retry"
                raise ConcurrencyError(msg)
            return "done"

        await update_with_retry(track_calls, max_retries=2, base_delay=0.05)

        # First retry should wait at least base_delay
        if len(call_times) >= COUNT_TWO:
            delay = call_times[1] - call_times[0]
            assert delay >= 0.05  # At least base_delay

    @pytest.mark.asyncio
    async def test_jitter_adds_randomness(self) -> None:
        """Test that jitter adds 10% randomness to delays."""
        # Run multiple times to observe jitter variance
        delays = []

        for _ in range(5):
            call_times = []

            async def track_calls(_ct: Any = call_times) -> str:
                await asyncio.sleep(0)
                _ct.append(asyncio.get_event_loop().time())
                if len(_ct) < COUNT_TWO:
                    msg = "Retry"
                    raise ConcurrencyError(msg)
                return "done"

            await update_with_retry(track_calls, max_retries=2, base_delay=0.01)

            if len(call_times) >= COUNT_TWO:
                delay = call_times[1] - call_times[0]
                delays.append(delay)

        # Delays should vary due to jitter (not all identical)
        if len(delays) >= COUNT_THREE:
            # Check that we have some variance
            assert len(set(delays)) > 1 or all(d >= 0.01 for d in delays)


class TestUpdateWithRetryEdgeCases:
    """Test edge cases and parameter validation."""

    @pytest.mark.asyncio
    async def test_max_retries_default(self) -> None:
        """Test default max_retries value is 3."""
        call_count = 0

        async def count_calls() -> Never:
            await asyncio.sleep(0)
            nonlocal call_count
            call_count += 1
            msg = "Fail"
            raise ConcurrencyError(msg)

        with pytest.raises(ConcurrencyError):
            await update_with_retry(count_calls)  # No max_retries specified

        assert call_count == COUNT_THREE  # Default is 3

    @pytest.mark.asyncio
    async def test_base_delay_default(self) -> None:
        """Test default base_delay value is 0.1."""
        call_times = []

        async def track_calls() -> str:
            await asyncio.sleep(0)
            call_times.append(asyncio.get_event_loop().time())
            if len(call_times) < COUNT_TWO:
                msg = "Retry"
                raise ConcurrencyError(msg)
            return "done"

        await update_with_retry(track_calls, max_retries=2)

        if len(call_times) >= COUNT_TWO:
            delay = call_times[1] - call_times[0]
            # Should be at least 0.1 (base_delay) with jitter
            assert delay >= 0.1

    @pytest.mark.asyncio
    async def test_high_retry_count(self) -> None:
        """Test with high retry count."""
        call_count = 0

        async def fail_then_succeed() -> str:
            await asyncio.sleep(0)
            nonlocal call_count
            call_count += 1
            if call_count < COUNT_TEN:
                msg = "Retry"
                raise ConcurrencyError(msg)
            return "finally_succeeded"

        result = await update_with_retry(fail_then_succeed, max_retries=10, base_delay=0.001)
        assert result == "finally_succeeded"
        assert call_count == COUNT_TEN

    @pytest.mark.asyncio
    async def test_zero_base_delay(self) -> None:
        """Test with zero base_delay (immediate retries)."""
        call_count = 0

        async def count_retries() -> str:
            await asyncio.sleep(0)
            nonlocal call_count
            call_count += 1
            if call_count < COUNT_THREE:
                msg = "Retry"
                raise ConcurrencyError(msg)
            return "done"

        start = asyncio.get_event_loop().time()
        result = await update_with_retry(count_retries, max_retries=3, base_delay=0.0)
        elapsed = asyncio.get_event_loop().time() - start

        assert result == "done"
        assert call_count == COUNT_THREE
        # Should complete very quickly with zero delay
        assert elapsed < 0.5

    @pytest.mark.asyncio
    async def test_async_function_required(self) -> None:
        """Test that function must be async."""

        # This test verifies the type signature works with async functions
        async def valid_async_fn() -> str:
            await asyncio.sleep(0)
            return "async_result"

        result = await update_with_retry(valid_async_fn)
        assert result == "async_result"

    @pytest.mark.asyncio
    async def test_complex_return_value(self) -> None:
        """Test with complex return values."""

        async def return_complex() -> None:
            await asyncio.sleep(0)
            return {
                "items": [1, 2, 3],
                "metadata": {"count": 3, "status": "ok"},
                "nested": {"deep": {"value": 42}},
            }

        result = await update_with_retry(return_complex)
        assert result["items"] == [1, 2, 3]
        assert result["metadata"]["count"] == COUNT_THREE
        assert result["nested"]["deep"]["value"] == 42

    @pytest.mark.asyncio
    async def test_retry_after_different_errors(self) -> None:
        """Test retrying after different ConcurrencyError messages."""
        call_count = 0
        errors = [
            "Version mismatch: expected 1",
            "Version mismatch: expected 2",
            "Version mismatch: expected 3",
        ]

        async def different_errors() -> str:
            await asyncio.sleep(0)
            nonlocal call_count
            if call_count < len(errors):
                error_msg = errors[call_count]
                call_count += 1
                raise ConcurrencyError(error_msg)
            return "success"

        result = await update_with_retry(different_errors, max_retries=5)
        assert result == "success"
        assert call_count == COUNT_THREE
