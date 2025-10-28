require('dotenv').config();
const DatabaseConnection = require('./database/DatabaseConnection');
const DataProvider = require('./api/DataProvider');
const PremiumOptimizer = require('./analysis/PremiumOptimizer');
const logger = require('./utils/logger');

class WheelStrategyApp {
  constructor() {
    // Database configuration from environment variables or defaults
    this.dbConfig = {
      host: process.env.DB_HOST || 'postgres',
      port: process.env.DB_PORT || 5432,
      database: process.env.DB_NAME || 'magnus',
      user: process.env.DB_USER || 'postgres',
      password: process.env.DB_PASSWORD || 'postgres123!'
    };

    // Initialize components
    this.database = new DatabaseConnection(this.dbConfig);
    this.dataProvider = new DataProvider({}); // Uses Yahoo Finance by default (free)
    this.optimizer = new PremiumOptimizer(this.dataProvider, this.database);
    
    logger.info('Wheel Strategy App initialized');
  }

  async initialize() {
    try {
      // Test database connection
      await this.database.query('SELECT NOW()');
      logger.info('Database connected successfully');
      
      // Create tables if they don't exist
      await this.database.createTables();
      
      // Test data provider
      const testStock = await this.dataProvider.getStockData('AAPL');
      logger.info(`Data provider connected. AAPL: $${testStock.currentPrice}`);
      
      return true;
    } catch (error) {
      logger.error('Initialization failed:', error);
      return false;
    }
  }

  async scanForOpportunities() {
    logger.info('Starting opportunity scan...');
    
    try {
      // Find best opportunities from your database stocks
      const opportunities = await this.optimizer.findBestOpportunities();
      
      // Generate report
      const report = await this.optimizer.generateReport(opportunities);
      
      // Log summary
      logger.info(`Found ${opportunities.length} opportunities`);
      logger.info(`Strong Buys: ${report.summary.strongBuys}, Buys: ${report.summary.buys}`);
      logger.info(`Average Expected Return: ${report.summary.avgExpectedReturn}%`);
      
      return report;
    } catch (error) {
      logger.error('Scan failed:', error);
      throw error;
    }
  }

  async displayOpportunities(report) {
    console.log('\n' + '='.repeat(80));
    console.log('WHEEL STRATEGY OPPORTUNITY REPORT');
    console.log('='.repeat(80));
    console.log(`Generated: ${report.timestamp.toLocaleString()}`);
    console.log('-'.repeat(80));
    
    // Summary
    console.log('\n📊 SUMMARY');
    console.log(`Total Opportunities: ${report.summary.totalOpportunities}`);
    console.log(`Strong Buys: ${report.summary.strongBuys} | Buys: ${report.summary.buys}`);
    console.log(`Average Confidence: ${report.summary.avgConfidence}%`);
    console.log(`Average Risk: ${report.summary.avgRisk}%`);
    console.log(`Average Expected Return: ${report.summary.avgExpectedReturn}%`);
    
    // Top Covered Calls
    if (report.topCoveredCalls.length > 0) {
      console.log('\n🎯 TOP COVERED CALL OPPORTUNITIES');
      console.log('-'.repeat(80));
      console.log('Symbol | Strike | Premium | Exp    | Confidence | Risk | Return | Action');
      console.log('-'.repeat(80));
      
      report.topCoveredCalls.forEach(opp => {
        const expDate = new Date(opp.expiration).toLocaleDateString('en-US', { month: '2-digit', day: '2-digit' });
        console.log(
          `${opp.symbol.padEnd(6)} | ` +
          `$${opp.strike.toFixed(2).padEnd(6)} | ` +
          `$${opp.premium.toFixed(2).padEnd(7)} | ` +
          `${expDate.padEnd(6)} | ` +
          `${opp.confidence.padStart(10)} | ` +
          `${opp.risk.padStart(4)} | ` +
          `${opp.expectedReturn.padStart(7)} | ` +
          `${opp.action}`
        );
        if (opp.reasons.length > 0) {
          console.log(`  ↳ ${opp.reasons.join(', ')}`);
        }
      });
    }
    
    // Top Cash-Secured Puts
    if (report.topCashSecuredPuts.length > 0) {
      console.log('\n💰 TOP CASH-SECURED PUT OPPORTUNITIES');
      console.log('-'.repeat(80));
      console.log('Symbol | Strike | Premium | Exp    | Confidence | Risk | Return | Action');
      console.log('-'.repeat(80));
      
      report.topCashSecuredPuts.forEach(opp => {
        const expDate = new Date(opp.expiration).toLocaleDateString('en-US', { month: '2-digit', day: '2-digit' });
        console.log(
          `${opp.symbol.padEnd(6)} | ` +
          `$${opp.strike.toFixed(2).padEnd(6)} | ` +
          `$${opp.premium.toFixed(2).padEnd(7)} | ` +
          `${expDate.padEnd(6)} | ` +
          `${opp.confidence.padStart(10)} | ` +
          `${opp.risk.padStart(4)} | ` +
          `${opp.expectedReturn.padStart(7)} | ` +
          `${opp.action}`
        );
        if (opp.reasons.length > 0) {
          console.log(`  ↳ ${opp.reasons.join(', ')}`);
        }
      });
    }
    
    // Risk Analysis
    console.log('\n⚠️  RISK ANALYSIS');
    console.log('-'.repeat(80));
    console.log(`Portfolio Diversification: ${report.riskAnalysis.diversification} symbols`);
    if (report.riskAnalysis.concentrationRisks.length > 0) {
      console.log('Concentration Risks:');
      report.riskAnalysis.concentrationRisks.forEach(risk => {
        console.log(`  • ${risk}`);
      });
    } else {
      console.log('No significant concentration risks detected');
    }
    
    console.log('\n' + '='.repeat(80));
  }

