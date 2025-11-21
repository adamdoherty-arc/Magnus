# Autonomous AI Coding Agents - Quick Reference Guide

**Purpose:** Quick reference for installing and using autonomous AI agents that can write code and manage tasks

**Date:** January 10, 2025

---

## 🚀 Top 5 Autonomous Coding Agents - GitHub Repositories

### **1. Cline (RECOMMENDED)**
```
Repository: https://github.com/cline/cline
Stars: 15K+
Type: VS Code Extension
Install: Search "Cline" in VS Code Extensions
Use Case: Best all-around autonomous coding agent
```

**Quick Start:**
```bash
# 1. Install from VS Code Extensions
# 2. Add API key in Cline settings
# 3. Open Cline panel: Ctrl+Shift+P → "Cline: Open"
# 4. Type: "Add a new Streamlit page for X feature"
```

---

### **2. GPT-Pilot (Pythagora)**
```
Repository: https://github.com/Pythagora-io/gpt-pilot
Stars: 32K+
Type: CLI Tool + VS Code Extension
Install: pip install gpt-pilot OR install Pythagora extension
Use Case: Building complete features from scratch
```

**Quick Start:**
```bash
# CLI Version
pip install gpt-pilot
gpt-pilot

# OR VS Code Extension
# Install "Pythagora" from Extensions
# Click Pythagora icon → "New Project" or "Continue Project"
```

---

### **3. Aider**
```
Repository: https://github.com/Aider-AI/aider
Stars: 25K+
Type: Terminal CLI
Install: pip install aider-chat
Use Case: Best for modifying existing codebases
```

**Quick Start:**
```bash
# Install
pip install aider-chat

# Use with Claude (recommended)
export ANTHROPIC_API_KEY=your_key
aider --model claude-sonnet-4.5

# Or use FREE Groq
export GROQ_API_KEY=your_key
aider --model groq/llama-3.3-70b-versatile

# Example usage
$ aider src/my_file.py
Aider> Add error handling to this function

# Voice mode
aider --voice-language en
```

---

### **4. CrewAI**
```
Repository: https://github.com/crewAIInc/crewAI
Stars: 25K+
Type: Python Framework
Install: pip install crewai crewai-tools
Use Case: Building custom multi-agent development systems
```

**Quick Start:**
```bash
# Install
pip install 'crewai[tools]'

# Create your first crew
from crewai import Agent, Task, Crew, Process
from langchain_groq import ChatGroq

# Define agents
coder = Agent(
    role='Senior Python Developer',
    goal='Write clean, tested Python code',
    backstory='Expert in Python with 10 years experience',
    llm=ChatGroq(model="llama-3.3-70b-versatile")
)

# Define tasks
task = Task(
    description='Add a new feature to calculate RSI indicator',
    agent=coder
)

# Create crew
crew = Crew(agents=[coder], tasks=[task], process=Process.sequential)

# Run
result = crew.kickoff()
```

---

### **5. OpenHands (OpenDevin)**
```
Repository: https://github.com/OpenDevin/OpenDevin
Stars: 25K+
Type: Autonomous software engineering platform
Install: Docker-based or from source
Use Case: Research-grade autonomous development
```

**Quick Start:**
```bash
# Using Docker (easiest)
docker pull ghcr.io/opendevin/opendevin:latest
docker run -it --rm -p 3000:3000 \
  -e ANTHROPIC_API_KEY=your_key \
  ghcr.io/opendevin/opendevin:latest

# Open browser: http://localhost:3000
# Give it a task in the chat interface
```

---

## 🎯 Which One Should You Use?

### **For Quick Testing (Today):**
```
→ Install Cline in VS Code
→ Try it on a small feature
→ See if you like the workflow
```

### **For Serious Development (This Week):**
```
→ Cline (VS Code) for daily coding
→ Aider (terminal) for git-aware edits
→ Keep your AVA bot for mobile monitoring
```

### **For Custom Automation (Long-term):**
```
→ Build custom CrewAI system
→ Integrate with your task management
→ Add voice interface
```

---

## 📋 Feature Comparison - At a Glance

| Feature | Cline | GPT-Pilot | Aider | CrewAI | OpenHands |
|---------|-------|-----------|-------|--------|-----------|
| **Ease of Use** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Code Quality** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Task Breakdown** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Git Integration** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| **Customization** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Speed** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Learning Curve** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |

---

## 🔧 Common Setup: API Keys

All these tools need an LLM API. You can use:

### **Option 1: Claude (Best Quality)**
```bash
# Get key from: https://console.anthropic.com/
export ANTHROPIC_API_KEY=sk-ant-xxx

# Cost: ~$3 per million tokens (~$10-30/month for active development)
```

### **Option 2: Groq (FREE!)**
```bash
# Get FREE key from: https://console.groq.com/
export GROQ_API_KEY=gsk_xxx

# Cost: $0/month (30 requests/minute limit)
# Model: llama-3.3-70b-versatile
```

