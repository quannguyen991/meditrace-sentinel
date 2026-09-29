# -*- coding: utf-8 -*-
"""Trich nhat ky loi nhac cho PHAN MA NGUON, tu ban ghi phien lam viec.

VI SAO CAN. Phu luc huong dan su dung AI cho phep "AI viet ma nguon ban dau"
voi hai dieu kien: ghi ro ma nao do AI sinh, va co **nhat ky loi nhac**. Tep
nay dung nhat ky do tu ban ghi phien, thay vi cheo lai bang tri nho.

PHAM VI — doc ky truoc khi dung:

  CO       loi nhac dan toi thay doi trong `src/` hoac `tests/`
  KHONG CO loi nhac chi dan toi tai lieu (`docs/`), cau hoi, hay trao doi

Day la nhat ky cho **ma nguon**, khong phai nhat ky cho toan bo cuoc trao doi.
Phu luc yeu cau nhat ky loi nhac o dung muc "AI viet ma nguon ban dau", nen
pham vi nay khop voi yeu cau. Nhung phai KHAI RO pham vi, khong duoc de nguoi
doc tuong day la tat ca.

CACH LOC — theo VIEC DA LAM, khong theo TU KHOA:

  Mot loi nhac vao nhat ky khi va chi khi cong viec ngay sau no co ghi vao
  `src/` hoac `tests/`. Loc theo tu khoa se vua bo sot vua bat nham; loc theo
  tep da bi ghi thi khong phu thuoc cach dien dat.

RIENG TU: thu muc phien chua ban ghi cua MOI du an tren may nay, khong chi
du an nay. Bo trich CHI doc phien co lam viec trong `meditrace-sentinel`, va chi
lay loi nhac cua nguoi dung — khong lay noi dung tep, khong lay dau ra lenh.

BO SUNG 17/09/2026 — hai lo hong cua ban 10/09:

  1. BO SOT. Chi dem Write/Edit la "da ghi ma". Nhung nhieu lan ma duoc sua
     bang lenh shell (python -, heredoc, sed), nen ban 10/09 chi tim duoc 48
     loi nhac trong khi kho co hon 160 commit. Nay LICH SU GIT la can cu thu
     hai: moi commit cham `src/`, `tests/`, `tools/` duoc gan cho loi nhac
     GAN NHAT truoc no ma phan viec sau loi nhac do co dung toi du an. Gan
     theo thoi gian nen co the lech mot loi nhac — tai lieu ghi ro muc nao
     gan theo commit.

  2. NOI DUNG NHAY CAM. Loi nhac la van noi tu nhien, xen chuyen ngoai du an
     (du an khac, may chu, tai khoan) va thong tin rieng (dia chi may, duong
     dan may ca nhan). `che_nhay_cam` che o MUC CUM TU, khong bao gio bo ca
     muc: loi nhac van con, tep va commit van con, va moi cho che deu de lai
     dau `[đã lược: …]` / `[đã che: …]`. Dau tai lieu khai so cho da che.

    python -m src.nhat_ky_loi_nhac --ra docs/nhat-ky-loi-nhac.md
"""
import argparse
import io
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

THU_MUC_PHIEN = Path.home() / ".claude" / "projects" / "D--Claude"
DAU_HIEU_DU_AN = "meditrace-sentinel"

# Cong cu co ghi ra tep. Chi nhung cai nay moi tinh la "da sinh ma".
CONG_CU_GHI = {"Write", "Edit", "NotebookEdit"}

# Thu muc tinh la MA NGUON. `docs/` co y khong nam o day.
THU_MUC_MA = ("src/", "src\\", "tests/", "tests\\", "tools/", "tools\\")


# Dong chu thich anh ma phan mem chen vao ban ghi ("[Image: source: ...]"): khong phai loi cua nguoi dung.
_CHU_THICH_ANH = re.compile(r"\[Image:[^\n]*\]")


