# ĐỌC MẪU 30 HỘI THOẠI V2 TRƯỚC KHI SỬA (`data/hoi_thoai_viet_v2_mo_rong.jsonl`)

- **Ngày thực hiện:** 23/11/2026 (Bước 0)
- **Nguồn dữ liệu:** `data/hoi_thoai_viet_v2_mo_rong.jsonl` (bản trước khi sửa, 5.000 ca)
- **Cách chọn mẫu:** Ngẫu nhiên 30 ca với hạt cố định `random.Random(20261123)`
- **Tổng số lượt thoại trong 30 ca:** 517 lượt
- **Phân bố độ dài trên 30 ca mẫu:** Trung vị **18 từ/lượt** · Lượt $\le 3$ từ: **0/517 (0.0%)** · Lượt $\ge 12$ từ: **460/517 (89.0%)**

---

## 1. Bảng Thống Kê Lỗi Gặp Phải Trên 30 Ca Đọc Mẫu

| Nhóm lỗi | Số lần xuất hiện (trên 517 lượt của 30 ca) | Tỷ lệ trên 517 lượt | Ví dụ thực tế trong 30 ca |
|---|---:|---:|---|
| 1. Lặp từ / cụm từ liền kề & ghép trùng ngữ pháp | **69** | 13.3% | `không không ạ?`, `phải không phải không ạ?`, `vậy vậy ạ?`, `nhé nhé?`, `giúp tôi giúp tôi nhé`, `một chút một chút nha`, `mấy hôm nay nay ạ`, `Từ độ hai tháng nay trước`, `Để tôi, để tôi...`, `uống ngày hai lần uống đúng giờ nhé`, `đâu hết á` |
| 2. Hạt đề nghị thừa sau dấu chấm (`. nhé.`, `. nha.`, `. nghen.`) | **29** | 5.6% | `Ống tai ngoài sưng nề, kéo vành tai đau tăng. nhé.`, `Thị lực không kính hai mắt giảm. nhé.` |
| 3. Cụm nhận xét thừa sau dấu chấm ở cuối câu | **37** | 7.2% | `Chẩn đoán của tôi là: Viêm tai ngoài cấp. rõ ràng.`, `...SpO2 97%. nghen.`, `...theo đúng hướng dẫn.` |
| 4. Tiểu từ đề nghị (`nhé/nha/nghen`) gắn vào câu hỏi `?` | **16** | 3.1% | `...có dị ứng với kháng sinh hay thuốc giảm đau gì không nhé?`, `...mình có đang dùng loại thuốc nào không nhé?` |
| 5. Lệch đại từ xưng hô / Sai chủ thể / Từ đệm lệch vai | **52** | 10.1% | Người nhà (mẹ) đáp `tôi không dị ứng với kháng sinh...` cho bệnh nhi; bố nói `Dạ con nghe rồi bác sĩ... tôi rõ...`; bác sĩ gọi cụ ông/cô/chú là `bạn`; mở đầu câu kể bằng `Dạ thưa đúng ạ` |
| 6. Hỏi đáp xã giao lệch cặp (hỏi một đằng, đáp một nẻo) | **13** | 2.5% | Hỏi `Anh đi thang máy hay thang bộ lên tầng này` -> Đáp `biển chỉ dẫn to rõ ngoài cổng nên em tìm thấy ngay` |
| 7. Biến f-string chưa thay (`{goi}`, `{goi_hoa}`) | **3** | 0.6% | `Bác sĩ mời {goi}, chị đã kịp ăn lót dạ món gì nhẹ nhàng chưa nhé?`, `{goi_hoa} ngồi ghế đệm bên ngoài...` |
| **Tổng cộng số lỗi ghi nhận trên 30 ca** | **219** | — | 30/30 ca (100% số ca đọc mẫu) đều có ít nhất 3 lỗi |

---

## 2. Chi Tiết Từng Ca Trong 30 Hội Thoại Đọc Mẫu

### Ca 01 — Mã: `hv_4717` (`viêm nang lông tụ cầu vàng`)
- **Thông tin ca:** `la_tre_em=True` | `nguoi_ke=bố` | `lo_danh_tinh=True` | `boi_canh=nguoi_nha_thay_mat` | `bay=['bo_sung', 'luoc_chu_ngu', 'nguoi_ke_benh_minh', 'nguoi_nha_ke_ho']` | `so_luot=16`
- **Lời thoại đầy đủ:**
```text
L01: Bác sĩ: Chào anh, nay anh đi thay à, cháu có triệu chứng gì mà không đến được?
L02: Người nhà: Dạ đúng rồi bác, ở nhà cháu nhà tôi mệt không dậy nổi, tôi sốt ruột quá nên đi khám thay.
L03: Bác sĩ: Cho bác sĩ hỏi, Anh là gì của cháu vậy vậy ạ?
L04: Người nhà: Vâng ạ, tôi là bố đưa cháu đi khám.
L05: Người nhà: Suốt gần một tuần qua bị sẩn mủ nhỏ hình chóp tại vị trí chân sợi lông xung quanh có quầng viêm đỏ làm phiền nhiều.
L06: Bác sĩ: Để bác sĩ nắm rõ hơn, ngoài ra còn triệu chứng nào làm mình lo lắng nữa không vậy ạ?
L07: Người nhà: Dạ bác sĩ, ngoài ra còn bị mụn mủ vỡ khô đóng vảy tiết nhỏ màu nâu vàng rụng đi không để lại sẹo, tập trung nhiều ở vùng râu cằm da đầu ngực lưng và đùi nữa.
L08: Người nhà: Tập trung nhiều ở vùng râu cằm da đầu ngực lưng và đùi thì tăng lên khi vận động ạ.
L09: Người nhà: Tôi bị hội chứng ruột kích thích mấy năm nay rồi ạ.
L10: Bác sĩ: Bác sĩ cần kiểm tra kỹ chỗ này, trước đây có dị ứng với kháng sinh hay thuốc giảm đau gì không nhé?
L11: Người nhà: Dạ vâng, cháu nhà tôi có tiền sử dị ứng amoxicillin ạ.
L12: Bác sĩ: Về thuốc thang mấy hôm nay, mình có dùng thuốc bôi ngoài da, thuốc xịt hay thuốc nhỏ mắt nào không vậy?
L13: Người nhà: Dạ thưa bác sĩ, trước có uống smecta một gói, ngày hai lần, ngừng 4 tuần rồi.
L14: Bác sĩ: Tôi tạm thời hướng đến bệnh cảnh viêm nang lông nông do tụ cầu khuẩn vùng ngực lưng, tuy nhiên cần đưa người bệnh đến kiểm tra cụ thể.
L15: Bác sĩ: Anh đưa cháu đến để tôi khám trực tiếp.
L16: Người nhà: Dạ con nghe rồi bác sĩ, cảm ơn bác sĩ rất nhiều, tôi rõ các hướng dẫn điều trị rồi nghen bác sĩ.
```
- **Đáp án mệnh đề (`dap_an`):**
  - `M01` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=sẩn mủ nhỏ hình chóp tại vị trí chân sợi lông xung quanh có quầng viêm đỏ` | `moc=gần một tuần` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Suốt gần một tuần qua bị sẩn mủ nhỏ hình chóp tại vị trí chân sợi lông xung quanh có quầng viêm đỏ làm phiền nhiều']`
  - `M02` [LÝ DO KHÁM BỆNH] `chu_the=bệnh nhân` | `noi_dung=sẩn mủ nhỏ hình chóp tại vị trí chân sợi lông xung quanh có quầng viêm đỏ` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Suốt gần một tuần qua bị sẩn mủ nhỏ hình chóp tại vị trí chân sợi lông xung quanh có quầng viêm đỏ làm phiền nhiều']`
  - `M03` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=mụn mủ vỡ khô đóng vảy tiết nhỏ màu nâu vàng rụng đi không để lại sẹo` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['ngoài ra còn bị mụn mủ vỡ khô đóng vảy tiết nhỏ màu nâu vàng rụng đi không để lại sẹo']`
  - `M04` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=tập trung nhiều ở vùng râu cằm da đầu ngực lưng và đùi` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['tập trung nhiều ở vùng râu cằm da đầu ngực lưng và đùi nữa', 'Tập trung nhiều ở vùng râu cằm da đầu ngực lưng và đùi thì tăng lên khi vận động ạ']`
  - `M05` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=tập trung nhiều ở vùng râu cằm da đầu ngực lưng và đùi tăng lên khi vận động` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=bổ sung` | `trich_dan=['Tập trung nhiều ở vùng râu cằm da đầu ngực lưng và đùi thì tăng lên khi vận động ạ']`
  - `M06` [TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI] `chu_the=bố` | `noi_dung=hội chứng ruột kích thích` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Tôi bị hội chứng ruột kích thích mấy năm nay rồi ạ']`
  - `M07` [DỊ ỨNG] `chu_the=bệnh nhân` | `noi_dung=dị ứng amoxicillin` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['cháu nhà tôi có tiền sử dị ứng amoxicillin ạ']`
  - `M08` [TIỀN SỬ BỆNH] `chu_the=bệnh nhân` | `noi_dung=từng dùng smecta, đã ngừng 4 tuần` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['trước có uống smecta một gói, ngày hai lần, ngừng 4 tuần rồi']`
  - `M09` [CHẨN ĐOÁN] `chu_the=bệnh nhân` | `noi_dung=Viêm nang lông nông do tụ cầu khuẩn vùng ngực lưng` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=nghi ngờ` | `quan_he=None` | `trich_dan=['Tôi tạm thời hướng đến bệnh cảnh viêm nang lông nông do tụ cầu khuẩn vùng ngực lưng']`
  - `M10` [KẾ HOẠCH ĐIỀU TRỊ] `chu_the=bệnh nhân` | `noi_dung=đưa bệnh nhân đến khám trực tiếp` | `moc=None` | `phu_dinh=False` | `tinh_huong=kế hoạch` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Anh đưa cháu đến để tôi khám trực tiếp']`
- **Các lỗi phát hiện khi đọc ca này (4 lỗi):**
  - **L03** — *Lặp từ nghi vấn `vậy vậy` / `vậy thế`*: `Bác sĩ: Cho bác sĩ hỏi, Anh là gì của cháu vậy vậy ạ?`
  - **L09** — *Lặp từ thời gian `nay nay` / `rồi nay` / `nay rồi nay`*: `Người nhà: Tôi bị hội chứng ruột kích thích mấy năm nay rồi ạ.`
  - **L10** — *Tiểu từ đề nghị (`nhé/nha/nghen`) gắn vào câu hỏi `?`*: `Bác sĩ: Bác sĩ cần kiểm tra kỹ chỗ này, trước đây có dị ứng với kháng sinh hay thuốc giảm đau gì không nhé?`
  - **L16** — *Xung đột đại từ tự xưng trong cùng một câu (`con` vs `tôi`)*: `Người nhà: Dạ con nghe rồi bác sĩ, cảm ơn bác sĩ rất nhiều, tôi rõ các hướng dẫn điều trị rồi nghen bác sĩ.`

### Ca 02 — Mã: `hv_4046` (`viêm tai ngoài`)
- **Thông tin ca:** `la_tre_em=False` | `nguoi_ke=None` | `lo_danh_tinh=False` | `boi_canh=kham_lan_dau` | `bay=['tien_su_gia_dinh']` | `so_luot=12`
- **Lời thoại đầy đủ:**
```text
L01: Bác sĩ: Cô kể rõ cho bác sĩ nghe xem tình trạng hiện tại thế nào ạ.
L02: Bệnh nhân: Dạ bác sĩ, tình trạng đau chói dữ dội khi kéo nhẹ vành tai hoặc ấn vào nắp bình tai của tôi kéo dài hai hôm rồi ạ.
L03: Bác sĩ: Bạn có thấy sụt cân, chán ăn hay mất ngủ kèm theo không nhỉ?
L04: Bệnh nhân: Dạ bác sĩ, tôi còn thấy tiền sử đi bơi lội tắm biển ngoáy tai bằng dụng cụ cứng nữa.
L05: Bác sĩ: Bác sĩ muốn hỏi một chút về gia đình, trong nhà có ai mắc bệnh về đường tiêu hóa hay ung thư không không ạ?
L06: Bệnh nhân: Dạ thưa đúng ạ, ông nội bị ung thư da.
L07: Bác sĩ: Để xem xét kỹ hơn, bác sĩ kiểm tra họng và amidan xem có viêm đỏ không giúp bác sĩ nhé.
L08: Bác sĩ: Khám thực thể: Ống tai ngoài sưng nề, kéo vành tai đau tăng. nhé.
L09: Bác sĩ: Chẩn đoán của tôi là: Viêm tai ngoài cấp. rõ ràng.
L10: Bác sĩ: Bác sĩ sẽ tiến hành: Giữ tai khô. Nhỏ tai kháng sinh. Hẹn khám lại sau một tuần. nhé.
L11: Bác sĩ: Tôi sẽ kê đơn augmentin 625 mg, uống ngày hai lần uống đúng giờ nhé.
L12: Bệnh nhân: Dạ tôi rõ phác đồ rồi, cảm ơn bác sĩ đã khám rất kỹ, tôi sẽ uống nhiều nước và ăn chín uống sôi như bác sĩ bảo nha bác sĩ.
```
- **Đáp án mệnh đề (`dap_an`):**
  - `M01` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=đau chói dữ dội khi kéo nhẹ vành tai hoặc ấn vào nắp bình tai` | `moc=hai hôm` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['tình trạng đau chói dữ dội khi kéo nhẹ vành tai hoặc ấn vào nắp bình tai của tôi kéo dài hai hôm rồi ạ']`
  - `M02` [LÝ DO KHÁM BỆNH] `chu_the=bệnh nhân` | `noi_dung=đau chói dữ dội khi kéo nhẹ vành tai hoặc ấn vào nắp bình tai` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['tình trạng đau chói dữ dội khi kéo nhẹ vành tai hoặc ấn vào nắp bình tai của tôi kéo dài hai hôm rồi ạ']`
  - `M03` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=tiền sử đi bơi lội tắm biển ngoáy tai bằng dụng cụ cứng` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['tôi còn thấy tiền sử đi bơi lội tắm biển ngoáy tai bằng dụng cụ cứng nữa']`
  - `M04` [TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI] `chu_the=ông nội` | `noi_dung=ung thư da` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['ông nội bị ung thư da']`
  - `M05` [KHÁM LÂM SÀNG] `chu_the=bệnh nhân` | `noi_dung=Ống tai ngoài sưng nề, kéo vành tai đau tăng` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Khám thực thể: Ống tai ngoài sưng nề, kéo vành tai đau tăng']`
  - `M06` [CHẨN ĐOÁN] `chu_the=bệnh nhân` | `noi_dung=Viêm tai ngoài cấp` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Chẩn đoán của tôi là: Viêm tai ngoài cấp']`
  - `M07` [KẾ HOẠCH ĐIỀU TRỊ] `chu_the=bệnh nhân` | `noi_dung=Giữ tai khô. Nhỏ tai kháng sinh. Hẹn khám lại sau một tuần` | `moc=None` | `phu_dinh=False` | `tinh_huong=kế hoạch` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Bác sĩ sẽ tiến hành: Giữ tai khô. Nhỏ tai kháng sinh. Hẹn khám lại sau một tuần']`
  - `M08` [KẾ HOẠCH ĐIỀU TRỊ] `chu_the=bệnh nhân` | `noi_dung=kê augmentin` | `moc=None` | `phu_dinh=False` | `tinh_huong=kế hoạch` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Tôi sẽ kê đơn augmentin 625 mg, uống ngày hai lần uống đúng giờ nhé']`
- **Các lỗi phát hiện khi đọc ca này (7 lỗi):**
  - **L03** — *Bác sĩ gọi người bệnh/người nhà là `bạn` (lệch vai xưng hô)*: `Bác sĩ: Bạn có thấy sụt cân, chán ăn hay mất ngủ kèm theo không nhỉ?`
  - **L05** — *Lặp từ nghi vấn `không không` / `chưa không`*: `Bác sĩ: Bác sĩ muốn hỏi một chút về gia đình, trong nhà có ai mắc bệnh về đường tiêu hóa hay ung thư không không ạ?`
  - **L06** — *Từ đệm `Dạ thưa đúng ạ` đặt trước câu kể triệu chứng/tiền sử*: `Bệnh nhân: Dạ thưa đúng ạ, ông nội bị ung thư da.`
  - **L08** — *Hạt đề nghị thừa sau dấu chấm (`. nhé.`, `. nha.`, `. nghen.`)*: `Bác sĩ: Khám thực thể: Ống tai ngoài sưng nề, kéo vành tai đau tăng. nhé.`
  - **L09** — *Cụm nhận xét thừa sau dấu chấm ở cuối câu*: `Bác sĩ: Chẩn đoán của tôi là: Viêm tai ngoài cấp. rõ ràng.`
  - **L10** — *Hạt đề nghị thừa sau dấu chấm (`. nhé.`, `. nha.`, `. nghen.`)*: `Bác sĩ: Bác sĩ sẽ tiến hành: Giữ tai khô. Nhỏ tai kháng sinh. Hẹn khám lại sau một tuần. nhé.`
  - **L11** — *Ghép thừa `uống ngày ... lần uống đúng giờ`*: `Bác sĩ: Tôi sẽ kê đơn augmentin 625 mg, uống ngày hai lần uống đúng giờ nhé.`

### Ca 03 — Mã: `hv_1311` (`ngưng thở khi ngủ do tắc nghẽn`)
- **Thông tin ca:** `la_tre_em=False` | `nguoi_ke=con gái` | `lo_danh_tinh=True` | `boi_canh=cho_ket_qua` | `bay=['dien_bien', 'nguoi_ke_benh_minh', 'nguoi_nha_ke_ho']` | `so_luot=18`
- **Lời thoại đầy đủ:**
```text
L01: Bác sĩ: Mời em ngồi, Em kể bác sĩ nghe xem chú bị mệt thế nào?
L02: Bác sĩ: Cho tôi hỏi rõ là, Em có quan hệ như thế nào với chú ấy ạ?
L03: Người nhà: Thưa bác sĩ, chú ấy là người thân của em, em là con gái bác sĩ ạ.
L04: Bác sĩ: Ngồi nghỉ ngơi ngoài khu vực chờ, chú có cần chỉnh lại hướng gió quạt không vậy ạ?
L05: Người nhà: Dạ em thấy, ghế ngồi êm ái nên đợi không bị mỏi lưng ạ.
L06: Người nhà: Bố em thấy xuất hiện biểu hiện ngủ ngáy rất to ngắt quãng có cơn nghẹt thở ngót nghét khoảng một tháng.
L07: Bác sĩ: Cho tôi hỏi thêm là, ngoài các triệu chứng trên thì còn dấu hiệu nào khác đi kèm không?
L08: Người nhà: Dạ thưa đúng ạ, song song đó bố em còn thấy khô miệng khi thức dậy ạ.
L09: Người nhà: Từ hôm chủ nhật thì buồn ngủ ban ngày dữ dội ngủ gật khi lái xe, hôm kia thì đỡ hẳn rồi ạ.
L10: Người nhà: Em thì bụi phổi, nói thêm để bác sĩ biết ạ.
L11: Bác sĩ: Về thuốc thang mấy hôm nay, mấy hôm nay đã tự điều trị bằng thuốc gì ở nhà chưa nhỉ?
L12: Người nhà: Dạ thưa bác sĩ, bố em có nhỏ thuốc nhỏ mắt natri clorid hai giọt, dùng được mấy hôm nay ạ.
L13: Bác sĩ: Vậy thì, bác sĩ kiểm tra kỹ các vùng hạch ở cổ và dưới hàm nghen chú.
L14: Bác sĩ: Ghi nhận khi thăm khám: Thể trạng béo phì (BMI 29), cổ ngắn to, màn hầu thấp, khẩu cái mềm dài (Mallampati độ 4).
L15: Bác sĩ: Tôi nghĩ nhiều đến hội chứng ngưng thở khi ngủ do tắc nghẽn (OSA) mức độ nặng, nhưng chưa kết luận được. Phải có kết quả chụp X-quang đã.
L16: Bác sĩ: Chú đi làm chụp X-quang rồi quay lại đây.
L17: Bác sĩ: Bác sĩ sẽ kê salbutamol hai nhát, xịt khi cần nghen.
L18: Người nhà: Dạ đa tạ bác sĩ, em sẽ kiêng vận động mạnh vài ngày tới nghen, chào bác sĩ.
```
- **Đáp án mệnh đề (`dap_an`):**
  - `M01` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=ngủ ngáy rất to ngắt quãng có cơn nghẹt thở` | `moc=khoảng một tháng` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Bố em thấy xuất hiện biểu hiện ngủ ngáy rất to ngắt quãng có cơn nghẹt thở ngót nghét khoảng một tháng']`
  - `M02` [LÝ DO KHÁM BỆNH] `chu_the=bệnh nhân` | `noi_dung=ngủ ngáy rất to ngắt quãng có cơn nghẹt thở` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Bố em thấy xuất hiện biểu hiện ngủ ngáy rất to ngắt quãng có cơn nghẹt thở ngót nghét khoảng một tháng']`
  - `M03` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=khô miệng khi thức dậy` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['song song đó bố em còn thấy khô miệng khi thức dậy ạ']`
  - `M04` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=buồn ngủ ban ngày dữ dội ngủ gật khi lái xe` | `moc=từ hôm chủ nhật` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Từ hôm chủ nhật thì buồn ngủ ban ngày dữ dội ngủ gật khi lái xe']`
  - `M05` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=buồn ngủ ban ngày dữ dội ngủ gật khi lái xe` | `moc=hôm kia` | `phu_dinh=True` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=diễn biến` | `trich_dan=['hôm kia thì đỡ hẳn rồi ạ']`
  - `M06` [TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI] `chu_the=con gái` | `noi_dung=bụi phổi` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Em thì bụi phổi']`
  - `M07` [THUỐC ĐANG DÙNG] `chu_the=bệnh nhân` | `noi_dung=thuốc nhỏ mắt natri clorid` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['bố em có nhỏ thuốc nhỏ mắt natri clorid hai giọt, dùng được mấy hôm nay ạ']`
  - `M08` [KHÁM LÂM SÀNG] `chu_the=bệnh nhân` | `noi_dung=Thể trạng béo phì (BMI 29), cổ ngắn to, màn hầu thấp, khẩu cái mềm dài (Mallampati độ 4)` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Ghi nhận khi thăm khám: Thể trạng béo phì (BMI 29), cổ ngắn to, màn hầu thấp, khẩu cái mềm dài (Mallampati độ 4)']`
  - `M09` [CHẨN ĐOÁN] `chu_the=bệnh nhân` | `noi_dung=Hội chứng ngưng thở khi ngủ do tắc nghẽn (OSA) mức độ nặng` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=nghi ngờ` | `quan_he=None` | `trich_dan=['Tôi nghĩ nhiều đến hội chứng ngưng thở khi ngủ do tắc nghẽn (OSA) mức độ nặng']`
  - `M10` [KẾ HOẠCH ĐIỀU TRỊ] `chu_the=bệnh nhân` | `noi_dung=làm chụp X-quang` | `moc=None` | `phu_dinh=False` | `tinh_huong=kế hoạch` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Chú đi làm chụp X-quang rồi quay lại đây']`
  - `M11` [KẾ HOẠCH ĐIỀU TRỊ] `chu_the=bệnh nhân` | `noi_dung=kê salbutamol` | `moc=None` | `phu_dinh=False` | `tinh_huong=kế hoạch` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Bác sĩ sẽ kê salbutamol hai nhát, xịt khi cần nghen']`
- **Các lỗi phát hiện khi đọc ca này (2 lỗi):**
  - **L04-L05** — *Hỏi đáp xã giao lệch cặp (hỏi một đằng, đáp một nẻo)*: `Bác sĩ: Ngồi nghỉ ngơi ngoài khu vực chờ, chú có cần chỉnh lại hướng gió quạt không vậy ạ? / Người nhà: Dạ em thấy, ghế ngồi êm ái nên đợi không bị mỏi lưng ạ.`
  - **L08** — *Từ đệm `Dạ thưa đúng ạ` đặt trước câu kể triệu chứng/tiền sử*: `Người nhà: Dạ thưa đúng ạ, song song đó bố em còn thấy khô miệng khi thức dậy ạ.`

### Ca 04 — Mã: `hv_1421` (`hội chứng ống cổ tay`)
- **Thông tin ca:** `la_tre_em=False` | `nguoi_ke=None` | `lo_danh_tinh=False` | `boi_canh=kham_lan_dau` | `bay=[]` | `so_luot=12`
- **Lời thoại đầy đủ:**
```text
L01: Bác sĩ: Chào chị, tình trạng khó chịu này bắt đầu từ khi nào thế?
L02: Bệnh nhân: Dạ thưa đúng ạ, cơn đầu ngón cứ rần rần này em bị tầm khoảng một tháng nay.
L03: Bác sĩ: Liệu còn vấn đề gì, có triệu chứng nào khác đi kèm mà mình nhận thấy không?
L04: Bệnh nhân: Dạ em nghe bác sĩ, em còn xuất hiện đau cổ tay nữa bác sĩ ạ.
L05: Bác sĩ: Trước giờ, bạn có dị ứng với penicillin, aspirin hay loại thuốc nào không nhé?
L06: Bệnh nhân: Dạ chưa bác sĩ, tôi không có cơ địa dị ứng thuốc men gì cả nghen bác sĩ.
L07: Bác sĩ: Để tôi, chị nằm lên bàn khám giúp tôi giúp tôi nhé.
L08: Bác sĩ: Khám lâm sàng bước đầu thấy: Dấu Tinel dương tính ở cổ tay. rõ ràng.
L09: Bác sĩ: Kết luận bước đầu là: Hội chứng ống cổ tay. nhé.
L10: Bác sĩ: Kế hoạch dùng thuốc và theo dõi: Nẹp cổ tay ban đêm. Đo điện cơ. Hạn chế động tác lặp lại. nhé ạ.
L11: Bác sĩ: Đơn thuốc hôm nay tôi kê panadol 500 mg, uống khi cần nhé.
L12: Bệnh nhân: Dạ bác sĩ, em cảm ơn bác sĩ đã tư vấn cặn kẽ cho em nghen bác sĩ.
```
- **Đáp án mệnh đề (`dap_an`):**
  - `M01` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=tê ngón tay` | `moc=khoảng một tháng` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['cơn đầu ngón cứ rần rần này em bị tầm khoảng một tháng nay']`
  - `M02` [LÝ DO KHÁM BỆNH] `chu_the=bệnh nhân` | `noi_dung=tê ngón tay` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['cơn đầu ngón cứ rần rần này em bị tầm khoảng một tháng nay']`
  - `M03` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=đau cổ tay` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['em còn xuất hiện đau cổ tay nữa bác sĩ ạ']`
  - `M04` [DỊ ỨNG] `chu_the=bệnh nhân` | `noi_dung=dị ứng thuốc` | `moc=None` | `phu_dinh=True` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['bạn có dị ứng với penicillin, aspirin hay loại thuốc nào không nhé', 'tôi không có cơ địa dị ứng thuốc men gì cả nghen bác sĩ']`
  - `M05` [KHÁM LÂM SÀNG] `chu_the=bệnh nhân` | `noi_dung=Dấu Tinel dương tính ở cổ tay` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Khám lâm sàng bước đầu thấy: Dấu Tinel dương tính ở cổ tay']`
  - `M06` [CHẨN ĐOÁN] `chu_the=bệnh nhân` | `noi_dung=Hội chứng ống cổ tay` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Kết luận bước đầu là: Hội chứng ống cổ tay']`
  - `M07` [KẾ HOẠCH ĐIỀU TRỊ] `chu_the=bệnh nhân` | `noi_dung=Nẹp cổ tay ban đêm. Đo điện cơ. Hạn chế động tác lặp lại` | `moc=None` | `phu_dinh=False` | `tinh_huong=kế hoạch` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Kế hoạch dùng thuốc và theo dõi: Nẹp cổ tay ban đêm. Đo điện cơ. Hạn chế động tác lặp lại']`
  - `M08` [KẾ HOẠCH ĐIỀU TRỊ] `chu_the=bệnh nhân` | `noi_dung=kê panadol` | `moc=None` | `phu_dinh=False` | `tinh_huong=kế hoạch` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Đơn thuốc hôm nay tôi kê panadol 500 mg, uống khi cần nhé']`
- **Các lỗi phát hiện khi đọc ca này (7 lỗi):**
  - **L02** — *Từ đệm `Dạ thưa đúng ạ` đặt trước câu kể triệu chứng/tiền sử*: `Bệnh nhân: Dạ thưa đúng ạ, cơn đầu ngón cứ rần rần này em bị tầm khoảng một tháng nay.`
  - **L05** — *Tiểu từ đề nghị (`nhé/nha/nghen`) gắn vào câu hỏi `?`*: `Bác sĩ: Trước giờ, bạn có dị ứng với penicillin, aspirin hay loại thuốc nào không nhé?`
  - **L05** — *Bác sĩ gọi người bệnh/người nhà là `bạn` (lệch vai xưng hô)*: `Bác sĩ: Trước giờ, bạn có dị ứng với penicillin, aspirin hay loại thuốc nào không nhé?`
  - **L07** — *Lặp cụm `giúp tôi giúp tôi`*: `Bác sĩ: Để tôi, chị nằm lên bàn khám giúp tôi giúp tôi nhé.`
  - **L08** — *Cụm nhận xét thừa sau dấu chấm ở cuối câu*: `Bác sĩ: Khám lâm sàng bước đầu thấy: Dấu Tinel dương tính ở cổ tay. rõ ràng.`
  - **L09** — *Hạt đề nghị thừa sau dấu chấm (`. nhé.`, `. nha.`, `. nghen.`)*: `Bác sĩ: Kết luận bước đầu là: Hội chứng ống cổ tay. nhé.`
  - **L10** — *Hạt đề nghị thừa sau dấu chấm (`. nhé.`, `. nha.`, `. nghen.`)*: `Bác sĩ: Kế hoạch dùng thuốc và theo dõi: Nẹp cổ tay ban đêm. Đo điện cơ. Hạn chế động tác lặp lại. nhé ạ.`

