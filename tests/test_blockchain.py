"""
Comprehensive tests for blockchain integration
"""

import pytest
import asyncio
from web3 import Web3
from src.blockchain.web3_client import BlockchainClient
from src.news_analysis.sentiment_analyzer import AdvancedSentimentAnalyzer

class TestBlockchainIntegration:
    @pytest.fixture
    def blockchain_client(self):
        return BlockchainClient(network='testnet')
    
    @pytest.fixture
    def sentiment_analyzer(self, blockchain_client):
        return AdvancedSentimentAnalyzer(blockchain_client)
    
    def test_blockchain_connection(self, blockchain_client):
        """Test blockchain connection"""
        assert blockchain_client.is_connected() == True
    
    def test_account_balance(self, blockchain_client):
        """Test balance checking"""
        balance = blockchain_client.get_balance()
        assert isinstance(balance, float)
        assert balance >= 0
    
    def test_sentiment_analysis(self, sentiment_analyzer):
        """Test sentiment analysis functionality"""
        test_text = "Company reports strong earnings with 20% growth"
        result = sentiment_analyzer.analyze_single_news(
            test_text, "", "", "TEST"
        )
        
        assert 'combined_sentiment' in result
        assert -1 <= result['combined_sentiment'] <= 1
        assert 'sentiment_confidence' in result
    
    def test_positive_sentiment(self, sentiment_analyzer):
        """Test positive sentiment detection"""
        positive_news = "Amazing results and outstanding performance"
        result = sentiment_analyzer.analyze_single_news(
            positive_news, "", "", "TEST"
        )
        assert result['combined_sentiment'] > 0
    
    def test_negative_sentiment(self, sentiment_analyzer):
        """Test negative sentiment detection"""
        negative_news = "Terrible earnings and massive losses reported"
        result = sentiment_analyzer.analyze_single_news(
            negative_news, "", "", "TEST"
        )
        assert result['combined_sentiment'] < 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
