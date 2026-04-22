@echo off
chcp 65001
:: change code page as UTF-8
title sample ::cmd窗口的名字
cls
:: clear screen
:: %1-firstParamSendIn
::~ use to remove " in both dir

if "%~1"=="" ( ::%1代表第一个参数，如果拖某个文件过来，那么第一个参数就是这个文件的绝对路径，~用来去除两边的双引号
    echo [错误] 请将需要识别的报表照片拖到此文件上！
    pause
    exit
)

echo ------------------------------------------
echo 比对原型b-0.35
echo ------------------------------------------
set /p target=理论数据: 
::set prompt as target
::set /p 用来暂停，等待用户输入
::单独 /p是无效的

:: 调用 Python，传递目标数字和图片路径
python meter_ocr_final.py %target% "%~1"
::send target to python's sys.argv[1]
::%~1 to sys.argv[2]
:: sys.argv[0]----always the script's name
:: %target%, double %, for it's normal environment variable, 
:: %VAR%, as it should be
:: %1, %2, %~1, %~2, ...
::batch script positional parameters, the arguments passed to the .bat file

echo.
echo 测试完成，按任意键关闭窗口...
pause >nul

::pause >null to remove "press any key to continue"
