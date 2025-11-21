#!/usr/bin/env python3
"""Fix AI Agent watchlist query to use correct tables"""

file_path = 'src/ai_options_agent/ai_options_db_manager.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the query to use _api tables
old_query = """            query = \"\"\"
                SELECT ws.symbol
                FROM tv_watchlist_symbols ws
                JOIN tv_watchlists w ON ws.watchlist_id = w.id
                WHERE w.name = %s
                ORDER BY ws.symbol
            \"\"\""""

new_query = """            # Query from tv_watchlists_api and tv_symbols_api (live API data)
            query = \"\"\"
                SELECT DISTINCT s.symbol
                FROM tv_symbols_api s
                JOIN tv_watchlists_api w ON s.watchlist_id = w.watchlist_id
                WHERE w.name = %s
                ORDER BY s.symbol
            \"\"\""""

content = content.replace(old_query, new_query)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed watchlist query to use tv_watchlists_api and tv_symbols_api tables")
print("AI Agent will now find watchlist symbols correctly")