### Ca 05 — Mã: `hv_4592` (`sa sút trí tuệ mạch máu`)
- **Thông tin ca:** `la_tre_em=False` | `nguoi_ke=chồng` | `lo_danh_tinh=True` | `boi_canh=cho_ket_qua` | `bay=['dien_bien', 'dinh_chinh', 'nguoi_nha_ke_ho']` | `so_luot=22`
- **Lời thoại đầy đủ:**
```text
L01: Bác sĩ: Mời em ngồi, bác sĩ nghe em kể về tình hình sức khỏe của em đây ạ.
L02: Bác sĩ: Bác sĩ hỏi một chút, em là người nhà gì của em ấy vậy ạ?
L03: Người nhà: Vâng ạ, em là chồng đưa em ấy đi khám bác sĩ ạ.
L04: Bác sĩ: Bác sĩ vệ sinh tay khử khuẩn một lát nhé, em có cần lấy thêm khẩu trang y tế mới không?
L05: Người nhà: Dạ thưa bác sĩ, em đeo khẩu trang y tế quen rồi nên thấy rất bình thường.
L06: Bác sĩ: Khâu tiếp đón ở bàn lễ tân, các bạn nhân viên hướng dẫn có chu đáo không em ạ?
L07: Người nhà: Dạ thưa bác sĩ, em đặt lịch hẹn trước trên mạng nên vào thẳng luôn ạ.
L08: Người nhà: Nửa năm rồi nay vợ em bị suy giảm trí nhớ và khả năng tính toán tiến triển từng bậc sau các biến cố mạch não suốt.
L09: Người nhà: Em nói lại cho đúng, hai tháng nay chứ không phải nửa năm rồi ạ.
L10: Bác sĩ: Còn điều gì về sức khỏe mấy hôm nay mà mình chưa kể không không ạ?
L11: Người nhà: Vâng em nghe, vợ em thấy có thêm rối loạn giấc ngủ đêm lộn ngày, đi lại chậm chạp vụng về mấy hôm nay.
L12: Người nhà: Hôm qua thì lú lẫn hay quên đường về, sáng nay thì đỡ hẳn rồi.
L13: Bác sĩ: Trước giờ, mình có đang theo dõi điều trị ở chuyên khoa nào khác không vậy ạ?
L14: Người nhà: Dạ thưa bác sĩ, vợ em có thiếu máu ạ.
L15: Bác sĩ: Bác sĩ cần kiểm tra kỹ chỗ này, trước giờ uống bất kỳ loại thuốc nào có từng bị dị ứng chưa không?
L16: Người nhà: Vâng chưa ạ, cơ thể đáp ứng thuốc tốt, không có tiền sử dị ứng đâu ạ.
L17: Bác sĩ: Bước tiếp theo, để tôi kiểm tra kỹ lại một lượt xem sao giúp tôi nhé.
L18: Bác sĩ: Khám lâm sàng ghi nhận: Điểm đánh giá nhận thức Mini-Mental State Examination (MMSE) giảm còn 18/30 điểm, có dấu hiệu phản xạ bệnh lý bó tháp nhẹ. cần theo dõi.
L19: Bác sĩ: Tôi nghĩ nhiều đến sa sút trí tuệ mạch máu (Vascular dementia) sau nhồi máu não nhiều ổ, nhưng chưa kết luận được. Phải có kết quả xét nghiệm nước tiểu đã nhé.
L20: Bác sĩ: Em đi làm xét nghiệm nước tiểu rồi quay lại đây nhé.
L21: Bác sĩ: Bác sĩ quyết định kê augmentin 1 g, uống ngày hai lần uống đúng giờ nhé.
L22: Người nhà: Dạ tôi rõ rồi, em đã hiểu rõ liều lượng và cách dùng thuốc, cảm ơn bác sĩ đã giúp đỡ ạ.
```
- **Đáp án mệnh đề (`dap_an`):**
  - `M01` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=suy giảm trí nhớ và khả năng tính toán tiến triển từng bậc sau các biến cố mạch não` | `moc=hai tháng nay` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=đính chính` | `trich_dan=['Nửa năm rồi nay vợ em bị suy giảm trí nhớ và khả năng tính toán tiến triển từng bậc sau các biến cố mạch não suốt', 'hai tháng nay chứ không phải nửa năm rồi ạ']`
  - `M02` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=suy giảm trí nhớ và khả năng tính toán tiến triển từng bậc sau các biến cố mạch não` | `moc=nửa năm rồi` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Nửa năm rồi nay vợ em bị suy giảm trí nhớ và khả năng tính toán tiến triển từng bậc sau các biến cố mạch não suốt', 'hai tháng nay chứ không phải nửa năm rồi ạ']`
  - `M03` [LÝ DO KHÁM BỆNH] `chu_the=bệnh nhân` | `noi_dung=suy giảm trí nhớ và khả năng tính toán tiến triển từng bậc sau các biến cố mạch não` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Nửa năm rồi nay vợ em bị suy giảm trí nhớ và khả năng tính toán tiến triển từng bậc sau các biến cố mạch não suốt']`
  - `M04` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=rối loạn giấc ngủ đêm lộn ngày` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['vợ em thấy có thêm rối loạn giấc ngủ đêm lộn ngày']`
  - `M05` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=đi lại chậm chạp vụng về` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['đi lại chậm chạp vụng về mấy hôm nay']`
  - `M06` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=lú lẫn hay quên đường về` | `moc=hôm qua` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Hôm qua thì lú lẫn hay quên đường về']`
  - `M07` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=lú lẫn hay quên đường về` | `moc=sáng nay` | `phu_dinh=True` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=diễn biến` | `trich_dan=['sáng nay thì đỡ hẳn rồi']`
  - `M08` [TIỀN SỬ BỆNH] `chu_the=bệnh nhân` | `noi_dung=thiếu máu` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['vợ em có thiếu máu ạ']`
  - `M09` [DỊ ỨNG] `chu_the=bệnh nhân` | `noi_dung=dị ứng thuốc` | `moc=None` | `phu_dinh=True` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['trước giờ uống bất kỳ loại thuốc nào có từng bị dị ứng chưa không', 'cơ thể đáp ứng thuốc tốt, không có tiền sử dị ứng đâu ạ']`
  - `M10` [KHÁM LÂM SÀNG] `chu_the=bệnh nhân` | `noi_dung=Điểm đánh giá nhận thức Mini-Mental State Examination (MMSE) giảm còn 18/30 điểm, có dấu hiệu phản xạ bệnh lý bó tháp nhẹ` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Khám lâm sàng ghi nhận: Điểm đánh giá nhận thức Mini-Mental State Examination (MMSE) giảm còn 18/30 điểm, có dấu hiệu phản xạ bệnh lý bó tháp nhẹ']`
  - `M11` [CHẨN ĐOÁN] `chu_the=bệnh nhân` | `noi_dung=Sa sút trí tuệ mạch máu (Vascular dementia) sau nhồi máu não nhiều ổ` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=nghi ngờ` | `quan_he=None` | `trich_dan=['Tôi nghĩ nhiều đến sa sút trí tuệ mạch máu (Vascular dementia) sau nhồi máu não nhiều ổ']`
  - `M12` [KẾ HOẠCH ĐIỀU TRỊ] `chu_the=bệnh nhân` | `noi_dung=làm xét nghiệm nước tiểu` | `moc=None` | `phu_dinh=False` | `tinh_huong=kế hoạch` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Em đi làm xét nghiệm nước tiểu rồi quay lại đây nhé']`
  - `M13` [KẾ HOẠCH ĐIỀU TRỊ] `chu_the=bệnh nhân` | `noi_dung=kê augmentin` | `moc=None` | `phu_dinh=False` | `tinh_huong=kế hoạch` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Bác sĩ quyết định kê augmentin 1 g, uống ngày hai lần uống đúng giờ nhé']`
- **Các lỗi phát hiện khi đọc ca này (8 lỗi):**
  - **L06** — *Bác sĩ gọi người bệnh/người nhà là `bạn` (lệch vai xưng hô)*: `Bác sĩ: Khâu tiếp đón ở bàn lễ tân, các bạn nhân viên hướng dẫn có chu đáo không em ạ?`
  - **L08** — *Lặp từ thời gian `nay nay` / `rồi nay` / `nay rồi nay`*: `Người nhà: Nửa năm rồi nay vợ em bị suy giảm trí nhớ và khả năng tính toán tiến triển từng bậc sau các biến cố mạch não suốt.`
  - **L10** — *Lặp từ nghi vấn `không không` / `chưa không`*: `Bác sĩ: Còn điều gì về sức khỏe mấy hôm nay mà mình chưa kể không không ạ?`
  - **L11** — *Từ đệm mở đầu lệch đại từ tự xưng với phần thân câu*: `Người nhà: Vâng em nghe, vợ em thấy có thêm rối loạn giấc ngủ đêm lộn ngày, đi lại chậm chạp vụng về mấy hôm nay.`
  - **L15** — *Lặp từ nghi vấn `không không` / `chưa không`*: `Bác sĩ: Bác sĩ cần kiểm tra kỹ chỗ này, trước giờ uống bất kỳ loại thuốc nào có từng bị dị ứng chưa không?`
  - **L18** — *Cụm nhận xét thừa sau dấu chấm ở cuối câu*: `Bác sĩ: Khám lâm sàng ghi nhận: Điểm đánh giá nhận thức Mini-Mental State Examination (MMSE) giảm còn 18/30 điểm, có dấu hiệu phản xạ bệnh lý bó tháp nhẹ. cần theo dõi.`
  - **L21** — *Ghép thừa `uống ngày ... lần uống đúng giờ`*: `Bác sĩ: Bác sĩ quyết định kê augmentin 1 g, uống ngày hai lần uống đúng giờ nhé.`
  - **L22** — *Xung đột đại từ tự xưng trong cùng một câu (`tôi` vs `em`)*: `Người nhà: Dạ tôi rõ rồi, em đã hiểu rõ liều lượng và cách dùng thuốc, cảm ơn bác sĩ đã giúp đỡ ạ.`

### Ca 06 — Mã: `hv_0728` (`bàng quang tăng hoạt OAB`)
- **Thông tin ca:** `la_tre_em=False` | `nguoi_ke=None` | `lo_danh_tinh=False` | `boi_canh=kham_lan_dau` | `bay=['dai_tu_ho_hang', 'dinh_chinh']` | `so_luot=23`
- **Lời thoại đầy đủ:**
```text
L01: Bác sĩ: Chị kể rõ cho bác sĩ nghe xem tình trạng hiện tại thế nào ạ.
L02: Bác sĩ: Bác sĩ muốn xác nhận trước, Chị đi khám cho mình phải không phải không ạ?
L03: Bệnh nhân: Dạ thưa bác sĩ, hôm nay em đi kiểm tra sức khỏe ạ.
L04: Bác sĩ: Lúc tới phòng khám, biển chỉ dẫn vào phòng khám có dễ nhìn không chị thế ạ?
L05: Bệnh nhân: Dạ, biển chỉ dẫn to rõ ngoài cổng nên em tìm thấy ngay ạ.
L06: Bác sĩ: Từ sáng tới giờ, chị đã kịp ăn lót dạ món gì nhẹ nhàng chưa?
L07: Bệnh nhân: Dạ thưa bác sĩ, em có mang theo bình nước ấm uống suốt dọc đường rồi bác sĩ ạ.
L08: Bệnh nhân: Từ độ hai tháng nay trước là em bắt đầu tiểu gấp cảm giác buồn tiểu dữ dội khẩn cấp không thể nhịn được phải chạy vào nhà vệ sinh ngay.
L09: Bệnh nhân: À không, em nói nhầm, vài năm rồi chứ không phải hai tháng nay.
L10: Bác sĩ: Bác sĩ muốn hỏi kỹ thêm, ngoài các triệu chứng trên thì còn dấu hiệu nào khác đi kèm không vậy ạ?
L11: Bệnh nhân: Vâng tôi nghe đây ạ, em thấy có thêm xét nghiệm tổng phân tích nước tiểu và cấy nước tiểu hoàn toàn bình thường không có nhiễm trùng, thang điểm bảng câu hỏi oab-q đánh giá chất lượng cuộc sống suy giảm nghiêm trọng mấy hôm nay.
L12: Bác sĩ: Bác sĩ cần hỏi về bệnh sử cũ một chút, sức khỏe của mình từ nhỏ đến giờ có vấn đề gì đáng lưu ý không nhỉ?
L13: Bệnh nhân: Vâng ạ, em có viêm khớp.
L14: Bác sĩ: Bạn có mẫn cảm đặc biệt với thành phần thuốc nào không không ạ?
L15: Bệnh nhân: Dạ không, chưa bao giờ bị nổi mề đay hay ngứa khi dùng thuốc đâu.
L16: Bác sĩ: Từ lúc phát bệnh đến giờ, ở nhà mình đã dùng thuốc hạ sốt, giảm đau hay thuốc gì chưa không ạ?
L17: Bệnh nhân: Dạ tôi không, chưa uống loại thuốc nào ở nhà xưa nay đâu ạ.
L18: Bác sĩ: Để xem xét kỹ hơn, tôi ấn nhẹ vào vùng này xem có đau tức không nghen chị.
L19: Bác sĩ: Tôi vừa khám xong: Khám bụng bình thường, cầu bàng quang âm tính, thăm trực tràng tiền liệt tuyến bình thường. nghen.
L20: Bác sĩ: Tình trạng này hướng tới: Hội chứng bàng quang tăng hoạt OAB thể ướt có són tiểu gấp. nhé.
L21: Bác sĩ: Kế hoạch xử trí cụ thể: Tập luyện bàng quang kéo dài khoảng cách giữa các lần đi tiểu và bài tập cơ sàn chậu Kegel. Thuốc kháng muscarinic solifenacin hoặc đồng vận beta 3 mirabegron. nghen.
L22: Bác sĩ: Đơn thuốc hôm nay tôi kê augmentin 625 mg, uống ngày hai lần nhé ạ.
L23: Bệnh nhân: Vâng, em xin ghi nhận lời dặn của bác sĩ, cảm ơn bác sĩ nhiều ạ, chào bác sĩ.
```
- **Đáp án mệnh đề (`dap_an`):**
  - `M01` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=tiểu gấp cảm giác buồn tiểu dữ dội khẩn cấp không thể nhịn được phải chạy vào nhà vệ sinh ngay` | `moc=vài năm rồi` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=đính chính` | `trich_dan=['Từ độ hai tháng nay trước là em bắt đầu tiểu gấp cảm giác buồn tiểu dữ dội khẩn cấp không thể nhịn được phải chạy vào nhà vệ sinh ngay', 'vài năm rồi chứ không phải hai tháng nay']`
  - `M02` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=tiểu gấp cảm giác buồn tiểu dữ dội khẩn cấp không thể nhịn được phải chạy vào nhà vệ sinh ngay` | `moc=hai tháng nay` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Từ độ hai tháng nay trước là em bắt đầu tiểu gấp cảm giác buồn tiểu dữ dội khẩn cấp không thể nhịn được phải chạy vào nhà vệ sinh ngay', 'vài năm rồi chứ không phải hai tháng nay']`
  - `M03` [LÝ DO KHÁM BỆNH] `chu_the=bệnh nhân` | `noi_dung=tiểu gấp cảm giác buồn tiểu dữ dội khẩn cấp không thể nhịn được phải chạy vào nhà vệ sinh ngay` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Từ độ hai tháng nay trước là em bắt đầu tiểu gấp cảm giác buồn tiểu dữ dội khẩn cấp không thể nhịn được phải chạy vào nhà vệ sinh ngay']`
  - `M04` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=xét nghiệm tổng phân tích nước tiểu và cấy nước tiểu hoàn toàn bình thường không có nhiễm trùng` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['em thấy có thêm xét nghiệm tổng phân tích nước tiểu và cấy nước tiểu hoàn toàn bình thường không có nhiễm trùng']`
  - `M05` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=thang điểm bảng câu hỏi oab-q đánh giá chất lượng cuộc sống suy giảm nghiêm trọng` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['thang điểm bảng câu hỏi oab-q đánh giá chất lượng cuộc sống suy giảm nghiêm trọng mấy hôm nay']`
  - `M06` [TIỀN SỬ BỆNH] `chu_the=bệnh nhân` | `noi_dung=viêm khớp` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['em có viêm khớp']`
  - `M07` [DỊ ỨNG] `chu_the=bệnh nhân` | `noi_dung=dị ứng thuốc` | `moc=None` | `phu_dinh=True` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Bạn có mẫn cảm đặc biệt với thành phần thuốc nào không không ạ', 'chưa bao giờ bị nổi mề đay hay ngứa khi dùng thuốc đâu']`
  - `M08` [KHÁM LÂM SÀNG] `chu_the=bệnh nhân` | `noi_dung=Khám bụng bình thường, cầu bàng quang âm tính, thăm trực tràng tiền liệt tuyến bình thường` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Tôi vừa khám xong: Khám bụng bình thường, cầu bàng quang âm tính, thăm trực tràng tiền liệt tuyến bình thường']`
  - `M09` [CHẨN ĐOÁN] `chu_the=bệnh nhân` | `noi_dung=Hội chứng bàng quang tăng hoạt OAB thể ướt có són tiểu gấp` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Tình trạng này hướng tới: Hội chứng bàng quang tăng hoạt OAB thể ướt có són tiểu gấp']`
  - `M10` [KẾ HOẠCH ĐIỀU TRỊ] `chu_the=bệnh nhân` | `noi_dung=Tập luyện bàng quang kéo dài khoảng cách giữa các lần đi tiểu và bài tập cơ sàn chậu Kegel. Thuốc kháng muscarinic solifenacin hoặc đồng vận beta 3 mirabegron` | `moc=None` | `phu_dinh=False` | `tinh_huong=kế hoạch` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Kế hoạch xử trí cụ thể: Tập luyện bàng quang kéo dài khoảng cách giữa các lần đi tiểu và bài tập cơ sàn chậu Kegel. Thuốc kháng muscarinic solifenacin hoặc đồng vận beta 3 mirabegron']`
  - `M11` [KẾ HOẠCH ĐIỀU TRỊ] `chu_the=bệnh nhân` | `noi_dung=kê augmentin` | `moc=None` | `phu_dinh=False` | `tinh_huong=kế hoạch` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Đơn thuốc hôm nay tôi kê augmentin 625 mg, uống ngày hai lần nhé ạ']`
- **Các lỗi phát hiện khi đọc ca này (10 lỗi):**
  - **L02** — *Lặp cụm `phải không phải không`*: `Bác sĩ: Bác sĩ muốn xác nhận trước, Chị đi khám cho mình phải không phải không ạ?`
  - **L06-L07** — *Hỏi đáp xã giao lệch cặp (hỏi một đằng, đáp một nẻo)*: `Bác sĩ: Từ sáng tới giờ, chị đã kịp ăn lót dạ món gì nhẹ nhàng chưa? / Bệnh nhân: Dạ thưa bác sĩ, em có mang theo bình nước ấm uống suốt dọc đường rồi bác sĩ ạ.`
  - **L08** — *Ghép sai mốc thời gian `từ độ ... nay/rồi trước`*: `Bệnh nhân: Từ độ hai tháng nay trước là em bắt đầu tiểu gấp cảm giác buồn tiểu dữ dội khẩn cấp không thể nhịn được phải chạy vào nhà vệ sinh ngay.`
  - **L11** — *Từ đệm mở đầu lệch đại từ tự xưng với phần thân câu*: `Bệnh nhân: Vâng tôi nghe đây ạ, em thấy có thêm xét nghiệm tổng phân tích nước tiểu và cấy nước tiểu hoàn toàn bình thường không có nhiễm trùng, thang điểm bảng câu hỏi oab-q đánh giá chất lượng cuộc sống suy giảm nghiêm trọng mấy hôm nay.`
  - **L14** — *Lặp từ nghi vấn `không không` / `chưa không`*: `Bác sĩ: Bạn có mẫn cảm đặc biệt với thành phần thuốc nào không không ạ?`
  - **L14** — *Bác sĩ gọi người bệnh/người nhà là `bạn` (lệch vai xưng hô)*: `Bác sĩ: Bạn có mẫn cảm đặc biệt với thành phần thuốc nào không không ạ?`
  - **L16** — *Lặp từ nghi vấn `không không` / `chưa không`*: `Bác sĩ: Từ lúc phát bệnh đến giờ, ở nhà mình đã dùng thuốc hạ sốt, giảm đau hay thuốc gì chưa không ạ?`
  - **L19** — *Hạt đề nghị thừa sau dấu chấm (`. nhé.`, `. nha.`, `. nghen.`)*: `Bác sĩ: Tôi vừa khám xong: Khám bụng bình thường, cầu bàng quang âm tính, thăm trực tràng tiền liệt tuyến bình thường. nghen.`
  - **L20** — *Hạt đề nghị thừa sau dấu chấm (`. nhé.`, `. nha.`, `. nghen.`)*: `Bác sĩ: Tình trạng này hướng tới: Hội chứng bàng quang tăng hoạt OAB thể ướt có són tiểu gấp. nhé.`
  - **L21** — *Hạt đề nghị thừa sau dấu chấm (`. nhé.`, `. nha.`, `. nghen.`)*: `Bác sĩ: Kế hoạch xử trí cụ thể: Tập luyện bàng quang kéo dài khoảng cách giữa các lần đi tiểu và bài tập cơ sàn chậu Kegel. Thuốc kháng muscarinic solifenacin hoặc đồng vận beta 3 mirabegron. nghen.`

### Ca 07 — Mã: `hv_4419` (`tay chân miệng thể 2b`)
- **Thông tin ca:** `la_tre_em=True` | `nguoi_ke=bà ngoại` | `lo_danh_tinh=True` | `boi_canh=kham_lan_dau` | `bay=['nguoi_ke_benh_minh', 'nguoi_nha_ke_ho']` | `so_luot=20`
- **Lời thoại đầy đủ:**
```text
L01: Bác sĩ: Mời bà ngồi xuống, bà thấy bé có triệu chứng gì nặng nhất?
L02: Bác sĩ: mình có quan hệ gia đình thế nào với bé thế ạ?
L03: Người nhà: Dạ vâng, bé là người thân của tôi, tôi là bà ngoại bác sĩ ạ.
L04: Bác sĩ: Hôm nay đi khám, Bé đưa phiếu thông tin cá nhân cho bác sĩ xem nhé ạ?
L05: Người nhà: Vâng ạ, em đã kẹp sẵn sổ khám bệnh cũ và kết quả xét nghiệm trong túi.
L06: Người nhà: Cháu tôi chịu đựng tình trạng giật mình chới với trên hai lần trong 30 phút lúc thiu thiu ngủ cũng từ hôm kia nay ạ.
L07: Bác sĩ: Trong mấy ngày nay, bạn có thấy kèm theo biểu hiện bất thường nào khác không không ạ?
L08: Người nhà: Thưa bác sĩ, cháu tôi còn run chi đi loạng choạng bước chân không vững nữa ạ.
L09: Bác sĩ: Có bệnh lý nền nào đang phải theo dõi định kỳ không không ạ?
L10: Người nhà: Vâng thưa bác sĩ, cháu tôi có viêm tai giữa tái đi tái lại ạ.
L11: Người nhà: Tôi bị thoái hóa khớp gối mấy năm nay rồi ạ.
L12: Bác sĩ: À, nhân tiện, bạn có dị ứng với penicillin, aspirin hay loại thuốc nào không hả bạn?
L13: Người nhà: Dạ vâng ạ, có dị ứng sulfamid từ mấy năm trước rồi.
L14: Bác sĩ: Nhân tiện thì, mấy hôm nay đã tự điều trị bằng thuốc gì ở nhà chưa vậy?
L15: Người nhà: Vâng thưa bác sĩ, cháu tôi có uống smecta một gói, ngày hai lần, dùng được một tháng nay ạ.
L16: Bác sĩ: Qua lời kể vừa rồi, Bé há to miệng cho tôi soi đèn xem họng xem thế nào nhé.
L17: Bác sĩ: Kiểm tra kỹ cho thấy: Trẻ bứt rứt, run chi độ 1, mạch quay rõ 155 l/p, SpO2 97%. nghen.
L18: Bác sĩ: Tôi xác định tình trạng này là: Bệnh tay chân miệng độ 2b nhóm một. rõ ràng.
L19: Bác sĩ: Bác sĩ sẽ tiến hành: Nhập viện khoa cấp cứu hồi sức nhi, truyền phenobarbital chống co giật. Theo dõi sát huyết áp mạch và tri giác mỗi 2 giờ. theo đúng hướng dẫn.
L20: Người nhà: Vâng bác sĩ, tôi thấy an tâm hơn nhiều rồi, cảm ơn bác sĩ đã giúp đỡ nhé ạ.
```
- **Đáp án mệnh đề (`dap_an`):**
  - `M01` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=giật mình chới với trên hai lần trong 30 phút lúc thiu thiu ngủ` | `moc=từ hôm kia` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Cháu tôi chịu đựng tình trạng giật mình chới với trên hai lần trong 30 phút lúc thiu thiu ngủ cũng từ hôm kia nay ạ']`
  - `M02` [LÝ DO KHÁM BỆNH] `chu_the=bệnh nhân` | `noi_dung=giật mình chới với trên hai lần trong 30 phút lúc thiu thiu ngủ` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Cháu tôi chịu đựng tình trạng giật mình chới với trên hai lần trong 30 phút lúc thiu thiu ngủ cũng từ hôm kia nay ạ']`
  - `M03` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=run chi đi loạng choạng bước chân không vững` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['cháu tôi còn run chi đi loạng choạng bước chân không vững nữa ạ']`
  - `M04` [TIỀN SỬ BỆNH] `chu_the=bệnh nhân` | `noi_dung=viêm tai giữa tái đi tái lại` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['cháu tôi có viêm tai giữa tái đi tái lại ạ']`
  - `M05` [TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI] `chu_the=bà ngoại` | `noi_dung=thoái hóa khớp gối` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Tôi bị thoái hóa khớp gối mấy năm nay rồi ạ']`
  - `M06` [DỊ ỨNG] `chu_the=bệnh nhân` | `noi_dung=dị ứng sulfamid` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['có dị ứng sulfamid từ mấy năm trước rồi']`
  - `M07` [THUỐC ĐANG DÙNG] `chu_the=bệnh nhân` | `noi_dung=smecta` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['cháu tôi có uống smecta một gói, ngày hai lần, dùng được một tháng nay ạ']`
  - `M08` [KHÁM LÂM SÀNG] `chu_the=bệnh nhân` | `noi_dung=Trẻ bứt rứt, run chi độ 1, mạch quay rõ 155 l/p, SpO2 97%` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Kiểm tra kỹ cho thấy: Trẻ bứt rứt, run chi độ 1, mạch quay rõ 155 l/p, SpO2 97%']`
  - `M09` [CHẨN ĐOÁN] `chu_the=bệnh nhân` | `noi_dung=Bệnh tay chân miệng độ 2b nhóm một` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Tôi xác định tình trạng này là: Bệnh tay chân miệng độ 2b nhóm một']`
  - `M10` [KẾ HOẠCH ĐIỀU TRỊ] `chu_the=bệnh nhân` | `noi_dung=Nhập viện khoa cấp cứu hồi sức nhi, truyền phenobarbital chống co giật. Theo dõi sát huyết áp mạch và tri giác mỗi 2 giờ` | `moc=None` | `phu_dinh=False` | `tinh_huong=kế hoạch` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Bác sĩ sẽ tiến hành: Nhập viện khoa cấp cứu hồi sức nhi, truyền phenobarbital chống co giật. Theo dõi sát huyết áp mạch và tri giác mỗi 2 giờ']`
- **Các lỗi phát hiện khi đọc ca này (10 lỗi):**
  - **L04** — *Tiểu từ đề nghị (`nhé/nha/nghen`) gắn vào câu hỏi `?`*: `Bác sĩ: Hôm nay đi khám, Bé đưa phiếu thông tin cá nhân cho bác sĩ xem nhé ạ?`
  - **L04-L05** — *Hỏi đáp xã giao lệch cặp (hỏi một đằng, đáp một nẻo)*: `Bác sĩ: Hôm nay đi khám, Bé đưa phiếu thông tin cá nhân cho bác sĩ xem nhé ạ? / Người nhà: Vâng ạ, em đã kẹp sẵn sổ khám bệnh cũ và kết quả xét nghiệm trong túi.`
  - **L07** — *Lặp từ nghi vấn `không không` / `chưa không`*: `Bác sĩ: Trong mấy ngày nay, bạn có thấy kèm theo biểu hiện bất thường nào khác không không ạ?`
  - **L07** — *Bác sĩ gọi người bệnh/người nhà là `bạn` (lệch vai xưng hô)*: `Bác sĩ: Trong mấy ngày nay, bạn có thấy kèm theo biểu hiện bất thường nào khác không không ạ?`
  - **L09** — *Lặp từ nghi vấn `không không` / `chưa không`*: `Bác sĩ: Có bệnh lý nền nào đang phải theo dõi định kỳ không không ạ?`
  - **L11** — *Lặp từ thời gian `nay nay` / `rồi nay` / `nay rồi nay`*: `Người nhà: Tôi bị thoái hóa khớp gối mấy năm nay rồi ạ.`
  - **L12** — *Bác sĩ gọi người bệnh/người nhà là `bạn` (lệch vai xưng hô)*: `Bác sĩ: À, nhân tiện, bạn có dị ứng với penicillin, aspirin hay loại thuốc nào không hả bạn?`
  - **L17** — *Hạt đề nghị thừa sau dấu chấm (`. nhé.`, `. nha.`, `. nghen.`)*: `Bác sĩ: Kiểm tra kỹ cho thấy: Trẻ bứt rứt, run chi độ 1, mạch quay rõ 155 l/p, SpO2 97%. nghen.`
  - **L18** — *Cụm nhận xét thừa sau dấu chấm ở cuối câu*: `Bác sĩ: Tôi xác định tình trạng này là: Bệnh tay chân miệng độ 2b nhóm một. rõ ràng.`
  - **L19** — *Cụm nhận xét thừa sau dấu chấm ở cuối câu*: `Bác sĩ: Bác sĩ sẽ tiến hành: Nhập viện khoa cấp cứu hồi sức nhi, truyền phenobarbital chống co giật. Theo dõi sát huyết áp mạch và tri giác mỗi 2 giờ. theo đúng hướng dẫn.`

