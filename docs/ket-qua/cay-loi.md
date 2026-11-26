# Đo lớp cảnh báo bằng lỗi cấy nhân tạo (25/11/2026)

Mọi số dưới đây là **trên lỗi cấy nhân tạo**, không phải độ chính xác thực tế. Không dùng nhãn người, không dùng mô
hình ngôn ngữ, không cần GPU. Đăng ký trước: `docs/dang-ky-truoc-bo-luat.md` (mục sửa đổi 25/11). Plan:
`docs/superpowers/plans/2026-11-25-cay-loi-do-canh-bao.md`.

**Cách đo.** Lấy đáp án làm bản ghi hoàn hảo, cấy **đúng một** lỗi đã biết loại và vị trí
(`tools/cay_loi.py`, 16 loại), chạy toàn bộ lớp cảnh báo (`canh_bao.gop.chay`), rồi đếm:

- **Độ nhạy** = tỉ lệ lần cấy có cảnh báo **đúng nhóm** trên đúng dòng bị cấy. Với lỗi xoá: cảnh báo bỏ sót chạm
  lượt của dòng bị xoá.
- **Báo nhầm** = số cảnh báo trên bản sạch (đáp án không cấy gì), tính trung bình mỗi ca.

Lệnh chạy:

```
python -m src.do_cay_loi --tap dieu_chinh --ra-json …
python -m src.do_cay_loi --tap giu_kin --toi-da-khoa-luat --ra-json …
```

## Tập điều chỉnh (400 ca từ `viet_train_v2`, được nhìn và được sửa luật)

| Loại lỗi cấy | n | Độ nhạy trước | Độ nhạy sau [Wilson 95%] | D đưa sang cần xác nhận (trước → sau) |
|---|---:|---:|---|---:|
| `doi_chu_the` | 400 | 0,945 | 0,945 [0,918–0,963] | 88 → 88 |
| `dao_phu_dinh` | 400 | 0,052 | **0,695** [0,648–0,738] | 35 → 276 |
| `nang_chac_chan` | 160 | 0,881 | 0,881 [0,822–0,923] | 141 → 141 |
| `gia_dinh_thanh_that` | 400 | 0,355 | **0,445** [0,397–0,494] | 146 → 182 |
| `ban_cu_con_hieu_luc` | 56 | 0,482 | 0,482 [0,357–0,610] | 28 → 28 |
| `doi_lieu` | 19 | 0,789 | 0,789 [0,567–0,915] | 15 → 15 |
| `doi_so` | 270 | 0,544 | **0,900** [0,858–0,930] | 50 → 53 |
| `doi_thuoc` | 247 | 0,996 | 0,996 | 246 → 246 |
| `doi_thoi_gian` | 345 | 0,916 | 0,916 | 114 → 114 |
| `bia_menh_de` | 400 | 1,000 | 1,000 | 400 → 400 |
| `bia_trich_dan` | 400 | 1,000 | 1,000 | 400 → 400 |
| `doi_bang_chung` | 400 | 1,000 | 1,000 | 81 → 87 |
| `xoa_di_ung` | 118 | 0,949 | **0,983** [0,940–0,995] | — |
| `xoa_thuoc` | 208 | 0,962 | 0,962 | — |
| `xoa_phu_dinh` | 181 | 1,000 | 1,000 | — |
| `xoa_so_lieu` | 270 | 0,952 | 0,948 | — |
| **Trung bình** | | **0,801** | **0,871** | |
| **Báo nhầm / ca sạch** | | **8,98** | **7,11** | |
| Chặn thừa chính sách D trên bản sạch | | 6,4% | 6,4% | |

### Các vòng sửa (tối đa 5, tiêu chí giữ đăng ký trước)

