# Chuoi THE HE 8 tren HoaiDuc: CHO the he 7 xong, TRAO ma + du lieu, roi HUAN LUYEN.
#
# CHI DUNG ASCII trong tep nay - PowerShell 5.1 doc UTF-8 khong BOM theo ANSI.
#
# PHAN VIEC (16/09/2026). HoaiDuc chi HUAN LUYEN: khau trich roi nhanh A, deu bf16
# nhu the he 7, de so sanh hai the he khong lan bien kieu so. Buoc SINH chay tren
# Kaggle 2xT4 (card T4 khong ho tro bf16 nen khong train o do duoc).
#
# VI SAO PHAI CHO, KHONG DONG BO NGAY. Moi buoc cua chuoi the he 7 mo mot tien trinh
# Python MOI va nap lai `src/`. Doi ma luc the he 7 con chay thi buoc dinh chinh va
# nhanh A cua the he 7 se chay bang loi nhac va luoc do moi. Nen ma va du lieu the he 8
# nam o `giai-doan-the-he-8\` cho toi khi the he 7 xong han.
#
# TRAO GI, CAT GI:
#   src\, tools\                -> thay bang ban the he 8
#   data\ bo du lieu            -> thay bang bo the he 8 (co van tay)
#   data\ tep dem trich + ra_*  -> CAT sang luu-the-he-7\data. The he 8 TRUNG ID ca voi
#                                  the he 7; de lai thi buoc sinh dung nham tep dem cu
#   models\nen-qwen3-4b-trich   -> doi ten thanh ...-the-he-7, de train the he 8 tu dau

$py = "D:\meditrace-venv\Scripts\python.exe"
$goc = "D:\meditrace-sentinel"
$moi = "$goc\giai-doan-the-he-8"
$luu = "$goc\luu-the-he-7"
$mo_hinh = "D:/hf-models/Qwen3-4B"
Set-Location $goc

function Moc($m) { Write-Host ("######## " + $m + " - " + (Get-Date -Format 'MM-dd HH:mm:ss')) }

function Chay-Lai {
    param([string]$Ten, [string[]]$Doi, [int]$LanToiDa = 3)
    for ($i = 1; $i -le $LanToiDa; $i++) {
        Moc "$Ten - lan $i"
        & $py @Doi
        if ($LASTEXITCODE -eq 0) { Moc "$Ten XONG"; return $true }
        Write-Host "######## $Ten HONG (ma $LASTEXITCODE)"
        Start-Sleep 30
    }
    Write-Host "######## $Ten BO CUOC sau $LanToiDa lan"
    return $false
}

# 1. CHO the he 7 het chay.
Moc "1-CHO-THE-HE-7"
while ((Get-ScheduledTask -TaskName 'MEDITRACE_THE_HE_7').State -eq 'Running') { Start-Sleep 300 }
$xong7 = @(Get-ChildItem "$goc\data\ra_A_*phat_trien.jsonl" -EA SilentlyContinue).Count
if ($xong7 -lt 5) {
    Moc "DUNG: MEDITRACE_THE_HE_7 het chay nhung chi co $xong7/5 tep ket qua nhanh A - the he 7 CHUA XONG, khong trao"
    exit 1
}
Moc "the he 7 xong ($xong7 tep ket qua nhanh A)"

# 2. Nhuong GPU: chuoi the he 7 bat lai Ollama Serve khi ket thuc; tat lai.
#    BDS van co embedding qua duong ham tu laptop (duong-ham-bds.ps1 theo doi ca
#    MEDITRACE_THE_HE_7 lan MEDITRACE_THE_HE_8).
Disable-ScheduledTask -TaskName 'Ollama Serve' | Out-Null
Stop-ScheduledTask -TaskName 'Ollama Serve' -EA SilentlyContinue
Get-Process ollama, 'ollama app', llama-server -EA SilentlyContinue | Stop-Process -Force
Moc "2-NHUONG-GPU: da tat Ollama Serve"

