@echo off
setlocal DisableDelayedExpansion
pushd "%~dp0" || exit /b 1
set "GUIFILEQR_BASIC=1"
call ".\ChayGuiFileQR.cmd"
set "GUIFILEQR_EXIT=%ERRORLEVEL%"
popd
exit /b %GUIFILEQR_EXIT%
