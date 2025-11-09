"""
Blockchain network configuration for multi-chain support
"""

NETWORKS = {
    'testnet': {
        'rpc_url': 'https://testnet.sovryn.app/rpc',
        'chain_id': 31,
        'explorer': 'https://explorer.testnet.rsk.co',
        'gas_price': 1000000000,
        'contracts': {
            'NewsOracle': '0x...',
            'TradingEngine': '0x...',
            'RiskManager': '0x...'
        }
    },
    'mainnet': {
        'rpc_url': 'https://mainnet.sovryn.app/rpc',
        'chain_id': 30,
        'explorer': 'https://explorer.rsk.co',
        'gas_price': 1000000000,
        'contracts': {
            'NewsOracle': '0x...',
            'TradingEngine': '0x...',
            'RiskManager': '0x...'
        }
    }
}

TOKEN_ADDRESSES = {
    'native': '0x0000000000000000000000000000000000000000',
    'DOC': '0xe700691da7b9851f2f35f8b8182c69c53ccad9db',
    'RIF': '0x19f64674d8a5b4e652319f5e239efd3bc969a1fe'
}
