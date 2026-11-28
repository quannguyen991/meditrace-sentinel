# MediTrace Sentinel

**Phần mềm dựng bản nháp hồ sơ khám bệnh từ lời nói của buổi khám bằng tiếng Việt, trong đó mỗi dòng đều chỉ ra được câu nói làm căn cứ.**

> **Lưu ý quan trọng.** MediTrace chỉ tạo **bản nháp để bác sĩ xem lại**. Phần mềm không chẩn đoán bệnh, không kê đơn, không thay quyết định của bác sĩ, và bản nháp không phải hồ sơ bệnh án chính thức. Toàn bộ dữ liệu dùng để xây dựng và đo kết quả là hội thoại **mô phỏng** do chương trình tạo ra. Không dùng hồ sơ, bản ghi âm hay thông tin của bệnh nhân thật.

---

## Dành cho ban người đánh giá: xem thử trong 3 phút

> **Báo cáo cải tiến Chặng 1 (AI 2026):** Xem đối chiếu chi tiết từng yêu cầu cải tiến (giảm bỏ sót & chốt chặn không hoàn tất hồ sơ khi thiếu căn cứ; kiểm soát lỗi giữa các bước AI & demo đa người nói; kiểm tra tính độc lập bộ dữ liệu 657 khuôn & kịch bản ngoài khuôn) tại **[`BAO_CAO_CAI_TIEN_CHANG_1.md`](BAO_CAO_CAI_TIEN_CHANG_1.md)**.

1. Mở **https://meditrace-sentinel.meditrace.workers.dev** và đăng nhập bằng tài khoản dùng thử ghi trong hồ sơ dự thi. (Phần mềm yêu cầu tài khoản để bảo vệ dữ liệu của người dùng.)
2. Ở **Trang chủ**, bấm nút **"Xem thử với ca mẫu"**. Mỗi lần bấm, phần mềm xoay vòng qua **3 ca khám đa người nói dựng sẵn** (*Bác sĩ – Mẹ – Bệnh nhi*, *Hai người bệnh cùng phòng trao đổi*, *Bác sĩ – Cụ ông 74 tuổi – Con gái*), có sẵn bản nháp và mục `Cần xác nhận`, không cần GPU và không phải chờ.
3. Bấm vào một dòng trong bản nháp để mở **ngăn duyệt** ngay bên cạnh, hoặc bấm nút xanh **"Duyệt từng mệnh đề"** để sang màn duyệt đầy đủ. Bên trái là lời thoại, bên phải là từng thông tin được rút ra kèm chủ thể và đường nối căn cứ. Những thông tin chưa chắc nằm trong mục **Cần xác nhận** kèm lý do — hệ thống **khóa cứng không cho ký duyệt hoàn tất hồ sơ** cho tới khi bác sĩ xác nhận, sửa hoặc bỏ hết các mục này.
4. Thử **ghi âm**: bấm "Bắt đầu ghi âm" và nói vài câu, hoặc "Tải tệp âm thanh". Với ca có ghi âm, mỗi mệnh đề có nút **"Nghe lại"** phát đúng đoạn ghi âm gốc làm căn cứ. Ca mẫu chỉ có chữ, nên mỗi lượt thoại có nút **"Nghe"** đọc to bằng giọng tiếng Việt của trình duyệt (nghe tự nhiên nhất trên Microsoft Edge).
5. Các công cụ lâm sàng (tiền kiểm BHYT/ICD-10, đơn thuốc TT26/DDI, cam đoan thủ thuật, đi buồng, SBAR, chép sang HIS, tờ dặn dò kèm mã QR cho người bệnh) nằm trong menu **"Công cụ"** trên thanh bản nháp.

> **Báo cáo cải tiến theo góp ý của ban giám khảo (26/11/2026):** [`docs/bao-cao-cai-tien/BAO_CAO_CAI_TIEN_BGK_26-11-2026.pdf`](docs/bao-cao-cai-tien/BAO_CAO_CAI_TIEN_BGK_26-11-2026.pdf) (12 trang; có bản HTML cùng tên).

Ghi chú: giao diện bằng tiếng Việt. Tạo một bản nháp mới bằng mô hình thật mất khoảng **3,5 phút** trên một card đồ hoạ phổ thông, nên nên dùng ca mẫu để xem nhanh.

---

## Vấn đề phần mềm giải quyết

Các mô hình trí tuệ nhân tạo ngày nay có thể nghe một buổi khám rồi viết ngay một bản ghi chép trôi chảy. Nhưng câu văn trôi chảy chưa chắc đúng. Lỗi nguy hiểm nhất là lỗi **khó nhìn thấy**: câu vẫn đúng ngữ pháp, đọc không thấy gì lạ, nhưng sai về người, về thời điểm hoặc về việc đã xảy ra hay chưa.

