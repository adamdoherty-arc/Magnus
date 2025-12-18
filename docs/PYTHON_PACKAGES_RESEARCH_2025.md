# Python Packages Research for AI Options Analysis - 2025

## Executive Summary

This document provides comprehensive research on modern Python packages for AI Options Analysis, including recommendations for upgrades, alternatives, and best practices based on 2025 industry standards.

**Key Findings:**
- LangChain 0.3+ with RunnableWithFallbacks provides robust multi-provider support
- vollib/py_vollib outperforms mibian for Greeks calculations
- asyncpg offers 5x performance improvement over psycopg3 for async operations
- Streamlit pagination requires custom components (no native support yet)
- yfinance should be replaced with official APIs for production use

---

## 1. LangChain 0.3+ Multi-Provider Architecture

### Current Status
- **Installed:** `langchain>=0.3.0`, `langchain-core>=0.3.0`, multiple provider packages
- **Current Usage:** Basic multi-provider support in `src/ai_options_agent/llm_manager.py`

### What's New in LangChain 0.3

#### Key Features
1. **Enhanced Multi-Agent Orchestration**
   - Sophisticated orchestration engine for coordinating agent interactions
   - Structured task sequencing and context sharing
   - Built-in failure response mechanisms

2. **RunnableWithFallbacks for Production Resilience**
   - Automatic provider fallback chains
   - Graceful degradation across multiple LLM providers
   - Zero-downtime provider switching

3. **Unified Provider Interface**
   - Consistent API across ChatOpenAI, ChatAnthropic, ChatGroq, etc.
   - ConfigurableField interface for runtime provider switching
   - Identical message structures across all providers

### Best Practices for Multi-Provider Systems

#### Pattern 1: Basic Fallback Chain
```python
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq

# Create a robust multi-provider chain
primary_model = ChatAnthropic(model="claude-3-7-sonnet-20250219")
fallback_1 = ChatOpenAI(model="gpt-4o")
fallback_2 = ChatGroq(model="llama-3.3-70b-versatile")

# Automatic fallback with .with_fallbacks()
robust_llm = primary_model.with_fallbacks([fallback_1, fallback_2])

# Usage - will automatically try providers in order
response = robust_llm.invoke("Analyze this options trade...")
```

#### Pattern 2: Chain-Level Fallback with Hardcoded Response
```python
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

def emergency_response(inputs):
    """Fallback when all LLM providers are down"""
    return {
        "analysis": "LLM providers unavailable. Using rule-based analysis.",
        "confidence": "low",
        "recommendation": "Manual review required"
    }

# Complete chain with fallback
options_analysis_chain = (
    PromptTemplate.from_template(
        "Analyze this options strategy: {strategy}\n"
        "Current price: {price}\n"
        "Greeks: {greeks}"
    )
    | robust_llm
    | StrOutputParser()
).with_fallbacks([RunnableLambda(emergency_response)])
```

#### Pattern 3: Tool Binding with Fallbacks
```python
from langchain_core.tools import tool

@tool
def calculate_greeks(symbol: str, strike: float, expiry: str):
    """Calculate option Greeks for analysis"""
    # Implementation
    pass

# Tool binding applies to all providers in fallback chain
tools = [calculate_greeks]
llm_with_tools = robust_llm.bind_tools(tools)

# This creates:
# RunnableWithFallbacks(
#     runnable=RunnableBinding(bound=ChatAnthropic(...), kwargs={"tools": [...]}),
#     fallbacks=[
#         RunnableBinding(bound=ChatOpenAI(...), kwargs={"tools": [...]}),
#         RunnableBinding(bound=ChatGroq(...), kwargs={"tools": [...]})
#     ]
# )
```

#### Pattern 4: Configuration-Driven Provider Management
```python
from typing import Dict, Any
from dataclasses import dataclass
import os

@dataclass
class LLMConfig:
    """Centralized LLM configuration"""
    provider: str
    model: str
    api_key: str
    temperature: float = 0.7
    max_tokens: int = 1000
    fallback_providers: list = None

class ProductionLLMManager:
    """Production-grade LLM manager with fallbacks"""

    def __init__(self, config: Dict[str, LLMConfig]):
        self.configs = config
        self.llm_cache = {}

    def get_llm_with_fallbacks(self, task: str = "default"):
        """Get LLM with automatic fallbacks based on task"""

        # Task-specific provider preferences
        task_preferences = {
            "options_analysis": ["anthropic", "openai", "groq"],
            "quick_summary": ["groq", "anthropic", "openai"],
            "complex_reasoning": ["openai", "anthropic", "groq"]
        }

        providers = task_preferences.get(task, ["anthropic", "openai", "groq"])

        # Build fallback chain
        llm_chain = []
        for provider_name in providers:
            if provider_name in self.configs:
                llm = self._create_llm(provider_name)
                llm_chain.append(llm)

        # Create fallback chain
        if len(llm_chain) > 0:
            primary = llm_chain[0]
            fallbacks = llm_chain[1:] if len(llm_chain) > 1 else []
            return primary.with_fallbacks(fallbacks) if fallbacks else primary

        raise ValueError("No LLM providers available")

    def _create_llm(self, provider_name: str):
        """Create LLM instance based on provider name"""
        config = self.configs[provider_name]

        if provider_name == "anthropic":
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(
                model=config.model,
                api_key=config.api_key,
                temperature=config.temperature,
                max_tokens=config.max_tokens
            )
        elif provider_name == "openai":
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=config.model,
                api_key=config.api_key,
                temperature=config.temperature,
                max_tokens=config.max_tokens
            )
        elif provider_name == "groq":
            from langchain_groq import ChatGroq
            return ChatGroq(
                model=config.model,
                api_key=config.api_key,
                temperature=config.temperature,
                max_tokens=config.max_tokens
            )
        # Add more providers as needed

        raise ValueError(f"Unknown provider: {provider_name}")

# Usage
configs = {
    "anthropic": LLMConfig(
        provider="anthropic",
        model="claude-3-7-sonnet-20250219",
        api_key=os.getenv("ANTHROPIC_API_KEY")
    ),
    "openai": LLMConfig(
        provider="openai",
        model="gpt-4o",
        api_key=os.getenv("OPENAI_API_KEY")
    ),
    "groq": LLMConfig(
        provider="groq",
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY")
    )
}

manager = ProductionLLMManager(configs)

# Get task-optimized LLM with fallbacks
options_llm = manager.get_llm_with_fallbacks("options_analysis")
quick_llm = manager.get_llm_with_fallbacks("quick_summary")
```

### Migration Recommendation

**RECOMMENDED UPGRADE:** Implement `RunnableWithFallbacks` in `src/ai_options_agent/llm_manager.py`

**Benefits:**
- Automatic failover between providers
- No single point of failure
- Task-optimized provider selection
- Production-ready error handling

---

## 2. Options Analysis Libraries

### Current Status
- **Installed:** `mibian==0.1.3`
- **Issues:** Limited functionality, older library, no active development

### Recommended Alternatives

#### Option 1: py_vollib (RECOMMENDED)
**Package:** `py_vollib` or `py-vollib-vectorized`

**Advantages:**
- Based on Peter Jäckel's LetsBeRational algorithm (extremely fast and accurate)
- Two orders of magnitude faster than scipy.stats for implied volatility
- Supports Black, Black-Scholes, and Black-Scholes-Merton models
- Both analytical and numerical Greeks
- Numba optimization brings performance close to C++ levels
- Active maintenance

**Installation:**
```bash
pip install py_vollib
# OR for vectorized operations (fastest)
pip install py-vollib-vectorized
```

**Usage Example:**
```python
from py_vollib.black_scholes import black_scholes
from py_vollib.black_scholes.greeks import analytical
from py_vollib import black_scholes_merton

# Calculate option price
price = black_scholes('c', S=100, K=105, t=0.25, r=0.05, sigma=0.25)

# Calculate Greeks (analytical - fastest)
delta = analytical.delta('c', S=100, K=105, t=0.25, r=0.05, sigma=0.25)
gamma = analytical.gamma('c', S=100, K=105, t=0.25, r=0.05, sigma=0.25)
theta = analytical.theta('c', S=100, K=105, t=0.25, r=0.05, sigma=0.25)
vega = analytical.vega('c', S=100, K=105, t=0.25, r=0.05, sigma=0.25)
rho = analytical.rho('c', S=100, K=105, t=0.25, r=0.05, sigma=0.25)

# Vectorized operations for multiple contracts
from py_vollib_vectorized import vectorized_black_scholes
import numpy as np

strikes = np.array([95, 100, 105, 110, 115])
prices = vectorized_black_scholes(
    flag='c',
    S=100,
    K=strikes,
    t=0.25,
    r=0.05,
    sigma=0.25
)
```

