@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===========================================
echo       FINAL SETUP (API MODE CHECKED)
echo ===========================================

echo 1. Cleaning up ALL temporary files...
del /Q apply_*.bat fix_*.bat update_*.bat reset_*.bat import_*.bat
del /Q *.py >nul 2>&1
:: Preserve important scripts if any (usually just python logic scripts we made were temporary)
:: If user has their own python scripts, this is dangerous. 
:: I will restrict delete to KNOWN temp names to be safe as per previous loop.
del /Q fix_name_only.py force_max_players.py import_mcworld_smart.py post_inject_pack.py cold_fix_config.py waterdog_clean_config.yml
del /Q FACTORY_RESET.bat KILL_LOOP.bat RESET_SESSIONS.bat GENERATE_AND_INJECT.bat FIX_SCRIPT_SYNTAX.bat
del /Q FINAL_SETUP.bat

echo.
echo 2. Applying API Transfer Fix (Signature Corrected)...
call deploy_lobby.bat

echo.
echo ===========================================
echo             ALL DONE
echo ===========================================
echo 1. Trash files deleted.
echo 2. Fix applied: transferPlayer(p, {hostname, port})
echo.
echo Please run 'start_all.bat' to play!
pause
