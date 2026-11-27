# -*- coding: utf-8 -*-
"""[Sinh, nạp và chia dữ liệu › Nạp và chia]
Làm gì   : Dựng dữ liệu huấn luyện cho bước rút mệnh đề từ các ca tự sinh: lời thoại vào,
           mệnh đề đáp án ra.
Vào → Ra : danh sách ca tự sinh (kèm đáp án) → danh sách ví dụ huấn luyện (hội thoại, mệnh
           đề); main() ghi tệp
Đọc từ   : dung() biến danh sách ca thành ví dụ huấn luyện; doi_mot_ca() đổi một ca; main()
           ghi tệp
Mục lục (các hàm/lớp chính):
  dung()                Dựng danh sách mẫu huấn luyện cho mô hình trích
  doi_mot_ca()          Đổi một ca thành hội thoại đánh số và đáp án JSON
  ban_lap_ly_do_kham()  Tìm mệnh đề lý do khám chỉ là bản sao
  main()                Chia train và giữ lại rồi ghi tệp huấn luyện trích
Gọi tới  : duong_ong/b1_vi_du_mau_loi_nhac, he_thong/duong_dan,
           huan_luyen/chon_mo_hinh_bakeoff
Dùng bởi : do_luong/cham_he_thong, do_luong/danh_gia_khoa, do_luong/do_trich,
           duong_ong/b7_ban_duyet_html
Tên cũ   : du_lieu_trich.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Dựng dữ liệu HUẤN LUYỆN cho khâu trích, từ bộ hội thoại Việt tự sinh.

VÌ SAO. Ba phép đo độc lập đều chỉ vào cùng một chỗ: khâu TRÍCH XUẤT là nút
thắt, không phải luật.

    hội thoại thật, đúng quy gán   A_nen 73,2%   C 57,4%
    bộ chẩn đoán tự sinh           A     92%     C 93%
    `quan_he` trên hội thoại thật  "khong" ở cả 282 phát biểu

Nhánh A được huấn luyện trên 1.357 bệnh án; khâu trích của C dùng mô hình nền
với 5 ví dụ. Chỗ không cần đo đã được gỡ một phần bằng nhánh A_nen (zero-shot,
cùng mô hình) — và A_nen VẪN hơn C về quy gán. Nhưng A_nen được huấn luyện
trước đó cho tác vụ VIẾT BỆNH ÁN, còn khâu trích thì chưa bao giờ được huấn
luyện cho tác vụ của nó.

Bộ `hoi_thoai_viet.jsonl` (1.000 ca, 8.361 mệnh đề) có đáp án cấu trúc, nên
dùng được làm dữ liệu huấn luyện cho chính khâu trích.

GIỚI HẠN CỦA BỘ NHÃN NÀY — phải ghi vào báo cáo, không được lờ đi:

  có       chu_the (238/8.361 không phải bệnh nhân), noi_dung, moc_thoi_gian,
           phu_dinh, tinh_huong (thực tế / kế hoạch), lượt làm bằng chứng
  KHÔNG có `do_chac_chan` -> không đẩy được mục "chưa ghi nhận".
  KHÔNG có `gia_dinh`     -> tinh_huong chỉ có "thực tế" và "kế hoạch".

`quan_he` — SỬA 09/09/2026. Trước đó đáp án không có trường này, nên mọi bản
ghi đều mang "khong": 2.231 ca ví dụ âm, KHÔNG MỘT ví dụ dương. Đó là lý do
đầy đủ của con số `quan_he` = "khong" ở 282/282 trên hội thoại thật — mô hình
học đúng thứ nó được dạy. Bộ sinh giờ ghi lại quan hệ (461 đính chính + 442
diễn biến trên 3.000 ca), nên bộ nhãn này dạy được cơ chế quan hệ.

Nên kết quả của thí nghiệm này nói được về QUY GÁN CHỦ THỂ và (từ 09/09/2026)
về QUAN HỆ. Vẫn chưa nói được về mức chắc chắn và tình huống gia đình.

    python -m src.bo_du_lieu.du_lieu_huan_luyen_trich --giu-lai 100
"""
import io
import json
import sys

