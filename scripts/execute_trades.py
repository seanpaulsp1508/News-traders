#!/usr/bin/env python3
"""
Main trading execution script with blockchain integration
"""

import asyncio
import yaml
import schedule
import time
from datetime import datetime
from src.blockchain.web3_client import BlockchainClient
from src.news_analysis.news_collector import NewsCollector
from src.news_analysis.sentiment_analyzer import AdvancedSentimentAnalyzer
from src.trading.risk_engine import RiskEngine
from loguru import logger

class NewsTradingBot:
    def __init__(self, config_path='config/trading_config.yaml'):
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize components
        self.blockchain_client = BlockchainClient(
            network=self.config['blockchain']['network']
        )
        self.news_collector = NewsCollector(self.config)
        self.sentiment_analyzer = AdvancedSentimentAnalyzer(self.blockchain_client)
        self.risk_engine = RiskEngine(self.config)
        
        # Trading state
        self.active_positions = {}
        self.trade_history = []
        self.daily_pnl = 0.0
        
        logger.info("🤖 News Trading Bot initialized")
    
    async def run_trading_cycle(self):
        """Execute one complete trading cycle"""
        try:
            logger.info("🔁 Starting trading cycle...")
            
            # 1. Collect and analyze news
            news_data = await self.news_collector.fetch_latest_news()
            if news_data.empty:
                logger.warning("No new news data available")
                return
            
            # 2. Analyze sentiment
            analyzed_data = self.sentiment_analyzer.analyze_news_with_blockchain(news_data)
            
            # 3. Generate trading signals
            signals = self.generate_trading_signals(analyzed_data)
            
            # 4. Execute trades
            for signal in signals:
                if await self.execute_trade(signal):
                    logger.info(f"✅ Trade executed: {signal}")
            
            logger.info("✅ Trading cycle completed")
            
        except Exception as e:
            logger.error(f"❌ Error in trading cycle: {e}")
    
    def generate_trading_signals(self, analyzed_data):
        """Generate trading signals from analyzed news"""
        signals = []
        
        for symbol in analyzed_data['symbol'].unique():
            symbol_data = analyzed_data[analyzed_data['symbol'] == symbol]
            latest = symbol_data.iloc[-1]
            
            sentiment = latest['combined_sentiment']
            confidence = latest.get('confidence', 0.8)
            
            # Generate signal based on sentiment thresholds
            if sentiment > self.config['sentiment']['thresholds']['strong_buy']:
                action = 'BUY'
                size = self.calculate_position_size(symbol, sentiment, confidence)
                signals.append({
                    'symbol': symbol,
                    'action': action,
                    'size': size,
                    'sentiment': sentiment,
                    'confidence': confidence,
                    'timestamp': datetime.now()
                })
            elif sentiment < self.config['sentiment']['thresholds']['strong_sell']:
                action = 'SELL' 
                size = self.calculate_position_size(symbol, sentiment, confidence)
                signals.append({
                    'symbol': symbol,
                    'action': action,
                    'size': size,
                    'sentiment': sentiment,
                    'confidence': confidence,
                    'timestamp': datetime.now()
                })
        
        return signals
    
    async def execute_trade(self, signal):
        """Execute a single trade through blockchain"""
        try:
            # Validate with risk engine
            if not self.risk_engine.validate_trade(signal, self.active_positions):
                logger.warning(f"🚫 Trade rejected by risk engine: {signal}")
                return False
            
            # Execute on blockchain
            trading_engine = self.blockchain_client.get_contract('TradingEngine')
            
            # Convert signal to blockchain format
            tx_hash = trading_engine.functions.executeTrade(
                signal['symbol'],
                0 if signal['action'] == 'BUY' else 1,  # 0=BUY, 1=SELL
                int(signal['size'] * 1e18),  # Convert to wei
                self.get_current_price(signal['symbol']),
                int(signal['sentiment'] * 100)  # Scale sentiment
            ).transact()
            
            # Wait for confirmation
            receipt = self.blockchain_client.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                logger.success(f"✅ Trade executed on blockchain: {tx_hash.hex()}")
                self.record_trade(signal, tx_hash.hex())
                return True
            else:
                logger.error(f"❌ Trade execution failed: {tx_hash.hex()}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Trade execution error: {e}")
            return False
    
    def start(self):
        """Start the trading bot"""
        logger.info("🚀 Starting News Trading Bot...")
        
        # Schedule trading cycles
        schedule.every(5).minutes.do(lambda: asyncio.create_task(self.run_trading_cycle()))
        
        # Initial run
        asyncio.create_task(self.run_trading_cycle())
        
        # Main loop
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("🛑 Trading bot stopped by user")
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Clean shutdown"""
        logger.info("🔚 Shutting down trading bot...")
        # Close positions, save state, etc.

def main():
    """Main entry point"""
    bot = NewsTradingBot()
    bot.start()

if __name__ == "__main__":
    main()
