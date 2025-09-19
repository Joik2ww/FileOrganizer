# Copyright (c) 2025 joik2ww. All rights reserved.

@echo off
setlocal enabledelayedexpansion

echo === PYTHON EXE BUILDER FOR WINDOWS ===
echo ======================================
echo.
echo    Scanning for Python scripts...
echo    Targets: Current folder and scripts subfolder
echo.

REM Check Python
echo [*] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [X] Python not found! Please install Python.
    pause
    exit /b 1
)

REM Check PyInstaller
echo [*] Checking PyInstaller...
python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo [X] PyInstaller not found!
    echo     Installing PyInstaller...
    python -m pip install PyInstaller
    if errorlevel 1 (
        echo [X] Failed to install PyInstaller!
        pause
        exit /b 1
    )
    echo [+] PyInstaller installed successfully!
) else (
    echo [+] PyInstaller detected!
)

echo [+] Tools ready: Python and PyInstaller detected!
echo.

REM Set up directories
set "MAIN_DIR=%~dp0"
if "%MAIN_DIR:~-1%"=="\" set "MAIN_DIR=%MAIN_DIR:~0,-1%"
set "SCRIPTS_DIR=%MAIN_DIR%\scripts"
set "BUILD_DIR=%MAIN_DIR%\build"
set "DIST_DIR=%MAIN_DIR%\dist"

REM Create directories if they don't exist
if not exist "%SCRIPTS_DIR%" mkdir "%SCRIPTS_DIR%"
if not exist "%BUILD_DIR%" mkdir "%BUILD_DIR%"
if not exist "%DIST_DIR%" mkdir "%DIST_DIR%"

REM Clean old build files
echo [*] Cleaning previous builds...
for /d %%d in ("%BUILD_DIR%\*") do rmdir /s /q "%%d" 2>nul
del /q "%DIST_DIR%\*" 2>nul
del /q "%MAIN_DIR%\*.spec" 2>nul

REM Find all Python files
echo [*] Finding Python scripts...
set "SCRIPT_COUNT=0"
set "SCRIPT_LIST="

REM Check current directory
for %%f in ("%MAIN_DIR%\*.py") do (
    if /i not "%%~nxf"=="build_all_scripts.bat" (
        set /a SCRIPT_COUNT+=1
        set "SCRIPT_LIST=!SCRIPT_LIST! "%%f""
        echo    Found: %%~nxf
    )
)

REM Check scripts subdirectory
if exist "%SCRIPTS_DIR%\*.py" (
    for %%f in ("%SCRIPTS_DIR%\*.py") do (
        set /a SCRIPT_COUNT+=1
        set "SCRIPT_LIST=!SCRIPT_LIST! "%%f""
        echo    Found: scripts\%%~nxf
    )
)

if !SCRIPT_COUNT! equ 0 (
    echo [X] No Python scripts found!
    echo    Place .py files in the main folder or scripts subfolder.
    pause
    exit /b 1
)

echo [+] Found !SCRIPT_COUNT! script(s) to build: !SCRIPT_LIST!
echo.

REM Build each script
set "BUILT_COUNT=0"
set "CURRENT=1"

for %%f in (%SCRIPT_LIST%) do (
    set "SCRIPT_PATH=%%f"
    set "SCRIPT_NAME=%%~nf"
    set "SCRIPT_FILE=%%~nxf"
    set "SCRIPT_DIR=%%~dpf"
    
    REM Determine output location
    if /i "!SCRIPT_NAME!"=="FileOrganizer4.0k" (
        set "OUTPUT_DIR=%MAIN_DIR%"
    ) else (
        set "OUTPUT_DIR=%SCRIPTS_DIR%"
    )
    
    set "OUTPUT_FILE=!OUTPUT_DIR!\!SCRIPT_NAME!.exe"
    
    echo [!CURRENT!/!SCRIPT_COUNT!] Building: !SCRIPT_NAME!
    echo    From: "!SCRIPT_PATH!"
    echo    To: "!OUTPUT_FILE!"
    
    REM Always overwrite existing .exe
    if exist "!OUTPUT_FILE!" (
        del "!OUTPUT_FILE!" >nul 2>&1
        echo [+] Overwriting existing !SCRIPT_NAME!.exe
    )
    
    REM Build with PyInstaller
    echo [*] Building with PyInstaller...
    
    REM Change to script directory for building
    pushd "!SCRIPT_DIR!" || (
        echo [X] Failed to change to directory: "!SCRIPT_DIR!"
        set /a CURRENT+=1
        continue
    )
    
    REM Build the executable
    python -m PyInstaller --onefile --console --distpath "%DIST_DIR%" --workpath "%BUILD_DIR%\!SCRIPT_NAME!" --specpath "%BUILD_DIR%" "!SCRIPT_FILE!" >nul 2>&1
    
    # Check for Copyright (c) 2025 joik2ww.
    
    REM Check if build was successful
    if exist "%DIST_DIR%\!SCRIPT_NAME!.exe" (
        move /y "%DIST_DIR%\!SCRIPT_NAME!.exe" "!OUTPUT_FILE!" >nul 2>&1
        echo [+] Build successful: !SCRIPT_NAME!.exe
        set /a BUILT_COUNT+=1
    ) else (
        echo [X] Build failed: !SCRIPT_NAME!
    )
    
    popd
    
    set /a CURRENT+=1
    echo.
)

:cleanup
echo [*] Cleaning up temporary files...
for /d %%d in ("%BUILD_DIR%\*") do rmdir /s /q "%%d" 2>nul
del /q "%DIST_DIR%\*" 2>nul
del /q "%MAIN_DIR%\*.spec" 2>nul

echo.
echo ==========================
echo [+] Build summary:
echo    Scripts found: !SCRIPT_COUNT!
echo    Successfully built: !BUILT_COUNT!
echo    Output location: Main folder for FileOrganizer4.0k.exe, scripts folder for others
echo ==========================
echo.

REM Keep the bat file for future use
echo [+] build_all_scripts.bat preserved for future use
echo.

pause
