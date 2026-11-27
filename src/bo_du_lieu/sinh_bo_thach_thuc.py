# -*- coding: utf-8 -*-
"""[Sinh, nạp và chia dữ liệu › Bộ thử thách]
Làm gì   : Sinh bốn bộ thử thách theo cặp (đổi người, tự sửa, lỗi chép giọng nói, phương
           ngữ) bằng luật, từ tập ca sẵn có.
Vào → Ra : tập ca có đáp án + số cặp + hạt giống → các cặp (ca gốc, ca đã biến đổi) kèm đáp
           án; main() ghi tệp
Đọc từ   : cap_doi_chu_the() cặp đổi người; bo_dinh_chinh() bộ tự sửa; cap_nhieu_asr() cặp
           lỗi chép giọng
Mục lục (các hàm/lớp chính):
  cap_doi_chu_the()  Sinh các cặp ca chỉ khác nhau ở việc đổi người
  cap_phuong_ngu()   Sinh các cặp ca có và không có phương ngữ
  cap_nhieu_asr()    Sinh cặp ca sạch và bản nhiễu như máy chép giọng nói
  cap_dan_gian()     Sinh các cặp ca gốc và bản đổi sang lời dân thường
  bo_dinh_chinh()    Sinh bộ ca cập nhật và tự sửa theo từng bẫy
  main()             Sinh và ghi các bộ thử thách kèm vân tay
Gọi tới  : bo_du_lieu/dan_gian, bo_du_lieu/nap_du_lieu, bo_du_lieu/nhieu_asr,
           bo_du_lieu/phuong_ngu, bo_du_lieu/sinh_hoi_thoai_viet, bo_du_lieu/van_tay_bo,
           he_thong/duong_dan
Tên cũ   : thach_thuc.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Bốn bài kiểm tra "dat" — sinh bằng LUẬT, trên khuôn của MỘT tập.

  doi_chu_the  CẶP ca giống hệt nhau, chỉ ĐẢO người mang dị ứng: người nhà <->
               bệnh nhân. Hồ sơ phải đổi theo, và phải đúng ở CẢ HAI bản.
  phuong_ngu   CẶP ca giống hệt nhau, một bản có từ phương ngữ, một bản không.
               Trạng thái hồ sơ phải GIỐNG NHAU. Nội dung cũng vậy, trừ cụm
               không đồng nghĩa ("nóng hầm hập" / "sốt", từ 24/09/2026).
  dinh_chinh   ca mang một bẫy cập nhật: đính chính, mâu thuẫn, diễn biến, bổ
               sung, hai nguồn khác nhau. Đo trạng thái CUỐI CÙNG.
  dan_gian     CẶP: bản gốc và CHÍNH bản đó với lời bệnh nhân đổi sang cách nói địa
               phương / dân gian / ẩn dụ lấy từ từ điển thật (`dan_gian`). Đáp án
               giống hệt trừ `trich_dan`. Thêm 24/09/2026, chỉ sinh khi gọi rõ
               `--chi dan_gian`.
  nhieu_asr    CẶP: bản sạch và CHÍNH bản đó đã làm nhiễu như đầu ra máy nhận
               dạng tiếng nói (mất dấu, mất dấu câu). Trạng thái hồ sơ phải
               GIỐNG NHAU — xem `nhieu_asr` để biết vì sao nhiễu không được
               đụng tới từ chỉ người, từ số và từ phủ định.

VÌ SAO LÀ CẶP. Một con số trên tập thường không tách được "hệ thống hiểu chủ
thể" với "hệ thống đoán trúng": đường tắt "chủ thể = người nói" đúng ở phần lớn
lượt. Hai bản chỉ khác ĐÚNG một điều thì mọi đường tắt đều lộ ra — đoán theo
người nói thì đúng một bản và sai bản kia.

KHÔNG DÙNG MÔ HÌNH NGÔN NGỮ. Cả ba bộ sinh từ `sinh_hoi_thoai_viet` bằng tùy
chọn (`TuyChon`) — ràng buộc số 1 của dự án áp cho cả bài kiểm tra.

CHỈ SINH TRÊN KHUÔN CỦA MỘT TẬP: bài kiểm tra trên khuôn đã học là đo "nhớ",
không phải đo "hiểu". Tập kiểm tra cuối chỉ sinh lúc khoá thiết kế — chốt
`du_lieu.chan_tap_khoa` chặn cả ở đây.

    python -m src.bo_du_lieu.sinh_bo_thach_thuc --khuon-tap phat_trien --the-he 5
"""
import argparse
import hashlib
import io
import json
import random
import sys

