@echo off
setlocal EnableExtensions DisableDelayedExpansion

REM Run from the folder containing this batch file.
pushd "%~dp0"
if errorlevel 1 (
    echo Could not open the project folder.
    pause
    exit /b 1
)

REM Use the project's Windows virtual environment when present.
if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
    if errorlevel 1 goto Failed
)

REM Read the release version directly from Version.py.
set "Version="
for /f "delims=" %%V in ('python -c "from Version import ProgramVersion; print(ProgramVersion)"') do set "Version=%%V"
if not defined Version (
    echo Could not read ProgramVersion. Check Python and Version.py.
    goto Failed
)

REM Bundle Python, the application, CustomTkinter assets, and the icons.
python -m PyInstaller ^
    --clean ^
    --noconfirm ^
    --onefile ^
    --windowed ^
    --collect-all customtkinter ^
    --name "Folder2WebP-%Version%" ^
    --specpath "build" ^
    --icon "%~dp0Icon.ico" ^
    --add-data "%~dp0Icon.ico:." ^
    --add-data "%~dp0Icon.png:." ^
    "ImageConverter.py"
if errorlevel 1 goto Failed

echo.
echo Build complete: "dist\Folder2WebP-%Version%.exe"
popd
pause
exit /b 0

:Failed
echo.
echo Build failed. Review the error messages above.
popd
pause
exit /b 1