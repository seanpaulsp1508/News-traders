"""
Advanced sentiment analysis with multiple models and blockchain integration
"""

import asyncio
import pandas as pd
import numpy as np
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import torch
from loguru import logger

class AdvancedSentimentAnalyzer:
    def __init__(self, blockchain_client=None):
        self.vader = SentimentIntensityAnalyzer()
        self.blockchain_client = blockchain_client
        
        # Initialize transformer models
        self.models = {}
        self.load_models()
        
        logger.info("🧠 Sentiment analyzer initialized")
    
    def load_models(self):
        """Load all sentiment analysis models"""
        try:
            # FinBERT for financial text
            self.models['finbert'] = pipeline(
                "sentiment-analysis",
                model="ProsusAI/finbert",
                tokenizer="ProsusAI/finbert",
                max_length=512
            )
        except Exception as e:
            logger.warning(f"Could not load FinBERT: {e}")
            self.models['finbert'] = None
        
        # VADER is already loaded
        self.models['vader'] = self.vader
        
    def analyze_news_batch(self, news_df):
        """Analyze sentiment for a batch of news articles"""
        results = []
        
        for _, row in news_df.iterrows():
            sentiment_result = self.analyze_single_news(
                row['title'],
                row.get('description', ''),
                row.get('content', ''),
                row['symbol']
            )
            
            results.append({
                **row.to_dict(),
                **sentiment_result
            })
        
        return pd.DataFrame(results)
    
    def analyze_single_news(self, title, description, content, symbol):
        """Analyze sentiment for a single news article"""
        # Combine text for analysis
        full_text = f"{title}. {description}. {content}"[:2000]  # Limit length
        
        # Get sentiment from all models
        vader_score = self.analyze_vader(full_text)
        textblob_score = self.analyze_textblob(full_text)
        finbert_score = self.analyze_finbert(full_text)
        
        # Calculate combined score with weights
        scores = {
            'vader': vader_score,
            'textblob': textblob_score,
            'finbert': finbert_score
        }
        
        # Remove None scores
        valid_scores = {k: v for k, v in scores.items() if v is not None}
        
        if not valid_scores:
            combined = 0.0
        else:
            # Weighted average (FinBERT gets higher weight)
            weights = {'vader': 0.3, 'textblob': 0.2, 'finbert': 0.5}
            total_weight = sum(weights[k] for k in valid_scores.keys())
            combined = sum(scores[k] * weights[k] for k in valid_scores.keys()) / total_weight
        
        result = {
            'vader_sentiment': vader_score,
            'textblob_sentiment': textblob_score,
            'finbert_sentiment': finbert_score,
            'combined_sentiment': combined,
            'sentiment_confidence': self.calculate_confidence(scores),
            'analysis_timestamp': pd.Timestamp.now()
        }
        
        # Record on blockchain if client available
        if self.blockchain_client and abs(combined) > 0.3:  # Only record significant sentiment
            asyncio.create_task(
                self.record_sentiment_on_blockchain(symbol, full_text, combined)
            )
        
        return result
    
    def analyze_vader(self, text):
        """VADER sentiment analysis"""
        try:
            scores = self.vader.polarity_scores(text)
            return scores['compound']
        except:
            return 0.0
    
    def analyze_textblob(self, text):
        """TextBlob sentiment analysis"""
        try:
            blob = TextBlob(text)
            return blob.sentiment.polarity
        except:
            return 0.0
    
    def analyze_finbert(self, text):
        """FinBERT sentiment analysis"""
        if self.models['finbert'] is None:
            return 0.0
        
        try:
            result = self.models['finbert'](text[:512])[0]  # Truncate for model limits
            label = result['label']
            score = result['score']
            
            if label == 'positive':
                return score
            elif label == 'negative':
                return -score
            else:
                return 0.0
        except Exception as e:
            logger.warning(f"FinBERT analysis failed: {e}")
            return 0.0
    
    def calculate_confidence(self, scores):
        """Calculate confidence based on model agreement"""
        non_zero_scores = [s for s in scores.values() if s is not None and s != 0]
        if not non_zero_scores:
            return 0.0
        
        # Confidence based on magnitude and agreement
        avg_magnitude = np.mean([abs(s) for s in non_zero_scores])
        return min(1.0, avg_magnitude * 1.5)
    
    async def record_sentiment_on_blockchain(self, symbol, content, sentiment):
        """Record sentiment analysis on blockchain"""
        try:
            if not self.blockchain_client:
                return
            
            oracle_contract = self.blockchain_client.get_contract('NewsOracle')
            
            # Create content hash
            content_hash = self.blockchain_client.w3.keccak(text=content[:500])
            confidence = int(self.calculate_confidence({'sentiment': sentiment}) * 100)
            scaled_sentiment = int(sentiment * 100)
            
            # Build transaction
            transaction = oracle_contract.functions.recordNews(
                symbol,
                content[:100],  # Headline
                scaled_sentiment,
                content_hash,
                confidence
            ).build_transaction({
                'from': self.blockchain_client.account.address,
                'gas': 200000
            })
            
            # Send transaction
            tx_hash = self.blockchain_client.send_transaction(transaction)
            logger.info(f"📝 Recorded sentiment on blockchain: {symbol} = {sentiment:.3f}")
            
        except Exception as e:
            logger.error(f"Failed to record sentiment on blockchain: {e}")
