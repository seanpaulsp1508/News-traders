#!/usr/bin/env python3
"""
Deployment script for news trading platform smart contracts
"""

import json
import argparse
from pathlib import Path
from web3 import Web3
from src.blockchain.web3_client import BlockchainClient
from loguru import logger

class ContractDeployer:
    def __init__(self, network='testnet'):
        self.client = BlockchainClient(network)
        self.network = network
        
    def deploy_contract(self, contract_name, constructor_args=None):
        """Deploy a single contract"""
        constructor_args = constructor_args or []
        
        # Load contract data
        contract_data = self.load_contract_data(contract_name)
        contract = self.client.w3.eth.contract(
            abi=contract_data['abi'],
            bytecode=contract_data['bytecode']
        )
        
        # Build deployment transaction
        constructor = contract.constructor(*constructor_args)
        transaction = constructor.build_transaction({
            'from': self.client.account.address,
            'nonce': self.client.w3.eth.get_transaction_count(self.client.account.address),
            'gasPrice': self.client.w3.eth.gas_price
        })
        
        # Estimate gas
        transaction['gas'] = self.client.w3.eth.estimate_gas(transaction)
        
        # Sign and send
        signed_txn = self.client.w3.eth.account.sign_transaction(
            transaction, self.client.private_key
        )
        tx_hash = self.client.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        # Wait for receipt
        receipt = self.client.w3.eth.wait_for_transaction_receipt(tx_hash)
        logger.info(f"✅ {contract_name} deployed at: {receipt.contractAddress}")
        
        return receipt.contractAddress
    
    def load_contract_data(self, contract_name):
        """Load contract ABI and bytecode"""
        artifact_path = Path(f'contracts/artifacts/{contract_name}.json')
        with open(artifact_path, 'r') as f:
            return json.load(f)
    
    def deploy_all_contracts(self):
        """Deploy all contracts in proper order"""
        logger.info(f"🚀 Deploying contracts to {self.network}...")
        
        # 1. Deploy NewsOracle first
        oracle_address = self.deploy_contract('NewsOracle')
        
        # 2. Deploy RiskManager
        risk_manager_address = self.deploy_contract('RiskManager')
        
        # 3. Deploy TradingEngine (depends on previous contracts)
        trading_engine_address = self.deploy_contract('TradingEngine', [
            oracle_address, risk_manager_address
        ])
        
        # Save deployment addresses
        addresses = {
            'NewsOracle': oracle_address,
            'RiskManager': risk_manager_address,
            'TradingEngine': trading_engine_address,
            'network': self.network,
            'deployer': self.client.account.address
        }
        
        self.save_deployment_addresses(addresses)
        return addresses
    
    def save_deployment_addresses(self, addresses):
        """Save deployment addresses to JSON file"""
        os.makedirs('deployments', exist_ok=True)
        filename = f'deployments/{self.network}_addresses.json'
        
        with open(filename, 'w') as f:
            json.dump(addresses, f, indent=2)
        
        logger.info(f"📄 Deployment addresses saved to: {filename}")

def main():
    parser = argparse.ArgumentParser(description='Deploy News Trading Contracts')
    parser.add_argument('--network', choices=['testnet', 'mainnet'], default='testnet')
    parser.add_argument('--contract', help='Deploy specific contract')
    
    args = parser.parse_args()
    
    try:
        deployer = ContractDeployer(args.network)
        
        if not deployer.client.is_connected():
            logger.error("❌ Failed to connect to blockchain network")
            return
        
        logger.info(f"🌐 Connected to {args.network}")
        logger.info(f"💰 Account balance: {deployer.client.get_balance()} RBTC")
        
        if args.contract:
            # Deploy specific contract
            address = deployer.deploy_contract(args.contract)
            logger.info(f"✅ {args.contract} deployed at: {address}")
        else:
            # Deploy all contracts
            addresses = deployer.deploy_all_contracts()
            
            print("\n" + "="*50)
            print("🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!")
            print("="*50)
            for contract, address in addresses.items():
                if contract not in ['network', 'deployer']:
                    print(f"📄 {contract}: {address}")
            
    except Exception as e:
        logger.error(f"❌ Deployment failed: {e}")
        raise

if __name__ == "__main__":
    main()