from src.bo_du_lieu import dan_gian as dan_gian
from src.bo_du_lieu import nap_du_lieu as du_lieu
from src.he_thong import duong_dan as duong_dan
from src.bo_du_lieu import nhieu_asr as nhieu_asr
from src.bo_du_lieu import van_tay_bo as van_tay_bo
from src.bo_du_lieu import sinh_hoi_thoai_viet as sh

THACH_THUC = ("doi_chu_the", "phuong_ngu", "dinh_chinh", "nhieu_asr", "dan_gian")
BAY_CAP_NHAT = ("dinh_chinh", "mau_thuan", "dien_bien", "bo_sung",
                "nguon_khac_nhau")
# Mỗi cặp / mỗi ca thử tối đa bấy nhiêu hạt. Quá số này là tùy chọn không thể
# đạt được — báo lỗi thay vì lặng lẽ trả về ít ca hơn.
SO_LAN_THU_TOI_DA = 60


# ─── _hat() — Tạo hạt ngẫu nhiên ổn định từ nhiều thành phần ──────────────────────────
# Băm sha256 các phần ghép bằng dấu hai chấm.
def _hat(*phan):
    s = ":".join(str(x) for x in phan)
    return int(hashlib.sha256(s.encode("utf-8")).hexdigest()[:12], 16)


# ─── _luot() — Tách các dòng không trống của hội thoại ────────────────────────────────
# Mỗi dòng là một lượt nói.
def _luot(ca):
    return [d for d in ca["input"].split("\n") if d.strip()]


# ═══ bo_trich_dan() — Bỏ trường câu trích khỏi đáp án ═════════════════════════════════
# Hai bản của cặp khác chữ nên câu trích phải khác; các trường khác giống hệt.
def bo_trich_dan(dap_an):
    """Đáp án bỏ `trich_dan`. Hai bản của cặp phương ngữ KHÁC CHỮ nên trích dẫn
    phải khác; mọi trường còn lại phải giống hệt."""
    return [{k: v for k, v in d.items() if k != "trich_dan"} for d in dap_an]


# ═══ cap_doi_chu_the() — Sinh các cặp ca chỉ khác nhau ở việc đổi người ═══════════════
# Bản A người nhà dị ứng, bệnh nhân chưa; bản B đảo hai người, khác đúng một lượt.
def cap_doi_chu_the(tap, so_cap, seed=42):
    """-> 2*so_cap ca. Bản A: người nhà dị ứng, bệnh nhân "chưa thấy bị báo
    giờ". Bản B: cùng câu đó, ĐẢO hai người. Chỉ ĐÚNG MỘT lượt khác nhau."""
    ra = []
    for i in range(so_cap):
        for thu in range(SO_LAN_THU_TOI_DA):
            h = _hat("doi_chu_the", seed, tap, i, thu)
            chung = dict(chi_tap=tap, ep_bay=("di_ung_nguoi_nha",),
                         ep_nguoi_ke=True, di_ung_cua_nguoi_ke=True)
            a = sh.sinh_mot_ca(f"dct_{i:03d}_A", random.Random(h),
                               sh.TuyChon(**chung))
            b = sh.sinh_mot_ca(f"dct_{i:03d}_B", random.Random(h),
                               sh.TuyChon(**chung, doi_chu_the=True))
            la, lb = _luot(a), _luot(b)
            khac = [j for j, (x, y) in enumerate(zip(la, lb)) if x != y]
            if len(la) == len(lb) and len(khac) == 1:
                break
        else:
            raise RuntimeError(f"khong sinh duoc cap doi chu the thu {i}")
        for x, bien_the in ((a, "A"), (b, "B")):
            x.update(thach_thuc="doi_chu_the", cap=i, bien_the=bien_the,
                     luot_khac=khac[0] + 1)
        ra += [a, b]
    return ra


