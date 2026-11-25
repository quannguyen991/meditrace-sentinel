# Danh mục 400 Khuôn Bệnh Mở rộng — Đợt 1 (201-400) & Đợt 2 (401-600)

> **Cập nhật ngày 22/11/2026:** Đã hoàn thành Task F1-F5 mở rộng quy mô bộ dữ liệu MediTrace Sentinel lên **600 khuôn lâm sàng** (200 khuôn gốc + 400 khuôn mở rộng).
> - **Lô 1 (50 khuôn, 201-250):** Đã hiện thực hóa 100% trong `src/khuon_mo_rong.py` kèm **ít nhất 6 biến thể lâm sàng đa dạng** cho mỗi mục khám, chẩn đoán, kế hoạch; `da_duyet = False`.
> - **Lô 2 - Lô 8 (350 khuôn, 251-600):** Đã hoàn tất brainstorm tên khoa học, phân nhóm tuổi, diễn tiến, hệ cơ quan và lý do lựa chọn lâm sàng, sẵn sàng cho Hội đồng Y khoa thẩm duyệt.
> - **Chỉ số Đa dạng Hệ cơ quan:** Đạt **21 hệ cơ quan**, không hệ nào vượt quá **10.83%** (dưới trần quy định 12.0%).

---

## PHẦN 1: LÔ 1 (ĐỢT 1: KHUÔN 201–250) — ĐÃ HIỆN THỰC HÓA 100%

*Toàn bộ 50 khuôn dưới đây đã được lập trình đầy đủ trong `src/khuon_mo_rong.py` với cấu trúc chuẩn và 6 biến thể lâm sàng mỗi mục:*

