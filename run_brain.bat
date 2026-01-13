@echo off
chcp 65001 >nul
cd /d "%~dp0\ai_server"
echo AIサーバーを起動しています... (ポート 8082)
..\.venv\Scripts\python.exe server.py
echo.
echo サーバーが停止しました。エラー内容を確認してください。
pause
