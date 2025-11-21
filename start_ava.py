"""
Start AVA - Automated Vector Agent
===================================

AVA continuously works through enhancement tasks from the database,
implementing improvements 24/7 using Claude Code's terminal tools.

This uses Claude Code directly (NO API COSTS) to:
- Select highest-priority tasks from database
- Implement enhancements using built-in tools
- Update database with progress
- Work continuously until you stop it

Launch Methods:
1. Manual Mode: You run process_next_task.py and implement each task
2. Assisted Mode: AVA suggests tasks, you approve and implement
3. Voice Mode: Talk to AVA via Telegram for status and requests
"""

import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║            🤖 AVA - Automated Vector Agent 🤖                        ║
║                                                                      ║
║  Continuously improving your trading platform 24/7                   ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

AVA Capabilities:
✅ Database-driven task queue (934 tasks loaded)
✅ Automatic priority selection
✅ Uses Claude Code directly (FREE!)
✅ Full tool access (Read, Write, Edit, Bash, Task)
✅ Voice conversations via Telegram
✅ Real-time status updates
✅ Portfolio monitoring
✅ Stock alerts

How to Work with AVA:

1. Get Next Task:
   python process_next_task.py

2. Mark Task Complete:
   python mark_task_complete.py <task_id> <hours>

3. Talk to AVA (Voice):
   python talk_to_ava.py

4. Check AVA's Status:
   python ava_status.py

Current Architecture:
- AVA identifies highest-priority tasks
- You (or Claude Code) implement using terminal tools
- Database stays updated automatically
- NO API COSTS - uses your Claude Code session!

Ready to work with AVA? Run: python process_next_task.py
""")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("To start working with AVA:")
    print("="*70)
    print("\n1. Get next task:")
    print("   python process_next_task.py")
    print("\n2. Implement the task using Claude Code tools")
    print("\n3. Mark complete:")
    print("   python mark_task_complete.py <task_id>")
    print("\n4. Repeat!")
    print("\n" + "="*70)
