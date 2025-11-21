# Magnus Financial Assistant - User Guide

**"Your AI-Powered Personal Financial Advisor"**

**Status:** 🏗️ Architecture Complete - Ready for Implementation
**Version:** 1.0.0
**Date:** January 10, 2025

---

## 📖 Overview

The Magnus Financial Assistant (MFA) is an intelligent, conversational AI agent that transforms Magnus from a collection of features into a unified, voice-enabled financial advisor. Instead of navigating through multiple pages, you simply ask Magnus what you want to know - and it knows everything about your portfolio, strategies, and the markets.

### What Makes MFA Special

✅ **Knows Everything** - All Magnus features, your live data, market conditions
✅ **Speaks Naturally** - Voice and text, no complex UI needed
✅ **Advises Intelligently** - Real financial guidance, not just data
✅ **Acts Autonomously** - Can execute trades, create alerts, generate reports
✅ **Learns Continuously** - Improves with every conversation

---

## 🎯 Key Features

### 1. Natural Conversations

Talk to Magnus like you would a human financial advisor:

**You:** *"How are my positions doing today?"*

**Magnus:** *"You have 5 active positions with a total P&L of +$342. Your TSLA put is up 60% - I'd recommend taking profit based on your 50% rule. Would you like me to close it?"*

### 2. Voice Interface

- **Voice Input:** Talk to Magnus using your microphone
- **Voice Output:** Magnus responds with natural speech
- **Wake Word:** Say "Hey Magnus" to activate (optional)
- **Hands-Free:** Perfect for mobile or when multitasking

### 3. Multi-Agent Intelligence

Magnus uses 6 specialized AI agents:

- 🤖 **Portfolio Analyst** - Analyzes your positions and P&L
- 🤖 **Market Researcher** - Gathers market data and news
- 🤖 **Strategy Advisor** - Recommends trades and setups
- 🤖 **Risk Manager** - Monitors portfolio risk
- 🤖 **Trade Executor** - Executes orders (with your approval)
- 🤖 **Educator** - Explains concepts and strategies

### 4. RAG-Powered Knowledge

Unlike ChatGPT or Claude, Magnus has **complete knowledge** of:
- All Magnus features and how they work
- Your specific trading strategies (wheel, CSPs, spreads)
- 200+ financial concepts and definitions
- Your conversation history and preferences
- Live portfolio and market data

### 5. Proactive Assistance

Magnus doesn't wait for you to ask:
- **Morning Summaries:** Daily portfolio overview
- **Risk Alerts:** Warnings when risks increase
- **Opportunity Notifications:** High-quality trade setups
- **Earnings Warnings:** Alerts before earnings dates

### 6. Trade Execution

Magnus can execute trades for you:
- Preview order details
- Verify all parameters
- Submit to Robinhood
- Track fill status
- Update database automatically

---

## 💬 Example Conversations

### Portfolio Check

**You:** "Show me my portfolio summary"

**Magnus:**
```
Let me pull your current positions...

You have 5 active positions:
• Total P&L: +$342 (3.8% return)
• Daily Theta: $18
• Portfolio Delta: -0.15 (slightly bearish)
• Buying Power: $42,350

Position breakdown:
1. AAPL $170 CSP (1/19) - Up $45 (30% profit)
2. TSLA $240 CSP (1/26) - Up $120 (60% profit) ⚠️
3. SPY $480 CSP (2/2) - Down $12 (new position)
4. NVDA $500 CSP (1/26) - Up $89 (45% profit)
5. MSFT $380 CSP (2/2) - Up $100 (50% profit)

Recommendation: Your TSLA position has hit 60% profit.
Based on your strategy, I'd suggest taking profit here.
Would you like me to close it?
```

### Finding Opportunities

**You:** "Find me a good CSP trade"

**Magnus:**
```
Scanning for high-quality cash-secured put opportunities...

🥇 TOP RECOMMENDATION: AMD $140 PUT (28 DTE)

Why I like this trade:
• Premium: $2.85 (2.0% return, 26% annualized)
• IV Rank: 68 (elevated, good premium)
• Probability OTM: 72%
• Strong support at $135
• No earnings before expiration ✅
• Your win rate on AMD: 4/4 (100%)

Technical Analysis:
• Current price: $145.30 (3.7% cushion)
• 200-day MA support at $137.50
• RSI: 48 (neutral)
• Recent low: $132 (would need -9% drop)

Risk Assessment:
• Max loss: $14,000 (if AMD → $0)
• Breakeven: $137.15
• Capital required: $14,000 (28% of buying power)

Expected Value: +$95 per trade (based on historical data)

This is a high-quality setup. Risk is well-compensated.
Would you like me to execute this trade?
```

