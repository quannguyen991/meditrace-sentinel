# Trợ lý nhiều tác tử trong ngăn chat — Kế hoạch triển khai

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Thêm vào ngăn chat của MediTrace một trợ lý nhiều tác tử: điều phối (mô hình thương mại) lập kế hoạch và giao việc cho các tác tử tìm kiếm, trả lời, đối chiếu và hai tác tử luật tại chỗ, hiện kế hoạch và tiến độ thật, và chỉ gửi ra ngoài dữ liệu đã ẩn danh.

**Architecture:** Mô-đun mới trong `web/may-chu/tro-ly/`, không đụng hàng GPU của `generate-note`. Lõi (ẩn danh, kiểm kế hoạch, chạy kế hoạch, hai tác tử tại chỗ) là hàm thuần nhận phụ thuộc qua tham số nên thử được bằng mô hình ngoài giả. `server.ts` chỉ nối: tách phần tìm tài liệu và soạn câu trả lời khỏi route `lookup-official` thành hàm dùng chung, thêm điểm cuối `/api/tro-ly`. Giao diện hỏi lại theo mã việc như `generate-note`.

**Tech Stack:** TypeScript (Express, `node:sqlite`, `tsx`), React + Tailwind (đã có), cổng ai-box `qwen3.8-flash` (đã có).

**Spec:** `docs/superpowers/specs/2026-11-23-tro-ly-nhieu-tac-tu-design.md`

## Global Constraints

- Mô hình ngoài chỉ nhận **chuỗi ca ẩn danh** theo mục 5.1 của thiết kế: chỉ mệnh đề thuộc mục `LÝ DO KHÁM BỆNH`, `BỆNH SỬ HIỆN TẠI`, `TIỀN SỬ BỆNH`, `THUỐC ĐANG DÙNG`, `DỊ ỨNG`, `KHÁM LÂM SÀNG`, `CHẨN ĐOÁN`; thuốc kèm liều được phép; nhóm tuổi (`sơ sinh`, `trẻ em`, `người lớn`, `cao tuổi`), giới, có thai được phép; **không** tuổi chính xác, ngày sinh, tên, ngày cụ thể, địa chỉ, nơi làm việc, số liên lạc, mã hồ sơ, tên cơ sở, tên bác sĩ, `trich_dan`, chữ trong hội thoại, chủ thể cụ thể (chỉ "người bệnh" hoặc "người nhà").
- Khâu trích mệnh đề và bản nháp chính luôn do Qwen3-4B tại chỗ làm; không đổi.
- Đường tra cứu ẩn danh luôn mở (không cần công tắc `allowExternal`) nhưng có **công tắc quản trị tắt toàn hệ thống** (khoá `tro_ly_ngoai` trong bảng `cai_dat`, hoặc biến môi trường `MEDITRACE_TRO_LY_NGOAI=tat`). Các việc ngoài khác (`edit-note`, `generate-note-external`, `clinical-qa`, `generate-document`) vẫn cần `allowExternal`, không đổi.
- Điều phối chỉ nhận **hình dạng của ca** (có mệnh đề hay không, có ca hay không) và câu hỏi đã qua máy phát hiện, không nhận nội dung ca.
- Kế hoạch (do mô hình đề xuất) và tiến độ (do code ghi) luôn tách riêng; một bước chỉ thành `xong` sau khi hàm của nó trả về.
- Trần kỹ thuật: tối đa 6 bước mỗi kế hoạch, một vòng sửa của Đối chiếu, `enable_thinking: false` (mặc định hiện nay), thời gian chờ mỗi bước 90 giây. Chưa đặt giới hạn tiền; vẫn ghi token và thời gian.
- Nhật ký chung không ghi chuỗi đã gửi ra ngoài; chỉ ghi tên tác tử, số ký tự, loại mệnh đề đã gửi, kết quả máy phát hiện, thời lượng, mã lỗi.
- Đáp án từ mô hình ngoài mang `source: "mo_hinh_ngoai"` và tên mô hình; không đưa vào phép đo của đề tài; không chẩn đoán, không kê đơn.
- Kho này không có git: mỗi tác vụ kết thúc bằng bước "Ghi nhận" (một dòng vào `docs/tien-do-21-11-2026.md`), không commit.
- Không sửa tệp tiếng Việt bằng PowerShell `Get-Content`/`Set-Content`; không cài thêm gói; chạy kiểm thử trong `D:\Claude\meditrace-ma-nguon\web`: `npx tsx may-chu/tro-ly/<tệp>.test.ts` và `npm run lint`.

## Review Focus

1. **Câu hỏi có danh tính viết nhẹ nhàng** ("chị Lan", "0912 345 678", "ngày 12/10", "số 5 đường Láng"): phải bị chặn, báo bác sĩ viết lại, không gửi. → Task 1.
2. **Mệnh đề thuộc mục không cho phép, hoặc mang trích dẫn và chủ thể cụ thể:** không được xuất hiện trong chuỗi gửi ra. → Task 1.
3. **Điều phối trả kế hoạch bịa** (tác tử lạ, vòng phụ thuộc, quá 6 bước, JSON hỏng, rỗng): dùng kế hoạch dự phòng bằng luật, không lỗi cả việc. → Task 4.
4. **Máy chủ khởi động lại khi một bước tốn tiền đã xong:** chạy lại bỏ qua bước đó, không gọi mô hình ngoài lần hai. → Task 2 và Task 4.
5. **Cổng ngoài lỗi, thiếu khoá, hết thời gian, hoặc công tắc quản trị tắt:** các tác tử cần mô hình ngoài ghi `bo_qua` hoặc `loi`, hai tác tử tại chỗ vẫn chạy, kết quả là câu trả lời một phần. → Task 4 và Task 6.
6. **Bác sĩ bấm gửi hai lần cùng một câu:** không tạo hai việc song song (trùng khoá thì trả lại việc đang chạy). → Task 2.

