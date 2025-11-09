// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title NewsOracle
 * @dev Decentralized oracle for storing and verifying news sentiment data
 */
contract NewsOracle {
    struct NewsRecord {
        string symbol;
        string headline;
        int256 sentiment;
        uint256 timestamp;
        address provider;
        bytes32 contentHash;
        uint256 confidence;
    }
    
    address public owner;
    mapping(bytes32 => NewsRecord) public newsRecords;
    mapping(address => bool) public authorizedProviders;
    mapping(string => NewsRecord[]) public symbolNewsHistory;
    
    event NewsRecorded(
        bytes32 indexed newsId,
        string symbol,
        int256 sentiment,
        uint256 timestamp
    );
    
    event ProviderAuthorized(address provider);
    event ProviderRevoked(address provider);
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can perform this action");
        _;
    }
    
    modifier onlyAuthorized() {
        require(authorizedProviders[msg.sender], "Not authorized provider");
        _;
    }
    
    constructor() {
        owner = msg.sender;
        authorizedProviders[msg.sender] = true;
    }
    
    /**
     * @dev Record news sentiment on-chain
     */
    function recordNews(
        string memory symbol,
        string memory headline,
        int256 sentiment,
        bytes32 contentHash,
        uint256 confidence
    ) external onlyAuthorized returns (bytes32) {
        require(sentiment >= -100 && sentiment <= 100, "Invalid sentiment range");
        require(confidence > 0 && confidence <= 100, "Invalid confidence");
        
        bytes32 newsId = keccak256(abi.encodePacked(symbol, headline, block.timestamp));
        
        NewsRecord memory record = NewsRecord({
            symbol: symbol,
            headline: headline,
            sentiment: sentiment,
            timestamp: block.timestamp,
            provider: msg.sender,
            contentHash: contentHash,
            confidence: confidence
        });
        
        newsRecords[newsId] = record;
        symbolNewsHistory[symbol].push(record);
        
        emit NewsRecorded(newsId, symbol, sentiment, block.timestamp);
        return newsId;
    }
    
    /**
     * @dev Get latest sentiment for a symbol
     */
    function getLatestSentiment(string memory symbol) 
        external 
        view 
        returns (int256, uint256, uint256) 
    {
        NewsRecord[] storage history = symbolNewsHistory[symbol];
        if (history.length == 0) {
            return (0, 0, 0);
        }
        
        NewsRecord memory latest = history[history.length - 1];
        return (latest.sentiment, latest.confidence, latest.timestamp);
    }
    
    /**
     * @dev Authorize a news provider
     */
    function authorizeProvider(address provider) external onlyOwner {
        authorizedProviders[provider] = true;
        emit ProviderAuthorized(provider);
    }
    
    /**
     * @dev Revoke provider authorization
     */
    function revokeProvider(address provider) external onlyOwner {
        authorizedProviders[provider] = false;
        emit ProviderRevoked(provider);
    }
}
