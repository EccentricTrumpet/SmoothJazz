# Backend
Run backend/main.py:
pip3 install beaker  
pip3 install bottle  
pip3 install cheroot  
pip3 install --upgrade google-api-python-client  
pip3 install --upgrade oauth2client  

# Frontend
1. Follow https://cordova.apache.org/ to install Cordova  
1. Website, do: cordova run browser  
1. iOS, install ios simulator and do: cordova run ios -- --buildFlag="-UseModernBuildSystem=0"  
1. Android, install AVD manager and do: cordova run android -- --gradleArg=-PcdvMinSdkVersion=22  
1. Electron and osX currently don't work  