---

### Task 1: Bộ luật ẩn danh

**Files:**
- Create: `web/may-chu/tro-ly/an-danh.ts`
- Test: `web/may-chu/tro-ly/an-danh.test.ts`

**Interfaces:**
- Produces:
  - `type MenhDeVao = { text?: string; section?: string; negated?: boolean; certainty?: string | null; drug?: string | null; time?: string | null }` (hình dạng của `menhDeChoGiaoDien` ở `server.ts`).
  - `type NguCanhVao = { tuoi?: number | null; gioi?: string | null; coThai?: boolean | null }`.
  - `type CaAnDanh = { nhomTuoi: NhomTuoi | null; gioi: "nam" | "nữ" | null; coThai: boolean | null; dong: string[]; soBo: Record<string, number> }`, trong đó `type NhomTuoi = "sơ sinh" | "trẻ em" | "người lớn" | "cao tuổi"`.
  - `const MUC_CHO_PHEP: readonly string[]` (bảy mục ở Global Constraints).
  - `nhomTuoi(tuoi: number): NhomTuoi` — dưới 1 là `sơ sinh`, 1–15 là `trẻ em`, 16–64 là `người lớn`, từ 65 là `cao tuổi`.
  - `lamSachDong(s: string): string | null` — bỏ tiền tố chủ thể (`^[^:]{1,30}:\s*`), bỏ dạng ngày; trả `null` nếu sau đó vẫn còn dấu hiệu danh tính (email, số điện thoại, chuỗi từ 9 chữ số, "tên là", từ xưng hô theo sau là tên viết hoa).
  - `xayCaAnDanh(menhDe: MenhDeVao[], nguCanh: NguCanhVao): CaAnDanh` — chỉ giữ mệnh đề có `section` thuộc `MUC_CHO_PHEP`; mỗi dòng là nội dung đã làm sạch, thêm "(không)" nếu `negated`, "(nghi ngờ)" nếu `certainty === "nghi ngờ"`; thuốc lấy từ `drug`; `soBo` đếm theo lý do (`muc_khong_cho_phep`, `con_danh_tinh`, `rong`).
  - `kiemCauHoi(cau: string): { ok: true; cau: string } | { ok: false; lyDo: string }` — chặn khi có email, số điện thoại Việt Nam, chuỗi từ 9 chữ số, dạng ngày (`dd/mm`, `dd/mm/yyyy`, "ngày 12 tháng 10"), "tên là", từ xưng hô (`bác|anh|chị|cô|chú|ông|bà|em|cháu|bé|bệnh nhân`) theo sau là từ viết hoa giữa câu, hoặc từ chỉ nơi (`đường|phố|phường|xã|quận|huyện|tỉnh|thành phố`) theo sau là từ viết hoa. Không chặn tên thuốc viết hoa (ví dụ "Augmentin").
  - `chuoiGuiRa(ca: CaAnDanh, cauHoi: string): string` — đúng chuỗi sẽ đưa vào lời gọi, dùng cho bản xem trước và cho tác tử Trả lời.

- [ ] **Step 1: Viết `an-danh.test.ts` (thất bại trước).** Các phép thử, mỗi cái là một khối `assert` kiểu `src/lib/ghepMenhDe.test.ts`:
  - `nhomTuoi`: 0 → `sơ sinh`, 7 → `trẻ em`, 40 → `người lớn`, 70 → `cao tuổi`; ranh giới 1, 15, 16, 64, 65.
  - `kiemCauHoi` chặn (từng câu một, `ok === false`): "chị Lan đau đầu ba ngày", "gọi 0912 345 678", "sinh ngày 12/10/1980", "ở số 5 đường Láng", "bệnh nhân Nguyễn Văn A", "email abc@x.vn", "CCCD 012345678901". Cho qua (`ok === true`): "đau đầu ba ngày kèm sốt, dùng Augmentin 625 mg có phù hợp không", "trẻ 3 tuổi sốt cao co giật nên xử trí thế nào".
  - `xayCaAnDanh`: mệnh đề `section: "KHÁM LÂM SÀNG"` được giữ; `section: "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI"` và `"KẾ HOẠCH ĐIỀU TRỊ"` bị bỏ (đếm trong `soBo.muc_khong_cho_phep`); `text: "bà Hoa: đau đầu (hôm qua)"` ra dòng không còn "bà Hoa"; mệnh đề có `quotes` hay `evidenceTurns` (thêm vào đối tượng vào) không làm xuất hiện chữ trong đó; `drug: "amoxicillin 500 mg"` đi ra đúng nguyên văn.
  - `chuoiGuiRa`: ca có tên "Nguyễn Văn An", số "0912345678" nhét vào `text` của mệnh đề cho phép thì chuỗi cuối **không chứa** "Nguyễn Văn An" và "0912345678" (dòng đó bị bỏ, `soBo.con_danh_tinh` tăng).
  - Phép thử tuổi chính xác: `nguCanh.tuoi = 34` cho chuỗi chứa "người lớn" và **không** chứa "34".
