const Position = require('../models/Position');

class Portfolio {
  constructor(initialCash = 0, maxPositionSize = 0.05) {
    this.cash = initialCash;
    this.positions = new Map();
    this.stockHoldings = new Map();
    this.maxPositionSize = maxPositionSize; // 5% max per position
    this.totalValue = initialCash;
    this.createdAt = new Date();
    this.performance = {
      totalReturns: 0,
      realizedPnL: 0,
      unrealizedPnL: 0,
      totalPremiumCollected: 0,
      totalAssignments: 0,
      winRate: 0,
      avgDaysToClose: 0
    };
  }

  addPosition(position) {
    if (this.validatePosition(position)) {
      this.positions.set(position.id, position);
      this.cash -= position.cashRequired;
      this.updatePerformance();
      return true;
    }
    return false;
  }

  validatePosition(position) {
    const portfolioValue = this.getTotalValue();
    const positionValue = position.cashRequired;
    const positionPercent = positionValue / portfolioValue;
    
    if (positionPercent > this.maxPositionSize) {
      throw new Error(`Position size ${(positionPercent * 100).toFixed(1)}% exceeds maximum of ${(this.maxPositionSize * 100)}%`);
    }
    
    if (positionValue > this.cash) {
      throw new Error(`Insufficient cash. Required: $${positionValue}, Available: $${this.cash}`);
    }
    
    return true;
  }

  closePosition(positionId, closingPrice = 0, assignmentDetails = null) {
    const position = this.positions.get(positionId);
    if (!position) return false;
    
    if (assignmentDetails) {
      position.status = 'assigned';
      position.assignmentPrice = assignmentDetails.assignmentPrice;
      
      if (position.strategy === 'cash-secured-put') {
        // Add stock to holdings
        this.addStockHolding(position.symbol, 100 * position.quantity, assignmentDetails.assignmentPrice);
      } else if (position.strategy === 'covered-call') {
        // Remove stock from holdings
        this.removeStockHolding(position.symbol, 100 * position.quantity);
      }
    } else {
      position.status = closingPrice === 0 ? 'expired' : 'closed';
      position.closingPrice = closingPrice;
    }
    
    // Return cash for cash-secured puts
    if (position.strategy === 'cash-secured-put' && position.status !== 'assigned') {
      this.cash += position.cashRequired;
    }
    
    // Collect closing premium if bought back
    if (closingPrice > 0) {
      this.cash -= closingPrice * position.quantity * 100;
    }
    
    position.updatedAt = new Date();
    this.updatePerformance();
    return true;
  }

  addStockHolding(symbol, shares, costBasis) {
    if (this.stockHoldings.has(symbol)) {
      const existing = this.stockHoldings.get(symbol);
      const totalShares = existing.shares + shares;
      const avgCostBasis = ((existing.shares * existing.costBasis) + (shares * costBasis)) / totalShares;
      
      this.stockHoldings.set(symbol, {
        symbol,
        shares: totalShares,
        costBasis: avgCostBasis,
        addedAt: existing.addedAt,
        updatedAt: new Date()
      });
    } else {
      this.stockHoldings.set(symbol, {
        symbol,
        shares,
        costBasis,
        addedAt: new Date(),
        updatedAt: new Date()
      });
    }
  }

  removeStockHolding(symbol, shares) {
    if (this.stockHoldings.has(symbol)) {
      const holding = this.stockHoldings.get(symbol);
      if (holding.shares <= shares) {
        this.stockHoldings.delete(symbol);
      } else {
        holding.shares -= shares;
        holding.updatedAt = new Date();
      }
    }
  }

  getTotalValue(currentPrices = {}) {
    let totalValue = this.cash;
    
    // Add stock holdings value
    for (const [symbol, holding] of this.stockHoldings) {
      const currentPrice = currentPrices[symbol] || holding.costBasis;
      totalValue += holding.shares * currentPrice;
    }
    
    // Add option positions value (negative for sold options)
    for (const [id, position] of this.positions) {
      if (position.status === 'open') {
        const currentOptionPrice = currentPrices[`${position.symbol}_${position.strategy}`] || 0;
        totalValue -= currentOptionPrice * position.quantity * 100;
      }
    }
    
    this.totalValue = totalValue;
    return totalValue;
  }

  getPositionsByStatus(status) {
    return Array.from(this.positions.values()).filter(p => p.status === status);
  }

  getPositionsByStrategy(strategy) {
    return Array.from(this.positions.values()).filter(p => p.strategy === strategy);
  }

  getPositionsNearExpiration(daysThreshold = 7) {
    return Array.from(this.positions.values()).filter(p => 
      p.status === 'open' && p.getDaysToExpiration() <= daysThreshold
    );
  }

  updatePerformance() {
    const allPositions = Array.from(this.positions.values());
    const closedPositions = allPositions.filter(p => p.status !== 'open');
    
    this.performance.realizedPnL = closedPositions.reduce((sum, p) => sum + p.calculateRealizedPL(), 0);
    this.performance.totalPremiumCollected = allPositions.reduce((sum, p) => sum + (p.premium * p.quantity * 100), 0);
    this.performance.totalAssignments = closedPositions.filter(p => p.status === 'assigned').length;
    
    if (closedPositions.length > 0) {
      this.performance.winRate = (closedPositions.filter(p => p.calculateRealizedPL() > 0).length / closedPositions.length) * 100;
      
      const totalDays = closedPositions.reduce((sum, p) => {
        const days = Math.ceil((p.updatedAt - p.entryDate) / (1000 * 60 * 60 * 24));
        return sum + days;
      }, 0);
      this.performance.avgDaysToClose = totalDays / closedPositions.length;
    }
  }

  getSectorAllocation() {
    const sectors = {};
    const totalValue = this.getTotalValue();
    
    for (const [symbol, holding] of this.stockHoldings) {
      // This would normally come from stock data
      const sector = 'Unknown'; // Would need to be populated from stock data
      const value = holding.shares * holding.costBasis;
      
      if (!sectors[sector]) sectors[sector] = 0;
      sectors[sector] += value;
    }
    
    // Convert to percentages
    for (const sector in sectors) {
      sectors[sector] = (sectors[sector] / totalValue) * 100;
    }
    
    return sectors;
  }

  generateReport() {
    const totalValue = this.getTotalValue();
    const totalReturn = ((totalValue - this.cash) / this.cash) * 100;
    
    return {
      summary: {
        totalValue: totalValue,
        cash: this.cash,
        totalReturn: totalReturn,
        ...this.performance
      },
      positions: {
        open: this.getPositionsByStatus('open').length,
        closed: this.getPositionsByStatus('closed').length,
        assigned: this.getPositionsByStatus('assigned').length,
        expired: this.getPositionsByStatus('expired').length
      },
      holdings: Array.from(this.stockHoldings.values()),
      sectorAllocation: this.getSectorAllocation(),
      nearExpiration: this.getPositionsNearExpiration().map(p => ({
        id: p.id,
        symbol: p.symbol,
        strategy: p.strategy,
        daysToExpiration: p.getDaysToExpiration(),
        strike: p.strike
      }))
    };
  }
}

module.exports = Portfolio;