| Điều được nói trong buổi khám | Bản ghi chép sai có thể ghi |
|---|---|
| Người con nói: "**Bố em** bị hen từ nhỏ." | "Bệnh nhân có tiền sử hen." (sai người) |
| Người bệnh nói: "Ho một tuần… à không, **mười ngày** rồi." | "Ho một tuần" vẫn được giữ lại như thể còn đúng (giữ thông tin đã bị sửa) |
| Bác sĩ dặn: "**Nếu** mai còn sốt thì chụp phim." | "Đã chụp phim." (biến lời dặn thành việc đã làm) |
| Bác sĩ hỏi: "Có dị ứng thuốc gì không?" (chưa ai trả lời) | "Không dị ứng thuốc." (ghi điều chưa ai nói) |

Với dị ứng hoặc thuốc đang dùng, những lỗi này có thể dẫn tới quyết định sai nếu người đọc không đối chiếu lại với hội thoại.

**Cách chấm điểm thông thường không phát hiện được các lỗi này.** Trong thử nghiệm của dự án trên 400 bản hồ sơ, khi cố ý đổi chỗ "bệnh nhân" và "người nhà", điểm **ROUGE-1** (điểm đếm số từ trùng với bản mẫu, rất hay dùng để chấm văn bản do AI viết) vẫn bằng đúng **1,0000**, tức là điểm tuyệt đối. Lý do: đổi chỗ hai người không thêm bớt từ nào, nên điểm không đổi.

**Tiếng Việt làm các lỗi này dễ xảy ra hơn**, vì câu nói thường bỏ chủ ngữ ("Sốt hai hôm rồi") và các từ chỉ họ hàng như "con", "cháu", "em" vừa dùng để tự xưng, vừa dùng để gọi người khác.

---

## Cách MediTrace làm

Thay vì để mô hình viết thẳng cả đoạn văn, MediTrace chia việc thành các bước nhỏ. Mỗi bước làm một việc, nên khi bản nháp sai thì biết sai ở bước nào.

```
lời thoại → 1. rút từng thông tin (AI) → 2. gom người → 3. cập nhật trạng thái → 4. kiểm căn cứ → 5. xếp chỗ → bản nháp
```

| Bước | Việc làm | Ai làm | Tệp mã |
|---|---|---|---|
| **1. Rút thông tin** | Đọc lời thoại và liệt kê từng thông tin lâm sàng, gọi là **mệnh đề**. Mỗi mệnh đề ghi: nội dung; thông tin này **nói về ai**; ai nói; chắc chắn hay chỉ nghi ngờ; có phủ định không ("không sốt"); là việc đã xảy ra, hay chỉ là giả định hoặc kế hoạch; thời gian; số thứ tự lượt nói làm căn cứ; và **câu trích nguyên văn**. | **Mô hình AI** (Qwen3-4B, chạy ngay trên máy) | `src/duong_ong/chay_duong_ong.py`, `src/duong_ong/b1_cau_truc_menh_de.py` |
| **2. Gom người** | Phân biệt **người nói** với **người được nói đến**. Ví dụ người con kể về bố thì thông tin thuộc về bố, không thuộc về người bệnh. | Chương trình theo luật cố định | `src/duong_ong/b2_gom_nguoi_thuc_the.py` |
| **3. Cập nhật trạng thái** | Khi người nói **tự sửa** ("một tuần… à không, mười ngày") thì bản cũ được đánh dấu "bị thay thế", **không xoá**. Khi hai thông tin theo thời gian đều đúng ("hôm qua đau, hôm nay hết") thì giữ cả hai. Khi hai người nói trái nhau mà chưa ai xác nhận thì đánh dấu **mâu thuẫn**. | Chương trình theo luật | `src/duong_ong/b3_cap_nhat_trang_thai.py` |
| **4. Kiểm căn cứ** | Đối chiếu từng thông tin với đúng lượt nói được dẫn. Bảy phép kiểm (K1–K7): (1) câu trích có thật trong lượt đó không; (2) nội dung có khớp không; (3) từ chỉ người có khớp với người được nhắc tới không; (4) mức chắc chắn có bị nâng lên không; (5) thời gian có xuất hiện trong lượt đó không; (6) liều thuốc có xuất hiện trong lượt đó không; (7) thông tin có bị một diễn biến mới hơn thay thế hoặc bị đính chính không. | Chương trình theo luật | `src/duong_ong/b4_kiem_can_cu.py` |
| **5. Xếp chỗ** | Mỗi thông tin vào một trong ba chỗ: **thân bản nháp**; mục **"Cần xác nhận"** (kèm lý do, để bác sĩ xem lại); hoặc **bị loại** (vẫn lưu vết). Sau đó bản nháp được viết ra theo mẫu câu cố định. | Chương trình theo luật | `src/duong_ong/b5_xep_cho_cong_rui_ro.py`, `src/canh_bao/` |
| *Phụ* | Gợi ý tối đa 3 câu hỏi để bác sĩ hỏi lại người bệnh. | Chương trình | `src/duong_ong/b6_goi_y_hoi_lai.py` |

**Chỉ bước 1 dùng mô hình AI. Các bước còn lại là luật mà con người đọc được.** Nhờ vậy, khi bản nháp có lỗi, có thể xác định lỗi do mô hình liệt kê thiếu hay do một luật xếp nhầm. Mỗi dòng của bản nháp đều truy ngược được về mệnh đề và câu nói gốc.

### Ví dụ chạy thật trên ca mô phỏng

