import time


def retry_with_backoff(
    function,
    max_retries=3,
    initial_delay=1
):
    """
    Retry a function when a temporary error occurs.

    Delay:
    1 second → 2 seconds → 4 seconds
    """

    delay = initial_delay

    for attempt in range(max_retries):

        try:
            return function()

        except Exception as error:

            if attempt == max_retries - 1:
                raise error

            print(
                f"Attempt {attempt + 1} failed: {error}"
            )

            print(
                f"Retrying in {delay} second(s)..."
            )

            time.sleep(delay)

            delay *= 2