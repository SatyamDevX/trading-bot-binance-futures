# Order logic

import logging

def place_order(client, symbol, side, order_type, quantity, price=None):
    try:
        logging.info(
            f"Placing order | symbol={symbol}, side={side}, type={order_type}, quantity={quantity}, price={price}"
        )

        if order_type == "MARKET":
            order = client.futures_create_order(
                symbol=symbol,
                side=side,
                type=order_type,
                quantity=quantity,
                newOrderRespType="RESULT"
            )

        elif order_type == "LIMIT":
            order = client.futures_create_order(
                symbol=symbol,
                side=side,
                type=order_type,
                quantity=quantity,
                price=price,
                timeInForce="GTC"
            )

        else:
            raise ValueError("Unsupported order type")

        logging.info(f"Order response: {order}")

        return order

    except Exception as e:
        logging.error(f"Order failed: {str(e)}")
        raise