Hội thoại:
- Bác sĩ: "Cô có dị ứng thuốc gì không ạ?"
- Bệnh nhân: "Tôi uống amoxicillin là nổi mẩn toàn thân."
- Con trai: "Bố em bị hen, không biết có liên quan không bác sĩ."
- Bệnh nhân: "Tôi ho chừng một tuần… à không, từ hôm rằm, mười ngày rồi."
- Bác sĩ: "Nếu mai còn sốt thì quay lại chụp phim."

Kết quả đúng: dị ứng amoxicillin thuộc về **bệnh nhân** (căn cứ ở lượt 1–2); bệnh hen thuộc về **bố**, ghi ở mục tiền sử gia đình; ho **mười ngày**, còn "một tuần" bị đánh dấu thay thế; việc chụp phim là **dự định có điều kiện**, được đưa sang mục "Cần xác nhận".

---

## Các thành phần của phần mềm

> **Tìm mã nguồn nhanh:** [`BAN_DO_MA_NGUON.md`](BAN_DO_MA_NGUON.md) xếp toàn bộ mã theo hệ thống (đường ống dựng bản nháp, dữ liệu, huấn luyện, đo lường, công cụ lâm sàng, dịch vụ và an toàn) và có bảng *"hỏi gì → mở tệp nào"*. Từ 27/11/2026 mã Python nằm trong các thư mục con của `src/` với tên mới; tài liệu cũ còn ghi tên trước đó (ví dụ `src/khoa_bang_chung.py`) thì tra bảng *Đối chiếu tên cũ* ở cuối bản đồ.

| Thành phần | Mô tả |
|---|---|
| **Xử lý bằng Python** (`src/`) | Bộ tạo dữ liệu mô phỏng, mô hình rút thông tin, các bước theo luật, bộ chấm điểm, dịch vụ chạy trên máy. |
| **Giao diện web** (`web/`) | Viết bằng React. Bác sĩ **giữ, sửa hoặc bỏ** từng dòng của bản nháp; mỗi dòng nối về lượt nói gốc. Có tài khoản đăng nhập bằng mã mời; ca khám lưu trong cơ sở dữ liệu SQLite, tách riêng cho từng người dùng. |
| **Đầu vào âm thanh** (`src/audio/`) | Chép lời bằng **PhoWhisper** (mô hình nhận dạng tiếng nói tiếng Việt) chạy ngay trên máy. Có thể tách giọng từng người nói bằng pyannote; khi đó bác sĩ chọn vai (bác sĩ, bệnh nhân, người nhà) cho từng giọng. |
| **Dịch vụ mô hình ngoài** (tuỳ chọn) | Chỉ dùng cho việc phụ như hỏi đáp về ca khám hoặc tra tài liệu. **Mặc định tắt**, chỉ chạy khi người dùng bật công tắc, có cảnh báo dữ liệu sẽ đi đâu, và **không bao giờ** dùng để viết bản nháp chính. Kết quả của phần này được ghi rõ là "chưa qua kiểm căn cứ". |

| **Lớp cảnh báo** (`src/canh_bao/`) | Sau khi kiểm căn cứ, đối chiếu từng dòng với lời thoại để bắt lỗi khó thấy: sai người, đảo phủ định, sai số, sai bên trái/phải, sai mức độ, nhầm chuyện trước đây với hiện tại, giữ giá trị đã bị đính chính, biến lời dặn thành việc đã làm, bỏ sót. Mỗi cảnh báo nêu lượt nói và lý do. |
| **Trợ lý nhiều tác tử** (`web/may-chu/tro-ly/`) | Bác sĩ hỏi ở ngăn bên phải màn soạn. Một bộ điều phối lập kế hoạch tối đa 6 bước rồi giao cho các tác tử tìm tài liệu, trả lời, đối chiếu, đối chiếu thuốc và dị ứng. Dữ liệu gửi ra ngoài được dựng từ danh sách cho phép (không có tên, số điện thoại, địa chỉ); câu hỏi có danh tính bị chặn. Quản trị có công tắc tắt toàn hệ thống. |

Trang chủ của phần mềm có bảng **"Ai xử lý phần nào"** nói rõ phần nào chạy ngay trên máy và phần nào có thể gửi ra ngoài.

### Tính năng hỗ trợ bác sĩ (bổ sung 24–25/11/2026)

Các tính năng này nằm quanh bản nháp. **Không tính năng nào thay đổi cách bản nháp được dựng.**