**Performance Comparison:**
- **Without Numba:** ~10x slower than original C++ vollib
- **With Numba:** Near C++ performance
- **LetsBeRational:** 2 iterations to maximum precision vs scipy's ~10+ iterations

#### Option 2: OptionGreeksGPU (For High-Volume Processing)
**Package:** `OptionGreeksGPU`

**Advantages:**
- GPU-accelerated for massive parallelization
- 1648+ contracts in 0.20 seconds (after warmup)
- Ideal for scanning large option chains
- Supports Delta, Gamma, Theta, Vega, Rho

**Installation:**
```bash
pip install OptionGreeksGPU
```

**Usage Example:**
```python
from OptionGreeksGPU import OptionGreeksCalculator

calculator = OptionGreeksCalculator()

# Process thousands of contracts
contracts = [
    {'S': 100, 'K': 95, 't': 0.25, 'r': 0.05, 'sigma': 0.25},
    {'S': 100, 'K': 100, 't': 0.25, 'r': 0.05, 'sigma': 0.25},
    # ... 1646 more contracts
]

greeks = calculator.calculate_batch(contracts)
# Returns: DataFrame with delta, gamma, theta, vega, rho for all contracts
```

**When to Use:**
- Scanning 500+ option contracts simultaneously
- Real-time market scanning
- High-frequency analysis

#### Option 3: optionlab (Strategy Analysis)
**Package:** `optionlab`

**Advantages:**
- Strategy-focused (vs single option pricing)
- P&L profiles on target dates
- Profitability ranges
- Probability of profit estimation
- Maximum/minimum return calculations

**Installation:**
```bash
pip install optionlab
```

**Usage Example:**
```python
from optionlab import Strategy

# Define a strategy (e.g., iron condor)
strategy = Strategy(
    stock_price=100,
    strategies=[
        {'type': 'call', 'strike': 105, 'premium': 2, 'n': -1},
        {'type': 'call', 'strike': 110, 'premium': 1, 'n': 1},
        {'type': 'put', 'strike': 95, 'premium': 2, 'n': -1},
        {'type': 'put', 'strike': 90, 'premium': 1, 'n': 1}
    ]
)

# Analyze strategy
pnl_profile = strategy.pnl_profile(target_date=30)
max_profit = strategy.max_profit()
max_loss = strategy.max_loss()
breakeven_points = strategy.breakeven()
prob_profit = strategy.probability_of_profit()
```

### Migration Recommendation

**RECOMMENDED:** Replace `mibian` with `py-vollib-vectorized` for general use + `optionlab` for strategy analysis

**Migration Steps:**
1. Install: `pip install py-vollib-vectorized optionlab`
2. Replace mibian Greeks calculations with py_vollib analytical Greeks
3. Add optionlab for multi-leg strategy analysis
4. Consider OptionGreeksGPU if processing 1000+ contracts

---

## 3. Technical Indicators: pandas-ta vs TA-Lib

### Current Status
- **Installed:** `pandas-ta==0.4.71b0`, `ta==0.11.0`
- **TA-Lib:** Not installed (requires C compilation)

### Comparison

| Feature | pandas-ta | TA-Lib |
|---------|-----------|--------|
| **Installation** | pip install (easy) | Requires C libraries (difficult) |
| **Performance** | Good with Numba | Excellent (C implementation) |
| **Indicators** | 150+ | 150+ |
| **Pandas Integration** | Native DataFrame support | Requires numpy conversion |
| **Ease of Use** | Very easy | Moderate |
| **Maintenance** | Active (2025) | Stable but slower updates |
| **Candlestick Patterns** | 60+ (when TA-Lib installed) | 60+ |
| **Vectorization** | DataFrame-based | NumPy array-based |

### Best Practices

#### For Current Setup (RECOMMENDED)
**Keep using pandas-ta** - Already installed, easier to use, good performance with numba

```python
import pandas as pd
import pandas_ta as ta

# Load data
df = pd.DataFrame(...)  # OHLCV data

# Add indicators directly to DataFrame
df.ta.rsi(length=14, append=True)
df.ta.macd(fast=12, slow=26, signal=9, append=True)
df.ta.bbands(length=20, std=2, append=True)
df.ta.atr(length=14, append=True)

# Custom strategy
my_strategy = ta.Strategy(
    name="Options Analysis Strategy",
    description="Technical indicators for options trading",
    ta=[
        {"kind": "rsi", "length": 14},
        {"kind": "macd", "fast": 12, "slow": 26, "signal": 9},
        {"kind": "bbands", "length": 20},
        {"kind": "atr", "length": 14},
        {"kind": "sma", "length": 50},
        {"kind": "ema", "length": 20}
    ]
)

# Apply entire strategy at once
df.ta.strategy(my_strategy)
```

#### If Performance is Critical
**Install TA-Lib** - For processing large datasets (10,000+ rows)

```bash
# Windows (using conda - easiest)
conda install -c conda-forge ta-lib

# Linux
sudo apt-get install libta-lib0-dev
pip install TA-Lib

# macOS
brew install ta-lib
pip install TA-Lib
```

```python
import talib
import numpy as np

# TA-Lib requires numpy arrays
close = df['close'].values
high = df['high'].values
low = df['low'].values

# Calculate indicators (faster for large datasets)
rsi = talib.RSI(close, timeperiod=14)
macd, macd_signal, macd_hist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
upper, middle, lower = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2)

# Convert back to DataFrame
df['rsi'] = rsi
df['macd'] = macd
```

### Recommendation

**KEEP CURRENT SETUP:** pandas-ta provides excellent balance of ease-of-use and performance

**Optional Enhancement:** Add TA-Lib only if:
- Processing 10,000+ rows regularly
- Need maximum performance for real-time analysis
- Have development environment with C compiler access

---

## 4. Market Data: yfinance Alternatives

### Current Status
- **Installed:** `yfinance>=0.2.48`
- **Issues:** Built on web scraping, not officially supported, rate limiting, IP bans

### Critical Recommendation

**WARNING:** yfinance is unreliable for production use in 2025
- Aggressive rate limiting
- Frequent IP bans
- Inconsistent data availability
- Not officially supported by Yahoo

### Production Alternatives

#### Option 1: Polygon.io (RECOMMENDED for Options)
**Best for:** Professional-grade options data, low latency

**Features:**
- Real-time and historical options data
- Options chain data
- Greeks and implied volatility
- Low-latency WebSocket feeds
- 99.9% uptime SLA

**Pricing:**
- Starter: $99/month (delayed data)
- Developer: $199/month (real-time)
- Advanced: $399/month (full options chain)

**Installation & Usage:**
```bash
pip install polygon-api-client
```

```python
from polygon import RESTClient
import os

client = RESTClient(api_key=os.getenv("POLYGON_API_KEY"))

# Get options chain
options_chain = client.list_options_contracts(
    underlying_ticker="AAPL",
    expiration_date_gte="2025-01-01",
    expiration_date_lte="2025-12-31"
)

# Get options quotes
quote = client.get_last_quote(ticker="O:AAPL250117C00150000")

# Get historical options data
aggs = client.get_aggs(
    ticker="O:AAPL250117C00150000",
    multiplier=1,
    timespan="day",
    from_="2025-01-01",
    to="2025-01-31"
)
```

#### Option 2: Alpha Vantage (Free Tier Available)
**Best for:** Budget-conscious development, limited usage

**Features:**
- Free tier: 25 requests/day
- Premium: 30 requests/minute ($49.99/month)
- Real-time and historical data
- Technical indicators built-in

**Installation & Usage:**
```bash
pip install alpha-vantage
```

```python
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators

ts = TimeSeries(key=os.getenv("ALPHA_VANTAGE_API_KEY"), output_format='pandas')

# Get stock data
data, meta_data = ts.get_daily(symbol='AAPL', outputsize='full')

# Get technical indicators
ti = TechIndicators(key=os.getenv("ALPHA_VANTAGE_API_KEY"), output_format='pandas')
rsi_data, meta = ti.get_rsi(symbol='AAPL', interval='daily', time_period=14)
```

