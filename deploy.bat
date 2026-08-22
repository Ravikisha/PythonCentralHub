@echo off
REM Build locally, deploy prebuilt to Vercel (skips Vercel-side build).
setlocal

echo ==^> Building locally...
call npm run build
if errorlevel 1 goto :fail

echo ==^> Wrapping dist/ in Build Output API...
if exist ".vercel\output" rmdir /s /q ".vercel\output"
if errorlevel 1 goto :fail
mkdir ".vercel\output\static"
if errorlevel 1 goto :fail
> ".vercel\output\config.json" echo {"version":3}
xcopy "dist" ".vercel\output\static" /e /i /q /y >nul
if errorlevel 1 goto :fail

echo ==^> Deploying prebuilt to production...
call npx vercel deploy --prebuilt --prod
if errorlevel 1 goto :fail

echo ==^> Done.
exit /b 0

:fail
echo.
echo ==^> FAILED (exit code %errorlevel%^)
exit /b 1
