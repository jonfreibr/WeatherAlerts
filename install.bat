@echo off
h:
cd \_BRMCApps\WeatherAlerts
echo Installing Python 3.11.5
python-3.11.5-amd64.exe /passive
echo upgrading pip
%LocalAppData%\Programs\Python\Python311\python.exe -m pip install --upgrade pip -q
echo Adding package requients
%LocalAppData%\Programs\Python\Python311\Scripts\pip.exe install -r requirements.txt -q
echo Copying files
if not exist %USERPROFILE%\Walerts md %USERPROFILE%\Walerts
copy /y walerts.py %USERPROFILE%\Walerts
copy /y "Weather Alerts.lnk" %USERPROFILE%\Desktop
echo Done with installation
start %USERPROFILE%"\Desktop\Weather Alerts.lnk"