| Vòng | Sửa gì | Kết quả | Giữ? |
|---|---|---|---|
| 0 | Sửa **công cụ**, không sửa luật: `dao_phu_dinh` vừa bật cờ vừa thêm "không" nên hai lần đảo triệt tiêu (phủ định = cờ XOR chữ "không"). Mốc lỗi 0,003 → mốc đúng 0,052 | — | — |
| 1 | Y lệnh bác sĩ ("tôi kê … nhé", "từ nay ngừng … nha") ghi thành sự việc → `PLAN_AS_FACT` | `gia_dinh_thanh_that` 0,355 → 0,445; báo nhầm không đổi | Giữ |
| 2 | Số **không đơn vị** ("độ 2", "2 đến 4 răng", "Marsh 3") phải có trong lượt dẫn, đếm theo số lần | `doi_so` 0,544 → 0,900; báo nhầm +1/400 ca | Giữ |
| 3 | Bản ghi phủ định mà lời được dẫn khẳng định (`phu_dinh_nguoc`) | Bản đầu: 0,052 → 0,713 nhưng báo nhầm +0,12/ca (vượt 0,02) — **không đạt**. Đã siết: xét "đỡ/hết/êm/ổn" ở cả lượt → 0,695, báo nhầm 0 | Giữ (bản siết) |
| 4 | Bỏ cảnh báo bỏ sót chung chung cho lời xã giao ("Vâng em nghe", "Chúc bác sĩ…") | Báo nhầm 9,1 → 7,1/ca; nhưng `xoa_di_ung`/`xoa_thuoc` tụt vì trước đó chỉ "bắt" nhờ cảnh báo xã giao trùng lượt | Chưa đạt một mình |
| 5 | Sửa gốc `doan_chua_ghi`: chất dị ứng chưa ghi không bị che bởi dòng dị ứng khác; bản bị thay thế không che tên thuốc | Gộp 4+5: TB 0,871, `xoa_di_ung` 0,983, báo nhầm 7,11 | Giữ |

Rào chắn sau vòng 5, trên đầu ra mô hình cũ (`data/thach_thuc`):

- Lọt lỗi nguy hiểm: C 45,2%, D 43,3%. Không đổi.
- Chặn thừa của D: 6,1%.
- Jaccard bất biến dấu câu: 0,885.
- Toàn bộ phép thử: 1.688 đạt.

## Tập giữ kín (đáp án 240 ca `thach_thuc_v2`, chạy một lần sau khi khoá luật)

Khoá luật lúc 25/11; SHA-256 các tệp luật ghi trong sổ thực thi. File: `cay-loi-giu-kin.json`.

| Loại lỗi cấy | n | Độ nhạy [Wilson 95%] |
|---|---:|---|
| `doi_chu_the` | 240 | 0,946 [0,910–0,968] |
| `dao_phu_dinh` | 240 | 0,617 [0,554–0,676] |
| `nang_chac_chan` | 106 | 0,896 [0,824–0,941] |
| `gia_dinh_thanh_that` | 240 | 0,417 [0,356–0,480] |
| `ban_cu_con_hieu_luc` | 45 | 0,311 [0,195–0,457] |
| `doi_lieu` | 10 | 1,000 [0,722–1,000] |
| `doi_so` | 173 | 0,908 [0,855–0,942] |
| `doi_thuoc` | 162 | 1,000 |
| `doi_thoi_gian` | 191 | 0,953 |
| `bia_menh_de` / `bia_trich_dan` / `doi_bang_chung` | 240 mỗi loại | 1,000 |
| `xoa_di_ung` | 108 | 0,972 [0,921–0,991] |
| `xoa_thuoc` | 141 | 0,972 [0,929–0,989] |
| `xoa_phu_dinh` | 88 | 0,989 |
| `xoa_so_lieu` | 173 | 0,954 |
| **Trung bình** | | **0,871** |
| **Báo nhầm / ca sạch** | | **8,00** (979 trong đó là bỏ sót chung chung, chỉ lưu ở hậu trường) |
| Chặn thừa chính sách D trên bản sạch | | 7,4% |

Ba luật mới trên tập giữ kín (precision trong lượt cấy / báo nhầm mỗi ca sạch):

- `NEGATION_FLIP`: 0,859 / 0,004.
- `NUMERIC_MISMATCH`: 0,823 / 0.
- `PLAN_AS_FACT`: 0,827 / 0.

Cả ba qua ngưỡng đăng ký trước (≥ 0,5 và ≤ 0,05).

**Độ nhạy trung bình giữ nguyên 0,871 từ tập điều chỉnh sang tập giữ kín**, nghĩa là các sửa đổi không chỉ khớp
riêng với tập điều chỉnh. Riêng `dao_phu_dinh` thấp hơn (0,695 → 0,617).

### Áp ngưỡng nâng mã `thu_nghiem` → `on_dinh`

Không mã nào đạt. Mình chỉ ghi khuyến nghị, không sửa `loai.py`.

