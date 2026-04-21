# Input validation

def validate_order(symbol, side, order_type, quantity, price):
    if side not in ["BUY", "SELL"]:
        raise ValueError("Side must be BUY or SELL")

    if order_type not in ["MARKET", "LIMIT"]:
        raise ValueError("Type must be MARKET or LIMIT")

    if quantity <= 0:
        raise ValueError("Quantity must be > 0")

    if order_type == "LIMIT":
        if price is None:
            raise ValueError("Price required for LIMIT orders")

        notional = quantity * price
        if notional < 50:
            raise ValueError("Order notional must be at least 50 USDT for BTCUSDT")