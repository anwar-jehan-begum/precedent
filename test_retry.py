from agent.retry import retry_with_backoff


attempts = 0


def test_function():

    global attempts

    attempts += 1

    print(f"Running attempt {attempts}")

    if attempts < 3:
        raise Exception("Temporary test error")

    return "SUCCESS"


result = retry_with_backoff(
    test_function,
    max_retries=3
)

print("\nFinal result:", result)