### Ca 08 — Mã: `hv_3092` (`viêm tụy mạn sỏi tụy`)
- **Thông tin ca:** `la_tre_em=False` | `nguoi_ke=None` | `lo_danh_tinh=False` | `boi_canh=kham_lan_dau` | `bay=['bo_sung', 'dien_bien']` | `so_luot=15`
- **Lời thoại đầy đủ:**
```text
L01: Bác sĩ: Cô nghỉ ngơi một chút rồi nói cho bác sĩ biết triệu chứng chính nhé.
L02: Bác sĩ: Bác sĩ vệ sinh tay khử khuẩn một lát nhé, cô có thấy ngột ngạt hay khó thở khi đeo khẩu trang không nhé ạ?
L03: Bệnh nhân: Dạ thưa bác sĩ, ngồi chờ một chút không sao đâu bác sĩ ạ.
L04: Bệnh nhân: Tôi cảm giác đại tiện phân mỡ phân sống nổi váng mỡ vàng óng trên mặt nước bồn cầu xuất hiện liên miên hơn một năm nay ạ.
L05: Bác sĩ: Bên cạnh đó, ngoài ra còn triệu chứng nào làm mình lo lắng nữa không nhỉ?
L06: Bệnh nhân: Vâng thưa bác sĩ, tôi thấy kèm theo triệu chứng tiền sử uống rượu bia nghiện rượu trên mười năm liên tục khó ở.
L07: Bệnh nhân: Tiền sử uống rượu bia nghiện rượu trên mười năm liên tục thì nặng hơn sau khi ăn ạ.
L08: Bệnh nhân: Từ hôm chủ nhật thì hình ảnh sỏi vôi hóa nhu mô và ống tụy rải rác trên phim xquang bụng không chuẩn bị, chiều hôm qua thì đỡ hẳn rồi ạ.
L09: Bác sĩ: Quay lại tiền sử trước đây, đã từng đi khám tổng quát hay phát hiện bệnh gì trước đây chưa vậy ạ?
L10: Bệnh nhân: Vâng, tôi có nhức nửa bên đầu ạ.
L11: Bác sĩ: Ngay sau đây, tôi ấn nhẹ vào vùng này xem có đau tức không nhé.
L12: Bác sĩ: Bác sĩ xem xét trực tiếp thấy: Thể trạng gầy đét, da khô bọc xương, bụng mềm ấn tức sâu vùng tụy thượng vị. đáng lưu ý.
L13: Bác sĩ: Khả năng cao mình đang bị: Viêm tụy mạn tính có sỏi ống tụy do nghiện rượu.
L14: Bác sĩ: Bác sĩ đề ra phác đồ: Bổ sung men tụy pancreatin liều cao uống trong bữa ăn, kiểm soát đường huyết bằng insulin. Cai rượu tuyệt đối và nội soi tán sỏi tụy qua ercp. nghen.
L15: Bệnh nhân: Thưa bác sĩ, tôi đã hiểu cặn kẽ hướng điều trị rồi, cảm ơn bác sĩ rất nhiều ạ, chào bác sĩ tôi về.
```
- **Đáp án mệnh đề (`dap_an`):**
  - `M01` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=đại tiện phân mỡ phân sống nổi váng mỡ vàng óng trên mặt nước bồn cầu` | `moc=hơn một năm` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Tôi cảm giác đại tiện phân mỡ phân sống nổi váng mỡ vàng óng trên mặt nước bồn cầu xuất hiện liên miên hơn một năm nay ạ']`
  - `M02` [LÝ DO KHÁM BỆNH] `chu_the=bệnh nhân` | `noi_dung=đại tiện phân mỡ phân sống nổi váng mỡ vàng óng trên mặt nước bồn cầu` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Tôi cảm giác đại tiện phân mỡ phân sống nổi váng mỡ vàng óng trên mặt nước bồn cầu xuất hiện liên miên hơn một năm nay ạ']`
  - `M03` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=tiền sử uống rượu bia nghiện rượu trên mười năm liên tục` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['tôi thấy kèm theo triệu chứng tiền sử uống rượu bia nghiện rượu trên mười năm liên tục khó ở', 'Tiền sử uống rượu bia nghiện rượu trên mười năm liên tục thì nặng hơn sau khi ăn ạ']`
  - `M04` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=tiền sử uống rượu bia nghiện rượu trên mười năm liên tục nặng hơn sau khi ăn` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=bổ sung` | `trich_dan=['Tiền sử uống rượu bia nghiện rượu trên mười năm liên tục thì nặng hơn sau khi ăn ạ']`
  - `M05` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=hình ảnh sỏi vôi hóa nhu mô và ống tụy rải rác trên phim xquang bụng không chuẩn bị` | `moc=từ hôm chủ nhật` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Từ hôm chủ nhật thì hình ảnh sỏi vôi hóa nhu mô và ống tụy rải rác trên phim xquang bụng không chuẩn bị']`
  - `M06` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=hình ảnh sỏi vôi hóa nhu mô và ống tụy rải rác trên phim xquang bụng không chuẩn bị` | `moc=chiều hôm qua` | `phu_dinh=True` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=diễn biến` | `trich_dan=['chiều hôm qua thì đỡ hẳn rồi ạ']`
  - `M07` [TIỀN SỬ BỆNH] `chu_the=bệnh nhân` | `noi_dung=đau nửa đầu` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['tôi có nhức nửa bên đầu ạ']`
  - `M08` [KHÁM LÂM SÀNG] `chu_the=bệnh nhân` | `noi_dung=Thể trạng gầy đét, da khô bọc xương, bụng mềm ấn tức sâu vùng tụy thượng vị` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Bác sĩ xem xét trực tiếp thấy: Thể trạng gầy đét, da khô bọc xương, bụng mềm ấn tức sâu vùng tụy thượng vị']`
  - `M09` [CHẨN ĐOÁN] `chu_the=bệnh nhân` | `noi_dung=Viêm tụy mạn tính có sỏi ống tụy do nghiện rượu` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Khả năng cao mình đang bị: Viêm tụy mạn tính có sỏi ống tụy do nghiện rượu']`
  - `M10` [KẾ HOẠCH ĐIỀU TRỊ] `chu_the=bệnh nhân` | `noi_dung=Bổ sung men tụy pancreatin liều cao uống trong bữa ăn, kiểm soát đường huyết bằng insulin. Cai rượu tuyệt đối và nội soi tán sỏi tụy qua ercp` | `moc=None` | `phu_dinh=False` | `tinh_huong=kế hoạch` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Bác sĩ đề ra phác đồ: Bổ sung men tụy pancreatin liều cao uống trong bữa ăn, kiểm soát đường huyết bằng insulin. Cai rượu tuyệt đối và nội soi tán sỏi tụy qua ercp']`
- **Các lỗi phát hiện khi đọc ca này (5 lỗi):**
  - **L02** — *Tiểu từ đề nghị (`nhé/nha/nghen`) gắn vào câu hỏi `?`*: `Bác sĩ: Bác sĩ vệ sinh tay khử khuẩn một lát nhé, cô có thấy ngột ngạt hay khó thở khi đeo khẩu trang không nhé ạ?`
  - **L02-L03** — *Hỏi đáp xã giao lệch cặp (hỏi một đằng, đáp một nẻo)*: `Bác sĩ: Bác sĩ vệ sinh tay khử khuẩn một lát nhé, cô có thấy ngột ngạt hay khó thở khi đeo khẩu trang không nhé ạ? / Bệnh nhân: Dạ thưa bác sĩ, ngồi chờ một chút không sao đâu bác sĩ ạ.`
  - **L05** — *Lặp từ nối `Bên cạnh đó, ngoài ra`*: `Bác sĩ: Bên cạnh đó, ngoài ra còn triệu chứng nào làm mình lo lắng nữa không nhỉ?`
  - **L12** — *Cụm nhận xét thừa sau dấu chấm ở cuối câu*: `Bác sĩ: Bác sĩ xem xét trực tiếp thấy: Thể trạng gầy đét, da khô bọc xương, bụng mềm ấn tức sâu vùng tụy thượng vị. đáng lưu ý.`
  - **L14** — *Hạt đề nghị thừa sau dấu chấm (`. nhé.`, `. nha.`, `. nghen.`)*: `Bác sĩ: Bác sĩ đề ra phác đồ: Bổ sung men tụy pancreatin liều cao uống trong bữa ăn, kiểm soát đường huyết bằng insulin. Cai rượu tuyệt đối và nội soi tán sỏi tụy qua ercp. nghen.`

### Ca 09 — Mã: `hv_3184` (`ghẻ`)
- **Thông tin ca:** `la_tre_em=False` | `nguoi_ke=vợ` | `lo_danh_tinh=True` | `boi_canh=dieu_duong_ban_giao` | `bay=['gia_dinh', 'hoi_khong_dap', 'nguoi_ke_benh_minh', 'nguoi_nha_ke_ho', 'nguon_khac_nhau']` | `so_luot=25`
- **Lời thoại đầy đủ:**
```text
L01: Điều dưỡng: Em chào bác sĩ. Chú này vừa vào phòng chờ, em đã kiểm tra mạch và nhiệt độ xong ạ.
L02: Bác sĩ: Cảm ơn em. Chú kể tôi nghe xem thế nào ạ.
L03: Bác sĩ: Bác sĩ muốn xác nhận, Cô có quan hệ như thế nào với chú ấy?
L04: Người nhà: Thưa bác sĩ, tôi là người nhà, cụ thể là vợ của chú ấy bác sĩ ạ.
L05: Bác sĩ: Ngồi nghỉ ngơi ngoài khu vực chờ, có cảm thấy thoải mái trong lúc chờ gọi tên không?
L06: Người nhà: Dạ thưa bác sĩ, phòng khám bật điều hòa mát mẻ rất dễ chịu ạ.
L07: Bác sĩ: {goi_hoa} ngồi ghế đệm bên ngoài, chú có cần chỉnh lại hướng gió quạt không thế ạ?
L08: Người nhà: Dạ, không gian yên tĩnh nên ngồi đợi rất nhẹ nhàng ạ.
L09: Người nhà: Nhà tôi xuất hiện tối đến là ngứa được từ hôm kia rồi.
L10: Bệnh nhân: Không đúng đâu, tôi tối đến là ngứa mấy hôm nay rồi.
L11: Bác sĩ: Để tôi ghi là chưa rõ từ hôm kia hay mấy hôm nay, mình xác nhận lại sau nhé.
L12: Bác sĩ: Ngoài chuyện đó ra, có xuất hiện thêm dấu hiệu đau nhức hay mệt mỏi ở đâu không ạ?
L13: Người nhà: Dạ thưa bác sĩ, cùng lúc đó nhà tôi cũng xuất hiện nằm mãi không ngủ được.
L14: Bác sĩ: Về tiền sử bệnh tật từ trước tới nay, đã từng đi khám tổng quát hay phát hiện bệnh gì trước đây chưa nhỉ?
L15: Người nhà: Thưa bác sĩ, nhà tôi có sỏi thận ạ.
L16: Người nhà: Tôi bị viêm phế quản mạn mấy năm nay rồi.
L17: Bác sĩ: Liên quan đến thuốc men, trong quá khứ có ghi nhận dị ứng thuốc nào đáng chú ý không hả bạn?
L18: Người nhà: Dạ không ạ, sức khỏe bình thường, chưa từng bị phản ứng lạ với thuốc cả.
L19: Bác sĩ: Chú có thấy đau mỏi vùng vai gáy khi ngồi làm việc không ạ?
L20: Bác sĩ: Rồi, để bác sĩ đo lại nồng độ oxy trong máu và mạch nha chú.
L21: Điều dưỡng: Sinh hiệu em đo được: Bác sĩ ghi nhận tình trạng: Sẩn và mụn nước ở kẽ ngón tay, có rãnh ghẻ. cần theo dõi.
L22: Bác sĩ: Tôi xác định tình trạng này là: Ghẻ. rõ ràng.
L23: Bác sĩ: Các bước điều trị tiếp theo là: Bôi thuốc trị ghẻ cho cả nhà cùng lúc. Giặt nóng quần áo, chăn màn. nghen.
L24: Bác sĩ: Nếu mai chú ấy còn nổi sẩn ở kẽ tay thì quay lại đây nhé.
L25: Người nhà: Dạ thưa bác sĩ, cảm ơn bác sĩ đã khám rất kỹ, tôi sẽ nghỉ ngơi bồi dưỡng theo lời dặn nhé ạ.
```
- **Đáp án mệnh đề (`dap_an`):**
  - `M01` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=ngứa về đêm` | `moc=từ hôm kia` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Nhà tôi xuất hiện tối đến là ngứa được từ hôm kia rồi']`
  - `M02` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=ngứa về đêm` | `moc=mấy hôm nay` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=mâu thuẫn` | `trich_dan=['tôi tối đến là ngứa mấy hôm nay rồi']`
  - `M03` [LÝ DO KHÁM BỆNH] `chu_the=bệnh nhân` | `noi_dung=ngứa về đêm` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Nhà tôi xuất hiện tối đến là ngứa được từ hôm kia rồi']`
  - `M04` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=khó ngủ` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['cùng lúc đó nhà tôi cũng xuất hiện nằm mãi không ngủ được']`
  - `M05` [TIỀN SỬ BỆNH] `chu_the=bệnh nhân` | `noi_dung=sỏi thận` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['nhà tôi có sỏi thận ạ']`
  - `M06` [TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI] `chu_the=vợ` | `noi_dung=viêm phế quản mạn` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Tôi bị viêm phế quản mạn mấy năm nay rồi']`
  - `M07` [DỊ ỨNG] `chu_the=bệnh nhân` | `noi_dung=dị ứng thuốc` | `moc=None` | `phu_dinh=True` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['trong quá khứ có ghi nhận dị ứng thuốc nào đáng chú ý không hả bạn', 'chưa từng bị phản ứng lạ với thuốc cả']`
  - `M08` [KHÁM LÂM SÀNG] `chu_the=bệnh nhân` | `noi_dung=Sẩn và mụn nước ở kẽ ngón tay, có rãnh ghẻ` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Sinh hiệu em đo được: Bác sĩ ghi nhận tình trạng: Sẩn và mụn nước ở kẽ ngón tay, có rãnh ghẻ']`
  - `M09` [CHẨN ĐOÁN] `chu_the=bệnh nhân` | `noi_dung=Ghẻ` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Tôi xác định tình trạng này là: Ghẻ']`
  - `M10` [KẾ HOẠCH ĐIỀU TRỊ] `chu_the=bệnh nhân` | `noi_dung=Bôi thuốc trị ghẻ cho cả nhà cùng lúc. Giặt nóng quần áo, chăn màn` | `moc=None` | `phu_dinh=False` | `tinh_huong=kế hoạch` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Các bước điều trị tiếp theo là: Bôi thuốc trị ghẻ cho cả nhà cùng lúc. Giặt nóng quần áo, chăn màn']`
  - `M11` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=nổi sẩn ở kẽ tay` | `moc=None` | `phu_dinh=False` | `tinh_huong=giả định` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Nếu mai chú ấy còn nổi sẩn ở kẽ tay thì quay lại đây nhé']`
- **Các lỗi phát hiện khi đọc ca này (8 lỗi):**
  - **L07** — *Biến f-string chưa thay (`{goi}`/`{goi_hoa}`)*: `Bác sĩ: {goi_hoa} ngồi ghế đệm bên ngoài, chú có cần chỉnh lại hướng gió quạt không thế ạ?`
  - **L10** — *Lặp từ thời gian `nay nay` / `rồi nay` / `nay rồi nay`*: `Bệnh nhân: Không đúng đâu, tôi tối đến là ngứa mấy hôm nay rồi.`
  - **L16** — *Lặp từ thời gian `nay nay` / `rồi nay` / `nay rồi nay`*: `Người nhà: Tôi bị viêm phế quản mạn mấy năm nay rồi.`
  - **L17** — *Bác sĩ gọi người bệnh/người nhà là `bạn` (lệch vai xưng hô)*: `Bác sĩ: Liên quan đến thuốc men, trong quá khứ có ghi nhận dị ứng thuốc nào đáng chú ý không hả bạn?`
  - **L21** — *Cụm nhận xét thừa sau dấu chấm ở cuối câu*: `Điều dưỡng: Sinh hiệu em đo được: Bác sĩ ghi nhận tình trạng: Sẩn và mụn nước ở kẽ ngón tay, có rãnh ghẻ. cần theo dõi.`
  - **L21** — *Điều dưỡng lặp hai lần dẫn nhập `Sinh hiệu em đo được: Bác sĩ/Tôi...`*: `Điều dưỡng: Sinh hiệu em đo được: Bác sĩ ghi nhận tình trạng: Sẩn và mụn nước ở kẽ ngón tay, có rãnh ghẻ. cần theo dõi.`
  - **L22** — *Cụm nhận xét thừa sau dấu chấm ở cuối câu*: `Bác sĩ: Tôi xác định tình trạng này là: Ghẻ. rõ ràng.`
  - **L23** — *Hạt đề nghị thừa sau dấu chấm (`. nhé.`, `. nha.`, `. nghen.`)*: `Bác sĩ: Các bước điều trị tiếp theo là: Bôi thuốc trị ghẻ cho cả nhà cùng lúc. Giặt nóng quần áo, chăn màn. nghen.`

### Ca 10 — Mã: `hv_1523` (`ung thư cổ tử cung`)
- **Thông tin ca:** `la_tre_em=False` | `nguoi_ke=None` | `lo_danh_tinh=False` | `boi_canh=tai_kham` | `bay=['bo_sung', 'dien_bien']` | `so_luot=23`
- **Lời thoại đầy đủ:**
```text
L01: Bác sĩ: Toa thuốc metformin lần trước bác sĩ kê, cô dùng đáp ứng ra sao ạ?
L02: Bệnh nhân: Dạ bác, uống được ít hôm rồi ngừng, ngừng 4 tuần rồi.
L03: Bác sĩ: Cho tôi hỏi một chút, cô đến đây khám bệnh cho mình hay cho ai khác vậy ạ?
L04: Bệnh nhân: Vâng, tôi đi khám cho chính mình ạ.
L05: Bác sĩ: Mấy ngày nay thời tiết, không khí dạo này hanh khô có làm cô bị khô rát họng không?
L06: Bệnh nhân: Vâng ạ, sáng sớm se lạnh em có quàng khăn ấm khi đi đường bác sĩ ạ.
L07: Bệnh nhân: Tôi cảm giác ra máu âm đạo bất thường sau quan hệ xuất hiện liên miên vài năm rồi nay.
L08: Bác sĩ: Thêm vào đó, ngoài những điều vừa kể, bạn có thấy phát sinh dấu hiệu nào mới không?
L09: Bệnh nhân: Dạ vâng, tôi thấy người còn có xuống mấy cân, tiểu khó nữa.
L10: Bệnh nhân: Xuống mấy cân thì chỉ bị lúc sáng sớm ạ.
L11: Bệnh nhân: Hôm kia thì khí hư lẫn máu có mùi hôi, tối qua thì đỡ hẳn rồi ạ.
L12: Bác sĩ: Thế về tiền sử sức khỏe, đã từng đi khám tổng quát hay phát hiện bệnh gì trước đây chưa ạ?
L13: Bệnh nhân: Dạ hổng có, chưa từng phẫu thuật hay mắc bệnh hiểm nghèo nào từ trước tới nay nha bác sĩ.
L14: Bác sĩ: Thế còn về tiền sử dị ứng, bạn có mẫn cảm đặc biệt với thành phần thuốc nào không vậy ạ?
L15: Bệnh nhân: Dạ bác sĩ, có, dị ứng cephalexin.
L16: Bác sĩ: À, cho tôi hỏi thêm, mình có đang phải uống thuốc huyết áp hay tiểu đường hàng ngày không hả bạn?
L17: Bệnh nhân: Dạ thưa bác sĩ, tôi có xịt salbutamol hai nhát, khi cần, dùng được một tháng nay ạ.
L18: Bác sĩ: Để tôi, tôi khám qua một chút một chút nha.
L19: Bác sĩ: Vừa khám xong cho thấy: Đặt mỏ vịt quan sát cổ tử cung có tổn thương dạng sùi loét, dễ chảy máu khi chạm.
L20: Bác sĩ: Bác sĩ nghĩ nhiều đến: Nghi ngờ ung thư cổ tử cung giai đoạn xâm lấn. cần chú ý điều trị.
L21: Bác sĩ: Phác đồ can thiệp đợt này: Làm xét nghiệm tế bào học Pap smear kết hợp HPV-DNA. Sinh thiết tổn thương cổ tử cung làm giải phẫu bệnh. nhé.
L22: Bác sĩ: Bác sĩ kê salbutamol hai nhát, xịt khi cần nghen.
L23: Bệnh nhân: Dạ thưa bác sĩ, tôi xin cảm ơn sự nhiệt tình của bác sĩ nghen bác sĩ.
```
- **Đáp án mệnh đề (`dap_an`):**
  - `M01` [TIỀN SỬ BỆNH] `chu_the=bệnh nhân` | `noi_dung=từng dùng metformin, đã ngừng 4 tuần` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Toa thuốc metformin lần trước bác sĩ kê, cô dùng đáp ứng ra sao ạ', 'ngừng 4 tuần rồi']`
  - `M02` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=ra máu âm đạo bất thường sau quan hệ` | `moc=vài năm rồi` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Tôi cảm giác ra máu âm đạo bất thường sau quan hệ xuất hiện liên miên vài năm rồi nay']`
  - `M03` [LÝ DO KHÁM BỆNH] `chu_the=bệnh nhân` | `noi_dung=ra máu âm đạo bất thường sau quan hệ` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Tôi cảm giác ra máu âm đạo bất thường sau quan hệ xuất hiện liên miên vài năm rồi nay']`
  - `M04` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=sụt cân` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['tôi thấy người còn có xuống mấy cân', 'Xuống mấy cân thì chỉ bị lúc sáng sớm ạ']`
  - `M05` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=tiểu khó` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['tiểu khó nữa']`
  - `M06` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=sụt cân chỉ bị lúc sáng sớm` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=bổ sung` | `trich_dan=['Xuống mấy cân thì chỉ bị lúc sáng sớm ạ']`
  - `M07` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=khí hư lẫn máu có mùi hôi` | `moc=hôm kia` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Hôm kia thì khí hư lẫn máu có mùi hôi']`
  - `M08` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=khí hư lẫn máu có mùi hôi` | `moc=tối qua` | `phu_dinh=True` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=diễn biến` | `trich_dan=['tối qua thì đỡ hẳn rồi ạ']`
  - `M09` [DỊ ỨNG] `chu_the=bệnh nhân` | `noi_dung=dị ứng cephalexin` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['dị ứng cephalexin']`
  - `M10` [THUỐC ĐANG DÙNG] `chu_the=bệnh nhân` | `noi_dung=salbutamol` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['tôi có xịt salbutamol hai nhát, khi cần, dùng được một tháng nay ạ']`
  - `M11` [KHÁM LÂM SÀNG] `chu_the=bệnh nhân` | `noi_dung=Đặt mỏ vịt quan sát cổ tử cung có tổn thương dạng sùi loét, dễ chảy máu khi chạm` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Vừa khám xong cho thấy: Đặt mỏ vịt quan sát cổ tử cung có tổn thương dạng sùi loét, dễ chảy máu khi chạm']`
  - `M12` [CHẨN ĐOÁN] `chu_the=bệnh nhân` | `noi_dung=Nghi ngờ ung thư cổ tử cung giai đoạn xâm lấn` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=nghi ngờ` | `quan_he=None` | `trich_dan=['Bác sĩ nghĩ nhiều đến: Nghi ngờ ung thư cổ tử cung giai đoạn xâm lấn']`
  - `M13` [KẾ HOẠCH ĐIỀU TRỊ] `chu_the=bệnh nhân` | `noi_dung=Làm xét nghiệm tế bào học Pap smear kết hợp HPV-DNA. Sinh thiết tổn thương cổ tử cung làm giải phẫu bệnh` | `moc=None` | `phu_dinh=False` | `tinh_huong=kế hoạch` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Phác đồ can thiệp đợt này: Làm xét nghiệm tế bào học Pap smear kết hợp HPV-DNA. Sinh thiết tổn thương cổ tử cung làm giải phẫu bệnh']`
  - `M14` [KẾ HOẠCH ĐIỀU TRỊ] `chu_the=bệnh nhân` | `noi_dung=kê salbutamol` | `moc=None` | `phu_dinh=False` | `tinh_huong=kế hoạch` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Bác sĩ kê salbutamol hai nhát, xịt khi cần nghen']`
- **Các lỗi phát hiện khi đọc ca này (8 lỗi):**
  - **L05-L06** — *Hỏi đáp xã giao lệch cặp (hỏi một đằng, đáp một nẻo)*: `Bác sĩ: Mấy ngày nay thời tiết, không khí dạo này hanh khô có làm cô bị khô rát họng không? / Bệnh nhân: Vâng ạ, sáng sớm se lạnh em có quàng khăn ấm khi đi đường bác sĩ ạ.`
  - **L07** — *Lặp từ thời gian `nay nay` / `rồi nay` / `nay rồi nay`*: `Bệnh nhân: Tôi cảm giác ra máu âm đạo bất thường sau quan hệ xuất hiện liên miên vài năm rồi nay.`
  - **L08** — *Bác sĩ gọi người bệnh/người nhà là `bạn` (lệch vai xưng hô)*: `Bác sĩ: Thêm vào đó, ngoài những điều vừa kể, bạn có thấy phát sinh dấu hiệu nào mới không?`
  - **L14** — *Bác sĩ gọi người bệnh/người nhà là `bạn` (lệch vai xưng hô)*: `Bác sĩ: Thế còn về tiền sử dị ứng, bạn có mẫn cảm đặc biệt với thành phần thuốc nào không vậy ạ?`
  - **L16** — *Bác sĩ gọi người bệnh/người nhà là `bạn` (lệch vai xưng hô)*: `Bác sĩ: À, cho tôi hỏi thêm, mình có đang phải uống thuốc huyết áp hay tiểu đường hàng ngày không hả bạn?`
  - **L18** — *Lặp cụm `một chút một chút`*: `Bác sĩ: Để tôi, tôi khám qua một chút một chút nha.`
  - **L20** — *Cụm nhận xét thừa sau dấu chấm ở cuối câu*: `Bác sĩ: Bác sĩ nghĩ nhiều đến: Nghi ngờ ung thư cổ tử cung giai đoạn xâm lấn. cần chú ý điều trị.`
  - **L21** — *Hạt đề nghị thừa sau dấu chấm (`. nhé.`, `. nha.`, `. nghen.`)*: `Bác sĩ: Phác đồ can thiệp đợt này: Làm xét nghiệm tế bào học Pap smear kết hợp HPV-DNA. Sinh thiết tổn thương cổ tử cung làm giải phẫu bệnh. nhé.`

### Ca 11 — Mã: `hv_0241` (`mất ngủ mạn tính`)
- **Thông tin ca:** `la_tre_em=False` | `nguoi_ke=None` | `lo_danh_tinh=False` | `boi_canh=kham_lan_dau` | `bay=['dinh_chinh']` | `so_luot=15`
- **Lời thoại đầy đủ:**
```text
L01: Bác sĩ: Chào chị, mấy hôm nay cơ thể có biểu hiện gì khiến chị phải đi khám ạ?
L02: Bác sĩ: Để rõ thông tin đăng ký, chị đến kiểm tra sức khỏe cho bản thân mình phải không phải không ạ?
L03: Bệnh nhân: Dạ đúng rồi, tôi đi khám cho chính mình ạ.
L04: Bệnh nhân: Từ độ vài năm rồi trước là tôi bắt đầu khó đi vào giấc ngủ trằn trọc trên một tiếng đồng hồ mới ngủ được ạ.
L05: Bệnh nhân: Tôi nói lại cho đúng, từ năm ngoái chứ không phải vài năm rồi.
L06: Bác sĩ: Về cảm giác trong người, ngoài những điều vừa kể, bạn có thấy phát sinh dấu hiệu nào mới không không ạ?
L07: Bệnh nhân: Dạ, tôi còn thấy thử nghiệm các biện pháp vệ sinh giấc ngủ chưa mang lại kết quả nữa.
L08: Bác sĩ: Bác sĩ muốn biết là, mấy hôm nay đã tự điều trị bằng thuốc gì ở nhà chưa thế?
L09: Bệnh nhân: Dạ không ạ, chưa dùng thuốc giảm đau hay hạ sốt nào từ lúc phát bệnh đâu ạ.
L10: Bác sĩ: Để xem xét kỹ hơn, bác sĩ kiểm tra phản xạ thần kinh và cơ lực một chút một chút nhé.
L11: Bác sĩ: Kiểm tra trực tiếp ghi nhận: Không phát hiện bất thường khi khám.
L12: Bác sĩ: Bác sĩ chẩn đoán là: Mất ngủ mạn tính. cần chú ý điều trị.
L13: Bác sĩ: Về kế hoạch điều trị: Vệ sinh giấc ngủ. Bỏ cà phê buổi chiều. Chưa dùng thuốc ngủ. theo đúng hướng dẫn.
L14: Bác sĩ: Đợt này tôi kê paracetamol 500 mg, uống khi cần nha.
L15: Bệnh nhân: Vâng, tôi đã hiểu cặn kẽ hướng điều trị rồi nhé bác sĩ.
```
- **Đáp án mệnh đề (`dap_an`):**
  - `M01` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=khó đi vào giấc ngủ trằn trọc trên một tiếng đồng hồ mới ngủ được` | `moc=từ năm ngoái` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=đính chính` | `trich_dan=['Từ độ vài năm rồi trước là tôi bắt đầu khó đi vào giấc ngủ trằn trọc trên một tiếng đồng hồ mới ngủ được ạ', 'từ năm ngoái chứ không phải vài năm rồi']`
  - `M02` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=khó đi vào giấc ngủ trằn trọc trên một tiếng đồng hồ mới ngủ được` | `moc=vài năm rồi` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Từ độ vài năm rồi trước là tôi bắt đầu khó đi vào giấc ngủ trằn trọc trên một tiếng đồng hồ mới ngủ được ạ', 'từ năm ngoái chứ không phải vài năm rồi']`
  - `M03` [LÝ DO KHÁM BỆNH] `chu_the=bệnh nhân` | `noi_dung=khó đi vào giấc ngủ trằn trọc trên một tiếng đồng hồ mới ngủ được` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Từ độ vài năm rồi trước là tôi bắt đầu khó đi vào giấc ngủ trằn trọc trên một tiếng đồng hồ mới ngủ được ạ']`
  - `M04` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=thử nghiệm các biện pháp vệ sinh giấc ngủ chưa mang lại kết quả` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['tôi còn thấy thử nghiệm các biện pháp vệ sinh giấc ngủ chưa mang lại kết quả nữa']`
  - `M05` [KHÁM LÂM SÀNG] `chu_the=bệnh nhân` | `noi_dung=Không phát hiện bất thường khi khám` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Kiểm tra trực tiếp ghi nhận: Không phát hiện bất thường khi khám']`
  - `M06` [CHẨN ĐOÁN] `chu_the=bệnh nhân` | `noi_dung=Mất ngủ mạn tính` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Bác sĩ chẩn đoán là: Mất ngủ mạn tính']`
  - `M07` [KẾ HOẠCH ĐIỀU TRỊ] `chu_the=bệnh nhân` | `noi_dung=Vệ sinh giấc ngủ. Bỏ cà phê buổi chiều. Chưa dùng thuốc ngủ` | `moc=None` | `phu_dinh=False` | `tinh_huong=kế hoạch` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Về kế hoạch điều trị: Vệ sinh giấc ngủ. Bỏ cà phê buổi chiều. Chưa dùng thuốc ngủ']`
  - `M08` [KẾ HOẠCH ĐIỀU TRỊ] `chu_the=bệnh nhân` | `noi_dung=kê paracetamol` | `moc=None` | `phu_dinh=False` | `tinh_huong=kế hoạch` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Đợt này tôi kê paracetamol 500 mg, uống khi cần nha']`
