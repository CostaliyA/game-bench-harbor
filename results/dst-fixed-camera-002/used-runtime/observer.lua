local G = _G
local function install()
 if not G.TheWorld.ismastersim then return end
 G.rawset(G, "c_eval_start", function()
  local p = G.AllPlayers[1]
  assert(p and #G.AllPlayers == 1 and p.prefab == "wilson", "Requires one Wilson")
  assert(not G.TheNet:IsOnlineMode(), "Requires offline world")
  assert(G.TheWorld.state.cycles == 0 and G.TheWorld.state.season == "autumn", "Requires day 1 autumn")
  assert(p.components.health:GetPercent() >= .999 and p.components.hunger:GetPercent() >= .999 and p.components.sanity:GetPercent() >= .999, "Requires full starting stats")
  assert(not p._eval_started, "Evaluation already started")
  assert(G.TheWorld.state.isday and G.TheWorld.state.time < .05, "Start in first 5% of a day")
  assert(G.next(p.components.inventory.itemslots) == nil and G.next(p.components.inventory.equipslots) == nil, "Start with empty inventory")
  assert(not p:HasTag("playerghost") and not p.components.health:IsDead(), "Requires alive player")
  p._eval_started = true
  local seq, done, milestones, fires, night_seconds = 0, false, {}, {}, 0
  local maxima = {}
  local start_cycle, lasttime = G.TheWorld.state.cycles, G.GetTime()
  local function emit(kind, data)
   data = data or {}; data.type=kind; data.seq=seq;seq=seq+1
   data.game_time=G.GetTime();data.cycle=G.TheWorld.state.cycles;data.phase=G.TheWorld.state.phase
   print("[DST_EVAL] " .. G.json.encode(data))
   G.TheSim:QueryServer("http://127.0.0.1:18765/event",function() end,"POST",G.json.encode(data))
  end
  local function mark(name)
   if not done and not milestones[name] then milestones[name]=true;emit("milestone",{name=name}) end
  end
  local function finish(kind, data) if not done then emit(kind,data);done=true;G.SetServerPaused(true) end end
  local function stock(prefab)
   local total=0
   for _,item in pairs(p.components.inventory.itemslots) do
    if item.prefab==prefab then total=total+(item.components.stackable and item.components.stackable:StackSize() or 1) end
   end
   return total
  end
  p:ListenForEvent("builditem",function(_,data)
   if data and data.item and data.item.prefab=="axe" then mark("crafted_axe") end
  end)
  p:ListenForEvent("buildstructure",function(_,data)
   if data and data.item and data.item.prefab=="campfire" then
    fires[data.item.GUID]=data.item;mark("built_campfire")
   end
  end)
  p:ListenForEvent("death",function() finish("death") end)
  G.rawset(G,"c_eval_abort",function() finish("abort") end)
  G.rawset(G,"dst_eval_timeout",function() finish("timeout") end)
  emit("start",{task="dst-first-night-v1",character=p.prefab,online=G.TheNet:IsOnlineMode()})
  p:DoPeriodicTask(.5,function()
   if done then return end
   local now=G.GetTime();local dt=now-lasttime;lasttime=now
   if p:HasTag("playerghost") or p.components.health:IsDead() then finish("death");return end
   for _,name in ipairs({"cutgrass","twigs","flint"}) do maxima[name]=math.max(maxima[name] or 0,stock(name)) end
   if maxima.cutgrass>=3 and maxima.twigs>=1 and maxima.flint>=1 then mark("starter_materials") end
   if milestones.crafted_axe and stock("log")>=2 then mark("gathered_logs") end
   if G.TheWorld.state.isnight then
    for _,fire in pairs(fires) do
     if fire:IsValid() and fire.components.burnable and fire.components.burnable:IsBurning() and p:GetDistanceSqToInst(fire)<=36 then
      night_seconds=night_seconds+dt;break
     end
    end
    if night_seconds>=30 then mark("night_fire_30s") end
   end
   if G.TheWorld.state.cycles>start_cycle and G.TheWorld.state.isday then
    finish("dawn",{alive=true,health=p.components.health.currenthealth,hunger=p.components.hunger.current,night_fire_seconds=night_seconds})
   end
  end)
 end)
 print("[DST_EVAL_READY] Use c_eval_start() at validated starting snapshot.")
end
install()