from src.huan_luyen import chon_mo_hinh_bakeoff as bakeoff
from src.he_thong import duong_dan as duong_dan

# Trường nào trong đáp án ánh xạ sang trường nào của LUOC_DO.
# `muc` không có trong lược đồ — bỏ đi chứ không nhét bừa vào, vì mô hình sẽ
# học sinh ra một trường mà bộ ép JSON sẽ chặn.
MAC_DINH = {"do_chac_chan": "chắc chắn", "thoi_gian_su_kien": "chưa rõ",
            "quan_he": "không", "quan_he_voi": None}


# ═══ ban_lap_ly_do_kham() — Tìm mệnh đề lý do khám chỉ là bản sao ═════════════════════
# Trả chỉ số các mệnh đề lý do khám trùng chủ thể và nội dung với mệnh đề khác.
def ban_lap_ly_do_kham(dap_an):
    """Chỉ số các mệnh đề LÝ DO KHÁM là BẢN SAO của một mệnh đề khác (cùng chủ thể,
    cùng nội dung).

    Bộ sinh ghi triệu chứng chính HAI lần: một ở bệnh sử, một ở lý do khám. Lược đồ
    trích không có trường `muc`, nên bản sao chỉ dạy mô hình viết TRÙNG — và bản
    nháp ra hai dòng "sốt cao" liền nhau trong bệnh sử (mục lý do khám do
    `sinh_benh_an.sinh` tự lấy dòng đầu bệnh sử). Tìm ra 11/09/2026 khi chấm trích
    HOÀN HẢO qua đường ống (`cham_he_thong`). Một định nghĩa, dùng chung cho nhãn
    huấn luyện, cho phép đo khâu trích và cho phép chấm hệ thống.
    """
    thuong = {(m.get("chu_the"), m.get("noi_dung")) for m in dap_an
              if m.get("muc") != "LÝ DO KHÁM BỆNH"}
    return {i for i, m in enumerate(dap_an) if m.get("muc") == "LÝ DO KHÁM BỆNH"
            and (m.get("chu_the"), m.get("noi_dung")) in thuong}