- **Các lỗi phát hiện khi đọc ca này (7 lỗi):**
  - **L02** — *Lặp cụm `phải không phải không`*: `Bác sĩ: Để rõ thông tin đăng ký, chị đến kiểm tra sức khỏe cho bản thân mình phải không phải không ạ?`
  - **L04** — *Ghép sai mốc thời gian `từ độ ... nay/rồi trước`*: `Bệnh nhân: Từ độ vài năm rồi trước là tôi bắt đầu khó đi vào giấc ngủ trằn trọc trên một tiếng đồng hồ mới ngủ được ạ.`
  - **L06** — *Lặp từ nghi vấn `không không` / `chưa không`*: `Bác sĩ: Về cảm giác trong người, ngoài những điều vừa kể, bạn có thấy phát sinh dấu hiệu nào mới không không ạ?`
  - **L06** — *Bác sĩ gọi người bệnh/người nhà là `bạn` (lệch vai xưng hô)*: `Bác sĩ: Về cảm giác trong người, ngoài những điều vừa kể, bạn có thấy phát sinh dấu hiệu nào mới không không ạ?`
  - **L10** — *Lặp cụm `một chút một chút`*: `Bác sĩ: Để xem xét kỹ hơn, bác sĩ kiểm tra phản xạ thần kinh và cơ lực một chút một chút nhé.`
  - **L12** — *Cụm nhận xét thừa sau dấu chấm ở cuối câu*: `Bác sĩ: Bác sĩ chẩn đoán là: Mất ngủ mạn tính. cần chú ý điều trị.`
  - **L13** — *Cụm nhận xét thừa sau dấu chấm ở cuối câu*: `Bác sĩ: Về kế hoạch điều trị: Vệ sinh giấc ngủ. Bỏ cà phê buổi chiều. Chưa dùng thuốc ngủ. theo đúng hướng dẫn.`

### Ca 12 — Mã: `hv_0605` (`mất ngủ mạn tính`)
- **Thông tin ca:** `la_tre_em=False` | `nguoi_ke=None` | `lo_danh_tinh=False` | `boi_canh=cho_ket_qua` | `bay=[]` | `so_luot=11`
- **Lời thoại đầy đủ:**
```text
L01: Bác sĩ: Chị kể rõ cho bác sĩ nghe xem tình trạng hiện tại thế nào.
L02: Bệnh nhân: Dạ bác, từ độ nửa năm rồi trước là tôi bắt đầu khó đi vào giấc ngủ trằn trọc trên một tiếng đồng hồ mới ngủ được.
L03: Bác sĩ: Ngoài chuyện đó ra, có xuất hiện thêm dấu hiệu đau nhức hay mệt mỏi ở đâu không ạ?
L04: Bệnh nhân: Dạ bác, song song đó tôi còn thấy ban ngày mệt mỏi đờ đẫn uể oải giảm hiệu suất làm việc.
L05: Bác sĩ: Trước giờ, mình có từng bị dị ứng với loại thuốc nào không?
L06: Bệnh nhân: Dạ không có đâu ạ, cơ thể đáp ứng thuốc tốt, không có tiền sử dị ứng hết ạ.
L07: Bác sĩ: Sau khi nghe kể, bác sĩ nghe tim và phổi cho chị nhé ạ.
L08: Bác sĩ: Kết quả khám cơ bản: Không phát hiện bất thường khi khám. nhé ạ.
L09: Bác sĩ: Tôi nghĩ nhiều đến mất ngủ mạn tính, nhưng chưa kết luận được. Phải có kết quả xét nghiệm nước tiểu đã.
L10: Bác sĩ: Chị đi làm xét nghiệm nước tiểu rồi quay lại đây nha.
L11: Bệnh nhân: Dạ em nghe rõ rồi, tôi đã nắm rõ đơn thuốc và liều lượng dữ lắm nghen.
```
- **Đáp án mệnh đề (`dap_an`):**
  - `M01` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=khó đi vào giấc ngủ trằn trọc trên một tiếng đồng hồ mới ngủ được` | `moc=nửa năm rồi` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['từ độ nửa năm rồi trước là tôi bắt đầu khó đi vào giấc ngủ trằn trọc trên một tiếng đồng hồ mới ngủ được']`
  - `M02` [LÝ DO KHÁM BỆNH] `chu_the=bệnh nhân` | `noi_dung=khó đi vào giấc ngủ trằn trọc trên một tiếng đồng hồ mới ngủ được` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['từ độ nửa năm rồi trước là tôi bắt đầu khó đi vào giấc ngủ trằn trọc trên một tiếng đồng hồ mới ngủ được']`
  - `M03` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=ban ngày mệt mỏi đờ đẫn uể oải giảm hiệu suất làm việc` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['song song đó tôi còn thấy ban ngày mệt mỏi đờ đẫn uể oải giảm hiệu suất làm việc']`
  - `M04` [DỊ ỨNG] `chu_the=bệnh nhân` | `noi_dung=dị ứng thuốc` | `moc=None` | `phu_dinh=True` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['mình có từng bị dị ứng với loại thuốc nào không', 'cơ thể đáp ứng thuốc tốt, không có tiền sử dị ứng hết ạ']`
  - `M05` [KHÁM LÂM SÀNG] `chu_the=bệnh nhân` | `noi_dung=Không phát hiện bất thường khi khám` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Kết quả khám cơ bản: Không phát hiện bất thường khi khám']`
  - `M06` [CHẨN ĐOÁN] `chu_the=bệnh nhân` | `noi_dung=Mất ngủ mạn tính` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=nghi ngờ` | `quan_he=None` | `trich_dan=['Tôi nghĩ nhiều đến mất ngủ mạn tính']`
  - `M07` [KẾ HOẠCH ĐIỀU TRỊ] `chu_the=bệnh nhân` | `noi_dung=làm xét nghiệm nước tiểu` | `moc=None` | `phu_dinh=False` | `tinh_huong=kế hoạch` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Chị đi làm xét nghiệm nước tiểu rồi quay lại đây nha']`
- **Các lỗi phát hiện khi đọc ca này (3 lỗi):**
  - **L02** — *Ghép sai mốc thời gian `từ độ ... nay/rồi trước`*: `Bệnh nhân: Dạ bác, từ độ nửa năm rồi trước là tôi bắt đầu khó đi vào giấc ngủ trằn trọc trên một tiếng đồng hồ mới ngủ được.`
  - **L08** — *Hạt đề nghị thừa sau dấu chấm (`. nhé.`, `. nha.`, `. nghen.`)*: `Bác sĩ: Kết quả khám cơ bản: Không phát hiện bất thường khi khám. nhé ạ.`
  - **L11** — *Xung đột đại từ tự xưng trong cùng một câu (`em` vs `tôi`)*: `Bệnh nhân: Dạ em nghe rõ rồi, tôi đã nắm rõ đơn thuốc và liều lượng dữ lắm nghen.`

### Ca 13 — Mã: `hv_0827` (`phì đại tuyến tiền liệt`)
- **Thông tin ca:** `la_tre_em=False` | `nguoi_ke=None` | `lo_danh_tinh=False` | `boi_canh=kham_lan_dau` | `bay=['tien_su_gia_dinh']` | `so_luot=17`
- **Lời thoại đầy đủ:**
```text
L01: Bác sĩ: Chú đi khám hôm nay vì vấn đề sức khỏe gì thế?
L02: Bác sĩ: Để rõ thông tin đăng ký, hôm nay chú là người trực tiếp cần khám đúng không thế ạ?
L03: Bệnh nhân: Dạ đúng rồi, tôi đi khám cho bản thân bác sĩ ạ.
L04: Bác sĩ: Lúc nãy đi đến phòng khám, Chú đi lại bằng xe buýt hay taxi tới đây vậy chú?
L05: Bệnh nhân: Dạ em, đoạn ngã tư hơi đông một chút nhưng vẫn đi lại thuận lợi.
L06: Bệnh nhân: Tôi cảm giác thang điểm triệu chứng tuyến tiền liệt ipss quốc tế trên 20 điểm xuất hiện liên miên khoảng một tháng nay ạ.
L07: Bác sĩ: Bác sĩ muốn hỏi kỹ thêm, có xuất hiện thêm dấu hiệu đau nhức hay mệt mỏi ở đâu không?
L08: Bệnh nhân: Dạ vâng ạ, tôi thấy người còn có tiểu gấp không nhịn được đôi khi són tiểu ra quần nữa.
L09: Bác sĩ: Người thân ruột thịt của mình, người thân có ai gặp vấn đề sức khỏe mạn tính đáng lưu ý không?
L10: Bệnh nhân: Dạ vâng ạ, bà ngoại bị đái tháo đường biến chứng thận ạ.
L11: Bác sĩ: À, cho tôi hỏi thêm, ở nhà mình đã dùng thuốc hạ sốt, giảm đau hay thuốc gì chưa nhỉ?
L12: Bệnh nhân: Dạ không ạ, chưa kịp dùng thuốc gì thì đã vào viện khám cả bác sĩ ạ.
L13: Bác sĩ: Được rồi, để bác sĩ nắn xem các hạch ngoại vi có sưng không một chút nhé.
L14: Bác sĩ: Kiểm tra thấy: Thăm trực tràng chạm tuyến tiền liệt to đều hai thùy, ranh giới rõ, mật độ chắc, mất rãnh giữa, không đau.
L15: Bác sĩ: Tôi nhận định tình trạng này là: Tăng sinh lành tính tuyến tiền liệt. nghen.
L16: Bác sĩ: Về phương án điều trị: Siêu âm đo thể tích tuyến tiền liệt và lượng nước tiểu tồn dư. Định lượng PSA toàn phần loại trừ ác tính. Dùng thuốc chẹn alpha alfuzosin. để theo dõi thêm.
L17: Bệnh nhân: Vâng thưa bác sĩ, xin cảm ơn sự tận tâm của bác sĩ, tôi sẽ nghỉ ngơi bồi dưỡng theo lời dặn ạ.
```
- **Đáp án mệnh đề (`dap_an`):**
  - `M01` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=thang điểm triệu chứng tuyến tiền liệt ipss quốc tế trên 20 điểm` | `moc=khoảng một tháng` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Tôi cảm giác thang điểm triệu chứng tuyến tiền liệt ipss quốc tế trên 20 điểm xuất hiện liên miên khoảng một tháng nay ạ']`
  - `M02` [LÝ DO KHÁM BỆNH] `chu_the=bệnh nhân` | `noi_dung=thang điểm triệu chứng tuyến tiền liệt ipss quốc tế trên 20 điểm` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Tôi cảm giác thang điểm triệu chứng tuyến tiền liệt ipss quốc tế trên 20 điểm xuất hiện liên miên khoảng một tháng nay ạ']`
  - `M03` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=tiểu gấp không nhịn được đôi khi són tiểu ra quần` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['tôi thấy người còn có tiểu gấp không nhịn được đôi khi són tiểu ra quần nữa']`
  - `M04` [TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI] `chu_the=bà ngoại` | `noi_dung=đái tháo đường biến chứng thận` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['bà ngoại bị đái tháo đường biến chứng thận ạ']`
  - `M05` [KHÁM LÂM SÀNG] `chu_the=bệnh nhân` | `noi_dung=Thăm trực tràng chạm tuyến tiền liệt to đều hai thùy, ranh giới rõ, mật độ chắc, mất rãnh giữa, không đau` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Kiểm tra thấy: Thăm trực tràng chạm tuyến tiền liệt to đều hai thùy, ranh giới rõ, mật độ chắc, mất rãnh giữa, không đau']`
  - `M06` [CHẨN ĐOÁN] `chu_the=bệnh nhân` | `noi_dung=Tăng sinh lành tính tuyến tiền liệt` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Tôi nhận định tình trạng này là: Tăng sinh lành tính tuyến tiền liệt']`
  - `M07` [KẾ HOẠCH ĐIỀU TRỊ] `chu_the=bệnh nhân` | `noi_dung=Siêu âm đo thể tích tuyến tiền liệt và lượng nước tiểu tồn dư. Định lượng PSA toàn phần loại trừ ác tính. Dùng thuốc chẹn alpha alfuzosin` | `moc=None` | `phu_dinh=False` | `tinh_huong=kế hoạch` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Về phương án điều trị: Siêu âm đo thể tích tuyến tiền liệt và lượng nước tiểu tồn dư. Định lượng PSA toàn phần loại trừ ác tính. Dùng thuốc chẹn alpha alfuzosin']`
- **Các lỗi phát hiện khi đọc ca này (3 lỗi):**
  - **L05** — *Từ đệm cụt `Dạ em,` / `Dạ tôi,`*: `Bệnh nhân: Dạ em, đoạn ngã tư hơi đông một chút nhưng vẫn đi lại thuận lợi.`
  - **L15** — *Hạt đề nghị thừa sau dấu chấm (`. nhé.`, `. nha.`, `. nghen.`)*: `Bác sĩ: Tôi nhận định tình trạng này là: Tăng sinh lành tính tuyến tiền liệt. nghen.`
  - **L16** — *Cụm nhận xét thừa sau dấu chấm ở cuối câu*: `Bác sĩ: Về phương án điều trị: Siêu âm đo thể tích tuyến tiền liệt và lượng nước tiểu tồn dư. Định lượng PSA toàn phần loại trừ ác tính. Dùng thuốc chẹn alpha alfuzosin. để theo dõi thêm.`

### Ca 14 — Mã: `hv_3478` (`nhiễm toan ống thận`)
- **Thông tin ca:** `la_tre_em=True` | `nguoi_ke=bà ngoại` | `lo_danh_tinh=False` | `boi_canh=tai_kham` | `bay=['di_ung_nguoi_nha', 'dien_bien', 'nguoi_nha_ke_ho']` | `so_luot=13`
- **Lời thoại đầy đủ:**
```text
L01: Bác sĩ: Tình hình uống vitamin C từ hôm tái khám trước tới nay thế nào rồi bé ạ?
L02: Người nhà: Vâng tôi nghe đây ạ, uống được ít hôm rồi ngừng, ngừng 2 tuần rồi ạ.
L03: Người nhà: Tình trạng chậm phát triển thể chất chậm lớn còi xương của cháu tôi kéo dài khoảng một tháng rồi ạ.
L04: Bác sĩ: Thêm vào đó, còn điều gì về sức khỏe mấy hôm nay mà mình chưa kể không hả bạn?
L05: Người nhà: Thưa bác sĩ, cháu tôi còn thấy yếu cơ từng cơn nữa ạ.
L06: Người nhà: Hôm qua thì nôn trớ nhiều đợt, đêm qua thì đỡ hẳn rồi ạ.
L07: Bác sĩ: Để đảm bảo an toàn khi kê đơn, bạn có dị ứng với penicillin, aspirin hay loại thuốc nào không nhỉ?
L08: Người nhà: Thưa bác sĩ, bà ngoại thì dị ứng trứng, còn cháu tôi chưa thấy bị bao giờ ạ.
L09: Bác sĩ: Được rồi, Bé ngồi yên để tôi nghe tim phổi nghen bé.
L10: Bác sĩ: Sau khi kiểm tra các cơ quan: Trẻ thấp bé hơn so với tuổi, lồng ngực dô hình ức gà, các đầu xương cổ tay to bè dạng còi xương.
L11: Bác sĩ: Nhiều khả năng là: Nhiễm toan ống thận typ 1 gây còi xương kháng vitamin D. cần chú ý điều trị.
L12: Bác sĩ: Hướng giải quyết là: Xét nghiệm khí máu động mạch, điện giải đồ máu và nước tiểu, pH nước tiểu. Điều trị bù kiềm bằng dung dịch natri bicarbonate hoặc citrat. để theo dõi thêm.
L13: Người nhà: Vâng bác sĩ, chúc bác sĩ một ngày làm việc thuận lợi, tôi sẽ chú ý theo dõi sức khỏe ở nhà ạ, chào bác sĩ tôi về.
```
- **Đáp án mệnh đề (`dap_an`):**
  - `M01` [TIỀN SỬ BỆNH] `chu_the=bệnh nhân` | `noi_dung=từng dùng vitamin C, đã ngừng 2 tuần` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Tình hình uống vitamin C từ hôm tái khám trước tới nay thế nào rồi bé ạ', 'ngừng 2 tuần rồi ạ']`
  - `M02` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=chậm phát triển thể chất chậm lớn còi xương` | `moc=khoảng một tháng` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Tình trạng chậm phát triển thể chất chậm lớn còi xương của cháu tôi kéo dài khoảng một tháng rồi ạ']`
  - `M03` [LÝ DO KHÁM BỆNH] `chu_the=bệnh nhân` | `noi_dung=chậm phát triển thể chất chậm lớn còi xương` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Tình trạng chậm phát triển thể chất chậm lớn còi xương của cháu tôi kéo dài khoảng một tháng rồi ạ']`
  - `M04` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=yếu cơ từng cơn` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['cháu tôi còn thấy yếu cơ từng cơn nữa ạ']`
  - `M05` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=nôn trớ nhiều đợt` | `moc=hôm qua` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Hôm qua thì nôn trớ nhiều đợt']`
  - `M06` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=nôn trớ nhiều đợt` | `moc=đêm qua` | `phu_dinh=True` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=diễn biến` | `trich_dan=['đêm qua thì đỡ hẳn rồi ạ']`
  - `M07` [TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI] `chu_the=bà ngoại` | `noi_dung=dị ứng trứng` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['bà ngoại thì dị ứng trứng']`
  - `M08` [DỊ ỨNG] `chu_the=bệnh nhân` | `noi_dung=dị ứng thuốc` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chưa ghi nhận` | `quan_he=None` | `trich_dan=['còn cháu tôi chưa thấy bị bao giờ ạ']`
  - `M09` [KHÁM LÂM SÀNG] `chu_the=bệnh nhân` | `noi_dung=Trẻ thấp bé hơn so với tuổi, lồng ngực dô hình ức gà, các đầu xương cổ tay to bè dạng còi xương` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Sau khi kiểm tra các cơ quan: Trẻ thấp bé hơn so với tuổi, lồng ngực dô hình ức gà, các đầu xương cổ tay to bè dạng còi xương']`
  - `M10` [CHẨN ĐOÁN] `chu_the=bệnh nhân` | `noi_dung=Nhiễm toan ống thận typ 1 gây còi xương kháng vitamin D` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Nhiều khả năng là: Nhiễm toan ống thận typ 1 gây còi xương kháng vitamin D']`
  - `M11` [KẾ HOẠCH ĐIỀU TRỊ] `chu_the=bệnh nhân` | `noi_dung=Xét nghiệm khí máu động mạch, điện giải đồ máu và nước tiểu, pH nước tiểu. Điều trị bù kiềm bằng dung dịch natri bicarbonate hoặc citrat` | `moc=None` | `phu_dinh=False` | `tinh_huong=kế hoạch` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Hướng giải quyết là: Xét nghiệm khí máu động mạch, điện giải đồ máu và nước tiểu, pH nước tiểu. Điều trị bù kiềm bằng dung dịch natri bicarbonate hoặc citrat']`
- **Các lỗi phát hiện khi đọc ca này (4 lỗi):**
  - **L04** — *Bác sĩ gọi người bệnh/người nhà là `bạn` (lệch vai xưng hô)*: `Bác sĩ: Thêm vào đó, còn điều gì về sức khỏe mấy hôm nay mà mình chưa kể không hả bạn?`
  - **L07** — *Bác sĩ gọi người bệnh/người nhà là `bạn` (lệch vai xưng hô)*: `Bác sĩ: Để đảm bảo an toàn khi kê đơn, bạn có dị ứng với penicillin, aspirin hay loại thuốc nào không nhỉ?`
  - **L11** — *Cụm nhận xét thừa sau dấu chấm ở cuối câu*: `Bác sĩ: Nhiều khả năng là: Nhiễm toan ống thận typ 1 gây còi xương kháng vitamin D. cần chú ý điều trị.`
  - **L12** — *Cụm nhận xét thừa sau dấu chấm ở cuối câu*: `Bác sĩ: Hướng giải quyết là: Xét nghiệm khí máu động mạch, điện giải đồ máu và nước tiểu, pH nước tiểu. Điều trị bù kiềm bằng dung dịch natri bicarbonate hoặc citrat. để theo dõi thêm.`

### Ca 15 — Mã: `hv_2226` (`cận thị tiến triển`)
- **Thông tin ca:** `la_tre_em=True` | `nguoi_ke=bà ngoại` | `lo_danh_tinh=False` | `boi_canh=tai_kham` | `bay=['nguoi_ke_benh_minh', 'nguoi_nha_ke_ho']` | `so_luot=19`
- **Lời thoại đầy đủ:**
```text
L01: Bác sĩ: Lần khám trước tôi có kê cetirizine, bé uống đều đặn chứ ạ?
L02: Người nhà: Dạ thưa bác sĩ, uống được ít hôm rồi ngừng, ngừng 1 tuần rồi ạ.
L03: Bác sĩ: Hôm nay đi khám, bé đã cài đặt ứng dụng VssID trên điện thoại chưa nhé ạ?
L04: Người nhà: Dạ có ạ, phiếu thông tin em đã tích đầy đủ ngoài bàn đón tiếp bác sĩ ạ.
L05: Bác sĩ: Bước vào phòng khám, bé có cảm thấy hồi hộp hay lo lắng quá không nha bé?
L06: Người nhà: Dạ thưa bác sĩ, lúc đầu hơi lo nhưng vào phòng khám thấy đỡ trong người bồn chồn hẳn.
L07: Người nhà: Khoảng mấy tháng nay trở lại đây cháu tôi thấy nhìn xa không rõ phải nheo mắt mới thấy rõ chữ trên bảng rõ rệt ạ.
L08: Bác sĩ: Ngoài chuyện đó ra, cơ thể có phát sinh thêm biểu hiện khó chịu nào nữa không ạ?
L09: Người nhà: Dạ, cháu tôi còn thấy mỏi điều tiết mắt chớp mắt nhiều khi nhìn xa, chỉ định đeo kính đúng độ và nhỏ thuốc atropin nồng độ thấp kiểm soát nữa.
L10: Bác sĩ: Về bệnh nền thì sao, sức khỏe của mình từ nhỏ đến giờ có vấn đề gì đáng lưu ý không hả bạn?
L11: Người nhà: Thưa bác sĩ, cháu tôi có chàm sữa ạ.
L12: Người nhà: Tôi cũng đang viêm gan B, nên tôi hay lo ạ.
L13: Bác sĩ: Để ghi vào hồ sơ bệnh án, mình có bị phản ứng lạ khi tiêm truyền hoặc uống thuốc không hả bạn?
L14: Người nhà: Vâng ạ, cơ địa cháu tôi bị dị ứng aspirin bác sĩ ạ.
L15: Bác sĩ: Qua lời kể vừa rồi, tôi sờ nắn vào chỗ đau xem mức độ thế nào một chút nhé.
L16: Bác sĩ: Kết quả khám thực thể ghi nhận: Thị lực không kính hai mắt giảm. nhé.
L17: Bác sĩ: Khả năng cao mình đang bị: Cận thị tiến triển. nha.
L18: Bác sĩ: Về phương án điều trị: Đo khúc xạ lại. Hạn chế màn hình, tăng hoạt động ngoài trời. nhé.
L19: Người nhà: Dạ thưa bác sĩ, tôi xin chân thành cảm ơn bác sĩ ạ, chào bác sĩ tôi về.
```
- **Đáp án mệnh đề (`dap_an`):**
  - `M01` [TIỀN SỬ BỆNH] `chu_the=bệnh nhân` | `noi_dung=từng dùng cetirizine, đã ngừng 1 tuần` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Lần khám trước tôi có kê cetirizine', 'ngừng 1 tuần rồi ạ']`
  - `M02` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=nhìn xa mờ phải nheo mắt mới thấy rõ chữ trên bảng` | `moc=mấy tháng nay` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Khoảng mấy tháng nay trở lại đây cháu tôi thấy nhìn xa không rõ phải nheo mắt mới thấy rõ chữ trên bảng rõ rệt ạ']`
  - `M03` [LÝ DO KHÁM BỆNH] `chu_the=bệnh nhân` | `noi_dung=nhìn xa mờ phải nheo mắt mới thấy rõ chữ trên bảng` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Khoảng mấy tháng nay trở lại đây cháu tôi thấy nhìn xa không rõ phải nheo mắt mới thấy rõ chữ trên bảng rõ rệt ạ']`
  - `M04` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=mỏi điều tiết mắt chớp mắt nhiều khi nhìn xa` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['cháu tôi còn thấy mỏi điều tiết mắt chớp mắt nhiều khi nhìn xa']`
  - `M05` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=chỉ định đeo kính đúng độ và nhỏ thuốc atropin nồng độ thấp kiểm soát` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['chỉ định đeo kính đúng độ và nhỏ thuốc atropin nồng độ thấp kiểm soát nữa']`
  - `M06` [TIỀN SỬ BỆNH] `chu_the=bệnh nhân` | `noi_dung=chàm sữa` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['cháu tôi có chàm sữa ạ']`
  - `M07` [TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI] `chu_the=người nhà` | `noi_dung=viêm gan B` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Tôi cũng đang viêm gan B']`
  - `M08` [DỊ ỨNG] `chu_the=bệnh nhân` | `noi_dung=dị ứng aspirin` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['cơ địa cháu tôi bị dị ứng aspirin bác sĩ ạ']`
  - `M09` [KHÁM LÂM SÀNG] `chu_the=bệnh nhân` | `noi_dung=Thị lực không kính hai mắt giảm` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Kết quả khám thực thể ghi nhận: Thị lực không kính hai mắt giảm']`
  - `M10` [CHẨN ĐOÁN] `chu_the=bệnh nhân` | `noi_dung=Cận thị tiến triển` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Khả năng cao mình đang bị: Cận thị tiến triển']`
  - `M11` [KẾ HOẠCH ĐIỀU TRỊ] `chu_the=bệnh nhân` | `noi_dung=Đo khúc xạ lại. Hạn chế màn hình, tăng hoạt động ngoài trời` | `moc=None` | `phu_dinh=False` | `tinh_huong=kế hoạch` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Về phương án điều trị: Đo khúc xạ lại. Hạn chế màn hình, tăng hoạt động ngoài trời']`
- **Các lỗi phát hiện khi đọc ca này (8 lỗi):**
  - **L03** — *Tiểu từ đề nghị (`nhé/nha/nghen`) gắn vào câu hỏi `?`*: `Bác sĩ: Hôm nay đi khám, bé đã cài đặt ứng dụng VssID trên điện thoại chưa nhé ạ?`
  - **L03-L04** — *Hỏi đáp xã giao lệch cặp (hỏi một đằng, đáp một nẻo)*: `Bác sĩ: Hôm nay đi khám, bé đã cài đặt ứng dụng VssID trên điện thoại chưa nhé ạ? / Người nhà: Dạ có ạ, phiếu thông tin em đã tích đầy đủ ngoài bàn đón tiếp bác sĩ ạ.`
  - **L05** — *Tiểu từ đề nghị (`nhé/nha/nghen`) gắn vào câu hỏi `?`*: `Bác sĩ: Bước vào phòng khám, bé có cảm thấy hồi hộp hay lo lắng quá không nha bé?`
  - **L10** — *Bác sĩ gọi người bệnh/người nhà là `bạn` (lệch vai xưng hô)*: `Bác sĩ: Về bệnh nền thì sao, sức khỏe của mình từ nhỏ đến giờ có vấn đề gì đáng lưu ý không hả bạn?`
  - **L13** — *Bác sĩ gọi người bệnh/người nhà là `bạn` (lệch vai xưng hô)*: `Bác sĩ: Để ghi vào hồ sơ bệnh án, mình có bị phản ứng lạ khi tiêm truyền hoặc uống thuốc không hả bạn?`
  - **L16** — *Hạt đề nghị thừa sau dấu chấm (`. nhé.`, `. nha.`, `. nghen.`)*: `Bác sĩ: Kết quả khám thực thể ghi nhận: Thị lực không kính hai mắt giảm. nhé.`
  - **L17** — *Hạt đề nghị thừa sau dấu chấm (`. nhé.`, `. nha.`, `. nghen.`)*: `Bác sĩ: Khả năng cao mình đang bị: Cận thị tiến triển. nha.`
  - **L18** — *Hạt đề nghị thừa sau dấu chấm (`. nhé.`, `. nha.`, `. nghen.`)*: `Bác sĩ: Về phương án điều trị: Đo khúc xạ lại. Hạn chế màn hình, tăng hoạt động ngoài trời. nhé.`

