const config = require('../config/config');
const logger = require('./utils/logger');
const Portfolio = require('./portfolio/Portfolio');
const RiskManager = require('./portfolio/RiskManager');
const CashSecuredPut = require('./strategies/CashSecuredPut');
const CoveredCall = require('./strategies/CoveredCall');
const TaxCalculator = require('./tax/TaxCalculator');
const StockScreener = require('./analysis/StockScreener');
const PerformanceAnalyzer = require('./analysis/PerformanceAnalyzer');
const DataProvider = require('./api/DataProvider');

class WheelStrategy {
  constructor() {
    this.config = config;
    this.logger = logger;
    
    // Initialize data provider (works with no API keys using Yahoo Finance!)
    this.dataProvider = new DataProvider(config.api);
    
    // Initialize components
    this.taxCalculator = new TaxCalculator(config.tax);
    this.riskManager = new RiskManager(config.portfolio);
    this.portfolio = new Portfolio(config.portfolio.initialCash, config.portfolio.maxPositionSize);
    
    // Initialize strategies
    this.cashSecuredPut = new CashSecuredPut(this.riskManager, this.taxCalculator);
    this.coveredCall = new CoveredCall(this.riskManager, this.taxCalculator);
    
    // Initialize analysis tools with data provider
    this.stockScreener = new StockScreener(this.dataProvider);
    this.performanceAnalyzer = new PerformanceAnalyzer();
    
    this.logger.info('Wheel Strategy application initialized');
  }

  async initialize() {
    try {
      // Create necessary directories
      await this.createDirectories();
      
      // Test data provider connection
      try {
        const testStock = await this.dataProvider.getStockData('AAPL');
        this.logger.info(`Data provider connected. AAPL price: $${testStock.currentPrice}`);
      } catch (error) {
        this.logger.warn('Data provider test failed, but continuing...', error.message);
      }
      
      this.logger.info('Application fully initialized');
      return true;
    } catch (error) {
      this.logger.error('Failed to initialize application:', error);
      return false;
    }
  }

  async createDirectories() {
    const fs = require('fs').promises;
    const directories = [
      config.storage.dataDirectory,
      config.storage.backupDirectory,
      config.storage.exportDirectory
    ];

    for (const dir of directories) {
      try {
        await fs.mkdir(dir, { recursive: true });
        this.logger.debug(`Created directory: ${dir}`);
      } catch (error) {
        this.logger.warn(`Failed to create directory ${dir}:`, error.message);
      }
    }
  }

  // Main application methods
  async scanForOpportunities() {
    try {
      this.logger.info('Scanning for cash-secured put opportunities...');
      const putOpportunities = await this.stockScreener.screenForCashSecuredPuts();
      
      this.logger.info('Scanning for covered call opportunities...');
      const callOpportunities = await this.stockScreener.screenForCoveredCalls(this.portfolio);
      
      return { puts: putOpportunities, calls: callOpportunities };
    } catch (error) {
      this.logger.error('Error scanning for opportunities:', error);
      return { puts: [], calls: [] };
    }
  }

  async analyzePosition(symbol, strategy, strike, expiration, premium) {
    try {
      // Get real stock data from Yahoo Finance
      const stock = await this.dataProvider.getStockData(symbol);
      const fundamentals = await this.dataProvider.getFundamentals(symbol);
      
      // Merge data
      Object.assign(stock, {
        impliedVolatility: fundamentals?.impliedVolatility || 30,
        beta: fundamentals?.beta || 1,
        dividendYield: fundamentals?.dividendYield || 0,
        sector: fundamentals?.sector || 'Unknown'
      });
      
      if (strategy === 'cash-secured-put') {
        return this.cashSecuredPut.analyzeOpportunity(stock, strike, expiration, premium);
      } else if (strategy === 'covered-call') {
        const shares = this.portfolio.stockHoldings.get(symbol)?.shares || 0;
        return this.coveredCall.analyzeOpportunity(stock, shares, strike, expiration, premium);
      }
      
      throw new Error(`Unknown strategy: ${strategy}`);
    } catch (error) {
      this.logger.error('Error analyzing position:', error);
      throw error;
    }
  }

