@echo off
echo Creating distribution...

:: Get user's desktop path
for /f "tokens=2*" %%a in ('reg query "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders" /v Desktop') do set desktop=%%b
echo Desktop path: %desktop%

:: Get current date and time for version
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set version=%datetime:~0,8%_%datetime:~8,6%

:: Create temp directory
mkdir temp_dist
echo Created temp directory

:: Create facebook_cookies.json (empty json file)
echo {} > temp_dist\facebook_cookies.json

:: Create LocalFBGroupPoster.exe using PyInstaller
pyinstaller --onefile --noconsole main.py --name LocalFBGroupPoster
copy dist\LocalFBGroupPoster.exe temp_dist\
rmdir /s /q build
rmdir /s /q dist
del LocalFBGroupPoster.spec

:: Create setup.bat
(
echo @echo off
echo start LocalFBGroupPoster.exe
) > temp_dist\setup.bat

:: Create zip file using PowerShell with version number on desktop
powershell Compress-Archive -Path temp_dist\* -DestinationPath "%desktop%\FacebookPoster_v%version%.zip" -Force
echo Created FacebookPoster_v%version%.zip on Desktop

:: Clean up
rmdir /s /q temp_dist
echo Cleaned up temporary files

echo Distribution created as FacebookPoster_v%version%.zip on your Desktop
echo Location: %desktop%\FacebookPoster_v%version%.zip
pause