### Ca 16 — Mã: `hv_0908` (`hen tim`)
- **Thông tin ca:** `la_tre_em=False` | `nguoi_ke=mẹ` | `lo_danh_tinh=True` | `boi_canh=dieu_duong_ban_giao` | `bay=['bo_sung', 'dai_tu_ho_hang', 'luoc_chu_ngu', 'nguoi_nha_ke_ho', 'nguon_khac_nhau']` | `so_luot=21`
- **Lời thoại đầy đủ:**
```text
L01: Điều dưỡng: Em chào bác sĩ. Chị này vừa được đưa tới, em đã kiểm tra mạch nhiệt độ huyết áp xong xuôi ạ.
L02: Bác sĩ: Cảm ơn em nhé. Mời Chị ngồi nghỉ rồi kể xem triệu chứng xuất hiện thế nào ạ.
L03: Bác sĩ: Bác sĩ hỏi một chút, mình có quan hệ gia đình thế nào với chị ấy vậy ạ?
L04: Người nhà: Dạ vâng, tôi là mẹ đưa chị ấy đi khám bác sĩ ạ.
L05: Người nhà: Suốt năm hôm qua bị cơn khó thở dữ dội xuất hiện đột ngột về nửa đêm làm phiền nhiều ạ.
L06: Bệnh nhân: Không đúng đâu, tôi cơn khó thở dữ dội xuất hiện đột ngột về nửa đêm từ hôm kia rồi ạ.
L07: Bác sĩ: Để tôi ghi là chưa rõ năm hôm hay từ hôm kia, mình xác nhận lại sau nhé ạ.
L08: Bác sĩ: Ngoài các dấu hiệu đó ra, mình còn thấy bứt rứt hay có dấu hiệu lạ nào nữa không hả bạn?
L09: Người nhà: Dạ thưa bác, thấy kèm theo triệu chứng lo âu hoảng sợ, tim đập nhanh trong người bồn chồn khó ở ạ.
L10: Người nhà: Lo âu hoảng sợ thì nặng hơn sau khi ăn ạ.
L11: Bác sĩ: Trước đây, mình có đang theo dõi điều trị ở chuyên khoa nào khác không nhỉ?
L12: Người nhà: Dạ thưa bác sĩ không có, sức khỏe trước giờ ổn định, không có bệnh lý cũ đâu.
L13: Bác sĩ: Mình có bị phản ứng lạ khi tiêm truyền hoặc uống thuốc không nhỉ?
L14: Người nhà: Dạ không, chưa bao giờ bị nổi mề đay hay ngứa khi dùng thuốc bao giờ mô bác sĩ.
L15: Bác sĩ: Về việc dùng thuốc thì, đã thử uống thuốc gì để đỡ khó chịu chưa ạ?
L16: Người nhà: Dạ không, ở nhà chưa điều trị hay dùng bất cứ viên thuốc nào đâu nhe bác sĩ.
L17: Bác sĩ: Để bác sĩ nắm rõ hơn, bác sĩ kiểm tra họng và amidan xem có viêm đỏ không xem thế nào nhé.
L18: Điều dưỡng: Sinh hiệu em đo được: Khám thực thể: Bệnh nhân ngồi thở dốc, nghe phổi có ran rít ran ngáy rải rác kèm ran ẩm ở hai đáy phổi, tim nhanh có tiếng ngựa phi T3. đáng lưu ý.
L19: Bác sĩ: Xác định ban đầu là: Hen tim / Cơn phù phổi cấp dọa vỡ trên nền suy tim trái. rõ ràng.
L20: Bác sĩ: Trước mắt, tôi sẽ: Thở oxy qua kính, tiêm tĩnh mạch lợi tiểu quai furosemide và thuốc giãn mạch nitroglycerin. Theo dõi sát huyết áp và nồng độ SpO2. cho an tâm nhé.
L21: Người nhà: Dạ bác sĩ, tôi đã nắm rõ đơn thuốc và liều lượng, chúc bác sĩ một ngày làm việc thuận lợi ạ, chúc bác sĩ sức khỏe.
```
- **Đáp án mệnh đề (`dap_an`):**
  - `M01` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=cơn khó thở dữ dội xuất hiện đột ngột về nửa đêm` | `moc=năm hôm` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Suốt năm hôm qua bị cơn khó thở dữ dội xuất hiện đột ngột về nửa đêm làm phiền nhiều ạ']`
  - `M02` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=cơn khó thở dữ dội xuất hiện đột ngột về nửa đêm` | `moc=từ hôm kia` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=mâu thuẫn` | `trich_dan=['tôi cơn khó thở dữ dội xuất hiện đột ngột về nửa đêm từ hôm kia rồi ạ']`
  - `M03` [LÝ DO KHÁM BỆNH] `chu_the=bệnh nhân` | `noi_dung=cơn khó thở dữ dội xuất hiện đột ngột về nửa đêm` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Suốt năm hôm qua bị cơn khó thở dữ dội xuất hiện đột ngột về nửa đêm làm phiền nhiều ạ']`
  - `M04` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=lo âu hoảng sợ` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['thấy kèm theo triệu chứng lo âu hoảng sợ', 'Lo âu hoảng sợ thì nặng hơn sau khi ăn ạ']`
  - `M05` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=tim đập nhanh hồi hộp` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['tim đập nhanh trong người bồn chồn khó ở ạ']`
  - `M06` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=lo âu hoảng sợ nặng hơn sau khi ăn` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=bổ sung` | `trich_dan=['Lo âu hoảng sợ thì nặng hơn sau khi ăn ạ']`
  - `M07` [DỊ ỨNG] `chu_the=bệnh nhân` | `noi_dung=dị ứng thuốc` | `moc=None` | `phu_dinh=True` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Mình có bị phản ứng lạ khi tiêm truyền hoặc uống thuốc không nhỉ', 'chưa bao giờ bị nổi mề đay hay ngứa khi dùng thuốc bao giờ mô bác sĩ']`
  - `M08` [KHÁM LÂM SÀNG] `chu_the=bệnh nhân` | `noi_dung=Bệnh nhân ngồi thở dốc, nghe phổi có ran rít ran ngáy rải rác kèm ran ẩm ở hai đáy phổi, tim nhanh có tiếng ngựa phi T3` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Sinh hiệu em đo được: Khám thực thể: Bệnh nhân ngồi thở dốc, nghe phổi có ran rít ran ngáy rải rác kèm ran ẩm ở hai đáy phổi, tim nhanh có tiếng ngựa phi T3']`
  - `M09` [CHẨN ĐOÁN] `chu_the=bệnh nhân` | `noi_dung=Hen tim / Cơn phù phổi cấp dọa vỡ trên nền suy tim trái` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Xác định ban đầu là: Hen tim / Cơn phù phổi cấp dọa vỡ trên nền suy tim trái']`
  - `M10` [KẾ HOẠCH ĐIỀU TRỊ] `chu_the=bệnh nhân` | `noi_dung=Thở oxy qua kính, tiêm tĩnh mạch lợi tiểu quai furosemide và thuốc giãn mạch nitroglycerin. Theo dõi sát huyết áp và nồng độ SpO2` | `moc=None` | `phu_dinh=False` | `tinh_huong=kế hoạch` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['tôi sẽ: Thở oxy qua kính, tiêm tĩnh mạch lợi tiểu quai furosemide và thuốc giãn mạch nitroglycerin. Theo dõi sát huyết áp và nồng độ SpO2']`
- **Các lỗi phát hiện khi đọc ca này (6 lỗi):**
  - **L08** — *Bác sĩ gọi người bệnh/người nhà là `bạn` (lệch vai xưng hô)*: `Bác sĩ: Ngoài các dấu hiệu đó ra, mình còn thấy bứt rứt hay có dấu hiệu lạ nào nữa không hả bạn?`
  - **L14** — *Lặp từ phủ định `chưa bao giờ ... bao giờ`*: `Người nhà: Dạ không, chưa bao giờ bị nổi mề đay hay ngứa khi dùng thuốc bao giờ mô bác sĩ.`
  - **L18** — *Cụm nhận xét thừa sau dấu chấm ở cuối câu*: `Điều dưỡng: Sinh hiệu em đo được: Khám thực thể: Bệnh nhân ngồi thở dốc, nghe phổi có ran rít ran ngáy rải rác kèm ran ẩm ở hai đáy phổi, tim nhanh có tiếng ngựa phi T3. đáng lưu ý.`
  - **L18** — *Điều dưỡng lặp hai lần dẫn nhập `Sinh hiệu em đo được: Bác sĩ/Tôi...`*: `Điều dưỡng: Sinh hiệu em đo được: Khám thực thể: Bệnh nhân ngồi thở dốc, nghe phổi có ran rít ran ngáy rải rác kèm ran ẩm ở hai đáy phổi, tim nhanh có tiếng ngựa phi T3. đáng lưu ý.`
  - **L19** — *Cụm nhận xét thừa sau dấu chấm ở cuối câu*: `Bác sĩ: Xác định ban đầu là: Hen tim / Cơn phù phổi cấp dọa vỡ trên nền suy tim trái. rõ ràng.`
  - **L20** — *Cụm nhận xét thừa sau dấu chấm ở cuối câu*: `Bác sĩ: Trước mắt, tôi sẽ: Thở oxy qua kính, tiêm tĩnh mạch lợi tiểu quai furosemide và thuốc giãn mạch nitroglycerin. Theo dõi sát huyết áp và nồng độ SpO2. cho an tâm nhé.`

### Ca 17 — Mã: `hv_0435` (`động kinh cục bộ thùy thái dương`)
- **Thông tin ca:** `la_tre_em=True` | `nguoi_ke=bố` | `lo_danh_tinh=True` | `boi_canh=kham_lan_dau` | `bay=['nguoi_ke_benh_minh', 'nguoi_nha_ke_ho']` | `so_luot=15`
- **Lời thoại đầy đủ:**
```text
L01: Bác sĩ: Chào anh, gia đình thấy con phát bệnh từ hôm nào thế?
L02: Bác sĩ: Anh là gì của cháu vậy thế ạ?
L03: Người nhà: Thưa bác sĩ, cháu là người thân của tôi, tôi là bố ạ.
L04: Người nhà: Bé nhà tôi khó chịu vì cảm giác tiền triệu aura dâng lên từ thượng vị cảm giác quen thuộc deja vu hoặc sợ hãi vô cớ dai dẳng khoảng một tháng nay.
L05: Bác sĩ: Về cảm giác trong người, mình còn thấy bứt rứt hay có dấu hiệu lạ nào nữa không không?
L06: Người nhà: Dạ bác, bé nhà tôi còn chụp mri sọ não phát hiện xơ teo hồi hải mã thùy thái dương bên trái nữa ạ.
L07: Người nhà: Tôi bị bướu giáp nhân mấy năm nay rồi ạ.
L08: Bác sĩ: Cho tôi hỏi thêm, mình có dị ứng chất nào gây khó thở hay sưng môi mắt không không?
L09: Người nhà: Dạ không, chưa từng bị dị ứng thuốc hay hóa chất gì hết đâu nghen.
L10: Bác sĩ: Để đánh giá toàn diện, Con thả lỏng cơ bụng để tôi thăm khám nhẹ nhàng xem thế nào nhé.
L11: Bác sĩ: Qua việc thăm khám cụ thể: Ngoài cơn: khám thần kinh bình thường, không có dấu hiệu thần kinh khu trú. nghen.
L12: Bác sĩ: Trường hợp này được chẩn đoán là: Động kinh cục bộ phức tạp thùy thái dương có xơ teo hồi hải mã. nghen.
L13: Bác sĩ: Bác sĩ đề ra phác đồ: Thuốc chống động kinh carbamazepine hoặc levetiracetam liều dò duy trì. Hướng dẫn an toàn tránh bơi lội làm việc trên cao và ngủ đủ giấc. nhé ạ.
L14: Bác sĩ: Tôi cho kê thuốc nhỏ mắt natri clorid một giọt, nhỏ ngày ba lần nghen.
L15: Người nhà: Dạ đa tạ bác sĩ, tôi xin cảm ơn bác sĩ đã thăm khám cặn kẽ nghen, chào bác sĩ.
```
- **Đáp án mệnh đề (`dap_an`):**
  - `M01` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=cảm giác tiền triệu aura dâng lên từ thượng vị cảm giác quen thuộc deja vu hoặc sợ hãi vô cớ` | `moc=khoảng một tháng` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Bé nhà tôi khó chịu vì cảm giác tiền triệu aura dâng lên từ thượng vị cảm giác quen thuộc deja vu hoặc sợ hãi vô cớ dai dẳng khoảng một tháng nay']`
  - `M02` [LÝ DO KHÁM BỆNH] `chu_the=bệnh nhân` | `noi_dung=cảm giác tiền triệu aura dâng lên từ thượng vị cảm giác quen thuộc deja vu hoặc sợ hãi vô cớ` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Bé nhà tôi khó chịu vì cảm giác tiền triệu aura dâng lên từ thượng vị cảm giác quen thuộc deja vu hoặc sợ hãi vô cớ dai dẳng khoảng một tháng nay']`
  - `M03` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=chụp mri sọ não phát hiện xơ teo hồi hải mã thùy thái dương bên trái` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['bé nhà tôi còn chụp mri sọ não phát hiện xơ teo hồi hải mã thùy thái dương bên trái nữa ạ']`
  - `M04` [TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI] `chu_the=bố` | `noi_dung=bướu giáp nhân` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Tôi bị bướu giáp nhân mấy năm nay rồi ạ']`
  - `M05` [DỊ ỨNG] `chu_the=bệnh nhân` | `noi_dung=dị ứng thuốc` | `moc=None` | `phu_dinh=True` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['mình có dị ứng chất nào gây khó thở hay sưng môi mắt không không', 'chưa từng bị dị ứng thuốc hay hóa chất gì hết đâu nghen']`
  - `M06` [KHÁM LÂM SÀNG] `chu_the=bệnh nhân` | `noi_dung=Ngoài cơn: khám thần kinh bình thường, không có dấu hiệu thần kinh khu trú` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Qua việc thăm khám cụ thể: Ngoài cơn: khám thần kinh bình thường, không có dấu hiệu thần kinh khu trú']`
  - `M07` [CHẨN ĐOÁN] `chu_the=bệnh nhân` | `noi_dung=Động kinh cục bộ phức tạp thùy thái dương có xơ teo hồi hải mã` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Trường hợp này được chẩn đoán là: Động kinh cục bộ phức tạp thùy thái dương có xơ teo hồi hải mã']`
  - `M08` [KẾ HOẠCH ĐIỀU TRỊ] `chu_the=bệnh nhân` | `noi_dung=Thuốc chống động kinh carbamazepine hoặc levetiracetam liều dò duy trì. Hướng dẫn an toàn tránh bơi lội làm việc trên cao và ngủ đủ giấc` | `moc=None` | `phu_dinh=False` | `tinh_huong=kế hoạch` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Bác sĩ đề ra phác đồ: Thuốc chống động kinh carbamazepine hoặc levetiracetam liều dò duy trì. Hướng dẫn an toàn tránh bơi lội làm việc trên cao và ngủ đủ giấc']`
  - `M09` [KẾ HOẠCH ĐIỀU TRỊ] `chu_the=bệnh nhân` | `noi_dung=kê thuốc nhỏ mắt natri clorid` | `moc=None` | `phu_dinh=False` | `tinh_huong=kế hoạch` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Tôi cho kê thuốc nhỏ mắt natri clorid một giọt, nhỏ ngày ba lần nghen']`
- **Các lỗi phát hiện khi đọc ca này (7 lỗi):**
  - **L02** — *Lặp từ nghi vấn `vậy vậy` / `vậy thế`*: `Bác sĩ: Anh là gì của cháu vậy thế ạ?`
  - **L05** — *Lặp từ nghi vấn `không không` / `chưa không`*: `Bác sĩ: Về cảm giác trong người, mình còn thấy bứt rứt hay có dấu hiệu lạ nào nữa không không?`
  - **L07** — *Lặp từ thời gian `nay nay` / `rồi nay` / `nay rồi nay`*: `Người nhà: Tôi bị bướu giáp nhân mấy năm nay rồi ạ.`
  - **L08** — *Lặp từ nghi vấn `không không` / `chưa không`*: `Bác sĩ: Cho tôi hỏi thêm, mình có dị ứng chất nào gây khó thở hay sưng môi mắt không không?`
  - **L11** — *Hạt đề nghị thừa sau dấu chấm (`. nhé.`, `. nha.`, `. nghen.`)*: `Bác sĩ: Qua việc thăm khám cụ thể: Ngoài cơn: khám thần kinh bình thường, không có dấu hiệu thần kinh khu trú. nghen.`
  - **L12** — *Hạt đề nghị thừa sau dấu chấm (`. nhé.`, `. nha.`, `. nghen.`)*: `Bác sĩ: Trường hợp này được chẩn đoán là: Động kinh cục bộ phức tạp thùy thái dương có xơ teo hồi hải mã. nghen.`
  - **L13** — *Hạt đề nghị thừa sau dấu chấm (`. nhé.`, `. nha.`, `. nghen.`)*: `Bác sĩ: Bác sĩ đề ra phác đồ: Thuốc chống động kinh carbamazepine hoặc levetiracetam liều dò duy trì. Hướng dẫn an toàn tránh bơi lội làm việc trên cao và ngủ đủ giấc. nhé ạ.`

### Ca 18 — Mã: `hv_2310` (`viêm tắc động mạch chi dưới mạn tính`)
- **Thông tin ca:** `la_tre_em=False` | `nguoi_ke=None` | `lo_danh_tinh=False` | `boi_canh=kham_lan_dau` | `bay=[]` | `so_luot=20`
- **Lời thoại đầy đủ:**
```text
L01: Bác sĩ: Mời chị ngồi. Chị bị làm sao?
L02: Bác sĩ: Để ghi vào hồ sơ thì, hôm nay chị là người trực tiếp cần khám đúng không vậy ạ?
L03: Bệnh nhân: Dạ thưa bác sĩ, tôi đi khám cho chính mình ạ.
L04: Bác sĩ: Trước khi vào phòng khám, Chị có cần dùng thêm cốc nước lọc ở cây nước không nhé?
L05: Bệnh nhân: Vâng ạ, em có mang theo bình nước ấm uống suốt dọc đường rồi nha bác sĩ.
L06: Bệnh nhân: Tình trạng dấu hiệu đau cách hồi đi bộ một đoạn khoảng 100 mét thì đau bắp chân phải dừng lại nghỉ của tôi kéo dài mấy tháng nay rồi.
L07: Bác sĩ: Ngoài các dấu hiệu đó ra, mình còn cảm thấy khó chịu ở chỗ nào khác nữa không nhỉ?
L08: Bệnh nhân: Dạ bác sĩ, tôi còn loét hoại tử khô ngón chân ngón cái bờ lõm sâu không chảy máu nữa.
L09: Bác sĩ: Cho tôi hỏi về sức khỏe trước giờ, bạn có tiền sử bệnh tim mạch, huyết áp hay dạ dày gì không vậy ạ?
L10: Bệnh nhân: Dạ thưa bác, tôi có đái tháo đường ạ.
L11: Bác sĩ: Để ghi vào hồ sơ bệnh án, bạn có mẫn cảm đặc biệt với thành phần thuốc nào không không?
L12: Bệnh nhân: Dạ hổng có, chưa bao giờ bị nổi mề đay hay ngứa khi dùng thuốc bao giờ nghen bác sĩ.
L13: Bác sĩ: Hiện tại, trước khi đến phòng khám, mình đã uống liều thuốc nào chưa vậy?
L14: Bệnh nhân: Dạ không có đâu ạ, chưa uống loại thuốc nào ở nhà đâu hết á.
L15: Bác sĩ: Bây giờ, để tôi đo lại huyết áp và sinh hiệu cho chị nha chị.
L16: Bác sĩ: Qua việc thăm khám cụ thể: Mạch mu chân hai bên mất, chân trái lạnh teo cơ bắp chân, ABI chân trái 0.55. cần theo dõi.
L17: Bác sĩ: Tôi xác định tình trạng này là: Viêm tắc động mạch chi dưới mạn tính giai đoạn 3 theo Fontaine do xơ vữa. nha.
L18: Bác sĩ: Kế hoạch dùng thuốc và theo dõi: Thuốc ức chế ngưng tập tiểu cầu clopidogrel kết hợp cilostazol giãn mạch tăng tuần hoàn bàng hệ. Chụp cắt lớp vi tính mạch máu cta chi dưới xét can thiệp nong đặt stent. để theo dõi thêm.
L19: Bác sĩ: Tôi bổ sung kê amoxicillin 250 mg, uống ngày ba lần nhé.
L20: Bệnh nhân: Dạ tôi rõ phác đồ rồi, tôi ghi nhớ kỹ các dặn dò này rồi, cảm ơn bác sĩ đã giúp đỡ nha, chào bác sĩ tôi về.
```
- **Đáp án mệnh đề (`dap_an`):**
  - `M01` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=dấu hiệu đau cách hồi đi bộ một đoạn khoảng 100 mét thì đau bắp chân phải dừng lại nghỉ` | `moc=mấy tháng nay` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Tình trạng dấu hiệu đau cách hồi đi bộ một đoạn khoảng 100 mét thì đau bắp chân phải dừng lại nghỉ của tôi kéo dài mấy tháng nay rồi']`
  - `M02` [LÝ DO KHÁM BỆNH] `chu_the=bệnh nhân` | `noi_dung=dấu hiệu đau cách hồi đi bộ một đoạn khoảng 100 mét thì đau bắp chân phải dừng lại nghỉ` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Tình trạng dấu hiệu đau cách hồi đi bộ một đoạn khoảng 100 mét thì đau bắp chân phải dừng lại nghỉ của tôi kéo dài mấy tháng nay rồi']`
  - `M03` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=loét hoại tử khô ngón chân ngón cái bờ lõm sâu không chảy máu` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['tôi còn loét hoại tử khô ngón chân ngón cái bờ lõm sâu không chảy máu nữa']`
  - `M04` [TIỀN SỬ BỆNH] `chu_the=bệnh nhân` | `noi_dung=đái tháo đường` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['tôi có đái tháo đường ạ']`
  - `M05` [DỊ ỨNG] `chu_the=bệnh nhân` | `noi_dung=dị ứng thuốc` | `moc=None` | `phu_dinh=True` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['bạn có mẫn cảm đặc biệt với thành phần thuốc nào không không', 'chưa bao giờ bị nổi mề đay hay ngứa khi dùng thuốc bao giờ nghen bác sĩ']`
  - `M06` [KHÁM LÂM SÀNG] `chu_the=bệnh nhân` | `noi_dung=Mạch mu chân hai bên mất, chân trái lạnh teo cơ bắp chân, ABI chân trái 0.55` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Qua việc thăm khám cụ thể: Mạch mu chân hai bên mất, chân trái lạnh teo cơ bắp chân, ABI chân trái 0.55']`
  - `M07` [CHẨN ĐOÁN] `chu_the=bệnh nhân` | `noi_dung=Viêm tắc động mạch chi dưới mạn tính giai đoạn 3 theo Fontaine do xơ vữa` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Tôi xác định tình trạng này là: Viêm tắc động mạch chi dưới mạn tính giai đoạn 3 theo Fontaine do xơ vữa']`
  - `M08` [KẾ HOẠCH ĐIỀU TRỊ] `chu_the=bệnh nhân` | `noi_dung=Thuốc ức chế ngưng tập tiểu cầu clopidogrel kết hợp cilostazol giãn mạch tăng tuần hoàn bàng hệ. Chụp cắt lớp vi tính mạch máu cta chi dưới xét can thiệp nong đặt stent` | `moc=None` | `phu_dinh=False` | `tinh_huong=kế hoạch` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Kế hoạch dùng thuốc và theo dõi: Thuốc ức chế ngưng tập tiểu cầu clopidogrel kết hợp cilostazol giãn mạch tăng tuần hoàn bàng hệ. Chụp cắt lớp vi tính mạch máu cta chi dưới xét can thiệp nong đặt stent']`
  - `M09` [KẾ HOẠCH ĐIỀU TRỊ] `chu_the=bệnh nhân` | `noi_dung=kê amoxicillin` | `moc=None` | `phu_dinh=False` | `tinh_huong=kế hoạch` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Tôi bổ sung kê amoxicillin 250 mg, uống ngày ba lần nhé']`
- **Các lỗi phát hiện khi đọc ca này (11 lỗi):**
  - **L04** — *Tiểu từ đề nghị (`nhé/nha/nghen`) gắn vào câu hỏi `?`*: `Bác sĩ: Trước khi vào phòng khám, Chị có cần dùng thêm cốc nước lọc ở cây nước không nhé?`
  - **L04-L05** — *Hỏi đáp xã giao lệch cặp (hỏi một đằng, đáp một nẻo)*: `Bác sĩ: Trước khi vào phòng khám, Chị có cần dùng thêm cốc nước lọc ở cây nước không nhé? / Bệnh nhân: Vâng ạ, em có mang theo bình nước ấm uống suốt dọc đường rồi nha bác sĩ.`
  - **L06** — *Lặp từ thời gian `nay nay` / `rồi nay` / `nay rồi nay`*: `Bệnh nhân: Tình trạng dấu hiệu đau cách hồi đi bộ một đoạn khoảng 100 mét thì đau bắp chân phải dừng lại nghỉ của tôi kéo dài mấy tháng nay rồi.`
  - **L09** — *Bác sĩ gọi người bệnh/người nhà là `bạn` (lệch vai xưng hô)*: `Bác sĩ: Cho tôi hỏi về sức khỏe trước giờ, bạn có tiền sử bệnh tim mạch, huyết áp hay dạ dày gì không vậy ạ?`
  - **L11** — *Lặp từ nghi vấn `không không` / `chưa không`*: `Bác sĩ: Để ghi vào hồ sơ bệnh án, bạn có mẫn cảm đặc biệt với thành phần thuốc nào không không?`
  - **L11** — *Bác sĩ gọi người bệnh/người nhà là `bạn` (lệch vai xưng hô)*: `Bác sĩ: Để ghi vào hồ sơ bệnh án, bạn có mẫn cảm đặc biệt với thành phần thuốc nào không không?`
  - **L12** — *Lặp từ phủ định `chưa bao giờ ... bao giờ`*: `Bệnh nhân: Dạ hổng có, chưa bao giờ bị nổi mề đay hay ngứa khi dùng thuốc bao giờ nghen bác sĩ.`
  - **L14** — *Ghép thừa hai từ phủ định `đâu hết á`*: `Bệnh nhân: Dạ không có đâu ạ, chưa uống loại thuốc nào ở nhà đâu hết á.`
  - **L16** — *Cụm nhận xét thừa sau dấu chấm ở cuối câu*: `Bác sĩ: Qua việc thăm khám cụ thể: Mạch mu chân hai bên mất, chân trái lạnh teo cơ bắp chân, ABI chân trái 0.55. cần theo dõi.`
  - **L17** — *Hạt đề nghị thừa sau dấu chấm (`. nhé.`, `. nha.`, `. nghen.`)*: `Bác sĩ: Tôi xác định tình trạng này là: Viêm tắc động mạch chi dưới mạn tính giai đoạn 3 theo Fontaine do xơ vữa. nha.`
  - **L18** — *Cụm nhận xét thừa sau dấu chấm ở cuối câu*: `Bác sĩ: Kế hoạch dùng thuốc và theo dõi: Thuốc ức chế ngưng tập tiểu cầu clopidogrel kết hợp cilostazol giãn mạch tăng tuần hoàn bàng hệ. Chụp cắt lớp vi tính mạch máu cta chi dưới xét can thiệp nong đặt stent. để theo dõi thêm.`

### Ca 19 — Mã: `hv_2803` (`viêm da tiếp xúc`)
- **Thông tin ca:** `la_tre_em=True` | `nguoi_ke=mẹ` | `lo_danh_tinh=False` | `boi_canh=kham_lan_dau` | `bay=['gia_dinh', 'hoi_khong_dap', 'luoc_chu_ngu', 'nguoi_nha_ke_ho']` | `so_luot=15`
- **Lời thoại đầy đủ:**
```text
L01: Bác sĩ: Mời chị ngồi. Bé nhà mình bị làm sao ạ?
L02: Bác sĩ: Dạo này trời chuyển mùa, bé đi ra ngoài có cảm thấy khó chịu trong người không thế bé?
L03: Người nhà: Vâng ạ, em có che chắn kỹ càng và đeo khẩu trang chống bụi bác sĩ ạ.
L04: Người nhà: Xuất hiện dát đỏ mụn nước ranh giới rõ rệt giới hạn đúng vị trí tiếp xúc được hơn một tuần rồi ạ.
L05: Bác sĩ: Liệu còn vấn đề gì, có triệu chứng nào khác đi kèm mà mình nhận thấy không nhé?
L06: Người nhà: Dạ vâng, còn than phiền là bị thử nghiệm áp da patch test tìm ra dị nguyên gây bệnh nữa.
L07: Bác sĩ: Trước đây, trước đây mình đã từng phải nằm viện hay phẫu thuật lần nào chưa nhỉ?
L08: Người nhà: Dạ hổng có, sức khỏe trước giờ ổn định, không có bệnh lý cũ cả nghen bác sĩ.
L09: Bác sĩ: Mấy hôm nay sinh hoạt ăn ngủ có điều độ không ạ?
L10: Bác sĩ: Bây giờ bác sĩ sẽ, để bác sĩ nắn xem các hạch ngoại vi có sưng không nha bé.
L11: Bác sĩ: Bác sĩ ghi nhận tình trạng: Ban đỏ giới hạn rõ ở vùng tiếp xúc. nhé.
L12: Bác sĩ: Qua tổng hợp dấu hiệu, tôi chẩn đoán: Viêm da tiếp xúc. rõ ràng.
L13: Bác sĩ: Phác đồ điều trị đợt này là: Ngừng tiếp xúc chất nghi ngờ. Bôi corticoid nhẹ trong năm ngày. cho an tâm nhé.
L14: Bác sĩ: Nếu mai bé còn cảm giác châm chích ngứa rát bỏng tại vùng da nghi ngờ thì đưa đi khám lại nhé.
L15: Người nhà: Dạ, chúc bác sĩ một ngày làm việc thuận lợi, em sẽ quay lại tái khám đúng ngày hẹn nè bác sĩ.
```
- **Đáp án mệnh đề (`dap_an`):**
  - `M01` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=dát đỏ mụn nước ranh giới rõ rệt giới hạn đúng vị trí tiếp xúc` | `moc=hơn một tuần` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Xuất hiện dát đỏ mụn nước ranh giới rõ rệt giới hạn đúng vị trí tiếp xúc được hơn một tuần rồi ạ']`
  - `M02` [LÝ DO KHÁM BỆNH] `chu_the=bệnh nhân` | `noi_dung=dát đỏ mụn nước ranh giới rõ rệt giới hạn đúng vị trí tiếp xúc` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Xuất hiện dát đỏ mụn nước ranh giới rõ rệt giới hạn đúng vị trí tiếp xúc được hơn một tuần rồi ạ']`
  - `M03` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=thử nghiệm áp da patch test tìm ra dị nguyên gây bệnh` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['còn than phiền là bị thử nghiệm áp da patch test tìm ra dị nguyên gây bệnh nữa']`
  - `M04` [KHÁM LÂM SÀNG] `chu_the=bệnh nhân` | `noi_dung=Ban đỏ giới hạn rõ ở vùng tiếp xúc` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Bác sĩ ghi nhận tình trạng: Ban đỏ giới hạn rõ ở vùng tiếp xúc']`
  - `M05` [CHẨN ĐOÁN] `chu_the=bệnh nhân` | `noi_dung=Viêm da tiếp xúc` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['tôi chẩn đoán: Viêm da tiếp xúc']`
  - `M06` [KẾ HOẠCH ĐIỀU TRỊ] `chu_the=bệnh nhân` | `noi_dung=Ngừng tiếp xúc chất nghi ngờ. Bôi corticoid nhẹ trong năm ngày` | `moc=None` | `phu_dinh=False` | `tinh_huong=kế hoạch` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Phác đồ điều trị đợt này là: Ngừng tiếp xúc chất nghi ngờ. Bôi corticoid nhẹ trong năm ngày']`
  - `M07` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=cảm giác châm chích ngứa rát bỏng tại vùng da nghi ngờ` | `moc=None` | `phu_dinh=False` | `tinh_huong=giả định` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Nếu mai bé còn cảm giác châm chích ngứa rát bỏng tại vùng da nghi ngờ thì đưa đi khám lại nhé']`