**Limitations:**
- 25 requests/day on free tier (very restrictive)
- No options data on free tier
- Rate limits can be problematic

#### Option 3: IEX Cloud (Transparent Pricing)
**Best for:** U.S. market data, pay-as-you-go flexibility

**Features:**
- Transparent pay-per-request pricing
- Reliable U.S. market data
- Developer-friendly API
- No rate limits (pay per call)

**Installation & Usage:**
```bash
pip install iexfinance
```

```python
from iexfinance.stocks import Stock
import os

token = os.getenv("IEX_CLOUD_TOKEN")

# Get stock data
aapl = Stock("AAPL", token=token)
quote = aapl.get_quote()
fundamentals = aapl.get_fundamentals()

# Get historical data
historical = aapl.get_historical_prices(range='1m')
```

#### Option 4: Financial Modeling Prep (Best Overall Alternative)
**Best for:** Comprehensive financial data, fair pricing

**Features:**
- Free tier: 250 requests/day
- Premium: $29.99/month (unlimited)
- Real-time quotes
- Financial statements
- Options data (premium)
- SEC filings

**Installation & Usage:**
```bash
pip install financialmodelingprep
```

```python
import requests
import os

API_KEY = os.getenv("FMP_API_KEY")
BASE_URL = "https://financialmodelingprep.com/api/v3"

# Get quote
response = requests.get(f"{BASE_URL}/quote/AAPL?apikey={API_KEY}")
quote = response.json()

# Get historical data
response = requests.get(f"{BASE_URL}/historical-price-full/AAPL?apikey={API_KEY}")
historical = response.json()

# Get options chain (premium)
response = requests.get(f"{BASE_URL}/option-chain/AAPL?apikey={API_KEY}")
options = response.json()
```

#### Option 5: yahooquery (Stable Yahoo Finance Access)
**Best for:** Migration from yfinance with minimal code changes

**Features:**
- Uses official Yahoo Finance endpoints (not scraping)
- More stable than yfinance
- Similar API to yfinance
- Free (but still subject to Yahoo's terms)

**Installation & Usage:**
```bash
pip install yahooquery
```

```python
from yahooquery import Ticker

# Single ticker
aapl = Ticker('aapl')
summary = aapl.summary_detail
history = aapl.history(period='1mo')

# Multiple tickers
tickers = Ticker(['aapl', 'msft', 'googl'])
prices = tickers.price
```

### Migration Strategy

**Immediate (Development):**
```python
# Replace yfinance with yahooquery for stability
pip uninstall yfinance
pip install yahooquery
```

**Short-term (Testing):**
```python
# Add FMP for comprehensive data
pip install financialmodelingprep
# Free tier: 250 requests/day
```

**Long-term (Production):**
```python
# Migrate to Polygon.io for professional options data
pip install polygon-api-client
# Cost: $199-$399/month for real-time options
```

### Code Migration Example

**Before (yfinance):**
```python
import yfinance as yf

ticker = yf.Ticker("AAPL")
hist = ticker.history(period="1mo")
options = ticker.option_chain("2025-01-17")
```

**After (yahooquery - minimal changes):**
```python
from yahooquery import Ticker

ticker = Ticker("AAPL")
hist = ticker.history(period="1mo")
options = ticker.option_chain  # Returns all available expirations
```

**After (Polygon.io - production):**
```python
from polygon import RESTClient
import os

client = RESTClient(api_key=os.getenv("POLYGON_API_KEY"))

# Historical stock data
aggs = client.get_aggs("AAPL", 1, "day", "2024-12-01", "2025-01-01")

# Options chain
options = client.list_options_contracts(
    underlying_ticker="AAPL",
    expiration_date="2025-01-17"
)
```

---

## 5. Database: psycopg2 vs SQLAlchemy vs asyncpg

### Current Status
- **Installed:** `psycopg2-binary==2.9.9`, `sqlalchemy==2.0.23`
- **Usage:** Primarily psycopg2 for direct PostgreSQL connections

### Performance Benchmarks (2025)

| Library | Performance | Async Support | Use Case |
|---------|-------------|---------------|----------|
| **asyncpg** | 5x faster than psycopg3 | Native | High-performance async |
| **SQLAlchemy + asyncpg** | ~2867 rows/s | Yes (2.0+) | ORM with async |
| **psycopg3** | ~30% slower than asyncpg | Yes (beta) | Modern sync/async |
| **psycopg2** | ~1765 rows/s | No | Legacy sync |

### When to Use Each

#### Use psycopg2 When:
- Simple CRUD operations
- Legacy codebase
- No async requirements
- Maximum compatibility

#### Use SQLAlchemy When:
- Need ORM functionality
- Database abstraction required
- Complex queries benefit from ORM
- Team prefers ORM patterns

#### Use asyncpg When:
- High-performance requirements
- Async/await architecture (FastAPI, Sanic)
- 1M+ rows/second needed
- Real-time data processing

### Best Practices for 2025

#### Pattern 1: High-Performance Async with asyncpg

**Installation:**
```bash
pip install asyncpg
```

**Usage:**
```python
import asyncpg
import asyncio

async def fetch_options_data():
    # Create connection pool (recommended)
    pool = await asyncpg.create_pool(
        user='user',
        password='password',
        database='magnus',
        host='localhost',
        min_size=10,
        max_size=20
    )

    async with pool.acquire() as conn:
        # Execute query
        rows = await conn.fetch(
            'SELECT * FROM stock_premiums WHERE symbol = $1',
            'AAPL'
        )

        # Process results
        for row in rows:
            print(dict(row))

    await pool.close()

# Run
asyncio.run(fetch_options_data())
```

**Performance Characteristics:**
- **1M rows/second** from PostgreSQL to Python
- 5x faster than psycopg3
- Native async/await support
- Connection pooling built-in

#### Pattern 2: SQLAlchemy 2.0 with asyncpg (RECOMMENDED for ORM)

**Installation:**
```bash
pip install sqlalchemy asyncpg
```

**Usage:**
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import select
import asyncio

# Database URL - note the +asyncpg driver
DATABASE_URL = "postgresql+asyncpg://user:password@localhost/magnus"

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True, pool_size=20)

# Create async session factory
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Define models
class Base(DeclarativeBase):
    pass

class StockPremium(Base):
    __tablename__ = 'stock_premiums'

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str]
    strike: Mapped[float]
    expiration: Mapped[str]
    premium: Mapped[float]

# Async operations
async def get_premiums(symbol: str):
    async with async_session() as session:
        result = await session.execute(
            select(StockPremium).where(StockPremium.symbol == symbol)
        )
        premiums = result.scalars().all()
        return premiums

async def insert_premium(symbol: str, strike: float, expiration: str, premium: float):
    async with async_session() as session:
        new_premium = StockPremium(
            symbol=symbol,
            strike=strike,
            expiration=expiration,
            premium=premium
        )
        session.add(new_premium)
        await session.commit()

# Usage
async def main():
    # Fetch data
    premiums = await get_premiums("AAPL")

    # Insert data
    await insert_premium("AAPL", 150.0, "2025-01-17", 5.50)

asyncio.run(main())
```

**Benefits:**
- ORM convenience with async performance
- Connection pooling
- Type safety with Mapped types
- ~2867 rows/s (when using asyncpg driver)

#### Pattern 3: Connection Pool for psycopg2 (Current Setup Enhancement)

**If sticking with psycopg2, add connection pooling:**

```python
from psycopg2 import pool
import os

class DatabasePool:
    """Connection pool for psycopg2"""

    def __init__(self, minconn=5, maxconn=20):
        self.connection_pool = pool.ThreadedConnectionPool(
            minconn,
            maxconn,
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT"),
            database=os.getenv("POSTGRES_DB")
        )

    def get_connection(self):
        """Get connection from pool"""
        return self.connection_pool.getconn()

    def return_connection(self, conn):
        """Return connection to pool"""
        self.connection_pool.putconn(conn)

    def close_all(self):
        """Close all connections"""
        self.connection_pool.closeall()

# Usage
db_pool = DatabasePool()

def fetch_data(symbol):
    conn = db_pool.get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM stock_premiums WHERE symbol = %s", (symbol,))
        results = cur.fetchall()
        return results
    finally:
        cur.close()
        db_pool.return_connection(conn)
