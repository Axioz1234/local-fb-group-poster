@echo off
echo Creating distribution package...

rem Check if Distribution folder exists
if not exist "Distribution" (
    echo Error: Distribution folder not found!
    pause
    exit /b
)

rem Create the ZIP file
powershell "Compress-Archive -Path '.\Distribution\LocalFBGroupPoster' -DestinationPath 'LocalFBGroupPoster_Setup.zip' -Force"

echo.
echo Distribution package created: LocalFBGroupPoster_Setup.zip
echo.
echo You can find the ZIP file in: %CD%\LocalFBGroupPoster_Setup.zip
echo.
pause
