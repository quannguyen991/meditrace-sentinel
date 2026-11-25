# -*- coding: utf-8 -*-
import sys

if sys.stdout:
    sys.stdout.reconfigure(encoding='utf-8')

f_lsc = r"C:\Users\admin\Downloads\MediTrace\Lịch sử câu lệnh.md"
with open(f_lsc, "r", encoding="utf-8") as f:
    t_lsc = f.read()

f_kkm = r"C:\Users\admin\Downloads\MediTrace\Kê khai mã nguồn.md"
with open(f_kkm, "r", encoding="utf-8") as f:
    t_kkm = f.read()

bad_words = [
    "[đã lược", "[đã che", "bị sập", "mặt bác sĩ", "cx dc", "sáng tạo trẻ",
    "nhạy cảm", "k hoạt động", "caid", "thế cũng được, với cả mấy cái đoạn nào"
]

print("=== KIEM TRA LICH SU CAU LENH.MD ===")
for w in bad_words:
    cnt = t_lsc.lower().count(w.lower())
    print(f'  - "{w}": {cnt}')

print("\n=== KIEM TRA KE KHAI MA NGUON.MD ===")
for w in bad_words:
    cnt = t_kkm.lower().count(w.lower())
    print(f'  - "{w}": {cnt}')

print("\n=== DEM SO TEP AI VIET + QUAN TRONG KE KHAI MA NGUON.MD ===")
print("  Tong so tep duoc gan AI viet + Quan:", t_kkm.count("AI viết + Quân"))

print("\n=== KIEM TRA CAC TEP NANG CAP THANG 10 TRONG KE KHAI MA NGUON.MD ===")
oct_files = [
    "can_lam_sang.py", "da_benh_ly.py", "dan_do_benh_nhan.py", "dieu_phoi_ha_tang.py",
    "duoc_ly_lam_sang.py", "fhir_exporter.py", "guardrails.py", "hieu_chinh_lieu.py",
    "khu_dinh_danh.py", "kiem_khuon.py", "thang_diem_lam_sang.py", "tro_ly_lam_sang.py",
    "test_can_lam_sang.py", "test_da_benh_ly.py", "test_dan_do_benh_nhan.py",
    "test_dieu_phoi_ha_tang.py", "test_duoc_ly_lam_sang.py", "test_fhir_exporter.py",
    "test_guardrails.py", "test_hieu_chinh_lieu.py", "test_khu_dinh_danh.py",
    "test_kiem_khuon.py", "test_thang_diem_lam_sang.py", "test_tro_ly_lam_sang.py",
    "tao_bo_anh_flow_meditrace.py", "them_3_ca_kho_bgk.js",
    "NhatKyTienTrinhAIModal.tsx", "ToDanDoBenhNhanModal.tsx"
]
for fn in oct_files:
    in_kkm = fn in t_kkm
    is_quan = f"`{fn}`" in t_kkm and "AI viết + Quân" in [l for l in t_kkm.split("\n") if f"`{fn}`" in l][0] if in_kkm else False
    print(f"  - {fn:32s}: Trong KKM={in_kkm}, AI viet + Quan={is_quan}")
