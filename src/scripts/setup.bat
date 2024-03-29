echo off
title space for Windows Installation
cls

SET mypath=%~dp0
SET apath=%mypath:~0,-8%
SET path=%path%;%mypath%\swigwin-space

echo -------------------------------------------
echo Welcome in AlexaPi installation for Windows
echo -------------------------------------------

echo Installing dependencies:

python3 -m pip install -r "%apath%\..\requirements.txt"

pause
cls

cd %apath%

copy config.template.yaml config.yaml

echo ######################################################################################################
echo IMPORTANT NOTICE:
echo You HAVE TO set up github.com/Space-Monkey-KD/space/ keys in the config.yaml file now
echo ######################################################################################################
pause

start python3.exe auth_web.py

echo =====
echo Done!
echo =====
pause
cls
echo ######################################################################################################
echo IMPORTANT NOTICE:
echo You may HAVE TO set up your system audio.
echo See on our wiki
echo ######################################################################################################
pause
