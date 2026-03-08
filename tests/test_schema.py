import unittest

from woistlib.schema import RESULT_SCHEMA_VERSION, wrap_results


class SchemaTest(unittest.TestCase):
    def test_wrap_results(self) -> None:
        payload = wrap_results([{"eingabe": "example.com"}])
        self.assertEqual(payload["schema_version"], RESULT_SCHEMA_VERSION)
        self.assertEqual(payload["result_count"], 1)
        self.assertEqual(payload["results"][0]["eingabe"], "example.com")


if __name__ == "__main__":
    unittest.main()

