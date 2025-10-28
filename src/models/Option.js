class Option {
  constructor({
    symbol,
    type, // 'put' or 'call'
    strike,
    expiration,
    premium,
    delta,
    theta,
    vega,
    gamma,
    impliedVolatility,
    bidAskSpread,
    volume,
    openInterest
  }) {
    this.symbol = symbol;
    this.type = type;
    this.strike = strike;
    this.expiration = new Date(expiration);
    this.premium = premium;
    this.delta = delta;
    this.theta = theta;
    this.vega = vega;
    this.gamma = gamma;
    this.impliedVolatility = impliedVolatility;
    this.bidAskSpread = bidAskSpread;
    this.volume = volume;
    this.openInterest = openInterest;
    this.createdAt = new Date();
  }

  getDaysToExpiration() {
    const now = new Date();
    const timeDiff = this.expiration.getTime() - now.getTime();
    return Math.ceil(timeDiff / (1000 * 3600 * 24));
  }

  calculateAnnualizedReturn(cashAtRisk) {
    const daysToExp = this.getDaysToExpiration();
    const periodReturn = (this.premium * 100) / cashAtRisk;
    return (periodReturn * 365) / daysToExp;
  }

  isLiquid() {
    return this.bidAskSpread <= 0.10 && this.volume > 100;
  }

  calculateMaxLoss(stockPrice = null) {
    if (this.type === 'put') {
      return this.strike - this.premium;
    } else if (this.type === 'call' && stockPrice) {
      return stockPrice - this.premium;
    }
    return 0;
  }

  calculateBreakeven(stockPrice = null) {
    if (this.type === 'put') {
      return this.strike - this.premium;
    } else if (this.type === 'call' && stockPrice) {
      return stockPrice + this.premium;
    }
    return 0;
  }
}

module.exports = Option;