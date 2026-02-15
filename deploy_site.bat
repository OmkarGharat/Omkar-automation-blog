@echo off
setlocal enabledelayedexpansion
echo ============================================
echo SAFE Secure Build and Deploy (Direct Mode)
echo ============================================
echo.

:: Safety Check: Make sure we're on main branch
for /f "tokens=*" %%i in ('git branch --show-current') do set CURRENT_BRANCH=%%i

if not "%CURRENT_BRANCH%"=="main" (
    echo [ERROR] You must be on 'main' branch to deploy!
    echo Current branch: %CURRENT_BRANCH%
    pause
    exit /b 1
)

echo [OK] Starting from main branch...
echo.

:: Clean old build files
echo [CLEAN] Removing old build files...
if exist "%~dp0mkdocs_base.yml" del "%~dp0mkdocs_base.yml"
if exist "%~dp0site" rd /s /q "%~dp0site"

:: 1. Build and Encrypt
echo [STEP 1] Building site with publish.py...
python "%~dp0publish.py" || (
    echo [ERROR] publish.py failed!
    pause
    exit /b 1
)
echo [OK] Build successful!

:: 2. Verify site folder exists
if not exist "%~dp0site" (
    echo [ERROR] site folder not found!
    pause
    exit /b 1
)

:: 3. Create temp folder
set "TEMP_DEPLOY=%TEMP%\mkdocs_deploy_%RANDOM%"
mkdir "%TEMP_DEPLOY%" || (
    echo [ERROR] Could not create temp folder
    pause
    exit /b 1
)

:: 4. Copy built site and configs to temp
echo [STEP 2] Copying files to temp folder...
xcopy "%~dp0site" "%TEMP_DEPLOY%\site\" /E /I /Q /Y >nul
if exist "%~dp0vercel.json" copy "%~dp0vercel.json" "%TEMP_DEPLOY%\" /Y >nul
if exist "%~dp0mkdocs_base.yml" copy "%~dp0mkdocs_base.yml" "%TEMP_DEPLOY%\" /Y >nul
echo [OK] Files backed up to temp

:: 5. Switch to deploy branch
echo [STEP 3] Switching to deploy branch...
git checkout deploy || (
    echo [ERROR] Could not switch to deploy branch
    rd /s /q "%TEMP_DEPLOY%"
    pause
    exit /b 1
)
echo [OK] On deploy branch

:: 6. Clean old files on deploy branch
echo [STEP 4] Cleaning old deployment...
if exist site rd /s /q site
if exist mkdocs_base.yml del mkdocs_base.yml
if exist vercel.json del vercel.json

:: 7. Copy new files from temp to deploy branch
echo [STEP 5] Copying new files...
xcopy "%TEMP_DEPLOY%\site" site\ /E /I /Q /Y >nul
copy "%TEMP_DEPLOY%\mkdocs_base.yml" . /Y >nul
if exist "%TEMP_DEPLOY%\vercel.json" copy "%TEMP_DEPLOY%\vercel.json" . /Y >nul

:: 8. Clean up temp
rd /s /q "%TEMP_DEPLOY%"

:: 9. Commit and push
echo [STEP 6] Committing and Pushing...
git add -A
git commit --allow-empty -m "Deploy: %date% %time%"
git push origin deploy || (
    echo [ERROR] Push failed!
    git checkout main
    pause
    exit /b 1
)
echo [OK] Pushed to deploy branch

:: 10. Return to main branch
echo [STEP 7] Returning to main branch...
git checkout main
echo ============================================
echo DEPLOYMENT SUCCESSFUL!
echo ============================================
pause