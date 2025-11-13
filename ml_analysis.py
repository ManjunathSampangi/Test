"""
Machine Learning Enhanced Analysis
Uses ensemble ML models for better predictions
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MLAnalysis:
    def __init__(self, config: Dict = None):
        """
        Initialize ML Analysis module
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.scaler = StandardScaler()
        self.models = {
            'random_forest': RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42),
            'gradient_boosting': GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
        }
        self.is_trained = False
        
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare features for ML model
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with features
        """
        features_df = df.copy()
        
        # Price features
        features_df['returns'] = df['close'].pct_change()
        features_df['returns_5'] = df['close'].pct_change(5)
        features_df['returns_10'] = df['close'].pct_change(10)
        
        # Volatility
        features_df['volatility'] = df['close'].pct_change().rolling(10).std()
        features_df['atr'] = self._calculate_atr(df)
        
        # Moving averages
        features_df['sma_5'] = df['close'].rolling(5).mean()
        features_df['sma_10'] = df['close'].rolling(10).mean()
        features_df['sma_20'] = df['close'].rolling(20).mean()
        features_df['ema_9'] = df['close'].ewm(span=9, adjust=False).mean()
        features_df['ema_21'] = df['close'].ewm(span=21, adjust=False).mean()
        
        # Price position
        features_df['price_sma5'] = (df['close'] - features_df['sma_5']) / features_df['sma_5']
        features_df['price_sma10'] = (df['close'] - features_df['sma_10']) / features_df['sma_10']
        features_df['price_sma20'] = (df['close'] - features_df['sma_20']) / features_df['sma_20']
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        features_df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        macd_data = self._calculate_macd(df)
        features_df['macd'] = macd_data['macd']
        features_df['macd_signal'] = macd_data['signal']
        features_df['macd_hist'] = macd_data['histogram']
        
        # Bollinger Bands
        bb_data = self._calculate_bollinger_bands(df)
        features_df['bb_upper'] = bb_data['upper']
        features_df['bb_lower'] = bb_data['lower']
        features_df['bb_position'] = (df['close'] - bb_data['lower']) / (bb_data['upper'] - bb_data['lower'])
        
        # Volume features
        features_df['volume_ma'] = df['volume'].rolling(20).mean()
        features_df['volume_ratio'] = df['volume'] / features_df['volume_ma']
        features_df['volume_change'] = df['volume'].pct_change()
        
        # Momentum
        features_df['momentum'] = df['close'].pct_change(5)
        features_df['momentum_10'] = df['close'].pct_change(10)
        
        # High-Low features
        features_df['hl_ratio'] = (df['high'] - df['low']) / df['close']
        features_df['close_position'] = (df['close'] - df['low']) / (df['high'] - df['low'])
        
        return features_df
    
    def create_target(self, df: pd.DataFrame, forward_periods: int = 5) -> pd.Series:
        """
        Create target variable (future price direction)
        
        Args:
            df: DataFrame with price data
            forward_periods: Number of periods to look ahead
            
        Returns:
            Target series (1 for up, 0 for down)
        """
        future_return = df['close'].shift(-forward_periods) / df['close'] - 1
        target = (future_return > 0.005).astype(int)  # 0.5% threshold
        return target
    
    def train_models(self, df: pd.DataFrame):
        """
        Train ML models on historical data
        
        Args:
            df: Historical DataFrame with OHLCV data
        """
        try:
            if len(df) < 100:
                logger.warning("Insufficient data for training")
                return
            
            # Prepare features
            features_df = self.prepare_features(df)
            
            # Create target
            target = self.create_target(df)
            
            # Select feature columns
            feature_columns = [
                'returns', 'returns_5', 'returns_10', 'volatility', 'atr',
                'price_sma5', 'price_sma10', 'price_sma20',
                'rsi', 'macd', 'macd_signal', 'macd_hist',
                'bb_position', 'volume_ratio', 'volume_change',
                'momentum', 'momentum_10', 'hl_ratio', 'close_position'
            ]
            
            # Prepare data
            X = features_df[feature_columns].dropna()
            y = target.loc[X.index]
            
            # Remove rows where target is NaN
            valid_idx = ~y.isna()
            X = X[valid_idx]
            y = y[valid_idx]
            
            if len(X) < 50:
                logger.warning("Not enough valid data points for training")
                return
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train models
            for name, model in self.models.items():
                model.fit(X_train_scaled, y_train)
                train_score = model.score(X_train_scaled, y_train)
                test_score = model.score(X_test_scaled, y_test)
                logger.info(f"{name} - Train score: {train_score:.3f}, Test score: {test_score:.3f}")
            
            self.is_trained = True
            self.feature_columns = feature_columns
            
        except Exception as e:
            logger.error(f"Error training models: {str(e)}")
            self.is_trained = False
    
    def predict(self, df: pd.DataFrame) -> Dict:
        """
        Predict price direction using ensemble of ML models
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Prediction dictionary
        """
        if not self.is_trained:
            # Use rule-based prediction if models not trained
            return self._rule_based_prediction(df)
        
        try:
            # Prepare features
            features_df = self.prepare_features(df)
            
            # Get latest features
            X = features_df[self.feature_columns].iloc[-1:].dropna()
            
            if X.empty:
                return self._rule_based_prediction(df)
            
            # Scale features
            X_scaled = self.scaler.transform(X)
            
            # Get predictions from all models
            predictions = {}
            probabilities = {}
            
            for name, model in self.models.items():
                pred = model.predict(X_scaled)[0]
                prob = model.predict_proba(X_scaled)[0]
                predictions[name] = pred
                probabilities[name] = prob[1] if len(prob) > 1 else prob[0]
            
            # Ensemble prediction (weighted average)
            avg_probability = np.mean(list(probabilities.values()))
            ensemble_prediction = 1 if avg_probability > 0.5 else 0
            
            # Calculate confidence
            confidence = abs(avg_probability - 0.5) * 2  # Scale to 0-1
            
            signal = 'BUY' if ensemble_prediction == 1 else 'SELL'
            
            return {
                'prediction': signal,
                'confidence': confidence,
                'probability': avg_probability,
                'model_predictions': predictions,
                'model_probabilities': probabilities,
                'ensemble': True
            }
            
        except Exception as e:
            logger.error(f"Error in ML prediction: {str(e)}")
            return self._rule_based_prediction(df)
    
    def _rule_based_prediction(self, df: pd.DataFrame) -> Dict:
        """Fallback rule-based prediction"""
        if len(df) < 20:
            return {'prediction': 'HOLD', 'confidence': 0.0}
        
        # Simple momentum-based prediction
        returns_5 = df['close'].pct_change(5).iloc[-1]
        returns_10 = df['close'].pct_change(10).iloc[-1]
        
        if returns_5 > 0.01 and returns_10 > 0:
            signal = 'BUY'
            confidence = min(abs(returns_5) * 10, 0.7)
        elif returns_5 < -0.01 and returns_10 < 0:
            signal = 'SELL'
            confidence = min(abs(returns_5) * 10, 0.7)
        else:
            signal = 'HOLD'
            confidence = 0.0
        
        return {
            'prediction': signal,
            'confidence': confidence,
            'probability': 0.5 + (confidence / 2) if signal != 'HOLD' else 0.5,
            'ensemble': False
        }
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        return true_range.rolling(window=period).mean()
    
    def _calculate_macd(self, df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
        """Calculate MACD"""
        ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line
        return {'macd': macd, 'signal': signal_line, 'histogram': histogram}
    
    def _calculate_bollinger_bands(self, df: pd.DataFrame, period: int = 20, std_dev: int = 2) -> Dict:
        """Calculate Bollinger Bands"""
        sma = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        return {'upper': upper_band, 'middle': sma, 'lower': lower_band}