| # | Tên khuôn | Nhóm | Diễn tiến | Hệ cơ quan | Tình trạng |
|---|---|---|---|---|---|
| 1 | viêm phổi ở trẻ em | nhi | cấp | hô hấp | Đã viết xong (6 biến thể) |
| 2 | vàng da sơ sinh kéo dài | nhi | mạn | nhi khoa | Đã viết xong (6 biến thể) |
| 3 | suy dinh dưỡng thấp còi | nhi | mạn | dinh dưỡng | Đã viết xong (6 biến thể) |
| 4 | thừa cân béo phì ở trẻ em | nhi | mạn | dinh dưỡng | Đã viết xong (6 biến thể) |
| 5 | hen phế quản ở trẻ em | nhi | mạn | hô hấp | Đã viết xong (6 biến thể) |
| 6 | bệnh Kawasaki | nhi | cấp | nhi khoa | Đã viết xong (6 biến thể) |
| 7 | viêm ruột thừa cấp ở trẻ em | nhi | cấp | nhi khoa | Đã viết xong (6 biến thể) |
| 8 | tắc lệ đạo sơ sinh | nhi | mạn | mắt | Đã viết xong (6 biến thể) |
| 9 | rối loạn tăng động giảm chú ý | nhi | mạn | tâm thần | Đã viết xong (6 biến thể) |
| 10 | dậy thì sớm | nhi | mạn | nội tiết - chuyển hoá | Đã viết xong (6 biến thể) |
| 11 | tưa miệng ở trẻ nhỏ | nhi | cấp | nhi khoa | Đã viết xong (6 biến thể) |
| 12 | chảy máu cam tái phát ở trẻ | nhi | cấp | tai mũi họng | Đã viết xong (6 biến thể) |
| 13 | lao phổi | cả hai | mạn | truyền nhiễm | Đã viết xong (6 biến thể) |
| 14 | viêm gan A cấp | cả hai | cấp | truyền nhiễm | Đã viết xong (6 biến thể) |
| 15 | sốt thương hàn | cả hai | cấp | truyền nhiễm | Đã viết xong (6 biến thể) |
| 16 | nhiễm COVID-19 thể nhẹ | cả hai | cấp | truyền nhiễm | Đã viết xong (6 biến thể) |
| 17 | bệnh do xoắn khuẩn leptospira | cả hai | cấp | truyền nhiễm | Đã viết xong (6 biến thể) |
| 18 | viêm thận bể thận cấp | người lớn | cấp | thận - tiết niệu | Đã viết xong (6 biến thể) |
| 19 | suy thận cấp trước thận | người lớn | cấp | thận - tiết niệu | Đã viết xong (6 biến thể) |
| 20 | tiểu không tự chủ khi gắng sức | người lớn | mạn | thận - tiết niệu | Đã viết xong (nữ, 6 biến thể) |
| 21 | động kinh cơn co cứng co giật toàn thể | người lớn | mạn | thần kinh | Đã viết xong (6 biến thể) |
| 22 | nhồi máu não giai đoạn phục hồi | người lớn | mạn | thần kinh | Đã viết xong (6 biến thể) |
| 23 | chóng mặt tư thế kịch phát lành tính | người lớn | cấp | thần kinh | Đã viết xong (6 biến thể) |
| 24 | bệnh thần kinh ngoại biên do đái tháo đường | người lớn | mạn | thần kinh | Đã viết xong (6 biến thể) |
| 25 | đau cơ xơ hoá | người lớn | mạn | cơ xương khớp | Đã viết xong (6 biến thể) |
| 26 | viêm gân lồi cầu ngoài xương cánh tay | người lớn | mạn | cơ xương khớp | Đã viết xong (6 biến thể) |
| 27 | gãy xương cổ tay do ngã | cả hai | cấp | chấn thương | Đã viết xong (6 biến thể) |
| 28 | chấn thương sọ não nhẹ | cả hai | cấp | chấn thương | Đã viết xong (6 biến thể) |
| 29 | bỏng nhiệt độ II diện tích nhỏ | cả hai | cấp | chấn thương | Đã viết xong (6 biến thể) |
| 30 | viêm ruột thừa cấp | người lớn | cấp | tiêu hoá | Đã viết xong (6 biến thể) |
| 31 | thoát vị bẹn | người lớn | mạn | tiêu hoá | Đã viết xong (6 biến thể) |
| 32 | sỏi ống mật chủ | người lớn | cấp | tiêu hoá | Đã viết xong (6 biến thể) |
| 33 | bệnh Crohn | người lớn | mạn | tiêu hoá | Đã viết xong (6 biến thể) |
| 34 | polyp đại tràng | người lớn | mạn | tiêu hoá | Đã viết xong (6 biến thể) |
| 35 | táo bón mạn tính ở người cao tuổi | người lớn | mạn | lão khoa | Đã viết xong (6 biến thể) |
| 36 | hội chứng chuyển hoá | người lớn | mạn | nội tiết - chuyển hoá | Đã viết xong (6 biến thể) |
| 37 | suy dinh dưỡng ở người cao tuổi | người lớn | mạn | dinh dưỡng | Đã viết xong (6 biến thể) |
| 38 | thiếu vitamin B12 | người lớn | mạn | huyết học | Đã viết xong (6 biến thể) |
| 39 | bệnh động mạch ngoại biên chi dưới | người lớn | mạn | tim mạch | Đã viết xong (6 biến thể) |
| 40 | nhịp nhanh trên thất kịch phát | người lớn | cấp | tim mạch | Đã viết xong (6 biến thể) |
| 41 | viêm vùng chậu | người lớn | cấp | sản phụ khoa | Đã viết xong (nữ, 6 biến thể) |
| 42 | tiền sản giật | người lớn | cấp | sản phụ khoa | Đã viết xong (nữ, 6 biến thể) |
| 43 | dọa sẩy thai | người lớn | cấp | sản phụ khoa | Đã viết xong (nữ, 6 biến thể) |
| 44 | tắc tia sữa | người lớn | cấp | sản phụ khoa | Đã viết xong (nữ, 6 biến thể) |
| 45 | rối loạn tiền mãn kinh | người lớn | mạn | sản phụ khoa | Đã viết xong (nữ, 6 biến thể) |
| 46 | viêm nha chu | cả hai | mạn | răng hàm mặt | Đã viết xong (6 biến thể) |
| 47 | ù tai | người lớn | mạn | tai mũi họng | Đã viết xong (6 biến thể) |
| 48 | chảy máu cam do tăng huyết áp | người lớn | cấp | tai mũi họng | Đã viết xong (6 biến thể) |
| 49 | nấm bàn chân | cả hai | mạn | da liễu | Đã viết xong (6 biến thể) |
| 50 | herpes môi tái phát | cả hai | cấp | da liễu | Đã viết xong (6 biến thể) |

---

