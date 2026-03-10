$exe = 'C:\Program Files\Nuke13.2v5\Nuke13.2.exe'
$out = 'Z:\P_Active\Nuke_Plugin\launch_status.txt'

try {
    $p = Start-Process -FilePath $exe -ArgumentList '--nukex' -PassThru
    Start-Sleep -Seconds 10

    $alive = Get-Process -Id $p.Id -ErrorAction SilentlyContinue
    if ($alive) {
        @(
            'status=running'
            "pid=$($p.Id)"
            "name=$($alive.ProcessName)"
        ) | Out-File -Encoding utf8 $out
    }
    else {
        @(
            'status=exited'
            "pid=$($p.Id)"
        ) | Out-File -Encoding utf8 $out
    }
}
catch {
    @(
        'status=error'
        "message=$($_.Exception.Message)"
    ) | Out-File -Encoding utf8 $out
}
