import type express from "express";
import { docKho, ghiKho, laTenKho } from "../csdl";
import { goiDichVu, traLoi } from "./dung-chung";

export function dangKyCaKhamRoutes(app: express.Express) {
  // /api/ca-kham giữ lại cho giao diện hiện có; /api/kho/<tên> dùng cho các kho khác.
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