## PHẦN 2: LÔ 2–4 (ĐỢT 1: KHUÔN 251–400) — ĐÃ BRAINSTORM & ĐỊNH HỆ CƠ QUAN

### Lô 2 (Khuôn 251–300): Nhi khoa, Sơ sinh, Di truyền nhi & Rối loạn chuyển hoá bẩm sinh
- Bao gồm 50 bệnh lý nhi khoa thực chứng: `lồng ruột cấp ở nhũ nhi`, `teo đường mật bẩm sinh`, `suy giáp bẩm sinh`, `tăng sản thượng thận bẩm sinh`, `còi xương do thiếu vitamin D`, `bệnh celiac ở trẻ em`, `xuất huyết giảm tiểu cầu miễn dịch nhi`, `viêm màng não mủ ở trẻ em`, `hẹp phì đại môn vị ở trẻ nhũ nhi`, `hội chứng thận hư tiên phát ở trẻ em`, `viêm mao mạch dị ứng Schonlein-Henoch ở trẻ`, `hội chứng Down`, `tự kỷ ở trẻ em`, `viêm khớp vô căn thiếu niên`, `tinh hoàn ẩn bẩm sinh`, `lỗ tiểu lệch thấp hypospadias`, `thiếu men G6PD gây tán huyết cấp ở trẻ`, `suy dinh dưỡng thể phù Kwashiorkor`, v.v. (Xem chi tiết tại `DANH_SACH_UNG_VIEN_350` trong `src/khuon_mo_rong.py`).

### Lô 3 (Khuôn 301–350): Cơ xương khớp, Thần kinh cơ & Chấn thương chỉnh hình ngoại trú
- Bao gồm 50 bệnh lý: `viêm gân lồi cầu trong xương cánh tay (golf elbow)`, `viêm bao gân De Quervain`, `rách chóp xoay khớp vai`, `hoại tử vô mạch chỏm xương đùi`, `hội chứng dải chậu chày`, `biến dạng ngón chân cái vẹo ngoài Hallux valgus`, `rách sụn chêm khớp gối`, `gãy kín xương đòn do ngã`, `hội chứng cơ hình lê chèn ép thần kinh tọa`, `liệt dây thần kinh quay gây bàn tay rủ`, `nhược cơ thể mắt`, `xơ cứng rải rác thể tái phát thuyên giảm`, `viêm khớp vảy nến`, `hội chứng Sjogren`, `bệnh Still người lớn`, `giả gout`, `hẹp ống sống thắt lưng thoái hóa`, v.v.

### Lô 4 (Khuôn 351–400): Lão khoa, Thận - Tiết niệu, Nam khoa & Chuyển hoá nội tiết
- Bao gồm 50 bệnh lý: `sa sút trí tuệ Alzheimer giai đoạn nhẹ`, `hội chứng suy yếu dễ tổn thương ở người già`, `ngã tái diễn ở người cao tuổi`, `mê sảng cấp tính ở người cao tuổi`, `bàng quang tăng hoạt OAB`, `viêm bàng quang kẽ mạn tính`, `thận đa nang di truyền trội`, `sỏi san hô đài bể thận`, `viêm tuyến tiền liệt mạn tính không do vi khuẩn`, `xoắn tinh hoàn dọa nghẹt`, `bệnh cong dương vật Peyronie`, `đái tháo đường típ 1 mới phát hiện`, `bệnh to đầu chi Acromegaly`, `viêm tuyến giáp Hashimoto`, `u tủy thượng thận Pheochromocytoma`, `bệnh Wilson lắng đọng đồng`, `bệnh Beriberi thiếu vitamin B1`, `bệnh Scorbut thiếu vitamin C`, v.v.

---

## PHẦN 3: LÔ 5–8 (ĐỢT 2: KHUÔN 401–600) — ĐÃ BRAINSTORM & ĐỊNH HỆ CƠ QUAN

