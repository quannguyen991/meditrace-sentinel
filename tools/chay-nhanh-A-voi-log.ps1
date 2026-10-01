# Boc `chay-nhanh-A.ps1` de LUU LOG - cung cach voi cac chuoi khac.
#
# CHI DUNG ASCII trong tep nay - PowerShell 5.1 doc UTF-8 khong BOM theo ANSI.
$goc = "D:\meditrace-core"
$log = "$goc\logs\nhanh-A-$(Get-Date -Format 'MMdd-HHmm').log"
New-Item -ItemType Directory -Force "$goc\logs" | Out-Null
& "$goc\tools\chay-nhanh-A.ps1" *> $log
