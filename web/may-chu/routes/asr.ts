import crypto from "crypto";
import type express from "express";
import type {
  ApiNoteResponse,
  ApiUiProposition,
  ApiUiWarning,
  PyGhiChu,
  PyNoteResponse,
  PyPhatBieu,
} from "../../src/types/api-contract";
import { db } from "../csdl";
import { taoHangDoi, type TrangThaiViecTra } from "../hang-doi";
import { goiDichVu, traLoi, TUOI_VIEC_TOI_DA_MS } from "./dung-chung";

const MUC_PHU = ["CẦN XÁC NHẬN", "CÂU HỎI LÀM RÕ"];
const CHO_TRUC_TIEP_MS = Number(process.env.MEDITRACE_CHO_NHAP_MS) || 20_000;
const CHU_KY_DON_VIEC_MS = 5 * 60_000;

export type MenhDeGiaoDienMoRong = ApiUiProposition & {
  chu_the_id: number | null;
  wormSeq?: number | null;
  wormHash?: string | null;
};

export type PhanHoiBanNhapMoRong = ApiNoteResponse & {
  wormSeq?: number | null;
  wormHash?: string | null;
};

/** Một cảnh báo -> dạng giao diện. Không gửi mã kỹ thuật lên làm tiêu đề. */
export function canhBaoGiaoDien(c: any): ApiUiWarning | null {
  if (!c) return null;
  return {
    code: c.ma,
    group: c.nhom,
    groupName: c.nhom_ten,
    title: c.tieu_de,
    explanation: c.giai_thich,
    reason: c.ly_do,
    turns: c.luot || [],
    quotes: c.trich || [],
    severity: c.muc_do,
    uncertainty: c.bat_dinh,
    kind: c.ket_luan,
    reliability: c.tin_cay,
    affectsState: !!c.anh_huong_trang_thai,
    tags: c.phu || [],
    tagTitles: c.phu_tieu_de || [],
    detector: c.bo_phat_hien,
  };
}

/** Mệnh đề để giao diện duyệt: mỗi dòng bản nháp kèm chủ thể (`chu_the_id`), lượt thoại căn cứ và `wormSeq`/`wormHash` nếu có. */
export function menhDeChoGiaoDien(r: PyNoteResponse | any): MenhDeGiaoDienMoRong[] {
  const cb = r?.canh_bao;
  const wormSeqCa = r?.worm_seq ?? r?.wormSeq;
  const wormHashCa = r?.worm_hash ?? r?.wormHash;
  const theoId = new Map<number, PyPhatBieu>((r?.phat_bieu || []).map((p: PyPhatBieu) => [p.id, p]));
  return (r?.ghi_chu || [])
    .filter((g: PyGhiChu) => g.id !== undefined && theoId.has(g.id!))
    .map((g: PyGhiChu) => {
      const p = theoId.get(g.id!)! as PyPhatBieu & { worm_seq?: number | null; worm_hash?: string | null };
      const lyDo = g.ly_do || null;
      let van = (g.van || "").trim();
      if (lyDo && van.endsWith(` — ${lyDo}`)) van = van.slice(0, -` — ${lyDo}`.length).trim();
      const thuoc = p.thuoc || null;
      const wormSeq = p.worm_seq !== undefined ? p.worm_seq : wormSeqCa;
      const wormHash = p.worm_hash !== undefined ? p.worm_hash : wormHashCa;
      return {
        id: p.id,
        text: van,
        section: g.muc || "",
        status: MUC_PHU.includes(g.muc || "") ? "can_xac_nhan" : "than",
        gateReason: lyDo,
        subject: p.ten_chu_the || (p.chu_the_id === 0 ? "bệnh nhân" : null),
        chu_the_id: typeof p.chu_the_id === "number" ? p.chu_the_id : null,
        negated: !!p.phu_dinh,
        certainty: p.do_chac_chan || null,
        situation: p.tinh_huong || null,
        time: p.moc_thoi_gian || null,
        drug: thuoc
          ? Object.entries(thuoc)
              .filter(([, v]) => v)
              .map(([k, v]) => `${k} ${v}`)
              .join(", ")
          : null,
        evidenceTurns: p.bang_chung || [],
        quotes: p.trich_dan || [],
        warning: canhBaoGiaoDien(cb?.theo_phat_bieu?.[String(p.id)]?.chinh),
        otherWarnings: (cb?.theo_phat_bieu?.[String(p.id)]?.khac || []).map(canhBaoGiaoDien),
        warningTags: cb?.theo_phat_bieu?.[String(p.id)]?.phu || [],
        stateD: cb?.trang_thai_D?.[String(p.id)]?.trang_thai || null,
        stateDReason: cb?.trang_thai_D?.[String(p.id)]?.ly_do || null,
        ...(wormSeq !== undefined && wormSeq !== null ? { wormSeq } : {}),
        ...(wormHash !== undefined && wormHash !== null ? { wormHash } : {}),
      };
    });
}

