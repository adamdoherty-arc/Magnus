const logger = require('../utils/logger');

class PremiumOptimizer {
  constructor(dataProvider, database) {
    this.dataProvider = dataProvider;
    this.database = database;
    this.weights = {
      // Confidence scoring weights
      premium: 0.25,
      probability: 0.20,
      liquidity: 0.15,
      volatility: 0.15,
      fundamentals: 0.10,
      technicals: 0.10,
      history: 0.05
    };
  }

  async findBestOpportunities() {
    const opportunities = [];
    
    // Get stocks from database
    const holdings = await this.database.getMyStocks();
    const watchlist = await this.database.getWatchlistStocks();
    const historicalTrades = await this.database.getHistoricalTrades();
    
    logger.info(`Analyzing ${holdings.length} holdings and ${watchlist.length} watchlist stocks`);
    
    // Analyze covered call opportunities for holdings
    for (const holding of holdings) {
      try {
        const ccOpportunities = await this.analyzeCoveredCalls(holding, historicalTrades);
        opportunities.push(...ccOpportunities);
      } catch (error) {
        logger.error(`Error analyzing covered calls for ${holding.symbol}:`, error.message);
      }
    }
    
    // Analyze cash-secured put opportunities for watchlist
    for (const stock of watchlist) {
      try {
        const putOpportunities = await this.analyzeCashSecuredPuts(stock, historicalTrades);
        opportunities.push(...putOpportunities);
      } catch (error) {
        logger.error(`Error analyzing puts for ${stock.symbol}:`, error.message);
      }
    }
    
    // Sort by confidence score
    opportunities.sort((a, b) => b.confidenceScore - a.confidenceScore);
    
    // Save top opportunities to database
    for (const opp of opportunities.slice(0, 20)) {
      await this.database.saveOpportunity(opp);
    }
    
    return opportunities;
  }

  async analyzeCoveredCalls(holding, historicalTrades) {
    const opportunities = [];
    
    try {
      // Get current stock data
      const stockData = await this.dataProvider.getStockData(holding.symbol);
      const optionsChain = await this.dataProvider.getOptionsChain(holding.symbol);
      const fundamentals = await this.dataProvider.getFundamentals(holding.symbol);
      
      // Calculate key metrics
      const currentPrice = stockData.currentPrice;
      const costBasis = holding.cost_basis;
      const shares = holding.shares;
      const contracts = Math.floor(shares / 100);
      
      if (contracts === 0) return opportunities;
      
      // Analyze each call option
      for (const call of optionsChain.calls || []) {
        // Skip if strike is below cost basis (don't lock in losses)
        if (call.strike < costBasis * 1.01) continue;
        
        // Skip if expiration is too far or too close
        if (call.daysToExpiration < 7 || call.daysToExpiration > 60) continue;
        
        // Skip illiquid options
        if (call.volume < 50 || call.openInterest < 100) continue;
        
        const opportunity = {
          symbol: holding.symbol,
          strategy: 'covered-call',
          strike: call.strike,
          premium: call.premium,
          expiration: call.expiration,
          daysToExpiration: call.daysToExpiration,
          contracts: contracts,
          currentPrice: currentPrice,
          costBasis: costBasis,
          shares: shares
        };
        
        // Calculate returns and risks
        opportunity.analysis = this.calculateCoveredCallMetrics(opportunity, stockData, fundamentals);
        
        // Calculate confidence and risk scores
        opportunity.confidenceScore = this.calculateConfidenceScore(opportunity, historicalTrades);
        opportunity.riskScore = this.calculateRiskScore(opportunity, stockData);
        
        // Expected return
        opportunity.expectedReturn = opportunity.analysis.annualizedReturn;
        
        // Add recommendation
        opportunity.recommendation = this.getRecommendation(opportunity);
        
        opportunities.push(opportunity);
      }
    } catch (error) {
      logger.error(`Failed to analyze covered calls for ${holding.symbol}:`, error);
    }
    
    return opportunities;
  }

