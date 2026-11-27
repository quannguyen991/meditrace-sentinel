# Âm thanh — `src/audio/`

Biến ghi âm buổi khám thành lời thoại theo lượt. Chép lời và tách người nói đều chạy tại chỗ.

| Tệp | Làm gì |
|---|---|
| [pipeline.py](pipeline.py) | Điều phối một phiên âm thanh từ ghi âm đến lời thoại chờ duyệt, qua các bước chuyển định dạng, chép, tách người nói, căn khớp. |
| [asr/phowhisper_provider.py](asr/phowhisper_provider.py) | Chép lời tiếng Việt bằng PhoWhisper chạy tại chỗ, là bộ chép chính của hệ thống. |
| [asr/faster_whisper_provider.py](asr/faster_whisper_provider.py) | Chép lời bằng faster-whisper làm mốc so sánh với bộ chép chính. |
| [asr/registry.py](asr/registry.py) | Chọn bộ chép lời theo tên trong cấu hình để đổi nhà cung cấp mà không sửa mã. |
| [asr/critical_tokens.py](asr/critical_tokens.py) | Lấy ra các từ lâm sàng dễ sai nghĩa (thuốc, liều, phủ định, ai) từ bản chép để so hai bản chép với nhau. |
| [asr/disagreement.py](asr/disagreement.py) | Chạy so hai bộ chép lời và chọn ra những đoạn hai bên bất đồng ở từ quan trọng để người duyệt xem kỹ. |
| [asr/bench_metrics.py](asr/bench_metrics.py) | Đo chất lượng chép lời bằng tỷ lệ sai từ và tỷ lệ sai từ khoá lâm sàng để so các bộ chép. |
| [pyannote_provider.py](pyannote_provider.py) | Tách người nói bằng pyannote bằng cách gọi tiến trình con trong môi trường Python riêng, có giới hạn bộ nhớ. |
| [alignment.py](alignment.py) | Gán người nói cho từng đoạn chép lời bằng cách đối chiếu mốc thời gian, không đổi chữ đã chép. |
| [adapter.py](adapter.py) | Đổi bản chép lời đã được duyệt sang dạng hội thoại mà đường ống dựng bản nháp đọc được. |
| [preprocessing.py](preprocessing.py) | Đưa âm thanh về WAV 16 kHz mono để bộ chép dùng, vẫn giữ nguyên tệp gốc. |
| [storage.py](storage.py) | Lưu phiên âm thanh vào đĩa tại chỗ, bền vững qua các lần chạy, kèm nhật ký sự kiện để kiểm toán. |
| [api.py](api.py) | Mở máy chủ HTTP nhỏ để tải ghi âm lên, xử lý và cho bác sĩ duyệt, sửa lời thoại trên trình duyệt. |
| [sim2real_v2.py](sim2real_v2.py) | Mô phỏng nhiễu, vọng, mất gói trên chữ để thử độ bền chép lời với bộ dữ liệu v2; là mô phỏng, không phải đo ASR thật. |

Bản đồ toàn dự án: [../../BAN_DO_MA_NGUON.md](../../BAN_DO_MA_NGUON.md)
