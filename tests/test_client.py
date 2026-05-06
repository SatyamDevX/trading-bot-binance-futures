import os
import unittest
from unittest.mock import patch

from bot.client import get_client


class FakeClient:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.FUTURES_URL = None


class GetClientTests(unittest.TestCase):
    @patch("bot.client.Client", FakeClient)
    def test_uses_base_url_from_environment(self):
        with patch.dict(
            os.environ,
            {
                "BINANCE_API_KEY": "key",
                "BINANCE_API_SECRET": "secret",
                "BINANCE_BASE_URL": "https://demo-fapi.binance.com",
            },
            clear=False,
        ):
            client = get_client()

        self.assertEqual(client.api_key, "key")
        self.assertEqual(client.api_secret, "secret")
        self.assertEqual(client.FUTURES_URL, "https://demo-fapi.binance.com")

    def test_missing_credentials_raise_clear_error(self):
        with patch.dict(
            os.environ,
            {
                "BINANCE_API_KEY": "",
                "BINANCE_API_SECRET": "",
                "BINANCE_BASE_URL": "https://demo-fapi.binance.com",
            },
            clear=False,
        ):
            with self.assertRaisesRegex(ValueError, "Missing required environment variables"):
                get_client()


if __name__ == "__main__":
    unittest.main()