```

### Migration Recommendation

**RECOMMENDED PATH:**

1. **Short-term (Current Setup):**
   - Add connection pooling to psycopg2
   - Keep using psycopg2 for simple queries
   - File: `src/database/connection_pool.py`

2. **Medium-term (Async Migration):**
   - Install asyncpg: `pip install asyncpg`
   - Create async wrapper: `src/database/async_db.py`
   - Migrate high-traffic endpoints to asyncpg

3. **Long-term (ORM + Async):**
   - Upgrade to SQLAlchemy 2.0 + asyncpg
   - Define models in `src/database/models.py`
   - Use async sessions throughout

**Migration Priority:**
1. Options scanning (high volume) → asyncpg
2. Real-time data sync → asyncpg
3. Dashboard queries → SQLAlchemy + asyncpg
4. Admin operations → keep psycopg2

---

## 6. Streamlit: Data Display & Pagination

### Current Status
- **Installed:** `streamlit>=1.40.0`
- **Issue:** No native pagination support

### Best Practices for Large Datasets (2025)

#### Pattern 1: Automatic Optimizations (Built-in)

Streamlit automatically optimizes for datasets > 150,000 rows:
- Disables column sorting
- Reduces data processing
- Applies performance optimizations

**No code changes needed** - works automatically

#### Pattern 2: Manual Pagination (RECOMMENDED)

**Installation:**
```bash
pip install streamlit-pagination
```

**Usage:**
```python
import streamlit as st
import pandas as pd
from streamlit_pagination import pagination_component

# Load large dataset
@st.cache_data
def load_data():
    return pd.read_csv("large_options_data.csv")  # 10,000+ rows

df = load_data()

# Configuration
ROWS_PER_PAGE = 100

# Split into chunks
def chunk_dataframe(df, chunk_size):
    chunks = []
    for i in range(0, len(df), chunk_size):
        chunks.append(df.iloc[i:i+chunk_size])
    return chunks

df_chunks = chunk_dataframe(df, ROWS_PER_PAGE)

# Pagination UI
st.title("Options Scanner Results")
st.caption(f"Showing {len(df):,} total results")

# Pagination component
layout = {
    "variant": "outlined",
    "size": "large",
    "count": len(df_chunks),
    "defaultPage": 1
}

page_number = pagination_component(
    len(df_chunks),
    layout=layout,
    key="options_pagination"
)

# Display current page
if page_number:
    current_page = page_number - 1  # 0-indexed
    st.dataframe(
        df_chunks[current_page],
        use_container_width=True,
        height=600
    )
```

#### Pattern 3: Session State Pagination (No External Package)

```python
import streamlit as st
import pandas as pd

# Initialize session state
if 'page_number' not in st.session_state:
    st.session_state.page_number = 0

ROWS_PER_PAGE = 100

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("large_options_data.csv")

df = load_data()

# Calculate pagination
total_pages = len(df) // ROWS_PER_PAGE + (1 if len(df) % ROWS_PER_PAGE > 0 else 0)
start_idx = st.session_state.page_number * ROWS_PER_PAGE
end_idx = start_idx + ROWS_PER_PAGE

# Display current page
st.title("Options Scanner Results")
st.caption(f"Showing {start_idx + 1}-{min(end_idx, len(df))} of {len(df):,} results")

st.dataframe(
    df.iloc[start_idx:end_idx],
    use_container_width=True,
    height=600
)

# Pagination controls
col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

with col1:
    if st.button("⏮️ First", disabled=(st.session_state.page_number == 0)):
        st.session_state.page_number = 0
        st.rerun()

with col2:
    if st.button("◀️ Previous", disabled=(st.session_state.page_number == 0)):
        st.session_state.page_number -= 1
        st.rerun()

with col3:
    st.markdown(f"**Page {st.session_state.page_number + 1} of {total_pages}**")

with col4:
    if st.button("Next ▶️", disabled=(st.session_state.page_number >= total_pages - 1)):
        st.session_state.page_number += 1
        st.rerun()

with col5:
    if st.button("Last ⏭️", disabled=(st.session_state.page_number >= total_pages - 1)):
        st.session_state.page_number = total_pages - 1
        st.rerun()
```

#### Pattern 4: Lazy Loading with Filtering

```python
import streamlit as st
import pandas as pd

# Load data with caching
@st.cache_data(ttl=300)  # 5-minute cache
def load_data(symbol_filter=None, min_premium=None):
    """Load data with server-side filtering"""
    import psycopg2

    conn = psycopg2.connect(...)

    query = "SELECT * FROM stock_premiums WHERE 1=1"
    params = []

    if symbol_filter:
        query += " AND symbol = %s"
        params.append(symbol_filter)

    if min_premium:
        query += " AND premium >= %s"
        params.append(min_premium)

    query += " LIMIT 1000"  # Always limit

    df = pd.read_sql(query, conn, params=params)
    conn.close()

    return df

# Filters
st.sidebar.header("Filters")
symbol = st.sidebar.selectbox("Symbol", ["", "AAPL", "MSFT", "GOOGL", "TSLA"])
min_premium = st.sidebar.number_input("Min Premium", min_value=0.0, value=1.0)

# Load filtered data
df = load_data(
    symbol_filter=symbol if symbol else None,
    min_premium=min_premium
)

# Display
st.dataframe(df, use_container_width=True)
st.caption(f"Showing {len(df):,} results (limited to 1,000)")
```

#### Pattern 5: st.data_editor for Interactive Tables

```python
import streamlit as st
import pandas as pd

# Load data
@st.cache_data
def load_watchlist():
    return pd.DataFrame({
        'Symbol': ['AAPL', 'MSFT', 'GOOGL'],
        'Strike': [150.0, 380.0, 140.0],
        'Premium': [5.50, 12.30, 8.75],
        'Watch': [True, True, False]
    })

df = load_watchlist()

# Editable dataframe
st.title("Options Watchlist")

edited_df = st.data_editor(
    df,
    column_config={
        "Symbol": st.column_config.TextColumn(
            "Symbol",
            help="Stock ticker symbol",
            max_chars=10,
            required=True
        ),
        "Strike": st.column_config.NumberColumn(
            "Strike Price",
            help="Option strike price",
            min_value=0,
            format="$%.2f"
        ),
        "Premium": st.column_config.NumberColumn(
            "Premium",
            help="Option premium",
            min_value=0,
            format="$%.2f"
        ),
        "Watch": st.column_config.CheckboxColumn(
            "Watch",
            help="Monitor this option",
            default=False
        )
    },
    num_rows="dynamic",  # Allow add/delete rows
    use_container_width=True,
    hide_index=True
)

# Save changes
if st.button("Save Watchlist"):
    # Save edited_df to database
    st.success("Watchlist saved!")
```

### Recommendation

**IMPLEMENT:**
1. Session state pagination for current options scanner pages
2. Server-side filtering with LIMIT clauses
3. st.data_editor for watchlist/interactive tables
4. Caching with TTL for all data loading functions

**Code Location:**
- `src/components/pagination.py` - Reusable pagination component
- Update all scanner pages to use pagination

---

## 7. GitHub Projects & Examples

### Notable Python Options Trading Projects

#### 1. Python Quantitative Trading Strategies (8.6k stars)
**URL:** https://github.com/je-suis-tm/quant-trading

**Features:**
- VIX Calculator
- Pattern Recognition
- Options Straddle strategies
- Monte Carlo simulations
- RSI, Bollinger Bands, MACD
- Pair Trading

**Useful For:**
- Strategy ideas
- Monte Carlo implementation
- Pattern recognition algorithms

#### 2. OpenAlgo (Options Trading Platform)
**URL:** https://github.com/marketcalls/openalgo

**Features:**
- Production-ready algorithmic trading platform
- Flask + Python
- Unified API layer across 24+ Indian brokers
- TradingView integration
- Amibroker integration

**Useful For:**
- Platform architecture ideas
- Multi-broker integration patterns
- Production deployment examples

#### 3. optionlab
**URL:** https://github.com/rgaveiga/optionlab

**Features:**
- Options strategy evaluation
- P&L profiles
- Greeks calculation
- Probability analysis

**Useful For:**
- Strategy analysis implementation
- Greeks calculation patterns

#### 4. NSE Option Chain Analysis (517 stars)
**URL:** https://github.com/VarunS2002/Python-NSE-Option-Chain-Analyzer

**Features:**
- Real-time option chain analysis
- Visual trend indicators
- Technical analysis
- Continuous refresh

**Useful For:**
- Real-time data handling
- Visual analysis techniques
- Auto-refresh patterns

#### 5. LangChain Trading Agents
**URL:** https://github.com/aitrados/langchain-trading-agents

**Features:**
- Multi-agent trading system
- ManagerAnalyst, IndicatorAnalyst, PriceActionAnalyst roles
- Real-time multi-source data
- Structured trading reports with confidence levels

**Useful For:**
- Multi-agent architecture
- LLM-based analysis
- Report generation

**Usage:**
```bash
git clone https://github.com/aitrados/langchain-trading-agents.git
cd langchain-trading-agents
pip install -r requirements.txt

