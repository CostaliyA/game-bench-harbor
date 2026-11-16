local G = _G
local M = dofile("/home/steam/dst-settlement-v1/common.lua")
assert(G.TheWorld.ismastersim)
G.rawset(G, "settlement_start", function()
    local p = G.AllPlayers[1]
    assert(p and #G.AllPlayers == 1 and p.prefab == "wilson", "one Wilson required")
    assert(not G.TheNet:IsOnlineMode(), "offline required")
    assert(G.TheWorld.state.cycles == 0 and G.TheWorld.state.season == "autumn", "day 1 autumn required")
    assert(G.TheWorld.state.isday and G.TheWorld.state.time < .05, "morning required")
    for _, name in ipairs({"health", "hunger", "sanity"}) do assert(p.components[name]:GetPercent() >= .999, "full starting stats required") end
    assert(#M.items(p) == 0 and not p:HasTag("playerghost"), "alive and empty required")
    assert(not p._settlement_started, "already started")
    assert(not p.components.builder.freebuildmode and not p.components.health.invincible, "cheats enabled")
    p._settlement_started = true
    local seq, done, milestones = 0, false, {}
    local crafted, labs, fires = {}, {}, {}
    local hunger_gained, last_time = 0, G.GetTime()
    local night_seconds = {[0]=0, [1]=0}
    local function emit(kind, data)
        data=data or {}; data.type=kind; data.seq=seq; seq=seq+1
        data.game_time=G.GetTime(); data.cycle=G.TheWorld.state.cycles; data.phase=G.TheWorld.state.phase
        print("[DST_SETTLEMENT] " .. G.json.encode(data))
        G.TheSim:QueryServer("http://127.0.0.1:18775/event", function() end, "POST", G.json.encode(data))
    end
    local function mark(name)
        if not done and not milestones[name] then milestones[name]=true; emit("milestone", {name=name}) end
    end
    local function camp()
        local nearest_lab, nearest_fire, distance
        for _, lab in pairs(labs) do
            if lab:IsValid() then
                for _, fire in pairs(fires) do
                    if fire:IsValid() and fire.prefab=="firepit" and lab:GetDistanceSqToInst(fire)<=144 then
                        local d=p:GetDistanceSqToInst(lab)
                        if not distance or d<distance then nearest_lab=lab;nearest_fire=fire;distance=d end
                    end
                end
            end
        end
        return nearest_lab, nearest_fire
    end
    local function status()
        local stock, food=M.stock(p); local lab, fire=camp()
        local body=p.components.inventory:GetEquippedItem(G.EQUIPSLOTS.BODY)
        local spear=false
        for id in pairs(crafted.spear or {}) do
            local e=G.Ents[id]
            if M.owned(e,p) and (not e.components.finiteuses or e.components.finiteuses:GetPercent()>0) then spear=true end
        end
        return {alive=not p:HasTag("playerghost") and not p.components.health:IsDead(),
            health=p.components.health.currenthealth, hunger=p.components.hunger.current, sanity=p.components.sanity.current,
            stock=stock, food_hunger=food, hunger_gained=hunger_gained,
            camp_intact=lab~=nil, at_camp=lab~=nil and p:GetDistanceSqToInst(lab)<=144,
            backpack_equipped=body~=nil and body.prefab=="backpack" and crafted.backpack~=nil and crafted.backpack[body.GUID]==true,
            spear_held=spear, night_seconds=night_seconds, milestones=milestones}
    end
    local function finish(kind)
        if not done then done=true; emit(kind, status()); G.SetServerPaused(true) end
    end
    G.rawset(G, "settlement_progress", status)
    G.rawset(G, "settlement_timeout", function() finish("timeout") end)
    p:ListenForEvent("death", function() finish("death") end)
    p:ListenForEvent("builditem", function(_, data)
        if done or not data or not data.item then return end
        local e=data.item; crafted[e.prefab]=crafted[e.prefab] or {}; crafted[e.prefab][e.GUID]=true
        if crafted.axe and crafted.pickaxe then mark("tools") end
        if e.prefab=="spear" then mark("spear") end
    end)
    p:ListenForEvent("buildstructure", function(_, data)
        if done or not data or not data.item then return end
        local e=data.item
        if e.prefab=="researchlab" then labs[e.GUID]=e; mark("science_machine") end
        if e.prefab=="firepit" or e.prefab=="campfire" then fires[e.GUID]=e end
    end)
    p:ListenForEvent("hungerdelta", function(_, data)
        if not done and data and data.delta and data.delta>0 then
            hunger_gained=hunger_gained+data.delta
            if hunger_gained>=60 then mark("nutrition") end
        end
    end)
    emit("start", {task="dst-science-settlement-v1", character=p.prefab, online=false})
    p:DoPeriodicTask(.5, function()
        if done then return end
        local now=G.GetTime(); local dt=now-last_time; last_time=now
        if p:HasTag("playerghost") or p.components.health:IsDead() then finish("death"); return end
        if p.components.builder.freebuildmode or p.components.health.invincible then finish("invalid"); return end
        local stock=M.stock(p)
        if crafted.pickaxe and (stock.goldnugget or 0)>=1 and (stock.rocks or 0)>=4 then mark("minerals") end
        local s=status()
        if s.backpack_equipped then mark("backpack") end
        if s.camp_intact then mark("camp") end
        if G.TheWorld.state.isnight then
            local cycle=G.TheWorld.state.cycles
            local safe=false
            if cycle==0 then
                local hand=p.components.inventory:GetEquippedItem(G.EQUIPSLOTS.HANDS)
                safe=hand and hand.prefab=="torch" and crafted.torch and crafted.torch[hand.GUID]
                    and hand.components.fueled and hand.components.fueled.currentfuel>0
                for _, f in pairs(fires) do
                    if M.burning(f) and p:GetDistanceSqToInst(f)<=36 then safe=true end
                end
            elseif cycle==1 then
                for _, lab in pairs(labs) do
                    if lab:IsValid() then
                        for _, f in pairs(fires) do
                            if f.prefab=="firepit" and M.burning(f) and lab:GetDistanceSqToInst(f)<=144 and p:GetDistanceSqToInst(f)<=36 then safe=true end
                        end
                    end
                end
            end
            if safe and night_seconds[cycle] then night_seconds[cycle]=night_seconds[cycle]+dt end
            if night_seconds[0]>=30 then mark("first_night") end
            if night_seconds[1]>=30 then mark("second_night") end
        end
        if G.TheWorld.state.cycles>=2 and G.TheWorld.state.isday then finish("day3_dawn") end
    end)
end)
