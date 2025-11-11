# Quick Start Guide

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Set Up Fyers API Credentials

1. Create a `.env` file in the project root:
```env
FYERS_APP_ID=your_app_id_here
FYERS_SECRET_KEY=your_secret_key_here
FYERS_REDIRECT_URI=https://127.0.0.1/
```

2. Get your Fyers App ID and Secret Key from [Fyers Developer Portal](https://myapi.fyers.in/)

## Step 3: Generate Access Token

Run the authentication helper:
```bash
python auth_helper.py
```

Follow the instructions to:
1. Visit the authorization URL
2. Authorize the application
3. Copy the authorization code
4. Paste it when prompted
5. Copy the generated access token to your `.env` file

Your `.env` file should now look like:
```env
FYERS_APP_ID=your_app_id_here
FYERS_SECRET_KEY=your_secret_key_here
FYERS_ACCESS_TOKEN=your_access_token_here
FYERS_REDIRECT_URI=https://127.0.0.1/
```

## Step 4: Configure Trading Parameters

Edit `config.json` to adjust:
- Risk parameters (stop-loss, take-profit)
- Maximum positions
- Symbols to trade
- Technical analysis parameters

## Step 5: Run the Bot

```bash
python trading_bot.py
```

The bot will:
- Authenticate with Fyers
- Start analyzing markets
- Execute trades automatically
- Monitor positions
- Run continuously

## Important Notes

⚠️ **Before Live Trading:**
1. Test with paper trading first
2. Start with small position sizes
3. Monitor the bot closely initially
4. Adjust risk parameters based on your risk tolerance
5. Ensure you understand the trading strategy

## Stopping the Bot

Press `Ctrl+C` to stop the bot gracefully.

## Troubleshooting

### "Authentication failed"
- Check your `.env` file has correct credentials
- Verify access token is not expired
- Regenerate access token if needed

### "Insufficient data"
- Check internet connection
- Verify symbols are correct
- Ensure market is open (9:15 AM - 3:30 PM IST)

### "Order placement failed"
- Check account balance/margin
- Verify symbol format
- Ensure trading hours

## Support

Check `trading_bot.log` for detailed logs of all bot activities.
