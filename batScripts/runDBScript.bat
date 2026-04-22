@echo off
setlocal

if "%~1"=="" (
    echo 请将一个 Python 文件拖入此脚本上运行。
    pause
    exit /b
)

:: 获取 Python 文件路径
set "PYFILE=%~1"
::safe assignment pattern , double queto""

:: 获取当前目录（假设 npm start 要在当前目录运行）
set "CURDIR=%~dp0"
:: %~dp0 stands for current script's absolute directory

:: 启动 npm start 的 PowerShell 窗口
start "NPM Server" powershell -NoExit -Command "title 'NPM Server'; cd '%CURDIR%' ; npm start"

:: 启动 Python 脚本的 PowerShell 窗口
start "Python Script" powershell -NoExit -Command "title 'python script'; python '%PYFILE%'"

endlocal

::setlocal ... endlocal
::this makes any variable changes local
::no global or systematical level changes