def _van_ban(noi_dung):
    """Loi nhac co the la chuoi, hoac danh sach khoi. Lay phan chu.

    Bo dong chu thich anh. Ban ghi chi co anh khong co chu thi bo qua: do khong phai loi nhac, va nhieu
    ban ghi nhu vay la anh do cong cu doc tep tra ve. Neu de lai thi cong viec bi gan nham cho no, con
    loi nhac that cua nguoi dung (nam trong ban ghi truoc do) bi mat khoi nhat ky.
    """
    if isinstance(noi_dung, str):
        van = noi_dung
    elif isinstance(noi_dung, list):
        van = "\n".join(kh.get("text", "") for kh in noi_dung
                        if isinstance(kh, dict) and kh.get("type") == "text")
    else:
        return ""
    if "[Image:" not in van:
        return van
    sach = "\n".join(d for d in (_CHU_THICH_ANH.sub("", l).strip() for l in van.split("\n")) if d)
    return sach   # chi co anh: khong co loi nao de ghi (thuong la anh do cong cu doc tep tra ve)


def _la_ma(duong_dan):
    """Duong dan co phai ma nguon CUA DE TAI NAY khong.

    Phai kiem CA HAI: nam trong kho `meditrace-sentinel`, VA nam trong thu muc ma.

    Ban dau chi kiem ve thu hai, nen mot lenh ghi vao
    `D:/Claude/ielts-writing-task1/src/build.py` cung khop `src/` va lot vao
    nhat ky. Cong voi viec loc THEO PHIEN (phien nao co dung toi du an thi
    lay het loi nhac cua phien do), ket qua la nhat ky co ca loi nhac cua
    VeriSocrates, ReadUp, va mot du an lam logo.
    """
    d = str(duong_dan or "").replace("\\", "/")
    if DAU_HIEU_DU_AN not in d:
        return False
    return any(x.replace("\\", "/") in d for x in THU_MUC_MA)


# Van ban KHONG phai loi nhac cua nguoi dung, du no nam o ban ghi "user":
# noi dung ky nang duoc nap, ban tom tat phien truoc, tai lieu tham chieu.
# Chung dai va bat dau bang nhung cum co dinh nen nhan ra duoc.
KHONG_PHAI_LOI_NHAC = (
    "base directory for this skill",       # noi dung ky nang duoc nap
    "this session is being continued",     # ban tom tat phien truoc
    "# workflow authoring reference",      # tai lieu tham chieu
    "<system-reminder>",                   # nhac he thong
    "<task-notification>",                 # bao tien do viec chay nen
    "<ci-monitor-event>",
    "caveat: the messages below were generated",
    "[system notification - not user input]",
    "approach this as the design lead",    # noi dung ky nang thiet ke duoc nap
    "[request interrupted by user",         # nguoi dung bam dung, khong phai loi nhac
)


