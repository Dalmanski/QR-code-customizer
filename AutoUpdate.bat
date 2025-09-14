@echo off
cd "%USERPROFILE%\OneDrive\Documents\Code\Python tkinter\QR code customizer"

echo === Building executable with PyInstaller ===
pyinstaller ^
  --noconsole ^
  --onefile ^
  --icon=icon.ico ^
  "QR Code Customizer.py"

set VERSION=1.1.0

echo === Creating ZIP archive ===
powershell -Command "Compress-Archive -Path 'dist\*' -DestinationPath 'QR_code_customizer_%VERSION%.zip' -Force"

echo === Done! ===