- `OMITTED_ANSWER`: precision 0,111, báo nhầm 0,20/ca. Giữ thử nghiệm.
- `DOSE_OVER_MAX`, `CONTRAINDICATION`, `DRUG_INTERACTION`, `IMPORTANT_MODIFIER_DROPPED`,
  `DOCTOR_STATEMENT_AS_PATIENT_FACT`, `UNSUPPORTED_CAUSALITY`, `UNSUPPORTED_FACT_COMBINATION`,
  `CLINICALLY_IRRELEVANT`: **chưa có loại lỗi cấy tương ứng**, nên phép đo này không đánh giá được. Precision 0 ở
  đây là do không có lỗi đích, không phải do luật sai.

## Giới hạn (phải ghi khi báo cáo)

- Lỗi cấy "sạch" hơn lỗi mô hình mắc thật. Mỗi bản chỉ có đúng một lỗi, trong khi đầu ra thật có thể có nhiều lỗi
  chồng nhau.
- Đáp án được coi là đúng tuyệt đối. Vì vậy cảnh báo hợp lý trên bản sạch vẫn bị tính là báo nhầm, ví dụ câu âm
  tính chung mà đáp án không ghi.
- Cùng bộ sinh dữ liệu tạo ra cả hội thoại lẫn đáp án, nên các mẫu câu lặp lại nhiều. Ví dụ "X, hôm qua thì đỡ hẳn
  rồi" chiếm phần lớn báo nhầm của vòng 3 bản đầu.
- Còn yếu: `ban_cu_con_hieu_luc` (0,31 trên tập giữ kín). Lần cấy nào cũng có cảnh báo, nhưng cảnh báo rơi vào nhóm
  trùng lặp hoặc thời gian, không vào STATE_UPDATE. `gia_dinh_thanh_that` cũng mới đạt 0,42.

## Lỗi KHÓ (25/11/2026 tối) — đo độ khó và dữ liệu cho lần train sau

`tools/cay_loi_kho.py` thêm 14 loại lỗi tinh vi. Lỗi được cấy thẳng vào đáp án; **lời trích dẫn giữ nguyên**, nên
nhìn qua vẫn thấy hợp lý.

**Phép đo:** `python -m src.do_cay_loi --tap dieu_chinh --kho`, trên 400 ca điều chỉnh, luật đã khoá. Bắt đúng nhóm:

| Loại lỗi khó | Ví dụ | n | Luật bắt đúng |
|---|---|---:|---:|
| `qua_khu_hien_tai` | "từng hút thuốc" ghi thành đang hút | 337 | **0,012** |
| `dinh_chinh_nguoc` | người bệnh đính chính "4 ngày", bản ghi giữ "3 ngày" | 33 | **0,000** |
| `doi_ben` | hố chậu phải → trái | 260 | **0,250** |
| `doi_muc_do` | âm ỉ → dữ dội, nhẹ → nặng | 330 | **0,500** |
| `nguoi_nha_thanh_benh_nhan` | bệnh của mẹ ghi thành của người bệnh | 149 | 0,577 |
| `phu_dinh_trong_chuoi` | "không ho, nhưng hơi khó thở" → ghi "ho" | 9 | 0,667 |
| `thuoc_gan_giong` | ceftriaxone → cefepime | 247 | 0,858 |
| `bo_tu_nghi` | "có thể viêm ruột thừa" → chắc chắn | 160 | 0,875 |
| `doi_tan_suat` | ngày một lần → hai lần | 163 | 0,939 |
| `so_lech_nho` | 38,5 → 39,5 | 261 | 0,946 |
| `doi_don_vi_thoi_gian` | 2 tháng → 2 tuần | 252 | 0,956 |
| `bia_phu_dinh` | thêm "không co giật" không ai hỏi | 400 | 0,973 |
| `bo_dieu_kien` | bỏ "nếu đau tăng" | 46 | 1,000 |
| `gan_nham_luot` | dẫn sang lượt bên cạnh | 355 | 1,000 |
| **Trung bình** | | | **0,682** (bộ cơ bản: 0,871) |

Bốn loại đầu là **điểm mù thật của bộ luật**. Cần làm luật mới hoặc để mô hình tự tránh.

**Dữ liệu huấn luyện:** `data/cay_loi/cap_loi_kho_train.jsonl` (không commit, sinh lại được bằng
`python -m tools.cay_loi_kho`, hạt 42).

