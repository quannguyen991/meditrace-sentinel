# Bàn giao: mở rộng câu, sinh thêm dữ liệu v2, giảm độ lặp

Viết ngày 21/11/2026 cho mô hình hoặc người nhận việc tiếp. Đọc hết trang này trước khi sửa. Tài liệu đi kèm: `docs/superpowers/plans/2026-11-21-nang-cap-toan-dien-meditrace.md` (kế hoạch đầy đủ, các Task B3, B4, F0–F5), `docs/tien-do-21-11-2026.md` (số đo và việc đã làm), `docs/do-lap-cau-nguon.md` (câu lặp đến từ đâu), `docs/khuon-mo-rong-danh-sach.md` (50 khuôn đề xuất).

Người làm dự án nói tiếng Việt. Trả lời và viết tài liệu bằng tiếng Việt, không ẩn dụ, giải thích mọi thuật ngữ ở lần đầu.

---

## 1. Việc cần làm

1. **Mở rộng câu (Task B3):** thêm biến thể cho các nhóm câu lặp nhiều nhất trong bộ sinh luật, để cùng một ý có nhiều cách nói.
2. **Sinh thêm dữ liệu (Task B4, F1–F5):** tạo bộ v2 (5.000 ca) với khuôn bệnh, tình huống và kịch bản mới. **Mục tiêu khuôn (người dùng chốt 21/11/2026): tổng 600 khuôn = 200 khuôn cũ + hai đợt viết mới, mỗi đợt 200 khuôn** (khuôn 201–400 rồi 401–600). *Cách hiểu suy từ "mỗi đợt 200 khuôn, tổng 3 đợt 600 khuôn"; nếu người dùng muốn ba đợt mới (tổng 800) thì hỏi lại.* Mục tiêu đi kèm là đa dạng loại bệnh hơn: mỗi khuôn có thêm trường `he_co_quan`; không hệ nào chiếm quá 12% tổng số khuôn và có ít nhất 18 hệ (phép thử `test_da_dang_he_co_quan`). Viết theo lô 50 khuôn, người dùng đọc mẫu sau mỗi lô. Đã có 50 tên đề xuất ở `docs/khuon-mo-rong-danh-sach.md` làm lô đầu; **các lô sau chưa có tên**, phải đề xuất từng lô và chờ người dùng duyệt trước khi viết nội dung.
3. **Độ lặp mục tiêu 30%:** người dùng đặt mục tiêu tỷ lệ lặp câu **≤ 30%** ở bộ v2 (ngày 21/11/2026; trước đó là 20%, đã nới theo yêu cầu). Xem mục 4: ở mức "mọi câu" mục tiêu này vẫn khó; phải đo và báo thật, không được "lách" chỉ số.
4. **Khắc phục độ lặp của bộ cũ:** bộ cũ (`data/hoi_thoai_viet_5000.jsonl`) lặp 76,92%. **Không sửa bộ cũ** (xem mục 3). "Khắc phục" nghĩa là tạo bộ v2 thay thế và so sánh trước sau.

Không nằm trong bàn giao này: huấn luyện lại mô hình, chạy gì trên HoaiĐức, gán nhãn dữ liệu ngoài (VietMed), hàng đợi web. Những việc đó có kế hoạch riêng.

## 2. Hiện trạng đã đo (bộ cũ, 5.000 ca)

Công cụ: `python -m src.do_luong.do_lap_cau data/hoi_thoai_viet_5000.jsonl` (chạy bằng `D:\khkt-venv-lap\Scripts\python`, đặt `PYTHONUTF8=1`).

Định nghĩa "câu" = một lượt nói sau khi bỏ phần ghi người nói (`Bác sĩ:`…), chuẩn hoá NFC, chữ thường.