- **Các lỗi phát hiện khi đọc ca này (6 lỗi):**
  - **L05** — *Tiểu từ đề nghị (`nhé/nha/nghen`) gắn vào câu hỏi `?`*: `Bác sĩ: Liệu còn vấn đề gì, có triệu chứng nào khác đi kèm mà mình nhận thấy không nhé?`
  - **L07** — *Lặp cụm `Trước đây, trước đây`*: `Bác sĩ: Trước đây, trước đây mình đã từng phải nằm viện hay phẫu thuật lần nào chưa nhỉ?`
  - **L10** — *Dẫn nhập bỏ lửng `Bây giờ bác sĩ sẽ, ...`*: `Bác sĩ: Bây giờ bác sĩ sẽ, để bác sĩ nắn xem các hạch ngoại vi có sưng không nha bé.`
  - **L11** — *Hạt đề nghị thừa sau dấu chấm (`. nhé.`, `. nha.`, `. nghen.`)*: `Bác sĩ: Bác sĩ ghi nhận tình trạng: Ban đỏ giới hạn rõ ở vùng tiếp xúc. nhé.`
  - **L12** — *Cụm nhận xét thừa sau dấu chấm ở cuối câu*: `Bác sĩ: Qua tổng hợp dấu hiệu, tôi chẩn đoán: Viêm da tiếp xúc. rõ ràng.`
  - **L13** — *Cụm nhận xét thừa sau dấu chấm ở cuối câu*: `Bác sĩ: Phác đồ điều trị đợt này là: Ngừng tiếp xúc chất nghi ngờ. Bôi corticoid nhẹ trong năm ngày. cho an tâm nhé.`

### Ca 20 — Mã: `hv_3823` (`đau dây thần kinh sinh ba số V`)
- **Thông tin ca:** `la_tre_em=False` | `nguoi_ke=None` | `lo_danh_tinh=False` | `boi_canh=dieu_duong_ban_giao` | `bay=[]` | `so_luot=14`
- **Lời thoại đầy đủ:**
```text
L01: Điều dưỡng: Em chào bác sĩ. Ông này vừa hoàn tất phiếu khám, em đo huyết áp thấy các chỉ số bình thường ạ.
L02: Bác sĩ: Tôi rõ rồi, cảm ơn em. Ông thấy sức khỏe có gì bất thường mấy hôm nay?
L03: Bệnh nhân: Dạ thưa bác, tôi khó chịu vì cơn đau nhói giật dữ dội như luồng điện giật hoặc dao đâm dọc nhánh hàm dưới dây v dai dẳng mấy tháng nay nay ạ.
L04: Bác sĩ: Ngoài chuyện đó ra, cơ thể có phát sinh thêm biểu hiện khó chịu nào nữa không nhé?
L05: Bệnh nhân: Dạ thưa bác, bên cạnh đó tôi cũng bị thời gian cơn đau kéo dài từ vài giây đến một phút rồi dứt cơn hoàn toàn, chụp mri mạch máu sọ não tìm thấy xung đột mạch máu thần kinh chèn ép rễ dây thần kinh sinh ba ạ.
L06: Bác sĩ: Liên quan đến thuốc men, đã có lần nào dùng thuốc mà bị phù mắt hay nổi ban dị ứng chưa nhỉ?
L07: Bệnh nhân: Dạ không có đâu ạ, chưa bao giờ bị nổi mề đay hay ngứa khi dùng thuốc xưa nay ạ.
L08: Bác sĩ: Mấy ngày qua, mấy hôm nay đã tự điều trị bằng thuốc gì ở nhà chưa vậy?
L09: Bệnh nhân: Dạ em nghe bác sĩ, tôi có uống augmentin 625 mg, ngày hai lần.
L10: Bác sĩ: Thôi được rồi, để tôi gõ nhẹ vùng lưng xem thận có đau không xem thế nào nhé.
L11: Điều dưỡng: Sinh hiệu em đo được: Tôi ghi nhận: Ấn điểm xuất chiếu dây V3 đau chói, cảm giác da mặt hai bên đối xứng không mất.
L12: Bác sĩ: Bác sĩ chẩn đoán mình bị: Đau dây thần kinh sinh ba nhánh V3 bên phải do xung đột mạch máu thần kinh. nha.
L13: Bác sĩ: Tôi đề xuất kế hoạch: Thuốc cắt cơn giảm đau thần kinh carbamazepine tegretol tăng dần liều. Nếu kháng thuốc chuyển phẫu thuật giải ép vi mạch jannetta hoặc can thiệp tiêm cồn hạch gasser. cho an tâm nhé.
L14: Bệnh nhân: Dạ tôi rõ phác đồ rồi, tôi đã rõ giờ uống các cữ thuốc trong ngày rồi, chúc phòng khám luôn đông bệnh nhân yêu quý dữ lắm nghen.
```
- **Đáp án mệnh đề (`dap_an`):**
  - `M01` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=cơn đau nhói giật dữ dội như luồng điện giật hoặc dao đâm dọc nhánh hàm dưới dây v` | `moc=mấy tháng nay` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['tôi khó chịu vì cơn đau nhói giật dữ dội như luồng điện giật hoặc dao đâm dọc nhánh hàm dưới dây v dai dẳng mấy tháng nay nay ạ']`
  - `M02` [LÝ DO KHÁM BỆNH] `chu_the=bệnh nhân` | `noi_dung=cơn đau nhói giật dữ dội như luồng điện giật hoặc dao đâm dọc nhánh hàm dưới dây v` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['tôi khó chịu vì cơn đau nhói giật dữ dội như luồng điện giật hoặc dao đâm dọc nhánh hàm dưới dây v dai dẳng mấy tháng nay nay ạ']`
  - `M03` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=thời gian cơn đau kéo dài từ vài giây đến một phút rồi dứt cơn hoàn toàn` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['bên cạnh đó tôi cũng bị thời gian cơn đau kéo dài từ vài giây đến một phút rồi dứt cơn hoàn toàn']`
  - `M04` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=chụp mri mạch máu sọ não tìm thấy xung đột mạch máu thần kinh chèn ép rễ dây thần kinh sinh ba` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['chụp mri mạch máu sọ não tìm thấy xung đột mạch máu thần kinh chèn ép rễ dây thần kinh sinh ba ạ']`
  - `M05` [DỊ ỨNG] `chu_the=bệnh nhân` | `noi_dung=dị ứng thuốc` | `moc=None` | `phu_dinh=True` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['đã có lần nào dùng thuốc mà bị phù mắt hay nổi ban dị ứng chưa nhỉ', 'chưa bao giờ bị nổi mề đay hay ngứa khi dùng thuốc xưa nay ạ']`
  - `M06` [THUỐC ĐANG DÙNG] `chu_the=bệnh nhân` | `noi_dung=augmentin` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['tôi có uống augmentin 625 mg, ngày hai lần']`
  - `M07` [KHÁM LÂM SÀNG] `chu_the=bệnh nhân` | `noi_dung=Ấn điểm xuất chiếu dây V3 đau chói, cảm giác da mặt hai bên đối xứng không mất` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Sinh hiệu em đo được: Tôi ghi nhận: Ấn điểm xuất chiếu dây V3 đau chói, cảm giác da mặt hai bên đối xứng không mất']`
  - `M08` [CHẨN ĐOÁN] `chu_the=bệnh nhân` | `noi_dung=Đau dây thần kinh sinh ba nhánh V3 bên phải do xung đột mạch máu thần kinh` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Bác sĩ chẩn đoán mình bị: Đau dây thần kinh sinh ba nhánh V3 bên phải do xung đột mạch máu thần kinh']`
  - `M09` [KẾ HOẠCH ĐIỀU TRỊ] `chu_the=bệnh nhân` | `noi_dung=Thuốc cắt cơn giảm đau thần kinh carbamazepine tegretol tăng dần liều. Nếu kháng thuốc chuyển phẫu thuật giải ép vi mạch jannetta hoặc can thiệp tiêm cồn hạch gasser` | `moc=None` | `phu_dinh=False` | `tinh_huong=kế hoạch` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Tôi đề xuất kế hoạch: Thuốc cắt cơn giảm đau thần kinh carbamazepine tegretol tăng dần liều. Nếu kháng thuốc chuyển phẫu thuật giải ép vi mạch jannetta hoặc can thiệp tiêm cồn hạch gasser']`
- **Các lỗi phát hiện khi đọc ca này (8 lỗi):**
  - **L03** — *Lặp từ thời gian `nay nay` / `rồi nay` / `nay rồi nay`*: `Bệnh nhân: Dạ thưa bác, tôi khó chịu vì cơn đau nhói giật dữ dội như luồng điện giật hoặc dao đâm dọc nhánh hàm dưới dây v dai dẳng mấy tháng nay nay ạ.`
  - **L04** — *Tiểu từ đề nghị (`nhé/nha/nghen`) gắn vào câu hỏi `?`*: `Bác sĩ: Ngoài chuyện đó ra, cơ thể có phát sinh thêm biểu hiện khó chịu nào nữa không nhé?`
  - **L08** — *Lặp mốc thời gian `Mấy ngày qua, mấy hôm nay`*: `Bác sĩ: Mấy ngày qua, mấy hôm nay đã tự điều trị bằng thuốc gì ở nhà chưa vậy?`
  - **L09** — *Xung đột đại từ tự xưng trong cùng một câu (`em` vs `tôi`)*: `Bệnh nhân: Dạ em nghe bác sĩ, tôi có uống augmentin 625 mg, ngày hai lần.`
  - **L09** — *Từ đệm mở đầu lệch đại từ tự xưng với phần thân câu*: `Bệnh nhân: Dạ em nghe bác sĩ, tôi có uống augmentin 625 mg, ngày hai lần.`
  - **L11** — *Điều dưỡng lặp hai lần dẫn nhập `Sinh hiệu em đo được: Bác sĩ/Tôi...`*: `Điều dưỡng: Sinh hiệu em đo được: Tôi ghi nhận: Ấn điểm xuất chiếu dây V3 đau chói, cảm giác da mặt hai bên đối xứng không mất.`
  - **L12** — *Hạt đề nghị thừa sau dấu chấm (`. nhé.`, `. nha.`, `. nghen.`)*: `Bác sĩ: Bác sĩ chẩn đoán mình bị: Đau dây thần kinh sinh ba nhánh V3 bên phải do xung đột mạch máu thần kinh. nha.`
  - **L13** — *Cụm nhận xét thừa sau dấu chấm ở cuối câu*: `Bác sĩ: Tôi đề xuất kế hoạch: Thuốc cắt cơn giảm đau thần kinh carbamazepine tegretol tăng dần liều. Nếu kháng thuốc chuyển phẫu thuật giải ép vi mạch jannetta hoặc can thiệp tiêm cồn hạch gasser. cho an tâm nhé.`

### Ca 21 — Mã: `hv_2677` (`đau vai gáy`)
- **Thông tin ca:** `la_tre_em=False` | `nguoi_ke=None` | `lo_danh_tinh=False` | `boi_canh=cho_ket_qua` | `bay=[]` | `so_luot=17`
- **Lời thoại đầy đủ:**
```text
L01: Bác sĩ: Anh kể tôi nghe xem dạo này thế nào ạ.
L02: Bác sĩ: Quy trình lấy số thứ tự hôm nay, Anh có phải chờ đợi lâu ở quầy đăng ký không ạ?
L03: Bệnh nhân: Dạ thưa bác sĩ, em bấm máy lấy số tự động là được vào ngay nghen bác sĩ.
L04: Bệnh nhân: Tôi chịu đựng tình trạng nhức sau gáy cũng nửa năm rồi nay ạ.
L05: Bác sĩ: Trong mấy ngày nay, ngoài những điều vừa kể, bạn có thấy phát sinh dấu hiệu nào mới không không ạ?
L06: Bệnh nhân: Dạ em nghe bác sĩ, tôi còn thấy khó xoay cổ nữa.
L07: Bác sĩ: Từ trước đến nay, có tiền sử gan, thận, hen suyễn hay tiểu đường gì không hả bạn?
L08: Bệnh nhân: Dạ đúng rồi bác sĩ, tôi có thiếu máu.
L09: Bác sĩ: Liên quan đến thuốc men, trong quá khứ có ghi nhận dị ứng thuốc nào đáng chú ý không?
L10: Bệnh nhân: Dạ không ạ, uống các loại thuốc tây hay thuốc nam đều bình thường đâu hết á.
L11: Bác sĩ: Nhân tiện thì, bạn đã tự mua thuốc gì ở tiệm thuốc tây uống chưa vậy?
L12: Bệnh nhân: Dạ, tôi có uống panadol, ngày ba lần, dùng được hai tuần nay ạ.
L13: Bác sĩ: Trước hết, bác sĩ kiểm tra phản xạ thần kinh và cơ lực một chút nhé.
L14: Bác sĩ: Dấu hiệu thực thể gồm: Co cứng cơ thang hai bên, ấn đau vùng gáy.
L15: Bác sĩ: Tôi nghĩ nhiều đến đau vai gáy do tư thế, nhưng chưa kết luận được. Phải có kết quả xét nghiệm nước tiểu đã.
L16: Bác sĩ: Anh đi làm xét nghiệm nước tiểu rồi quay lại đây.
L17: Bệnh nhân: Dạ tôi hiểu rồi nè, tôi đã lưu số điện thoại phòng khám để liên hệ, chúc bác sĩ vạn sự như ý nha, tôi ra quầy lấy thuốc đây.
```
- **Đáp án mệnh đề (`dap_an`):**
  - `M01` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=đau gáy` | `moc=nửa năm rồi` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Tôi chịu đựng tình trạng nhức sau gáy cũng nửa năm rồi nay ạ']`
  - `M02` [LÝ DO KHÁM BỆNH] `chu_the=bệnh nhân` | `noi_dung=đau gáy` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Tôi chịu đựng tình trạng nhức sau gáy cũng nửa năm rồi nay ạ']`
  - `M03` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=khó xoay cổ` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['tôi còn thấy khó xoay cổ nữa']`
  - `M04` [TIỀN SỬ BỆNH] `chu_the=bệnh nhân` | `noi_dung=thiếu máu` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['tôi có thiếu máu']`
  - `M05` [DỊ ỨNG] `chu_the=bệnh nhân` | `noi_dung=dị ứng thuốc` | `moc=None` | `phu_dinh=True` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['trong quá khứ có ghi nhận dị ứng thuốc nào đáng chú ý không', 'uống các loại thuốc tây hay thuốc nam đều bình thường đâu hết á']`
  - `M06` [THUỐC ĐANG DÙNG] `chu_the=bệnh nhân` | `noi_dung=panadol` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['tôi có uống panadol, ngày ba lần, dùng được hai tuần nay ạ']`
  - `M07` [KHÁM LÂM SÀNG] `chu_the=bệnh nhân` | `noi_dung=Co cứng cơ thang hai bên, ấn đau vùng gáy` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Dấu hiệu thực thể gồm: Co cứng cơ thang hai bên, ấn đau vùng gáy']`
  - `M08` [CHẨN ĐOÁN] `chu_the=bệnh nhân` | `noi_dung=Đau vai gáy do tư thế` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=nghi ngờ` | `quan_he=None` | `trich_dan=['Tôi nghĩ nhiều đến đau vai gáy do tư thế']`
  - `M09` [KẾ HOẠCH ĐIỀU TRỊ] `chu_the=bệnh nhân` | `noi_dung=làm xét nghiệm nước tiểu` | `moc=None` | `phu_dinh=False` | `tinh_huong=kế hoạch` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Anh đi làm xét nghiệm nước tiểu rồi quay lại đây']`
- **Các lỗi phát hiện khi đọc ca này (9 lỗi):**
  - **L04** — *Lặp từ thời gian `nay nay` / `rồi nay` / `nay rồi nay`*: `Bệnh nhân: Tôi chịu đựng tình trạng nhức sau gáy cũng nửa năm rồi nay ạ.`
  - **L05** — *Lặp từ nghi vấn `không không` / `chưa không`*: `Bác sĩ: Trong mấy ngày nay, ngoài những điều vừa kể, bạn có thấy phát sinh dấu hiệu nào mới không không ạ?`
  - **L05** — *Bác sĩ gọi người bệnh/người nhà là `bạn` (lệch vai xưng hô)*: `Bác sĩ: Trong mấy ngày nay, ngoài những điều vừa kể, bạn có thấy phát sinh dấu hiệu nào mới không không ạ?`
  - **L06** — *Xung đột đại từ tự xưng trong cùng một câu (`em` vs `tôi`)*: `Bệnh nhân: Dạ em nghe bác sĩ, tôi còn thấy khó xoay cổ nữa.`
  - **L06** — *Từ đệm mở đầu lệch đại từ tự xưng với phần thân câu*: `Bệnh nhân: Dạ em nghe bác sĩ, tôi còn thấy khó xoay cổ nữa.`
  - **L07** — *Bác sĩ gọi người bệnh/người nhà là `bạn` (lệch vai xưng hô)*: `Bác sĩ: Từ trước đến nay, có tiền sử gan, thận, hen suyễn hay tiểu đường gì không hả bạn?`
  - **L08** — *Từ đệm `Dạ thưa đúng ạ` đặt trước câu kể triệu chứng/tiền sử*: `Bệnh nhân: Dạ đúng rồi bác sĩ, tôi có thiếu máu.`
  - **L10** — *Ghép thừa hai từ phủ định `đâu hết á`*: `Bệnh nhân: Dạ không ạ, uống các loại thuốc tây hay thuốc nam đều bình thường đâu hết á.`
  - **L11** — *Bác sĩ gọi người bệnh/người nhà là `bạn` (lệch vai xưng hô)*: `Bác sĩ: Nhân tiện thì, bạn đã tự mua thuốc gì ở tiệm thuốc tây uống chưa vậy?`

### Ca 22 — Mã: `hv_0369` (`bệnh kawasaki`)
- **Thông tin ca:** `la_tre_em=True` | `nguoi_ke=mẹ` | `lo_danh_tinh=False` | `boi_canh=kham_lan_dau` | `bay=['nguoi_ke_benh_minh', 'nguoi_nha_ke_ho']` | `so_luot=17`
- **Lời thoại đầy đủ:**
```text
L01: Bác sĩ: Mời chị ngồi. Con nhà mình bị làm sao?
L02: Bác sĩ: Về giấy tờ khám bệnh, con có mang theo thẻ bảo hiểm y tế hoặc căn cước công dân không?
L03: Người nhà: Vâng ạ, em có mang đầy đủ thẻ căn cước gắn chip và thẻ BHYT đây.
L04: Người nhà: Cháu nó than phiền sốt cao liên tục trên 5 ngày không đáp ứng kháng sinh cũng được mấy hôm nay nay ạ.
L05: Bác sĩ: Ngoài chuyện đó ra, còn điều gì về sức khỏe mấy hôm nay mà mình chưa kể không hả bạn?
L06: Người nhà: Dạ bác sĩ, chưa kể cháu nó còn bị phù cứng mu bàn tay bàn chân bong da đầu ngón tay, phát ban đa dạng dạng sởi hồng ban toàn thân nữa.
L07: Bác sĩ: Quay lại tiền sử trước đây, sức khỏe của mình từ nhỏ đến giờ có vấn đề gì đáng lưu ý không nhỉ?
L08: Người nhà: Dạ thưa đúng ạ, cháu nó có thiếu máu thiếu sắt ạ.
L09: Người nhà: Em cũng đang thiếu máu thiếu sắt, nên em hay lo ạ.
L10: Bác sĩ: Cho tôi hỏi thêm, đã có lần nào dùng thuốc mà bị phù mắt hay nổi ban dị ứng chưa hả bạn?
L11: Người nhà: Dạ bác, có, dị ứng penicillin ạ.
L12: Bác sĩ: Để tôi, để tôi gõ nhẹ vùng lưng xem thận có đau không giúp tôi nhé.
L13: Bác sĩ: Khám lâm sàng: Lưỡi dâu tây điển hình, lòng bàn tay đỏ ửng phù nề, tim đập nhanh. đáng lưu ý.
L14: Bác sĩ: Kết luận bước đầu là: Bệnh Kawasaki thể điển hình ngày thứ sáu. rõ ràng.
L15: Bác sĩ: Trước mắt, tôi sẽ: Truyền tĩnh mạch immunoglobulin ivig liều duy nhất kết hợp aspirin liều chống viêm. Siêu âm tim Doppler tầm soát phình giãn động mạch vành. theo đúng hướng dẫn.
L16: Bác sĩ: Bác sĩ quyết định kê salbutamol hai nhát, xịt khi cần nhé bạn.
L17: Người nhà: Dạ tôi hiểu rồi nè, em rõ hết phác đồ điều trị rồi, xin cảm ơn bác sĩ rất nhiều dữ lắm nghen.
```
- **Đáp án mệnh đề (`dap_an`):**
  - `M01` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=sốt cao liên tục trên 5 ngày không đáp ứng kháng sinh` | `moc=mấy hôm nay` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Cháu nó than phiền sốt cao liên tục trên 5 ngày không đáp ứng kháng sinh cũng được mấy hôm nay nay ạ']`
  - `M02` [LÝ DO KHÁM BỆNH] `chu_the=bệnh nhân` | `noi_dung=sốt cao liên tục trên 5 ngày không đáp ứng kháng sinh` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Cháu nó than phiền sốt cao liên tục trên 5 ngày không đáp ứng kháng sinh cũng được mấy hôm nay nay ạ']`
  - `M03` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=phù cứng mu bàn tay bàn chân bong da đầu ngón tay` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['chưa kể cháu nó còn bị phù cứng mu bàn tay bàn chân bong da đầu ngón tay']`
  - `M04` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=phát ban đa dạng dạng sởi hồng ban toàn thân` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['phát ban đa dạng dạng sởi hồng ban toàn thân nữa']`
  - `M05` [TIỀN SỬ BỆNH] `chu_the=bệnh nhân` | `noi_dung=thiếu máu thiếu sắt` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['cháu nó có thiếu máu thiếu sắt ạ']`
  - `M06` [TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI] `chu_the=người nhà` | `noi_dung=thiếu máu thiếu sắt` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Em cũng đang thiếu máu thiếu sắt']`
  - `M07` [DỊ ỨNG] `chu_the=bệnh nhân` | `noi_dung=dị ứng penicillin` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['dị ứng penicillin ạ']`
  - `M08` [KHÁM LÂM SÀNG] `chu_the=bệnh nhân` | `noi_dung=Lưỡi dâu tây điển hình, lòng bàn tay đỏ ửng phù nề, tim đập nhanh` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Khám lâm sàng: Lưỡi dâu tây điển hình, lòng bàn tay đỏ ửng phù nề, tim đập nhanh']`
  - `M09` [CHẨN ĐOÁN] `chu_the=bệnh nhân` | `noi_dung=Bệnh Kawasaki thể điển hình ngày thứ sáu` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Kết luận bước đầu là: Bệnh Kawasaki thể điển hình ngày thứ sáu']`
  - `M10` [KẾ HOẠCH ĐIỀU TRỊ] `chu_the=bệnh nhân` | `noi_dung=Truyền tĩnh mạch immunoglobulin ivig liều duy nhất kết hợp aspirin liều chống viêm. Siêu âm tim Doppler tầm soát phình giãn động mạch vành` | `moc=None` | `phu_dinh=False` | `tinh_huong=kế hoạch` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['tôi sẽ: Truyền tĩnh mạch immunoglobulin ivig liều duy nhất kết hợp aspirin liều chống viêm. Siêu âm tim Doppler tầm soát phình giãn động mạch vành']`
  - `M11` [KẾ HOẠCH ĐIỀU TRỊ] `chu_the=bệnh nhân` | `noi_dung=kê salbutamol` | `moc=None` | `phu_dinh=False` | `tinh_huong=kế hoạch` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Bác sĩ quyết định kê salbutamol hai nhát, xịt khi cần nhé bạn']`
- **Các lỗi phát hiện khi đọc ca này (11 lỗi):**
  - **L04** — *Lặp từ thời gian `nay nay` / `rồi nay` / `nay rồi nay`*: `Người nhà: Cháu nó than phiền sốt cao liên tục trên 5 ngày không đáp ứng kháng sinh cũng được mấy hôm nay nay ạ.`
  - **L05** — *Bác sĩ gọi người bệnh/người nhà là `bạn` (lệch vai xưng hô)*: `Bác sĩ: Ngoài chuyện đó ra, còn điều gì về sức khỏe mấy hôm nay mà mình chưa kể không hả bạn?`
  - **L08** — *Từ đệm `Dạ thưa đúng ạ` đặt trước câu kể triệu chứng/tiền sử*: `Người nhà: Dạ thưa đúng ạ, cháu nó có thiếu máu thiếu sắt ạ.`
  - **L10** — *Bác sĩ gọi người bệnh/người nhà là `bạn` (lệch vai xưng hô)*: `Bác sĩ: Cho tôi hỏi thêm, đã có lần nào dùng thuốc mà bị phù mắt hay nổi ban dị ứng chưa hả bạn?`
  - **L12** — *Lặp dẫn nhập `Để tôi, để tôi...`*: `Bác sĩ: Để tôi, để tôi gõ nhẹ vùng lưng xem thận có đau không giúp tôi nhé.`
  - **L13** — *Cụm nhận xét thừa sau dấu chấm ở cuối câu*: `Bác sĩ: Khám lâm sàng: Lưỡi dâu tây điển hình, lòng bàn tay đỏ ửng phù nề, tim đập nhanh. đáng lưu ý.`
  - **L14** — *Cụm nhận xét thừa sau dấu chấm ở cuối câu*: `Bác sĩ: Kết luận bước đầu là: Bệnh Kawasaki thể điển hình ngày thứ sáu. rõ ràng.`
  - **L15** — *Cụm nhận xét thừa sau dấu chấm ở cuối câu*: `Bác sĩ: Trước mắt, tôi sẽ: Truyền tĩnh mạch immunoglobulin ivig liều duy nhất kết hợp aspirin liều chống viêm. Siêu âm tim Doppler tầm soát phình giãn động mạch vành. theo đúng hướng dẫn.`
  - **L16** — *Bác sĩ gọi người bệnh/người nhà là `bạn` (lệch vai xưng hô)*: `Bác sĩ: Bác sĩ quyết định kê salbutamol hai nhát, xịt khi cần nhé bạn.`
  - **L17** — *Ghép thừa `rất nhiều dữ lắm`*: `Người nhà: Dạ tôi hiểu rồi nè, em rõ hết phác đồ điều trị rồi, xin cảm ơn bác sĩ rất nhiều dữ lắm nghen.`
  - **L17** — *Xung đột đại từ tự xưng trong cùng một câu (`tôi` vs `em`)*: `Người nhà: Dạ tôi hiểu rồi nè, em rõ hết phác đồ điều trị rồi, xin cảm ơn bác sĩ rất nhiều dữ lắm nghen.`

### Ca 23 — Mã: `hv_0498` (`thiếu vitamin D`)
- **Thông tin ca:** `la_tre_em=True` | `nguoi_ke=mẹ` | `lo_danh_tinh=True` | `boi_canh=tai_kham` | `bay=['bo_sung', 'hoi_khong_dap', 'nguoi_ke_benh_minh', 'nguoi_nha_ke_ho', 'tien_su_gia_dinh']` | `so_luot=21`
- **Lời thoại đầy đủ:**
```text
L01: Bác sĩ: Tình hình uống hapacol từ hôm tái khám trước tới nay thế nào rồi bé?
L02: Người nhà: Dạ, vẫn đang uống hapacol.
L03: Bác sĩ: Chị là gì của bé vậy thế ạ?
L04: Người nhà: Dạ thưa bác sĩ, tôi là mẹ đưa bé đi khám bác sĩ ạ.
L05: Bác sĩ: Sáng sớm hôm nay trời se lạnh, không khí dạo này hanh khô có làm bé bị khô rát họng không thế bé?
L06: Người nhà: Dạ, trời chuyển mùa nên em cũng thấy cơ thể nhạy cảm hơn.
L07: Người nhà: Cháu nhà tôi xuất hiện lâu rồi chưa thấy mọc răng được hai tháng nay rồi ạ.
L08: Bác sĩ: Về cảm giác trong người, cơ thể có phát sinh thêm biểu hiện khó chịu nào nữa không vậy ạ?
L09: Người nhà: Dạ, ngoài ra cháu nhà tôi còn bị trở mình cả đêm không ngủ, biếng ăn nữa.
L10: Người nhà: Biếng ăn thì nặng hơn sau khi ăn ạ.
L11: Bác sĩ: Trong gia đình mình, bên nội hay bên ngoại có ai từng có bệnh lý di truyền đặc biệt không nhé?
L12: Người nhà: Dạ bác sĩ, chị gái bị trĩ.
L13: Người nhà: Tôi thì hở van hai lá, nói thêm để bác sĩ biết.
L14: Bác sĩ: Bác sĩ muốn hỏi một chút, trước đây có dị ứng với kháng sinh hay thuốc giảm đau gì không không?
L15: Người nhà: Dạ chưa có, tôi không dị ứng với kháng sinh, giảm đau hay chất nào đâu mô bác sĩ.
L16: Bác sĩ: Bé ngủ nghỉ thế nào?
L17: Bác sĩ: Được rồi, Bé há to miệng cho tôi soi đèn xem họng một chút nha.
L18: Bác sĩ: Khám lâm sàng bước đầu thấy: Thóp rộng, chưa biến dạng xương. nha.
L19: Bác sĩ: Bác sĩ hướng tới chẩn đoán: Thiếu vitamin D.
L20: Bác sĩ: Trước mắt phác đồ là: Bổ sung vitamin D theo liều. Cho tắm nắng buổi sáng. theo đúng hướng dẫn.
L21: Người nhà: Dạ vâng, tôi đã lưu số điện thoại phòng khám để liên hệ, cảm ơn bác sĩ dữ lắm ạ, chào bác sĩ.
```
- **Đáp án mệnh đề (`dap_an`):**
  - `M01` [THUỐC ĐANG DÙNG] `chu_the=bệnh nhân` | `noi_dung=đang dùng hapacol` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['vẫn đang uống hapacol']`
  - `M02` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=chậm mọc răng` | `moc=hai tháng nay` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Cháu nhà tôi xuất hiện lâu rồi chưa thấy mọc răng được hai tháng nay rồi ạ']`
  - `M03` [LÝ DO KHÁM BỆNH] `chu_the=bệnh nhân` | `noi_dung=chậm mọc răng` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Cháu nhà tôi xuất hiện lâu rồi chưa thấy mọc răng được hai tháng nay rồi ạ']`
  - `M04` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=khó ngủ` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['ngoài ra cháu nhà tôi còn bị trở mình cả đêm không ngủ']`
  - `M05` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=biếng ăn` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['biếng ăn nữa', 'Biếng ăn thì nặng hơn sau khi ăn ạ']`
  - `M06` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=biếng ăn nặng hơn sau khi ăn` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=bổ sung` | `trich_dan=['Biếng ăn thì nặng hơn sau khi ăn ạ']`
  - `M07` [TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI] `chu_the=chị gái` | `noi_dung=trĩ` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['chị gái bị trĩ']`
  - `M08` [TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI] `chu_the=mẹ` | `noi_dung=hở van hai lá` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Tôi thì hở van hai lá']`
  - `M09` [DỊ ỨNG] `chu_the=bệnh nhân` | `noi_dung=dị ứng thuốc` | `moc=None` | `phu_dinh=True` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['trước đây có dị ứng với kháng sinh hay thuốc giảm đau gì không không', 'tôi không dị ứng với kháng sinh']`
  - `M10` [KHÁM LÂM SÀNG] `chu_the=bệnh nhân` | `noi_dung=Thóp rộng, chưa biến dạng xương` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Khám lâm sàng bước đầu thấy: Thóp rộng, chưa biến dạng xương']`
  - `M11` [CHẨN ĐOÁN] `chu_the=bệnh nhân` | `noi_dung=Thiếu vitamin D` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Bác sĩ hướng tới chẩn đoán: Thiếu vitamin D']`
  - `M12` [KẾ HOẠCH ĐIỀU TRỊ] `chu_the=bệnh nhân` | `noi_dung=Bổ sung vitamin D theo liều. Cho tắm nắng buổi sáng` | `moc=None` | `phu_dinh=False` | `tinh_huong=kế hoạch` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Trước mắt phác đồ là: Bổ sung vitamin D theo liều. Cho tắm nắng buổi sáng']`
