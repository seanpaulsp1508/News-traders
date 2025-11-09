"""
Network and Connectivity Configuration for News Trading Platform

This module contains all network-related settings including:
- API endpoints and rate limits
- Blockchain RPC configurations
- WebSocket connections
- Timeout and retry settings
- Network security parameters
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from decimal import Decimal

@dataclass
class APIConfig:
    """Configuration for API endpoints"""
    base_url: str
    api_key: Optional[str] = None
    secret_key: Optional[str] = None
    rate_limit_per_minute: int = 60
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0

@dataclass
class BlockchainNodeConfig:
    """Configuration for blockchain node connections"""
    rpc_url: str
    ws_url: Optional[str] = None
    chain_id: int = 1
    gas_price: int = 1000000000  # 1 Gwei
    gas_limit: int = 1000000
    confirmation_blocks: int = 3
    timeout: int = 60

@dataclass
class DatabaseConfig:
    """Database connection configuration"""
    host: str
    port: int
    database: str
    username: str
    password: str
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30

class NetworkSettings:
    """
    Main network configuration class that consolidates all network settings
    """
    
    # ==================== NEWS API CONFIGURATIONS ====================
    
    NEWS_API_CONFIGS = {
        'newsapi': APIConfig(
            base_url='https://newsapi.org/v2',
            api_key=os.getenv('NEWSAPI_KEY'),
            rate_limit_per_minute=1000,  # NewsAPI limit
            timeout=30
        ),
        
        'alphavantage': APIConfig(
            base_url='https://www.alphavantage.co/query',
            api_key=os.getenv('ALPHAVANTAGE_KEY'),
            rate_limit_per_minute=5,  # Alpha Vantage free tier limit
            timeout=45
        ),
        
        'polygon': APIConfig(
            base_url='https://api.polygon.io/v2',
            api_key=os.getenv('POLYGON_API_KEY'),
            rate_limit_per_minute=500,
            timeout=30
        ),
        
        'financialmodelingprep': APIConfig(
            base_url='https://financialmodelingprep.com/api/v3',
            api_key=os.getenv('FMP_API_KEY'),
            rate_limit_per_minute
