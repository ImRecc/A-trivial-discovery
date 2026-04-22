@echo off
chcp 65001
echo ========================================
echo 【离线安装依赖中】(4Win7 32bits)
echo 正在安装文件夹里所有.whl 包...
echo ========================================

for %%f in (*.whl) do (
:: a loop variable, must have double %
:: (*.whl) tells the for loop
:: to find all files in the current dir that match *.whl
:: the loop over them.
:: part of windows batch scripting's behaving
    echo 正在安装 %%f ...
    python -m pip install --no-deps --force-reinstall "%%f"
    echo.
)

echo ========================================
echo 所有包安装完成！
echo 现在测试百度SDK是否可用...
echo ========================================

python -c "from aip import AipOcr; print('安装成功！可以运行演示程序了。')" 2>nul || echo 安装失败
::python -c "<code>"
::Run the Python code inside the quotes directly from the command line, without using a .py file.
::2>null
:: 2=stderr, > redirect, nul=discard output
:: || run follow commands only when previous command FAILED

pause