- **Các lỗi phát hiện khi đọc ca này (9 lỗi):**
  - **L03** — *Lặp từ nghi vấn `vậy vậy` / `vậy thế`*: `Bác sĩ: Chị là gì của bé vậy thế ạ?`
  - **L05-L06** — *Hỏi đáp xã giao lệch cặp (hỏi một đằng, đáp một nẻo)*: `Bác sĩ: Sáng sớm hôm nay trời se lạnh, không khí dạo này hanh khô có làm bé bị khô rát họng không thế bé? / Người nhà: Dạ, trời chuyển mùa nên em cũng thấy cơ thể nhạy cảm hơn.`
  - **L07** — *Lặp từ thời gian `nay nay` / `rồi nay` / `nay rồi nay`*: `Người nhà: Cháu nhà tôi xuất hiện lâu rồi chưa thấy mọc răng được hai tháng nay rồi ạ.`
  - **L11** — *Tiểu từ đề nghị (`nhé/nha/nghen`) gắn vào câu hỏi `?`*: `Bác sĩ: Trong gia đình mình, bên nội hay bên ngoại có ai từng có bệnh lý di truyền đặc biệt không nhé?`
  - **L14** — *Lặp từ nghi vấn `không không` / `chưa không`*: `Bác sĩ: Bác sĩ muốn hỏi một chút, trước đây có dị ứng với kháng sinh hay thuốc giảm đau gì không không?`
  - **L15** — *Người nhà trả lời phủ định nhưng tự xưng `tôi` thay vì nói về bệnh nhân*: `Người nhà: Dạ chưa có, tôi không dị ứng với kháng sinh, giảm đau hay chất nào đâu mô bác sĩ.`
  - **L18** — *Hạt đề nghị thừa sau dấu chấm (`. nhé.`, `. nha.`, `. nghen.`)*: `Bác sĩ: Khám lâm sàng bước đầu thấy: Thóp rộng, chưa biến dạng xương. nha.`
  - **L20** — *Cụm nhận xét thừa sau dấu chấm ở cuối câu*: `Bác sĩ: Trước mắt phác đồ là: Bổ sung vitamin D theo liều. Cho tắm nắng buổi sáng. theo đúng hướng dẫn.`
  - **L21** — *Trộn phương ngữ và tiểu từ `dữ lắm ạ`*: `Người nhà: Dạ vâng, tôi đã lưu số điện thoại phòng khám để liên hệ, cảm ơn bác sĩ dữ lắm ạ, chào bác sĩ.`

### Ca 24 — Mã: `hv_2230` (`viêm cột sống dính khớp`)
- **Thông tin ca:** `la_tre_em=False` | `nguoi_ke=chồng` | `lo_danh_tinh=False` | `boi_canh=kham_lan_dau` | `bay=['dai_tu_ho_hang', 'nguoi_ke_benh_minh', 'nguoi_nha_ke_ho', 'nguon_khac_nhau']` | `so_luot=15`
- **Lời thoại đầy đủ:**
```text
L01: Bác sĩ: Mời ông ngồi xuống, ông thấy bà có triệu chứng gì nặng nhất ạ?
L02: Người nhà: Dạ thưa bác, bà nhà tôi bị đau thắt lưng và vùng mông kiểu viêm kéo dài trên 3 tháng liên tục khoảng một tháng nay rồi.
L03: Bệnh nhân: Theo tôi thì hơn một năm mới đúng.
L04: Bác sĩ: Để tôi ghi là chưa rõ khoảng một tháng hay hơn một năm, mình xác nhận lại sau nhé ạ.
L05: Bác sĩ: Trong mấy ngày nay, có triệu chứng nào khác đi kèm mà mình nhận thấy không không?
L06: Người nhà: Dạ thưa bác, chưa kể bà nhà tôi còn bị viêm màng bồ đào mắt, đau sưng khớp háng hoặc khớp gối nữa.
L07: Bác sĩ: Quay lại tiền sử trước đây, bạn có tiền sử bệnh tim mạch, huyết áp hay dạ dày gì không ạ?
L08: Người nhà: Dạ bác sĩ, bà nhà tôi có viêm gan B.
L09: Người nhà: Tôi bị trứng cá nặng mấy năm nay rồi ạ.
L10: Bác sĩ: Bây giờ bác sĩ sẽ, bà nằm lên bàn khám giúp tôi giúp tôi nhé.
L11: Bác sĩ: Khám lâm sàng bước đầu thấy: Độ giãn cột sống thắt lưng giảm rõ (nghiệm pháp Schober dưới 10/13 cm), ấn khớp cùng chậu hai bên đau buốt. cần theo dõi.
L12: Bác sĩ: Căn cứ thăm khám, tôi chẩn đoán: Viêm cột sống dính khớp thể trục (Ankylosing spondylitis). nghen.
L13: Bác sĩ: Các biện pháp điều trị gồm: Chụp X-quang hoặc MRI khớp cùng chậu hai bên, xét nghiệm kháng nguyên HLA-B27 và CRP. Dùng NSAIDs liều đầy đủ, xem xét thuốc sinh học kháng TNF-alpha. theo đúng hướng dẫn.
L14: Bác sĩ: Bác sĩ sẽ kê paracetamol 500 mg, uống khi cần nghen.
L15: Người nhà: Dạ vâng, chúc bác sĩ thật nhiều sức khỏe, tôi ghi nhớ kỹ các dặn dò này rồi nhe bác sĩ.
```
- **Đáp án mệnh đề (`dap_an`):**
  - `M01` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=đau thắt lưng và vùng mông kiểu viêm kéo dài trên 3 tháng` | `moc=khoảng một tháng` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['bà nhà tôi bị đau thắt lưng và vùng mông kiểu viêm kéo dài trên 3 tháng liên tục khoảng một tháng nay rồi']`
  - `M02` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=đau thắt lưng và vùng mông kiểu viêm kéo dài trên 3 tháng` | `moc=hơn một năm` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=mâu thuẫn` | `trich_dan=['Theo tôi thì hơn một năm mới đúng']`
  - `M03` [LÝ DO KHÁM BỆNH] `chu_the=bệnh nhân` | `noi_dung=đau thắt lưng và vùng mông kiểu viêm kéo dài trên 3 tháng` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['bà nhà tôi bị đau thắt lưng và vùng mông kiểu viêm kéo dài trên 3 tháng liên tục khoảng một tháng nay rồi']`
  - `M04` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=viêm màng bồ đào mắt` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['chưa kể bà nhà tôi còn bị viêm màng bồ đào mắt']`
  - `M05` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=đau sưng khớp háng hoặc khớp gối` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['đau sưng khớp háng hoặc khớp gối nữa']`
  - `M06` [TIỀN SỬ BỆNH] `chu_the=bệnh nhân` | `noi_dung=viêm gan B` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['bà nhà tôi có viêm gan B']`
  - `M07` [TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI] `chu_the=người nhà` | `noi_dung=trứng cá nặng` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Tôi bị trứng cá nặng mấy năm nay rồi ạ']`
  - `M08` [KHÁM LÂM SÀNG] `chu_the=bệnh nhân` | `noi_dung=Độ giãn cột sống thắt lưng giảm rõ (nghiệm pháp Schober dưới 10/13 cm), ấn khớp cùng chậu hai bên đau buốt` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Khám lâm sàng bước đầu thấy: Độ giãn cột sống thắt lưng giảm rõ (nghiệm pháp Schober dưới 10/13 cm), ấn khớp cùng chậu hai bên đau buốt']`
  - `M09` [CHẨN ĐOÁN] `chu_the=bệnh nhân` | `noi_dung=Viêm cột sống dính khớp thể trục (Ankylosing spondylitis)` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['tôi chẩn đoán: Viêm cột sống dính khớp thể trục (Ankylosing spondylitis)']`
  - `M10` [KẾ HOẠCH ĐIỀU TRỊ] `chu_the=bệnh nhân` | `noi_dung=Chụp X-quang hoặc MRI khớp cùng chậu hai bên, xét nghiệm kháng nguyên HLA-B27 và CRP. Dùng NSAIDs liều đầy đủ, xem xét thuốc sinh học kháng TNF-alpha` | `moc=None` | `phu_dinh=False` | `tinh_huong=kế hoạch` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Các biện pháp điều trị gồm: Chụp X-quang hoặc MRI khớp cùng chậu hai bên, xét nghiệm kháng nguyên HLA-B27 và CRP. Dùng NSAIDs liều đầy đủ, xem xét thuốc sinh học kháng TNF-alpha']`
  - `M11` [KẾ HOẠCH ĐIỀU TRỊ] `chu_the=bệnh nhân` | `noi_dung=kê paracetamol` | `moc=None` | `phu_dinh=False` | `tinh_huong=kế hoạch` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Bác sĩ sẽ kê paracetamol 500 mg, uống khi cần nghen']`
- **Các lỗi phát hiện khi đọc ca này (8 lỗi):**
  - **L02** — *Lặp từ thời gian `nay nay` / `rồi nay` / `nay rồi nay`*: `Người nhà: Dạ thưa bác, bà nhà tôi bị đau thắt lưng và vùng mông kiểu viêm kéo dài trên 3 tháng liên tục khoảng một tháng nay rồi.`
  - **L05** — *Lặp từ nghi vấn `không không` / `chưa không`*: `Bác sĩ: Trong mấy ngày nay, có triệu chứng nào khác đi kèm mà mình nhận thấy không không?`
  - **L07** — *Bác sĩ gọi người bệnh/người nhà là `bạn` (lệch vai xưng hô)*: `Bác sĩ: Quay lại tiền sử trước đây, bạn có tiền sử bệnh tim mạch, huyết áp hay dạ dày gì không ạ?`
  - **L09** — *Lặp từ thời gian `nay nay` / `rồi nay` / `nay rồi nay`*: `Người nhà: Tôi bị trứng cá nặng mấy năm nay rồi ạ.`
  - **L10** — *Lặp cụm `giúp tôi giúp tôi`*: `Bác sĩ: Bây giờ bác sĩ sẽ, bà nằm lên bàn khám giúp tôi giúp tôi nhé.`
  - **L11** — *Cụm nhận xét thừa sau dấu chấm ở cuối câu*: `Bác sĩ: Khám lâm sàng bước đầu thấy: Độ giãn cột sống thắt lưng giảm rõ (nghiệm pháp Schober dưới 10/13 cm), ấn khớp cùng chậu hai bên đau buốt. cần theo dõi.`
  - **L12** — *Hạt đề nghị thừa sau dấu chấm (`. nhé.`, `. nha.`, `. nghen.`)*: `Bác sĩ: Căn cứ thăm khám, tôi chẩn đoán: Viêm cột sống dính khớp thể trục (Ankylosing spondylitis). nghen.`
  - **L13** — *Cụm nhận xét thừa sau dấu chấm ở cuối câu*: `Bác sĩ: Các biện pháp điều trị gồm: Chụp X-quang hoặc MRI khớp cùng chậu hai bên, xét nghiệm kháng nguyên HLA-B27 và CRP. Dùng NSAIDs liều đầy đủ, xem xét thuốc sinh học kháng TNF-alpha. theo đúng hướng dẫn.`

### Ca 25 — Mã: `hv_0414` (`viêm da cơ địa`)
- **Thông tin ca:** `la_tre_em=False` | `nguoi_ke=chồng` | `lo_danh_tinh=True` | `boi_canh=dieu_duong_ban_giao` | `bay=['di_ung_nguoi_nha', 'nguoi_nha_ke_ho', 'nguon_khac_nhau']` | `so_luot=21`
- **Lời thoại đầy đủ:**
```text
L01: Điều dưỡng: Em chào bác sĩ. Chị này đã làm thủ tục tiếp đón, sinh hiệu ban đầu đo được ổn định ạ.
L02: Bác sĩ: Cảm ơn em điều dưỡng nhiều. Chị kể từ đầu xem tình trạng dạo này thế nào nhé ạ.
L03: Bác sĩ: Bác sĩ muốn xác nhận, mình có quan hệ gia đình thế nào với chị ấy ạ?
L04: Người nhà: Dạ thưa bác sĩ, chị ấy là người thân của em, em là chồng đây ạ.
L05: Bác sĩ: Lúc gửi xe máy, chị có dễ dàng tìm thấy chỗ đỗ xe không hả chị?
L06: Người nhà: Dạ, biển chỉ dẫn to rõ ngoài cổng nên em tìm thấy ngay.
L07: Người nhà: Vợ em bị dày da lichen hóa hằn cổ trâu ở các nếp gấp khuỷu tay khoeo chân liên tục nửa năm rồi nay rồi ạ.
L08: Bệnh nhân: Theo em thì hơn một năm mới đúng.
L09: Bác sĩ: Để tôi ghi là chưa rõ nửa năm rồi hay hơn một năm, mình xác nhận lại sau nhé.
L10: Bác sĩ: Thêm vào đó, bạn có thấy kèm theo biểu hiện bất thường nào khác không nhé?
L11: Người nhà: Dạ thưa bác, ngoài ra vợ em còn bị dấu vẽ nổi da da gà dày sừng nang lông nữa ạ.
L12: Bác sĩ: Thế còn về tiền sử dị ứng, mình có cơ địa dị ứng thuốc, thức ăn hay thời tiết không ạ?
L13: Người nhà: Dạ thưa bác, em thì dị ứng cao su, còn vợ em chưa thấy bị bao giờ ạ.
L14: Bác sĩ: À, cho tôi hỏi thêm, mấy hôm nay đã tự điều trị bằng thuốc gì ở nhà chưa nhỉ?
L15: Người nhà: Dạ bác sĩ, vợ em có uống amlodipin, ngày một lần buổi sáng ạ.
L16: Bác sĩ: Bác sĩ hiểu rồi, tôi ấn nhẹ vào vùng này xem có đau tức không giúp bác sĩ nhé.
L17: Điều dưỡng: Sinh hiệu em đo được: Khám kỹ các cơ quan cho thấy: Da vùng khoeo chân và khuỷu tay đỏ, có vảy khô. nhé.
L18: Bác sĩ: Qua triệu chứng và khám, tôi kết luận: Viêm da cơ địa. rõ ràng.
L19: Bác sĩ: Phác đồ điều trị đợt này là: Dưỡng ẩm ngày hai lần, tránh tắm nước quá nóng và xà phòng mạnh. nghen.
L20: Bác sĩ: Bác sĩ dặn là ngưng uống amlodipin từ bữa nay uống đúng giờ nhé.
L21: Người nhà: Dạ tôi hiểu rồi nè, em sẽ chú ý nghỉ ngơi và ăn uống cẩn thận, xin cảm ơn bác sĩ rất nhiều nghen, cảm ơn bác sĩ nhiều.
```
- **Đáp án mệnh đề (`dap_an`):**
  - `M01` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=dày da lichen hóa hằn cổ trâu ở các nếp gấp khuỷu tay khoeo chân` | `moc=nửa năm rồi` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Vợ em bị dày da lichen hóa hằn cổ trâu ở các nếp gấp khuỷu tay khoeo chân liên tục nửa năm rồi nay rồi ạ']`
  - `M02` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=dày da lichen hóa hằn cổ trâu ở các nếp gấp khuỷu tay khoeo chân` | `moc=hơn một năm` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=mâu thuẫn` | `trich_dan=['Theo em thì hơn một năm mới đúng']`
  - `M03` [LÝ DO KHÁM BỆNH] `chu_the=bệnh nhân` | `noi_dung=dày da lichen hóa hằn cổ trâu ở các nếp gấp khuỷu tay khoeo chân` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Vợ em bị dày da lichen hóa hằn cổ trâu ở các nếp gấp khuỷu tay khoeo chân liên tục nửa năm rồi nay rồi ạ']`
  - `M04` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=dấu vẽ nổi da da gà dày sừng nang lông` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['ngoài ra vợ em còn bị dấu vẽ nổi da da gà dày sừng nang lông nữa ạ']`
  - `M05` [TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI] `chu_the=chồng` | `noi_dung=dị ứng cao su` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['em thì dị ứng cao su']`
  - `M06` [DỊ ỨNG] `chu_the=bệnh nhân` | `noi_dung=dị ứng thuốc` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chưa ghi nhận` | `quan_he=None` | `trich_dan=['còn vợ em chưa thấy bị bao giờ ạ']`
  - `M07` [THUỐC ĐANG DÙNG] `chu_the=bệnh nhân` | `noi_dung=amlodipin` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['vợ em có uống amlodipin, ngày một lần buổi sáng ạ']`
  - `M08` [KHÁM LÂM SÀNG] `chu_the=bệnh nhân` | `noi_dung=Da vùng khoeo chân và khuỷu tay đỏ, có vảy khô` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Sinh hiệu em đo được: Khám kỹ các cơ quan cho thấy: Da vùng khoeo chân và khuỷu tay đỏ, có vảy khô']`
  - `M09` [CHẨN ĐOÁN] `chu_the=bệnh nhân` | `noi_dung=Viêm da cơ địa` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['tôi kết luận: Viêm da cơ địa']`
  - `M10` [KẾ HOẠCH ĐIỀU TRỊ] `chu_the=bệnh nhân` | `noi_dung=Dưỡng ẩm ngày hai lần, tránh tắm nước quá nóng và xà phòng mạnh` | `moc=None` | `phu_dinh=False` | `tinh_huong=kế hoạch` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Phác đồ điều trị đợt này là: Dưỡng ẩm ngày hai lần, tránh tắm nước quá nóng và xà phòng mạnh']`
  - `M11` [KẾ HOẠCH ĐIỀU TRỊ] `chu_the=bệnh nhân` | `noi_dung=ngừng amlodipin` | `moc=None` | `phu_dinh=False` | `tinh_huong=kế hoạch` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Bác sĩ dặn là ngưng uống amlodipin từ bữa nay uống đúng giờ nhé']`
- **Các lỗi phát hiện khi đọc ca này (10 lỗi):**
  - **L05-L06** — *Hỏi đáp xã giao lệch cặp (hỏi một đằng, đáp một nẻo)*: `Bác sĩ: Lúc gửi xe máy, chị có dễ dàng tìm thấy chỗ đỗ xe không hả chị? / Người nhà: Dạ, biển chỉ dẫn to rõ ngoài cổng nên em tìm thấy ngay.`
  - **L07** — *Lặp từ thời gian `nay nay` / `rồi nay` / `nay rồi nay`*: `Người nhà: Vợ em bị dày da lichen hóa hằn cổ trâu ở các nếp gấp khuỷu tay khoeo chân liên tục nửa năm rồi nay rồi ạ.`
  - **L10** — *Tiểu từ đề nghị (`nhé/nha/nghen`) gắn vào câu hỏi `?`*: `Bác sĩ: Thêm vào đó, bạn có thấy kèm theo biểu hiện bất thường nào khác không nhé?`
  - **L10** — *Bác sĩ gọi người bệnh/người nhà là `bạn` (lệch vai xưng hô)*: `Bác sĩ: Thêm vào đó, bạn có thấy kèm theo biểu hiện bất thường nào khác không nhé?`
  - **L17** — *Hạt đề nghị thừa sau dấu chấm (`. nhé.`, `. nha.`, `. nghen.`)*: `Điều dưỡng: Sinh hiệu em đo được: Khám kỹ các cơ quan cho thấy: Da vùng khoeo chân và khuỷu tay đỏ, có vảy khô. nhé.`
  - **L17** — *Điều dưỡng lặp hai lần dẫn nhập `Sinh hiệu em đo được: Bác sĩ/Tôi...`*: `Điều dưỡng: Sinh hiệu em đo được: Khám kỹ các cơ quan cho thấy: Da vùng khoeo chân và khuỷu tay đỏ, có vảy khô. nhé.`
  - **L18** — *Cụm nhận xét thừa sau dấu chấm ở cuối câu*: `Bác sĩ: Qua triệu chứng và khám, tôi kết luận: Viêm da cơ địa. rõ ràng.`
  - **L19** — *Hạt đề nghị thừa sau dấu chấm (`. nhé.`, `. nha.`, `. nghen.`)*: `Bác sĩ: Phác đồ điều trị đợt này là: Dưỡng ẩm ngày hai lần, tránh tắm nước quá nóng và xà phòng mạnh. nghen.`
  - **L20** — *Mâu thuẫn y lệnh `ngưng uống ... uống đúng giờ`*: `Bác sĩ: Bác sĩ dặn là ngưng uống amlodipin từ bữa nay uống đúng giờ nhé.`
  - **L21** — *Xung đột đại từ tự xưng trong cùng một câu (`tôi` vs `em`)*: `Người nhà: Dạ tôi hiểu rồi nè, em sẽ chú ý nghỉ ngơi và ăn uống cẩn thận, xin cảm ơn bác sĩ rất nhiều nghen, cảm ơn bác sĩ nhiều.`

### Ca 26 — Mã: `hv_3860` (`sởi ở trẻ em`)
- **Thông tin ca:** `la_tre_em=True` | `nguoi_ke=mẹ` | `lo_danh_tinh=False` | `boi_canh=dieu_duong_ban_giao` | `bay=['nguoi_nha_ke_ho']` | `so_luot=16`
- **Lời thoại đầy đủ:**
```text
L01: Điều dưỡng: Em chào bác sĩ. Cháu này đã bấm số thứ tự, em đo nhịp tim và SpO2 xong rồi bác sĩ ạ.
L02: Bác sĩ: Cảm ơn em. Cháu kể tôi nghe xem thế nào.
L03: Bác sĩ: Bác sĩ thấy ngoài đường khá đông, thời gian di chuyển từ nhà tới phòng khám có lâu không cháu thế cháu?
L04: Người nhà: Dạ tôi, đường xá sáng nay khá thông thoáng nên đi nhanh lắm nè bác sĩ.
L05: Người nhà: Bé nhà em cảm giác sốt cao liên tục 39-40 độ xuất hiện liên miên hai hôm nay ạ.
L06: Bác sĩ: Ngoài chuyện đó ra, bạn có thấy sụt cân, chán ăn hay mất ngủ kèm theo không không?
L07: Người nhà: Vâng em nghe, bé nhà em thấy người còn có tiêu chảy, hạt trắng nhỏ Koplik trong niêm mạc má nữa.
L08: Bác sĩ: Về tiền sử bệnh tật từ trước tới nay, bạn có tiền sử bệnh tim mạch, huyết áp hay dạ dày gì không hả bạn?
L09: Người nhà: Dạ tôi không, từ trước tới nay đi khám định kỳ đều bình thường bao giờ bác sĩ ạ.
L10: Bác sĩ: Trước giờ, từ trước tới nay dùng thuốc có bị ngứa ngáy hay nổi mẩn đỏ không hả bạn?
L11: Người nhà: Vâng không ạ, từ trước tới nay tôi uống thuốc gì cũng an toàn hết.
L12: Bác sĩ: Trước khi kết luận, để tôi khám cho cháu một chút nha.
L13: Điều dưỡng: Sinh hiệu em đo được: Kết quả thăm khám cho thấy: Ban đỏ dạng sởi nổi gồ mịn mọc dày ở mặt và ngực, kết mạc mắt đỏ nhiều gỉ mắt, khám miệng thấy nốt Koplik đối diện răng hàm. đáng lưu ý.
L14: Bác sĩ: Tình trạng bệnh hiện tại là: Bệnh sởi giai đoạn phát ban ngày thứ hai. đừng quá lo lắng nhé.
L15: Bác sĩ: Phương hướng điều trị cụ thể: Cách ly trẻ tại phòng riêng thoáng khí. Bổ sung Vitamin A liều cao theo tuổi phòng biến chứng giác mạc, hạ sốt, rửa mắt mũi bằng nước muối sinh lý.
L16: Người nhà: Dạ vâng, xin chúc bác sĩ nhiều niềm vui trong công việc, em đã hiểu rõ liều lượng và cách dùng thuốc nhé bác sĩ.
```
- **Đáp án mệnh đề (`dap_an`):**
  - `M01` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=sốt cao liên tục 39-40 độ` | `moc=hai hôm` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Bé nhà em cảm giác sốt cao liên tục 39-40 độ xuất hiện liên miên hai hôm nay ạ']`
  - `M02` [LÝ DO KHÁM BỆNH] `chu_the=bệnh nhân` | `noi_dung=sốt cao liên tục 39-40 độ` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Bé nhà em cảm giác sốt cao liên tục 39-40 độ xuất hiện liên miên hai hôm nay ạ']`
  - `M03` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=tiêu chảy` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['bé nhà em thấy người còn có tiêu chảy']`
  - `M04` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=hạt trắng nhỏ Koplik trong niêm mạc má` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['hạt trắng nhỏ Koplik trong niêm mạc má nữa']`
  - `M05` [DỊ ỨNG] `chu_the=bệnh nhân` | `noi_dung=dị ứng thuốc` | `moc=None` | `phu_dinh=True` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['từ trước tới nay dùng thuốc có bị ngứa ngáy hay nổi mẩn đỏ không hả bạn', 'từ trước tới nay tôi uống thuốc gì cũng an toàn hết']`
  - `M06` [KHÁM LÂM SÀNG] `chu_the=bệnh nhân` | `noi_dung=Ban đỏ dạng sởi nổi gồ mịn mọc dày ở mặt và ngực, kết mạc mắt đỏ nhiều gỉ mắt, khám miệng thấy nốt Koplik đối diện răng hàm` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Sinh hiệu em đo được: Kết quả thăm khám cho thấy: Ban đỏ dạng sởi nổi gồ mịn mọc dày ở mặt và ngực, kết mạc mắt đỏ nhiều gỉ mắt, khám miệng thấy nốt Koplik đối diện răng hàm']`
  - `M07` [CHẨN ĐOÁN] `chu_the=bệnh nhân` | `noi_dung=Bệnh sởi giai đoạn phát ban ngày thứ hai` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Tình trạng bệnh hiện tại là: Bệnh sởi giai đoạn phát ban ngày thứ hai']`
  - `M08` [KẾ HOẠCH ĐIỀU TRỊ] `chu_the=bệnh nhân` | `noi_dung=Cách ly trẻ tại phòng riêng thoáng khí. Bổ sung Vitamin A liều cao theo tuổi phòng biến chứng giác mạc, hạ sốt, rửa mắt mũi bằng nước muối sinh lý` | `moc=None` | `phu_dinh=False` | `tinh_huong=kế hoạch` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Phương hướng điều trị cụ thể: Cách ly trẻ tại phòng riêng thoáng khí. Bổ sung Vitamin A liều cao theo tuổi phòng biến chứng giác mạc, hạ sốt, rửa mắt mũi bằng nước muối sinh lý']`
- **Các lỗi phát hiện khi đọc ca này (11 lỗi):**
  - **L04** — *Từ đệm cụt `Dạ em,` / `Dạ tôi,`*: `Người nhà: Dạ tôi, đường xá sáng nay khá thông thoáng nên đi nhanh lắm nè bác sĩ.`
  - **L06** — *Lặp từ nghi vấn `không không` / `chưa không`*: `Bác sĩ: Ngoài chuyện đó ra, bạn có thấy sụt cân, chán ăn hay mất ngủ kèm theo không không?`
  - **L06** — *Bác sĩ gọi người bệnh/người nhà là `bạn` (lệch vai xưng hô)*: `Bác sĩ: Ngoài chuyện đó ra, bạn có thấy sụt cân, chán ăn hay mất ngủ kèm theo không không?`
  - **L07** — *Từ đệm mở đầu lệch đại từ tự xưng với phần thân câu*: `Người nhà: Vâng em nghe, bé nhà em thấy người còn có tiêu chảy, hạt trắng nhỏ Koplik trong niêm mạc má nữa.`
  - **L08** — *Bác sĩ gọi người bệnh/người nhà là `bạn` (lệch vai xưng hô)*: `Bác sĩ: Về tiền sử bệnh tật từ trước tới nay, bạn có tiền sử bệnh tim mạch, huyết áp hay dạ dày gì không hả bạn?`
  - **L09** — *Lặp/xung đột trạng ngữ `từ trước tới nay ... bao giờ`*: `Người nhà: Dạ tôi không, từ trước tới nay đi khám định kỳ đều bình thường bao giờ bác sĩ ạ.`
  - **L10** — *Bác sĩ gọi người bệnh/người nhà là `bạn` (lệch vai xưng hô)*: `Bác sĩ: Trước giờ, từ trước tới nay dùng thuốc có bị ngứa ngáy hay nổi mẩn đỏ không hả bạn?`
  - **L11** — *Người nhà trả lời phủ định nhưng tự xưng `tôi` thay vì nói về bệnh nhân*: `Người nhà: Vâng không ạ, từ trước tới nay tôi uống thuốc gì cũng an toàn hết.`
  - **L13** — *Cụm nhận xét thừa sau dấu chấm ở cuối câu*: `Điều dưỡng: Sinh hiệu em đo được: Kết quả thăm khám cho thấy: Ban đỏ dạng sởi nổi gồ mịn mọc dày ở mặt và ngực, kết mạc mắt đỏ nhiều gỉ mắt, khám miệng thấy nốt Koplik đối diện răng hàm. đáng lưu ý.`
  - **L13** — *Điều dưỡng lặp hai lần dẫn nhập `Sinh hiệu em đo được: Bác sĩ/Tôi...`*: `Điều dưỡng: Sinh hiệu em đo được: Kết quả thăm khám cho thấy: Ban đỏ dạng sởi nổi gồ mịn mọc dày ở mặt và ngực, kết mạc mắt đỏ nhiều gỉ mắt, khám miệng thấy nốt Koplik đối diện răng hàm. đáng lưu ý.`
  - **L14** — *Cụm nhận xét thừa sau dấu chấm ở cuối câu*: `Bác sĩ: Tình trạng bệnh hiện tại là: Bệnh sởi giai đoạn phát ban ngày thứ hai. đừng quá lo lắng nhé.`

