# AVA Natural Language - Quick Start Guide

## ✅ What's New

AVA Telegram bot now understands **natural language**! You can ask questions conversationally instead of using slash commands.

---

## 🚀 How to Use

### 1. Start AVA Bot

```bash
cd c:\Code\WheelStrategy
python src/ava/telegram_bot_enhanced.py
```

### 2. Open Telegram and Ask Questions Naturally

**Instead of:**
```
/portfolio
/positions
/opportunities
```

**Just ask:**
```
"How's my portfolio?"
"What positions do I have?"
"Show me the best opportunities"
"Are there any good trades?"
"What are you working on?"
```

---

## 💬 Example Conversations

### Portfolio Query:
```
You: "How's my portfolio doing?"
AVA: 📊 Sure Adam, let me get your portfolio...
     [Shows portfolio with balance and performance]
```

### Position Query:
```
You: "What trades do I have open?"
AVA: 📋 Checking your positions Adam...
     [Shows all active options positions]
```

### Opportunity Query:
```
You: "Any good plays right now?"
AVA: 🎯 Finding the best opportunities for you...
     [Shows top CSP opportunities]
```

### Help Query:
```
You: "What can you do?"
AVA: 📚 Here's what I can do...
     [Shows full help with natural language examples]
```

---

## 🎯 What AVA Understands

| What You Want | Say This | AVA Does |
|---------------|----------|----------|
| Portfolio | "How's my portfolio?", "What's my balance?" | Shows portfolio |
| Positions | "What positions?", "My trades?", "Show positions" | Shows positions |
| Opportunities | "Good trades?", "Best plays?", "Opportunities?" | Shows CSPs |
| TradingView | "TradingView", "Charts", "Watchlists" | Shows TradingView |
| Xtrades | "Xtrades", "Who am I following?", "Signals" | Shows Xtrades |
| Tasks | "What are you doing?", "Your tasks?" | Shows tasks |
| Status | "Are you online?", "System status" | Shows status |
| Help | "Help", "What can you do?", "Commands" | Shows help |

---

## 💰 Cost

**$0.00/month** - Uses your existing FREE Groq/Gemini/DeepSeek infrastructure!

---

## 🔧 Technical Details

**How it works:**
1. You send a natural language message
2. AVA uses FREE LLM (Groq) to detect your intent
3. Routes to appropriate command
4. Returns results conversationally

**Powered by:**
- ✅ Groq (FREE, Llama 3.1 70B)
- ✅ Gemini (FREE fallback)
- ✅ DeepSeek (ultra cheap fallback)
- ✅ Your existing LLM service

---

## 📁 Files Changed

1. **Created:** `src/ava/nlp_handler.py` (260 lines) - Natural language understanding
2. **Modified:** `src/ava/telegram_bot_enhanced.py` (~100 lines) - Integrated NLP

---

## ✅ Status

**Production Ready** - Just start the bot and ask questions naturally! 🎉

---

**Implementation:** November 10, 2025
**Cost:** $0.00/month
**Status:** ✅ Ready to use