# Cặp phương ngữ cần NHIỀU lần thử hơn: bảng thay của miền Trung chỉ có 4 cặp từ
# ("hôm kia", "dạo này", "bây giờ", "trẻ em"), nên phần lớn ca miền Trung KHÔNG
# mang từ phương ngữ nào. Lần chạy đầu ngày 11/09/2026: cặp thứ 9 (miền Trung)
# trượt cả 60 lần thử.
SO_LAN_THU_PHUONG_NGU = 800


# ─── _so_cap_phuong_ngu() — Chuẩn bị đáp án để so hai bản cặp phương ngữ ──────────────
# Bỏ câu trích rồi đưa cụm giữ lời người nói về từ chuẩn.
def _so_cap_phuong_ngu(dap_an):
    """`bo_trich_dan`, rồi trả cụm giữ nguyên lời người nói về từ chuẩn.

    Từ 24/09/2026 bản A nói "nóng hầm hập" thì đáp án A ghi đúng cụm đó
    (`phuong_ngu.GIU_NGUYEN`), bản B nói "sốt" thì ghi "sốt": hai bản CÓ Ý khác
    nhau ở đúng chỗ đó. Mọi trường còn lại vẫn phải giống hệt, và so bằng hàm này
    thì các cặp cũ vẫn được nhấn ý như trước — không cặp nào bị sinh lại."""
    from src.bo_du_lieu import phuong_ngu as phuong_ngu
    ra = bo_trich_dan(dap_an)
    for d in ra:
        d["noi_dung"] = phuong_ngu.ve_tu_chuan(d["noi_dung"])
    return ra


# ═══ cap_phuong_ngu() — Sinh các cặp ca có và không có phương ngữ ═════════════════════
# Bản A có từ phương ngữ, bản B tắt tầng vùng; đáp án giống trừ câu trích.
def cap_phuong_ngu(tap, so_cap, seed=42):
    """-> 2*so_cap ca. Bản A có từ phương ngữ, bản B tắt tầng vùng. Đáp án phải
    giống hệt trừ `trich_dan`, và trừ nội dung mang cụm giữ nguyên lời người nói
    (`_so_cap_phuong_ngu`)."""
    ra = []
    for i in range(so_cap):
        mien = ("nam", "trung")[i % 2]
        for thu in range(SO_LAN_THU_PHUONG_NGU):
            h = _hat("phuong_ngu", seed, tap, i, thu)
            chung = dict(chi_tap=tap, ep_mien=mien)
            a = sh.sinh_mot_ca(f"png_{i:03d}_A", random.Random(h),
                               sh.TuyChon(**chung))
            b = sh.sinh_mot_ca(f"png_{i:03d}_B", random.Random(h),
                               sh.TuyChon(**chung, ap_phuong_ngu=False))
            if (a["tu_phuong_ngu"] and not b["tu_phuong_ngu"]
                    and len(_luot(a)) == len(_luot(b))
                    and _so_cap_phuong_ngu(a["dap_an"]) == _so_cap_phuong_ngu(b["dap_an"])):
                break
        else:
            raise RuntimeError(f"khong sinh duoc cap phuong ngu thu {i}")
        for x, bien_the in ((a, "A"), (b, "B")):
            x.update(thach_thuc="phuong_ngu", cap=i, bien_the=bien_the)
        ra += [a, b]
    return ra


# ═══ cap_nhieu_asr() — Sinh cặp ca sạch và bản nhiễu như máy chép giọng nói ═══════════
# Sinh một ca rồi làm xấu chữ của chính nó; đáp án giống trừ câu trích.
def cap_nhieu_asr(tap, so_cap, seed=42, ti_le=0.5):
    """-> 2*so_cap ca. Bản A là bản SẠCH, bản B là chính bản đó đã làm nhiễu như
    đầu ra máy nhận dạng tiếng nói. Đáp án giống hệt trừ `trich_dan`.

    KHÁC BA BỘ KIA MỘT ĐIỂM: hai bộ trên sinh HAI ca rồi đổi một điều, còn ở đây
    chỉ sinh MỘT ca rồi làm xấu chữ của chính nó. Làm vậy vì nhiễu ASR là thứ xảy
    ra SAU khi người ta nói — nó không đổi nội dung buổi khám, chỉ đổi bản ghi.
    Sinh hai ca rồi làm nhiễu một bản thì hai bản đã khác nhau từ trước, và phép
    thử mất ý nghĩa.
    """
    ra = []
    for i in range(so_cap):
        h = _hat("nhieu_asr", seed, tap, i)
        a = sh.sinh_mot_ca(f"asr_{i:03d}_A", random.Random(h),
                           sh.TuyChon(chi_tap=tap))
        b = nhieu_asr.nhieu_ca(a, random.Random(h ^ 0x5A5A), ti_le)
        b["id"] = f"asr_{i:03d}_B"
        if bo_trich_dan(a["dap_an"]) != bo_trich_dan(b["dap_an"]):
            raise RuntimeError(f"lam nhieu da doi dap an o cap {i}")
        for x, bien_the in ((a, "A"), (b, "B")):
            x.update(thach_thuc="nhieu_asr", cap=i, bien_the=bien_the,
                     ti_le_nhieu=ti_le)
        ra += [a, b]
    return ra


