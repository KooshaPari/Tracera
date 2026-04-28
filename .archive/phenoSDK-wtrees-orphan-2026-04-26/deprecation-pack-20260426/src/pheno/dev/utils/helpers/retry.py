"""
Retry and backoff helpers for resilient integration tests.
"""



class WaitStrategy:
    """
    Wait strategies for retry delays.
    """

    @staticmethod
    def immediate() -> float:
        """
        No wait.
        """
        return 0.0

    @staticmethod
    def linear(attempt: int, base_delay: float = 1.0) -> float:
        """Linear backoff: delay × attempt."""
        return base_delay * attempt

    @staticmethod
    def exponential(
        attempt: int,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
    ) -> float:
        """
        Exponential backoff capped at max_delay.
        """
        delay = base_delay * (2 ** (attempt - 1))
        return min(delay, max_delay)

    @staticmethod
    def fibonacci(attempt: int, base_delay: float = 1.0) -> float:
        """
        Fibonacci backoff sequence.
        """

        def fib(n: int) -> int:
            if n <= 1:
                return n
            a, b = 0, 1
            for _ in range(n - 1):
                a, b = b, a + b
            return b

        return base_delay * fib(attempt)


def is_connection_error(error: str) -> bool:
    """
    Check if an error message indicates a connection failure.
    """
    connection_keywords: list[str] = [
        "connection refused",
        "connection reset",
        "connection timeout",
        "network unreachable",
        "host unreachable",
        "timeout",
        "timed out",
        "connection error",
        "connection failed",
        "broken pipe",
        "cannot connect",
        "httpstatuserror",
        "server error",
        "530",
        "502",
        "503",
        "504",
        "500",
    ]
    error_lower = error.lower()
    return any(keyword in error_lower for keyword in connection_keywords)


__all__ = ["WaitStrategy", "is_connection_error"]
