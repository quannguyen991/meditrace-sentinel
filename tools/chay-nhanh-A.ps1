# Huan luyen nhanh A tren bo the he 6, roi chay A tren nam tap.
#
# CHI DUNG ASCII trong tep nay - PowerShell 5.1 doc UTF-8 khong BOM theo ANSI.
#
# VI SAO TACH RIENG (14/09/2026). Buoc 3 va 4 cua `chay-the-he-6.ps1` deu BO CUOC
# luc 17:12: `--hau-to` duoc truyen la hai token ("--hau-to", "-viet6"), ma argparse
# thay gia tri bat dau bang dau gach thi coi do la mot THAM SO KHAC va bao thieu
# gia tri. Phai viet lien mot token: `--hau-to=-viet6`.
#
# Lo~i nay co tu ban the he 5 va chua bao gio lo ra, vi chuoi the he 5 chua tung
# chay. Bon bo thach thuc da xong roi nen chi can chay lai hai buoc nay.
$py = "D:\meditrace-venv\Scripts\python.exe"
$goc = "D:\meditrace-core"
$mo_hinh = "D:/hf-models/Qwen3-4B"
Set-Location $goc

function Chay-Lai {
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

# 1. Huan luyen nhanh A: hoi thoai -> ban tham chieu (truong `output`).
#    2048 du cho A - do bang tokenizer 11/09/2026, khong loai mau nao.
Chay-Lai "A1-TRAIN" @(
    "-m", "src.train_baseline", "--model", $mo_hinh,
    "--nhiem-vu", "benh_an", "--buoc", "400", "--do-dai", "2048",
    "--tep-train", "viet_train.jsonl", "--tep-val", "viet_phat_trien.jsonl",
    "--hau-to=-viet6") | Out-Null

# 2. Chay A tren cung nam tap ma duong ong da chay.
$adapter_a = "models/nen-qwen3-4b-viet6/best_checkpoint"
Chay-Lai "A2-DEV" @(
    "-m", "src.nhanh", "--nhanh", "A", "--model", $mo_hinh,
    "--adapter", $adapter_a, "--tap", "viet_phat_trien", "--n", "60") | Out-Null
foreach ($t in @("thach_thuc_doi_chu_the_phat_trien",
                 "thach_thuc_phuong_ngu_phat_trien",
                 "thach_thuc_dinh_chinh_phat_trien",
                 "thach_thuc_nhieu_asr_phat_trien")) {
    Chay-Lai "A3-$t" @(
        "-m", "src.nhanh", "--nhanh", "A", "--model", $mo_hinh,
        "--adapter", $adapter_a, "--tap", $t) | Out-Null
}

Write-Host ""
Write-Host ("######## HET - " + (Get-Date -Format 'MM-dd HH:mm:ss'))
