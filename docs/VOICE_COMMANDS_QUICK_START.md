# Voice Commands Quick Start

Get started with hands-free AVA interaction in under 5 minutes.

---

## Installation

**Requirements:**
- Chrome or Edge browser (for Web Speech API)
- Microphone access

**Optional (for offline wake word detection):**
```bash
pip install pvporcupine
```

Get free access key at https://console.picovoice.ai/

---

## Basic Usage

### 1. Open AVA Chatbot

Navigate to **AVA Chatbot** page

### 2. Click Voice Button

Look for the **🎤 Voice Commands** button in the chat interface

### 3. Speak Your Command

**Option A: Direct Command (No Wake Word)**
- Click the voice button
- Speak your command immediately
- Example: "Show my portfolio"

**Option B: With Wake Word**
- Click the voice button
- Say "Hey AVA"
- Then say your command
- Example: "Hey AVA, what's the price of Apple"

---

## Quick Command Reference

### Most Common Commands

| What You Want | Say This |
|---------------|----------|
| See portfolio | "Show my portfolio" |
| Check balance | "What's my balance" |
| Get stock price | "What's the price of [ticker]" |
| Analyze stock | "Analyze [ticker]" |
| Find trades | "Find options opportunities" |
| Go to page | "Go to dashboard" |
| Get help | "What can you do" |

### Portfolio Commands

```
"Show my portfolio"
"What's my balance"
"How did I do today"
"Show my positions"
```

### Market Data Commands

```
"What's the price of Apple"
"How's Tesla doing"
"Show NVDA chart"
"How's the market"
```

### Analysis Commands

```
"Analyze Apple"
"What should I do with Tesla"
"Find options opportunities"
"Show me the best trades"
```

### Navigation Commands

```
"Go to dashboard"
"Open options page"
"Switch to positions"
"Show calendar spreads"
```

---

## Configuration

### Change Wake Word

1. Open **Settings** in sidebar
2. Scroll to **Voice Settings**
3. Select wake word:
   - "Hey AVA" (default, recommended)
   - "Magnus"
   - "Computer"
   - "Assistant"

### Enable Voice Feedback

Have AVA speak responses aloud:

1. Open **Voice Settings**
2. Enable "Voice Responses"
3. Adjust speed and pitch to your preference

### Adjust Sensitivity

If wake word triggers too often (or not enough):

1. Open **Voice Settings**
2. Adjust "Wake Word Sensitivity"
   - **0.3-0.4**: Lenient (easier to trigger)
   - **0.5**: Balanced (default)
   - **0.6-0.7**: Strict (fewer false positives)

---

## Troubleshooting

### Microphone Not Working

✅ **Check browser permissions** - Allow microphone access when prompted
✅ **Verify system microphone** - Test in system settings
✅ **Try Chrome or Edge** - Best browser support
✅ **Close other apps** - Ensure no other app is using microphone

### Commands Not Recognized

✅ **Speak clearly** - Direct voice toward microphone
✅ **Use exact phrases** - Check command list
✅ **Try typing command** - Test if command works
✅ **Check transcript** - See what AVA heard

### Voice Feedback Not Working

✅ **Enable in settings** - Turn on "Voice Responses"
✅ **Check browser support** - Chrome/Edge work best
✅ **Unmute volume** - Ensure system volume is on

---

## Examples

### Example 1: Quick Portfolio Check

```
User clicks voice button
User: "Show my portfolio"
AVA: [Displays portfolio on screen]
```

### Example 2: Stock Research

```
User clicks voice button
User: "Hey AVA"
AVA: "I'm listening..."
User: "What's the price of Apple"
AVA: [Shows AAPL quote with price, chart, and key metrics]
```

### Example 3: Find Trading Opportunities

```
User clicks voice button
User: "Find options opportunities"
AVA: [Opens AI Options Agent with top-ranked opportunities]
```

### Example 4: Multi-Step Workflow

```
1. "Show my portfolio"           → View current positions
2. "How's Tesla doing"            → Check TSLA price
3. "Analyze Tesla"                → Open full analysis
4. "Find Tesla options"           → Scan opportunities
```

---

## Tips for Best Results

### 1. Speak Naturally
- Use conversational language
- Don't need to be overly formal
- AVA understands variations

### 2. Be Specific
- Use ticker symbols for stocks
- Specify which page to navigate to
- Include details in requests

### 3. Use Wake Word for Multi-Command Sessions
- Start with "Hey AVA"
- Multiple commands in sequence
- Natural conversation flow

### 4. Check Transcript
- Review what AVA heard
- Adjust speaking if misunderstood
- Learn command variations

### 5. Combine with Typing
- Type complex tickers or numbers
- Voice for common commands
- Hybrid approach is fine

---

## Advanced Features

### Voice Macros (Coming Soon)

Create custom multi-step routines:
```
"Run morning routine"
→ Show market overview
→ Check portfolio
→ Scan opportunities
```

### Multi-Language Support (Coming Soon)

Spanish, French, German, and more:
```
"Muéstrame mi portafolio"  (Spanish)
"Afficher mon portefeuille" (French)
"Zeige mein Portfolio"      (German)
```

### Custom Wake Words (Advanced)

Train your own wake word at https://console.picovoice.ai/
- Download trained `.ppn` file
- Load in voice settings
- Use personalized activation

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + Shift + V` | Activate voice (coming soon) |
| `Esc` | Stop listening |
| `Ctrl + H` | Show voice help |

---

## Privacy & Security

✅ **Browser-based** - Uses your browser's speech recognition
✅ **No recording** - Audio not saved or logged
✅ **Local processing** - With Picovoice, 100% offline
✅ **Confirmation required** - For trading commands
✅ **Disable anytime** - Toggle in settings

---

## Getting Help

### In AVA
Say: **"What can you do"** or **"Help"**

### Documentation
- [Full Voice Command Guide](VOICE_COMMAND_SYSTEM_GUIDE.md)
- [API Reference](VOICE_COMMAND_SYSTEM_GUIDE.md#api-reference)

### Common Issues
- [Troubleshooting](VOICE_COMMAND_SYSTEM_GUIDE.md#troubleshooting)

---

## Next Steps

1. ✅ Try basic commands ("Show portfolio", "Help")
2. ✅ Configure your preferred wake word
3. ✅ Explore advanced commands (analysis, navigation)
4. ✅ Enable voice feedback (optional)
5. ✅ Create custom workflows

---

**Happy trading with voice commands! 🎤**

*Magnus Trading Platform • Voice Commands v1.0*
