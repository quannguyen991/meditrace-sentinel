# MediTrace Sentinel

**Phần mềm dựng bản nháp hồ sơ khám bệnh từ lời nói của buổi khám bằng tiếng Việt, trong đó mỗi dòng đều chỉ ra được câu nói làm căn cứ.**

> **Lưu ý quan trọng.** MediTrace chỉ tạo **bản nháp để bác sĩ xem lại**. Phần mềm không chẩn đoán bệnh, không kê đơn, không thay quyết định của bác sĩ, và bản nháp không phải hồ sơ bệnh án chính thức. Toàn bộ dữ liệu dùng để xây dựng và đo kết quả là hội thoại **mô phỏng** do chương trình tạo ra. Không dùng hồ sơ, bản ghi âm hay thông tin của bệnh nhân thật.

---

## Dành cho ban người đánh giá: xem thử trong 3 phút

1. Mở **https://meditrace-sentinel.vercel.app** và đăng nhập bằng tài khoản dùng thử ghi trong hồ sơ dự thi. (Phần mềm yêu cầu tài khoản để bảo vệ dữ liệu của người dùng.)
2. Ở **Trang chủ**, bấm nút **"Xem thử với ca mẫu"**. Phần mềm mở ngay một ca khám mô phỏng đã được xử lý trước, có sẵn bản nháp, không phải chờ.
3. Vào **"Bằng chứng hội thoại"** (màn **"Duyệt từng mệnh đề"**). Bên trái là lời thoại, bên phải là từng thông tin được rút ra. Các đường nối chỉ ra thông tin nào lấy từ câu nói nào. Những thông tin đáng ngờ nằm trong ô vàng kèm lý do.
4. Thử **ghi âm**: bấm "Bắt đầu ghi âm" và nói vài câu. Dải trên cùng có các vạch nhảy theo giọng để cho biết micrô đang thu.

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
| **1. Rút thông tin** | Đọc lời thoại và liệt kê từng thông tin lâm sàng, gọi là **mệnh đề**. Mỗi mệnh đề ghi: nội dung; thông tin này **nói về ai**; ai nói; chắc chắn hay chỉ nghi ngờ; có phủ định không ("không sốt"); là việc đã xảy ra, hay chỉ là giả định hoặc kế hoạch; thời gian; số thứ tự lượt nói làm căn cứ; và **câu trích nguyên văn**. | **Mô hình AI** (Qwen3-4B, chạy ngay trên máy) | `src/nhanh.py`, `src/phat_bieu.py` |
| **2. Gom người** | Phân biệt **người nói** với **người được nói đến**. Ví dụ người con kể về bố thì thông tin thuộc về bố, không thuộc về người bệnh. | Chương trình theo luật cố định | `src/thuc_the.py` |
| **3. Cập nhật trạng thái** | Khi người nói **tự sửa** ("một tuần… à không, mười ngày") thì bản cũ được đánh dấu "bị thay thế", **không xoá**. Khi hai thông tin theo thời gian đều đúng ("hôm qua đau, hôm nay hết") thì giữ cả hai. Khi hai người nói trái nhau mà chưa ai xác nhận thì đánh dấu **mâu thuẫn**. | Chương trình theo luật | `src/cap_nhat.py` |
| **4. Kiểm căn cứ** | Đối chiếu từng thông tin với đúng lượt nói được dẫn. Sáu phép kiểm: (1) câu trích có thật trong lượt đó không; (2) nội dung có khớp không; (3) từ chỉ người có khớp với người được nhắc tới không; (4) mức chắc chắn có bị nâng lên không; (5) thời gian có xuất hiện trong lượt đó không; (6) liều thuốc có xuất hiện trong lượt đó không. | Chương trình theo luật | `src/khoa_bang_chung.py` |
| **5. Xếp chỗ** | Mỗi thông tin vào một trong ba chỗ: **thân bản nháp**; mục **"Cần xác nhận"** (kèm lý do, để bác sĩ xem lại); hoặc **bị loại** (vẫn lưu vết). Sau đó bản nháp được viết ra theo mẫu câu cố định. | Chương trình theo luật | `src/cong_rui_ro.py`, `src/canh_bao/` |
| *Phụ* | Gợi ý tối đa 3 câu hỏi để bác sĩ hỏi lại người bệnh. | Chương trình | `src/hoi_lai.py` |

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

