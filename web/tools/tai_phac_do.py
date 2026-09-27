# -*- coding: utf-8 -*-
"""Tai PHAC DO / HUONG DAN CHUYEN MON cua Bo Y te tu kcb.vn ve may, boc chu theo trang.

Vi sao: tim tren kcb.vn chi ra trang gioi thieu quyet dinh; toan van phac do nam o tep PDF dinh
kem. Tai san ve de server tra duoc NOI DUNG phac do (truyen dich, lieu, chi dinh…), khong chi link.

NGUON — chi ten mien nha nuoc (.gov.vn), khong lay tu trang tong hop tu nhan:
  kcb.vn             Cuc Quan ly Kham, chua benh — Bo Y te (nhieu tep cu da hong lien ket)
  syt.gialai.gov.vn  So Y te Gia Lai: thu vien "Huong dan chan doan dieu tri, Quy trinh ky thuat…",
                     dang lai NGUYEN VAN quyet dinh cua Bo Y te kem tep (bo sung 24/09/2026)
  TRUC_TIEP          vai tep le tren trang So Y te khac, tim bang tim kiem web, kiem tay
Tep nen (.rar) va ban scan khong co lop chu thi GHI RO la chua doc duoc, khong bo qua im lang.

    python tools/tai_phac_do.py            # tai them nhung gi chua co
    python tools/tai_phac_do.py --lam-lai  # boc chu lai tu cac PDF da tai

Ra:
    data/phac-do/pdf/<ma>.pdf
    data/phac-do/muc-luc.json      danh sach van ban: tieu de, nam, so trang, trang thai
    data/phac-do/doan.jsonl        moi dong mot TRANG: {ma, tieu_de, nam, trang, van, url_trang, url_pdf}
Can: pypdf.
"""
import argparse
import hashlib
import html
import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent / "data" / "phac-do"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126 MediTrace-phac-do"
TRAN_MB = 80

# Benh / chuyen khoa thuong gap o phong kham. Them tu khoa vao day de mo rong thu vien.
TU_KHOA = [
    "tăng huyết áp", "đái tháo đường", "hen phế quản", "bệnh phổi tắc nghẽn mạn tính", "viêm phổi",
    "sốt xuất huyết Dengue", "tay chân miệng", "viêm gan vi rút B", "viêm gan vi rút C", "suy tim",
    "đột quỵ", "nhồi máu cơ tim", "rung nhĩ", "lao", "sốt rét", "sởi", "cúm", "COVID-19",
    "tiêu chảy cấp", "nhiễm khuẩn tiết niệu", "viêm dạ dày", "loét dạ dày tá tràng", "bệnh thận mạn",
    "rối loạn lipid máu", "gút", "viêm khớp dạng thấp", "loãng xương", "thiếu máu", "trầm cảm",
    "động kinh", "sốc phản vệ", "nhiễm khuẩn huyết", "bệnh hô hấp", "nội khoa", "nhi khoa",
    "da liễu", "bệnh về mắt", "tai mũi họng", "sản phụ khoa", "thần kinh", "tiêu hóa", "tim mạch",
    "nội tiết", "truyền nhiễm", "ngộ độc", "cấp cứu",
]


NOI_DANG_KCB = "Cục Quản lý Khám, chữa bệnh (kcb.vn)"
NOI_DANG_GL = "Sở Y tế Gia Lai (syt.gialai.gov.vn) — đăng lại văn bản Bộ Y tế"
THU_VIEN_GL = ("https://syt.gialai.gov.vn/index.php/vi/download/"
               "Thu-vien-Huong-dan-chan-doan-dieu-tri-Quy-trinh-ky-thuat-va-cac-Tai-lieu-chuyen-mon-kham-chua-benh/")
# Tep le tren trang .gov.vn khac, tim duoc bang tim kiem web ngay 24/09/2026.
TRUC_TIEP = [
    {"tieu_de": "Hướng dẫn chẩn đoán và điều trị suy tim cấp và mạn (QĐ 1857/QĐ-BYT)", "nam": 2022,
     "url_trang": "https://soyte.hungyen.gov.vn/",
     "url_tep": "https://soyte.hungyen.gov.vn/portal/VanBan/2022-07/ef8ae3311d0bcfddPh%C3%A1c%20%20%20%20Suy%20tim%202022%20c%20a%20B%20%20Y%20t%20%20b%20n%20Final%2022.6.2022.signed.pdf",
     "noi_dang": "Sở Y tế Hưng Yên (soyte.hungyen.gov.vn) — bản có chữ ký số"},
]
LIEN_QUAN = re.compile(r"chẩn đoán|điều trị|phác đồ|xử trí|quy trình lâm sàng", re.I)


