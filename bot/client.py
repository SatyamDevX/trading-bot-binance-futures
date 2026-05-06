# Binance Futures client wrapper

from bot.settings import validate_binance_settings

Client = None


def _get_client_class():
    global Client
    if Client is None:
        from binance.client import Client as BinanceClient

        Client = BinanceClient
    return Client


def get_client():
    settings = validate_binance_settings()

    client_class = _get_client_class()
    client = client_class(settings["api_key"], settings["api_secret"])
    client.FUTURES_URL = settings["base_url"]
    return client
