@echo off
chcp 65001 >nul
title Python 依赖安装器
rem 不要搞没用的，直接 pip install pipreqs, pipreqs ./ --encoding=utf-8, 然后pip install -r requirements.txt
:: 判断有无输入文件
if "%~1"=="" (
    color 0c
    echo [error] 请把需要安装依赖的.py文件拖上来
    pause
    exit /b
)

echo =================================
echo 处理 "%~nx1" 中
echo =================================

rem 核心 Python 脚本 (注意：代码里不能有百分号，否则会炸)
python -c "import sys, re, os; f=open(sys.argv[1], encoding='utf-8').read(); pkgs=set(re.findall(r'^(?:import|from)\s+([a-zA-Z0-9_]+)', f, re.M)); [os.system(f'pip install {p}') for p in pkgs if p not in sys.builtin_module_names]" "%~1"

echo.
echo ======================
echo [完成]
echo ======================
pause
