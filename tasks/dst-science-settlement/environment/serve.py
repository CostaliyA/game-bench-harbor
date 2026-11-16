import os
import json,urllib.request
from mcp.server.fastmcp import FastMCP
mcp=FastMCP('dst')
URL=os.environ.get('DST_BRIDGE_URL','http://172.17.0.2:18775')
def call(path,data):
 req=urllib.request.Request(URL+path,json.dumps(data).encode(),{'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=45) as r:return json.load(r)
@mcp.tool()
def observe()->dict:
 """Start once if needed, then observe local world radius 25, inventory including backpack, stats, recipes and technology availability, and reward events. Game runs in real time while thinking. Never resets."""
 return call('/observe',{})
@mcp.tool()
def act(action:str,target:int=0,item:int=0,recipe:str='',x:float|None=None,z:float|None=None,seconds:float=2)->dict:
 """Perform one action and observe after 0.5-15 real seconds. Actions: move(x,z within 30 units); pick(target grass/sapling/berries); pickup(target ground item); chop(target tree, one swing, equip axe first); mine(target rock, equip pickaxe); attack(target enemy); craft(recipe from observe, structures x,z within 6 units; first science prototypes need a nearby science machine); equip(target inventory item); eat(target inventory food); cook(target fire,item food); fuel(target fire,item log/grass); wait. Use entity id from observation. Every call advances real time. Returns actual success/failure status; moving may still be in progress. No spawning, teleporting or reset."""
 data={k:v for k,v in locals().items() if v is not None};return call('/act',data)
if __name__=='__main__':mcp.run(transport='stdio')
