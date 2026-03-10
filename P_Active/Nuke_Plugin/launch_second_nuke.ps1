$exePath = 'C:\Program Files\Nuke13.2v5\Nuke13.2.exe'
$out = 'Z:\P_Active\Nuke_Plugin\launch_second_nuke_status.txt'

function Get-GuiRows {
    @(Get-CimInstance Win32_Process |
        Where-Object Name -EQ 'Nuke13.2.exe' |
        Where-Object CommandLine -Match '--nukex' |
        Select-Object ProcessId, ParentProcessId, CommandLine)
}

$before = @(Get-GuiRows)
$beforeIds = @($before | ForEach-Object { $_.ProcessId })

$p = Start-Process -FilePath $exePath -ArgumentList '--nukex' -PassThru
Start-Sleep -Seconds 8

$after = @(Get-GuiRows)
$newRows = @($after | Where-Object { $beforeIds -notcontains $_.ProcessId })
$launchedStillAlive = Get-Process -Id $p.Id -ErrorAction SilentlyContinue

$result = @(
    "started_pid=$($p.Id)"
    "started_pid_alive=$([bool]$launchedStillAlive)"
    "before_gui_count=$($before.Count)"
    "after_gui_count=$($after.Count)"
    "new_gui_count=$($newRows.Count)"
)

foreach ($row in $after) {
    $result += "gui_pid=$($row.ProcessId)"
}

$result | Out-File -FilePath $out -Encoding utf8
Write-Host "Wrote $out"
