import type express from "express";
import { docKho, ghiKho, ghiMotCaKham, laTenKho, xoaMotCaKham } from "../csdl";
import { goiDichVu, traLoi } from "./dung-chung";
import { cheLog } from "../che-log";

export function dangKyCaKhamRoutes(app: express.Express) {
  // /api/ca-kham giữ lại tương thích ngược 100% cho giao diện hiện có; /api/kho/<tên> dùng cho các kho khác.
  app.get(["/api/ca-kham", "/api/kho/:ten"], (req, res) => {
    const uid = req.nguoiDung?.id;
    if (typeof uid !== "number") return res.status(401).json({ error: "Chưa đăng nhập" });
    const ten = req.params.ten || "ca-kham";
    if (!laTenKho(ten)) return res.status(404).json({ error: `Không có kho ${ten}` });
    try {
      res.set("Cache-Control", "no-store").json(docKho(uid, ten));
    } catch (err: any) {
      console.error(`[kho ${ten}] đọc lỗi:`, cheLog(err, 1500));
      res.status(500).json({ error: `Không đọc được kho ${ten}` });
    }
  });

  // Ghi cả danh sách: chỉ xoá ca trong `deletedIds`; có `baseUpdatedAt` thì ca nào đã mới hơn -> 409.
  app.put(["/api/ca-kham", "/api/kho/:ten"], (req, res) => {
    const uid = req.nguoiDung?.id;
    if (typeof uid !== "number") return res.status(401).json({ error: "Chưa đăng nhập" });
    const ten = req.params.ten || "ca-kham";
    if (!laTenKho(ten)) return res.status(404).json({ error: `Không có kho ${ten}` });
    const { sessions, items, savedAt, baseUpdatedAt, deletedIds } = req.body || {};
    const danhSach = Array.isArray(sessions) ? sessions : ten !== "ca-kham" && Array.isArray(items) ? items : null;
    if (!danhSach) return res.status(400).json({ error: "Thiếu danh sách" });
    if (deletedIds !== undefined && !Array.isArray(deletedIds)) return res.status(400).json({ error: "deletedIds phải là mảng" });
    try {
      const kq = ghiKho(uid, ten, danhSach, savedAt, { baseUpdatedAt, deletedIds });
      res.json({ ok: true, count: danhSach.length, ...kq });
    } catch (err: any) {
      const status = Number(err?.status || err?.ma) || 500;
      if (status >= 500) console.error(`[kho ${ten}] ghi lỗi:`, cheLog(err, 1500));
      res.status(status).json({
        error: status >= 500 ? `Không ghi được kho ${ten}` : `Không ghi được kho ${ten}: ${err?.message || err}`,
        ...(err?.code ? { code: err.code } : {}),
        ...(Array.isArray(err?.conflicts) ? { conflicts: err.conflicts } : {}),
        ...(err?.updatedAt ? { updatedAt: err.updatedAt } : {}),
      });
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
      const status = Number(err?.status || err?.ma) || 500;
      if (status >= 500) return traLoi(res, err);
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
      traLoi(res, { ...err, message: err?.message, status: err?.status || err?.ma });
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