# Edit examples/analyze_btc.py
# Run analysis
python examples/analyze_btc.py
```

### Streamlit Pagination Examples

#### 1. streamlit-pagination Component
**URL:** https://github.com/Socvest/streamlit-pagination

**Installation:**
```bash
pip install streamlit-pagination
```

#### 2. Simple Paginator Gist
**URL:** https://gist.github.com/treuille/2ce0acb6697f205e44e3e0f576e810b7

**Direct implementation** without external dependencies

---

## 8. Implementation Recommendations

### Priority 1: Critical Upgrades (Immediate)

1. **Replace yfinance with yahooquery**
   ```bash
   pip uninstall yfinance
   pip install yahooquery
   ```

   **Impact:** More stable data retrieval
   **Effort:** Low (similar API)
   **Files to update:** All files using `yf.Ticker`

2. **Add Connection Pooling to psycopg2**
   ```bash
   # Create: src/database/connection_pool.py
   ```

   **Impact:** Better database performance
   **Effort:** Medium
   **Files:** All database access files

3. **Implement Pagination in Scanner Pages**
   ```bash
   pip install streamlit-pagination
   # OR use session state approach
   ```

   **Impact:** Better UX for large result sets
   **Effort:** Medium
   **Files:** `options_analysis_page.py`, `premium_scanner_page.py`

### Priority 2: Performance Enhancements (1-2 weeks)

4. **Migrate to py-vollib for Greeks**
   ```bash
   pip install py-vollib-vectorized
   ```

   **Impact:** Faster, more accurate Greeks calculations
   **Effort:** Medium
   **Files:** `src/ai_options_advisor.py`, options analysis modules

5. **Implement RunnableWithFallbacks in LLM Manager**
   ```python
   # Update: src/ai_options_agent/llm_manager.py
   # Add fallback chains for all providers
   ```

   **Impact:** Production-ready LLM resilience
   **Effort:** Medium
   **Benefits:** Zero-downtime provider switching

6. **Add asyncpg for High-Volume Queries**
   ```bash
   pip install asyncpg
   # Create: src/database/async_db.py
   ```

   **Impact:** 5x faster for bulk operations
   **Effort:** High
   **Files:** Options scanner, real-time sync

### Priority 3: Long-term Improvements (1-2 months)

7. **Migrate to Polygon.io (Production Data)**
   ```bash
   pip install polygon-api-client
   ```

   **Impact:** Reliable, professional-grade data
   **Effort:** High
   **Cost:** $199-$399/month

8. **SQLAlchemy 2.0 + asyncpg Migration**
   ```bash
   pip install sqlalchemy[asyncio] asyncpg
   ```

   **Impact:** Modern ORM with async performance
   **Effort:** Very High
   **Files:** All database access layers

9. **Add optionlab for Strategy Analysis**
   ```bash
   pip install optionlab
   ```

   **Impact:** Multi-leg strategy evaluation
   **Effort:** Medium
   **New Feature:** Strategy analyzer page

### Optional Enhancements

10. **TA-Lib for Maximum Performance**
    ```bash
    conda install -c conda-forge ta-lib
    ```

    **Impact:** Faster technical indicators (if needed)
    **Effort:** Low (if using conda)
    **When:** Processing 10,000+ rows regularly

11. **OptionGreeksGPU for Mass Scanning**
    ```bash
    pip install OptionGreeksGPU
    ```

    **Impact:** 1000+ contracts in <1 second
    **Effort:** Medium
    **When:** Scanning full option chains

---

## 9. Updated requirements.txt

```txt
# Core Web Framework
streamlit>=1.40.0
fastapi>=0.115.0
uvicorn[standard]>=0.32.0

# Brokerage APIs
robin-stocks==3.0.5

# Database - UPGRADED
psycopg2-binary==2.9.9
sqlalchemy==2.0.36  # Latest 2.0 with async support
asyncpg==0.30.0  # NEW: High-performance async PostgreSQL
alembic==1.13.3  # Updated
redis==5.2.1  # Updated

# Data Processing
pandas>=2.2.0
numpy>=2.0.0

# Visualization
plotly==5.24.1  # Updated

# Market Data - REPLACED
# yfinance>=0.2.48  # REMOVED
yahooquery==2.3.7  # NEW: More stable Yahoo Finance
# polygon-api-client==1.14.1  # OPTIONAL: Production use
# alpha-vantage==2.3.1  # OPTIONAL: Alternative
# financialmodelingprep==0.1.8  # OPTIONAL: FMP API

tradingview-ta>=3.3.0
alpaca-trade-api>=3.0.2

# Web Scraping & Automation
selenium==4.16.0
beautifulsoup4==4.12.2
undetected-chromedriver==3.5.4

# HTTP Requests
requests==2.31.0
aiohttp==3.9.1
websocket-client==1.6.4

# Environment & Configuration
python-dotenv==1.0.0

# Authentication & Security
pyotp==2.9.0

# Scientific Computing
scipy==1.11.4
ta==0.11.0
pandas-ta==0.4.71b0

# Options & Greeks - UPGRADED
# mibian==0.1.3  # REMOVED: Replaced with vollib
py-vollib-vectorized==0.1.2  # NEW: Faster, more accurate Greeks
optionlab==0.1.7  # NEW: Strategy analysis
# OptionGreeksGPU==0.1.0  # OPTIONAL: GPU-accelerated Greeks

# Reddit API
praw==7.7.1

# Task Scheduling
celery==5.3.4
apscheduler==3.10.4

# Logging & Monitoring
loguru==0.7.2
prometheus-client==0.19.0

# Notifications
python-telegram-bot==20.7

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-mock==3.12.0
pytest-cov==4.1.0

# Development Tools
black==23.11.0
flake8==6.1.0
mypy==1.7.1

# Data Validation
pydantic==2.5.0
pydantic-settings==2.1.0

# LangChain & LangGraph - UPDATED
langchain>=0.3.20  # Updated to latest 0.3
langchain-core>=0.3.25  # Updated
langchain-community>=0.3.20  # Updated
langchain-openai>=0.2.10  # Updated
langchain-anthropic>=0.2.10  # Updated
langchain-groq>=0.2.5  # Updated
langchain-google-genai>=2.0.5  # Updated
langchain-huggingface>=0.1.5  # Updated
langgraph>=0.2.60  # Updated
langchain-text-splitters>=0.3.5  # Updated

# Model Context Protocol (MCP)
mcp>=1.0.0

# AI/ML for Prediction Markets
sentence-transformers>=3.0.0
transformers>=4.40.0
tokenizers>=0.21,<0.22
torch>=2.0.0
scikit-learn>=1.4.0

# Vector Database & RAG
qdrant-client==1.7.0
chromadb==0.4.22

# LLM Providers - UPDATED
openai>=1.58.1  # Updated to latest
anthropic>=0.40.0  # Updated
groq>=0.13.0  # Updated
google-generativeai>=0.8.3  # Updated

# Sports Data & Analytics
nfl-data-py>=0.3.0

# Streamlit Extensions - NEW
streamlit-pagination==0.1.1  # NEW: Pagination component
```

---

## 10. Code Examples & Migration Snippets

### Example 1: LLM Fallback Chain (Complete Implementation)

**File:** `src/ai_options_agent/llm_manager_v2.py`

```python
"""
Enhanced LLM Manager with RunnableWithFallbacks
Provides production-ready multi-provider LLM support with automatic failover
"""

import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import logging

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnableLambda
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

logger = logging.getLogger(__name__)


