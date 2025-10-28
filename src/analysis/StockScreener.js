class StockScreener {
  constructor(dataProvider) {
    this.dataProvider = dataProvider;
    this.criteria = {
      minMarketCap: 10e9, // $10B
      maxMarketCap: Infinity,
      minOptionsVolume: 1000,
      maxBidAskSpread: 0.10,
      minImpliedVolatility: 20,
      maxImpliedVolatility: 40,
      minBeta: 0.5,
      maxBeta: 1.5,
      minDividendYield: 2,
      maxDividendYield: 6,
      maxDebtToEquity: 2.0,
      sectors: [], // Empty means all sectors
      excludedSectors: ['REIT'], // High-risk sectors to avoid
      minPrice: 20, // Avoid penny stocks
      maxPrice: 1000
    };
  }

  async screenForCashSecuredPuts(customCriteria = {}) {
    const criteria = { ...this.criteria, ...customCriteria };
    const candidates = [];

    try {
      // Get universe of stocks
      const stocks = await this.dataProvider.getStockUniverse();
      
      for (const stock of stocks) {
        if (this.passesBasicScreening(stock, criteria)) {
          // Get options data for strike analysis
          const optionsData = await this.dataProvider.getOptionsChain(stock.symbol);
          const putOpportunities = this.analyzePutOpportunities(stock, optionsData);
          
          if (putOpportunities.length > 0) {
            candidates.push({
              stock: stock,
              opportunities: putOpportunities,
              score: this.scoreStock(stock, 'put'),
              fundamentals: await this.getFundamentals(stock.symbol)
            });
          }
        }
      }

      return candidates
        .sort((a, b) => b.score - a.score)
        .slice(0, 50); // Top 50 candidates
        
    } catch (error) {
      console.error('Error screening for cash-secured puts:', error);
      return [];
    }
  }

  async screenForCoveredCalls(portfolio) {
    const opportunities = [];
    
    try {
      for (const [symbol, holding] of portfolio.stockHoldings) {
        if (holding.shares < 100) continue; // Need at least 100 shares
        
        const stock = await this.dataProvider.getStockData(symbol);
        const optionsData = await this.dataProvider.getOptionsChain(symbol);
        const callOpportunities = this.analyzeCallOpportunities(stock, optionsData, holding);
        
        if (callOpportunities.length > 0) {
          opportunities.push({
            stock: stock,
            holding: holding,
            opportunities: callOpportunities,
            score: this.scoreStock(stock, 'call')
          });
        }
      }

      return opportunities.sort((a, b) => b.score - a.score);
      
    } catch (error) {
      console.error('Error screening for covered calls:', error);
      return [];
    }
  }

  passesBasicScreening(stock, criteria) {
    return (
      stock.marketCap >= criteria.minMarketCap &&
      stock.marketCap <= criteria.maxMarketCap &&
      stock.optionsVolume >= criteria.minOptionsVolume &&
      stock.impliedVolatility >= criteria.minImpliedVolatility &&
      stock.impliedVolatility <= criteria.maxImpliedVolatility &&
      stock.beta >= criteria.minBeta &&
      stock.beta <= criteria.maxBeta &&
      stock.dividendYield >= criteria.minDividendYield &&
      stock.dividendYield <= criteria.maxDividendYield &&
      stock.currentPrice >= criteria.minPrice &&
      stock.currentPrice <= criteria.maxPrice &&
      !criteria.excludedSectors.includes(stock.sector) &&
      (criteria.sectors.length === 0 || criteria.sectors.includes(stock.sector))
    );
  }

  analyzePutOpportunities(stock, optionsData) {
    const opportunities = [];
    const targetStrikes = this.generatePutStrikes(stock.currentPrice);
    
    targetStrikes.forEach(strike => {
      const putOption = this.findBestPutOption(optionsData.puts, strike);
      if (putOption && this.isGoodPutOpportunity(stock, putOption)) {
        opportunities.push({
          strike: strike,
          premium: putOption.premium,
          expiration: putOption.expiration,
          annualizedReturn: this.calculateAnnualizedReturn(putOption.premium, strike, putOption.daysToExpiration),
          qualityScore: this.scorePutOpportunity(stock, putOption)
        });
      }
    });

    return opportunities.sort((a, b) => b.qualityScore - a.qualityScore).slice(0, 3);
  }

  analyzeCallOpportunities(stock, optionsData, holding) {
    const opportunities = [];
    const targetStrikes = this.generateCallStrikes(stock.currentPrice, holding.costBasis);
    
    targetStrikes.forEach(strike => {
      const callOption = this.findBestCallOption(optionsData.calls, strike);
      if (callOption && this.isGoodCallOpportunity(stock, callOption, holding)) {
        opportunities.push({
          strike: strike,
          premium: callOption.premium,
          expiration: callOption.expiration,
          annualizedReturn: this.calculateAnnualizedReturn(callOption.premium, stock.currentPrice, callOption.daysToExpiration),
          maxProfit: this.calculateMaxCallProfit(stock.currentPrice, strike, callOption.premium),
          qualityScore: this.scoreCallOpportunity(stock, callOption, holding)
        });
      }
    });

    return opportunities.sort((a, b) => b.qualityScore - a.qualityScore).slice(0, 3);
  }

  generatePutStrikes(currentPrice) {
    const strikes = [];
    // Generate strikes 5-15% below current price
    for (let discount = 0.05; discount <= 0.15; discount += 0.025) {
      const strike = Math.round((currentPrice * (1 - discount)) * 2) / 2; // Round to nearest 0.50
      strikes.push(strike);
    }
    return strikes;
  }

  generateCallStrikes(currentPrice, costBasis) {
    const strikes = [];
    const minStrike = Math.max(currentPrice * 1.02, costBasis * 1.01); // At least 2% above current or 1% above cost basis
    
    // Generate strikes 2-15% above current price, but above cost basis
    for (let premium = 0.02; premium <= 0.15; premium += 0.025) {
      const strike = Math.max(minStrike, currentPrice * (1 + premium));
      const roundedStrike = Math.round(strike * 2) / 2; // Round to nearest 0.50
      strikes.push(roundedStrike);
    }
    return strikes;
  }

  findBestPutOption(puts, targetStrike) {
    // Find put options near target strike with 20-45 days to expiration
    return puts
      .filter(put => 
        Math.abs(put.strike - targetStrike) <= 2.5 && // Within $2.50 of target
        put.daysToExpiration >= 20 && 
        put.daysToExpiration <= 45 &&
        put.bidAskSpread <= this.criteria.maxBidAskSpread
      )
      .sort((a, b) => this.calculateAnnualizedReturn(b.premium, b.strike, b.daysToExpiration) - 
                     this.calculateAnnualizedReturn(a.premium, a.strike, a.daysToExpiration))[0];
  }

  findBestCallOption(calls, targetStrike) {
    // Find call options near target strike with 20-45 days to expiration
    return calls
      .filter(call => 
        Math.abs(call.strike - targetStrike) <= 2.5 && // Within $2.50 of target
        call.daysToExpiration >= 20 && 
        call.daysToExpiration <= 45 &&
        call.bidAskSpread <= this.criteria.maxBidAskSpread
      )
      .sort((a, b) => this.calculateAnnualizedReturn(b.premium, targetStrike, b.daysToExpiration) - 
                     this.calculateAnnualizedReturn(a.premium, targetStrike, a.daysToExpiration))[0];
  }

  isGoodPutOpportunity(stock, putOption) {
    const annualizedReturn = this.calculateAnnualizedReturn(putOption.premium, putOption.strike, putOption.daysToExpiration);
    return (
      annualizedReturn >= 12 && // Minimum 12% annualized return
      putOption.premium / putOption.strike >= 0.008 && // At least 0.8% premium
      putOption.volume >= 50 // Minimum liquidity
    );
  }

  isGoodCallOpportunity(stock, callOption, holding) {
    const annualizedReturn = this.calculateAnnualizedReturn(callOption.premium, stock.currentPrice, callOption.daysToExpiration);
    const wouldLockInGain = callOption.strike > holding.costBasis;
    
    return (
      annualizedReturn >= 8 && // Minimum 8% annualized return
      callOption.premium / stock.currentPrice >= 0.01 && // At least 1% premium
      callOption.volume >= 50 && // Minimum liquidity
      wouldLockInGain // Don't sell calls below cost basis
    );
  }

  calculateAnnualizedReturn(premium, cashAtRisk, daysToExpiration) {
    const periodReturn = premium / cashAtRisk;
    return (periodReturn * 365 / daysToExpiration) * 100;
  }

  calculateMaxCallProfit(currentPrice, strike, premium) {
    return (strike - currentPrice + premium) * 100; // Per contract
  }

  scoreStock(stock, strategy) {
    let score = 0;
    
    // Market cap score (0-20)
    if (stock.marketCap > 100e9) score += 20; // Large cap
    else if (stock.marketCap > 50e9) score += 15; // Mid-large cap
    else if (stock.marketCap > 10e9) score += 10; // Mid cap
    
    // Liquidity score (0-20)
    if (stock.optionsVolume > 5000) score += 20;
    else if (stock.optionsVolume > 2000) score += 15;
    else if (stock.optionsVolume > 1000) score += 10;
    
    // Volatility score (0-20)
    if (stock.impliedVolatility >= 25 && stock.impliedVolatility <= 35) score += 20;
    else if (stock.impliedVolatility >= 20 && stock.impliedVolatility <= 40) score += 15;
    else score += 10;
    
    // Beta score (0-15)
    if (stock.beta >= 0.8 && stock.beta <= 1.2) score += 15;
    else if (stock.beta >= 0.5 && stock.beta <= 1.5) score += 10;
    else score += 5;
    
    // Dividend score (0-15)
    if (strategy === 'call' && stock.dividendYield >= 3) score += 15;
    else if (stock.dividendYield >= 2) score += 10;
    else score += 5;
    
    // Sector diversification bonus (0-10)
    const preferredSectors = ['Technology', 'Healthcare', 'Consumer Staples', 'Financials'];
    if (preferredSectors.includes(stock.sector)) score += 10;
    else score += 5;
    
    return Math.min(score, 100);
  }

  scorePutOpportunity(stock, putOption) {
    let score = 0;
    
    const annualizedReturn = this.calculateAnnualizedReturn(putOption.premium, putOption.strike, putOption.daysToExpiration);
    
    // Return score (0-40)
    if (annualizedReturn >= 20) score += 40;
    else if (annualizedReturn >= 15) score += 30;
    else if (annualizedReturn >= 12) score += 20;
    else score += 10;
    
    // Discount score (0-25)
    const discount = (stock.currentPrice - putOption.strike) / stock.currentPrice;
    if (discount >= 0.10) score += 25;
    else if (discount >= 0.05) score += 20;
    else score += 10;
    
    // Time score (0-20)
    if (putOption.daysToExpiration >= 30 && putOption.daysToExpiration <= 40) score += 20;
    else if (putOption.daysToExpiration >= 20 && putOption.daysToExpiration <= 50) score += 15;
    else score += 10;
    
    // Liquidity score (0-15)
    if (putOption.volume >= 500) score += 15;
    else if (putOption.volume >= 100) score += 10;
    else score += 5;
    
    return Math.min(score, 100);
  }

  scoreCallOpportunity(stock, callOption, holding) {
    let score = 0;
    
    const annualizedReturn = this.calculateAnnualizedReturn(callOption.premium, stock.currentPrice, callOption.daysToExpiration);
    
    // Return score (0-40)
    if (annualizedReturn >= 15) score += 40;
    else if (annualizedReturn >= 12) score += 30;
    else if (annualizedReturn >= 8) score += 20;
    else score += 10;
    
    // Upside capture score (0-25)
    const upside = (callOption.strike - stock.currentPrice) / stock.currentPrice;
    if (upside >= 0.08 && upside <= 0.15) score += 25;
    else if (upside >= 0.05) score += 20;
    else score += 10;
    
    // Gain lock-in score (0-20)
    const gainVsCostBasis = (callOption.strike - holding.costBasis) / holding.costBasis;
    if (gainVsCostBasis >= 0.20) score += 20;
    else if (gainVsCostBasis >= 0.10) score += 15;
    else if (gainVsCostBasis >= 0.05) score += 10;
    else score += 5;
    
    // Time score (0-15)
    if (callOption.daysToExpiration >= 30 && callOption.daysToExpiration <= 40) score += 15;
    else if (callOption.daysToExpiration >= 20 && callOption.daysToExpiration <= 50) score += 12;
    else score += 8;
    
    return Math.min(score, 100);
  }

  async getFundamentals(symbol) {
    try {
      return await this.dataProvider.getFundamentals(symbol);
    } catch (error) {
      return { pe: null, debt_to_equity: null, roe: null };
    }
  }

  generateWatchList(screenResults, maxItems = 20) {
    return screenResults
      .slice(0, maxItems)
      .map(result => ({
        symbol: result.stock.symbol,
        currentPrice: result.stock.currentPrice,
        impliedVolatility: result.stock.impliedVolatility,
        score: result.score,
        topOpportunity: result.opportunities[0],
        alerts: this.generateAlerts(result.stock, result.opportunities[0])
      }));
  }

  generateAlerts(stock, opportunity) {
    const alerts = [];
    
    if (opportunity.annualizedReturn >= 20) {
      alerts.push('HIGH_RETURN');
    }
    
    if (stock.impliedVolatility > 35) {
      alerts.push('HIGH_VOLATILITY');
    }
    
    if (opportunity.daysToExpiration <= 14) {
      alerts.push('SHORT_EXPIRATION');
    }
    
    return alerts;
  }
}

module.exports = StockScreener;