### Lô 5 (Khuôn 401–450): Truyền nhiễm nhiệt đới hiếm, Ký sinh trùng & Lao ngoài phổi
- Bao gồm 50 bệnh lý: `lao hạch ngoại biên vùng cổ`, `lao màng bụng thể cổ trướng`, `lao xương khớp cột sống bệnh Pott`, `sốt rét cơn do Plasmodium vivax`, `bệnh sán lá gan lớn Fasciola`, `bệnh sán lá phổi Paragonimus`, `ấu trùng sán lợn dưới da và cơ`, `nhiễm giun lươn Strongyloides`, `hội chứng ấu trùng di chuyển nội tạng Toxocara`, `nhiễm giun chỉ bạch huyết phù chân voi`, `viêm ruột do Clostridioides difficile`, `bệnh Whitmore thể viêm phổi áp xe hóa`, `nhiễm nấm sâu Cryptococcus`, `sốt Chikungunya`, `bệnh phong thể củ Hansen`, `hạ cam mềm Chancroid`, `co thắt tâm vị thực quản Achalasia`, `túi thừa đại tràng sigma viêm cấp tính`, v.v.

### Lô 6 (Khuôn 451–500): Mắt, Tai mũi họng & Răng hàm mặt chuyên sâu
- Bao gồm 50 bệnh lý: `viêm củng mạc trước hoại tử`, `viêm màng bồ đào trước vô căn`, `bong võng mạc nguyên phát`, `tắc tĩnh mạch trung tâm võng mạc`, `thoái hóa hoàng điểm tuổi già thể khô`, `bệnh võng mạc đái tháo đường tiền tăng sinh`, `viêm loét giác mạc do nấm sợi`, `viêm tai giữa mạn tính có cholesteatoma`, `điếc đột ngột tiếp nhận thần kinh`, `bệnh Meniere`, `viêm xoang hàm do nấm Aspergillus`, `hạt xơ dây thanh`, `polyp dây thanh quản`, `viêm khớp thái dương hàm TMD`, `răng khôn hàm dưới mọc lệch biến chứng viêm lợi trùm`, `viêm tủy răng hoại tử`, `áp xe quanh chóp răng`, `bạch sản niêm mạc má`, v.v.

### Lô 7 (Khuôn 501–550): Da liễu hiếm, Dị ứng - Miễn dịch lâm sàng & Độc chất ngoại trú
- Bao gồm 50 bệnh lý: `bệnh da bọng nước tự miễn Pemphigus vulgaris`, `bọng nước dạng Pemphigoid`, `hội chứng Stevens-Johnson do thuốc`, `hoại tử thượng bì nhiễm độc Lyell`, `vảy phấn hồng Gibert`, `lichen phẳng da niêm mạc`, `viêm tuyến mồ hôi mủ hidradenitis suppurativa`, `rụng tóc từng mảng alopecia areata`, `viêm quầng Erysipelas cẳng chân`, `phù mạch dị ứng di truyền phù Quincke`, `sốc phản vệ độ 2 do thức ăn`, `dị ứng thuốc kháng sinh beta-lactam`, `viêm mạch hoại tử GPA Wegener`, `viêm động mạch thái dương Horton`, `ngộ độc paracetamol giai đoạn sớm`, `ngộ độc nấm độc amanita`, `rắn lục đuôi đỏ cắn`, v.v.

### Lô 8 (Khuôn 551–600): Huyết học, Tim mạch chuyên sâu, Tâm thần & Bệnh nghề nghiệp / Hô hấp hiếm
- Bao gồm 50 bệnh lý: `suy tủy xương dòng hồng cầu đơn thuần`, `thiếu máu do suy thận mạn`, `thiếu máu bất sản tủy aplastic anemia`, `đa hồng cầu nguyên phát Polycythemia vera`, `bệnh máu khó đông Hemophilia A`, `xuất huyết giảm tiểu cầu huyết khối TTP`, `đau tủy xương đa u tủy xương Multiple Myeloma`, `u lympho Hodgkin`, `viêm nội tâm mạc nhiễm khuẩn Osler`, `bệnh cơ tim phì đại`, `hội chứng Brugada typ 1`, `hội chứng QT dài bẩm sinh`, `block nhĩ thất độ 2 Mobitz 2`, `rối loạn stress sau sang chấn PTSD`, `rối loạn ám ảnh sợ khoảng trống Agoraphobia`, `rối loạn dạng cơ thể Somatization`, `xơ cứng bì tổn thương phổi kẽ`, `bệnh u hạt Sarcoidosis phổi`, `bụi phổi amiăng Asbestosis`, `bệnh phổi nông dân do nấm mốc dị ứng`, v.v.