@dataclass
class ProviderConfig:
    """Configuration for an LLM provider"""
    name: str
    model: str
    api_key: str
    temperature: float = 0.7
    max_tokens: int = 1000
    timeout: int = 60


class EnhancedLLMManager:
    """Production-ready LLM Manager with automatic fallbacks"""

    def __init__(self):
        """Initialize with all available providers"""
        self.providers = self._load_providers()
        self.fallback_chains = {}
        self._build_fallback_chains()

    def _load_providers(self) -> Dict[str, ProviderConfig]:
        """Load all available LLM providers from environment"""
        providers = {}

        # Anthropic Claude
        if api_key := os.getenv("ANTHROPIC_API_KEY"):
            providers["anthropic"] = ProviderConfig(
                name="anthropic",
                model="claude-3-7-sonnet-20250219",
                api_key=api_key,
                temperature=0.7,
                max_tokens=4096
            )

        # OpenAI GPT
        if api_key := os.getenv("OPENAI_API_KEY"):
            providers["openai"] = ProviderConfig(
                name="openai",
                model="gpt-4o",
                api_key=api_key,
                temperature=0.7,
                max_tokens=4096
            )

        # Groq (Fast & Free)
        if api_key := os.getenv("GROQ_API_KEY"):
            providers["groq"] = ProviderConfig(
                name="groq",
                model="llama-3.3-70b-versatile",
                api_key=api_key,
                temperature=0.7,
                max_tokens=8000
            )

        # Google Gemini
        if api_key := os.getenv("GOOGLE_API_KEY"):
            providers["google"] = ProviderConfig(
                name="google",
                model="gemini-2.0-flash-exp",
                api_key=api_key,
                temperature=0.7,
                max_tokens=8000
            )

        logger.info(f"Loaded {len(providers)} LLM providers: {list(providers.keys())}")
        return providers

    def _create_llm(self, provider_name: str):
        """Create LLM instance from provider config"""
        if provider_name not in self.providers:
            raise ValueError(f"Provider {provider_name} not available")

        config = self.providers[provider_name]

        if provider_name == "anthropic":
            return ChatAnthropic(
                model=config.model,
                api_key=config.api_key,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                timeout=config.timeout
            )
        elif provider_name == "openai":
            return ChatOpenAI(
                model=config.model,
                api_key=config.api_key,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                timeout=config.timeout
            )
        elif provider_name == "groq":
            return ChatGroq(
                model=config.model,
                api_key=config.api_key,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                timeout=config.timeout
            )
        elif provider_name == "google":
            return ChatGoogleGenerativeAI(
                model=config.model,
                google_api_key=config.api_key,
                temperature=config.temperature,
                max_output_tokens=config.max_tokens
            )

        raise ValueError(f"Unknown provider: {provider_name}")

    def _build_fallback_chains(self):
        """Build fallback chains for different use cases"""

        # Task-specific provider preferences
        task_preferences = {
            "options_analysis": ["anthropic", "openai", "google", "groq"],
            "quick_summary": ["groq", "google", "anthropic", "openai"],
            "complex_reasoning": ["openai", "anthropic", "google", "groq"],
            "default": ["anthropic", "openai", "groq", "google"]
        }

        for task, preferences in task_preferences.items():
            # Filter to only available providers
            available = [p for p in preferences if p in self.providers]

            if not available:
                logger.warning(f"No providers available for task: {task}")
                continue

            # Build fallback chain
            llms = [self._create_llm(p) for p in available]

            # Create fallback chain
            if len(llms) > 0:
                primary = llms[0]
                fallbacks = llms[1:] if len(llms) > 1 else []

                if fallbacks:
                    # Add final emergency fallback
                    emergency = RunnableLambda(
                        lambda x: "LLM providers unavailable. Using rule-based analysis."
                    )
                    fallbacks.append(emergency)

                    self.fallback_chains[task] = primary.with_fallbacks(fallbacks)
                else:
                    self.fallback_chains[task] = primary

                logger.info(
                    f"Built fallback chain for {task}: "
                    f"{' -> '.join(available)} -> emergency"
                )

    def get_llm(self, task: str = "default"):
        """Get LLM with automatic fallbacks for specific task"""
        if task not in self.fallback_chains:
            task = "default"

        if task not in self.fallback_chains:
            raise ValueError("No LLM providers available")

        return self.fallback_chains[task]

    def invoke(self, prompt: str, task: str = "default") -> str:
        """Invoke LLM with automatic fallbacks"""
        llm = self.get_llm(task)

        try:
            response = llm.invoke(prompt)

            # Handle different response types
            if hasattr(response, 'content'):
                return response.content
            elif isinstance(response, str):
                return response
            else:
                return str(response)

        except Exception as e:
            logger.error(f"LLM invocation failed: {e}")
            return "Analysis unavailable due to LLM error. Please try again."

    def create_chain(self, prompt_template: str, task: str = "default"):
        """Create a complete chain with prompt, LLM, and parser"""
        llm = self.get_llm(task)

        chain = (
            ChatPromptTemplate.from_template(prompt_template)
            | llm
            | StrOutputParser()
        )

        return chain


# Global instance
_llm_manager = None

def get_llm_manager() -> EnhancedLLMManager:
    """Get or create global LLM manager instance"""
    global _llm_manager

    if _llm_manager is None:
        _llm_manager = EnhancedLLMManager()

    return _llm_manager


# Usage example
if __name__ == "__main__":
    manager = get_llm_manager()

    # Simple invocation
    result = manager.invoke(
        "Analyze a covered call strategy on AAPL at $150 strike, expiring in 30 days",
        task="options_analysis"
    )
    print(result)

    # Chain invocation
    analysis_chain = manager.create_chain(
        "Analyze this options strategy:\n"
        "Symbol: {symbol}\n"
        "Strategy: {strategy}\n"
        "Strike: {strike}\n"
        "Expiration: {expiration}\n\n"
        "Provide a detailed analysis including risks and potential returns.",
        task="options_analysis"
    )

    result = analysis_chain.invoke({
        "symbol": "AAPL",
        "strategy": "Covered Call",
        "strike": "$150",
        "expiration": "30 days"
    })
    print(result)
```

### Example 2: asyncpg High-Performance Database Access

**File:** `src/database/async_db.py`

```python
"""
High-performance async PostgreSQL access using asyncpg
5x faster than psycopg3 for bulk operations
"""

import asyncpg
import asyncio
from typing import List, Dict, Any, Optional
import os
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)


class AsyncDatabasePool:
    """Async PostgreSQL connection pool using asyncpg"""

    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self._pool_initialized = False

    async def initialize(self, min_size: int = 10, max_size: int = 20):
        """Initialize connection pool"""
        if self._pool_initialized:
            return

        self.pool = await asyncpg.create_pool(
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            database=os.getenv("POSTGRES_DB"),
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            min_size=min_size,
            max_size=max_size,
            command_timeout=60
        )

        self._pool_initialized = True
        logger.info(f"Initialized asyncpg pool (min={min_size}, max={max_size})")

    async def close(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
            self._pool_initialized = False

    @asynccontextmanager
    async def acquire(self):
        """Acquire connection from pool"""
        if not self._pool_initialized:
            await self.initialize()

        async with self.pool.acquire() as conn:
            yield conn

    async def execute(self, query: str, *args) -> str:
        """Execute a query (INSERT, UPDATE, DELETE)"""
        async with self.acquire() as conn:
            return await conn.execute(query, *args)

    async def fetch(self, query: str, *args) -> List[asyncpg.Record]:
        """Fetch multiple rows"""
        async with self.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args) -> Optional[asyncpg.Record]:
        """Fetch single row"""
        async with self.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def fetchval(self, query: str, *args) -> Any:
        """Fetch single value"""
        async with self.acquire() as conn:
            return await conn.fetchval(query, *args)


# Global pool instance
_db_pool = AsyncDatabasePool()


async def get_db_pool() -> AsyncDatabasePool:
    """Get or create global database pool"""
    if not _db_pool._pool_initialized:
        await _db_pool.initialize()
    return _db_pool


# High-level async database functions
async def fetch_options_premiums(symbol: str) -> List[Dict[str, Any]]:
    """Fetch options premiums for a symbol (high-performance)"""
    pool = await get_db_pool()

    rows = await pool.fetch(
        """
        SELECT symbol, strike, expiration, premium, delta, theta, gamma, vega
        FROM stock_premiums
        WHERE symbol = $1
        ORDER BY expiration, strike
        """,
        symbol
    )

    # Convert asyncpg.Record to dict
    return [dict(row) for row in rows]