- SHA-256 `16edc40479a71c923ae6927d0e6884f845a610cbc058ba515a926fa3c847cc43`.
- 10.729 cặp từ 3.925 ca **train**. Mỗi ca ba biến thể, lần lượt 1, 2 và 3 lỗi.
- Mỗi dòng gồm `{id, chosen, rejected, loi: [{loai, chi_so, chi_so_ra, mo_ta}], bien_the}`.
- `chosen` và `rejected` cùng định dạng đầu ra của `du_lieu_trich`. Lời nhắc lấy từ `data/trich_train_v2.jsonl`
  theo `id`.
- Dùng được cho DPO (bản đúng / bản lỗi), hoặc để dạy một bộ kiểm tra tìm lỗi. `chi_so_ra` trỏ đúng dòng lỗi trong
  `rejected`.
- Không có ca nào từ tập giữ kín hay tập kiểm tra cuối.
- Giới hạn: lỗi sinh bằng luật nên vẫn có mẫu lặp. Số loại không đều: `phu_dinh_trong_chuoi` hiếm vì dữ liệu sinh ít
  có câu kiểu "không X, nhưng Y".

## Vòng 6 (26/11/2026): vá 4 điểm mù lỗi khó

Đo trên tập điều chỉnh (400 ca, hạt 42). **Không chạy lại tập giữ kín**: tập đó đã dùng một lần, và các luật vòng 6
được chọn ngưỡng trên tập điều chỉnh. Con số dưới đây vì vậy là số **lạc quan**.

| Loại lỗi khó | Trước | Sau | Wilson 95% (sau) | Luật thêm |
|---|---:|---:|---|---|
| `doi_ben` | 0,250 | **0,950** | [0,916; 0,971] | `than_the`: từ chỉ bên (trái/phải/trên/dưới) trong bản ghi không có ở lượt dẫn, từ ngược lại có |
| `doi_muc_do` | 0,500 | **0,970** | [0,945; 0,983] | `than_the`: cặp trái nghĩa (âm ỉ/dữ dội, nhẹ/nặng, tăng/giảm, ít/nhiều, hơi/rất) so với cả lượt dẫn |
| `qua_khu_hien_tai` | 0,012 | **0,730** | [0,680; 0,775] | `thoi_diem._thoi_khong_khop`: đối chiếu `thoi_gian_su_kien` với câu hỏi bác sĩ ngay trước ("trước giờ", "bệnh nền", "tiền sử"…) và mốc thời gian |
| `dinh_chinh_nguoc` | 0,000 | **1,000** | [0,896; 1,000] | `toan_ca.dinh_chinh_nguoc`: dòng còn hiệu lực giữ giá trị nằm sau "không phải"/trước "à nhầm", hoặc dòng bị thay thế tự khai là đính chính |
| **Trung bình 14 loại** | 0,682 | **0,889** | | |

Rào chắn (đều đạt):

- Báo nhầm trên bản sạch: 7,110 → 7,112 mỗi ca (ngưỡng +0,02).
- Bộ lỗi cơ bản: độ nhạy trung bình giữ 0,871.
- Lọt nguy hiểm trên `data/thach_thuc`: C 98 → 98, D 94 → 93.
- Chặn thừa giữ nguyên. Jaccard 0,885. Bộ phép thử 1.729 qua, 27 bỏ qua.

Giới hạn:

- `qua_khu_hien_tai` chỉ đổi một trường siêu dữ liệu, nội dung giữ nguyên. Luật chỉ đoán được qua câu hỏi của bác sĩ
  và mốc thời gian. `PAST_CURRENT_CONFUSION` vẫn báo trên 0,185 dòng mỗi ca sạch (chủ yếu là luật cũ).
- `CORRECTION_NOT_APPLIED` báo trên **cả hai** dòng của cặp, nên precision theo dòng là 0,49 dù cặp nào cũng đúng.
- Bản đầu của luật quá khứ/hiện tại báo nhầm 17 dòng trên bản sạch ("từng đợt", "tiêu chảy mạn tính", "bệnh nền").
  Đã siết còn 1 trước khi đo lần cuối.

Kết quả chi tiết: `cay-loi-kho-vong6.json` (lỗi khó), `cay-loi-vong6.json` (lỗi cơ bản).
