import "./may-chu/env";
/**
 * Lớp trung gian giữa giao diện và DỊCH VỤ CHẠY TẠI CHỖ của MediTrace.
 *
 * Đã được module hoá thành các router độc lập trong `may-chu/routes/`:
 *   - `ca-kham.ts`:   /api/ca-kham, /api/ca-kham/:id, /api/kho/:ten, /api/health, /api/sample-cases
 *   - `asr.ts`:       /api/transcribe, /api/assign-roles, /api/generate-note, /api/error-attribution
 *   - `llm-ngoai.ts`: /api/external/status, /api/edit-note, /api/clinical-qa, /api/questions-external, ...
 *   - `tra-cuu.ts`:   /api/pubmed-search, /api/phac-do/muc-luc, /api/lookup-official
 *   - `tro-ly.ts`:    /api/tro-ly/*
 *   - `bhyt-ocr.ts`:  /api/ocr/phieu-cu, /api/bhyt/precheck, /api/bhyt/recompile
 *   - `boost-lam-sang.ts`: /api/clinical/informed-consent, /api/inpatient/ward-round-diff, /api/formulary/upload-csv
 *   - `sign-off.ts`:  /api/sessions/:id/sign-off, /api/worm/verify
 */
import express from "express";
import path from "path";
import { lapTaiKhoan } from "./may-chu/tai-khoan";
import { API, GOC, traLoi } from "./may-chu/routes/dung-chung";
import { cauHinhViteDev, chanTepNhayCam, diaChiLangNghe } from "./may-chu/chan-tep-dev";
import { dangKyCaKhamRoutes } from "./may-chu/routes/ca-kham";
import { dangKyAsrRoutes } from "./may-chu/routes/asr";
import { dangKyLlmNgoaiRoutes } from "./may-chu/routes/llm-ngoai";
import { dangKyTraCuuRoutes } from "./may-chu/routes/tra-cuu";
import { dangKyTroLyRoutes } from "./may-chu/routes/tro-ly";
import { dangKyBhytOcrRoutes } from "./may-chu/routes/bhyt-ocr";
import { dangKyBoostLamSangRoutes } from "./may-chu/routes/boost-lam-sang";
import { dangKySignOffRoutes } from "./may-chu/routes/sign-off";

export function taoUngDung() {
  const ungDung = express();
  const jsonToanCuc = express.json({ limit: "2mb" });
  const jsonAmThanh = express.json({ limit: "60mb" });

  // Qua đường hầm (Cloudflare Tunnel) kết nối đến từ chính máy này: tin X-Forwarded-Proto để biết là https.
  ungDung.set("trust proxy", "loopback");

  // Giới hạn JSON toàn cục 2MB; riêng /api/transcribe (kể cả có dấu / cuối hoặc chữ hoa) chờ sau middleware đăng nhập mới đọc tới 60MB.
  ungDung.use((req, res, next) => {
    if (req.path.replace(/\/+$/, "").toLowerCase() === "/api/transcribe") return next();
    return jsonToanCuc(req, res, next);
  });

  // Sau dòng lapTaiKhoan(ungDung) mọi /api/* đều yêu cầu đăng nhập.
  lapTaiKhoan(ungDung);

  // Chỉ sau khi đã xác thực phiên mới cho phép nhận payload âm thanh lớn tới 60MB.
  ungDung.use("/api/transcribe", jsonAmThanh);

  dangKyCaKhamRoutes(ungDung);
  const khoiDongHangDoiBanNhap = dangKyAsrRoutes(ungDung);
  dangKyLlmNgoaiRoutes(ungDung);
  dangKyTraCuuRoutes(ungDung);
  dangKyTroLyRoutes(ungDung);
  dangKyBhytOcrRoutes(ungDung);
  dangKyBoostLamSangRoutes(ungDung);
  dangKySignOffRoutes(ungDung);

  // Catch-all 404 JSON chuẩn cho mọi đường dẫn /api/* không khớp
  ungDung.use("/api", (_req, res) => {
    res.status(404).json({ error: "Không tìm thấy API" });
  });

  // Global error handler của Express (bắt cả 413 Payload Too Large và 400 Invalid JSON trả JSON chuẩn thay vì HTML)
  ungDung.use((err: any, _req: express.Request, res: express.Response, next: express.NextFunction) => {
    if (res.headersSent) return next(err);
    if (err?.type === "entity.too.large" || err?.status === 413 || err?.statusCode === 413) {
      return res.status(413).json({ error: "Dữ liệu gửi lên vượt quá giới hạn cho phép", code: "payload_too_large" });
    }
    if (err?.type === "entity.parse.failed" || (err instanceof SyntaxError && (err as any).status === 400)) {
      return res.status(400).json({ error: "JSON gửi lên không hợp lệ", code: "invalid_json" });
    }
    // Lỗi 5xx chỉ trả thông điệp chung, chi tiết ghi log (không lộ đường dẫn máy / stack).
    return traLoi(res, err);
  });

  return { app: ungDung, khoiDongHangDoiBanNhap };
}

const PORT = Number(process.env.PORT) || 3000;
const { app, khoiDongHangDoiBanNhap } = taoUngDung();
export { app };

async function khoiDong() {
  const laProduction = process.env.NODE_ENV === "production";
  // Đặt TRƯỚC Vite / express.static: không bao giờ phục vụ data/, db/, may-chu/, server.*, .env*, *.db*.
  app.use(chanTepNhayCam(GOC));
  if (laProduction) {
    app.use(express.static(path.join(GOC, "dist")));
    app.get("*", (_req, res) => res.sendFile(path.join(GOC, "dist", "index.html")));
  } else {
    const { createServer } = await import("vite");
    const vite = await createServer({ server: cauHinhViteDev(GOC, process.env), appType: "spa" });
    app.use(vite.middlewares);
  }
  khoiDongHangDoiBanNhap();
  const host = diaChiLangNghe(process.env, laProduction);
  const daNghe = () => {
    console.log(`Giao diện: http://${host && host !== "0.0.0.0" ? host : "localhost"}:${PORT}${host ? ` (chỉ nghe ${host})` : ""}`);
    console.log(`Dịch vụ MediTrace: ${API} (đổi bằng biến môi trường MEDITRACE_API)`);
  };
  if (host) app.listen(PORT, host, daNghe);
  else app.listen(PORT, daNghe);
}

if (process.env.MEDITRACE_KHONG_LISTEN !== "1") {
  void khoiDong();
}