# ------------------------------------------------------ che noi dung nhay cam
#
# Thu tu co y nghia: "may@dia-chi-IP" phai che TRUOC mau email, khong thi mau
# email an mat phan dau va de lo dia chi IP.
MAU_CHE = (
    (re.compile(r"[\w.-]+@\d{1,3}(?:\.\d{1,3}){3}"), "[đã che: địa chỉ máy]"),
    (re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"), "[đã che: email]"),
    (re.compile(r"(?<![\d.])\d{1,3}(?:\.\d{1,3}){3}(?![\d.])"), "[đã che: địa chỉ IP]"),
    (re.compile(r"(?<!\d)(?:\+84|0)\d{9,10}(?!\d)"), "[đã che: số điện thoại]"),
    (re.compile(r"\b(?:sk|ghp|gho|hf|xoxb|xoxp)[-_][A-Za-z0-9_-]{16,}"), "[đã che: khoá]"),
)

# Tep nguoi dung dinh kem: giu TEN tep (la thong tin nghien cuu), bo duong dan
# may ca nhan va ma phien.
MAU_TEP_KEM = re.compile(
    r'@?"?[A-Za-z]:\\Users\\[^"\n]*?\\(?:[0-9a-f]{8}-)?([^"\\\n]+?\.\w{2,5})"?')

# Cum tu ngoai du an hoac rieng tu. Cum chua mot trong cac tu nay bi thay
# bang dau luoc. So khop theo TU (khong khop giua tu): "bds" khong an "bdsx".
TU_NGOAI_DE_TAI = (
    "bđs", "bds", "bất động sản", "ollama", "readup", "facebook", "victor",
    "verisocrates", "ielts", "laptop", "lap asus", "ổ d", "sdt", "số điện thoại",
    "đăng nhập", "mật khẩu", "password", "tài khoản", "tk kaggle",
)
_MAU_NGOAI = re.compile(
    r"(?<!\w)(?:" + "|".join(re.escape(t) for t in TU_NGOAI_DE_TAI) + r")(?!\w)")
DAU_LUOC = "[đã lược: nội dung ngoài dự án hoặc riêng tư]"


def che_nhay_cam(van):
    """-> (van da che, so cho da che). Khong bao gio tra ve chuoi rong khi
    dau vao co chu: ca loi nhac bi luoc thi con lai dau luoc."""
    so = 0
    van, n = MAU_TEP_KEM.subn(lambda m: f"[tệp đính kèm: {m.group(1)}]", van)
    so += n
    for mau, thay in MAU_CHE:
        van, n = mau.subn(thay, van)
        so += n
    # Cat theo xuong dong va dau phay/cham: van noi cua nguoi dung it khi co
    # cau hoan chinh, dau phay thuong la ranh gioi y.
    manh = re.split(r"(\n|,\s+|\.\s+)", van)
    ra = []
    for i, m in enumerate(manh):
        if i % 2 == 1:                       # dau phan cach
            ra.append(m)
            continue
        if _MAU_NGOAI.search(m.lower()):
            so += 1
            if ra and ra[-2:-1] == [DAU_LUOC]:
                ra.pop()                     # gop hai dau luoc lien nhau
                continue
            ra.append(DAU_LUOC)
        else:
            ra.append(m)
    return "".join(ra), so


def _la_loi_nhac_that(van):
    thap = van.strip().lower()
    if not thap:
        return False
    return not any(thap.startswith(x) or x in thap[:200]
                   for x in KHONG_PHAI_LOI_NHAC)


def doc_phien(tep):
    """-> danh sach {thoi_gian, loi_nhac, tep_da_ghi} cho MOT phien.

    Doc theo dong, khong nap ca tep: tong ban ghi phien la vai tram MB.
    """
    ra = []
    hien = None
    with open(tep, encoding="utf-8", errors="replace") as f:
        for dong in f:
            dong = dong.strip()
            if not dong:
                continue
            try:
                d = json.loads(dong)
            except Exception:                      # noqa: BLE001
                continue
            loai = d.get("type")
            if d.get("isSidechain"):
                continue          # viec cua tac tu con, khong phai loi nhac
            if loai == "user":
                noi_dung = d.get("message", {}).get("content")
                # KET QUA CONG CU cung mang type "user". Chung KHONG duoc coi
                # la loi nhac moi, va quan trong hon: KHONG duoc cat lien ket
                # giua loi nhac dang xet voi phan viec sau no.
                #
                # Ban dau cho nay dat `hien = None` cho moi ban ghi khong phai
                # chu, nen ngay sau lenh dau tien la lien ket dut — va nhat ky
                # chi ra 3 muc thay vi hang tram. Con so 3 do la dau hieu duy
                # nhat cho thay co loi.
                if isinstance(noi_dung, list) and any(
                        isinstance(k, dict) and k.get("type") == "tool_result"
                        for k in noi_dung):
                    continue
                van = _van_ban(noi_dung)
                if not _la_loi_nhac_that(van):
                    continue
                hien = {"thoi_gian": d.get("timestamp", ""),
                        "loi_nhac": van.strip(), "tep_da_ghi": [],
                        "dung_de_tai": False}
                ra.append(hien)
            elif loai == "assistant" and hien is not None:
                c = d.get("message", {}).get("content")
                if not isinstance(c, list):
                    continue
                for kh in c:
                    if not isinstance(kh, dict) or kh.get("type") != "tool_use":
                        continue
                    # Moi lenh (ke ca shell) cham toi kho du an: loi nhac nay
                    # du tu cach nhan commit gan theo thoi gian.
                    if DAU_HIEU_DU_AN in json.dumps(kh.get("input", {}),
                                                    ensure_ascii=False):
                        hien["dung_de_tai"] = True
                    if kh.get("name") not in CONG_CU_GHI:
                        continue
                    dd = kh.get("input", {}).get("file_path", "")
                    if _la_ma(dd):
                        hien["tep_da_ghi"].append(
                            str(dd).replace("\\", "/").split("meditrace-sentinel/")[-1])
    return ra


GIO_VN = timezone(timedelta(hours=7))


def _luc(ts):
    """Chuoi ISO (ban ghi phien: UTC co 'Z'; git: co mui gio) -> datetime."""
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def commit_ma():
    """-> [{ma, luc, tieu_de, tep}] cho moi commit cham thu muc ma nguon."""
    try:
        out = subprocess.run(
            ["git", "log", "--format=@@%h|%aI|%s", "--name-only", "--",
             "src", "tests", "tools"],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace").stdout
    except OSError:
        return []
    ra = []
    for dong in out.splitlines():
        dong = dong.strip()
        if dong.startswith("@@"):
            ma, luc, tieu_de = dong[2:].split("|", 2)
            ra.append({"ma": ma, "luc": _luc(luc), "tieu_de": tieu_de, "tep": []})
        elif dong and ra:
            ra[-1]["tep"].append(dong)
    return [c for c in ra if c["luc"] is not None]


def gan_commit(tat_ca, commits):
    """Gan moi commit cho loi nhac GAN NHAT truoc no co dung toi du an.

    Sua `tat_ca` tai cho (them khoa `commit`). Tra ve cac commit khong gan
    duoc (khong co loi nhac nao truoc no) — phai khai, khong duoc im lang.
    """
    ung_vien = sorted((m for m in tat_ca if m.get("dung_de_tai") and _luc(m["thoi_gian"])),
                      key=lambda m: _luc(m["thoi_gian"]))
    khong_gan = []
    for c in commits:
        truoc = [m for m in ung_vien if _luc(m["thoi_gian"]) <= c["luc"]]
        if not truoc:
            khong_gan.append(c)
            continue
        truoc[-1].setdefault("commit", []).append(c)
        c["da_gan"] = True
    return khong_gan


def gom(thu_muc=None, phien=None, commits=None):
    """-> danh sach muc, da loc va sap theo thoi gian.

    Mot loi nhac vao danh sach khi phan viec sau no GHI THANG vao ma nguon,
    hoac khi no nhan mot commit ma nguon (xem `gan_commit`).

    `phien`: gioi han o MOT ma phien, de doi chieu.
    `commits`: None thi doc tu git; [] thi tat can cu commit (dung trong test).
    """
    thu_muc = Path(thu_muc or THU_MUC_PHIEN)
    ds = [thu_muc / f"{phien}.jsonl"] if phien else sorted(thu_muc.glob("*.jsonl"))
    tat_ca = []
    for tep in ds:
        if tep.exists():
            tat_ca += doc_phien(tep)
    gan_commit(tat_ca, commit_ma() if commits is None else commits)
    ra = []
    for m in tat_ca:
        if m["tep_da_ghi"] or m.get("commit"):
            m["tep_da_ghi"] = sorted(set(m["tep_da_ghi"]))
            ra.append(m)
    ra.sort(key=lambda m: m["thoi_gian"])
    return ra


def tep_cua(m):
    """Moi tep ma nguon gan voi mot muc: ghi thang + qua commit."""
    tep = set(m.get("tep_da_ghi", []))
    for c in m.get("commit", []):
        tep.update(c["tep"])
    return sorted(tep)


def _gio_vn(ts):
    luc = _luc(ts)
    return luc.astimezone(GIO_VN) if luc else None


def _ngay(ts):
    luc = _gio_vn(ts)
    return luc.strftime("%Y-%m-%d") if luc else (ts or "")[:10]


def _gon(van, toi_da=300):
    """Loi nhac dai thi cat, va NOI RO la da cat."""
    van = re.sub(r"\s+", " ", van).strip()
    return van if len(van) <= toi_da else van[:toi_da] + " […đã cắt]"


def dung_bang(muc):
    d = ["# Nhật ký lời nhắc — phần mã nguồn",
         "",
         "## Phạm vi của tài liệu này",
         "",
         "Tài liệu ghi lại các lời nhắc đã dẫn tới **thay đổi trong mã nguồn**",
         "(`src/`, `tests/`, `tools/`), trích tự động từ bản ghi phiên làm việc.",
         "",
         "**Không** bao gồm: lời nhắc chỉ dẫn tới tài liệu trong `docs/`, câu hỏi,",
         "và trao đổi. Phụ lục hướng dẫn sử dụng AI yêu cầu nhật ký lời nhắc ở",
         "mục *“AI viết mã nguồn ban đầu”*, nên phạm vi này khớp với yêu cầu —",
         "nhưng phải đọc đúng là **nhật ký cho mã nguồn**, không phải nhật ký cho",
         "toàn bộ cuộc trao đổi.",
         "",
         "Cách lọc là **theo việc đã làm**, không theo từ khoá. Một lời nhắc vào",
         "đây khi công việc ngay sau nó thỏa một trong hai điều kiện:",
         "",
         "1. **ghi thẳng** vào một tệp mã nguồn; hoặc",
         "2. **dẫn tới một commit** mã nguồn: mỗi commit được gắn cho lời nhắc gần",
         "   nhất trước nó mà phần việc sau lời nhắc đó có dùng tới kho dự án.",
         "   Cách gắn này theo thời gian, nên có thể lệch một lời nhắc; những mục",
         "   gắn theo cách này ghi rõ *“qua commit”*.",
         "",
         "Bản ghi phiên trên máy chứa cả các dự án khác; bộ trích chỉ lấy lời nhắc",
         "của người dùng, và chỉ lấy lời nhắc có phần việc chạm tới `meditrace-sentinel`.",
         "",
         "Giờ ghi theo **giờ Việt Nam (UTC+7)**.",
         "",
         "## Nội dung đã che",
         "",
         "Lời nhắc là lời nói tự nhiên, có xen chuyện ngoài dự án (dự án khác,",
         "máy chủ, tài khoản) và thông tin riêng (địa chỉ máy, đường dẫn máy cá",
         "nhân). Những cụm đó được thay bằng dấu *[đã lược: …]* hoặc *[đã che: …]*.",
         "Việc che **không bỏ lời nhắc nào**, không bỏ tệp hay commit nào; chỉ",
         "thay cụm từ. Lời nhắc dài quá 300 ký tự được cắt và ghi rõ là đã cắt.",
         ""]
    if not muc:
        d += ["*(chưa có mục nào)*", ""]
        return "\n".join(d)

    da_che = []
    for m in muc:
        van, so = che_nhay_cam(m["loi_nhac"])
        da_che.append((van, so))
    so_commit = sum(len(m.get("commit", [])) for m in muc)
    d += [f"**Số lời nhắc:** {len(muc)}  ·  **Số commit mã nguồn:** {so_commit}  ·  "
          f"**Khoảng thời gian:** {_ngay(muc[0]['thoi_gian'])} → "
          f"{_ngay(muc[-1]['thoi_gian'])}  ·  "
          f"**Số chỗ đã che:** {sum(s for _v, s in da_che)} "
          f"(trong {sum(1 for _v, s in da_che if s)} lời nhắc)",
          "", "---", ""]
    ngay_truoc = None
    for m, (van, _so) in zip(muc, da_che):
        ng = _ngay(m["thoi_gian"])
        if ng != ngay_truoc:
            d += ["", f"## {ng}", ""]
            ngay_truoc = ng
        luc = _gio_vn(m["thoi_gian"])
        gio = luc.strftime("%H:%M") if luc else ""
        d += [f"**{gio}** — {_gon(van)}", ""]
        if m.get("tep_da_ghi"):
            d.append("  Tệp đã ghi: " + ", ".join(f"`{x}`" for x in m["tep_da_ghi"]))
        for c in m.get("commit", []):
            # Tieu de commit cung la van ban tu do: che nhu loi nhac.
            d.append(f"  Qua commit `{c['ma']}` — {che_nhay_cam(c['tieu_de'])[0]} "
                     f"({len(c['tep'])} tệp mã nguồn)")
        d.append("")
    return "\n".join(d)


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--thu-muc", default=None)
    ap.add_argument("--phien", default=None,
                    help="chi doc MOT phien (ma phien), thay vi ca thu muc")
    ap.add_argument("--ra", default="docs/nhat-ky-loi-nhac.md")
    a = ap.parse_args()

    commits = commit_ma()
    muc = gom(a.thu_muc, a.phien, commits=commits)
    Path(a.ra).write_text(dung_bang(muc), encoding="utf-8")
    tep = sorted({t for m in muc for t in tep_cua(m)})
    khong_gan = [c["ma"] for c in commits if not c.get("da_gan")]
    print(f"{len(muc)} loi nhac dan toi thay doi ma nguon")
    print(f"{len(tep)} tep ma nguon gan duoc loi nhac")
    print(f"{len(commits)} commit ma nguon, {len(khong_gan)} khong gan duoc: {khong_gan}")
    print(f"-> {a.ra}")


if __name__ == "__main__":
    main()
