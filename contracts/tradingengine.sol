// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "./interfaces/INewsOracle.sol";
import "./interfaces/IRiskManager.sol";

/**
 * @title TradingEngine
 * @dev Core trading engine that executes trades based on news sentiment
 */
contract TradingEngine {
    INewsOracle public newsOracle;
    IRiskManager public riskManager;
    address public owner;
    
    enum TradeAction { BUY, SELL }
    
    struct Trade {
        address trader;
        string symbol;
        TradeAction action;
        uint256 amount;
        uint256 price;
        int256 sentiment;
        uint256 timestamp;
        bytes32 newsId;
        bool executed;
    }
    
    mapping(address => Trade[]) public tradeHistory;
    mapping(bytes32 => bool) public executedNews;
    mapping(string => uint256) public lastTradeTime;
    
    uint256 public constant COOLDOWN_PERIOD = 30 minutes;
    
    event TradeExecuted(
        address indexed trader,
        string symbol,
        TradeAction action,
        uint256 amount,
        uint256 price,
        int256 sentiment,
        bytes32 newsId
    );
    
    event TradeRejected(
        address trader,
        string symbol,
        string reason
    );
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner");
        _;
    }
    
    constructor(address _newsOracle, address _riskManager) {
        owner = msg.sender;
        newsOracle = INewsOracle(_newsOracle);
        riskManager = IRiskManager(_riskManager);
    }
    
    /**
     * @dev Execute a trade based on news sentiment
     */
    function executeTrade(
        string memory symbol,
        TradeAction action,
        uint256 amount,
        uint256 price,
        bytes32 newsId
    ) external returns (bool) {
        // Prevent duplicate execution
        require(!executedNews[newsId], "Trade already executed for this news");
        
        // Check cooldown period
        require(
            block.timestamp - lastTradeTime[symbol] >= COOLDOWN_PERIOD,
            "Cooldown period active"
        );
        
        // Get sentiment from oracle
        (int256 sentiment, uint256 confidence, ) = newsOracle.getLatestSentiment(symbol);
        require(confidence >= 50, "Low confidence sentiment");
        
        // Validate trade with risk manager
        bool riskApproved = riskManager.validateTrade(
            msg.sender,
            symbol,
            amount,
            price,
            sentiment,
            action == TradeAction.BUY
        );
        
        if (!riskApproved) {
            emit TradeRejected(msg.sender, symbol, "Risk validation failed");
            return false;
        }
        
        // Execute trade
        Trade memory trade = Trade({
            trader: msg.sender,
            symbol: symbol,
            action: action,
            amount: amount,
            price: price,
            sentiment: sentiment,
            timestamp: block.timestamp,
            newsId: newsId,
            executed: true
        });
        
        tradeHistory[msg.sender].push(trade);
        executedNews[newsId] = true;
        lastTradeTime[symbol] = block.timestamp;
        
        emit TradeExecuted(
            msg.sender,
            symbol,
            action,
            amount,
            price,
            sentiment,
            newsId
        );
        
        return true;
    }
    
    /**
     * @dev Get user's trade history
     */
    function getTradeHistory(address user) 
        external 
        view 
        returns (Trade[] memory) 
    {
        return tradeHistory[user];
    }
    
    /**
     * @dev Update oracle address
     */
    function updateOracle(address newOracle) external onlyOwner {
        newsOracle = INewsOracle(newOracle);
    }
    
    /**
     * @dev Update risk manager address
     */
    function updateRiskManager(address newRiskManager) external onlyOwner {
        riskManager = IRiskManager(newRiskManager);
    }
}
