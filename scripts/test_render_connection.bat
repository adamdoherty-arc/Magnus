@echo off
echo ============================================
echo AVA - Test Render Database Connection
echo ============================================
echo.

python -c "import sys; sys.path.insert(0, 'src'); from config_manager import get_config; config = get_config(); print(f'Testing connection to: {config.get(\"database\")}'); import psycopg2; conn = psycopg2.connect(host=config.get('database.host'), port=config.get('database.port', 5432), dbname=config.get('database.name'), user=config.get('database.user'), password=config.get('database.password')); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM pg_tables WHERE schemaname = \\'public\\''); count = cursor.fetchone()[0]; print(f'✅ Connected successfully!'); print(f'📊 Tables found: {count}'); cursor.execute('SELECT table_name FROM information_schema.tables WHERE table_schema = \\'public\\' ORDER BY table_name LIMIT 10'); tables = cursor.fetchall(); print('📋 Sample tables:'); [print(f'   - {t[0]}') for t in tables]; conn.close(); print('🎉 Connection test passed!')"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================
    echo ✅ SUCCESS! Connected to Render database
    echo ============================================
    echo.
    echo 🎉 Your AVA platform is now using Render!
    echo.
    echo 🚀 You can now start your application!
    echo    Database is ready on Render
    echo.
) else (
    echo.
    echo ❌ Connection failed!
    echo 💡 Check your .env file credentials
)

pause
