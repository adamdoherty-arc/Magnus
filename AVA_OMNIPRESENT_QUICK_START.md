# AVA Omnipresent - Quick Start Guide

## What Was Done

You requested AVA to be omnipresent across Magnus - able to speak to every page, manage tasks, and have access to everything. This has been **fully implemented**!

## What You Have Now

### 1. AVA Appears on Every Page

Open your Magnus dashboard (it's already running) and you'll see AVA at the top of every page:

```
🤖 AVA - Your Expert Trading Assistant  [▼ Click to expand]
```

### 2. Full System Access

AVA can now:
- ✅ Query any data in Magnus database
- ✅ Create tasks when you want improvements
- ✅ Analyze watchlists for trading opportunities
- ✅ Check your Robinhood portfolio
- ✅ Search Magnus project knowledge
- ✅ View and update tasks
- ✅ Get stock prices
- ✅ Remember all conversations

### 3. Automatic Improvement

When AVA can't answer a question:
- Logs it to database
- Tracks how many times it's asked
- **Automatically creates Legion tasks** when asked 5+ times
- Tasks include investigation steps, implementation requirements, and QA checklist

### 4. Telegram Integration Ready

The same AVA can be integrated into your Telegram bot (next step).

## How to Use

### Open Magnus Dashboard

The dashboard is already running at: **http://localhost:8501**

### Expand AVA

Click the purple box at the top of any page to open AVA's chat interface.

### Ask AVA Anything

**Examples:**

```
"What's my current portfolio balance?"
"Analyze the NVDA watchlist"
"Create a task to add more indicators to the dashboard"
"Show me all pending tasks"
"What's the current price of TSLA?"
"How many wheel positions do I have?"
```

## Key Features

### 1. Context Awareness

AVA knows what page you're on and can reference it:

```
User: "Show me opportunities on this page"
AVA: *Analyzes current watchlist/page context*
```

### 2. Task Management

```
User: "I want better supply/demand zone detection"
AVA: "I'll create a task for that" *creates in database*
```

### 3. Memory & Recall

```
User: "What did we discuss earlier about NVDA?"
AVA: *Recalls previous conversation from database*
```

### 4. Learning System

If you ask something AVA doesn't know:
- It's logged with the reason (no_data, unsupported_feature, error, etc.)
- After 5 times, **automatic Legion task created**
- Task includes full details for implementation
- After task completion, AVA can answer the question

## Architecture

```
User → Magnus Dashboard → AVA (LangChain Agent)
                           ↓
                    8 Custom Tools:
                    - query_database
                    - create_task
                    - analyze_watchlist
                    - get_portfolio_status
                    - search_magnus_knowledge
                    - get_recent_tasks
                    - update_task_status
                    - get_stock_price
                           ↓
                    ConversationMemoryManager
                           ↓
                    PostgreSQL (11 tables)
```

## Files Created

1. **`src/ava/omnipresent_ava.py`** - Main AVA implementation (650 lines)
2. **`src/ava/conversation_memory_schema.sql`** - Database schema (800 lines)
3. **`src/ava/conversation_memory_manager.py`** - Memory management (700 lines)
4. **`src/ava/legion_task_creator.py`** - Auto-create tasks (500 lines)
5. **`initialize_ava_database.py`** - Database setup script
6. **`AVA_OMNIPRESENT_INTEGRATION_COMPLETE.md`** - Full documentation
7. **`AVA_MEMORY_LEGION_INTEGRATION_COMPLETE.md`** - Memory system docs
8. **`LEGION_QA_CONSOLIDATION_PLAN.md`** - Legion QA integration plan

## Files Modified

- **`dashboard.py`** - Added `show_omnipresent_ava()` call (line 152)

## Database Tables Created

11 tables for conversation memory:
- `ava_conversations` - Session tracking
- `ava_messages` - All messages
- `ava_unanswered_questions` - Failed queries (auto-tracked)
- `ava_legion_task_log` - Auto-created tasks
- `ava_action_history` - Action log
- `ava_conversation_context` - Context storage
- `ava_user_preferences` - User settings
- Plus analytics views

## CLI Tools Available

### Create Legion Tasks from Unanswered Questions

```bash
# See what would be created
python src/ava/legion_task_creator.py --dry-run

# Create tasks
python src/ava/legion_task_creator.py

# Resolve completed tasks
python src/ava/legion_task_creator.py --resolve
```

### Initialize/Reinitialize Database

```bash
python initialize_ava_database.py
```

## Next Steps

### 1. Test AVA Now

Go to http://localhost:8501 and:
1. Look for purple AVA box at top
2. Click to expand
3. Ask: "What is Magnus?"
4. Try: "Show me my portfolio"
5. Try: "Analyze a watchlist"

### 2. Telegram Bot Integration (Optional)

Update `src/ava/telegram_bot.py` to use OmnipresentAVA:

```python
from src.ava.omnipresent_ava import OmnipresentAVA

ava = OmnipresentAVA()

def handle_message(update, context):
    user_msg = update.message.text
    user_id = str(update.effective_user.id)

    response = ava.process_message(user_msg, user_id, 'telegram')
    update.message.reply_text(response['response'])
```

### 3. Monitor Unanswered Questions

Check what users are asking but AVA can't answer:

```sql
SELECT
    user_question,
    occurrence_count,
    failure_reason,
    last_occurred_at
FROM ava_unanswered_questions
WHERE NOT resolved
ORDER BY occurrence_count DESC
LIMIT 10;
```

### 4. Create Tasks Automatically

Set up a daily cron job:

```bash
# Add to crontab
0 9 * * * cd /path/to/WheelStrategy && python src/ava/legion_task_creator.py
```

This will auto-create Legion tasks from high-frequency unanswered questions.

## Troubleshooting

### AVA Not Appearing

Check browser at http://localhost:8501 - refresh if needed.

### AVA Not Responding

Check GROQ_API_KEY in `.env` file:
```bash
GROQ_API_KEY=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
```

### Database Errors

Reinitialize schema:
```bash
python initialize_ava_database.py
```

## Technology Stack

- **LangChain** - Agent framework with ReAct pattern
- **ChatGroq** - LLM backend (Llama 3.1 70B, free API)
- **PostgreSQL** - Conversation memory storage
- **Streamlit** - UI framework
- **Python 3.12** - Implementation language

## Summary

AVA is now:
- ✅ **Omnipresent** - On every page
- ✅ **Expert** - Full system access via 8 tools
- ✅ **Memory-enabled** - Remembers all conversations
- ✅ **Self-improving** - Auto-creates tasks from failures
- ✅ **Legion-integrated** - Tasks flow through QA

**Status: READY FOR TESTING**

Open http://localhost:8501 and look for the purple AVA box at the top!

---

## Questions?

- **Full docs:** `AVA_OMNIPRESENT_INTEGRATION_COMPLETE.md`
- **Memory system:** `AVA_MEMORY_LEGION_INTEGRATION_COMPLETE.md`
- **QA process:** `LEGION_QA_CONSOLIDATION_PLAN.md`
- **Code:** `src/ava/omnipresent_ava.py`