def _nfc(s):
    return unicodedata.normalize("NFC", s or "")


def lay(url, nhi_phan=False, giay=40):
    # Duong dan tep co chu tieng Viet ("Hướng-dẫn-….pdf"): phai ma hoa, khong thi urllib bao loi ascii.
    url = urllib.parse.quote(url, safe=":/?&=%#+,;@")
    yc = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(yc, timeout=giay) as r:
        du = r.read()
    return du if nhi_phan else du.decode("utf-8", "replace")


def tim_trang(tu_khoa):
    """-> [(url trang, tieu de)] cac trang van ban / tai lieu chuyen mon cho mot tu khoa."""
    ra = []
    for truy_van in (f"hướng dẫn chẩn đoán và điều trị {tu_khoa}", tu_khoa):
        q = urllib.parse.quote_plus(truy_van)
        try:
            t = lay(f"https://kcb.vn/?keyword={q}&site=2005611&page=search")
        except Exception as exc:
            print(f"  ! tim '{truy_van}': {exc}")
            continue
        for m in re.finditer(r'href="(/(?:van-ban|tin-tuc)/[^"?]+\.html)[^"]*"[^>]*title="([^"]+)"', t):
            ten = html.unescape(m.group(2)).strip()
            if re.search(r"hướng dẫn|phác đồ|tài liệu chuyên môn|quyết định", ten, re.I) and \
                    re.search(r"chẩn đoán|điều trị|phác đồ|xử trí", ten, re.I):
                ra.append((f"https://kcb.vn{m.group(1)}", ten))
        time.sleep(0.5)
    return ra


def tep_dinh_kem(url_trang):
    t = lay(url_trang)
    tep = []
    for m in re.finditer(r'href="([^"]+\.(?:pdf|rar|zip|docx?))"', t, re.I):
        u = m.group(1)
        if "thumbnail" in u:
            continue
        tep.append(urllib.parse.urljoin("https://kcb.vn/", u))
    chu = html.unescape(re.sub(r"<[^>]+>", " ", t))
    return list(dict.fromkeys(tep)), chu


def _nam_trong_ten(ten):
    m = re.search(r"\d{1,2}/\d{1,2}/(\d{4})|năm (\d{4})", ten or "")
    return int(m.group(1) or m.group(2)) if m else None


def nam_ban_hanh(*van):
    for v in van:
        m = re.search(r"(?:QĐ-BYT|Quyết định)[^\n]{0,80}?năm\s+(\d{4})", v or "") or \
            re.search(r"/QĐ-BYT\s+ngày\s+\d{1,2}[/-]\d{1,2}[/-](\d{4})", v or "")
        if m:
            return int(m.group(1))
    return None


def thu_vien_gia_lai():
    """-> [(url trang, tieu de)] moi van ban chan doan / dieu tri trong thu vien So Y te Gia Lai."""
    muc = {}
    for n in range(1, 80):
        try:
            t = lay(THU_VIEN_GL if n == 1 else f"{THU_VIEN_GL}page-{n}/")
        except Exception as exc:
            print(f"  ! Gia Lai trang {n}: {exc}")
            break
        moi = 0
        for m in re.finditer(r'href="(/vi/download/Thu-vien-Huong-dan[^"/]*/[^"]+\.html)"[^>]*>([^<]{10,400})<', t):
            if m.group(1) not in muc:
                muc[m.group(1)] = re.sub(r"\s+", " ", html.unescape(m.group(2))).strip()
                moi += 1
        if not moi:
            break
        time.sleep(0.3)
    return [(f"https://syt.gialai.gov.vn{u}", ten) for u, ten in muc.items() if LIEN_QUAN.search(ten)]


