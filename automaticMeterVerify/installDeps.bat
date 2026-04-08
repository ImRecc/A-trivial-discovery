@echo off
chcp 65001
echo ========================================
echo 【离线安装依赖中】Win7 32位
echo 正在安装文件夹里【所有】.whl 包...
echo ========================================

for %%f in (*.whl) do (
    echo 正在安装 %%f ...
    python -m pip install --no-deps --force-reinstall "%%f"
    echo.
)

echo ========================================
echo 所有包安装完成！
echo 现在测试百度SDK是否可用...
echo ========================================

python -c "from aip import AipOcr; print('安装成功！可以运行演示程序了。')" 2>nul || echo ❌ 测试失败

pause
