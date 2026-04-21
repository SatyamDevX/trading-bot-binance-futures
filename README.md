# Binance Futures Trading Bot (Testnet)

## 🚀 Overview

This project is a Python-based CLI trading bot that places MARKET and LIMIT orders on Binance Futures Testnet (USDT-M).

It is designed with a modular structure, proper validation, logging, and error handling to simulate real-world trading systems.

---

## ⚙️ Setup Instructions

### 1. Clone Repository

git clone <your-repo-link>
cd trading_bot

### 2. Install Dependencies

pip install -r requirements.txt

### 3. Setup Environment Variables

Create a `.env` file:

```
API_KEY=your_testnet_api_key
API_SECRET=your_testnet_secret
BASE_URL=https://testnet.binancefuture.com/fapi
```
---

## ▶️ How to Run

### Market Order

python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.002

### Limit Order

python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.002 --price 30000

---

## 📊 Features

* Place MARKET and LIMIT orders
* Supports BUY and SELL
* CLI input validation
* Structured modular code
* Logging of requests, responses, and errors
* Handles API errors (margin, notional, etc.)

---

## 📄 Example Output

### Market Order

Status: FILLED
Executed Qty: 0.002
Avg Price: 75708

### Limit Order

Status: NEW
Executed Qty: 0.000

---

## 🧠 Assumptions

* Binance Futures Testnet is used
* Minimum notional for BTCUSDT ≈ 50 USDT
* Testnet funds must be added before trading

---

## 📁 Logs

All API requests, responses, and errors are logged in:
bot.log

---

## 🔮 Future Improvements

* Add Stop-Limit orders
* Add order tracking (polling)
* Add retry mechanism
* Build a simple UI/dashboard
