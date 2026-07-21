@echo off
setlocal
cd /d "%~dp0"

echo ============================================
echo  Building TorrentSearch.exe
echo ============================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo Python was not found on PATH. Install it from python.org and try again.
    pause
    exit /b 1
)

echo Creating a temporary build environment...
python -m venv build_venv
if errorlevel 1 (
    echo Failed to create the build environment.
    pause
    exit /b 1
)

echo Installing build dependencies (this only happens once)...
build_venv\Scripts\python.exe -m pip install --upgrade pip >nul
build_venv\Scripts\python.exe -m pip install -r src\requirements.txt pyinstaller pyinstaller-hooks-contrib
if errorlevel 1 (
    echo Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo Building the executable...
build_venv\Scripts\python.exe -m PyInstaller ^
    --onefile ^
    --console ^
    --name TorrentSearch ^
    --icon "%~dp0icon\torrent_search.ico" ^
    --distpath dist ^    --workpath build_temp ^
    --specpath build_temp ^
    --clean ^
    --noconfirm ^
    src\torrent_search.py

if errorlevel 1 (
    echo.
    echo Build failed. See the errors above.
    pause
    exit /b 1
)

echo Cleaning up temporary build files...
rmdir /s /q build_temp 2>nul
rmdir /s /q build_venv 2>nul

echo.
echo ============================================
echo  Done! Built: dist\TorrentSearch.exe
echo ============================================
echo.
echo Next step: run install.bat to add it to your Start Menu
echo and Windows' Installed Apps list.
echo.
pause