  async analyzeCashSecuredPuts(stock, historicalTrades) {
    const opportunities = [];
    
    try {
      // Get current stock data
      const stockData = await this.dataProvider.getStockData(stock.symbol);
      const optionsChain = await this.dataProvider.getOptionsChain(stock.symbol);
      const fundamentals = await this.dataProvider.getFundamentals(stock.symbol);
      
      const currentPrice = stockData.currentPrice;
      const targetPrice = stock.target_price || currentPrice * 0.95;
      
      // Analyze each put option
      for (const put of optionsChain.puts || []) {
        // Skip if strike is too high (don't overpay)
        if (put.strike > currentPrice * 0.98) continue;
        
        // Skip if strike is too far from target
        if (Math.abs(put.strike - targetPrice) / targetPrice > 0.10) continue;
        
        // Skip if expiration is too far or too close
        if (put.daysToExpiration < 7 || put.daysToExpiration > 60) continue;
        
        // Skip illiquid options
        if (put.volume < 50 || put.openInterest < 100) continue;
        
        const opportunity = {
          symbol: stock.symbol,
          strategy: 'cash-secured-put',
          strike: put.strike,
          premium: put.premium,
          expiration: put.expiration,
          daysToExpiration: put.daysToExpiration,
          contracts: 1, // Can be adjusted based on available capital
          currentPrice: currentPrice,
          targetPrice: targetPrice,
          priority: stock.priority || 5
        };
        
        // Calculate returns and risks
        opportunity.analysis = this.calculateCashSecuredPutMetrics(opportunity, stockData, fundamentals);
        
        // Calculate confidence and risk scores
        opportunity.confidenceScore = this.calculateConfidenceScore(opportunity, historicalTrades);
        opportunity.riskScore = this.calculateRiskScore(opportunity, stockData);
        
        // Expected return
        opportunity.expectedReturn = opportunity.analysis.annualizedReturn;
        
        // Add recommendation
        opportunity.recommendation = this.getRecommendation(opportunity);
        
        opportunities.push(opportunity);
      }
    } catch (error) {
      logger.error(`Failed to analyze cash-secured puts for ${stock.symbol}:`, error);
    }
    
    return opportunities;
  }

  calculateCoveredCallMetrics(opportunity, stockData, fundamentals) {
    const { strike, premium, currentPrice, costBasis, contracts, daysToExpiration } = opportunity;
    
    const premiumIncome = premium * contracts * 100;
    const stockValue = currentPrice * contracts * 100;
    
    // Calculate various return scenarios
    const ifCalledAway = strike > currentPrice ? 
      ((strike - currentPrice) * contracts * 100) + premiumIncome : premiumIncome;
    
    const metrics = {
      premiumIncome: premiumIncome,
      percentPremium: (premium / currentPrice) * 100,
      annualizedReturn: ((premium / currentPrice) * 365 / daysToExpiration) * 100,
      maxProfit: ifCalledAway,
      maxProfitPercent: (ifCalledAway / stockValue) * 100,
      breakeven: currentPrice - premium,
      upside: ((strike - currentPrice) / currentPrice) * 100,
      downsideProtection: (premium / currentPrice) * 100,
      profitIfCalled: strike > costBasis ? ((strike - costBasis) * contracts * 100) + premiumIncome : premiumIncome,
      probabilityOfProfit: this.calculateProbabilityOfProfit('call', currentPrice, strike, daysToExpiration, fundamentals?.impliedVolatility || 30),
      moneyness: currentPrice / strike
    };
    
    return metrics;
  }

  calculateCashSecuredPutMetrics(opportunity, stockData, fundamentals) {
    const { strike, premium, currentPrice, daysToExpiration } = opportunity;
    
    const cashRequired = strike * 100; // Per contract
    const premiumIncome = premium * 100;
    
    const metrics = {
      premiumIncome: premiumIncome,
      cashRequired: cashRequired,
      percentPremium: (premium / strike) * 100,
      annualizedReturn: ((premium / strike) * 365 / daysToExpiration) * 100,
      effectivePurchasePrice: strike - premium,
      discountToCurrentPrice: ((currentPrice - strike) / currentPrice) * 100,
      breakeven: strike - premium,
      maxLoss: strike - premium,
      downsideProtection: (premium / strike) * 100,
      probabilityOfProfit: this.calculateProbabilityOfProfit('put', currentPrice, strike, daysToExpiration, fundamentals?.impliedVolatility || 30),
      moneyness: strike / currentPrice
    };
    
    return metrics;
  }

