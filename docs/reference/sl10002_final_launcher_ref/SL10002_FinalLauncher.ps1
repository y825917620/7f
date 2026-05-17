param(
    [ValidateSet("Host", "Client", "Single")]
    [string]$Mode = "Host",
    [string]$HostIP = "",
    [string]$PlayerName = "Player1",
    [ValidateRange(1,24)]
    [int]$PlayerSlot = 1,
    [ValidateSet("ControlOnly", "FramePulse", "Type3Pulse", "Stable", "Type3", "TurnStream")]
    [string]$ProtocolVariant = "ControlOnly"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

# V24: generate a map-author protocol/runtime ConfigLua in ASCII/no-BOM.
# This file is a local runtime context source used by the map script layer.
# It does NOT spoof VIP/sponsor fields and is NOT used to fabricate network option_info.
function Write-SL10002ConfigLuaV45 {
    param(
        [string]$RootDir,
        [int]$ControlId
    )
    try {
        $src = Join-Path $RootDir 'config.lua'
        $vals = @{}
        if (Test-Path -LiteralPath $src -PathType Leaf) {
            $bytes = [System.IO.File]::ReadAllBytes($src)
            # Try UTF8 and ANSI-compatible decoding only for extracting simple numeric option pairs.
            $txt = [System.Text.Encoding]::Default.GetString($bytes)
            foreach ($m in [regex]::Matches($txt, '\{\s*(\d+)\s*,\s*(-?\d+)\s*\}')) {
                $idx = [int]$m.Groups[1].Value
                $val = [int]$m.Groups[2].Value
                if ($idx -ge 0 -and $idx -le 9) { $vals[$idx] = $val }
            }
            if ($vals.Count -eq 0) {
                $txt = [System.Text.Encoding]::UTF8.GetString($bytes)
                foreach ($m in [regex]::Matches($txt, '\{\s*(\d+)\s*,\s*(-?\d+)\s*\}')) {
                    $idx = [int]$m.Groups[1].Value
                    $val = [int]$m.Groups[2].Value
                    if ($idx -ge 0 -and $idx -le 9) { $vals[$idx] = $val }
                }
            }
        }
        if (-not $vals.ContainsKey(0)) { $vals[0] = 1 }
        for ($i=1; $i -le 9; $i++) { if (-not $vals.ContainsKey($i)) { $vals[$i] = 0 } }
        if ($ControlId -lt 1) { $ControlId = 1 }
        if ($ControlId -gt 24) { $ControlId = 24 }

        $pairs = New-Object System.Collections.Generic.List[string]
        $values = New-Object System.Collections.Generic.List[string]
        for ($i=0; $i -le 9; $i++) {
            $pairs.Add(('{' + $i + ' , ' + $vals[$i] + '}'))
            $values.Add([string]$vals[$i])
        }

        # Keep all generated Lua strictly ASCII to avoid Lua 5.1 BOM/encoding parse errors.
        $lua = @()
        $lua += '-- SL10002 V45 generated config.lua. ASCII no BOM. LAN ordinary user runtime.'
        $lua += 'local function __sl10002_log(msg)'
        $lua += '  local ok, err = pcall(function()'
        $lua += "    local f = io.open('SL10002_map_protocol_v45.log', 'a')"
        $lua += "    if f then f:write(tostring(os.date('%Y-%m-%d %H:%M:%S')) .. ' ' .. tostring(msg) .. '\\n'); f:close() end"
        $lua += '  end)'
        $lua += 'end'
        $lua += 'function helper_get004() return {10002,1,1,24} end'
        $lua += ('function helper_get005() return {' + ($values -join ',') + '} end')
        $lua += ('tempConfigLuaMapOptionInfo = { ' + ($pairs -join ',') + ',}')
        $lua += ('if type(SetCurrentControlID) == "function" then SetCurrentControlID(' + $ControlId + ') end')
        $lua += 'function GetMapOptionInfo() return tempConfigLuaMapOptionInfo end'
        $lua += "function helper_get006() return '10002' end"
        $lua += 'function GetMapOptionDisplay() return 1 end'
        $lua += 'function SrvScriptInfo(a,b) __sl10002_log("[CALL] SrvScriptInfo("..tostring(a)..","..tostring(b)..") => ordinary_connected"); return 1 end'
        $lua += 'function load_rolesdk(mapid, data) __sl10002_log("[CALL] load_rolesdk("..tostring(mapid)..","..tostring(data)..") => ordinary_connected"); return 1 end'
        $lua += 'function SL10002_RuntimeProtocolInfo() return { mapid=10002, control_id=' + $ControlId + ', mode="lan", vip=0, sponsor=0 } end'
        $lua += ''
        $lua += '-- SL10002 V45 map-chain diagnostic hooks. No object spawning, no VIP/sponsor modification.'
        $lua += 'local __sl10002_unpack = unpack or (table and table.unpack)'
        $lua += 'local __sl10002_chain_targets = {'
        $lua += '  ''map_init'',''GameEvent_MapInit'',''GameEventJoinGame'',''GameEvent_GameStart'',''GameEvent_StartGame'',''GameEvent_RunGameLogic'',''GameEvent_GameLogic'','
        $lua += '  ''TgrMainTimer'',''CustomEventTimer'',''TriggerAddChaFromCoordinate'',''tgr_GetSideBirthPoint'',''GetSessionPlayerInfo'',''GetSessionPlayerInfoEx'','
        $lua += '  ''AddCha'',''lua_sceAddCha'',''sceAddCha'',''lua_AddCha_New'',''lua_AddCha_NewEx'',''lua_AddCha_NewEx_Use_ContrlID'','
        $lua += '  ''AddSceneObj'',''AddSceneObject'',''sceAddSceneObject'',''map_addchar'',''map_addsceneobj'',''player_station'',''player_mode_station'',''player_bar_station'',''tgr_map_init'',''tgr_maptab_init'',''map_init_0000'',''map_init_0004'',''map_init_allregion'',''lua_AddTimer'',''AddTimer'',''lua_EnableTimer'',''lua_EnableAllTimer'''
        $lua += '}'
        $lua += 'local __sl10002_chain_wrapped = {}'
        $lua += 'local function __sl10002_chain_args(...)'
        $lua += '  local n = select(''#'', ...); local out = {}'
        $lua += '  for i=1,n do out[#out+1] = tostring(select(i, ...)) end'
        $lua += '  return table.concat(out, '','')'
        $lua += 'end'
        $lua += 'local function __sl10002_chain_wrap(name, fn)'
        $lua += '  if type(fn) ~= ''function'' then return fn end'
        $lua += '  if __sl10002_chain_wrapped[name] then return fn end'
        $lua += '  __sl10002_chain_wrapped[name] = true'
        $lua += '  return function(...)'
        $lua += '    __sl10002_log(''[CHAIN_BEGIN] ''..name..'' args=''..__sl10002_chain_args(...))'
        $lua += '    local r = { pcall(fn, ...) }'
        $lua += '    __sl10002_log(''[CHAIN_END] ''..name..'' ok=''..tostring(r[1])..'' r1=''..tostring(r[2]))'
        $lua += '    if not r[1] then error(r[2]) end'
        $lua += '    if __sl10002_unpack then return __sl10002_unpack(r, 2) end'
        $lua += '    return r[2]'
        $lua += '  end'
        $lua += 'end'
        $lua += 'local function __sl10002_chain_install_now()'
        $lua += '  for _,n in ipairs(__sl10002_chain_targets) do'
        $lua += '    local f = rawget(_G, n)'
        $lua += '    if type(f) == ''function'' then'
        $lua += '      rawset(_G, n, __sl10002_chain_wrap(n, f))'
        $lua += '      __sl10002_log(''[CHAIN_WRAP_NOW] ''..n)'
        $lua += '    else'
        $lua += '      __sl10002_log(''[CHAIN_WAIT] ''..n)'
        $lua += '    end'
        $lua += '  end'
        $lua += 'end'
        $lua += 'pcall(__sl10002_chain_install_now)'
        $lua += 'local ok_mt, err_mt = pcall(function()'
        $lua += '  local mt = getmetatable(_G) or {}'
        $lua += '  local old_newindex = mt.__newindex'
        $lua += '  mt.__newindex = function(t,k,v)'
        $lua += '    if type(k) == ''string'' and type(v) == ''function'' then'
        $lua += '      for _,n in ipairs(__sl10002_chain_targets) do'
        $lua += '        if k == n then'
        $lua += '          __sl10002_log(''[CHAIN_WRAP_FUTURE] ''..k)'
        $lua += '          v = __sl10002_chain_wrap(k, v)'
        $lua += '          break'
        $lua += '        end'
        $lua += '      end'
        $lua += '    end'
        $lua += '    if old_newindex then return old_newindex(t,k,v) end'
        $lua += '    return rawset(t,k,v)'
        $lua += '  end'
        $lua += '  setmetatable(_G, mt)'
        $lua += 'end)'
        $lua += '__sl10002_log(''[CHAIN_BOOT] V45 map-chain diagnostic installed mt=''..tostring(ok_mt)..'' err=''..tostring(err_mt))'
        
        $lua += ''
        $lua += '-- SL10002 V45 original map-chain replay + session table dump. Uses original map functions only.'
        $lua += 'local function __sl10002_dump_table_once(tag, t)'
        $lua += '  if type(t) ~= ''table'' then return tostring(t) end'
        $lua += '  local out = {}; local c = 0'
        $lua += '  for k,v in pairs(t) do'
        $lua += '    c = c + 1; if c > 60 then out[#out+1] = ''...''; break end'
        $lua += '    if type(v) == ''table'' then out[#out+1] = tostring(k)..''={table}'' else out[#out+1] = tostring(k)..''=''..tostring(v) end'
        $lua += '  end'
        $lua += '  return ''{''..table.concat(out,'';'')..''}'''
        $lua += 'end'
        $lua += 'local __sl10002_replay_done = false'
        $lua += 'function SL10002_V45_PostMapChainReplay()'
        $lua += '  if __sl10002_replay_done then return end'
        $lua += '  __sl10002_replay_done = true'
        $lua += '  __sl10002_log(''[V45_REPLAY_BEGIN] original-map function replay after map_init'')'
        $lua += '  local names = {''tgr_maptab_init'',''tgr_map_init'',''map_init_0000'',''map_init_0004'',''map_init_allregion'',''player_station'',''player_mode_station'',''player_bar_station'',''map_addsceneobj'',''map_addchar''}'
        $lua += '  for _,n in ipairs(names) do'
        $lua += '    local f = rawget(_G,n)'
        $lua += '    if type(f) == ''function'' then local ok,err = pcall(f); __sl10002_log(''[V45_REPLAY_CALL] ''..n..'' ok=''..tostring(ok)..'' err=''..tostring(err)) else __sl10002_log(''[V45_REPLAY_MISSING] ''..n) end'
        $lua += '  end'
        $lua += '  if type(CustomEventTimer)==''function'' then local ok,err=pcall(CustomEventTimer); __sl10002_log(''[V45_REPLAY_CALL] CustomEventTimer ok=''..tostring(ok)..'' err=''..tostring(err)) end'
        $lua += '  if type(TgrMainTimer)==''function'' then local ok,err=pcall(TgrMainTimer,102); __sl10002_log(''[V45_REPLAY_CALL] TgrMainTimer(102) ok=''..tostring(ok)..'' err=''..tostring(err)) end'
        $lua += '  for i=1,25 do if type(GetSessionPlayerInfo)==''function'' then local ok,t=pcall(GetSessionPlayerInfo,i); if ok then __sl10002_log(''[V45_PLAYERINFO] ''..i..'' ''..__sl10002_dump_table_once(''p'',t)) else __sl10002_log(''[V45_PLAYERINFO_ERR] ''..i..'' ''..tostring(t)) end end end'
        $lua += '  if type(GetSessionPlayerInfoEx)==''function'' then for i=1,25 do local ok,t=pcall(GetSessionPlayerInfoEx,i); if ok then __sl10002_log(''[V45_PLAYERINFOEX] ''..i..'' ''..__sl10002_dump_table_once(''px'',t)) else __sl10002_log(''[V45_PLAYERINFOEX_ERR] ''..i..'' ''..tostring(t)) end end end'
        $lua += '  __sl10002_log(''[V45_REPLAY_END]'')'
        $lua += 'end'
        $lua += 'local __sl10002_old_chain_wrap = __sl10002_chain_wrap'
        $lua += '__sl10002_chain_wrap = function(name, fn)'
        $lua += '  local wrapped = __sl10002_old_chain_wrap(name, fn)'
        $lua += '  if name == ''map_init'' and type(wrapped)==''function'' then'
        $lua += '    return function(...)'
        $lua += '      local r = { pcall(wrapped, ...) }'
        $lua += '      __sl10002_log(''[V45_AFTER_MAP_INIT] ok=''..tostring(r[1])..'' r1=''..tostring(r[2]))'
        $lua += '      if type(AddTimer)==''function'' then pcall(AddTimer,''SL10002_V45_PostMapChainReplay'',100) end'
        $lua += '      pcall(SL10002_V45_PostMapChainReplay)'
        $lua += '      if not r[1] then error(r[2]) end'
        $lua += '      if __sl10002_unpack then return __sl10002_unpack(r,2) end; return r[2]'
        $lua += '    end'
        $lua += '  end'
        $lua += '  return wrapped'
        $lua += 'end'
        $lua += 'pcall(__sl10002_chain_install_now)'

$lua += 'local function __sl10002_try_mod(p) local ok,err=pcall(dofile,p); if ok then __sl10002_log("[MOD] loaded "..p); return true else __sl10002_log("[MOD] load failed "..p.." err="..tostring(err)); return false end end'
        $lua += '-- V45 protocol-first with TGA2DDS UI repair: ModRuntime autoload disabled until clock/delay are correct.'
        $out = ($lua -join "`r`n") + "`r`n"

        $ascii = [System.Text.Encoding]::ASCII
        $rootCfg = Join-Path $RootDir 'config.lua'
        [System.IO.File]::WriteAllText($rootCfg, $out, $ascii)
        $core = Join-Path $RootDir 'core'
        if (-not (Test-Path -LiteralPath $core)) { New-Item -ItemType Directory -Force -Path $core | Out-Null }
        $coreCfg = Join-Path $core 'config.lua'
        [System.IO.File]::WriteAllText($coreCfg, $out, $ascii)

        $first = [System.IO.File]::ReadAllBytes($rootCfg) | Select-Object -First 12
        $hex = (($first | ForEach-Object { $_.ToString('X2') }) -join ' ')
        $summary = @()
        $summary += ('ControlID=' + $ControlId)
        $summary += ('Options=' + ($values -join ','))
        $summary += 'NetworkOptionInfo=ZeroCountSafe'
        $summary += 'ConfigEncoding=ASCII_NO_BOM'
        $summary += ('ConfigFirstBytes=' + $hex)
        $summary += 'MapProtocolStubs=SrvScriptInfo,load_rolesdk ordinary-user connected-status diagnostics only'
        [System.IO.File]::WriteAllText((Join-Path $RootDir 'SL10002_config_v45_summary.txt'), (($summary -join "`r`n") + "`r`n"), $ascii)
    } catch {
        try { Add-Content -LiteralPath (Join-Path $RootDir 'SL10002_config_v45_summary.txt') -Encoding UTF8 -Value ('[CONFIG_V45_ERROR] ' + $_.Exception.Message) } catch {}
    }
}
Write-SL10002ConfigLuaV45 -RootDir $Root -ControlId $PlayerSlot

# V45 protocol-first marker logs. ModRuntime is intentionally not auto-loaded.
try {
  Set-Content -LiteralPath (Join-Path $Root 'SL10002_protocol_clock_v45.log') -Encoding ASCII -Value 'V45 MAPCHAIN REPLAY + 0259 SESSION ACK baseline deployed. start_10002.bat and PS default pass ControlOnly; full 10002.o resource scan is restored before game launch; no frame pulse; adds 0x0259->0x0159 mirror ack, 0x026A add-player refresh, Lua table dump, and original map function replay after map_init.'
  Set-Content -LiteralPath (Join-Path $Root 'SL10002_protocol_v45_status.txt') -Encoding ASCII -Value 'V45 keeps resource completeness and ControlOnly, then tests missing session-login ack and original map-chain replay: 0x0259 mirror ack, 0x026A player refresh, GetSessionPlayerInfo table dump, map_addchar/map_addsceneobj/player_station replay.'
  Set-Content -LiteralPath (Join-Path $Root 'AddCha.log') -Encoding ASCII -Value 'V45 AddCha overlay disabled. V45 only replays original map functions; any AddCha/SceneObj calls are from original map logic.'
} catch {}

# V45: complete the only missing referenced UI resource with a real adjacent original UI asset.
# This is a compatibility alias, not a generated placeholder: ValuableItemShop.tga is referenced by 10002.o,
# while ValuableShop.tga exists in the same UI set. The alias is created before C# resource scan so it is
# copied/reported through the normal preload pipeline.
try {
  $dstAlias = Join-Path $Root 'resource\sanguo\ui\ValuableItemShop.tga'
  $srcAlias = Join-Path $Root 'resource\sanguo\ui\ValuableShop.tga'
  if ((-not (Test-Path -LiteralPath $dstAlias -PathType Leaf)) -and (Test-Path -LiteralPath $srcAlias -PathType Leaf)) {
    Copy-Item -LiteralPath $srcAlias -Destination $dstAlias -Force
    Set-Content -LiteralPath (Join-Path $Root 'SL10002_resource_alias_v45.log') -Encoding ASCII -Value 'V45_ALIAS_OK ValuableItemShop.tga <= ValuableShop.tga'
  } else {
    Set-Content -LiteralPath (Join-Path $Root 'SL10002_resource_alias_v45.log') -Encoding ASCII -Value ('V45_ALIAS_SKIP exists=' + (Test-Path -LiteralPath $dstAlias -PathType Leaf) + ' src=' + (Test-Path -LiteralPath $srcAlias -PathType Leaf))
  }
} catch {
  try { Set-Content -LiteralPath (Join-Path $Root 'SL10002_resource_alias_v45.log') -Encoding ASCII -Value ('V45_ALIAS_ERROR ' + $_.Exception.Message) } catch {}
}

$Source = @'
using System;
using System.IO;
using System.Text;
using System.Diagnostics;
using System.IO.MemoryMappedFiles;
using System.Net;
using System.Net.Sockets;
using System.Net.NetworkInformation;
using System.Threading;

#pragma warning disable 0414
#pragma warning disable 0420

namespace SL10002FinalLauncher
{
    public static class Launcher
    {
        static string RootDir;
        static string LogPath;
        static string PacketDir;
        static volatile bool StopFlag = false;
        static readonly object LogLock = new object();
        const int HostPort = 29002;
        static int TcpPacketIndex = 0;
        static int UdpPacketIndex = 0;
        static volatile bool GlobalClientReady = false;
        static volatile bool GlobalPlayerInfoSent = false;
        static volatile bool GlobalGameStarted = false;
        static volatile uint GlobalTurn = 1;
        static int NextAssignedSlot = -1;
        static string LaunchMode = "Host";
        static string HostIpText = "127.0.0.1";
        static IPAddress HostIPAddress = IPAddress.Loopback;
        static string LocalPlayerName = "Player1";
        static int LocalPlayerSlot = 1;
        static bool IsHostMode = true;
        static bool IsClientMode = false;
        static bool IsSingleMode = false;
        static IPAddress BindAddress = IPAddress.Any;
        static string ProtocolVariant = "ControlOnly";

        static void Log(string s)
        {
            string line = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss.fff") + " " + s;
            // V24 quiet mode: never print the detailed launcher log to console.
            // The user should see only one launcher window; all diagnostics go to files.
            lock (LogLock)
            {
                File.AppendAllText(LogPath, line + Environment.NewLine, Encoding.UTF8);
            }
        }

        static void EnsureDir(string p)
        {
            if (!Directory.Exists(p)) Directory.CreateDirectory(p);
        }

        static void CopyStrict(string src, string dst)
        {
            if (!File.Exists(src)) throw new FileNotFoundException("missing file", src);
            EnsureDir(Path.GetDirectoryName(dst));
            File.Copy(src, dst, true);
            Log("[COPY] " + src + " -> " + dst + " size=" + new FileInfo(dst).Length);
        }


        static void CopyCompatResource(string rel)
        {
            string src = Path.Combine(RootDir, "compat_resource", rel);
            string dst = Path.Combine(RootDir, "resource", rel);
            if (!File.Exists(src)) { Log("[WARN] compat resource missing in package: " + src); return; }
            if (File.Exists(dst))
            {
                long sz = new FileInfo(dst).Length;
                string bak = dst + ".bak_SL10002_FORCE";
                try { File.Copy(dst, bak, true); Log("[BACKUP] " + dst + " -> " + bak + " size=" + sz.ToString()); } catch {}
            }
            EnsureDir(Path.GetDirectoryName(dst));
            File.Copy(src, dst, true);
            Log("[RESOURCE_FORCE] " + src + " -> " + dst + " size=" + new FileInfo(dst).Length.ToString());
            try
            {
                byte[] head = File.ReadAllBytes(dst);
                if (dst.ToLowerInvariant().EndsWith(".dds"))
                {
                    if (head.Length < 128 || head[0] != 0x44 || head[1] != 0x44 || head[2] != 0x53 || head[3] != 0x20)
                        Log("[WARN] DDS header check failed: " + dst);
                    else Log("[OK] DDS header: " + dst);
                }
                if (dst.ToLowerInvariant().EndsWith(".tga"))
                {
                    if (head.Length < 18 || head[2] != 2)
                        Log("[WARN] TGA header check failed: " + dst);
                    else Log("[OK] TGA header: " + dst);
                }
            }
            catch (Exception ex) { Log("[WARN] resource validation failed: " + ex.Message); }
        }

        static void RestoreBackupIfAny(string rel)
        {
            string dst = Path.Combine(RootDir, "resource", rel);
            string bak1 = dst + ".bak_SL10002_FORCE";
            string bak2 = dst + ".bak_SL10002";
            try
            {
                if (File.Exists(bak1))
                {
                    File.Copy(bak1, dst, true);
                    Log("[RESTORE] " + bak1 + " -> " + dst + " size=" + new FileInfo(dst).Length.ToString());
                    return;
                }
                if (File.Exists(bak2))
                {
                    File.Copy(bak2, dst, true);
                    Log("[RESTORE] " + bak2 + " -> " + dst + " size=" + new FileInfo(dst).Length.ToString());
                    return;
                }
                Log("[RESTORE_SKIP] no backup for " + dst);
            }
            catch (Exception ex) { Log("[RESTORE_WARN] " + rel + " " + ex.Message); }
        }

        static bool TryRestoreFromAnyKnownBackup(string rel)
        {
            string dst = Path.Combine(RootDir, "resource", rel);
            string[] suffixes = new string[] {
                ".bak_SL10002_FORCE",
                ".bak_SL10002",
                ".bak_SL10002_V16_BAD",
                ".bak_SL10002_V17_BAD",
                ".bak_SL10002_V18_BAD",
                ".bak_SL10002_V24_BAD",
                ".bak"
            };
            foreach (string suffix in suffixes)
            {
                string bak = dst + suffix;
                try
                {
                    if (File.Exists(bak))
                    {
                        EnsureDir(Path.GetDirectoryName(dst));
                        File.Copy(bak, dst, true);
                        Log("[V20_RESTORE_VISUAL_BACKUP] " + bak + " -> " + dst + " size=" + new FileInfo(dst).Length.ToString());
                        return true;
                    }
                }
                catch (Exception ex)
                {
                    Log("[V20_RESTORE_VISUAL_BACKUP_WARN] " + bak + " " + ex.Message);
                }
            }
            return false;
        }

        static bool LooksLikeTinyPlaceholderVisual(string path)
        {
            try
            {
                if (!File.Exists(path)) return false;
                FileInfo fi = new FileInfo(path);
                string lower = path.ToLowerInvariant();
                if (lower.EndsWith(".dds"))
                {
                    // V19 accepted 192-byte DDS stubs because the DDS magic existed.
                    // D3DXGetImageInfoFromFile still rejects these; treat small DDS as a broken placeholder.
                    return fi.Length < 4096;
                }
                if (lower.EndsWith(".tga"))
                {
                    byte[] head = File.ReadAllBytes(path);
                    bool oneByOneTga = head.Length == 22 && head[2] == 2 && head[12] == 1 && head[14] == 1;
                    // V24: the previous package had 82-byte terrain/UI TGA stubs.
                    // They are technically TGA-like, but not real game textures.
                    return oneByOneTga || fi.Length < 1024;
                }
                return false;
            }
            catch { return false; }
        }

        static void QuarantineFile(string path, string reason)
        {
            try
            {
                if (!File.Exists(path)) return;
                string quarantine = path + ".quarantine_SL10002_V20_" + DateTime.Now.ToString("yyyyMMdd_HHmmss");
                File.Move(path, quarantine);
                Log("[V20_QUARANTINE_VISUAL] " + reason + " " + path + " -> " + quarantine);
            }
            catch (Exception ex)
            {
                Log("[V20_QUARANTINE_VISUAL_WARN] " + path + " " + ex.Message);
            }
        }

        static void RestoreOrQuarantineVisualResource(string rel)
        {
            string dst = Path.Combine(RootDir, "resource", rel);
            if (TryRestoreFromAnyKnownBackup(rel))
            {
                return;
            }
            if (LooksLikeTinyPlaceholderVisual(dst))
            {
                QuarantineFile(dst, "tiny/bad placeholder");
                return;
            }
            if (File.Exists(dst))
            {
                Log("[V20_KEEP_VISUAL_UNTOUCHED] " + dst + " size=" + new FileInfo(dst).Length.ToString());
            }
            else
            {
                Log("[V20_VISUAL_MISSING_NO_PLACEHOLDER] " + dst + " (left missing intentionally; no fake UI/texture will be written)");
            }
        }

        static void V20RestoreVisualResourceSafety()
        {
            Log("[V20_RESOURCE_PURE] begin restore/quarantine. No compat_resource copy. No tiny TGA. No DDS placeholder.");
            RestoreOrQuarantineVisualResource(@"sanguo\ui\loading_misc.dds");
            RestoreOrQuarantineVisualResource(@"sanguo\ui\mission_misc.dds");
            RestoreOrQuarantineVisualResource(@"sanguo\ui\main_misc.dds");
            RestoreOrQuarantineVisualResource(@"sanguo\ui\ValuableItemShop.tga");
            Log("[V20_RESOURCE_PURE] end restore/quarantine.");
        }


        static void CopyCompatResourceIfMissing(string rel)
        {
            string src = Path.Combine(RootDir, "compat_resource", rel);
            string dst = Path.Combine(RootDir, "resource", rel);
            if (File.Exists(dst)) { Log("[KEEP] existing resource: " + dst + " size=" + new FileInfo(dst).Length.ToString()); return; }
            if (!File.Exists(src)) { Log("[WARN] compat resource missing in package: " + src); return; }
            EnsureDir(Path.GetDirectoryName(dst));
            File.Copy(src, dst, true);
            Log("[RESOURCE_MISSING_ONLY] " + src + " -> " + dst + " size=" + new FileInfo(dst).Length.ToString());
        }


        static bool ResourceLooksValid(string path)
        {
            try
            {
                if (!File.Exists(path)) return false;
                FileInfo fi = new FileInfo(path);
                if (fi.Length <= 0) return false;
                string lower = path.ToLowerInvariant();
                byte[] head = File.ReadAllBytes(path);
                if (lower.EndsWith(".dds"))
                {
                    return head.Length >= 128 && head[0] == 0x44 && head[1] == 0x44 && head[2] == 0x53 && head[3] == 0x20;
                }
                if (lower.EndsWith(".tga"))
                {
                    return head.Length >= 1024 && head.Length >= 18;
                }
                if (lower.EndsWith(".bmp"))
                {
                    return head.Length >= 54 && head[0] == 0x42 && head[1] == 0x4D;
                }
                return true;
            }
            catch { return false; }
        }

        static void CopyCompatResourceIfMissingOrBad(string rel)
        {
            string src = Path.Combine(RootDir, "compat_resource", rel);
            string dst = Path.Combine(RootDir, "resource", rel);
            if (ResourceLooksValid(dst))
            {
                Log("[KEEP_VALID] existing resource OK: " + dst + " size=" + new FileInfo(dst).Length.ToString());
                return;
            }
            if (!File.Exists(src))
            {
                Log("[WARN] compat repair source missing: " + src);
                return;
            }
            EnsureDir(Path.GetDirectoryName(dst));
            try
            {
                if (File.Exists(dst))
                {
                    string bak = dst + ".bak_SL10002_V16_BAD";
                    File.Copy(dst, bak, true);
                    Log("[BACKUP_BAD_RESOURCE] " + dst + " -> " + bak);
                }
            }
            catch (Exception ex) { Log("[BACKUP_BAD_RESOURCE_WARN] " + dst + " " + ex.Message); }
            File.Copy(src, dst, true);
            Log("[RESOURCE_REPAIR_V16] " + src + " -> " + dst + " size=" + new FileInfo(dst).Length.ToString());
            if (!ResourceLooksValid(dst)) Log("[WARN] repaired resource still fails header check: " + dst);
        }


        static void WriteTinyTgaIfMissing(string rel)
        {
            string dst = Path.Combine(RootDir, "resource", rel);
            if (File.Exists(dst)) { Log("[KEEP] existing resource: " + dst + " size=" + new FileInfo(dst).Length.ToString()); return; }
            EnsureDir(Path.GetDirectoryName(dst));
            byte[] tga = new byte[22];
            tga[2] = 2;          // uncompressed true-color
            tga[12] = 1; tga[13] = 0; // width 1
            tga[14] = 1; tga[15] = 0; // height 1
            tga[16] = 32;        // 32 bpp
            tga[17] = 8;         // alpha bits
            tga[18] = 0; tga[19] = 0; tga[20] = 0; tga[21] = 0; // transparent pixel
            File.WriteAllBytes(dst, tga);
            Log("[RESOURCE_TGA_PLACEHOLDER] created missing " + dst + " size=" + new FileInfo(dst).Length.ToString());
        }

        static void CloneCliffTransIfMissing()
        {
            string modelDir = Path.Combine(RootDir, @"resource\sanguo\model");
            EnsureDir(modelDir);
            string[] need = new string[] {
                "CliffTransAAHL0.lmo", "CliffTransAALH0.lmo", "CliffTransAHLA0.lmo", "CliffTransALHA0.lmo",
                "CliffTransHAAL0.lmo", "CliffTransHLAA0.lmo", "CliffTransLAAH0.lmo", "CliffTransLHAA0.lmo"
            };
            string src = null;
            foreach (string f in Directory.GetFiles(modelDir, "CliffTrans*.lmo"))
            {
                string name = Path.GetFileName(f);
                bool isNeed = false;
                foreach (string n in need) if (String.Equals(name, n, StringComparison.OrdinalIgnoreCase)) { isNeed = true; break; }
                if (!isNeed) { src = f; break; }
            }
            if (src == null)
            {
                // fallback: use any existing LMO as a visual placeholder only when the exact transition models are absent
                string[] any = Directory.GetFiles(modelDir, "*.lmo");
                if (any.Length > 0) src = any[0];
            }
            foreach (string n in need)
            {
                string dst = Path.Combine(modelDir, n);
                if (File.Exists(dst)) { Log("[KEEP] existing resource: " + dst + " size=" + new FileInfo(dst).Length.ToString()); continue; }
                if (src == null) { Log("[WARN] cannot clone missing cliff transition, no local .lmo source found: " + dst); continue; }
                File.Copy(src, dst, true);
                Log("[RESOURCE_CLIFF_CLONE] " + src + " -> " + dst + " size=" + new FileInfo(dst).Length.ToString());
            }
        }



        static bool BytesMatch(byte[] data, int off, byte[] pat)
        {
            if (off < 0 || off + pat.Length > data.Length) return false;
            for (int i = 0; i < pat.Length; i++) if (data[off + i] != pat[i]) return false;
            return true;
        }

        static string HexAt(byte[] data, int off, int len)
        {
            if (off < 0 || off >= data.Length) return "<off out of range>";
            int n = Math.Min(len, data.Length - off);
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < n; i++)
            {
                if (i > 0) sb.Append(' ');
                sb.Append(data[off + i].ToString("X2"));
            }
            return sb.ToString();
        }

        static bool PatchBytes(byte[] data, int off, byte[] expected, byte[] patch, string name)
        {
            if (off < 0 || off + patch.Length > data.Length)
            {
                Log("[NOCLOSE_STRONG_WARN] " + name + " offset out of range 0x" + off.ToString("X"));
                return false;
            }
            bool already = true;
            for (int i = 0; i < patch.Length; i++) if (data[off + i] != patch[i]) already = false;
            if (already)
            {
                Log("[NOCLOSE_STRONG] already patched " + name + " at file offset 0x" + off.ToString("X"));
                return true;
            }
            if (expected != null && expected.Length > 0 && !BytesMatch(data, off, expected))
            {
                Log("[NOCLOSE_STRONG_WARN] pattern mismatch for " + name + " at 0x" + off.ToString("X") + ", current=" + HexAt(data, off, Math.Max(expected.Length, patch.Length)));
                return false;
            }
            for (int i = 0; i < patch.Length; i++) data[off + i] = patch[i];
            Log("[NOCLOSE_STRONG] patched " + name + " at file offset 0x" + off.ToString("X") + " -> " + HexAt(data, off, patch.Length));
            return true;
        }

        static void PatchGameEventCloseWindowCall(string gamePath)
        {
            try
            {
                if (!File.Exists(gamePath)) { Log("[NOCLOSE_STRONG_WARN] game.exe not found: " + gamePath); return; }
                byte[] data = File.ReadAllBytes(gamePath);
                string bak = gamePath + ".bak_SL10002_NOCLOSE_STRONG";
                if (!File.Exists(bak))
                {
                    File.Copy(gamePath, bak, false);
                    Log("[NOCLOSE_STRONG] backup created: " + bak);
                }

                bool changed = false;

                // 1) Main frame-5 branch: call gpigame!GameEventCloseWindow at VA 0x410F0C / file 0x10F0C.
                //    Old V9 only patched this direct call. Keep it, but add verification.
                changed |= PatchBytes(data, 0x10F0C,
                    new byte[] { 0xE8, 0x0F, 0x3E, 0x02, 0x00 },
                    new byte[] { 0x90, 0x90, 0x90, 0x90, 0x90 },
                    "direct call 0x410F0C GameEventCloseWindow");

                // 2) Import jump stub at VA 0x434D20 / file 0x34D20: FF 25 B8 95 4A 00.
                //    Patch the stub to RET so any other internal caller cannot close the window.
                changed |= PatchBytes(data, 0x34D20,
                    new byte[] { 0xFF, 0x25, 0xB8, 0x95, 0x4A, 0x00 },
                    new byte[] { 0xC3, 0x90, 0x90, 0x90, 0x90, 0x90 },
                    "import stub 0x434D20 GameEventCloseWindow -> RET");

                // 3) Pipe exit notifier at VA 0x419AD0 / file 0x19AD0. This is the function that logs/sends
                //    CMD_CLIENT_G2P_EXIT. Patch to 'mov al,1; ret' so exit pipe notifications do not propagate.
                changed |= PatchBytes(data, 0x19AD0,
                    new byte[] { 0x83, 0xEC, 0x0C, 0x33, 0xC0, 0x39, 0x05, 0x00, 0x64, 0x4D, 0x00 },
                    new byte[] { 0xB0, 0x01, 0xC3, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90 },
                    "pipe exit notifier 0x419AD0 CMD_CLIENT_G2P_EXIT -> return true");

                // 4) Optional hard kill: change the diagnostic string so we can prove whether the old path is still running.
                //    We do not remove it; this only lets the log identify STRONG patch if the path is reached.
                if (changed)
                {
                    File.WriteAllBytes(gamePath, data);
                    Log("[NOCLOSE_STRONG] game.exe written. Active patches verified:");
                    Log("[NOCLOSE_STRONG] 0x10F0C=" + HexAt(data, 0x10F0C, 5));
                    Log("[NOCLOSE_STRONG] 0x34D20=" + HexAt(data, 0x34D20, 6));
                    Log("[NOCLOSE_STRONG] 0x19AD0=" + HexAt(data, 0x19AD0, 11));
                }
                else
                {
                    Log("[NOCLOSE_STRONG_WARN] no patch was applied; check bytes above. The launcher will continue for tracing.");
                }
            }
            catch (Exception ex)
            {
                Log("[NOCLOSE_STRONG_ERROR] " + ex.Message);
            }
        }

        static void RestoreGameExeNoClosePatch(string gamePath)
        {
            try
            {
                string bak = gamePath + ".bak_SL10002_NOCLOSE";
                if (File.Exists(bak))
                {
                    File.Copy(bak, gamePath, true);
                    Log("[NOCLOSE_RESTORE] restored game.exe from " + bak);
                }
                else Log("[NOCLOSE_RESTORE_SKIP] no backup found: " + bak);
            }
            catch (Exception ex) { Log("[NOCLOSE_RESTORE_ERROR] " + ex.Message); }
        }

        static void RestoreGameExeExperimentalBackups(string gamePath)
        {
            try
            {
                string[] suffixes = new string[] { ".bak_SL10002_NOCLOSE_STRONG", ".bak_SL10002_NOCLOSE" };
                foreach (string suffix in suffixes)
                {
                    string bak = gamePath + suffix;
                    if (File.Exists(bak))
                    {
                        File.Copy(bak, gamePath, true);
                        Log("[RESTORE_GAME_EXE] restored experimental patched game.exe from " + bak);
                        return;
                    }
                }
                Log("[RESTORE_GAME_EXE_SKIP] no experimental game.exe backup found");
            }
            catch (Exception ex) { Log("[RESTORE_GAME_EXE_WARN] " + ex.Message); }
        }

        static void RestoreMapOKPatchedDllIfBackupExists(string gpigamePath)
        {
            string bak = gpigamePath + ".bak_SL10002_MAPOK";
            try
            {
                if (File.Exists(bak))
                {
                    File.Copy(bak, gpigamePath, true);
                    Log("[RESTORE_GPI] restored original gpigame.dll from MAPOK backup: " + bak);
                }
            }
            catch (Exception ex) { Log("[RESTORE_GPI_WARN] " + ex.Message); }
        }

        static void WriteAscii(byte[] buf, int offset, string text, int maxBytes)
        {
            byte[] src = Encoding.ASCII.GetBytes(text ?? "");
            int n = Math.Min(src.Length, Math.Max(0, maxBytes - 1));
            Buffer.BlockCopy(src, 0, buf, offset, n);
            if (offset + n < buf.Length) buf[offset + n] = 0;
        }

        static void WriteWide(byte[] buf, int offset, string text, int maxBytes)
        {
            byte[] src = Encoding.Unicode.GetBytes((text ?? "") + "\0");
            int n = Math.Min(src.Length, maxBytes);
            if ((n & 1) != 0) n--;
            Buffer.BlockCopy(src, 0, buf, offset, n);
            if (n < maxBytes)
            {
                buf[offset + n] = 0;
                if (n + 1 < maxBytes) buf[offset + n + 1] = 0;
            }
        }

        static void WriteU16(byte[] buf, int offset, ushort v)
        {
            byte[] b = BitConverter.GetBytes(v);
            Buffer.BlockCopy(b, 0, buf, offset, 2);
        }

        static void WriteU32(byte[] buf, int offset, uint v)
        {
            byte[] b = BitConverter.GetBytes(v);
            Buffer.BlockCopy(b, 0, buf, offset, 4);
        }

        static string Hex(byte[] data, int len, int max)
        {
            int n = Math.Min(len, Math.Min(data.Length, max));
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < n; i++)
            {
                if (i > 0) sb.Append(' ');
                sb.Append(data[i].ToString("X2"));
            }
            if (len > n) sb.Append(" ...");
            return sb.ToString();
        }

        static string AsciiPreview(byte[] data, int len)
        {
            int n = Math.Min(len, data.Length);
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < n && i < 128; i++)
            {
                byte b = data[i];
                if (b >= 32 && b <= 126) sb.Append((char)b);
                else sb.Append('.');
            }
            return sb.ToString();
        }

        static void SavePacket(string prefix, byte[] data, int len, string info)
        {
            EnsureDir(PacketDir);
            int idx;
            if (prefix.StartsWith("tcp")) idx = Interlocked.Increment(ref TcpPacketIndex);
            else idx = Interlocked.Increment(ref UdpPacketIndex);
            string name = prefix + "_" + idx.ToString("D4") + "_" + len.ToString() + ".bin";
            string path = Path.Combine(PacketDir, name);
            byte[] outb = new byte[len];
            Buffer.BlockCopy(data, 0, outb, 0, len);
            File.WriteAllBytes(path, outb);
            File.AppendAllText(Path.Combine(PacketDir, "packets_index.tsv"),
                DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss.fff") + "\t" + name + "\t" + info + "\t" + Hex(data, len, 256) + "\t" + AsciiPreview(data, len) + Environment.NewLine,
                Encoding.UTF8);
        }

        static string ReadWide(byte[] buf, int offset, int maxBytes)
        {
            int len = 0;
            while (len + 1 < maxBytes)
            {
                if (buf[offset + len] == 0 && buf[offset + len + 1] == 0) break;
                len += 2;
            }
            return Encoding.Unicode.GetString(buf, offset, len);
        }

        static bool LooksVirtualInterface(NetworkInterface ni)
        {
            string s = ((ni.Name ?? "") + " " + (ni.Description ?? "")).ToLowerInvariant();
            string[] bad = new string[] { "virtual", "vmware", "virtualbox", "hyper-v", "wsl", "docker", "vpn", "tap", "loopback", "tunnel", "bluetooth" };
            foreach (string x in bad) if (s.Contains(x)) return true;
            return false;
        }

        static bool IsPrivateLanPreferred(string ip)
        {
            return ip.StartsWith("192.168.") || ip.StartsWith("10.");
        }

        static bool IsLikelyVirtualIPv4(string ip)
        {
            if (ip.StartsWith("169.254.")) return true;
            if (ip.StartsWith("127.")) return true;
            // 172.16-31 is private, but in this project logs showed 172.19.0.1 from a virtual/WSL adapter.
            // Prefer 192.168/10.x first; use 172.x only when user explicitly enters it or no better IP exists.
            string[] p = ip.Split('.');
            if (p.Length == 4 && p[0] == "172")
            {
                int n;
                if (Int32.TryParse(p[1], out n) && n >= 16 && n <= 31) return true;
            }
            return false;
        }

        static string DetectLanIPv4()
        {
            string fallback = null;
            string virtualFallback = null;
            try
            {
                foreach (NetworkInterface ni in NetworkInterface.GetAllNetworkInterfaces())
                {
                    if (ni.OperationalStatus != OperationalStatus.Up) continue;
                    if (ni.NetworkInterfaceType == NetworkInterfaceType.Loopback) continue;
                    bool virtualLike = LooksVirtualInterface(ni);
                    IPInterfaceProperties props = ni.GetIPProperties();
                    foreach (UnicastIPAddressInformation ua in props.UnicastAddresses)
                    {
                        if (ua.Address.AddressFamily != AddressFamily.InterNetwork) continue;
                        string ip = ua.Address.ToString();
                        if (ip.StartsWith("169.254.") || ip.StartsWith("127.")) continue;
                        Log("[LAN_IP_CANDIDATE] " + ip + " iface=" + ni.Name + " desc=" + ni.Description + " virtualLike=" + virtualLike.ToString());
                        if (!virtualLike && IsPrivateLanPreferred(ip)) return ip;
                        if (!virtualLike && !IsLikelyVirtualIPv4(ip) && fallback == null) fallback = ip;
                        if (virtualFallback == null) virtualFallback = ip;
                    }
                }
            }
            catch (Exception ex) { Log("[LAN_WARN] detect LAN IPv4 failed: " + ex.Message); }
            if (fallback != null) return fallback;
            if (virtualFallback != null)
            {
                Log("[LAN_WARN] only virtual/private-172 style IP found, fallback=" + virtualFallback + ". For real LAN host mode, manually enter the actual 192.168.x.x/10.x.x.x address in the menu.");
                return virtualFallback;
            }
            return "127.0.0.1";
        }

        static IPAddress ParseIPv4OrLoopback(string ip)
        {
            IPAddress parsed;
            if (!String.IsNullOrWhiteSpace(ip) && IPAddress.TryParse(ip, out parsed) && parsed.AddressFamily == AddressFamily.InterNetwork) return parsed;
            return IPAddress.Loopback;
        }

        static void ConfigureMode(string mode, string hostIpArg, string playerNameArg, int playerSlotArg)
        {
            LaunchMode = String.IsNullOrWhiteSpace(mode) ? "Host" : mode.Trim();
            IsClientMode = String.Equals(LaunchMode, "Client", StringComparison.OrdinalIgnoreCase);
            IsSingleMode = String.Equals(LaunchMode, "Single", StringComparison.OrdinalIgnoreCase);
            IsHostMode = !IsClientMode;
            LocalPlayerName = String.IsNullOrWhiteSpace(playerNameArg) ? "Player1" : playerNameArg.Trim();
            if (playerSlotArg < 1) playerSlotArg = 1;
            if (playerSlotArg > 24) playerSlotArg = 24;
            LocalPlayerSlot = playerSlotArg;

            if (IsSingleMode)
            {
                HostIpText = "127.0.0.1";
                BindAddress = IPAddress.Loopback;
            }
            else if (IsClientMode)
            {
                HostIpText = String.IsNullOrWhiteSpace(hostIpArg) ? "127.0.0.1" : hostIpArg.Trim();
                BindAddress = IPAddress.Loopback;
            }
            else
            {
                HostIpText = String.IsNullOrWhiteSpace(hostIpArg) ? DetectLanIPv4() : hostIpArg.Trim();
                BindAddress = IPAddress.Any;
            }
            HostIPAddress = ParseIPv4OrLoopback(HostIpText);

            Log("[LAN_CONFIG] mode=" + LaunchMode + " hostIp=" + HostIpText + " bind=" + BindAddress.ToString() + " playerName=" + LocalPlayerName + " playerSlot=" + LocalPlayerSlot.ToString() + " port=" + HostPort.ToString());
            if (IsHostMode && !IsSingleMode)
            {
                Log("[LAN_HOST] Other players should use HostIP=" + HostIpText + " and port " + HostPort.ToString() + ". Windows firewall must allow TCP/UDP 29002.");
            }
            if (IsClientMode)
            {
                Log("[LAN_CLIENT] This machine will NOT start local HostService. It will connect to host " + HostIpText + ":" + HostPort.ToString() + " through MemoryMap.");
            }
        }

        static int AllocateConnectionSlot()
        {
            int slot = Interlocked.Increment(ref NextAssignedSlot);
            if (slot < 0) slot = 0;
            if (slot > 23) slot = 23;
            return slot;
        }

        static byte[] BuildPlatformBlock()
        {
            const int StructSize = 0x435;
            byte[] buf = new byte[StructSize];
            WriteU16(buf, 0x00, 1);
            WriteWide(buf, 0x02, "10002", 0x40);
            byte[] ipBytes = HostIPAddress.GetAddressBytes();
            if (ipBytes == null || ipBytes.Length != 4) ipBytes = IPAddress.Loopback.GetAddressBytes();
            buf[0x42] = ipBytes[0]; buf[0x43] = ipBytes[1]; buf[0x44] = ipBytes[2]; buf[0x45] = ipBytes[3];
            WriteU16(buf, 0x46, (ushort)HostPort);
            // Report-grounded memory-map alignment:
            // sub_0043A7A0 writes a player Pos byte around +0x48. net_state for player1 expects Pos:0.
            // Therefore LocalPlayerSlot remains 1-based for UI, but memory map Pos is zero-based.
            byte zeroBasedPos = (byte)Math.Max(0, Math.Min(23, LocalPlayerSlot - 1));
            buf[0x48] = zeroBasedPos; buf[0x49] = 0;
            WriteU32(buf, 0x4A, 1); // HostSrvSessionId / room session candidate
            WriteU32(buf, 0x4E, (uint)(100000 + LocalPlayerSlot));
            WriteWide(buf, 0x52, LocalPlayerName, 0x20);
            WriteU32(buf, 0x72, (uint)zeroBasedPos);
            WriteWide(buf, 0x284, "SL10002", 0x60);
            buf[0x2E4] = 0;
            WriteAscii(buf, 0x2E5, LaunchMode.ToLowerInvariant(), 0x10);
            WriteU32(buf, 0x2F5, 0);
            WriteU32(buf, 0x2F9, 0);
            WriteU32(buf, 0x2FD, 0);
            WriteU32(buf, 0x305, 0);
            WriteWide(buf, 0x309, "", 0x20);
            WriteWide(buf, 0x329, "", 0x20);
            WriteU32(buf, 0x349, 0);
            WriteWide(buf, 0x34D, "", 0x44);
            WriteU32(buf, 0x391, 10002);
            WriteU32(buf, 0x427, 1);
            Log("[CHECK] MapNameWide=" + ReadWide(buf, 0x02, 0x40));
            Log("[CHECK] UserNameWide=" + ReadWide(buf, 0x52, 0x20));
            Log("[CHECK] HostIP=" + HostIPAddress.ToString());
            Log("[CHECK] HostSrvPort=" + HostPort.ToString());
            Log("[CHECK] LocalPlayerSlot=" + LocalPlayerSlot.ToString() + " zeroBasedPos=" + Math.Max(0, Math.Min(23, LocalPlayerSlot - 1)).ToString());
            return buf;
        }

        static MemoryMappedFile CreateAndWriteMap(string name, byte[] data)
        {
            MemoryMappedFile mmf = MemoryMappedFile.CreateOrOpen(name, data.Length);
            using (var acc = mmf.CreateViewAccessor(0, data.Length, MemoryMappedFileAccess.ReadWrite))
            {
                acc.WriteArray(0, data, 0, data.Length);
                acc.Flush();
            }
            Log("[OK] MemoryMap write OK: " + name + " size=" + data.Length);
            return mmf;
        }

        static byte[] BuildPacket(ushort opcode, byte[] payload)
        {
            if (payload == null) payload = new byte[0];
            int len = payload.Length + 4;
            byte[] p = new byte[len];
            WriteU16(p, 0, opcode);
            WriteU16(p, 2, (ushort)len);
            if (payload.Length > 0) Buffer.BlockCopy(payload, 0, p, 4, payload.Length);
            return p;
        }

        static byte[] BuildLoginResultPayload()
        {
            // Packet 0x013A is accepted as login/session success.
            // V15 logs showed server_time as Thu Jan 01 08:00:01 1970 because this was zero.
            // V19 writes a real Unix server_time so in-game time/elapsed-time logic has a valid base.
            byte[] b = new byte[0x34];
            uint unix = (uint)(DateTimeOffset.UtcNow.ToUnixTimeSeconds());
            WriteU32(b, 0x00, (uint)Math.Max(1, LocalPlayerSlot)); // global_id / local player id candidate
            WriteU32(b, 0x04, unix);                              // server_time candidate
            WriteU32(b, 0x08, 1);                                 // protocol/session ok candidate
            WriteU32(b, 0x0C, 1);                                 // room/session id mirror
            return b;
        }

        static byte[] BuildControlPayload(uint turn, bool clientReady, uint keepCounter)
        {
            // Verified from disassembly around game.exe 0x423330 and net_state logs:
            // full packet: opcode(2)+len(2)+payload(12)
            // payload+0 DWORD startFlag   -> net_state: start
            // payload+4 BYTE  fps         -> net_state: fps
            // payload+5 BYTE  turn        -> net_state: turn
            // payload+6 DWORD keep_alive  -> net_state: keep_alive
            // payload+10..11 unused/padding.
            // CONTROLTURN_FIX2 wrote turn at payload+10, which only changed an unused field.
            byte[] b = new byte[12];
            uint start = clientReady ? 2u : 1u;
            WriteU32(b, 0, start);
            b[4] = 30;
            b[5] = clientReady ? (byte)(turn & 0xFFu) : (byte)0;
            WriteU32(b, 6, keepCounter);
            WriteU16(b, 10, 0);
            return b;
        }


        static string GetSlotName(int slot)
        {
            // slot is 0-based network slot; map SetPlayer uses 1-based player id.
            int pid = slot + 1;
            if (pid == 9) return "\u661f\u96e8\u9601";
            if (pid == 20) return "\u708e\u9ec4\u8054\u76df";
            if (pid == 21) return "\u4e1c\u5937\u96c6\u56e2";
            if (pid == 22) return "\u4e0a\u53e4\u90aa\u795e";
            if (pid == 23) return "\u4e2d\u7acb\u654c\u5bf9";
            if (pid == 24) return "\u4e2d\u7acb\u65e0\u654c\u610f";
            if (pid == LocalPlayerSlot) return LocalPlayerName;
            if (pid == 1) return "Player1";
            return "P" + pid.ToString();
        }

        static byte GetSlotSide(int slot)
        {
            int pid = slot + 1;
            if (pid >= 1 && pid <= 10) return 1;
            if (pid >= 11 && pid <= 22) return 2;
            if (pid == 23) return 23;
            if (pid == 24) return 24;
            return 0;
        }

        static byte[] BuildPlayerRecordForSlot(int slot)
        {
            // Server player record parser for opcode 0x017A reads exactly 0x6F bytes.
            // WIDE_V5 proved name must be UTF-16LE. FULLSLOTS_V6_FIXED fills all 24 map player slots,
            // matching map/10002/10002.o player_station(): players 1-24, including hostile and neutral sides.
            byte[] r = new byte[0x6F];
            uint id = (uint)(100001 + slot);
            WriteU32(r, 0x00, id);
            WriteU32(r, 0x05, id);
            byte[] name = Encoding.Unicode.GetBytes(GetSlotName(slot) + "\0");
            Buffer.BlockCopy(name, 0, r, 0x09, Math.Min(name.Length, 0x60));
            r[0x69] = (byte)slot;        // network pos, 0-based
            r[0x6A] = GetSlotSide(slot); // side/camp from map SetPlayer
            return r;
        }

        static byte[] BuildPlayerRecord()
        {
            return BuildPlayerRecordForSlot(0);
        }

        static byte[] BuildPlayerInfoListPayload()
        {
            // opcode 0x015A parser first reads an 8-byte header:
            // +0 DWORD count, +6 WORD record_size, then count records of record_size bytes.
            // V5 only sent count=1. Map 10002 uses AddCha owners 9/20/21/22/23/24, so send all slots.
            const int count = 24;
            const int recLen = 0x6F;
            byte[] b = new byte[8 + count * recLen];
            WriteU32(b, 0x00, count);
            WriteU16(b, 0x04, 0);
            WriteU16(b, 0x06, recLen);
            for (int i = 0; i < count; i++)
            {
                byte[] rec = BuildPlayerRecordForSlot(i);
                Buffer.BlockCopy(rec, 0, b, 8 + i * recLen, recLen);
            }
            return b;
        }

        static byte[] BuildAddPlayerInfoPayload()
        {
            return BuildAddPlayerInfoPayloadForSlot(0);
        }

        static byte[] BuildAddPlayerInfoPayloadForSlot(int slot)
        {
            if (slot < 0) slot = 0;
            if (slot > 23) slot = 23;
            return BuildPlayerRecordForSlot(slot);
        }

        static byte[] BuildOptionInfoPayload()
        {
            // V24: do NOT synthesize game options from map.o/g_map_opt.
            // The popup "游戏选项数目非法 35/20" proves that exporting g_map_opt keys as network options is wrong.
            // map.o contains a local Lua option/default table, not the wire-format option selection list.
            // Safe baseline: send zero selected network options, matching the older V19 path that the client accepted.
            // After the real option wire format is recovered, this can be replaced with at most 20 selected option records.
            return new byte[] { 0x00 };
        }

        static byte[] BuildItemInfoPayload()
        {
            // opcode 0x016E parser reads WORD count then count records of 0x13 bytes.
            return new byte[] { 0x00, 0x00 };
        }

        static byte[] BuildRoomInfoPayload()
        {
            // internal opcode 0x0186 logs recv room info(%u).
            // V20 sent only 4 bytes, leaving room/session state too empty. Keep the first DWORD compatible,
            // then append conservative room metadata used by script/session checks.
            byte[] b = new byte[0x20];
            WriteU32(b, 0x00, 1);      // room/session id
            WriteU32(b, 0x04, 10002);  // map id
            WriteU32(b, 0x08, (uint)Math.Max(1, LocalPlayerSlot));
            WriteU32(b, 0x0C, 1);      // current human player count on this client
            WriteU32(b, 0x10, 24);     // map max slots
            WriteU32(b, 0x14, (uint)(DateTimeOffset.UtcNow.ToUnixTimeSeconds()));
            WriteU32(b, 0x18, 1);      // game mode/session ok candidate
            WriteU32(b, 0x1C, 0);
            return b;
        }

        static byte[] BuildGameStartFirstTurnPayload()
        {
            // game.exe dispatch 0x0138 reads exactly 5 bytes:
            // DWORD turn/frame, BYTE type. type 1 or 3 can start game logic.
            // V19 keeps type=1 by default; Type3 variant is kept for protocol comparison.
            byte[] b = new byte[5];
            WriteU32(b, 0, 0);
            b[4] = String.Equals(ProtocolVariant, "Type3", StringComparison.OrdinalIgnoreCase) ? (byte)3 : (byte)1;
            return b;
        }

        static bool ShouldSendContinuousTurnStream()
        {
            return String.Equals(ProtocolVariant, "TurnStream", StringComparison.OrdinalIgnoreCase);
        }

        static bool ShouldSendFramePulse()
        {
            return String.Equals(ProtocolVariant, "FramePulse", StringComparison.OrdinalIgnoreCase) ||
                   String.Equals(ProtocolVariant, "Type3Pulse", StringComparison.OrdinalIgnoreCase);
        }

        static byte[] BuildFramePulsePayload(uint frame)
        {
            // V45: sparse type=1/type=3 frame pulse. This is deliberately smaller than TurnStream:
            // no synthetic 0x012E command is embedded. It tests whether the engine clock advances
            // when the server provides frame ticks while leaving command execution to the client/map.
            byte[] b = new byte[5];
            WriteU32(b, 0, frame);
            b[4] = String.Equals(ProtocolVariant, "Type3Pulse", StringComparison.OrdinalIgnoreCase) ? (byte)3 : (byte)1;
            return b;
        }

        static void SendSessionPlayerBundle(NetworkStream ns, int assignedSlot, string why, ref uint turnStreamFrame)
        {
            SendPacket(ns, 0x0130, BuildPlayerInfoListPayload(), why + "_player_info_list_internal_015A");
            SendPacket(ns, 0x0150, BuildAddPlayerInfoPayloadForSlot(assignedSlot), why + "_add_player_info_internal_017A_assigned_slot_" + (assignedSlot + 1).ToString());
            SendPacket(ns, 0x0142, BuildOptionInfoPayload(), why + "_option_info_internal_016C");
            SendPacket(ns, 0x0144, BuildItemInfoPayload(), why + "_item_info_internal_016E");
            SendPacket(ns, 0x015C, BuildRoomInfoPayload(), why + "_room_info_internal_0186");
            if (ShouldSendContinuousTurnStream())
            {
                SendPacket(ns, 0x0138, BuildCmd012ETurnPayload(turnStreamFrame), why + "_turnstream_0138_frame_" + turnStreamFrame.ToString());
                turnStreamFrame++;
            }
        }

        static byte[] BuildCmd012ETurnPayload(uint frame)
        {
            // V7: type=2 turn packet with one length-prefixed 0x012E no-op/sync command.
            // Empty type=2 turn packets were accepted but did not drive do_cmd_list/time-flow.
            // Layout: DWORD frame, BYTE type=2, WORD cmdLen=6, WORD cmd=0x012E, BYTE playerPos=0, BYTE flag=0, WORD reserved=0.
            byte[] b = new byte[13];
            WriteU32(b, 0, frame);
            b[4] = 2;
            WriteU16(b, 5, 6);
            WriteU16(b, 7, 0x012E);
            b[9] = 0;
            b[10] = 0;
            WriteU16(b, 11, 0);
            return b;
        }

        static byte[] BuildHeartbeatEchoPayload(uint keepAlive)
        {
            byte[] b = new byte[4];
            WriteU32(b, 0, keepAlive);
            return b;
        }

        static byte[] BuildHeartbeatEchoPayloadFromClientPacket(byte[] clientPacket, uint fallbackKeepAlive)
        {
            // V45: delay UI likely expects the exact 4-byte token from client 0x025D to be echoed in server 0x015D.
            // Previous builds sent our keepCounter instead, which can keep the connection alive but leave 延时 blank.
            if (clientPacket != null && clientPacket.Length >= 8)
            {
                byte[] b = new byte[clientPacket.Length - 4];
                Buffer.BlockCopy(clientPacket, 4, b, 0, b.Length);
                return b;
            }
            return BuildHeartbeatEchoPayload(fallbackKeepAlive);
        }

        static System.Collections.Generic.List<byte[]> ExtractPacketsByOpcode(byte[] buf, int len, ushort opcode)
        {
            var list = new System.Collections.Generic.List<byte[]>();
            for (int i = 0; i + 3 < len; i++)
            {
                ushort op = BitConverter.ToUInt16(buf, i);
                ushort plen = BitConverter.ToUInt16(buf, i + 2);
                if (op == opcode && plen >= 4 && i + plen <= len)
                {
                    byte[] p = new byte[plen];
                    Buffer.BlockCopy(buf, i, p, 0, plen);
                    list.Add(p);
                    i += plen - 1;
                }
            }
            return list;
        }

        static byte[] BuildClientCommandAckPayload(byte[] clientPacket)
        {
            // V45: 0x0263 is the first non-heartbeat in-game client packet observed after the map survives longer.
            // Server opcodes usually mirror client 0x02xx as 0x01xx for acknowledgements.
            // Echo only the payload portion as a conservative ACK probe; the full raw packet is also forwarded in a turn frame.
            if (clientPacket == null || clientPacket.Length <= 4) return new byte[0];
            byte[] b = new byte[clientPacket.Length - 4];
            Buffer.BlockCopy(clientPacket, 4, b, 0, b.Length);
            return b;
        }

        static byte[] BuildGenericMirrorAckPayload(byte[] clientPacket)
        {
            // V45 reconnect/session guard: for client 0x02xx requests that expect a mirrored 0x01xx response,
            // echo the payload bytes exactly. This is used for 0x026A and 0x0265 diagnostics.
            if (clientPacket == null || clientPacket.Length <= 4) return new byte[0];
            byte[] b = new byte[clientPacket.Length - 4];
            Buffer.BlockCopy(clientPacket, 4, b, 0, b.Length);
            return b;
        }

        static byte[] BuildClientCommandTurnPayload(uint frame, byte[] clientPacket)
        {
            // Type=2 turn packets carry a length-prefixed command list.
            // Earlier builds sent only a synthetic 0x012E no-op. V45 forwards the client's real 0x0263 packet
            // as a command candidate so the host-service path can drive command/trigger progression instead of ignoring it.
            if (clientPacket == null) clientPacket = new byte[0];
            int cmdLen = clientPacket.Length;
            if (cmdLen > 0xFFFF) cmdLen = 0xFFFF;
            byte[] b = new byte[7 + cmdLen];
            WriteU32(b, 0, frame);
            b[4] = 2;
            WriteU16(b, 5, (ushort)cmdLen);
            if (cmdLen > 0) Buffer.BlockCopy(clientPacket, 0, b, 7, cmdLen);
            return b;
        }

        static bool ContainsOpcode(byte[] buf, int len, ushort opcode)
        {
            for (int i = 0; i + 3 < len; i++)
            {
                ushort op = BitConverter.ToUInt16(buf, i);
                ushort plen = BitConverter.ToUInt16(buf, i + 2);
                if (op == opcode && plen >= 4 && i + plen <= len) return true;
            }
            return false;
        }

        static bool ContainsLoadCompleteProgress(byte[] buf, int len)
        {
            // Client progress packet observed: 61 02 06 00 XX 64
            // XX reaches 0x64 when loading reports 100%.
            for (int i = 0; i + 5 < len; i++)
            {
                if (buf[i] == 0x61 && buf[i+1] == 0x02 && buf[i+2] == 0x06 && buf[i+3] == 0x00 && buf[i+4] == 0x64 && buf[i+5] == 0x64)
                    return true;
            }
            return false;
        }

        static void SendPacket(NetworkStream ns, ushort opcode, byte[] payload, string why)
        {
            byte[] p = BuildPacket(opcode, payload);
            ns.Write(p, 0, p.Length);
            ns.Flush();
            Log("[TCP] send opcode=0x" + opcode.ToString("X4") + " len=" + p.Length + " why=" + why + " hex=" + Hex(p, p.Length, 128));
            SavePacket("tcp_send", p, p.Length, why);
        }

        static void StartUdpTrace()
        {
            Thread t = new Thread(delegate()
            {
                UdpClient udp = null;
                try
                {
                    udp = new UdpClient(new IPEndPoint(BindAddress, HostPort));
                    udp.Client.ReceiveTimeout = 1000;
                    Log("[FINAL] UDP listening on " + BindAddress.ToString() + ":" + HostPort.ToString());
                    IPEndPoint remote = new IPEndPoint(IPAddress.Any, 0);
                    while (!StopFlag)
                    {
                        try
                        {
                            byte[] data = udp.Receive(ref remote);
                            Log("[UDP] recv " + data.Length + " from " + remote.ToString() + " hex=" + Hex(data, data.Length, 128));
                            SavePacket("udp_recv", data, data.Length, remote.ToString());
                            try
                            {
                                udp.Send(data, data.Length, remote);
                                Log("[UDP] echo " + data.Length.ToString() + " to " + remote.ToString());
                                SavePacket("udp_send_echo", data, data.Length, remote.ToString());
                            }
                            catch (Exception ex) { Log("[UDP] echo warn " + ex.Message); }
                        }
                        catch (SocketException ex)
                        {
                            if (ex.SocketErrorCode != SocketError.TimedOut) Log("[UDP] socket " + ex.SocketErrorCode.ToString());
                        }
                    }
                }
                catch (Exception ex) { Log("[UDP] error " + ex.Message); }
                finally { if (udp != null) udp.Close(); }
            });
            t.IsBackground = true;
            t.Start();
        }

        static void StartTcpProto()
        {
            Thread t = new Thread(delegate()
            {
                TcpListener listener = null;
                try
                {
                    listener = new TcpListener(BindAddress, HostPort);
                    listener.Start();
                    Log("[FINAL] TCP listening on " + BindAddress.ToString() + ":" + HostPort.ToString());
                    while (!StopFlag)
                    {
                        if (!listener.Pending()) { Thread.Sleep(50); continue; }
                        TcpClient client = listener.AcceptTcpClient();
                        ThreadPool.QueueUserWorkItem(delegate(object state)
                        {
                            TcpClient c = (TcpClient)state;
                            try
                            {
                                int assignedSlot = AllocateConnectionSlot();
                                Log("[TCP] accept " + c.Client.RemoteEndPoint.ToString() + " assignedSlot=" + (assignedSlot + 1).ToString());
                                try { c.NoDelay = true; } catch {}
                                try { c.SendTimeout = 5000; } catch {}
                                try { c.ReceiveTimeout = 0; } catch {}
                                try { c.Client.SetSocketOption(SocketOptionLevel.Socket, SocketOptionName.KeepAlive, true); } catch {}
                                NetworkStream ns = c.GetStream();
                                byte[] buf = new byte[65536];
                                bool sentInit = false;
                                uint turn = GlobalTurn > 1 ? GlobalTurn : 1;
                                uint keepCounter = turn;
                                bool clientReady = GlobalClientReady;
                                bool readyByTimeout = false;
                                bool sentGameStart = false;
                                bool sentPlayerInfo = false;
                                uint turnStreamFrame = turn > 1 ? turn : 1;
                                if (clientReady) Log("[RECONNECT_V24] new TCP session starts in ready mode; assignedSlot=" + (assignedSlot + 1).ToString() + " globalTurn=" + GlobalTurn.ToString() + " globalPlayerInfo=" + GlobalPlayerInfoSent.ToString() + " globalGameStarted=" + GlobalGameStarted.ToString());
                                DateTime sessionStart = DateTime.Now;
                                DateTime lastControl = DateTime.MinValue;
                                DateTime lastFramePulse = DateTime.MinValue;

                                // V45: do NOT start the game/session before the client reports map-load completion.
                                // V37 sent start=2 too early; logs then showed the real 0x0261 progress100 + 0x025F ready pair being ignored.
                                // V45 keeps the engine in loading control state until 0x0261/0x025F arrives, then sends player/session tables and first turn.
                                try
                                {
                                    Log("[V45_BOOTSTRAP] post-load state machine: initial login_result + loading control only. Waiting for client 0x0261 progress100 / 0x025F ready.");
                                    SendPacket(ns, 0x013A, BuildLoginResultPayload(), "v45_bootstrap_login_result_loading_only");
                                    SendPacket(ns, 0x0133, BuildControlPayload(turn, false, keepCounter), "v45_bootstrap_control_loading_start1");
                                    sentInit = true;
                                    lastControl = DateTime.Now;
                                    turn++;
                                    keepCounter++;
                                    GlobalTurn = turn;
                                }
                                catch (Exception ex)
                                {
                                    Log("[V45_BOOTSTRAP_WARN] " + ex.Message);
                                }

                                while (!StopFlag && c.Connected)
                                {
                                    if (sentInit && (DateTime.Now - lastControl).TotalMilliseconds >= 100)
                                    {
                                        if (!clientReady && !readyByTimeout && (DateTime.Now - sessionStart).TotalMilliseconds > 12000)
                                        {
                                            readyByTimeout = true;
                                            Log("[V45_WAIT] still waiting for 0x0261/0x025F load-ready; keeping start=1 loading control instead of forcing game start early.");
                                        }
                                        SendPacket(ns, 0x0133, BuildControlPayload(turn, clientReady, keepCounter), clientReady ? "control_ready_turn" : "control_loading_turn");
                                        if (clientReady && !sentGameStart)
                                        {
                                            SendPacket(ns, 0x0138, BuildGameStartFirstTurnPayload(), "game_start_first_turn_0138_after_ready");
                                            sentGameStart = true;
                                            GlobalGameStarted = true;
                                        }
                                        if (clientReady && sentGameStart && sentPlayerInfo && ShouldSendFramePulse() && (DateTime.Now - lastFramePulse).TotalMilliseconds >= 1200)
                                        {
                                            SendPacket(ns, 0x0138, BuildFramePulsePayload(turnStreamFrame), "v45_sparse_framepulse_timer_0138_frame_" + turnStreamFrame.ToString());
                                            lastFramePulse = DateTime.Now;
                                            turnStreamFrame++;
                                        }
                                        if (clientReady && sentGameStart && sentPlayerInfo && ShouldSendContinuousTurnStream())
                                        {
                                            SendPacket(ns, 0x0138, BuildCmd012ETurnPayload(turnStreamFrame), "cmd012e_turn_stream_0138_type2_frame_" + turnStreamFrame.ToString());
                                            turnStreamFrame++;
                                        }
                                        lastControl = DateTime.Now;
                                        turn++;
                                        keepCounter++;
                                        GlobalTurn = turn;
                                    }

                                    if (!ns.DataAvailable) { Thread.Sleep(10); continue; }
                                    int n = 0;
                                    try { n = ns.Read(buf, 0, buf.Length); }
                                    catch (IOException) { break; }
                                    if (n <= 0) break;
                                    Log("[TCP] recv " + n + " hex=" + Hex(buf, n, 128));
                                    SavePacket("tcp_recv", buf, n, c.Client.RemoteEndPoint.ToString());
                                    if (ContainsOpcode(buf, n, 0x0259))
                                    {
                                        string tracePath259 = Path.Combine(Path.GetDirectoryName(LogPath), "SL10002_0259_v45_trace.txt");
                                        var loginPackets = ExtractPacketsByOpcode(buf, n, 0x0259);
                                        Log("[STATE] client 0x0259 login/map-session request detected; V45 sends mirrored 0x0159 plus login/session seed. count=" + loginPackets.Count.ToString());
                                        File.AppendAllText(tracePath259, DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss.fff") + " raw=" + Hex(buf, n, n) + " clientReady=" + clientReady.ToString() + "\r\n", Encoding.UTF8);
                                        foreach (byte[] lp in loginPackets)
                                        {
                                            SendPacket(ns, 0x0159, BuildGenericMirrorAckPayload(lp), "v45_0259_0159_mirror_ack");
                                        }
                                        SendPacket(ns, 0x013A, BuildLoginResultPayload(), "v45_0259_login_result_seed");
                                        if (!sentPlayerInfo)
                                        {
                                            sentPlayerInfo = true;
                                            GlobalPlayerInfoSent = true;
                                            SendSessionPlayerBundle(ns, assignedSlot, "v45_0259_session_seed", ref turnStreamFrame);
                                        }
                                    }

                                    if (ContainsOpcode(buf, n, 0x0265))
                                    {
                                        Log("[STATE] client sent 0x0265 exit/close notification; V45 sends only mirrored 0x0165 ACK; exitguard session refresh is disabled to avoid polluting the close path.");
                                        var exitPackets = ExtractPacketsByOpcode(buf, n, 0x0265);
                                        if (exitPackets.Count == 0) SendPacket(ns, 0x0165, new byte[0], "v45_exit_0165_empty_ack");
                                        foreach (byte[] ep in exitPackets) SendPacket(ns, 0x0165, BuildGenericMirrorAckPayload(ep), "v45_exit_0165_mirror_ack");
                                        Log("[V45_EXIT_ACK_ONLY] No player/session table refresh is sent after 0x0265; client close decision is treated as final diagnostic signal.");
                                    }

                                    bool hasProgressPacket = ContainsOpcode(buf, n, 0x0261);
                                    bool hasReadyPacket = ContainsOpcode(buf, n, 0x025F);
                                    bool hasProgress100 = ContainsLoadCompleteProgress(buf, n);
                                    if (hasProgressPacket || hasReadyPacket || hasProgress100)
                                    {
                                        string tracePathLoad = Path.Combine(Path.GetDirectoryName(LogPath), "SL10002_loadready_v45_trace.txt");
                                        File.AppendAllText(tracePathLoad, DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss.fff") + " raw=" + Hex(buf, n, n) + " hasProgress100=" + hasProgress100.ToString() + " has025F=" + hasReadyPacket.ToString() + "\r\n", Encoding.UTF8);
                                        var progPackets = ExtractPacketsByOpcode(buf, n, 0x0261);
                                        foreach (byte[] pp in progPackets)
                                        {
                                            Log("[STATE] client 0x0261 load progress detected; V45 mirrors 0x0161 ACK but does NOT start session unless progress=100.");
                                            SendPacket(ns, 0x0161, BuildGenericMirrorAckPayload(pp), "v45_0261_0161_progress_ack");
                                        }
                                        var readyPackets = ExtractPacketsByOpcode(buf, n, 0x025F);
                                        foreach (byte[] rp in readyPackets)
                                        {
                                            Log("[STATE] client 0x025F load-ready detected; V45 mirrors 0x015F ACK.");
                                            SendPacket(ns, 0x015F, BuildGenericMirrorAckPayload(rp), "v45_025F_015F_ready_ack");
                                        }

                                        bool postLoadReadyNow = hasReadyPacket || hasProgress100;
                                        if (!clientReady && postLoadReadyNow)
                                        {
                                            clientReady = true;
                                            GlobalClientReady = true;
                                            Log("[STATE] V45 strict post-load transition: progress100/025F confirmed; now sending session/player tables, start=2 control, first game turn.");
                                            if (!sentPlayerInfo)
                                            {
                                                sentPlayerInfo = true;
                                                GlobalPlayerInfoSent = true;
                                                SendSessionPlayerBundle(ns, assignedSlot, "v45_postload_session_bundle", ref turnStreamFrame);
                                            }
                                            SendPacket(ns, 0x013A, BuildLoginResultPayload(), "v45_postload_login_result_refresh");
                                            SendPacket(ns, 0x0133, BuildControlPayload(turn, true, keepCounter), "v45_postload_control_start2");
                                            if (!sentGameStart)
                                            {
                                                SendPacket(ns, 0x0138, BuildGameStartFirstTurnPayload(), "v45_postload_game_start_first_turn");
                                                sentGameStart = true;
                                                GlobalGameStarted = true;
                                            }
                                        }
                                        else if (!clientReady)
                                        {
                                            Log("[V45_PROGRESS_ONLY] progress packet observed but not 100/025F yet; keep loading control, no session/start.");
                                            SendPacket(ns, 0x0133, BuildControlPayload(turn, false, keepCounter), "v45_progress_only_control_loading_start1");
                                        }
                                        lastControl = DateTime.Now;
                                        turn++;
                                        keepCounter++;
                                        GlobalTurn = turn;
                                    }

                                    if (ContainsOpcode(buf, n, 0x025D))
                                    {
                                        // Client TCP heartbeat/check packet was observed once per second in V15 traces.
                                        // V19 immediately answers with fresh control + optional turn frame instead of waiting for the next timer tick.
                                        Log("[STATE] client 0x025D heartbeat/check detected; V45 sends 0x0133 control plus exact 0x015D token echo for delay UI.");
                                        if (!clientReady)
                                        {
                                            Log("[V45_HEARTBEAT_LOADING] heartbeat received before 0x0261/0x025F; echo delay token but keep start=1 loading state.");
                                        }
                                        SendPacket(ns, 0x0133, BuildControlPayload(turn, clientReady, keepCounter), "immediate_control_ack_after_025D");
                                        var hbPackets = ExtractPacketsByOpcode(buf, n, 0x025D);
                                        if (hbPackets.Count == 0)
                                        {
                                            SendPacket(ns, 0x015D, BuildHeartbeatEchoPayload(keepCounter), "heartbeat_echo_fallback_keepcounter_v45");
                                        }
                                        else
                                        {
                                            foreach (byte[] hp in hbPackets)
                                            {
                                                SendPacket(ns, 0x015D, BuildHeartbeatEchoPayloadFromClientPacket(hp, keepCounter), "heartbeat_exact_token_echo_v45");
                                            }
                                        }
                                        if (clientReady && sentGameStart && ShouldSendFramePulse())
                                        {
                                            SendPacket(ns, 0x0138, BuildFramePulsePayload(turnStreamFrame), "v45_sparse_framepulse_0138_frame_" + turnStreamFrame.ToString());
                                            lastFramePulse = DateTime.Now;
                                            turnStreamFrame++;
                                        }
                                        if (clientReady && sentGameStart && ShouldSendContinuousTurnStream())
                                        {
                                            SendPacket(ns, 0x0138, BuildCmd012ETurnPayload(turnStreamFrame), "immediate_cmd012e_after_025D_frame_" + turnStreamFrame.ToString());
                                            turnStreamFrame++;
                                        }
                                        lastControl = DateTime.Now;
                                        turn++;
                                        keepCounter++;
                                        GlobalTurn = turn;
                                    }

                                    if (ContainsOpcode(buf, n, 0x0263))
                                    {
                                        string tracePath263 = Path.Combine(Path.GetDirectoryName(LogPath), "SL10002_0263_v45_trace.txt");
                                        var cmdPackets = ExtractPacketsByOpcode(buf, n, 0x0263);
                                        Log("[STATE] client 0x0263 in-game command/state packet detected; V45 ACKs 0x0163 and forwards it as 0x0138 type=2 turn command candidate. count=" + cmdPackets.Count.ToString());
                                        foreach (byte[] cp in cmdPackets)
                                        {
                                            File.AppendAllText(tracePath263, DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss.fff") + " raw=" + Hex(cp, cp.Length, cp.Length) + "\r\n", Encoding.UTF8);
                                            SendPacket(ns, 0x0163, BuildClientCommandAckPayload(cp), "client_0263_ack_echo_internal_018D");
                                            SendPacket(ns, 0x0138, BuildClientCommandTurnPayload(turnStreamFrame, cp), "client_0263_forward_turn_0138_type2_frame_" + turnStreamFrame.ToString());
                                            turnStreamFrame++;
                                        }
                                        SendPacket(ns, 0x0133, BuildControlPayload(turn, true, keepCounter), "control_after_0263_client_command");
                                        lastControl = DateTime.Now;
                                        turn++;
                                        keepCounter++;
                                        GlobalTurn = turn;
                                    }

                                    if (ContainsOpcode(buf, n, 0x0272))
                                    {
                                        string tracePath272 = Path.Combine(Path.GetDirectoryName(LogPath), "SL10002_0272_v45_trace.txt");
                                        var rPackets = ExtractPacketsByOpcode(buf, n, 0x0272);
                                        Log("[STATE] client 0x0272 postload/game-scene-ready packet detected; V45 sends conservative 0x0172 ACK. count=" + rPackets.Count.ToString());
                                        File.AppendAllText(tracePath272, DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss.fff") + " raw=" + Hex(buf, n, n) + " clientReady=" + clientReady.ToString() + "\r\n", Encoding.UTF8);
                                        if (rPackets.Count == 0) SendPacket(ns, 0x0172, new byte[0], "v45_0272_0172_empty_ack");
                                        foreach (byte[] rp272 in rPackets)
                                        {
                                            SendPacket(ns, 0x0172, BuildGenericMirrorAckPayload(rp272), "v45_0272_0172_mirror_ack");
                                        }
                                        SendPacket(ns, 0x0133, BuildControlPayload(turn, clientReady, keepCounter), clientReady ? "v45_0272_control_ready_ack" : "v45_0272_control_loading_ack");
                                        lastControl = DateTime.Now;
                                        turn++;
                                        keepCounter++;
                                        GlobalTurn = turn;
                                    }

                                    if (ContainsOpcode(buf, n, 0x026A))
                                    {
                                        string tracePath = Path.Combine(Path.GetDirectoryName(LogPath), "SL10002_026A_v45_trace.txt");
                                        var qPackets = ExtractPacketsByOpcode(buf, n, 0x026A);
                                        Log("[STATE] client 0x026A session/reconnect request detected; V45 mirrors 0x016A ACK. clientReady=" + clientReady.ToString() + " count=" + qPackets.Count.ToString());
                                        File.AppendAllText(tracePath, DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss.fff") + " raw=" + Hex(buf, n, n) + " clientReady=" + clientReady.ToString() + "\r\n", Encoding.UTF8);
                                        foreach (byte[] qp in qPackets)
                                        {
                                            SendPacket(ns, 0x016A, BuildGenericMirrorAckPayload(qp), "v45_026A_016A_mirror_ack");
                                        }
                                        if (!clientReady)
                                        {
                                            Log("[V45_026A_LOADING] 0x026A arrived before progress100/025F; do not force start=2, keep loading session.");
                                            SendPacket(ns, 0x013A, BuildLoginResultPayload(), "v45_026A_loading_login_result_ack");
                                            SendPacket(ns, 0x0133, BuildControlPayload(turn, false, keepCounter), "v45_026A_loading_control_start1");
                                            lastControl = DateTime.Now;
                                            turn++;
                                            keepCounter++;
                                            GlobalTurn = turn;
                                        }
                                        else
                                        {
                                            Log("[V45_026A_READY_ACK_PLUS_PLAYER] 0x026A arrived after load-ready; ACK plus add-player refresh for requested session slots.");
                                            foreach (byte[] qp2 in qPackets) { int reqSlot = 0; if (qp2.Length >= 9) reqSlot = Math.Max(0, Math.Min(23, ((int)qp2[4] | ((int)qp2[5] << 8) | ((int)qp2[6] << 16) | ((int)qp2[7] << 24)) - 1)); SendPacket(ns, 0x0150, BuildAddPlayerInfoPayloadForSlot(reqSlot), "v45_026A_add_player_refresh_slot_" + (reqSlot+1).ToString()); }
                                            SendPacket(ns, 0x015C, BuildRoomInfoPayload(), "v45_026A_room_refresh");
                                            SendPacket(ns, 0x0133, BuildControlPayload(turn, true, keepCounter), "v45_026A_control_start2_ackplus");
                                            lastControl = DateTime.Now;
                                            turn++;
                                            keepCounter++;
                                            GlobalTurn = turn;
                                        }
                                    }

                                    if (!sentInit)
                                    {
                                        SendPacket(ns, 0x013A, BuildLoginResultPayload(), "login_result_probe_v19_real_server_time");
                                        if (clientReady && !sentPlayerInfo)
                                        {
                                            sentPlayerInfo = true;
                                            GlobalPlayerInfoSent = true;
                                            SendSessionPlayerBundle(ns, assignedSlot, "reconnect_immediate_session_bundle", ref turnStreamFrame);
                                        }
                                        SendPacket(ns, 0x0133, BuildControlPayload(turn, clientReady, keepCounter), "first_control_loading_turn");
                                        lastControl = DateTime.Now;
                                        turn++;
                                        keepCounter++;
                                        GlobalTurn = turn;
                                        sentInit = true;
                                    }
                                }
                            }
                            catch (Exception ex) { Log("[TCP] client error " + ex.Message); }
                            finally { try { c.Close(); } catch {} Log("[TCP] closed"); }
                        }, client);
                    }
                }
                catch (Exception ex) { Log("[TCP] error " + ex.Message); }
                finally { if (listener != null) listener.Stop(); }
            });
            t.IsBackground = true;
            t.Start();
        }


        static System.Collections.Generic.List<string> ExtractMapResourceRefs(string objPath)
        {
            byte[] data = File.ReadAllBytes(objPath);
            System.Collections.Generic.HashSet<string> set = new System.Collections.Generic.HashSet<string>(StringComparer.OrdinalIgnoreCase);
            StringBuilder cur = new StringBuilder();
            Action<string> addIfResource = delegate(string t)
            {
                if (t.StartsWith("sanguo/model/", StringComparison.OrdinalIgnoreCase) ||
                    t.StartsWith("sanguo/terrain/", StringComparison.OrdinalIgnoreCase) ||
                    t.StartsWith("sanguo/effect/", StringComparison.OrdinalIgnoreCase) ||
                    t.StartsWith("sanguo/ui/", StringComparison.OrdinalIgnoreCase))
                {
                    set.Add(t.Replace('/', Path.DirectorySeparatorChar));
                }
            };
            for (int i = 0; i < data.Length; i++)
            {
                byte b = data[i];
                if (b >= 32 && b <= 126) cur.Append((char)b);
                else
                {
                    if (cur.Length >= 4) addIfResource(cur.ToString());
                    cur.Length = 0;
                }
            }
            if (cur.Length >= 4) addIfResource(cur.ToString());
            System.Collections.Generic.List<string> all = new System.Collections.Generic.List<string>(set);
            all.Sort(StringComparer.OrdinalIgnoreCase);
            return all;
        }

        static bool IsRealResourceFile(string path)
        {
            try
            {
                if (!File.Exists(path)) return false;
                FileInfo fi = new FileInfo(path);
                if (fi.Length <= 0) return false;
                string lower = path.ToLowerInvariant();
                byte[] head = File.ReadAllBytes(path);
                if (lower.EndsWith(".dds")) return head.Length >= 4096 && head[0] == 0x44 && head[1] == 0x44 && head[2] == 0x53 && head[3] == 0x20;
                if (lower.EndsWith(".tga")) return head.Length >= 1024 && head.Length >= 18;
                if (lower.EndsWith(".bmp")) return head.Length >= 54 && head[0] == 0x42 && head[1] == 0x4D;
                return fi.Length > 0;
            }
            catch { return false; }
        }

        static string FindRealResourceSource(string rel)
        {
            string rootRes = Path.Combine(RootDir, "resource", rel);
            string coreRes = Path.Combine(RootDir, "core", "resource", rel);
            string compat = Path.Combine(RootDir, "compat_resource", rel);
            if (IsRealResourceFile(rootRes)) return rootRes;
            if (IsRealResourceFile(coreRes)) return coreRes;
            // compat_resource is allowed only when it is a real file. This intentionally rejects the old 192B DDS UI stubs.
            if (IsRealResourceFile(compat)) return compat;
            return null;
        }

        static void CopyRealResourceToSearchPath(string src, string dst, string rel, string tag)
        {
            try
            {
                if (IsRealResourceFile(dst))
                {
                    Log("[V24_RESOURCE_KEEP] " + tag + " " + dst + " size=" + new FileInfo(dst).Length.ToString());
                    return;
                }
                if (LooksLikeTinyPlaceholderVisual(dst))
                {
                    QuarantineFile(dst, "V24 bad placeholder before real mount");
                }
                EnsureDir(Path.GetDirectoryName(dst));
                File.Copy(src, dst, true);
                Log("[V24_RESOURCE_MOUNT] " + rel + " " + src + " -> " + dst + " size=" + new FileInfo(dst).Length.ToString());
            }
            catch (Exception ex)
            {
                Log("[V24_RESOURCE_MOUNT_WARN] " + rel + " -> " + dst + " " + ex.Message);
            }
        }

        static void MountReferencedMapResources(string objPath)
        {
            string mountReport = Path.Combine(RootDir, "SL10002_resource_mount_v45.log");
            StringBuilder sb = new StringBuilder();
            int total = 0, mounted = 0, already = 0, missing = 0, skippedCompat = 0;
            try
            {
                System.Collections.Generic.List<string> refs = ExtractMapResourceRefs(objPath);
                total = refs.Count;
                sb.AppendLine("SL10002 V24 quiet resource mount report");
                sb.AppendLine("obj=" + objPath);
                sb.AppendLine("rule=mirror only real resource files into data\\resource and data\\core\\resource; never create fake UI/TGA/DDS");
                sb.AppendLine();
                foreach (string rel in refs)
                {
                    string rootDst = Path.Combine(RootDir, "resource", rel);
                    string coreDst = Path.Combine(RootDir, "core", "resource", rel);
                    if (LooksLikeTinyPlaceholderVisual(rootDst)) QuarantineFile(rootDst, "V24 bad map-resource placeholder before mount");
                    if (LooksLikeTinyPlaceholderVisual(coreDst)) QuarantineFile(coreDst, "V24 bad core map-resource placeholder before mount");
                    string src = FindRealResourceSource(rel);
                    if (src == null)
                    {
                        string compat = Path.Combine(RootDir, "compat_resource", rel);
                        if (File.Exists(compat) && !IsRealResourceFile(compat)) { skippedCompat++; sb.AppendLine("SKIP_BAD_COMPAT\t" + rel + "\t" + compat + "\tsize=" + new FileInfo(compat).Length.ToString()); }
                        else { missing++; sb.AppendLine("MISSING_REAL\t" + rel); }
                        continue;
                    }
                    bool rootOk = IsRealResourceFile(rootDst);
                    bool coreOk = IsRealResourceFile(coreDst);
                    if (rootOk && coreOk)
                    {
                        already++;
                        sb.AppendLine("OK_BOTH\t" + rel + "\tsrc=" + src);
                        continue;
                    }
                    CopyRealResourceToSearchPath(src, rootDst, rel, "root");
                    CopyRealResourceToSearchPath(src, coreDst, rel, "core");
                    mounted++;
                    sb.AppendLine("MOUNTED\t" + rel + "\tsrc=" + src);
                }
                sb.Insert(0, "summary total=" + total.ToString() + " mounted=" + mounted.ToString() + " already=" + already.ToString() + " missing=" + missing.ToString() + " skipped_bad_compat=" + skippedCompat.ToString() + Environment.NewLine);
                File.WriteAllText(mountReport, sb.ToString(), Encoding.UTF8);
                Log("[V45_RESOURCE_MOUNT_SUMMARY] total=" + total.ToString() + " mounted=" + mounted.ToString() + " already=" + already.ToString() + " missing=" + missing.ToString() + " skipped_bad_compat=" + skippedCompat.ToString() + " report=" + mountReport);
            }
            catch (Exception ex)
            {
                Log("[V24_RESOURCE_MOUNT_FATAL_WARN] " + ex.Message);
                try { File.WriteAllText(mountReport, sb.ToString() + Environment.NewLine + "FATAL_WARN=" + ex.Message, Encoding.UTF8); } catch {}
            }
        }

        static void WriteMapResourceReport(string objPath)
        {
            try
            {
                string report = Path.Combine(RootDir, "SL10002_scene_resource_check.txt");
                byte[] data = File.ReadAllBytes(objPath);
                System.Collections.Generic.HashSet<string> set = new System.Collections.Generic.HashSet<string>(StringComparer.OrdinalIgnoreCase);
                StringBuilder cur = new StringBuilder();
                for (int i = 0; i < data.Length; i++)
                {
                    byte b = data[i];
                    if (b >= 32 && b <= 126) cur.Append((char)b);
                    else
                    {
                        if (cur.Length >= 4)
                        {
                            string t = cur.ToString();
                            if (t.StartsWith("sanguo/model/", StringComparison.OrdinalIgnoreCase) ||
                                t.StartsWith("sanguo/terrain/", StringComparison.OrdinalIgnoreCase) ||
                                t.StartsWith("sanguo/effect/", StringComparison.OrdinalIgnoreCase) ||
                                t.StartsWith("sanguo/ui/", StringComparison.OrdinalIgnoreCase))
                            {
                                set.Add(t.Replace('/', Path.DirectorySeparatorChar));
                            }
                        }
                        cur.Length = 0;
                    }
                }
                if (cur.Length >= 4)
                {
                    string t = cur.ToString();
                    if (t.StartsWith("sanguo/model/", StringComparison.OrdinalIgnoreCase) ||
                        t.StartsWith("sanguo/terrain/", StringComparison.OrdinalIgnoreCase) ||
                        t.StartsWith("sanguo/effect/", StringComparison.OrdinalIgnoreCase) ||
                        t.StartsWith("sanguo/ui/", StringComparison.OrdinalIgnoreCase))
                    {
                        set.Add(t.Replace('/', Path.DirectorySeparatorChar));
                    }
                }

                System.Collections.Generic.List<string> all = new System.Collections.Generic.List<string>(set);
                all.Sort(StringComparer.OrdinalIgnoreCase);
                System.Collections.Generic.List<string> missing = new System.Collections.Generic.List<string>();
                System.Collections.Generic.List<string> exists = new System.Collections.Generic.List<string>();
                foreach (string rel in all)
                {
                    string full = Path.Combine(RootDir, "resource", rel);
                    if (File.Exists(full)) exists.Add(rel); else missing.Add(rel);
                }
                StringBuilder sb = new StringBuilder();
                sb.AppendLine("SL10002 scene resource preflight");
                sb.AppendLine("obj=" + objPath);
                sb.AppendLine("total_refs=" + all.Count.ToString());
                sb.AppendLine("exists=" + exists.Count.ToString());
                sb.AppendLine("missing=" + missing.Count.ToString());
                sb.AppendLine();
                sb.AppendLine("[MISSING]");
                foreach (string m in missing) sb.AppendLine(m);
                sb.AppendLine();
                sb.AppendLine("[EXISTS]");
                foreach (string e in exists) sb.AppendLine(e);
                File.WriteAllText(report, sb.ToString(), Encoding.UTF8);
                Log("[SCENE_RESOURCE_CHECK] total=" + all.Count.ToString() + " exists=" + exists.Count.ToString() + " missing=" + missing.Count.ToString() + " report=" + report);
                int preview = Math.Min(20, missing.Count);
                for (int i = 0; i < preview; i++) Log("[SCENE_RESOURCE_MISSING] " + missing[i]);
            }
            catch (Exception ex)
            {
                Log("[SCENE_RESOURCE_CHECK_WARN] " + ex.Message);
            }
        }


        static void PatchGameInitLuaExitGuard()
        {
            try
            {
                string script = Path.Combine(RootDir, @"scripts\game_init.lua");
                if (!File.Exists(script))
                {
                    Directory.CreateDirectory(Path.GetDirectoryName(script));
                    File.WriteAllText(script, "-- SL10002 V45 generated scripts/game_init.lua bootstrap\r\n", Encoding.Default);
                    Log("[LUA_EXIT_GUARD_CREATE] scripts/game_init.lua did not exist; created bootstrap: " + script);
                }
                byte[] oldBytes = File.ReadAllBytes(script);
                string oldText = Encoding.Default.GetString(oldBytes);
                if (oldText.IndexOf("SL10002_LUA_LOGIC_GUARD_V24", StringComparison.Ordinal) >= 0)
                {
                    Log("[LUA_LOGIC_GUARD_KEEP] V19 marker already exists in scripts/game_init.lua");
                    return;
                }
                string bak = script + ".bak_SL10002_LUA_LOGIC_GUARD_V24";
                if (!File.Exists(bak))
                {
                    File.Copy(script, bak, true);
                    Log("[LUA_LOGIC_GUARD_BACKUP] " + bak);
                }
                string patch = @"
-- SL10002_LUA_LOGIC_GUARD_V24
-- Purpose: keep map logic alive long enough for LAN HostService, and log whether Lua reaches AddCha/AddSceneObject/Timer chain.
if not __SL10002_LUA_LOGIC_GUARD_V24 then
  __SL10002_LUA_LOGIC_GUARD_V24 = true

  local function __sl10002_log(msg)
    local ok, err = pcall(function()
      local line = os.date('%Y-%m-%d %H:%M:%S') .. ' ' .. tostring(msg) .. '\n'
      local f = io.open('SL10002_lua_trace_v24.log', 'a')
      if f then f:write(line); f:close() end
    end)
  end

  local function __sl10002_addcha_log(msg)
    local ok, err = pcall(function()
      local line = os.date('%Y-%m-%d %H:%M:%S') .. ' ' .. tostring(msg) .. '\n'
      local f = io.open('AddCha.log', 'a')
      if f then f:write(line); f:close() end
    end)
  end

  local function __sl10002_pack_args(...)
    local n = select('#', ...)
    local t = {}
    for i = 1, n do t[#t+1] = tostring(select(i, ...)) end
    return table.concat(t, ',')
  end

  local function __sl10002_wrap_func(name, is_addcha)
    local real = rawget(_G, name)
    if type(real) ~= 'function' then
      __sl10002_log('[WRAP_WAIT] '..name..' not function yet')
      return false
    end
    local mark = '__SL10002_REAL_' .. name .. '_V24'
    if rawget(_G, mark) then return true end
    rawset(_G, mark, real)
    rawset(_G, name, function(...)
      local args = __sl10002_pack_args(...)
      if is_addcha then __sl10002_addcha_log('[CALL] '..name..'('..args..')') end
      __sl10002_log('[CALL] '..name..'('..args..')')
      return real(...)
    end)
    __sl10002_log('[WRAPPED] '..name)
    if is_addcha then __sl10002_addcha_log('[WRAPPED] '..name) end
    return true
  end

  local function __sl10002_wrap_all()
    __sl10002_wrap_func('AddCha', true)
    __sl10002_wrap_func('lua_sceAddCha', true)
    __sl10002_wrap_func('lua_AddCha_New', true)
    __sl10002_wrap_func('lua_AddCha_NewEx', true)
    __sl10002_wrap_func('lua_AddCha_NewEx_Use_ContrlID', true)
    __sl10002_wrap_func('AddSceneObject', false)
    __sl10002_wrap_func('lua_AddTimer', false)
    __sl10002_wrap_func('lua_EnableTimer', false)
    __sl10002_wrap_func('lua_EnableAllTimer', false)
    __sl10002_wrap_func('GetSessionPlayerInfo', false)
    __sl10002_wrap_func('GetSessionPlayerInfoEx', false)
    __sl10002_wrap_func('GameEvent_MapInit', false)
    __sl10002_wrap_func('map_init', false)
  end

  __sl10002_wrap_all()
  __sl10002_log('[BOOT] V24 Lua logic guard installed')
  __sl10002_addcha_log('[BOOT] V24 AddCha logger installed')

  local function __sl10002_block_func(name)
    local old = rawget(_G, name)
    rawset(_G, '__SL10002_REAL_EXIT_' .. name .. '_V24', old)
    rawset(_G, name, function(...)
      __sl10002_log('[BLOCK_EXIT] '..name..' blocked, args='..__sl10002_pack_args(...))
      return nil
    end)
  end

  -- These are only blocked to prevent frame-5 network bootstrap failure from killing the process before map logic can run.
  __sl10002_block_func('appExit')
  __sl10002_block_func('close_net')
  __sl10002_block_func('CloseNet')
  __sl10002_block_func('CloseNetwork')
  __sl10002_block_func('GameEventCloseWindow')
  __sl10002_block_func('GameEventCloseNet')
  __sl10002_block_func('NotifyOffline')
end
";
                using (FileStream fs = new FileStream(script, FileMode.Append, FileAccess.Write, FileShare.Read))
                {
                    byte[] add = Encoding.Default.GetBytes(patch);
                    fs.Write(add, 0, add.Length);
                }
                Log("[LUA_LOGIC_GUARD_PATCHED] appended V24 AddCha/timer/session diagnostics + exit guard to scripts/game_init.lua; original backup: " + bak);
            }
            catch (Exception ex)
            {
                Log("[LUA_LOGIC_GUARD_WARN] " + ex.Message);
            }
        }



        static void V45CleanOldDiagnostics()
        {
            try
            {
                string[] files = new string[] {
                    "log_mgr", "init.log", "net_state.log", "error.log",
                    "SL10002_map_protocol_v45.log", "SL10002_0261_v45_trace.txt",
                    "SL10002_025F_v45_trace.txt", "SL10002_0263_v45_trace.txt",
                    "SL10002_026A_v45_trace.txt", "SL10002_protocol_stage_v45.log",
                    "SL10002_lan_v42a_launcher.log", "SL10002_launcher_console_v42a.log", "SL10002_protocol_clock_v42a.log",
                    "SL10002_lan_v43_launcher.log", "SL10002_launcher_console_v43.log", "SL10002_protocol_clock_v43.log",
                    "SL10002_map_protocol_v43.log", "SL10002_map_protocol_v42a.log"
                };
                foreach (string f in files)
                {
                    string p = Path.Combine(RootDir, f);
                    if (File.Exists(p))
                    {
                        try { File.Delete(p); Log("[V45_CLEAN] deleted stale diagnostic " + p); }
                        catch (Exception ex) { Log("[V45_CLEAN_WARN] " + p + " " + ex.Message); }
                    }
                }
            }
            catch (Exception ex) { Log("[V45_CLEAN_WARN] " + ex.Message); }
        }

        static bool V45ReadTgaBgra(string path, out int width, out int height, out byte[] bgra)
        {
            width = 0; height = 0; bgra = null;
            try
            {
                if (!File.Exists(path)) return false;
                byte[] d = File.ReadAllBytes(path);
                if (d.Length < 18) return false;
                int idLen = d[0];
                int colorMapType = d[1];
                int imageType = d[2];
                if (colorMapType != 0 || imageType != 2) return false; // uncompressed true-color only
                width = d[12] | (d[13] << 8);
                height = d[14] | (d[15] << 8);
                int bpp = d[16];
                int desc = d[17];
                if (width <= 0 || height <= 0) return false;
                if (bpp != 24 && bpp != 32) return false;
                int bytesPerPixel = bpp / 8;
                int off = 18 + idLen;
                int need = width * height * bytesPerPixel;
                if (off < 0 || off + need > d.Length) return false;
                bgra = new byte[width * height * 4];
                bool topOrigin = (desc & 0x20) != 0;
                for (int y = 0; y < height; y++)
                {
                    int srcY = topOrigin ? y : (height - 1 - y);
                    int srcBase = off + srcY * width * bytesPerPixel;
                    int dstBase = y * width * 4;
                    for (int x = 0; x < width; x++)
                    {
                        int si = srcBase + x * bytesPerPixel;
                        int di = dstBase + x * 4;
                        bgra[di + 0] = d[si + 0];
                        bgra[di + 1] = d[si + 1];
                        bgra[di + 2] = d[si + 2];
                        bgra[di + 3] = (bytesPerPixel == 4) ? d[si + 3] : (byte)255;
                    }
                }
                return true;
            }
            catch { return false; }
        }

        static void V45WriteU32(byte[] b, int off, uint v)
        {
            byte[] x = BitConverter.GetBytes(v);
            Buffer.BlockCopy(x, 0, b, off, 4);
        }

        static bool V45WriteDdsA8R8G8B8(string path, int width, int height, byte[] bgra)
        {
            try
            {
                if (width <= 0 || height <= 0 || bgra == null || bgra.Length < width * height * 4) return false;
                byte[] header = new byte[128];
                header[0] = (byte)'D'; header[1] = (byte)'D'; header[2] = (byte)'S'; header[3] = (byte)' ';
                V45WriteU32(header, 4, 124);
                V45WriteU32(header, 8, 0x0002100Fu); // CAPS|HEIGHT|WIDTH|PITCH|PIXELFORMAT
                V45WriteU32(header, 12, (uint)height);
                V45WriteU32(header, 16, (uint)width);
                V45WriteU32(header, 20, (uint)(width * 4));
                V45WriteU32(header, 76, 32);         // DDS_PIXELFORMAT size
                V45WriteU32(header, 80, 0x00000041u); // RGB | ALPHAPIXELS
                V45WriteU32(header, 88, 32);         // RGBBitCount
                V45WriteU32(header, 92, 0x00FF0000u); // R
                V45WriteU32(header, 96, 0x0000FF00u); // G
                V45WriteU32(header, 100, 0x000000FFu); // B
                V45WriteU32(header, 104, 0xFF000000u); // A
                V45WriteU32(header, 108, 0x00001000u); // DDSCAPS_TEXTURE
                EnsureDir(Path.GetDirectoryName(path));
                using (FileStream fs = new FileStream(path, FileMode.Create, FileAccess.Write, FileShare.Read))
                {
                    fs.Write(header, 0, header.Length);
                    fs.Write(bgra, 0, width * height * 4);
                }
                return true;
            }
            catch (Exception ex) { Log("[V45_TGA2DDS_WRITE_WARN] " + path + " " + ex.Message); return false; }
        }

        static void V45ForceRepairUiDdsFromTga(string relDds)
        {
            try
            {
                string dds = Path.Combine(RootDir, relDds);
                if (V45LooksLikeUsableDds(dds))
                {
                    Log("[V45_UI_OK] " + dds + " size=" + new FileInfo(dds).Length.ToString());
                    return;
                }
                string tga = Path.ChangeExtension(dds, ".tga");
                int w, h; byte[] pixels;
                if (V45ReadTgaBgra(tga, out w, out h, out pixels))
                {
                    if (File.Exists(dds))
                    {
                        string bak = dds + ".bak_SL10002_V45_BEFORE_TGA2DDS_" + DateTime.Now.ToString("yyyyMMdd_HHmmss");
                        try { File.Copy(dds, bak, true); Log("[V45_UI_BACKUP_BAD_DDS] " + dds + " -> " + bak); } catch {}
                    }
                    if (V45WriteDdsA8R8G8B8(dds, w, h, pixels))
                    {
                        Log("[V45_TGA2DDS_OK] " + tga + " -> " + dds + " " + w.ToString() + "x" + h.ToString() + " size=" + new FileInfo(dds).Length.ToString());
                        return;
                    }
                }
                Log("[V45_TGA2DDS_SKIP] cannot convert " + tga + " for " + dds);
            }
            catch (Exception ex) { Log("[V45_TGA2DDS_WARN] " + relDds + " " + ex.Message); }
        }

        static bool V45LooksLikeUsableDds(string path)
        {
            try
            {
                if (!File.Exists(path)) return false;
                FileInfo fi = new FileInfo(path);
                if (fi.Length < 16384) return false;
                byte[] head = new byte[4]; using (FileStream fs = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.ReadWrite)) { int n = fs.Read(head, 0, 4); if (n < 4) return false; }
                return head.Length == 4 && head[0] == 0x44 && head[1] == 0x44 && head[2] == 0x53 && head[3] == 0x20;
            }
            catch { return false; }
        }

        static void V45TryRestoreGoodUiBackup(string rel)
        {
            try
            {
                string path = Path.Combine(RootDir, rel);
                if (V45LooksLikeUsableDds(path))
                {
                    Log("[V45_UI_OK] " + path + " size=" + new FileInfo(path).Length.ToString());
                    return;
                }
                string dir = Path.GetDirectoryName(path);
                string name = Path.GetFileName(path);
                if (String.IsNullOrEmpty(dir) || !Directory.Exists(dir))
                {
                    Log("[V45_UI_WARN] directory missing for " + path);
                    return;
                }
                string[] candidates = Directory.GetFiles(dir, name + ".bak*", SearchOption.TopDirectoryOnly);
                string best = null;
                long bestLen = 0;
                foreach (string c in candidates)
                {
                    string low = c.ToLowerInvariant();
                    if (low.Contains("v16_bad") || low.Contains("bad")) continue;
                    if (!V45LooksLikeUsableDds(c)) continue;
                    long len = new FileInfo(c).Length;
                    if (len > bestLen) { best = c; bestLen = len; }
                }
                if (best != null)
                {
                    File.Copy(best, path, true);
                    Log("[V45_UI_RESTORE_GOOD_BACKUP] " + best + " -> " + path + " size=" + bestLen.ToString());
                }
                else
                {
                    long len = File.Exists(path) ? new FileInfo(path).Length : 0;
                    Log("[V45_UI_WARN] no usable non-BAD backup found for " + path + "; current size=" + len.ToString() + ". V45 will not write fake UI resources.");
                }
            }
            catch (Exception ex) { Log("[V45_UI_WARN] " + rel + " " + ex.Message); }
        }

        static void V45ProtocolOnlyResourceSafety()
        {
            Log("[V45_RESOURCE_PROTOCOL_ONLY] no V16_BAD restore and no fake placeholder UI. If a DDS is invalid, convert its real companion TGA to a standard DDS.");
            V45TryRestoreGoodUiBackup(@"resource\sanguo\ui\loading_misc.dds");
            V45TryRestoreGoodUiBackup(@"resource\sanguo\ui\mission_misc.dds");
            V45TryRestoreGoodUiBackup(@"resource\sanguo\ui\main_misc.dds");
            V45ForceRepairUiDdsFromTga(@"resource\sanguo\ui\loading_misc.dds");
            V45ForceRepairUiDdsFromTga(@"resource\sanguo\ui\mission_misc.dds");
            V45ForceRepairUiDdsFromTga(@"resource\sanguo\ui\main_misc.dds");
        }

        public static int Run(string root, string mode, string hostIpArg, string playerNameArg, int playerSlotArg, string protocolVariantArg)
        {
            RootDir = root;
            LogPath = Path.Combine(root, "SL10002_lan_v45_launcher.log");
            PacketDir = Path.Combine(root, "SL10002_lan_v45_packets");
            if (File.Exists(LogPath)) File.Delete(LogPath);
            if (Directory.Exists(PacketDir)) Directory.Delete(PacketDir, true);
            Directory.CreateDirectory(PacketDir);
            File.WriteAllText(Path.Combine(PacketDir, "packets_index.tsv"), "time\tfile\tinfo\thex_preview\tascii_preview" + Environment.NewLine, Encoding.UTF8);

            V45CleanOldDiagnostics();

            Log("==================================================");
            Log("SL10002 Final Launcher V45 LAN_CORE_HOSTSERVICE");
            Log("root=" + root);
            Log("Mode: V45 RESOURCE-PRELOAD + CONTROLONLY SAFE LOWPORT BASELINE. ModRuntime auto-generation is disabled. This build restores full 10002.o referenced-resource scan before game.exe starts, then validates /mapfile=10002 + UTF-16LE MemoryMap + 29002, player/session tables, start=2 controls, 10Hz control frames with fps=30, and exact 0x025D ping-token echo for delay UI diagnostics.");
            Log("No DLL injection. No process memory write. No VIP/sponsor modification. V45 does not restore experimental game.exe backups. Mod AddCha/AddSceneObj remain disabled. Resource preload is scan/copy/report only, using existing real resource files and no fake placeholders.");
            ConfigureMode(mode, hostIpArg, playerNameArg, playerSlotArg);
            ProtocolVariant = String.IsNullOrWhiteSpace(protocolVariantArg) ? "ControlOnly" : protocolVariantArg.Trim();
            Log("[V45_PROTOCOL] variant=" + ProtocolVariant + " (ControlOnly default: strict postload start=2 + heartbeat token echo; sparse 0x0138 frame pulse disabled. FramePulse/TurnStream remain available for comparison.)");
            Log("==================================================");

            string game = Path.Combine(root, @"core\game.exe");
            string gpigame = Path.Combine(root, @"core\gpigame.dll");
            string mapSrc = Path.Combine(root, @"prepared_map\10002\10002.map");
            string objSrc = Path.Combine(root, @"prepared_map\10002\10002.o");
            string originalMapObj = Path.Combine(root, @"prepared_original\map.o");
            string originalEdt2Obj = Path.Combine(root, @"prepared_original\edt2.o");
            string shader = Path.Combine(root, @"core\shader\pu4nt0_ld.vsh");

            if (!File.Exists(game)) throw new FileNotFoundException("missing core game exe", game);
            if (!File.Exists(gpigame)) throw new FileNotFoundException("missing core gpigame dll", gpigame);
            try {
                Directory.CreateDirectory(Path.Combine(root, "scripts"));
                Directory.CreateDirectory(Path.Combine(root, @"core\scripts"));
                string noOpScript = "-- SL10002 V45 protocol-only bootstrap. No ModRuntime, no AddCha hook, no timer hook.\r\n";
                File.WriteAllText(Path.Combine(root, @"scripts\game_init.lua"), noOpScript, Encoding.ASCII);
                File.WriteAllText(Path.Combine(root, @"core\scripts\game_init.lua"), noOpScript, Encoding.ASCII);
                Log("[LUA_PROTOCOL_ONLY] reset scripts/game_init.lua and core/scripts/game_init.lua to no-op protocol baseline.");
            } catch (Exception ex) { Log("[LUA_PROTOCOL_ONLY_WARN] " + ex.Message); }
            RestoreMapOKPatchedDllIfBackupExists(gpigame);
            Log("[V45_GAME_EXE] experimental game.exe restore disabled; current core\\game.exe is left untouched.");
            if (!Directory.Exists(Path.Combine(root, "resource"))) Log("[WARN] resource directory not found");
            if (!File.Exists(shader)) Log("[WARN] shader not found: " + shader); else Log("[OK] shader exists: " + shader);
            // V20: Do not write or overwrite UI/terrain resources.
            // Previous versions created/kept tiny DDS/TGA placeholders that changed UI style and still failed D3DX loading.
            // Only restore known backups or quarantine obvious placeholders; leave real resources untouched.
            V45ProtocolOnlyResourceSafety();
            string cliffBmp = Path.Combine(root, @"resource\sanguo\model\A_cliff1.bmp");
            string loadingMisc = Path.Combine(root, @"resource\sanguo\ui\loading_misc.dds");
            if (!File.Exists(cliffBmp)) Log("[WARN] missing optional resource: " + cliffBmp); else Log("[OK] resource exists: " + cliffBmp);
            if (!File.Exists(loadingMisc)) Log("[WARN] missing optional resource: " + loadingMisc); else Log("[OK] resource exists: " + loadingMisc);

            Log("[V45_RESOURCE_PRELOAD] full 10002.o referenced-resource mount scan is enabled before game.exe starts. Existing real resources are kept; missing refs are reported; no fake UI placeholders are generated.");
            try { File.WriteAllText(Path.Combine(root, "SL10002_resource_mount_v45.log"), "V45 resource preload scheduled: the launcher will scan deployed map\\10002\\10002.o and mirror only real resource files into data\\resource and data\\core\\resource before game.exe starts.\r\n", Encoding.UTF8); } catch {}
            try { File.WriteAllText(Path.Combine(root, "SL10002_scene_resource_check.txt"), "V45 resource preload scheduled. Detailed map resource check will be written after 10002.map/10002.o are deployed.\r\n", Encoding.UTF8); } catch {}
            File.WriteAllText(Path.Combine(root, "SL10002_v24_logic_notes.txt"),
                "V45 restores the loading-stage map-resource preload before HostService/game launch: scan 10002.o, mirror real resources, report missing refs, then start the protocol clock/delay test. ModRuntime autoload remains disabled. No authentication removal, no VIP/sponsor fields, no AddCha overlay.\r\n", Encoding.UTF8);
            Log("[REPORT_BASED] gpigame.dll LoadMap/LuaServer/AddCha path => fix resource search paths + table/timer/session chain, not HTTP AddCha.");
            Log("[REPORT_BASED] map.o is g_map_opt/g_map_display helper/cache; deploying root + core copies.");

            if (File.Exists(originalMapObj))
            {
                CopyStrict(originalMapObj, Path.Combine(root, "map.o"));
                CopyStrict(originalMapObj, Path.Combine(root, @"core\map.o"));
            }
            else Log("[WARN] original generated map.o not packaged: " + originalMapObj);
            if (File.Exists(originalEdt2Obj))
            {
                CopyStrict(originalEdt2Obj, Path.Combine(root, "edt2.o"));
                CopyStrict(originalEdt2Obj, Path.Combine(root, @"core\edt2.o"));
            }
            else Log("[WARN] original generated edt2.o not packaged: " + originalEdt2Obj);

            CopyStrict(mapSrc, Path.Combine(root, @"map\10002\10002.map"));
            CopyStrict(objSrc, Path.Combine(root, @"map\10002\10002.o"));
            CopyStrict(mapSrc, Path.Combine(root, @"core\map\10002\10002.map"));
            CopyStrict(objSrc, Path.Combine(root, @"core\map\10002\10002.o"));

            string deployedObj = Path.Combine(root, @"map\10002\10002.o");
            Log("[V45_RESOURCE_PRELOAD_BEGIN] scanning deployed 10002.o before HostService/game launch: " + deployedObj);
            MountReferencedMapResources(deployedObj);
            WriteMapResourceReport(deployedObj);
            Log("[V45_RESOURCE_PRELOAD_END] map resource preload/check completed before HostService/game launch.");

            if (IsHostMode)
            {
                StartUdpTrace();
                StartTcpProto();
                Thread.Sleep(300);
            }
            else
            {
                Log("[LAN_CLIENT] local TCP/UDP service skipped; remote host must already be running.");
            }

            byte[] block = BuildPlatformBlock();
            string customMapName = "SL10002_LANV24_10002_" + Process.GetCurrentProcess().Id.ToString();

            using (var mmfDefault = CreateAndWriteMap("10002", block))
            using (var mmfCustom = CreateAndWriteMap(customMapName, block))
            {
                string args = "/mapfile=10002 MemoryMapName=" + customMapName;
                Log("[MODE] LAN V24 CORE: /mapfile=10002 + MemoryMapName + HostIP=" + HostIpText + " + Mode=" + LaunchMode + ". No sanguo hybrid mode.");
                Log("cwd=" + root);
                Log("cmd=" + game + " " + args);
                ProcessStartInfo psi = new ProcessStartInfo();
                psi.FileName = game;
                psi.WorkingDirectory = root;
                psi.Arguments = args;
                psi.UseShellExecute = false;
                Process p = Process.Start(psi);
                Log("[OK] PID=" + p.Id.ToString());
                Log("Memory maps stay alive until game.exe exits. In Host/Single mode local HostService also stays alive.");
                p.WaitForExit();
                StopFlag = true;
                Log("[END] game.exe exited. ExitCode=" + p.ExitCode.ToString());
                Log("[INFO] Packet dir: " + PacketDir);
                return p.ExitCode;
            }
        }
    }
}
'@
try {
    Add-Type -TypeDefinition $Source -Language CSharp
    [SL10002FinalLauncher.Launcher]::Run($Root, $Mode, $HostIP, $PlayerName, [int]$PlayerSlot, $ProtocolVariant) | Out-Null
}
catch {
    Write-Host "[ERROR] Launcher failed. Details: SL10002_lan_v45_launcher.log"
    try {
        Add-Content -LiteralPath (Join-Path $Root "SL10002_lan_v45_launcher.log") -Encoding UTF8 -Value ("[ERROR] " + $_.Exception.Message)
        Add-Content -LiteralPath (Join-Path $Root "SL10002_lan_v45_launcher.log") -Encoding UTF8 -Value $_.ScriptStackTrace
    } catch {}
    exit 1
}
