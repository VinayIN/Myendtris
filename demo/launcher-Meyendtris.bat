:: Launcher version 2015-04-03
echo off
cd .\src\
cls
call:menuloop
goto:eof


:: MENU TITLE

:menu_Meyendtris
:menu_
goto:eof

:: MENU ENTRIES

:menu_1   Calibration (Alpha)
ppython launcher.py -m Alpha-02-001-calibration -e studies/calibrationdisplaysettings.prc
goto:eof

:menu_2   Classifier Test (Bar)
ppython launcher.py -m Alpha-01-001-bar -e studies/calibrationdisplaysettings.prc
goto:eof

:menu_3   Meyendtris
ppython launcher.py -m Meyendtris -e studies/meyendtrisdisplaysettings.prc
goto:eof

:menu_

:menu_-   options
goto:optionsloop
goto:eof















:: OPTIONS MENU ENTRIES

:option_s   toggle LSL SessionID
IF EXIST %USERPROFILE%\lsl_api\lsl_api.cfg (
    echo DELETING %USERPROFILE%\lsl_api\lsl_api.cfg
    echo DELETING %USERPROFILE%\lsl_api\
    echo Ctrl+C to cancel
    pause
    del %USERPROFILE%\lsl_api\lsl_api.cfg
    rmdir %USERPROFILE%\lsl_api\
) ELSE (
    echo writing %USERPROFILE%\lsl_api\lsl_api.cfg setting SessionID to phypa
    echo Ctrl+C to cancel
    pause
    if not exist %USERPROFILE%\lsl_api\ mkdir %USERPROFILE%\lsl_api
    >%USERPROFILE%\lsl_api\lsl_api.cfg echo [lab]
    >>%USERPROFILE%\lsl_api\lsl_api.cfg echo SessionID = phypa
)
echo.
goto:eof



:: STUFF

:menuloop
call:logo
for /f "tokens=1,2,* delims=_" %%A in ('"findstr /b /c:":menu_" "%~f0""') do echo.  %%B  %%C
set choice=
echo.&set /p choice="> " || goto:eof
echo.&call:menu_%choice%
goto:menuloop
    
:optionsloop
call:statuscheck
for /f "tokens=1,2,* delims=_" %%A in ('"findstr /b /c:":option_" "%~f0""') do echo.  %%B  %%C
set choice=
echo.&set /p choice="> " || goto:eof
echo.&call:option_%choice%
goto:optionsloop
    
:statuscheck
echo   host: %COMPUTERNAME%
echo   cwd: %CD%
IF EXIST %USERPROFILE%\lsl_api\lsl_api.cfg (
    echo   lsl_api.cfg found in user directory
) ELSE (
    echo   lsl_api.cfg not found in user directory
)
echo.
goto:eof
 
:logo
echo.
echo   _______                     _____  _           _____
echo  ^|__   __^|                   ^|  __ \^| ^|         ^|  __ \ /\   :)
echo     ^| ^| ___  __ _ _ __ ___   ^| ^|__) ^| ^|__  _   _^| ^|__) /  \
echo     ^| ^|/ _ \/ _` ^| '_ ` _ \  ^|  ___/^| '_ \^| ^| ^| ^|  ___/ /\ \
echo     ^| ^|  __^| (_^| ^| ^| ^| ^| ^| ^| ^| ^|    ^| ^| ^| ^| ^|_^| ^| ^|  / ____ \
echo     ^|_^|\___^|\__,_^|_^| ^|_^| ^|_^| ^|_^|    ^|_^| ^|_^|\__, ^|_^| /_/    \_\
echo                                             __/ '
echo   Physiological Parameters for Adaptation  :___/  teamphypa.org
echo.
echo.
goto:eof