| # | Tính năng | Làm gì | Tệp chính |
|---|---|---|---|
| 1 | **Nghe lại đúng đoạn** | Bấm vào một dòng để phát lại đoạn ghi âm gốc (thêm 0,5 giây hai đầu). Dòng có số kèm đơn vị, có từ phủ định, hoặc chép lời kém chắc chắn được tô sáng. | `web/src/lib/asrHighlight.ts`, `DuyetBenCanh.tsx` |
| 2 | **Ký duyệt có chuỗi băm & chốt chặn căn cứ** | Chặn cứng ký duyệt khi chưa có mệnh đề có căn cứ hoặc còn mục `Cần xác nhận` chưa xử lý. Khi ký, bản ghi nối vào nhật ký chỉ-ghi-thêm có chuỗi băm SHA-256 (WORM) kèm tệp neo `.anchor.json`; sửa sau ký hiện cảnh báo `Đã sửa · Ký lại`. | `web/may-chu/worm.ts`, `compileEffectiveNote.ts`, `src/he_thong/nhat_ky_ky_duyet_worm.py` |
| 3 | **Phiếu bàn giao SBAR và chép sang HIS** | Tạo phiếu bàn giao SBAR từ bản nháp (tôn trọng dòng đã giữ/sửa/bỏ) và chép nhanh từng ô sang phần mềm bệnh viện. | `web/src/lib/sbar.ts`, `HisSmartCopyPopover.tsx` |
| 4 | **Gợi ý câu hỏi cờ đỏ** | Trong lúc khám, gợi ý tối đa 2 câu hỏi an toàn chưa hỏi (theo tuổi, giới); tự đánh dấu khi bác sĩ đã hỏi. Chạy tại chỗ, không gọi mô hình. | `web/src/lib/radarCoDo.ts` |
| 5 | **Tờ dặn dò cho người bệnh** | Tờ dặn dò in được, có nút đọc to bằng giọng tiếng Việt của trình duyệt. | `ToDanDoBenhNhanModal.tsx` |
| 6 | **Tiền kiểm BHYT** | Gợi ý mã ICD-10 (gồm mã 4 ký tự) và cảnh báo các điểm dễ bị xuất toán; không gợi ý mã cho bệnh đã bị phủ định. | `src/cong_cu_lam_sang/tien_kiem_bhyt_va_khoi_phuc_bo_sot.py`, `BhytPrecheckModal.tsx` |
| 7 | **Đọc phiếu xét nghiệm, đơn thuốc cũ** | Bóc chỉ số từ phiếu cũ, quy đổi đơn vị (creatinin µmol/L ↔ mg/dL), tính độ thanh thải creatinin để gợi ý chỉnh liều, cảnh báo kết hợp nguy hiểm (ví dụ kali ≥ 5,0 kèm spironolacton). | `src/cong_cu_lam_sang/doc_phieu_xet_nghiem.py`, `src/cong_cu_lam_sang/hieu_chinh_lieu.py` |
| 8 | **Đối chiếu với lần khám trước** | Báo khi dị ứng, bệnh nền hoặc thuốc mạn tính trái với các lần khám trước của cùng người bệnh; bỏ qua dòng bác sĩ đã bỏ hoặc đã đính chính. | `web/src/lib/doiChieuLanKham.ts`, `CrossVisitBanner.tsx` |

Các tính năng 6 và 7 dùng bảng tri thức thuốc và mã bệnh **chưa được dược sĩ hay bác sĩ duyệt** (`data/tri_thuc_thuoc.json`, mọi mục `da_duyet = false`). Chúng chỉ là gợi ý để đối chiếu.

### Nhật ký nâng cấp 15–26/11/2026

| Thời gian | Nâng cấp | Chi tiết / minh chứng |
|---|---|---|
| 17–21/11 | Kế hoạch nâng cấp toàn diện, rà lại số liệu | `KE_HOACH_NANG_CAP_TOAN_DIEN_MEDITRACE.md`; đếm lại 200 khuôn bộ v1; rút bỏ con số chưa có phép đo; quyết định về các mô hình Qwen (`docs/BAN-GIAO-CONG-VIEC-DANG-DO.md`). |
| 20–24/11 | **Bộ dữ liệu v2** | 657 khuôn bệnh thuộc 21 hệ cơ quan, 5.000 ca; tỷ lệ lặp câu giảm từ 76,92% xuống 47,37%; 100% trích dẫn khớp nguyên văn; chia train/phát triển/kiểm tra cuối không trùng khuôn (`docs/BAN-GIAO-SINH-DU-LIEU-V2.md`, `data/manifest_v2_mo_rong_5000.json`). |
| 22–24/11 | Huấn luyện tiết kiệm bộ nhớ, adapter v3 | `src/huan_luyen/loss_theo_doan.py` hạ đỉnh VRAM xuống 6,4 GiB trên RTX 3060; adapter v3 train trên bộ v2 (kết quả bỏ sót ở mục "Kết quả đo"). Hàng đợi việc nền bền vững bằng SQLite (`web/may-chu/hang-doi.ts`). |
| 24–25/11 | 8 tính năng hỗ trợ bác sĩ | Bảng ở trên: nghe lại đúng đoạn, ký duyệt có chuỗi băm, SBAR/HIS, câu hỏi cờ đỏ, tờ dặn dò, tiền kiểm BHYT, đọc phiếu cũ, đối chiếu lần khám trước. |
| 25–26/11 | **Lớp cảnh báo** vòng 6 và đo bằng cấy lỗi | `src/canh_bao/`; tiêu chí đăng ký trước (`docs/dang-ky-truoc-bo-luat.md`); kết quả ở mục "Kết quả đo". |
| 26/11 | Thử DPO trên cặp lỗi khó | `src/huan_luyen/huan_luyen_dpo.py`; chưa dùng trong hệ thống ([`docs/ket-qua/dpo-v3.md`](docs/ket-qua/dpo-v3.md)). |
| 26/11 | Rà soát độc lập, sửa 9 lỗi nghiêm trọng | Mục "Quyền riêng tư và an toàn". |
| 26/11 | **Công cụ lâm sàng mở rộng (Boost, M1–M4)** | Menu "Công cụ": tiền kiểm BHYT/ICD-10, đối soát đơn thuốc TT 26 và tương tác thuốc, cam đoan thủ thuật, đi buồng nội trú và bàn giao ca trực. Đọc khám rảnh tay (F2, PhoWhisper tại chỗ); gợi ý vai người nói một chạm; báo động giá trị xét nghiệm nguy kịch, nạp kết quả LIS/HL7 và danh mục thuốc bệnh viện (.csv) ở tab "Ngữ cảnh"; khôi phục mục bỏ sót một chạm; xuất gói HL7 FHIR R4 / BHYT XML 130. Màn "KHTH & Giám định BHYT" (kiểm toán XML 1–5) và cổng QR cho người bệnh. Bảng tri thức đi kèm **chưa được chuyên gia duyệt**. |
| 26/11 | Giao diện gọn cho bác sĩ | Mở ca là thấy bản nháp (danh sách ca và khung tra cứu thu gọn sẵn); công cụ gom vào một menu; bấm một dòng mở ngăn duyệt bên cạnh; nút "Nghe lại" ghi âm gốc trên từng mệnh đề, nút "Nghe" đọc to từng lượt cho ca chỉ có chữ. |
| 26/11 | Triển khai mới | Chuyển từ Vercel sang Cloudflare Worker, đường hầm tự cập nhật (mục "Chạy thử trên máy của bạn"). |

