const Option = require('../models/Option');
const Position = require('../models/Position');

class CashSecuredPut {
  constructor(riskManager, taxCalculator) {
    this.riskManager = riskManager;
    this.taxCalculator = taxCalculator;
  }

  analyzeOpportunity(stock, targetStrike, expiration, premium) {
    const cashRequired = targetStrike * 100;
    const daysToExpiration = Math.ceil((new Date(expiration) - new Date()) / (1000 * 60 * 60 * 24));
    
    const analysis = {
      symbol: stock.symbol,
      strategy: 'cash-secured-put',
      strike: targetStrike,
      premium: premium,
      cashRequired: cashRequired,
      immediateIncome: premium * 100,
      periodReturn: (premium / targetStrike) * 100,
      annualizedReturn: ((premium / targetStrike) * 365 / daysToExpiration) * 100,
      effectivePurchasePrice: targetStrike - premium,
      maxLoss: targetStrike - premium,
      breakeven: targetStrike - premium,
      daysToExpiration: daysToExpiration,
      discountToCurrentPrice: ((stock.currentPrice - targetStrike) / stock.currentPrice) * 100
    };

    analysis.qualityScore = this.calculateQualityScore(stock, analysis);
    analysis.recommendation = this.getRecommendation(analysis);
    
    return analysis;
  }

  calculateQualityScore(stock, analysis) {
    let score = 0;
    
    // Premium yield (0-30 points)
    if (analysis.annualizedReturn >= 20) score += 30;
    else if (analysis.annualizedReturn >= 15) score += 25;
    else if (analysis.annualizedReturn >= 12) score += 20;
    else if (analysis.annualizedReturn >= 8) score += 15;
    else score += 10;
    
    // Stock quality (0-25 points)
    if (stock.meetsScreeningCriteria()) score += 25;
    else score += 10;
    
    // Discount to current price (0-20 points)
    if (analysis.discountToCurrentPrice >= 10) score += 20;
    else if (analysis.discountToCurrentPrice >= 5) score += 15;
    else if (analysis.discountToCurrentPrice >= 0) score += 10;
    else score += 5;
    
    // Days to expiration (0-15 points)
    if (analysis.daysToExpiration >= 30 && analysis.daysToExpiration <= 45) score += 15;
    else if (analysis.daysToExpiration >= 20 && analysis.daysToExpiration <= 60) score += 12;
    else score += 8;
    
    // Implied volatility (0-10 points)
    if (stock.impliedVolatility >= 25 && stock.impliedVolatility <= 35) score += 10;
    else if (stock.impliedVolatility >= 20 && stock.impliedVolatility <= 40) score += 8;
    else score += 5;
    
    return Math.min(score, 100);
  }

  getRecommendation(analysis) {
    if (analysis.qualityScore >= 80) return 'BUY';
    if (analysis.qualityScore >= 60) return 'CONSIDER';
    if (analysis.qualityScore >= 40) return 'WEAK';
    return 'AVOID';
  }

  createPosition(analysis, quantity = 1) {
    const positionId = `CSP_${analysis.symbol}_${Date.now()}`;
    
    return new Position({
      id: positionId,
      symbol: analysis.symbol,
      strategy: 'cash-secured-put',
      entryDate: new Date(),
      expirationDate: new Date(Date.now() + (analysis.daysToExpiration * 24 * 60 * 60 * 1000)),
      strike: analysis.strike,
      premium: analysis.premium,
      quantity: quantity,
      status: 'open',
      stockPrice: null,
      cashRequired: analysis.cashRequired * quantity
    });
  }

  scanForOpportunities(stocks, maxPositions = 10) {
    const opportunities = [];
    
    for (const stock of stocks) {
      if (!stock.meetsScreeningCriteria()) continue;
      
      // Generate strike prices 5-15% below current price
      const strikes = this.generateStrikes(stock.currentPrice, 0.05, 0.15, 5);
      
      for (const strike of strikes) {
        // Simulate premium calculation (would normally come from options data API)
        const estimatedPremium = this.estimatePremium(stock, strike, 30);
        
        const analysis = this.analyzeOpportunity(stock, strike, 
          new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), estimatedPremium);
        
        if (analysis.recommendation === 'BUY' || analysis.recommendation === 'CONSIDER') {
          opportunities.push(analysis);
        }
      }
    }
    
    return opportunities
      .sort((a, b) => b.qualityScore - a.qualityScore)
      .slice(0, maxPositions);
  }

  generateStrikes(currentPrice, minDiscount, maxDiscount, count) {
    const strikes = [];
    const step = (maxDiscount - minDiscount) / (count - 1);
    
    for (let i = 0; i < count; i++) {
      const discount = minDiscount + (step * i);
      const strike = Math.round((currentPrice * (1 - discount)) * 2) / 2; // Round to nearest 0.50
      strikes.push(strike);
    }
    
    return strikes;
  }

  estimatePremium(stock, strike, daysToExpiration) {
    // Simplified premium estimation using Black-Scholes approximation
    const timeValue = Math.sqrt(daysToExpiration / 365);
    const moneyness = strike / stock.currentPrice;
    const ivDecimal = stock.impliedVolatility / 100;
    
    // Basic approximation for out-of-the-money put
    return Math.max(0.05, strike * ivDecimal * timeValue * Math.sqrt(moneyness) * 0.4);
  }
}

module.exports = CashSecuredPut;