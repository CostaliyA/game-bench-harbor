local G = _G
local json = G.json or require('json')
local url='http://127.0.0.1:18765'
local function post(path,data) TheSim:QueryServer(url..path,function() end,'POST',json.encode(data)) end
local p=AllPlayers[1]
assert(p and TheWorld.ismastersim)
local active=false
local last={id=0,status='ready'}
local function item(e)
 local x,y,z=e.Transform:GetWorldPosition()
 return {id=e.GUID,prefab=e.prefab,x=x,z=z,count=e.components.stackable and e.components.stackable:StackSize() or 1,
 pickable=e.components.pickable and e.components.pickable:CanBePicked() or false,
 pickup=e.components.inventoryitem and not e.components.inventoryitem.owner or false,
 chop=e.components.workable and e.components.workable:GetWorkAction()==ACTIONS.CHOP or false,
 burning=e.components.burnable and e.components.burnable:IsBurning() or false}
end
local function observe()
 local x,y,z=p.Transform:GetWorldPosition();local inv={};local nearby={}
 for _,v in pairs(p.components.inventory.itemslots) do table.insert(inv,item(v)) end
 for _,v in pairs(p.components.inventory.equipslots) do local t=item(v);t.equipped=true;table.insert(inv,t) end
 for _,v in ipairs(TheSim:FindEntities(x,y,z,25, nil, {'INLIMBO','FX','NOCLICK','DECOR'})) do
  if v~=p and v.prefab then table.insert(nearby,item(v)) end
 end
 table.sort(nearby,function(a,b)return (a.x-x)^2+(a.z-z)^2<(b.x-x)^2+(b.z-z)^2 end)
 while #nearby>90 do table.remove(nearby) end
 local recipes={}
 for _,name in ipairs({'axe','campfire','torch'}) do
  local r=AllRecipes[name]; local ingredients={}
  for _,v in ipairs(r.ingredients) do ingredients[v.type]=v.amount end
  recipes[name]={ingredients=ingredients,can_build=p.components.builder:HasIngredients(r)}
 end
 return {time=GetTime(),cycle=TheWorld.state.cycles,day_fraction=TheWorld.state.time,phase=TheWorld.state.phase,
 x=x,z=z,health=p.components.health.currenthealth,hunger=p.components.hunger.current,sanity=p.components.sanity.current,
 alive=not p:HasTag('playerghost') and not p.components.health:IsDead(),inventory=inv,nearby=nearby,recipes=recipes,last_action=last,active=active}
end
local function execute(c)
 last={id=c.id,status='running',action=c.action}
 if c.action=='wait' then last.status='success';return end
 local x,y,z=p.Transform:GetWorldPosition()
 if c.action=='move' then
  assert(type(c.x)=='number' and type(c.z)=='number' and (c.x-x)^2+(c.z-z)^2<=900,'move limited to 30 units')
  p.components.locomotor:GoToPoint(Vector3(c.x,0,c.z),nil,true);last.status='moving';return
 end
 if c.action=='craft' then
  assert(c.recipe=='axe' or c.recipe=='campfire' or c.recipe=='torch','recipe not allowed')
  local r=AllRecipes[c.recipe];local b=p.components.builder
  assert(b:KnowsRecipe(r) and b:HasIngredients(r),'missing ingredients or unknown recipe')
  local pt=Vector3(c.x or x,0,c.z or z)
  assert(p:GetDistanceSqToPoint(pt)<=36,'build within 6 units')
  if r.placer then assert(TheWorld.Map:CanDeployRecipeAtPoint(pt,r,0,p),'invalid placement') end
  local id=c.id
  assert(b:MakeRecipe(r,pt,0,nil,function()if last.id==id then last.status='success' end end),'craft failed');return
 end
 local t=Ents[tonumber(c.target)]
 local obj=Ents[tonumber(c.item)]
 local map={pick='PICK',pickup='PICKUP',chop='CHOP',equip='EQUIP',eat='EAT',cook='COOK',fuel='ADDFUEL'}
 assert(map[c.action],'invalid action')
 if c.action=='equip' or c.action=='eat' then obj=t;t=nil end
 if t then assert(t:IsValid() and p:GetDistanceSqToInst(t)<=625,'target outside observation') end
 if obj then assert(obj.components.inventoryitem and obj.components.inventoryitem.owner==p,'item not in inventory') end
 local a=BufferedAction(p,t,ACTIONS[map[c.action]],obj)
 local id=c.id
 a:AddSuccessAction(function() if last.id==id then last.status='success' end end)
 a:AddFailAction(function() if last.id==id then last.status='failed' end end)
 p.components.locomotor:PushAction(a,true)
end
_G.dst_eval_observe=observe
_G.dst_eval_begin=function()
 assert(not active);c_eval_start();active=true;SetServerPaused(false)
end
p:DoPeriodicTask(.5,function() post('/state',observe()) end)
local querying=false
p:DoPeriodicTask(.25,function()
 if not active or querying then return end
 querying=true
 TheSim:QueryServer(url..'/command',function(body,ok)
  querying=false
  if ok and body and #body>2 then
   local good,c=pcall(json.decode,body)
   if good and c and c.action then
    local success,err=pcall(execute,c)
    if not success then last={id=c.id,status='error',error=tostring(err)} end
   end
  end
 end,'GET')
end)
post('/state',observe())
print('[DST_BRIDGE_READY]')
