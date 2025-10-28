const { Pool } = require('pg');
const logger = require('../utils/logger');

class DatabaseConnection {
  constructor(config) {
    // PostgreSQL connection configuration
    // Support both individual params and connection string
    if (process.env.DATABASE_URL) {
      this.pool = new Pool({
        connectionString: process.env.DATABASE_URL,
        ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false,
        max: 20,
        idleTimeoutMillis: 30000,
        connectionTimeoutMillis: 2000
      });
    } else {
      this.pool = new Pool({
        host: config.host || 'postgres',
        port: config.port || 5432,
        database: config.database || 'magnus',
        user: config.user || 'postgres',
        password: config.password || 'postgres123!',
        max: 20,
        idleTimeoutMillis: 30000,
        connectionTimeoutMillis: 2000
      });
    }

    this.pool.on('error', (err) => {
      logger.error('Unexpected database error:', err);
    });
  }

  async query(text, params) {
    const start = Date.now();
    try {
      const res = await this.pool.query(text, params);
      const duration = Date.now() - start;
      logger.debug(`Query executed in ${duration}ms`, { text, rows: res.rowCount });
      return res;
    } catch (error) {
      logger.error('Database query error:', { text, error: error.message });
      throw error;
    }
  }

  async getClient() {
    return await this.pool.connect();
  }

  async end() {
    await this.pool.end();
  }

  // Get all stocks from your holdings
  async getMyStocks() {
    const query = `
      SELECT 
        symbol,
        shares,
        cost_basis,
        purchase_date,
        account_type,
        notes
      FROM stock_holdings
      WHERE active = true
      ORDER BY symbol
    `;
    
    try {
      const result = await this.query(query);
      return result.rows;
    } catch (error) {
      // If table doesn't exist, create it
      if (error.code === '42P01') {
        await this.createTables();
        return [];
      }
      throw error;
    }
  }

  // Get watchlist stocks for cash-secured puts
  async getWatchlistStocks() {
    const query = `
      SELECT 
        symbol,
        target_price,
        max_shares,
        priority,
        notes
      FROM watchlist
      WHERE active = true
      ORDER BY priority DESC, symbol
    `;
    
    try {
      const result = await this.query(query);
      return result.rows;
    } catch (error) {
      if (error.code === '42P01') {
        await this.createTables();
        return [];
      }
      throw error;
    }
  }

  // Get historical trades for learning patterns
  async getHistoricalTrades() {
    const query = `
      SELECT 
        symbol,
        strategy,
        strike,
        premium,
        expiration,
        entry_date,
        exit_date,
        profit_loss,
        exit_reason,
        notes
      FROM trade_history
      ORDER BY entry_date DESC
      LIMIT 1000
    `;
    
    try {
      const result = await this.query(query);
      return result.rows;
    } catch (error) {
      if (error.code === '42P01') {
        await this.createTables();
        return [];
      }
      throw error;
    }
  }

  // Store a new trade opportunity
  async saveOpportunity(opportunity) {
    const query = `
      INSERT INTO opportunities (
        symbol, strategy, strike, premium, expiration,
        confidence_score, risk_score, expected_return,
        analysis_data, created_at
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW())
      RETURNING id
    `;
    
    const values = [
      opportunity.symbol,
      opportunity.strategy,
      opportunity.strike,
      opportunity.premium,
      opportunity.expiration,
      opportunity.confidenceScore,
      opportunity.riskScore,
      opportunity.expectedReturn,
      JSON.stringify(opportunity.analysis)
    ];
    
    const result = await this.query(query, values);
    return result.rows[0].id;
  }

  // Get saved opportunities
  async getOpportunities(strategy = null, minConfidence = 0) {
    let query = `
      SELECT * FROM opportunities
      WHERE confidence_score >= $1
      AND created_at > NOW() - INTERVAL '24 hours'
    `;
    
    const values = [minConfidence];
    
    if (strategy) {
      query += ` AND strategy = $2`;
      values.push(strategy);
    }
    
    query += ` ORDER BY confidence_score DESC, expected_return DESC`;
    
    const result = await this.query(query, values);
    return result.rows;
  }

