const axios = require('axios');
const logger = require('../utils/logger');

class DataProvider {
  constructor(config = {}) {
    this.config = config;
    this.providers = [];
    
    // Initialize available providers based on config
    if (config.alphaVantage) {
      this.providers.push(new AlphaVantageProvider(config.alphaVantage));
    }
    
    // Add Yahoo Finance (no API key needed!)
    this.providers.push(new YahooFinanceProvider());
    
    // Add Finnhub if available
    if (config.finnhub) {
      this.providers.push(new FinnhubProvider(config.finnhub));
    }
    
    logger.info(`Initialized DataProvider with ${this.providers.length} providers`);
  }

  async getStockData(symbol) {
    for (const provider of this.providers) {
      try {
        const data = await provider.getStockData(symbol);
        if (data) return data;
      } catch (error) {
        logger.warn(`Provider ${provider.name} failed for ${symbol}:`, error.message);
      }
    }
    throw new Error(`Failed to get stock data for ${symbol} from all providers`);
  }

  async getOptionsChain(symbol, expiration = null) {
    for (const provider of this.providers) {
      try {
        const data = await provider.getOptionsChain(symbol, expiration);
        if (data) return data;
      } catch (error) {
        logger.warn(`Provider ${provider.name} failed for options chain:`, error.message);
      }
    }
    throw new Error(`Failed to get options chain for ${symbol} from all providers`);
  }

  async getStockUniverse() {
    // Get popular stocks for screening
    return this.providers[0].getStockUniverse();
  }

  async getFundamentals(symbol) {
    for (const provider of this.providers) {
      try {
        const data = await provider.getFundamentals(symbol);
        if (data) return data;
      } catch (error) {
        logger.warn(`Provider ${provider.name} failed for fundamentals:`, error.message);
      }
    }
    return null;
  }
}

// Yahoo Finance Provider (FREE - No API key needed!)
class YahooFinanceProvider {
  constructor() {
    this.name = 'YahooFinance';
    this.baseUrl = 'https://query2.finance.yahoo.com';
  }

  async getStockData(symbol) {
    try {
      // Using Yahoo Finance v8 API (free, no key needed)
      const url = `${this.baseUrl}/v8/finance/chart/${symbol}`;
      const response = await axios.get(url, {
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
      });

      const result = response.data.chart.result[0];
      const quote = result.meta;
      const indicators = result.indicators.quote[0];
      
      return {
        symbol: symbol,
        currentPrice: quote.regularMarketPrice,
        previousClose: quote.previousClose,
        marketCap: quote.marketCap || 0,
        volume: indicators.volume[indicators.volume.length - 1],
        high: quote.regularMarketDayHigh,
        low: quote.regularMarketDayLow,
        fiftyTwoWeekHigh: quote.fiftyTwoWeekHigh,
        fiftyTwoWeekLow: quote.fiftyTwoWeekLow
      };
    } catch (error) {
      logger.error(`YahooFinance error for ${symbol}:`, error.message);
      throw error;
    }
  }

