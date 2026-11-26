# Chay tren HoaiDuc, canh duong ham tam (quick tunnel) cua MediTrace.
# Moi 30 giay doc link *.trycloudflare.com moi nhat trong duong-ham.log; neu khac link da gui
# thi POST link do toi Worker (duong /__meditrace/cap-nhat-dich) kem mat ma chung; Worker ghi
# vao KV va tu do chuyen tiep sang duong ham moi. Khong can khoa API Cloudflare.
#
# Mat ma chung nam trong $TepKhoa (cung gia tri voi secret KHOA_CAP_NHAT cua Worker) — KHONG in ra.
# Goi tu chay-duong-ham.cmd:  start "" /b powershell -NoProfile -ExecutionPolicy Bypass -File cap-nhat-kv.ps1
param(
  [string]$Log = 'C:\Users\hapur\meditrace\duong-ham.log',
  [string]$TepKhoa = 'C:\Users\hapur\.secrets\meditrace-cf-cap-nhat.key',
  [string]$NhatKy = 'C:\Users\hapur\meditrace\cap-nhat-kv.log',
  [string]$Worker = 'https://meditrace-sentinel.meditrace.workers.dev/__meditrace/cap-nhat-dich'
)
$daGui = ''
function Ghi($s) { ((Get-Date).ToString('MM-dd HH:mm:ss') + ' ' + $s) | Add-Content $NhatKy -Encoding utf8 }
Ghi 'bat dau canh duong ham'
while ($true) {
  try {
    $m = Select-String -Path $Log -Pattern 'https://[a-z0-9-]+\.trycloudflare\.com' -AllMatches -EA Stop | Select-Object -Last 1
    $link = if ($m) { $m.Matches[-1].Value } else { '' }
    if ($link -and $link -ne $daGui) {
      if (-not (Test-Path $TepKhoa)) { Ghi "THIEU mat ma $TepKhoa - chua gui $link" }
      else {
        $khoa = (Get-Content $TepKhoa -Raw).Trim()
        $r = Invoke-WebRequest -UseBasicParsing -Method Post -Uri $Worker -Headers @{ 'x-meditrace-khoa' = $khoa } -ContentType 'text/plain' -Body $link -TimeoutSec 30
        if ($r.StatusCode -eq 200) { $daGui = $link; Ghi "da gui $link" } else { Ghi "Worker tra $($r.StatusCode)" }
      }
    }
  } catch { Ghi "LOI: $($_.Exception.Message)" }
  Start-Sleep -Seconds 30
}
