package.path = ""
package.cpath = ""
local f = loadfile("E:/玩家原创/神龙地图启动器/data/core/edt2.o")
if f then
    f()
    print("tempConfigLuaMapOptionInfo:")
    for i, v in ipairs(tempConfigLuaMapOptionInfo) do
        print("  " .. i .. " = {" .. v[1] .. ", " .. v[2] .. "}")
    end
    print("helper_get004:")
    local t = helper_get004()
    for i, v in ipairs(t) do print("  " .. i .. " = " .. v) end
    print("helper_get005:")
    t = helper_get005()
    for i, v in ipairs(t) do print("  " .. i .. " = " .. v) end
    print("helper_get006: " .. helper_get006())
    print("GetMapOptionDisplay: " .. GetMapOptionDisplay())
else
    print("Failed to load")
end
