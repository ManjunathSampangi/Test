# Scalping Trading Bot Guide

## What is Scalping?

Scalping is a high-frequency trading strategy that aims to profit from small price movements by entering and exiting positions quickly (typically within seconds to minutes). The goal is to make many small profits that add up over time.

## How This Bot Implements Scalping

### 1. **Fast Timeframes**
- Uses **1-minute candles** for analysis (vs 15-minute for regular trading)
- Analyzes markets every **30 seconds** (vs 5 minutes)
- Quick decision-making based on short-term price movements

### 2. **Tight Risk Controls**
- **Stop Loss**: 0.3% - Very tight to limit losses
- **Take Profit**: 0.5% - Quick profit-taking
- **Trailing Stop**: 0.2% - Locks in profits as price moves favorably
- **Max Holding Time**: 5 minutes - Forces quick exits

### 3. **Quick Profit Taking**
- **Quick Exit**: Exits at 0.15% profit if reached quickly
- **Time-Based Exit**: Closes position after 5 minutes regardless of profit/loss
- **Trailing Stop**: Automatically adjusts stop-loss to lock in profits

### 4. **High-Frequency Trading**
- Analyzes multiple symbols simultaneously
- Can hold up to 10 positions at once
- Executes trades quickly when opportunities arise
- Monitors positions continuously

### 5. **Profit-Focused Features**

#### Daily Profit Target
- Bot automatically stops when daily profit target (₹5,000) is reached
- Prevents overtrading and protects profits

#### Daily Loss Limit
- Bot stops trading if daily loss reaches ₹-3,000
- Protects capital from significant drawdowns

#### Performance Tracking
- Tracks win rate (target: 55%+)
- Tracks profit factor (target: 1.5+)
- Monitors average win vs average loss

## Scalping Strategy Details

### Entry Criteria
1. **Technical Signals**: At least 2 indicators must agree
2. **Momentum**: Strong price momentum (minimum 0.1)
3. **Volume**: Volume must be 1.5x above average
4. **Confidence**: Minimum 60% confidence score

### Exit Criteria
1. **Take Profit**: 0.5% profit target hit
2. **Stop Loss**: 0.3% loss limit hit
3. **Quick Exit**: 0.15% profit reached quickly
4. **Trailing Stop**: Price reverses 0.2% from peak
5. **Time Limit**: 5 minutes maximum holding time

### Risk Management
- **Position Size**: 1% of account per trade
- **Max Positions**: 10 concurrent positions
- **Max Position Value**: ₹5,000 per position
- **Total Risk**: Maximum 10% of account at any time

## Expected Performance

### Typical Scalping Trade
- **Holding Time**: 1-5 minutes
- **Profit Target**: 0.3% - 0.5%
- **Risk**: 0.3% stop loss
- **Win Rate**: Target 55%+

### Daily Expectations
- **Number of Trades**: 20-50 trades per day
- **Daily Profit Target**: ₹5,000
- **Daily Loss Limit**: ₹-3,000
- **Average Trade**: ₹100-200 profit per winning trade

## Best Practices

### 1. **Start Small**
- Begin with smaller position sizes
- Test the strategy with paper trading first
- Gradually increase size as you gain confidence

### 2. **Monitor Performance**
- Check win rate regularly
- Monitor profit factor
- Adjust parameters if performance degrades

### 3. **Market Conditions**
- Scalping works best in:
  - High volatility markets
  - High liquidity instruments
  - Active trading hours (10 AM - 2 PM IST)

### 4. **Risk Management**
- Never risk more than you can afford to lose
- Respect daily loss limits
- Don't override the bot's decisions manually

### 5. **Optimization**
- Adjust parameters based on market conditions
- Fine-tune stop-loss and take-profit levels
- Optimize for your specific symbols

## Configuration Tips

### For More Aggressive Scalping
```json
{
  "stop_loss_percentage": 0.25,
  "take_profit_percentage": 0.4,
  "quick_exit_threshold": 0.12,
  "max_holding_time_seconds": 180
}
```

### For More Conservative Scalping
```json
{
  "stop_loss_percentage": 0.4,
  "take_profit_percentage": 0.6,
  "quick_exit_threshold": 0.2,
  "max_holding_time_seconds": 600
}
```

### For Higher Profit Targets
```json
{
  "daily_profit_target": 10000,
  "daily_loss_limit": -5000,
  "max_positions": 15
}
```

## Common Questions

**Q: Why does the bot exit so quickly?**
A: Scalping requires quick exits to capture small profits and avoid reversals. The 5-minute max holding time ensures we don't hold losing positions.

**Q: What if I want bigger profits?**
A: You can increase `take_profit_percentage` but this may reduce win rate. Scalping is about many small wins, not few large wins.

**Q: Why so many trades?**
A: Scalping relies on high frequency. Many small profits add up. The bot aims for 20-50 trades per day.

**Q: What if the bot stops trading?**
A: The bot stops when daily profit target is reached or daily loss limit is hit. This protects profits and capital.

**Q: Can I run it overnight?**
A: No, the bot only trades during market hours (9:15 AM - 3:30 PM IST) on weekdays.

## Troubleshooting

### Low Win Rate
- Check if market conditions are suitable for scalping
- Verify volume requirements are being met
- Consider tightening entry criteria

### Not Enough Trades
- Check if symbols have sufficient liquidity
- Verify volume thresholds aren't too high
- Ensure market is active

### Hitting Loss Limit Too Quickly
- Reduce position sizes
- Tighten stop-losses further
- Check if market is too volatile

### Not Reaching Profit Target
- Increase number of positions
- Optimize entry criteria
- Check if take-profit levels are too high

## Important Notes

⚠️ **Scalping requires:**
- Fast internet connection
- Low latency to exchange
- Sufficient capital for multiple positions
- Active monitoring (even though bot is autonomous)

⚠️ **Risks:**
- High transaction costs (many trades)
- Slippage on quick entries/exits
- Market volatility can cause rapid losses
- Requires discipline to follow the strategy

⚠️ **Success Factors:**
- Consistent execution
- Proper risk management
- Suitable market conditions
- Regular performance monitoring