---

## Kết quả đo

**Dữ liệu.** 5.000 hội thoại mô phỏng thế hệ v1 (200 khuôn bệnh, tỷ lệ lặp câu 76,92%) và thế hệ v2 mở rộng (657 khuôn ca bệnh phân bố trên 21 hệ cơ quan; tỷ lệ lặp câu giảm xuống 47,37%, câu khác nhau tăng 127% lên 45.835 câu, MTLD 145,4, Distinct-2 0,0468; 100% trích dẫn nguyên văn chuỗi con 52.634/52.634 và 0 lỗi quy tắc ngữ pháp; manifest đóng băng WORM tại `data/manifest_v2_mo_rong_5000.json`). Toàn bộ được chia độc lập theo khuôn bệnh để mô hình không nhìn thấy trước bài kiểm tra. Ngoài ra có 300 ca "thử thách" tạo theo cặp, mỗi cặp chỉ khác nhau một điểm: đổi người mang dị ứng, người nói tự sửa, lỗi khi chép giọng nói, và phương ngữ.

**Cách đọc các chỉ số.** *F₁* là điểm gộp giữa "ghi đúng" và "ghi đủ" (càng cao càng tốt). *SER* là tỷ lệ ô ghi sai, thiếu hoặc thừa so với đáp án (càng thấp càng tốt).

| Kết quả | Trước | Sau |
|---|---|---|
| Thêm các bước kiểm tra vào cách chỉ rút thông tin, bộ "đổi người": F₁ | 66,1 % | **70,8 %** |
| Cùng bộ đó: SER | 45,4 % | **36,9 %** |
| Thông tin đã bị sửa nhưng vẫn còn trong bản nháp (bộ "tự sửa") | 11,48 % | **0,80 %** |
| Thông tin đúng bị bước kiểm căn cứ chặn nhầm | — | **0 trên 30.136** |
| Đổi chỗ bệnh nhân và người nhà: điểm ROUGE-1 | 1,0000 | 1,0000 (không phát hiện) |
| Cùng phép đổi đó: điểm riêng của dự án | — | giảm 0,1381 (phát hiện được) |
| **Tỷ lệ bỏ sót mệnh đề lâm sàng (30 ca phát triển, 304 mệnh đề)** | Qwen3-4B chưa train: **43,1%** (khoảng 37,6%–48,7%) | Qwen3-4B + adapter: **11,5%** (khoảng 8,4%–15,6%, 0 ca JSON lỗi) |
| Cùng phép đo, lần chạy 26/11/2026 | Adapter v1: **11,8%** (8,7%–16,0%) | Adapter v3: **14,1%** (10,7%–18,5%) — không tốt hơn v1 |

**Những kết quả không có lợi, ghi đúng như đo:**

