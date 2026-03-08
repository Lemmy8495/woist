import tempfile
import unittest
from pathlib import Path

from woistlib.cli_inputs import normalize_target, parse_ports, read_targets


class CliInputsTest(unittest.TestCase):
    def test_normalize_target_url_with_port(self) -> None:
        self.assertEqual(normalize_target("https://example.com:443/path"), "example.com")

    def test_parse_ports_supports_ranges(self) -> None:
        self.assertEqual(parse_ports("80,443-445"), [80, 443, 444, 445])

    def test_parse_ports_rejects_invalid(self) -> None:
        with self.assertRaises(ValueError):
            parse_ports("abc")

    def test_read_targets_from_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "targets.txt"
            file_path.write_text("# comment\nexample.com\n1.1.1.1\n", encoding="utf-8")
            targets = read_targets([], str(file_path))
            self.assertEqual(targets, ["example.com", "1.1.1.1"])


if __name__ == "__main__":
    unittest.main()

