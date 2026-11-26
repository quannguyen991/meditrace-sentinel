# Chay tren HoaiDuc, canh duong ham tam (quick tunnel) cua MediTrace.
# Moi 30 giay doc link *.trycloudflare.com moi nhat trong duong-ham.log; neu khac link da ghi
# thi ghi vao KV `CAU_HINH` (khoa `dich`) de Worker meditrace-sentinel chuyen tiep dung cho.
#
# Khoa API Cloudflare (chi quyen "Workers KV Storage: Edit") nam trong tep $TepKhoa — KHONG in ra.
# Goi tu chay-duong-ham.cmd:  start "" /b powershell -NoProfile -ExecutionPolicy Bypass -File cap-nhat-kv.ps1
param(
  [string]$Log = 'C:\Users\hapur\meditrace\duong-ham.log',
  [string]$TepKhoa = 'C:\Users\hapur\.secrets\cloudflare-kv.token',
  [string]$NhatKy = 'C:\Users\hapur\meditrace\cap-nhat-kv.log'
)
$TaiKhoan = '23e0788e9cc2305d63a842ebf3809d52'
$KhoKV = 'd4a5576f38bd4c578530d8ae26973173'
$Url = "https://api.cloudflare.com/client/v4/accounts/$TaiKhoan/storage/kv/namespaces/$KhoKV/values/dich"
$daGhi = ''
function Ghi($s) { ((Get-Date).ToString('MM-dd HH:mm:ss') + ' ' + $s) | Add-Content $NhatKy -Encoding utf8 }
Ghi 'bat dau canh duong ham'
while ($true) {
  try {
    $m = Select-String -Path $Log -Pattern 'https://[a-z0-9-]+\.trycloudflare\.com' -AllMatches -EA Stop | Select-Object -Last 1
    $link = if ($m) { $m.Matches[-1].Value } else { '' }
    if ($link -and $link -ne $daGhi) {
      if (-not (Test-Path $TepKhoa)) { Ghi "THIEU khoa $TepKhoa - chua ghi $link" }
      else {
        $khoa = (Get-Content $TepKhoa -Raw).Trim()
        $r = Invoke-RestMethod -Method Put -Uri $Url -Headers @{ Authorization = "Bearer $khoa" } -ContentType 'text/plain' -Body $link
        if ($r.success) { $daGhi = $link; Ghi "da ghi $link" } else { Ghi "LOI ghi KV: $($r.errors | ConvertTo-Json -Compress)" }
      }
    }
  } catch { Ghi "LOI: $($_.Exception.Message)" }
  Start-Sleep -Seconds 30
}
