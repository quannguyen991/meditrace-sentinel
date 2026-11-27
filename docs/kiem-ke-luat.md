# Kiểm kê mô-đun src/ (sinh bằng `python -m tools.kiem_ke_luat`)

Tổng 142 mô-đun; 67 nằm trên luồng chính (bao đóng nhập từ `src/he_thong/dich_vu_http.py`).

Danh sách dưới đây chỉ để người dùng quyết; **không xoá gì tự động**. Một mô-đun không ai nhập vẫn có thể là lệnh chạy độc lập (`python -m src.x`).

## Ứng viên mã chết: không ai nhập, không trên luồng chính (45)

| Mô-đun | Dòng | Có phép thử | Chỗ ghi nguồn |
|---|---|---|---|
| `kiem_nghiem_ngoai_khuon` | 977 | có | 0 |
| `bo_kiem_tra` | 444 | có | 1 |
| `chung_chi_thuoc_do` | 407 | có | 0 |
| `quet_an_toan_duoc_ly_v2` | 406 | có | 0 |
| `bo_gpt500` | 363 | có | 5 |
| `doi_chung_tam_thuong` | 352 | có | 0 |
| `do_van_xuoi` | 333 | có | 0 |
| `bo_nguoi_that` | 313 | có | 0 |
| `cham_lai_bang_quy_gan` | 294 | có | 0 |
| `thach_thuc` | 290 | có | 0 |
| `cham_muc_thach_thuc` | 279 | có | 1 |
| `duong_danh_doi` | 266 | có | 0 |
| `kiem_khuon` | 263 | có | 0 |
| `audio.sim2real_v2` | 260 | có | 1 |
| `do_dac` | 246 | có | 0 |
| `do_dan_gian` | 246 | không | 0 |
| `do_tang_quy_gan` | 232 | có | 1 |
| `do_vidia2std` | 214 | không | 1 |
| `audio.phan_tich_am_thanh_v2` | 209 | có | 0 |
| `do_bit_nhan` | 200 | không | 4 |
| `khai_ma_nguon` | 198 | có | 2 |
| `do_canh_bao` | 194 | có | 0 |
| `do_quan_he` | 192 | có | 0 |
| `giao_dien_duyet` | 187 | không | 3 |
| `worm_audit_log` | 187 | có | 4 |
| `ocr_lam_sang` | 171 | có | 0 |
| `tang_cuong` | 171 | có | 1 |
| `kiem_thu_dot_bien` | 170 | có | 0 |
| `dau_vet_nguon` | 169 | không | 0 |
| `audio.asr.contextual_trie_600` | 163 | có | 0 |
| `da_benh_ly` | 155 | có | 0 |
| `nguon_lap_cau` | 151 | có | 2 |
| `do_tang_quan_he` | 142 | không | 0 |
| `do_neu_ten` | 140 | có | 0 |
| `nhanh_e` | 134 | có | 1 |
| `audio.pyannote_chay` | 119 | không | 0 |
| `gan_nhan_truoc` | 107 | có | 0 |
| `audio.asr.bench_metrics` | 100 | có | 0 |
| `audio.api` | 94 | không | 0 |
| `kiem_mo_hinh` | 92 | không | 0 |
| `nap_vietmed` | 75 | có | 0 |
| `tach_tap` | 72 | có | 0 |
| `cham_chu_the` | 70 | không | 0 |
| `do_bo_sot` | 46 | có | 0 |
| `audio` | 9 | không | 0 |

## Trên luồng chính nhưng không có phép thử nào nhập trực tiếp (6)

| Mô-đun | Dòng | Chỗ ghi nguồn |
|---|---|---|
| `canh_bao.phat_hien` | 758 | 1 |
| `canh_bao.toan_ca` | 150 | 0 |
| `audio.providers` | 103 | 0 |
| `audio.preprocessing` | 77 | 0 |
| `canh_bao.asr` | 48 | 0 |
| `audio.asr.sidecar_provider` | 42 | 0 |

