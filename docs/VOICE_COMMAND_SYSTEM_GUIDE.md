# Voice Command System Guide

Complete guide for hands-free interaction with AVA using voice commands.

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Wake Word Detection](#wake-word-detection)
4. [Available Commands](#available-commands)
5. [Command Examples](#command-examples)
6. [Configuration](#configuration)
7. [Integration Guide](#integration-guide)
8. [Troubleshooting](#troubleshooting)
9. [Advanced Features](#advanced-features)

---

## Overview

The Magnus Voice Command System enables hands-free interaction with AVA through natural language voice commands. The system consists of:

- **Wake Word Detection**: Activates voice listening ("Hey AVA", "Magnus", etc.)
- **Speech-to-Text**: Converts voice to text using Web Speech API
- **Command Matching**: Pattern-based command recognition
- **Action Execution**: Automated task execution based on voice input
- **Voice Feedback**: Optional text-to-speech responses

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Voice Input (Microphone)              │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│          Wake Word Detection (Picovoice/Browser)         │
│          "Hey AVA", "Magnus", "Computer"                 │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│              Speech-to-Text (Web Speech API)             │
│              Transcript: "show my portfolio"             │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│         Voice Command Handler (Pattern Matching)         │
│         Matches to: show_portfolio command               │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│              Action Execution (AVA System)               │
│              Navigate to dashboard, display data         │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│         Voice Feedback (Optional Text-to-Speech)         │
│         "Displaying your portfolio now"                  │
└─────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Installation

1. **Install Picovoice (Optional - for offline wake word detection)**
   ```bash
   pip install pvporcupine
   ```

2. **Get Picovoice Access Key (Free Tier Available)**
   - Sign up at https://console.picovoice.ai/
   - Copy your access key
   - Add to `.env`:
     ```
     PICOVOICE_ACCESS_KEY=your_key_here
     ```

### Basic Usage

1. **Open AVA Chatbot** (`ava_chatbot_page.py`)

2. **Enable Voice Commands** in sidebar settings

3. **Say the Wake Word**: "Hey AVA"

4. **Speak Your Command**: "Show my portfolio"

5. **AVA Responds** and executes the action

### Browser Compatibility

| Browser | Wake Word | Speech Recognition | Text-to-Speech |
|---------|-----------|-------------------|----------------|
| Chrome  | ✅ Yes     | ✅ Yes             | ✅ Yes          |
| Edge    | ✅ Yes     | ✅ Yes             | ✅ Yes          |
| Safari  | ⚠️ Limited | ⚠️ Limited         | ✅ Yes          |
| Firefox | ❌ No      | ❌ No              | ✅ Yes          |

**Recommended**: Chrome or Edge for full functionality

---

## Wake Word Detection

### Available Wake Words

1. **"Hey AVA"** (Default)
   - Most natural for AVA assistant
   - Maps to "Jarvis" keyword in Picovoice

2. **"Magnus"**
   - Named after the platform
   - Maps to "Computer" keyword

3. **"Computer"**
   - Star Trek style
   - Direct Picovoice keyword

4. **"Assistant"**
   - Generic assistant activation
   - Maps to "Jarvis" keyword

### How Wake Word Detection Works

**Browser-Based (No Picovoice)**:
- Uses pattern matching on transcripts
- Always listening for wake word phrase
- Less accurate but works in any browser with Web Speech API

**Picovoice-Based (Offline)**:
- Hardware-accelerated wake word detection
- Runs locally, no cloud needed
- Highly accurate, low false positives
- Requires access key (free tier: 3 wake words)

### Configuration Example

```python
from src.voice.voice_command_handler import VoiceCommandHandler, WakeWordConfig, WakeWord

# Custom wake word configuration
config = WakeWordConfig(
    wake_word=WakeWord.HEY_AVA,
    sensitivity=0.5,  # 0.0 = lenient, 1.0 = strict
    timeout_seconds=5,  # Listen for 5 seconds after wake word
    confirmation_sound=True,
    visual_feedback=True
)

handler = VoiceCommandHandler(wake_word_config=config)
```

---

## Available Commands

### Portfolio Commands

| Command | Description | Example |
|---------|-------------|---------|
| Show portfolio | Display portfolio overview | "Show my portfolio" |
| Check balance | Current account balance | "What's my balance" |
| View positions | Display all positions | "Show positions" |
| Today's performance | Daily P&L | "How did I do today" |

### Market Data Commands

| Command | Description | Example |
|---------|-------------|---------|
| Get stock price | Current stock quote | "What's the price of Apple" |
| Check performance | How stock is trading | "How's Tesla doing" |
| Show chart | Display stock chart | "Show NVDA chart" |
| Market overview | Indices and futures | "How's the market" |

### Analysis Commands

| Command | Description | Example |
|---------|-------------|---------|
| Analyze stock | Comprehensive analysis | "Analyze Apple" |
| Strategy recommendation | What to do with stock | "What should I do with Tesla" |
| Scan options | Find opportunities | "Find options opportunities" |
| Best trades | Top ranked trades | "Show me the best trades" |

### Trading Commands ⚠️ Requires Confirmation

| Command | Description | Example |
|---------|-------------|---------|
| Buy stock | Purchase shares | "Buy 10 shares of Apple" |
| Sell stock | Sell shares | "Sell 5 shares of Tesla" |
| Place order | Create trade | "Place a cash secured put on AMD" |

### Navigation Commands

| Command | Description | Example |
|---------|-------------|---------|
| Go to page | Navigate to page | "Go to dashboard" |
| Open page | Switch pages | "Open options page" |
| Switch to | Change view | "Switch to positions" |

### Settings Commands

| Command | Description | Example |
|---------|-------------|---------|
| Change personality | Switch AVA mode | "Change personality to analyst" |
| Be more [style] | Adjust tone | "Be more friendly" |
| Enable feature | Turn on setting | "Enable voice feedback" |
| Disable feature | Turn off setting | "Disable notifications" |

### Help Commands

| Command | Description | Example |
|---------|-------------|---------|
| What can you do | List capabilities | "What can you do" |
| Help | Show help | "Help" |
| Show commands | List all commands | "Show commands" |

---

## Command Examples

### Conversational Examples

```
User: "Hey AVA"
AVA:  "I'm listening. What would you like me to do?"

User: "What's the price of Apple?"
AVA:  "Getting quote for AAPL... [displays quote]"

User: "Analyze Tesla"
AVA:  "Analyzing TSLA... [opens analysis page with comprehensive data]"

User: "Find options opportunities"
AVA:  "Scanning for options opportunities... [opens AI Options Agent]"

User: "Go to dashboard"
AVA:  "Navigating to dashboard... [switches page]"

User: "Change personality to analyst"
AVA:  "Switching to analyst mode... [updates personality]"
```

### Multi-Step Workflows

**Workflow 1: Research & Trade**
```
1. "Hey AVA"
2. "What's the price of NVDA"       → Shows quote
3. "Analyze NVDA"                   → Opens analysis
4. "Find NVDA options"              → Scans opportunities
5. "Buy 100 shares of NVDA"         → Confirmation dialog
6. "Confirm"                        → Executes trade
```

**Workflow 2: Portfolio Review**
```
1. "Hey AVA"
2. "Show my portfolio"              → Displays portfolio
3. "How did I do today"             → Shows daily P&L
4. "What are my positions"          → Lists all positions
5. "Show me TSLA chart"             → Displays TSLA chart
```

---

## Configuration

### Voice Settings UI

Access voice settings in the AVA chatbot sidebar:

```python
from src.voice.streamlit_voice_commands import create_voice_settings

# In sidebar
with st.sidebar:
    st.divider()
    create_voice_settings()
```

### Settings Options

1. **Wake Word**
   - Choose: Hey AVA, Magnus, Computer, Assistant
   - Default: Hey AVA

2. **Sensitivity**
   - Range: 0.0 (lenient) to 1.0 (strict)
   - Default: 0.5
   - Higher = fewer false positives, may miss some activations

3. **Command Timeout**
   - Range: 3-30 seconds
   - Default: 5 seconds
   - How long to listen after wake word

4. **Confirmation Sound**
   - Play beep when wake word detected
   - Default: Enabled

5. **Visual Feedback**
   - Show listening indicator
   - Default: Enabled

6. **Voice Responses** (Text-to-Speech)
   - AVA speaks responses aloud
   - Default: Disabled
   - Voice speed: 0.5x to 2.0x
   - Voice pitch: 0.5 to 2.0

### Configuration File

Settings are saved to `config/voice_commands.yaml`:

```yaml
wake_word: hey_ava
sensitivity: 0.5
timeout: 5
confirmation_sound: true
visual_feedback: true
enable_tts: false
voice_speed: 1.0
voice_pitch: 1.0
```

---

## Integration Guide

### Add Voice Commands to Any Page

```python
from src.voice.streamlit_voice_commands import create_voice_command_interface, handle_voice_command_action

# Define callback for command execution
def on_command_executed(result):
    handle_voice_command_action(result)

# Create voice interface
result = create_voice_command_interface(
    key_prefix="my_page_voice_",
    on_command=on_command_executed,
    show_history=True,
    show_help=True
)

# Check for specific actions
if result and result.get("action") == "analyze_stock":
    ticker = result.get("ticker")
    st.write(f"Analyzing {ticker}...")
    # Perform analysis
```

### Compact Sidebar Button

```python
from src.voice.streamlit_voice_commands import create_compact_voice_button

with st.sidebar:
    voice_input = create_compact_voice_button()

    if voice_input:
        st.write(f"You said: {voice_input}")
```

### Custom Command Handler

```python
from src.voice.voice_command_handler import VoiceCommandHandler, CommandPattern, CommandCategory

handler = VoiceCommandHandler()

# Add custom command pattern
custom_pattern = CommandPattern(
    category=CommandCategory.ANALYSIS,
    patterns=[r"backtest (.+) strategy"],
    handler="backtest_strategy",
    description="Backtest a trading strategy",
    examples=["Backtest wheel strategy"],
    requires_parameter=True,
    parameter_type="strategy_name"
)

# Process command
result = handler.process_voice_input("Hey AVA, backtest wheel strategy")
```

---

## Troubleshooting

### Microphone Not Working

**Issue**: No voice input detected

**Solutions**:
1. Check browser permissions (allow microphone access)
2. Verify microphone is working in system settings
3. Try a different browser (Chrome/Edge recommended)
4. Check if another app is using the microphone

### Wake Word Not Detecting

**Issue**: Wake word doesn't activate listening

**Solutions**:
1. Lower sensitivity in settings (0.3 - 0.4)
2. Speak clearly and directly into microphone
3. Check Picovoice access key is set correctly
4. Try different wake word
5. Use browser-based detection (fallback)

### Commands Not Recognized

**Issue**: AVA doesn't understand command

**Solutions**:
1. Say "Help" to see available commands
2. Speak clearly and use exact command phrases
3. Check command history for transcript accuracy
4. Try typing command to test pattern matching

### Voice Feedback Not Working

**Issue**: AVA doesn't speak responses

**Solutions**:
1. Enable "Voice Responses" in settings
2. Check browser supports Web Speech API
3. Verify volume is not muted
4. Try different browser (Chrome/Edge work best)

### Performance Issues

**Issue**: Slow response or lag

**Solutions**:
1. Disable voice feedback if not needed
2. Clear command history periodically
3. Use wake word detection to reduce processing
4. Check network connection (some features use cloud STT)

---

## Advanced Features

### Multi-Language Support

The Web Speech API supports 100+ languages. To add language support:

```javascript
recognition.lang = 'es-ES';  // Spanish
recognition.lang = 'fr-FR';  // French
recognition.lang = 'de-DE';  // German
```

### Custom Wake Words (Picovoice)

Train custom wake words at https://console.picovoice.ai/:

1. Go to "Wake Word" section
2. Click "Train Custom Wake Word"
3. Enter wake word phrase (e.g., "Trading Assistant")
4. Download `.ppn` file
5. Load in code:

```python
import pvporcupine

porcupine = pvporcupine.create(
    access_key=access_key,
    keyword_paths=['path/to/custom_wake_word.ppn']
)
```

### Voice Macros

Create multi-step voice macros:

```python
# Define macro
VOICE_MACROS = {
    "morning routine": [
        "show market overview",
        "check my portfolio",
        "scan for options opportunities"
    ],
    "weekly review": [
        "show portfolio performance",
        "analyze top positions",
        "check upcoming earnings"
    ]
}

# Execute macro
if command_text == "run morning routine":
    for cmd in VOICE_MACROS["morning routine"]:
        handler.process_voice_input(f"Hey AVA, {cmd}")
```

### Voice Analytics

Track voice command usage:

```python
stats = handler.get_statistics()

# Returns:
{
    "total_commands": 145,
    "success_rate": 87.5,
    "most_used_command": "portfolio",
    "commands_by_category": {
        "portfolio": 45,
        "market_data": 32,
        "analysis": 28,
        # ...
    }
}
```

### Integration with AVA Agents

Voice commands can trigger AVA agents:

```python
# When voice command detected
if result.get("action") == "analyze_stock":
    ticker = result.get("ticker")

    # Trigger AVA's Options Strategy Agent
    from src.ava.core.agent_orchestrator import get_orchestrator

    orchestrator = get_orchestrator()
    response = orchestrator.process_message(
        f"Analyze options strategies for {ticker}"
    )

    st.write(response)
```

---

## Performance Metrics

### Response Time Benchmarks

| Operation | Time | Notes |
|-----------|------|-------|
| Wake word detection | < 100ms | Picovoice hardware accelerated |
| Speech-to-text | 500-1000ms | Depends on phrase length |
| Command matching | < 50ms | Regex pattern matching |
| Action execution | 100-2000ms | Depends on action complexity |
| **Total** | **~1-3 seconds** | End-to-end response time |

### Accuracy Metrics

| Metric | Rate | Notes |
|--------|------|-------|
| Wake word detection | 95%+ | Picovoice in quiet environment |
| Speech transcription | 90%+ | Web Speech API, clear speech |
| Command recognition | 85%+ | Pattern matching with variations |
| **Overall accuracy** | **80%+** | Combined pipeline |

---

## Security Considerations

### Privacy

- **Browser-based STT**: Audio sent to Google/Microsoft cloud
- **Picovoice**: Fully offline, runs on device
- **No recording**: Audio not saved or logged
- **Transcript logging**: Only successful commands logged locally

### Safety Features

1. **Confirmation Required**: Trading commands require verbal/tap confirmation
2. **Wake Word**: Prevents accidental activation
3. **Timeout**: Listening automatically stops after timeout
4. **Command History**: Review all executed commands
5. **Disable Anytime**: Toggle voice commands on/off

### Best Practices

1. Use Picovoice for offline wake word detection
2. Enable voice feedback only in private spaces
3. Review command history regularly
4. Use confirmation for critical actions
5. Set appropriate sensitivity (0.4-0.6 recommended)

---

## Future Enhancements

### Planned Features

1. **Multi-Language Support**
   - Spanish, French, German, Mandarin
   - Language auto-detection

2. **Natural Language Understanding**
   - Intent classification with ML models
   - Context-aware command interpretation
   - Follow-up questions without wake word

3. **Voice Biometrics**
   - Speaker verification
   - User-specific settings
   - Security authentication

4. **Offline Speech Recognition**
   - On-device STT (Vosk, Whisper)
   - No internet required
   - Privacy-first approach

5. **Voice Command Builder**
   - GUI to create custom commands
   - Regex pattern wizard
   - Test command matching

6. **Advanced Macros**
   - Conditional logic
   - Variables and parameters
   - Scheduled voice routines

---

## API Reference

### VoiceCommandHandler

```python
class VoiceCommandHandler:
    def __init__(self, wake_word_config: Optional[WakeWordConfig] = None)

    def process_voice_input(self, transcript: str) -> Dict[str, Any]:
        """Process voice input and execute matched command"""

    def get_command_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent command history"""

    def get_statistics(self) -> Dict[str, Any]:
        """Get voice command usage statistics"""
```

### WakeWordDetector

```python
class WakeWordDetector:
    def __init__(self, wake_word: WakeWord = WakeWord.HEY_AVA)

    def start_listening(self, callback: Callable[[bool], None]):
        """Start listening for wake word"""

    def stop_listening(self):
        """Stop listening for wake word"""
```

### Streamlit Components

```python
def create_voice_command_interface(
    key_prefix: str = "voice_cmd_",
    on_command: Optional[Callable] = None,
    show_history: bool = True,
    show_help: bool = True
) -> Optional[Dict[str, Any]]:
    """Create complete voice command interface"""

def create_voice_settings(key_prefix: str = "voice_settings_"):
    """Create voice command settings panel"""

def create_compact_voice_button(key_prefix: str = "compact_voice_") -> Optional[str]:
    """Create compact voice button for sidebar"""
```

---

## Support

### Getting Help

1. **Say "Help"**: Voice command to show available commands
2. **Documentation**: This guide
3. **Command History**: Review past commands and transcripts
4. **Test Mode**: Type commands to test without voice

### Reporting Issues

Include in bug reports:
- Browser and version
- Microphone type
- Wake word used
- Command transcript
- Error message (if any)
- Expected vs actual behavior

---

**Voice Command System v1.0** • Magnus Trading Platform
