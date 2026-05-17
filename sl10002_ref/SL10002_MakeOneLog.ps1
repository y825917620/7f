param(
    [string]$VersionTag = 'V45'
)
$ErrorActionPreference = 'SilentlyContinue'
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$tag = if ([string]::IsNullOrWhiteSpace($VersionTag)) { 'V45' } else { $VersionTag }
$tagLower = $tag.ToLowerInvariant()
$Out = Join-Path $Root 'SL10002_ONE_LOG.txt'
function Add-Line([string]$s='') { Add-Content -LiteralPath $Out -Encoding UTF8 -Value $s }
function Add-FileBlock {
    param([string]$Title, [string[]]$Paths, [int]$Tail = 260)
    Add-Line ""
    Add-Line "==================== $Title ===================="
    $found = $false
    foreach ($rel in $Paths) {
        $p = Join-Path $Root $rel
        if (Test-Path -LiteralPath $p -PathType Leaf) {
            $found = $true
            $it = Get-Item -LiteralPath $p
            Add-Line ("--- FILE: {0} | size={1} | modified={2} ---" -f $rel, $it.Length, $it.LastWriteTime.ToString('yyyy-MM-dd HH:mm:ss'))
            try { Get-Content -LiteralPath $p -Encoding UTF8 -Tail $Tail | ForEach-Object { Add-Line $_ } }
            catch { try { Get-Content -LiteralPath $p -Tail $Tail | ForEach-Object { Add-Line $_ } } catch { Add-Line ("[READ_ERROR] " + $_.Exception.Message) } }
        }
    }
    if (-not $found) { Add-Line '[MISSING] no matching file found' }
}
try { Remove-Item -LiteralPath $Out -Force -ErrorAction SilentlyContinue } catch {}
Add-Line ("SL10002 ONE LOG {0} generated={1}" -f $tag, (Get-Date).ToString('yyyy-MM-dd HH:mm:ss'))
Add-Line ("Root=" + $Root)
Add-Line ("Computer=" + $env:COMPUTERNAME)
Add-Line ("User=" + $env:USERNAME)
Add-Line ("OS=" + [System.Environment]::OSVersion.VersionString)
Add-Line ""
Add-Line "Send only this file next time: SL10002_ONE_LOG.txt"
Add-FileBlock -Title 'LAUNCHER_MAIN' -Paths @("SL10002_lan_${tagLower}_launcher.log") -Tail 520
Add-FileBlock -Title 'CONSOLE_CAPTURE' -Paths @("SL10002_launcher_console_${tagLower}.log") -Tail 260
Add-FileBlock -Title 'CONFIG' -Paths @("SL10002_config_${tagLower}_summary.txt", "SL10002_protocol_${tagLower}_status.txt", "config.lua", "core\config.lua") -Tail 220
Add-FileBlock -Title 'RESOURCE_PRELOAD' -Paths @("SL10002_resource_alias_${tagLower}.log", "SL10002_resource_mount_${tagLower}.log", "SL10002_scene_resource_check.txt") -Tail 260
Add-FileBlock -Title 'LUA_CHAIN_TRACE' -Paths @("SL10002_map_protocol_${tagLower}.log", "SL10002_lua_trace_${tagLower}.log", "AddCha.log") -Tail 420
Add-FileBlock -Title 'INIT_LOG' -Paths @('init.log') -Tail 220
Add-FileBlock -Title 'NET_STATE' -Paths @('net_state.log') -Tail 220
Add-FileBlock -Title 'ERROR_LOG' -Paths @('error.log','log_err.log') -Tail 220
Add-FileBlock -Title 'PROTOCOL_TRACE' -Paths @("SL10002_protocol_clock_${tagLower}.log", "SL10002_loadready_${tagLower}_trace.txt", "SL10002_0259_${tagLower}_trace.txt", "SL10002_0263_${tagLower}_trace.txt", "SL10002_026A_${tagLower}_trace.txt", "SL10002_0272_${tagLower}_trace.txt") -Tail 360
Add-FileBlock -Title 'PACKETS_INDEX_LAST' -Paths @("SL10002_lan_${tagLower}_packets\packets_index.tsv") -Tail 360
Add-FileBlock -Title 'LOG_MGR' -Paths @('log_mgr') -Tail 160
Add-Line ""
Add-Line "==================== END ONE LOG ===================="
