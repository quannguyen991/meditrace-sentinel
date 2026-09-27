# Boc `chay-the-he-7.ps1` de LUU LOG - cung cach voi chay-the-he-6-voi-log.ps1.
#
# CHI DUNG ASCII trong tep nay - PowerShell 5.1 doc UTF-8 khong BOM theo ANSI.
#
# Dung `*>` chu khong dung `| Tee-Object`: PowerShell dem dau ra cua mot lenh
# goi script truoc khi day xuong duong ong, nen log chi xuat hien khi moi thu da
# xong. Chuyen huong `*>` ghi theo dong.
$goc = "D:\meditrace-sentinel"
$log = "$goc\logs\the-he-7-$(Get-Date -Format 'MMdd-HHmm').log"
New-Item -ItemType Directory -Force "$goc\logs" | Out-Null
& "$goc\tools\chay-the-he-7.ps1" *> $log

# TRA GPU cho BDS. Truoc khi phong chuoi, task 'Ollama Serve' duoc TAT TAY (15/09/2026,
# nguoi dung dong y dung tam) - `ollama-guard.ps1` co y khong tu bat lai task bi tat. Bat
# lai o day, du chuoi xong hay hong, de BDS khong nam im cho toi khi co nguoi nho ra.
"######## tra GPU: bat lai Ollama Serve - $(Get-Date -Format 'MM-dd HH:mm:ss')" | Out-File -Append -Encoding ascii $log
# Trong luc chuoi chay, cong 127.0.0.1:11434 cua may nay la DUONG HAM SSH nguoc tu laptop
# (Ollama chi co bge-m3 de BDS co vector). Phai cat duong ham truoc: con giu cong thi
# 'Ollama Serve' khong mo duoc cong, va guard van thay "/api/tags co model" nen bao khoe.
Get-NetTCPConnection -LocalPort 11434 -State Listen -EA SilentlyContinue |
    ForEach-Object { Get-Process -Id $_.OwningProcess -EA SilentlyContinue } |
    Where-Object { $_.ProcessName -eq 'sshd' } |
    Stop-Process -Force -EA SilentlyContinue
Start-Sleep 3
Enable-ScheduledTask -TaskName 'Ollama Serve' | Out-Null
Start-ScheduledTask -TaskName 'Ollama Serve'
