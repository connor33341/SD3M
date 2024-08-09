@echo off
@rem Start Server
echo Server Starting
echo Updating pip
python -m pip install --upgrade pip
echo Installing
python -m pip install -r ..\requirements.txt
cd ..\src
echo Running Server
python main.py
echo Finished
pause