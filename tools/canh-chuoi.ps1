# Canh chuoi thi nghiem: chay lai neu may vua khoi dong lai giua chung.
#
# CHI DUNG ASCII trong tep nay - PowerShell 5.1 doc UTF-8 khong BOM theo ANSI.
#
# VI SAO CO (16/09/2026). HoaiDuc tat dot ngot HAI lan trong mot dem khi dang train
# khau trich the he 7: 15/09 20:55 (Kernel-Power 41, bugcheck 0 - mat dien hoac treo)
# va 16/09 03:20. Ca hai lan may tu khoi dong lai nhung KHONG co gi chay lai chuoi,
# nen GPU nam khong 2 gio 38 phut va 3 gio 42 phut. Checkpoint 50 buoc mot lan nen
# moi lan sap chi mat toi da ~2 gio train, nhung thoi gian NAM KHONG moi la phan lon.
#
# Tep nay chay moi 10 phut. No CHI phong lai chuoi khi ca ba dieu cung dung:
#   1. task MEDITRACE_THE_HE_7 khong o trang thai Running
#   2. co tep MOC (`data/the-he-6-luu/.da-cat`) - tuc chuoi da tung chay, chua xong
#   3. chua co du ket qua cuoi cung (thieu tep ra_A_* cua buoc 4)
# Dieu 3 la cai chan "chay lai vo han sau khi chuoi da xong".
#
# KHONG tu bat lai Ollama Serve, va khong dung duong ham cua laptop: hai viec do co
# chu cua no (`chay-the-he-7-voi-log.ps1` va `duong-ham-bds.ps1`).

$goc = "D:\meditrace-sentinel"
$log = "$goc\logs\canh-chuoi.log"
$task = "MEDITRACE_THE_HE_7"

function Ghi($m) {
    Add-Content -Path $log -Value ((Get-Date).ToString('MM-dd HH:mm:ss') + "  " + $m) -Encoding ASCII
}

if ((Get-ScheduledTask -TaskName $task -EA SilentlyContinue).State -eq 'Running') { exit 0 }
if (-not (Test-Path "$goc\data\the-he-6-luu\.da-cat")) {
    Ghi "chua co moc - chuoi chua tung chay, khong tu phong"
    exit 0
}
# Buoc 4 sinh ra ra_A_<tap>.jsonl cho 5 tap. Du 5 tep la chuoi da xong.
$xong = @(Get-ChildItem "$goc\data\ra_A_*phat_trien.jsonl" -EA SilentlyContinue).Count
if ($xong -ge 5) {
    Ghi "da co $xong tep ket qua nhanh A - chuoi xong, khong phong lai"
    exit 0
}

$boot = (Get-CimInstance Win32_OperatingSystem).LastBootUpTime
Ghi "task khong chay, moi co, ket qua moi $xong/5 - phong lai. May khoi dong luc $boot"
Start-ScheduledTask -TaskName $task
Start-Sleep 30
Ghi ("trang thai sau khi phong: " + (Get-ScheduledTask -TaskName $task).State)