def tai_gia_lai(url_trang):
    """Tep dinh kem cua mot van ban Gia Lai. He thong NukeViet can COOKIE PHIEN cua lan mo trang
    truoc khi cho tai (op=down) — mo trang bang cung mot opener giu cookie."""
    import http.cookiejar
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    op.addheaders = [("User-Agent", UA)]
    t = op.open(urllib.parse.quote(url_trang, safe=":/?&=%#+,;@"), timeout=40).read().decode("utf-8", "replace")
    ra = []
    for ten_tep in dict.fromkeys(re.findall(r"nv_download_file\('idown',\s*'([^']+)'\)", t)):
        u = ("https://syt.gialai.gov.vn/index.php?language=vi&nv=download&op=down&filename="
             + urllib.parse.quote(ten_tep))
        yc = urllib.request.Request(u, headers={"Referer": url_trang})
        try:
            du = op.open(yc, timeout=240).read()
        except Exception as exc:
            ra.append((ten_tep, None, f"lỗi tải: {exc}"))
            continue
        ra.append((ten_tep, du, None))
        time.sleep(0.3)
    chu = html.unescape(re.sub(r"<[^>]+>", " ", t))
    return ra, chu


def boc_chu(pdf_path):
    from pypdf import PdfReader
    r = PdfReader(str(pdf_path))
    trang = []
    for i, p in enumerate(r.pages):
        try:
            v = p.extract_text() or ""
        except Exception:
            v = ""
        v = _nfc(re.sub(r"[ \t]+", " ", v)).strip()
        trang.append(v)
    return trang


