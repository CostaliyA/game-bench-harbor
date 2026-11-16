local M = {}
M.recipes = {"axe", "pickaxe", "campfire", "firepit", "torch", "researchlab", "rope", "spear", "backpack", "armorgrass"}
function M.items(p)
    return p.components.inventory:FindItems(function() return true end)
end
function M.stock(p)
    local counts, food = {}, 0
    for _, e in ipairs(M.items(p)) do
        local n = e.components.stackable and e.components.stackable:StackSize() or 1
        counts[e.prefab] = (counts[e.prefab] or 0) + n
        if e.components.edible and p.components.eater:CanEat(e) then
            food = food + math.max(0, e.components.edible:GetHunger(p)) * n
        end
    end
    return counts, food
end
function M.owned(e, p)
    return e and e:IsValid() and e.components.inventoryitem and e.components.inventoryitem:GetGrandOwner() == p
end
function M.burning(e)
    return e and e:IsValid() and e.components.burnable and e.components.burnable:IsBurning()
end
function M.describe(e, p)
    local x, _, z = e.Transform:GetWorldPosition()
    local w = e.components.workable
    local action = w and w:CanBeWorked() and w:GetWorkAction()
    local t = {id=e.GUID, prefab=e.prefab, x=x, z=z,
        count=e.components.stackable and e.components.stackable:StackSize() or 1,
        pickable=e.components.pickable and e.components.pickable:CanBePicked() or false,
        pickup=e.components.inventoryitem and not e.components.inventoryitem.owner or false,
        chop=action == ACTIONS.CHOP, mine=action == ACTIONS.MINE,
        burning=M.burning(e) or false}
    if e.components.equippable then t.equipped=e.components.equippable:IsEquipped() end
    if e.components.finiteuses then t.durability=e.components.finiteuses:GetPercent() end
    if e.components.fueled then t.fuel=e.components.fueled:GetPercent() end
    if e.components.perishable then t.freshness=e.components.perishable:GetPercent() end
    if e.components.edible and p.components.eater:CanEat(e) then
        t.food_hunger=e.components.edible:GetHunger(p)
        t.food_health=e.components.edible:GetHealth(p)
        t.food_sanity=e.components.edible:GetSanity(p)
    end
    if e.components.inventoryitem and M.owned(e,p) then
        t.container=e.components.inventoryitem.owner == p and "inventory" or "backpack"
    end
    if e.components.health then t.health=e.components.health.currenthealth end
    if e.components.cookable then t.cook_product=e.components.cookable.product end
    return t
end
return M
