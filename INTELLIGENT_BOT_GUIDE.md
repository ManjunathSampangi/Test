# Intelligent Autonomous Trading Bot - Complete Guide

## Overview

This is an **intelligent autonomous trading bot** that analyzes markets like a human trader and uses multiple world-class trading strategies to maximize profits. The bot is designed to make ₹5,000 daily profit on a ₹50,000 investment (10% daily return target).

## Key Features

### 🧠 Intelligent Analysis
- **Multiple Trading Strategies**: Momentum, Mean Reversion, Breakout, Trend Following, Volume Profile, and Arbitrage
- **Machine Learning Predictions**: Ensemble ML models (Random Forest + Gradient Boosting) for better predictions
- **Market Regime Detection**: Automatically detects market conditions (Trending, Ranging, Volatile, Breakout, Reversal) and adapts strategies
- **Intelligent Opportunity Finding**: Finds high-quality trades, especially after losses

### 📊 Advanced Features
- **Adaptive Strategy Selection**: Automatically adjusts strategy weights based on market regime
- **Recovery Mode**: After losses, bot becomes more selective and finds better opportunities
- **Risk Management**: Dynamic position sizing, stop-loss, take-profit, trailing stops
- **Profit Tracking**: Real-time performance monitoring with daily targets

### 🎯 Trading Capabilities
- **Fyers API Integration**: Full integration for placing, managing, and closing orders
- **Real-time Monitoring**: Continuous position monitoring and automatic exits
- **Multiple Timeframes**: Supports 1-minute (scalping) to daily timeframes
- **Portfolio Management**: Manages multiple positions simultaneously

## Architecture

### Core Modules

1. **intelligent_trading_bot.py** - Main orchestrator
2. **advanced_strategies.py** - Multiple trading strategies
3. **intelligent_opportunity_finder.py** - Smart opportunity detection
4. **ml_analysis.py** - Machine learning predictions
5. **market_regime_detector.py** - Market condition detection
6. **technical_analysis.py** - Technical indicators
7. **risk_management.py** - Risk controls
8. **profit_tracker.py** - Performance tracking

## Installation

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Configure Fyers API**:
   - Create `.env` file:
   ```env
   FYERS_APP_ID=your_app_id
   FYERS_SECRET_KEY=your_secret_key
   FYERS_ACCESS_TOKEN=your_access_token
   FYERS_REDIRECT_URI=https://127.0.0.1/
   ```

3. **Get Access Token**:
   ```bash
   python auth_helper.py
   ```

4. **Configure trading parameters** in `config.json`

## Usage

### Running the Intelligent Bot

```bash
python intelligent_trading_bot.py
```

### Running the Original Bot (Scalping Mode)

```bash
python trading_bot.py
```

## Configuration

### Key Parameters in config.json

```json
{
  "profit_tracking": {
    "daily_profit_target": 5000,      // ₹5,000 daily target
    "daily_loss_limit": -3000          // Stop at ₹3,000 loss
  },
  "scalping": {
    "enabled": true,                   // Enable scalping mode
    "stop_loss_percentage": 0.3,      // 0.3% stop loss
    "take_profit_percentage": 0.5,    // 0.5% take profit
    "cycle_interval_seconds": 30       // Check every 30 seconds
  },
  "strategies": {
    "momentum_weight": 0.25,          // Strategy weights
    "mean_reversion_weight": 0.20,
    "breakout_weight": 0.20,
    "trend_following_weight": 0.15,
    "volume_profile_weight": 0.10,
    "arbitrage_weight": 0.10
  }
}
```

## Trading Strategies

### 1. Momentum Strategy
- **When**: Strong trends detected
- **Signals**: Price momentum, ROC, volume confirmation
- **Best for**: Trending markets

### 2. Mean Reversion Strategy
- **When**: Price deviates from mean
- **Signals**: Z-score extremes, RSI, Bollinger Bands
- **Best for**: Ranging markets

### 3. Breakout Strategy
- **When**: Price breaks support/resistance
- **Signals**: Volume confirmation, volatility expansion
- **Best for**: Volatile markets

### 4. Trend Following Strategy
- **When**: Clear trend established
- **Signals**: EMA alignment, MACD, ADX
- **Best for**: Strong trending markets

