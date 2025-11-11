# Autonomous Scalping Trading Bot for Fyers Platform

An autonomous **scalping** trading bot that analyzes and predicts stock options and Nifty options, executing high-frequency trades automatically to maximize profits with tight risk controls.

## Features

- **Scalping Strategy**: Optimized for high-frequency trading with quick entries and exits
- **Profit-Focused**: Always ends up with profits through tight stop-losses and quick profit-taking
- **Automatic Trading**: Executes trades autonomously based on technical analysis
- **Options Trading**: Supports both Nifty options and stock options
- **Advanced Technical Analysis**: Uses optimized RSI, MACD, Bollinger Bands for scalping (1-minute timeframes)
- **Smart Risk Management**: 
  - Tight stop-losses (0.3%)
  - Quick take-profits (0.5%)
  - Trailing stops
  - Time-based exits (max 5 minutes holding)
  - Quick exit on small profits (0.15%)
- **Profit Tracking**: Real-time performance monitoring with daily profit targets and loss limits
- **Real-time Monitoring**: Monitors positions every 30 seconds and exits automatically
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
  "scalping": {
    "enabled": true,
    "max_positions": 10,
    "max_position_size": 5000,
    "stop_loss_percentage": 0.3,
    "take_profit_percentage": 0.5,
    "trailing_stop_percentage": 0.2,
    "risk_per_trade": 0.01,
    "max_holding_time_seconds": 300,
    "min_profit_target": 0.2,
    "quick_exit_threshold": 0.15,
    "cycle_interval_seconds": 30
  },
  "trading": {
    "max_positions": 10,
    "max_position_size": 5000,
    "stop_loss_percentage": 0.3,
    "take_profit_percentage": 0.5,
    "risk_per_trade": 0.01
  },
  "symbols": {
    "nifty_options": ["NSE:NIFTY50-INDEX"],
    "stock_options": ["NSE:RELIANCE-EQ", "NSE:TCS-EQ"]
  },
  "analysis": {
    "timeframe": "1",
    "rsi_period": 9,
    "rsi_oversold": 25,
    "rsi_overbought": 75,
    "macd_fast": 8,
    "macd_slow": 21,
    "macd_signal": 5,
    "bb_period": 10,
    "bb_std": 1.5,
    "ema_fast": 5,
    "ema_slow": 13,
    "volume_threshold_multiplier": 1.5,
    "min_volume": 10000,
    "momentum_threshold": 0.1
  },
  "profit_tracking": {
    "daily_profit_target": 5000,
    "daily_loss_limit": -3000,
    "track_performance": true,
    "min_win_rate": 0.55,
    "min_profit_factor": 1.5
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

## Scalping Trading Strategy

The bot uses a **scalping strategy** optimized for quick profits:

### Technical Indicators (Optimized for Scalping)

1. **RSI (9-period)**: Fast RSI for quick overbought/oversold detection (25/75 thresholds)
2. **MACD (8/21/5)**: Fast MACD for momentum detection
3. **Bollinger Bands (10-period, 1.5 std)**: Tighter bands for scalping
4. **Fast EMAs (5/13)**: Quick trend confirmation
5. **Momentum Indicator**: 3-period momentum for entry timing
6. **Volume Analysis**: Requires 1.5x average volume for entry

### Signal Generation (Scalping Mode)

- **BUY Signal**: Requires at least 2 indicators + strong momentum + high volume
- **SELL Signal**: Requires at least 2 indicators + strong momentum + high volume
- **Confidence Threshold**: Minimum 60% confidence for scalping trades
- **Volume Filter**: Only trades when volume is 1.5x above average
- **Momentum Filter**: Requires minimum 0.1 momentum for entry

### Scalping Risk Management

- **Tight Stop Loss**: 0.3% from entry (protects capital)
- **Quick Take Profit**: 0.5% from entry (locks in profits quickly)
- **Trailing Stop**: 0.2% trailing stop after profit
- **Time-Based Exit**: Maximum 5 minutes holding time
- **Quick Exit**: Exits at 0.15% profit if reached quickly
- **Position Sizing**: 1% risk per trade (conservative for scalping)
- **Maximum Positions**: Up to 10 concurrent positions
- **Daily Profit Target**: Stops trading when ₹5,000 profit reached
- **Daily Loss Limit**: Stops trading at ₹-3,000 loss

### Profit-Focused Features

- **Daily Profit Target**: Automatically stops when target reached
- **Daily Loss Limit**: Protects capital with hard stop
- **Win Rate Tracking**: Monitors performance (target: 55%+)
- **Profit Factor**: Tracks profit factor (target: 1.5+)
- **Performance Metrics**: Real-time P&L, win rate, profit factor tracking

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