- [ ] **Step 2: Chạy, xác nhận thất bại.** `npx tsx may-chu/tro-ly/an-danh.test.ts` → lỗi không tìm thấy `./an-danh`.
- [ ] **Step 3: Cài các hàm ở khối Interfaces** trong `an-danh.ts`. Dùng danh sách cho phép theo `section`, không "lau sạch" văn bản; `lamSachDong` và `kiemCauHoi` dùng biểu thức chính quy có cờ `u` và lớp `\p{L}` cho chữ có dấu.
- [ ] **Step 4: Chạy lại, PASS.** Mong đợi: `an-danh.test.ts: tất cả đều qua`.
- [ ] **Step 5: `npm run lint`** sạch. Ghi nhận.

### Task 2: Hàng đợi việc trợ lý

**Files:**
- Create: `web/may-chu/tro-ly/kieu.ts`, `web/may-chu/tro-ly/viec-tro-ly.ts`
- Test: `web/may-chu/tro-ly/viec-tro-ly.test.ts`

**Interfaces:**
- Produces (`kieu.ts`):
  - `type TacTuMa = "dieu_phoi" | "tim_kiem" | "tra_loi" | "doi_chieu" | "chu_de_can_ban" | "doi_chieu_thuoc"`.
  - `type TrangThaiBuoc = "cho" | "dang" | "xong" | "bo_qua" | "loi"`.
  - `type Buoc = { ma: string; tacTu: TacTuMa; ten: string; trangThai: TrangThaiBuoc; ghiChu?: string; batDau?: number; ketThuc?: number; dau?: unknown }` (`dau` là kết quả trung gian của bước đã xong, dùng để chạy lại không lặp).
  - `type MucKePhach = { tacTu: TacTuMa; nhiemVu: string; phuThuoc: number[] }`.
  - `type YeuCauTroLy = { cauHoi: string; menhDe: MenhDeVao[]; nguCanh: NguCanhVao; nguon?: Record<string, boolean>; batTacTu: TacTuMa[] }` (`MenhDeVao`, `NguCanhVao` từ `an-danh.ts`).
  - `type TienTrinh = { keHoach: MucKePhach[]; keHoachTuMoHinh: boolean; buoc: Buoc[]; xemTruoc: string | null }`.
  - `type KetQuaTroLy = { phan: Array<{ tacTu: TacTuMa; ten: string; noiDung: string; traLoi?: unknown; canhBao?: string }>; thongKe: { token: number; giay: number; loiGoi: number } }`.
- Produces (`viec-tro-ly.ts`), nhận `db: DatabaseSync` như `hang-doi.ts`: `taoKhoViec(db): KhoViec` với
  - `them(nguoiDungId: number, khoaTrung: string, yeuCau: YeuCauTroLy): number` — trùng `khoaTrung` còn chưa kết thúc thì trả `id` cũ.
  - `layViecTiepTheo(toiDaDongThoi: number): { id: number; nguoiDungId: number; yeuCau: YeuCauTroLy; tienTrinh: TienTrinh | null } | null` — trả `null` khi đã có `toiDaDongThoi` việc `dang_chay`.
  - `ghiTienTrinh(id: number, tt: TienTrinh): void`.
  - `xong(id: number, kq: KetQuaTroLy): void`, `loi(id: number, ma: string): void`.
  - `khoiPhuc(toiDaLanThuNgoai = 1, toiDaLanThuTaiCho = 2): { chayLai: number; thatBai: number }` — việc `dang_chay` về `cho_chay` **giữ nguyên `tien_trinh`**; quá số lần thì `that_bai` với mã `crash_recovery_exhausted`. Việc có bước tốn tiền (`tacTu` thuộc `tim_kiem | tra_loi | doi_chieu | dieu_phoi` đã `xong` hoặc `dang`) dùng ngưỡng ngoài.
  - `trangThai(id: number, nguoiDungId: number): { trangThai: string; tienTrinh: TienTrinh | null; ketQua?: KetQuaTroLy; ma?: string; taoLuc: number } | null`.
  - `xoa(id: number, nguoiDungId: number): void`, `donViecCu(tuoiToiDaMs: number): number`.
- Bảng `viec_tro_ly` tự tạo trong `taoKhoViec`: `id`, `nguoi_dung_id`, `khoa_trung`, `yeu_cau TEXT`, `tien_trinh TEXT`, `ket_qua TEXT`, `trang_thai`, `so_lan_thu`, `ma_loi`, `tao_luc`, `bat_dau_luc`.