| Chỉ số | Giá trị |
|---|---|
| Số câu / số câu duy nhất | 87.473 / 20.190 |
| Tỷ lệ lặp (mọi câu) | 76,92% |
| Tỷ lệ lặp, câu từ 4 từ trở lên | 76,20% |
| Tỷ lệ lặp, câu từ 6 từ trở lên | 74,50% |
| Tỷ lệ lặp, **câu từ 8 từ trở lên** | **69,24%** |
| TTR (tỷ lệ từ khác nhau trên tổng số từ) | 0,0023 |
| MTLD (độ đa dạng từ vựng ít lệ thuộc độ dài) | 93,0 |
| Distinct-2 (tỷ lệ cặp từ liền nhau khác nhau) | 0,0188 |

Bản bàn giao 20/11 ghi 76,3% (87.265 câu, 20.652 duy nhất). Đo lại ra 76,92%, lệch 0,6 điểm phần trăm vì cách chuẩn hoá khác nhẹ. Phép thử `tests/test_do_lap_cau.py::test_bo_cu_ty_le_lap_khoang_0_763` cho phép sai số 1 điểm.

### Câu lặp đến từ đâu (`docs/do-lap-cau-nguon.md`, 67.283 lần lặp)

- **Câu hỏi khai thác của bác sĩ** (hỏi dị ứng, thuốc, "còn gì nữa không"): khoảng 41% không quy được về một nhóm cụ thể; mỗi câu lặp 130–170 lần. Là các nhóm `HOI_DI_UNG`, `HOI_THUOC`, `HOI_THEM`, `HOI_TIEN_SU`, `HOI_GIA_DINH`, `HOI_THOI_GIAN` trong `src/bo_du_lieu/ngu_lieu_viet.py` kèm biến thể có hoặc không có "ạ".
- **Câu trả lời ngắn và câu chào cuối** (`XA_GIAO` 8,3%, `MIEN.*.chao_cuoi` khoảng 7,7%): "Dạ, cảm ơn bác sĩ ạ." lặp 1.055 lần, "Dạ, không." 802 lần.
- **Mô tả khám, chẩn đoán, kế hoạch của từng khuôn** (`BENH[i]["kham"]`, `["chan_doan"]`, `["ke_hoach"]`): khoảng 17,5%. Mỗi khuôn chỉ có **một** câu cho mỗi mục, dùng lại ở mọi ca của khuôn đó (khoảng 25 ca mỗi khuôn).
- **Câu ghép bằng f-string** trong `src/bo_du_lieu/sinh_hoi_thoai_viet.py` (khoảng 25%): các dòng chính là 681, 860, 604, 614, 1128, 615, 556, 735. Ví dụ `f"{_hoa(ca.goi_bn)} đi khám cho mình phải không ạ?"` ở dòng 604, chỉ khác nhau ở cách gọi (anh, chị, em, chú, cô, bác, bà).

Chạy `python -m src.do_luong.nguon_lap_cau data/hoi_thoai_viet_5000.jsonl --ra <tệp>.md` để xem lại bảng này.

## 3. Ràng buộc bắt buộc

