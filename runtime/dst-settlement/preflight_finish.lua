-- Supplemental disposable-world smoke check. Never load during evaluation.
local G=_G
G.rawset(G,"SETTLEMENT_PREFLIGHT",true)
dofile("/home/steam/dst-settlement-v1/bridge.lua")
local M=dofile("/home/steam/dst-settlement-v1/common.lua")
local p=G.AllPlayers[1]
local function report(name,data) print("[SETTLEMENT_SMOKE] "..G.json.encode({name=name,data=data})) end
local function later(t,fn) p:DoTaskInTime(t,function() local ok,err=pcall(fn);if not ok then report("error",tostring(err)) end end) end
local rock
later(.5,function() G.settlement_test_execute({id=20,action="craft",recipe="pickaxe"}) end)
later(3,function()
    local pick=p.components.inventory:GetEquippedItem(G.EQUIPSLOTS.HANDS)
    assert(pick and pick.prefab=="pickaxe")
    G.settlement_test_execute({id=21,action="equip",target=pick.GUID})
    report("equip_already_equipped",G.settlement_observe().last_action)
    local x,_,z=p.Transform:GetWorldPosition()
    rock=G.SpawnPrefab("rock2");rock.Transform:SetPosition(x+4,0,z)
    report("mine_before",{workleft=rock.components.workable:GetWorkLeft()})
end)
later(4,function() G.settlement_test_execute({id=22,action="mine",target=rock.GUID}) end)
later(8,function()
    report("mine_after",{workleft=rock.components.workable:GetWorkLeft(),last_action=G.settlement_observe().last_action})
    local food,fire
    for _,e in ipairs(M.items(p)) do if e.prefab=="berries" then food=e;break end end
    for _,e in pairs(G.Ents) do if e.prefab=="firepit" and M.burning(e) and p:GetDistanceSqToInst(e)<=625 then fire=e;break end end
    assert(food and fire)
    report("cook_input",M.describe(food,p))
    G.settlement_test_execute({id=23,action="cook",target=fire.GUID,item=food.GUID})
end)
later(13,function()
    local stock,food=M.stock(p)
    report("cook_result",{stock=stock,food_hunger=food,last_action=G.settlement_observe().last_action})
    G.SetServerPaused(true)
end)
for _=1,5 do local s=G.TheFrontEnd:GetActiveScreen();if not s or s==p.HUD or s.name=="HUD" then break end;G.TheFrontEnd:PopScreen() end
G.SetServerPaused(false)
