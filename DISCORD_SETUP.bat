@echo off
echo ============================================
echo Discord Message Sync Setup
echo ============================================
echo.

echo Step 1: Installing DiscordChatExporter...
echo.
echo Please download DiscordChatExporter from:
echo https://github.com/Tyrrrz/DiscordChatExporter/releases/latest
echo.
echo Download: DiscordChatExporter.Cli.zip
echo Extract to: C:\Tools\DiscordChatExporter\
echo.
pause

echo.
echo Step 2: Testing Discord connection...
echo.
set CHANNEL_ID=
set /p CHANNEL_ID=Enter a Discord channel ID to test:

if "%CHANNEL_ID%"=="" (
    echo No channel ID provided. Skipping test.
    goto end
)

echo.
echo Syncing channel %CHANNEL_ID% for last 7 days...
python src/discord_message_sync.py %CHANNEL_ID% 7

:end
echo.
echo Setup complete!
echo.
echo Next steps:
echo 1. Update DISCORD_EXPORTER_PATH in .env if not in C:\Tools\
echo 2. Get channel IDs from Discord (right-click channel > Copy ID)
echo 3. Run: python src/discord_message_sync.py CHANNEL_ID
echo.
pause