  // Create tables if they don't exist
  async createTables() {
    const tables = [
      // Your stock holdings
      `CREATE TABLE IF NOT EXISTS stock_holdings (
        id SERIAL PRIMARY KEY,
        symbol VARCHAR(10) NOT NULL,
        shares INTEGER NOT NULL,
        cost_basis DECIMAL(10, 2),
        purchase_date DATE,
        account_type VARCHAR(50),
        notes TEXT,
        active BOOLEAN DEFAULT true,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
      )`,
      
      // Watchlist for potential cash-secured puts
      `CREATE TABLE IF NOT EXISTS watchlist (
        id SERIAL PRIMARY KEY,
        symbol VARCHAR(10) NOT NULL UNIQUE,
        target_price DECIMAL(10, 2),
        max_shares INTEGER DEFAULT 100,
        priority INTEGER DEFAULT 5,
        notes TEXT,
        active BOOLEAN DEFAULT true,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
      )`,
      
      // Trade history for pattern learning
      `CREATE TABLE IF NOT EXISTS trade_history (
        id SERIAL PRIMARY KEY,
        symbol VARCHAR(10) NOT NULL,
        strategy VARCHAR(20) NOT NULL,
        strike DECIMAL(10, 2),
        premium DECIMAL(10, 2),
        quantity INTEGER DEFAULT 1,
        expiration DATE,
        entry_date DATE,
        exit_date DATE,
        profit_loss DECIMAL(10, 2),
        exit_reason VARCHAR(50),
        notes TEXT,
        created_at TIMESTAMP DEFAULT NOW()
      )`,
      
      // Discovered opportunities
      `CREATE TABLE IF NOT EXISTS opportunities (
        id SERIAL PRIMARY KEY,
        symbol VARCHAR(10) NOT NULL,
        strategy VARCHAR(20) NOT NULL,
        strike DECIMAL(10, 2),
        premium DECIMAL(10, 2),
        expiration DATE,
        confidence_score INTEGER,
        risk_score INTEGER,
        expected_return DECIMAL(10, 2),
        analysis_data JSONB,
        created_at TIMESTAMP DEFAULT NOW(),
        executed BOOLEAN DEFAULT false
      )`,
      
      // Real-time positions
      `CREATE TABLE IF NOT EXISTS positions (
        id SERIAL PRIMARY KEY,
        symbol VARCHAR(10) NOT NULL,
        strategy VARCHAR(20) NOT NULL,
        strike DECIMAL(10, 2),
        premium DECIMAL(10, 2),
        quantity INTEGER DEFAULT 1,
        entry_date DATE,
        expiration DATE,
        status VARCHAR(20) DEFAULT 'open',
        cash_required DECIMAL(10, 2),
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
      )`,
      
      // Performance metrics
      `CREATE TABLE IF NOT EXISTS performance_metrics (
        id SERIAL PRIMARY KEY,
        date DATE NOT NULL UNIQUE,
        total_premium_collected DECIMAL(10, 2),
        realized_pnl DECIMAL(10, 2),
        win_rate DECIMAL(5, 2),
        avg_days_to_close INTEGER,
        total_positions INTEGER,
        created_at TIMESTAMP DEFAULT NOW()
      )`
    ];

    for (const table of tables) {
      await this.query(table);
    }

    // Create indexes for better performance
    const indexes = [
      'CREATE INDEX IF NOT EXISTS idx_holdings_symbol ON stock_holdings(symbol)',
      'CREATE INDEX IF NOT EXISTS idx_watchlist_symbol ON watchlist(symbol)',
      'CREATE INDEX IF NOT EXISTS idx_history_symbol ON trade_history(symbol)',
      'CREATE INDEX IF NOT EXISTS idx_opportunities_confidence ON opportunities(confidence_score DESC)',
      'CREATE INDEX IF NOT EXISTS idx_positions_status ON positions(status)'
    ];

    for (const index of indexes) {
      await this.query(index);
    }

    logger.info('Database tables created successfully');
  }

  // Add sample data for testing
  async addSampleData() {
    // Sample stock holdings
    const holdings = [
      { symbol: 'AAPL', shares: 200, cost_basis: 150.00 },
      { symbol: 'MSFT', shares: 100, cost_basis: 250.00 },
      { symbol: 'VZ', shares: 400, cost_basis: 38.50 },
      { symbol: 'KO', shares: 300, cost_basis: 55.00 }
    ];

    for (const holding of holdings) {
      await this.query(
        `INSERT INTO stock_holdings (symbol, shares, cost_basis, purchase_date) 
         VALUES ($1, $2, $3, NOW()) 
         ON CONFLICT DO NOTHING`,
        [holding.symbol, holding.shares, holding.cost_basis]
      );
    }

    // Sample watchlist for cash-secured puts
    const watchlist = [
      { symbol: 'NVDA', target_price: 400.00, priority: 10 },
      { symbol: 'AMD', target_price: 100.00, priority: 8 },
      { symbol: 'TSLA', target_price: 200.00, priority: 7 },
      { symbol: 'JPM', target_price: 140.00, priority: 9 }
    ];

    for (const stock of watchlist) {
      await this.query(
        `INSERT INTO watchlist (symbol, target_price, priority) 
         VALUES ($1, $2, $3) 
         ON CONFLICT (symbol) DO UPDATE SET target_price = $2, priority = $3`,
        [stock.symbol, stock.target_price, stock.priority]
      );
    }

    logger.info('Sample data added to database');
  }
}

module.exports = DatabaseConnection;