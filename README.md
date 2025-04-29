# Nanabot
🚀 Nanabot — Crypto Trading Bot
Nanabot is a fully automated crypto trading bot that trades BTC-USD on Coinbase Advanced Trade API (v3) using a simple, trend-following strategy based on EMA crossovers and RSI filters.
It operates live with real USD funds through secure JWT authentication.

📈 Strategy
Indicators Used:

EMA 20 / EMA 50 Cross

RSI 14 (Relative Strength Index)

Entry Conditions:

BUY (long): When EMA20 crosses above EMA50 and RSI is between 40 and 60

SELL (short): When EMA20 crosses below EMA50 and RSI is between 40 and 60

Risk Management:

Position Size: 2% of available account balance per trade

Take Profit: +4% gain

Stop Loss: -2% loss

🔐 Authentication
Nanabot uses Coinbase Advanced Trade v3 API authentication by generating a JWT (JSON Web Token) signed with an ECDSA private key.
A fresh JWT is generated per API request (valid for 2 minutes maximum).

Requirements:

API Key ID (organizations/.../apiKeys/...)

ECDSA Private Key

Correct API permissions (View, Trade) on Coinbase Advanced Trade.

⚙️ Installation
Clone the Repository:

bash
Copy
git clone https://github.com/yourusername/nanabot.git
cd nanabot
Create a Virtual Environment and Activate:

bash
Copy
python3 -m venv venv
source venv/bin/activate
Install Requirements:

bash
Copy
pip install -r requirements.txt
Set Up Environment Variables: Create a .env file in the root directory:

env
Copy
API_KEY_ID=your_api_key_id_here
API_PRIVATE_KEY_PATH=path_to_your_private_key.pem
COINBASE_API_URL=https://api.coinbase.com/api/v3/brokerage
SYMBOL=BTC-USD
🧠 How It Works
Pulls live candle data from Coinbase.

Calculates EMA20, EMA50, and RSI14.

Checks for crossover + RSI filter signals.

Places market orders when conditions are met.

Automatically manages position exits based on stop-loss or take-profit rules.

Generates new JWT tokens automatically every time a request is made.

🚀 Running the Bot
bash
Copy
source venv/bin/activate
python bot_v3.py
The bot will:

Print each trade action to the console

Sleep and wait between candle intervals

Manage open positions intelligently

📦 Project Structure
plaintext
Copy
nanabot/
├── bot_v3.py         # Main bot file (trading logic)
├── generate_jwt.py   # JWT token generator utility
├── requirements.txt  # Required Python packages
├── README.md         # This file
├── .env              # Environment configuration (not committed)
🛡️ Disclaimers
Nanabot is for educational and personal use only.

Trading cryptocurrencies involves substantial risk.

Past performance is not indicative of future results.

Always test thoroughly on sandbox accounts before live trading!

