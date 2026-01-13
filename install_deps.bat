@echo off
chcp 65001 >nul
cd /d "%~dp0\ai_server"
echo 必要なライブラリをインストールしています... (数分かかる場合があります)
..\.venv\Scripts\python.exe -m pip install -r requirements.txt
echo.
echo インストールが完了しました！
pause