  async getOptionsChain(symbol, expiration = null) {
    try {
      // Yahoo Finance options endpoint
      const url = `${this.baseUrl}/v7/finance/options/${symbol}`;
      const response = await axios.get(url, {
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        },
        params: expiration ? { date: Math.floor(new Date(expiration).getTime() / 1000) } : {}
      });

      const optionChain = response.data.optionChain.result[0];
      const options = optionChain.options[0];
      
      return {
        symbol: symbol,
        expirationDates: optionChain.expirationDates.map(ts => new Date(ts * 1000)),
        calls: options.calls.map(this.parseOption),
        puts: options.puts.map(this.parseOption)
      };
    } catch (error) {
      logger.error(`YahooFinance options error for ${symbol}:`, error.message);
      throw error;
    }
  }

  parseOption(opt) {
    const expiration = new Date(opt.expiration * 1000);
    const daysToExpiration = Math.ceil((expiration - new Date()) / (1000 * 60 * 60 * 24));
    
    return {
      contractSymbol: opt.contractSymbol,
      strike: opt.strike,
      expiration: expiration,
      daysToExpiration: daysToExpiration,
      premium: opt.lastPrice || ((opt.bid + opt.ask) / 2),
      bid: opt.bid,
      ask: opt.ask,
      bidAskSpread: opt.ask - opt.bid,
      volume: opt.volume || 0,
      openInterest: opt.openInterest || 0,
      impliedVolatility: (opt.impliedVolatility || 0) * 100,
      inTheMoney: opt.inTheMoney
    };
  }

  async getFundamentals(symbol) {
    try {
      const url = `${this.baseUrl}/v10/finance/quoteSummary/${symbol}`;
      const response = await axios.get(url, {
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        },
        params: {
          modules: 'defaultKeyStatistics,financialData,summaryDetail'
        }
      });

      const result = response.data.quoteSummary.result[0];
      
      return {
        pe: result.summaryDetail?.trailingPE?.raw || null,
        forwardPE: result.summaryDetail?.forwardPE?.raw || null,
        dividendYield: (result.summaryDetail?.dividendYield?.raw || 0) * 100,
        beta: result.defaultKeyStatistics?.beta?.raw || 1,
        debtToEquity: result.financialData?.debtToEquity?.raw || null,
        profitMargins: (result.financialData?.profitMargins?.raw || 0) * 100,
        returnOnEquity: (result.financialData?.returnOnEquity?.raw || 0) * 100,
        sector: result.summaryProfile?.sector || 'Unknown'
      };
    } catch (error) {
      logger.error(`YahooFinance fundamentals error for ${symbol}:`, error.message);
      return null;
    }
  }

  async getStockUniverse() {
    // Return popular stocks for screening
    const popularStocks = [
      'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA',
      'JPM', 'V', 'JNJ', 'WMT', 'PG', 'UNH', 'HD', 'MA',
      'DIS', 'BAC', 'VZ', 'CMCSA', 'PFE', 'CSCO', 'INTC',
      'KO', 'PEP', 'T', 'MRK', 'ABT', 'CVX', 'XOM', 'TMO'
    ];

    const stocks = [];
    for (const symbol of popularStocks) {
      try {
        const stockData = await this.getStockData(symbol);
        const fundamentals = await this.getFundamentals(symbol);
        
        stocks.push({
          symbol: symbol,
          currentPrice: stockData.currentPrice,
          marketCap: stockData.marketCap,
          beta: fundamentals?.beta || 1,
          dividendYield: fundamentals?.dividendYield || 0,
          peRatio: fundamentals?.pe || null,
          sector: fundamentals?.sector || 'Unknown',
          impliedVolatility: 25, // Would calculate from options
          optionsVolume: 5000 // Placeholder
        });
        
        // Rate limiting
        await new Promise(resolve => setTimeout(resolve, 200));
      } catch (error) {
        logger.warn(`Failed to get data for ${symbol}`);
      }
    }

    return stocks;
  }
}

// Alpha Vantage Provider (Free tier: 5 calls/min, 500/day)
class AlphaVantageProvider {
  constructor(apiKey) {
    this.name = 'AlphaVantage';
    this.apiKey = apiKey;
    this.baseUrl = 'https://www.alphavantage.co/query';
    this.callCount = 0;
    this.lastCallTime = Date.now();
  }

  async rateLimit() {
    // Enforce 5 calls per minute limit
    this.callCount++;
    const now = Date.now();
    const timeSinceLastCall = now - this.lastCallTime;
    
    if (this.callCount >= 5 && timeSinceLastCall < 60000) {
      const waitTime = 60000 - timeSinceLastCall;
      logger.info(`AlphaVantage rate limit: waiting ${waitTime}ms`);
      await new Promise(resolve => setTimeout(resolve, waitTime));
      this.callCount = 0;
    }
    
    this.lastCallTime = Date.now();
  }