  async addSampleData() {
    logger.info('Adding sample data to database...');
    await this.database.addSampleData();
    logger.info('Sample data added successfully');
  }

  async getMyHoldings() {
    return await this.database.getMyStocks();
  }

  async getWatchlist() {
    return await this.database.getWatchlistStocks();
  }

  async addToWatchlist(symbol, targetPrice, priority = 5) {
    const query = `
      INSERT INTO watchlist (symbol, target_price, priority)
      VALUES ($1, $2, $3)
      ON CONFLICT (symbol) DO UPDATE 
      SET target_price = $2, priority = $3, updated_at = NOW()
    `;
    await this.database.query(query, [symbol, targetPrice, priority]);
    logger.info(`Added ${symbol} to watchlist with target price $${targetPrice}`);
  }

  async addHolding(symbol, shares, costBasis) {
    const query = `
      INSERT INTO stock_holdings (symbol, shares, cost_basis, purchase_date)
      VALUES ($1, $2, $3, NOW())
    `;
    await this.database.query(query, [symbol, shares, costBasis]);
    logger.info(`Added ${shares} shares of ${symbol} at $${costBasis}`);
  }

  async close() {
    await this.database.end();
    logger.info('Database connection closed');
  }
}

// CLI interface
async function main() {
  const app = new WheelStrategyApp();
  
  try {
    // Initialize
    const initialized = await app.initialize();
    if (!initialized) {
      console.error('Failed to initialize application');
      process.exit(1);
    }
    
    // Parse command line arguments
    const args = process.argv.slice(2);
    const command = args[0];
    
    switch (command) {
      case 'scan':
        // Scan for opportunities
        const report = await app.scanForOpportunities();
        await app.displayOpportunities(report);
        break;
        
      case 'setup':
        // Add sample data
        await app.addSampleData();
        console.log('Sample data added to database');
        break;
        
      case 'holdings':
        // Show holdings
        const holdings = await app.getMyHoldings();
        console.log('\n📈 YOUR HOLDINGS:');
        holdings.forEach(h => {
          console.log(`${h.symbol}: ${h.shares} shares @ $${h.cost_basis}`);
        });
        break;
        
      case 'watchlist':
        // Show watchlist
        const watchlist = await app.getWatchlist();
        console.log('\n👀 YOUR WATCHLIST:');
        watchlist.forEach(w => {
          console.log(`${w.symbol}: Target $${w.target_price} (Priority: ${w.priority})`);
        });
        break;
        
      case 'add-holding':
        // Add a holding: node app.js add-holding AAPL 100 150.00
        if (args.length < 4) {
          console.log('Usage: node app.js add-holding <symbol> <shares> <cost_basis>');
          break;
        }
        await app.addHolding(args[1], parseInt(args[2]), parseFloat(args[3]));
        console.log('Holding added successfully');
        break;
        
      case 'add-watchlist':
        // Add to watchlist: node app.js add-watchlist NVDA 400 10
        if (args.length < 3) {
          console.log('Usage: node app.js add-watchlist <symbol> <target_price> [priority]');
          break;
        }
        await app.addToWatchlist(args[1], parseFloat(args[2]), parseInt(args[3]) || 5);
        console.log('Added to watchlist successfully');
        break;
        
      default:
        console.log(`
Wheel Strategy Premium Optimizer
================================

Commands:
  scan          - Scan for best covered call and cash-secured put opportunities
  setup         - Add sample data to database
  holdings      - Show your stock holdings
  watchlist     - Show your watchlist
  add-holding   - Add a stock holding (symbol, shares, cost_basis)
  add-watchlist - Add stock to watchlist (symbol, target_price, priority)

Examples:
  node app.js scan
  node app.js add-holding AAPL 100 150.00
  node app.js add-watchlist NVDA 400 10

Configuration:
  Edit .env file to set database connection:
  DB_HOST=localhost
  DB_PORT=5432
  DB_NAME=trading
  DB_USER=postgres
  DB_PASSWORD=yourpassword
        `);
    }
  } catch (error) {
    console.error('Error:', error.message);
    logger.error('Application error:', error);
  } finally {
    await app.close();
  }
}

// Run if called directly
if (require.main === module) {
  main();
}

module.exports = WheelStrategyApp;