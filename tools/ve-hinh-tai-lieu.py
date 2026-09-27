# -*- coding: utf-8 -*-
"""Ve hinh cho hai tai lieu Word (ban cho thanh vien nhom, ban ky thuat).

MOI SO LIEU TRONG HINH DOC TU TEP KET QUA hoac tu phep do da ghi trong docs/ket-qua/,
khong go tay tru nhung cho ghi ro nguon ben canh (phep do do tre 17/09/2026).

    python tools/ve-hinh-tai-lieu.py
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

GOC = Path(__file__).resolve().parent.parent
RA = GOC / "docs" / "tai-lieu" / "hinh"
RA.mkdir(parents=True, exist_ok=True)
KQ = GOC / "docs" / "ket-qua"

plt.rcParams.update({
    "font.family": "Times New Roman",
    "font.size": 11,
    "axes.titlesize": 12,
    "axes.labelsize": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "savefig.dpi": 200,
    "savefig.bbox": "tight",
})

# Mau theo VAI, dung chung moi hinh.
MO_HINH = "#0E5A52"
CHUONG_TRINH = "#4F6D8A"
KIEM_SOAT = "#A32B1F"
NGUOI = "#9C6B18"
NEN = "#F4F6F5"
MAU_NHANH = {"B": "#A9B7C4", "C": "#4F6D8A", "C_khoa": "#0E5A52",
             "context": "#C9A66B", "context_vai": "#B08243", "day_du": "#8C6A33"}


def hop(ax, x, y, w, h, chu, vien, nen="white", co=10.5, dam=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.06",
                                linewidth=1.4, edgecolor=vien, facecolor=nen))
    ax.text(x + w / 2, y + h / 2, chu, ha="center", va="center", fontsize=co,
            fontweight="bold" if dam else "normal", wrap=True)


def mui_ten(ax, x1, y1, x2, y2, mau="#555555", chu=None, co=9.5):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=14,
                                 linewidth=1.3, color=mau))
    if chu:
        ax.text((x1 + x2) / 2 + 0.05, (y1 + y2) / 2, chu, fontsize=co, color=mau, va="center")


def luu(fig, ten):
    fig.savefig(RA / ten)
    plt.close(fig)
    print("->", RA / ten)


# ------------------------------------------------------------ 1. duong ong
def hinh_duong_ong():
    fig, ax = plt.subplots(figsize=(7.2, 9.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.3, 11.9)
    ax.axis("off")
    buoc = [
        ("Hội thoại khám bệnh\n(mỗi lượt nói được đánh số 1, 2, 3...)", "#777777", "Đầu vào"),
        ("Bước 1. Chuẩn hoá lời thoại\nhiểu phương ngữ nhưng giữ nguyên văn", CHUONG_TRINH, "Chương trình"),
        ("Bước 2. Trích mệnh đề lâm sàng\nmỗi thông tin thành một bản ghi JSON", MO_HINH, "Mô hình ngôn ngữ\n(Qwen3-4B)"),
        ("Bước 3. Liên kết người + cập nhật trạng thái\nđính chính, diễn biến, mâu thuẫn", CHUONG_TRINH, "Chương trình"),
        ("Bước 4. Khoá bằng chứng\nđối chiếu từng bản ghi với lời thoại gốc", KIEM_SOAT, "Chương trình"),
        ("Bước 5. Xếp ưu tiên rủi ro\n+ gợi ý tối đa 3 câu hỏi làm rõ", CHUONG_TRINH, "Chương trình"),
        ("Bước 6. Viết bản nháp theo luật\nthân bản nháp + mục CẦN XÁC NHẬN", CHUONG_TRINH, "Chương trình"),
        ("Bác sĩ đọc, sửa và chịu trách nhiệm", NGUOI, "Con người"),
    ]
    h, khe = 1.12, 0.38
    y = 11.9 - h
    for i, (chu, mau, vai) in enumerate(buoc):
        hop(ax, 2.7, y, 7.1, h, chu, mau, nen="white" if mau != MO_HINH else "#E6F0EE",
            co=10.5, dam=(mau in (MO_HINH, KIEM_SOAT)))
        ax.text(2.45, y + h / 2, vai, ha="right", va="center", fontsize=10, color=mau,
                fontweight="bold")
        if i < len(buoc) - 1:
            mui_ten(ax, 6.25, y, 6.25, y - khe + 0.02)
        y -= h + khe
    ax.set_title("Hình 1. Các bước xử lý thông tin trong hệ thống", fontsize=12.5, fontweight="bold")
    luu(fig, "h1-duong-ong.png")


# ---------------------------------------------------- 2. ba duong cua menh de
def hinh_ba_duong():
    fig, ax = plt.subplots(figsize=(10, 5.4))
    ax.set_xlim(0, 12.4)
    ax.set_ylim(0, 8)
    ax.axis("off")
    hop(ax, 3.7, 6.4, 5, 1.2, "Một mệnh đề do mô hình trích ra\n(kèm lượt thoại và đoạn trích dẫn)", MO_HINH, "#E6F0EE", dam=True)
    hop(ax, 3.7, 4.3, 5, 1.2, "Khoá bằng chứng đối chiếu\nvới CHÍNH lời thoại gốc", KIEM_SOAT, dam=True)
    mui_ten(ax, 6.2, 6.4, 6.2, 5.52)
    o = [
        (0.1, "QUA\nkhông thấy vấn đề", "Vào thân bản nháp,\nkèm số lượt thoại", MO_HINH),
        (3.2, "CẢNH BÁO\nthiếu bằng chứng\nkhẳng định", "Vẫn vào thân bản nháp,\nxếp lên đầu\ndanh sách duyệt", NGUOI),
        (6.3, "CHẶN\ncó bằng chứng\nphủ định", "Xuống mục\nCẦN XÁC NHẬN,\nkèm lý do", KIEM_SOAT),
        (9.4, "BỊ THAY THẾ\nđã bị đính chính", "Không vào bản nháp,\nvẫn giữ trong\nvết kiểm tra", "#777777"),
    ]
    for x, dau, cuoi, mau in o:
        hop(ax, x, 2.0, 2.9, 1.4, dau, mau, co=9.8, dam=True)
        hop(ax, x, 0.1, 2.9, 1.5, cuoi, mau, nen=NEN, co=9.5)
        mui_ten(ax, 6.2, 4.3, x + 1.45, 3.42, mau=mau)
        mui_ten(ax, x + 1.45, 2.0, x + 1.45, 1.62, mau=mau)
    fig.suptitle("Hình 2. Bốn kết quả có thể có của một mệnh đề", y=0.99, fontsize=12.5, fontweight="bold")
    luu(fig, "h2-bon-duong-menh-de.png")


# ------------------------------------------------------------- 3. cac nhanh
def hinh_nhanh():
    thanh_phan = ["Mô hình\nviết thẳng\nhồ sơ", "Trích\nmệnh đề, viết\ntheo luật",
                  "Liên kết\nngười, cập nhật\ntrạng thái", "Khoá\nbằng chứng", "Câu hỏi\nlàm rõ"]
    nhanh = [("A", [1, 0, 0, 0, 0]), ("B", [0, 1, 0, 0, 0]), ("C", [0, 1, 1, 0, 0]),
             ("C_khoa", [0, 1, 1, 1, 0]), ("C_khoa_hoi", [0, 1, 1, 1, 1])]
    fig, ax = plt.subplots(figsize=(9.2, 4.8))
    ax.set_xlim(-2.2, len(thanh_phan))
    ax.set_ylim(-0.6, len(nhanh) + 0.4)
    ax.axis("off")
    for j, t in enumerate(thanh_phan):
        ax.text(j + 0.5, len(nhanh) + 0.05, t, ha="center", va="bottom", fontsize=9.5, fontweight="bold")
    for i, (ten, co) in enumerate(nhanh):
        yy = len(nhanh) - 1 - i
        ax.text(-0.15, yy + 0.4, ten, ha="right", va="center", fontsize=11.5, fontweight="bold")
        for j, c in enumerate(co):
            mau = (MO_HINH if j == 0 else (KIEM_SOAT if j == 3 else CHUONG_TRINH)) if c else "#EEEEEE"
            ax.add_patch(FancyBboxPatch((j + 0.08, yy + 0.08), 0.84, 0.64,
                                        boxstyle="round,pad=0,rounding_size=0.08",
                                        facecolor=mau, edgecolor="white"))
            ax.text(j + 0.5, yy + 0.4, "có" if c else "—", ha="center", va="center",
                    color="white" if c else "#999999", fontsize=10.5)
    fig.suptitle("Hình 3. Các nhánh so sánh: mỗi nhánh thêm đúng một thành phần so với nhánh trên",
                 y=1.02, fontsize=12, fontweight="bold")
    luu(fig, "h3-cac-nhanh.png")


# ---------------------------------------------------------------- 4. QLoRA
def hinh_qlora():
    fig, ax = plt.subplots(figsize=(8, 4.6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0.3, 6.2)
    ax.axis("off")
    hop(ax, 0.3, 1.2, 6.2, 4.6, "", "#999999", nen="#EFEFEF")
    ax.text(3.4, 5.35, "Mô hình nền Qwen3-4B", ha="center", fontsize=11.5, fontweight="bold")
    ax.text(3.4, 4.85, "khoảng 4 tỷ tham số, nén xuống 4 bit (NF4)", ha="center", fontsize=10)
    ax.text(3.4, 4.4, "GIỮ NGUYÊN: không thay đổi khi huấn luyện", ha="center", fontsize=10, color=KIEM_SOAT,
            fontweight="bold")
    for k in range(6):
        ax.add_patch(FancyBboxPatch((0.8 + k * 0.95, 1.6), 0.75, 2.3, boxstyle="round,pad=0,rounding_size=0.05",
                                    facecolor="#D5D5D5", edgecolor="#AAAAAA"))
    ax.text(3.4, 1.35, "36 tầng xử lý giống nhau", ha="center", fontsize=9.5, color="#555555")
    hop(ax, 7.6, 3.3, 4.1, 2.1, "Bộ chuyển đổi LoRA\nr = 16, khoảng 33 triệu tham số\n(khoảng 0,8% mô hình)\nĐƯỢC HUẤN LUYỆN",
        MO_HINH, nen="#E6F0EE", co=10, dam=True)
    hop(ax, 7.6, 0.6, 4.1, 1.9, "Tệp adapter lưu riêng\n(vài chục MB), nạp kèm\nmô hình nền khi chạy", CHUONG_TRINH,
        co=10)
    mui_ten(ax, 7.55, 4.35, 6.55, 3.6, mau=MO_HINH, chu=None)
    ax.text(7.05, 3.35, "gắn vào 7 lớp\nchiếu của\nmỗi tầng", fontsize=9, color=MO_HINH, ha="center", va="top")
    mui_ten(ax, 9.65, 3.3, 9.65, 2.52, mau=CHUONG_TRINH)
    ax.set_title("Hình 4. QLoRA: nén mô hình nền, chỉ huấn luyện một phần nhỏ gắn thêm",
                 fontsize=12, fontweight="bold")
    luu(fig, "h4-qlora.png")


# ------------------------------------------------------------ doc ket qua
def doc(tep):
    return json.loads((KQ / tep).read_text(encoding="utf-8"))


def gia_tri(d, nhanh, khoa):
    m = d[nhanh]["tong_hop"]["bang"][khoa]
    return m["gia_tri"] * 100, m["thap"] * 100, m["cao"] * 100


def cot_nhom(ax, nhom, nhanh, lay, mau=None, mo=None, nhan_so=True):
    """nhom: ten cac nhom tren truc x; lay(nhom, nhanh) -> (gia tri, thap, cao) | None."""
    n = len(nhanh)
    rong = 0.8 / n
    for j, nh in enumerate(nhanh):
        for i, g in enumerate(nhom):
            v = lay(g, nh)
            if v is None:
                continue
            gt, th, ca = v
            x = i - 0.4 + rong * (j + 0.5)
            mo_nay = mo(g) if mo else False
            ax.bar(x, gt, rong * 0.92, color=(mau or MAU_NHANH)[nh], label=nh if i == 0 else None,
                   hatch="//" if mo_nay else None, edgecolor="white" if not mo_nay else "#444444",
                   linewidth=0.6)
            if th is not None:
                ax.errorbar(x, gt, yerr=[[gt - th], [ca - gt]], fmt="none", ecolor="#333333",
                            elinewidth=0.9, capsize=2.5)
            if nhan_so:
                ax.text(x, (ca if th is not None else gt) + 0.8, f"{gt:.1f}".replace(".", ","),
                        ha="center", va="bottom", fontsize=8.3)
    ax.set_xticks(range(len(nhom)))


def hinh_sai_chu_the():
    # 19/09/2026: tep cu la ket qua the he 6 cham bang dap an the he 7 (Phu luc A.3).
    th6 = doc("cham-he-thong-thach_thuc_doi_chu_the_phat_trien-the-he-6.json")
    th7 = doc("the-he-7/cham-he-thong-thach_thuc_doi_chu_the_phat_trien.json")
    fig, ax = plt.subplots(figsize=(7.6, 4.3))
    nhom = ["B", "C", "C_khoa"]
    lay = {"Thế hệ 6": lambda nh: gia_tri(th6, nh, "sai_chu_the_tren_ghep"),
           "Thế hệ 7": lambda nh: gia_tri(th7, nh, "sai_chu_the_tren_ghep")}
    mau = {"Thế hệ 6": "#C9A66B", "Thế hệ 7": MO_HINH}
    cot_nhom(ax, nhom, list(lay), lambda g, th: lay[th](g), mau=mau)
    ax.set_xticklabels(["B\n(trích + viết luật)", "C\n(+ liên kết, trạng thái)", "C_khoa\n(+ khoá bằng chứng)"])
    ax.set_ylabel("Tỉ lệ sai chủ thể (%)")
    ax.set_ylim(0, 60)
    ax.legend(frameon=False, loc="upper right")
    ax.set_title("Hình 5. Sai chủ thể trên bộ đổi chủ thể, trước và sau khi sửa lỗi rò danh tính\n"
                 "(tính trên các mệnh đề ghép được với đáp án; vạch đen là khoảng tin cậy 95%)", fontsize=11)
    luu(fig, "h5-sai-chu-the-th6-th7.png")


def hinh_danh_doi(the_he="7", ten_tep="h6-danh-doi.png", tran=48):
    fig, axs = plt.subplots(1, 2, figsize=(9, 4.2), sharey=True)
    for ax, (tep, ten) in zip(axs, [("thach_thuc_doi_chu_the_phat_trien", "Bộ đổi chủ thể (80 ca)"),
                                    ("thach_thuc_dinh_chinh_phat_trien", "Bộ đính chính (60 ca)")]):
        d = doc(f"the-he-{the_he}/cham-he-thong-{tep}.json")
        nhom = ["loi_nghiem_trong", "bo_sot_nghiem_trong"]
        cot_nhom(ax, nhom, ["B", "C", "C_khoa"], lambda g, nh: gia_tri(d, nh, g))
        ax.set_xticklabels(["Lỗi nghiêm trọng\n(ghi sai)", "Bỏ sót nghiêm trọng\n(ghi thiếu)"])
        ax.set_title(ten, fontsize=11)
        ax.set_ylim(0, tran)
    axs[0].set_ylabel("Tỉ lệ (%) — dị ứng, thuốc, chẩn đoán")
    axs[1].legend(frameon=False, loc="upper right")
    fig.suptitle(f"Hình 6. Đánh đổi của khoá bằng chứng (thế hệ {the_he}): ghi sai giảm, nhưng ghi thiếu tăng",
                 y=1.02, fontsize=12, fontweight="bold")
    luu(fig, ten_tep)


def hinh_nam_tap():
    tap = [("viet_phat_trien", "Tập phát\ntriển"), ("thach_thuc_doi_chu_the_phat_trien", "Đổi\nchủ thể"),
           ("thach_thuc_dinh_chinh_phat_trien", "Đính\nchính"), ("thach_thuc_phuong_ngu_phat_trien", "Phương\nngữ*"),
           ("thach_thuc_nhieu_asr_phat_trien", "Nhiễu\nASR*")]
    d = {t: doc(f"the-he-7/cham-he-thong-{t}.json") for t, _ in tap}
    fig, ax = plt.subplots(figsize=(9, 4.4))
    cot_nhom(ax, [t for t, _ in tap], ["B", "C", "C_khoa"], lambda g, nh: gia_tri(d[g], nh, "loi_bat_ky"),
             mo=lambda g: g in ("thach_thuc_phuong_ngu_phat_trien", "thach_thuc_nhieu_asr_phat_trien"))
    ax.set_xticklabels([n for _, n in tap])
    ax.set_ylabel("Mệnh đề trong thân bản nháp mắc ít nhất một lỗi (%)")
    ax.set_ylim(0, 50)
    ax.legend(frameon=False, loc="upper left")
    ax.set_title("Hình 7. Tỉ lệ lỗi bất kỳ theo từng tập, thế hệ 7\n"
                 "* cột gạch chéo: lần chạy chưa ép JSON, đang chạy lại, số sẽ còn đổi", fontsize=11)
    luu(fig, "h7-loi-bat-ky-nam-tap.png")


def hinh_doi_chung_luat():
    # 19/09/2026: ca sau cot deu la the he 7. Truoc do ba cot dau la the he 6 (va la
    # ban cham sai cap), ba cot sau la the he 7 — bang tron hai the he.
    d_nhanh = doc("the-he-7/cham-he-thong-thach_thuc_doi_chu_the_phat_trien.json")
    d_luat = doc("cham-he-thong-thach_thuc_doi_chu_the_phat_trien-doi-chung-luat-the-he-7.json")
    d = {**d_nhanh, **d_luat}
    ten = [("B", "B"), ("C", "C"), ("C_khoa", "C_khoa"), ("tat_context", "context"),
           ("tat_context_vai", "context_vai"), ("tat_day_du", "day_du")]
    fig, axs = plt.subplots(1, 3, figsize=(10.5, 4.0))
    for ax, (khoa, tieu_de) in zip(axs, [("sai_chu_the_tren_ghep", "Sai chủ thể (trên mệnh đề ghép được)"),
                                         ("bo_sot", "Bỏ sót"), ("loi_nghiem_trong", "Lỗi nghiêm trọng")]):
        gt = [d[k]["tong_hop"]["bang"][khoa]["gia_tri"] * 100 for k, _ in ten]
        mau = [MAU_NHANH[n] for _, n in ten]
        ax.bar(range(len(ten)), gt, color=mau)
        for i, v in enumerate(gt):
            ax.text(i, v + 1, f"{v:.1f}".replace(".", ","), ha="center", fontsize=8.3)
        ax.set_xticks(range(len(ten)))
        ax.set_xticklabels([n for _, n in ten], rotation=35, ha="right", fontsize=9.5)
        ax.set_title(tieu_de, fontsize=10.5)
        ax.set_ylim(0, 90)
    axs[0].set_ylabel("%")
    fig.suptitle("Hình 8. Chuỗi xử lý dùng mô hình (B, C, C_khoa) so với ba đối chứng chỉ dùng luật — "
                 "bộ đổi chủ thể, thế hệ 7", y=1.03, fontsize=11.5, fontweight="bold")
    luu(fig, "h8-doi-chung-luat.png")


def hinh_do_tre():
    # Phep do Kaggle T4 ngay 17/09/2026, docs/ket-qua/do-do-tre-kaggle-17-09.json
    d = json.loads((KQ / "do-do-tre-kaggle-17-09.json").read_text(encoding="utf-8"))
    bang = {r["cau_hinh"]: r for r in d["lan2"] if "giay_moi_ca" in r}
    hang = [("1-nf4-ep", "1. Nén 4 bit + ép JSON\n(cách đang dùng)", "#777777"),
            ("3-fp16-gop-ep", "3. fp16 gộp adapter\n+ ép JSON", CHUONG_TRINH),
            ("4-fp16-gop-khong-ep", "4. fp16 gộp adapter\nkhông ép", CHUONG_TRINH),
            ("5-vllm-fp16-gop-khong-ep", "5. vLLM, fp16 gộp\nkhông ép", MO_HINH)]
    fig, ax = plt.subplots(figsize=(8, 4.0))
    y = list(range(len(hang)))[::-1]
    for yy, (k, nhan, mau) in zip(y, hang):
        v = bang[k]["giay_moi_ca"]
        ax.barh(yy, v, color=mau, height=0.6)
        khop = bang[k].get("phat_bieu_trung_voi_1")
        ghi = f"{v:.0f} giây/ca" + ("" if k.startswith("1-") else f" · phát biểu trùng cách 1: {khop * 100:.0f}%")
        ax.text(v + 3, yy, ghi, va="center", fontsize=9.5)
    ax.set_yticks(y)
    ax.set_yticklabels([h[1] for h in hang], fontsize=9.5)
    ax.set_xlim(0, 330)
    ax.set_xlabel("Thời gian trích một ca trên một card T4 (giây)")
    ax.set_title("Hình 9. Đo độ trễ khâu trích, 5 ca, Kaggle T4 (17/09/2026)", fontsize=11.5, fontweight="bold")
    luu(fig, "h9-do-tre.png")


def hinh_cat_token():
    # Do tren 80 dau ra that cua mo hinh, 17/09/2026 (xem tai lieu ky thuat, muc do tre).
    pa = [("A. Hiện tại", 1202, "#777777"), ("B. Bỏ giá trị mặc định trung tính", 969, CHUONG_TRINH),
          ("C. Bỏ mọi giá trị mặc định", 728, KIEM_SOAT), ("D. B + rút gọn tên khoá", 724, MO_HINH),
          ("E. C + rút gọn tên khoá", 556, KIEM_SOAT)]
    fig, ax = plt.subplots(figsize=(8, 3.8))
    y = list(range(len(pa)))[::-1]
    for yy, (ten, v, mau) in zip(y, pa):
        ax.barh(yy, v, color=mau, height=0.6)
        giam = "" if v == 1202 else f"  (giảm {100 - v * 100 / 1202:.0f}%)"
        rui_ro = "  rủi ro cao" if mau == KIEM_SOAT else ("  đề xuất" if mau == MO_HINH else "")
        ax.text(v + 10, yy, f"{v} token{giam}{rui_ro}", va="center", fontsize=9.5)
    ax.set_yticks(y)
    ax.set_yticklabels([p[0] for p in pa], fontsize=9.8)
    ax.set_xlim(0, 1650)
    ax.set_xlabel("Số token đầu ra trung bình mỗi ca")
    ax.set_title("Hình 10. Các cách rút gọn đầu ra và rủi ro đi kèm", fontsize=11.5, fontweight="bold")
    luu(fig, "h10-cat-token.png")


def hinh_du_lieu():
    fig, ax = plt.subplots(figsize=(9.4, 4.4))
    ax.set_xlim(0, 13.4)
    ax.set_ylim(0, 6.4)
    ax.axis("off")
    hop(ax, 0.1, 2.3, 2.6, 1.8, "Kịch bản ca\nlâm sàng tổng hợp\n(khung tình huống)", CHUONG_TRINH, co=10)
    hop(ax, 3.3, 2.3, 2.7, 1.8, "Bộ sinh dữ liệu\n(chương trình,\ncó hạt giống\nngẫu nhiên)", CHUONG_TRINH,
        co=10, dam=True)
    mui_ten(ax, 2.7, 3.2, 3.28, 3.2)
    hop(ax, 6.6, 1.6, 3.2, 3.2, "", "#777777", nen=NEN)
    ax.text(8.2, 4.5, "Mỗi ca gồm", ha="center", fontsize=10, fontweight="bold")
    hop(ax, 6.85, 3.0, 2.7, 1.1, "Hội thoại\n(có bẫy cài sẵn)", MO_HINH, co=9.8)
    hop(ax, 6.85, 1.8, 2.7, 1.1, "Đáp án: mệnh đề\n+ hồ sơ mẫu", NGUOI, co=9.8)
    mui_ten(ax, 6.0, 3.2, 6.58, 3.2)
    ra = [(5.2, "Huấn luyện", MO_HINH, "#E6F0EE"), (4.0, "Phát triển", CHUONG_TRINH, "white"),
          (2.8, "Kiểm tra cuối\n(khoá lại)", KIEM_SOAT, "white"), (1.1, "4 bộ thử thách\ntheo cặp", NGUOI, "white")]
    for yy, chu, mau, nen in ra:
        hop(ax, 10.7, yy - 0.45, 2.5, 0.95, chu, mau, nen=nen, co=10)
        mui_ten(ax, 9.82, 3.2, 10.68, yy, mau="#555555")
    ax.text(11.95, 5.95, "chia theo KỊCH BẢN, không theo ca", ha="center", fontsize=9.5, color=KIEM_SOAT)
    ax.set_title("Hình 11. Dữ liệu được sinh ra như thế nào và chia ra sao", fontsize=12, fontweight="bold")
    luu(fig, "h11-du-lieu.png")


def hinh_may_chay():
    fig, ax = plt.subplots(figsize=(9, 4.2))
    ax.set_xlim(0, 13)
    ax.set_ylim(-0.1, 5.8)
    ax.axis("off")
    hop(ax, 0.2, 2.2, 3.0, 1.8, "Máy soạn thảo\n(viết mã, sinh dữ liệu,\nchấm điểm, viết tài liệu)", "#777777", co=10)
    hop(ax, 4.6, 3.6, 3.8, 1.9, "Máy HoaiDuc\nRTX 3060 12 GB\nHUẤN LUYỆN (bf16)", MO_HINH, co=10, dam=True)
    hop(ax, 4.6, 0.5, 3.8, 1.9, "Kaggle, 2 card T4\n(miễn phí, khoảng 30 giờ/tuần)\nCHẠY SINH KẾT QUẢ", CHUONG_TRINH,
        co=10, dam=True)
    hop(ax, 9.8, 2.2, 3.0, 1.8, "Tệp kết quả\nra_<nhánh>_<tập>.jsonl\n→ chấm điểm", NGUOI, co=10)
    mui_ten(ax, 3.2, 3.5, 4.58, 4.4)
    ax.text(3.0, 4.6, "mã + dữ liệu", fontsize=9.3, color="#555555", ha="center")
    mui_ten(ax, 3.2, 2.7, 4.58, 1.5)
    mui_ten(ax, 6.5, 3.6, 6.5, 2.42, mau=MO_HINH)
    ax.text(6.65, 3.0, "adapter đã huấn luyện", fontsize=9.3, color=MO_HINH)
    mui_ten(ax, 8.4, 1.5, 9.78, 2.7)
    mui_ten(ax, 8.4, 4.5, 9.78, 3.5)
    ax.text(6.5, 0.15, "Card T4 không hỗ trợ bf16 nên không huấn luyện trên Kaggle", fontsize=9.5,
            color=KIEM_SOAT, ha="center")
    ax.set_title("Hình 12. Chia việc giữa các máy", fontsize=12, fontweight="bold")
    luu(fig, "h12-may-chay.png")


if __name__ == "__main__":
    hinh_duong_ong()
    hinh_ba_duong()
    hinh_nhanh()
    hinh_qlora()
    hinh_sai_chu_the()
    hinh_danh_doi()
    hinh_danh_doi("8", "h13-danh-doi-th8.png", 56)
    hinh_nam_tap()
    hinh_doi_chung_luat()
    hinh_do_tre()
    hinh_cat_token()
    hinh_du_lieu()
    hinh_may_chay()
