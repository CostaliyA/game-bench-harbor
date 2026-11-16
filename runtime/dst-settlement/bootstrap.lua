-- Administrative preparation, before any trial/model request. Only use after
-- restoring the full baseline and restarting the game process.
local G=_G
assert(not G.rawget(G,"SETTLEMENT_PREFLIGHT"),"restart after mechanic preflight")
local p=G.AllPlayers[1]
assert(p and G.TheWorld.ismastersim and not G.TheNet:IsOnlineMode())
local M=dofile("/home/steam/dst-settlement-v1/common.lua")
assert(#M.items(p)==0,"baseline is not empty")
assert(G.TheWorld.state.cycles==0,"baseline is not day 1")
p.components.playercontroller:Enable(false)
p.components.locomotor:Stop()
p.components.locomotor:Clear()
p.components.playercontroller.directwalking=false
p.components.playercontroller.dragwalking=false
p.components.playercontroller.draggingonground=false
-- Exact position from the original immutable baseline/initial-observation.json.
-- Normalize before the trial so desktop setup cannot shift its start position.
p.Physics:Teleport(-264.53506469727,0,-197.64739990234)
local clock=G.TheWorld.components.clock
local saved=clock:OnSave()
saved.cycles=0;saved.phase="day"
saved.totaltimeinphase=saved.segs.day*G.TUNING.SEG_TIME
saved.remainingtimeinphase=saved.totaltimeinphase
clock:OnLoad(saved)
for _=1,5 do
    local screen=G.TheFrontEnd:GetActiveScreen()
    if not screen or screen.name=="HUD" or screen==p.HUD then break end
    G.TheFrontEnd:PopScreen()
end
p:DoTaskInTime(.2,function()
    for _,name in ipairs({"health","hunger","sanity"}) do p.components[name]:SetPercent(1) end
    G.SetServerPaused(true)
    dofile("/home/steam/dst-settlement-v1/camera.lua")
    dofile("/home/steam/dst-settlement-v1/observer.lua")
    dofile("/home/steam/dst-settlement-v1/bridge.lua")
    print("[SETTLEMENT_BASELINE_READY] day1 empty full-stats; complete observation sent to bridge")
end)
G.SetServerPaused(false)
