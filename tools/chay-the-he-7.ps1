# Chuoi THE HE 7 tren HoaiDuc.
#
# CHI DUNG ASCII trong tep nay - PowerShell 5.1 doc UTF-8 khong BOM theo ANSI.
#
# BO THE HE 7 KHAC BO THE HE 6 O CHO: dap an CHI ghi dich danh nguoi nha dang ke
# ("bo", "ba ngoai") khi loi thoai noi ro "X la bo cua chau"; con lai ghi "nguoi
# nha". Do 15/09/2026 tren train the he 6: 1.323/1.829 menh de dich danh mang mot
# ten KHONG co trong hoi thoai - ca nhanh A lan khau trich deu bi day doan thong tin
# khong ai noi. The he 7: 0/1.311. Commit f9fcd56.
#
# Chuoi y het the he 6 (xem chay-the-he-6.ps1 cho ly do tung buoc), tru ba cho:
#   0a. KIEM VAN TAY truoc khi dung vao gi - quen dong bo la train 1,5 ngay tren bo cu
#   0b. CAT HAN tep dem trich + ket qua the he 6, KHONG loc theo id: the he 7 trung id
#       va trung so ca voi the he 6 o ca bon bo thach thuc, `don-dem-trich.py` khong
#       phan biet duoc (no tu ghi gioi han nay)
#   3.  adapter A mang hau to -viet7, adapter trich the he 6 giu duoi ten rieng
#
# BO GPT-500 van ngoai chuoi, nhu the he 6.
#
# GPU: chuoi chiem gan het 12 GB. Ollama cua BDS (task 'Ollama Serve') KHONG chay
# song song duoc - lan train 12/09 da lam no chet va canh gac bao cho chu may. Chi
# phong chuoi nay khi da thong nhat cach nhuong GPU.

$py = "D:\meditrace-venv\Scripts\python.exe"
$goc = "D:\meditrace-sentinel"
$mo_hinh = "D:/hf-models/Qwen3-4B"
$do_dai_trich = 3072
Set-Location $goc

function Chay-Lai {
    # Moc buoc di bang Write-Host - xem chay-the-he-6.ps1.
    param([string]$Ten, [string[]]$Doi, [int]$LanToiDa = 3)
    for ($i = 1; $i -le $LanToiDa; $i++) {
        Write-Host ""
        Write-Host ("######## $Ten - lan $i - " + (Get-Date -Format 'MM-dd HH:mm:ss'))
        & $py @Doi
        if ($LASTEXITCODE -eq 0) {
            Write-Host ("######## $Ten XONG - " + (Get-Date -Format 'MM-dd HH:mm:ss'))
            return $true
        }
        Write-Host "######## $Ten HONG (ma $LASTEXITCODE)"
        Start-Sleep 30
    }
    Write-Host "######## $Ten BO CUOC sau $LanToiDa lan"
    return $false
}

$cac_tap = @("viet_phat_trien",
             "thach_thuc_doi_chu_the_phat_trien",
             "thach_thuc_phuong_ngu_phat_trien",
             "thach_thuc_dinh_chinh_phat_trien",
             "thach_thuc_nhieu_asr_phat_trien")

# 0a. Du lieu tren may PHAI la the he 7.
Write-Host "######## 0a-KIEM-THE-HE"
& $py "$goc\tools\kiem-the-he.py" "7" "viet_train" @cac_tap
if ($LASTEXITCODE -ne 0) {
    Write-Host "######## DUNG: du lieu tren may khong phai the he 7 - dong bo lai roi chay lai"
    exit 1
}

# 0b. Cat tep dem va ket qua the he 6 MOT lan. Co moc thi bo qua - chay lai giua
#     chung khong duoc cat mat tep dem the he 7 dang tinh do.
$kho = "$goc\data\the-he-6-luu"
if (-not (Test-Path "$kho\.da-cat")) {
    New-Item -ItemType Directory -Force $kho | Out-Null
    foreach ($tap in $cac_tap) {
        Get-ChildItem "$goc\data\trich_${tap}_*.jsonl*" -EA SilentlyContinue |
            Move-Item -Destination $kho
    }
    Get-ChildItem "$goc\data\ra_*_phat_trien.jsonl" -EA SilentlyContinue |
        Move-Item -Destination $kho
    New-Item -ItemType File "$kho\.da-cat" | Out-Null
    Write-Host "######## da cat tep dem + ket qua the he 6 -> $kho"
}
$cu = "$goc\models\nen-qwen3-4b-trich"
$luu = "$goc\models\nen-qwen3-4b-trich-the-he-6"
if ((Test-Path $cu) -and -not (Test-Path $luu)) {
    Move-Item $cu $luu
    Write-Host "######## da giu adapter trich the he 6 -> $luu"
}

# 1. Huan luyen khau trich tren the he 7.
Chay-Lai "1-TRAIN-TRICH-TH7" @(
    "-m", "src.train_baseline", "--model", $mo_hinh,
    "--nhiem-vu", "trich", "--buoc", "400", "--do-dai", "$do_dai_trich") | Out-Null

# 2. Trich + nhanh B, C tren tap phat trien va bon bo thach thuc.
$adapter = "models/nen-qwen3-4b-trich/best_checkpoint"
Chay-Lai "2a-TRICH-DEV" @(
    "-m", "src.nhanh", "--nhanh", "B", "C", "C_khoa", "C_khoa_hoi", "--model", $mo_hinh,
    "--tap", "viet_phat_trien", "--max-token", "3072", "--n", "60",
    "--adapter-trich", $adapter) | Out-Null
foreach ($t in $cac_tap[1..4]) {
    Chay-Lai "2b-TRICH-$t" @(
        "-m", "src.nhanh", "--nhanh", "B", "C", "C_khoa", "C_khoa_hoi", "--model", $mo_hinh,
        "--tap", $t, "--max-token", "3072", "--adapter-trich", $adapter) | Out-Null
}

# 3. Huan luyen nhanh A tren bo tu sinh the he 7.
Chay-Lai "3-TRAIN-A-TH7" @(
    "-m", "src.train_baseline", "--model", $mo_hinh,
    "--nhiem-vu", "benh_an", "--buoc", "400", "--do-dai", "2048",
    "--tep-train", "viet_train.jsonl", "--tep-val", "viet_phat_trien.jsonl",
    "--hau-to=-viet7") | Out-Null   # LIEN mot token - xem chay-nhanh-A.ps1

# 4. Chay A tren cung cac tap.
$adapter_a = "models/nen-qwen3-4b-viet7/best_checkpoint"
Chay-Lai "4a-A-DEV" @(
    "-m", "src.nhanh", "--nhanh", "A", "--model", $mo_hinh,
    "--adapter", $adapter_a, "--tap", "viet_phat_trien", "--n", "60") | Out-Null
foreach ($t in $cac_tap[1..4]) {
    Chay-Lai "4b-A-$t" @(
        "-m", "src.nhanh", "--nhanh", "A", "--model", $mo_hinh,
        "--adapter", $adapter_a, "--tap", $t) | Out-Null
}

Write-Host ""
Write-Host ("######## HET - " + (Get-Date -Format 'MM-dd HH:mm:ss'))
Get-ChildItem "$goc\data\ra_*phat_trien.jsonl" -EA SilentlyContinue |
    Sort-Object LastWriteTime | Select-Object -Last 12 |
    ForEach-Object { "{0,-56} {1}" -f $_.Name, $_.LastWriteTime }
