@echo off
setlocal

:: 检查是否有参数（即拖入的 Python 文件）
if "%~1"=="" (
    echo 请将一个 Python 文件拖入此脚本上运行。
    pause
    exit /b
)

:: 获取 Python 文件路径
set "PYFILE=%~1"

:: 获取当前目录（假设 npm start 要在当前目录运行）
set "CURDIR=%~dp0"

:: 启动 npm start 的 PowerShell 窗口
start "NPM Server" powershell -NoExit -Command "cd '%CURDIR%' ; npm start"

:: 启动 Python 脚本的 PowerShell 窗口
start "Python Script" powershell -NoExit -Command "python '%PYFILE%'"

endlocal