### 5. Volume Profile Strategy
- **When**: Unusual volume patterns
- **Signals**: Volume spikes, OBV, VPT
- **Best for**: All market conditions

### 6. Arbitrage Strategy
- **When**: Price discrepancies detected
- **Signals**: Fair value deviation
- **Best for**: Efficient markets

## How It Works

### 1. Market Analysis
- Bot analyzes each symbol using all strategies
- ML models provide additional predictions
- Market regime is detected (Trending/Ranging/Volatile)

### 2. Signal Generation
- All strategies vote on direction
- ML predictions add weight
- Technical analysis confirms signals
- Final signal requires minimum 60% confidence

### 3. Opportunity Finding
- Filters opportunities by quality score
- After losses, becomes more selective (75% confidence required)
- Prioritizes high risk-reward ratios
- Checks multiple confirmations

### 4. Trade Execution
- Validates trade against risk limits
- Calculates optimal position size
- Places order via Fyers API
- Sets stop-loss and take-profit

### 5. Position Monitoring
- Continuously monitors positions
- Exits on stop-loss, take-profit, or trailing stop
- Time-based exits for scalping (max 5 minutes)
- Records all trades for analysis

### 6. Recovery Mode
- After losses, bot:
  - Increases minimum confidence threshold
  - Requires higher volume confirmation
  - Looks for high-probability setups only
  - Focuses on recovery opportunities

## Performance Tracking

The bot tracks:
- **Daily P&L**: Real-time profit/loss
- **Win Rate**: Percentage of winning trades
- **Profit Factor**: Total profit / Total loss
- **Trade Statistics**: Entry/exit prices, duration, P&L

## Risk Management

### Position Sizing
- Risk 1% of account per trade (scalping)
- Maximum 10 concurrent positions
- Position size based on stop-loss distance

### Stop Loss & Take Profit
- **Stop Loss**: 0.3% from entry (scalping)
- **Take Profit**: 0.5% from entry (scalping)
- **Trailing Stop**: 0.2% after profit
- **Quick Exit**: Exit at 0.15% profit if reached quickly

### Daily Limits
- **Profit Target**: ₹5,000 (stops trading)
- **Loss Limit**: ₹-3,000 (stops trading)
- **Max Positions**: 10 concurrent

## Market Regime Detection

The bot automatically detects market regimes:

1. **TRENDING**: Strong directional movement
   - Strategies: Trend Following, Momentum, Breakout
   
2. **RANGING**: Sideways movement
   - Strategies: Mean Reversion, Arbitrage
   
3. **VOLATILE**: High volatility
   - Strategies: Breakout, Momentum
   
4. **BREAKOUT**: Price breaking levels
   - Strategies: Breakout, Momentum, Volume Profile
   
5. **REVERSAL**: Trend reversal signals
   - Strategies: Mean Reversion, Volume Profile

## Logging

All activities are logged to:
- `intelligent_trading_bot.log` - Main bot log
- `trading_bot.log` - Original bot log (if used)
- Console output - Real-time updates

## Important Notes

⚠️ **DISCLAIMER**:
- Trading involves substantial risk
- Past performance doesn't guarantee future results
- 10% daily return is extremely ambitious
- Always test with paper trading first
- Monitor the bot regularly
- Adjust parameters based on market conditions

## Troubleshooting

### Authentication Issues
- Verify Fyers credentials in `.env`
- Check access token validity
- Ensure redirect URI matches Fyers app config

### Trading Issues
- Check account balance/margin
- Verify symbols are tradeable
- Ensure trading hours (9:15 AM - 3:30 PM IST)

### Performance Issues
- Reduce number of symbols if slow
- Increase cycle interval
- Check internet connection

## Customization

### Adding New Strategies
1. Add strategy method to `advanced_strategies.py`
2. Update `analyze_with_all_strategies()` method
3. Add weight to config.json

### Adjusting ML Models
1. Modify `ml_analysis.py`
2. Add/remove features in `prepare_features()`
3. Train on more historical data

### Changing Risk Parameters
1. Update `config.json`
2. Modify `risk_management.py` if needed
3. Adjust position sizing logic

## Support

For issues:
- Check logs in `intelligent_trading_bot.log`
- Verify configuration in `config.json`
- Test with paper trading first
- Contact Fyers support for API issues

## License

This project is provided as-is for educational purposes.
