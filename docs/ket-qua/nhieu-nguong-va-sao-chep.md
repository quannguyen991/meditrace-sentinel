# Nhiều ngưỡng và mức sao chép

F1 ghép mệnh đề cho biết mức khớp từ giữa mệnh đề trích và đáp án; ngưỡng càng thấp càng dễ ghép. Độ phủ là tỷ lệ từ trong bản thảo nằm trong các mảnh liên tiếp có ở hội thoại, còn mật độ tăng khi các mảnh đó dài hơn. F1 được gộp theo số mệnh đề, còn độ phủ và mật độ là trung bình theo ca; hai chỉ số sao chép tính trên toàn bộ bản thảo, kể cả tiêu đề. Đây là các tập phát triển từ dữ liệu tổng hợp, nên kết quả không chứng minh chất lượng hay mức sao chép trên hội thoại thực tế.

| Hệ thống | Tập | Số ca | F1 0.4 | F1 0.5 | F1 0.6 | F1 0.7 | Độ phủ | Mật độ |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| C_khoa | thach_thuc_dinh_chinh_phat_trien | 60/60 | 0.980 | 0.976 | 0.971 | 0.955 | 0.706 | 3.910 |
| C_khoa | thach_thuc_doi_chu_the_phat_trien | 80/80 | 0.963 | 0.961 | 0.946 | 0.924 | 0.644 | 3.259 |
| C_khoa | thach_thuc_nhieu_asr_phat_trien | 80/80 | 0.878 | 0.860 | 0.788 | 0.706 | 0.669 | 3.846 |
| C_khoa | thach_thuc_phuong_ngu_phat_trien | 80/80 | 0.970 | 0.969 | 0.965 | 0.943 | 0.695 | 3.806 |