  calculateConfidenceScore(opportunity, historicalTrades) {
    let score = 50; // Base score
    
    const { analysis, strategy, symbol, daysToExpiration } = opportunity;
    
    // Premium return component (0-25 points)
    if (analysis.annualizedReturn >= 20) score += 25;
    else if (analysis.annualizedReturn >= 15) score += 20;
    else if (analysis.annualizedReturn >= 10) score += 15;
    else if (analysis.annualizedReturn >= 8) score += 10;
    else score += 5;
    
    // Probability of profit component (0-20 points)
    if (analysis.probabilityOfProfit >= 80) score += 20;
    else if (analysis.probabilityOfProfit >= 70) score += 15;
    else if (analysis.probabilityOfProfit >= 60) score += 10;
    else score += 5;
    
    // Liquidity component (0-15 points)
    if (opportunity.volume >= 500) score += 15;
    else if (opportunity.volume >= 200) score += 10;
    else if (opportunity.volume >= 100) score += 7;
    else score += 3;
    
    // Optimal expiration window (0-10 points)
    if (daysToExpiration >= 20 && daysToExpiration <= 45) score += 10;
    else if (daysToExpiration >= 15 && daysToExpiration <= 60) score += 7;
    else score += 3;
    
    // Historical success with this symbol (0-10 points)
    const symbolHistory = historicalTrades.filter(t => t.symbol === symbol && t.strategy === strategy);
    if (symbolHistory.length > 0) {
      const winRate = symbolHistory.filter(t => t.profit_loss > 0).length / symbolHistory.length;
      score += Math.round(winRate * 10);
    }
    
    // Strategy-specific adjustments
    if (strategy === 'covered-call') {
      // Bonus for calls above cost basis
      if (opportunity.strike > opportunity.costBasis * 1.05) score += 5;
      // Bonus for reasonable upside
      if (analysis.upside >= 3 && analysis.upside <= 10) score += 5;
    } else if (strategy === 'cash-secured-put') {
      // Bonus for good discount
      if (analysis.discountToCurrentPrice >= 5 && analysis.discountToCurrentPrice <= 15) score += 5;
      // Bonus for high priority watchlist items
      if (opportunity.priority >= 8) score += 5;
    }
    
    return Math.min(Math.round(score), 100);
  }

  calculateRiskScore(opportunity, stockData) {
    let riskScore = 0;
    
    const { analysis, daysToExpiration } = opportunity;
    
    // Volatility risk (0-30 points)
    const impliedVol = stockData.impliedVolatility || 30;
    if (impliedVol > 50) riskScore += 30;
    else if (impliedVol > 40) riskScore += 25;
    else if (impliedVol > 30) riskScore += 20;
    else if (impliedVol > 20) riskScore += 15;
    else riskScore += 10;
    
    // Time risk (0-20 points)
    if (daysToExpiration < 7) riskScore += 20;
    else if (daysToExpiration < 14) riskScore += 15;
    else if (daysToExpiration > 60) riskScore += 15;
    else riskScore += 5;
    
    // Moneyness risk (0-25 points)
    if (analysis.moneyness > 1.05) riskScore += 25; // Deep ITM
    else if (analysis.moneyness > 1.02) riskScore += 20;
    else if (analysis.moneyness > 0.98) riskScore += 15;
    else if (analysis.moneyness < 0.90) riskScore += 20; // Deep OTM
    else riskScore += 10;
    
    // Assignment risk (0-25 points)
    if (analysis.probabilityOfProfit < 50) riskScore += 25;
    else if (analysis.probabilityOfProfit < 60) riskScore += 20;
    else if (analysis.probabilityOfProfit < 70) riskScore += 15;
    else if (analysis.probabilityOfProfit < 80) riskScore += 10;
    else riskScore += 5;
    
    return Math.min(Math.round(riskScore), 100);
  }

  calculateProbabilityOfProfit(optionType, currentPrice, strike, daysToExpiration, impliedVolatility) {
    // Simplified probability calculation using normal distribution
    const timeToExpiration = daysToExpiration / 365;
    const volatility = impliedVolatility / 100;
    
    // Calculate expected move
    const expectedMove = currentPrice * volatility * Math.sqrt(timeToExpiration);
    
    // Calculate z-score
    const priceDistance = Math.abs(strike - currentPrice);
    const zScore = priceDistance / expectedMove;
    
    // Approximate probability using standard normal distribution
    // This is simplified - real calculation would use Black-Scholes
    let probability = 0.5 * (1 + this.erf(zScore / Math.sqrt(2)));
    
    if (optionType === 'put') {
      // For puts, we profit if price stays above strike
      probability = strike < currentPrice ? probability : 1 - probability;
    } else {
      // For calls, we profit if price stays below strike
      probability = strike > currentPrice ? probability : 1 - probability;
    }
    
    return Math.round(probability * 100);
  }

  // Error function for normal distribution calculation
  erf(x) {
    const a1 =  0.254829592;
    const a2 = -0.284496736;
    const a3 =  1.421413741;
    const a4 = -1.453152027;
    const a5 =  1.061405429;
    const p  =  0.3275911;

    const sign = x < 0 ? -1 : 1;
    x = Math.abs(x);

    const t = 1.0 / (1.0 + p * x);
    const y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * Math.exp(-x * x);

    return sign * y;
  }

