import crypto from "crypto";
import { EventEmitter } from "events";
import type express from "express";
import { db, ghiNhatKy } from "../csdl";
import { datTuKhoaTraCuu, soanTraLoiCoNguon, type TaiLieu, timTaiLieuTheoTuKhoa } from "../tra-cuu/dich-vu-tra-cuu";
import { kiemCauHoi } from "../tro-ly/an-danh";
import { docCaiDat, ghiCaiDat, ghiNgoaiBat, ngoaiBat } from "../tro-ly/cai-dat-tro-ly";
import { xuLyViecTroLy } from "../tro-ly/chay-viec";
import type { Phu } from "../tro-ly/dieu-phoi";
import type { TacTuMa, YeuCauTroLy } from "../tro-ly/kieu";
import { type KhoViec, taoKhoViec } from "../tro-ly/viec-tro-ly";
import { traLoi, TUOI_VIEC_TOI_DA_MS } from "./dung-chung";
import { chayVoiNguoiDung, goiNgoai, NGOAI } from "./llm-ngoai";

const TRO_LY_TOI_DA_DONG_THOI = 2;
const TRO_LY_CHO_TRUC_TIEP_MS = Number(process.env.MEDITRACE_TRO_LY_CHO_MS) || 1500;
const CHU_KY_DON_TRO_LY_MS = 5 * 60_000;
const dungToken = (u: any) => (u?.prompt_tokens || 0) + (u?.completion_tokens || 0);
const TAC_TU_NGOAI_GIAO_DIEN: ReadonlySet<string> = new Set(["tim_kiem", "tra_loi", "doi_chieu", "dieu_phoi"]);

