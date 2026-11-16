local G = _G
local M = dofile("/home/steam/dst-settlement-v1/common.lua")
local url="http://127.0.0.1:18775"
local p=G.AllPlayers[1]
assert(p and G.TheWorld.ismastersim)
-- Isolate the evaluated agent from held desktop keys/mouse input. The model's
-- buffered actions still use the native locomotor, inventory and builder.
p.components.playercontroller:Enable(false)
p.components.locomotor:Stop()
p.components.locomotor:Clear()
p.components.playercontroller.directwalking=false
p.components.playercontroller.dragwalking=false
p.components.playercontroller.draggingonground=false
local active=false
local last={id=0,status="ready"}
local function post(path,data) G.TheSim:QueryServer(url..path,function() end,"POST",G.json.encode(data)) end
local function observe()
    local x,_,z=p.Transform:GetWorldPosition(); local inv, nearby, recipes={}, {}, {}
    for _,v in ipairs(M.items(p)) do table.insert(inv,M.describe(v,p)) end
    for _,v in ipairs(G.TheSim:FindEntities(x,0,z,25,nil,{"INLIMBO","FX","NOCLICK","DECOR"})) do
        if v~=p and v.prefab then table.insert(nearby,M.describe(v,p)) end
    end
    table.sort(nearby,function(a,b) return (a.x-x)^2+(a.z-z)^2<(b.x-x)^2+(b.z-z)^2 end)
    while #nearby>90 do table.remove(nearby) end
    local b=p.components.builder
    for _,name in ipairs(M.recipes) do
        local r=G.AllRecipes[name]; local ingredients={}
        for _,v in ipairs(r.ingredients) do ingredients[v.type]=v.amount end
        local known=b:KnowsRecipe(r)
        local proto=b:CanLearn(name) and G.CanPrototypeRecipe(r.level,b.accessible_tech_trees)
        recipes[name]={ingredients=ingredients,known=known,can_prototype_here=proto,
            has_ingredients=b:HasIngredients(r),can_build=b:HasIngredients(r) and (known or proto)}
    end
    return {time=G.GetTime(),cycle=G.TheWorld.state.cycles,phase=G.TheWorld.state.phase,day_fraction=G.TheWorld.state.time,
        x=x,z=z,health=p.components.health.currenthealth,hunger=p.components.hunger.current,sanity=p.components.sanity.current,
        alive=not p:HasTag("playerghost") and not p.components.health:IsDead(),inventory=inv,nearby=nearby,recipes=recipes,
        last_action=last,active=active,camera_heading=G.TheCamera:GetHeading(),camera_target=G.TheCamera:GetHeadingTarget(),
        progress=G.rawget(G,"settlement_progress") and G.settlement_progress() or nil}
