-- SL10002_ModRuntime V33 delayed in-game runtime. ASCII no BOM.
-- V33 changes V32's empty-screen behavior: it still waits until map_init has completed,
-- but then spawns near the initial visible camera area and prefers table-row based C API calls.
-- No VIP/sponsor/auth modification. No game.exe patch. No numeric direct call to lua_sceAddCha.

local PREV = rawget(_G,'__SL10002_MOD_RUNTIME_V33')
_G.__SL10002_MOD_RUNTIME_V33 = true

local LOG_FILE='SL10002_mod_runtime_v33.log'
local TRACE_FILE='SL10002_original_mechanics_v33_trace.txt'
local ADD_FILE='AddCha.log'
local STATUS_FILE='SL10002_fullmod_v33_status.txt'

local cfg = rawget(_G,'SL10002_MOD_CONFIG') or {
  enabled=true,
  dry_run=false,
  force_overlay=true,
  original_bridge=true,
  safe_api_only=true,
  control_id=1,
  player_id=1,
  owner=1,
  -- V33 positions: place validation objects near the initial visible camera area, not far off-screen.
  base_x=1450, base_y=780,
  npc_x=1500, npc_y=960,
  wave_x=1800, wave_y=1160,
  player_x=1439, player_y=800,
  -- These are candidates only. V33 uses AddCha/AddSceneObj wrappers, never raw sceAddCha(number,...).
  selector_sceneobj_candidates={12,4,15,3},
  base_sceneobj_candidates={12,4,15,3},
  selector_unit_candidates={109,2188,2189},
  npc_candidates={109,2188,2189,2054,2057},
  hero_candidates={2215,2223,2224,2227},
  wave_candidates={2215,2223,2224,2227},
  -- V33 barrier: only spawn after map init has completed.
  require_mapinit_done=true, -- V33: map_init return is accepted as map done; GameEvent_MapInit is optional
  require_game_start=false,
  post_mapinit_event_delay=1, -- wait at least one post-map event before overlay
  wave_every_event_ticks=10,
  spawn_hero_immediately=true,
  spawn_wave_immediately=true
}
_G.SL10002_MOD_CONFIG = cfg

local unpack_fn = unpack or table.unpack
local installed=false
local wrapper_installed=false
local hero_spawned=false
local wave_count=0
local install_attempts=0
local event_tick=0
local mapinit_seen=false
local mapinit_done=false
local mapjoin_seen=false
local gamestart_seen=false
local runtime_seen=false
local last_ready_state=''
local timer_hook_installed=false

local function now()
  local ok,v=pcall(os.date,'%Y-%m-%d %H:%M:%S')
  if ok then return v else return 'time' end
end
local function append(path,msg)
  pcall(function()
    local f=io.open(path,'a')
    if f then f:write(now()..' '..tostring(msg)..'\n'); f:close() end
  end)
