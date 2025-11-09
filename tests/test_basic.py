"""
Basic unit tests for News Trading Platform
"""

import pytest
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_imports():
    """Test that all main modules can be imported"""
    try:
        from news_analysis.sentiment_analyzer import SentimentAnalyzer
        from blockchain.web3_client import BlockchainClient
        assert True
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")

def test_sentiment_analysis():
    """Test basic sentiment analysis functionality"""
    from news_analysis.sentiment_analyzer import SentimentAnalyzer
    
    analyzer = SentimentAnalyzer()
    
    # Test positive sentiment
    positive_text = "Great earnings report with strong growth outlook"
    result = analyzer.analyze_sentiment(positive_text)
    assert 'sentiment' in result
    assert isinstance(result['sentiment'], (int, float))
    
    # Test negative sentiment  
    negative_text = "Poor results and declining revenue forecast"
    result = analyzer.analyze_sentiment(negative_text)
    assert 'sentiment' in result

def test_config_loading():
    """Test configuration loading"""
    import yaml
    with open('config/trading_config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    assert 'trading' in config
    assert 'symbols' in config['trading']
    assert isinstance(config['trading']['symbols'], list)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
