@echo off
setlocal DisableDelayedExpansion
pushd "%~dp0" || exit /b 1
set "APP_PYTHON=.venv\Scripts\python.exe"

if exist "%APP_PYTHON%" (
    "%APP_PYTHON%" -c "import sys; sys.exit(sys.version_info < (3, 10))" >nul 2>&1 && goto check_tkinter
)
py -3 -c "import sys; sys.exit(sys.version_info < (3, 10))" >nul 2>&1 && py -3 -m venv .venv && goto check_tkinter
python -c "import sys; sys.exit(sys.version_info < (3, 10))" >nul 2>&1 && python -m venv .venv && goto check_tkinter
echo Khong the tao moi truong ao. Can Python 3.10 tro len.
goto failed

:check_tkinter
"%APP_PYTHON%" -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    echo Ban Python dang dung thieu Tcl/Tk. Hay cai Python kem tuy chon Tcl/Tk.
    goto failed
)
call :check_dependencies
if not errorlevel 1 goto launch

echo Dang cai thu vien cho Gui File QR...
"%APP_PYTHON%" -m pip --version >nul 2>&1 || "%APP_PYTHON%" -m ensurepip --upgrade || goto install_failed
"%APP_PYTHON%" -m pip install --disable-pip-version-check --force-reinstall -r requirements.txt || goto install_failed
call :check_dependencies
if errorlevel 1 goto install_failed

:launch
set "APP_SCRIPT=app.py"
if defined GUIFILEQR_BASIC set "APP_SCRIPT=basic.py"
"%APP_PYTHON%" "%APP_SCRIPT%"
if errorlevel 1 goto failed
popd
exit /b 0

:check_dependencies
"%APP_PYTHON%" -c "from importlib.metadata import version; import flask, qrcode; from PIL import Image; version('Flask'); version('qrcode'); version('Pillow')" >nul 2>&1 || exit /b 1
"%APP_PYTHON%" -m pip check >nul 2>&1
exit /b %errorlevel%

:install_failed
echo Cai thu vien chua thanh cong. Kiem tra mang roi mo lai file nay.
:failed
popd
pause
exit /b 1
