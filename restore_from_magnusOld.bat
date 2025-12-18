@echo off
REM Magnus Restoration Script - Restore files from magnusOld
REM Run this to complete Phases 3-9 of the restoration plan

echo ========================================
echo Magnus Codebase Restoration
echo ========================================
echo.
echo This will restore ~60 files from magnusOld to Magnus
echo Phases 1-2 already completed
echo.
pause

REM Phase 3: AVA Chatbot Files
echo.
echo [Phase 3] Restoring AVA chatbot files...
copy /Y "C:\code\magnusOld\ava_chatbot_page.py" "C:\code\Magnus\ava_chatbot_page.py"
copy /Y "C:\code\magnusOld\src\ava\autonomous_agent.py" "C:\code\Magnus\src\ava\autonomous_agent.py"
copy /Y "C:\code\magnusOld\src\ava\betting_data_interface.py" "C:\code\Magnus\src\ava\betting_data_interface.py"
copy /Y "C:\code\magnusOld\src\ava\charts.py" "C:\code\Magnus\src\ava\charts.py"
copy /Y "C:\code\magnusOld\src\ava\db_manager.py" "C:\code\Magnus\src\ava\db_manager.py"
copy /Y "C:\code\magnusOld\src\ava\enhanced_project_handler.py" "C:\code\Magnus\src\ava\enhanced_project_handler.py"
copy /Y "C:\code\magnusOld\src\ava\inline_keyboards.py" "C:\code\Magnus\src\ava\inline_keyboards.py"
copy /Y "C:\code\magnusOld\src\ava\legion_task_creator.py" "C:\code\Magnus\src\ava\legion_task_creator.py"
copy /Y "C:\code\magnusOld\src\ava\magnus_integration.py" "C:\code\Magnus\src\ava\magnus_integration.py"
copy /Y "C:\code\magnusOld\src\ava\magnus_project_knowledge.py" "C:\code\Magnus\src\ava\magnus_project_knowledge.py"
copy /Y "C:\code\magnusOld\src\ava\nlp_handler.py" "C:\code\Magnus\src\ava\nlp_handler.py"
copy /Y "C:\code\magnusOld\src\ava\omnipresent_ava.py" "C:\code\Magnus\src\ava\omnipresent_ava.py"
copy /Y "C:\code\magnusOld\src\ava\rate_limiter.py" "C:\code\Magnus\src\ava\rate_limiter.py"
copy /Y "C:\code\magnusOld\src\ava\research_agent.py" "C:\code\Magnus\src\ava\research_agent.py"
copy /Y "C:\code\magnusOld\src\ava\state_manager.py" "C:\code\Magnus\src\ava\state_manager.py"
copy /Y "C:\code\magnusOld\src\ava\telegram_bot.py" "C:\code\Magnus\src\ava\telegram_bot.py"
copy /Y "C:\code\magnusOld\src\ava\telegram_bot_enhanced.py" "C:\code\Magnus\src\ava\telegram_bot_enhanced.py"
copy /Y "C:\code\magnusOld\src\ava\voice_handler.py" "C:\code\Magnus\src\ava\voice_handler.py"
copy /Y "C:\code\magnusOld\src\ava\webhook_server.py" "C:\code\Magnus\src\ava\webhook_server.py"
copy /Y "C:\code\magnusOld\src\ava\xtrades_background_sync.py" "C:\code\Magnus\src\ava\xtrades_background_sync.py"

REM Copy AVA directories
echo Copying AVA directories...
xcopy /E /I /Y "C:\code\magnusOld\src\ava\adapters" "C:\code\Magnus\src\ava\adapters"
xcopy /E /I /Y "C:\code\magnusOld\src\ava\agents" "C:\code\Magnus\src\ava\agents"
xcopy /E /I /Y "C:\code\magnusOld\src\ava\tools" "C:\code\Magnus\src\ava\tools"
xcopy /E /I /Y "C:\code\magnusOld\src\ava\mcp" "C:\code\Magnus\src\ava\mcp"
xcopy /E /I /Y "C:\code\magnusOld\src\ava\migrations" "C:\code\Magnus\src\ava\migrations"

