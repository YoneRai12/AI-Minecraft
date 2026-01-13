@echo off
echo ==========================================
echo        Java Environment Debugger
echo ==========================================
echo.
echo Checking environment variables...
echo PATH=%PATH%
echo.
echo Checking java command...
where java
echo.
echo Checking java version...
java -version
echo.
echo.
echo If you see "not recognized" above, Java is not in PATH.
echo ==========================================
pause
