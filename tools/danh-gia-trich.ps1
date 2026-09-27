# Danh gia khau trich sau khi huan luyen xong. Tu cho train ket thuc roi chay.
#
# CHI DUNG ASCII trong tep nay - PowerShell 5.1 doc UTF-8 khong BOM theo ANSI,
# dau gach dai se dong chuoi va vo ca kich ban.
#
# Ba buoc, xep theo do quan trong giam dan (hong buoc sau van con buoc truoc):
#
#   1. Hoi thoai THAT (35 ca) voi adapter da huan luyen  <- cau hoi quyet dinh
#      Co chuyen duoc tu du lieu mo phong sang hoi thoai that khong?
#   2. Tap giu lai (40 ca, 4 khuon chua thay) voi adapter <- kiem tinh
#      No co hoc duoc gi khong?
#   3. Tap giu lai KHONG adapter                          <- moc so sanh cho 2
#
# Buoc 3 chay cuoi vi no chi la moc so sanh; neu het thoi gian thi buoc 1 va
# 2 da du de ket luan huong.

$py = "D:\meditrace-venv\Scripts\python.exe"
$goc = "D:\meditrace-sentinel"
$mo_hinh = "D:/hf-models/Qwen3-4B"
$adapter = "models/nen-qwen3-4b-trich/best_checkpoint"
Set-Location $goc

# Cho tien trinh huan luyen ket thuc. Toi da 90 phut.
for ($i = 0; $i -lt 120; $i++) {
    $p = Get-Process python -EA SilentlyContinue | Where-Object { $_.WS -gt 500MB }
    if (-not $p) { break }
    Start-Sleep 45
}
Write-Output ("Train da xong luc " + (Get-Date -Format 'HH:mm:ss'))

if (-not (Test-Path (Join-Path $goc $adapter))) {
    Write-Output "KHONG THAY adapter $adapter - dung."
    exit 1
}

function Chay-Lai {
    param([string]$Ten, [string[]]$Doi, [int]$LanToiDa = 3)
    for ($i = 1; $i -le $LanToiDa; $i++) {
        Write-Output ""
        Write-Output ("######## $Ten - lan $i - " + (Get-Date -Format 'HH:mm:ss'))
        & $py @Doi
        if ($LASTEXITCODE -eq 0) { return $true }
        Write-Output "######## $Ten HONG (ma $LASTEXITCODE)"
        Start-Sleep 30
    }
    return $false
}

# 1. Hoi thoai that, co adapter. Chay ca sau nhanh tu MOT lan trich.
Chay-Lai "1-THAT-CO-ADAPTER" @(
    "-m", "src.nhanh", "--nhanh", "B", "C_khong_luat", "C_khong_lien_ket",
    "C", "C_ghi_de", "D", "--model", $mo_hinh, "--tap", "phat_trien",
    "--max-token", "3072", "--adapter-trich", $adapter) | Out-Null

# 2. Tap giu lai (4 khuon chua thay), co adapter.
Chay-Lai "2-GIU-LAI-CO-ADAPTER" @(
    "-m", "src.nhanh", "--nhanh", "C", "--model", $mo_hinh,
    "--tap", "hv_giu_lai", "--max-token", "3072",
    "--adapter-trich", $adapter) | Out-Null

# 3. Tap giu lai, KHONG adapter - moc so sanh.
Chay-Lai "3-GIU-LAI-KHONG-ADAPTER" @(
    "-m", "src.nhanh", "--nhanh", "C", "--model", $mo_hinh,
    "--tap", "hv_giu_lai", "--max-token", "3072") | Out-Null

Write-Output ""
Write-Output ("######## HET - " + (Get-Date -Format 'HH:mm:ss'))
Get-ChildItem "$goc\data\trich_*.jsonl" | ForEach-Object {
    "{0,-40} {1} ca" -f $_.Name, (Get-Content $_.FullName).Count
}
