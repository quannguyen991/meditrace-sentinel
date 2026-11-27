# -*- coding: utf-8 -*-
"""[Dịch vụ, an toàn và minh bạch › Minh bạch]
Làm gì   : Trích các lời nhắc của người dùng dẫn tới sửa mã nguồn từ bản ghi phiên làm việc,
           che thông tin nhạy cảm.
Vào → Ra : tệp phiên làm việc và commit của kho mã → nhật ký lời nhắc dạng Markdown gắn từng
           lời nhắc với commit
Đọc từ   : gom() gom và sắp lời nhắc; doc_phien() đọc một tệp phiên và rút lời nhắc
Mục lục (các hàm/lớp chính):
  gom()           Gom và sắp xếp các lời nhắc dẫn tới sửa mã nguồn
  doc_phien()     Đọc một tệp phiên và rút các lời nhắc
  commit_ma()     Lấy commit mã nguồn của cả hai kho
  gan_commit()    Gắn mỗi commit vào lời nhắc gần nhất trước nó
  che_nhay_cam()  Che thông tin nhạy cảm trong lời nhắc
  dung_bang()     Dựng tài liệu nhật ký lời nhắc dạng Markdown
  main()          Điểm vào: sinh tệp nhật ký lời nhắc
Dùng bởi : he_thong/khai_ma_nguon
Tên cũ   : nhat_ky_loi_nhac.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Trích nhật ký lời nhắc cho PHẦN MÃ NGUỒN, từ bản ghi phiên làm việc.

VÌ SAO CẦN. Phụ lục hướng dẫn sử dụng AI cho phép "AI viết mã nguồn ban đầu"
với hai điều kiện: ghi rõ mã nào do AI sinh, và có **nhật ký lời nhắc**. Tệp
này dựng nhật ký đó từ bản ghi phiên, thay vì chéo lại bằng trí nhớ.

PHẠM VI — đọc kỹ trước khi dùng:

  CÓ       lời nhắc dẫn tới thay đổi trong `src/` hoặc `tests/`
  KHÔNG CÓ lời nhắc chỉ dẫn tới tài liệu (`docs/`), câu hỏi, hay trao đổi

Đây là nhật ký cho **mã nguồn**, không phải nhật ký cho toàn bộ cuộc trao đổi.
Phụ lục yêu cầu nhật ký lời nhắc ở đúng mục "AI viết mã nguồn ban đầu", nên
phạm vi này khớp với yêu cầu. Nhưng phải KHAI RÕ phạm vi, không được để người
đọc tưởng đây là tất cả.

CÁCH LỌC — theo VIỆC ĐÃ LÀM, không theo TỪ KHOÁ:

  Một lời nhắc vào nhật ký khi và chỉ khi công việc ngay sau nó có ghi vào
  `src/` hoặc `tests/`. Lọc theo từ khoá sẽ vừa bỏ sót vừa bắt nhầm; lọc theo
  tệp đã bị ghi thì không phụ thuộc cách diễn đạt.

RIÊNG TƯ: thư mục phiên chứa bản ghi của MỌI dự án trên máy này, không chỉ
dự án này. Bộ trích CHỈ đọc phiên có làm việc trong `meditrace-core`, và chỉ
lấy lời nhắc của người dùng — không lấy nội dung tệp, không lấy đầu ra lệnh.

BỔ SUNG 17/09/2026 — hai lỗ hổng của bản 10/09:

  1. BỎ SÓT. Chỉ đếm Write/Edit là "đã ghi mã". Nhưng nhiều lần mã được sửa
     bằng lệnh shell (python -, heredoc, sed), nên bản 10/09 chỉ tìm được 48
     lời nhắc trong khi kho có hơn 160 commit. Nay LỊCH SỬ GIT là căn cứ thứ
     hai: mỗi commit chạm `src/`, `tests/`, `tools/` được gán cho lời nhắc
     GẦN NHẤT trước nó mà phần việc sau lời nhắc đó có đụng tới dự án. Gán
     theo thời gian nên có thể lệch một lời nhắc — tài liệu ghi rõ mục nào
     gán theo commit.

  2. NỘI DUNG NHẠY CẢM. Lời nhắc là văn nói tự nhiên, xen chuyện ngoài dự án
     (dự án khác, máy chủ, tài khoản) và thông tin riêng (địa chỉ máy, đường
     dẫn máy cá nhân). `che_nhay_cam` che ở MỨC CỤM TỪ, không bao giờ bỏ cả
     mục: lời nhắc vẫn còn, tệp và commit vẫn còn, và mỗi chỗ che đều để lại
     dau `[đã lược: …]` / `[đã che: …]`. Dau tai lieu khai so cho da che.

    python -m src.he_thong.nhat_ky_loi_nhac --ra docs/nhat-ky-loi-nhac.md
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
DAU_HIEU_DU_AN = "meditrace-core"      # kho Python
DAU_HIEU_WEB = "meditrace-sentinel"  # kho giao diện web (thư mục con web/ trong bản công khai)
# Thư mục mã nguồn của kho web (không tính docs, dist, node_modules).
THU_MUC_MA_WEB = ("src/", "may-chu/", "db/", "server.ts")


# ─── _thuoc_du_an() — Kiểm chuỗi có nhắc tới kho của dự án không ──────────────────────
# Áp cho đường dẫn hoặc lệnh.
def _thuoc_du_an(van_ban):
    """Chuỗi (đường dẫn hoặc lệnh) có nhắc tới một trong hai kho của dự án không."""
    return DAU_HIEU_DU_AN in van_ban or DAU_HIEU_WEB in van_ban


# Công cụ có ghi ra tệp. Chỉ những cái này mới tính là "đã sinh mã".
CONG_CU_GHI = {"Write", "Edit", "NotebookEdit"}

# Thư mục tính là MÃ NGUỒN. `docs/` cố ý không nằm ở đây.
THU_MUC_MA = ("src/", "src\\", "tests/", "tests\\", "tools/", "tools\\")


# Dòng chú thích ảnh mà phần mềm chèn vào bản ghi ("[Image: source: ...]"): không phải lời của người dùng.
_CHU_THICH_ANH = re.compile(r"\[Image:[^\n]*\]")


# ─── _van_ban() — Lấy phần chữ của một lời nhắc ───────────────────────────────────────
# Lời nhắc có thể là chuỗi hoặc danh sách khối; bỏ chú thích ảnh và bản ghi chỉ có ảnh.
def _van_ban(noi_dung):
    """Lời nhắc có thể là chuỗi, hoặc danh sách khối. Lấy phần chữ.

    Bỏ dòng chú thích ảnh. Bản ghi chỉ có ảnh không có chữ thì bỏ qua: đó không phải lời nhắc, và nhiều
    bản ghi như vậy là ảnh do công cụ đọc tệp trả về. Nếu để lại thì công việc bị gán nhầm cho nó, còn
    lời nhắc thật của người dùng (nằm trong bản ghi trước đó) bị mất khỏi nhật ký.
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
    return sach   # chỉ có ảnh: không có lời nào để ghi (thường là ảnh do công cụ đọc tệp trả về)