- [ ] **Step 1: Viết `viec-tro-ly.test.ts` (thất bại trước)** bằng `:memory:`, kiểu `hang-doi.test.ts`: (a) thêm hai lần cùng `khoaTrung` trả cùng `id` (Review Focus 6); (b) `layViecTiepTheo(2)` lấy tối đa hai việc cùng lúc rồi trả `null`; (c) `ghiTienTrinh` rồi `khoiPhuc()` giữ `tienTrinh` và trả việc về `cho_chay` (Review Focus 4); (d) việc có bước `tim_kiem` đã `xong` bị `that_bai` ở lần `khoiPhuc` thứ hai (ngưỡng ngoài 1), việc chỉ có bước tại chỗ chịu được hai lần; (e) `trangThai` với người dùng khác trả `null`; (f) `xoa` đúng chủ mới xoá; (g) mở lại tệp CSDL tạm giữ nguyên dữ liệu.
- [ ] **Step 2: Chạy, xác nhận thất bại** (`npx tsx may-chu/tro-ly/viec-tro-ly.test.ts`).
- [ ] **Step 3: Cài `kieu.ts` và `viec-tro-ly.ts`.** `layViecTiepTheo` dùng giao dịch `BEGIN IMMEDIATE` như `hang-doi.ts`.
- [ ] **Step 4: Chạy lại, PASS; `npm run lint`.** Ghi nhận.

### Task 3: Hai tác tử luật tại chỗ

**Files:**
- Create: `web/may-chu/tro-ly/tac-tu-tai-cho.ts`
- Test: `web/may-chu/tro-ly/tac-tu-tai-cho.test.ts`

**Interfaces:**
- Consumes: `MenhDeVao` (Task 1).
- Produces:
  - `const CHU_DE: ReadonlyArray<{ ma: string; ten: string; mucLienQuan: string[] }>` — gồm `ly_do` (mục `LÝ DO KHÁM BỆNH`), `benh_su` (`BỆNH SỬ HIỆN TẠI`), `tien_su` (`TIỀN SỬ BỆNH`), `thuoc` (`THUỐC ĐANG DÙNG`), `di_ung` (`DỊ ỨNG`), `gia_dinh` (`TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI`), `kham` (`KHÁM LÂM SÀNG`).
  - `chuDeCanBan(menhDe: MenhDeVao[]): { daBan: Array<{ ma: string; ten: string; soMenhDe: number }>; chuaBan: Array<{ ma: string; ten: string }> }` — chủ đề `daBan` khi có ít nhất một mệnh đề thuộc `mucLienQuan`.
  - `doiChieuThuocDiUng(menhDe: MenhDeVao[]): { thuoc: string[]; diUng: string[]; mauThuan: string[]; thieu: string[] }` — `thuoc` lấy từ trường `drug`; `diUng` lấy từ mệnh đề mục `DỊ ỨNG` có `negated !== true`; `mauThuan` có một dòng khi cùng một tên thuốc xuất hiện với hai liều khác nhau, hoặc khi một tên thuốc trùng một chuỗi trong `diUng` (so không phân biệt hoa thường); `thieu` chứa "chưa có mục dị ứng" khi không có mệnh đề mục `DỊ ỨNG` và "chưa có thuốc đang dùng" khi không có mệnh đề mục `THUỐC ĐANG DÙNG`.

- [ ] **Step 1: Viết phép thử (thất bại trước):** ca chỉ có `LÝ DO KHÁM BỆNH` và `KHÁM LÂM SÀNG` → `chuaBan` gồm `di_ung`, `thuoc`, `tien_su`, `gia_dinh`, `benh_su`; ca đủ mục → `chuaBan` rỗng; `drug: "amoxicillin 500 mg"` và `drug: "amoxicillin 250 mg"` → một dòng trong `mauThuan`; mục `DỊ ỨNG` có "penicillin" và `drug: "Penicillin V 500 mg"` → một dòng trong `mauThuan`; "không dị ứng" (`negated: true`) không vào `diUng`; danh sách rỗng → không lỗi, cả hai chủ đề `thieu`.
- [ ] **Step 2: Chạy, xác nhận thất bại.**
- [ ] **Step 3: Cài `CHU_DE`, `chuDeCanBan`, `doiChieuThuocDiUng`** (hàm thuần, không gọi ra ngoài).
- [ ] **Step 4: Chạy lại, PASS; `npm run lint`.** Ghi nhận.

### Task 4: Điều phối và chạy kế hoạch

**Files:**
- Create: `web/may-chu/tro-ly/dieu-phoi.ts`
- Test: `web/may-chu/tro-ly/dieu-phoi.test.ts`