  async getStockData(symbol) {
    await this.rateLimit();
    
    try {
      const response = await axios.get(this.baseUrl, {
        params: {
          function: 'GLOBAL_QUOTE',
          symbol: symbol,
          apikey: this.apiKey
        }
      });

      const quote = response.data['Global Quote'];
      if (!quote) throw new Error('No data returned');

      return {
        symbol: symbol,
        currentPrice: parseFloat(quote['05. price']),
        previousClose: parseFloat(quote['08. previous close']),
        volume: parseInt(quote['06. volume']),
        high: parseFloat(quote['03. high']),
        low: parseFloat(quote['04. low']),
        changePercent: parseFloat(quote['10. change percent'].replace('%', ''))
      };
    } catch (error) {
      logger.error(`AlphaVantage error for ${symbol}:`, error.message);
      throw error;
    }
  }

  async getOptionsChain(symbol, expiration = null) {
    // Alpha Vantage doesn't provide options data in free tier
    // Would need premium subscription
    throw new Error('Options data requires Alpha Vantage premium subscription');
  }

  async getFundamentals(symbol) {
    await this.rateLimit();
    
    try {
      const response = await axios.get(this.baseUrl, {
        params: {
          function: 'OVERVIEW',
          symbol: symbol,
          apikey: this.apiKey
        }
      });

      const data = response.data;
      if (!data.Symbol) throw new Error('No data returned');

      return {
        marketCap: parseFloat(data.MarketCapitalization),
        pe: parseFloat(data.PERatio),
        dividendYield: parseFloat(data.DividendYield) * 100,
        beta: parseFloat(data.Beta),
        eps: parseFloat(data.EPS),
        sector: data.Sector,
        profitMargin: parseFloat(data.ProfitMargin) * 100,
        returnOnEquity: parseFloat(data.ReturnOnEquityTTM) * 100
      };
    } catch (error) {
      logger.error(`AlphaVantage fundamentals error for ${symbol}:`, error.message);
      throw error;
    }
  }

  async getStockUniverse() {
    // Use S&P 500 constituents
    return [];
  }
}

// Finnhub Provider (Free tier: 60 calls/min)
class FinnhubProvider {
  constructor(apiKey) {
    this.name = 'Finnhub';
    this.apiKey = apiKey;
    this.baseUrl = 'https://finnhub.io/api/v1';
  }

  async getStockData(symbol) {
    try {
      const response = await axios.get(`${this.baseUrl}/quote`, {
        params: {
          symbol: symbol,
          token: this.apiKey
        }
      });

      const data = response.data;
      
      return {
        symbol: symbol,
        currentPrice: data.c,
        previousClose: data.pc,
        high: data.h,
        low: data.l,
        open: data.o,
        changePercent: ((data.c - data.pc) / data.pc) * 100
      };
    } catch (error) {
      logger.error(`Finnhub error for ${symbol}:`, error.message);
      throw error;
    }
  }

  async getOptionsChain(symbol, expiration = null) {
    // Finnhub doesn't provide options data in free tier
    throw new Error('Options data not available in Finnhub free tier');
  }

  async getFundamentals(symbol) {
    try {
      const response = await axios.get(`${this.baseUrl}/stock/metric`, {
        params: {
          symbol: symbol,
          metric: 'all',
          token: this.apiKey
        }
      });

      const metrics = response.data.metric;
      
      return {
        pe: metrics['peBasicExclExtraTTM'],
        dividendYield: metrics['dividendYieldIndicatedAnnual'],
        beta: metrics['beta'],
        marketCap: metrics['marketCapitalization'],
        debtToEquity: metrics['totalDebt/totalEquityQuarterly'],
        returnOnEquity: metrics['roeTTM']
      };
    } catch (error) {
      logger.error(`Finnhub fundamentals error for ${symbol}:`, error.message);
      return null;
    }
  }

  async getStockUniverse() {
    return [];
  }
}

module.exports = DataProvider;