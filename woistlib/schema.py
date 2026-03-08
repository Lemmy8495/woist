import time


RESULT_SCHEMA_VERSION = "1.0.0"


def wrap_results(results: list[dict]) -> dict:
    return {
        "schema_version": RESULT_SCHEMA_VERSION,
        "generated_at_unix": int(time.time()),
        "result_count": len(results),
        "results": results,
    }

