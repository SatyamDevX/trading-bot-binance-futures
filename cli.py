# CLI entry point

import argparse
import logging

from bot.client import get_client
from bot.orders import place_order
from bot.validators import validate_order
from bot.logging_config import setup_logging


def main():
    parser = argparse.ArgumentParser(
        description="Binance Futures Testnet Trading Bot CLI"
    )

    parser.add_argument("--symbol", required=True)
    parser.add_argument("--side", required=True)
    parser.add_argument("--type", required=True)
    parser.add_argument("--quantity", type=float, required=True)
    parser.add_argument("--price", type=float)

    args = parser.parse_args()

    # Normalize inputs
    args.symbol = args.symbol.upper()
    args.side = args.side.upper()
    args.type = args.type.upper()

    setup_logging()

    try:
        validate_order(args.symbol, args.side, args.type, args.quantity, args.price)

        client = get_client()

        # 📌 REQUEST
        print("\n📌 ORDER REQUEST")
        print(f"Symbol      : {args.symbol}")
        print(f"Side        : {args.side}")
        print(f"Type        : {args.type}")
        print(f"Quantity    : {args.quantity}")
        if args.price:
            print(f"Price       : {args.price}")

        logging.info(f"Request: {vars(args)}")

        # 🚀 PLACE ORDER
        response = place_order(
            client,
            args.symbol,
            args.side,
            args.type,
            args.quantity,
            args.price
        )

        # 📊 RESPONSE SAFE EXTRACTION
        order_id = response.get("orderId")
        status = response.get("status")
        executed_qty = response.get("executedQty")
        avg_price = response.get("avgPrice") or response.get("price")

        print("\n📊 ORDER RESPONSE")
        print(f"Order ID    : {order_id}")
        print(f"Status      : {status}")
        print(f"Executed Qty: {executed_qty}")

        if avg_price is not None:
            print(f"Avg Price   : {avg_price}")
        else:
            print("Avg Price   : N/A")

        print("\n✅ ORDER SUCCESS")

        logging.info(f"Response: {response}")

    except Exception as e:
        error_msg = str(e).lower()

        if "insufficient margin" in error_msg:
            print("\n❌ Trade failed: Not enough margin. Add USDT in Futures wallet.")
        elif "notional must be no smaller" in error_msg:
            print("\n❌ Trade failed: Order size too small (min ≈ 50 USDT).")
        else:
            print(f"\n❌ ERROR: {str(e)}")

        logging.error(f"Error: {str(e)}")


if __name__ == "__main__":
    main()