async function taoBanNhap({
  transcript,
  sessionId,
  sampleCaseId,
  branch,
  thong_tin_benh_nhan,
  du_lieu_xet_nghiem,
  user_id,
}: Record<string, any>): Promise<PhanHoiBanNhapMoRong> {
  const d = await goiDichVu("/api/ho-so", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      input: transcript,
      phien: sessionId,
      chay_truoc: sampleCaseId,
      nhanh: branch || "C_khoa_hoi",
      ...(thong_tin_benh_nhan ? { thong_tin_benh_nhan } : {}),
      ...(du_lieu_xet_nghiem ? { du_lieu_xet_nghiem } : {}),
      ...(user_id ? { user_id } : {}),
    }),
  });
  const wormSeq = d.worm_seq ?? d.wormSeq;
  const wormHash = d.worm_hash ?? d.wormHash;
  return {
    content: d.du_doan,
    contentWithoutExtras: d.du_doan_khong_muc_phu,
    propositions: menhDeChoGiaoDien(d),
    questions: (d.cau_hoi || []).map((c: any) => c.van),
    needsConfirmCount: d.so_can_xac_nhan ?? 0,
    caseId: d.id,
    branch: d.nhanh,
    policy: d.chinh_sach,
    source: d.nguon,
    seconds: d.giay_xu_ly,
    transcript: d.input,
    caseWarnings: (d.canh_bao?.toan_ca || []).filter((c: any) => c.ket_luan !== "can_xem").map(canhBaoGiaoDien),
    warningPolicy: d.canh_bao?.chinh_sach || null,
    warningVersion: d.canh_bao?.phien_ban || null,
    clinicalSafety: d.lam_sang_nang_cao || null,
    ...(wormSeq !== undefined && wormSeq !== null ? { wormSeq } : {}),
    ...(wormHash !== undefined && wormHash !== null ? { wormHash } : {}),
  };
}

