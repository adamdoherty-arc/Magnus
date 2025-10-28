require('dotenv').config();

const config = {
  // Environment
  NODE_ENV: process.env.NODE_ENV || 'development',
  PORT: parseInt(process.env.PORT) || 3000,
  LOG_LEVEL: process.env.LOG_LEVEL || 'info',

  // API Keys
  api: {
    alphaVantage: process.env.ALPHA_VANTAGE_API_KEY,
    polygon: process.env.POLYGON_API_KEY,
    finnhub: process.env.FINNHUB_API_KEY,
    iexCloud: process.env.IEX_CLOUD_API_KEY
  },

  // Database
  database: {
    url: process.env.DATABASE_URL || 'sqlite:./data/portfolio.db',
    logging: process.env.NODE_ENV === 'development'
  },

  // Portfolio Settings
  portfolio: {
    initialCash: parseFloat(process.env.INITIAL_CASH) || 100000,
    maxPositionSize: parseFloat(process.env.MAX_POSITION_SIZE) || 0.05,
    maxSectorAllocation: parseFloat(process.env.MAX_SECTOR_ALLOCATION) || 0.30,
    maxSingleStockAllocation: parseFloat(process.env.MAX_SINGLE_STOCK_ALLOCATION) || 0.10,
    maxOptionsAllocation: parseFloat(process.env.MAX_OPTIONS_ALLOCATION) || 0.40,
    maxDrawdown: parseFloat(process.env.MAX_DRAWDOWN) || 0.15,
    riskFreeRate: parseFloat(process.env.RISK_FREE_RATE) || 0.05
  },

  // Tax Configuration
  tax: {
    taxYear: parseInt(process.env.TAX_YEAR) || new Date().getFullYear(),
    filingStatus: process.env.FILING_STATUS || 'single',
    stateRate: parseFloat(process.env.STATE_TAX_RATE) || 0
  },

  // Trading Parameters
  trading: {
    minOptionsVolume: parseInt(process.env.MIN_OPTIONS_VOLUME) || 1000,
    maxBidAskSpread: parseFloat(process.env.MAX_BID_ASK_SPREAD) || 0.10,
    minImpliedVolatility: parseFloat(process.env.MIN_IMPLIED_VOLATILITY) || 20,
    maxImpliedVolatility: parseFloat(process.env.MAX_IMPLIED_VOLATILITY) || 40,
    minDaysToExpiration: parseInt(process.env.MIN_DAYS_TO_EXPIRATION) || 7,
    maxDaysToExpiration: parseInt(process.env.MAX_DAYS_TO_EXPIRATION) || 60,
    targetAnnualReturn: parseFloat(process.env.TARGET_ANNUAL_RETURN) || 15,
    profitTargetPercent: parseFloat(process.env.PROFIT_TARGET_PERCENT) || 50,
    minStockPrice: parseFloat(process.env.MIN_STOCK_PRICE) || 20,
    maxStockPrice: parseFloat(process.env.MAX_STOCK_PRICE) || 1000
  },

  // Screening Criteria
  screening: {
    minMarketCap: parseFloat(process.env.MIN_MARKET_CAP) || 10e9,
    maxMarketCap: parseFloat(process.env.MAX_MARKET_CAP) || Infinity,
    minBeta: parseFloat(process.env.MIN_BETA) || 0.5,
    maxBeta: parseFloat(process.env.MAX_BETA) || 1.5,
    minDividendYield: parseFloat(process.env.MIN_DIVIDEND_YIELD) || 2,
    maxDividendYield: parseFloat(process.env.MAX_DIVIDEND_YIELD) || 6,
    maxDebtToEquity: parseFloat(process.env.MAX_DEBT_TO_EQUITY) || 2.0,
    excludedSectors: (process.env.EXCLUDED_SECTORS || 'REIT').split(','),
    preferredSectors: (process.env.PREFERRED_SECTORS || 'Technology,Healthcare,Consumer Staples,Financials').split(',')
  },

  // Data Storage
  storage: {
    dataDirectory: process.env.DATA_DIRECTORY || './data',
    backupDirectory: process.env.BACKUP_DIRECTORY || './backups',
    exportDirectory: process.env.EXPORT_DIRECTORY || './exports'
  },

  // Notifications
  notifications: {
    email: {
      enabled: !!process.env.SMTP_HOST,
      smtp: {
        host: process.env.SMTP_HOST,
        port: parseInt(process.env.SMTP_PORT) || 587,
        secure: false,
        auth: {
          user: process.env.SMTP_USER,
          pass: process.env.SMTP_PASSWORD
        }
      },
      to: process.env.NOTIFICATION_EMAIL
    },
    discord: {
      enabled: !!process.env.DISCORD_WEBHOOK_URL,
      webhookUrl: process.env.DISCORD_WEBHOOK_URL
    },
    slack: {
      enabled: !!process.env.SLACK_WEBHOOK_URL,
      webhookUrl: process.env.SLACK_WEBHOOK_URL
    }
  },

  // Market Hours (EST)
  marketHours: {
    preMarket: { start: '04:00', end: '09:30' },
    regular: { start: '09:30', end: '16:00' },
    afterHours: { start: '16:00', end: '20:00' }
  },

  // Data Refresh Intervals (in minutes)
  dataRefresh: {
    stocks: parseInt(process.env.STOCK_REFRESH_INTERVAL) || 15,
    options: parseInt(process.env.OPTIONS_REFRESH_INTERVAL) || 5,
    portfolio: parseInt(process.env.PORTFOLIO_REFRESH_INTERVAL) || 1
  }
};

// Validation
function validateConfig() {
  const errors = [];

  // Check for at least one API key
  const apiKeys = Object.values(config.api).filter(key => key);
  if (apiKeys.length === 0) {
    errors.push('At least one market data API key is required');
  }

  // Validate portfolio settings
  if (config.portfolio.maxPositionSize > 0.2) {
    errors.push('Max position size should not exceed 20%');
  }

  if (config.portfolio.maxSectorAllocation > 0.5) {
    errors.push('Max sector allocation should not exceed 50%');
  }

  // Validate trading parameters
  if (config.trading.minDaysToExpiration >= config.trading.maxDaysToExpiration) {
    errors.push('Min days to expiration must be less than max days to expiration');
  }

  if (config.trading.minImpliedVolatility >= config.trading.maxImpliedVolatility) {
    errors.push('Min implied volatility must be less than max implied volatility');
  }

  if (errors.length > 0) {
    console.error('Configuration errors:', errors);
    throw new Error('Invalid configuration: ' + errors.join(', '));
  }
}

// Only validate in production
if (config.NODE_ENV === 'production') {
  validateConfig();
}

module.exports = config;