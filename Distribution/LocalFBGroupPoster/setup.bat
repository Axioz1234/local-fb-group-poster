@echo off 
echo Installing Local FB Group Poster... 
echo Creating desktop shortcut... 
powershell "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut($WshShell.SpecialFolders('Desktop') + '\Local FB Group Poster.lnk'); $Shortcut.TargetPath = '%%~dp0LocalFBGroupPoster.exe'; $Shortcut.Save()" 
echo Installation complete! 
pause 