### **Option 3: OpenAI**
```bash
# Get key from: https://platform.openai.com/
export OPENAI_API_KEY=sk-proj-xxx

# Cost: ~$5 per million tokens
```

### **Option 4: Local (FREE, Private)**
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Download model
ollama pull deepseek-coder:33b

# Use with tools (most support ollama)
export OLLAMA_API_BASE=http://localhost:11434
```

---

## 💬 Adding Voice Control

### **Method 1: Whisper Local (What You Have)**
```python
# You already have this in AVA
import openai
audio_file = open("voice.wav", "rb")
transcription = openai.Audio.transcribe("whisper-1", audio_file)
# Send transcription.text to Cline/Aider
```

### **Method 2: Whisper.cpp (Faster, Local)**
```bash
# Install
git clone https://github.com/ggerganov/whisper.cpp
cd whisper.cpp && make

# Download model
bash ./models/download-ggml-model.sh base.en

# Use
./main -m models/ggml-base.en.bin -f voice.wav > transcription.txt

# Send to agent
aider < transcription.txt
```

### **Method 3: Browser Speech API**
```javascript
// In VS Code webview or browser
const recognition = new webkitSpeechRecognition();
recognition.onresult = (event) => {
  const transcript = event.results[0][0].transcript;
  // Send to Cline API
  cline.executeCommand(transcript);
};
recognition.start();
```

---

## 🎬 Real-World Usage Examples

### **Example 1: Add New Feature with Cline**
```
You: "Create a new page called ai_trade_analyzer_page.py that:
1. Uses our LLM service to analyze options trades
2. Shows AI recommendations in a Streamlit table
3. Follows the same pattern as calendar_spreads_page.py
4. Integrates with our Robinhood data
5. Add it to the dashboard navigation"

Cline will:
✅ Read calendar_spreads_page.py to understand the pattern
✅ Read src/services/llm_service.py to use LLM correctly
✅ Create ai_trade_analyzer_page.py with all components
✅ Update dashboard.py to add navigation link
✅ Show you diffs for each change
✅ Wait for your approval before applying

Time: 2-5 minutes
Your work: Just approve changes
```

### **Example 2: Fix Bug with Aider**
```bash
$ aider src/xtrades_scraper.py

You: "Fix the Chrome driver compatibility issue on line 127"

Aider:
✅ Reads the file and surrounding context
✅ Identifies the webdriver initialization
✅ Updates to use compatible ChromeDriver
✅ Adds error handling
✅ Tests the change
✅ Commits: "fix: Update ChromeDriver for compatibility"

Time: 30 seconds - 2 minutes
```

### **Example 3: Build Complete Feature with GPT-Pilot**
```bash
$ gpt-pilot

GPT-Pilot: "What would you like to build?"

You: "Add real-time options Greeks monitoring with PostgreSQL storage,
live Streamlit dashboard, and Telegram alerts when Greeks hit thresholds"

GPT-Pilot will:
✅ Ask clarifying questions (which Greeks? what thresholds?)
✅ Create database schema (greeks_history table)
✅ Build data fetcher (greeks_fetcher.py)
✅ Create Streamlit page (greeks_monitor_page.py)
✅ Add alert logic (greeks_alerts.py)
✅ Integrate with Telegram bot
✅ Write tests
✅ Run tests and fix failures
✅ Create complete, working feature

Time: 15-30 minutes
Your work: Answer questions, review code
```

### **Example 4: Custom Automation with CrewAI**
```python
# File: autonomous_feature_builder.py

from crewai import Agent, Task, Crew
from langchain_groq import ChatGroq

# Use your FREE Groq API
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

# Create specialized agents
architect = Agent(
    role='Software Architect',
    goal='Design features following Magnus platform patterns',
    llm=llm
)

coder = Agent(
    role='Python Developer',
    goal='Implement features with clean, tested code',
    llm=llm
)

tester = Agent(
    role='QA Engineer',
    goal='Test features and ensure they work correctly',
    llm=llm
)

# Define workflow
crew = Crew(
    agents=[architect, coder, tester],
    tasks=[...],
    verbose=True
)

# Use it
feature_request = """
Add momentum indicators (RSI, MACD, Stochastic) to the
supply/demand zones page with real-time calculations
"""

result = crew.kickoff(inputs={'feature': feature_request})

