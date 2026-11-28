import type express from "express";
import { tinhKyDuyetTuCa } from "../../src/lib/kyDuyet";
import { caKhamThuocNguoiKhac, docMotCaKham, ghiNhatKy, khoWorm } from "../csdl";
import { ghiBanKyDuyet } from "../kiem-ky-may-chu";
import { traLoi } from "./dung-chung";

export function dangKySignOffRoutes(app: express.Express) {
  /**
   * Ký duyệt pháp lý bản nháp (Human-in-the-Loop Forensic Sign-off).
   * Máy chủ KHÔNG tin số liệu của trình duyệt: ca phải tồn tại và thuộc đúng bác sĩ đăng nhập; tổng mệnh đề,
   * số giữ/sửa/bỏ, tỷ lệ có nguồn, số mục cần xác nhận chưa xử lý và băm nội dung đều tính từ `ca_kham.du_lieu`.
   * Trình duyệt chỉ được gửi `tabId` (tab bệnh án muốn ký) và tuỳ chọn `contentHash` để đối chiếu.
   */
  app.post("/api/sessions/:id/sign-off", (req, res) => {
    try {
      const sessionId = String(req.params.id || "").trim();
      if (!sessionId) return res.status(400).json({ error: "Thiếu mã phiên khám" });

      const uid = req.nguoiDung?.id;
      if (typeof uid !== "number") return res.status(401).json({ error: "Chưa đăng nhập" });

      const ca = docMotCaKham(uid, sessionId);
      if (!ca) {
        if (caKhamThuocNguoiKhac(uid, sessionId)) {
          return res.status(403).json({ error: "Không được ký duyệt ca khám của bác sĩ khác", code: "idor_forbidden" });
        }
        return res.status(404).json({
          error: "Không tìm thấy ca khám này trên máy chủ. Hãy chờ ca được lưu rồi ký lại.",
          code: "khong_tim_thay_ca",
        });
      }

      const body = req.body && typeof req.body === "object" ? req.body : {};
      const tabId = typeof body.tabId === "string" ? body.tabId.slice(0, 200) : null;
      const kq = tinhKyDuyetTuCa(ca.duLieu, tabId);
      if (!kq.kiemTra.duDieuKien) {
        return res.status(400).json({
          error: kq.kiemTra.thongDiep || "Hồ sơ chưa đủ điều kiện ký duyệt",
          code: kq.kiemTra.maLoi,
          soChuaXacNhan: kq.soChuaXacNhan,
          chuaXacNhanIds: kq.kiemTra.chuaXacNhanIds,
        });
      }
      if (typeof body.contentHash === "string" && body.contentHash.trim() && body.contentHash.trim() !== kq.contentHash) {
        return res.status(409).json({
          error:
            "Nội dung bệnh án hoặc quyết định duyệt trên máy chủ khác với màn hình đang ký (chưa đồng bộ xong). Chờ lưu rồi ký lại.",
          code: "lech_noi_dung",
        });
      }

      const ketQua = khoWorm.ghiSignOff({
        sessionId,
        userId: uid,
        tongMenhDe: kq.tongMenhDe,
        soGiu: kq.soGiu,
        soSua: kq.soSua,
        soBo: kq.soBo,
        tyLeCoNguon: kq.tyLeCoNguon,
        contentHash: kq.contentHash,
        soChuaXacNhan: kq.soChuaXacNhan,
      });

      // Bản chụp do MÁY CHỦ ghi: đúng tab đã ký + dữ liệu ca lúc ký. Chốt xuất chỉ tin bản này,
      // không tin `signOff.tabId` trình duyệt lưu trong ca.
      ghiBanKyDuyet({
        uid,
        sessionId,
        wormSeq: ketQua.wormSeq,
        tabId: kq.tabId,
        contentHash: kq.contentHash,
        duLieu: ca.duLieu,
      });

      ghiNhatKy(uid, "ky_duyet_worm", `session=${sessionId} seq=${ketQua.wormSeq} tab=${kq.tabId ?? "-"}`);
      res.json({ ...ketQua, contentHash: kq.contentHash, tabId: kq.tabId });
    } catch (err) {
      traLoi(res, err);
    }
  });

  app.get("/api/sessions/:id/sign-off", (req, res) => {
    try {
      const sessionId = String(req.params.id || "").trim();
      if (!sessionId) return res.status(400).json({ error: "Thiếu mã phiên khám" });

      const uid = req.nguoiDung?.id;
      if (typeof uid !== "number") return res.status(401).json({ error: "Chưa đăng nhập" });
      const laQuanTri = req.nguoiDung?.vai === "quan_tri";
      if (!laQuanTri && caKhamThuocNguoiKhac(uid, sessionId)) {
        return res.status(403).json({ error: "Không có quyền xem lịch sử ký duyệt của bác sĩ khác", code: "idor_forbidden" });
      }

      // Mã ca chỉ duy nhất theo từng bác sĩ: quản trị lọc thêm theo ?userId= khi hai bác sĩ trùng mã ca.
      const locNguoi = Number(req.query.userId);
      const entries = laQuanTri
        ? Number.isInteger(locNguoi) && locNguoi > 0
          ? khoWorm.docLichSuSignOff(sessionId, { userId: locNguoi })
          : khoWorm.docLichSuSignOff(sessionId)
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
