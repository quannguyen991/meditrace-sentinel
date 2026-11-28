# Giải thích cấu trúc dự án MediTrace Sentinel

> Tài liệu này giải thích **dự án gồm những phần nào, mỗi phần làm gì và nối với nhau ra sao**.
> Muốn tra nhanh "câu hỏi nào → mở tệp nào" thì xem [`BAN_DO_MA_NGUON.md`](../BAN_DO_MA_NGUON.md).
> Bộ hỏi – đáp chuẩn bị cho Ban Giám khảo: [`HOI_DAP_BGK.md`](HOI_DAP_BGK.md). Số liệu bối cảnh có nguồn (kiệt sức, quá tải, an toàn người bệnh): mục 1.1 của [`GIAI_THICH_DU_AN_MEDITRACE_SENTINEL.md`](../GIAI_THICH_DU_AN_MEDITRACE_SENTINEL.md).
> Cập nhật: 28/11/2026.

---

## Mục lục

1. [Dự án làm gì (một phút)](#1-dự-án-làm-gì-một-phút)
2. [Bức tranh tổng thể](#2-bức-tranh-tổng-thể) — kèm kiến trúc lai, 4 trụ cột, phần nào chạy thật
3. [Cây thư mục](#3-cây-thư-mục)
4. [Đơn vị dữ liệu trung tâm: mệnh đề](#4-đơn-vị-dữ-liệu-trung-tâm-mệnh-đề)
5. [Đường ống dựng bản nháp, từng bước](#5-đường-ống-dựng-bản-nháp-từng-bước)
6. [Theo chân một ca khám thật](#6-theo-chân-một-ca-khám-thật)
7. [Lớp cảnh báo](#7-lớp-cảnh-báo)
8. [Âm thanh](#8-âm-thanh)
9. [Giao diện web và ký duyệt](#9-giao-diện-web-và-ký-duyệt)
10. [Hệ thống, an toàn và minh bạch](#10-hệ-thống-an-toàn-và-minh-bạch)
11. [Dữ liệu](#11-dữ-liệu)
12. [Huấn luyện mô hình](#12-huấn-luyện-mô-hình)
13. [Đo lường](#13-đo-lường)
14. [Công cụ lâm sàng phụ trợ](#14-công-cụ-lâm-sàng-phụ-trợ)
15. [Các nhánh so sánh A–E](#15-các-nhánh-so-sánh-ae)
16. [Cách chạy](#16-cách-chạy)
17. [Số liệu chính và giới hạn](#17-số-liệu-chính-và-giới-hạn)
18. [Cách đọc một tệp mã nguồn](#18-cách-đọc-một-tệp-mã-nguồn)

---

## 1. Dự án làm gì (một phút)

MediTrace nghe cuộc khám bằng tiếng Việt giữa bác sĩ, người bệnh và người nhà, rồi dựng **bản nháp hồ sơ khám bệnh**. Bản nháp có ba đặc điểm:

- **Mỗi dòng đều có bằng chứng.** Bấm vào dòng nào cũng thấy câu nói gốc, kèm nút nghe lại đoạn ghi âm.
- **Thông tin chưa chắc không bị đoán.** Nó được đưa vào mục **"Cần xác nhận"**, kèm lý do bằng lời dễ hiểu.
- **Bác sĩ quyết định cuối cùng.** Còn mục "Cần xác nhận" thì chưa ký được hồ sơ.

**Nguyên tắc thiết kế cốt lõi:**

> **AI chỉ đọc hiểu. Chương trình kiểm từng dòng. Bác sĩ quyết định.**

Trong cả hệ thống, **chỉ có một bước dùng mô hình AI** (bước b1: rút thông tin từ hội thoại). Mọi bước khác là quy tắc cố định: đọc được, kiểm được, giải thích được.

---

## 2. Bức tranh tổng thể

```
  🎤 Cuộc khám (lời nói hoặc tệp ghi âm)
        │
        ▼
  ┌───────────────────────────────┐
  │ src/audio/                    │  Chép lời (PhoWhisper) + tách người nói
  │ chạy tại máy, không gửi ra ngoài│  → bác sĩ duyệt vai người nói
  └───────────────────────────────┘
        │  lời thoại theo lượt: [bác sĩ] … [mẹ] … [bé] …
        ▼
  ┌───────────────────────────────┐
  │ src/duong_ong/  (b0 → b6)     │  b0 chuẩn hoá
  │ ĐƯỜNG ỐNG DỰNG BẢN NHÁP       │  b1 🤖 AI rút mệnh đề
  │                               │  b2 gom người · b3 cập nhật trạng thái
  │                               │  b4 kiểm căn cứ K1–K7
  │                               │  b5 xếp chỗ + viết bản nháp (chính sách C)
  │                               │  b6 gợi ý hỏi lại
  └───────────────────────────────┘
        │  ra: BẢNG MỆNH ĐỀ + bản nháp
        ▼
  ┌───────────────────────────────┐
  │ src/canh_bao/                 │  Vào: bảng mệnh đề + lời thoại gốc (không đọc văn bản nháp)
  │ LỚP CẢNH BÁO                  │  Bắt lỗi khó thấy, rồi áp CHÍNH SÁCH D: kéo thêm
  └───────────────────────────────┘  dòng đáng ngờ sang "Cần xác nhận"
        │  bản nháp + mục "Cần xác nhận" (giao diện ưu tiên kết quả chính sách D)
        ▼
  ┌───────────────────────────────┐
  │ src/he_thong/dich_vu_http.py  │  Dịch vụ HTTP tại chỗ
  │ web/                          │  Giao diện bác sĩ: duyệt, sửa, ký
  └───────────────────────────────┘
        │
        ▼
  ✍️ Bác sĩ ký → nhật ký WORM (chỉ ghi thêm, nối chuỗi băm)

  ── Phía sau, bác sĩ không nhìn thấy ─────────────────────────────
  src/bo_du_lieu/   sinh dữ liệu luyện tập và kiểm tra
  src/huan_luyen/   dạy mô hình AI cho bước b1
  src/do_luong/     chấm điểm, sinh mọi con số trong báo cáo
  src/cong_cu_lam_sang/  công cụ phụ: thuốc, BHYT, xét nghiệm, giấy tờ
```

### 2.1. Kiến trúc lai nơ-ron – ký hiệu

MediTrace ghép **hai kiểu trí tuệ**, mỗi kiểu làm phần việc mình giỏi:

| | **Nơ-ron** (neural) | **Ký hiệu** (symbolic) |
|---|---|---|
| Là gì | AI tự học từ dữ liệu: mô hình Qwen3-4B | Luật do người viết, dạng "nếu… thì…" |
| Giỏi | **Hiểu** lời nói lộn xộn: nói trống không, phương ngữ, câu lủng củng | **Bảo đảm**: kiểm chính xác, mọi lần như nhau, giải thích được |
| Kém | Có thể bịa; khó giải thích vì sao | Cứng nhắc, không hiểu cách nói ngoài luật |
| Trong MediTrace | Chỉ bước **b1** (rút mệnh đề) | b0, b2–b6, lớp cảnh báo |

Hình dung: một **thư ký nhanh nhẹn** (AI) ghi lại thông tin, một **người kiểm theo checklist** (luật) soát từng dòng với lời gốc, rồi **bác sĩ** ký. Mỗi lần chặn đều có lý do bằng chữ, nên khi có sự cố y khoa thì truy được vì sao một dòng vào hồ sơ.

### 2.2. Lõi và vòng ngoài

```
┌────────────────────── VÒNG NGOÀI (tiện ích, chỉ gợi ý, chưa đo như lõi) ──────────────────────┐
│   Âm thanh · Công cụ lâm sàng (thuốc, xét nghiệm, BHYT, FHIR) · Tra cứu y khoa · Triển khai    │
│   ┌──────────────────────── LÕI (đóng góp chính, đã đo) ─────────────────────────┐            │
│   │ 1. Không bịa   2. Đúng người, đúng lúc   3. Không chắc thì hỏi   4. Đo trung thực │       │
│   └──────────────────────────────────────────────────────────────────────────────┘            │
│                     Xuyên suốt: xử lý tại máy, che danh tính                                    │
└────────────────────────────────────────────────────────────────────────────────────────────────┘
```

Mọi con số đo được (bỏ sót, chặn lỗi nguy hiểm, đính chính) đều thuộc **lõi**. Vòng ngoài chưa được đánh giá theo cùng tiêu chuẩn.

### 2.3. Bốn trụ cột của lõi và nơi chúng chạy

🟢 = chạy trong lúc khám · 🔵 = chạy trước, ngoài luồng khám

| Trụ cột | Câu hỏi | Phần việc chính | Tệp | Khi nào |
|---|---|---|---|---|
| **1. Không bịa** | Thư ký có bịa không? | AI chỉ điền phiếu (mệnh đề); ép đúng khung JSON; bắt buộc câu trích; kiểm K1–K7; ghép bản nháp bằng mẫu câu | `b1_cau_truc_menh_de`, `_ep_json` trong `huan_luyen/chon_mo_hinh_bakeoff`, `b4_kiem_can_cu`, `b5_viet_ban_nhap` | 🟢 |
| | | Dạy AI chép đúng chữ | `huan_luyen/huan_luyen_sft` | 🔵 |
| **2. Đúng người, đúng lúc** | Có ghi đúng người và lấy lời sửa sau cùng không? | Chốt duyệt vai người nói; tách ai nói / nói về ai; đính chính – diễn biến – mâu thuẫn; K3, K7 | `he_thong/dich_vu_http` (lỗi 409), `b2_gom_nguoi_thuc_the`, `b3_cap_nhat_trang_thai`, `b4_kiem_can_cu` | 🟢 |
| **3. Không chắc thì hỏi** | Gặp chỗ không chắc thì làm gì? | Chấm rủi ro; lớp cảnh báo + chính sách D; gợi ý ≤ 3 câu hỏi; nghe lại; khoá ký hai tầng; nhật ký WORM | `b5_xep_cho_cong_rui_ro`, `canh_bao/gop`, `b6_goi_y_hoi_lai`, `web/src/lib/kyDuyet.ts`, `web/may-chu/routes/sign-off.ts`, `web/may-chu/worm.ts` | 🟢 |
| **4. Đo trung thực** | Làm sao biết hệ thống tốt? | Dữ liệu 657 khuôn, chia theo khuôn; thước đo quy gán; cấy lỗi; so các nhánh | `bo_du_lieu/`, `do_luong/`, `docs/ket-qua/` | 🔵 |
| Xuyên suốt | Có lộ dữ liệu bệnh nhân không? | Chép lời tại máy; khử định danh; che log; AI ngoài mặc định tắt | `audio/`, `he_thong/khu_dinh_danh`, `he_thong/che_log`, `web/may-chu/routes/llm-ngoai.ts` | 🟢 |

### 2.4. Phần nào chạy thật, phần nào là thử nghiệm

Đường ống **thiết kế 8 bước (b0–b7)**. Dịch vụ chạy nhánh **`C_khoa_hoi`**, gồm **7 bước b0–b6**; màn hình duyệt do giao diện web làm thay b7.

| Trong luồng khám thật | Chỉ dùng ở nhánh thử nghiệm / đo đạc / chạy riêng |
|---|---|
| `b0_chuan_hoa_phuong_ngu`, `b0_cat_doan_van` | `b1_ep_dau_ra_json` (ngữ pháp GBNF, cây chuỗi con — chưa nối vào lúc sinh) |
| `b1_cau_truc_menh_de`, `b1_vi_du_mau_loi_nhac` | `b1_quet_lai_ve` (quét lại vế bị sót — tuỳ chọn `quet_lai`, **mặc định tắt**) |
| `b2_gom_nguoi_thuc_the` | `b2_bu_chu_ngu_tinh_luoc` (chỉ nhánh `C_khoa_v2`, và phép thử 10 bệnh ngoài khuôn) |
| `b3_cap_nhat_trang_thai` | `b3_sinh_cap_ung_vien_quan_he`, `b3_phan_xu_quan_he` (các nhánh `C_quan_he…`) |
| `b4_kiem_can_cu` | `b4_kiem_day_du`, `b6_sua_cuc_bo` (nhánh `D`); `b4_kiem_noi_dung_trich` (mới, chưa nối) |
| `b5_xep_cho_cong_rui_ro`, `b5_viet_ban_nhap` | `b5_diem_rui_ro_quy_gan` (chỉ dùng để đo đường đánh đổi) |
| `b6_goi_y_hoi_lai` | `b7_ban_duyet_html` (lệnh dựng HTML riêng) |

**Lưu ý khi trình bày:** con số "10 bệnh ngoài khuôn đúng 52/52" đo trên `b2_bu_chu_ngu_tinh_luoc` và **phần luật**, không phải bước AI và không phải nhánh dịch vụ.

---

## 3. Cây thư mục

```
meditrace-ma-nguon/
├── src/                       ← toàn bộ mã Python lõi (~170 tệp, số tệp ngày 28/11/2026)
│   ├── duong_ong/       22    Đường ống dựng bản nháp (b0 → b7)   ★ phần chính
│   ├── canh_bao/        10    Lớp cảnh báo lỗi khó thấy
│   ├── audio/           23    Chép lời, tách người nói (kể cả asr/)
│   ├── he_thong/        11    Dịch vụ HTTP, an toàn, minh bạch
│   ├── bo_du_lieu/      32    Sinh, nạp, chia dữ liệu
│   ├── huan_luyen/       6    Huấn luyện mô hình cho bước b1
│   ├── do_luong/        37    Bộ chấm và phép đo
│   ├── cong_cu_lam_sang/ 20   Công cụ phụ trợ bác sĩ
│   └── README.md              Giới thiệu ngắn từng thư mục
├── web/                       Giao diện React + máy chủ Node
├── tests/                     ~1.950 phép thử tự động (pytest)
├── tools/                     Script chạy thí nghiệm, đo, dựng báo cáo
├── kaggle-kernels/            Chạy huấn luyện / đo trên GPU Kaggle
├── data/                      Bộ dữ liệu, manifest đóng băng, bảng tri thức thuốc
├── docs/                      Tài liệu, báo cáo, kết quả đo (docs/ket-qua/)
├── trien-khai/                Cấu hình triển khai
├── BAN_DO_MA_NGUON.md         Bản đồ: câu hỏi → tệp, tên cũ → tên mới
└── BAO_CAO_CAI_TIEN_CHANG_1.md Báo cáo trả lời 3 yêu cầu cải tiến của BGK
```

**Quy ước đặt tên trong `src/`:**

| Quy ước | Nghĩa | Ví dụ |
|---|---|---|
| `bN_` (trong `duong_ong/`) | Số thứ tự bước trong đường ống | `b4_kiem_can_cu.py` là bước 4 |
| `cham_` (trong `do_luong/`) | Bộ chấm: so đầu ra với đáp án | `cham_he_thong.py` |
| `do_` (trong `do_luong/`) | Phép đo: sinh một con số trong báo cáo | `do_bo_sot.py` |
| `nap_` (trong `bo_du_lieu/`) | Nạp dữ liệu từ nguồn ngoài | `nap_vimq.py` |
| `sinh_` | Sinh ra dữ liệu hoặc văn bản | `sinh_hoi_thoai_viet.py` |
| `doi_chung_` | Phương pháp đối chứng để so sánh | `doi_chung_context_vi.py` |

---

## 4. Đơn vị dữ liệu trung tâm: mệnh đề

Điểm khác biệt quan trọng nhất của kiến trúc: hệ thống **không làm việc trên văn bản**, mà làm việc trên **mệnh đề**. Mỗi mệnh đề là một thông tin nhỏ, có cấu trúc, mang theo bằng chứng của nó.

Định nghĩa nằm ở [`src/duong_ong/b1_cau_truc_menh_de.py`](../src/duong_ong/b1_cau_truc_menh_de.py) (lớp `PhatBieu`):

| Trường | Ý nghĩa | Ví dụ |
|---|---|---|
| `noi_dung` | Thông tin | "dị ứng penicillin" |
| `nguoi_noi` | **Ai nói** câu này | "người nhà" |
| `chu_the_id` | **Nói về ai** (0 = bệnh nhân, 1..n = người khác) | 1 (người mẹ) |
| `trich_dan` | Câu nói gốc, **nguyên văn** | "bản thân tôi thì bị dị ứng penicillin" |
| `bang_chung` | Số thứ tự lượt nói chứa câu đó | [5] |
| `do_chac_chan` | chắc chắn / nghi ngờ… | "chắc chắn" |
| `phu_dinh` | Câu khẳng định hay phủ định | false |
| `tinh_huong` | Thực tế hay giả định ("nếu…") | "thực tế" |
| `moc_thoi_gian` | Thời điểm | "từ chiều hôm qua" |
| `thuoc` | Chi tiết thuốc: liều, số lần, đường dùng | {lieu: "500 mg"} |
| `trang_thai` | còn hiệu lực / bị thay thế / chưa giải quyết | "còn hiệu lực" |
| `audio_spans` | Mốc thời gian trong tệp ghi âm | để nút **Nghe lại** |

**Vì sao chọn mệnh đề thay vì văn bản?** Vì với mệnh đề, hệ thống làm được những việc văn bản không làm được:

- đánh dấu riêng một thông tin là "bị thay thế" khi người bệnh nói lại;
- kiểm riêng từng thông tin với đúng câu nói gốc;
- chấm rủi ro riêng từng thông tin;
- chuyển đúng một dòng xuống "Cần xác nhận" mà không phải viết lại cả bản.

Hai trường **`nguoi_noi`** và **`chu_the_id`** được tách riêng có chủ đích. Trong phòng khám Việt Nam, người nói thường **không phải** người bệnh: mẹ kể cho con, con gái kể cho bố.

**Ví dụ: một câu nói chứa bốn thông tin cần xử lý khác nhau.** Người mẹ nói: *"Bản thân tôi thì bị dị ứng penicillin, còn cháu chưa thấy dị ứng gì, sốt từ 4 ngày… à không, từ chiều hôm qua."*

| Thông tin | Của ai | Trạng thái | Nơi đặt |
|---|---|---|---|
| Dị ứng penicillin | Mẹ | Còn hiệu lực | Tiền sử gia đình |
| Chưa dị ứng thuốc | Bé | Còn hiệu lực | Dị ứng của bé |
| Sốt 4 ngày | Bé | Bị đính chính | Không vào hồ sơ, giữ vết |
| Sốt từ chiều qua | Bé | Còn hiệu lực | Bệnh sử |

Nếu để AI viết thành một đoạn văn kiểu *"Bé sốt từ chiều qua, tiền sử dị ứng penicillin"*, đoạn đó đúng một nửa, sai một nửa, và không ai kiểm được. Tách mệnh đề để mỗi thông tin được **kiểm riêng, gán người riêng, sửa riêng và đo riêng**.

**Cái giá của cách làm này:** dễ bỏ sót thông tin nằm chung câu với thông tin khác; câu văn ghép từ mẫu kém mượt; khó biểu diễn quan hệ nhân quả ("đau bụng **do** ăn đồ lạ"); tốn công tạo dữ liệu có đáp án theo từng mệnh đề. Cách tiếp cận này cùng hướng với các nghiên cứu đánh giá tính xác thực bằng cách tách văn bản thành "atomic facts" (ví dụ FActScore).

---

## 5. Đường ống dựng bản nháp, từng bước

Thư mục [`src/duong_ong/`](../src/duong_ong/). Tệp điều phối là [`chay_duong_ong.py`](../src/duong_ong/chay_duong_ong.py) (hàm `chay_trung_gian()`).

### b0. Chuẩn hoá đầu vào (luật)

| Tệp | Việc |
|---|---|
| `b0_chuan_hoa_phuong_ngu.py` | Hiểu từ địa phương và khẩu ngữ ("nhức quá trời", "ói") để so khớp, **nhưng giữ nguyên lời gốc** để trích dẫn |
| `b0_cat_doan_van.py` | Cắt lời nói thành đoạn ngắn theo dấu câu. Nơi sinh dữ liệu và nơi kiểm căn cứ dùng chung một cách cắt |

### b1. Rút mệnh đề (🤖 bước duy nhất dùng AI)

| Tệp | Việc |
|---|---|
| `b1_cau_truc_menh_de.py` | Định nghĩa mệnh đề (mục 4); đổi JSON của mô hình thành mệnh đề |
| `b1_vi_du_mau_loi_nhac.py` | Ví dụ mẫu đặt vào lời nhắc để mô hình làm đúng |
| `b1_ep_dau_ra_json.py` | Ngữ pháp GBNF (cho llama.cpp) và cây chuỗi con của hội thoại. *Chưa dùng trong luồng thật* — xem lưu ý bên dưới |
| `b1_quet_lai_ve.py` | Tìm các **vế** hội thoại có tín hiệu lâm sàng mà chưa câu trích nào phủ, hỏi lại mô hình đúng các vế đó, rồi gộp mệnh đề mới. Bật bằng tuỳ chọn `quet_lai` (**mặc định tắt**), chỉ dùng cho các nhánh có khoá K1–K7 |

- **Mô hình:** Qwen3-4B cộng adapter LoRA tự huấn luyện (xem mục 12).
- **Vào:** lời thoại theo lượt.
- **Ra:** danh sách mệnh đề, mỗi mệnh đề kèm câu trích và số lượt.
- Mô hình **không viết văn**, chỉ điền bảng.

**Chống ảo giác ngay ở bước sinh — giải mã có ràng buộc (constrained decoding).** Mô hình ngôn ngữ sinh chữ theo cơ chế tự hồi quy: ở mỗi bước, nó chấm điểm (logit) mọi token trong bộ từ vựng, đổi thành xác suất, rồi chọn token. Nó chọn cái **nghe hợp lý**, không phải cái **đúng sự thật** — đó là nguồn gốc của ảo giác. Bộ ép định dạng can thiệp đúng chỗ này:

```
Đã sinh tới:   "nguoi_noi": "
Bảng xác suất: bà 35% · người nhà 30% · mẹ 20% · bệnh nhân 10% · bác sĩ 5% …
Sau khi ép:    bà 0% · người nhà 67% · mẹ 0% · bệnh nhân 22% · bác sĩ 11%
               (logit của token sai lược đồ đặt về −∞; phần còn lại chuẩn hoá lại 100%)
→ mô hình chỉ chọn được trong: bác sĩ / bệnh nhân / người nhà / điều dưỡng
```

- Bộ ép **đang chạy thật** là `_ep_json()` trong [`huan_luyen/chon_mo_hinh_bakeoff.py`](../src/huan_luyen/chon_mo_hinh_bakeoff.py), dùng thư viện **lm-format-enforcer** với lược đồ JSON. Nếu máy chưa cài thư viện này, mô hình chạy **không ép** và chỉ in một dòng thông báo — nên kiểm trước khi demo.
- Kèm **giải mã tham lam** (`do_sample=False`) và **tắt chế độ suy nghĩ** của Qwen3 (`enable_thinking=False`, giống lúc huấn luyện) để kết quả tất định ([`chay_duong_ong.py`](../src/duong_ong/chay_duong_ong.py), hàm `_sinh`).
- Kết quả: **0/30** ca lỗi định dạng JSON.
- **Giới hạn:** ép định dạng chỉ bảo đảm **đúng hình dạng**, không bảo đảm **đúng sự thật**. Ô lựa chọn vẫn có thể bị chọn sai (ghi "chắc chắn" khi câu gốc chỉ nghi), ô viết tự do (câu trích, liều) vẫn có thể bị bịa. Phần nội dung do K1–K7 kiểm ở bước b4.
- **Hướng cải tiến:** nếu nối cây chuỗi con trong `b1_ep_dau_ra_json.py` vào lúc sinh, ô `trich_dan` sẽ chỉ được chứa đoạn có thật trong hội thoại, tức mô hình **không thể** bịa câu trích ngay từ đầu. Chú thích đầu tệp đó ghi "loại trừ hoàn toàn ảo giác trích dẫn" — câu này **chưa đúng với luồng đang chạy**.

### b2. Gom người (luật)

| Tệp | Việc |
|---|---|
| `b2_gom_nguoi_thuc_the.py` | Gom các cách gọi ("tôi", "mẹ tôi", "bà ấy", "cháu") về đúng một người; phân biệt người nói với người được nói đến |
| `b2_bu_chu_ngu_tinh_luoc.py` | Bù chủ ngữ cho câu bị lược ("Đêm qua nôn hai lần" — ai nôn?) theo ngữ cảnh hội thoại, kèm một máy trạng thái đính chính riêng. *Chỉ dùng ở nhánh thử nghiệm `C_khoa_v2`.* Lưu ý: khi không có manh mối, tệp mặc định gán cho bệnh nhân — chiều rủi ro hơn; ở luồng thật K3 vẫn cảnh báo "chủ thể chỉ suy từ người nói" |

### b3. Cập nhật trạng thái (luật)

| Tệp | Việc |
|---|---|
| `b3_cap_nhat_trang_thai.py` | Áp luật chuyển trạng thái. **Đây là tệp luồng thật dùng** |
| `b3_sinh_cap_ung_vien_quan_he.py` | Tìm các cặp mệnh đề có thể liên quan nhau. *Nhánh thử nghiệm `C_quan_he…`* |
| `b3_phan_xu_quan_he.py` | Quyết định quan hệ của từng cặp, bằng luật hoặc hỏi mô hình. *Nhánh thử nghiệm `C_quan_he…`* |

Có bốn loại quan hệ:

| Quan hệ | Ví dụ | Xử lý |
|---|---|---|
| **Bổ sung** | "Ho" rồi "ho có đờm" | Giữ cả hai |
| **Đính chính** | "4 ngày… à không, từ chiều qua" | Bản cũ → **bị thay thế** (không xoá, vẫn lưu lịch sử) |
| **Diễn biến** | "Hôm qua sốt 38, nay 39 độ" | Giữ cả hai theo thời gian |
| **Mâu thuẫn** | Con gái nói bố quên thuốc, bố nói vẫn uống | **Chưa giải quyết** → đưa bác sĩ hỏi lại |

### b4. Kiểm căn cứ (luật)

Tệp [`b4_kiem_can_cu.py`](../src/duong_ong/b4_kiem_can_cu.py). Mỗi mệnh đề phải **chứng minh được bằng chính lời thoại**, qua 7 phép kiểm:

🔴 chặn = chuyển sang "Cần xác nhận", **không xoá** · 🟡 cảnh báo = vẫn vào thân bản nháp, được đánh dấu

| Mã | Kiểm gì | Ví dụ lỗi | 🔴 Chặn khi | 🟡 Cảnh báo khi |
|---|---|---|---|---|
| **K1** Nguồn | Câu trích có **nguyên văn** trong lượt được dẫn không | AI trích "sốt 3 ngày", người bệnh nói "sốt mấy hôm nay" | Không có câu trích; lượt không tồn tại; câu trích không có trong hội thoại | Câu trích nằm ở lượt khác lượt được dẫn |
| **K2** Nội dung | Nội dung có trùng từ với câu trích không (chỉ so từ, không hiểu ý) | Ghi "ho", câu trích nói đau đầu | — | Không trùng từ nào; chỉ khớp qua một từ phương ngữ mơ hồ |
| **K3** Người | Câu trích nói về **đúng người** không | Ghi dị ứng cho bé, câu gốc là "bản thân tôi" của mẹ | Ghi cho bệnh nhân mà câu gốc là người kể tự nói về mình; ghi cho người nhà mà câu gốc nói về bệnh nhân | Có nhắc người nhà; chủ thể chỉ suy từ người nói; chưa rõ chủ thể |
| **K4** Mức | Không biến nghi ngờ, "nếu…", "chưa ghi nhận" thành điều chắc chắn | "Nếu mai còn sốt thì chụp phim" thành "đã chụp phim" | Câu gốc chỉ nghi; là câu điều kiện hay dự phòng; là chưa ghi nhận; đã bị đính chính ngầm ("tưởng viêm phổi nhưng chụp phim thì không phải") | Đoạn dẫn có từ phủ định |
| **K5** Thời gian | Mốc thời gian có trong lượt dẫn không | "Mười ngày" thành "ba tuần" | — | Không thấy mốc thời gian |
| **K6** Thuốc | Chi tiết thuốc có trong lời nói không | Tự thêm "500 mg" | Liều không có trong lượt dẫn | Số lần dùng, lúc bắt đầu/ngừng, đường dùng không thấy |
| **K7** Thay thế | Đã bị đính chính hay diễn biến mới thay thế chưa (trạng thái từ bước b3) | "250 mg… à nhầm, 500 mg" mà vẫn giữ 250 | Bị thay thế | Đang mâu thuẫn, chưa giải quyết |

Tên các lý do nằm trong bảng `LY_DO` của tệp; khung đầu tệp cũng có bảng tóm tắt K1–K7.

**Giới hạn cần biết:** K1 là phép **so chuỗi** nên chắc chắn 100%. K2–K6 là **luật theo từ**, nên chỉ bắt được một phần: một câu trích có thật nhưng bị diễn giải sai có thể chỉ bị cảnh báo. Kết quả đo: **0 / 30.136** dòng đáp án đúng bị chặn oan.

**Tệp phụ của bước b4:**

| Tệp | Việc | Trong luồng thật? |
|---|---|---|
| `b4_kiem_day_du.py` | Tìm chỗ bản nháp bỏ sót mệnh đề còn hiệu lực | Không — nhánh `D` |
| `b4_kiem_noi_dung_trich.py` | So nội dung mệnh đề với chính câu trích của nó, **chặt hơn K2**: có chữ không nằm trong câu trích, chép nguyên lỗi chép âm không dấu, bỏ mất vế bổ nghĩa ("về đêm", "sau khi ăn"), trùng dưới 50% chữ | Chưa — tệp mới thêm 28/11/2026, chưa nối vào đường ống |

### b5. Xếp chỗ và viết bản nháp (luật)

| Tệp | Việc |
|---|---|
| `b5_xep_cho_cong_rui_ro.py` | Chấm rủi ro từng mệnh đề và quyết định chỗ của nó |
| `b5_diem_rui_ro_quy_gan.py` | Điểm rủi ro riêng cho lỗi gán nhầm người. *Chỉ dùng để đo đường đánh đổi* |
| `b5_viet_ban_nhap.py` | Viết bản nháp bằng **mẫu câu cố định**, không dùng AI |

Điểm rủi ro được tính như sau:

```
điểm rủi ro = mức nghiêm trọng × độ thiếu căn cứ × hệ số cơ địa

mức nghiêm trọng:  dị ứng 1,0 · thuốc khoảng điều trị hẹp 1,0 · thuốc 0,9
                   chẩn đoán 0,8 · thời gian 0,6 · khác 0,3
độ thiếu căn cứ:   mâu thuẫn 1,0 · chủ thể là người khác 0,75 · chưa rõ chủ thể 0,65 …
hệ số cơ địa:      tăng với trẻ nhỏ, người cao tuổi, thai kỳ, suy thận, suy gan, đa thuốc
ngưỡng cao:        0,5
```

Kết quả mỗi mệnh đề rơi vào một trong bốn nhóm: **bị chặn**, **nguy cơ cao**, **rủi ro thấp**, **đã kiểm chứng**. Nhóm này dùng để xếp thứ tự cho bác sĩ duyệt (nguy hiểm nhất lên trước). Quy tắc xếp chỗ:

- **Bị chặn** (không qua K1–K7) → mục **Cần xác nhận**, kèm lý do.
- **Dị ứng và thuốc** mà còn **bất kỳ cảnh báo nào** → cũng chuyển sang **Cần xác nhận**, dù không bị chặn.
- Các thông tin khác còn cảnh báo → vẫn vào thân bản nháp, được đánh dấu để bác sĩ xem kỹ.
- Thông tin **bị thay thế** → không vào thân, vẫn giữ trong lịch sử.

**Vì sao viết bằng mẫu câu mà không để AI viết?** Nếu để AI viết lại cho mượt, bước cuối lại mở cửa cho chuyện bịa, và mất khả năng truy từng dòng về câu nói gốc.

### b6. Hỏi lại và sửa (luật)

| Tệp | Việc |
|---|---|
| `b6_goi_y_hoi_lai.py` | Chọn **tối đa 3 câu hỏi** giải quyết được nhiều rủi ro nhất để bác sĩ hỏi lại người bệnh |
| `b6_sua_cuc_bo.py` | Sửa đúng câu sai trong bản nháp, không sinh lại cả bản. *Nhánh `D`* |

### b7. Bản duyệt

`b7_ban_duyet_html.py` dựng trang ba cột (lời thoại · mệnh đề · bản nháp). Bấm dòng nào thì tô sáng câu nói gốc của dòng đó. *Chạy bằng lệnh riêng; trong sản phẩm, giao diện web làm việc này.*

### Điều phối

| Tệp | Việc |
|---|---|
| `chay_duong_ong.py` | Chạy cả đường ống; chạy các nhánh so sánh (mục 15) |
| `chay_nhanh_e.py` | Nhánh E: lấy bản nháp văn xuôi, bổ sung chỗ sót và sửa bằng bảng mệnh đề |

---

## 6. Theo chân một ca khám thật

Ca mẫu `demo_bs_nguoi_nha_nhi` trong [`src/bo_du_lieu/ca_mau_bgk.py`](../src/bo_du_lieu/ca_mau_bgk.py). Trên giao diện, bấm **"Xem thử với ca mẫu"** là chạy được, không cần GPU.

**Hội thoại (rút gọn):**

```
[T2] Mẹ : Cháu sốt cao với ho đờm từ 4 ngày nay.
[T3] Bé : Không phải 4 ngày đâu ạ, con mới bị sốt nóng từ chiều hôm qua thôi.
[T5] Mẹ : Bản thân tôi thì bị dị ứng penicillin… còn cháu chưa thấy bị dị ứng thuốc gì.
[T7] BS : Nếu đêm nay cháu sốt cao trên 39 độ thì…
```

**Ca này đi qua từng bước:**

| Bước | Chuyện gì xảy ra |
|---|---|
| b1 🤖 | AI rút ra các mệnh đề: "sốt cao 4 ngày" (T2), "sốt từ chiều hôm qua" (T3), "dị ứng penicillin" (T5), "chưa dị ứng thuốc" (T5), "sốt trên 39 độ" (T7)… |
| b2 | "Bản thân tôi" ở T5 do **mẹ** nói → dị ứng penicillin là **của mẹ**, không phải của bé |
| b3 | T3 đính chính T2 → "sốt cao 4 ngày" chuyển thành **bị thay thế** |
| b4 | K3: nếu AI lỡ ghi dị ứng cho bé, câu trích có "bản thân tôi" của người mẹ → **chặn**. K4: T7 là câu "nếu…" → **chặn**, không ghi thành sự thật. K7: mệnh đề bị thay thế → **chặn** |
| b5 | Thân bản nháp: *Bệnh sử: sốt từ chiều hôm qua* · *Dị ứng: chưa ghi nhận* · *Tiền sử gia đình: mẹ dị ứng penicillin*. Mục **Cần xác nhận**: "sốt cao 4 ngày" (đã bị đính chính), lời dặn "nếu sốt trên 39 độ" (câu giả định) |
| Web | Nút ký hiện **"Cần xác nhận (N)"**, bị khoá cho tới khi bác sĩ xác nhận, sửa hoặc bỏ từng mục |

---

## 7. Lớp cảnh báo

Thư mục [`src/canh_bao/`](../src/canh_bao/). Hình dung lớp này là **người soát lỗi thứ hai**: đường ống đã dựng xong bảng mệnh đề, người soát cầm từng mệnh đề so lại với lời nói gốc để bắt những lỗi tinh vi mà K1–K7 chưa bắt hết. Toàn bộ là luật.

### 7.1. Chạy ở đâu trong luồng

```
① Đường ống b0–b6     → BẢNG MỆNH ĐỀ + bản nháp + "Cần xác nhận" (chính sách C)
② Lớp cảnh báo         vào: BẢNG MỆNH ĐỀ + LỜI THOẠI GỐC (không đọc văn bản nháp)
   he_thong/dich_vu_http._them_canh_bao() → canh_bao/gop.chay()
   → danh sách cảnh báo + TRẠNG THÁI MỚI cho từng mệnh đề (chính sách D)
③ Giao diện web        ưu tiên trạng thái chính sách D để quyết định dòng nào cần xác nhận
                       (web/src/lib/compileEffectiveNote.ts, hàm canXacNhan) và khoá ký theo đó
```

Lớp cảnh báo **dùng lại kết quả K1–K7** (gọi lại `khoa_ca()` của bước b4), rồi chạy thêm các bộ bắt lỗi riêng. Nó **không chỉ ghi chú**: một dòng đường ống đã cho vào thân bản nháp vẫn có thể bị kéo sang "Cần xác nhận". Nhờ vậy lỗi nguy hiểm lọt vào bản nháp giảm từ **45,9%** (chính sách C) xuống **11,8%** (chính sách D).

### 7.2. Mười tệp, bốn vai

```
              loai.py  ← SỔ QUY ĐỊNH: có những lỗi gì, nặng nhẹ ra sao
                 │
   ┌─────────────┼─────────────┬──────────────┬─────────────┐
phat_hien.py  toan_ca.py    lam_sang.py     asr.py        ← NGƯỜI BẮT LỖI (mỗi người soi một kiểu)
                 │
              bo_sot.py   (toan_ca gọi sang để tìm chỗ bị sót)
   └─────────────┴─────────────┴──────────────┴─────────────┘
                 │
              gop.py   ← TỔ TRƯỞNG: gom kết quả, bỏ trùng, ra quyết định
                 │
   loi_noi.py · so_lieu.py · nhat_ky.py   ← ĐỒ NGHỀ dùng chung
```

| Vai | Tệp | Câu hỏi nó trả lời | Ví dụ |
|---|---|---|---|
| **Sổ quy định** | `loai.py` | Có những loại lỗi nào? | **13 nhóm, 56 mã**; tiêu đề và lời giải thích cho bác sĩ; mức nghiêm trọng; độ tin cậy của từng bộ bắt lỗi; **7 nhóm chưa phát hiện được** (`CHUA_PHAT_HIEN`). Tệp này không bắt lỗi nào |
| **Bắt lỗi từng dòng** | `phat_hien.py` | Dòng này có khớp lời gốc không? | "Bé dị ứng" nhưng câu gốc là "**tôi** bị dị ứng" của mẹ; "**không** đau" thành "đau"; chân **trái** thành **phải**; sai số, sai mức độ |
| **Bắt lỗi cả bản** | `toan_ca.py` (+ `bo_sot.py`) | Các dòng có mâu thuẫn, lặp, thiếu không? | Dòng 3 "sốt 3 ngày", dòng 7 "sốt 1 tuần"; ghi một thông tin hai lần; giữ số cũ đã bị sửa; **thông tin bị sót** |
| **Bắt lỗi kiến thức** | `lam_sang.py` | Thuốc này có an toàn không? | Liều vượt trần mỗi ngày; hai thuốc tương tác; kê thuốc người bệnh đang dị ứng. Bảng thuốc **chưa có chuyên gia duyệt**, nên nhóm này là *thử nghiệm* |
| **Bắt lỗi chép âm** | `asr.py` | Máy có nghe nhầm không? | Máy chép không chắc ở chỗ có tên thuốc; chưa chắc ai đang nói. Chỉ chạy khi đầu vào là ghi âm |
| **Tổ trưởng** | `gop.py` | Gộp lại thì dòng nào phải xác nhận? | Gọi mọi bộ bắt lỗi, gộp trùng, giới hạn hiển thị, phân tầng, áp chính sách D. **Tệp duy nhất ra quyết định** |
| **Đồ nghề** | `loi_noi.py`, `so_lieu.py`, `nhat_ky.py` | — | Chuẩn hoá lời nói (tách ý, nhận câu hỏi, bỏ từ đệm); tách con số kèm đơn vị ("500 mg"); ghi cảnh báo ra tệp để đo |

**Ba cặp hay bị nhầm:**

- **`phat_hien` và `toan_ca`:** `phat_hien` nhìn **một dòng**, hỏi "dòng này có khớp câu gốc không?". `toan_ca` nhìn **cả bản**, hỏi "các dòng có hợp với nhau không, có thiếu gì không?". Hai dòng "sốt 3 ngày" và "sốt 1 tuần" mỗi dòng đều có thể khớp câu gốc của nó, nhưng đặt cạnh nhau thì mâu thuẫn — chỉ `toan_ca` thấy.
- **`phat_hien` và `lam_sang`:** `phat_hien` hỏi "**có ai nói điều này không?**" (so với lời thoại). `lam_sang` hỏi "**điều này có an toàn không?**" (so với kiến thức thuốc). "Uống paracetamol 6 g/ngày" mà người bệnh nói đúng như vậy: `phat_hien` cho qua, `lam_sang` báo vượt liều trần.
- **`toan_ca` và `bo_sot`:** `bo_sot.py` là **bộ tìm chỗ sót dùng chung** cho cả hệ thống (công cụ BHYT cũng dùng). `toan_ca.py` gọi sang nó rồi đổi kết quả thành cảnh báo.

Lỗi của `asr.py` khác hẳn các lỗi kia: nó xảy ra **trước khi AI đọc**. Nếu máy chép nghe nhầm tên thuốc, câu trích vẫn "khớp" bản chép sai, nên `phat_hien` không thấy.

### 7.3. Một cảnh báo gồm những gì

Bản ghi `CanhBao` trong `loai.py`:

| Trường | Ý nghĩa |
|---|---|
| `ma` | Mã lỗi, ví dụ `WRONG_SUBJECT` |
| `phat_bieu_id` | Gắn vào dòng nào (để trống = cảnh báo cả ca) |
| `luot`, `trich` | Lượt nói và **câu gốc** làm lý do |
| `ly_do` | Giải thích bằng lời thường |
| `ket_luan` | **Lỗi đã phát hiện** / **nghi có rủi ro** / **chỉ cần xem** |
| `muc_do` | Nếu sai thì nguy hiểm đến đâu: cao / trung / thấp |
| `bat_dinh` | Bằng chứng của chính cảnh báo chắc đến đâu |

Mỗi mã còn mang **độ tin cậy của bộ bắt lỗi**: *ổn định* (đã có phép thử — **chỉ loại này được đổi trạng thái**), *thử nghiệm* (chỉ hiện để bác sĩ lưu ý), *chưa tin cậy* (chưa có bộ bắt lỗi).

### 7.4. Chống báo động tràn lan

Một lỗi có thể làm nhiều bộ cùng kêu: "Bố tôi bị hen" ghi thành "bệnh nhân bị hen" kích cả *sai người*, *nhầm người nhà với bệnh nhân*, *không có căn cứ*. `gop.py` xử lý:

1. Cùng mã từ nhiều bộ → gộp làm một.
2. Cùng nhóm → một **cảnh báo chính**, mã khác thành mã phụ.
3. Khác nhóm nhưng đủ nặng → giữ riêng, tối đa 2.
4. **Ngân sách hiển thị:** mặc định **2 cảnh báo mỗi dòng**; cảnh báo mức cao luôn hiện; phần còn lại thu gọn.
5. **Phân 3 tầng:** 🔴 chặn ngay · 🟡 cần xem xét (thuốc, dị ứng, bỏ sót quan trọng) · ⚪ tinh lược (nhiễu, giá trị thấp).
6. Mã có độ chính xác thấp (ví dụ một mã chỉ đúng **5,8%**) bị hạ thành **gợi ý**, không được đổi trạng thái — trừ trên dị ứng và thuốc.

### 7.5. Chính sách D quyết định thế nào

Hàm `trang_thai_D()` xét **lần lượt**, dừng ở câu đầu tiên trả lời "có":

```
1. Đã bị người nói đính chính?        → BỊ THAY THẾ    (không vào bản nháp, giữ vết)
2. K1–K7 đã chặn?                      → CẦN XÁC NHẬN
3. Đang mâu thuẫn với nguồn khác?      → CẦN XÁC NHẬN
4. Có cảnh báo "đủ nặng"?              → CẦN XÁC NHẬN  (kèm tiêu đề + lý do)
5. Không có gì ở trên                  → ĐÃ KIỂM CHỨNG (vẫn có thể kèm cảnh báo nhẹ)
```

"Đủ nặng" nghĩa là: bộ bắt lỗi **ổn định** (nhóm chất lượng, chép âm, bỏ sót **không bao giờ** đổi trạng thái), **và** là lỗi đã phát hiện ở mức cao/trung, **hoặc** nghi có rủi ro mà bằng chứng không quá mờ. **Riêng dị ứng và thuốc** thì nghi yếu cũng chặn, vì phép đo cho thấy trên hai loại này cảnh báo yếu vẫn trúng lỗi thật khoảng 44% số lần.

**Ví dụ trọn vòng:** con trai nói *"Bố tôi bị hen, còn tôi khoẻ"*, AI ghi "Bệnh nhân bị hen". `WRONG_SUBJECT` và `FAMILY_PATIENT_MIXUP` cùng kêu → gộp thành một cảnh báo chính "gán sai người" → lỗi đã phát hiện, mức cao, bộ ổn định → **CẦN XÁC NHẬN**, kèm câu gốc "bố tôi" và nút nghe lại.

### 7.6. Kết quả và giới hạn

| | Số |
|---|---|
| Lỗi nguy hiểm lọt vào bản nháp | 45,9% → **11,8%** (chặn 88,2%) |
| Câu đúng bị chặn nhầm | 8,0% → **10,0%** (cái giá phải trả) |
| Bắt lỗi cài sẵn, tập giữ kín 240 ca | **0,871** |
| Cảnh báo trên bản ghi không có lỗi | khoảng **7–8 mỗi ca** (ngân sách hiển thị và phân tầng giảm phần bác sĩ thấy) |

Các số đo trên tập phát triển và lỗi cài nhân tạo, nên là cận lạc quan. 7 nhóm lỗi ngữ nghĩa sâu (đại từ qua nhiều lượt, suy luận ngầm ý…) được công khai là chưa bắt được.

### 7.7. Tên tệp dự kiến đổi

Để dễ tìm, các tệp sẽ được đổi tên theo **vai** (chưa đổi, chờ khi không còn phiên nào khác đang sửa thư mục này):

| Tên hiện tại | Tên dự kiến |
|---|---|
| `loai.py` | `danh_muc_loi.py` |
| `phat_hien.py` | `bat_loi_tung_dong.py` |
| `toan_ca.py` | `bat_loi_ca_ban.py` |
| `bo_sot.py` | `bat_loi_bo_sot.py` |
| `lam_sang.py` | `bat_loi_kien_thuc_thuoc.py` |
| `asr.py` | `bat_loi_chep_am.py` |
| `gop.py` | `quyet_dinh_gop_canh_bao.py` |
| `loi_noi.py`, `so_lieu.py`, `nhat_ky.py` | `tien_ich_loi_noi.py`, `tien_ich_so_lieu.py`, `tien_ich_nhat_ky.py` |

---

## 8. Âm thanh

Thư mục [`src/audio/`](../src/audio/). Toàn bộ chạy tại máy, không gửi ghi âm ra internet.

```
tệp ghi âm
  → preprocessing.py         đổi về WAV 16 kHz mono (giữ tệp gốc)
  → asr/phowhisper_provider  chép lời bằng PhoWhisper (bộ chép chính)
  → pyannote_provider        tách người nói
  → alignment.py             gán người nói cho từng đoạn theo mốc thời gian
  → bác sĩ duyệt vai người nói   ← chưa duyệt xong thì KHÔNG cho dựng bản nháp
  → adapter.py               đổi sang dạng lời thoại cho đường ống
```

- `asr/disagreement.py` chạy hai bộ chép lời (PhoWhisper và faster-whisper), đánh dấu chỗ hai bên bất đồng ở từ quan trọng (thuốc, liều, phủ định).
- `pipeline.py` điều phối cả phiên; `storage.py` lưu phiên kèm nhật ký; `api.py` là máy chủ nhỏ cho tải lên và duyệt lời thoại.

---

## 9. Giao diện web và ký duyệt

Thư mục [`web/`](../web/).

| Phần | Việc |
|---|---|
| `web/server.ts` | Máy chủ Node, nối giao diện với lõi Python |
| `web/may-chu/routes/` | Các API: ca khám, ký duyệt, chép lời, BHYT, công cụ lâm sàng, tra cứu, trợ lý |
| `web/may-chu/routes/sign-off.ts` + `worm.ts` | **Ký duyệt**: máy chủ từ chối ký nếu còn mục chưa xác nhận; ghi nhật ký chỉ-ghi-thêm có chuỗi băm |
| `web/may-chu/routes/llm-ngoai.ts` | Cổng gọi AI bên ngoài: **mặc định tắt**, có hạn mức, không dùng để viết bản nháp |
| `web/may-chu/tro-ly/an-danh.ts` | Che thông tin định danh trước khi gửi bất cứ thứ gì ra ngoài |
| `web/may-chu/tra-cuu/` | Tra tài liệu y khoa công khai (PubMed, WHO, openFDA, kcb.vn…) |
| `web/src/components/` | Màn hình React: soạn bản nháp, duyệt từng mệnh đề, bằng chứng hội thoại, menu Công cụ |
| `web/src/lib/kyDuyet.ts`, `compileEffectiveNote.ts` | Điều kiện ký phía giao diện; ghép bản nháp sau khi bác sĩ sửa |

**Khoá ký có hai tầng:**

1. **Giao diện:** còn mục chưa xác nhận thì nút ký hiện "Cần xác nhận (N)", bấm vào sẽ cuộn tới mục đó.
2. **Máy chủ:** dù có ai gửi lệnh ký thẳng, máy chủ vẫn từ chối (HTTP 400).

Sau khi ký, nếu bản ghi bị sửa dù chỉ một ký tự, trạng thái chuyển thành "Đã sửa · Ký lại".

**Máy chủ web `web/may-chu/` gồm 6 nhóm tệp** (bảng từng tệp ở [`BAN_DO_MA_NGUON.md`](../BAN_DO_MA_NGUON.md#máy-chủ-web--webmay-chu-từng-tệp)):

| Nhóm | Tệp | Vai trò |
|---|---|---|
| Quầy nhận yêu cầu | `routes/asr.ts`, `ca-kham.ts`, `sign-off.ts`, `llm-ngoai.ts`, `tro-ly.ts`, `tra-cuu.ts`, `boost-lam-sang.ts`, `bhyt-ocr.ts`, `benh-nhan-portal.ts`, `quan-tri-bv.ts`, `dung-chung.ts` | Mỗi tệp một nhóm API; `asr.ts` là luồng chính chép lời → dựng bản nháp |
| Ký duyệt, chống sửa | `worm.ts`, `kiem-ky-may-chu.ts` | Sổ ký có khoá bí mật; chỉ xuất hồ sơ đã ký và chưa sửa |
| Quyền riêng tư | `an-danh-ngoai.ts`, `tro-ly/an-danh.ts`, `che-log.ts`, `loi-ra-mang.ts`, `noi-luu-du-lieu.ts`, `sinh-so-do-du-lieu.ts`, `chan-tep-dev.ts` | Che danh tính, khai báo lối ra mạng và nơi lưu; lệch thì kiểm thử đỏ |
| Tra cứu | `tra-cuu/*` | Vòng ngoài, xem mục 9.1 |
| Trợ lý | `tro-ly/*` | Vòng ngoài; AI ngoài chỉ lập kế hoạch, không thấy dữ liệu ca |
| Hạ tầng | `csdl.ts`, `tai-khoan.ts`, `hang-doi.ts`, `env.ts` | SQLite, đăng nhập, hàng đợi việc nền |

Nguyên tắc chung: **máy chủ không tin trình duyệt**. Việc đã ký chưa, còn mục cần xác nhận không và mã băm nội dung đều do máy chủ tự tính lại.

Hợp đồng dữ liệu giữa Python và TypeScript: [`src/he_thong/hop_dong_api.py`](../src/he_thong/hop_dong_api.py) ↔ `web/src/types/api-contract.ts`. Có phép thử kiểm hai bên khớp nhau.

**Màn hình duyệt của bác sĩ:**

| Việc | Tệp |
|---|---|
| Duyệt từng mệnh đề: Xác nhận / Sửa / Bỏ | `web/src/components/DuyetBenCanh.tsx` |
| Dây nối từ dòng bản nháp về câu nói gốc | `web/src/components/VerificationView.tsx` |
| Nghe lại đúng đoạn ghi âm (đệm ±0,5 giây) | `web/src/hooks/useTurnAudioPlayer.ts` |
| Ghép lại bản nháp sau khi bác sĩ sửa; quyết định dòng nào "cần xác nhận" (ưu tiên chính sách D) | `web/src/lib/compileEffectiveNote.ts` |

### 9.1. Tra cứu y khoa: chấm điểm tài liệu và kiểm số liệu

Thư mục `web/may-chu/tra-cuu/`. Tính năng này thuộc **vòng ngoài** và **khác hẳn** đường ống bản nháp: ở đây **mô hình AI bên ngoài viết câu trả lời** từ tài liệu tra được, nên chỉ chạy khi quản trị bật cổng AI ngoài, và dữ liệu được ẩn danh trước khi gửi.

| Bước | Việc | Tệp |
|---|---|---|
| Đặt từ khoá | Mô hình ngoài đổi câu hỏi thành từ khoá cho từng nguồn | `dich-vu-tra-cuu.ts` (`datTuKhoaTraCuu`) |
| Tìm và **chấm điểm tài liệu** | Mỗi bài được cộng/trừ điểm: tiêu đề khớp tên bệnh thì cộng; câu hỏi cấp cứu mà bài nói "acute/emergency" thì cộng; bài thử nghiệm lâm sàng, giải phẫu, lịch sử thì trừ; bài trẻ em/thai kỳ khi câu hỏi không liên quan thì trừ. Xếp hạng rồi giữ những bài đầu | `nguon-ngoai.ts` (PubMed, WHO, openFDA, NICE, MSD, kcb.vn…), `phac-do-byt.ts` |
| Lọc bài lạc đề | Bỏ bài không chứa từ khoá, tên bệnh, tên thuốc | `tu-dien.ts` (`lienQuan`, `lienQuanChat`) |
| **Kiểm số liệu** trong câu trả lời | `soLech` lấy từng con số kèm đơn vị trong câu trả lời, đổi về cùng đơn vị (1 g = 1000 mg), so với **đúng tài liệu được trích**; không khớp thì gắn cờ "lệch" (bắt được "125 mg" khi tài liệu ghi "0,125 mg") | `kiem-dinh-so.ts` |
| **Kiểm số trích dẫn** | Câu trả lời trích `[7]` mà không có tài liệu số 7 thì phát hiện được | `dich-vu-tra-cuu.ts` |

Giới hạn: `soLech` chỉ kiểm **con số**, không kiểm ý văn; cách chấm điểm tài liệu là luật thủ công, chưa được đo độ chính xác như phần lõi.

---

## 10. Hệ thống, an toàn và minh bạch

Thư mục [`src/he_thong/`](../src/he_thong/).

| Tệp | Việc |
|---|---|
| `dich_vu_http.py` | Dịch vụ HTTP tại chỗ mà web gọi vào; chạy đường ống nhánh `C_khoa` / `C_khoa_hoi` |
| `hop_dong_api.py` | Hình dạng dữ liệu trả về cho web |
| `dieu_phoi_cac_chot_an_toan.py` | Nối các chốt an toàn thành một đường chạy, ghi vết thời gian và kết quả từng chốt |
| `rao_chan_an_toan.py` | Rào chắn nhiều tầng: chất lượng chép lời, nhất quán người nói, câu hỏi và giả định, an toàn lâm sàng |
| `khu_dinh_danh.py` | Che tên, CCCD, số điện thoại, số BHYT. Giới hạn: chỉ che được mẫu có cấu trúc rõ; thử trên văn bản báo chí `PhoNER_COVID19` mới che được 10/847 (1,2%) tên và mã bệnh nhân viết tắt |
| `che_log.py` | Che định danh trước khi ghi log; khi có lỗi chỉ in tên lớp lỗi, vị trí và thông điệp đã che (thêm 28/11/2026) |
| `nhat_ky_ky_duyet_worm.py` | Nhật ký ký duyệt chỉ thêm, nối chuỗi băm SHA-256 |
| `ep_kieu_dau_vao.py` | Ép dữ liệu nhập về đúng kiểu, chống lỗi nhập liệu |
| `duong_dan.py` | Khai báo tập trung các đường dẫn thư mục |
| `khai_ma_nguon.py`, `nhat_ky_loi_nhac.py` | Minh bạch phần mã do AI hỗ trợ viết |

---

## 11. Dữ liệu

Thư mục [`src/bo_du_lieu/`](../src/bo_du_lieu/).

**Dữ liệu mô phỏng, không phải dữ liệu bệnh nhân thật.** Hội thoại khám có thông tin định danh, nên dự án tự sinh dữ liệu bằng luật.

| Nhóm tệp | Việc |
|---|---|
| `kho_khuon.py`, `khuon_lo_3..8.py`, `khuon_mo_rong.py`, `kiem_khuon.py` | **657 khuôn bệnh** thuộc 21 hệ cơ quan (200 khuôn gốc đã duyệt + 457 khuôn mở rộng **chưa có bác sĩ duyệt**) |
| `sinh_hoi_thoai_viet.py`, `ngu_lieu_viet.py`, `bien_the_cau.py`, `loi_dan_thuong.py`, `phuong_ngu.py`, `tang_cuong.py` | **Bộ sinh**: từ khuôn bệnh sinh hội thoại kèm đáp án có cấu trúc (ai nói, của ai, đính chính ở đâu) |
| `sinh_bo_thach_thuc.py`, `dan_gian.py`, `nhieu_asr.py`, `sinh_bo_chan_doan.py` | **Bộ thử thách** theo cặp: mỗi cặp chỉ khác **một điểm** (đổi người, tự sửa, nhiễu chép âm, phương ngữ) |
| `chia_tap_theo_khuon.py`, `chia_bon_tap.py`, `nap_du_lieu.py`, `van_tay_bo.py` | **Chia tập theo khuôn bệnh**: một bệnh chỉ nằm ở một tập, mã chặn việc chạm vào tập kiểm tra cuối |
| `nap_vimq.py`, `nap_vietmed.py`, `nap_bo_gpt500.py`, `nap_bo_nguoi_that.py`, `gan_nhan_truoc.py`, `loc_nhan_may.py` | **Dữ liệu ngoài nguồn**, dùng để đo độ tổng quát |
| `ca_mau_bgk.py` | 3 ca demo nhiều người nói |
| `sinh_ca_da_benh_ly.py` | Sinh ca có bệnh nền và thuốc nền (để tạo dữ liệu, **không** chạy trong luồng khám) |

**Vì sao sinh bằng luật mà không nhờ ChatGPT viết?** Hội thoại do mô hình lớn viết thường quá "sạch", đủ chủ ngữ, nên mất đúng các hiện tượng gây lỗi khó nhất trong tiếng Việt: lược chủ ngữ và đại từ họ hàng đa nghĩa.

---

## 12. Huấn luyện mô hình

Thư mục [`src/huan_luyen/`](../src/huan_luyen/). Phần này chỉ phục vụ **bước b1**.

| Tệp | Việc |
|---|---|
| `huan_luyen_sft.py` | Huấn luyện có giám sát adapter LoRA cho Qwen3-4B (nạp 4-bit); giữ lời nhắc hệ thống dùng chung |
| `loss_theo_doan.py` | Tính loss theo từng đoạn để hạ đỉnh bộ nhớ GPU với chuỗi dài |
| `chon_mo_hinh_bakeoff.py` | So các mô hình bằng số đo, không chọn theo cảm tính |
| `kiem_moi_truong.py` | Kiểm nhanh GPU và mô hình đã sẵn sàng chưa |
| `huan_luyen_dpo.py` | Thử DPO trên cặp lỗi khó, **chưa dùng** trong hệ thống |
| `ham_thuong_rlvr.py` | Hàm thưởng kiểm chứng được cho học tăng cường |

Huấn luyện thực tế chạy trên GPU Kaggle (`kaggle-kernels/`).

---

## 13. Đo lường

Thư mục [`src/do_luong/`](../src/do_luong/). **Mọi con số trong báo cáo đều do các tệp ở đây in ra.**

| Nhóm | Tệp tiêu biểu | Trả lời câu hỏi |
|---|---|---|
| **Thước đo riêng** | `thuoc_do_quy_gan.py`, `chung_chi_thuoc_do.py` | Ghi **đúng người** không? ROUGE chấm 1,0 cho bản đổi dị ứng của mẹ sang con; thước đo này phát hiện được |
| **Bộ chấm** | `cham_he_thong.py`, `cham_diem.py`, `cham_muc_thach_thuc.py` | Đầu ra sai ở đâu: sai người, sai mức, bịa, bỏ sót |
| **Phép đo** | `do_bo_sot.py`, `do_trich.py`, `do_dac.py`, `do_quan_he.py` | Tỷ lệ bỏ sót, chất lượng rút mệnh đề, so các nhánh |
| **Lớp cảnh báo** | `do_canh_bao.py`, `do_cay_loi.py` | Lớp cảnh báo bắt được bao nhiêu lỗi (kể cả lỗi cấy có chủ đích) |
| **Kiểm mô hình "ăn gian"** | `bit_nhan.py`, `do_bit_nhan.py`, `doi_chung_tam_thuong.py` | Mô hình hiểu thật hay chỉ đoán "ai nói thì là của người đó"? |
| **Đối chứng** | `doi_chung_context_vi.py` | So với luật ConText kiểu cũ |
| **Thống kê** | `khoang_tin_cay.py`, `duong_danh_doi.py` | Khoảng tin cậy; đường đánh đổi lỗi ↔ bỏ sót |
| **Chất lượng dữ liệu** | `do_lap_cau.py`, `dau_vet_nguon.py`, `kiem_nghiem_ngoai_khuon.py` | Dữ liệu có lặp, có lộ đề, có đúng trên bệnh ngoài kho không |
| **Kiểm thử đột biến** | `kiem_thu_dot_bien.py` | Cấy lỗi lâm sàng nguy hiểm, đếm các chốt bắt được |
| **Mới thêm 28/11/2026** | `cham_nhieu_nguong.py` | Chấm ghép mệnh đề ở nhiều ngưỡng giống từ, để xem kết luận có phụ thuộc một ngưỡng duy nhất không |
| | `dong_thuan_nhan.py` | Tính độ đồng thuận giữa hai người gán nhãn (Cohen κ, mục tiêu ≥ 0,6). κ đo độ **nhất quán** của nhãn người, không đo độ đúng của hệ thống |
| | `do_sao_chep.py` | Đo các mảnh chữ liên tiếp trùng giữa bản nháp và hội thoại (bản nháp chép lại lời gốc đến mức nào) |

**Phân biệt ba nơi "chấm điểm và duyệt" trong dự án:**

| Nơi | Ai chấm hoặc duyệt | Khi nào |
|---|---|---|
| Bản nháp hồ sơ | Máy chấm (K1–K7, rủi ro, lớp cảnh báo), rồi **bác sĩ duyệt và ký** | Trong lúc khám |
| Đánh giá hệ thống | Bộ chấm `src/do_luong/` so với đáp án | Trước, khi làm báo cáo |
| Tra cứu y khoa | Chấm điểm, lọc tài liệu; kiểm số liệu và số trích dẫn trong câu trả lời (mục 9.1) | Khi bác sĩ hỏi tra cứu |

**Thước đo quy gán — giải thích dễ hiểu.** Người mẹ nói *"Tôi bị dị ứng penicillin. Cháu thì sốt 3 ngày nay."*, máy ghi *"**Cháu** dị ứng penicillin. **Mẹ** sốt 3 ngày."*. ROUGE đếm chữ trùng nên cho **100%** (Section F1 cũng 1,0000 ở 271/271 cặp thử). Thước đo quy gán tách mỗi thông tin thành **"cái gì"** và **"của ai"**, ghép theo "cái gì" trước rồi mới kiểm "của ai", nên phát hiện được hai lỗi nhầm người (điểm giảm 0,138). Hai luật cứng: lệch **phủ định** và lệch **con số** không bao giờ coi là cùng nội dung. Thước đo đã được kiểm trên bệnh án thật: đổi người thì điểm tụt mạnh, đổi từ đồng nghĩa thì chỉ tụt ít. Giới hạn: nhận người bằng danh sách từ (cố ý không nhận "ba", "má", "bác" vì dễ nhầm với "ba ngày", "bác sĩ", "sưng má"); chỉ phân biệt bệnh nhân với người nhà; nhạy với cách gói câu, nên không dùng `f1_quy_gan` một mình để so văn xuôi với bản sinh theo luật.

Kết quả đo lưu ở [`docs/ket-qua/`](ket-qua/).

---

## 14. Công cụ lâm sàng phụ trợ

Thư mục [`src/cong_cu_lam_sang/`](../src/cong_cu_lam_sang/). Đây là các công cụ trong menu **Công cụ** quanh bản nháp. **Chúng chỉ gợi ý, không thay đổi cách dựng bản nháp.** Bảng tri thức thuốc (`data/tri_thuc_thuoc.json`) **chưa được chuyên gia duyệt**.

| Nhóm | Tệp |
|---|---|
| Thuốc | `canh_bao_tuong_tac_thuoc.py`, `di_ung_cheo.py`, `hieu_chinh_lieu.py` (theo thận, gan) |
| Tri thức | `tri_thuc_thuoc.py`, `tra_duoc_thu_aho_corasick.py` (tra Dược thư tại chỗ), `tu_dien_phuong_ngu_lam_sang.py` |
| Xét nghiệm | `doi_soat_can_lam_sang.py`, `chuan_hoa_don_vi_xet_nghiem.py`, `doc_phieu_xet_nghiem.py`, `nap_ket_qua_lis_hl7.py`, `quy_dao_nhieu_lan_kham.py` |
| Thang điểm | `thang_diem_nguy_co.py` (CURB-65, CHA2DS2-VASc, Wells, GCS, Child-Pugh…) |
| BHYT | `tien_kiem_bhyt_va_khoi_phuc_bo_sot.py`, `kiem_toan_xml_bhyt.py` (gói XML1–XML5) |
| Giấy tờ | `to_dan_do_benh_nhan.py`, `cam_doan_thu_thuat.py`, `di_buong_noi_tru.py`, `ho_so_benh_nhan_qr.py` |
| Trong lúc khám | `goi_y_cau_hoi_socrates.py` (gợi ý câu hỏi còn thiếu theo SOCRATES) |
| Liên thông | `xuat_fhir_r4.py` (xuất gói FHIR R4) |

Ràng buộc an toàn chung: thông tin của người nhà (`chu_the_id ≠ 0`) **không bao giờ** được đưa vào mục dị ứng hay thuốc của bệnh nhân, kể cả trong gói FHIR và hồ sơ BHYT.

---

## 15. Các nhánh so sánh A–E

Để chứng minh **mỗi bước có đóng góp thật**, `chay_duong_ong.py` chạy nhiều nhánh. Các nhánh **dùng chung một đầu ra mô hình**, nên chênh lệch giữa chúng chỉ đến từ các bước luật, không lẫn với độ ngẫu nhiên của AI.

| Nhánh | Gồm những gì |
|---|---|
| **A**, **A+** | Mốc đối chứng: mô hình viết thẳng bản nháp văn xuôi |
| **B** | Rút mệnh đề, **không** gom người |
| **C** | B + gom người + luật trạng thái |
| **C_khoa** | C + **kiểm căn cứ K1–K7 + cổng rủi ro**. Chênh lệch C_khoa − C là đóng góp riêng của tầng kiểm |
| **C_khoa_hoi** | C_khoa + gợi ý hỏi lại. **Đây là nhánh dịch vụ thật đang chạy** |
| **D** | C + hậu kiểm (kiểm đầy đủ + sửa cục bộ) |
| **E** | Lấy bản nháp của A, bổ sung và sửa bằng bảng mệnh đề |
| Các biến thể khác | `C_khong_luat`, `C_khong_lien_ket`, `C_ghi_de`, `C_quan_he`… để tắt từng phần một |

---

## 16. Cách chạy

```bash
# Kiểm thử toàn bộ
python -m pytest tests/ -q

# Sinh dữ liệu mô phỏng
python -m src.bo_du_lieu.sinh_hoi_thoai_viet --so-ca 1000 --seed 42

# Chạy đường ống một nhánh
python -m src.duong_ong.chay_duong_ong --nhanh C_khoa ...

# Dịch vụ HTTP tại chỗ
python -m src.he_thong.dich_vu_http --cong 8765

# Giao diện web
cd web && npm install && npm run dev

# Đo lại lớp cảnh báo (ghi docs/ket-qua/canh-bao.json)
python -m src.do_luong.do_canh_bao
```

Không có GPU vẫn xem được demo: trên giao diện bấm **"Xem thử với ca mẫu"**.

---

## 17. Số liệu chính và giới hạn

| Kết quả | Con số | Nguồn |
|---|---|---|
| Bỏ sót mệnh đề (30 ca phát triển, 304 mệnh đề) | 43,1% (chưa huấn luyện) → **11,5%** (có adapter) | `docs/ket-qua/bo-sot-qwen3-4b.md` |
| Thông tin đã bị đính chính mà vẫn còn trong bản nháp | 11,48% → **0,80%** | README |
| Lỗi nguy hiểm lọt vào thân bản nháp, chính sách D | 45,9% (C) → **11,8%** (26/220), tức chặn **88,2%** | `docs/ket-qua/canh-bao.json` |
| Câu đúng bị chặn nhầm | 8,0% (C) → 10,0% (D) | như trên |
| Lớp cảnh báo bắt lỗi cấy, tập giữ kín 240 ca | **0,871** | `docs/ket-qua/cay-loi.md` |
| Thông tin đúng bị kiểm căn cứ chặn oan | 0 / 30.136 | README |

**Giới hạn phải nói rõ:**

- Kết quả **chỉ có hiệu lực trên dữ liệu mô phỏng**; chưa thử trên hội thoại bệnh nhân thật.
- Con số 88,2% đo trên **tập phát triển đã dùng để viết luật**, nên là cận lạc quan.
- Kiểm căn cứ làm **tăng bỏ sót** (4,5% → 7,7% ở bộ "đổi người"): đánh đổi có chủ đích, vì sai nguy hiểm hơn thiếu.
- Trên bản ghi không có lỗi, lớp cảnh báo vẫn đưa ra khoảng 7–8 cảnh báo mỗi ca.
- Mô hình thương mại lớn gán đúng người tốt hơn mô hình 4B của dự án. Dự án **không** khẳng định chính xác hơn; điểm mạnh là **kiểm được từng dòng** và **chạy tại chỗ**.
- 457 khuôn bệnh mở rộng và bảng tri thức thuốc **chưa có chuyên gia duyệt**.

---

## 18. Cách đọc một tệp mã nguồn

Mọi tệp Python trong `src/` mở đầu bằng cùng một khung:

```python
"""[Đường ống dựng bản nháp › Bước 4 – Kiểm căn cứ]       ← thuộc hệ thống nào
Làm gì   : Kiểm mỗi mệnh đề có thật sự được nói …          ← đọc dòng này là đủ hiểu
Vào → Ra : danh sách mệnh đề + lời thoại → đạt / cảnh báo / chặn
Đọc từ   : khoa_ca() …; khoa_mot() là 7 phép kiểm K1–K7    ← nên đọc hàm nào trước
Mục lục (các hàm/lớp chính): …
Gọi tới  : …                                               ← tệp này dùng tệp nào
Dùng bởi : …                                               ← tệp nào dùng tệp này
Tên cũ   : khoa_bang_chung.py (trước 27/11/2026)
────────────────────────────────────────────
(ghi chú chi tiết của tác giả)
"""
```

Trước mỗi hàm có một dòng nhãn để dò nhanh:

```python
# ═══ khoa_mot() — Khoá căn cứ một mệnh đề qua các phép kiểm K1 đến K7 ═══   (hàm chính)
# ─── _thuoc_moi() — Kiểm đoạn có hoạt chất chưa nằm trong mệnh đề ───       (hàm phụ)
```

Tên tệp cũ (trước khi quy hoạch ngày 27/11/2026) vẫn còn trong các bản ghi lịch sử. Bảng đối chiếu tên cũ → tên mới nằm cuối [`BAN_DO_MA_NGUON.md`](../BAN_DO_MA_NGUON.md). Xem lịch sử đầy đủ của một tệp: `git log --follow src/<thư_mục>/<tên>.py`.