# ─── _la_ma() — Kiểm đường dẫn có phải mã nguồn của đề tài ────────────────────────────
# Phải nằm trong kho meditrace-core và trong thư mục mã.
def _la_ma(duong_dan):
    """Đường dẫn có phải mã nguồn CỦA ĐỀ TÀI NÀY không.

    Phải kiểm CẢ HAI: nằm trong kho `meditrace-core`, VÀ nằm trong thư mục mã.

    Ban đầu chỉ kiểm về thứ hai, nên một lệnh ghi vào
    `D:/Claude/ielts-writing-task1/src/build.py` cũng khớp `src/` và lọt vào
    nhật ký. Cộng với việc lọc THEO PHIÊN (phiên nào có đụng tới dự án thì
    lấy hết lời nhắc của phiên đó), kết quả là nhật ký có cả lời nhắc của
    VeriSocrates, ReadUp, và một dự án làm logo.
    """
    d = str(duong_dan or "").replace("\\", "/")
    if DAU_HIEU_WEB in d:
        goc = d.split(DAU_HIEU_WEB + "/")[-1]
        return any(goc.startswith(x) for x in THU_MUC_MA_WEB)
    if DAU_HIEU_DU_AN not in d:
        return False
    return any(x.replace("\\", "/") in d for x in THU_MUC_MA)


# Văn bản KHÔNG phải lời nhắc của người dùng, dù nó nằm ở bản ghi "user":
# nội dung kỹ năng được nạp, bản tóm tắt phiên trước, tài liệu tham chiếu.
# Chúng dài và bắt đầu bằng những cụm cố định nên nhận ra được.
KHONG_PHAI_LOI_NHAC = (
    "base directory for this skill",       # nội dung kỹ năng được nạp
    "this session is being continued",     # bản tóm tắt phiên trước
    "# workflow authoring reference",      # tài liệu tham chiếu
    "<system-reminder>",                   # nhắc hệ thống
    "<task-notification>",                 # báo tiến độ việc chạy nền
    "<ci-monitor-event>",
    "caveat: the messages below were generated",
    "[system notification - not user input]",
    "approach this as the design lead",    # nội dung kỹ năng thiết kế được nạp
    "[request interrupted by user",         # người dùng bấm dừng, không phải lời nhắc
)