def main():
    sys.stdout = __import__("io").TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--lam-lai", action="store_true", help="chi boc chu lai tu PDF da tai")
    a = ap.parse_args()
    (GOC / "pdf").mkdir(parents=True, exist_ok=True)
    tep_ml = GOC / "muc-luc.json"
    muc_luc = json.loads(tep_ml.read_text(encoding="utf-8")) if tep_ml.exists() else {}

    if not a.lam_lai:
        # Thu tai lai nhung tep lan truoc loi tai (khong tim lai trang).
        for ma, muc in muc_luc.items():
            if not str(muc.get("trang_thai", "")).startswith("lỗi tải"):
                continue
            dich = GOC / "pdf" / f"{ma}.pdf"
            try:
                du = lay(muc["url_tep"], nhi_phan=True, giay=180)
                if not du.startswith(b"%PDF"):
                    muc["trang_thai"] = "liên kết hỏng (không phải PDF)"
                elif len(du) > TRAN_MB * 2 ** 20:
                    muc["trang_thai"] = f"quá lớn (> {TRAN_MB} MB)"
                else:
                    dich.write_bytes(du)
                    muc["trang_thai"] = "đã tải"
            except Exception as exc:
                muc["trang_thai"] = f"lỗi tải: {exc}"
            print(f"  ~ {muc['tieu_de'][:70]} [{muc['trang_thai']}]")
            time.sleep(0.3)
        trang_da = {v["url_trang"] for v in muc_luc.values()}
        cac_trang = {}
        for k in TU_KHOA:
            for u, ten in tim_trang(k):
                cac_trang.setdefault(u, ten)
            print(f"tìm '{k}': tổng {len(cac_trang)} trang")
        # --- Nguon 2: thu vien So Y te Gia Lai
        for u, ten in thu_vien_gia_lai():
            if u in trang_da:
                continue
            try:
                tep, chu_trang = tai_gia_lai(u)
            except Exception as exc:
                print(f"  ! {u}: {exc}")
                continue
            for ten_tep, du, loi in tep:
                ma = hashlib.sha1(f"{u}|{ten_tep}".encode()).hexdigest()[:12]
                muc = {"ma": ma, "tieu_de": ten, "url_trang": u, "url_tep": u, "ten_tep": ten_tep,
                       "noi_dang": NOI_DANG_GL, "nam": nam_ban_hanh(ten, chu_trang) or _nam_trong_ten(ten)}
                if loi:
                    muc["trang_thai"] = loi
                elif not du.startswith(b"%PDF"):
                    muc["trang_thai"] = f"chưa đọc được (tệp .{ten_tep.rsplit('.', 1)[-1].lower()})"
                elif len(du) > TRAN_MB * 2 ** 20:
                    muc["trang_thai"] = f"quá lớn (> {TRAN_MB} MB)"
                else:
                    (GOC / "pdf" / f"{ma}.pdf").write_bytes(du)
                    muc["trang_thai"] = "đã tải"
                muc_luc[ma] = muc
                print(f"  + [Gia Lai] {ten[:80]} [{muc['trang_thai']}]")
        # --- Nguon 3: tep le tren trang .gov.vn khac
        for d in TRUC_TIEP:
            ma = hashlib.sha1(d["url_tep"].encode()).hexdigest()[:12]
            if ma in muc_luc and muc_luc[ma].get("trang_thai") in ("đã tải", "đọc được"):
                continue
            muc = {"ma": ma, **d}
            try:
                du = lay(d["url_tep"], nhi_phan=True, giay=180)
                if du.startswith(b"%PDF"):
                    (GOC / "pdf" / f"{ma}.pdf").write_bytes(du)
                    muc["trang_thai"] = "đã tải"
                else:
                    muc["trang_thai"] = "liên kết hỏng (không phải PDF)"
            except Exception as exc:
                muc["trang_thai"] = f"lỗi tải: {exc}"
            muc_luc[ma] = muc
            print(f"  + [trực tiếp] {d['tieu_de'][:80]} [{muc['trang_thai']}]")

        for u, ten in cac_trang.items():
            if u in trang_da:
                continue
            try:
                tep, chu_trang = tep_dinh_kem(u)
            except Exception as exc:
                print(f"  ! {u}: {exc}")
                continue
            if not tep:
                continue
            for url_tep in tep:
                ma = hashlib.sha1(url_tep.encode()).hexdigest()[:12]
                muc = {"ma": ma, "tieu_de": ten, "url_trang": u, "url_tep": url_tep,
                       "nam": nam_ban_hanh(ten, chu_trang)}
                duoi = url_tep.rsplit(".", 1)[-1].lower()
                if duoi != "pdf":
                    muc.update(trang_thai=f"chưa đọc được (tệp .{duoi})")
                    muc_luc[ma] = muc
                    continue
                dich = GOC / "pdf" / f"{ma}.pdf"
                try:
                    if not dich.exists():
                        du = lay(url_tep, nhi_phan=True, giay=180)
                        if not du.startswith(b"%PDF"):
                            muc.update(trang_thai="liên kết hỏng (không phải PDF)")
                            muc_luc[ma] = muc
                            continue
                        if len(du) > TRAN_MB * 2 ** 20:
                            muc.update(trang_thai=f"quá lớn (> {TRAN_MB} MB)")
                            muc_luc[ma] = muc
                            continue
                        dich.write_bytes(du)
                    muc.update(trang_thai="đã tải")
                except Exception as exc:
                    muc.update(trang_thai=f"lỗi tải: {exc}")
                muc_luc[ma] = muc
                print(f"  + {ten[:70]} [{muc['trang_thai']}]")
                time.sleep(0.5)

    # Boc chu moi PDF da tai -> doan.jsonl (ghi lai toan bo moi lan)
    so_doc = 0
    with open(GOC / "doan.jsonl", "w", encoding="utf-8") as f:
        for ma, muc in muc_luc.items():
            dich = GOC / "pdf" / f"{ma}.pdf"
            if not dich.exists():
                continue
            try:
                trang = boc_chu(dich)
            except Exception as exc:
                muc["trang_thai"] = f"lỗi đọc PDF: {exc}"
                continue
            muc["so_trang"] = len(trang)
            co_chu = [t for t in trang if len(t) > 150]
            if len(co_chu) < max(1, len(trang) // 5):
                muc["trang_thai"] = "bản scan, không có lớp chữ — chưa đọc được"
                continue
            muc["trang_thai"] = "đọc được"
            muc["nam"] = muc.get("nam") or nam_ban_hanh(" ".join(trang[:2]))
            so_doc += 1
            for i, v in enumerate(trang, 1):
                if len(v) > 80:
                    f.write(json.dumps({"ma": ma, "tieu_de": muc["tieu_de"], "nam": muc.get("nam"), "trang": i,
                                        "noi_dang": muc.get("noi_dang", NOI_DANG_KCB),
                                        "van": v[:4000], "url_trang": muc["url_trang"],
                                        "url_pdf": muc["url_tep"]}, ensure_ascii=False) + "\n")
    tep_ml.write_text(json.dumps(muc_luc, ensure_ascii=False, indent=1), encoding="utf-8")
    dem = {}
    for m in muc_luc.values():
        k = m.get("trang_thai", "?").split(" (")[0].split(":")[0]
        dem[k] = dem.get(k, 0) + 1
    print(f"\n{len(muc_luc)} tệp; đọc được {so_doc}; theo trạng thái: {dem}")


if __name__ == "__main__":
    main()