export function dangKyTroLyRoutes(app: express.Express) {
  const khoGoc = taoKhoViec(db);
  const kenhSuKien = new EventEmitter();
  kenhSuKien.setMaxListeners(0);
  const boHuyTheoViec = new Map<number, AbortController>();

  const phatSuKien = (id: number) => kenhSuKien.emit(`viec:${id}`);

  const khoTroLy: KhoViec = {
    ...khoGoc,
    ghiTienTrinh(id, tt) {
      khoGoc.ghiTienTrinh(id, tt);
      phatSuKien(id);
    },
    xong(id, kq) {
      khoGoc.xong(id, kq);
      phatSuKien(id);
    },
    loi(id, ma) {
      khoGoc.loi(id, ma);
      phatSuKien(id);
    },
    huy(id, nguoiDungId) {
      const ok = khoGoc.huy(id, nguoiDungId);
      if (ok) {
        boHuyTheoViec.get(id)?.abort();
        phatSuKien(id);
      }
      return ok;
    },
  };

  // Dọn nhẹ định kỳ các việc đã kết thúc quá 30 phút (unref để không treo tiến trình khi đóng server/test)
  const boDonDinhKy = setInterval(() => {
    try {
      if (db.isOpen) khoTroLy.donViecCu(TUOI_VIEC_TOI_DA_MS);
    } catch {}
  }, CHU_KY_DON_TRO_LY_MS);
  boDonDinhKy.unref?.();

  function taoPhuChoViec(viecId: number, signal: AbortSignal): Phu {
    const chanNeuDaHuy = () => {
      if (signal.aborted || khoTroLy.daHuy(viecId)) {
        throw new Error("Việc đã được người dùng hủy");
      }
    };
    return {
      async goiNgoai(heThong, nguoiDung, maxToken) {
        chanNeuDaHuy();
        return goiNgoai(heThong, nguoiDung, maxToken, {}, signal);
      },
      async datTuKhoa(truyVan) {
        chanNeuDaHuy();
        const r = await datTuKhoaTraCuu(truyVan, "", "", false, signal);
        if (!r.tuKhoa?.pubmed) throw new Error("mô hình không trả được từ khoá tìm kiếm");
        return { tuKhoa: r.tuKhoa, token: dungToken(r.b1.usage), giay: r.b1.seconds };
      },
      async timTaiLieu(tuKhoa, cauHoi, nguon) {
        chanNeuDaHuy();
        return timTaiLieuTheoTuKhoa({ cauHoi, tuKhoa, nguon: nguon ?? {} });
      },
      async soanTraLoi(a) {
        chanNeuDaHuy();
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
          signal,
        });
        return { traLoi: { ...r, source: "mo_hinh_ngoai" }, token: dungToken(r.usage), giay: r.seconds };
      },
      ngoaiMo: () => !signal.aborted && !khoTroLy.daHuy(viecId) && ngoaiBat(db, process.env) && Boolean(NGOAI.key && NGOAI.base),
      bay: () => Date.now(),
    };
  }

  function kichHoatTroLy() {
    for (
      let v = khoTroLy.layViecTiepTheo(TRO_LY_TOI_DA_DONG_THOI);
      v;
      v = khoTroLy.layViecTiepTheo(TRO_LY_TOI_DA_DONG_THOI)
    ) {
      const viec = v;
      const ctl = new AbortController();
      boHuyTheoViec.set(viec.id, ctl);
      phatSuKien(viec.id);
      // Lời gọi mô hình ngoài trong việc nền tính hạn mức theo người tạo việc.
      void chayVoiNguoiDung(viec.nguoiDungId, () =>
        xuLyViecTroLy(taoPhuChoViec(viec.id, ctl.signal), khoTroLy, viec, (hanhDong, chiTiet) =>
          ghiNhatKy(viec.nguoiDungId, hanhDong, chiTiet),
        ),
      )
        .catch((e) => console.error("[tro-ly] lỗi không bắt được:", e))
        .finally(() => {
          boHuyTheoViec.delete(viec.id);
          kichHoatTroLy();
        });
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

  function dongGoiThanhCong(t: NonNullable<ReturnType<typeof khoTroLy.trangThai>>) {
    const dungNgoai =
      (t.tienTrinh?.dieuPhoi?.token ?? 0) > 0 ||
      !!t.tienTrinh?.buoc.some((b) => TAC_TU_NGOAI_GIAO_DIEN.has(b.tacTu) && ["xong", "dang", "loi"].includes(b.trangThai));
    return {
      ketQua: t.ketQua,
      tienTrinh: t.tienTrinh,
      source: dungNgoai ? "mo_hinh_ngoai" : "tai_cho",
      ...(dungNgoai ? { model: NGOAI.model } : {}),
    };
  }

  function dongGoiLoi(t: NonNullable<ReturnType<typeof khoTroLy.trangThai>>) {
    if (t.trangThai === "da_huy" || t.ma === "da_huy") {
      return { status: 410, body: { error: "Việc trợ lý này đã được hủy.", code: "da_huy" } };
    }
    const het = t.ma === "crash_recovery_exhausted";
    return {
      status: 500,
      body: {
        error: het
          ? "Máy chủ khởi động lại khi trợ lý đang làm và đã thử lại quá số lần cho phép. Hãy hỏi lại."
          : "Trợ lý gặp lỗi. Hãy hỏi lại.",
        code: t.ma || undefined,
      },
    };
  }

  /**
   * KHÔNG xoá việc ngay lần đọc đầu tiên (sửa dứt điểm Read-Once Delete Race để F5, rớt mạng,
   * hoặc 2 tab cùng `khoaTrung` đều đọc lại được kết quả trong vòng 30 phút mà không bị 404).
   */
  function giaoKetQuaTroLy(
    res: express.Response,
    t: NonNullable<ReturnType<typeof khoTroLy.trangThai>>,
  ) {
    if (t.trangThai === "xong") {
      return res.json(dongGoiThanhCong(t));
    }
    const { status, body } = dongGoiLoi(t);
    return res.status(status).json(body);
  }

  app.get("/api/tro-ly/cai-dat", (req, res) => {
    try {
      res.json({
        batTacTu: docCaiDat(db, req.nguoiDung!.id).batTacTu,
        ngoaiBat: ngoaiBat(db, process.env),
        ngoaiCoKhoa: Boolean(NGOAI.key && NGOAI.base),
      });
    } catch (err) {
      traLoi(res, err);
    }
  });

  app.put("/api/tro-ly/cai-dat", (req, res) => {
    try {
      const ds = req.body?.batTacTu;
      if (!Array.isArray(ds)) return res.status(400).json({ error: "Thiếu danh sách tác tử" });
      ghiCaiDat(db, req.nguoiDung!.id, ds as TacTuMa[]);
      res.json({ batTacTu: docCaiDat(db, req.nguoiDung!.id).batTacTu });
    } catch (err) {
      traLoi(res, err);
    }
  });

  app.put("/api/tro-ly/cai-dat/ngoai", chiQuanTriTroLy, (req, res) => {
    try {
      if (typeof req.body?.bat !== "boolean") return res.status(400).json({ error: "Thiếu bat (true/false)" });
      ghiNgoaiBat(db, req.body.bat);
      ghiNhatKy(req.nguoiDung!.id, "tro_ly_cong_tac_ngoai", req.body.bat ? "bat" : "tat");
      res.json({ ngoaiBat: ngoaiBat(db, process.env) });
    } catch (err) {
      traLoi(res, err);
    }
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
                error:
                  "Câu hỏi còn dấu hiệu danh tính (tên, ngày, địa chỉ hay số liên lạc). Hãy bỏ các chi tiết đó rồi hỏi lại — hệ thống không gửi câu này ra ngoài.",
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
        if (t && (t.trangThai === "xong" || t.trangThai === "that_bai" || t.trangThai === "da_huy")) {
          return giaoKetQuaTroLy(res, t);
        }
        if (Date.now() >= han) break;
        await new Promise((r) => setTimeout(r, 150));
      }
      const t = khoTroLy.trangThai(id, uid);
      res.status(202).json({ jobId: String(id), tienTrinh: t?.tienTrinh ?? null });
    } catch (err) {
      traLoi(res, err);
    }
  });

  /** Luồng SSE đẩy tiến trình & kết quả thời gian thực cho một việc trợ lý. */
  app.get("/api/tro-ly/:id/stream", (req, res) => {
    try {
      const id = Number(req.params.id);
      const uid = req.nguoiDung!.id;
      if (!Number.isInteger(id) || id <= 0) {
        return res.status(400).json({ error: "Mã việc không hợp lệ" });
      }
      const banDau = khoTroLy.trangThai(id, uid);
      if (!banDau) {
        return res.status(404).json({ error: "Không thấy việc này (có thể đã quá hạn 30 phút). Hãy hỏi lại." });
      }

      res.status(200);
      res.setHeader("Content-Type", "text/event-stream; charset=utf-8");
      res.setHeader("Cache-Control", "no-cache, no-transform");
      res.setHeader("Connection", "keep-alive");
      res.setHeader("X-Accel-Buffering", "no");
      res.flushHeaders?.();

      let daDong = false;
      let banChupTruoc = "";

      const guiSuKien = (ten: string, duLieu: unknown) => {
        if (daDong || res.writableEnded) return;
        res.write(`event: ${ten}\ndata: ${JSON.stringify(duLieu)}\n\n`);
      };

      const donDep = () => {
        if (daDong) return;
        daDong = true;
        clearInterval(nhipTim);
        kenhSuKien.off(`viec:${id}`, dayCapNhat);
        if (!res.writableEnded) res.end();
      };

      const dayCapNhat = () => {
        if (daDong) return;
        let t: ReturnType<typeof khoTroLy.trangThai> = null;
        try {
          t = khoTroLy.trangThai(id, uid);
        } catch {
          donDep();
          return;
        }
        if (!t) {
          guiSuKien("error", { jobId: String(id), error: "Không còn thấy việc này", code: "not_found" });
          donDep();
          return;
        }
        if (t.trangThai === "xong") {
          guiSuKien("done", { jobId: String(id), trangThai: "xong", ...dongGoiThanhCong(t) });
          donDep();
          return;
        }
        if (t.trangThai === "that_bai" || t.trangThai === "da_huy") {
          const { body } = dongGoiLoi(t);
          guiSuKien("error", { jobId: String(id), trangThai: t.trangThai, ...body });
          donDep();
          return;
        }
        const goi = JSON.stringify({ jobId: String(id), trangThai: t.trangThai, tienTrinh: t.tienTrinh });
        if (goi !== banChupTruoc) {
          banChupTruoc = goi;
          res.write(`event: progress\ndata: ${goi}\n\n`);
        }
      };

      const nhipTim = setInterval(() => {
        if (!daDong && !res.writableEnded) res.write(": keepalive\n\n");
      }, 15_000);
      nhipTim.unref?.();

      req.on("close", donDep);
      kenhSuKien.on(`viec:${id}`, dayCapNhat);
      dayCapNhat();
    } catch (err) {
      if (!res.headersSent) traLoi(res, err);
      else if (!res.writableEnded) res.end();
    }
  });

  app.get("/api/tro-ly/:id", (req, res) => {
    try {
      const id = Number(req.params.id);
      const uid = req.nguoiDung!.id;
      const t = Number.isInteger(id) && id > 0 ? khoTroLy.trangThai(id, uid) : null;
      if (!t) return res.status(404).json({ error: "Không thấy việc này (có thể đã quá hạn 30 phút). Hãy hỏi lại." });
      if (t.trangThai === "xong" || t.trangThai === "that_bai" || t.trangThai === "da_huy") {
        return giaoKetQuaTroLy(res, t);
      }
      res.status(202).json({ jobId: req.params.id, tienTrinh: t.tienTrinh });
    } catch (err) {
      traLoi(res, err);
    }
  });

  /** Hủy một việc trợ lý đang chờ hoặc đang chạy của chính người dùng. */
  app.delete("/api/tro-ly/:id", (req, res) => {
    try {
      const id = Number(req.params.id);
      const uid = req.nguoiDung!.id;
      if (!Number.isInteger(id) || id <= 0) {
        return res.status(400).json({ error: "Mã việc không hợp lệ" });
      }
      const daHuy = khoTroLy.huy(id, uid);
      if (!daHuy) {
        return res.status(404).json({ error: "Không thấy việc này" });
      }
      ghiNhatKy(uid, "huy_viec_tro_ly", `id=${id}`);
      kichHoatTroLy();
      res.json({ ok: true, jobId: String(id), cancelled: true, trangThai: "da_huy" });
    } catch (err) {
      traLoi(res, err);
    }
  });
}