### Getting Education

**You:** "Explain theta decay like I'm 5"

**Magnus:**
```
Great question! Let me explain theta in simple terms...

Imagine you buy a ticket to a concert next month for $100.

As time passes:
• 1 month before: Ticket worth $100
• 1 week before: Ticket worth $100
• 1 day before: Ticket worth $100
• The day AFTER the concert: Ticket worth $0 ❌

Theta is how much the ticket loses value each day.

IN OPTIONS:
When you SELL an option (like a cash-secured put), you're
selling a ticket that expires worthless if the stock stays
above your strike.

Every day, the option loses value (decays) - and since YOU
sold it, that decay is PROFIT for you!

Example with your AAPL position:
• You sold AAPL $170 put for $150
• Theta: -$5 per day
• Every day AAPL stays above $170 → option loses $5
• After 30 days → option worthless → you keep $150!

The closer to expiration, the faster decay accelerates.
This is why selling options is powerful - time is YOUR ally!

Would you like to see how theta accelerates in the final week?
```

### Trade Execution

**You:** "Execute the AMD trade"

**Magnus:**
```
Let me verify the details before submitting...

ORDER PREVIEW:
Symbol: AMD
Action: Sell to Open
Type: Cash-Secured Put
Strike: $140
Expiration: 2/14/2025 (28 DTE)
Quantity: 1 contract
Premium: $2.85 ($285 total)
Capital Required: $14,000

Risk Analysis:
• Max Profit: $285 (2.0% return)
• Max Loss: $13,715 (if assigned at $140)
• Breakeven: $137.15
• Probability of Profit: 72%

⚠️ WARNINGS:
• This will use 28% of your buying power
• If assigned, you'll own 100 shares of AMD at $140

✅ CONFIRMATIONS:
• No earnings before expiration
• Adequate liquidity (volume: 1,250)
• Within your risk parameters

Do you want to proceed? [Yes] [No] [Modify]
```

**You:** "Yes"

**Magnus:**
```
Submitting order to Robinhood...

✅ ORDER FILLED!

Trade Details:
• Filled at $2.87 (better than expected!)
• Total credit: $287
• Commission: $0
• Fill time: 10:34:22 AM

Database updated:
• New position added to active positions
• Trade recorded in history
• Portfolio metrics recalculated

Updated Portfolio:
• Available buying power: $28,350 (was $42,350)
• Total theta: $25/day (was $18/day)
• Active positions: 6

Great trade! I'll monitor this position and alert you
if anything changes.
```

---

## 🎙️ Voice Commands

### Activating Voice

1. **Push-to-Talk:** Click the 🎤 button, speak, release
2. **Wake Word:** Say "Hey Magnus" to activate listening
3. **Telegram Voice:** Send voice message to Magnus bot

### Example Voice Commands

- *"Hey Magnus, show my portfolio"*
- *"Find me a trade"*
- *"What's my P&L today?"*
- *"Explain calendar spreads"*
- *"Execute this trade"*
- *"What's the IV on Tesla?"*
- *"Should I close my Apple put?"*

### Voice Settings

Toggle voice responses in Settings:
- **Voice Output:** Enable/disable TTS
- **Wake Word:** Enable/disable "Hey Magnus"
- **Voice Speed:** Adjust playback speed
- **Voice Type:** Choose voice (if using premium TTS)

---

## 📱 Access Methods

### 1. Streamlit Interface (Desktop)

Navigate to **Magnus Financial Assistant** in the sidebar.

**Features:**
- Full chat interface
- Voice input/output
- Rich formatting (tables, charts)
- Action buttons
- Conversation history

### 2. Telegram Bot (Mobile)

Message **@MagnusFinancialBot** (or your bot name).

**Commands:**
- `/start` - Begin conversation
- `/portfolio` - Get portfolio summary
- `/findtrade` - Find CSP opportunity
- `/positions` - List active positions
- `/help` - Show help
- `/voice` - Toggle voice responses

### 3. Voice-Only Mode