end
local function execute(c)
    last={id=c.id,status="running",action=c.action}
    if c.action=="wait" then last.status="success"; return end
    local x,_,z=p.Transform:GetWorldPosition()
    if c.action=="move" then
        assert(type(c.x)=="number" and type(c.z)=="number" and (c.x-x)^2+(c.z-z)^2<=900,"move limited to 30 units")
        assert(G.TheWorld.Map:IsAboveGroundAtPoint(c.x,0,c.z),"destination is not land")
        p.components.locomotor:GoToPoint(G.Vector3(c.x,0,c.z),nil,true); last.status="moving"; return
    end
    if c.action=="craft" then
        local allowed=false; for _,n in ipairs(M.recipes) do if n==c.recipe then allowed=true end end
        assert(allowed,"recipe not allowed")
        local r=G.AllRecipes[c.recipe]; local b=p.components.builder
        assert(b:HasIngredients(r),"missing ingredients")
        assert(b:KnowsRecipe(r) or (b:CanLearn(c.recipe) and G.CanPrototypeRecipe(r.level,b.accessible_tech_trees)),"recipe needs nearby science machine")
        if r.placer then
            local pt=G.Vector3(c.x or x,0,c.z or z)
            assert(p:GetDistanceSqToPoint(pt)<=36,"build within 6 units")
            assert(G.TheWorld.Map:CanDeployRecipeAtPoint(pt,r,0,p),"invalid placement")
            local id=c.id
            assert(b:MakeRecipe(r,pt,0,nil,function() if last.id==id then last.status="success" end end),"craft failed")
        else
            -- The native menu path checks technology, consumes ingredients and unlocks prototypes.
            local id=c.id
            local onbuild
            onbuild=function(_,data)
                if data and data.item and data.item.prefab==r.product then
                    if last.id==id then last.status="success" end
                    p:RemoveEventCallback("builditem",onbuild)
                end
            end
            p:ListenForEvent("builditem",onbuild)
            b:MakeRecipeFromMenu(r)
            p:DoTaskInTime(10,function() p:RemoveEventCallback("builditem",onbuild) end)
        end
        return
    end
    local t=G.Ents[tonumber(c.target)]; local obj=G.Ents[tonumber(c.item)]
    local map={pick="PICK",pickup="PICKUP",chop="CHOP",mine="MINE",equip="EQUIP",eat="EAT",cook="COOK",fuel="ADDFUEL",attack="ATTACK"}
    assert(map[c.action],"invalid action")
    if c.action=="equip" or c.action=="eat" then obj=t;t=nil end
    if t then assert(t:IsValid() and p:GetDistanceSqToInst(t)<=625,"target outside observation") end
    if obj then assert(M.owned(obj,p),"item not in inventory/backpack") end
    if c.action=="equip" and obj and obj.components.equippable and obj.components.equippable:IsEquipped() then
        last.status="success"; return
    end
    if c.action=="pick" then assert(t and t.components.pickable and t.components.pickable:CanBePicked(),"target is not a harvestable plant; ground items use pickup") end
    if c.action=="pickup" then assert(t and t.components.inventoryitem and not t.components.inventoryitem.owner,"target is not a loose ground item") end
    if c.action=="chop" or c.action=="mine" then
        local action=G.ACTIONS[map[c.action]]
        assert(t and t.components.workable and t.components.workable:CanBeWorked() and t.components.workable:GetWorkAction()==action,"target cannot be worked; inspect drops")
        local hand=p.components.inventory:GetEquippedItem(G.EQUIPSLOTS.HANDS)
        assert(hand and hand.components.tool and hand.components.tool:CanDoAction(action),"equip the correct tool first")
    end
    assert(t or obj,"missing target or item")
    local a=G.BufferedAction(p,t,G.ACTIONS[map[c.action]],obj); local id=c.id
    a:AddSuccessAction(function() if last.id==id then last.status="success" end end)
    a:AddFailAction(function() if last.id==id then last.status="failed" end end)
    p.components.locomotor:PushAction(a,true)
end
G.rawset(G,"settlement_observe",observe)
if G.rawget(G,"SETTLEMENT_PREFLIGHT") == true then G.rawset(G,"settlement_test_execute",execute) end
G.rawset(G,"settlement_begin",function()
    assert(not active,"already active")
    G.settlement_start(); active=true
    -- Close startup menus through the game's own UI; no blind click on the HUD.
    for _=1,5 do
        local screen=G.TheFrontEnd:GetActiveScreen()
        if not screen or screen.name=="HUD" or screen==p.HUD then break end
        G.TheFrontEnd:PopScreen()
    end
    G.SetServerPaused(false)
    post("/state",observe())
end)
p:DoPeriodicTask(.5,function() post("/state",observe()) end)
local querying=false
p:DoPeriodicTask(.25,function()
    if not active or querying then return end
    querying=true
    G.TheSim:QueryServer(url.."/command",function(body,ok)
        querying=false
        if ok and body and #body>2 then
            local good,c=pcall(G.json.decode,body)
            if good and c and c.action then
                local success,err=pcall(execute,c)
                if not success then last={id=c.id,status="error",error=tostring(err)} end
            end
        end
    end,"GET")
end)
post("/state",observe())
print("[DST_SETTLEMENT_READY]")
