# Boc `chay-bo-5000.ps1` de LUU LOG.
#
# CHI DUNG ASCII trong tep nay - PowerShell 5.1 doc UTF-8 khong BOM theo ANSI.
#
# VI SAO CAN BOC. Tac vu goc chay script truc tiep, nen dau ra di vao stdout cua
# Task Scheduler va bi bo. Suot dem 10-11/09/2026 tep logs/bo5000.log la 0 byte,
# nen khi chuoi chet luc 03:22 vi Windows Update khoi dong lai may thi khong co
# mot dong nao de doan - phai lan theo LastTaskResult, so ban ghi trong tep
# trich, va nhat ky su kien Windows.
#
# DUNG `*>` CHU KHONG DUNG `| Tee-Object`. Ban dau toi viet
#
#     & $script *>&1 | Tee-Object -FilePath $log
#
# va tep log KHONG duoc tao ra trong suot luc chay: PowerShell dem dau ra cua
# mot lenh goi script truoc khi day xuong duong ong, nen log chi xuat hien khi
# moi thu da xong - dung luc khong con can no nua. Chuyen huong `*>` ghi theo
# dong.
$goc = "D:\meditrace-sentinel"
$log = "$goc\logs\bo5000-$(Get-Date -Format 'MMdd-HHmm').log"
New-Item -ItemType Directory -Force "$goc\logs" | Out-Null
& "$goc\tools\chay-bo-5000.ps1" *> $log