export function dangKyAsrRoutes(app: express.Express) {
  const hangDoiViec = taoHangDoi(db);
  let dangChayNen = false;

  // Dọn nhẹ định kỳ các việc đã hoàn tất quá 30 phút (unref để không giữ tiến trình khi đóng server/test)
  const boDonDinhKy = setInterval(() => {
    try {
      if (db.isOpen) hangDoiViec.donViecCu(TUOI_VIEC_TOI_DA_MS);
    } catch {}
  }, CHU_KY_DON_VIEC_MS);
  boDonDinhKy.unref?.();

  async function chayViecNen() {
    if (dangChayNen) return;
    dangChayNen = true;
    try {
      for (let v = hangDoiViec.layViecTiepTheo(); v; v = hangDoiViec.layViecTiepTheo()) {
        try {
          hangDoiViec.xong(v.id, JSON.stringify(await taoBanNhap(JSON.parse(v.taiTrong))));
        } catch (err: any) {
          hangDoiViec.loi(
            v.id,
            JSON.stringify({ status: err?.status || 500, error: err?.message || "Lỗi không rõ", code: err?.code }),
          );
        }
      }
    } finally {
      dangChayNen = false;
    }
  }

  /**
   * Giao kết quả việc: KHÔNG xoá ngay lần đọc đầu tiên (tránh Read-Once Delete Race khi F5, rớt mạng,
   * hoặc 2 tab cùng `khoaTrung` cùng đọc `jobId`). Việc cũ > 30 phút được dọn bởi `donViecCu`.
   */
  function giaoKetQuaViec(res: express.Response, t: TrangThaiViecTra) {
    if (t.trangThai === "xong") return res.json(JSON.parse(t.ketQua || "null"));
    let loi: { status: number; error: string; code?: string };
    try {
      loi = JSON.parse(t.ma || "");
      if (!loi || typeof loi.error !== "string") throw new Error("không phải lỗi của việc");
    } catch {
      loi = {
        status: 500,
        error: "Máy chủ khởi động lại khi đang tạo bản nháp và đã thử lại quá số lần cho phép. Bấm tạo lại.",
        code: t.ma || undefined,
      };
    }
    return res.status(loi.status).json({ error: loi.error, code: loi.code });
  }

  app.post("/api/transcribe", async (req, res) => {
    try {
      const { audioBase64, fileName, diarize } = req.body || {};
      if (!audioBase64) return res.status(400).json({ error: "Thiếu dữ liệu âm thanh" });
      const d = await goiDichVu("/api/chep-am", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          am_thanh_base64: audioBase64,
          ten_tep: fileName || "ghi-am.webm",
          tach_nguoi_noi: diarize !== false,
        }),
      });
      const doan = d.doan || [];
      const transcript = doan.map((s: any) => `${s.speaker_id || "Người nói"}: ${s.text_original}`).join("\n");
      const transcriptSegments = doan.map((s: any, idx: number) => ({
        luot: idx + 1,
        start_s: typeof s.start_time === "number" ? s.start_time : typeof s.start_s === "number" ? s.start_s : 0,
        end_s: typeof s.end_time === "number" ? s.end_time : typeof s.end_s === "number" ? s.end_s : 0,
        lowConf: Boolean(s.asr_review_required || (typeof s.asr_confidence === "number" && s.asr_confidence < 0.75)),
      }));
      res.json({
        transcript,
        segments: doan,
        transcriptSegments,
        sessionId: d.phien,
        seconds: d.giay_xu_ly,
        source: d.nguon,
        diarization: d.tach_nguoi_noi || null,
        note: d.ghi_chu,
      });
    } catch (err) {
      traLoi(res, err);
    }
  });

  app.post("/api/assign-roles", async (req, res) => {
    try {
      const { sessionId, roles } = req.body || {};
      if (!sessionId || !roles) return res.status(400).json({ error: "Thiếu sessionId hoặc roles" });
      const d = await goiDichVu("/api/gan-vai", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ phien: sessionId, vai: roles }),
      });
      res.json({ sessionId: d.phien, segments: d.doan });
    } catch (err) {
      traLoi(res, err);
    }
  });

  app.post("/api/generate-note", async (req, res) => {
    try {
      const { transcript, sessionId, sampleCaseId, branch, patientInfo, thong_tin_benh_nhan, labResults, du_lieu_xet_nghiem } =
        req.body || {};
      if (!transcript && !sessionId && !sampleCaseId) {
        return res.status(400).json({ error: "Cần transcript, sessionId hoặc sampleCaseId" });
      }
      hangDoiViec.donViecCu(TUOI_VIEC_TOI_DA_MS);
      const uid = req.nguoiDung!.id;
      const tai = JSON.stringify({
        transcript,
        sessionId,
        sampleCaseId,
        branch,
        thong_tin_benh_nhan: thong_tin_benh_nhan || patientInfo || null,
        du_lieu_xet_nghiem: du_lieu_xet_nghiem || labResults || null,
        user_id: String(uid),
      });
      const id = hangDoiViec.them(uid, crypto.createHash("sha256").update(tai).digest("hex"), tai);
      void chayViecNen();
      const han = Date.now() + CHO_TRUC_TIEP_MS;
      for (;;) {
        const t = hangDoiViec.trangThai(id, uid);
        if (t && (t.trangThai === "xong" || t.trangThai === "that_bai")) return giaoKetQuaViec(res, t);
        if (Date.now() >= han) break;
        await new Promise((r) => setTimeout(r, 100));
      }
      const t = hangDoiViec.trangThai(id, uid);
      res.status(202).json({ jobId: String(id), queued: hangDoiViec.soViecTruoc(id), startedAt: t?.taoLuc ?? Date.now() });
    } catch (err) {
      traLoi(res, err);
    }
  });

  app.get("/api/generate-note/:ma", (req, res) => {
    try {
      const id = Number(req.params.ma);
      const uid = req.nguoiDung!.id;
      const t = Number.isInteger(id) ? hangDoiViec.trangThai(id, uid) : null;
      if (!t) {
        return res.status(404).json({ error: "Không thấy việc tạo bản nháp này (có thể đã quá hạn 30 phút). Bấm tạo lại." });
      }
      if (t.trangThai === "xong" || t.trangThai === "that_bai") return giaoKetQuaViec(res, t);
      return res.status(202).json({ jobId: req.params.ma, queued: hangDoiViec.soViecTruoc(id), startedAt: t.taoLuc });
    } catch (err) {
      traLoi(res, err);
    }
  });

  app.post("/api/error-attribution", async (req, res) => {
    try {
      const { action, originalProposition, updatedProposition } = req.body || {};
      const d = await goiDichVu("/api/quy-ket-loi", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          thao_tac: action,
          menh_de_goc: originalProposition,
          menh_de_sua: updatedProposition,
        }),
      });
      res.json(d);
    } catch (err) {
      traLoi(res, err);
    }
  });

  return function khoiDongHangDoiBanNhap() {
    const kp = hangDoiViec.khoiPhucSauKhoiDong();
    if (kp.chayLai || kp.thatBai) {
      console.log(`Hàng đợi: chạy lại ${kp.chayLai} việc dở dang, ${kp.thatBai} việc quá số lần thử.`);
    }
    void chayViecNen();
  };
}
