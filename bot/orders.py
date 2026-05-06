# Order logic

import logging
import time


def _create_order(client, symbol, side, order_type, quantity, price=None):
    if order_type == "MARKET":
        return client.futures_create_order(
            symbol=symbol,
            side=side,
            type=order_type,
            quantity=quantity,
            newOrderRespType="RESULT"
        )

    if order_type == "LIMIT":
        return client.futures_create_order(
            symbol=symbol,
            side=side,
            type=order_type,
            quantity=quantity,
            price=price,
            timeInForce="GTC"
        )

    raise ValueError("Unsupported order type")


def _is_timestamp_error(error):
    return "APIError(code=-1021)" in str(error)


def _sync_client_time(client):
    server_time = client.futures_time()["serverTime"]
    local_time_ms = int(time.time() * 1000)
    client.timestamp_offset = server_time - local_time_ms
    logging.warning(
        "Timestamp drift detected. Synced client offset to %sms.",
        client.timestamp_offset,
    )

def place_order(client, symbol, side, order_type, quantity, price=None):
    try:
        logging.info(
            f"Placing order | symbol={symbol}, side={side}, type={order_type}, quantity={quantity}, price={price}"
        )
        client.last_retry_reason = None

        try:
            order = _create_order(client, symbol, side, order_type, quantity, price)
        except Exception as e:
            if not _is_timestamp_error(e):
                raise

            logging.warning("Retrying order after Binance server time sync.")
            client.last_retry_reason = "timestamp_sync"
            _sync_client_time(client)
            order = _create_order(client, symbol, side, order_type, quantity, price)

        logging.info(f"Order response: {order}")

        return order

    except Exception as e:
        logging.error(f"Order failed: {str(e)}")
        raise
