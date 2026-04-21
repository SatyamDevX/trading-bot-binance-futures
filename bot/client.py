# Binance Futures Testnet Client Wrapper

from binance.client import Client
import os
from dotenv import load_dotenv

load_dotenv()

def get_client():
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    base_url = os.getenv("BINANCE_BASE_URL")
    client = Client(api_key, api_secret)

    # Futures Testnet URL
    client.FUTURES_URL = base_url

    return client