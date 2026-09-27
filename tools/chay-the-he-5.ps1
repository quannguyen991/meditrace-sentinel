# Chuoi THE HE 5 tren HoaiDuc.
#
# CHI DUNG ASCII trong tep nay - PowerShell 5.1 doc UTF-8 khong BOM theo ANSI.
#
# BO THE HE 5 KHAC BO THE HE 4 O CHO: moi phat bieu trong dap an co trich dan
# nguyen van, loai phat bieu, muc chac chan; co bay hai nguon khac nhau; nhan
# chan doan rao don da sua. Nen khau trich phai huan luyen LAI - adapter the he 4
# chua bao gio thay truong trich dan.
#
# CAU HOI CHUOI NAY TRA LOI:
#   1. Khau trich hoc duoc TRICH DAN nguyen van khong - tang khoa bang chung dua
#      vao dung dieu do
#   2. Tren tap phat trien va ba bo thach thuc (doi chu the, phuong ngu, dinh
#      chinh), khoa + rui ro + hoi lai co giam loi nguy co cao khong - so voi
#      nhanh sinh thang A, CUNG mo hinh nen, CUNG bo du lieu
#   3. Nhanh A duoc huan luyen tren BO TU SINH, khong tren du lieu cuoc thi (ban
#      to chuc khuyen khong dung) - de phep so cong bang
#
# Cac tang moi (khoa, rui ro, hoi lai) la HAU XU LY, chay tren may ca nhan tu tep
# dem trich. Chuoi nay chi lam phan can GPU.
#
# CACH PHONG - PHAI DUNG TASK SCHEDULER (xem chay-bo-5000.ps1 ve vi sao), va
# CHI SAU KHI chuoi the he 4 da xong va tac vu khoi dong lai cua no da tat.

$py = "D:\meditrace-venv\Scripts\python.exe"
$goc = "D:\meditrace-sentinel"
$mo_hinh = "D:/hf-models/Qwen3-4B"
# 3072, KHONG phai 2048. Nhan the he 5 dai hon 34% vi co trich dan nguyen van. Do
# bang chinh tokenizer tren may nay ngay 11/09/2026: o 2048 bi LOAI 3.339/3.759
# mau train (con 420) - huan luyen tren 11% bo du lieu ma khong co gi bao loi
# ngoai mot dong in. O 3072 chi loai 6.
$do_dai_trich = 3072
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

# 0. GIU adapter trich the he 4 duoi ten rieng. Lan huan luyen moi se tu choi
#    chay tiep tren checkpoint cua bo khac (van_tay_du_lieu), va ta muon giu no
#    de doi chieu. Chi di chuyen MOT lan: chay lai chuoi thi bo qua.
$cu = "$goc\models\nen-qwen3-4b-trich"
$luu = "$goc\models\nen-qwen3-4b-trich-the-he-4"
if ((Test-Path $cu) -and -not (Test-Path $luu)) {
    Move-Item $cu $luu
    Write-Output "######## da giu adapter the he 4 -> $luu"
}

# 1. Huan luyen khau trich tren the he 5.
Chay-Lai "1-TRAIN-TRICH-TH5" @(
    "-m", "src.train_baseline", "--model", $mo_hinh,
    "--nhiem-vu", "trich", "--buoc", "400", "--do-dai", "$do_dai_trich") | Out-Null

# 2. Trich + nhanh B, C tren tap phat trien va ba bo thach thuc. Tep dem trich
#    (trich_<tap>_3072_hl.jsonl) la dau vao cua moi tang hau xu ly.
$adapter = "models/nen-qwen3-4b-trich/best_checkpoint"
Chay-Lai "2a-TRICH-DEV" @(
    "-m", "src.nhanh", "--nhanh", "B", "C", "C_khoa", "C_khoa_hoi", "--model", $mo_hinh,
    "--tap", "viet_phat_trien", "--max-token", "3072", "--n", "60",
    "--adapter-trich", $adapter) | Out-Null
foreach ($t in @("thach_thuc_doi_chu_the_phat_trien",
                 "thach_thuc_phuong_ngu_phat_trien",
                 "thach_thuc_dinh_chinh_phat_trien")) {
    Chay-Lai "2b-TRICH-$t" @(
        "-m", "src.nhanh", "--nhanh", "B", "C", "C_khoa", "C_khoa_hoi", "--model", $mo_hinh,
        "--tap", $t, "--max-token", "3072", "--adapter-trich", $adapter) | Out-Null
}

# 3. Huan luyen nhanh A tren BO TU SINH: dau vao la hoi thoai, dau ra la ban
#    tham chieu (truong output cua viet_train.jsonl). 2048 du cho A: do bang
#    tokenizer ngay 11/09/2026, khong loai mau nao (3.759/3.759 train).
Chay-Lai "3-TRAIN-A-TH5" @(
    "-m", "src.train_baseline", "--model", $mo_hinh,
    "--nhiem-vu", "benh_an", "--buoc", "400", "--do-dai", "2048",
    "--tep-train", "viet_train.jsonl", "--tep-val", "viet_phat_trien.jsonl",
    "--hau-to", "-viet5") | Out-Null

# 4. Chay A tren cung cac tap.
$adapter_a = "models/nen-qwen3-4b-viet5/best_checkpoint"
Chay-Lai "4a-A-DEV" @(
    "-m", "src.nhanh", "--nhanh", "A", "--model", $mo_hinh,
    "--adapter", $adapter_a, "--tap", "viet_phat_trien", "--n", "60") | Out-Null
foreach ($t in @("thach_thuc_doi_chu_the_phat_trien",
                 "thach_thuc_phuong_ngu_phat_trien",
                 "thach_thuc_dinh_chinh_phat_trien")) {
    Chay-Lai "4b-A-$t" @(
        "-m", "src.nhanh", "--nhanh", "A", "--model", $mo_hinh,
        "--adapter", $adapter_a, "--tap", $t) | Out-Null
}

# 5. Bo 500 hoi thoai phuong ngu DO GPT SINH (nguoi dung cung cap, xac nhan
#    11/09/2026) - CHI DE DO, khong bao gio huan luyen (du_lieu.chan_du_lieu_gpt).
#    Chay CUOI CUNG de khong lam cham ket qua chinh; hong thi ket qua chinh van con.
Chay-Lai "5-TRICH-GPT500" @(
    "-m", "src.nhanh", "--nhanh", "B", "C", "C_khoa", "C_khoa_hoi", "--model", $mo_hinh,
    "--tap", "gpt500_phuong_ngu", "--max-token", "3072",
    "--adapter-trich", $adapter) | Out-Null

Write-Output ""
Write-Output ("######## HET - " + (Get-Date -Format 'MM-dd HH:mm:ss'))
Get-ChildItem "$goc\data\ra_*phat_trien.jsonl" -EA SilentlyContinue |
    Sort-Object LastWriteTime | Select-Object -Last 12 |
    ForEach-Object { "{0,-56} {1}" -f $_.Name, $_.LastWriteTime }
