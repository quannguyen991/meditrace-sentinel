import type express from "express";
import { caKhamThuocNguoiKhac, ghiNhatKy, khoWorm } from "../csdl";
import { traLoi } from "./dung-chung";

export function dangKySignOffRoutes(app: express.Express) {
  /**
   * Ký duyệt pháp lý bản nháp (Human-in-the-Loop Forensic Sign-off):
   * Chặn IDOR theo chủ sở hữu ca khám và kiểm định chặt số nguyên / tổng mệnh đề / tỷ lệ nguồn / contentHash.
   */
  app.post("/api/sessions/:id/sign-off", (req, res) => {
    try {
      const sessionId = String(req.params.id || "").trim();
      if (!sessionId) return res.status(400).json({ error: "Thiếu mã phiên khám" });

      const uid = req.nguoiDung?.id ?? null;
      if (uid !== null && caKhamThuocNguoiKhac(uid, sessionId)) {
        return res.status(403).json({ error: "Không được ký duyệt ca khám của bác sĩ khác", code: "idor_forbidden" });
      }

      const body = req.body && typeof req.body === "object" ? req.body : {};
      const {
        tongMenhDe,
        soGiu = 0,
        soSua = 0,
        soBo = 0,
        tyLeCoNguon = 100,
        contentHash,
        soChuaXacNhan,
      } = body;

      const kq = khoWorm.ghiSignOff({
        sessionId,
        userId: uid,
        tongMenhDe,
        soGiu,
        soSua,
        soBo,
        tyLeCoNguon,
        contentHash,
        ...(soChuaXacNhan !== undefined ? { soChuaXacNhan } : {}),
      });

      ghiNhatKy(uid, "ky_duyet_worm", `session=${sessionId} seq=${kq.wormSeq}`);
      res.json(kq);
    } catch (err) {
      traLoi(res, err);
    }
  });

  app.get("/api/sessions/:id/sign-off", (req, res) => {
    try {
      const sessionId = String(req.params.id || "").trim();
      if (!sessionId) return res.status(400).json({ error: "Thiếu mã phiên khám" });

      const uid = req.nguoiDung?.id ?? null;
      const laQuanTri = req.nguoiDung?.vai === "quan_tri";
      if (!laQuanTri && uid !== null && caKhamThuocNguoiKhac(uid, sessionId)) {
        return res.status(403).json({ error: "Không có quyền xem lịch sử ký duyệt của bác sĩ khác", code: "idor_forbidden" });
      }

      const entries = laQuanTri || uid === null
        ? khoWorm.docLichSuSignOff(sessionId)
        : khoWorm.docLichSuSignOff(sessionId, { userId: uid });
      res.json({ entries });
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