**Interfaces:**
- Consumes: `an-danh.ts` (`xayCaAnDanh`, `kiemCauHoi`, `chuoiGuiRa`), `tac-tu-tai-cho.ts`, kiểu ở `kieu.ts`.
- Produces:
  - `type Phu = { goiNgoai(heThong: string, nguoiDung: string, maxToken: number): Promise<{ text: string; model: string; usage: { prompt_tokens?: number; completion_tokens?: number } | null; seconds: number }>; datTuKhoa(truyVan: string): Promise<{ tuKhoa: unknown; token: number; giay: number }>; timTaiLieu(tuKhoa: unknown, cauHoi: string, nguon?: Record<string, boolean>): Promise<{ taiLieu: unknown[]; daTra: unknown[]; loiTim: string[]; boLacDe: number; tuKhoaRa: unknown }>; soanTraLoi(args: { cauHoi: string; caAnDanh: string; taiLieu: unknown[]; daTra: unknown[]; boLacDe: number; loiTim: string[]; tuKhoaRa: unknown }): Promise<{ traLoi: unknown; token: number; giay: number }>; ngoaiMo(): boolean; bay(): number }`.
  - `kiemKePhach(raw: unknown, batTacTu: ReadonlySet<TacTuMa>): MucKePhach[] | null` — `null` khi: không phải mảng; rỗng; quá 6 mục; `tacTu` lạ hoặc không nằm trong `batTacTu`; `phuThuoc` trỏ vào chỉ số không tồn tại, trỏ vào chính nó hoặc tạo vòng; `nhiemVu` không phải chuỗi.
  - `kePhachDuPhong(ctx: { coMenhDe: boolean; ngoaiMo: boolean; batTacTu: ReadonlySet<TacTuMa> }): MucKePhach[]` — luật ở thiết kế: có mệnh đề thì thêm `chu_de_can_ban` và `doi_chieu_thuoc`; ngoài mở thì thêm `tim_kiem` → `tra_loi` → `doi_chieu` (phụ thuộc nối tiếp); chỉ thêm tác tử đang bật.
  - `lapKePhach(phu: Phu, yeuCau: YeuCauTroLy, caAnDanh: CaAnDanh, cauHoiDaChe: string): Promise<{ keHoach: MucKePhach[]; tuMoHinh: boolean; token: number; giay: number }>` — gọi điều phối chỉ khi `phu.ngoaiMo()`; lời nhắc hệ thống nói rõ danh sách tác tử và "chỉ trả JSON"; điều phối **chỉ nhận** `cauHoiDaChe` và các cờ `coMenhDe`, `coCa` (không nhận `caAnDanh.dong`); kết quả sai khuôn hoặc `goiNgoai` lỗi thì trả `kePhachDuPhong` với `tuMoHinh: false`.
  - `chayKePhach(phu: Phu, yeuCau: YeuCauTroLy, keHoach: MucKePhach[], tt: TienTrinh, ghi: (tt: TienTrinh) => void): Promise<KetQuaTroLy>` — chạy theo thứ tự phụ thuộc, các mục độc lập chạy song song; **trước mỗi bước** gọi `ghi` với trạng thái `dang`, **sau khi hàm của bước trả về** gọi `ghi` với `xong` và `dau`; bước đã `xong` trong `tt.buoc` (có `dau`) được bỏ qua và dùng lại `dau`; mỗi bước hết 90 giây thì `loi`; một bước lỗi không dừng bước khác; tác tử cần mô hình ngoài mà `phu.ngoaiMo()` sai thì `bo_qua` với `ghiChu: "chưa bật mô hình ngoài"`.
  - `buocChoMucKePhach`: quy ước bước của từng tác tử (tên chữ hiển thị là quyết định của người xây): `tim_kiem` có bước `dat_tu_khoa`, `tim_tai_lieu`; `tra_loi` có `soan_tra_loi`; `doi_chieu` có `kiem_bang_may` (đoạn trích và số liệu khớp, dùng kết quả của `soanTraLoi`) và `xet_tung_y`; `chu_de_can_ban` và `doi_chieu_thuoc` mỗi cái một bước.
  - `doi_chieu` sửa lại tối đa một lần: nếu `xet_tung_y` đánh dấu ý thiếu căn cứ thì gọi `phu.soanTraLoi` thêm đúng một lần với ghi chú các ý thiếu căn cứ, rồi gắn `canhBao` nếu vẫn còn ý thiếu.

- [ ] **Step 1: Viết `dieu-phoi.test.ts` (thất bại trước)** với `Phu` giả ghi lại mọi lời gọi:
  - `kiemKePhach`: chấp nhận `[{tacTu:"tim_kiem",nhiemVu:"x",phuThuoc:[]},{tacTu:"tra_loi",nhiemVu:"y",phuThuoc:[0]}]`; trả `null` cho tác tử lạ (`"hack"`), vòng (`[{..phuThuoc:[1]},{..phuThuoc:[0]}]`), tự phụ thuộc, 7 mục, mảng rỗng, chỉ số ngoài phạm vi, tác tử không nằm trong `batTacTu`. (Review Focus 3)
  - `lapKePhach` với `goiNgoai` giả trả "xin chào" (không phải JSON) → dùng dự phòng, `tuMoHinh === false`; trả JSON hợp lệ → `tuMoHinh === true`; ghi lại `nguoiDung` của lời gọi và khẳng định chuỗi đó **không chứa** nội dung `caAnDanh.dong` (Review Focus 2).
  - `chayKePhach` thứ tự: `tim_kiem` → `tra_loi` → `doi_chieu` ghi trạng thái đúng thứ tự `dang` rồi `xong`; **dấu tích không xuất hiện trước khi hàm trả về** (trong `datTuKhoa` giả, đọc `tt` qua `ghi` và khẳng định bước đó còn `dang`).
  - Một bước lỗi (`timTaiLieu` ném) không làm hỏng `chu_de_can_ban`; kết quả có phần của tác tử tại chỗ và `canhBao` ở phần lỗi. (Review Focus 5)
  - `ngoaiMo() === false`: các tác tử ngoài `bo_qua` với ghi chú, hai tác tử tại chỗ `xong`; `phu.goiNgoai` không được gọi lần nào.
  - Chạy lại với `tt` đã có `dat_tu_khoa` xong và `dau`: `phu.datTuKhoa` không bị gọi lần hai. (Review Focus 4)
  - `doi_chieu` sửa lại đúng một lần khi `xet_tung_y` báo thiếu căn cứ (đếm số lần `soanTraLoi`) và không sửa lần hai.