REM Phase 4: Sports Betting Files
echo.
echo [Phase 4] Restoring sports betting files...
copy /Y "C:\code\magnusOld\src\kalshi_client_v2.py" "C:\code\Magnus\src\kalshi_client_v2.py"
copy /Y "C:\code\magnusOld\src\kalshi_public_client.py" "C:\code\Magnus\src\kalshi_public_client.py"
copy /Y "C:\code\magnusOld\src\nfl_db_manager.py" "C:\code\Magnus\src\nfl_db_manager.py"
copy /Y "C:\code\magnusOld\src\nfl_realtime_sync.py" "C:\code\Magnus\src\nfl_realtime_sync.py"
copy /Y "C:\code\magnusOld\src\nfl_analytics.py" "C:\code\Magnus\src\nfl_analytics.py"
copy /Y "C:\code\magnusOld\src\nba_team_database.py" "C:\code\Magnus\src\nba_team_database.py"
copy /Y "C:\code\magnusOld\src\mlb_team_database.py" "C:\code\Magnus\src\mlb_team_database.py"
copy /Y "C:\code\magnusOld\src\ncaa_realtime_sync.py" "C:\code\Magnus\src\ncaa_realtime_sync.py"
copy /Y "C:\code\magnusOld\src\enhanced_sports_predictor.py" "C:\code\Magnus\src\enhanced_sports_predictor.py"
copy /Y "C:\code\magnusOld\src\live_betting_analyzer.py" "C:\code\Magnus\src\live_betting_analyzer.py"
copy /Y "C:\code\magnusOld\src\odds_validator.py" "C:\code\Magnus\src\odds_validator.py"
copy /Y "C:\code\magnusOld\src\odds_alert_system.py" "C:\code\Magnus\src\odds_alert_system.py"
copy /Y "C:\code\magnusOld\src\realtime_betting_sync.py" "C:\code\Magnus\src\realtime_betting_sync.py"
copy /Y "C:\code\magnusOld\src\ncaa_team_database.py" "C:\code\Magnus\src\ncaa_team_database.py"
copy /Y "C:\code\magnusOld\src\nfl_team_database.py" "C:\code\Magnus\src\nfl_team_database.py"

REM Phase 5: Technical Analysis Files
echo.
echo [Phase 5] Restoring technical analysis files...
copy /Y "C:\code\magnusOld\src\advanced_technical_indicators.py" "C:\code\Magnus\src\advanced_technical_indicators.py"
copy /Y "C:\code\magnusOld\src\momentum_indicators.py" "C:\code\Magnus\src\momentum_indicators.py"
copy /Y "C:\code\magnusOld\src\volume_profile_analyzer.py" "C:\code\Magnus\src\volume_profile_analyzer.py"
copy /Y "C:\code\magnusOld\src\fibonacci_calculator.py" "C:\code\Magnus\src\fibonacci_calculator.py"
copy /Y "C:\code\magnusOld\src\smart_money_indicators.py" "C:\code\Magnus\src\smart_money_indicators.py"
copy /Y "C:\code\magnusOld\src\enhanced_zone_analyzer.py" "C:\code\Magnus\src\enhanced_zone_analyzer.py"
copy /Y "C:\code\magnusOld\src\zone_buy_scanner.py" "C:\code\Magnus\src\zone_buy_scanner.py"
copy /Y "C:\code\magnusOld\src\price_action_monitor.py" "C:\code\Magnus\src\price_action_monitor.py"
copy /Y "C:\code\magnusOld\src\technical_analysis_db_manager.py" "C:\code\Magnus\src\technical_analysis_db_manager.py"
copy /Y "C:\code\magnusOld\src\zone_analyzer.py" "C:\code\Magnus\src\zone_analyzer.py"
copy /Y "C:\code\magnusOld\src\zone_detector.py" "C:\code\Magnus\src\zone_detector.py"
copy /Y "C:\code\magnusOld\src\price_monitor.py" "C:\code\Magnus\src\price_monitor.py"

