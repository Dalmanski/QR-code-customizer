@echo off
cd "%USERPROFILE%\OneDrive\Documents\Code\Python tkinter\QR code customizer"

echo === Building executable with PyInstaller ===
pyinstaller ^
  --noconsole ^
  --onefile ^
  --icon=icon.ico ^
  "QR Code Customizer.py"

echo === Creating ZIP archive ===
powershell -Command "Compress-Archive -Path 'dist\*' -DestinationPath 'QR_code_customizer.zip' -Force"

echo === Done! ===