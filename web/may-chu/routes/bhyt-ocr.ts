import type express from "express";
import { chayPythonJson, goiDichVu, traLoi } from "./dung-chung";

export function dangKyBhytOcrRoutes(app: express.Express) {
  /**
   * Bóc tách chỉ số XN & đơn thuốc cũ (Clinical OCR Parser 100% cục bộ + hiệu chỉnh liều KDIGO):
   * Gọi `src/ocr_lam_sang.py` nối thẳng `src/hieu_chinh_lieu.py`.
   */
  app.post("/api/ocr/phieu-cu", async (req, res) => {
    try {
      const { text = "", tuoi = 50, laNu = false, canNangKg = null } = req.body || {};
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
      const kq = await chayPythonJson("src.ocr_lam_sang", ["--parse"], payload);
      res.json(kq);
    } catch (err) {
      traLoi(res, err);
    }
  });

  /**
   * Tiền kiểm BHYT & Gợi ý mã ICD-10 4 ký tự (Quyết định 130/4750/QĐ-BYT):
   * Ưu tiên gọi dịch vụ Python persistent, fallback sang `chayPythonJson` nếu dịch vụ chưa bật.
   */
  app.post("/api/bhyt/precheck", async (req, res) => {
    try {
      const { propositions = [], transcript = "" } = req.body || {};
      const payload = { propositions, transcript };
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
      const kq = await chayPythonJson("src.kiem_duyet_bhyt_va_bo_sot", ["--precheck"], payload);
      res.json(kq);
    } catch (err) {
      traLoi(res, err);
    }
  });
}
