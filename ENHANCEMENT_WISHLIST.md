# Magnus Enhancement Wishlist

**Last Updated**: 2025-11-02
**Dashboard Health Score**: 7.5/10
**Status**: Operational with identified improvements

---

## 🚨 Critical Fixes (COMPLETED)

- ✅ **Streamlit Deprecation**: Fixed `use_container_width` → `width='stretch'`
- ✅ **Missing Logger Import**: Added to positions_page_improved.py
- ✅ **Division by Zero**: Fixed probability calculation in option_roll_evaluator.py

---

## 🎯 Quick Wins (< 1 Hour Each)

### Priority: HIGH

1. **Export Positions to CSV** (30 min)
   - **What**: Add download button on Positions page
   - **Why**: Users frequently request this for record-keeping
   - **Impact**: High user satisfaction
   - **File**: positions_page_improved.py

2. **Add Loading Indicators** (30 min)
   - **What**: Show spinner during TradingView sync and Premium scanner
   - **Why**: Users don't know if process is running
   - **Impact**: Better UX, reduces confusion
   - **Files**: dashboard.py (lines 473-481, 1200-1300)

3. **Move Credentials to .env** (15 min)
   - **What**: Remove hardcoded Robinhood login from dashboard.py line 831
   - **Why**: Security best practice
   - **Impact**: Critical for production deployment
   - **File**: dashboard.py

---

## ⚡ Medium Improvements (1-4 Hours)

### Priority: HIGH

4. **Implement Rate Limiting** (2-3 hours)
   - **What**: Add request throttling to prevent Yahoo Finance 429 errors
   - **Why**: Currently causes failures on large watchlists
   - **Impact**: Prevents crashes, improves reliability
   - **Implementation**:
     ```python
     # src/yfinance_utils.py
     import time
     from functools import wraps

     def rate_limit(calls_per_second=2):
         min_interval = 1.0 / calls_per_second
         last_called = [0.0]

         def decorator(func):
             @wraps(func)
             def wrapper(*args, **kwargs):
                 elapsed = time.time() - last_called[0]
                 wait_time = max(0, min_interval - elapsed)
                 if wait_time > 0:
                     time.sleep(wait_time)
                 result = func(*args, **kwargs)
                 last_called[0] = time.time()
                 return result
             return wrapper
         return decorator
     ```
   - **Files**: src/yfinance_utils.py, src/watchlist_sync_service.py

5. **Bulk Stock Import** (1 hour)
   - **What**: CSV upload for adding multiple stocks at once
   - **Why**: Adding stocks one-by-one is tedious
   - **Impact**: Saves significant time
   - **Features**:
     - Upload CSV with ticker symbols
     - Import S&P 500 / NASDAQ 100 lists
     - Validate tickers before import
   - **File**: dashboard.py Database Scan tab

6. **Greeks Display** (1 hour)
   - **What**: Show delta, theta, gamma for each position
   - **Why**: Critical risk metrics for options traders
   - **Impact**: Professional-grade feature
   - **Design**:
     - Add columns to positions table
     - Color-code by risk level (delta >0.5 = red)
     - Tooltip explanations
   - **File**: positions_page_improved.py

7. **Multi-DTE Options Scanner** (1 hour)
   - **What**: Let users select 21, 30, 45, 60 day options
   - **Why**: Different strategies need different DTEs
   - **Impact**: More flexible tool
   - **File**: src/csp_opportunities_finder.py

8. **Earnings Filter** (1 hour)
   - **What**: Flag stocks with earnings in next 30 days
   - **Why**: Avoid positions before volatility events
   - **Impact**: Risk management
   - **Integration**:
     - Add to Premium Scanner filter
     - Show icon on Positions page
     - Link to Earnings Calendar
   - **Files**: dashboard.py, positions_page_improved.py

### Priority: MEDIUM

9. **Position Alerts** (2 hours)
   - **What**: Notify when position down >10%, DTE < 7 days, or approaching strike
   - **Why**: Proactive risk management
   - **Impact**: Prevents losses
   - **Implementation**: Email/SMS via Twilio or SendGrid