async def bulk_insert_premiums(premiums: List[Dict[str, Any]]) -> int:
    """Bulk insert premiums (extremely fast with asyncpg)"""
    pool = await get_db_pool()

    async with pool.acquire() as conn:
        # Use COPY for maximum performance
        result = await conn.copy_records_to_table(
            'stock_premiums',
            records=[
                (
                    p['symbol'],
                    p['strike'],
                    p['expiration'],
                    p['premium'],
                    p.get('delta'),
                    p.get('theta'),
                    p.get('gamma'),
                    p.get('vega')
                )
                for p in premiums
            ],
            columns=['symbol', 'strike', 'expiration', 'premium', 'delta', 'theta', 'gamma', 'vega']
        )

    return len(premiums)


async def scan_high_premium_options(min_premium: float = 1.0, limit: int = 1000) -> List[Dict[str, Any]]:
    """Scan for high-premium options (fast query)"""
    pool = await get_db_pool()

    rows = await pool.fetch(
        """
        SELECT
            symbol,
            strike,
            expiration,
            premium,
            delta,
            theta,
            (premium / strike * 100) as return_pct,
            EXTRACT(DAY FROM expiration::timestamp - CURRENT_TIMESTAMP) as days_to_expiry
        FROM stock_premiums
        WHERE premium >= $1
            AND expiration > CURRENT_DATE
        ORDER BY return_pct DESC
        LIMIT $2
        """,
        min_premium,
        limit
    )

    return [dict(row) for row in rows]


# Usage example
async def main():
    """Example usage"""

    # Fetch premiums for a symbol
    aapl_premiums = await fetch_options_premiums("AAPL")
    print(f"Found {len(aapl_premiums)} premiums for AAPL")

    # Scan for high-premium options
    high_premiums = await scan_high_premium_options(min_premium=2.0, limit=100)
    print(f"Found {len(high_premiums)} high-premium options")

    # Bulk insert example
    new_premiums = [
        {
            'symbol': 'MSFT',
            'strike': 380.0,
            'expiration': '2025-02-21',
            'premium': 12.50,
            'delta': 0.45,
            'theta': -0.25,
            'gamma': 0.015,
            'vega': 0.35
        },
        # ... more premiums
    ]

    inserted = await bulk_insert_premiums(new_premiums)
    print(f"Inserted {inserted} premiums")

    # Close pool
    await _db_pool.close()


if __name__ == "__main__":
    asyncio.run(main())
```

### Example 3: Streamlit Pagination Component

**File:** `src/components/pagination.py`

```python
"""
Reusable pagination component for Streamlit
Handles large datasets efficiently
"""

import streamlit as st
import pandas as pd
from typing import Optional, Callable


class PaginatedDataFrame:
    """Pagination handler for Streamlit DataFrames"""

    def __init__(
        self,
        df: pd.DataFrame,
        rows_per_page: int = 100,
        key: str = "pagination"
    ):
        self.df = df
        self.rows_per_page = rows_per_page
        self.key = key

        # Initialize session state
        if f'{key}_page' not in st.session_state:
            st.session_state[f'{key}_page'] = 0

    @property
    def total_pages(self) -> int:
        """Calculate total number of pages"""
        return (len(self.df) - 1) // self.rows_per_page + 1

    @property
    def current_page(self) -> int:
        """Get current page number"""
        return st.session_state[f'{self.key}_page']

    @property
    def start_idx(self) -> int:
        """Get start index for current page"""
        return self.current_page * self.rows_per_page

    @property
    def end_idx(self) -> int:
        """Get end index for current page"""
        return min(self.start_idx + self.rows_per_page, len(self.df))

    def get_page_data(self) -> pd.DataFrame:
        """Get data for current page"""
        return self.df.iloc[self.start_idx:self.end_idx]

    def render_pagination_controls(self):
        """Render pagination controls"""
        col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

        with col1:
            if st.button(
                "⏮️ First",
                key=f"{self.key}_first",
                disabled=(self.current_page == 0)
            ):
                st.session_state[f'{self.key}_page'] = 0
                st.rerun()

        with col2:
            if st.button(
                "◀️ Previous",
                key=f"{self.key}_prev",
                disabled=(self.current_page == 0)
            ):
                st.session_state[f'{self.key}_page'] -= 1
                st.rerun()

        with col3:
            st.markdown(
                f"<div style='text-align: center; padding: 8px;'>"
                f"<b>Page {self.current_page + 1} of {self.total_pages}</b><br/>"
                f"<small>Showing {self.start_idx + 1}-{self.end_idx} of {len(self.df):,} rows</small>"
                f"</div>",
                unsafe_allow_html=True
            )

        with col4:
            if st.button(
                "Next ▶️",
                key=f"{self.key}_next",
                disabled=(self.current_page >= self.total_pages - 1)
            ):
                st.session_state[f'{self.key}_page'] += 1
                st.rerun()

        with col5:
            if st.button(
                "Last ⏭️",
                key=f"{self.key}_last",
                disabled=(self.current_page >= self.total_pages - 1)
            ):
                st.session_state[f'{self.key}_page'] = self.total_pages - 1
                st.rerun()

    def render(
        self,
        height: int = 600,
        use_container_width: bool = True,
        column_config: Optional[dict] = None
    ):
        """Render paginated dataframe with controls"""

        # Show pagination info
        st.caption(f"📊 Total Results: {len(self.df):,}")

        # Show current page data
        page_data = self.get_page_data()

        st.dataframe(
            page_data,
            use_container_width=use_container_width,
            height=height,
            column_config=column_config
        )

        # Show pagination controls
        self.render_pagination_controls()

        return page_data


# Convenience function
def paginated_dataframe(
    df: pd.DataFrame,
    rows_per_page: int = 100,
    key: str = "pagination",
    height: int = 600,
    column_config: Optional[dict] = None
) -> pd.DataFrame:
    """
    Display a paginated dataframe

    Args:
        df: DataFrame to display
        rows_per_page: Number of rows per page
        key: Unique key for pagination state
        height: Height of dataframe display
        column_config: Column configuration for st.dataframe

    Returns:
        Current page data
    """
    paginator = PaginatedDataFrame(df, rows_per_page, key)
    return paginator.render(height=height, column_config=column_config)


# Usage example
if __name__ == "__main__":
    st.title("Paginated DataFrame Example")

    # Load sample data
    @st.cache_data
    def load_data():
        return pd.DataFrame({
            'Symbol': ['AAPL', 'MSFT', 'GOOGL'] * 100,
            'Strike': [150.0, 380.0, 140.0] * 100,
            'Premium': [5.50, 12.30, 8.75] * 100,
            'Expiration': ['2025-01-17', '2025-02-21', '2025-03-21'] * 100
        })

    df = load_data()

    # Display with pagination
    paginated_dataframe(
        df,
        rows_per_page=50,
        key="options_scanner",
        column_config={
            "Premium": st.column_config.NumberColumn(
                "Premium",
                format="$%.2f"
            )
        }
    )
