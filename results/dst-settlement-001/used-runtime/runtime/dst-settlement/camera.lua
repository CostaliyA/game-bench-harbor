-- Fixed recording orientation; preserves normal camera tracking and game actions.
local G = _G
local cam = assert(G.TheCamera, 'camera is not ready')
if not cam.dst_fixed_heading_original_update then
    cam.dst_fixed_heading_original_update = cam.Update
end
local heading = 45
cam.Update = function(self, ...)
    self.heading = heading
    self.headingtarget = heading
    self.headingdelta = nil
    self.lastheadingdelta = nil
    return self.dst_fixed_heading_original_update(self, ...)
end
cam:SetHeadingTarget(heading)
cam.heading = heading
print('[DST_FIXED_CAMERA]', heading)
