class TaxCalculator {
  constructor(taxConfig = {}) {
    this.taxYear = taxConfig.taxYear || new Date().getFullYear();
    this.filingStatus = taxConfig.filingStatus || 'single'; // 'single', 'married_joint', 'married_separate', 'head_of_household'
    this.stateRate = taxConfig.stateRate || 0; // State tax rate
    this.taxBrackets = this.getTaxBrackets(this.taxYear, this.filingStatus);
    this.capitalGainsRates = this.getCapitalGainsRates(this.taxYear, this.filingStatus);
  }

  getTaxBrackets(year, status) {
    // 2024 Federal tax brackets (simplified)
    const brackets = {
      single: [
        { min: 0, max: 11000, rate: 0.10 },
        { min: 11001, max: 44725, rate: 0.12 },
        { min: 44726, max: 95375, rate: 0.22 },
        { min: 95376, max: 182050, rate: 0.24 },
        { min: 182051, max: 231250, rate: 0.32 },
        { min: 231251, max: 578125, rate: 0.35 },
        { min: 578126, max: Infinity, rate: 0.37 }
      ],
      married_joint: [
        { min: 0, max: 22000, rate: 0.10 },
        { min: 22001, max: 89450, rate: 0.12 },
        { min: 89451, max: 190750, rate: 0.22 },
        { min: 190751, max: 364200, rate: 0.24 },
        { min: 364201, max: 462500, rate: 0.32 },
        { min: 462501, max: 693750, rate: 0.35 },
        { min: 693751, max: Infinity, rate: 0.37 }
      ]
    };
    
    return brackets[status] || brackets.single;
  }

  getCapitalGainsRates(year, status) {
    // 2024 Long-term capital gains rates
    const rates = {
      single: [
        { min: 0, max: 44625, rate: 0.00 },
        { min: 44626, max: 492300, rate: 0.15 },
        { min: 492301, max: Infinity, rate: 0.20 }
      ],
      married_joint: [
        { min: 0, max: 89250, rate: 0.00 },
        { min: 89251, max: 553850, rate: 0.15 },
        { min: 553851, max: Infinity, rate: 0.20 }
      ]
    };
    
    return rates[status] || rates.single;
  }

  calculateOptionsTax(positions, income = 0) {
    const taxResults = {
      totalPremiumIncome: 0,
      shortTermCapitalGains: 0,
      longTermCapitalGains: 0,
      ordinaryIncome: 0,
      totalTaxOwed: 0,
      effectiveRate: 0,
      breakdown: {
        premiumTax: 0,
        capitalGainsTax: 0,
        additionalIncomeTax: 0
      }
    };

    // Calculate premium income (always short-term treatment)
    const premiumIncome = positions.reduce((sum, pos) => {
      if (pos.status !== 'open') {
        return sum + (pos.premium * pos.quantity * 100);
      }
      return sum;
    }, 0);

    taxResults.totalPremiumIncome = premiumIncome;
    taxResults.ordinaryIncome = premiumIncome; // Premium income taxed as ordinary income

    // Calculate assignment consequences
    positions.forEach(pos => {
      if (pos.status === 'assigned') {
        if (pos.strategy === 'cash-secured-put') {
          // Cost basis reduction - no immediate tax consequence
          // Tax impact occurs when stock is eventually sold
        } else if (pos.strategy === 'covered-call') {
          // Stock sale at assignment
          const salePrice = pos.strike + pos.premium;
          const gain = (salePrice - pos.stockPrice) * pos.quantity * 100;
          
          // Determine holding period (simplified - assumes > 1 year for long-term)
          taxResults.longTermCapitalGains += gain;
        }
      }
    });

    // Calculate taxes
    const totalIncome = income + taxResults.ordinaryIncome;
    const ordinaryTax = this.calculateOrdinaryIncomeTax(totalIncome) - this.calculateOrdinaryIncomeTax(income);
    const capitalGainsTax = this.calculateCapitalGainsTax(taxResults.longTermCapitalGains, income);

    taxResults.breakdown.premiumTax = ordinaryTax;
    taxResults.breakdown.capitalGainsTax = capitalGainsTax;
    taxResults.totalTaxOwed = ordinaryTax + capitalGainsTax;

    if (taxResults.totalPremiumIncome > 0) {
      taxResults.effectiveRate = (taxResults.totalTaxOwed / taxResults.totalPremiumIncome) * 100;
    }

    return taxResults;
  }

