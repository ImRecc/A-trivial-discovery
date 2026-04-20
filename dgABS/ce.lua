-- CE 监控脚本
local targetAddress = "0x282FE1DB7D4" -- 地址
local filePath = "D:\\DGL_socket\\game_val.txt" -- 确保 C 盘有 temp 文件夹，或者改成别的路径
local lastValue = -1

local timer = createTimer(nil) -- 创建了没有父对象(nil)的全局计时器
timer.Interval = 50 -- 50毫秒扫一次，比 Python 快，保证不漏掉瞬时伤害
timer.OnTimer = function() -- function() ... end 是一个函数可以直接赋值给变量或对象的字段
    local currentValue = readInteger(targetAddress) -- 如果是浮点数改用 readFloat
    if currentValue ~= nil and currentValue ~= lastValue then
        local f = io.open(filePath, "w")
        if f then
            f:write(tostring(currentValue))
            f:close()
            lastValue = currentValue
            -- print("检测到变化，已更新文件: " .. currentValue) -- 调试用
        end
    end
end
print("CE 监控已启动，正在盯着地址: " .. targetAddress)
