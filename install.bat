@echo off
echo Sourcing from: %~dp0
echo Installing Python 3.11.5
"%~dp0\python-3.11.5-amd64.exe" /passive
echo upgrading pip
%LocalAppData%\Programs\Python\Python311\python.exe -m pip install --upgrade pip
echo Adding package requirements
%LocalAppData%\Programs\Python\Python311\Scripts\pip.exe install -r "%~dp0\requirements.txt"
echo Copying files
if not exist %USERPROFILE%\Walerts md %USERPROFILE%\Walerts
copy /y "%~dp0\walerts.py" %USERPROFILE%\Walerts
copy /y "%~dp0\WAlertWidgetDefaults.reg" %USERPROFILE%\Walerts
copy /y "%~dp0\*.png" %USERPROFILE%\Walerts
copy /y "%~dp0\Weather Alerts.lnk" %USERPROFILE%\Desktop
if not exist %USERPROFILE%\Walerts\walerts.cfg copy /y %~dp0\walerts.json %USERPROFILE%\Walerts
echo Done with installation
start %USERPROFILE%"\Desktop\Weather Alerts.lnk"