  calculateOrdinaryIncomeTax(income) {
    let tax = 0;
    let remainingIncome = income;

    for (const bracket of this.taxBrackets) {
      if (remainingIncome <= 0) break;

      const taxableInBracket = Math.min(remainingIncome, bracket.max - bracket.min + 1);
      tax += taxableInBracket * bracket.rate;
      remainingIncome -= taxableInBracket;
    }

    return tax;
  }

  calculateCapitalGainsTax(gains, ordinaryIncome) {
    if (gains <= 0) return 0;

    // Find appropriate capital gains rate based on total income
    const totalIncome = ordinaryIncome + gains;
    let rate = 0;

    for (const bracket of this.capitalGainsRates) {
      if (totalIncome >= bracket.min && totalIncome <= bracket.max) {
        rate = bracket.rate;
        break;
      }
    }

    return gains * rate;
  }

  calculateWashSaleImpact(positions) {
    // Simplified wash sale calculation
    const washSales = [];
    const thirtyDays = 30 * 24 * 60 * 60 * 1000;

    positions.forEach((pos1, i) => {
      if (pos1.calculateRealizedPL() >= 0) return; // Only losses subject to wash sale

      positions.slice(i + 1).forEach(pos2 => {
        if (pos1.symbol === pos2.symbol) {
          const timeDiff = Math.abs(pos2.entryDate - pos1.entryDate);
          if (timeDiff <= thirtyDays) {
            washSales.push({
              lossPosition: pos1.id,
              acquisitionPosition: pos2.id,
              disallowedLoss: Math.abs(pos1.calculateRealizedPL()),
              symbol: pos1.symbol
            });
          }
        }
      });
    });

    return washSales;
  }

  generateTaxReport(positions, income = 0, currentYear = new Date().getFullYear()) {
    const currentYearPositions = positions.filter(pos => 
      pos.entryDate.getFullYear() === currentYear && pos.status !== 'open'
    );

    const taxCalc = this.calculateOptionsTax(currentYearPositions, income);
    const washSales = this.calculateWashSaleImpact(currentYearPositions);

    // Summary by strategy
    const strategyBreakdown = {};
    currentYearPositions.forEach(pos => {
      if (!strategyBreakdown[pos.strategy]) {
        strategyBreakdown[pos.strategy] = {
          positions: 0,
          totalPremium: 0,
          totalPnL: 0,
          assignments: 0
        };
      }

      const breakdown = strategyBreakdown[pos.strategy];
      breakdown.positions++;
      breakdown.totalPremium += pos.premium * pos.quantity * 100;
      breakdown.totalPnL += pos.calculateRealizedPL();
      if (pos.status === 'assigned') breakdown.assignments++;
    });

    return {
      taxYear: currentYear,
      summary: taxCalc,
      washSales: washSales,
      strategyBreakdown: strategyBreakdown,
      positions: currentYearPositions.map(pos => ({
        id: pos.id,
        symbol: pos.symbol,
        strategy: pos.strategy,
        entryDate: pos.entryDate,
        premium: pos.premium * pos.quantity * 100,
        realizedPnL: pos.calculateRealizedPL(),
        status: pos.status,
        taxTreatment: this.getPositionTaxTreatment(pos)
      })),
      recommendations: this.generateTaxRecommendations(currentYearPositions, taxCalc)
    };
  }