# ═══ doi_mot_ca() — Đổi một ca thành hội thoại đánh số và đáp án JSON ═════════════════
# Bỏ mệnh đề không có bằng chứng và ánh xạ lại chỉ số quan hệ cho đúng.
def doi_mot_ca(k):
    """Một ca -> (chuỗi hội thoại đã đánh số, chuỗi JSON đáp án).

    ÁNH XẠ LẠI `quan_he_voi`. Trong đáp án, `quan_he_voi` là chỉ số trong
    `dap_an`. Nhưng vòng lặp dưới BỎ các mệnh đề không có bằng chứng, nên chỉ
    số bị xê dịch. Không ánh xạ lại thì một phần ba số quan hệ sẽ trỏ sang một
    bản ghi khác hẳn — và đó là lỗi im lặng: JSON vẫn hợp lệ, mô hình vẫn học
    được, chỉ là học sai.
    """
    danh_so, so_luot = bakeoff.danh_so_luot(k["input"])
    dap_an = k["dap_an"]

    # Vòng 1: quyết định giữ mệnh đề nào, và nhớ chỉ số mới của nó.
    giu, chi_so_moi = [], {}
    lap = ban_lap_ly_do_kham(dap_an)
    for i, m in enumerate(dap_an):
        if i in lap:
            continue                       # bản sao lý do khám — xem hàm trên
        luot = [n for n in (m.get("luot") or []) if 1 <= n <= so_luot]
        if not luot:
            continue                       # không có bằng chứng thì không đẩy
        chi_so_moi[i] = len(giu)
        giu.append((i, m, luot))

    # Vòng 2: dựng bản ghi, ánh xạ lại `quan_he_voi`.
    ps = []
    for i, m, luot in giu:
        quan_he = m.get("quan_he") or MAC_DINH["quan_he"]
        dich = m.get("quan_he_voi")
        dich_moi = chi_so_moi.get(dich) if dich is not None else None
        if dich_moi is None:
            # Bản ghi kia bị bỏ (không có bằng chứng) -> không còn quan hệ để
            # đẩy. Hạ về "khong" chứ KHÔNG giữ quan hệ trỏ vào khoảng không.
            quan_he, dich_moi = MAC_DINH["quan_he"], None
        ban_ghi = {
            "chu_the": m["chu_the"],
            "noi_dung": m["noi_dung"],
            # ĐỌC TỪ ĐÁP ÁN từ 11/09/2026. Trước đó là MAC_DINH ở mỗi nhãn — cùng
            # hình với `thoi_gian_su_kien` bên dưới, lần thứ sau của họ lỗi. Bộ
            # cũ (đáp án không có trường này) vẫn lùi về mặc định.
            "do_chac_chan": m.get("do_chac_chan") or MAC_DINH["do_chac_chan"],
            "phu_dinh": bool(m.get("phu_dinh", False)),
            "tinh_huong": m.get("tinh_huong", "thực tế"),
            # ĐỌC TỪ ĐÁP ÁN, không đóng cứng mặc định.
            #
            # Trước 11/09/2026 dòng này là `MAC_DINH["thoi_gian_su_kien"]`, nên
            # MỌI nhãn huấn luyện mang "chưa rõ" — một trường hằng số. Mô hình
            # học đúng thứ nó được dạy và xuất "chưa rõ" ở **cả 462** phát biểu
            # trên tập phát triển, làm luật `thoi_gian_su_kien == "qua khu" ->
            # TIEN SU BENH` của `sinh_benh_an` thành mã chết.
            #
            # Cùng hình với `quan_he` (09/09): một trường khai trong lược đồ,
            # được một khâu sau đọc, và không bao giờ có giá trị thứ hai trong
            # nhãn. Lần thứ tư của họ lỗi này.
            "thoi_gian_su_kien": (m.get("thoi_gian_su_kien")
                                  or MAC_DINH["thoi_gian_su_kien"]),
            "moc_thoi_gian": m.get("moc_thoi_gian"),
            "quan_he": quan_he,
            "quan_he_voi": dich_moi,
            "luot_thoai": luot,
        }
        # Trích dẫn đi THEO lượt: bỏ lượt nào (ngoài khoảng) thì bỏ trích dẫn của
        # lượt đó, để hai danh sách vẫn thẳng hàng từng phần tử. Bộ cũ không có
        # hai trường này thì bản ghi không mang chúng — không đẩy một giá trị rỗng.
        trich = [td for n, td in zip(m.get("luot") or [], m.get("trich_dan") or [])
                 if 1 <= n <= so_luot]
        if trich:
            ban_ghi["trich_dan"] = trich
        if m.get("hanh_vi"):
            ban_ghi["hanh_vi"] = m["hanh_vi"]
        # Chi tiết thuốc (15/09/2026). Chỉ phát biểu thuốc mang trường này — các
        # phát biểu khác không mang, để mô hình không học sinh `"thuoc": null` ở mỗi
        # bản ghi. Quên dòng này là họ lỗi "khai mà không đẩy" lần thứ bảy.
        if m.get("thuoc"):
            ban_ghi["thuoc"] = m["thuoc"]
        ps.append(ban_ghi)
    return danh_so, json.dumps({"phat_bieu": ps}, ensure_ascii=False)