- **Cách để mô hình viết thẳng bản nháp được điểm "ghi đúng người" cao hơn MediTrace** ở cả bốn bộ thử thách (ví dụ 0,939 so với 0,748 ở bộ "đổi người"). Một phần lý do là mô hình đó đã học cách viết của các bản mẫu và chép giống từng chữ ở 30–63 % số ca, trong khi điểm lại so với chính các bản mẫu đó. Phần còn lại là thật: nó ghi đúng người nhiều hơn (97,1 % so với 88,3 %). Vì vậy dự án **không** khẳng định MediTrace chính xác hơn cách viết thẳng. Điểm mạnh của MediTrace là **kiểm tra được từng dòng**, còn bản văn viết thẳng thì không.
- Một mô hình thương mại lớn ghi nhầm người **ít hơn** mô hình nhỏ của dự án (1,4 % so với 7,6 % ở bộ "tự sửa"). Dự án không giải quyết trọn vẹn việc gán đúng người; điểm khác biệt là chạy ngay trên máy và kiểm được từng dòng.
- Bước kiểm căn cứ giảm lỗi nghiêm trọng (dị ứng, thuốc, chẩn đoán) nhưng làm **tăng số thông tin bị bỏ sót** (ví dụ 4,5 % lên 7,7 % ở bộ "đổi người"). Đây là một sự đánh đổi có thật.
- Đáp án mô phỏng gần như chép nguyên văn từ lời thoại, nên kết quả **chỉ có hiệu lực trên dữ liệu mô phỏng**, chưa nói được điều gì về hội thoại thật.
- **Tỷ lệ lặp câu của bộ dữ liệu v2 dừng ở 47,37%** (câu $\ge 8$ từ lặp 42,19%), do bản chất tự nhiên của 5.000 ca khám lâm sàng chứa các phản xạ chào hỏi và xác nhận lịch sự của người bệnh ("của tôi ạ.", "vâng ạ."); dự án không cắt gọt gượng ép để làm đẹp chỉ số.

**Đo lớp cảnh báo bằng cách cấy lỗi (25–26/11/2026).** Chưa có nhãn của người, nên dự án đo lớp cảnh báo bằng cách lấy đáp án đúng làm bản ghi hoàn hảo, cố ý cấy **đúng một lỗi đã biết**, rồi xem lớp cảnh báo có bắt được không. Tiêu chí, ngưỡng và tập dữ liệu đã đăng ký trước trong `docs/dang-ky-truoc-bo-luat.md`.

| Đo trên 400 ca tập điều chỉnh | Trước khi sửa luật | Sau khi sửa luật |
|---|---|---|
| 16 loại lỗi cơ bản (đổi người, đảo phủ định, đổi số, xoá dị ứng…): tỷ lệ bắt đúng loại | 0,801 | **0,871** |
| 14 loại lỗi khó (lệch 1 đơn vị, đổi bên trái/phải, nhầm quá khứ/hiện tại, đính chính ngược…) | 0,682 | **0,889** |
| Số cảnh báo trên bản ghi **không có lỗi**, trung bình mỗi ca | 8,98 | **7,11** |

- Trên tập giữ kín (240 ca, chạy đúng một lần sau 5 vòng đầu): bắt đúng 0,871, báo nhầm 8,0 cảnh báo mỗi ca sạch.
- 4 luật của vòng 6 chỉ đo trên tập điều chỉnh, nên con số lỗi khó là số **lạc quan**.
- Lỗi do chương trình tạo ra đều đặn hơn lỗi thật của mô hình. Đây là phép đo khả năng bắt lỗi, **không phải** độ chính xác trên hồ sơ thật.
- Còn nhiều báo nhầm: trung bình 7 cảnh báo trên một bản ghi đúng hoàn toàn, chủ yếu là cảnh báo "có thể bỏ sót" ở mức cần xem.

Chi tiết: `docs/ket-qua/cay-loi.md`.

**Tốc độ.** Khoảng **3,5 phút** để tạo một bản nháp trên một card RTX 3060. Các bước theo luật mất dưới một giây.

---

## Cấu trúc thư mục

| Đường dẫn | Nội dung |
|---|---|
| `src/` | Toàn bộ phần xử lý bằng Python (xem bảng các bước ở trên). |
| `tests/` | **1.942 bài kiểm thử `pytest` qua**, 27 bỏ qua theo môi trường phần cứng (chạy lại ngày 26/11/2026). 3 bài hỏng khi chạy cả bộ trên Windows không bật UTF-8 hoặc khi máy bận (2 bài in tiếng Việt qua dòng lệnh, 1 bài đo độ trễ < 50 ms); bật `PYTHONUTF8=1` và chạy riêng thì qua. Phần `web/` có 96 bài kiểm thử TypeScript (giao diện + máy chủ, chạy bằng `npm test`), đều qua. |
| `tools/` | Các lệnh chạy thí nghiệm (`.ps1`, `.py`), đóng gói để chạy trên Kaggle, bộ đo tốc độ, công cụ cấy lỗi (`cay_loi.py`, `cay_loi_kho.py`). |
| `data/` | Chỉ có bảng tri thức thuốc, vân tay (mã băm) của các tập dữ liệu và manifest. Bản thân dữ liệu không nằm trong kho. |
| `kaggle-kernels/` | Mỗi thư mục là một lượt huấn luyện hoặc chạy mô hình trên Kaggle (điền tên tài khoản Kaggle của bạn trong `kernel-metadata.json` nếu muốn chạy lại). |
| `web/` | Giao diện web và máy chủ; xem `web/README.md`. |

Không có trong kho này: dữ liệu hội thoại, trọng số mô hình, kết quả chạy thô, tài liệu nội bộ. Dữ liệu mô phỏng sinh lại được bằng mã có sẵn.

## Chạy thử trên máy của bạn

