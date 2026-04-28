"""Framework-Agnostic Middleware Stack Example.

Demonstrates using pheno.gateway.stack for composing middleware without ASGI/FastAPI
dependencies.
"""

import asyncio

from pheno.gateway.stack import add_gateway_stack


# Example handler (could be any async function)
async def my_handler(message: dict) -> dict:
    """
    Process a message and return a response.
    """
    print(f"Processing: {message}")
    await asyncio.sleep(0.1)  # Simulate work
    return {"status": "success", "echo": message}


# Wrap handler with gateway middleware stack
wrapped_handler = add_gateway_stack(
    my_handler,
    rate_limit={
        "max_requests": 10,
        "window_seconds": 60,
        "key_func": lambda msg: msg.get("user_id", "anonymous"),
    },
    timeout={"timeout_seconds": 5},
    retry={
        "max_retries": 2,
        "backoff_factor": 0.5,
    },
)


async def main():
    """
    Run example requests through the middleware stack.
    """
    print("Testing middleware stack...\n")

    # Test 1: Normal request
    print("1. Normal request:")
    result = await wrapped_handler({"user_id": "user123", "action": "test"})
    print(f"   Result: {result}\n")

    # Test 2: Multiple requests (rate limiting)
    print("2. Testing rate limiting (10 requests):")
    for i in range(12):
        try:
            result = await wrapped_handler({"user_id": "user456", "request": i})
            print(f"   Request {i+1}: OK")
        except Exception as e:
            print(f"   Request {i+1}: RATE LIMITED - {e}")
    print()

    # Test 3: Timeout
    print("3. Testing timeout:")

    async def slow_handler(message: dict) -> dict:
        await asyncio.sleep(10)  # Will timeout
        return {"status": "success"}

    slow_wrapped = add_gateway_stack(
        slow_handler,
        timeout={"timeout_seconds": 1},
    )

    try:
        await slow_wrapped({"action": "slow"})
    except Exception as e:
        print(f"   Timeout caught: {type(e).__name__}\n")

    print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