| Thành phần | Mô tả |
|---|---|
| **Xử lý bằng Python** (`src/`) | Bộ tạo dữ liệu mô phỏng, mô hình rút thông tin, các bước theo luật, bộ chấm điểm, dịch vụ chạy trên máy. |
| **Giao diện web** (`web/`) | Viết bằng React. Bác sĩ **giữ, sửa hoặc bỏ** từng dòng của bản nháp; mỗi dòng nối về lượt nói gốc. Có tài khoản đăng nhập bằng mã mời; ca khám lưu trong cơ sở dữ liệu SQLite, tách riêng cho từng người dùng. |
| **Đầu vào âm thanh** (`src/audio/`) | Chép lời bằng **PhoWhisper** (mô hình nhận dạng tiếng nói tiếng Việt) chạy ngay trên máy. Có thể tách giọng từng người nói bằng pyannote; khi đó bác sĩ chọn vai (bác sĩ, bệnh nhân, người nhà) cho từng giọng. |
| **Dịch vụ mô hình ngoài** (tuỳ chọn) | Chỉ dùng cho việc phụ như hỏi đáp về ca khám hoặc tra tài liệu. **Mặc định tắt**, chỉ chạy khi người dùng bật công tắc, có cảnh báo dữ liệu sẽ đi đâu, và **không bao giờ** dùng để viết bản nháp chính. Kết quả của phần này được ghi rõ là "chưa qua kiểm căn cứ". |

Trang chủ của phần mềm có bảng **"Ai xử lý phần nào"** nói rõ phần nào chạy ngay trên máy và phần nào có thể gửi ra ngoài.

---

## Kết quả đo

**Dữ liệu.** 5.000 hội thoại mô phỏng sinh ra từ 100 khuôn ca bệnh, chia theo khuôn để mô hình không nhìn thấy trước bài kiểm tra. Ngoài ra có 300 ca "thử thách" tạo theo cặp, mỗi cặp chỉ khác nhau một điểm: đổi người mang dị ứng, người nói tự sửa, lỗi khi chép giọng nói, và phương ngữ.

**Cách đọc các chỉ số.** *F₁* là điểm gộp giữa "ghi đúng" và "ghi đủ" (càng cao càng tốt). *SER* là tỷ lệ ô ghi sai, thiếu hoặc thừa so với đáp án (càng thấp càng tốt).

| Kết quả | Trước | Sau |
|---|---|---|
| Thêm các bước kiểm tra vào cách chỉ rút thông tin, bộ "đổi người": F₁ | 66,1 % | **70,8 %** |
| Cùng bộ đó: SER | 45,4 % | **36,9 %** |
| Thông tin đã bị sửa nhưng vẫn còn trong bản nháp (bộ "tự sửa") | 11,48 % | **0,80 %** |
| Thông tin đúng bị bước kiểm căn cứ chặn nhầm | — | **0 trên 30.136** |
| Đổi chỗ bệnh nhân và người nhà: điểm ROUGE-1 | 1,0000 | 1,0000 (không phát hiện) |
| Cùng phép đổi đó: điểm riêng của dự án | — | giảm 0,1381 (phát hiện được) |

**Những kết quả không có lợi, ghi đúng như đo:**

- **Cách để mô hình viết thẳng bản nháp được điểm "ghi đúng người" cao hơn MediTrace** ở cả bốn bộ thử thách (ví dụ 0,939 so với 0,748 ở bộ "đổi người"). Một phần lý do là mô hình đó đã học cách viết của các bản mẫu và chép giống từng chữ ở 30–63 % số ca, trong khi điểm lại so với chính các bản mẫu đó. Phần còn lại là thật: nó ghi đúng người nhiều hơn (97,1 % so với 88,3 %). Vì vậy dự án **không** khẳng định MediTrace chính xác hơn cách viết thẳng. Điểm mạnh của MediTrace là **kiểm tra được từng dòng**, còn bản văn viết thẳng thì không.
- Một mô hình thương mại lớn ghi nhầm người **ít hơn** mô hình nhỏ của dự án (1,4 % so với 7,6 % ở bộ "tự sửa"). Dự án không giải quyết trọn vẹn việc gán đúng người; điểm khác biệt là chạy ngay trên máy và kiểm được từng dòng.
- Bước kiểm căn cứ giảm lỗi nghiêm trọng (dị ứng, thuốc, chẩn đoán) nhưng làm **tăng số thông tin bị bỏ sót** (ví dụ 4,5 % lên 7,7 % ở bộ "đổi người"). Đây là một sự đánh đổi có thật.
- Đáp án mô phỏng gần như chép nguyên văn từ lời thoại, nên kết quả **chỉ có hiệu lực trên dữ liệu mô phỏng**, chưa nói được điều gì về hội thoại thật.

**Tốc độ.** Khoảng **3,5 phút** để tạo một bản nháp trên một card RTX 3060. Các bước theo luật mất dưới một giây.

---

## Cấu trúc thư mục

