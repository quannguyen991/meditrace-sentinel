# Bộ ca bẫy viết tay (28/11/2026)

16 cuộc khám mô phỏng giữa bác sĩ và bệnh nhân hoặc người nhà. Mỗi ca cài sẵn chỗ dễ ghi sai, dùng để kiểm thử MediTrace.

**Nguồn:** Claude viết theo yêu cầu tác giả. **Chỉ dùng để đo, không dùng để huấn luyện.** Chưa có bác sĩ duyệt. Không có dữ liệu người thật. Âm thanh là giọng máy VieNeu-TTS (lõi của Zoo Voice), không phải giọng người.

## Các loại bẫy

| Nhóm | Ví dụ trong bộ |
|---|---|
| Đổi chủ thể | mẹ đưa con khám rồi kể mình nôn (02); "đấy là chồng em mổ" (03); người kể tự nói mình bị tiểu đường (04); vợ đang điều trị lao (15); "thầy cháu" là bố, không phải thầy thuốc (16) |
| Đổi trạng thái | thuốc cũ đã ngừng, thuốc mới thay (01); gối hết sưng (04); hết sốt (06, 10); kali tạm ngừng (07); bỏ thuốc lá (05); lao cũ đã khỏi (09) |
| Đính chính | "một tuần, à không, mười ngày" (01); đổi bên trái/phải (03, 10); đổi tên thuốc dị ứng (11); **đính chính ngược**: sửa rồi quay lại số đầu (11) |
| Khẳng định / phủ định | "Không, à có" (01); phủ định trong chuỗi (03, 12); phủ định kép "không phải là không đều", "hổng phải hổng sốt" (03, 15); phủ định lược "còn lại không ạ" (12) |
| Giả định / kế hoạch | "Nếu … thì vào viện" (hầu hết các ca) |
| Câu trả lời mơ hồ | "Có ạ" cho câu hỏi gộp ba ý; câu hỏi dị ứng bị lờ đi (06) |
| Số và đơn vị | 12,5 với 1,25; 3 g với 3 mg; ba năm với ba tháng; MMSE (05, 08, 11, 12) |
| Hai người kể ngược nhau | con gái nói bố hay quên và uống rượu, bố chối (08) |
| **Phương ngữ** | Huế: rứa, răng, mô, chừ, mạ (04) · Nam Bộ: hổng, bả, ổng, bữa giờ, ói, té (13, 15) · Nghệ Tĩnh: nỏ, chi, mô, o, eng (14) · Bắc quê: u, thầy (16) |

Mỗi ca giữ một vùng nói từ đầu đến cuối. Các từ địa phương là từ thông dụng, nhưng vẫn cần người nói vùng đó đọc lại trước khi dùng kết quả để kết luận.

## Tệp

- `ca_bay.py`: kịch bản, đáp án và các bản ghi sai, viết tay.
- `sinh.py` → `ra/ca_bay.jsonl`: cùng định dạng với `data/thach_thuc_v2`, có thêm `ban_sai` và `phuong_ngu`. Bước này kiểm mọi trích dẫn có nằm nguyên văn trong lượt nói.
- `do.py`: chạy lớp cảnh báo (`src/canh_bao`) trên bản sạch và từng bản sai, tính bắt đúng và báo nhầm. `--loi-thoai` thay lời thoại gốc bằng bản chép âm.
- `doc.py`: đọc thành `ra/am_thanh/<id>.wav` (16 kHz) kèm mốc từng lượt. Chạy bằng `D:\venv-vieneu`, mỗi vùng dùng giọng của vùng đó.
- `nghe.py`: chép âm bằng PhoWhisper của MediTrace, giả định tách người nói hoàn hảo, rồi đếm từ then chốt (phủ định, trái/phải, số, tên thuốc) bị mất.

```
D:\khkt-venv-lap\Scripts\python -X utf8 thi-nghiem\bo-bay-tay\sinh.py
D:\khkt-venv-lap\Scripts\python -X utf8 thi-nghiem\bo-bay-tay\do.py
D:\venv-vieneu\Scripts\python -X utf8 thi-nghiem\bo-bay-tay\doc.py
D:\khkt-venv-lap\Scripts\python -X utf8 thi-nghiem\bo-bay-tay\nghe.py
D:\khkt-venv-lap\Scripts\python -X utf8 thi-nghiem\bo-bay-tay\do.py --loi-thoai thi-nghiem\bo-bay-tay\ra\loi_thoai_asr.jsonl --ra thi-nghiem\bo-bay-tay\ra\ket_qua_luat_asr.json
```

## Giới hạn

- Giọng Trung của VieNeu không phải giọng Nghệ, nên ca 14 chỉ có từ Nghệ, không có ngữ điệu Nghệ.
- Bản sạch là đáp án, tức là coi khâu trích là hoàn hảo. Chỉ đo được lớp cảnh báo, chưa đo mô hình Qwen3-4B. Muốn đo cả mô hình thì đưa `ra/am_thanh/*.wav` vào app trên HoaiĐức.
- Đường dùng thuốc trong `b1_cau_truc_menh_de.DUONG_DUNG` không có "tiêm", nên insulin trong ca 05 ghi `duong_dung = None`.