```

### Example 4: py_vollib Greeks Calculation

**File:** `src/options/greeks_calculator.py`

```python
"""
Options Greeks Calculator using py_vollib
Faster and more accurate than mibian
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

# Import py_vollib
from py_vollib.black_scholes import black_scholes
from py_vollib.black_scholes.greeks import analytical
from py_vollib.black_scholes.implied_volatility import implied_volatility

# For vectorized operations (even faster)
try:
    from py_vollib_vectorized import vectorized_black_scholes, vectorized_implied_volatility
    VECTORIZED_AVAILABLE = True
except ImportError:
    VECTORIZED_AVAILABLE = False


@dataclass
class OptionContract:
    """Represents an options contract"""
    symbol: str
    strike: float
    expiration: str  # YYYY-MM-DD
    option_type: str  # 'c' for call, 'p' for put
    underlying_price: float
    risk_free_rate: float = 0.05
    dividend_yield: float = 0.0


@dataclass
class GreeksResult:
    """Greeks calculation result"""
    price: float
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float
    implied_volatility: Optional[float] = None


class GreeksCalculator:
    """High-performance Greeks calculator using py_vollib"""

    def __init__(self, risk_free_rate: float = 0.05):
        self.risk_free_rate = risk_free_rate

    def calculate_time_to_expiry(self, expiration: str) -> float:
        """
        Calculate time to expiration in years

        Args:
            expiration: Expiration date in YYYY-MM-DD format

        Returns:
            Time to expiry in years
        """
        exp_date = datetime.strptime(expiration, "%Y-%m-%d")
        today = datetime.now()
        days = (exp_date - today).days
        return max(days / 365.0, 0.001)  # Minimum 0.001 to avoid division by zero

    def calculate_greeks(
        self,
        contract: OptionContract,
        implied_vol: float
    ) -> GreeksResult:
        """
        Calculate all Greeks for a single contract

        Args:
            contract: Option contract details
            implied_vol: Implied volatility (as decimal, e.g., 0.25 for 25%)

        Returns:
            GreeksResult with all calculated Greeks
        """
        flag = contract.option_type.lower()
        S = contract.underlying_price
        K = contract.strike
        t = self.calculate_time_to_expiry(contract.expiration)
        r = contract.risk_free_rate
        sigma = implied_vol

        # Calculate option price
        price = black_scholes(flag, S, K, t, r, sigma)

        # Calculate Greeks (analytical - fastest method)
        delta = analytical.delta(flag, S, K, t, r, sigma)
        gamma = analytical.gamma(flag, S, K, t, r, sigma)
        theta = analytical.theta(flag, S, K, t, r, sigma)
        vega = analytical.vega(flag, S, K, t, r, sigma)
        rho = analytical.rho(flag, S, K, t, r, sigma)

        return GreeksResult(
            price=price,
            delta=delta,
            gamma=gamma,
            theta=theta / 365.0,  # Convert to daily theta
            vega=vega / 100.0,  # Convert to vega per 1% move
            rho=rho / 100.0,  # Convert to rho per 1% move
            implied_volatility=implied_vol
        )

    def calculate_implied_volatility(
        self,
        contract: OptionContract,
        market_price: float
    ) -> float:
        """
        Calculate implied volatility from market price

        Args:
            contract: Option contract details
            market_price: Current market price of the option

        Returns:
            Implied volatility (as decimal)
        """
        flag = contract.option_type.lower()
        S = contract.underlying_price
        K = contract.strike
        t = self.calculate_time_to_expiry(contract.expiration)
        r = contract.risk_free_rate

        try:
            iv = implied_volatility(market_price, S, K, t, r, flag)
            return iv
        except Exception as e:
            # If calculation fails, return None or a default value
            return None

    def analyze_contract_with_price(
        self,
        contract: OptionContract,
        market_price: float
    ) -> GreeksResult:
        """
        Complete analysis: calculate IV from price, then all Greeks

        Args:
            contract: Option contract details
            market_price: Current market price

        Returns:
            Complete Greeks analysis
        """
        # First calculate implied volatility
        iv = self.calculate_implied_volatility(contract, market_price)

        if iv is None:
            # Use a default IV if calculation fails
            iv = 0.25

        # Then calculate all Greeks
        greeks = self.calculate_greeks(contract, iv)
        greeks.implied_volatility = iv

        return greeks

    def batch_calculate_greeks(
        self,
        contracts: List[OptionContract],
        implied_vols: List[float]
    ) -> pd.DataFrame:
        """
        Calculate Greeks for multiple contracts (vectorized if available)

        Args:
            contracts: List of option contracts
            implied_vols: List of implied volatilities

        Returns:
            DataFrame with all contracts and their Greeks
        """
        if not VECTORIZED_AVAILABLE or len(contracts) < 10:
            # Use standard calculation for small batches
            results = []
            for contract, iv in zip(contracts, implied_vols):
                greeks = self.calculate_greeks(contract, iv)
                results.append({
                    'symbol': contract.symbol,
                    'strike': contract.strike,
                    'expiration': contract.expiration,
                    'type': contract.option_type,
                    'price': greeks.price,
                    'delta': greeks.delta,
                    'gamma': greeks.gamma,
                    'theta': greeks.theta,
                    'vega': greeks.vega,
                    'rho': greeks.rho,
                    'iv': greeks.implied_volatility
                })

            return pd.DataFrame(results)

        else:
            # Use vectorized calculation (much faster for large batches)
            flags = np.array([c.option_type.lower() for c in contracts])
            S = np.array([c.underlying_price for c in contracts])
            K = np.array([c.strike for c in contracts])
            t = np.array([self.calculate_time_to_expiry(c.expiration) for c in contracts])
            r = np.array([c.risk_free_rate for c in contracts])
            sigma = np.array(implied_vols)

            # Vectorized calculations
            prices = vectorized_black_scholes(flags, S, K, t, r, sigma, return_as='numpy')

            # Note: py_vollib_vectorized may not have vectorized Greeks yet
            # Fall back to individual calculations for Greeks
            results = []
            for i, contract in enumerate(contracts):
                greeks = self.calculate_greeks(contract, implied_vols[i])
                results.append({
                    'symbol': contract.symbol,
                    'strike': contract.strike,
                    'expiration': contract.expiration,
                    'type': contract.option_type,
                    'price': prices[i],
                    'delta': greeks.delta,
                    'gamma': greeks.gamma,
                    'theta': greeks.theta,
                    'vega': greeks.vega,
                    'rho': greeks.rho,
                    'iv': greeks.implied_volatility
                })

            return pd.DataFrame(results)


# Usage example
if __name__ == "__main__":
    calculator = GreeksCalculator(risk_free_rate=0.05)

    # Single contract analysis
    contract = OptionContract(
        symbol="AAPL",
        strike=150.0,
        expiration="2025-02-21",
        option_type="c",
        underlying_price=155.0,
        risk_free_rate=0.05
    )

    # From market price (calculates IV automatically)
    greeks = calculator.analyze_contract_with_price(contract, market_price=8.50)

    print(f"Price: ${greeks.price:.2f}")
    print(f"Delta: {greeks.delta:.4f}")
    print(f"Gamma: {greeks.gamma:.4f}")
    print(f"Theta: {greeks.theta:.4f} (daily)")
    print(f"Vega: {greeks.vega:.4f}")
    print(f"Rho: {greeks.rho:.4f}")
    print(f"IV: {greeks.implied_volatility*100:.2f}%")

    # Batch calculation
    contracts = [
        OptionContract("AAPL", 145.0, "2025-02-21", "c", 155.0),
        OptionContract("AAPL", 150.0, "2025-02-21", "c", 155.0),
        OptionContract("AAPL", 155.0, "2025-02-21", "c", 155.0),
        OptionContract("AAPL", 160.0, "2025-02-21", "c", 155.0),
    ]

    ivs = [0.25, 0.25, 0.25, 0.25]

    df = calculator.batch_calculate_greeks(contracts, ivs)
    print("\nBatch Greeks:")
    print(df.to_string())
```

---

## Summary of Recommendations

### Immediate Actions (This Week)
1. Replace yfinance → yahooquery
2. Add connection pooling to psycopg2
3. Implement pagination in scanner pages

### Short-term Actions (1-2 Weeks)
4. Migrate mibian → py-vollib-vectorized
5. Implement RunnableWithFallbacks in LLM manager
6. Add asyncpg for high-volume queries

### Long-term Actions (1-2 Months)
7. Evaluate Polygon.io for production data
8. Complete SQLAlchemy 2.0 + asyncpg migration
9. Add optionlab for multi-leg strategy analysis

### Optional Enhancements
10. TA-Lib (if processing 10,000+ rows regularly)
11. OptionGreeksGPU (if scanning 1000+ contracts simultaneously)

---

## References

1. LangChain Documentation: https://python.langchain.com/
2. vollib Documentation: https://vollib.org/
3. asyncpg Documentation: https://magicstack.github.io/asyncpg/
4. Streamlit Documentation: https://docs.streamlit.io/
5. SQLAlchemy 2.0 Documentation: https://docs.sqlalchemy.org/en/20/
6. Polygon.io API: https://polygon.io/docs
7. GitHub - langchain-trading-agents: https://github.com/aitrados/langchain-trading-agents
8. GitHub - optionlab: https://github.com/rgaveiga/optionlab

---

**Document Version:** 1.0
**Last Updated:** 2025-01-21
**Author:** Python Pro Agent
**Status:** Research Complete - Ready for Implementation
