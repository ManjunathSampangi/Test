# Autonomous Trading Bot for Fyers Platform

An autonomous trading bot that analyzes and predicts stock options and Nifty options, executing trades automatically without human interaction.

## Features

- **Automatic Trading**: Executes trades autonomously based on technical analysis
- **Options Trading**: Supports both Nifty options and stock options
- **Technical Analysis**: Uses RSI, MACD, Bollinger Bands, and other indicators
- **Risk Management**: Implements stop-loss, take-profit, position sizing, and risk limits
- **Real-time Monitoring**: Monitors positions and exits automatically when targets are hit
- **Fyers Integration**: Full integration with Fyers API for authentication and trading

## Prerequisites

- Python 3.8 or higher
- Fyers account with API access
- Fyers App ID and Secret Key
- Active Fyers trading account

## Installation

1. **Clone or download the project**

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure Fyers API credentials**:
   - Create a `.env` file in the project root:
   ```env
   FYERS_APP_ID=your_app_id_here
   FYERS_SECRET_KEY=your_secret_key_here
   FYERS_ACCESS_TOKEN=your_access_token_here
   FYERS_REDIRECT_URI=https://127.0.0.1/
   ```

4. **Get Fyers Access Token**:
   - Run the authentication script to generate authorization URL
   - Visit the URL and authorize the application
   - Copy the authorization code and generate access token
   - Add the access token to `.env` file

5. **Configure trading parameters** in `config.json`:
   - Adjust risk parameters (stop-loss, take-profit percentages)
   - Set maximum positions and position sizes
   - Configure symbols to trade (Nifty and stock options)
   - Adjust technical analysis parameters

## Configuration

### config.json Structure

```json
{
  "fyers": {
    "app_id": "YOUR_APP_ID",
    "secret_key": "YOUR_SECRET_KEY",
    "redirect_uri": "https://127.0.0.1/",
    "response_type": "code",
    "grant_type": "authorization_code"
  },
  "trading": {
    "max_positions": 5,
    "max_position_size": 10000,
    "stop_loss_percentage": 2.0,
    "take_profit_percentage": 3.0,
    "risk_per_trade": 0.02
  },
  "symbols": {
    "nifty_options": ["NSE:NIFTY50-INDEX"],
    "stock_options": ["NSE:RELIANCE-EQ", "NSE:TCS-EQ"]
  },
  "analysis": {
    "rsi_period": 14,
    "rsi_oversold": 30,
    "rsi_overbought": 70,
    "macd_fast": 12,
    "macd_slow": 26,
    "macd_signal": 9
  }
}
```

## Usage

### Running the Bot

```bash
python trading_bot.py
```

The bot will:
1. Authenticate with Fyers
2. Start monitoring market data
3. Analyze symbols using technical indicators
4. Execute trades automatically when opportunities are found
5. Monitor positions and exit when stop-loss or take-profit is hit
6. Run continuously in cycles (default: every 5 minutes)

### Stopping the Bot

Press `Ctrl+C` to stop the bot gracefully. The bot will finish the current cycle before stopping.

## Architecture

### Modules

1. **fyers_auth.py**: Handles Fyers API authentication and token management
2. **market_data.py**: Fetches real-time and historical market data
3. **technical_analysis.py**: Performs technical analysis and generates trading signals
4. **trading_execution.py**: Executes buy/sell orders and manages positions
5. **risk_management.py**: Implements risk controls (position sizing, stop-loss, etc.)
6. **trading_bot.py**: Main orchestrator that runs the bot autonomously

## Trading Strategy

The bot uses a combination of technical indicators:

1. **RSI (Relative Strength Index)**: Identifies overbought/oversold conditions
2. **MACD**: Detects trend changes and momentum
3. **Bollinger Bands**: Identifies volatility and potential reversals
4. **Moving Averages**: Confirms trend direction

### Signal Generation

- **BUY Signal**: Generated when multiple indicators suggest upward momentum
- **SELL Signal**: Generated when multiple indicators suggest downward momentum
- **Confidence Score**: Each signal has a confidence score (0-1) based on indicator agreement

### Risk Management

- **Position Sizing**: Calculated based on account value and risk per trade
- **Stop Loss**: Automatically set at configured percentage from entry
- **Take Profit**: Automatically set at configured percentage from entry
- **Maximum Positions**: Limits number of concurrent positions
- **Position Size Limits**: Caps maximum position value

## Important Notes

⚠️ **DISCLAIMER**: 
- This bot is for educational purposes only
- Trading involves substantial risk of loss
- Past performance does not guarantee future results
- Always test with paper trading before using real money
- Monitor the bot regularly and adjust parameters as needed
- The bot operates autonomously but should be supervised

## Troubleshooting

### Authentication Issues
- Verify your Fyers App ID and Secret Key are correct
- Ensure your access token is valid and not expired
- Check that redirect URI matches your Fyers app configuration

### Trading Issues
- Verify you have sufficient margin/balance
- Check that symbols are correctly formatted
- Ensure trading hours are correct (9:15 AM - 3:30 PM IST on weekdays)

### Data Issues
- Check internet connection
- Verify Fyers API is accessible
- Ensure symbols exist and are tradeable

## Logging

The bot logs all activities to `trading_bot.log` file. Check this file for:
- Trade executions
- Errors and warnings
- Position monitoring
- Analysis results

## Customization

You can customize the bot by:

1. **Adding more indicators**: Extend `technical_analysis.py`
2. **Modifying strategy**: Adjust signal generation logic in `technical_analysis.py`
3. **Changing risk parameters**: Update `config.json`
4. **Adding more symbols**: Update symbols list in `config.json`
5. **Adjusting cycle interval**: Change `cycle_interval` parameter in `trading_bot.py`

## Support

For issues related to:
- **Fyers API**: Contact Fyers support
- **Bot functionality**: Check logs and configuration
- **Trading strategy**: Modify analysis parameters

## License

This project is provided as-is for educational purposes.
