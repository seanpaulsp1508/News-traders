"""
Web3 client for blockchain interactions with enhanced error handling and retry logic
"""

import os
import time
from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.exceptions import TransactionNotFound, ContractLogicError
from loguru import logger
from config.blockchain_config import NETWORKS

class BlockchainClient:
    def __init__(self, network='testnet', private_key=None):
        self.network = network
        self.config = NETWORKS[network]
        
        # Initialize Web3 connection
        self.w3 = Web3(Web3.HTTPProvider(self.config['rpc_url']))
        
        # Add POA middleware for compatibility
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        # Set up account
        self.private_key = private_key or os.getenv('BLOCKCHAIN_PRIVATE_KEY')
        if self.private_key:
            self.account = self.w3.eth.account.from_key(self.private_key)
            logger.info(f"🔗 Connected with account: {self.account.address}")
        else:
            logger.warning("⚠️  No private key provided - read-only mode")
            self.account = None
        
        # Contract cache
        self._contracts = {}
    
    def is_connected(self):
        """Check blockchain connection"""
        try:
            return self.w3.is_connected()
        except:
            return False
    
    def get_balance(self, address=None, token='native'):
        """Get balance for address"""
        address = address or self.account.address
        
        if token == 'native':
            balance_wei = self.w3.eth.get_balance(address)
            return self.w3.from_wei(balance_wei, 'ether')
        else:
            # ERC20 token balance
            token_contract = self.get_contract('IERC20', self.config['tokens'][token])
            balance = token_contract.functions.balanceOf(address).call()
            decimals = token_contract.functions.decimals().call()
            return balance / (10 ** decimals)
    
    def get_contract(self, contract_name, address=None):
        """Get contract instance with caching"""
        cache_key = f"{contract_name}_{address}"
        
        if cache_key not in self._contracts:
            contract_address = address or self.config['contracts'].get(contract_name)
            if not contract_address:
                raise ValueError(f"Contract address for {contract_name} not found")
            
            abi = self.load_contract_abi(contract_name)
            self._contracts[cache_key] = self.w3.eth.contract(
                address=contract_address,
                abi=abi
            )
        
        return self._contracts[cache_key]
    
    def send_transaction(self, transaction, retries=3):
        """Send transaction with retry logic"""
        for attempt in range(retries):
            try:
                if not self.account:
                    raise ValueError("No account available for sending transactions")
                
                # Build transaction
                if 'nonce' not in transaction:
                    transaction['nonce'] = self.w3.eth.get_transaction_count(self.account.address)
                
                if 'gasPrice' not in transaction:
                    transaction['gasPrice'] = self.w3.eth.gas_price
                
                if 'gas' not in transaction:
                    transaction['gas'] = self.w3.eth.estimate_gas(transaction)
                
                # Sign and send
                signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
                tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
                
                logger.info(f"📤 Transaction sent: {tx_hash.hex()}")
                return tx_hash
                
            except Exception as e:
                if attempt == retries - 1:
                    raise e
                logger.warning(f"Retrying transaction ({attempt + 1}/{retries}): {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
    
    def wait_for_confirmation(self, tx_hash, timeout=120):
        """Wait for transaction confirmation"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                receipt = self.w3.eth.get_transaction_receipt(tx_hash)
                if receipt is not None:
                    return receipt
            except TransactionNotFound:
                pass
            
            time.sleep(5)
        
        raise TimeoutError(f"Transaction {tx_hash.hex()} not confirmed within {timeout} seconds")
