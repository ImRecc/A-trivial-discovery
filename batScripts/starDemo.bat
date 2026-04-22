@echo off
chcp 65001
:: change code page as UTF-8
title sample
cls
:: clear screen
:: %1-firstParamSendIn
::~ use to remove " in both dir

if "%~1"=="" (
    echo [错误] 请将需要识别的报表照片拖到此文件上！
    pause
    exit
)

echo ------------------------------------------
echo 比对原型b-0.35
echo ------------------------------------------
set /p target=理论数据: 
::set prompt as target

:: 调用 Python，传递目标数字和图片路径
python meter_ocr_final.py %target% "%~1"
::send target to python's sys.argv[1]
::%~1 to sys.argv[2]

echo.
echo 测试完成，按任意键关闭窗口...
pause >nul

::pause >null to remove "press any key to continue"
