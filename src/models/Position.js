class Position {
  constructor({
    id,
    symbol,
    strategy, // 'cash-secured-put' or 'covered-call'
    entryDate,
    expirationDate,
    strike,
    premium,
    quantity,
    status, // 'open', 'closed', 'assigned', 'expired'
    stockPrice,
    assignmentPrice = null,
    closingPrice = null,
    cashRequired
  }) {
    this.id = id;
    this.symbol = symbol;
    this.strategy = strategy;
    this.entryDate = new Date(entryDate);
    this.expirationDate = new Date(expirationDate);
    this.strike = strike;
    this.premium = premium;
    this.quantity = quantity;
    this.status = status;
    this.stockPrice = stockPrice;
    this.assignmentPrice = assignmentPrice;
    this.closingPrice = closingPrice;
    this.cashRequired = cashRequired;
    this.updatedAt = new Date();
  }

  calculateUnrealizedPL(currentOptionPrice) {
    if (this.status !== 'open') return 0;
    return (this.premium - currentOptionPrice) * this.quantity * 100;
  }

  calculateRealizedPL() {
    if (this.status === 'open') return 0;
    
    if (this.status === 'expired') {
      return this.premium * this.quantity * 100;
    }
    
    if (this.status === 'closed' && this.closingPrice) {
      return (this.premium - this.closingPrice) * this.quantity * 100;
    }
    
    if (this.status === 'assigned') {
      if (this.strategy === 'cash-secured-put') {
        return this.premium * this.quantity * 100;
      } else if (this.strategy === 'covered-call') {
        const stockGain = (this.strike - this.stockPrice) * this.quantity * 100;
        const premiumIncome = this.premium * this.quantity * 100;
        return stockGain + premiumIncome;
      }
    }
    
    return 0;
  }

  calculateReturnOnCapital() {
    const profit = this.calculateRealizedPL();
    return (profit / this.cashRequired) * 100;
  }

  calculateAnnualizedReturn() {
    const daysHeld = Math.ceil((this.updatedAt - this.entryDate) / (1000 * 60 * 60 * 24));
    const returnOnCapital = this.calculateReturnOnCapital();
    return (returnOnCapital * 365) / daysHeld;
  }

  getDaysToExpiration() {
    const now = new Date();
    const timeDiff = this.expirationDate.getTime() - now.getTime();
    return Math.ceil(timeDiff / (1000 * 3600 * 24));
  }

  shouldClose(profitTargetPercent = 50) {
    if (this.status !== 'open') return false;
    
    const daysToExp = this.getDaysToExpiration();
    const maxProfit = this.premium * this.quantity * 100;
    const currentProfit = this.calculateUnrealizedPL(0);
    const profitPercent = (currentProfit / maxProfit) * 100;
    
    return profitPercent >= profitTargetPercent || daysToExp <= 7;
  }
}

module.exports = Position;