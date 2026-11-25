/**
 * Lớp trung gian giữa giao diện và DỊCH VỤ CHẠY TẠI CHỖ của MediTrace.
 *
 * Đã được module hoá thành các router độc lập trong `may-chu/routes/`:
 *   - `ca-kham.ts`:   /api/ca-kham, /api/kho/:ten, /api/health, /api/sample-cases
 *   - `asr.ts`:       /api/transcribe, /api/assign-roles, /api/generate-note, /api/error-attribution
 *   - `llm-ngoai.ts`: /api/external/status, /api/edit-note, /api/clinical-qa, /api/questions-external, ...
 *   - `tra-cuu.ts`:   /api/pubmed-search, /api/phac-do/muc-luc, /api/lookup-official
 *   - `tro-ly.ts`:    /api/tro-ly/*
 *   - `bhyt-ocr.ts`:  /api/ocr/phieu-cu, /api/bhyt/precheck
 *   - `sign-off.ts`:  /api/sessions/:id/sign-off, /api/worm/verify
 */
import express from "express";
import path from "path";
import dotenv from "dotenv";
import { lapTaiKhoan } from "./may-chu/tai-khoan";
import { API, GOC } from "./may-chu/routes/dung-chung";
import { dangKyCaKhamRoutes } from "./may-chu/routes/ca-kham";
import { dangKyAsrRoutes } from "./may-chu/routes/asr";
import { dangKyLlmNgoaiRoutes } from "./may-chu/routes/llm-ngoai";
import { dangKyTraCuuRoutes } from "./may-chu/routes/tra-cuu";
import { dangKyTroLyRoutes } from "./may-chu/routes/tro-ly";
import { dangKyBhytOcrRoutes } from "./may-chu/routes/bhyt-ocr";
import { dangKySignOffRoutes } from "./may-chu/routes/sign-off";

dotenv.config({ path: ".env.local" });
dotenv.config();

const app = express();
const PORT = Number(process.env.PORT) || 3000;

app.use(express.json({ limit: "60mb" }));
// Qua đường hầm (Cloudflare Tunnel) kết nối đến từ chính máy này: tin X-Forwarded-Proto để biết là https.
app.set("trust proxy", "loopback");

// Sau dòng lapTaiKhoan(app) mọi /api/* đều yêu cầu đăng nhập.
lapTaiKhoan(app);

dangKyCaKhamRoutes(app);
const khoiDongHangDoiBanNhap = dangKyAsrRoutes(app);
dangKyLlmNgoaiRoutes(app);
dangKyTraCuuRoutes(app);
dangKyTroLyRoutes(app);
dangKyBhytOcrRoutes(app);
dangKySignOffRoutes(app);

async function khoiDong() {
  if (process.env.NODE_ENV === "production") {
    app.use(express.static(path.join(GOC, "dist")));
    app.get("*", (_req, res) => res.sendFile(path.join(GOC, "dist", "index.html")));
  } else {
    const { createServer } = await import("vite");
    const vite = await createServer({ server: { middlewareMode: true, allowedHosts: true }, appType: "spa" });
    app.use(vite.middlewares);
  }
  khoiDongHangDoiBanNhap();
  app.listen(PORT, () => {
    console.log(`Giao diện: http://localhost:${PORT}`);
    console.log(`Dịch vụ MediTrace: ${API} (đổi bằng biến môi trường MEDITRACE_API)`);
  });
}

khoiDong();