# Result: Complete, tested feature ready to commit
```

---

## 📊 Productivity Comparison

### **Manual Development:**
```
Time to add feature: 2-4 hours
- 30 min: Design and planning
- 60-90 min: Writing code
- 30 min: Testing and debugging
- 30 min: Documentation
Total: ~3 hours
```

### **With Cline:**
```
Time to add feature: 10-20 minutes
- 2 min: Describe what you want
- 3-5 min: Cline generates code
- 5-10 min: Review and approve changes
Total: ~15 minutes
Productivity gain: 12x faster
```

### **With GPT-Pilot:**
```
Time to add feature: 20-40 minutes
- 5 min: Answer clarifying questions
- 10-15 min: Pilot generates full implementation
- 5-10 min: Review code and test
Total: ~30 minutes
Productivity gain: 6x faster
```

### **With Aider:**
```
Time to fix bug: 2-5 minutes
- 1 min: Describe the bug
- 1-2 min: Aider generates fix
- 1-2 min: Review and test
Total: ~3 minutes
Productivity gain: 10-20x faster (for bugs)
```

---

## ⚡ Pro Tips

### **Tip 1: Start Small**
```
❌ Don't: "Rebuild the entire platform with new architecture"
✅ Do: "Add a new column to this table showing daily change %"
```

### **Tip 2: Be Specific**
```
❌ Don't: "Make it better"
✅ Do: "Add error handling for database connection failures with retry logic"
```

### **Tip 3: Reference Existing Code**
```
❌ Don't: "Create a new page"
✅ Do: "Create a new page following the same pattern as positions_page_improved.py"
```

### **Tip 4: Use Your Codebase Patterns**
```
❌ Don't: "Add a database table"
✅ Do: "Add a database table using our existing schema pattern in src/*_schema.sql"
```

### **Tip 5: Combine Tools**
```
- Cline: Daily feature development
- Aider: Quick bug fixes and refactoring
- AVA: Mobile monitoring
- CrewAI: Complex, multi-step automations
```

---

## 🔍 Troubleshooting

### **Issue: Agent doesn't understand my codebase**
```
Solution 1: Use Aider (has better codebase mapping)
Solution 2: Give Cline specific file references
Solution 3: Add .clinerules file with project patterns
```

### **Issue: Generated code doesn't match my style**
```
Solution 1: Reference existing file: "Follow the style in X.py"
Solution 2: Create .clinerules with coding standards
Solution 3: Use Aider with --lint flag
```

### **Issue: Agent makes too many changes**
```
Solution 1: Be more specific in requirements
Solution 2: Break into smaller tasks
Solution 3: Use GPT-Pilot's task breakdown
```

### **Issue: Costs too much**
```
Solution 1: Switch to FREE Groq (llama-3.3-70b-versatile)
Solution 2: Use local Ollama models
Solution 3: Use Aider with --cache for common patterns
```

---

## 📚 Learning Resources

### **Cline:**
- Docs: https://github.com/cline/cline/blob/main/README.md
- Discord: https://discord.gg/cline
- YouTube: Search "Cline AI tutorial"

### **GPT-Pilot:**
- Docs: https://github.com/Pythagora-io/gpt-pilot/wiki
- Examples: https://github.com/Pythagora-io/gpt-pilot/wiki/Apps-created-with-GPT-Pilot
- YouTube: "GPT-Pilot tutorial"

### **Aider:**
- Docs: https://aider.chat/docs/
- Examples: https://aider.chat/examples/
- Benchmarks: https://aider.chat/docs/benchmarks.html

### **CrewAI:**
- Docs: https://docs.crewai.com/
- Examples: https://github.com/crewAIInc/crewAI-examples
- Discord: https://discord.gg/crewai

---

## ✅ Your Action Plan

### **Today (30 minutes):**
```
1. ☐ Install Cline in VS Code
2. ☐ Add your API key (Claude or FREE Groq)
3. ☐ Try one small task
4. ☐ Read this guide
```

### **This Week (2 hours):**
```
1. ☐ Use Cline for 2-3 real features
2. ☐ Try Aider for bug fixes
3. ☐ Compare productivity vs manual coding
4. ☐ Decide if you want to continue
```

### **Next Week (if you like it):**
```
1. ☐ Integrate Cline into daily workflow
2. ☐ Install GPT-Pilot for larger features
3. ☐ Keep AVA for mobile monitoring
4. ☐ Document what works best
```

### **Long-term (1 month):**
```
1. ☐ Evaluate productivity gains
2. ☐ Consider building custom CrewAI system
3. ☐ Add voice interface integration
4. ☐ Share learnings with team
```

---

## 🎯 Quick Reference Commands

### **Cline (VS Code):**
```
Ctrl+Shift+P → "Cline: Open"
Type task → Wait for code → Approve/Reject
```

### **Aider (Terminal):**
```bash
aider --model claude-sonnet-4.5 src/file.py
> Add feature X
> /commit  # Auto-commit changes
```

### **GPT-Pilot (Terminal):**
```bash
gpt-pilot
> Describe your feature
> Answer questions
> Review generated code
```

### **CrewAI (Python):**
```python
from crewai import Crew, Agent, Task
crew = Crew(agents=[...], tasks=[...])
result = crew.kickoff()
```

---

**Created:** January 10, 2025
**Last Updated:** January 10, 2025
**Status:** Ready to use

**Next Step:** Install Cline and try your first autonomous coding task! 🚀
