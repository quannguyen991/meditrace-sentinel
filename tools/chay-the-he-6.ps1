# Chuoi THE HE 6 tren HoaiDuc.
#
# CHI DUNG ASCII trong tep nay - PowerShell 5.1 doc UTF-8 khong BOM theo ANSI.
#
# BO THE HE 6 KHAC BO THE HE 5 O CHO: hoi thoai co chen trao doi XA GIAO de do
# dai khong con lo ca nay co bay hay khong, va co them bo thach thuc thu tu
# (nhieu ASR). Bo the he 5 khac bo the he 4 o cho: moi phat bieu trong dap an co trich dan
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
    # Moc buoc phai di bang Write-Host, KHONG bang Write-Output.
    #
    # Write-Output ghi vao duong ong TRA VE cua ham, ma moi cho goi ham nay deu
    # co `| Out-Null` de nuot gia tri $true/$false - the la nuot luon ca moc.
    # Do duoc ngay 13/09/2026: log cua ca chuoi the he 4 lan the he 6 khong co
    # lay mot dong "########" nao cua tung buoc, nen khong the biet chuoi dang o
    # buoc nao neu chi doc log. Write-Host di vao luong thong tin, `*>` van bat
    # duoc, va `| Out-Null` thi khong dong toi.
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

# 0. GIU adapter trich the he 4 duoi ten rieng. Lan huan luyen moi se tu choi
#    chay tiep tren checkpoint cua bo khac (van_tay_du_lieu), va ta muon giu no
#    de doi chieu. Chi di chuyen MOT lan: chay lai chuoi thi bo qua.
$cu = "$goc\models\nen-qwen3-4b-trich"
$luu = "$goc\models\nen-qwen3-4b-trich-the-he-4"
if ((Test-Path $cu) -and -not (Test-Path $luu)) {
    Move-Item $cu $luu
    Write-Output "######## da giu adapter the he truoc -> $luu"
}

# 0b. DON TEP DEM TRICH CUA THE HE TRUOC - CHI NHUNG TEP LAC BO.
#
# LO~I IM LANG THU BA cua du an, tai dien 13/09/2026: tep dem cua chuoi the he 4
# con nguyen, buoc chay nhanh NOI TIEP vao do - 69 ban ghi thi 52 mang id khong
# ton tai trong bo the he 6. `tests/test_kiem_khop.py` canh duoc khi CHAM nhung
# khong ai canh luc CHAY.
#
# Ban dau cho o day doi ten TAT CA tep dem. Cach do chan duoc lo~i tren nhung bien
# chuoi thanh thu khong khoi dong lai duoc giua chung: 14/09 phai dung chuoi de bo
# buoc GPT-500, va neu khoi dong lai thi 240 ca da trich (20 gio GPU) mat sach.
# Nen gio goi cong cu kiem TUNG BAN GHI - lac bo thi doi ten, dung bo thi giu de
# chay tiep dung cho do.
& $py "$goc\tools\don-dem-trich.py" `
    "viet_phat_trien" `
    "thach_thuc_doi_chu_the_phat_trien" `
    "thach_thuc_phuong_ngu_phat_trien" `
    "thach_thuc_dinh_chinh_phat_trien" `
    "thach_thuc_nhieu_asr_phat_trien" `
    "gpt500_phuong_ngu"

# 1. Huan luyen khau trich tren the he 6.
Chay-Lai "1-TRAIN-TRICH-TH6" @(
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
                 "thach_thuc_dinh_chinh_phat_trien",
                 "thach_thuc_nhieu_asr_phat_trien")) {
    Chay-Lai "2b-TRICH-$t" @(
        "-m", "src.nhanh", "--nhanh", "B", "C", "C_khoa", "C_khoa_hoi", "--model", $mo_hinh,
        "--tap", $t, "--max-token", "3072", "--adapter-trich", $adapter) | Out-Null
}

# 3. Huan luyen nhanh A tren BO TU SINH: dau vao la hoi thoai, dau ra la ban
#    tham chieu (truong output cua viet_train.jsonl). 2048 du cho A: do bang
#    tokenizer ngay 11/09/2026, khong loai mau nao (3.759/3.759 train).
Chay-Lai "3-TRAIN-A-TH6" @(
    "-m", "src.train_baseline", "--model", $mo_hinh,
    "--nhiem-vu", "benh_an", "--buoc", "400", "--do-dai", "2048",
    "--tep-train", "viet_train.jsonl", "--tep-val", "viet_phat_trien.jsonl",
    "--hau-to=-viet6") | Out-Null   # LIEN mot token: argparse thay "-viet6"
                                     # dung sau dau cach thi tuong la tham so khac

# 4. Chay A tren cung cac tap.
$adapter_a = "models/nen-qwen3-4b-viet6/best_checkpoint"
Chay-Lai "4a-A-DEV" @(
    "-m", "src.nhanh", "--nhanh", "A", "--model", $mo_hinh,
    "--adapter", $adapter_a, "--tap", "viet_phat_trien", "--n", "60") | Out-Null
foreach ($t in @("thach_thuc_doi_chu_the_phat_trien",
                 "thach_thuc_phuong_ngu_phat_trien",
                 "thach_thuc_dinh_chinh_phat_trien",
                 "thach_thuc_nhieu_asr_phat_trien")) {
    Chay-Lai "4b-A-$t" @(
        "-m", "src.nhanh", "--nhanh", "A", "--model", $mo_hinh,
        "--adapter", $adapter_a, "--tap", $t) | Out-Null
}

# 5. Bo 500 hoi thoai phuong ngu DO GPT SINH - DA BO KHOI CHUOI MAC DINH.
#
# Do 14/09/2026: 500 ca x 5 phut/ca = gan 42 gio, bang ca phan con lai cong lai,
# trong khi no chi phuc vu phep do phuong ngu NGOAI BANG - khong dung toi ket qua
# chinh nao. Chay rieng khi can:
#
#   & $py -m src.nhanh --nhanh B C C_khoa C_khoa_hoi --model $mo_hinh `
#         --tap gpt500_phuong_ngu --max-token 3072 --adapter-trich $adapter
#
# NHO: bo nay do GPT sinh, CHI DE DO, khong bao gio huan luyen
# (`du_lieu.chan_du_lieu_gpt` chan, `tests/test_chan_du_lieu_gpt.py` canh).

Write-Output ""
Write-Output ("######## HET - " + (Get-Date -Format 'MM-dd HH:mm:ss'))
Get-ChildItem "$goc\data\ra_*phat_trien.jsonl" -EA SilentlyContinue |
    Sort-Object LastWriteTime | Select-Object -Last 12 |
    ForEach-Object { "{0,-56} {1}" -f $_.Name, $_.LastWriteTime }
