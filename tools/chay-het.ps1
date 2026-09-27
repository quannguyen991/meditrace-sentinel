# Chay ca ba viec lien mach, khong can nguoi truc.
#
# CHI DUNG ASCII trong tep nay. PowerShell 5.1 doc tep UTF-8 khong BOM
# theo bang ma ANSI, nen dau gach dai (em dash) thanh ba byte trong do
# co mot dau nhay - va dau nhay do DONG CHUOI, lam vo ca kich ban.
# Da xay ra that: ban dau tep nay khong chay duoc vi ly do do.
#
#   1. Sau nhanh trung gian voi max_token 3072 (o 1536 thi 8/35 bi cat cut)
#   2. Huan luyen mo hinh nen (Task 6)
#   3. Nhanh A va A+ tren adapter vua train
#
# Moi buoc duoc THU LAI toi 4 lan. Ly do: may nay da mot lan bao
# `CUDA error: unspecified launch failure` giua chung. Buoc 1 va buoc 2 deu
# chay tiep duoc (tep dem cho trich, checkpoint cho train), nen thu lai chi
# mat vai phut chu khong mat ca lan chay.
#
#   powershell -File chay-het.ps1

$py = "D:\meditrace-venv\Scripts\python.exe"
$goc = "D:\meditrace-sentinel"
$mo_hinh = "D:/hf-models/Qwen3-4B"
$adapter = "models/nen-qwen3-4b/best_checkpoint"
Set-Location $goc

function Chay-Lai {
    param([string]$Ten, [string[]]$Doi, [int]$LanToiDa = 4)
    for ($i = 1; $i -le $LanToiDa; $i++) {
        Write-Output ""
        Write-Output ("############ $Ten - lan $i - " + (Get-Date -Format 'HH:mm:ss'))
        & $py @Doi
        if ($LASTEXITCODE -eq 0) {
            Write-Output ("############ $Ten XONG - " + (Get-Date -Format 'HH:mm:ss'))
            return $true
        }
        Write-Output "############ $Ten HONG (ma $LASTEXITCODE)"
        Start-Sleep 30
    }
    Write-Output "############ $Ten BO CUOC sau $LanToiDa lan"
    return $false
}

$ok1 = Chay-Lai "1-SAU-NHANH" @(
    "-m", "src.nhanh", "--nhanh", "B", "C_khong_luat", "C_khong_lien_ket",
    "C", "C_ghi_de", "D", "--model", $mo_hinh, "--tap", "phat_trien",
    "--max-token", "3072")

$ok2 = Chay-Lai "2-TRAIN-NEN" @(
    "-m", "src.train_baseline", "--model", $mo_hinh, "--buoc", "200")

if ($ok2) {
    $ok3 = Chay-Lai "3-NHANH-A" @(
        "-m", "src.nhanh", "--nhanh", "A", "--model", $mo_hinh,
        "--adapter", $adapter, "--tap", "phat_trien")
    if ($ok3) {
        Chay-Lai "4-NHANH-A-CONG" @(
            "-m", "src.nhanh", "--nhanh", "A+", "--model", $mo_hinh,
            "--adapter", $adapter, "--tap", "phat_trien") | Out-Null
    }
}
else {
    Write-Output "Khong train duoc nen bo qua nhanh A va A+."
}

Write-Output ""
Write-Output ("############ HET - " + (Get-Date -Format 'HH:mm:ss'))
Get-ChildItem "$goc\data\ra_*_phat_trien.jsonl" | ForEach-Object {
    "{0,-40} {1} dong" -f $_.Name, (Get-Content $_.FullName).Count
}
