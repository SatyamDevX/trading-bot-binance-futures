import unittest

from bot.validators import validate_order


class ValidateOrderTests(unittest.TestCase):
    def test_market_order_accepts_positive_quantity(self):
        validate_order("BTCUSDT", "BUY", "MARKET", 0.01, None)

    def test_limit_order_requires_price(self):
        with self.assertRaisesRegex(ValueError, "Price required for LIMIT orders"):
            validate_order("BTCUSDT", "BUY", "LIMIT", 0.01, None)

    def test_limit_order_enforces_minimum_notional(self):
        with self.assertRaisesRegex(ValueError, "at least 50 USDT"):
            validate_order("BTCUSDT", "BUY", "LIMIT", 0.001, 30000)

    def test_side_must_be_buy_or_sell(self):
        with self.assertRaisesRegex(ValueError, "Side must be BUY or SELL"):
            validate_order("BTCUSDT", "HOLD", "MARKET", 0.01, None)


if __name__ == "__main__":
    unittest.main()
