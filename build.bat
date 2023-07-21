pushd %~dp0
if not exist build\ mkdir build
copy src build\ /y
pyarmor gen src\env.py -O build
pyinstaller --onefile -i scorpio.ico build\scorpio.py