10. **Settings Persistence** (3 hours)
    - **What**: Save/load all settings from database
    - **Why**: Currently settings don't persist
    - **Impact**: Better UX
    - **Schema**:
      ```sql
      CREATE TABLE user_settings (
          setting_key VARCHAR(100) PRIMARY KEY,
          setting_value JSONB,
          updated_at TIMESTAMP DEFAULT NOW()
      );
      ```
    - **File**: dashboard.py Settings page

11. **Greeks-Based Roll Scoring** (2 hours)
    - **What**: Use actual option Greeks instead of simplified formulas
    - **Why**: More accurate recommendations
    - **Impact**: Better trading decisions
    - **File**: src/option_roll_evaluator.py

---

## 🚀 Major Features (> 4 Hours)

### Priority: CRITICAL

12. **Bulk Options Data Sync** (8 hours)
    - **What**: Background job to sync all 1,205 stocks
    - **Why**: Currently only 89 stocks have options data (7.4% coverage)
    - **Impact**: Feature parity, enables full functionality
    - **Implementation**:
      - Batch processing (10 stocks per minute)
      - Progress dashboard with ETA
      - Nightly cron job
      - Error handling with retry logic
    - **Files**: New file src/bulk_options_sync.py

### Priority: HIGH

13. **Tax Reporting** (6 hours)
    - **What**: Group trades by tax year, calculate short/long-term gains
    - **Why**: Critical for tax season (April deadline)
    - **Impact**: Saves users hours of manual work
    - **Features**:
      - Export for TurboTax
      - Wash sale detection
      - PDF report generation
    - **File**: New page tax_reporting_page.py

14. **Strategy Performance Analytics** (5 hours)
    - **What**: Compare CSP vs CC vs Long strategies
    - **Why**: Data-driven strategy optimization
    - **Impact**: Improve trading performance
    - **Metrics**:
      - Win rate by strategy
      - Average return by symbol
      - Best time of month/year analysis
      - Correlation with market indices
    - **File**: Enhance Trade History page

15. **Execute Rolls via API** (8 hours)
    - **What**: Submit roll orders directly to Robinhood
    - **Why**: Eliminate manual execution errors
    - **Impact**: Streamlined workflow
    - **Features**:
      - One-click roll execution
      - Confirmation dialog with order details
      - Track planned vs actual results
    - **Security**: Requires 2FA confirmation
    - **File**: src/robinhood_integration.py enhancement

---

## 💎 Nice-to-Have Enhancements

16. **Dark Mode** (2 hours)
    - Toggle in settings
    - Better for late-night trading
    - File: Add to .streamlit/config.toml

17. **Mobile App** (40+ hours)
    - React Native or Flutter
    - Push notifications
    - Quick position check
    - Execute trades on-the-go

18. **Backtesting Engine** (20 hours)
    - Test strategies on historical data
    - Monte Carlo simulations
    - Risk/reward analysis
    - Strategy optimization

19. **Social Trading** (10 hours)
    - Share strategies with community
    - Leaderboard by performance
    - Follow successful traders

20. **Voice Alerts** (3 hours)
    - Text-to-speech for critical alerts
    - "Position AAPL approaching strike"

---

## 🔒 Security Enhancements

21. **Add Authentication** (8 hours)
    - Streamlit basic auth
    - OAuth2 for production
    - User roles (admin, trader, viewer)

22. **Rate Limit API Keys** (2 hours)
    - Track OpenAI API usage
    - Alert if approaching quota
    - Graceful degradation

23. **Encrypt Credentials** (4 hours)
    - Use AWS Secrets Manager or HashiCorp Vault
    - Don't store passwords in .env plaintext
    - Rotate keys monthly

24. **Audit Logging** (3 hours)
    - Track who viewed what
    - Log all trade executions
    - Compliance requirement

---

## 📊 Performance Optimizations

25. **Add Database Indexes** (1 hour)
    - Index on `stock_premiums.dte`
    - Index on `stock_data.symbol`
    - Speeds up queries by 10-100x

26. **Connection Pooling** (2 hours)
    - Support concurrent users
    - Prevent connection exhaustion
    - Use pgbouncer or SQLAlchemy pool

