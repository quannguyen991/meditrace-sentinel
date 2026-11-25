import crypto from "crypto";
import type express from "express";
import { db, ghiNhatKy } from "../csdl";
import { kiemCauHoi } from "../tro-ly/an-danh";
import { docCaiDat, ghiCaiDat, ghiNgoaiBat, ngoaiBat } from "../tro-ly/cai-dat-tro-ly";
import { xuLyViecTroLy } from "../tro-ly/chay-viec";
import type { Phu } from "../tro-ly/dieu-phoi";
import type { TacTuMa, YeuCauTroLy } from "../tro-ly/kieu";
import { taoKhoViec } from "../tro-ly/viec-tro-ly";
import { traLoi, TUOI_VIEC_TOI_DA_MS } from "./dung-chung";
import { goiNgoai, NGOAI } from "./llm-ngoai";
import { datTuKhoaTraCuu, soanTraLoiCoNguon, type TaiLieu, timTaiLieuTheoTuKhoa } from "./tra-cuu";

const TRO_LY_TOI_DA_DONG_THOI = 2;
const TRO_LY_CHO_TRUC_TIEP_MS = Number(process.env.MEDITRACE_TRO_LY_CHO_MS) || 1500;
const dungToken = (u: any) => (u?.prompt_tokens || 0) + (u?.completion_tokens || 0);
const TAC_TU_NGOAI_GIAO_DIEN: ReadonlySet<string> = new Set(["tim_kiem", "tra_loi", "doi_chieu", "dieu_phoi"]);

