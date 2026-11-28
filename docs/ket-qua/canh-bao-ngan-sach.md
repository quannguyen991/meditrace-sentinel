# Ngân sách cảnh báo và dọn mã vô dụng (MT5, 28/11/2026)

Plan: Task 5 trong `docs/superpowers/plans/2026-11-27-nang-cap-toan-dien-bgk.md`, V11 trong
`docs/superpowers/plans/2026-11-28-kich-ban-nang-cap-v2.md`. Chỉ chạy CPU. Không mở `viet_kiem_tra_cuoi*`, không chạy
lại tập giữ kín, không chạy lại 240 ca đáp án đã dùng.

**MT5 KHÔNG ĐẠT.**

| | Đo được | Ngưỡng |
|---|---:|---:|
| Cảnh báo hiển thị mỗi ca sạch | 3,87 | ≤ 2,0 |
| Độ nhạy hiển thị | 0,801 | ≥ 0,85 |

Chính sách D giữ nguyên: lọt nguy hiểm 26/220 = 11,8%, chặn thừa 10,0%.

## Đã đổi gì

1. **Hàm ngân sách** `gop.chon_hien_thi(ds, ngan_sach=2) -> (hien, gap)`.
   - Mỗi mệnh đề hiện tối đa 2 cảnh báo. Cảnh báo toàn ca (bỏ sót) là một nhóm riêng, ngân sách cũng là 2.
   - **Luôn hiện**, kể cả khi vượt ngân sách: mức `cao`, kết luận `loi_phat_hien`, mã `LUON_CAO`.
   - **Luôn gập**: mã gợi ý (mục 2) và cảnh báo `can_xem` của bộ phát hiện thử nghiệm.
   - Thứ tự sắp: mức → kết luận → độ chính xác cùng loại đã đo → ưu tiên → mã → lượt.
2. **Mã gợi ý** (`loai.MA_GOI_Y_CHINH_XAC_THAP`). Tiêu chí: báo ≥ 20 lần, độ chính xác cùng loại < 0,10 trong
   `canh-bao.json`, và không thuộc `LUON_CAO`. Có ba mã:

   | Mã | Số lần báo | Độ chính xác cùng loại |
   |---|---:|---:|
   | `SPEAKER_SUBJECT_MISMATCH` | 382 | 0,058 |
   | `DUPLICATE_INFORMATION` | 108 | 0,056 |
   | `IMPORTANT_MODIFIER_DROPPED` | 84 | 0,000 |

   Ba mã này bị hạ xuống `thap`, không chặn theo chính sách D và luôn bị gập.

   Có hai ngoại lệ:
   - Kết luận là `loi_phat_hien`.
   - Loại thông tin là dị ứng hoặc thuốc (`loai.LOAI_GOI_Y_VAN_CHAN` = `di_ung`, `thuoc`, `thuoc_nti`). Ở đây mã vẫn
     chặn D. Vì cảnh báo đã đổi trạng thái thì không được gập, nên nó **vẫn hiện**.

   Ngoại lệ này lấy theo quyết định 28/11 sau phép đo ở cuối tệp.
3. **API.** Mỗi `theo_phat_bieu[id]` có thêm `canh_bao_hien` và `canh_bao_gap`. Cả ca có thêm `toan_ca_ngan_sach` và
   `ngan_sach`. Bản ghi lưu từ trước được bổ sung trong `_them_canh_bao`. Các trường cũ giữ nguyên.
4. **BFF.** `web/may-chu/routes/asr.ts` ánh xạ các trường trên thành `warningsShown`, `warningsFolded`,
   `caseWarningsShown` và `caseWarningsFolded`.
5. **Giao diện.** `VerificationView` chỉ hiện phần `hien`. Phần gập nằm sau nút "Xem thêm N gợi ý". Thiếu trường thì
   hiển thị như cũ.

## MT5 trên 400 ca cấy lỗi (tập điều chỉnh, hạt 42)

Lệnh: `PYTHONUTF8=1 python -m tools.do_canh_bao_hien_thi --ra-json docs/ket-qua/canh-bao-ngan-sach-cay-loi.json`.

### Đường cơ sở đã tăng từ 7,11 lên 11,55 cảnh báo mỗi ca sạch

Đo lại trên mã hiện tại, mỗi ca sạch có **11,55** cảnh báo. Con số 7,11 trong `cay-loi.md` là đo ngày 25/11 (vòng 6,
`cay-loi-vong6.json`). Độ nhạy trung bình không đổi, vẫn 0,871.

So từng mã giữa hai lần đo:

| Mã | Vòng 6 | Hôm nay | Tăng |
|---|---:|---:|---:|
| `POSSIBLE_IMPORTANT_OMISSION` | 1.564 | 3.368 | **+1.804** (4,5 mỗi ca) |
| `WRONG_SUBJECT` | 6 | 59 | +53 |
| Các mã khác | | | gần như không đổi |

Phần tăng gần như toàn bộ là cảnh báo bỏ sót chung chung ở mức toàn ca, do các thay đổi trong lớp bỏ sót sau vòng 6. Mình
không truy được từng commit gây ra.

### Kết quả chính