| Đường dẫn | Nội dung |
|---|---|
| `src/` | Toàn bộ phần xử lý bằng Python (xem bảng các bước ở trên). |
| `tests/` | Hơn 1.200 phép thử tự động (`pytest`). |
| `tools/` | Các lệnh chạy thí nghiệm (`.ps1`, `.py`), đóng gói để chạy trên Kaggle, bộ đo tốc độ. |
| `kaggle-kernels/` | Mỗi thư mục là một lượt huấn luyện hoặc chạy mô hình trên Kaggle (điền tên tài khoản Kaggle của bạn trong `kernel-metadata.json` nếu muốn chạy lại). |
| `web/` | Giao diện web và máy chủ; xem `web/README.md`. |

Không có trong kho này: dữ liệu, trọng số mô hình, kết quả chạy thô, tài liệu nội bộ. Dữ liệu mô phỏng sinh lại được bằng mã có sẵn.

## Chạy thử trên máy của bạn

Cần Python 3.11. Các thư viện chính: `torch 2.6`, `transformers ≥ 4.51`, `peft`, `bitsandbytes`, `lm-format-enforcer`, `pytest`. Tách giọng người nói cần một môi trường Python **riêng** (xem `src/audio/pyannote-moi-truong.txt`) và một khoá truy cập của Hugging Face.

```bash
# chạy các phép thử
python -m pytest tests/ -q

# sinh hội thoại mô phỏng
python -m src.sinh_hoi_thoai_viet --so-ca 1000 --seed 42

# dịch vụ cho giao diện web (chỉ nghe trên máy này, địa chỉ 127.0.0.1)
python -m src.dich_vu --cong 8765
#   --khong-mo-hinh            không nạp mô hình; chỉ phục vụ các ca đã chạy trước
#   --tach-nguoi-noi pyannote  bật tách giọng người nói (cần tệp khoá Hugging Face)

# giao diện web
cd web && npm install && npm run dev
```

Các khoá bí mật (khoá Hugging Face, khoá và địa chỉ của dịch vụ mô hình ngoài) được đọc lúc chạy từ tệp hoặc biến môi trường. Không có khoá nào nằm trong kho mã.

## Quyền riêng tư và an toàn

- Chép lời và viết bản nháp đều chạy ngay trên máy, không gửi nội dung buổi khám ra ngoài.
- Công tắc "Mô hình ngoài" mặc định **tắt**; khi bật có cảnh báo rõ, mỗi lần dùng đều được ghi lại.
- Mật khẩu người dùng được băm trước khi lưu; người mới chỉ đăng ký được bằng mã mời dùng một lần.
- Mọi kết quả của mô hình ngoài đều gắn nhãn "chưa qua kiểm căn cứ"; bản nháp luôn ghi "chưa có bác sĩ duyệt".

## Giới hạn đã biết

- Dữ liệu hoàn toàn là mô phỏng và đều đặn hơn lời nói thật. Chưa thử trên buổi khám thật.
- Chưa có nghiên cứu với bác sĩ: chưa đo thời gian tiết kiệm được, mức dễ dùng hay tác động an toàn. Bác sĩ được hỏi ý kiến cho biết thời gian ghi hồ sơ chủ yếu tốn ở việc hỏi bệnh chứ không phải ở việc gõ, nên phần mềm **không** hứa là "giảm thời gian làm hồ sơ".
- Cấu trúc bản nháp là 9 mục cố định, trong khi hồ sơ thật thay đổi theo lý do khám và chuyên khoa. Phần mềm chưa đọc kết quả xét nghiệm.
- Bước gom người còn một lỗi đã biết: khi mô hình ghi người được nhắc tới là "bố em", cụm này có thể bị gộp nhầm vào người bệnh.
- Nhận dạng tiếng nói sai tên thuốc ở gần như mọi câu trong thử nghiệm; tách giọng người nói chưa được chạy thử với mô hình thật.

## Công cụ AI đã dùng để làm dự án

Phần lớn mã nguồn do trợ lý lập trình AI (Claude Code của Anthropic, và Codex cho một mô-đun âm thanh) viết **theo chỉ đạo, yêu cầu và sự kiểm tra của tác giả**. Tác giả chọn hướng làm, đặt yêu cầu, đọc và chạy lại các kết quả. Mô hình trong sản phẩm: Qwen3-4B (huấn luyện thêm bằng QLoRA), PhoWhisper, pyannote.audio.

---

### English summary

MediTrace Sentinel turns a Vietnamese doctor–patient conversation into a **draft** clinical note in which every line links back to the exact turn it came from. Only the first step uses an AI model (Qwen3-4B, fine-tuned, running locally); linking people, tracking corrections, evidence checks and routing are readable rules. All data is synthetic; the software does not diagnose or prescribe. Try it at https://meditrace-sentinel.vercel.app (demo account in the submission notes; click "Xem thử với ca mẫu" for an instant sample case).
