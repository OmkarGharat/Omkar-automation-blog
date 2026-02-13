@echo off
echo ============================================
echo SAFE Secure Build and Deploy
echo ============================================
echo.

:: Safety Check: Make sure we're on main branch
for /f "tokens=*" %%i in ('git branch --show-current') do set CURRENT_BRANCH=%%i

if not "%CURRENT_BRANCH%"=="main" (
    echo ERROR: You must be on 'main' branch to deploy!
    echo Current branch: %CURRENT_BRANCH%
    echo.
    echo Run: git checkout main
    pause
    exit /b 1
)

echo [OK] Starting from main branch...
echo.

:: 1. Build and Encrypt
echo [STEP 1] Building and Encrypting Site...
call .\venv\Scripts\activate
python publish.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Build failed. Cannot deploy.
    pause
    exit /b %ERRORLEVEL%
)

echo [OK] Build successful!
echo.

:: 2. Verify site folder exists
if not exist site (
    echo [ERROR] site folder not found!
    echo Something went wrong with the build.
    pause
    exit /b 1
)

echo [STEP 2] Preparing Deployment...

:: 3. Create a temporary folder OUTSIDE the git repo structure
set "TEMP_DEPLOY=%TEMP%\mkdocs_deploy_%RANDOM%"
echo Creating temp folder: %TEMP_DEPLOY%

:: 4. Copy the built site to temp location (SAFETY: keeps it safe during branch switch)
xcopy site "%TEMP_DEPLOY%\site\" /E /I /Q /Y
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to copy site to temp location
    pause
    exit /b 1
)

:: 5. Copy vercel.json if it exists
if exist vercel.json (
    copy vercel.json "%TEMP_DEPLOY%\vercel.json" /Y
)

echo [OK] Files backed up to temp location
echo.

:: 6. Switch to deploy branch (FILES ARE SAFE IN TEMP FOLDER)
echo [STEP 3] Switching to deploy branch...
git checkout deploy

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to switch to deploy branch
    echo Cleaning up temp folder...
    rd /s /q "%TEMP_DEPLOY%"
    git checkout main
    pause
    exit /b 1
)

echo [OK] On deploy branch
echo.

:: 7. Clean ONLY the site folder (not the entire directory!)
echo [STEP 4] Cleaning old deployment...
if exist site (
    rd /s /q site
    echo [OK] Old site folder removed
)

:: 8. Copy fresh site from temp location
echo [STEP 5] Copying new site...
xcopy "%TEMP_DEPLOY%\site" site\ /E /I /Q /Y

:: 9. Copy vercel.json if it exists
if exist "%TEMP_DEPLOY%\vercel.json" (
    copy "%TEMP_DEPLOY%\vercel.json" vercel.json /Y
)

echo [OK] New files copied
echo.

:: 10. Clean up temp folder
echo Cleaning up temp folder...
rd /s /q "%TEMP_DEPLOY%"

:: 11. Git operations
echo [STEP 6] Committing and Pushing...

:: Check if there are changes to commit
git add -A
git commit --allow-empty -m "Deploy: %date% %time%"
git push origin deploy
    
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Push failed
        git checkout main
        pause
        exit /b 1
    )
    
    echo [OK] Pushed to deploy branch

echo.

:: 12. Return to main branch
echo [STEP 7] Returning to main branch...
git checkout main

if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Failed to return to main branch
    echo You may need to manually run: git checkout main
    pause
    exit /b 1
)

echo [OK] Back on main branch
echo.
echo ============================================
echo DEPLOYMENT SUCCESSFUL!
echo ============================================
echo.
echo Your site has been deployed to the 'deploy' branch.
echo Check your hosting platform for the live site.
echo.
echo All your files on main branch are SAFE!
echo.
pause