# ------------------------------------------------------ che nội dung nhạy cảm
#
# Thứ tự có ý nghĩa: "may@dia-chi-IP" phải che TRƯỚC mẫu email, không thì mẫu
# email ăn mất phần đầu và để lộ địa chỉ IP.
MAU_CHE = (
    (re.compile(r"[\w.-]+@\d{1,3}(?:\.\d{1,3}){3}"), "[đã che: địa chỉ máy]"),
    (re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"), "[đã che: email]"),
    (re.compile(r"(?<![\d.])\d{1,3}(?:\.\d{1,3}){3}(?![\d.])"), "[đã che: địa chỉ IP]"),
    (re.compile(r"(?<!\d)(?:\+84|0)\d{9,10}(?!\d)"), "[đã che: số điện thoại]"),
    (re.compile(r"\b(?:sk|ghp|gho|hf|xoxb|xoxp)[-_][A-Za-z0-9_-]{16,}"), "[đã che: khoá]"),
    (re.compile(r"(?i)\b[\w.-]*\.trycloudflare\.com\b"), "[đã che: địa chỉ tạm]"),
    (re.compile(r"(?i)\bkhoa-(?:phieu|giai-ma)\.json\b"), "[đã che: tệp khoá chấm mù]"),
)

# Tệp người dùng đính kèm: giữ TÊN tệp (là thông tin nghiên cứu), bỏ đường dẫn
# máy cá nhân và mã phiên.
MAU_TEP_KEM = re.compile(
    r'@?"?[A-Za-z]:\\Users\\[^"\n]*?\\(?:[0-9a-f]{8}-)?([^"\\\n]+?\.\w{2,5})"?')

# Cụm từ ngoài dự án hoặc riêng tư. Cụm chứa một trong các từ này bị thay
# bằng dấu lược. So khớp theo TỪ (không khớp giữa từ): "bds" không ăn "bdsx".
TU_NGOAI_DE_TAI = (
    "bđs", "bds", "bất động sản", "ollama", "readup", "facebook", "victor",
    "verisocrates", "ielts", "nguyễn nam", "laptop", "lap asus", "ổ d", "sdt", "số điện thoại",
    "đăng nhập", "mật khẩu", "password", "tài khoản", "tk kaggle",
)
_MAU_NGOAI = re.compile(
    r"(?<!\w)(?:" + "|".join(re.escape(t) for t in TU_NGOAI_DE_TAI) + r")(?!\w)")
DAU_LUOC = "[đã lược: nội dung ngoài dự án hoặc riêng tư]"


# Cụm từ riêng cần che (tên tài khoản, tên người...) nằm trong TỆP RIÊNG, không nằm trong mã nguồn:
# mã nguồn được đưa lên cho người ngoài, nên không được liệt kê chính những tên cần giấu.
# Mỗi dòng một cụm; khớp không phân biệt hoa thường, theo từ.
TEP_CHE_THEM = Path("D:/Claude/.secrets/che-them.txt")


# ─── _cum_che_them() — Đọc các cụm cần che thêm từ tệp cấu hình ───────────────────────
# Không có tệp thì trả danh sách rỗng.
def _cum_che_them():
    try:
        return [d.strip() for d in TEP_CHE_THEM.read_text(encoding="utf-8").splitlines()
                if d.strip() and not d.startswith("#")]
    except OSError:
        return []


# ═══ che_nhay_cam() — Che thông tin nhạy cảm trong lời nhắc ═══════════════════════════
# Trả (văn bản đã che, số chỗ che); không bao giờ trả chuỗi rỗng khi đầu vào có chữ.
def che_nhay_cam(van):
    """-> (văn đã che, số chỗ đã che). Không bao giờ trả về chuỗi rỗng khi
    đầu vào có chữ: cả lời nhắc bị lược thì còn lại dấu lược."""
    so = 0
    van, n = MAU_TEP_KEM.subn(lambda m: f"[tệp đính kèm: {m.group(1)}]", van)
    so += n
    for mau, thay in MAU_CHE:
        van, n = mau.subn(thay, van)
        so += n
    for cum in _cum_che_them():
        van, n = re.subn(r"(?i)(?<!\w)" + re.escape(cum) + r"(?!\w)", "[đã che: tên riêng]", van)
        so += n
    # Cắt theo xuống dòng và dấu phẩy/chấm: văn nói của người dùng ít khi có
    # câu hoàn chỉnh, dấu phẩy thường là ranh giới ý.
    manh = re.split(r"(\n|,\s+|\.\s+)", van)
    ra = []
    for i, m in enumerate(manh):
        if i % 2 == 1:                       # dấu phân cách
            ra.append(m)
            continue
        if _MAU_NGOAI.search(m.lower()):
            so += 1
            if ra and ra[-2:-1] == [DAU_LUOC]:
                ra.pop()                     # gộp hai dấu lược liền nhau
                continue
            ra.append(DAU_LUOC)
        else:
            ra.append(m)
    return "".join(ra), so


# ─── _la_loi_nhac_that() — Phân biệt lời nhắc thật với tin nhắn hệ thống ──────────────
# Loại các câu mở đầu thuộc danh sách không phải lời nhắc.
def _la_loi_nhac_that(van):
    thap = van.strip().lower()
    if not thap:
        return False
    return not any(thap.startswith(x) or x in thap[:200]
                   for x in KHONG_PHAI_LOI_NHAC)


# ═══ doc_phien() — Đọc một tệp phiên và rút các lời nhắc ══════════════════════════════
# Trả thời gian, lời nhắc và tệp đã ghi; đọc theo dòng vì tệp lớn.
def doc_phien(tep):
    """-> danh sách {thoi_gian, loi_nhac, tep_da_ghi} cho MỘT phiên.

    Đọc theo dòng, không nạp cả tệp: tổng bản ghi phiên là vài trăm MB.
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
                continue          # việc của tác tử con, không phải lời nhắc
            if loai == "user":
                noi_dung = d.get("message", {}).get("content")
                # KẾT QUẢ CÔNG CỤ cũng mang type "user". Chúng KHÔNG được coi
                # là lời nhắc mới, và quan trọng hơn: KHÔNG được cắt liên kết
                # giữa lời nhắc đang xét với phần việc sau nó.
                #
                # Ban đầu chỗ này đặt `hien = None` cho mọi bản ghi không phải
                # chữ, nên ngay sau lệnh đầu tiên là liên kết đứt — và nhật ký
                # chỉ ra 3 mục thay vì hàng trăm. Con số 3 đó là dấu hiệu duy
                # nhất cho thấy có lỗi.
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
                    # Mỗi lệnh (kể cả shell) chạm tới kho dự án: lời nhắc này
                    # đủ tư cách nhận commit gần theo thời gian.
                    if _thuoc_du_an(json.dumps(kh.get("input", {}),
                                               ensure_ascii=False)):
                        hien["dung_de_tai"] = True
                    if kh.get("name") not in CONG_CU_GHI:
                        continue
                    dd = kh.get("input", {}).get("file_path", "")
                    if _la_ma(dd):
                        dd = str(dd).replace("\\", "/")
                        hien["tep_da_ghi"].append(
                            "web/" + dd.split(DAU_HIEU_WEB + "/")[-1]
                            if DAU_HIEU_WEB in dd else dd.split(DAU_HIEU_DU_AN + "/")[-1])
    return ra


GIO_VN = timezone(timedelta(hours=7))


# ─── _luc() — Đổi chuỗi thời gian ISO thành datetime ──────────────────────────────────
# Xử lý cả đuôi Z của phiên và múi giờ của git.
def _luc(ts):
    """Chuỗi ISO (bản ghi phiên: UTC có 'Z'; git: có múi giờ) -> datetime."""
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


KHO_WEB = Path("D:/meditrace-sentinel")


# ─── _commit_kho() — Lấy các commit chạm thư mục mã của một kho ───────────────────────
# Trả mã, thời gian, tiêu đề và tệp; kho không có thì bỏ qua.
def _commit_kho(repo, thu_muc, tien_to=""):
    try:
        cmd = ["git"] + (["-C", str(repo)] if repo else []) + [
            "log", "--format=@@%h|%aI|%s", "--name-only", "--", *thu_muc]
        out = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
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
            ra[-1]["tep"].append(tien_to + dong)
    return [c for c in ra if c["luc"] is not None]


# ═══ commit_ma() — Lấy commit mã nguồn của cả hai kho ═════════════════════════════════
# Tệp kho web được gắn tiền tố web/.
def commit_ma():
    """-> [{ma, luc, tieu_de, tep}] cho mỗi commit chạm thư mục mã nguồn của CẢ HAI kho.

    Tệp của kho web có tiền tố `web/`. Kho web không có trên máy thì bỏ qua.
    """
    ra = _commit_kho(None, ("src", "tests", "tools"))
    if KHO_WEB.exists():
        ra += _commit_kho(KHO_WEB, ("src", "may-chu", "db", "server.ts"), "web/")
    return ra


# ═══ gan_commit() — Gắn mỗi commit vào lời nhắc gần nhất trước nó ═════════════════════
# Sửa tại chỗ; trả các commit không gắn được để khai rõ.
def gan_commit(tat_ca, commits):
    """Gán mỗi commit cho lời nhắc GẦN NHẤT trước nó có đụng tới dự án.

    Sửa `tat_ca` tại chỗ (thêm khoá `commit`). Trả về các commit không gán
    được (không có lời nhắc nào trước nó) — phải khai, không được im lặng.
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


# ═══ gom() — Gom và sắp xếp các lời nhắc dẫn tới sửa mã nguồn ═════════════════════════
# Chỉ giữ lời nhắc ghi thẳng vào mã hoặc nhận commit; có thể giới hạn theo phiên.
def gom(thu_muc=None, phien=None, commits=None):
    """-> danh sách mục, đã lọc và sắp theo thời gian.

    Một lời nhắc vào danh sách khi phần việc sau nó GHI THẲNG vào mã nguồn,
    hoặc khi nó nhận một commit mã nguồn (xem `gan_commit`).

    `phien`: giới hạn ở MỘT mã phiên, để đối chiếu.
    `commits`: None thì đọc từ git; [] thì tắt căn cứ commit (dùng trong test).
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


# ═══ tep_cua() — Liệt kê tệp mã nguồn gắn với một mục ═════════════════════════════════
# Gồm tệp ghi thẳng và tệp qua commit.
def tep_cua(m):
    """Mỗi tệp mã nguồn gắn với một mục: ghi thẳng + qua commit."""
    tep = set(m.get("tep_da_ghi", []))
    for c in m.get("commit", []):
        tep.update(c["tep"])
    return sorted(tep)


# ─── _gio_vn() — Đổi thời gian sang giờ Việt Nam ──────────────────────────────────────
def _gio_vn(ts):
    luc = _luc(ts)
    return luc.astimezone(GIO_VN) if luc else None


# ─── _ngay() — Lấy ngày từ chuỗi thời gian ────────────────────────────────────────────
def _ngay(ts):
    luc = _gio_vn(ts)
    return luc.strftime("%Y-%m-%d") if luc else (ts or "")[:10]


# ─── _gon() — Rút gọn lời nhắc dài ────────────────────────────────────────────────────
# Cắt và ghi rõ là đã cắt.
def _gon(van, toi_da=300):
    """Lời nhắc dài thì cắt, và NÓI RÕ là đã cắt."""
    van = re.sub(r"\s+", " ", van).strip()
    return van if len(van) <= toi_da else van[:toi_da] + " […đã cắt]"


# ═══ dung_bang() — Dựng tài liệu nhật ký lời nhắc dạng Markdown ═══════════════════════
# Nêu rõ phạm vi chỉ là mã nguồn rồi liệt kê từng lời nhắc.
def dung_bang(muc):
    d = ["# Nhật ký lời nhắc — phần mã nguồn",
         "",
         "## Phạm vi của tài liệu này",
         "",
         "Tài liệu ghi lại các lời nhắc đã dẫn tới **thay đổi trong mã nguồn**",
         "(`src/`, `tests/`, `tools/` của phần xử lý; `src/`, `may-chu/`, `db/`, `server.ts`",
         "của giao diện web, ghi là `web/…`), trích tự động từ bản ghi phiên làm việc.",
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
         "của người dùng, và chỉ lấy lời nhắc có phần việc chạm tới kho phần xử lý",
         "(`meditrace-core`) hoặc kho giao diện web (`meditrace-sentinel`).",
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
            # Tiêu đề commit cũng là văn bản tự do: che như lời nhắc.
            d.append(f"  Qua commit `{c['ma']}` — {che_nhay_cam(c['tieu_de'])[0]} "
                     f"({len(c['tep'])} tệp mã nguồn)")
        d.append("")
    return "\n".join(d)


# ═══ main() — Điểm vào: sinh tệp nhật ký lời nhắc ═════════════════════════════════════
# Ghi docs/nhat-ky-loi-nhac.md và in thống kê gán commit.
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
