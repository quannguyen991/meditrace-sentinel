import type express from "express";
import { docKho, ghiKho, ghiMotCaKham, laTenKho, xoaMotCaKham } from "../csdl";
import { goiDichVu, traLoi } from "./dung-chung";

export function dangKyCaKhamRoutes(app: express.Express) {
  // /api/ca-kham giữ lại tương thích ngược 100% cho giao diện hiện có; /api/kho/<tên> dùng cho các kho khác.
  app.get(["/api/ca-kham", "/api/kho/:ten"], (req, res) => {
    const ten = req.params.ten || "ca-kham";
    if (!laTenKho(ten)) return res.status(404).json({ error: `Không có kho ${ten}` });
    try {
      res.set("Cache-Control", "no-store").json(docKho(req.nguoiDung!.id, ten));
    } catch (err: any) {
      res.status(500).json({ error: `Không đọc được kho ${ten}: ${err?.message || err}` });
    }
  });

  app.put(["/api/ca-kham", "/api/kho/:ten"], (req, res) => {
    const ten = req.params.ten || "ca-kham";
    if (!laTenKho(ten)) return res.status(404).json({ error: `Không có kho ${ten}` });
    const { sessions, savedAt } = req.body || {};
    if (!Array.isArray(sessions)) return res.status(400).json({ error: "Thiếu danh sách" });
    try {
      ghiKho(req.nguoiDung!.id, ten, sessions, savedAt);
      res.json({ ok: true, count: sessions.length });
    } catch (err: any) {
      res.status(err?.ma || 500).json({ error: `Không ghi được kho ${ten}: ${err?.message || err}` });
    }
  });

  // Đồng bộ hạt mịn từng ca khám kèm kiểm tra khóa lạc quan `expectedUpdatedAt` tùy chọn (-> 409 nếu cũ hơn)
  app.put("/api/ca-kham/:id", (req, res) => {
    try {
      const id = String(req.params.id || "").trim();
      if (!id) return res.status(400).json({ error: "Thiếu mã ca khám" });
      const body = req.body && typeof req.body === "object" && !Array.isArray(req.body) ? req.body : null;
      if (!body) return res.status(400).json({ error: "Thiếu dữ liệu ca khám" });

      const expectedUpdatedAt = body.expectedUpdatedAt;
      const savedAt = body.savedAt;
      let ca: Record<string, unknown>;
      if (body.session && typeof body.session === "object" && !Array.isArray(body.session)) {
        ca = body.session as Record<string, unknown>;
      } else {
        const { expectedUpdatedAt: _e, savedAt: _s, ...phanConLai } = body;
        ca = phanConLai;
      }

      const kq = ghiMotCaKham(req.nguoiDung!.id, id, ca, { expectedUpdatedAt, savedAt });
      res.json(kq);
    } catch (err: any) {
      const status = err?.status || err?.ma || 500;
      res.status(status).json({
        error: err?.message || String(err),
        ...(err?.code ? { code: err.code } : {}),
        ...(typeof err?.currentUpdatedAt === "number" ? { currentUpdatedAt: err.currentUpdatedAt } : {}),
      });
    }
  });

  app.delete("/api/ca-kham/:id", (req, res) => {
    try {
      const id = String(req.params.id || "").trim();
      if (!id) return res.status(400).json({ error: "Thiếu mã ca khám" });
      res.json(xoaMotCaKham(req.nguoiDung!.id, id));
    } catch (err: any) {
      res.status(err?.status || err?.ma || 500).json({ error: err?.message || String(err) });
    }
  });

  app.get("/api/health", async (_req, res) => {
    try {
      res.json(await goiDichVu("/api/suc-khoe"));
    } catch (err) {
      traLoi(res, err);
    }
  });

  app.get("/api/sample-cases", async (req, res) => {
    try {
      const bo = req.query.bo ? `?bo=${encodeURIComponent(String(req.query.bo))}` : "";
      res.json(await goiDichVu(`/api/ca-mau${bo}`));
    } catch (err) {
      traLoi(res, err);
    }
  });
}
