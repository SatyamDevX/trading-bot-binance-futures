import os
import unittest
from unittest.mock import patch

from bot.settings import get_public_config_status, validate_binance_settings


class SettingsTests(unittest.TestCase):
    def test_validate_returns_expected_values(self):
        with patch.dict(
            os.environ,
            {
                "BINANCE_API_KEY": "key",
                "BINANCE_API_SECRET": "secret",
                "BINANCE_BASE_URL": "https://demo-fapi.binance.com",
            },
            clear=False,
        ):
            settings = validate_binance_settings()

        self.assertEqual(settings["base_url"], "https://demo-fapi.binance.com")

    def test_validate_reports_missing_names(self):
        with patch.dict(
            os.environ,
            {
                "BINANCE_API_KEY": "",
                "BINANCE_API_SECRET": "",
                "BINANCE_BASE_URL": "",
            },
            clear=False,
        ):
            with self.assertRaisesRegex(
                ValueError,
                "BINANCE_API_KEY, BINANCE_API_SECRET, BINANCE_BASE_URL",
            ):
                validate_binance_settings()

    def test_public_status_hides_secret_values(self):
        with patch.dict(
            os.environ,
            {
                "BINANCE_API_KEY": "key",
                "BINANCE_API_SECRET": "secret",
                "BINANCE_BASE_URL": "https://demo-fapi.binance.com",
            },
            clear=False,
        ):
            status = get_public_config_status()

        self.assertTrue(status["has_api_key"])
        self.assertTrue(status["has_api_secret"])
        self.assertEqual(status["base_url"], "https://demo-fapi.binance.com")
        self.assertNotIn("key", status.values())
        self.assertNotIn("secret", status.values())


if __name__ == "__main__":
    unittest.main()
