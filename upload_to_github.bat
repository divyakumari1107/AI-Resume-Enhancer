@echo off
echo ========================================================
echo Uploading AI-Resume-Enhancer to GitHub
echo Repository: https://github.com/divyakumari1107/AI-Resume-Enhancer
echo ========================================================
echo.
cd /d "%~dp0"

echo Current Git Status:
git status
echo.

echo Pushing to GitHub...
echo (A browser window or prompt may appear asking you to sign in as divyakumari1107)
echo.

git push -u origin main

echo.
if %ERRORLEVEL% EQU 0 (
    echo ========================================================
    echo SUCCESS: All files have been uploaded to GitHub!
    echo Visit: https://github.com/divyakumari1107/AI-Resume-Enhancer
    echo ========================================================
) else (
    echo ========================================================
    echo If push failed due to login, you can also push with a Personal Access Token:
    echo git push https://YOUR_TOKEN@github.com/divyakumari1107/AI-Resume-Enhancer.git main
    echo ========================================================
)

pause