- [ ] **Step 2: Chạy, xác nhận thất bại.**
- [ ] **Step 3: Cài `dieu-phoi.ts`.** `chayKePhach` dùng `Promise.allSettled` theo từng "đợt" các mục đã đủ phụ thuộc; hết giờ mỗi bước bằng `Promise.race` với bộ đếm giờ.
- [ ] **Step 4: Chạy lại, PASS; `npm run lint`.** Ghi nhận.

### Task 5: Tách phần tìm tài liệu và soạn câu trả lời khỏi `lookup-official`

**Files:**
- Modify: `web/server.ts` (route `app.post("/api/lookup-official", …)` khoảng dòng 1640–1940)

**Interfaces:**
- Produces trong `server.ts` (module-level, cùng tệp, dùng cho cả route cũ và Task 6):
  - `datTuKhoaTraCuu(cauHoi: string, ngucanh: string, caKham: string, coCa: boolean): Promise<{ tuKhoa: any; b1: { text: string; model: string; usage: any; seconds: number } }>` — phần "1. Từ khoá" của route (lời gọi `goiNgoai` đầu tiên và `JSON.parse`).
  - `timTaiLieuTheoTuKhoa(opts: { cauHoi: string; tuKhoa: any; nguon: any }): Promise<{ taiLieu: TaiLieu[]; daTra: Array<{ nguon: string; so: number; ghiChu?: string }>; loiTim: string[]; boLacDe: number; tuKhoaRa: any; kcb: any[]; phacDo: any[]; thuoc: string[]; tenAnh: string }>` — phần "2. Server tự tìm" cùng việc ghép `taiLieu` và `daTra`.
  - `soanTraLoiCoNguon(opts: { cauHoi: string; caKham: string; coCa: boolean; taiLieu: TaiLieu[]; daTra: …; boLacDe: number; loiTim: string[]; tuKhoaRa: any; kcb: any[]; phacDo: any[] }): Promise<{ answer: string; sources: any[]; searched: any[]; cauTruc: any; removedSources: number; warning: string | null; model: string; usage: any; seconds: number }>` — phần "3. Mô hình chỉ tóm tắt" đến câu trả lời cuối. Với Task 6, tham số `caKham` được truyền **chuỗi ca ẩn danh** thay cho hội thoại.
- Route cũ giữ nguyên chữ ký yêu cầu và phản hồi; chỉ gọi lại ba hàm trên.

- [ ] **Step 1: Chụp đường cơ sở.** `npm run lint` sạch; ghi lại hình dạng phản hồi hiện tại từ mã (các khoá `answer, sources, searched, cauTruc, removedSources, warning, searchTerms, source, model, seconds, usage`).
- [ ] **Step 2: Tách ba hàm** theo ranh giới ở khối Interfaces, **không đổi logic**: chuyển nguyên khối mã, thay biến cục bộ bằng tham số, giữ mọi chú thích. Route cũ gọi `datTuKhoaTraCuu` → (nhánh `can_tra_cuu === false` vẫn nằm trong route) → `timTaiLieuTheoTuKhoa` → `soanTraLoiCoNguon` rồi `res.json` với đúng các khoá cũ (`searchTerms` lấy từ `tuKhoaRa`, `source: "mo_hinh_ngoai"`).
- [ ] **Step 3: `npm run lint`** sạch.
- [ ] **Step 4: Thử khói tương đương** (cần khoá ai-box ở `D:/Claude/.secrets/` và mạng): chạy máy chủ thử với CSDL tạm (`MEDITRACE_DB`), đăng nhập bằng tài khoản thử tạo trên máy, gọi `POST /api/lookup-official` với `allowExternal: true` và câu hỏi "tăng huyết áp độ 1 điều trị ban đầu"; mong đợi `answer` không rỗng, `sources.length > 0`, đủ các khoá ở Step 1. Nếu không có khoá hoặc mạng, ghi rõ trong ghi nhận rằng bước này chưa chạy được và dừng ở lint.
- [ ] **Step 5: Ghi nhận.**

### Task 6: Nối máy chủ — điểm cuối, công tắc, bộ chạy

**Files:**
- Modify: `web/server.ts` (thêm điểm cuối và bộ chạy; `import` các mô-đun `tro-ly`)
- Create: `web/may-chu/tro-ly/cai-dat-tro-ly.ts`
- Test: `web/may-chu/tro-ly/cai-dat-tro-ly.test.ts`

**Interfaces:**
- Produces (`cai-dat-tro-ly.ts`), nhận `db: DatabaseSync`:
  - `docCaiDat(db, nguoiDungId: number): { batTacTu: TacTuMa[] }` — mặc định bật cả sáu tác tử (khoá `tro_ly:<id>` trong `cai_dat`).
  - `ghiCaiDat(db, nguoiDungId: number, batTacTu: TacTuMa[]): void` — bỏ giá trị không phải `TacTuMa`.
  - `ngoaiBat(db, env: NodeJS.ProcessEnv): boolean` — `false` khi `env.MEDITRACE_TRO_LY_NGOAI === "tat"` hoặc khoá `tro_ly_ngoai` bằng `"tat"`; mặc định `true`.
  - `ghiNgoaiBat(db, bat: boolean): void`.