  async addPosition(analysis) {
    try {
      let position;
      
      if (analysis.strategy === 'cash-secured-put') {
        position = this.cashSecuredPut.createPosition(analysis);
      } else if (analysis.strategy === 'covered-call') {
        position = this.coveredCall.createPosition(analysis);
      } else {
        throw new Error(`Unknown strategy: ${analysis.strategy}`);
      }

      // Validate with risk manager
      const stock = { symbol: analysis.symbol }; // Would get full stock data
      const riskAssessment = this.riskManager.validateTrade(this.portfolio, position, stock);
      
      if (!riskAssessment.approved) {
        throw new Error(`Position rejected by risk manager: ${riskAssessment.risks.map(r => r.message).join(', ')}`);
      }

      // Add to portfolio
      const success = this.portfolio.addPosition(position);
      if (success) {
        this.logger.info(`Added position: ${position.id}`);
        return position;
      } else {
        throw new Error('Failed to add position to portfolio');
      }
    } catch (error) {
      this.logger.error('Error adding position:', error);
      throw error;
    }
  }

  async closePosition(positionId, closingPrice = 0, assignmentDetails = null) {
    try {
      const success = this.portfolio.closePosition(positionId, closingPrice, assignmentDetails);
      if (success) {
        this.logger.info(`Closed position: ${positionId}`);
        return true;
      } else {
        throw new Error('Failed to close position');
      }
    } catch (error) {
      this.logger.error('Error closing position:', error);
      throw error;
    }
  }

  generateReport(type = 'full') {
    try {
      switch (type) {
        case 'performance':
          return this.performanceAnalyzer.generatePerformanceReport(this.portfolio);
        case 'tax':
          const positions = Array.from(this.portfolio.positions.values());
          return this.taxCalculator.generateTaxReport(positions);
        case 'portfolio':
          return this.portfolio.generateReport();
        case 'risk':
          return this.riskManager.validatePortfolioRisk(this.portfolio);
        default:
          return {
            portfolio: this.portfolio.generateReport(),
            performance: this.performanceAnalyzer.generatePerformanceReport(this.portfolio),
            risk: this.riskManager.validatePortfolioRisk(this.portfolio)
          };
      }
    } catch (error) {
      this.logger.error('Error generating report:', error);
      throw error;
    }
  }

  async getPositionsNearExpiration(daysThreshold = 7) {
    try {
      const positions = this.portfolio.getPositionsNearExpiration(daysThreshold);
      return positions.map(pos => ({
        id: pos.id,
        symbol: pos.symbol,
        strategy: pos.strategy,
        strike: pos.strike,
        daysToExpiration: pos.getDaysToExpiration(),
        unrealizedPnL: pos.calculateUnrealizedPL(0), // Would use current option price
        shouldClose: pos.shouldClose()
      }));
    } catch (error) {
      this.logger.error('Error getting positions near expiration:', error);
      return [];
    }
  }

  getConfiguration() {
    return {
      portfolio: this.config.portfolio,
      trading: this.config.trading,
      screening: this.config.screening,
      tax: this.config.tax
    };
  }

  updateConfiguration(newConfig) {
    try {
      // Update risk manager with new config
      if (newConfig.portfolio) {
        Object.assign(this.config.portfolio, newConfig.portfolio);
        this.riskManager = new RiskManager(this.config.portfolio);
      }

      if (newConfig.trading) {
        Object.assign(this.config.trading, newConfig.trading);
      }

      if (newConfig.screening) {
        Object.assign(this.config.screening, newConfig.screening);
      }

      if (newConfig.tax) {
        Object.assign(this.config.tax, newConfig.tax);
        this.taxCalculator = new TaxCalculator(this.config.tax);
      }

      this.logger.info('Configuration updated');
      return true;
    } catch (error) {
      this.logger.error('Error updating configuration:', error);
      return false;
    }
  }
}

// Export for use as a module
module.exports = WheelStrategy;

// If run directly, start the application
if (require.main === module) {
  const app = new WheelStrategy();
  
  app.initialize().then(success => {
    if (success) {
      console.log('Wheel Strategy application started successfully');
      console.log('Configuration:', app.getConfiguration());
    } else {
      console.error('Failed to start application');
      process.exit(1);
    }
  });
}