end
local function log(msg) append(LOG_FILE,msg) end
local function trace(msg) append(TRACE_FILE,msg) end
local function addlog(msg) append(ADD_FILE,msg) end
local function status(msg) append(STATUS_FILE,msg) end
local function pack_args(...)
  local n=select('#',...); local t={}
  for i=1,n do t[#t+1]=tostring(select(i,...)) end
  return table.concat(t,',')
end
local function asnum(v, def) v=tonumber(v); if v==nil then return def end; return v end

local function lookup_row(tblname, id)
  local t=rawget(_G,tblname)
  if type(t)~='table' then return nil, 'no_'..tblname end
  local row=t[id]
  if row==nil then row=t[tostring(id)] end
  if type(row)=='table' then return row, 'ok' end
  return nil, tblname..'_missing_'..tostring(id)..'_type_'..type(row)
end

local function ready_state()
  local s='AddCha='..type(rawget(_G,'AddCha'))..
          ' AddSceneObj='..type(rawget(_G,'AddSceneObj'))..
          ' AddSceneObject='..type(rawget(_G,'AddSceneObject'))..
          ' sceAddCha='..type(rawget(_G,'sceAddCha'))..
          ' sceAddSceneObject='..type(rawget(_G,'sceAddSceneObject'))..
          ' tab_cha='..type(rawget(_G,'tab_cha'))..
          ' tab_sceneobj='..type(rawget(_G,'tab_sceneobj'))..
          ' AddTimer='..type(rawget(_G,'AddTimer'))..
          ' phase={join='..tostring(mapjoin_seen)..',mapinit='..tostring(mapinit_seen)..',mapdone='..tostring(mapinit_done)..',start='..tostring(gamestart_seen)..',runtime='..tostring(runtime_seen)..'}'
  if s~=last_ready_state then
    log('[READY_STATE] '..s)
    trace('[READY_STATE] '..s)
    status(s)
    last_ready_state=s
  end
end

local function safe_pcall(label, f, ...)
  if cfg.dry_run then log('[DRY] '..label..'('..pack_args(...)..')'); return true, 'dry' end
  local ok,a,b,c,d=pcall(f,...)
  if ok then log('[OK] '..label..'('..pack_args(...)..') => '..tostring(a)); return true,a end
  log('[ERR] '..label..'('..pack_args(...)..') err='..tostring(a)); return false,a
end

local function install_compat_wrappers()
  if wrapper_installed then return end
  wrapper_installed=true
  -- If original wrappers are absent but low-level API + tables exist, create compatible wrappers.
  -- IMPORTANT: the low-level C binding receives tab_cha[id], never numeric id.
  if type(rawget(_G,'AddCha'))~='function' and type(rawget(_G,'sceAddCha'))=='function' then
    rawset(_G,'__SL10002_V33_ADDCHA_WRAPPER_MARK',true)
    rawset(_G,'AddCha',function(id,x,y,dir,owner)
      local row,why=lookup_row('tab_cha', id)
      if type(row)~='table' then log('[WRAP_WAIT] AddCha row missing id='..tostring(id)..' '..tostring(why)); return nil end
      return rawget(_G,'sceAddCha')(row, x, y, dir or 0, owner or -1)
    end)
    log('[WRAP] installed AddCha(id,x,y,dir,owner) using tab_cha row + sceAddCha; no numeric raw call')
  end
  if type(rawget(_G,'AddSceneObj'))~='function' and (type(rawget(_G,'sceAddSceneObject'))=='function' or type(rawget(_G,'sceAddSceneObj'))=='function') then
    rawset(_G,'__SL10002_V33_SCENE_WRAPPER_MARK',true)
    rawset(_G,'AddSceneObj',function(id,x,y,dir,owner)
      local row,why=lookup_row('tab_sceneobj', id)
      if type(row)~='table' then log('[WRAP_WAIT] AddSceneObj row missing id='..tostring(id)..' '..tostring(why)); return nil end
      local low=rawget(_G,'sceAddSceneObject') or rawget(_G,'sceAddSceneObj')
      return low(row, x, y, dir or 180, owner or -1)
    end)
    log('[WRAP] installed AddSceneObj(id,x,y,dir,owner) using tab_sceneobj row + sceAddSceneObject')
  end
end

local function try_low_sce_addcha(id,x,y,dir,owner,label)
  local row,why=lookup_row('tab_cha', id)
  local low=rawget(_G,'sceAddCha')
  if type(row)~='table' or type(low)~='function' then return false, why or 'no_sceAddCha_or_row' end
  local ok,res=safe_pcall('sceAddChaTable/'..tostring(label), low, row,x,y,dir,owner)
  if ok then addlog('[V33_OK] '..tostring(label)..' via sceAddCha(tab_cha['..tostring(id)..']) args='..pack_args(id,x,y,dir,owner)); return true,res end
  return false,res
end

local function call_addcha_id(id,x,y,dir,owner,label)
  id=asnum(id,0); x=asnum(x,0); y=asnum(y,0); dir=asnum(dir,0); owner=asnum(owner,cfg.owner or 1)
  -- V33: prefer the proven safe signature: sceAddCha(tab_cha[id], x, y, dir, owner).
  -- V29 proved numeric raw calls show lua_sceAddCha parameter errors; V32's numeric AddCha path could succeed but stay invisible.
  local ok,res=try_low_sce_addcha(id,x,y,dir,owner,label)
  if ok then return true,res end
  local f=rawget(_G,'AddCha')
  if type(f)=='function' then
    -- Use the engine/map wrapper as fallback. This is kept because some maps implement AddCha(id,...).
    ok,res=safe_pcall('AddChaFallback/'..tostring(label), f, id,x,y,dir,owner)
    if ok then addlog('[V33_OK] '..tostring(label)..' via AddCha fallback args='..pack_args(id,x,y,dir,owner)); return true,res end
    return false,res
  end
  log('[WAIT_API] '..tostring(label)..' no usable AddCha/sceAddCha(tab_cha) path: '..tostring(res))
  return false,'no_AddCha'
end

local function call_addscene_id(id,x,y,dir,owner,label)
  id=asnum(id,0); x=asnum(x,0); y=asnum(y,0); dir=asnum(dir,180); owner=asnum(owner,-1)
  local row,why=lookup_row('tab_sceneobj', id)
  local low=rawget(_G,'sceAddSceneObject') or rawget(_G,'sceAddSceneObj')
  if type(row)=='table' and type(low)=='function' then
    local ok,res=safe_pcall('sceAddSceneTable/'..tostring(label), low, row,x,y,dir,owner)
    if ok then addlog('[V33_OK] '..tostring(label)..' via sceAddScene(tab_sceneobj['..tostring(id)..']) args='..pack_args(id,x,y,dir,owner)); return true,res end
  end
  local f=rawget(_G,'AddSceneObj') or rawget(_G,'AddSceneObject')
  if type(f)=='function' then
    -- Most observed maps expose AddSceneObj(id,x,y,dir,owner); use it as fallback.
    local ok,res=safe_pcall('AddSceneObjFallback/'..tostring(label), f, id,x,y,dir,owner)
    if ok then addlog('[V33_OK] '..tostring(label)..' via AddScene fallback args='..pack_args(id,x,y,dir,owner)); return true,res end
    return false,res
  end
  log('[WAIT_API] '..tostring(label)..' no usable scene API, row='..tostring(why))
  return false,'no_AddScene'
end

local function spawn_scene_group(label, ids, x, y)
  local any=false; local off=0
  for _,id in ipairs(ids or {}) do
    local ok=call_addscene_id(id,(x or 4750)+off,(y or 10650),180,-1,label..'_'..tostring(id))
    if ok then any=true; off=off+120 end
  end
  if not any then addlog('[V33_WAIT] '..label..' no scene object created yet') end
  return any
end
local function spawn_cha_group(label, ids, x, y, owner)
  local any=false; local off=0
  for _,id in ipairs(ids or {}) do
    local ok=call_addcha_id(id,(x or 2500)+off,(y or 8800),180,owner or cfg.owner or 1,label..'_'..tostring(id))
    if ok then any=true; off=off+80 end
  end
  if not any then addlog('[V33_WAIT] '..label..' no cha created yet') end
  return any
end

local function phase_allows_spawn(reason)
  if cfg.enabled==false then return false,'disabled' end
  if cfg.require_mapinit_done~=false and not mapinit_done then return false,'wait_mapinit_done_map_init_not_returned' end
  if cfg.require_game_start==true and not gamestart_seen and not runtime_seen then return false,'wait_game_start' end
  if event_tick < (cfg.post_mapinit_event_delay or 1) then return false,'wait_post_mapinit_event_delay_'..tostring(event_tick) end
  return true,'ok'
end

function SL10002_Mod_SpawnHero(reason)
  if hero_spawned then return 1 end
  local allowed,why=phase_allows_spawn('hero_'..tostring(reason))
  if not allowed then log('[PHASE_WAIT] hero '..tostring(why)); return 0 end
  trace('[SPAWN_HERO_REQUEST] reason='..tostring(reason))
  local ok=spawn_cha_group('hero_spawn_'..tostring(reason), cfg.hero_candidates, cfg.player_x or 1439, cfg.player_y or 800, cfg.owner or 1)
  if ok then hero_spawned=true; return 1 end
  return 0
end

function SL10002_Mod_SpawnWave(reason)
  local allowed,why=phase_allows_spawn('wave_'..tostring(reason))
  if not allowed then log('[PHASE_WAIT] wave '..tostring(why)); return 0 end
  wave_count=wave_count+1
  trace('[SPAWN_WAVE_REQUEST] wave='..tostring(wave_count)..' reason='..tostring(reason))
  local x=(cfg.wave_x or 9700) + wave_count*90
  local y=(cfg.wave_y or 11930)
  return spawn_cha_group('wave_'..tostring(wave_count), cfg.wave_candidates, x, y, 20) and 1 or 0
end

function SL10002_Mod_EnsureOverlay(reason)
  install_attempts=install_attempts+1
  ready_state()
  install_compat_wrappers()
  if installed then return 1 end
  local allowed,why=phase_allows_spawn(reason)
  if not allowed then
    log('[PHASE_WAIT] overlay reason='..tostring(reason)..' why='..tostring(why))
    status('overlay_wait='..tostring(why)..' reason='..tostring(reason)..' attempts='..tostring(install_attempts))
    return 0
  end
  trace('[INSTALL_ATTEMPT] #'..tostring(install_attempts)..' reason='..tostring(reason))
  local any=false
  any = spawn_scene_group('hero_selector_sceneobj', cfg.selector_sceneobj_candidates, cfg.base_x or 4750, cfg.base_y or 10650) or any
  any = spawn_scene_group('base_sceneobj', cfg.base_sceneobj_candidates, (cfg.base_x or 4750)+600, (cfg.base_y or 10650)+200) or any
  any = spawn_cha_group('selector_units', cfg.selector_unit_candidates, cfg.npc_x or 2500, cfg.npc_y or 8800, 9) or any
  any = spawn_cha_group('interaction_npc', cfg.npc_candidates, (cfg.npc_x or 2500)+400, cfg.npc_y or 8800, 9) or any
  if any then
    installed=true
    log('[INSTALL_OK] V33 visible overlay installed near initial camera. reason='..tostring(reason))
    addlog('[V33_INSTALL_OK] visible_overlay reason='..tostring(reason))
    status('installed=1 visible_overlay reason='..tostring(reason))
    if cfg.spawn_hero_immediately~=false then pcall(SL10002_Mod_SpawnHero, 'overlay_install') end
    if cfg.spawn_wave_immediately~=false then pcall(SL10002_Mod_SpawnWave, 'overlay_install') end
    return 1
  end
  log('[INSTALL_WAIT] V33 map phase ready but AddCha/AddScene APIs not usable. reason='..tostring(reason))
  status('installed=0 api_wait reason='..tostring(reason)..' attempts='..tostring(install_attempts))
  return 0
end

local function after_event(name,...)
  trace('[EVENT] '..tostring(name)..' args='..pack_args(...))
  if name=='GameEventJoinGame' then mapjoin_seen=true end
  if name=='map_init' then mapinit_seen=true; mapinit_done=true; trace('[MAPINIT_DONE] map_init returned, treating as full map init boundary') end
  if name=='GameEvent_MapInit' then mapinit_done=true; trace('[MAPINIT_DONE] GameEvent_MapInit observed') end
  if name=='GameEvent_GameStart' or name=='GameEvent_RunGameLogic' or name=='GameEvent_GameLogic' or name=='GameEvent_StartGame' then gamestart_seen=true; runtime_seen=true end
  if mapinit_done then event_tick=event_tick+1 end
  -- V33: when original click/hero selection hooks fire, try a real hero near the current visible area.
  if name=='GameOp_AddHero' or name=='game_event_decide_select_cha' or name=='game_event_end_select' or name=='TriggerAddChaFromCoordinate' or name=='chabirth' then
    pcall(SL10002_Mod_SpawnHero, name)
  end
  ready_state()
  install_compat_wrappers()
  if cfg.force_overlay~=false then SL10002_Mod_EnsureOverlay('after_'..tostring(name)) end
  if installed and event_tick>0 and (event_tick % (cfg.wave_every_event_ticks or 12)==0) then SL10002_Mod_SpawnWave('event_tick_'..tostring(event_tick)) end
  if name=='game_event_CallBackHero' or name=='SelectHero' or name=='ChooseHero' or name=='HeroSelect' or name=='OnHeroSelected' or name=='GameEvent_CityClick' or name=='GameEvent_UnitClick' then
    SL10002_Mod_SpawnHero(name)
  end
end

local function wrap(name)
  local real=rawget(_G,name)
  if type(real)~='function' then return false end
  local mark='__SL10002_V33_REAL_'..name
  if rawget(_G,mark) then return true end
  rawset(_G,mark,real)
  rawset(_G,name,function(...)
    trace('[HOOK_BEFORE] '..name..' args='..pack_args(...))
    local r={pcall(real,...)}
    if r[1] then trace('[HOOK_AFTER] '..name..' ok') else trace('[HOOK_ERR] '..name..' err='..tostring(r[2])) end
    pcall(after_event,name,...)
    if not r[1] then error(r[2]) end
    return unpack_fn(r,2)
  end)
  log('[HOOK] '..name)
  return true
end

local watch_names={
 'map_init','GameEvent_MapInit','GameEventJoinGame','GameEvent_GameStart','GameEvent_StartGame','GameEvent_RunGameLogic','GameEvent_GameLogic',
 'GameEventClick','GameEvent_Click','GameEventObjClick','GameEvent_ChaClick','GameEventSceneObjClick','GameEvent_SceneObjClick',
 'GameEventSelectCha','GameEvent_SelectCha','GameEvent_UnitClick','GameEvent_CityClick',
 'game_event_CallBackHero','Check_If_TestHeroNpc','openChooseHeroCoverPanel',
 'SelectHero','select_hero','ChooseHero','choose_hero','HeroSelect','hero_select','OnHeroSelected','on_hero_selected',
 'CreateHero','create_hero','BirthHero','birth_hero','HeroBirth','hero_birth','BaseBirth','base_birth',
 'MonsterWave','monster_wave','SpawnWave','spawn_wave','WaveTimer','wave_timer','CreateMonster','create_monster'
}
for _,n in ipairs(watch_names) do wrap(n) end

local function interesting(k)
  if type(k)~='string' then return false end
  if k=='AddCha' or k=='AddSceneObj' or k=='AddSceneObject' or k=='tab_cha' or k=='tab_sceneobj' or k=='TriggerAddChaFromCoordinate' or k=='AddTimer' then return true end
  local n=string.lower(k)
  return string.find(n,'hero') or string.find(n,'select') or string.find(n,'choose') or string.find(n,'click') or string.find(n,'city') or string.find(n,'base') or string.find(n,'birth') or string.find(n,'wave') or string.find(n,'monster') or string.find(n,'timer') or k=='map_init' or k=='GameEvent_MapInit'
end

local mt=getmetatable(_G) or {}
local old_newindex=mt.__newindex
mt.__newindex=function(t,k,v)
  rawset(t,k,v)
  if interesting(k) then
    trace('[WATCH_ASSIGN] '..tostring(k)..' type='..type(v))
    if type(v)=='function' then wrap(k) end
    -- V33 does not spawn on assignment before map init. It only refreshes wrappers and status.
    pcall(function() ready_state(); install_compat_wrappers(); if mapinit_done then SL10002_Mod_EnsureOverlay('assign_after_mapinit_'..tostring(k)) end end)
  end
  if type(old_newindex)=='function' then return end
end
pcall(setmetatable,_G,mt)

function SrvScriptInfo(a,b) log('[CALL] SrvScriptInfo '..pack_args(a,b)..' => 1'); return 1 end
function load_rolesdk(mapid,data) log('[CALL] load_rolesdk '..pack_args(mapid,data)..' => 1'); return 1 end
function SL10002_ModRuntime_V33_Status()
  return {version='V33',installed=installed,wave_count=wave_count,hero_spawned=hero_spawned,attempts=install_attempts,mapinit_done=mapinit_done,gamestart_seen=gamestart_seen,event_tick=event_tick}
end

log('[BOOT] SL10002 ModRuntime V33 loaded. visible_post_mapinit=1 previous='..tostring(PREV))
trace('[BOOT] V33 loaded. Only hooks are installed before map_init. After map_init, V33 spawns visible validation units near initial camera using sceAddCha(tab_cha[id]) when available.')
status('boot=1 delayed=1 previous='..tostring(PREV))
ready_state()
install_compat_wrappers()
-- CRITICAL: no SL10002_Mod_EnsureOverlay call here. This prevents early AddCha before 10002.o finishes loading.