- Điểm cuối trong `server.ts`:
  - `GET /api/tro-ly/cai-dat` → `{ batTacTu, ngoaiBat }`; `PUT /api/tro-ly/cai-dat` ghi `batTacTu` của chính người dùng; `PUT /api/tro-ly/cai-dat/ngoai` (chỉ `vai === "quan_tri"`, dùng middleware quản trị đã có ở `tai-khoan.ts`) ghi công tắc toàn hệ thống.
  - `POST /api/tro-ly` nhận `{ cauHoi, menhDe, nguCanh, nguon }` (`nguCanh.tuoi` chỉ dùng để tính nhóm tuổi tại máy chủ, không chuyển tiếp). Chạy `kiemCauHoi`; sai thì `400 { error, code: "cau_hoi_co_danh_tinh", lyDo }`. Đúng thì tạo việc (`khoaTrung` là SHA-256 của người dùng và yêu cầu), kích hoạt bộ chạy, chờ tối đa 20 giây như `generate-note`, rồi trả `200` kèm kết quả hoặc `202 { jobId, tienTrinh }`.
  - `GET /api/tro-ly/:id` trả `{ trangThai, tienTrinh, ketQua?, ma? }` (`202` khi chưa xong); khi xong giao kết quả rồi `xoa` việc, như `giaoKetQuaViec`.
- Bộ chạy: vòng lặp nền như `chayViecNen`, nhưng `layViecTiepTheo(2)`; mỗi việc: `xayCaAnDanh`, `chuoiGuiRa` (lưu vào `tienTrinh.xemTruoc`), `lapKePhach`, `chayKePhach` với `Phu` thật nối vào `goiNgoai`, `datTuKhoaTraCuu`, `timTaiLieuTheoTuKhoa`, `soanTraLoiCoNguon` (Task 5); ghi `ghiNhatKy` một dòng cho mỗi việc theo Global Constraints (không ghi chuỗi gửi). Khi khởi động gọi `khoiPhuc()` rồi kích hoạt bộ chạy.
- `Phu.goiNgoai` thật bỏ qua `chanNeuChuaChoPhep` (đường ẩn danh luôn mở) nhưng kiểm `ngoaiBat(...)`; `Phu.ngoaiMo()` trả `ngoaiBat(...) && Boolean(NGOAI.key && NGOAI.base)`.

- [ ] **Step 1: Viết `cai-dat-tro-ly.test.ts` (thất bại trước)** bằng `:memory:` có bảng `cai_dat`: mặc định bật đủ sáu tác tử; `ghiCaiDat` rồi `docCaiDat` đúng; giá trị rác bị bỏ; `ngoaiBat` mặc định `true`, `false` khi env `tat`, `false` sau `ghiNgoaiBat(db, false)`.
- [ ] **Step 2: Chạy, xác nhận thất bại; cài `cai-dat-tro-ly.ts`; chạy lại, PASS.**
- [ ] **Step 3: Thêm điểm cuối và bộ chạy vào `server.ts`** theo khối Interfaces. Không đổi các điểm cuối cũ.
- [ ] **Step 4: `npm run lint`** sạch; chạy lại mọi `*.test.ts` trong `web/` (`hang-doi`, `an-danh`, `viec-tro-ly`, `tac-tu-tai-cho`, `dieu-phoi`, `cai-dat-tro-ly`, `ghepMenhDe`, `mayTinh`, …).
- [ ] **Step 5: Thử tích hợp có mô hình ngoài giả.** Viết `web/may-chu/tro-ly/tich-hop.test.ts` dựng một `Phu` giả và chạy `lapKePhach` + `chayKePhach` với dữ liệu mẫu có tên và số điện thoại trong `text` của mệnh đề; khẳng định mọi chuỗi mà `Phu.goiNgoai` giả nhận được **không chứa** tên và số đó (kiểm đường ẩn danh đầu cuối).
- [ ] **Step 6: Ghi nhận.**

### Task 7: Giao diện — bảng tác tử, kế hoạch và tiến độ

**Files:**
- Create: `web/src/components/TroLyTacTu.tsx`, `web/src/lib/troLy.ts`
- Modify: `web/src/types.ts` (thêm `troLy?` vào `ClinicalChatMessage`), `web/src/App.tsx` (nhánh `mode === "tra_cuu"` của `handleSendEvidenceMessage`), `web/src/components/ClinicalEvidenceDrawer.tsx` (vẽ thẻ, nút mở bảng, bỏ khoá ô nhập vì đường ẩn danh luôn mở)
- Test: `web/src/lib/troLy.test.ts`