# ═══ dung() — Dựng danh sách mẫu huấn luyện cho mô hình trích ═════════════════════════
# Mỗi mẫu có id, lời nhắc đầy đủ như lúc suy luận và đầu ra.
def dung(danh_sach, vi_du=False):
    """-> danh sách {id, input, output} đúng định dạng `train_baseline` đọc.

    `input` là LỜI NHẮC ĐẦY ĐỦ giống hệt lúc suy luận (`bakeoff.trich`), để
    mô hình học đúng điều kiện nó sẽ gặp. Khác một chữ là lệch phân phối.
    `vi_du=False`: khi đã huấn luyện thì không cần 5 ví dụ mẫu nữa, và bỏ đi
    thì lời nhắc ngắn hơn ba lần.
    """
    from src.duong_ong.b1_vi_du_mau_loi_nhac import VI_DU
    ra = []
    for k in danh_sach:
        danh_so, dap_an = doi_mot_ca(k)
        loi_nhac = bakeoff.HUONG_DAN + (
            f"\n\n{VI_DU}\n\nBây giờ đến lượt bạn." if vi_du else "")
        ra.append({"id": k["id"],
                   "input": f"{loi_nhac}\n\nHội thoại:\n{danh_so}",
                   "output": dap_an})
    return ra


# ═══ main() — Chia train và giữ lại rồi ghi tệp huấn luyện trích ══════════════════════
# Tách theo khuôn bệnh hoặc dùng tập đã chia; in số ca và mệnh đề.
def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--nguon", default="hoi_thoai_viet_5000.jsonl")
    # Tập đã được chia sẵn bởi `tach_tap_viet` (theo KHUÔN BỆNH). Dùng nó
    # thay vì tự chia lại, để khâu trích và nhánh A học trên ĐÚNG một tập.
    ap.add_argument("--da-chia", action="store_true")
    ap.add_argument("--giu-khuon", type=int, default=4,
                    help="so KHUON BENH giu rieng — don vi doc lap la khuon, "
                         "khong phai dong")
    ap.add_argument("--hau-to", default="",
                    help="hau to cho ten tep ra, vi du _v2")
    ap.add_argument("--hau-to-nguon", default=None,
                    help="hau to cho ten tep nguon da chia (neu khac --hau-to)")
    a = ap.parse_args()

    d = duong_dan.THU_MUC_DU_LIEU

    ht_nguon = a.hau_to_nguon if a.hau_to_nguon is not None else a.hau_to
    if a.da_chia:
        train = [json.loads(x) for x in
                 open(d / f"viet_train{ht_nguon}.jsonl", encoding="utf-8") if x.strip()]
        giu = [json.loads(x) for x in
               open(d / f"viet_phat_trien{ht_nguon}.jsonl", encoding="utf-8") if x.strip()]
    else:
        ca = [json.loads(x) for x in open(d / a.nguon, encoding="utf-8") if x.strip()]
        # Tách theo KHUÔN BỆNH, không theo dòng: hai dòng cùng khuôn gần như
        # là một bài, cắt theo dòng thì tập kiểm chỉ đo "gặp lại khuôn đã học".
        khuon = sorted({k["benh"] for k in ca})
        giu_khuon = set(khuon[-a.giu_khuon:]) if a.giu_khuon else set()
        giu = [k for k in ca if k["benh"] in giu_khuon]
        train = [k for k in ca if k["benh"] not in giu_khuon]

    for ten, ds in (("trich_train", train), ("trich_giu_lai", giu)):
        if not ds:
            continue
        mau = dung(ds)
        dp = d / f"{ten}{a.hau_to}.jsonl"
        dp.write_text("\n".join(json.dumps(m, ensure_ascii=False) for m in mau),
                      encoding="utf-8")
        so_md = sum(len(json.loads(m["output"])["phat_bieu"]) for m in mau)
        khac = sum(1 for m in mau
                   for p in json.loads(m["output"])["phat_bieu"]
                   if p["chu_the"] != "bệnh nhân")
        print(f"{dp.name:22} {len(mau):5} ca  {so_md:6} menh de  "
              f"{khac:4} khong phai benh nhan ({100*khac/max(1,so_md):.1f}%)")

    khuon_train = {k["benh"] for k in train}
    khuon_giu = {k["benh"] for k in giu}
    print(f"\nKhuon benh: train {len(khuon_train)}, giu lai {len(khuon_giu)}, "
          f"chi co o tap giu lai: {sorted(khuon_giu - khuon_train)}")


if __name__ == "__main__":
    main()
