if not "%1"=="am_admin" (powershell start -verb runas '%0' am_admin & exit /b)

cd %0\..\

powershell.exe -File .\install.ps1