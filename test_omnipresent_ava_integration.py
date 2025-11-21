"""
Test Omnipresent AVA Integration
=================================

Quick test to verify that omnipresent AVA can be imported and initialized.
"""

import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

print("=" * 80)
print("TESTING OMNIPRESENT AVA INTEGRATION")
print("=" * 80)

# Test 1: Import the module
print("\n[Test 1] Importing omnipresent_ava module...")
try:
    from src.ava.omnipresent_ava import show_omnipresent_ava, OmnipresentAVA
    print("✓ Successfully imported omnipresent_ava")
except Exception as e:
    print(f"✗ Failed to import: {e}")
    sys.exit(1)

# Test 2: Check dependencies
print("\n[Test 2] Checking LangChain dependencies...")
try:
    import langchain
    from langchain.agents import create_react_agent, AgentExecutor, tool
    from langchain.memory import ConversationBufferMemory
    from langchain_groq import ChatGroq
    print("✓ LangChain dependencies available")
except Exception as e:
    print(f"✗ LangChain import failed: {e}")
    sys.exit(1)

# Test 3: Check environment variables
print("\n[Test 3] Checking environment variables...")
from dotenv import load_dotenv
load_dotenv()

groq_api_key = os.getenv('GROQ_API_KEY')
db_host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')

if groq_api_key:
    print(f"✓ GROQ_API_KEY found: {groq_api_key[:20]}...")
else:
    print("⚠ GROQ_API_KEY not found (will use Ollama fallback)")

if db_host and db_name:
    print(f"✓ Database config found: {db_name}@{db_host}")
else:
    print("✗ Database config missing")
    sys.exit(1)

# Test 4: Check database connection
print("\n[Test 4] Testing database connection...")
try:
    import psycopg2
    conn = psycopg2.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password
    )
    cur = conn.cursor()

    # Check if AVA tables exist
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_name = 'ava_conversations'
        )
    """)

    tables_exist = cur.fetchone()[0]

    if tables_exist:
        print("✓ AVA conversation memory tables exist")
    else:
        print("⚠ AVA conversation memory tables not found (need to run schema)")

    conn.close()
except Exception as e:
    print(f"✗ Database connection failed: {e}")

# Test 5: Initialize AVA (without Streamlit)
print("\n[Test 5] Initializing OmnipresentAVA class...")
try:
    ava = OmnipresentAVA()
    print("✓ OmnipresentAVA initialized successfully")

    # Check if agent is available
    if ava.agent_executor:
        print("✓ LangChain agent initialized")
    else:
        print("⚠ Agent not initialized (may need Groq API key)")

except Exception as e:
    print(f"⚠ AVA initialization partial: {e}")

# Test 6: Test a simple query (without Streamlit session)
print("\n[Test 6] Testing simple message processing...")
try:
    # Create a test user
    test_message = "What is Magnus?"
    test_user_id = "test_user_integration"
    test_platform = "test"

    print(f"Test query: '{test_message}'")

    # Note: This will only work if all dependencies are properly set up
    # including database, Groq API, etc.

    response = ava.process_message(test_message, test_user_id, test_platform)

    if response.get('success'):
        print(f"✓ AVA responded: {response['response'][:100]}...")
    else:
        print(f"⚠ AVA response had issues: {response.get('error', 'Unknown error')}")

except Exception as e:
    print(f"⚠ Message processing test failed: {e}")
    print("  (This is expected if Groq API or database is not fully configured)")

print("\n" + "=" * 80)
print("INTEGRATION TEST COMPLETE")
print("=" * 80)

print("\n📋 Next Steps:")
print("1. Ensure database schema is initialized: psql -U postgres -d magnus -f src/ava/conversation_memory_schema.sql")
print("2. Verify Groq API key in .env file")
print("3. Run the dashboard: streamlit run dashboard.py")
print("4. Look for the expandable 'AVA - Your Expert Trading Assistant' at the top")
print("5. Test AVA with queries like 'What is my portfolio status?' or 'Create a task to improve...'")