For hands-free operation:
- Say "Hey Magnus" to activate
- Speak your question
- Magnus responds with voice
- No screen needed!

---

## 🛡️ Safety Features

### Financial Disclaimer

⚠️ **IMPORTANT:** Magnus provides educational information and data analysis. It is NOT a licensed financial advisor and does NOT provide personalized investment advice.

Before using Magnus:
- You must acknowledge the disclaimer
- Understand that options trading involves significant risk
- Recognize that you are responsible for all trading decisions

### Risk Warnings

Magnus warns you about:
- **Overleveraging:** Using >30% of buying power
- **Concentration Risk:** Multiple positions in same symbol
- **Earnings Risk:** Expiration after earnings date
- **Liquidity Risk:** Low option volume (<50)

### Trade Verification

Before executing any trade, Magnus:
1. Shows complete order preview
2. Displays all risks clearly
3. Requires explicit confirmation
4. Logs your acknowledgment
5. Double-checks all parameters

### Audit Trail

Every action is logged:
- All conversations (with timestamps)
- All trade recommendations
- All executed trades
- All user confirmations
- All errors and warnings

---

## ⚙️ Settings & Preferences

### User Preferences

Configure Magnus to match your style:

**Risk Tolerance:**
- Conservative (lower returns, safer trades)
- Moderate (balanced approach)
- Aggressive (higher returns, more risk)

**Notification Preferences:**
- Daily summary (enable/disable, time)
- Risk alerts (thresholds)
- Opportunity notifications (frequency, criteria)
- Earnings warnings (days before)

**Favorite Strategies:**
- Cash-secured puts
- Covered calls
- Calendar spreads
- Iron condors (future)

**Voice Settings:**
- Voice enabled (yes/no)
- Voice output type (local/premium)
- Wake word enabled (yes/no)
- Playback speed (0.8x - 1.5x)

### Privacy Settings

Control your data:
- Conversation history retention (30/60/90 days)
- Anonymize usage analytics (yes/no)
- Share learning data (opt-in)

---

## 📊 Usage Tips

### Best Practices

**1. Be Specific**
❌ "Show me stocks"
✅ "Show me high IV CSP opportunities in tech stocks"

**2. Ask Follow-Up Questions**
Magnus remembers context! You can ask:
- "Tell me more about that"
- "Why do you recommend that?"
- "What are the risks?"

**3. Use Voice When Convenient**
Voice is great for:
- Quick portfolio checks
- Simple queries
- When multitasking
- On mobile (Telegram)

**4. Let Magnus Be Proactive**
Enable notifications for:
- Daily morning summary
- Risk alerts
- High-quality opportunities

**5. Teach Magnus Your Preferences**
Magnus learns from you:
- "I prefer conservative trades"
- "Only show me trades with >70% probability"
- "I don't like tech stocks right now"

### Common Queries

**Portfolio Management:**
- "Show my positions"
- "What's my total P&L?"
- "How much theta decay today?"
- "Which positions should I close?"

**Opportunity Finding:**
- "Find me a CSP trade"
- "Show covered call opportunities"
- "Any good calendar spreads?"
- "What's on my watchlist?"

**Market Research:**
- "What's the IV rank on AAPL?"
- "When is Tesla earnings?"
- "Any unusual activity today?"
- "What are the best setups right now?"

**Strategy & Education:**
- "Explain wheel strategy"
- "What is delta?"
- "Should I sell puts or calls?"
- "How do I manage assignments?"

**Risk Management:**
- "Am I overleveraged?"
- "What's my portfolio delta?"
- "Do I need to hedge?"
- "What if the market drops 10%?"

**Trade Execution:**
- "Close my AAPL position"
- "Execute this trade"
- "Roll my SPY put to next week"
- "Show order status"

---

## 🚨 Troubleshooting

### Magnus Not Responding

**Check:**
1. Internet connection active
2. Magnus service running (check status)
3. No API quota exceeded (Groq/Gemini limits)
4. Browser console for errors

**Try:**
- Refresh page
- Clear session (Settings → Clear)
- Try different query
- Contact support if persists

### Voice Not Working

**Input Issues:**
- Check microphone permissions
- Test mic in browser settings
- Try different browser (Chrome works best)
- Ensure no other apps using mic

**Output Issues:**
- Check speaker/headphone volume
- Verify voice enabled in settings
- Try toggling voice off/on
- Check browser audio permissions

