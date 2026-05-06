import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app import app


class AppTests(unittest.TestCase):
    def setUp(self):
        from app import order_activity

        order_activity.clear()

    def test_health_endpoint_reports_config_state(self):
        with patch.dict(
            os.environ,
            {
                "BINANCE_API_KEY": "key",
                "BINANCE_API_SECRET": "secret",
                "BINANCE_BASE_URL": "https://demo-fapi.binance.com",
            },
            clear=False,
        ):
            client = TestClient(app)
            response = client.get("/health")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "ok")
        self.assertTrue(body["binance"]["api_key_configured"])
        self.assertTrue(body["binance"]["api_secret_configured"])
        self.assertTrue(body["binance"]["base_url_configured"])

    def test_dashboard_renders_without_exposing_secret_values(self):
        with patch.dict(
            os.environ,
            {
                "BINANCE_API_KEY": "sample-api-key",
                "BINANCE_API_SECRET": "sample-secret-value",
                "BINANCE_BASE_URL": "https://demo-fapi.binance.com",
            },
            clear=False,
        ):
            client = TestClient(app)
            response = client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Binance Demo Dashboard", response.text)
        self.assertIn("https://demo-fapi.binance.com", response.text)
        self.assertIn("Order Validation", response.text)
        self.assertNotIn("sample-secret-value", response.text)
        self.assertNotIn("sample-api-key", response.text)

    def test_valid_market_order_shows_success_message(self):
        client = TestClient(app)
        response = client.post(
            "/orders/validate",
            data={
                "symbol": "btcusdt",
                "side": "buy",
                "order_type": "market",
                "quantity": "0.01",
                "price": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Order request is valid", response.text)
        self.assertIn("BTCUSDT", response.text)
        self.assertIn("Recent Activity", response.text)
        self.assertIn("Validation passed", response.text)

    def test_invalid_limit_order_shows_validation_error(self):
        client = TestClient(app)
        response = client.post(
            "/orders/validate",
            data={
                "symbol": "BTCUSDT",
                "side": "BUY",
                "order_type": "LIMIT",
                "quantity": "0.01",
                "price": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Price required for LIMIT orders", response.text)

    @patch("app.place_order")
    @patch("app.get_client")
    def test_execute_order_shows_response_details(self, mock_get_client, mock_place_order):
        mock_get_client.return_value = object()
        mock_place_order.return_value = {
            "orderId": 12345,
            "status": "FILLED",
            "executedQty": "0.01",
            "avgPrice": "30000.00",
        }

        client = TestClient(app)
        response = client.post(
            "/orders/execute",
            data={
                "symbol": "btcusdt",
                "side": "buy",
                "order_type": "market",
                "quantity": "0.01",
                "price": "",
                "confirm_execution": "yes",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Demo order submitted successfully", response.text)
        self.assertIn("12345", response.text)
        self.assertIn("FILLED", response.text)
        self.assertIn("Execution succeeded", response.text)
        mock_get_client.assert_called_once()
        mock_place_order.assert_called_once()

    @patch("app.place_order")
    @patch("app.get_client")
    def test_execute_invalid_order_does_not_call_binance(self, mock_get_client, mock_place_order):
        client = TestClient(app)
        response = client.post(
            "/orders/execute",
            data={
                "symbol": "BTCUSDT",
                "side": "BUY",
                "order_type": "LIMIT",
                "quantity": "0.01",
                "price": "",
                "confirm_execution": "yes",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Price required for LIMIT orders", response.text)
        mock_get_client.assert_not_called()
        mock_place_order.assert_not_called()

    @patch("app.place_order")
    @patch("app.get_client")
    def test_execute_requires_explicit_confirmation(self, mock_get_client, mock_place_order):
        client = TestClient(app)
        response = client.post(
            "/orders/execute",
            data={
                "symbol": "BTCUSDT",
                "side": "BUY",
                "order_type": "MARKET",
                "quantity": "0.01",
                "price": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Please confirm demo execution before submitting", response.text)
        self.assertIn("Execution blocked", response.text)
        mock_get_client.assert_not_called()
        mock_place_order.assert_not_called()

    @patch("app.place_order")
    @patch("app.get_client")
    def test_execute_failure_is_shown_in_recent_activity(self, mock_get_client, mock_place_order):
        mock_get_client.return_value = object()
        mock_place_order.side_effect = Exception(
            "APIError(code=-1021): Timestamp for this request was 1000ms ahead of the server's time."
        )

        client = TestClient(app)
        response = client.post(
            "/orders/execute",
            data={
                "symbol": "BTCUSDT",
                "side": "BUY",
                "order_type": "MARKET",
                "quantity": "0.01",
                "price": "",
                "confirm_execution": "yes",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Timestamp for this request", response.text)
        self.assertIn("Execution failed", response.text)

    @patch("app.place_order")
    @patch("app.get_client")
    def test_execute_success_after_timestamp_sync_still_shows_success(
        self, mock_get_client, mock_place_order
    ):
        mock_get_client.return_value = object()
        mock_place_order.return_value = {
            "orderId": 67890,
            "status": "FILLED",
            "executedQty": "0.002",
            "avgPrice": "30100.00",
        }

        client = TestClient(app)
        response = client.post(
            "/orders/execute",
            data={
                "symbol": "BTCUSDT",
                "side": "BUY",
                "order_type": "MARKET",
                "quantity": "0.002",
                "price": "",
                "confirm_execution": "yes",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Demo order submitted successfully", response.text)
        self.assertIn("67890", response.text)


if __name__ == "__main__":
    unittest.main()
