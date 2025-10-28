class PerformanceAnalyzer {
  constructor() {
    this.benchmarks = {
      SPY: 'S&P 500',
      QQQ: 'NASDAQ 100',
      IWM: 'Russell 2000',
      VTI: 'Total Stock Market'
    };
  }

  calculatePortfolioMetrics(portfolio, benchmarkReturns = {}) {
    const positions = Array.from(portfolio.positions.values());
    const closedPositions = positions.filter(p => p.status !== 'open');
    
    const metrics = {
      overview: this.calculateOverviewMetrics(portfolio, closedPositions),
      returns: this.calculateReturnMetrics(portfolio, closedPositions),
      risk: this.calculateRiskMetrics(portfolio, closedPositions),
      trading: this.calculateTradingMetrics(closedPositions),
      strategy: this.calculateStrategyMetrics(closedPositions),
      benchmark: this.calculateBenchmarkComparison(portfolio, benchmarkReturns)
    };

    return metrics;
  }

  calculateOverviewMetrics(portfolio, closedPositions) {
    const totalValue = portfolio.getTotalValue();
    const initialValue = portfolio.cash + portfolio.performance.realizedPnL;
    const totalReturn = ((totalValue - initialValue) / initialValue) * 100;
    
    return {
      totalValue: totalValue,
      totalReturn: totalReturn,
      realizedPnL: portfolio.performance.realizedPnL,
      unrealizedPnL: portfolio.performance.unrealizedPnL,
      totalPremiumCollected: portfolio.performance.totalPremiumCollected,
      cashUtilization: ((totalValue - portfolio.cash) / totalValue) * 100,
      numberOfPositions: portfolio.positions.size,
      activePositions: portfolio.getPositionsByStatus('open').length
    };
  }

  calculateReturnMetrics(portfolio, closedPositions) {
    if (closedPositions.length === 0) {
      return {
        avgReturnPerTrade: 0,
        annualizedReturn: 0,
        bestTrade: 0,
        worstTrade: 0,
        profitFactor: 0
      };
    }

    const returns = closedPositions.map(p => p.calculateReturnOnCapital());
    const profits = closedPositions.filter(p => p.calculateRealizedPL() > 0);
    const losses = closedPositions.filter(p => p.calculateRealizedPL() < 0);
    
    const totalProfit = profits.reduce((sum, p) => sum + p.calculateRealizedPL(), 0);
    const totalLoss = Math.abs(losses.reduce((sum, p) => sum + p.calculateRealizedPL(), 0));
    
    // Calculate time-weighted return
    const daysActive = Math.ceil((new Date() - portfolio.createdAt) / (1000 * 60 * 60 * 24));
    const totalReturn = portfolio.performance.realizedPnL / portfolio.cash;
    const annualizedReturn = daysActive > 0 ? (totalReturn * 365 / daysActive) * 100 : 0;

    return {
      avgReturnPerTrade: returns.reduce((sum, r) => sum + r, 0) / returns.length,
      annualizedReturn: annualizedReturn,
      bestTrade: Math.max(...returns),
      worstTrade: Math.min(...returns),
      profitFactor: totalLoss > 0 ? totalProfit / totalLoss : totalProfit > 0 ? Infinity : 0,
      sharpeRatio: this.calculateSharpeRatio(returns),
      calmarRatio: this.calculateCalmarRatio(annualizedReturn, this.calculateMaxDrawdown(closedPositions))
    };
  }

  calculateRiskMetrics(portfolio, closedPositions) {
    const returns = closedPositions.map(p => p.calculateReturnOnCapital());
    
    return {
      volatility: this.calculateVolatility(returns),
      maxDrawdown: this.calculateMaxDrawdown(closedPositions),
      sortinoRatio: this.calculateSortinoRatio(returns),
      valueAtRisk: this.calculateVaR(returns, 0.05), // 5% VaR
      expectedShortfall: this.calculateExpectedShortfall(returns, 0.05),
      betaToMarket: this.calculateBeta(portfolio, 'SPY') // Would need market data
    };
  }

  calculateTradingMetrics(closedPositions) {
    if (closedPositions.length === 0) {
      return {
        winRate: 0,
        avgWinSize: 0,
        avgLossSize: 0,
        avgDaysToClose: 0,
        assignmentRate: 0,
        expirationRate: 0
      };
    }

    const winners = closedPositions.filter(p => p.calculateRealizedPL() > 0);
    const losers = closedPositions.filter(p => p.calculateRealizedPL() < 0);
    const assigned = closedPositions.filter(p => p.status === 'assigned');
    const expired = closedPositions.filter(p => p.status === 'expired');
    
    const totalDays = closedPositions.reduce((sum, p) => {
      const days = Math.ceil((p.updatedAt - p.entryDate) / (1000 * 60 * 60 * 24));
      return sum + days;
    }, 0);

    return {
      winRate: (winners.length / closedPositions.length) * 100,
      avgWinSize: winners.length > 0 ? winners.reduce((sum, p) => sum + p.calculateReturnOnCapital(), 0) / winners.length : 0,
      avgLossSize: losers.length > 0 ? losers.reduce((sum, p) => sum + p.calculateReturnOnCapital(), 0) / losers.length : 0,
      avgDaysToClose: totalDays / closedPositions.length,
      assignmentRate: (assigned.length / closedPositions.length) * 100,
      expirationRate: (expired.length / closedPositions.length) * 100,
      avgDaysToAssignment: assigned.length > 0 ? assigned.reduce((sum, p) => {
        const days = Math.ceil((p.updatedAt - p.entryDate) / (1000 * 60 * 60 * 24));
        return sum + days;
      }, 0) / assigned.length : 0
    };
  }

  calculateStrategyMetrics(closedPositions) {
    const strategies = ['cash-secured-put', 'covered-call'];
    const metrics = {};

    strategies.forEach(strategy => {
      const strategyPositions = closedPositions.filter(p => p.strategy === strategy);
      
      if (strategyPositions.length > 0) {
        const returns = strategyPositions.map(p => p.calculateReturnOnCapital());
        const totalPnL = strategyPositions.reduce((sum, p) => sum + p.calculateRealizedPL(), 0);
        const totalPremium = strategyPositions.reduce((sum, p) => sum + (p.premium * p.quantity * 100), 0);
        
        metrics[strategy] = {
          positions: strategyPositions.length,
          totalPnL: totalPnL,
          totalPremium: totalPremium,
          avgReturn: returns.reduce((sum, r) => sum + r, 0) / returns.length,
          winRate: (strategyPositions.filter(p => p.calculateRealizedPL() > 0).length / strategyPositions.length) * 100,
          assignmentRate: (strategyPositions.filter(p => p.status === 'assigned').length / strategyPositions.length) * 100
        };
      }
    });

    return metrics;
  }

  calculateBenchmarkComparison(portfolio, benchmarkReturns) {
    const portfolioReturn = portfolio.performance.totalReturns;
    const comparison = {};

    Object.keys(this.benchmarks).forEach(symbol => {
      if (benchmarkReturns[symbol]) {
        const benchmarkReturn = benchmarkReturns[symbol];
        comparison[symbol] = {
          name: this.benchmarks[symbol],
          return: benchmarkReturn,
          outperformance: portfolioReturn - benchmarkReturn,
          trackingError: this.calculateTrackingError(portfolio, benchmarkReturns[symbol])
        };
      }
    });

    return comparison;
  }

  calculateSharpeRatio(returns, riskFreeRate = 0.05) {
    if (returns.length === 0) return 0;
    
    const avgReturn = returns.reduce((sum, r) => sum + r, 0) / returns.length;
    const volatility = this.calculateVolatility(returns);
    
    return volatility > 0 ? (avgReturn - riskFreeRate) / volatility : 0;
  }

  calculateSortinoRatio(returns, targetReturn = 0) {
    if (returns.length === 0) return 0;
    
    const avgReturn = returns.reduce((sum, r) => sum + r, 0) / returns.length;
    const downReturns = returns.filter(r => r < targetReturn);
    
    if (downReturns.length === 0) return Infinity;
    
    const downsideDeviation = Math.sqrt(
      downReturns.reduce((sum, r) => sum + Math.pow(r - targetReturn, 2), 0) / downReturns.length
    );
    
    return downsideDeviation > 0 ? (avgReturn - targetReturn) / downsideDeviation : 0;
  }

  calculateCalmarRatio(annualizedReturn, maxDrawdown) {
    return maxDrawdown > 0 ? annualizedReturn / maxDrawdown : 0;
  }

  calculateVolatility(returns) {
    if (returns.length <= 1) return 0;
    
    const avgReturn = returns.reduce((sum, r) => sum + r, 0) / returns.length;
    const variance = returns.reduce((sum, r) => sum + Math.pow(r - avgReturn, 2), 0) / (returns.length - 1);
    
    return Math.sqrt(variance);
  }

  calculateMaxDrawdown(positions) {
    if (positions.length === 0) return 0;
    
    let peak = 0;
    let maxDrawdown = 0;
    let runningValue = 0;

    // Sort by date to track cumulative performance
    const sortedPositions = positions.sort((a, b) => a.entryDate - b.entryDate);
    
    sortedPositions.forEach(position => {
      runningValue += position.calculateRealizedPL();
      peak = Math.max(peak, runningValue);
      const drawdown = (peak - runningValue) / peak;
      maxDrawdown = Math.max(maxDrawdown, drawdown);
    });

    return maxDrawdown * 100; // Return as percentage
  }

  calculateVaR(returns, confidenceLevel = 0.05) {
    if (returns.length === 0) return 0;
    
    const sortedReturns = [...returns].sort((a, b) => a - b);
    const index = Math.floor(returns.length * confidenceLevel);
    
    return sortedReturns[index] || 0;
  }

  calculateExpectedShortfall(returns, confidenceLevel = 0.05) {
    if (returns.length === 0) return 0;
    
    const sortedReturns = [...returns].sort((a, b) => a - b);
    const cutoffIndex = Math.floor(returns.length * confidenceLevel);
    const tailReturns = sortedReturns.slice(0, cutoffIndex);
    
    return tailReturns.length > 0 ? tailReturns.reduce((sum, r) => sum + r, 0) / tailReturns.length : 0;
  }

  calculateBeta(portfolio, benchmarkSymbol) {
    // Placeholder - would need historical portfolio and benchmark returns
    // This would require implementing correlation and variance calculations
    return 1.0; // Placeholder value
  }

  calculateTrackingError(portfolio, benchmarkReturns) {
    // Placeholder - would need historical portfolio and benchmark returns
    return 0; // Placeholder value
  }

  generatePerformanceReport(portfolio, benchmarkReturns = {}) {
    const metrics = this.calculatePortfolioMetrics(portfolio, benchmarkReturns);
    
    return {
      generatedAt: new Date(),
      period: {
        start: portfolio.createdAt,
        end: new Date(),
        daysActive: Math.ceil((new Date() - portfolio.createdAt) / (1000 * 60 * 60 * 24))
      },
      summary: {
        totalReturn: metrics.overview.totalReturn,
        annualizedReturn: metrics.returns.annualizedReturn,
        sharpeRatio: metrics.returns.sharpeRatio,
        maxDrawdown: metrics.risk.maxDrawdown,
        winRate: metrics.trading.winRate
      },
      detailed: metrics,
      highlights: this.generateHighlights(metrics),
      recommendations: this.generateRecommendations(metrics)
    };
  }

  generateHighlights(metrics) {
    const highlights = [];
    
    if (metrics.returns.annualizedReturn > 15) {
      highlights.push({
        type: 'positive',
        message: `Strong annualized return of ${metrics.returns.annualizedReturn.toFixed(1)}%`
      });
    }
    
    if (metrics.trading.winRate > 80) {
      highlights.push({
        type: 'positive',
        message: `High win rate of ${metrics.trading.winRate.toFixed(1)}%`
      });
    }
    
    if (metrics.returns.sharpeRatio > 1.5) {
      highlights.push({
        type: 'positive',
        message: `Excellent risk-adjusted return (Sharpe: ${metrics.returns.sharpeRatio.toFixed(2)})`
      });
    }
    
    if (metrics.risk.maxDrawdown < 5) {
      highlights.push({
        type: 'positive',
        message: `Low maximum drawdown of ${metrics.risk.maxDrawdown.toFixed(1)}%`
      });
    }
    
    if (metrics.trading.assignmentRate > 30) {
      highlights.push({
        type: 'warning',
        message: `High assignment rate of ${metrics.trading.assignmentRate.toFixed(1)}% - consider adjusting strike selection`
      });
    }
    
    return highlights;
  }

  generateRecommendations(metrics) {
    const recommendations = [];
    
    if (metrics.returns.annualizedReturn < 10) {
      recommendations.push({
        priority: 'HIGH',
        category: 'Returns',
        message: 'Consider targeting higher premium opportunities or adjusting strike selection',
        action: 'Review screening criteria to identify higher-yield opportunities'
      });
    }
    
    if (metrics.trading.winRate < 70) {
      recommendations.push({
        priority: 'MEDIUM',
        category: 'Risk Management',
        message: 'Win rate below target - review position management rules',
        action: 'Consider closing positions at 25-50% of maximum profit more consistently'
      });
    }
    
    if (metrics.risk.maxDrawdown > 15) {
      recommendations.push({
        priority: 'HIGH',
        category: 'Risk Management',
        message: 'Maximum drawdown exceeds comfort zone',
        action: 'Reduce position sizing and improve diversification'
      });
    }
    
    if (metrics.trading.avgDaysToClose > 35) {
      recommendations.push({
        priority: 'MEDIUM',
        category: 'Efficiency',
        message: 'Positions held longer than optimal',
        action: 'Consider targeting shorter-duration options (20-30 days) for better capital turnover'
      });
    }
    
    return recommendations;
  }

  compareStrategies(positions) {
    const strategies = ['cash-secured-put', 'covered-call'];
    const comparison = {};
    
    strategies.forEach(strategy => {
      const strategyPositions = positions.filter(p => p.strategy === strategy);
      
      if (strategyPositions.length > 0) {
        const metrics = this.calculateStrategyMetrics(strategyPositions);
        comparison[strategy] = {
          ...metrics[strategy],
          riskAdjustedReturn: this.calculateSharpeRatio(
            strategyPositions.map(p => p.calculateReturnOnCapital())
          )
        };
      }
    });
    
    return comparison;
  }
}

module.exports = PerformanceAnalyzer;