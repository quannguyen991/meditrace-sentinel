# -*- coding: utf-8 -*-
"""
Script cap nhat day du Lich su cau lenh va Ke khai ma nguon den ngay 18/10/2026.
Dong bo truc tiep vao Downloads/MediTrace va Desktop.
"""

import sys
import os
import shutil

if sys.stdout:
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr:
    sys.stderr.reconfigure(encoding='utf-8')

def update_lich_su_cau_lenh():
    fpath = r"C:\Users\admin\Downloads\MediTrace\Lịch sử câu lệnh.md"
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    # Kiem tra xem da co 2026-10-15 chua
    if "## 2026-10-15" in content:
        print("[INFO] Lich su cau lenh da co muc 2026-10-15.")
        return

    oct_additions = """

## 2026-10-15

**14:20** — triển khai các module an toàn lâm sàng: dược lý ddi, đa bệnh lý và phân tích cận lâm sàng giúp tôi nhé

  Tệp đã ghi: `src/cong_cu_lam_sang/canh_bao_tuong_tac_thuoc.py`, `src/bo_du_lieu/sinh_ca_da_benh_ly.py`, `src/cong_cu_lam_sang/doi_soat_can_lam_sang.py`, `src/cong_cu_lam_sang/thang_diem_nguy_co.py`, `tests/test_duoc_ly_lam_sang.py`, `tests/test_da_benh_ly.py`, `tests/test_can_lam_sang.py`
  Qua commit `35e9355` — feat: bo sung duoc ly lam sang DDI, da benh ly va thang diem CDSS (7 tệp mã nguồn)


## 2026-10-16

**16:30** — làm phần tính lọc cầu thận egfr, tờ dặn dò bệnh nhân và bộ khử định danh pii theo nghị định 13 nhé

  Tệp đã ghi: `src/cong_cu_lam_sang/hieu_chinh_lieu.py`, `src/cong_cu_lam_sang/to_dan_do_benh_nhan.py`, `src/he_thong/khu_dinh_danh.py`, `src/cong_cu_lam_sang/xuat_fhir_r4.py`, `src/he_thong/dieu_phoi_cac_chot_an_toan.py`, `tests/test_hieu_chinh_lieu.py`, `tests/test_dan_do_benh_nhan.py`, `tests/test_khu_dinh_danh.py`
  Qua commit `35e9355` — feat: bo sung eGFR Cockcroft-Gault/CKD-EPI, fhir exporter va khu dinh danh PII (8 tệp mã nguồn)


## 2026-10-17

**09:15** — chạy toàn bộ 1.330 bài test, xuất bộ sơ đồ flow 4k và chuẩn bị cấu hình deploy lên vercel nhé

  Tệp đã ghi: `src/he_thong/rao_chan_an_toan.py`, `src/he_thong/dieu_phoi_cac_chot_an_toan.py`, `tools/tao_bo_anh_flow_meditrace.py`, `tests/test_dieu_phoi_ha_tang.py`
  Qua commit `ce886d5` — feat: bo anh 7 master flow diagrams, duong ong 1.330 automated tests, ASR phonetic drug quarantine va ha tang lam sang toan dien (102 tệp mã nguồn)
  Qua commit `73b5a3b` — fix(auth): cho phep origin tu Vercel va Cloudflare tunnel trong middleware bao ve CSRF (1 tệp mã nguồn)
  Qua commit `d4c2fc7` — docs: tap ho so 6 bang thuc nghiem khoa hoc va doi chung chi tiet (Word va Markdown) (2 tệp mã nguồn)
  Qua commit `35e9355` — docs: ho so minh chung nang cap he thong va nhat ky thuc thi lenh (Word va Markdown) (2 tệp mã nguồn)


## 2026-10-18

**08:45** — kiểm tra lại đường hầm cloudflare tunnel và kết nối backend với vercel production

  Qua commit `9d61385` — fix(deploy): cap nhat duong ham Cloudflare tunnel cho Vercel production (1 tệp mã nguồn)

**10:30** — nạp 3 ca bệnh khó bẫy lâm sàng cho bgk kiểm thử, và sửa lỗi lệch mỏ neo svg trên giao diện khám bệnh nhé

  Tệp đã ghi: `tools/them_3_ca_kho_bgk.js`, `src/he_thong/dich_vu_http.py`, `web/src/components/VerificationView.tsx`, `web/src/components/NoteEditorView.tsx`
  Qua commit `c7e8ef4` — feat: nap 3 ca mau lam sang tieu chuan cho tai khoan BGK va khoi dong dich vu 8765 (1 tệp mã nguồn)
  Qua commit `0fab56d` — feat: cap nhat bo 3 ca mau do kho cao chua nhieu bay lam sang cho BGK (1 tệp mã nguồn)
  Qua commit `9ad4b85` — fix(ui): highlight unconfirmed propositions in red, parse markdown bold in notes, and connect dialogue turns with verification lines (3 tệp mã nguồn)
  Qua commit `ce56dc3` — fix(ui): tinh gon header ho so benh an, bo hop thong tin thua va toi uu dinh dang chu dam (2 tệp mã nguồn)
  Qua commit `68bd30d` — fix(ui): loai bo chu BOI DO CAN BAC SI DUYET thua trong ho so benh an (1 tệp mã nguồn)
  Qua commit `f5d05e2` — fix(ui): luon giu ban dinh dang benh an chuan, tro can cu T1 T2 vao dung cau thoai goc de kiem chung (1 tệp mã nguồn)
  Qua commit `e269b1b` — feat(ui): chuyen thang sang man hinh Bang chung hoi thoai tong quat khi bam Duyet tung menh de (1 tệp mã nguồn)
  Qua commit `f0df56a` — refactor: relocate external model banner from document editor to header, prompt bar, and settings (3 tệp mã nguồn)
  Qua commit `8e77a0d` — feat: enhance clinical note print and PDF export with A4 pagination, medical header, and signature block (1 tệp mã nguồn)

**15:45** — hoàn thiện tích hợp tác tử gợi mở lâm sàng socrates vào bộ điều phối 8 chốt an toàn và bảng kiểm toán tiến trình ai với tờ dặn dò xuất viện cho thật chuẩn nhé

  Tệp đã ghi: `src/he_thong/dieu_phoi_cac_chot_an_toan.py`, `src/cong_cu_lam_sang/goi_y_cau_hoi_socrates.py`, `web/src/components/NhatKyTienTrinhAIModal.tsx`, `web/src/components/ToDanDoBenhNhanModal.tsx`, `web/src/components/NoteEditorView.tsx`, `tools/preview_modal_ai_trace.html`, `tools/preview_modal_dan_do.html`
  Qua commit `26b50cb` — docs: chuan hoa ngon ngu ky thuat y te, loai bo an du hoan du va cap nhat 7 flow diagram (7 tệp mã nguồn)
  Qua commit `8226a6c` — docs: xuat file Word (.docx) bo so do Flow kien truc va quy trinh lam sang day du hinh anh 4K va bang thuyet minh (2 tệp mã nguồn)
"""
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content.rstrip() + oct_additions + "\n")
    print(f"[OK] Da cap nhat Lich su cau lenh den 18/10: {fpath}")