27. **Redis Caching** (4 hours)
    - Cache Yahoo Finance calls (5-min TTL)
    - Cache AI research results (1-hour TTL)
    - Dramatically reduces API calls

28. **Pagination** (2 hours)
    - Large DataFrames (500+ rows) slow rendering
    - Show 50 rows per page
    - Lazy loading

---

## 🎨 UI/UX Improvements

29. **Keyboard Shortcuts** (2 hours)
    - `r` = refresh positions
    - `s` = open scanner
    - `h` = trade history
    - Power user feature

30. **Customizable Dashboard** (4 hours)
    - Drag-and-drop widgets
    - Save layouts per user
    - Hide unused features

31. **Mobile Responsiveness** (3 hours)
    - Current layout breaks on mobile
    - Stack columns vertically
    - Larger touch targets

32. **Onboarding Flow** (4 hours)
    - First-time user tutorial
    - Sample data to explore
    - Video walkthrough

---

## 📝 Documentation Needs

33. **API Documentation** (4 hours)
    - OpenAPI/Swagger spec
    - Interactive API explorer
    - Code examples

34. **Database Schema Docs** (2 hours)
    - Entity-relationship diagrams
    - Table descriptions
    - Migration history

35. **User Manual** (8 hours)
    - Feature documentation
    - Trading strategies guide
    - FAQ section
    - Video tutorials

36. **Contributing Guidelines** (2 hours)
    - How to contribute
    - Code style guide
    - PR process

---

## 🧪 Testing & Quality

37. **Add Pytest Tests** (8 hours)
    - Target 60% coverage
    - Mock API responses
    - Test edge cases
    - Files needing tests:
      - option_roll_evaluator.py (914 lines, 0% coverage)
      - csp_opportunities_finder.py (191 lines, 0% coverage)
      - recovery_strategies_tab.py (852 lines, 0% coverage)

38. **CI/CD Pipeline** (4 hours)
    - GitHub Actions
    - Automated testing
    - Linting (black, flake8)
    - Deploy to staging

39. **Performance Monitoring** (4 hours)
    - Prometheus metrics
    - Grafana dashboards
    - Alert on errors

---

## 💰 Monetization (If Applicable)

40. **Premium Tier** ($29/mo)
    - Advanced Greeks analysis
    - Unlimited AI research
    - Email/SMS alerts
    - Priority support

41. **Professional Tier** ($99/mo)
    - Tax reporting
    - Multi-account support
    - API access
    - Custom strategies

42. **Enterprise** (Custom pricing)
    - White-label solution
    - Dedicated servers
    - Compliance features
    - Training/support

---

## 📅 Recommended Timeline

### **This Week** (4.5 hours total)
- ✅ Fix Streamlit deprecation (30 min) - DONE
- ✅ Fix division by zero (30 min) - DONE
- ✅ Add logger import (5 min) - DONE
- 🔲 Move credentials to .env (15 min)
- 🔲 Add rate limiting (3 hours)

### **This Month** (15.5 hours total)
- 🔲 Bulk options data sync (8 hours) - **Critical**
- 🔲 Position alerts (2 hours)
- 🔲 Settings persistence (3 hours)
- 🔲 Earnings filter (1 hour)
- 🔲 Export positions CSV (30 min)
- 🔲 Greeks display (1 hour)

### **Next Quarter** (22 hours total)
- 🔲 Tax reporting (6 hours)
- 🔲 Strategy performance analytics (5 hours)
- 🔲 Execute rolls via API (8 hours)
- 🔲 Multi-DTE scanner (1 hour)
- 🔲 Greeks-based roll scoring (2 hours)

---

## 🎯 Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Dashboard Health Score | 7.5/10 | 9.0/10 |
| Stock Options Coverage | 7.4% (89/1,205) | 90%+ (1,084/1,205) |
| Test Coverage | ~19% | 60% |
| User-Reported Bugs | ~5/week | <1/week |
| API Error Rate | ~15% (Yahoo 429s) | <1% |
| Page Load Time | ~3-5s | <2s |

---

## 📞 Contact & Feedback

For suggestions or to prioritize features, create an issue or discussion in the repository.

**Last Review**: 2025-11-02 by Magnus Agent
**Next Review**: 2025-11-16