  getPositionTaxTreatment(position) {
    const treatment = {
      premiumIncome: position.premium * position.quantity * 100,
      taxType: 'ordinary_income',
      notes: []
    };

    if (position.status === 'assigned') {
      if (position.strategy === 'cash-secured-put') {
        treatment.notes.push('Premium reduces cost basis of acquired stock');
        treatment.costBasisReduction = treatment.premiumIncome;
      } else if (position.strategy === 'covered-call') {
        treatment.notes.push('Premium added to stock sale price');
        treatment.effectiveSalePrice = position.strike + position.premium;
      }
    }

    // Check for qualified covered call rules
    if (position.strategy === 'covered-call' && position.getDaysToExpiration() > 30) {
      treatment.notes.push('May qualify for qualified covered call treatment');
      treatment.qualifiedCoveredCall = true;
    }

    return treatment;
  }

  generateTaxRecommendations(positions, taxCalc) {
    const recommendations = [];

    // High tax burden warning
    if (taxCalc.effectiveRate > 30) {
      recommendations.push({
        type: 'TAX_EFFICIENCY',
        priority: 'HIGH',
        message: `Effective tax rate of ${taxCalc.effectiveRate.toFixed(1)}% is high. Consider using tax-advantaged accounts.`,
        suggestion: 'Move high-turnover options strategies to IRA or 401(k)'
      });
    }

    // Wash sale warnings
    const washSales = this.calculateWashSaleImpact(positions);
    if (washSales.length > 0) {
      recommendations.push({
        type: 'WASH_SALE',
        priority: 'MEDIUM',
        message: `${washSales.length} potential wash sale violations detected`,
        suggestion: 'Review trading patterns to avoid disallowed losses'
      });
    }

    // Year-end planning
    const currentMonth = new Date().getMonth();
    if (currentMonth >= 10) { // November or December
      const openPositions = positions.filter(p => p.status === 'open');
      const losers = openPositions.filter(p => p.calculateUnrealizedPL(0) < 0);
      
      if (losers.length > 0) {
        recommendations.push({
          type: 'TAX_LOSS_HARVESTING',
          priority: 'MEDIUM',
          message: `Consider closing ${losers.length} losing positions for tax loss harvesting`,
          suggestion: 'Close positions with unrealized losses before year-end'
        });
      }
    }

    return recommendations;
  }

  calculateOptimalAccountPlacement(strategies, accountTypes) {
    // Determine best account type for each strategy based on tax efficiency
    const placements = {};

    strategies.forEach(strategy => {
      let bestAccount = 'taxable';
      let reasoning = '';

      if (strategy.turnover === 'high' || strategy.shortTermGains) {
        bestAccount = 'tax_advantaged';
        reasoning = 'High turnover strategies benefit from tax deferral';
      } else if (strategy.dividendFocused) {
        bestAccount = 'tax_advantaged';
        reasoning = 'Dividend income taxed as ordinary income';
      } else if (strategy.longTermGains) {
        bestAccount = 'taxable';
        reasoning = 'Long-term capital gains rates are favorable';
      }

      placements[strategy.name] = {
        recommendedAccount: bestAccount,
        reasoning: reasoning,
        taxEfficiency: this.calculateTaxEfficiency(strategy, bestAccount)
      };
    });

    return placements;
  }

  calculateTaxEfficiency(strategy, accountType) {
    // Simple tax efficiency score (0-100)
    let score = 50; // baseline

    if (accountType === 'tax_advantaged') {
      if (strategy.turnover === 'high') score += 30;
      if (strategy.shortTermGains) score += 20;
      if (strategy.dividendFocused) score += 15;
    } else {
      if (strategy.longTermGains) score += 25;
      if (strategy.turnover === 'low') score += 15;
      if (strategy.taxLossHarvesting) score += 10;
    }

    return Math.min(score, 100);
  }
}

module.exports = TaxCalculator;