# Chay lai toan bo tren BO 5.000 CA (60 khuon, 5 boi canh).
#
# CHI DUNG ASCII trong tep nay - PowerShell 5.1 doc UTF-8 khong BOM theo ANSI.
#
# VI SAO CO CHUOI NAY. Bo 3.000 ca cu chi co 32 mach thong tin va mot boi canh;
# `eval_loss` dung o 3x10^-4 ke ca sau khi da them nhan quan he. Do la dau hieu
# du lieu qua deu chu khong phai mo hinh hieu tot. Bo 5.000 co 118 mach va 5
# boi canh; chuoi nay do xem con so do co doi khong.
#
# CAU HOI CHUOI NAY TRA LOI:
#   1. `eval_loss` tren khuon chua thay co ra khoi muc 10^-4 khong
#   2. Adapter trich co phat hien duoc quan he khong (do bang do_quan_he)
#   3. C co hon B khong, tren bo du lieu da het deu
#   4. Huan luyen dong gop bao nhieu (A so voi A nen) - LAN NAY KHONG MAT COT,
#      vi ten tep da kem hau to `_nen`
#
# Bon buoc, xep theo do quan trong GIAM dan.
#
# CACH PHONG - PHAI DUNG TASK SCHEDULER, khong chay thang qua ssh:
#
#     schtasks /create /tn MEDITRACE_BO5000 /tr "powershell.exe -NoProfile
#         -ExecutionPolicy Bypass -File <goc>/tools/chay-bo-5000.ps1"
#         /sc once /st 23:59 /f
#     schtasks /run /tn MEDITRACE_BO5000
#
# (<goc> la D: cheo meditrace-sentinel. Viet bang gach cheo xuoi o day co chu dinh:
#  duong dan Windows trong chu thich da bi mot doan ma sinh tep nuot mat dau
#  gach nguoc: `\t` cua `\tools\` thanh mot ky tu tab. Lan thu tu trong du an.)
#
# VI SAO. Windows OpenSSH giet CA CAY tien trinh khi phien ssh dong. Chay thang
# `ssh ... powershell -File ...` thi chuoi chet ngay khi may goi lenh sap hoac
# mat mang - da mat mot lan nhu the.
#
# `Start-Process -WindowStyle Hidden` KHONG cuu duoc: tien trinh con van thuoc
# job object cua phien ssh, chet cung, va log ra 0 byte nen khong co dau vet gi
# de doan. Task Scheduler thi thuoc ve he dieu hanh, khong thuoc phien ssh.

$py = "D:\meditrace-venv\Scripts\python.exe"
$goc = "D:\meditrace-sentinel"
$mo_hinh = "D:/hf-models/Qwen3-4B"
$tap = "viet_phat_trien"
Set-Location $goc

function Chay-Lai {
    param([string]$Ten, [string[]]$Doi, [int]$LanToiDa = 3)
    for ($i = 1; $i -le $LanToiDa; $i++) {
        Write-Output ""
        Write-Output ("######## $Ten - lan $i - " + (Get-Date -Format 'MM-dd HH:mm:ss'))
        & $py @Doi
        if ($LASTEXITCODE -eq 0) {
            Write-Output ("######## $Ten XONG - " + (Get-Date -Format 'HH:mm:ss'))
            return $true
        }
        Write-Output "######## $Ten HONG (ma $LASTEXITCODE)"
        Start-Sleep 30
    }
    Write-Output "######## $Ten BO CUOC sau $LanToiDa lan"
    return $false
}

# 1. Huan luyen lai khau trich tren bo 5.000.
#    3.773 ca train. 400 buoc x tich luy 16 = 6.400 mau = khoang 1,7 vong.
#    Day la buoc tra loi cau hoi 1 va 2.
Chay-Lai "1-TRAIN-TRICH-5000" @(
    "-m", "src.train_baseline", "--model", $mo_hinh,
    "--nhiem-vu", "trich", "--buoc", "400", "--do-dai", "2048") | Out-Null

# 2. Chay cac nhanh trung gian voi adapter trich moi.
#    Them ba nhanh quan he - chung chi co nghia khi adapter da biet danh dau
#    quan he, nen phai chay SAU buoc 1.
Chay-Lai "2-CAC-NHANH" @(
    "-m", "src.nhanh", "--nhanh", "B", "C_khong_luat", "C_khong_lien_ket",
    "C", "C_ghi_de", "D", "C_quan_he_luat", "C_quan_he", "D_quan_he",
    "--model", $mo_hinh, "--tap", $tap, "--max-token", "3072", "--n", "60",
    "--adapter-trich", "models/nen-qwen3-4b-trich/best_checkpoint") | Out-Null

# 3. Do chat luong phat hien quan he. Khong can GPU, chay nhanh.
Chay-Lai "3-DO-QUAN-HE" @(
    "-m", "src.do_quan_he", "--tap", $tap, "--adapter-trich") | Out-Null

# 4. Hai moc sinh thang. CHAY A NEN TRUOC:
#    neu buoc sau hong thi van con cot doi chung cong bang nhat.
#    Ten tep nay da kem hau to `_nen` nen KHONG de len nhau nua
#    (xem nhanh.ten_ket_qua).
Chay-Lai "4a-NHANH-A-NEN" @(
    "-m", "src.nhanh", "--nhanh", "A", "--model", $mo_hinh,
    "--tap", $tap, "--n", "60") | Out-Null

Chay-Lai "4b-NHANH-A" @(
    "-m", "src.nhanh", "--nhanh", "A", "--model", $mo_hinh,
    "--adapter", "models/nen-qwen3-4b/best_checkpoint",
    "--tap", $tap, "--n", "60") | Out-Null

Write-Output ""
Write-Output ("######## HET - " + (Get-Date -Format 'MM-dd HH:mm:ss'))
Get-ChildItem "$goc\data\ra_*_$tap.jsonl" -EA SilentlyContinue |
    ForEach-Object { "{0,-46} {1} dong" -f $_.Name, (Get-Content $_.FullName).Count }
