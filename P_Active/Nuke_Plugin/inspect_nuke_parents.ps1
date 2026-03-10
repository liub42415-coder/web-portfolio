$out = 'Z:\P_Active\Nuke_Plugin\nuke_process_tree.txt'

$procs = Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'Nuke13.2.exe' }
$rows = foreach ($p in $procs) {
    $live = Get-Process -Id $p.ProcessId -ErrorAction SilentlyContinue
    [PSCustomObject]@{
        ProcessId = $p.ProcessId
        ParentProcessId = $p.ParentProcessId
        Responding = if ($live) { $live.Responding } else { $null }
        MainWindowTitle = if ($live) { $live.MainWindowTitle } else { '' }
        CommandLine = $p.CommandLine
    }
}

$rows | Sort-Object ProcessId | Format-List | Out-File -FilePath $out -Encoding utf8
Write-Host "Wrote $out"