1. **Không sửa bộ cũ** và các tệp đóng băng: `data/hoi_thoai_viet_5000.jsonl`, `data/viet_train.jsonl`, `data/viet_phat_trien.jsonl`, `data/viet_kiem_tra_cuoi.jsonl`, `data/trich_train.jsonl`, `data/trich_giu_lai.jsonl`, và manifest `data-rieng-tu/ket-qua/manifest/dong-bang-5000.json`. Đổi dữ liệu cũ làm hỏng checkpoint đã huấn luyện và làm lộ tập kiểm tra.
2. **Bộ sinh cũ phải giữ nguyên từng bit khi cờ mở rộng tắt.** Phép thử vàng `tests/test_bo_sinh_goc_khong_doi.py` (băm SHA-256 của `sinh_bo(200, seed=42)` = `2bedc64168fe45dd…`, và danh sách 26 khuôn phát triển, 24 khuôn kiểm tra) phải PASS trước và sau mọi sửa đổi. Mọi tính năng mới nằm sau cờ `mo_rong`, mặc định tắt.
3. **Cách chia 200 khuôn cũ không được đổi.** `tach_tap_viet.phan_khuon` hiện xếp mọi khuôn ngoài 100 khuôn đầu vào cùng một nhóm và xếp hạng bằng băm. Thêm khuôn thẳng vào `nl.BENH` sẽ làm xáo trộn tập phát triển và tập kiểm tra đã đóng băng. Khuôn mới phải đi vào một nhóm riêng (Task F2) và để trong `src/bo_du_lieu/khuon_mo_rong.py`, không thêm vào `nl.BENH` (phép thử `test_du_200_khuon` yêu cầu đúng 200).
4. **Nhãn không được đổi nghĩa khi đổi cách nói.** Mệnh đề trong `dap_an` (chủ thể, phủ định, thời gian, thuốc, liều, độ chắc chắn) phải giống hệt dù câu viết khác. Mọi `trich_dan` phải là chuỗi con nguyên văn của `input` (phép thử `test_trich_dan_la_chuoi_con_cua_input` ở Task B3). Phần "bẫy" như đính chính, mâu thuẫn, người nhà kể hộ đang dựa vào việc `luot_goc` (lời thoại trước các tầng ngôn ngữ) khớp từng chỉ số với `luot`; đừng làm lệch hai danh sách này.
5. **Dùng luồng số ngẫu nhiên riêng cho mỗi tầng mới.** Bộ sinh đã làm vậy: `_Soan.__init__` rút `hat = rng.getrandbits(48)` đúng một lần rồi tạo `rng_vung = Random(2*hat+1)` và `rng_ngu_vuc = Random(2*hat+2)` (`src/bo_du_lieu/sinh_hoi_thoai_viet.py:355-357`). Tầng mới thêm `Random(2*hat+3)` để bật hay tắt nó không làm lệch nội dung các tầng còn lại. Đừng gọi `self.rng` thêm lần nào khi cờ tắt.
6. **Không dùng mô hình thương mại hay dữ liệu do GPT sinh** làm dữ liệu huấn luyện. Biến thể câu mới phải do bạn viết tay hoặc do luật sinh. Ghi vào đầu mỗi nhóm câu mới là "do AI viết, chưa bác sĩ duyệt" (quyết định D1 còn mở).
7. **Không sửa tệp tiếng Việt bằng PowerShell `Get-Content`/`Set-Content`** (hỏng dấu). Dùng công cụ sửa tệp hoặc Python có `encoding="utf-8"`. Heredoc Bash nuốt dấu `\`, nên chuỗi có `\n` phải dùng công cụ sửa tệp. In tiếng Việt ra console Windows cần `PYTHONUTF8=1` hoặc `sys.stdout.reconfigure(encoding="utf-8")`.
8. **Môi trường:** chạy kiểm thử bằng `D:\khkt-venv-lap\Scripts\python -m pytest tests/ -q` trong `D:\Claude\meditrace-ma-nguon`. Không cài thêm gói vào môi trường này. Không chạy gì trên HoaiĐức (`100.108.54.12`) khi chưa hỏi người dùng. Không ghi vào ổ E. Không commit git (kho này không có `.git`). Không tải tệp mới khi chưa được duyệt.
9. **Không in nội dung khoá** trong `D:\Claude\.secrets\`.

## 4. Về mục tiêu lặp 30% (đọc kỹ)

**Vấn đề:** tổng 87.473 câu. Để lặp ≤ 30% cần ít nhất khoảng **61.200 câu khác nhau** (70% của 87.473), trong khi bộ cũ chỉ có 20.190, tức gấp khoảng 3 lần. Ở chỉ số "câu từ 8 từ trở lên" (57.314 câu) cần khoảng 40.100 câu khác nhau, bộ cũ có 17.632, gấp khoảng 2,3 lần. Trong hội thoại khám bệnh có nhiều câu ngắn lặp một cách tự nhiên ("Dạ", "Vâng ạ", "Dạ, không."). Thêm vài chục biến thể cho mỗi nhóm câu không đủ: ví dụ 150 câu hỏi cơ bản nhân với 8 mở đầu và 4 đuôi chỉ cho ra khoảng 4.800 biến thể, trong khi bộ cần thêm hàng chục nghìn câu khác nhau. Có hai cách làm bộ đạt được con số đó: (a) tăng số câu khác nhau như các cách ở dưới, (b) bớt các lượt thoại ngắn lặp hoặc rút ngắn hội thoại. Cách (b) làm đổi phân bố của bộ; người dùng đã cho phép dùng **sau khi** cách (a) đã làm hết mức mà vẫn chưa đạt (21/11/2026).

**Đối chiếu dữ liệu thật:** VietMed chép lời (9.122 đoạn) có tỷ lệ lặp 0,03%. Số này **không so trực tiếp được**: mỗi đoạn là một lát cắt khoảng 5 giây của ghi âm dài, không phải một lượt thoại trọn vẹn.

**Cách đo (đã chốt ngưỡng chính là mọi câu):** báo cáo ba chỉ số cạnh nhau, không chỉ một:
- tỷ lệ lặp mọi câu (**mục tiêu chính, người dùng chốt: ≤ 30%**);
- tỷ lệ lặp **câu từ 8 từ trở lên** (hiện 69,24%): chỉ báo cáo kèm theo, không còn là ngưỡng chính;
- Distinct-2 và MTLD, so với bộ cũ.

**Cách làm để thật sự giảm lặp (thứ tự ưu tiên theo ảnh hưởng, lấy từ bảng nguồn lặp):**
1. **Nhóm `HOI_*` (câu hỏi bác sĩ), khoảng 41%.** Chuyển từ danh sách cố định sang ghép nhiều tầng: lời dẫn (không có, "Vậy", "Cho tôi hỏi thêm," …) × lõi câu hỏi × đuôi. Vẫn giữ nghĩa câu hỏi.
2. **Mô tả khám, chẩn đoán, kế hoạch theo khuôn (17,5%).** Mỗi khuôn cần nhiều cách diễn đạt cho mỗi mục (đề xuất ít nhất 6), nhưng cùng nội dung y khoa. Việc này viết tay và cần bác sĩ duyệt; đánh dấu `da_duyet = False`.
3. **Câu f-string (25%).** Thay cách gọi, xưng hô, câu mở đầu bằng nhiều dạng hơn (theo vùng miền và quan hệ người nói).
4. **Câu trả lời ngắn và câu chào (khoảng 16%).** Mở rộng, nhưng chấp nhận một phần lặp là tự nhiên.

**Cấm lách chỉ số:** không được làm câu "khác nhau" bằng cách thêm số ngẫu nhiên, mã, từ vô nghĩa, hay đảo thứ tự từ vô ý nghĩa. Mỗi biến thể phải là một câu tiếng Việt tự nhiên mà bác sĩ đọc không thấy lạ. Phải đọc mẫu `data/v2_mo_rong_mau_duyet.md` (50 ca) để kiểm.

**Thứ tự bắt buộc và điều kiện dừng:**
1. Làm cách (a) tối đa hai vòng "đo nguồn lặp → thêm biến thể".
2. Nếu tỷ lệ lặp mọi câu vẫn trên 30%, mới được dùng cách (b), với ba giới hạn: (i) chỉ bỏ hoặc rút lượt thoại **không mang nhãn** (không nằm trong `luot` của mệnh đề nào, và không phải câu hỏi mà một câu trả lời tắt cần để làm bằng chứng, xem `kem_cau_hoi` trong `_Soan.ghi`); (ii) mỗi hội thoại còn ít nhất một lượt hỏi và một lượt đáp cho mỗi mệnh đề; (iii) ghi vào báo cáo số lượt đã bỏ, loại lượt nào, và độ dài hội thoại trước và sau.
3. Nếu sau (a) và (b) tỷ lệ lặp vẫn trên 30%, **dừng và báo** số thật; không tiếp tục lách.

## 5. Các việc, thứ tự, và tiêu chí xong

Chi tiết từng bước, chữ ký hàm và phép thử nằm trong kế hoạch. Tóm tắt thứ tự:

| # | Việc | Tiêu chí xong |
|---|---|---|
| 1 | Chạy lại `pytest tests/test_bo_sinh_goc_khong_doi.py tests/test_mo_rong_bo_du_lieu.py tests/test_do_lap_cau.py tests/test_nguon_lap_cau.py -q` | 4 tệp đều PASS (đường cơ sở) |
| 2 | **B3**: thêm biến thể cho nhóm đứng đầu bảng nguồn lặp, sau cờ `mo_rong` (tầng mới có luồng số riêng, mục 3.5) | Phép thử vàng vẫn PASS; `test_trich_dan_la_chuoi_con_cua_input` và `test_moi_menh_de_co_du_truong_nhan` PASS ở bộ mới; số đo trước và sau ghi vào `docs/tien-do-21-11-2026.md` |
| 3 | **F1**, hai đợt 200 khuôn mới, viết theo lô 50 (sau khi người dùng duyệt danh sách tên của lô đó) | Mỗi đợt: 200 khuôn trong `src/bo_du_lieu/khuon_mo_rong.py` (`DOT[1]`, `DOT[2]`), `da_duyet = False`, `tests/test_khuon_mo_rong.py` PASS; người dùng đọc mẫu sau mỗi lô 50; tổng cuối 400 khuôn mới (600 khuôn cả thảy) |
| 4 | **F2**: nhóm khuôn mở rộng trong `phan_khuon`, **mỗi đợt 200 khuôn là một nhóm chia độc lập** | 200 khuôn cũ giữ đúng tập (phép thử vàng); mỗi đợt chia 160/20/20; thêm đợt sau không làm đổi tập của đợt trước |
| 5 | **F3, F4**: ba tình huống và ba kịch bản mới | Chỉ làm khi người dùng chốt nghĩa nhãn (xem plan, F3 Step 1 và F4 Step 1). Không tự đặt nghĩa nhãn |
| 6 | **B4, F5**: sinh `data/hoi_thoai_viet_v2_mo_rong.jsonl` (5.000 ca, seed khác 42, ví dụ 2611) và manifest riêng | Không trùng mã ca hay văn bản với bộ cũ; báo ba chỉ số của mục 4; xuất `data/v2_mo_rong_mau_duyet.md` |
| 7 | Báo cáo | Ghi vào `docs/tien-do-21-11-2026.md`: số trước và sau, kết quả bất lợi ngang hàng, việc chưa xong |

## 6. Công cụ đã có

| Tệp | Làm gì |
|---|---|
| `src/do_luong/do_lap_cau.py` | `do_lap_cau(cac_ca) -> dict` (lặp câu, TTR, MTLD, distinct-2, top câu lặp), `doc_jsonl(duong_dan)`, `tach_cau(input)` |
| `src/do_luong/nguon_lap_cau.py` | `bang_nguon_lap(cac_ca)` và `phan_loai_nguon(cau)`: gán câu lặp cho nhóm câu, hằng chuỗi cố định, hay f-string (kèm số dòng) |
| `src/huan_luyen/loss_theo_doan.py` | Không liên quan việc này (dùng cho huấn luyện) |
| `tests/test_bo_sinh_goc_khong_doi.py` | Phép thử vàng |
| `tests/test_mo_rong_bo_du_lieu.py` | Kiểm 200 khuôn, bể nội dung người nhà, cách chia tập |

Cấu trúc bộ sinh (`src/bo_du_lieu/sinh_hoi_thoai_viet.py`, đọc trước khi sửa):
- `sinh_bo(so_ca, seed=42) -> List[dict]`: bộ sinh chính. Mỗi bản ghi có `id`, `input` (hội thoại, mỗi dòng một lượt, đầu dòng ghi người nói), `output`, `bay`, `so_luot`, `benh`, `dap_an` (danh sách mệnh đề), v.v.
- `_Soan.noi(vai, cau, cau_goc)`: mọi lượt thoại đi qua đây. `bs()` ghi lượt bác sĩ, `ke()` ghi lượt bệnh nhân và người nhà (có hai tầng ngôn ngữ riêng: `loi_dan_thuong` và `phuong_ngu`, mỗi tầng một luồng số ngẫu nhiên).
- `MenhDe` (dòng 195): đáp án gốc. Các khoá quan trọng: `chu_the`, `noi_dung`, `muc`, `phu_dinh`, `tinh_huong` (thực tế | giả định | kế hoạch), `do_chac_chan` (chắc chắn | nghi ngờ | chưa ghi nhận), `thoi_gian_su_kien`, `quan_he`, `trang_thai`, `thuoc`, `luot`.
- `BAY` (dòng 51): 14 kịch bản hiện có. `BAY_RUT` là phần rút ngẫu nhiên; `nguoi_ke_benh_minh`, `nguon_khac_nhau`, `lieu_dinh_chinh` bật riêng. Thêm vào `BAY_RUT` làm loãng tỷ lệ các bẫy cũ (xem chú thích ở đầu `sinh_hoi_thoai_viet.py`), nên bẫy mới phải bật riêng sau cờ.
- `BOI_CANH` (dòng 162): 5 tình huống hiện có, kèm `TRONG_SO_BOI_CANH`.

Nhóm câu nằm ở `src/bo_du_lieu/ngu_lieu_viet.py`: `BENH` (200 khuôn), `MIEN` (3 vùng, trong đó có `chao_cuoi`, `ket`, `de_nghi`, `da_vang`), `XA_GIAO`, `MO_DAU`, `MO_DAU_NGUOI_NHA`, `HOI_*`, `CHUYEN_KHAM`, `DAN_DO`, `BAC_SI_TIEP_LOI`.

## 7. Điều còn mở (hỏi người dùng, đừng tự quyết)

1. ~~Chốt mục tiêu lặp~~ **Đã chốt (21/11/2026):** tỷ lệ lặp **mọi câu ≤ 30%**. Hệ quả: câu trả lời ngắn và câu chào cũng phải đa dạng hơn, vì chúng chiếm một phần lớn số câu lặp. **Đã cho phép (21/11/2026)** dùng cách (b) ở mục 4 (bớt lượt thoại ngắn lặp hoặc rút ngắn hội thoại) **chỉ khi cách (a) không đủ**: phải làm cách (a) trước, đo, ghi số, rồi mới dùng (b) cho phần còn thiếu, và ghi rõ trong báo cáo (b) đã đổi gì (số lượt bỏ, loại lượt nào, độ dài hội thoại trước sau).
2. Duyệt tên khuôn **từng lô 50** (lô đầu: danh sách ở `docs/khuon-mo-rong-danh-sach.md`, các lô sau chưa có); có giữ các khuôn chỉ một giới (đợt 1: số 20, 41–45) không (cần sửa `_hop_gioi`, dùng `CHI_NU` riêng).
3. Nghĩa nhãn của 3 tình huống và 3 kịch bản mới (`tinh_huong` là `"giả định"` hay `"kế hoạch"` cho câu điều kiện "nếu sốt thì uống thuốc").
4. Ai duyệt nội dung y khoa AI viết (D1). Trước khi có duyệt, mọi thứ mới mang `da_duyet = False` và không được trình bày như nội dung y khoa đã thẩm định.

## 8. Chuyển giao kết quả

Khi xong, ghi vào `docs/tien-do-21-11-2026.md`: các tệp đã tạo hoặc sửa, số đo trước và sau (bảng ở mục 2 làm mốc), phép thử nào đã chạy và kết quả, việc chưa làm, và mọi thay đổi so với kế hoạch. Không bắt đầu huấn luyện trên bộ v2 khi chưa được người dùng duyệt (huấn luyện trên v2 là lần chạy mới, không tiếp tục từ checkpoint hiện có).
