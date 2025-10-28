class Stock {
  constructor({
    symbol,
    currentPrice,
    marketCap,
    beta,
    dividendYield,
    peRatio,
    sector,
    impliedVolatility,
    optionsVolume
  }) {
    this.symbol = symbol;
    this.currentPrice = currentPrice;
    this.marketCap = marketCap;
    this.beta = beta;
    this.dividendYield = dividendYield;
    this.peRatio = peRatio;
    this.sector = sector;
    this.impliedVolatility = impliedVolatility;
    this.optionsVolume = optionsVolume;
    this.updatedAt = new Date();
  }

  meetsScreeningCriteria() {
    return (
      this.marketCap > 10e9 && // > $10B market cap
      this.optionsVolume > 1000 && // > 1000 daily volume
      this.impliedVolatility >= 20 && this.impliedVolatility <= 40 && // 20-40% IV
      this.beta >= 0.5 && this.beta <= 1.5 && // 0.5-1.5 beta
      this.dividendYield >= 2 && this.dividendYield <= 6 // 2-6% dividend yield
    );
  }

  calculateEffectivePurchasePrice(putStrike, premium) {
    return putStrike - premium;
  }

  calculateMaxCoveredCallProfit(strikePrice, premium, purchasePrice) {
    const stockAppreciation = strikePrice - purchasePrice;
    return premium + stockAppreciation;
  }
}

module.exports = Stock;