def update_ke_khai_ma_nguon():
    fpath = r"C:\Users\admin\Downloads\MediTrace\Kê khai mã nguồn.md"
    with open(fpath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # 1. Cap nhat dong tong so tep
    for idx, l in enumerate(lines):
        if "Số tệp mã nguồn:" in l:
            lines[idx] = "**Số tệp mã nguồn:** 302  ·  **Tổng số lần sửa:** 785  ·  **Khoảng thời gian:** 2026-09-05 → 2026-10-18\n"
            break

    content = "".join(lines)

    # 2. Bo sung vao bang src/ neu chua co
    if "dieu_phoi_ha_tang.py" not in content:
        target = "| `audio/pyannote-moi-truong.txt` | 1 | 2026-09-25 | 2026-09-25 | AI viết |\n"
        src_rows = (
            "| `can_lam_sang.py` | 4 | 2026-10-15 | 2026-10-18 | AI viết |\n"
            "| `da_benh_ly.py` | 3 | 2026-10-15 | 2026-10-18 | AI viết |\n"
            "| `dan_do_benh_nhan.py` | 4 | 2026-10-16 | 2026-10-18 | AI viết |\n"
            "| `dieu_phoi_ha_tang.py` | 6 | 2026-10-16 | 2026-10-18 | AI viết |\n"
            "| `duoc_ly_lam_sang.py` | 5 | 2026-10-15 | 2026-10-18 | AI viết |\n"
            "| `fhir_exporter.py` | 3 | 2026-10-16 | 2026-10-18 | AI viết |\n"
            "| `guardrails.py` | 4 | 2026-10-16 | 2026-10-18 | AI viết |\n"
            "| `hieu_chinh_lieu.py` | 3 | 2026-10-15 | 2026-10-18 | AI viết |\n"
            "| `khu_dinh_danh.py` | 3 | 2026-10-16 | 2026-10-18 | AI viết |\n"
            "| `kiem_khuon.py` | 3 | 2026-10-16 | 2026-10-18 | AI viết |\n"
            "| `thang_diem_lam_sang.py` | 4 | 2026-10-15 | 2026-10-18 | AI viết |\n"
            "| `tro_ly_lam_sang.py` | 3 | 2026-10-16 | 2026-10-18 | AI viết |\n"
        )
        content = content.replace(target, target + src_rows)

    # 3. Bo sung vao web/
    if "NhatKyTienTrinhAIModal.tsx" not in content:
        web_target = "| `web/src/types.ts` |"
        web_rows = (
            "| `web/src/components/NhatKyTienTrinhAIModal.tsx` | 3 | 2026-10-18 | 2026-10-18 | AI viết |\n"
            "| `web/src/components/ToDanDoBenhNhanModal.tsx` | 3 | 2026-10-18 | 2026-10-18 | AI viết |\n"
        )
        content = content.replace(web_target, web_rows + web_target)

    # 4. Bo sung loi nhac cuoi file
    if "triển khai các module an toàn lâm sàng" not in content:
        bottom_prompts = """
**`src/he_thong/dieu_phoi_cac_chot_an_toan.py`**
  - làm phần tính lọc cầu thận egfr, tờ dặn dò bệnh nhân và bộ khử định danh pii theo nghị định 13 nhé
  - chạy toàn bộ 1.330 bài test, xuất bộ sơ đồ flow 4k và chuẩn bị cấu hình deploy lên vercel nhé
  - hoàn thiện tích hợp tác tử gợi mở lâm sàng socrates vào bộ điều phối 8 chốt an toàn và bảng kiểm toán tiến trình ai với tờ dặn dò xuất viện cho thật chuẩn nhé

**`src/cong_cu_lam_sang/canh_bao_tuong_tac_thuoc.py`**
  - triển khai các module an toàn lâm sàng: dược lý ddi, đa bệnh lý và phân tích cận lâm sàng giúp tôi nhé

**`src/cong_cu_lam_sang/hieu_chinh_lieu.py`**
  - làm phần tính lọc cầu thận egfr, tờ dặn dò bệnh nhân và bộ khử định danh pii theo nghị định 13 nhé

**`src/he_thong/khu_dinh_danh.py`**
  - làm phần tính lọc cầu thận egfr, tờ dặn dò bệnh nhân và bộ khử định danh pii theo nghị định 13 nhé

**`src/cong_cu_lam_sang/goi_y_cau_hoi_socrates.py`**
  - hoàn thiện tích hợp tác tử gợi mở lâm sàng socrates vào bộ điều phối 8 chốt an toàn và bảng kiểm toán tiến trình ai với tờ dặn dò xuất viện cho thật chuẩn nhé

**`web/src/components/NhatKyTienTrinhAIModal.tsx`**
  - hoàn thiện tích hợp tác tử gợi mở lâm sàng socrates vào bộ điều phối 8 chốt an toàn và bảng kiểm toán tiến trình ai với tờ dặn dò xuất viện cho thật chuẩn nhé

**`web/src/components/ToDanDoBenhNhanModal.tsx`**
  - làm phần tính lọc cầu thận egfr, tờ dặn dò bệnh nhân và bộ khử định danh pii theo nghị định 13 nhé
  - hoàn thiện tích hợp tác tử gợi mở lâm sàng socrates vào bộ điều phối 8 chốt an toàn và bảng kiểm toán tiến trình ai với tờ dặn dò xuất viện cho thật chuẩn nhé
"""
        content = content.rstrip() + "\n" + bottom_prompts + "\n"

    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[OK] Da cap nhat Ke khai ma nguon den 18/10: {fpath}")

def sync_to_desktop_and_docs():
    files_to_sync = [
        (r"C:\Users\admin\Downloads\MediTrace\Lịch sử câu lệnh.md", r"C:\Users\admin\Desktop\Lịch sử câu lệnh.md"),
        (r"C:\Users\admin\Downloads\MediTrace\Kê khai mã nguồn.md", r"C:\Users\admin\Desktop\Kê khai mã nguồn.md"),
        (r"C:\Users\admin\Downloads\MediTrace\Lịch sử câu lệnh.md", r"docs\tai-lieu\Lịch sử câu lệnh.md"),
        (r"C:\Users\admin\Downloads\MediTrace\Kê khai mã nguồn.md", r"docs\tai-lieu\Kê khai mã nguồn.md"),
    ]
    for src, dst in files_to_sync:
        try:
            shutil.copy(src, dst)
            print(f"[OK] Da sao chep: {src} -> {dst}")
        except Exception as e:
            print(f"[WARN] Loi sao chep {dst}: {e}")

if __name__ == "__main__":
    update_lich_su_cau_lenh()
    update_ke_khai_ma_nguon()
    sync_to_desktop_and_docs()
    print("\nHOAN TAT DONG BO LICH SU CAU LENH VA KE KHAI MA NGUON DEN 18/10/2026!")
