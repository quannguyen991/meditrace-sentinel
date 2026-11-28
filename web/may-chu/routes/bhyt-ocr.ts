import type express from "express";
import { chanNeuChuaKy, layMaCaTuYeuCau } from "../kiem-ky-may-chu";
import { chayPythonJson, goiDichVu, traLoi } from "./dung-chung";

export function dangKyBhytOcrRoutes(app: express.Express) {
  /**
   * Bóc tách chỉ số XN & đơn thuốc cũ (Clinical OCR Parser 100% cục bộ + hiệu chỉnh liều KDIGO):
   * Gọi `src/cong_cu_lam_sang/doc_phieu_xet_nghiem.py` nối thẳng `src/cong_cu_lam_sang/hieu_chinh_lieu.py`.
   * Không bao giờ tự bịa `tuoi = 50` khi giao diện không gửi tuổi (`tuoi: req.body?.tuoi ?? null`).
   */
  app.post("/api/ocr/phieu-cu", async (req, res) => {
    try {
      const { text = "", laNu = false, canNangKg = null } = req.body || {};
      const tuoi = req.body?.tuoi ?? null;
      if (!String(text).trim()) {
        return res.status(400).json({ error: "Vui lòng nhập hoặc dán nội dung phiếu xét nghiệm / đơn thuốc cũ." });
      }
      const payload = { text: String(text), tuoi, laNu: Boolean(laNu), canNangKg };
      try {
        const kqHttp = await goiDichVu("/api/ocr/phieu-cu", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        return res.json(kqHttp);
      } catch (err: any) {
        // Chỉ chạy Python tại chỗ khi dịch vụ đang tắt; thiếu/sai khoá nội bộ thì báo lỗi rõ.
        if (err?.code !== "dich_vu_tat") throw err;
      }
      const kq = await chayPythonJson("src.cong_cu_lam_sang.doc_phieu_xet_nghiem", ["--parse"], payload);
      res.json(kq);
    } catch (err) {
      traLoi(res, err);
    }
  });

  /**
   * Tiền kiểm BHYT & Gợi ý mã ICD-10 4 ký tự + Liều Nhi khoa mg/kg (Quyết định 130/4750/QĐ-BYT):
   * Truyền đầy đủ `thong_tin_benh_nhan` (`can_nang_kg`, `tuoi`, ...) sang cả dịch vụ Python lẫn CLI fallback.
   */
  app.post("/api/bhyt/precheck", async (req, res) => {
    try {
      // Kết quả có gói XML1–XML5 để nộp BHYT = xuất hồ sơ: phải ký và chưa sửa sau ký (`sessionId` = mã ca).
      if (chanNeuChuaKy(req, res, layMaCaTuYeuCau(req, "sessionId", "caseId"))) return;
      const { propositions = [], transcript = "", thong_tin_benh_nhan = null, patientInfo = null } = req.body || {};
      const payload = {
        propositions,
        transcript,
        thong_tin_benh_nhan: thong_tin_benh_nhan || patientInfo || undefined,
      };
      try {
        const kqHttp = await goiDichVu("/api/bhyt/precheck", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        return res.json(kqHttp);
      } catch (err: any) {
        if (err?.code !== "dich_vu_tat") throw err;
      }
      const kq = await chayPythonJson("src.cong_cu_lam_sang.tien_kiem_bhyt_va_khoi_phuc_bo_sot", ["--precheck"], payload);
      res.json(kq);
    } catch (err) {
      traLoi(res, err);
    }
  });

  /**
   * Tái biên dịch gói XML 1–5 (QĐ 130/4750/QĐ-BYT) & HL7 FHIR R4 từ danh sách mệnh đề hiệu lực
   * sau khi bác sĩ duyệt (giữ/sửa/bỏ), không để lọt mệnh đề đã bị bác bỏ ra hồ sơ xuất bản.
   */
  app.post(["/api/bhyt/recompile", "/api/fhir/recompile"], async (req, res) => {
    try {
      // Gói XML 1–5 / FHIR xuất bản: phải ký và chưa sửa sau ký (`sessionId`, hoặc `caseId` = mã ca đã lưu).
      if (chanNeuChuaKy(req, res, layMaCaTuYeuCau(req, "sessionId", "caseId"))) return;
      const {
        caseId = "web",
        propositions = [],
        transcript = "",
        noteSections = null,
        thong_tin_benh_nhan = null,
        patientInfo = null,
        du_lieu_xet_nghiem = null,
      } = req.body || {};
      if (!Array.isArray(propositions)) {
        return res.status(400).json({ error: "propositions phải là mảng" });
      }
      const payload = {
        caseId: String(caseId || "web"),
        ma_ca: String(caseId || "web"),
        propositions,
        transcript: String(transcript || ""),
        ...(noteSections && typeof noteSections === "object" ? { noteSections, ban_nhap: noteSections } : {}),
        thong_tin_benh_nhan: thong_tin_benh_nhan || patientInfo || undefined,
        ...(du_lieu_xet_nghiem && typeof du_lieu_xet_nghiem === "object" ? { du_lieu_xet_nghiem } : {}),
      };
      try {
        const kqHttp = await goiDichVu("/api/bhyt/recompile", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        return res.json(kqHttp);
      } catch (err: any) {
        if (err?.status === 404 || err?.code === "khong_co_duong") {
          try {
            const kqPrecheck = await goiDichVu("/api/bhyt/precheck", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(payload),
            });
            return res.json(kqPrecheck);
          } catch (err2: any) {
            if (err2?.code !== "dich_vu_tat") throw err2;
          }
        } else if (err?.code !== "dich_vu_tat") {
          throw err;
        }
      }
      try {
        const kqRecompile = await chayPythonJson("src.cong_cu_lam_sang.tien_kiem_bhyt_va_khoi_phuc_bo_sot", ["--recompile"], payload);
        return res.json(kqRecompile);
      } catch {
        const kqFallback = await chayPythonJson("src.cong_cu_lam_sang.tien_kiem_bhyt_va_khoi_phuc_bo_sot", ["--precheck"], payload);
        return res.json(kqFallback);
      }
    } catch (err) {
      traLoi(res, err);
    }
  });
}
