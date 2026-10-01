# Boc `chay-the-he-8.ps1` de LUU LOG, va tra GPU cho BDS khi xong.
#
# CHI DUNG ASCII trong tep nay - PowerShell 5.1 doc UTF-8 khong BOM theo ANSI.
$goc = "D:\meditrace-core"
$log = "$goc\logs\the-he-8-$(Get-Date -Format 'MMdd-HHmm').log"
New-Item -ItemType Directory -Force "$goc\logs" | Out-Null
& "$goc\tools\chay-the-he-8.ps1" *> $log

# Tra GPU cho BDS: cat duong ham tu laptop (dang giu cong 11434) roi bat lai Ollama Serve.
"######## tra GPU: bat lai Ollama Serve - $(Get-Date -Format 'MM-dd HH:mm:ss')" | Out-File -Append -Encoding ascii $log
Get-NetTCPConnection -LocalPort 11434 -State Listen -EA SilentlyContinue |
    ForEach-Object { Get-Process -Id $_.OwningProcess -EA SilentlyContinue } |
    Where-Object { $_.ProcessName -eq 'sshd' } |
    Stop-Process -Force -EA SilentlyContinue
Start-Sleep 3
Enable-ScheduledTask -TaskName 'Ollama Serve' | Out-Null
Start-ScheduledTask -TaskName 'Ollama Serve'
