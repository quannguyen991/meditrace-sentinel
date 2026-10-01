# Boc `chay-the-he-6.ps1` de LUU LOG - cung cach voi chay-bo-5000-voi-log.ps1.
#
# CHI DUNG ASCII trong tep nay - PowerShell 5.1 doc UTF-8 khong BOM theo ANSI.
#
# Dung `*>` chu khong dung `| Tee-Object`: PowerShell dem dau ra cua mot lenh
# goi script truoc khi day xuong duong ong, nen log chi xuat hien khi moi thu da
# xong. Chuyen huong `*>` ghi theo dong.
$goc = "D:\meditrace-core"
$log = "$goc\logs\the-he-6-$(Get-Date -Format 'MMdd-HHmm').log"
New-Item -ItemType Directory -Force "$goc\logs" | Out-Null
& "$goc\tools\chay-the-he-6.ps1" *> $log
