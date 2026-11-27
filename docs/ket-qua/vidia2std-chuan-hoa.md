# Bảng chuẩn hoá phương ngữ trên câu thật — ViDia2Std

Sinh bằng `python -m src.do_luong.do_vidia2std`. Đừng sửa tay. Nguồn: Ta, Dinh, Nguyen, *ViDia2Std*, AAAI-26 (2026), CC-BY-NC-4.0; bình luận Facebook do người bản ngữ viết lại sang tiếng Việt chuẩn. **Không phải hội thoại khám bệnh** — số dưới đây chỉ nói bảng chuẩn hoá phủ được bao nhiêu chỗ khác biệt phương ngữ trong tiếng Việt viết tự nhiên.

## Tập test (1.603 câu) — bảng đầy đủ (cả mục "cần hỏi")

| Vùng | Câu | Chỗ thay từ (người viết lại) | Bảng đổi đúng chữ | Bảng đổi, khác chữ | Bảng bỏ qua | Bảng đổi thừa | Chỗ thêm/bớt từ | Lỗi từ so với câu chuẩn: gốc → sau chuẩn hoá |
|---|---|---|---|---|---|---|---|---|
| Bắc | 201 | 221 | 48/221 (21.7 %) | 2/221 (0.9 %) | 171/221 (77.4 %) | 6 | 1 | 230/1883 (12.2 %) → 193/1883 (10.2 %) |
| Trung | 1067 | 3178 | 1715/3178 (54.0 %) | 610/3178 (19.2 %) | 853/3178 (26.8 %) | 71 | 97 | 3832/11834 (32.4 %) → 1831/11834 (15.5 %) |
| Nam | 335 | 865 | 259/865 (29.9 %) | 43/865 (5.0 %) | 563/865 (65.1 %) | 3 | 49 | 1166/3672 (31.8 %) → 846/3672 (23.0 %) |
| Tất cả | 1603 | 4264 | 2022/4264 (47.4 %) | 655/4264 (15.4 %) | 1587/4264 (37.2 %) | 80 | 147 | 5228/17389 (30.1 %) → 2870/17389 (16.5 %) |

## Tập test — chỉ các mục "chắc"

| Vùng | Câu | Chỗ thay từ (người viết lại) | Bảng đổi đúng chữ | Bảng đổi, khác chữ | Bảng bỏ qua | Bảng đổi thừa | Chỗ thêm/bớt từ | Lỗi từ so với câu chuẩn: gốc → sau chuẩn hoá |
|---|---|---|---|---|---|---|---|---|
| Bắc | 201 | 221 | 48/221 (21.7 %) | 2/221 (0.9 %) | 171/221 (77.4 %) | 1 | 1 | 230/1883 (12.2 %) → 183/1883 (9.7 %) |
| Trung | 1067 | 3178 | 1705/3178 (53.7 %) | 606/3178 (19.1 %) | 867/3178 (27.3 %) | 59 | 97 | 3832/11834 (32.4 %) → 1819/11834 (15.4 %) |
| Nam | 335 | 865 | 256/865 (29.6 %) | 42/865 (4.9 %) | 567/865 (65.5 %) | 3 | 49 | 1166/3672 (31.8 %) → 852/3672 (23.2 %) |
| Tất cả | 1603 | 4264 | 2009/4264 (47.1 %) | 650/4264 (15.2 %) | 1605/4264 (37.6 %) | 63 | 147 | 5228/17389 (30.1 %) → 2854/17389 (16.4 %) |

Cách đọc: *chỗ thay từ* là chỗ người viết lại đổi một hay vài từ thành từ khác (cụm cùng độ dài tách thành từng cặp một từ); *đổi, khác chữ* là bảng có đổi nhưng ra chữ khác chữ người viết lại dùng — phần lớn là từ cùng nghĩa hoặc sửa được một phần cụm, xem danh sách tập dev bên dưới; *đổi thừa* là chỗ bảng đổi nhưng người viết lại giữ nguyên; *thêm/bớt từ* (ví dụ bỏ tiểu từ cuối câu) thì phép thay từ không làm được, tính riêng. Lỗi từ = số phép sửa (thay, xoá, chèn) để thành câu chuẩn, chia cho số từ câu chuẩn.