**Interfaces:**
- Produces (`troLy.ts`, hàm thuần, thử được bằng `tsx`):
  - `type BuocHienThi = { ten: string; trangThai: "cho" | "dang" | "xong" | "bo_qua" | "loi"; ghiChu?: string }` và `type TheTienDo = { keHoach: Array<{ tacTu: string; nhiemVu: string }>; keHoachTuMoHinh: boolean; nhom: Array<{ tacTu: string; ten: string; buoc: BuocHienThi[] }>; xemTruoc: string | null }`.
  - `taoTheTienDo(tt: { keHoach: any[]; keHoachTuMoHinh: boolean; buoc: any[]; xemTruoc: string | null }): TheTienDo` — nhóm bước theo tác tử, giữ thứ tự, tên tác tử bằng tiếng Việt (`dieu_phoi` "Điều phối", `tim_kiem` "Tìm kiếm", `tra_loi` "Trả lời", `doi_chieu` "Đối chiếu", `chu_de_can_ban` "Chủ đề cần bàn", `doi_chieu_thuoc` "Đối chiếu thuốc và dị ứng").
  - `hoiTroLy(body: unknown, dangCho: (tt: any) => void): Promise<{ ketQua: any } | { loi: string; code?: string; lyDo?: string }>` — `POST /api/tro-ly`, nếu `202` thì hỏi lại `GET /api/tro-ly/:id` mỗi 1500 ms gọi `dangCho(tienTrinh)` cho đến khi xong hoặc lỗi.
  - `chuyenKetQuaThanhTin(ketQua: any, cauHoi: string): Partial<ClinicalChatMessage>` — phần `tra_loi` có `traLoi.answer`, `sources`, `cauTruc` thì ánh xạ sang `content`, `sources`, `cauTruc`, `warning`, `meta` (ghi "Mô hình ngoài · qwen3.8-flash · … · dữ liệu đã ẩn danh"); các phần khác thành khối thêm trong `content` có tiêu đề theo tác tử.
- `TroLyTacTu.tsx` xuất `BangTacTu` (công tắc bốn đến sáu tác tử, đọc/ghi `GET/PUT /api/tro-ly/cai-dat`, hiện công tắc quản trị khi `vai === "quan_tri"`) và `TheTienDoTroLy` (kế hoạch có nhãn "do mô hình đề xuất", từng nhóm bước có dấu tích ✓ / vòng nét đứt ◌ / ✗, mục xem trước "Dữ liệu gửi ra ngoài" có thể thu gọn).

- [ ] **Step 1: Viết `troLy.test.ts` (thất bại trước).** `taoTheTienDo`: nhóm đúng, bước `dang` có trạng thái `dang`, bước `bo_qua` giữ `ghiChu`, tên tác tử tiếng Việt; `chuyenKetQuaThanhTin` với kết quả có phần `tra_loi` ánh xạ `content`/`sources`/`cauTruc` đúng; kết quả không có phần `tra_loi` (ngoài tắt) vẫn cho `content` không rỗng từ hai tác tử tại chỗ.
- [ ] **Step 2: Chạy, xác nhận thất bại; cài `troLy.ts`; chạy lại, PASS.**
- [ ] **Step 3: Cài `TroLyTacTu.tsx`** (Tailwind theo kiểu các thành phần cạnh nó, không thêm phông chữ; không dùng phông Be Vietnam Pro). Thẻ tiến độ cập nhật theo `dangCho`.
- [ ] **Step 4: Nối vào `App.tsx` và `ClinicalEvidenceDrawer.tsx`.** Nhánh `mode === "tra_cuu"` gọi `hoiTroLy` với `{ cauHoi, menhDe: noteMeta?.propositions ?? [], nguCanh: {}, nguon }`; lỗi `cau_hoi_co_danh_tinh` hiện thông báo yêu cầu viết lại, không thêm tin trợ lý; ô nhập không còn bị khoá bởi `allowExternal` ở đường tra cứu; các chế độ khác giữ nguyên.
- [ ] **Step 5: `npm run lint` sạch.** Chạy `npx tsx src/lib/troLy.test.ts`.
- [ ] **Step 6: Xem bằng trình duyệt trong khung xem trước** (`npm run dev` trên cổng thử với CSDL tạm, tài khoản thử): mở ngăn phải, mở bảng tác tử, bật tắt công tắc, gửi một câu hỏi và quan sát thẻ kế hoạch, tiến độ có dấu tích, câu trả lời kèm thẻ nguồn; gửi câu có tên người thì thấy thông báo chặn. Chụp màn hình cho báo cáo.
- [ ] **Step 7: Ghi nhận.**

### Task 8: Kiểm tra tổng thể và tài liệu

**Files:**
- Modify: `docs/tien-do-21-11-2026.md`, `docs/superpowers/specs/2026-11-23-tro-ly-nhieu-tac-tu-design.md` (ghi các quyết định lệch thiết kế nếu có)

- [ ] **Step 1: Chạy toàn bộ** `npm run lint` và mọi `*.test.ts` trong `web/` (mong đợi không lỗi mới).
- [ ] **Step 2: Chạy toàn bộ Python** `D:\khkt-venv-lap\Scripts\python -m pytest tests -q` (mong đợi không phép thử nào hỏng mới so với trước; ghi số).
- [ ] **Step 3: Đối chiếu thiết kế mục 5.1** từng gạch đầu dòng với mã và phép thử (danh sách cho phép, câu hỏi, xem trước, chỉ nhận ca ẩn danh, không ghi được gì, công tắc quản trị, nhật ký, năm phép thử bắt buộc); ghi gạch nào chưa có phép thử.
- [ ] **Step 4: Viết báo cáo vào `docs/tien-do-21-11-2026.md`:** các tệp đã tạo hoặc sửa, kết quả kiểm thử, ảnh chụp màn hình, việc chưa làm (theo dõi trực tiếp lúc ghi âm, đo chi phí thật, bản xem trước chuỗi gửi ra), và mọi chỗ lệch thiết kế.
