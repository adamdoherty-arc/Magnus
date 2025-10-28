class RiskManager {
  constructor(config = {}) {
    this.maxPositionSize = config.maxPositionSize || 0.05; // 5%
    this.maxSectorAllocation = config.maxSectorAllocation || 0.30; // 30%
    this.maxSingleStockAllocation = config.maxSingleStockAllocation || 0.10; // 10%
    this.maxOptionsAllocation = config.maxOptionsAllocation || 0.40; // 40% of portfolio in options
    this.maxDrawdown = config.maxDrawdown || 0.15; // 15%
    this.volatilityLimit = config.volatilityLimit || 40; // 40% max IV
    this.minLiquidity = config.minLiquidity || 1000; // Min daily volume
    this.maxDaysToExpiration = config.maxDaysToExpiration || 60;
    this.minDaysToExpiration = config.minDaysToExpiration || 7;
  }

  validateTrade(portfolio, position, stock) {
    const risks = [];
    const warnings = [];
    
    // Position size validation
    const portfolioValue = portfolio.getTotalValue();
    const positionValue = position.cashRequired;
    const positionPercent = positionValue / portfolioValue;
    
    if (positionPercent > this.maxPositionSize) {
      risks.push({
        type: 'POSITION_SIZE',
        severity: 'HIGH',
        message: `Position size ${(positionPercent * 100).toFixed(1)}% exceeds maximum of ${(this.maxPositionSize * 100)}%`,
        current: positionPercent,
        limit: this.maxPositionSize
      });
    }
    
    // Sector concentration
    const currentSectorAllocation = this.calculateSectorAllocation(portfolio, position, stock);
    if (currentSectorAllocation > this.maxSectorAllocation) {
      risks.push({
        type: 'SECTOR_CONCENTRATION',
        severity: 'MEDIUM',
        message: `Sector allocation ${(currentSectorAllocation * 100).toFixed(1)}% exceeds maximum of ${(this.maxSectorAllocation * 100)}%`,
        current: currentSectorAllocation,
        limit: this.maxSectorAllocation
      });
    }
    
    // Single stock concentration
    const stockAllocation = this.calculateStockAllocation(portfolio, position, stock);
    if (stockAllocation > this.maxSingleStockAllocation) {
      warnings.push({
        type: 'STOCK_CONCENTRATION',
        severity: 'MEDIUM',
        message: `Stock allocation ${(stockAllocation * 100).toFixed(1)}% exceeds recommended maximum of ${(this.maxSingleStockAllocation * 100)}%`,
        current: stockAllocation,
        limit: this.maxSingleStockAllocation
      });
    }
    
    // Volatility check
    if (stock.impliedVolatility > this.volatilityLimit) {
      warnings.push({
        type: 'HIGH_VOLATILITY',
        severity: 'MEDIUM',
        message: `Implied volatility ${stock.impliedVolatility}% exceeds recommended limit of ${this.volatilityLimit}%`,
        current: stock.impliedVolatility,
        limit: this.volatilityLimit
      });
    }
    
    // Liquidity check
    if (stock.optionsVolume < this.minLiquidity) {
      risks.push({
        type: 'LOW_LIQUIDITY',
        severity: 'HIGH',
        message: `Options volume ${stock.optionsVolume} below minimum of ${this.minLiquidity}`,
        current: stock.optionsVolume,
        limit: this.minLiquidity
      });
    }
    
    // Time to expiration
    const daysToExp = position.getDaysToExpiration();
    if (daysToExp > this.maxDaysToExpiration) {
      warnings.push({
        type: 'LONG_EXPIRATION',
        severity: 'LOW',
        message: `Days to expiration ${daysToExp} exceeds recommended maximum of ${this.maxDaysToExpiration}`,
        current: daysToExp,
        limit: this.maxDaysToExpiration
      });
    }
    
    if (daysToExp < this.minDaysToExpiration) {
      risks.push({
        type: 'SHORT_EXPIRATION',
        severity: 'HIGH',
        message: `Days to expiration ${daysToExp} below minimum of ${this.minDaysToExpiration}`,
        current: daysToExp,
        limit: this.minDaysToExpiration
      });
    }
    
    // Cash requirements
    if (positionValue > portfolio.cash) {
      risks.push({
        type: 'INSUFFICIENT_CASH',
        severity: 'HIGH',
        message: `Insufficient cash. Required: $${positionValue.toLocaleString()}, Available: $${portfolio.cash.toLocaleString()}`,
        required: positionValue,
        available: portfolio.cash
      });
    }
    
    return {
      approved: risks.length === 0,
      risks: risks,
      warnings: warnings,
      riskScore: this.calculateRiskScore(risks, warnings)
    };
  }

  calculateSectorAllocation(portfolio, newPosition, stock) {
    // This would normally integrate with stock sector data
    // For now, return a placeholder calculation
    const portfolioValue = portfolio.getTotalValue();
    const newPositionValue = newPosition.cashRequired;
    
    // Simulate getting sector allocation - would need real sector data
    const currentSectorValue = 0; // Would calculate from portfolio holdings
    const newSectorValue = currentSectorValue + newPositionValue;
    
    return newSectorValue / portfolioValue;
  }

  calculateStockAllocation(portfolio, newPosition, stock) {
    const portfolioValue = portfolio.getTotalValue();
    const newPositionValue = newPosition.cashRequired;
    
    // Check existing exposure to this stock
    let currentStockValue = 0;
    
    // Check stock holdings
    if (portfolio.stockHoldings.has(stock.symbol)) {
      const holding = portfolio.stockHoldings.get(stock.symbol);
      currentStockValue += holding.shares * stock.currentPrice;
    }
    
    // Check existing options positions
    const existingPositions = Array.from(portfolio.positions.values())
      .filter(p => p.symbol === stock.symbol && p.status === 'open');
    
    for (const pos of existingPositions) {
      currentStockValue += pos.cashRequired;
    }
    
    const totalStockValue = currentStockValue + newPositionValue;
    return totalStockValue / portfolioValue;
  }

  calculateRiskScore(risks, warnings) {
    let score = 0;
    
    risks.forEach(risk => {
      switch (risk.severity) {
        case 'HIGH': score += 30; break;
        case 'MEDIUM': score += 20; break;
        case 'LOW': score += 10; break;
      }
    });
    
    warnings.forEach(warning => {
      switch (warning.severity) {
        case 'HIGH': score += 15; break;
        case 'MEDIUM': score += 10; break;
        case 'LOW': score += 5; break;
      }
    });
    
    return Math.min(score, 100);
  }

  validatePortfolioRisk(portfolio, currentPrices = {}) {
    const issues = [];
    const portfolioValue = portfolio.getTotalValue(currentPrices);
    
    // Check overall options allocation
    let totalOptionsExposure = 0;
    for (const [id, position] of portfolio.positions) {
      if (position.status === 'open') {
        totalOptionsExposure += position.cashRequired;
      }
    }
    
    const optionsAllocation = totalOptionsExposure / portfolioValue;
    if (optionsAllocation > this.maxOptionsAllocation) {
      issues.push({
        type: 'EXCESSIVE_OPTIONS_EXPOSURE',
        severity: 'HIGH',
        message: `Options allocation ${(optionsAllocation * 100).toFixed(1)}% exceeds maximum of ${(this.maxOptionsAllocation * 100)}%`,
        current: optionsAllocation,
        limit: this.maxOptionsAllocation
      });
    }
    
    // Check positions near expiration
    const nearExpiration = portfolio.getPositionsNearExpiration(this.minDaysToExpiration);
    if (nearExpiration.length > 0) {
      issues.push({
        type: 'POSITIONS_NEAR_EXPIRATION',
        severity: 'MEDIUM',
        message: `${nearExpiration.length} positions expire within ${this.minDaysToExpiration} days`,
        positions: nearExpiration.map(p => ({
          id: p.id,
          symbol: p.symbol,
          daysToExpiration: p.getDaysToExpiration()
        }))
      });
    }
    
    // Check for over-concentration
    const sectorAllocations = portfolio.getSectorAllocation();
    for (const [sector, allocation] of Object.entries(sectorAllocations)) {
      if (allocation > this.maxSectorAllocation * 100) {
        issues.push({
          type: 'SECTOR_OVERWEIGHT',
          severity: 'MEDIUM',
          message: `${sector} sector allocation ${allocation.toFixed(1)}% exceeds maximum of ${(this.maxSectorAllocation * 100)}%`,
          sector: sector,
          current: allocation / 100,
          limit: this.maxSectorAllocation
        });
      }
    }
    
    return {
      healthy: issues.length === 0,
      issues: issues,
      overallRiskScore: this.calculateRiskScore(
        issues.filter(i => i.severity === 'HIGH'),
        issues.filter(i => i.severity === 'MEDIUM' || i.severity === 'LOW')
      )
    };
  }

  generateRecommendations(portfolio, riskAssessment) {
    const recommendations = [];
    
    riskAssessment.issues.forEach(issue => {
      switch (issue.type) {
        case 'POSITIONS_NEAR_EXPIRATION':
          recommendations.push({
            action: 'REVIEW_EXPIRING_POSITIONS',
            priority: 'HIGH',
            description: 'Review positions expiring soon for closing or rolling opportunities',
            positions: issue.positions
          });
          break;
          
        case 'SECTOR_OVERWEIGHT':
          recommendations.push({
            action: 'REDUCE_SECTOR_EXPOSURE',
            priority: 'MEDIUM',
            description: `Consider reducing exposure to ${issue.sector} sector`,
            sector: issue.sector
          });
          break;
          
        case 'EXCESSIVE_OPTIONS_EXPOSURE':
          recommendations.push({
            action: 'REDUCE_OPTIONS_ALLOCATION',
            priority: 'HIGH',
            description: 'Reduce overall options exposure to maintain risk limits'
          });
          break;
      }
    });
    
    return recommendations;
  }
}

module.exports = RiskManager;