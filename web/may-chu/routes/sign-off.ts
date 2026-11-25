import type express from "express";
import { ghiNhatKy, khoWorm } from "../csdl";
import { traLoi } from "./dung-chung";

export function dangKySignOffRoutes(app: express.Express) {
  /**
   * Ký duyệt pháp lý bản nháp (Human-in-the-Loop Forensic Sign-off):
   * Ghi nhận kết quả thẩm định từng mệnh đề của bác sĩ vào sổ kiểm toán bất biến WORM
   * trên SQLite (`worm_signoff`) song song với `worm_signoff_log.jsonl`.
   */
  app.post("/api/sessions/:id/sign-off", (req, res) => {
    try {
      const sessionId = String(req.params.id || "").trim();
      if (!sessionId) return res.status(400).json({ error: "Thiếu mã phiên khám" });
      const { tongMenhDe = 0, soGiu = 0, soSua = 0, soBo = 0, tyLeCoNguon = 100, contentHash = "" } = req.body || {};

      const kq = khoWorm.ghiSignOff({
        sessionId,
        userId: req.nguoiDung?.id ?? null,
        tongMenhDe: Number(tongMenhDe),
        soGiu: Number(soGiu),
        soSua: Number(soSua),
        soBo: Number(soBo),
        tyLeCoNguon: Number(tyLeCoNguon),
        contentHash: String(contentHash),
      });

      ghiNhatKy(req.nguoiDung?.id ?? null, "ky_duyet_worm", `session=${sessionId} seq=${kq.wormSeq}`);
      res.json(kq);
    } catch (err) {
      traLoi(res, err);
    }
  });

  app.get("/api/sessions/:id/sign-off", (req, res) => {
    try {
      const sessionId = String(req.params.id || "").trim();
      if (!sessionId) return res.status(400).json({ error: "Thiếu mã phiên khám" });
      res.json({ entries: khoWorm.docLichSuSignOff(sessionId) });
    } catch (err) {
      traLoi(res, err);
    }
  });

  app.get("/api/worm/verify", (_req, res) => {
    try {
      res.json(khoWorm.xacMinhChuoi());
    } catch (err) {
      traLoi(res, err);
    }
  });
}