## Toàn bộ

| Mô-đun | Dòng | Luồng chính | Phép thử | Nguồn | Được nhập bởi |
|---|---|---|---|---|---|
| `(src)` | 0 |  |  | 0 |  |
| `aho_corasick_duoc_thu` | 690 | ✓ | ✓ | 8 | duoc_ly_lam_sang, quet_an_toan_duoc_ly_v2 |
| `audio` | 9 |  |  | 0 |  |
| `audio.adapter` | 42 | ✓ | ✓ | 1 | audio.pipeline, dich_vu |
| `audio.alignment` | 159 | ✓ | ✓ | 0 | audio.pipeline |
| `audio.api` | 94 |  |  | 0 |  |
| `audio.asr` | 6 | ✓ | ✓ | 0 | audio.asr.bench_metrics, audio.asr.disagreement, audio.pipeline |
| `audio.asr.base` | 47 | ✓ | ✓ | 0 | audio.asr, audio.asr.faster_whisper_provider, audio.asr.phowhisper_provider, audio.asr.registry … |
| `audio.asr.bench_metrics` | 100 |  | ✓ | 0 |  |
| `audio.asr.contextual_trie_600` | 163 |  | ✓ | 0 |  |
| `audio.asr.critical_tokens` | 292 | ✓ | ✓ | 1 | audio.asr.bench_metrics, audio.asr.disagreement |
| `audio.asr.disagreement` | 48 | ✓ | ✓ | 1 | audio.pipeline |
| `audio.asr.faster_whisper_provider` | 93 | ✓ | ✓ | 0 | audio.asr.registry, audio.providers |
| `audio.asr.phowhisper_provider` | 283 | ✓ | ✓ | 0 | audio.asr.registry |
| `audio.asr.registry` | 82 | ✓ | ✓ | 0 | audio.pipeline |
| `audio.asr.schemas` | 105 | ✓ | ✓ | 0 | audio.asr, audio.asr.base, audio.asr.disagreement, audio.asr.faster_whisper_provider … |
| `audio.asr.sidecar_provider` | 42 | ✓ |  | 0 | audio.asr.registry, audio.pipeline |
| `audio.config` | 103 | ✓ | ✓ | 0 | audio.pipeline |
| `audio.models` | 84 | ✓ | ✓ | 0 | audio, audio.alignment, audio.pipeline, audio.storage |
| `audio.phan_tich_am_thanh_v2` | 209 |  | ✓ | 0 |  |
| `audio.pipeline` | 286 | ✓ | ✓ | 0 | audio.api, dich_vu |
| `audio.preprocessing` | 77 | ✓ |  | 0 | audio.pipeline |
| `audio.providers` | 103 | ✓ |  | 0 | audio.pipeline |
| `audio.pyannote_chay` | 119 |  |  | 0 |  |
| `audio.pyannote_provider` | 191 | ✓ | ✓ | 0 | audio.pipeline |
| `audio.sim2real_v2` | 260 |  | ✓ | 1 |  |
| `audio.storage` | 75 | ✓ | ✓ | 0 | audio.api, audio.pipeline, dich_vu |
| `bakeoff` | 381 | ✓ | ✓ | 0 | dich_vu, do_bit_nhan, do_bo_chan_doan, do_quan_he … |
| `bien_the_cau` | 2029 |  | ✓ | 0 | sinh_hoi_thoai_viet |
| `bit_nhan` | 128 |  | ✓ | 0 | do_bit_nhan |
| `bo_gpt500` | 363 |  | ✓ | 5 |  |
| `bo_kiem_tra` | 444 |  | ✓ | 1 |  |
| `bo_nguoi_that` | 313 |  | ✓ | 0 |  |
| `can_lam_sang` | 220 | ✓ | ✓ | 0 | dieu_phoi_ha_tang |
| `canh_bao` | 0 | ✓ | ✓ | 0 | canh_bao.asr, canh_bao.gop, canh_bao.phat_hien, canh_bao.toan_ca … |
| `canh_bao.asr` | 48 | ✓ |  | 0 | canh_bao.gop |
| `canh_bao.gop` | 156 | ✓ | ✓ | 0 | dich_vu, do_canh_bao, nhanh |
| `canh_bao.loai` | 320 | ✓ | ✓ | 0 | canh_bao.asr, canh_bao.gop, canh_bao.nhat_ky, canh_bao.phat_hien … |
| `canh_bao.nhat_ky` | 41 |  |  | 0 | do_canh_bao |
| `canh_bao.phat_hien` | 758 | ✓ |  | 1 | canh_bao.asr, canh_bao.gop, canh_bao.toan_ca |
| `canh_bao.so_lieu` | 167 | ✓ | ✓ | 0 | canh_bao.asr, canh_bao.phat_hien, canh_bao.toan_ca |
| `canh_bao.toan_ca` | 150 | ✓ |  | 0 | canh_bao.gop |
| `cap_nhat` | 173 | ✓ | ✓ | 0 | duong_danh_doi, kiem_thu_dot_bien, may_trang_thai_hoi_thoai, nhanh … |
| `cham_chu_the` | 70 |  |  | 0 |  |
| `cham_diem` | 93 | ✓ | ✓ | 0 | cham_lai_bang_quy_gan, chung_chi_thuoc_do, do_dac, sai_so |
| `cham_he_thong` | 699 | ✓ | ✓ | 0 | dich_vu, do_canh_bao |
| `cham_lai_bang_quy_gan` | 294 |  | ✓ | 0 |  |
| `cham_muc_thach_thuc` | 279 |  | ✓ | 1 |  |
| `chuan_dinh_dang` | 155 |  | ✓ | 0 | cham_muc_thach_thuc, do_dac |
| `chuan_hoa` | 235 | ✓ | ✓ | 0 | bo_gpt500, bo_kiem_tra, canh_bao.phat_hien, cham_he_thong … |
| `chung_chi_thuoc_do` | 407 |  | ✓ | 0 |  |
| `cong_rui_ro` | 295 | ✓ | ✓ | 0 | canh_bao.gop, cham_he_thong, dich_vu, dieu_phoi_ha_tang … |
| `context_vi` | 128 |  | ✓ | 0 | doi_chung_tam_thuong |
| `da_benh_ly` | 155 |  | ✓ | 0 |  |
| `dan_do_benh_nhan` | 226 | ✓ | ✓ | 0 | dieu_phoi_ha_tang |
| `dan_gian` | 226 | ✓ | ✓ | 1 | canh_bao.phat_hien, chuan_hoa, do_dan_gian, thach_thuc |
| `danh_gia_khoa` | 188 |  | ✓ | 0 | do_dan_gian |
| `dau_vet_nguon` | 169 |  |  | 0 |  |
| `dich_vu` | 661 | ✓ | ✓ | 2 |  |
| `dieu_phoi_ha_tang` | 389 | ✓ | ✓ | 3 | dich_vu |
| `do_bit_nhan` | 200 |  |  | 4 |  |
| `do_bo_chan_doan` | 330 |  | ✓ | 0 | doi_chung_tam_thuong |
| `do_bo_sot` | 46 |  | ✓ | 0 |  |
| `do_canh_bao` | 194 |  | ✓ | 0 |  |
| `do_dac` | 246 |  | ✓ | 0 |  |
| `do_dan_gian` | 246 |  |  | 0 |  |
| `do_lap_cau` | 154 |  | ✓ | 0 | nguon_lap_cau |
| `do_neu_ten` | 140 |  | ✓ | 0 |  |
| `do_quan_he` | 192 |  | ✓ | 0 |  |
| `do_tang_quan_he` | 142 |  |  | 0 |  |
| `do_tang_quy_gan` | 232 |  | ✓ | 1 |  |
| `do_trich` | 264 | ✓ | ✓ | 0 | cham_he_thong, do_bo_sot, loc_nhan_may |
| `do_van_xuoi` | 333 |  | ✓ | 0 |  |
| `do_vidia2std` | 214 |  |  | 1 |  |
| `doan_van` | 50 | ✓ | ✓ | 0 | khoa_bang_chung, sinh_hoi_thoai_viet |
| `doi_chung_tam_thuong` | 352 |  | ✓ | 0 |  |
| `du_lieu` | 204 | ✓ | ✓ | 0 | bakeoff, cham_chu_the, cham_he_thong, cham_lai_bang_quy_gan … |
| `du_lieu_trich` | 222 | ✓ | ✓ | 1 | cham_he_thong, danh_gia_khoa, do_trich, giao_dien_duyet |
| `duoc_ly_lam_sang` | 307 | ✓ | ✓ | 2 | dieu_phoi_ha_tang, quet_an_toan_duoc_ly_v2 |
| `duong_dan` | 48 | ✓ | ✓ | 0 | bakeoff, bo_gpt500, cham_chu_the, cham_he_thong … |
| `duong_danh_doi` | 266 |  | ✓ | 0 |  |
| `fhir_exporter` | 653 | ✓ | ✓ | 3 | dieu_phoi_ha_tang |
| `gan_nhan_truoc` | 107 |  | ✓ | 0 |  |
| `giao_dien_duyet` | 187 |  |  | 3 |  |
| `guardrails` | 351 | ✓ | ✓ | 9 | bo_kiem_tra, dieu_phoi_ha_tang |
| `hieu_chinh_lieu` | 588 | ✓ | ✓ | 0 | dieu_phoi_ha_tang, ocr_lam_sang |
| `hoi_lai` | 401 | ✓ | ✓ | 0 | nhanh |
| `khai_ma_nguon` | 198 |  | ✓ | 2 |  |
| `kho_khuon` | 110 |  | ✓ | 0 | sinh_hoi_thoai_viet, tach_tap_viet |
| `khoa_bang_chung` | 545 | ✓ | ✓ | 1 | bo_kiem_tra, canh_bao.gop, canh_bao.phat_hien, canh_bao.toan_ca … |
| `khu_dinh_danh` | 212 | ✓ | ✓ | 0 | dieu_phoi_ha_tang |
| `khuon_lo_3` | 2958 |  |  | 0 | khuon_mo_rong |
| `khuon_lo_4` | 2731 |  | ✓ | 2 | khuon_mo_rong |
| `khuon_lo_5` | 2264 |  |  | 2 | khuon_mo_rong |
| `khuon_lo_6` | 2262 |  |  | 0 | khuon_mo_rong |
| `khuon_lo_7` | 2432 |  | ✓ | 1 | khuon_mo_rong |
| `khuon_lo_8` | 2499 |  |  | 1 | khuon_mo_rong |
| `khuon_mo_rong` | 6616 |  | ✓ | 3 | kho_khuon |
| `kiem_day_du` | 151 | ✓ | ✓ | 0 | nhanh, nhanh_e |
| `kiem_duyet_bhyt_va_bo_sot` | 672 | ✓ | ✓ | 6 | dich_vu |
| `kiem_khuon` | 263 |  | ✓ | 0 |  |
| `kiem_mo_hinh` | 92 |  |  | 0 |  |
| `kiem_nghiem_ngoai_khuon` | 977 |  | ✓ | 0 |  |
| `kiem_thu_dot_bien` | 170 |  | ✓ | 0 |  |
| `loc_nhan_may` | 72 |  | ✓ | 0 | gan_nhan_truoc |
| `loi_dan_thuong` | 271 |  | ✓ | 0 | sinh_hoi_thoai_viet |
| `loss_theo_doan` | 89 | ✓ | ✓ | 0 | train_baseline |
| `may_trang_thai_hoi_thoai` | 381 |  | ✓ | 0 | bo_kiem_tra, kiem_nghiem_ngoai_khuon |
| `nap_vietmed` | 75 |  | ✓ | 0 |  |
| `nap_vimq` | 48 |  | ✓ | 0 | gan_nhan_truoc |
| `ngu_lieu_viet` | 3625 |  | ✓ | 0 | da_benh_ly, kho_khuon, kiem_khuon, nguon_lap_cau … |
| `nguon_lap_cau` | 151 |  | ✓ | 2 |  |
| `nhanh` | 501 | ✓ | ✓ | 1 | dich_vu, giao_dien_duyet |
| `nhanh_e` | 134 |  | ✓ | 1 |  |
| `nhat_ky_loi_nhac` | 489 |  | ✓ | 3 | khai_ma_nguon |
| `nhieu_asr` | 192 |  | ✓ | 0 | thach_thuc |
| `ocr_lam_sang` | 171 |  | ✓ | 0 |  |
| `phan_quan_he` | 252 | ✓ | ✓ | 1 | nhanh |
| `phat_bieu` | 386 | ✓ | ✓ | 0 | bakeoff, bo_kiem_tra, canh_bao.phat_hien, cap_nhat … |
| `phuong_ngu` | 228 |  | ✓ | 0 | sinh_hoi_thoai_viet, thach_thuc |
| `phuong_ngu_lam_sang` | 334 | ✓ | ✓ | 0 | guardrails, trich_xuat_thuc_the |
| `quet_an_toan_duoc_ly_v2` | 406 |  | ✓ | 0 |  |
| `rui_ro_quy_gan` | 164 |  | ✓ | 0 | duong_danh_doi |
| `sai_so` | 551 | ✓ | ✓ | 1 | bo_gpt500, bo_nguoi_that, cham_he_thong, danh_gia_khoa … |
| `sinh_benh_an` | 432 | ✓ | ✓ | 0 | bo_nguoi_that, cham_he_thong, cham_muc_thach_thuc, chuan_dinh_dang … |
| `sinh_bo_chan_doan` | 280 |  | ✓ | 0 | do_bo_chan_doan, do_van_xuoi, doi_chung_tam_thuong |
| `sinh_hoi_thoai_viet` | 2040 |  | ✓ | 1 | cham_muc_thach_thuc, chuan_dinh_dang, giao_dien_duyet, tach_tap_viet … |
| `sua_cuc_bo` | 233 | ✓ | ✓ | 0 | nhanh, nhanh_e |
| `tach_tap` | 72 |  | ✓ | 0 |  |
| `tach_tap_viet` | 229 |  | ✓ | 1 | sinh_hoi_thoai_viet |
| `tang_cuong` | 171 |  | ✓ | 1 |  |
| `thach_thuc` | 290 |  | ✓ | 0 |  |
| `thang_diem_lam_sang` | 628 | ✓ | ✓ | 0 | dieu_phoi_ha_tang |
| `thuc_the` | 274 | ✓ | ✓ | 0 | bo_kiem_tra, canh_bao.phat_hien, canh_bao.toan_ca, cap_nhat … |
| `thuoc_do_quy_gan` | 310 | ✓ | ✓ | 0 | bo_gpt500, bo_nguoi_that, canh_bao.phat_hien, cham_lai_bang_quy_gan … |
| `train_baseline` | 327 | ✓ | ✓ | 0 | bakeoff, nhanh |
| `trich_xuat_thuc_the` | 571 |  | ✓ | 1 | bo_kiem_tra |
| `tro_ly_lam_sang` | 196 | ✓ | ✓ | 0 | dieu_phoi_ha_tang |
| `ung_vien_quan_he` | 313 | ✓ | ✓ | 0 | do_tang_quan_he, phan_quan_he |
| `van_tay_bo` | 202 | ✓ | ✓ | 0 | sai_so, tach_tap_viet, thach_thuc |
| `vi_du_mau` | 97 | ✓ | ✓ | 0 | bakeoff, du_lieu_trich |
| `worm_audit_log` | 187 |  | ✓ | 4 |  |