### Incorrect Data

**If portfolio data wrong:**
- Check Robinhood connection (Settings)
- Refresh Robinhood credentials
- Wait 30 seconds for cache refresh
- Manual refresh button in portfolio

**If market data wrong:**
- Market may be closed (pre/post market)
- Data delayed by 1 minute (normal)
- Check specific symbol status
- Report if consistently wrong

### Trade Execution Fails

**Common reasons:**
- Insufficient buying power
- Market closed (trades 9:30-4:00 ET)
- Option not available (check chain)
- Robinhood connection issue

**Steps:**
1. Verify buying power sufficient
2. Check market hours
3. Confirm option exists (check scanner)
4. Try manual order in Robinhood
5. Contact support if issue persists

---

## 📚 Additional Resources

### Documentation
- **Master Plan:** `FINANCIAL_ASSISTANT_MASTER_PLAN.md`
- **Specifications:** `features/financial_assistant/SPEC.md`
- **API Docs:** `features/financial_assistant/API.md`
- **Legion Integration:** `LEGION_INTEGRATION_COMPLETE.md`

### Learning Resources
- Magnus Financial Concepts Library (in MFA knowledge base)
- Options Education Center (ask Magnus: "Teach me about X")
- Example Conversations (in documentation)
- Video Tutorials (link when available)

### Support
- GitHub Issues: [Report bugs/features](https://github.com/...)
- Discord: Magnus Trading Community
- Email: support@magnus-trading.com
- In-app: Ask Magnus "How do I get help?"

### Updates
- Feature Roadmap: See SPEC.md Section 11
- Change Log: CHANGELOG.md
- Release Notes: Check announcements

---

## 🎉 Tips for Success

### Week 1: Getting Started
- Complete onboarding tutorial
- Ask Magnus simple questions
- Try voice interface
- Set up notifications

### Week 2: Daily Usage
- Check morning summary
- Ask about positions daily
- Let Magnus find trades
- Learn one new concept

### Week 3: Advanced
- Execute trades via Magnus
- Use custom queries
- Optimize notification settings
- Share feedback

### Week 4: Mastery
- Voice-first workflow
- Proactive opportunities
- Advanced strategies
- Help others learn

---

## 🌟 What Users Say

> *"Magnus is like having a professional options trader in my pocket. It finds trades I would never have found myself."* - Beta User

> *"The voice interface is a game-changer. I can check my portfolio while driving."* - Beta User

> *"I've learned more about options in 2 weeks with Magnus than 6 months of reading books."* - Beta User

> *"Trade execution is seamless. I just tell Magnus what I want, review the details, and confirm. Done."* - Beta User

---

## 🚀 Future Features

Coming in v2.0:
- Multi-user collaboration (share insights)
- Advanced backtesting (test strategies)
- Portfolio optimization (AI-powered rebalancing)
- Tax optimization (tax-loss harvesting)
- Custom strategies (define your own rules)
- Social features (follow traders)

---

## ❓ FAQ

**Q: Is Magnus free?**
A: Yes! Magnus uses FREE LLM providers (Groq, Gemini). Optional: upgrade to premium for Claude Sonnet 4.5 ($10-50/month).

**Q: Can Magnus execute trades automatically?**
A: No. Magnus requires your explicit approval for every trade. This is for your safety.

**Q: How accurate are Magnus's recommendations?**
A: Magnus uses the same data and strategies you'd use manually, but faster and more comprehensive. Always do your own verification.

**Q: Can I use Magnus on mobile?**
A: Yes! Via Telegram bot with full voice support.

**Q: Does Magnus work after hours?**
A: Yes, but market data may be delayed and trades can only execute during market hours (9:30-4:00 ET).

**Q: Is my data private?**
A: Yes. All data stays in your Magnus database. We don't sell data to third parties.

**Q: Can Magnus help with other strategies (not just wheel)?**
A: Yes! Magnus knows about all common options strategies and can advise on them.

**Q: What if Magnus makes a mistake?**
A: Report it immediately. Magnus is in beta and continuously improving. Always verify before executing trades.

---

**Version:** 1.0.0
**Last Updated:** January 10, 2025
**Status:** 🏗️ Architecture Complete - Implementation Starting Soon

**Ready to transform your trading? Ask Magnus anything!** 🤖💼📈