  getRecommendation(opportunity) {
    const { confidenceScore, riskScore, analysis } = opportunity;
    
    // Calculate risk-adjusted score
    const riskAdjustedScore = confidenceScore - (riskScore * 0.3);
    
    let recommendation = {
      action: '',
      strength: '',
      reasoning: []
    };
    
    // Determine action
    if (riskAdjustedScore >= 75 && analysis.annualizedReturn >= 15) {
      recommendation.action = 'STRONG BUY';
      recommendation.strength = 'HIGH';
    } else if (riskAdjustedScore >= 60 && analysis.annualizedReturn >= 10) {
      recommendation.action = 'BUY';
      recommendation.strength = 'MEDIUM';
    } else if (riskAdjustedScore >= 45 && analysis.annualizedReturn >= 8) {
      recommendation.action = 'CONSIDER';
      recommendation.strength = 'LOW';
    } else {
      recommendation.action = 'AVOID';
      recommendation.strength = 'NONE';
    }
    
    // Add reasoning
    if (analysis.annualizedReturn >= 20) {
      recommendation.reasoning.push(`Excellent return of ${analysis.annualizedReturn.toFixed(1)}%`);
    }
    
    if (analysis.probabilityOfProfit >= 75) {
      recommendation.reasoning.push(`High probability of profit (${analysis.probabilityOfProfit}%)`);
    }
    
    if (riskScore <= 30) {
      recommendation.reasoning.push('Low risk profile');
    } else if (riskScore >= 70) {
      recommendation.reasoning.push('High risk - proceed with caution');
    }
    
    if (opportunity.strategy === 'covered-call' && analysis.upside >= 5) {
      recommendation.reasoning.push(`${analysis.upside.toFixed(1)}% upside potential`);
    }
    
    if (opportunity.strategy === 'cash-secured-put' && analysis.discountToCurrentPrice >= 5) {
      recommendation.reasoning.push(`${analysis.discountToCurrentPrice.toFixed(1)}% discount to current price`);
    }
    
    return recommendation;
  }

  async generateReport(opportunities) {
    const report = {
      timestamp: new Date(),
      summary: {
        totalOpportunities: opportunities.length,
        strongBuys: opportunities.filter(o => o.recommendation.action === 'STRONG BUY').length,
        buys: opportunities.filter(o => o.recommendation.action === 'BUY').length,
        avgConfidence: Math.round(opportunities.reduce((sum, o) => sum + o.confidenceScore, 0) / opportunities.length),
        avgRisk: Math.round(opportunities.reduce((sum, o) => sum + o.riskScore, 0) / opportunities.length),
        avgExpectedReturn: (opportunities.reduce((sum, o) => sum + o.expectedReturn, 0) / opportunities.length).toFixed(2)
      },
      topCoveredCalls: opportunities
        .filter(o => o.strategy === 'covered-call')
        .slice(0, 5)
        .map(o => this.formatOpportunity(o)),
      topCashSecuredPuts: opportunities
        .filter(o => o.strategy === 'cash-secured-put')
        .slice(0, 5)
        .map(o => this.formatOpportunity(o)),
      riskAnalysis: this.analyzePortfolioRisk(opportunities)
    };
    
    return report;
  }

  formatOpportunity(opp) {
    return {
      symbol: opp.symbol,
      strategy: opp.strategy,
      strike: opp.strike,
      premium: opp.premium,
      expiration: opp.expiration,
      confidence: `${opp.confidenceScore}%`,
      risk: `${opp.riskScore}%`,
      expectedReturn: `${opp.expectedReturn.toFixed(2)}%`,
      action: opp.recommendation.action,
      reasons: opp.recommendation.reasoning
    };
  }

  analyzePortfolioRisk(opportunities) {
    const bySymbol = {};
    
    opportunities.forEach(opp => {
      if (!bySymbol[opp.symbol]) {
        bySymbol[opp.symbol] = {
          count: 0,
          totalRisk: 0,
          strategies: new Set()
        };
      }
      bySymbol[opp.symbol].count++;
      bySymbol[opp.symbol].totalRisk += opp.riskScore;
      bySymbol[opp.symbol].strategies.add(opp.strategy);
    });
    
    const concentrationRisks = [];
    
    Object.entries(bySymbol).forEach(([symbol, data]) => {
      if (data.count > 3) {
        concentrationRisks.push(`High concentration in ${symbol} (${data.count} opportunities)`);
      }
      if (data.totalRisk / data.count > 70) {
        concentrationRisks.push(`High average risk for ${symbol} (${Math.round(data.totalRisk / data.count)}%)`);
      }
    });
    
    return {
      diversification: Object.keys(bySymbol).length,
      concentrationRisks: concentrationRisks,
      avgRiskPerSymbol: Object.values(bySymbol).reduce((acc, data) => {
        acc[data.symbol] = Math.round(data.totalRisk / data.count);
        return acc;
      }, {})
    };
  }
}

module.exports = PremiumOptimizer;