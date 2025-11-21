# 🚀 Quick Start - AVA Enhanced Chatbot

## Launch the Enhanced Chatbot

### Option 1: Default Port
```bash
streamlit run ava_chat_enhanced.py
```
Opens at: **http://localhost:8501**

### Option 2: Custom Port (Recommended if dashboard is running)
```bash
streamlit run ava_chat_enhanced.py --server.port 8504
```
Opens at: **http://localhost:8504**

### Option 3: Headless Mode (Background)
```bash
streamlit run ava_chat_enhanced.py --server.headless=true
```

## Currently Running

✅ **Main Dashboard**: http://localhost:8503
✅ **Enhanced Chatbot**: http://localhost:8504

## Features to Try

### 1. Quick Actions
Click these buttons for instant queries:
- 📊 **Portfolio** - Check portfolio status
- 📈 **Analyze** - Analyze watchlists
- 💡 **Help** - See what AVA can do
- 🔍 **About** - Learn about AVA

### 2. Chat with AVA
Type natural language questions like:
- "What is my portfolio status?"
- "Analyze my watchlist"
- "Show me trading opportunities"
- "What can you help me with?"
- "Tell me about the wheel strategy"

### 3. Use the Sidebar
- View online status
- Check session statistics
- Clear chat history
- Export conversation
- Adjust settings

## What AVA Can Do

### Portfolio Management
```
"Show my portfolio"
"What's my current balance?"
"How are my positions performing?"
```

### Position Analysis
```
"Analyze my positions"
"Should I roll this position?"
"What are my Greeks?"
```

### Trading Opportunities
```
"Find CSP opportunities"
"Show covered call candidates"
"Analyze calendar spreads"
```

### Watchlist Analysis
```
"Analyze my watchlist"
"Rank stocks by strategy"
"What's the best opportunity?"
```

### General Help
```
"What can you do?"
"How does the wheel strategy work?"
"Tell me about AVA"
```

## Tips for Best Results

### 1. Be Specific
❌ "Check stocks"
✅ "Analyze my TradingView watchlist for CSP opportunities"

### 2. Follow Up
AVA remembers context, so you can have natural conversations:
```
You: "Analyze my watchlist"
AVA: "Which watchlist would you like me to analyze?"
You: "The tech stocks one"
```

### 3. Use Quick Actions
The buttons are pre-configured for common queries - fastest way to get started!

### 4. Export Your Chats
Save important conversations using the "📥 Export Chat" button in the sidebar.

## Keyboard Shortcuts

- **Enter** - Send message
- **Clear Chat** - Reset conversation
- **Export** - Download chat history

## UI Tour

### Header
- AVA's beautiful avatar
- Welcome message
- Platform tagline

### Quick Actions
- One-click common queries
- Instant responses
- No typing needed

### Chat Area
- Scrollable message history
- Color-coded bubbles (purple=you, blue=AVA)
- Timestamps and context

### Input Area
- Text input field
- Send button
- Clean, modern design

### Sidebar
- Status indicator (green=online)
- Session statistics
- Settings toggles
- Action buttons

## Troubleshooting

### Chatbot won't start
```bash
# Check if port is available
netstat -ano | findstr "8504"

# Use different port
streamlit run ava_chat_enhanced.py --server.port 8505
```

### Avatar not showing
```bash
# Check if image exists
dir assets\ava\ava_main.jpg

# If missing, copy from source
python -c "import shutil; from pathlib import Path; Path('assets/ava').mkdir(parents=True, exist_ok=True); shutil.copy(r'C:\Code\Legion\docs\ava\pics\AvaNewTry.jpg', r'assets\ava\ava_main.jpg')"
```

### Slow responses
- First message takes longer (loading embeddings)
- Subsequent messages are faster
- Using Groq free tier (30 calls/min limit)

### No LLM response
- Check internet connection
- Verify API keys in `.env`
- LLM service auto-selects best available provider

## Advanced Usage

### Running Multiple Instances
```bash
# Terminal 1 - Main dashboard
streamlit run dashboard.py --server.port 8503

# Terminal 2 - Enhanced chatbot
streamlit run ava_chat_enhanced.py --server.port 8504

# Terminal 3 - Original chatbot (if needed)
streamlit run ava_chatbot_page.py --server.port 8505
```

### Customizing Theme
Edit the CSS in `ava_chat_enhanced.py` to change colors:
```python
# Line 40-250: CSS styling
# Change gradient colors, bubble styles, etc.
```

### Adding Custom Quick Actions
Edit around line 186 in `ava_chat_enhanced.py`:
```python
quick_actions = [
    ("📊 Portfolio", "Show my portfolio status"),
    ("📈 Analyze", "Analyze my watchlist"),
    ("💡 Help", "What can you help me with?"),
    ("🔍 About", "Tell me about AVA"),
    # Add your custom actions here:
    ("🎯 Your Action", "Your query here")
]
```

## Next Steps

1. ✅ **Try the enhanced chatbot** - Open http://localhost:8504
2. 🎯 **Test quick actions** - Click all four buttons
3. 💬 **Have a conversation** - Type natural language queries
4. 📊 **Check sidebar** - Explore settings and stats
5. 📥 **Export a chat** - Save your conversation
6. 🎨 **Customize** - Modify colors and style to your preference

## Integration with Main Dashboard

The enhanced chatbot works alongside the main dashboard:
- Same AVA backend (NLP handler)
- Shared conversation memory
- Access to all platform features
- Can be embedded in dashboard later

## Performance Expectations

- **Initial Load**: 5-10 seconds (embedding model)
- **First Response**: 40-50 seconds (RAG initialization)
- **Subsequent Responses**: 2-3 seconds (cached)
- **UI Rendering**: < 1 second

## Support

If you encounter issues:
1. Check `AVA_CHATBOT_ENHANCEMENT_COMPLETE.md` for details
2. Review console for error messages
3. Verify all dependencies are installed
4. Ensure PostgreSQL is running (for data access)

---

**Ready to chat with AVA? Open http://localhost:8504 now!** 🚀
