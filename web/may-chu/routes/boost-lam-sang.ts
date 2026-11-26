import crypto from "crypto";
import type express from "express";
import { caKhamThuocNguoiKhac, ghiNhatKy } from "../csdl";
import { chayPythonJson, goiDichVu, traLoi } from "./dung-chung";

const TOI_DA_CSV_DUOC_THU_BYTES = 500 * 1024; // 500 KB

export function dangKyBoostLamSangRoutes(app: express.Express) {
  /**
   * Boost 8 — Kiểm định Cam đoan Thủ thuật xâm lấn (Informed Consent Checklist & WORM Stamping):
   * Ưu tiên gọi dịch vụ Python `/api/cam-doan-thu-thuat`, fallback sang `src.cam_doan_thu_thuat --check`
   * khi dịch vụ tại chỗ đang tắt (`dich_vu_tat`). Hỗ trợ đóng dấu băm SHA-256 `consentHash` và ghi nhật ký.
   */
  app.post("/api/clinical/informed-consent", async (req, res) => {
    try {
      const uid = req.nguoiDung?.id;
      if (typeof uid !== "number") return res.status(401).json({ error: "Chưa đăng nhập" });

      const {
        transcript = "",
        propositions = [],
        audioMetadata = null,
        procedureName = null,
        stampWorm = false,
        sessionId = null,
      } = req.body || {};

      if (!Array.isArray(propositions)) {
        return res.status(400).json({ error: "propositions phải là mảng" });
      }

      const cleanSessionId = typeof sessionId === "string" ? sessionId.trim() : "";
      if (cleanSessionId.length > 200) {
        return res.status(400).json({ error: "sessionId vượt quá 200 ký tự" });
      }
      if (stampWorm === true && cleanSessionId && caKhamThuocNguoiKhac(uid, cleanSessionId)) {
        return res.status(403).json({
          error: "Không được đóng dấu cam đoan thủ thuật cho ca khám của bác sĩ khác",
          code: "idor_forbidden",
        });
      }

      const transcriptStr = String(transcript ?? "");
      const payload = {
        transcript: transcriptStr,
        hoi_thoai: transcriptStr,
        propositions,
        phat_bieu: propositions,
        audioMetadata: audioMetadata ?? null,
        metadata_am_thanh: audioMetadata ?? null,
        metadata: audioMetadata ?? null,
        procedureName: procedureName ?? null,
        ten_thu_thuat: procedureName ?? null,
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
        kq = await chayPythonJson("src.cam_doan_thu_thuat", ["--check"], payload);
      }

      if (stampWorm === true && cleanSessionId) {
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

        ghiNhatKy(
          uid,
          "cam_doan_thu_thuat_worm",
          `session=${cleanSessionId} procedure=${String(procedureName || "-").slice(0, 120)} hash=${consentHash}`,
        );

        return res.json({
          ...(kq && typeof kq === "object" && !Array.isArray(kq) ? kq : { result: kq }),
          consentHash,
          checkedAt,
          sessionId: cleanSessionId,
        });
      }

      res.json(kq);
    } catch (err) {
      traLoi(res, err);
    }
  });

  /**
   * Boost 10 — Đi buồng Nội trú & So sánh Diễn biến Tờ điều trị (Inpatient Ward-Round Diff):
   * Ưu tiên gọi `/api/noi-tru/to-dieu-tri`, fallback sang `src.di_buong_noi_tru --diff` khi dịch vụ tắt.
   */
  app.post("/api/inpatient/ward-round-diff", async (req, res) => {
    try {
      const uid = req.nguoiDung?.id;
      if (typeof uid !== "number") return res.status(401).json({ error: "Chưa đăng nhập" });

      const {
        todayPropositions = [],
        yesterdayPropositions = [],
        todayTranscript = "",
        transcriptToday = "",
        dayNumber = null,
        treatmentDay = null,
      } = req.body || {};

      if (!Array.isArray(todayPropositions) || !Array.isArray(yesterdayPropositions)) {
        return res.status(400).json({ error: "todayPropositions và yesterdayPropositions phải là mảng" });
      }
      const rawDay = dayNumber ?? treatmentDay ?? null;
      if (rawDay !== null && rawDay !== undefined && (typeof rawDay !== "number" || !Number.isFinite(rawDay) || rawDay < 1)) {
        return res.status(400).json({ error: "dayNumber phải là số dương hợp lệ hoặc null" });
      }

      const transcriptStr = String(todayTranscript || transcriptToday || "");
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
        kq = await chayPythonJson("src.di_buong_noi_tru", ["--diff"], payload);
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

      const rawCsv = req.body?.csvContent ?? req.body?.csv_content;
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
        body: JSON.stringify({ csvContent: rawCsv, csv_content: rawCsv }),
      });

      ghiNhatKy(uid, "nap_duoc_thu_csv", `bytes=${byteLen} vai=${req.nguoiDung?.vai || "bac_si"}`);
      res.json(kqHttp);
    } catch (err) {
      traLoi(res, err);
    }
  });
}
