# Tai mo hinh tu HuggingFace. LUON gui Range header.
#
# Do bang thuc nghiem tren HoaiDuc, ba lan do doc lap:
#
#   GET khong Range        tep nho (< 12 MB) ve binh thuong; tep safetensors
#                          vai GB dung han o 0 byte - ca huggingface_hub lan
#                          curl deu vay, cho hang chuc phut khong duoc byte nao
#   GET co Range           chay ngay. `-r 0-` ghi thang ra tep: 5,34 MB/s.
#                          Vi tri trong tep khong anh huong: dau tep 7,2 MB/s,
#                          offset 2 GB 6,6 MB/s
#
# Nen: `-C <offset>` - curl gui `Range: bytes=<offset>-` va ghi tiep vao tep.
# Mot request moi tep, va ngat giua chung thi chay lai la tiep tuc dung cho.
#
# (Ban truoc chia khoi 32 MB roi noi lai: chay duoc nhung chi 0,53 MB/s, vi
#  moi khoi ton them ~15 giay cho lan ghi tep tam. Mot request lien la du.)
#
#   powershell -File tai-mo-hinh.ps1 -Repo Qwen/Qwen3-4B -Dich D:\hf-models

param(
    [Parameter(Mandatory = $true)][string]$Repo,
    [string]$Dich = "D:\hf-models",
    [int]$LanToiDa = 40
)

$ErrorActionPreference = "Stop"
$ten = $Repo.Split("/")[-1]
$thuMuc = Join-Path $Dich $ten
New-Item -ItemType Directory -Force -Path $thuMuc | Out-Null

function Kich-Thuoc-Xa($url) {
    # Xin dung 1 byte. Header Content-Range tra ve tong kich thuoc that.
    $h = & curl.exe -sL -r 0-0 -D - -o NUL $url
    foreach ($d in $h) {
        if ($d -match 'Content-Range:\s*bytes\s+\d+-\d+/(\d+)') { return [int64]$Matches[1] }
    }
    return [int64](-1)
}

Write-Output "Lay danh sach tep cua $Repo"
$json = & curl.exe -sL "https://huggingface.co/api/models/$Repo"
$tep = ($json | ConvertFrom-Json).siblings | ForEach-Object { $_.rfilename } |
    Where-Object { $_ -match '\.(safetensors|json|txt)$' -and $_ -notmatch '/' } |
    Sort-Object
Write-Output ("Can tai " + $tep.Count + " tep")

foreach ($t in $tep) {
    $dichTep = Join-Path $thuMuc $t
    $url = "https://huggingface.co/$Repo/resolve/main/$t"
    [int64]$tong = Kich-Thuoc-Xa $url
    if ($tong -lt 0) { Write-Output ("  BO QUA (khong ro kich thuoc) " + $t); continue }

    # [int64] o khap noi: tep 4 GB tran Int32.
    [int64]$co = if (Test-Path $dichTep) { (Get-Item $dichTep).Length } else { 0 }
    if ($co -gt $tong) { Remove-Item $dichTep -Force; $co = 0 }
    if ($co -eq $tong) {
        Write-Output ("  {0,-42} da du {1,9:N1} MB" -f $t, ($tong / 1MB))
        continue
    }

    $batDau = Get-Date
    $daTai = $tong - $co
    $lan = 0
    while ($co -lt $tong -and $lan -lt $LanToiDa) {
        $lan++
        # -C <offset> gui Range: bytes=<offset>- va ghi tiep. Khong dung -C -
        # vi voi tep chua ton tai no gui GET khong Range, va cai do treo.
        & curl.exe -sL --retry 10 --retry-delay 5 --retry-all-errors `
            -C $co -o $dichTep $url
        [int64]$moi = if (Test-Path $dichTep) { (Get-Item $dichTep).Length } else { 0 }
        if ($moi -le $co) {
            Write-Output ("     lan {0}: khong tien duoc tu {1:N0} B" -f $lan, $co)
            Start-Sleep 5
        }
        $co = $moi
    }
    if ($co -lt $tong) { throw ("$t moi duoc {0:N0}/{1:N0} B sau $lan lan" -f $co, $tong) }

    $giay = ((Get-Date) - $batDau).TotalSeconds
    $tocDo = if ($giay -gt 0) { ($daTai / 1MB) / $giay } else { 0 }
    Write-Output ("  {0,-42} {1,9:N1} MB  {2,5:N1} MB/s  ({3} lan)" -f `
            $t, ($tong / 1MB), $tocDo, $lan)
}

$tongTM = (Get-ChildItem $thuMuc -File | Measure-Object Length -Sum).Sum
Write-Output ("XONG $Repo -> $thuMuc  (" + [math]::Round($tongTM / 1GB, 2) + " GB)")
