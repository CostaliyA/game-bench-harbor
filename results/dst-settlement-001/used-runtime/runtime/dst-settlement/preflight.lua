-- Mechanic smoke test ONLY, on a disposable world. Restore the full
-- frozen baseline and restart the game before evaluation. Not an oracle run.
local G=_G
G.SETTLEMENT_PREFLIGHT=true
dofile("/home/steam/dst-settlement-v1/bridge.lua")
local p=G.AllPlayers[1]
local function report(name,data)
    if data.inventory then
        local inventory={}
        for _,e in ipairs(data.inventory) do
            inventory[e.prefab]={count=e.count,equipped=e.equipped,container=e.container}
        end
        local structures={}
        for _,e in ipairs(data.nearby) do
            if e.prefab=="researchlab" or e.prefab=="firepit" then table.insert(structures,e.prefab) end
        end
        data={inventory=inventory,structures=structures,last_action=data.last_action,x=data.x,z=data.z}
    end
    G.TheSim:QueryServer("http://127.0.0.1:18775/preflight",function() end,"POST",G.json.encode({name=name,data=data}))
    print("[SETTLEMENT_PREFLIGHT] "..name)
end
local audit={}
local x,_,z=p.Transform:GetWorldPosition()
for _,e in pairs(G.Ents) do
    if e:IsValid() and e.prefab and e.Transform and not e:HasTag("INLIMBO") then
        local dist=math.sqrt(p:GetDistanceSqToInst(e))
        if dist<=250 and (e.prefab=="rock2" or e.prefab=="rocks" or e.prefab=="flint" or e.prefab=="goldnugget" or e.prefab=="berrybush" or e.prefab=="berrybush2" or e.prefab=="carrot_planted") then
            local v=audit[e.prefab] or {count=0,nearest=dist}; v.count=v.count+1;v.nearest=math.min(v.nearest,dist);audit[e.prefab]=v
        end
    end
end
report("natural_resources_within_250",audit)
for name,n in pairs({log=20,rocks=40,goldnugget=3,cutgrass=40,twigs=30,flint=10,berries=5}) do
    local item=G.SpawnPrefab(name)
    if item.components.stackable then item.components.stackable:SetStackSize(n) end
    p.components.inventory:GiveItem(item)
end
local n=0
local test_rock
local function action(c)
    n=n+1;c.id=n
    local ok,err=pcall(G.settlement_test_execute,c)
    report("action",{command=c,ok=ok,error=not ok and tostring(err) or nil})
end
local function later(t,fn)
    p:DoTaskInTime(t,function()
        local ok,err=pcall(fn)
        if not ok then report("test_error",{at=t,error=tostring(err)}) end
    end)
end
later(.5,function() action({action="craft",recipe="pickaxe"}) end)
later(3,function()
    report("pickaxe",G.settlement_observe())
    action({action="craft",recipe="researchlab",x=x+4,z=z})
end)
later(7,function()
    report("science_machine",G.settlement_observe())
    action({action="move",x=x+3,z=z})
end)
later(10,function() action({action="craft",recipe="backpack"}) end)
later(13,function() report("backpack",G.settlement_observe()); action({action="craft",recipe="rope"}) end)
later(16,function() action({action="craft",recipe="spear"}) end)
later(19,function()
    report("spear",G.settlement_observe())
    action({action="craft",recipe="firepit",x=x+4,z=z+5})
end)
later(23,function()
    report("firepit",G.settlement_observe())
    local pick=p.components.inventory:GetEquippedItem(G.EQUIPSLOTS.HANDS)
    if not pick or pick.prefab~="pickaxe" then pick=p.components.inventory:FindItem(function(e)return e.prefab=="pickaxe" end) end
    assert(pick,"pickaxe was not crafted")
    action({action="equip",target=pick.GUID})
    local rock=G.SpawnPrefab("rock2");rock.Transform:SetPosition(x+6,0,z-4)
    test_rock=rock
end)
later(26,function() action({action="mine",target=test_rock.GUID}) end)
later(30,function()
    report("mine",{last_action=G.settlement_observe().last_action,workleft=test_rock.components.workable:GetWorkLeft()})
    local fire=G.TheSim:FindEntities(x+4,0,z+5,2,{"campfire"})[1]
    if not fire then for _,e in pairs(G.Ents) do if e.prefab=="firepit" and p:GetDistanceSqToInst(e)<=625 then fire=e;break end end end
    local food=p.components.inventory:FindItem(function(e)return e.prefab=="berries" end)
    if fire and food then action({action="cook",target=fire.GUID,item=food.GUID}) end
end)
later(34,function()
    local food=p.components.inventory:FindItem(function(e)return e.prefab=="berries" end)
    if food then
        p.components.inventory:RemoveItem(food,true)
        p.components.inventory:GetOverflowContainer():GiveItem(food)
    end
    report("cook_and_overflow",G.settlement_observe())
    G.SetServerPaused(true)
end)
for _=1,5 do
    local screen=G.TheFrontEnd:GetActiveScreen()
    if not screen or screen.name=="HUD" or screen==p.HUD then break end
    G.TheFrontEnd:PopScreen()
end
G.SetServerPaused(false)