| Cách đếm | Cảnh báo mỗi ca sạch | Độ nhạy hiển thị trung bình |
|---|---:|---:|
| Mọi cảnh báo (cách đếm của `cay-loi.md`) | 11,55 | 0,871 |
| Giao diện cũ: cảnh báo chính, tối đa 2 cảnh báo khác nhóm, cảnh báo toàn ca khác `can_xem` | 2,33 | 0,772 |
| **Ngân sách 2 (bản cuối)** | **3,87** | **0,801** |
| Ngưỡng MT5 | ≤ 2,0 | ≥ 0,85 |

So với giao diện cũ, ngân sách hiện thêm 1,5 cảnh báo mỗi ca và độ nhạy cao hơn 0,03.

Phần dư chủ yếu là `POSSIBLE_IMPORTANT_OMISSION`, khoảng 1,65 lần mỗi ca sạch. Giao diện cũ bỏ mã này (`can_xem`) khỏi
khung bỏ sót. Ngân sách thì giữ nó, vì nó lấp chỗ trống trong nhóm toàn ca.

Ngoại lệ dị ứng/thuốc làm hiện thêm khoảng 0,15 cảnh báo mỗi ca: 3,72 khi gập cả trên dị ứng/thuốc, 3,87 khi giữ ngoại
lệ. Mình **không** chỉnh thêm luật sau khi xem kết quả.

### Độ nhạy hiển thị theo loại lỗi

| Loại lỗi cấy | n | Mọi cảnh báo | Giao diện cũ | Ngân sách |
|---|---:|---:|---:|---:|
| `doi_chu_the` | 400 | 0,945 | 0,932 | 0,892 |
| `dao_phu_dinh` | 400 | 0,695 | 0,690 | 0,695 |
| `nang_chac_chan` | 160 | 0,881 | 0,881 | 0,881 |
| `gia_dinh_thanh_that` | 400 | 0,448 | 0,448 | 0,448 |
| `ban_cu_con_hieu_luc` | 56 | 0,482 | 0,482 | 0,482 |
| `doi_lieu` | 19 | 0,789 | 0,789 | 0,789 |
| `doi_so` | 270 | 0,900 | 0,878 | 0,900 |
| `doi_thuoc` | 247 | 0,996 | 0,996 | 0,996 |
| `doi_thoi_gian` | 345 | 0,916 | 0,826 | 0,916 |
| `bia_menh_de` | 400 | 1,000 | 1,000 | 1,000 |
| `bia_trich_dan` | 400 | 1,000 | 0,998 | 1,000 |
| `doi_bang_chung` | 400 | 1,000 | 0,465 | 0,818 |
| `xoa_di_ung` | 118 | 0,983 | 0,907 | 0,907 |
| `xoa_thuoc` | 276 | 0,960 | 0,928 | 0,946 |
| `xoa_phu_dinh` | 181 | 1,000 | 0,425 | **0,453** |
| `xoa_so_lieu` | 270 | 0,948 | 0,711 | **0,696** |

Nhóm lỗi nguy hiểm:
- Đổi thuốc (0,996) và đổi liều (0,789) giữ nguyên.
- Xoá dị ứng giảm từ 0,983 xuống 0,907, bằng giao diện cũ.
- Đổi chủ thể giảm 0,05, vì `SPEAKER_SUBJECT_MISMATCH` trên thông tin thường nay bị gập.

Xoá phủ định và xoá số liệu chủ yếu chỉ được bắt bằng cảnh báo bỏ sót chung chung, nên hiển thị thấp.

## Chính sách D (4 bộ `thach_thuc/*_phat_trien`)

Lệnh: `PYTHONUTF8=1 python -m src.do_luong.do_canh_bao --ra-json docs/ket-qua/canh-bao-ngan-sach.json`.

| | Trước | Hạ cả trên dị ứng/thuốc (đã bỏ) | **Bản cuối (giữ chặn dị ứng/thuốc)** |
|---|---:|---:|---:|
| D: lỗi nguy hiểm lọt vào thân | 26/220 = 11,8% | 53/220 = 24,1% | **26/220 = 11,8%** |
| D: chặn thừa | 202 = 10,0% | 145 = 7,2% | **202 = 10,0%** |
| D: chặn thừa trên bản sạch (cấy lỗi) | 8,8% | 7,2% | 8,8% |
| C (mặc định sản phẩm) | 45,9% | không đổi | không đổi |

Cả 89 lần `SPEAKER_SUBJECT_MISMATCH` đổi trạng thái đều rơi vào dị ứng hoặc thuốc. Nếu hạ cả ở hai loại này, D lọt thêm
27 lỗi nguy hiểm, đổi lại bớt 57 lần chặn thừa. Vì vậy mình giữ ngoại lệ. Phép thử:
`test_ma_goi_y_van_chan_D_tren_di_ung_va_thuoc`.

## Giới hạn

- Mọi số đo là trên lỗi cấy nhân tạo. Bản sạch là đáp án, nên một cảnh báo hợp lý vẫn bị tính là báo nhầm.
- Bảng độ chính xác dùng để xếp thứ tự lấy từ cùng tập phát triển đã nhìn (24/09).
- Chưa kiểm trên trình duyệt. Giao diện chỉ nhận trường mới nếu `App.tsx` chuyển nguyên phản hồi BFF vào `NoteMeta`.
  Mình không đọc hay sửa `App.tsx` để xác nhận điều này.