SO_LAN_THU_DAN_GIAN = 3000


# ─── _luot_chen() — Tìm lượt của bệnh nhân hoặc người nhà để chèn câu ─────────────────
# Lấy lượt đầu tiên sau lượt 1; chèn vào cuối nên câu trích cũ vẫn là chuỗi con.
def _luot_chen(input_):
    """-> số lượt (đếm từ 1) của lượt bệnh nhân / người nhà ĐẦU TIÊN sau lượt 1, hoặc
    None. Chèn vào cuối lượt nên mọi trích dẫn cũ của lượt đó vẫn là chuỗi con."""
    so = 0
    for d in input_.split("\n"):
        if not d.strip():
            continue
        so += 1
        m = dan_gian._DONG.match(d)
        if so > 1 and m and not dan_gian._la_bac_si(m.group(2)):
            return so
    return None


# ═══ cap_dan_gian() — Sinh các cặp ca gốc và bản đổi sang lời dân thường ══════════════
# Phân bổ ép theo vòng 3 cặp để cụm mơ hồ hiếm vẫn xuất hiện đủ.
def cap_dan_gian(tap, so_cap, seed=42):
    """-> 2*so_cap ca. Bản A là ca gốc, bản B là CHÍNH ca đó với lời bệnh nhân và
    người nhà đổi sang cách nói dân gian (`dan_gian.BANG`). Đáp án giống hệt trừ
    `trich_dan`.

    Giống `cap_nhieu_asr`: sinh MỘT ca rồi đổi chữ, không sinh hai ca — hai bản chỉ
    khác nhau ở cách nói, không khác nội dung buổi khám.

    Ép phân bố theo vòng 3 cặp, vì cụm mơ hồ hiếm (dưới 6% ca của khuôn phát triển):
      i % 3 == 0  có ít nhất một chỗ MO_HO
      i % 3 == 1  có ít nhất một chỗ KHÔNG nằm trong bảng chuẩn hóa (giữ lại)
      i % 3 == 2  có CHÈN một câu "gió" (`dan_gian.CHEN`, xen kẽ hai câu)
    Mỗi cặp có ít nhất HAI chỗ đổi (tính cả câu chèn).
    """
    ra = []
    for i in range(so_cap):
        for thu in range(SO_LAN_THU_DAN_GIAN):
            h = _hat("dan_gian", seed, tap, i, thu)
            a = sh.sinh_mot_ca(f"dgn_{i:03d}_A", random.Random(h),
                               sh.TuyChon(chi_tap=tap))
            chen = None
            if i % 3 == 2:
                so = _luot_chen(a["input"])
                if so is None:
                    continue
                chen = (so, dan_gian.CHEN[(i // 3) % len(dan_gian.CHEN)][0])
            vao, cho = dan_gian.doi_hoi_thoai(a["input"], chen)
            loai = {c["loai"] for c in cho}
            if len(cho) < 2:
                continue
            if i % 3 == 0 and dan_gian.MO_HO not in loai:
                continue
            if i % 3 == 1 and not any(not c["trong_bang"] and c["loai"] != "chen"
                                      for c in cho):
                continue
            break
        else:
            raise RuntimeError(f"khong sinh duoc cap dan gian thu {i}")
        b = dict(a, id=f"dgn_{i:03d}_B", input=vao,
                 dap_an=dan_gian.doi_trich_dan(a["dap_an"], a["input"]))
        if bo_trich_dan(a["dap_an"]) != bo_trich_dan(b["dap_an"]):
            raise RuntimeError(f"doi chu da doi dap an o cap {i}")
        a.update(thach_thuc="dan_gian", cap=i, bien_the="A", cho_dan_gian=[])
        b.update(thach_thuc="dan_gian", cap=i, bien_the="B", cho_dan_gian=cho)
        ra += [a, b]
    return ra


# ═══ bo_dinh_chinh() — Sinh bộ ca cập nhật và tự sửa theo từng bẫy ════════════════════
# Lần lượt mang từng bẫy trong danh sách bẫy cập nhật.
def bo_dinh_chinh(tap, so_ca, seed=42):
    """-> so_ca ca, lần lượt mang từng bẫy trong BAY_CAP_NHAT."""
    ra = []
    for i in range(so_ca):
        bay = BAY_CAP_NHAT[i % len(BAY_CAP_NHAT)]
        for thu in range(SO_LAN_THU_TOI_DA):
            h = _hat("dinh_chinh", seed, tap, i, thu)
            ca = sh.sinh_mot_ca(
                f"dch_{i:03d}", random.Random(h),
                sh.TuyChon(chi_tap=tap, ep_bay=(bay,),
                           ep_nguoi_ke=(bay == "nguon_khac_nhau")))
            if bay in ca["bay"]:
                break
        else:
            raise RuntimeError(f"khong sinh duoc ca mang bay {bay}")
        ca.update(thach_thuc="dinh_chinh", bay_chinh=bay)
        ra.append(ca)
    return ra


# ═══ main() — Sinh và ghi các bộ thử thách kèm vân tay ════════════════════════════════
# Bắt buộc --the-he; --chi chọn bộ cần sinh; chặn tập kiểm tra cuối.
def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    ap = argparse.ArgumentParser()
    # `--khuon-tap`, KHÔNG phải `--tap`: đây là TẬP KHUÔN để rút bệnh, không
    # phải tên tệp dữ liệu. Đặt tên `--tap` với mặc định "phat_trien" thì trùng
    # tên một tập của cuộc thi cũ, và `test_chan_tap_ngoai` bắt đúng điều đó.
    ap.add_argument("--khuon-tap", default="phat_trien",
                    choices=("phat_trien", "kiem_tra_cuoi"))
    ap.add_argument("--so-cap", type=int, default=40)
    ap.add_argument("--so-ca-dinh-chinh", type=int, default=60)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--ti-le-nhieu", type=float, default=0.5,
                    help="ti le tu bi bo dau trong bo nhieu ASR")
    ap.add_argument("--the-he", required=True)
    ap.add_argument("--chi", nargs="+", choices=THACH_THUC,
                    help="chi sinh cac bo nay; mac dinh bon bo cu (khong gom dan_gian), "
                         "de lenh cu chay lai ra dung tep cu")
    a = ap.parse_args()
    du_lieu.chan_tap_khoa(a.khuon_tap)

    tap = a.khuon_tap
    sinh = {"doi_chu_the": lambda: cap_doi_chu_the(tap, a.so_cap, a.seed),
            "phuong_ngu": lambda: cap_phuong_ngu(tap, a.so_cap, a.seed),
            "dinh_chinh": lambda: bo_dinh_chinh(tap, a.so_ca_dinh_chinh, a.seed),
            "nhieu_asr": lambda: cap_nhieu_asr(tap, a.so_cap, a.seed, a.ti_le_nhieu),
            "dan_gian": lambda: cap_dan_gian(tap, a.so_cap, a.seed)}
    chon = a.chi or [t for t in THACH_THUC if t != "dan_gian"]
    bo = {ten: sinh[ten]() for ten in chon}
    d = duong_dan.THU_MUC_DU_LIEU
    for ten, ds in bo.items():
        dp = d / f"thach_thuc_{ten}_{tap}.jsonl"
        dp.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in ds),
                      encoding="utf-8")
        van_tay_bo.ghi(dp, ds, a.the_he, hat=a.seed,
                       ghi_chu=f"thach thuc {ten}, khuon cua tap {tap}")
        print(f"{dp.name:48} {len(ds):4d} ca")


if __name__ == "__main__":
    main()