Cần Python 3.11. Các thư viện chính: `torch 2.6`, `transformers ≥ 4.51`, `peft`, `bitsandbytes`, `lm-format-enforcer`, `pytest`. Tách giọng người nói cần một môi trường Python **riêng** (xem `src/audio/pyannote-moi-truong.txt`) và một khoá truy cập của Hugging Face.

```bash
# chạy các phép thử
python -m pytest tests/ -q

# sinh hội thoại mô phỏng
python -m src.bo_du_lieu.sinh_hoi_thoai_viet --so-ca 1000 --seed 42

# dịch vụ cho giao diện web (chỉ nghe trên máy này, địa chỉ 127.0.0.1)
python -m src.he_thong.dich_vu_http --cong 8765
#   --khong-mo-hinh            không nạp mô hình; chỉ phục vụ các ca đã chạy trước
#   --tach-nguoi-noi pyannote  bật tách giọng người nói (cần tệp khoá Hugging Face)

# giao diện web
cd web && npm install && npm run dev
```

Các khoá bí mật (khoá Hugging Face, khoá và địa chỉ của dịch vụ mô hình ngoài) được đọc lúc chạy từ tệp hoặc biến môi trường. Không có khoá nào nằm trong kho mã.

Biến môi trường cần đặt từ 26/11/2026 (đủ danh sách ở `web/.env.example`):

| Biến | Dùng để |
|---|---|
| `MEDITRACE_INTERNAL_TOKEN` | Khoá giữa máy chủ web và dịch vụ Python; đặt **cùng giá trị** ở hai bên. Dịch vụ Python tự sinh tệp `data/.meditrace_internal_token` nếu chưa đặt. Thiếu khoá thì mọi `/api` (trừ `/api/suc-khoe`) bị từ chối. |
| `MEDITRACE_WORM_KEY` | Khoá HMAC của nhật ký ký duyệt. Không đặt thì tự sinh vào `~/.meditrace/worm.key`; phải sao lưu cùng cơ sở dữ liệu. |
| `HOST`, `MEDITRACE_ALLOWED_HOSTS` | Chế độ dev chỉ nghe `127.0.0.1`; muốn mở qua đường hầm thì liệt kê tên miền. |
| `MEDITRACE_NGOAI_TOI_DA_PHUT`, `MEDITRACE_NGOAI_TOI_DA_NGAY` | Giới hạn số lần gọi mô hình ngoài mỗi người dùng (mặc định 10/phút, 200/ngày). |
| `MEDITRACE_TRO_LY_NGOAI` | Đường ra mô hình ngoài (AIBOX, **dịch vụ bên thứ ba**) **mặc định TẮT**. Quản trị bật trong giao diện; bác sĩ còn phải bật cho từng lần gửi. `tat` khóa hẳn (nên đặt ở bản cho phòng khám); `bat` chỉ mở khi quản trị chưa chọn. |

Bản chạy thử công khai (từ 26/11/2026, thay Vercel): máy chủ web và dịch vụ Python chạy trên một máy có GPU, ra ngoài qua đường hầm Cloudflare; một Cloudflare Worker (`trien-khai/cloudflare/`) giữ địa chỉ cố định https://meditrace-sentinel.meditrace.workers.dev và chuyển tiếp tới đường hầm hiện tại (đọc từ kho KV). Khi đường hầm đổi địa chỉ, máy chủ tự gửi địa chỉ mới lên Worker qua một đường riêng có mật mã chung (`cap-nhat-kv.ps1`), không cần khoá API Cloudflare. Trang chính không được trình duyệt giữ bản cũ; các tệp giao diện của bản trước được giữ lại khi triển khai, nên trang đang mở không bị lỗi khi máy chủ đổi bản.

## Quyền riêng tư và an toàn

- Chép lời và viết bản nháp đều chạy ngay trên máy, không gửi nội dung buổi khám ra ngoài.
- Công tắc "Mô hình ngoài" mặc định **tắt**; khi bật có cảnh báo rõ, mỗi lần dùng đều được ghi lại.
- Mật khẩu người dùng được băm trước khi lưu; người mới chỉ đăng ký được bằng mã mời dùng một lần.
- Mọi kết quả của mô hình ngoài đều gắn nhãn "chưa qua kiểm căn cứ"; bản nháp luôn ghi "chưa có bác sĩ duyệt".
- Mọi lời gọi mô hình ngoài đi qua **một cổng duy nhất**: kiểm công tắc quản trị ở máy chủ, giới hạn số lần, che tên, số điện thoại, ngày sinh, địa chỉ, mã bệnh nhân; còn sót dấu hiệu danh tính thì **từ chối gửi**. Đường gửi sang máy GPU từ xa cũng chặn như vậy.
- Ký duyệt: máy chủ tự tính mã băm và số liệu từ ca đã lưu, không tin số trình duyệt gửi lên; ca phải tồn tại và thuộc đúng bác sĩ.

Rà soát độc lập ngày 26/11/2026 (hai lượt, Python và web) tìm ra 9 lỗi nghiêm trọng, đã sửa cùng ngày, mỗi lỗi có phép thử hồi quy. Đáng kể nhất: khoá kiểm liều coi "5 mg" khớp "2.5 mg"; hiệu chỉnh liều dabigatran/enoxaparin dùng eGFR thay vì CrCl; thiếu tuổi thì ngầm lấy 50; chế độ dev cho tải cả tệp cơ sở dữ liệu không cần đăng nhập. Sau khi sửa, các số đo của lớp cảnh báo ở trên **không đổi** (chạy lại cùng ngày).

