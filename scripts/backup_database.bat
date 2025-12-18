@echo off
echo ============================================
echo AVA Database Backup Tool
echo ============================================
echo.

REM Set PostgreSQL bin path
set PG_BIN="C:\Program Files\PostgreSQL\16\bin"

REM Create backup filename with timestamp
set BACKUP_DIR=backups
set TIMESTAMP=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
set BACKUP_FILE=%BACKUP_DIR%\ava_backup_%TIMESTAMP%.sql

echo 📦 Backing up database: magnus
echo 📁 Backup location: %BACKUP_FILE%
echo.

REM Set password from .env
set PGPASSWORD=postgres123!

REM Create backup with all schemas
%PG_BIN%\pg_dump -h localhost -U postgres -d magnus --no-owner --no-acl -f %BACKUP_FILE%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Backup completed successfully!
    echo 📊 Backup file size:
    dir %BACKUP_FILE% | find "%TIMESTAMP%"
    echo.
    echo 💡 To restore to Render, use: restore_to_render.bat
) else (
    echo.
    echo ❌ Backup failed! Check PostgreSQL connection.
)

pause