# 3. TRAO ma va du lieu. Mot lan: co moc thi bo qua (chay lai giua chung khong trao lai).
if (-not (Test-Path "$luu\.da-trao")) {
    New-Item -ItemType Directory -Force "$luu\data", "$luu\models" | Out-Null
    Move-Item "$goc\src" "$luu\src"
    Copy-Item "$moi\src" "$goc\src" -Recurse
    Copy-Item "$moi\tools\*" "$goc\tools\" -Force
    $bo = @("viet_train", "viet_phat_trien", "viet_kiem_tra_cuoi", "trich_train", "trich_giu_lai",
            "thach_thuc_doi_chu_the_phat_trien", "thach_thuc_phuong_ngu_phat_trien",
            "thach_thuc_dinh_chinh_phat_trien", "thach_thuc_nhieu_asr_phat_trien")
    foreach ($b in $bo) {
        foreach ($duoi in @(".jsonl", ".van_tay.json")) {
            if (Test-Path "$goc\data\$b$duoi") { Move-Item "$goc\data\$b$duoi" "$luu\data\" -Force }
            if (Test-Path "$moi\data\$b$duoi") { Copy-Item "$moi\data\$b$duoi" "$goc\data\" -Force }
        }
    }
    Get-ChildItem "$goc\data\trich_viet_phat_trien_*.jsonl*", "$goc\data\trich_thach_thuc_*.jsonl*",
                  "$goc\data\ra_*phat_trien.jsonl" -EA SilentlyContinue |
        Move-Item -Destination "$luu\data\" -Force
    if (Test-Path "$goc\models\nen-qwen3-4b-trich") {
        Move-Item "$goc\models\nen-qwen3-4b-trich" "$goc\models\nen-qwen3-4b-trich-the-he-7"
    }
    New-Item -ItemType File "$luu\.da-trao" | Out-Null
    Moc "3-TRAO: ma va du lieu the he 8 da vao cho; the he 7 cat o $luu"
}

# 4. Du lieu PHAI la the he 8 truoc khi dung GPU.
& $py "$goc\tools\kiem-the-he.py" "8" "viet_train" "viet_phat_trien" `
    "thach_thuc_doi_chu_the_phat_trien" "thach_thuc_phuong_ngu_phat_trien" `
    "thach_thuc_dinh_chinh_phat_trien" "thach_thuc_nhieu_asr_phat_trien"
if ($LASTEXITCODE -ne 0) { Moc "DUNG: du lieu khong phai the he 8"; exit 1 }

# 5. Train khau trich the he 8. Xong thi ghi MOC de phien Claude biet day adapter
#    len Kaggle cho buoc sinh.
Chay-Lai "5-TRAIN-TRICH-TH8" @(
    "-m", "src.train_baseline", "--model", $mo_hinh,
    "--nhiem-vu", "trich", "--buoc", "400", "--do-dai", "3072") | Out-Null
if (Test-Path "$goc\models\nen-qwen3-4b-trich\best_checkpoint") {
    New-Item -ItemType File -Force "$goc\logs\moc-trich-the-he-8-xong" | Out-Null
}

# 6. Train nhanh A the he 8 (buoc sinh cua A cung chay tren Kaggle).
Chay-Lai "6-TRAIN-A-TH8" @(
    "-m", "src.train_baseline", "--model", $mo_hinh,
    "--nhiem-vu", "benh_an", "--buoc", "400", "--do-dai", "2048",
    "--tep-train", "viet_train.jsonl", "--tep-val", "viet_phat_trien.jsonl",
    "--hau-to=-viet8") | Out-Null
if (Test-Path "$goc\models\nen-qwen3-4b-viet8\best_checkpoint") {
    New-Item -ItemType File -Force "$goc\logs\moc-A-the-he-8-xong" | Out-Null
}
Moc "HET phan huan luyen the he 8"