## Tập DEV — đọc tay (không lấy từ test)

### Bảng có đổi nhưng khác chữ người viết lại dùng

| Số lần | Phương ngữ → chữ người viết lại (bảng ghi) |
|---|---|
| 63 | mô → nào  (bảng: đâu) |
| 28 | ni → nay  (bảng: này) |
| 13 | mô → nào  (bảng: khi nào) |
| 12 | ni → nay  (bảng: hôm nay) |
| 10 | ri → vậy  (bảng: thế) |
| 9 | ri → thế này  (bảng: thế) |
| 9 | rứa → thế  (bảng: vậy) |
| 7 | nớ → đấy  (bảng: đó) |
| 7 | chộ → chỗ  (bảng: thấy) |
| 7 | mệ → mẹ  (bảng: bà) |
| 5 | bữa → hôm  (bảng: hôm nay) |
| 5 | răng → sao  (bảng: làm sao) |
| 5 | chừ → giờ  (bảng: bây giờ) |
| 5 | mô → ở đâu  (bảng: đâu) |
| 5 | chi → sao  (bảng: gì) |
| 4 | ri → như thế này  (bảng: thế) |
| 4 | tau → tôi  (bảng: tao) |
| 3 | chi → nào  (bảng: gì) |
| 3 | chi → sự  (bảng: gì) |
| 3 | dừ → bây giờ  (bảng: giờ) |
| 3 | hầy → nhé  (bảng: nhỉ) |
| 3 | chi → đâu  (bảng: gì) |
| 3 | mần → làm  (bảng: làm sao) |
| 2 | ni chi → nay cái gì  (bảng: hôm nay gì) |
| 2 | rứa bây → vậy chúng mày  (bảng: vậy bây) |

### Bảng đổi thừa (người viết lại giữ nguyên)

| Số lần | Chữ gốc (bảng đổi thành) |
|---|---|
| 19 | vô  (bảng: vào) |
| 6 | chi  (bảng: gì) |
| 4 | thiệt  (bảng: thật) |
| 4 | tui  (bảng: tôi) |
| 4 | ảnh  (bảng: anh ấy) |
| 2 | cấy  (bảng: cái) |
| 2 | hè  (bảng: nhỉ) |
| 2 | rứa  (bảng: vậy) |
| 2 | chớ  (bảng: chứ) |
| 2 | răng  (bảng: sao) |
| 2 | con nít  (bảng: trẻ em) |
| 2 | giò  (bảng: chân) |
| 1 | mô  (bảng: đâu) |
| 1 | tới công chuyện  (bảng: trở nặng) |
| 1 | đi cầu  (bảng: đi đại tiện) |

### Cụm bảng còn bỏ qua nhiều nhất

| Số lần | Phương ngữ → chuẩn |
|---|---|
| 43 | đó → đấy |
| 37 | coi → xem |
| 36 | răng → sao |
| 21 | nha → nhé |
| 13 | mai → hôm |
| 13 | mốt → nào |
| 13 | rầu → rồi |
| 13 | bựa → bữa |
| 11 | ả → chị |
| 11 | mai → sau |
| 11 | mốt → này |
| 11 | á → đấy |
| 11 | á → ấy |
| 10 | ngài → người |
| 10 | trốc → đầu |
| 10 | kiếm → tìm |
| 9 | túi → tối |
| 8 | nhờ → nhỉ |
| 8 | mồ → nào |
| 8 | thâu → thôi |
| 8 | nghe → nhé |
| 8 | o → cô |
| 7 | nhẽ → lẽ |
| 7 | lẹ → lẽ |
| 7 | bùng → vòng |
| 7 | binh → xoay |
| 7 | nhởi → chơi |
| 6 | quại → ngoại |
| 6 | chửa → chưa |
| 6 | mụ → bà |

Muốn thêm từ vào bảng thì lấy từ tập *train* của ViDia2Std và đo lại trên test; không thêm từ danh sách trên rồi đo lại trên chính tập đã nhìn.
