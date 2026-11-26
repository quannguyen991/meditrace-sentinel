/**
 * Chặn tệp nhạy cảm khi chạy giao diện ở chế độ phát triển (Vite middleware gắn vào Express).
 * Vite phục vụ mọi tệp trong thư mục gốc dự án, nên không có lớp này thì GET /data/meditrace.db,
 * /db/schema.sql, /may-chu/*.ts, /server.ts, /.env* đều trả 200 mà không cần đăng nhập.
 */
import path from "path";
import type express from "express";

/** Thư mục cấp một (tính từ gốc dự án web) không bao giờ được phục vụ qua HTTP. */
const THU_MUC_CAM = new Set(["data", "db", "may-chu", ".git", ".secrets", ".meditrace"]);
/** Tệp ở gốc dự án không được phục vụ. */
const TEP_GOC_CAM = new Set(["server.ts", "server.js", "server.cjs", "server.cjs.map", "package-lock.json", "bun.lock"]);
/** Tên tệp cấm ở bất kỳ đâu. */
const DUOI_CAM = /(?:\.(?:db|sqlite|sqlite3)(?:-wal|-shm|-journal)?|\.anchor\.json|\.jsonl|\.key|\.pem|\.crt)$/i;

function giaiMa(u: string): string {
  let s = u;
  for (let i = 0; i < 3; i++) {
    try {
      const d = decodeURIComponent(s);
      if (d === s) break;
      s = d;
    } catch {
      break;
    }
  }
  return s;
}

/** `true` nếu đường dẫn URL (kể cả dạng /@fs/<đường dẫn tuyệt đối>) trỏ tới tệp nhạy cảm. */
export function laDuongDanCam(url: string, goc: string): boolean {
  let p = giaiMa(String(url || "")).split(/[?#]/)[0].replace(/\\/g, "/");
  p = path.posix.normalize(p.startsWith("/") ? p : `/${p}`);

  const doanToanBo = p.split("/").filter(Boolean);
  for (const doan of doanToanBo) {
    const d = doan.toLowerCase();
    if (d.startsWith(".env") || d === ".git" || d === ".secrets" || DUOI_CAM.test(d)) return true;
  }

  let tuongDoi: string | null = p.slice(1);
  if (p.startsWith("/@fs/")) {
    const tuyetDoi = p.slice("/@fs/".length).toLowerCase();
    const gocChuan = goc.replace(/\\/g, "/").replace(/\/+$/, "").toLowerCase();
    tuongDoi = tuyetDoi.startsWith(`${gocChuan}/`) ? tuyetDoi.slice(gocChuan.length + 1) : null;
  }
  if (tuongDoi === null) return false;
  const cacDoan = tuongDoi.toLowerCase().split("/").filter(Boolean);
  if (!cacDoan.length) return false;
  if (THU_MUC_CAM.has(cacDoan[0])) return true;
  if (cacDoan.length === 1 && TEP_GOC_CAM.has(cacDoan[0])) return true;
  if (cacDoan[0] === "dist" && cacDoan[1]?.startsWith("server.")) return true;
  return false;
}

/** Middleware Express đặt TRƯỚC Vite: trả 404 (không tiết lộ tệp có tồn tại hay không). */
export function chanTepNhayCam(goc: string): express.RequestHandler {
  return (req, res, next) => {
    if (laDuongDanCam(req.originalUrl || req.url, goc)) {
      res.status(404).type("text/plain").send("Không tìm thấy");
      return;
    }
    next();
  };
}

/** Cấu hình `server` cho Vite middleware: bỏ `allowedHosts: true`, thêm `fs.deny` cho tệp nhạy cảm. */
export function cauHinhViteDev(goc: string, env: NodeJS.ProcessEnv) {
  const g = goc.replace(/\\/g, "/").replace(/\/+$/, "");
  const dsHost = String(env.MEDITRACE_ALLOWED_HOSTS || "")
    .split(",")
    .map((x) => x.trim())
    .filter(Boolean);
  return {
    middlewareMode: true as const,
    // Mặc định Vite chỉ nhận Host là localhost/IP; tên miền đường hầm phải liệt kê qua MEDITRACE_ALLOWED_HOSTS.
    allowedHosts: dsHost.length ? dsHost : undefined,
    fs: {
      deny: [
        ".env",
        ".env.*",
        "*.{crt,pem,key}",
        "**/.git/**",
        "**/*.db",
        "**/*.db-*",
        "**/*.{sqlite,sqlite3}",
        "**/*.{sqlite,sqlite3}-*",
        "**/*.anchor.json",
        "**/*.jsonl",
        `${g}/data/**`,
        `${g}/db/**`,
        `${g}/may-chu/**`,
        `${g}/server.ts`,
      ],
    },
  };
}

/**
 * Địa chỉ lắng nghe: chế độ phát triển mặc định chỉ 127.0.0.1 (đổi bằng HOST),
 * production giữ hành vi cũ (mọi giao diện mạng) trừ khi đặt HOST.
 */
export function diaChiLangNghe(env: NodeJS.ProcessEnv, laProduction: boolean): string | undefined {
  const host = String(env.HOST || "").trim();
  if (host) return host;
  return laProduction ? undefined : "127.0.0.1";
}