## Giới hạn đã biết

- Dữ liệu hoàn toàn là mô phỏng và đều đặn hơn lời nói thật. Chưa thử trên buổi khám thật.
- Chưa có nghiên cứu với bác sĩ: chưa đo thời gian tiết kiệm được, mức dễ dùng hay tác động an toàn. Bác sĩ được hỏi ý kiến cho biết thời gian ghi hồ sơ chủ yếu tốn ở việc hỏi bệnh chứ không phải ở việc gõ, nên phần mềm **không** hứa là "giảm thời gian làm hồ sơ".
- Cấu trúc bản nháp là 9 mục cố định, trong khi hồ sơ thật thay đổi theo lý do khám và chuyên khoa. Phần mềm chưa đọc kết quả xét nghiệm.
- Bước gom người còn một lỗi đã biết: khi mô hình ghi người được nhắc tới là "bố em", cụm này có thể bị gộp nhầm vào người bệnh.
- Nhận dạng tiếng nói sai tên thuốc ở gần như mọi câu trong thử nghiệm; tách giọng người nói chưa được chạy thử với mô hình thật.
- Các tính năng bổ sung 11/2026 (BHYT, chỉnh liều, đối chiếu lần khám, cờ đỏ) mới qua kiểm thử tự động, chưa được bác sĩ dùng thử. Bảng thuốc và mã bệnh chưa qua chuyên gia duyệt.
- Mô hình trích xuất bản v3 (huấn luyện trên bộ dữ liệu v2) bỏ sót **14,1%** trên 30 ca phát triển, so với 11,8% của bản v1 đo cùng lúc. Hai khoảng tin cậy chồng nhau nên chưa nói được bản nào hơn, nhưng v3 **không** cải thiện. 30 ca này thuộc bộ dữ liệu v1, khác phân phối với dữ liệu train của v3. Đã thử huấn luyện thêm v3 bằng DPO trên 407 cặp lỗi khó (`src/huan_luyen/huan_luyen_dpo.py`). Trên 140 cặp kiểm tra, độ chênh log-prob giữa câu đúng và câu sai tăng từ 20,5 lên 45,1 (tăng ở cả 13 loại lỗi), nhưng log-prob của câu đúng giảm từ −1,38 xuống −4,90 và chưa đo bỏ sót trên ca đầy đủ, nên **chưa** dùng bản DPO trong hệ thống. Chi tiết: [docs/ket-qua/dpo-v3.md](docs/ket-qua/dpo-v3.md).

## Công cụ AI đã dùng để làm dự án

Phần lớn mã nguồn do trợ lý lập trình AI viết **theo chỉ đạo, yêu cầu và sự kiểm tra của tác giả**. Tác giả chọn hướng làm, đặt yêu cầu, đọc và chạy lại các kết quả. Mô hình trong sản phẩm: Qwen3-4B (huấn luyện thêm bằng QLoRA), PhoWhisper, pyannote.audio.

| Công cụ | Đã làm gì |
|---|---|
| Claude Code (Anthropic) | Phần lớn mã Python và giao diện, phép đo, tài liệu; rà soát độc lập |
| Codex (OpenAI) | Một mô-đun âm thanh |
| Antigravity | Một số commit 25–27/11/2026, gồm sắp xếp lại `src/` thành 6 gói và mở rộng phương ngữ; đội đã rà và sửa 3 lỗi trong đó (`2fc4eba`) |
| ChatGPT | Ảnh minh họa |

Chưa từng đưa hồ sơ bệnh nhân thật vào công cụ AI nào: khi phát triển chỉ dùng dữ liệu mô phỏng và bộ dữ liệu công khai. Chi tiết việc AI hỗ trợ và chỗ đội tự sửa: [docs/minh-bach/](docs/minh-bach/).

**Ghi công cụ trong lịch sử sửa đổi.** Từ 28/11/2026 mọi commit kết thúc bằng một dòng `Cong-cu-AI: <claude_code|antigravity|codex|chatgpt|khong>`. Bật kiểm tự động bằng `git config core.hooksPath .githooks`. Bảng truy nguồn: [docs/minh-bach/truy-nguon-commit.md](docs/minh-bach/truy-nguon-commit.md) (sinh bằng `python -m tools.truy_nguon_commit`); commit cũ không ghi công cụ được để `chua_xac_dinh`, không đoán.

---

### English summary

MediTrace Sentinel turns a Vietnamese doctor–patient conversation into a **draft** clinical note in which every line links back to the exact turn it came from. Only the first step uses an AI model (Qwen3-4B, fine-tuned, running locally); linking people, tracking corrections, evidence checks and routing are readable rules. All data is synthetic; the software does not diagnose or prescribe. Try it at https://meditrace-sentinel.meditrace.workers.dev (demo account in the submission notes; click "Xem thử với ca mẫu" for an instant sample case).
