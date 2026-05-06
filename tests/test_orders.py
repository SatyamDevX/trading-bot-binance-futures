import unittest

from bot.orders import place_order


class FakeClient:
    def __init__(self):
        self.timestamp_offset = 0
        self.server_time_calls = 0
        self.create_order_calls = 0
        self.fail_once = False
        self.fail_always = False

    def futures_time(self):
        self.server_time_calls += 1
        return {"serverTime": 1_700_000_000_500}

    def futures_create_order(self, **kwargs):
        self.create_order_calls += 1
        if self.fail_always:
            raise Exception(
                "APIError(code=-1021): Timestamp for this request was 1000ms ahead of the server's time."
            )
        if self.fail_once:
            self.fail_once = False
            raise Exception(
                "APIError(code=-1021): Timestamp for this request was 1000ms ahead of the server's time."
            )
        return {
            "orderId": 42,
            "status": "FILLED",
            "executedQty": kwargs["quantity"],
            "avgPrice": "30000.00",
        }


class PlaceOrderTests(unittest.TestCase):
    def test_market_order_retries_after_timestamp_sync(self):
        client = FakeClient()
        client.fail_once = True

        response = place_order(client, "BTCUSDT", "BUY", "MARKET", 0.01)

        self.assertEqual(response["orderId"], 42)
        self.assertEqual(client.server_time_calls, 1)
        self.assertEqual(client.create_order_calls, 2)
        self.assertNotEqual(client.timestamp_offset, 0)

    def test_limit_order_retries_after_timestamp_sync(self):
        client = FakeClient()
        client.fail_once = True

        response = place_order(client, "BTCUSDT", "BUY", "LIMIT", 0.01, 30000)

        self.assertEqual(response["status"], "FILLED")
        self.assertEqual(client.server_time_calls, 1)
        self.assertEqual(client.create_order_calls, 2)

    def test_raises_if_timestamp_sync_does_not_fix_error(self):
        client = FakeClient()
        client.fail_always = True

        with self.assertRaisesRegex(Exception, "Timestamp for this request"):
            place_order(client, "BTCUSDT", "BUY", "MARKET", 0.01)

        self.assertEqual(client.server_time_calls, 1)
        self.assertEqual(client.create_order_calls, 2)


if __name__ == "__main__":
    unittest.main()
