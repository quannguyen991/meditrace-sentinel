import crypto from "crypto";
import type express from "express";
import { cheLog } from "../che-log";
import { caKhamThuocNguoiKhac, ghiNhatKy, khoWorm } from "../csdl";
import {
  chanNeuTruongLech,
  goiCamDoanTuBanKy,
  goiDiBuongTuBanKy,
  hopNhatMaCa,
  layBanKyDeXuat,
  layBanKyTheoMa,
} from "../kiem-ky-may-chu";
import { chayPythonJson, goiDichVu, traLoi } from "./dung-chung";

const TOI_DA_CSV_DUOC_THU_BYTES = 500 * 1024; // 500 KB

export function dangKyBoostLamSangRoutes(app: express.Express) {
  /**
   * Boost 8 — Kiểm định Cam đoan Thủ thuật xâm lấn (Informed Consent Checklist & WORM Stamping):
   * Ưu tiên gọi dịch vụ Python `/api/cam-doan-thu-thuat`, fallback sang `src.cong_cu_lam_sang.cam_doan_thu_thuat --check`
   * khi dịch vụ tại chỗ đang tắt (`dich_vu_tat`). Hỗ trợ đóng dấu băm SHA-256 `consentHash` và ghi nhật ký.
   */
  app.post("/api/clinical/informed-consent", async (req, res) => {
    try {
      const uid = req.nguoiDung?.id;
      if (typeof uid !== "number") return res.status(401).json({ error: "Chưa đăng nhập" });

      const body = req.body && typeof req.body === "object" ? (req.body as Record<string, unknown>) : {};
      // Chỉ tên thủ thuật / ghi chú bác sĩ / cờ đóng dấu là của riêng phiếu cam đoan và được lấy từ trình duyệt;
      // dữ liệu hồ sơ (mệnh đề, lời thoại, thông tin BN, mốc âm thanh) lấy từ bản đã ký.
      const procedureName = typeof body.procedureName === "string" ? body.procedureName : null;
      const stampWorm = body.stampWorm === true;

      const cleanSessionId = typeof body.sessionId === "string" ? body.sessionId.trim() : "";
      if (cleanSessionId.length > 200) {
        return res.status(400).json({ error: "sessionId vượt quá 200 ký tự" });
      }
      const rawCaseId = typeof body.caseId === "string" ? body.caseId.trim().slice(0, 200) : "";
      const maCa = cleanSessionId || rawCaseId;
      if (maCa && caKhamThuocNguoiKhac(uid, maCa)) {
        return res.status(403).json({
          error: "Không được đóng dấu cam đoan thủ thuật cho ca khám của bác sĩ khác",
          code: "idor_forbidden",
        });
      }
      const banKy = layBanKyDeXuat(req, res);
      if (!banKy) return;
      const goi = goiCamDoanTuBanKy(banKy);
      if (
        chanNeuTruongLech(res, body, [
          ["propositions", goi.propositions],
          ["transcript", goi.transcript],
          ["thong_tin_benh_nhan", goi.thong_tin_benh_nhan],
          ["patientInfo", goi.thong_tin_benh_nhan],
          ["audioMetadata", goi.audioMetadata],
        ])
      ) {
        return;
      }

      const propositions = goi.propositions;
      const transcriptStr = goi.transcript;
      const payload = {
        transcript: transcriptStr,
        hoi_thoai: transcriptStr,
        propositions,
        phat_bieu: propositions,
        audioMetadata: goi.audioMetadata,
        metadata_am_thanh: goi.audioMetadata,
        metadata: goi.audioMetadata,
        procedureName,
        ten_thu_thuat: procedureName,
      };

      let kq: any;
      try {
        kq = await goiDichVu("/api/cam-doan-thu-thuat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
      } catch (err: any) {
        if (err?.code !== "dich_vu_tat") throw err;
        kq = await chayPythonJson("src.cong_cu_lam_sang.cam_doan_thu_thuat", ["--check"], payload);
      }

      if (stampWorm && banKy.sessionId) {
        const cleanSessionId = banKy.sessionId;
        const checkedAt = new Date().toISOString();
        const consentHash = crypto
          .createHash("sha256")
          .update(
            JSON.stringify({
              sessionId: cleanSessionId,
              transcript: transcriptStr,
              propositions,
              checkedAt,
            }),
          )
          .digest("hex");

        const wormRes = khoWorm.ghiSignOff({
          sessionId: cleanSessionId,
          userId: uid,
          tongMenhDe: Math.max(1, propositions.length),
          soGiu: Math.max(1, propositions.length),
          soSua: 0,
          soBo: 0,
          tyLeCoNguon: 100,
          contentHash: consentHash,
          soChuaXacNhan: 0,
        });

        ghiNhatKy(
          uid,
          "cam_doan_thu_thuat_worm",
          `session=${cleanSessionId} procedure=${cheLog(String(procedureName || "-"), 120)} seq=${wormRes.wormSeq} hash=${consentHash}`,
        );

        return res.json({
          ...(kq && typeof kq === "object" && !Array.isArray(kq) ? kq : { result: kq }),
          consentHash,
          checkedAt,
          sessionId: cleanSessionId,
          wormSeq: wormRes.wormSeq,
          wormHash: wormRes.hash,
        });
      }

      res.json(kq);
    } catch (err) {
      traLoi(res, err);
    }
  });

  /**
   * Boost 10 — Đi buồng Nội trú & So sánh Diễn biến Tờ điều trị (Inpatient Ward-Round Diff):
   * Ưu tiên gọi `/api/noi-tru/to-dieu-tri`, fallback sang `src.cong_cu_lam_sang.di_buong_noi_tru --diff` khi dịch vụ tắt.
   */
  app.post("/api/inpatient/ward-round-diff", async (req, res) => {
    try {
      const uid = req.nguoiDung?.id;
      if (typeof uid !== "number") return res.status(401).json({ error: "Chưa đăng nhập" });
      const body = req.body && typeof req.body === "object" ? (req.body as Record<string, unknown>) : {};
      const q = (req.query || {}) as Record<string, unknown>;
      // Ca hôm nay: sessionId / caseId / currentSessionId phải chỉ cùng MỘT ca, nếu lệch -> 422 lech_ma_ca.
      const maHomNay = hopNhatMaCa(res, [body.sessionId, body.caseId, body.currentSessionId, q.sessionId, q.caseId]);
      if (maHomNay === null) return;
      const banHomNay = layBanKyTheoMa(req, res, maHomNay);
      if (!banHomNay) return;
      // Ca hôm qua (nếu có) cũng phải do chính bác sĩ này ký và chưa đổi sau ký.
      const maHomQua = hopNhatMaCa(res, [body.previousSessionId, body.yesterdaySessionId]);
      if (maHomQua === null) return;
      const banHomQua = maHomQua ? layBanKyTheoMa(req, res, maHomQua) : null;
      if (maHomQua && !banHomQua) return;

      // Dữ liệu hồ sơ lấy từ hai bản đã ký; trình duyệt gửi kèm thì phải trùng khít.
      const homNay = goiDiBuongTuBanKy(banHomNay);
      const homQua = banHomQua ? goiDiBuongTuBanKy(banHomQua).propositions : [];
      const thanKhongRong: Record<string, unknown> = { ...body };
      if (!banHomQua && Array.isArray(body.yesterdayPropositions) && body.yesterdayPropositions.length === 0) {
        delete thanKhongRong.yesterdayPropositions; // [] khi không có ca trước là hợp lệ
      }
      if (
        chanNeuTruongLech(res, thanKhongRong, [
          ["todayPropositions", homNay.propositions],
          ["yesterdayPropositions", homQua],
          ["todayTranscript", homNay.transcript],
          ["transcriptToday", homNay.transcript],
        ])
      ) {
        return;
      }

      const { dayNumber = null, treatmentDay = null } = body as { dayNumber?: unknown; treatmentDay?: unknown };
      const rawDay = dayNumber ?? treatmentDay ?? null;
      if (rawDay !== null && rawDay !== undefined && (typeof rawDay !== "number" || !Number.isFinite(rawDay) || rawDay < 1)) {
        return res.status(400).json({ error: "dayNumber phải là số dương hợp lệ hoặc null" });
      }

      const todayPropositions = homNay.propositions;
      const yesterdayPropositions = homQua;
      const transcriptStr = homNay.transcript;
      const payload = {
        todayPropositions,
        phat_bieu_hom_nay: todayPropositions,
        yesterdayPropositions,
        phat_bieu_hom_qua: yesterdayPropositions,
        todayTranscript: transcriptStr,
        transcriptToday: transcriptStr,
        hoi_thoai_hom_nay: transcriptStr,
        dayNumber: rawDay,
        treatmentDay: rawDay,
        ngay_dieu_tri_thu: rawDay,
      };

      let kq: any;
      try {
        kq = await goiDichVu("/api/noi-tru/to-dieu-tri", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
      } catch (err: any) {
        if (err?.code !== "dich_vu_tat") throw err;
        kq = await chayPythonJson("src.cong_cu_lam_sang.di_buong_noi_tru", ["--diff"], payload);
      }

      res.json(kq);
    } catch (err) {
      traLoi(res, err);
    }
  });

  /**
   * Boost 12 — Nạp Danh mục Dược thư Bệnh viện từ CSV (tối đa 500 KB):
   * Yêu cầu bác sĩ hoặc quản trị đã xác thực, gọi `/api/duoc-thu/nap-csv` và ghi nhận kiểm toán `ghiNhatKy`.
   */
  app.post("/api/formulary/upload-csv", async (req, res) => {
    try {
      const uid = req.nguoiDung?.id;
      if (typeof uid !== "number") return res.status(401).json({ error: "Chưa đăng nhập" });

      const rawCsv =
        req.body?.csvContent ??
        req.body?.csv_content ??
        req.body?.csv ??
        req.body?.csv_text ??
        req.body?.csvText ??
        req.body?.text;
      if (typeof rawCsv !== "string" || !rawCsv.trim()) {
        return res.status(400).json({ error: "Vui lòng cung cấp nội dung CSV danh mục thuốc (csvContent)." });
      }

      const byteLen = Buffer.byteLength(rawCsv, "utf8");
      if (byteLen > TOI_DA_CSV_DUOC_THU_BYTES) {
        return res.status(413).json({
          error: "Nội dung CSV danh mục thuốc vượt quá giới hạn 500KB cho phép.",
          code: "csv_too_large",
        });
      }

      const kqHttp = await goiDichVu("/api/duoc-thu/nap-csv", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ noi_dung_csv: rawCsv, csvContent: rawCsv }),
      });

      ghiNhatKy(uid, "nap_duoc_thu_csv", `bytes=${byteLen} vai=${req.nguoiDung?.vai || "bac_si"}`);
      res.json(kqHttp);
    } catch (err) {
      traLoi(res, err);
    }
  });

  /**
   * M4 — Tái kiểm tra lâm sàng vòng lặp kín (<50ms deterministic re-verification):
   * Chạy lại bộ kiểm duyệt an toàn DDI/dị ứng/thang điểm nguy cơ khi bác sĩ bổ sung mệnh đề (F2/SOCRATES/CLS).
   */
  app.post("/api/lam-sang/tai-kiem-tra", async (req, res) => {
    try {
      const uid = req.nguoiDung?.id;
      if (typeof uid !== "number") return res.status(401).json({ error: "Chưa đăng nhập" });

      const body = req.body && typeof req.body === "object" ? req.body : {};
      const propositions = body.propositions;
      if (!Array.isArray(propositions)) {
        return res.status(400).json({ error: "propositions phải là mảng" });
      }

      const payload = {
        propositions,
        transcript: String(body.transcript ?? ""),
        thong_tin_benh_nhan: body.thong_tin_benh_nhan ?? body.patientInfo ?? null,
        du_lieu_xet_nghiem: body.du_lieu_xet_nghiem ?? body.labResults ?? null,
        lich_su_lan_kham: body.lich_su_lan_kham ?? body.visitHistory ?? null,
      };

      let kq: any;
      try {
        kq = await goiDichVu("/api/lam-sang/tai-kiem-tra", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
      } catch (err: any) {
        if (err?.code !== "dich_vu_tat" && err?.status !== 404 && err?.code !== "khong_co_duong") throw err;
        kq = await chayPythonJson("src.he_thong.dieu_phoi_cac_chot_an_toan", ["--tai-kiem-tra"], payload);
      }

      res.json(kq);
    } catch (err) {
      traLoi(res, err);
    }
  });

  /**
   * M4 — Phân tích thông điệp HL7 v2 ORU^R01 / LIS (Lab Information System):
   * Chuyển kết quả xét nghiệm chuẩn HL7 sang chỉ số lâm sàng + cảnh báo giá trị nguy kịch (Panic Values).
   */
  app.post("/api/lis/parse", async (req, res) => {
    try {
      const uid = req.nguoiDung?.id;
      if (typeof uid !== "number") return res.status(401).json({ error: "Chưa đăng nhập" });

      const text = String(req.body?.text ?? "");
      if (!text.trim()) {
        return res.status(400).json({ error: "Vui lòng cung cấp nội dung thông điệp HL7 ORU^R01 (text)." });
      }

      const payload = { text };
      let kq: any;
      try {
        kq = await goiDichVu("/api/lis/parse", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
      } catch (err: any) {
        if (err?.code !== "dich_vu_tat" && err?.status !== 404 && err?.code !== "khong_co_duong") throw err;
        kq = await chayPythonJson("src.cong_cu_lam_sang.nap_ket_qua_lis_hl7", ["--parse"], payload);
      }

      res.json(kq);
    } catch (err) {
      traLoi(res, err);
    }
  });
}