### Ca 27 — Mã: `hv_4631` (`cơn đau thắt ngực không ổn định`)
- **Thông tin ca:** `la_tre_em=False` | `nguoi_ke=mẹ` | `lo_danh_tinh=True` | `boi_canh=kham_lan_dau` | `bay=['nguoi_ke_benh_minh', 'nguoi_nha_ke_ho']` | `so_luot=14`
- **Lời thoại đầy đủ:**
```text
L01: Bác sĩ: Chào bác, lý do chính mà gia đình đưa chị đi khám hôm nay là gì ạ?
L02: Bác sĩ: Bác sĩ muốn xác nhận, bác là người nhà gì của chị ấy ạ?
L03: Người nhà: Vâng ạ, chị ấy là người thân của tôi, tôi là mẹ bác sĩ ạ.
L04: Bác sĩ: Bác sĩ mời {goi}, chị đã kịp ăn lót dạ món gì nhẹ nhàng chưa nhé?
L05: Người nhà: Dạ thưa bác sĩ, em cảm ơn bác sĩ đã chu đáo quan tâm ạ.
L06: Người nhà: Tình trạng cơn đau thắt ngực xuất hiện ngay cả khi đang nghỉ ngơi tĩnh của con tôi kéo dài hơn một tuần rồi ạ.
L07: Bác sĩ: Cho tôi hỏi thêm là, mình còn cảm thấy khó chịu ở chỗ nào khác nữa không?
L08: Người nhà: Dạ, cùng lúc đó con tôi cũng xuất hiện ngậm nitroglycerin dưới lưỡi hai ba lần vẫn không cắt được cơn đau, chỉ định chụp mạch vành cấp cứu can thiệp đặt stent.
L09: Người nhà: Tôi cũng đang viêm họng mạn, nên tôi hay lo ạ.
L10: Bác sĩ: Bước tiếp theo, để tôi kiểm tra vùng bụng một chút nha chị.
L11: Bác sĩ: Khám thực thể phát hiện: Bệnh nhân vẻ mặt hốt hoảng, vã mồ hôi lạnh, huyết áp 150/90 mmHg, nhịp tim 95 lần/phút. rõ ràng.
L12: Bác sĩ: Bác sĩ nghĩ nhiều đến: Hội chứng vành cấp: cơn đau thắt ngực không ổn định. đừng quá lo lắng nhé.
L13: Bác sĩ: Bác sĩ đề ra phác đồ: Đo điện tâm đồ ngay lập tức, xét nghiệm troponin hàng loạt. Ngậm dưới lưỡi nitroglycerin, chống đông heparin và chuyển viện cấp cứu can thiệp mạch vành. theo đúng hướng dẫn.
L14: Người nhà: Dạ vâng ạ, tôi xin ghi nhận lời dặn dò của bác sĩ, xin chúc bác sĩ nhiều niềm vui trong công việc ạ, xin phép bác sĩ tôi ra lấy thuốc.
```
- **Đáp án mệnh đề (`dap_an`):**
  - `M01` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=cơn đau thắt ngực xuất hiện ngay cả khi đang nghỉ ngơi tĩnh` | `moc=hơn một tuần` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Tình trạng cơn đau thắt ngực xuất hiện ngay cả khi đang nghỉ ngơi tĩnh của con tôi kéo dài hơn một tuần rồi ạ']`
  - `M02` [LÝ DO KHÁM BỆNH] `chu_the=bệnh nhân` | `noi_dung=cơn đau thắt ngực xuất hiện ngay cả khi đang nghỉ ngơi tĩnh` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Tình trạng cơn đau thắt ngực xuất hiện ngay cả khi đang nghỉ ngơi tĩnh của con tôi kéo dài hơn một tuần rồi ạ']`
  - `M03` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=ngậm nitroglycerin dưới lưỡi hai ba lần vẫn không cắt được cơn đau` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['cùng lúc đó con tôi cũng xuất hiện ngậm nitroglycerin dưới lưỡi hai ba lần vẫn không cắt được cơn đau']`
  - `M04` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=chỉ định chụp mạch vành cấp cứu can thiệp đặt stent` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['chỉ định chụp mạch vành cấp cứu can thiệp đặt stent']`
  - `M05` [TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI] `chu_the=mẹ` | `noi_dung=viêm họng mạn` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Tôi cũng đang viêm họng mạn']`
  - `M06` [KHÁM LÂM SÀNG] `chu_the=bệnh nhân` | `noi_dung=Bệnh nhân vẻ mặt hốt hoảng, vã mồ hôi lạnh, huyết áp 150/90 mmHg, nhịp tim 95 lần/phút` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Khám thực thể phát hiện: Bệnh nhân vẻ mặt hốt hoảng, vã mồ hôi lạnh, huyết áp 150/90 mmHg, nhịp tim 95 lần/phút']`
  - `M07` [CHẨN ĐOÁN] `chu_the=bệnh nhân` | `noi_dung=Hội chứng vành cấp: cơn đau thắt ngực không ổn định` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Bác sĩ nghĩ nhiều đến: Hội chứng vành cấp: cơn đau thắt ngực không ổn định']`
  - `M08` [KẾ HOẠCH ĐIỀU TRỊ] `chu_the=bệnh nhân` | `noi_dung=Đo điện tâm đồ ngay lập tức, xét nghiệm troponin hàng loạt. Ngậm dưới lưỡi nitroglycerin, chống đông heparin và chuyển viện cấp cứu can thiệp mạch vành` | `moc=None` | `phu_dinh=False` | `tinh_huong=kế hoạch` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Bác sĩ đề ra phác đồ: Đo điện tâm đồ ngay lập tức, xét nghiệm troponin hàng loạt. Ngậm dưới lưỡi nitroglycerin, chống đông heparin và chuyển viện cấp cứu can thiệp mạch vành']`
- **Các lỗi phát hiện khi đọc ca này (6 lỗi):**
  - **L04** — *Biến f-string chưa thay (`{goi}`/`{goi_hoa}`)*: `Bác sĩ: Bác sĩ mời {goi}, chị đã kịp ăn lót dạ món gì nhẹ nhàng chưa nhé?`
  - **L04** — *Tiểu từ đề nghị (`nhé/nha/nghen`) gắn vào câu hỏi `?`*: `Bác sĩ: Bác sĩ mời {goi}, chị đã kịp ăn lót dạ món gì nhẹ nhàng chưa nhé?`
  - **L04-L05** — *Hỏi đáp xã giao lệch cặp (hỏi một đằng, đáp một nẻo)*: `Bác sĩ: Bác sĩ mời {goi}, chị đã kịp ăn lót dạ món gì nhẹ nhàng chưa nhé? / Người nhà: Dạ thưa bác sĩ, em cảm ơn bác sĩ đã chu đáo quan tâm ạ.`
  - **L11** — *Cụm nhận xét thừa sau dấu chấm ở cuối câu*: `Bác sĩ: Khám thực thể phát hiện: Bệnh nhân vẻ mặt hốt hoảng, vã mồ hôi lạnh, huyết áp 150/90 mmHg, nhịp tim 95 lần/phút. rõ ràng.`
  - **L12** — *Cụm nhận xét thừa sau dấu chấm ở cuối câu*: `Bác sĩ: Bác sĩ nghĩ nhiều đến: Hội chứng vành cấp: cơn đau thắt ngực không ổn định. đừng quá lo lắng nhé.`
  - **L13** — *Cụm nhận xét thừa sau dấu chấm ở cuối câu*: `Bác sĩ: Bác sĩ đề ra phác đồ: Đo điện tâm đồ ngay lập tức, xét nghiệm troponin hàng loạt. Ngậm dưới lưỡi nitroglycerin, chống đông heparin và chuyển viện cấp cứu can thiệp mạch vành. theo đúng hướng dẫn.`

### Ca 28 — Mã: `hv_1928` (`đái tháo nhạt`)
- **Thông tin ca:** `la_tre_em=False` | `nguoi_ke=None` | `lo_danh_tinh=False` | `boi_canh=kham_lan_dau` | `bay=['dai_tu_ho_hang', 'hoi_khong_dap']` | `so_luot=16`
- **Lời thoại đầy đủ:**
```text
L01: Bác sĩ: Mời anh ngồi xuống, hôm nay anh thấy sức khỏe thế nào ạ?
L02: Bác sĩ: Ngồi đối diện bác sĩ, Anh hít thở sâu vài nhịp để lấy lại bình tĩnh nhé nhé?
L03: Bệnh nhân: Vâng ạ, gặp bác sĩ nhẹ nhàng thế này em thấy an tâm hơn nhiều rồi nghen bác sĩ.
L04: Bác sĩ: Bác sĩ mời {goi}, anh đã kịp ăn lót dạ món gì nhẹ nhàng chưa nhé?
L05: Bệnh nhân: Vâng ạ, em có mang theo bình nước ấm uống suốt dọc đường rồi ạ.
L06: Bệnh nhân: Tình trạng uống nước liên tục trên 5 lít một ngày của tôi kéo dài mấy tháng nay rồi ạ.
L07: Bác sĩ: Ngoài chuyện đó ra, có xuất hiện thêm dấu hiệu đau nhức hay mệt mỏi ở đâu không vậy ạ?
L08: Bệnh nhân: Dạ vâng, tôi ghi nhận thêm hiện tượng khô miệng khát dữ dội nữa ạ.
L09: Bác sĩ: Thế về tiền sử sức khỏe, trước đây có từng mắc bệnh tương tự như đợt này chưa nhé?
L10: Bệnh nhân: Dạ em nghe bác sĩ, tôi có viêm xoang mạn ạ.
L11: Bác sĩ: Anh có hay bị hoa mắt chóng mặt khi đứng lên ngồi xuống không?
L12: Bác sĩ: Bước tiếp theo, để tôi gõ nhẹ vùng lưng xem thận có đau không nhé ạ.
L13: Bác sĩ: Đánh giá tình trạng thực thể: Dấu hiệu mất nước nhẹ, da khô, mạch nhanh 92 lần/phút, huyết áp bình thường. cần theo dõi.
L14: Bác sĩ: Tôi chẩn đoán là: Theo dõi đái tháo nhạt trung ương. nghen.
L15: Bác sĩ: Về phương án điều trị: Xét nghiệm áp lực thẩm thấu máu và nước tiểu, tỷ trọng nước tiểu. Chụp MRI tuyến yên loại trừ u đè ép. để theo dõi thêm.
L16: Bệnh nhân: Dạ, tôi sẽ kiêng các món ăn cay nóng và dầu mỡ như bác khuyên nghen, chào bác sĩ.
```
- **Đáp án mệnh đề (`dap_an`):**
  - `M01` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=uống nước liên tục trên 5 lít một ngày` | `moc=mấy tháng nay` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Tình trạng uống nước liên tục trên 5 lít một ngày của tôi kéo dài mấy tháng nay rồi ạ']`
  - `M02` [LÝ DO KHÁM BỆNH] `chu_the=bệnh nhân` | `noi_dung=uống nước liên tục trên 5 lít một ngày` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Tình trạng uống nước liên tục trên 5 lít một ngày của tôi kéo dài mấy tháng nay rồi ạ']`
  - `M03` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=khô miệng khát dữ dội` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['tôi ghi nhận thêm hiện tượng khô miệng khát dữ dội nữa ạ']`
  - `M04` [TIỀN SỬ BỆNH] `chu_the=bệnh nhân` | `noi_dung=viêm xoang mạn` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['tôi có viêm xoang mạn ạ']`
  - `M05` [KHÁM LÂM SÀNG] `chu_the=bệnh nhân` | `noi_dung=Dấu hiệu mất nước nhẹ, da khô, mạch nhanh 92 lần/phút, huyết áp bình thường` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Đánh giá tình trạng thực thể: Dấu hiệu mất nước nhẹ, da khô, mạch nhanh 92 lần/phút, huyết áp bình thường']`
  - `M06` [CHẨN ĐOÁN] `chu_the=bệnh nhân` | `noi_dung=đái tháo nhạt trung ương` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=nghi ngờ` | `quan_he=None` | `trich_dan=['Tôi chẩn đoán là: Theo dõi đái tháo nhạt trung ương']`
  - `M07` [KẾ HOẠCH ĐIỀU TRỊ] `chu_the=bệnh nhân` | `noi_dung=Xét nghiệm áp lực thẩm thấu máu và nước tiểu, tỷ trọng nước tiểu. Chụp MRI tuyến yên loại trừ u đè ép` | `moc=None` | `phu_dinh=False` | `tinh_huong=kế hoạch` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Về phương án điều trị: Xét nghiệm áp lực thẩm thấu máu và nước tiểu, tỷ trọng nước tiểu. Chụp MRI tuyến yên loại trừ u đè ép']`
- **Các lỗi phát hiện khi đọc ca này (12 lỗi):**
  - **L02** — *Tiểu từ đề nghị (`nhé/nha/nghen`) gắn vào câu hỏi `?`*: `Bác sĩ: Ngồi đối diện bác sĩ, Anh hít thở sâu vài nhịp để lấy lại bình tĩnh nhé nhé?`
  - **L02** — *Lặp tiểu từ `nhé nhé`*: `Bác sĩ: Ngồi đối diện bác sĩ, Anh hít thở sâu vài nhịp để lấy lại bình tĩnh nhé nhé?`
  - **L04** — *Biến f-string chưa thay (`{goi}`/`{goi_hoa}`)*: `Bác sĩ: Bác sĩ mời {goi}, anh đã kịp ăn lót dạ món gì nhẹ nhàng chưa nhé?`
  - **L04** — *Tiểu từ đề nghị (`nhé/nha/nghen`) gắn vào câu hỏi `?`*: `Bác sĩ: Bác sĩ mời {goi}, anh đã kịp ăn lót dạ món gì nhẹ nhàng chưa nhé?`
  - **L04-L05** — *Hỏi đáp xã giao lệch cặp (hỏi một đằng, đáp một nẻo)*: `Bác sĩ: Bác sĩ mời {goi}, anh đã kịp ăn lót dạ món gì nhẹ nhàng chưa nhé? / Bệnh nhân: Vâng ạ, em có mang theo bình nước ấm uống suốt dọc đường rồi ạ.`
  - **L06** — *Lặp từ thời gian `nay nay` / `rồi nay` / `nay rồi nay`*: `Bệnh nhân: Tình trạng uống nước liên tục trên 5 lít một ngày của tôi kéo dài mấy tháng nay rồi ạ.`
  - **L09** — *Tiểu từ đề nghị (`nhé/nha/nghen`) gắn vào câu hỏi `?`*: `Bác sĩ: Thế về tiền sử sức khỏe, trước đây có từng mắc bệnh tương tự như đợt này chưa nhé?`
  - **L10** — *Xung đột đại từ tự xưng trong cùng một câu (`em` vs `tôi`)*: `Bệnh nhân: Dạ em nghe bác sĩ, tôi có viêm xoang mạn ạ.`
  - **L10** — *Từ đệm mở đầu lệch đại từ tự xưng với phần thân câu*: `Bệnh nhân: Dạ em nghe bác sĩ, tôi có viêm xoang mạn ạ.`
  - **L13** — *Cụm nhận xét thừa sau dấu chấm ở cuối câu*: `Bác sĩ: Đánh giá tình trạng thực thể: Dấu hiệu mất nước nhẹ, da khô, mạch nhanh 92 lần/phút, huyết áp bình thường. cần theo dõi.`
  - **L14** — *Hạt đề nghị thừa sau dấu chấm (`. nhé.`, `. nha.`, `. nghen.`)*: `Bác sĩ: Tôi chẩn đoán là: Theo dõi đái tháo nhạt trung ương. nghen.`
  - **L15** — *Cụm nhận xét thừa sau dấu chấm ở cuối câu*: `Bác sĩ: Về phương án điều trị: Xét nghiệm áp lực thẩm thấu máu và nước tiểu, tỷ trọng nước tiểu. Chụp MRI tuyến yên loại trừ u đè ép. để theo dõi thêm.`

### Ca 29 — Mã: `hv_1605` (`nhiễm khuẩn sơ sinh sớm`)
- **Thông tin ca:** `la_tre_em=True` | `nguoi_ke=bà ngoại` | `lo_danh_tinh=False` | `boi_canh=cho_ket_qua` | `bay=['nguoi_nha_ke_ho']` | `so_luot=16`
- **Lời thoại đầy đủ:**
```text
L01: Bác sĩ: Mời bà ngồi, Bà kể bác sĩ nghe xem cháu bị mệt thế nào?
L02: Bác sĩ: Trời nắng nóng thế này, không khí dạo này hanh khô có làm cháu bị khô rát họng không?
L03: Người nhà: Dạ đúng rồi bác, thời tiết nắng gắt nên đi ngoài đường cũng hơi mệt một chút bác sĩ ạ.
L04: Người nhà: Cháu tôi khó chịu vì vàng da xuất hiện sớm trước 24 giờ sau sinh dai dẳng hơn một tuần nay.
L05: Bác sĩ: Cho tôi hỏi thêm là, mình còn cảm thấy khó chịu ở chỗ nào khác nữa không nhỉ?
L06: Người nhà: Dạ vâng, ngoài ra cháu tôi còn bị xét nghiệm crp huyết thanh tăng vọt trên 10 mg/l, gan lách to sờ thấy dưới bờ sườn nữa.
L07: Bác sĩ: Mình có từng được chẩn đoán bệnh gì lâu năm chưa khỏi không vậy ạ?
L08: Người nhà: Dạ bác sĩ, cháu tôi có sinh non.
L09: Bác sĩ: Về phần dị ứng thì sao, mình có cơ địa dị ứng thuốc, thức ăn hay thời tiết không hả bạn?
L10: Người nhà: Dạ, có, dị ứng penicillin ạ.
L11: Bác sĩ: Để tôi, để tôi gõ nhẹ vùng lưng xem thận có đau không nha.
L12: Bác sĩ: Sau khi kiểm tra trực tiếp: Trẻ lờ đờ, trương lực cơ giảm, thóp trũng nhẹ, da tái vân tím.
L13: Bác sĩ: Tôi nghĩ nhiều đến nhiễm khuẩn sơ sinh sớm ngày thứ hai, nhưng chưa kết luận được. Phải có kết quả xét nghiệm nước tiểu đã nha.
L14: Bác sĩ: Cháu đi làm xét nghiệm nước tiểu rồi quay lại đây.
L15: Bác sĩ: Trong toa thuốc tôi kê oresol một gói, uống ngày ba lần uống đúng giờ nhé.
L16: Người nhà: Dạ bác sĩ, tôi sẽ kiêng các món ăn cay nóng và dầu mỡ như bác khuyên, chúc bác sĩ một ngày làm việc thuận lợi nghen, chào bác sĩ.
```
- **Đáp án mệnh đề (`dap_an`):**
  - `M01` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=vàng da xuất hiện sớm trước 24 giờ sau sinh` | `moc=hơn một tuần` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Cháu tôi khó chịu vì vàng da xuất hiện sớm trước 24 giờ sau sinh dai dẳng hơn một tuần nay']`
  - `M02` [LÝ DO KHÁM BỆNH] `chu_the=bệnh nhân` | `noi_dung=vàng da xuất hiện sớm trước 24 giờ sau sinh` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Cháu tôi khó chịu vì vàng da xuất hiện sớm trước 24 giờ sau sinh dai dẳng hơn một tuần nay']`
  - `M03` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=xét nghiệm crp huyết thanh tăng vọt trên 10 mg/l` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['ngoài ra cháu tôi còn bị xét nghiệm crp huyết thanh tăng vọt trên 10 mg/l']`
  - `M04` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=gan lách to sờ thấy dưới bờ sườn` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['gan lách to sờ thấy dưới bờ sườn nữa']`
  - `M05` [TIỀN SỬ BỆNH] `chu_the=bệnh nhân` | `noi_dung=sinh non` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['cháu tôi có sinh non']`
  - `M06` [DỊ ỨNG] `chu_the=bệnh nhân` | `noi_dung=dị ứng penicillin` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['dị ứng penicillin ạ']`
  - `M07` [KHÁM LÂM SÀNG] `chu_the=bệnh nhân` | `noi_dung=Trẻ lờ đờ, trương lực cơ giảm, thóp trũng nhẹ, da tái vân tím` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Sau khi kiểm tra trực tiếp: Trẻ lờ đờ, trương lực cơ giảm, thóp trũng nhẹ, da tái vân tím']`
  - `M08` [CHẨN ĐOÁN] `chu_the=bệnh nhân` | `noi_dung=nhiễm khuẩn sơ sinh sớm ngày thứ hai` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=nghi ngờ` | `quan_he=None` | `trich_dan=['Tôi nghĩ nhiều đến nhiễm khuẩn sơ sinh sớm ngày thứ hai']`
  - `M09` [KẾ HOẠCH ĐIỀU TRỊ] `chu_the=bệnh nhân` | `noi_dung=làm xét nghiệm nước tiểu` | `moc=None` | `phu_dinh=False` | `tinh_huong=kế hoạch` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Cháu đi làm xét nghiệm nước tiểu rồi quay lại đây']`
  - `M10` [KẾ HOẠCH ĐIỀU TRỊ] `chu_the=bệnh nhân` | `noi_dung=kê oresol` | `moc=None` | `phu_dinh=False` | `tinh_huong=kế hoạch` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Trong toa thuốc tôi kê oresol một gói, uống ngày ba lần uống đúng giờ nhé']`
- **Các lỗi phát hiện khi đọc ca này (4 lỗi):**
  - **L02-L03** — *Hỏi đáp xã giao lệch cặp (hỏi một đằng, đáp một nẻo)*: `Bác sĩ: Trời nắng nóng thế này, không khí dạo này hanh khô có làm cháu bị khô rát họng không? / Người nhà: Dạ đúng rồi bác, thời tiết nắng gắt nên đi ngoài đường cũng hơi mệt một chút bác sĩ ạ.`
  - **L09** — *Bác sĩ gọi người bệnh/người nhà là `bạn` (lệch vai xưng hô)*: `Bác sĩ: Về phần dị ứng thì sao, mình có cơ địa dị ứng thuốc, thức ăn hay thời tiết không hả bạn?`
  - **L11** — *Lặp dẫn nhập `Để tôi, để tôi...`*: `Bác sĩ: Để tôi, để tôi gõ nhẹ vùng lưng xem thận có đau không nha.`
  - **L15** — *Ghép thừa `uống ngày ... lần uống đúng giờ`*: `Bác sĩ: Trong toa thuốc tôi kê oresol một gói, uống ngày ba lần uống đúng giờ nhé.`

### Ca 30 — Mã: `hv_3910` (`sốt rét plasmodium vivax`)
- **Thông tin ca:** `la_tre_em=False` | `nguoi_ke=None` | `lo_danh_tinh=False` | `boi_canh=tai_kham` | `bay=[]` | `so_luot=18`
- **Lời thoại đầy đủ:**
```text
L01: Bác sĩ: Tình hình uống paracetamol từ hôm tái khám trước tới nay thế nào rồi anh ạ?
L02: Bệnh nhân: Dạ vâng, vẫn đang uống paracetamol ạ.
L03: Bác sĩ: Cho tôi hỏi một chút, hôm nay anh là người trực tiếp cần khám đúng không ạ?
L04: Bệnh nhân: Dạ đúng rồi, tôi đi khám cho bản thân đây ạ.
L05: Bác sĩ: Lúc tới phòng khám, Anh đi thang máy hay thang bộ lên tầng này vậy thế ạ?
L06: Bệnh nhân: Vâng ạ, biển chỉ dẫn to rõ ngoài cổng nên em tìm thấy ngay.
L07: Bệnh nhân: Tôi bắt đầu thấy cơn sốt rét run có chu kỳ cách nhật ba giai đoạn rét sốt ướt hết áo khoảng gần một tuần nay ạ.
L08: Bác sĩ: Liệu còn vấn đề gì, trong người còn thấy gì khang khác hay thay đổi gì không?
L09: Bệnh nhân: Vâng thưa bác sĩ, tôi ghi nhận thêm hiện tượng tiểu cầu máu ngoại vi giảm nhẹ kèm men gan tăng nữa.
L10: Bác sĩ: Cho hỏi thêm là, bạn có mẫn cảm đặc biệt với thành phần thuốc nào không hả bạn?
L11: Bệnh nhân: Dạ thưa bác sĩ không ạ, sức khỏe bình thường, chưa từng bị phản ứng lạ với thuốc từ trước tới nay đâu ạ.
L12: Bác sĩ: Thế gần đây, mình có đang dùng loại thuốc nào không nhé?
L13: Bệnh nhân: Dạ, trước tôi có uống amlodipin 5 mg, ngày một lần buổi sáng, ngừng 4 tuần rồi ạ.
L14: Bác sĩ: Ngay sau đây, tôi sờ nắn vào chỗ đau xem mức độ thế nào nha.
L15: Bác sĩ: Khám lâm sàng: Lách to độ 1 dưới bờ sườn, da sạm tái, gan không to. nghen.
L16: Bác sĩ: Trường hợp này được chẩn đoán là: Sốt rét cơn do Plasmodium vivax chưa biến chứng. rõ ràng.
L17: Bác sĩ: Về kế hoạch điều trị: Điều trị diệt thể phân liệt bằng artesunate hoặc chloroquine phối hợp primaquine diệt thể ngủ ở gan 14 ngày để chống tái phát. nhé.
L18: Bệnh nhân: Dạ thưa bác sĩ, tôi hiểu rõ phác đồ bác sĩ đưa ra rồi, xin chúc bác sĩ nhiều niềm vui trong công việc ạ, tôi xin phép ra quầy thanh toán.
```
- **Đáp án mệnh đề (`dap_an`):**
  - `M01` [THUỐC ĐANG DÙNG] `chu_the=bệnh nhân` | `noi_dung=đang dùng paracetamol` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['vẫn đang uống paracetamol ạ']`
  - `M02` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=cơn sốt rét run có chu kỳ cách nhật ba giai đoạn rét sốt vã mồ hôi` | `moc=gần một tuần` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Tôi bắt đầu thấy cơn sốt rét run có chu kỳ cách nhật ba giai đoạn rét sốt ướt hết áo khoảng gần một tuần nay ạ']`
  - `M03` [LÝ DO KHÁM BỆNH] `chu_the=bệnh nhân` | `noi_dung=cơn sốt rét run có chu kỳ cách nhật ba giai đoạn rét sốt vã mồ hôi` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Tôi bắt đầu thấy cơn sốt rét run có chu kỳ cách nhật ba giai đoạn rét sốt ướt hết áo khoảng gần một tuần nay ạ']`
  - `M04` [BỆNH SỬ HIỆN TẠI] `chu_the=bệnh nhân` | `noi_dung=tiểu cầu máu ngoại vi giảm nhẹ kèm men gan tăng` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['tôi ghi nhận thêm hiện tượng tiểu cầu máu ngoại vi giảm nhẹ kèm men gan tăng nữa']`
  - `M05` [DỊ ỨNG] `chu_the=bệnh nhân` | `noi_dung=dị ứng thuốc` | `moc=None` | `phu_dinh=True` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['bạn có mẫn cảm đặc biệt với thành phần thuốc nào không hả bạn', 'chưa từng bị phản ứng lạ với thuốc từ trước tới nay đâu ạ']`
  - `M06` [TIỀN SỬ BỆNH] `chu_the=bệnh nhân` | `noi_dung=từng dùng amlodipin, đã ngừng 4 tuần` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['trước tôi có uống amlodipin 5 mg, ngày một lần buổi sáng, ngừng 4 tuần rồi ạ']`
  - `M07` [KHÁM LÂM SÀNG] `chu_the=bệnh nhân` | `noi_dung=Lách to độ 1 dưới bờ sườn, da sạm tái, gan không to` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Khám lâm sàng: Lách to độ 1 dưới bờ sườn, da sạm tái, gan không to']`
  - `M08` [CHẨN ĐOÁN] `chu_the=bệnh nhân` | `noi_dung=Sốt rét cơn do Plasmodium vivax chưa biến chứng` | `moc=None` | `phu_dinh=False` | `tinh_huong=thực tế` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Trường hợp này được chẩn đoán là: Sốt rét cơn do Plasmodium vivax chưa biến chứng']`
  - `M09` [KẾ HOẠCH ĐIỀU TRỊ] `chu_the=bệnh nhân` | `noi_dung=Điều trị diệt thể phân liệt bằng artesunate hoặc chloroquine phối hợp primaquine diệt thể ngủ ở gan 14 ngày để chống tái phát` | `moc=None` | `phu_dinh=False` | `tinh_huong=kế hoạch` | `do_chac_chan=chắc chắn` | `quan_he=None` | `trich_dan=['Về kế hoạch điều trị: Điều trị diệt thể phân liệt bằng artesunate hoặc chloroquine phối hợp primaquine diệt thể ngủ ở gan 14 ngày để chống tái phát']`
- **Các lỗi phát hiện khi đọc ca này (7 lỗi):**
  - **L05** — *Lặp từ nghi vấn `vậy vậy` / `vậy thế`*: `Bác sĩ: Lúc tới phòng khám, Anh đi thang máy hay thang bộ lên tầng này vậy thế ạ?`
  - **L05-L06** — *Hỏi đáp xã giao lệch cặp (hỏi một đằng, đáp một nẻo)*: `Bác sĩ: Lúc tới phòng khám, Anh đi thang máy hay thang bộ lên tầng này vậy thế ạ? / Bệnh nhân: Vâng ạ, biển chỉ dẫn to rõ ngoài cổng nên em tìm thấy ngay.`
  - **L10** — *Bác sĩ gọi người bệnh/người nhà là `bạn` (lệch vai xưng hô)*: `Bác sĩ: Cho hỏi thêm là, bạn có mẫn cảm đặc biệt với thành phần thuốc nào không hả bạn?`
  - **L12** — *Tiểu từ đề nghị (`nhé/nha/nghen`) gắn vào câu hỏi `?`*: `Bác sĩ: Thế gần đây, mình có đang dùng loại thuốc nào không nhé?`
  - **L15** — *Hạt đề nghị thừa sau dấu chấm (`. nhé.`, `. nha.`, `. nghen.`)*: `Bác sĩ: Khám lâm sàng: Lách to độ 1 dưới bờ sườn, da sạm tái, gan không to. nghen.`
  - **L16** — *Cụm nhận xét thừa sau dấu chấm ở cuối câu*: `Bác sĩ: Trường hợp này được chẩn đoán là: Sốt rét cơn do Plasmodium vivax chưa biến chứng. rõ ràng.`
  - **L17** — *Hạt đề nghị thừa sau dấu chấm (`. nhé.`, `. nha.`, `. nghen.`)*: `Bác sĩ: Về kế hoạch điều trị: Điều trị diệt thể phân liệt bằng artesunate hoặc chloroquine phối hợp primaquine diệt thể ngủ ở gan 14 ngày để chống tái phát. nhé.`
