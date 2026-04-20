-- ==========================================
-- CE 智能读取脚本：直接读 CT 表里的记录
-- ==========================================

-- 1. ！！！在这里填入你刚才在 CE 列表里起的名字！！！
local recordName = "HP" 
local filePath = "D:\\DGL_socket\\game_val.txt"
local lastValue = -1

os.execute('mkdir "D:\\DGL_socket"') 

local timer = createTimer(nil)
timer.Interval = 50 
timer.OnTimer = function()
    local al = getAddressList()
    -- 直接通过名字获取那一条记录
    local rec = al.getMemoryRecordByDescription(recordName)

    if rec ~= nil then
        -- rec.Value 会自动处理所有指针、浮点数转换，直接返回界面上显示的文本
        local valStr = rec.Value
        
        -- 确保读到的不是空值或是 "??" (地址失效时会显示 ??)
        if valStr ~= nil and valStr ~= "??" then
            -- 把字符串转成数字
            local currentValue = tonumber(valStr)
            
            if currentValue ~= nil and currentValue ~= lastValue then
                local f = io.open(filePath, "w")
                if f then
                    f:write(tostring(currentValue))
                    f:close()
                    lastValue = currentValue
                    -- print("智能更新数值: " .. currentValue) -- 调试用，觉得吵可以注释掉
                end
            end
        end
    end
end

print("【智能指针监控已启动】正在紧盯记录: " .. recordName)