REM Phase 6: Database Schemas
echo.
echo [Phase 6] Restoring database schemas...
copy /Y "C:\code\magnusOld\src\analytics_schema.sql" "C:\code\Magnus\src\analytics_schema.sql"
copy /Y "C:\code\magnusOld\src\kalshi_schema.sql" "C:\code\Magnus\src\kalshi_schema.sql"
copy /Y "C:\code\magnusOld\src\nfl_data_schema.sql" "C:\code\Magnus\src\nfl_data_schema.sql"
copy /Y "C:\code\magnusOld\src\odds_data_quality_schema.sql" "C:\code\Magnus\src\odds_data_quality_schema.sql"
copy /Y "C:\code\magnusOld\src\position_recommendations_schema.sql" "C:\code\Magnus\src\position_recommendations_schema.sql"
copy /Y "C:\code\magnusOld\src\qa_multi_agent_schema.sql" "C:\code\Magnus\src\qa_multi_agent_schema.sql"
copy /Y "C:\code\magnusOld\src\supply_demand_schema.sql" "C:\code\Magnus\src\supply_demand_schema.sql"
copy /Y "C:\code\magnusOld\src\task_management_schema.sql" "C:\code\Magnus\src\task_management_schema.sql"
copy /Y "C:\code\magnusOld\src\technical_analysis_schema.sql" "C:\code\Magnus\src\technical_analysis_schema.sql"
copy /Y "C:\code\magnusOld\src\discord_schema.sql" "C:\code\Magnus\src\discord_schema.sql"

REM Phase 7: Portfolio Management
echo.
echo [Phase 7] Restoring portfolio management files...
copy /Y "C:\code\magnusOld\src\portfolio_balance_tracker.py" "C:\code\Magnus\src\portfolio_balance_tracker.py"
copy /Y "C:\code\magnusOld\src\bankroll_manager.py" "C:\code\Magnus\src\bankroll_manager.py"
copy /Y "C:\code\magnusOld\src\config_manager.py" "C:\code\Magnus\src\config_manager.py"
copy /Y "C:\code\magnusOld\src\task_manager.py" "C:\code\Magnus\src\task_manager.py"
copy /Y "C:\code\magnusOld\src\task_completion_with_qa.py" "C:\code\Magnus\src\task_completion_with_qa.py"
copy /Y "C:\code\magnusOld\src\qa_verification_agent.py" "C:\code\Magnus\src\qa_verification_agent.py"
copy /Y "C:\code\magnusOld\src\alert_manager.py" "C:\code\Magnus\src\alert_manager.py"
copy /Y "C:\code\magnusOld\src\portfolio_balance_display.py" "C:\code\Magnus\src\portfolio_balance_display.py"

REM Phase 8: Dashboard Pages
echo.
echo [Phase 8] Restoring dashboard pages...
copy /Y "C:\code\magnusOld\analytics_performance_page.py" "C:\code\Magnus\analytics_performance_page.py"
copy /Y "C:\code\magnusOld\enhancement_qa_management_page.py" "C:\code\Magnus\enhancement_qa_management_page.py"
copy /Y "C:\code\magnusOld\options_analysis_hub_page.py" "C:\code\Magnus\options_analysis_hub_page.py"
copy /Y "C:\code\magnusOld\seven_day_dte_scanner_page.py" "C:\code\Magnus\seven_day_dte_scanner_page.py"
copy /Y "C:\code\magnusOld\test_components_page.py" "C:\code\Magnus\test_components_page.py"
copy /Y "C:\code\magnusOld\test_kalshi_nfl_markets_page.py" "C:\code\Magnus\test_kalshi_nfl_markets_page.py"
copy /Y "C:\code\magnusOld\test_streamlit_comprehensive_page.py" "C:\code\Magnus\test_streamlit_comprehensive_page.py"

REM Phase 9: Communication Features
echo.
echo [Phase 9] Restoring communication features...
copy /Y "C:\code\magnusOld\src\discord_message_sync.py" "C:\code\Magnus\src\discord_message_sync.py"
copy /Y "C:\code\magnusOld\src\email_game_reports.py" "C:\code\Magnus\src\email_game_reports.py"
copy /Y "C:\code\magnusOld\src\game_watchlist_monitor.py" "C:\code\Magnus\src\game_watchlist_monitor.py"

echo.
echo ========================================
echo Restoration Complete!
echo ========================================
echo.
echo Next Steps:
echo 1. Review the restored files
echo 2. Run: python -c "from src.kalshi_db_manager import KalshiDBManager"
echo 3. Run: python -c "from src.services.robinhood_client import RobinhoodClient"
echo 4. Test dashboard pages load correctly
echo 5. Verify AVA chatbot full functionality
echo.
echo Local LLM features (magnus_local_llm.py) have been preserved.
echo.
pause
