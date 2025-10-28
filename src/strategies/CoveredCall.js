const Option = require('../models/Option');
const Position = require('../models/Position');

class CoveredCall {
  constructor(riskManager, taxCalculator) {
    this.riskManager = riskManager;
    this.taxCalculator = taxCalculator;
  }

  analyzeOpportunity(stock, shares, targetStrike, expiration, premium) {
    const contracts = Math.floor(shares / 100);
    const daysToExpiration = Math.ceil((new Date(expiration) - new Date()) / (1000 * 60 * 60 * 24));
    const stockValue = stock.currentPrice * shares;
    
    const analysis = {
      symbol: stock.symbol,
      strategy: 'covered-call',
      currentPrice: stock.currentPrice,
      shares: shares,
      contracts: contracts,
      strike: targetStrike,
      premium: premium,
      totalPremium: premium * contracts * 100,
      periodReturn: (premium * contracts * 100) / stockValue * 100,
      annualizedReturn: ((premium * contracts * 100) / stockValue * 365 / daysToExpiration) * 100,
      maxProfit: (targetStrike - stock.currentPrice + premium) * contracts * 100,
      maxLoss: (stock.currentPrice - premium) * shares,
      breakeven: stock.currentPrice - premium,
      daysToExpiration: daysToExpiration,
      upSideCap: ((targetStrike - stock.currentPrice) / stock.currentPrice) * 100,
      downsideProtection: (premium / stock.currentPrice) * 100
    };

    // Calculate if-called return
    if (targetStrike > stock.currentPrice) {
      const stockAppreciation = (targetStrike - stock.currentPrice) * contracts * 100;
      const dividendIncome = this.estimateDividendIncome(stock, daysToExpiration, shares);
      analysis.ifCalledReturn = ((analysis.totalPremium + stockAppreciation + dividendIncome) / stockValue) * 100;
      analysis.ifCalledAnnualized = (analysis.ifCalledReturn * 365) / daysToExpiration;
    }

    analysis.qualityScore = this.calculateQualityScore(stock, analysis);
    analysis.recommendation = this.getRecommendation(analysis);
    
    return analysis;
  }

  calculateQualityScore(stock, analysis) {
    let score = 0;
    
    // Premium yield (0-25 points)
    if (analysis.annualizedReturn >= 15) score += 25;
    else if (analysis.annualizedReturn >= 12) score += 20;
    else if (analysis.annualizedReturn >= 8) score += 15;
    else if (analysis.annualizedReturn >= 6) score += 10;
    else score += 5;
    
    // Stock quality (0-25 points)
    if (stock.meetsScreeningCriteria()) score += 25;
    else score += 15;
    
    // Upside capture (0-20 points)
    if (analysis.upSideCap >= 8 && analysis.upSideCap <= 15) score += 20;
    else if (analysis.upSideCap >= 5 && analysis.upSideCap <= 20) score += 15;
    else if (analysis.upSideCap >= 3) score += 10;
    else score += 5;
    
    // Days to expiration (0-15 points)
    if (analysis.daysToExpiration >= 30 && analysis.daysToExpiration <= 45) score += 15;
    else if (analysis.daysToExpiration >= 20 && analysis.daysToExpiration <= 60) score += 12;
    else score += 8;
    
    // Downside protection (0-10 points)
    if (analysis.downsideProtection >= 3) score += 10;
    else if (analysis.downsideProtection >= 2) score += 8;
    else if (analysis.downsideProtection >= 1) score += 6;
    else score += 3;
    
    // If-called return bonus (0-5 points)
    if (analysis.ifCalledAnnualized && analysis.ifCalledAnnualized >= 20) score += 5;
    else if (analysis.ifCalledAnnualized && analysis.ifCalledAnnualized >= 15) score += 3;
    
    return Math.min(score, 100);
  }

  getRecommendation(analysis) {
    if (analysis.qualityScore >= 80) return 'BUY';
    if (analysis.qualityScore >= 60) return 'CONSIDER';
    if (analysis.qualityScore >= 40) return 'WEAK';
    return 'AVOID';
  }

  createPosition(analysis) {
    const positionId = `CC_${analysis.symbol}_${Date.now()}`;
    
    return new Position({
      id: positionId,
      symbol: analysis.symbol,
      strategy: 'covered-call',
      entryDate: new Date(),
      expirationDate: new Date(Date.now() + (analysis.daysToExpiration * 24 * 60 * 60 * 1000)),
      strike: analysis.strike,
      premium: analysis.premium,
      quantity: analysis.contracts,
      status: 'open',
      stockPrice: analysis.currentPrice,
      cashRequired: 0 // No additional cash required for covered calls
    });
  }

  scanExistingHoldings(holdings, maxPositions = 10) {
    const opportunities = [];
    
    for (const holding of holdings) {
      if (holding.shares < 100) continue; // Need at least 100 shares
      
      const availableContracts = Math.floor(holding.shares / 100);
      
      // Generate strike prices 5-15% above current price
      const strikes = this.generateStrikes(holding.stock.currentPrice, 0.05, 0.15, 5);
      
      for (const strike of strikes) {
        // Simulate premium calculation
        const estimatedPremium = this.estimatePremium(holding.stock, strike, 30);
        
        const analysis = this.analyzeOpportunity(
          holding.stock, 
          holding.shares, 
          strike,
          new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), 
          estimatedPremium
        );
        
        if (analysis.recommendation === 'BUY' || analysis.recommendation === 'CONSIDER') {
          opportunities.push({
            ...analysis,
            holdingId: holding.id,
            currentCostBasis: holding.costBasis
          });
        }
      }
    }
    
    return opportunities
      .sort((a, b) => b.qualityScore - a.qualityScore)
      .slice(0, maxPositions);
  }

  generateStrikes(currentPrice, minPremium, maxPremium, count) {
    const strikes = [];
    const step = (maxPremium - minPremium) / (count - 1);
    
    for (let i = 0; i < count; i++) {
      const premium = minPremium + (step * i);
      const strike = Math.round((currentPrice * (1 + premium)) * 2) / 2; // Round to nearest 0.50
      strikes.push(strike);
    }
    
    return strikes;
  }

  estimatePremium(stock, strike, daysToExpiration) {
    // Simplified premium estimation
    const timeValue = Math.sqrt(daysToExpiration / 365);
    const moneyness = stock.currentPrice / strike;
    const ivDecimal = stock.impliedVolatility / 100;
    
    // Basic approximation for out-of-the-money call
    return Math.max(0.05, stock.currentPrice * ivDecimal * timeValue * Math.sqrt(moneyness) * 0.3);
  }

  estimateDividendIncome(stock, daysToExpiration, shares) {
    if (!stock.dividendYield) return 0;
    
    // Estimate quarterly dividend
    const quarterlyDividend = (stock.currentPrice * stock.dividendYield / 100) / 4;
    const dividendsInPeriod = Math.floor(daysToExpiration / 90);
    
    return quarterlyDividend * dividendsInPeriod * shares;
  }

  shouldRoll(position, currentOptionPrice, newStrike, newPremium, newExpiration) {
    const currentValue = currentOptionPrice * position.quantity * 100;
    const costToBuyBack = currentValue;
    const newPremiumIncome = newPremium * position.quantity * 100;
    const netCredit = newPremiumIncome - costToBuyBack;
    
    return {
      shouldRoll: netCredit > 0,
      netCredit: netCredit,
      newStrike: newStrike,
      newExpiration: newExpiration,
      additionalDays: Math.ceil((new Date(newExpiration) - position.expirationDate) / (1000 * 60 * 60 * 24))
    };
  }
}

module.exports = CoveredCall;