export function dangKyTroLyRoutes(app: express.Express) {
  const khoTroLy = taoKhoViec(db);

  const phuThat: Phu = {
    async goiNgoai(heThong, nguoiDung, maxToken) {
      return goiNgoai(heThong, nguoiDung, maxToken);
    },
    async datTuKhoa(truyVan) {
      const r = await datTuKhoaTraCuu(truyVan, "", "", false);
      if (!r.tuKhoa?.pubmed) throw new Error("mô hình không trả được từ khoá tìm kiếm");
      return { tuKhoa: r.tuKhoa, token: dungToken(r.b1.usage), giay: r.b1.seconds };
    },
    async timTaiLieu(tuKhoa, cauHoi, nguon) {
      return timTaiLieuTheoTuKhoa({ cauHoi, tuKhoa, nguon: nguon ?? {} });
    },
    async soanTraLoi(a) {
      const taiLieu = a.taiLieu as TaiLieu[];
      const r = await soanTraLoiCoNguon({
        cauHoi: a.cauHoi,
        caKham: a.caAnDanh,
        coCa: a.caAnDanh.trim().length > 0,
        caAnDanh: true,
        taiLieu,
        daTra: a.daTra as Array<{ nguon: string; so: number; ghiChu?: string }>,
        boLacDe: a.boLacDe,
        loiTim: a.loiTim,
        tuKhoaRa: a.tuKhoaRa,
        kcb: taiLieu.filter((t) => t.nguon === "Bộ Y tế"),
        phacDo: taiLieu.filter((t) => t.nguon === "Phác đồ BYT"),
      });
      return { traLoi: { ...r, source: "mo_hinh_ngoai" }, token: dungToken(r.usage), giay: r.seconds };
    },
    ngoaiMo: () => ngoaiBat(db, process.env) && Boolean(NGOAI.key && NGOAI.base),
    bay: () => Date.now(),
  };

  function kichHoatTroLy() {
    for (
      let v = khoTroLy.layViecTiepTheo(TRO_LY_TOI_DA_DONG_THOI);
      v;
      v = khoTroLy.layViecTiepTheo(TRO_LY_TOI_DA_DONG_THOI)
    ) {
      const viec = v;
      void xuLyViecTroLy(phuThat, khoTroLy, viec, (hanhDong, chiTiet) => ghiNhatKy(viec.nguoiDungId, hanhDong, chiTiet))
        .catch((e) => console.error("[tro-ly] lỗi không bắt được:", e))
        .finally(kichHoatTroLy);
    }
  }

  {
    const kp = khoTroLy.khoiPhuc();
    if (kp.chayLai || kp.thatBai) {
      console.log(`[tro-ly] khởi động lại: chạy lại ${kp.chayLai} việc, bỏ ${kp.thatBai} việc quá số lần cho phép`);
    }
    kichHoatTroLy();
  }

  const chiQuanTriTroLy: express.RequestHandler = (req, res, next) =>
    req.nguoiDung?.vai === "quan_tri" ? next() : res.status(403).json({ error: "Chỉ quản trị làm được việc này" });

  function giaoKetQuaTroLy(
    res: express.Response,
    id: number,
    nguoiDungId: number,
    t: NonNullable<ReturnType<typeof khoTroLy.trangThai>>,
  ) {
    khoTroLy.xoa(id, nguoiDungId);
    if (t.trangThai === "xong") {
      const dungNgoai =
        (t.tienTrinh?.dieuPhoi?.token ?? 0) > 0 ||
        !!t.tienTrinh?.buoc.some((b) => TAC_TU_NGOAI_GIAO_DIEN.has(b.tacTu) && ["xong", "dang", "loi"].includes(b.trangThai));
      return res.json({
        ketQua: t.ketQua,
        tienTrinh: t.tienTrinh,
        source: dungNgoai ? "mo_hinh_ngoai" : "tai_cho",
        ...(dungNgoai ? { model: NGOAI.model } : {}),
      });
    }
    const het = t.ma === "crash_recovery_exhausted";
    return res.status(500).json({
      error: het ? "Máy chủ khởi động lại khi trợ lý đang làm và đã thử lại quá số lần cho phép. Hãy hỏi lại." : "Trợ lý gặp lỗi. Hãy hỏi lại.",
      code: t.ma || undefined,
    });
  }

  app.get("/api/tro-ly/cai-dat", (req, res) => {
    res.json({
      batTacTu: docCaiDat(db, req.nguoiDung!.id).batTacTu,
      ngoaiBat: ngoaiBat(db, process.env),
      ngoaiCoKhoa: Boolean(NGOAI.key && NGOAI.base),
    });
  });

  app.put("/api/tro-ly/cai-dat", (req, res) => {
    const ds = req.body?.batTacTu;
    if (!Array.isArray(ds)) return res.status(400).json({ error: "Thiếu danh sách tác tử" });
    ghiCaiDat(db, req.nguoiDung!.id, ds as TacTuMa[]);
    res.json({ batTacTu: docCaiDat(db, req.nguoiDung!.id).batTacTu });
  });

  app.put("/api/tro-ly/cai-dat/ngoai", chiQuanTriTroLy, (req, res) => {
    if (typeof req.body?.bat !== "boolean") return res.status(400).json({ error: "Thiếu bat (true/false)" });
    ghiNgoaiBat(db, req.body.bat);
    ghiNhatKy(req.nguoiDung!.id, "tro_ly_cong_tac_ngoai", req.body.bat ? "bat" : "tat");
    res.json({ ngoaiBat: ngoaiBat(db, process.env) });
  });

  app.post("/api/tro-ly", async (req, res) => {
    try {
      const { cauHoi, menhDe, nguCanh, nguon } = req.body || {};
      const k = kiemCauHoi(String(cauHoi ?? "").slice(0, 1000));
      if (!k.ok) {
        return res.status(400).json(
          k.lyDo === "rong"
            ? { error: "Thiếu câu hỏi" }
            : {
                error: "Câu hỏi còn dấu hiệu danh tính (tên, ngày, địa chỉ hay số liên lạc). Hãy bỏ các chi tiết đó rồi hỏi lại — hệ thống không gửi câu này ra ngoài.",
                code: "cau_hoi_co_danh_tinh",
                lyDo: k.lyDo,
              },
        );
      }
      const ds: any[] = Array.isArray(menhDe) ? menhDe.slice(0, 300) : [];
      const gon = ds
        .filter((m) => m && typeof m === "object")
        .map((m) => ({
          text: String(m.text ?? "").slice(0, 400),
          section: String(m.section ?? ""),
          subject: m.subject == null ? null : String(m.subject).slice(0, 60),
          negated: m.negated === true,
          certainty: m.certainty == null ? null : String(m.certainty),
          drug: m.drug == null ? null : String(m.drug).slice(0, 120),
        }));
      const nc = nguCanh && typeof nguCanh === "object" ? nguCanh : {};
      const uid = req.nguoiDung!.id;
      const yeuCau: YeuCauTroLy = {
        cauHoi: k.cau,
        menhDe: gon,
        nguCanh: {
          tuoi: typeof nc.tuoi === "number" ? nc.tuoi : null,
          gioi: typeof nc.gioi === "string" ? nc.gioi : null,
          coThai: typeof nc.coThai === "boolean" ? nc.coThai : null,
        },
        nguon: nguon && typeof nguon === "object" ? nguon : undefined,
        batTacTu: docCaiDat(db, uid).batTacTu,
      };
      khoTroLy.donViecCu(TUOI_VIEC_TOI_DA_MS);
      const noiDung = JSON.stringify(yeuCau);
      const id = khoTroLy.them(uid, crypto.createHash("sha256").update(`${uid}|${noiDung}`).digest("hex"), yeuCau);
      kichHoatTroLy();
      const han = Date.now() + TRO_LY_CHO_TRUC_TIEP_MS;
      for (;;) {
        const t = khoTroLy.trangThai(id, uid);
        if (t && (t.trangThai === "xong" || t.trangThai === "that_bai")) return giaoKetQuaTroLy(res, id, uid, t);
        if (Date.now() >= han) break;
        await new Promise((r) => setTimeout(r, 200));
      }
      const t = khoTroLy.trangThai(id, uid);
      res.status(202).json({ jobId: String(id), tienTrinh: t?.tienTrinh ?? null });
    } catch (err) {
      traLoi(res, err);
    }
  });

  app.get("/api/tro-ly/:id", (req, res) => {
    const id = Number(req.params.id);
    const uid = req.nguoiDung!.id;
    const t = Number.isInteger(id) ? khoTroLy.trangThai(id, uid) : null;
    if (!t) return res.status(404).json({ error: "Không thấy việc này (có thể đã giao kết quả hoặc quá hạn). Hãy hỏi lại." });
    if (t.trangThai === "xong" || t.trangThai === "that_bai") return giaoKetQuaTroLy(res, id, uid, t);
    res.status(202).json({ jobId: req.params.id, tienTrinh: t.tienTrinh });
  });
}
