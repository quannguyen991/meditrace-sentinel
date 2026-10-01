# Dung lai toan bo ket qua tren DU LIEU CUA MINH, sau khi cat het tai san
# cua cuoc thi cu.
#
# CHI DUNG ASCII trong tep nay - PowerShell 5.1 doc UTF-8 khong BOM theo ANSI.
#
# Bon buoc, xep theo do quan trong GIAM dan de hong buoc sau van con buoc truoc:
#
#   1. Train nhanh A tren benh an tu sinh      (~3 gio)  - moc so sanh
#   2. Chay tam nhanh tren tap phat trien      (~2 gio)  - bang chinh
#   3. Train khau trich tren dap an cau truc   (~7 gio)  - thi nghiem chuyen giao
#   4. Chay lai cac nhanh voi adapter trich    (~2 gio)
#
# Buoc 1 va 2 du de co bang ket qua day du. Buoc 3 va 4 la phan mo rong.
# Moi buoc thu lai toi 3 lan; buoc train chay tiep tu checkpoint, buoc trich
# chay tiep tu tep dem.

$py = "D:\meditrace-venv\Scripts\python.exe"
$goc = "D:\meditrace-core"
$mo_hinh = "D:/hf-models/Qwen3-4B"
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

# 1. Train nhanh A. 500 buoc x grad_accum 16 = 8.000 mau tren 2.231 ca
#    = khoang 3,6 epoch. Train ky hon lan truoc (200 buoc).
Chay-Lai "1-TRAIN-A" @(
    "-m", "src.train_baseline", "--model", $mo_hinh,
    "--nhiem-vu", "benh_an", "--buoc", "500", "--do-dai", "1024") | Out-Null

# 2. Tam nhanh tren tap phat trien, mot lan trich dung chung.
Chay-Lai "2-CAC-NHANH" @(
    "-m", "src.nhanh", "--nhanh", "B", "C_khong_luat", "C_khong_lien_ket",
    "C", "C_ghi_de", "D", "--model", $mo_hinh, "--tap", "viet_phat_trien",
    "--max-token", "3072", "--n", "60") | Out-Null

Chay-Lai "2b-NHANH-A" @(
    "-m", "src.nhanh", "--nhanh", "A", "--model", $mo_hinh,
    "--adapter", "models/nen-qwen3-4b/best_checkpoint",
    "--tap", "viet_phat_trien", "--n", "60") | Out-Null

Chay-Lai "2c-NHANH-A-NEN" @(
    "-m", "src.nhanh", "--nhanh", "A", "--model", $mo_hinh,
    "--tap", "viet_phat_trien", "--n", "60") | Out-Null

# 3. Train khau trich. 2048 token nen cham hon nhieu; 300 buoc = ~2,2 epoch.
Chay-Lai "3-TRAIN-TRICH" @(
    "-m", "src.train_baseline", "--model", $mo_hinh,
    "--nhiem-vu", "trich", "--buoc", "300", "--do-dai", "2048") | Out-Null

# 4. Chay lai cac nhanh voi adapter trich.
Chay-Lai "4-NHANH-CO-ADAPTER" @(
    "-m", "src.nhanh", "--nhanh", "B", "C", "D", "--model", $mo_hinh,
    "--tap", "viet_phat_trien", "--max-token", "3072", "--n", "60",
    "--adapter-trich", "models/nen-qwen3-4b-trich/best_checkpoint") | Out-Null

Write-Output ""
Write-Output ("######## HET - " + (Get-Date -Format 'MM-dd HH:mm:ss'))
Get-ChildItem "$goc\data\ra_*_viet_phat_trien.jsonl" -EA SilentlyContinue |
    ForEach-Object { "{0,-44} {1} dong" -f $_.Name, (Get-Content $_.FullName).Count }
