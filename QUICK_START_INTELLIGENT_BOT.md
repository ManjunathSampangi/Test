# Quick Start Guide - Intelligent Trading Bot

## Setup (5 Minutes)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure Fyers API
Create `.env` file:
```env
FYERS_APP_ID=your_app_id_here
FYERS_SECRET_KEY=your_secret_key_here
FYERS_ACCESS_TOKEN=your_access_token_here
FYERS_REDIRECT_URI=https://127.0.0.1/
```

### Step 3: Get Access Token
```bash
python auth_helper.py
```
Follow the prompts to generate your access token.

### Step 4: Run the Bot
```bash
python intelligent_trading_bot.py
```

## What the Bot Does

1. **Analyzes Markets** using 6 different strategies:
   - Momentum Trading
   - Mean Reversion
   - Breakout Trading
   - Trend Following
   - Volume Profile Analysis
   - Arbitrage

2. **Uses Machine Learning** to predict price direction

3. **Detects Market Regime** and adapts strategies accordingly

4. **Finds Opportunities** intelligently, especially after losses

5. **Executes Trades** automatically via Fyers API

6. **Manages Risk** with stop-loss, take-profit, and position sizing

7. **Tracks Performance** and stops at daily profit/loss limits

## Key Features

✅ **Multiple Strategies**: Uses best trading strategies in the world
✅ **ML-Powered**: Machine learning for better predictions
✅ **Adaptive**: Adjusts to market conditions
✅ **Intelligent Recovery**: Finds opportunities after losses
✅ **Risk Management**: Protects capital with stops
✅ **Profit Tracking**: Monitors performance in real-time

## Daily Targets

- **Profit Target**: ₹5,000 (10% on ₹50,000)
- **Loss Limit**: ₹-3,000 (stops trading)
- **Trading Hours**: 9:15 AM - 3:30 PM IST (weekdays)

## Monitoring

Check logs:
```bash
tail -f intelligent_trading_bot.log
```

## Important Notes

⚠️ **Always test with paper trading first!**
⚠️ **Monitor the bot regularly**
⚠️ **Adjust parameters based on market conditions**
⚠️ **Trading involves risk - never invest more than you can afford to lose**

## Need Help?

- Check `INTELLIGENT_BOT_GUIDE.md` for detailed documentation
- Review logs in `intelligent_trading_bot.log`
- Verify configuration in `config.json`
