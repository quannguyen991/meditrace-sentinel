/**
 * ĐĂNG KÝ / ĐĂNG NHẬP.
 *
 * - Mật khẩu băm bằng scrypt (có sẵn trong Node), muối riêng từng người.
 * - Phiên: token ngẫu nhiên 32 byte trong cookie HttpOnly + SameSite=Lax (+ Secure khi chạy https);
 *   cơ sở dữ liệu chỉ giữ mã băm của token.
 * - Đăng ký phải có MÃ MỜI do quản trị tạo, trừ tài khoản đầu tiên — tài khoản đầu tiên thành
 *   quản trị và CHỈ tạo được từ chính máy chạy server (không qua đường hầm/mạng ngoài), để khi
 *   đưa web ra ngoài không ai lạ giành được quyền quản trị.
 * - Mọi đường /api/* khác đều phải đăng nhập (khối app.use("/api", …) sau /api/dang-xuat).
 * - Sai mật khẩu quá nhiều lần thì khoá tạm theo địa chỉ + email.
 */
import crypto from "crypto";
import type express from "express";
import { db, giaoDich, ghiNhatKy, chuyenJsonCu } from "./csdl";

const COOKIE = "mt_phien";
const HAN_PHIEN = 14 * 24 * 3600_000; // 14 ngày
const HAN_MA_MOI = 7 * 24 * 3600_000;

export type NguoiDung = { id: number; email: string; hoTen: string; vai: "quan_tri" | "bac_si" };
declare global {
  namespace Express {
    interface Request {
      nguoiDung?: NguoiDung;
    }
  }
}

// ------------------------------------------------------------------ băm
const THAM_SO = { N: 16384, r: 8, p: 1 };
function scrypt(matKhau: string, muoi: Buffer, N: number, r: number, p: number): Promise<Buffer> {
  return new Promise((ok, loi) =>
    crypto.scrypt(matKhau, muoi, 64, { N, r, p, maxmem: 64 * 1024 * 1024 }, (e, k) => (e ? loi(e) : ok(k))),
  );
}
async function bamMatKhau(matKhau: string) {
  const muoi = crypto.randomBytes(16);
  const k = await scrypt(matKhau, muoi, THAM_SO.N, THAM_SO.r, THAM_SO.p);
  return `scrypt$${THAM_SO.N}$${THAM_SO.r}$${THAM_SO.p}$${muoi.toString("base64")}$${k.toString("base64")}`;
}
async function khopMatKhau(matKhau: string, luu: string) {
  const [ten, N, r, p, muoi, bam] = luu.split("$");
  if (ten !== "scrypt") return false;
  const k = await scrypt(matKhau, Buffer.from(muoi, "base64"), +N, +r, +p);
  const goc = Buffer.from(bam, "base64");
  return goc.length === k.length && crypto.timingSafeEqual(goc, k);
}
// Khi email không tồn tại vẫn băm một lần, để thời gian trả lời không lộ email nào có tài khoản.
let BAM_GIA = "";
bamMatKhau(crypto.randomBytes(12).toString("hex")).then((b) => (BAM_GIA = b));

const sha256 = (s: string) => crypto.createHash("sha256").update(s).digest("hex");

// ------------------------------------------------------------------ địa chỉ, cookie
/** Địa chỉ người gọi. Qua Cloudflare Tunnel thì kết nối đến từ máy này, địa chỉ thật nằm ở cf-connecting-ip. */
function diaChi(req: express.Request) {
  const tuMay = laMayNay(req.socket.remoteAddress);
  return (tuMay && (req.get("cf-connecting-ip") || req.get("x-forwarded-for")?.split(",")[0].trim())) || req.socket.remoteAddress || "?";
}
function laMayNay(a?: string) {
  return !!a && (a === "127.0.0.1" || a === "::1" || a === "::ffff:127.0.0.1");
}
/** Yêu cầu đến thẳng từ máy chạy server, không qua proxy/đường hầm nào. */
function tuChinhMayNay(req: express.Request) {
  return laMayNay(req.socket.remoteAddress) && !req.get("cf-connecting-ip") && !req.get("x-forwarded-for");
}
const quaHttps = (req: express.Request) => req.secure || req.get("x-forwarded-proto") === "https";

function docCookie(req: express.Request, ten: string) {
  for (const phan of (req.get("cookie") || "").split(";")) {
    const i = phan.indexOf("=");
    if (i > 0 && phan.slice(0, i).trim() === ten) return decodeURIComponent(phan.slice(i + 1).trim());
  }
  return null;
}
function datCookie(req: express.Request, res: express.Response, gia: string, tuoiGiay: number) {
  res.append(
    "Set-Cookie",
    `${COOKIE}=${encodeURIComponent(gia)}; Path=/; HttpOnly; SameSite=Lax; Max-Age=${tuoiGiay}${quaHttps(req) ? "; Secure" : ""}`,
  );
}

function taoPhien(req: express.Request, res: express.Response, uid: number) {
  const token = crypto.randomBytes(32).toString("base64url");
  const bay = Date.now();
  db.prepare("DELETE FROM phien WHERE het_han < ?").run(bay);
  db.prepare("INSERT INTO phien (bam_token, nguoi_dung_id, tao_luc, het_han, dia_chi, trinh_duyet) VALUES (?, ?, ?, ?, ?, ?)").run(
    sha256(token),
    uid,
    bay,
    bay + HAN_PHIEN,
    diaChi(req),
    (req.get("user-agent") || "").slice(0, 200),
  );
  db.prepare("UPDATE nguoi_dung SET dang_nhap_cuoi = ? WHERE id = ?").run(bay, uid);
  datCookie(req, res, token, HAN_PHIEN / 1000);
}

function nguoiDungTuPhien(req: express.Request): NguoiDung | null {
  const token = docCookie(req, COOKIE);
  if (!token) return null;
  const r = db
    .prepare(
      `SELECT n.id, n.email, n.ho_ten, n.vai FROM phien p JOIN nguoi_dung n ON n.id = p.nguoi_dung_id
       WHERE p.bam_token = ? AND p.het_han > ?`,
    )
    .get(sha256(token), Date.now()) as { id: number; email: string; ho_ten: string; vai: NguoiDung["vai"] } | undefined;
  return r ? { id: r.id, email: r.email, hoTen: r.ho_ten, vai: r.vai } : null;
}

// ------------------------------------------------------------------ giới hạn số lần thử
const LAN_THU = new Map<string, number[]>();
/** Trả số phút phải chờ nếu đã vượt `toiDa` lần trong `phut` phút; không thì 0. */
function conPhaiCho(khoa: string, toiDa: number, phut: number) {
  const bay = Date.now();
  const ds = (LAN_THU.get(khoa) || []).filter((t) => bay - t < phut * 60_000);
  LAN_THU.set(khoa, ds);
  return ds.length >= toiDa ? Math.ceil((ds[0] + phut * 60_000 - bay) / 60_000) : 0;
}
const ghiLanThu = (khoa: string) => LAN_THU.set(khoa, [...(LAN_THU.get(khoa) || []), Date.now()]);

// ------------------------------------------------------------------ kiểm dữ liệu nhập
const EMAIL = /^[^\s@]{1,64}@[^\s@]{1,190}\.[^\s@]{2,}$/;
function kiemDangKy(b: any): string | null {
  if (!b || typeof b !== "object") return "Thiếu thông tin";
  if (typeof b.hoTen !== "string" || b.hoTen.trim().length < 2 || b.hoTen.length > 80) return "Họ tên từ 2 đến 80 ký tự";
  if (typeof b.email !== "string" || !EMAIL.test(b.email.trim())) return "Email không đúng dạng";
  if (typeof b.matKhau !== "string" || b.matKhau.length < 8) return "Mật khẩu ít nhất 8 ký tự";
  if (b.matKhau.length > 200) return "Mật khẩu quá dài";
  return null;
}
const chuanMaMoi = (m: unknown) => (typeof m === "string" ? m.toUpperCase().replace(/[^A-Z0-9]/g, "") : "");

// ------------------------------------------------------------------ các đường
export function lapTaiKhoan(app: express.Express) {
  // Chặn gửi biểu mẫu từ trang khác: yêu cầu ghi phải là JSON, và nếu có Origin thì phải cùng máy chủ,
  // hoặc nằm trong danh sách MEDITRACE_NGUON_DUOC_PHEP (tên miền, cách nhau dấu phẩy) — dùng cho tên
  // miền cố định trên Vercel chuyển tiếp về đây, nơi Host là đường hầm còn Origin là tên miền Vercel.
  const nguonDuocPhep = new Set(
    (process.env.MEDITRACE_NGUON_DUOC_PHEP || "").split(",").map((s) => s.trim().toLowerCase()).filter(Boolean),
  );
  app.use("/api", (req, res, next) => {
    if (req.method === "GET" || req.method === "HEAD" || req.method === "OPTIONS") return next();
    const nguon = req.get("origin");
    if (nguon) {
      try {
        const may = new URL(nguon).host.toLowerCase();
        if (may !== req.get("host") && !nguonDuocPhep.has(may))
          return res.status(403).json({ error: "Yêu cầu từ trang khác bị từ chối" });
      } catch {
        return res.status(403).json({ error: "Origin không hợp lệ" });
      }
    }
    // Biểu mẫu HTML chỉ gửi được text/plain, urlencoded, multipart — chặn hết, chỉ nhận JSON (hoặc không có thân).
    const coThan = Number(req.get("content-length") || 0) > 0 || !!req.get("transfer-encoding");
    if (coThan && !req.is("application/json")) return res.status(415).json({ error: "Chỉ nhận JSON" });
    next();
  });

  app.get("/api/toi", (req, res) => {
    const coNguoi = (db.prepare("SELECT COUNT(*) AS n FROM nguoi_dung").get() as { n: number }).n > 0;
    res.set("Cache-Control", "no-store").json({
      nguoiDung: nguoiDungTuPhien(req),
      // Chưa có tài khoản nào: người đầu tiên đăng ký không cần mã mời (và phải ngồi ở máy chạy server).
      canMaMoi: coNguoi,
      taoQuanTriDuocTuDay: !coNguoi && tuChinhMayNay(req),
    });
  });

  app.post("/api/dang-ky", async (req, res) => {
    const ip = diaChi(req);
    const cho = conPhaiCho(`dk|${ip}`, 10, 60);
    if (cho) return res.status(429).json({ error: `Đăng ký quá nhiều lần. Thử lại sau ${cho} phút.` });
    ghiLanThu(`dk|${ip}`);

    const loi = kiemDangKy(req.body);
    if (loi) return res.status(400).json({ error: loi });
    const email = req.body.email.trim().toLowerCase();
    const hoTen = req.body.hoTen.trim();
    const bamMa = sha256(chuanMaMoi(req.body.maMoi));
    const matKhauBam = await bamMatKhau(req.body.matKhau);

    let uid = 0;
    let vai = "bac_si" as NguoiDung["vai"];
    try {
      giaoDich(() => {
        const soNguoi = (db.prepare("SELECT COUNT(*) AS n FROM nguoi_dung").get() as { n: number }).n;
        if (soNguoi === 0) {
          if (!tuChinhMayNay(req))
            throw Object.assign(new Error("Tài khoản quản trị đầu tiên phải tạo trên chính máy chạy máy chủ."), { ma: 403 });
          vai = "quan_tri";
        } else {
          const ma = db.prepare("SELECT dung_boi, het_han FROM ma_moi WHERE bam_ma = ?").get(bamMa) as
            | { dung_boi: number | null; het_han: number }
            | undefined;
          if (!ma || ma.dung_boi || ma.het_han < Date.now())
            throw Object.assign(new Error("Mã mời không đúng, đã dùng hoặc đã hết hạn. Hỏi quản trị để lấy mã mới."), { ma: 403 });
        }
        if (db.prepare("SELECT 1 FROM nguoi_dung WHERE email = ?").get(email))
          throw Object.assign(new Error("Email này đã có tài khoản. Chuyển sang Đăng nhập."), { ma: 409 });
        const r = db
          .prepare("INSERT INTO nguoi_dung (email, ho_ten, mat_khau_bam, vai, tao_luc) VALUES (?, ?, ?, ?, ?)")
          .run(email, hoTen, matKhauBam, vai, Date.now());
        uid = Number(r.lastInsertRowid);
        if (soNguoi > 0) db.prepare("UPDATE ma_moi SET dung_boi = ?, dung_luc = ? WHERE bam_ma = ?").run(uid, Date.now(), bamMa);
      });
    } catch (e: any) {
      return res.status(e?.ma || 500).json({ error: e?.message || String(e) });
    }
    ghiNhatKy(uid, "dang_ky", vai, ip);
    if (vai === "quan_tri") {
      const chuyen = chuyenJsonCu(uid);
      if (chuyen.length) ghiNhatKy(uid, "chuyen_json_cu", chuyen.join("; "), ip);
    }
    taoPhien(req, res, uid);
    res.json({ nguoiDung: { id: uid, email, hoTen, vai } });
  });

  app.post("/api/dang-nhap", async (req, res) => {
    const ip = diaChi(req);
    const email = typeof req.body?.email === "string" ? req.body.email.trim().toLowerCase() : "";
    const matKhau = typeof req.body?.matKhau === "string" ? req.body.matKhau : "";
    const cho = Math.max(conPhaiCho(`dn|${ip}|${email}`, 5, 15), conPhaiCho(`dn|${ip}`, 20, 15));
    if (cho) return res.status(429).json({ error: `Sai quá nhiều lần. Thử lại sau ${cho} phút.` });

    const r = db.prepare("SELECT id, email, ho_ten, vai, mat_khau_bam FROM nguoi_dung WHERE email = ?").get(email) as
      | { id: number; email: string; ho_ten: string; vai: NguoiDung["vai"]; mat_khau_bam: string }
      | undefined;
    const dung = await khopMatKhau(matKhau, r?.mat_khau_bam || BAM_GIA);
    if (!r || !dung) {
      ghiLanThu(`dn|${ip}|${email}`);
      ghiLanThu(`dn|${ip}`);
      ghiNhatKy(r?.id ?? null, "dang_nhap_sai", r ? null : `email không có: ${email.slice(0, 80)}`, ip);
      return res.status(401).json({ error: "Email hoặc mật khẩu không đúng" });
    }
    LAN_THU.delete(`dn|${ip}|${email}`);
    ghiNhatKy(r.id, "dang_nhap", null, ip);
    taoPhien(req, res, r.id);
    res.json({ nguoiDung: { id: r.id, email: r.email, hoTen: r.ho_ten, vai: r.vai } });
  });

  app.post("/api/dang-xuat", (req, res) => {
    const token = docCookie(req, COOKIE);
    if (token) {
      const p = db.prepare("SELECT nguoi_dung_id FROM phien WHERE bam_token = ?").get(sha256(token)) as
        | { nguoi_dung_id: number }
        | undefined;
      db.prepare("DELETE FROM phien WHERE bam_token = ?").run(sha256(token));
      if (p) ghiNhatKy(p.nguoi_dung_id, "dang_xuat", null, diaChi(req));
    }
    datCookie(req, res, "", 0);
    res.json({ ok: true });
  });

  // Từ đây trở xuống: mọi /api/* phải đăng nhập.
  app.use("/api", (req, res, next) => {
    const nd = nguoiDungTuPhien(req);
    if (!nd) return res.status(401).json({ error: "Phiên đăng nhập đã hết. Đăng nhập lại." });
    req.nguoiDung = nd;
    // Ghi lại mỗi lần nội dung được phép gửi ra mô hình ngoài (công tắc trên giao diện đang bật).
    if (req.method === "POST" && req.body?.allowExternal === true) ghiNhatKy(nd.id, "goi_mo_hinh_ngoai", req.path, diaChi(req));
    next();
  });

  const chiQuanTri: express.RequestHandler = (req, res, next) =>
    req.nguoiDung?.vai === "quan_tri" ? next() : res.status(403).json({ error: "Chỉ quản trị làm được việc này" });

  /** Tạo mã mời: 8 ký tự, dùng một lần, hết hạn sau 7 ngày. Mã chỉ hiện MỘT LẦN ở đây. */
  app.post("/api/ma-moi", chiQuanTri, (req, res) => {
    const BANG = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"; // bỏ I, O, 0, 1 cho khỏi nhầm
    const ma = Array.from(crypto.randomBytes(8), (b) => BANG[b % BANG.length]).join("");
    const bay = Date.now();
    db.prepare("INSERT INTO ma_moi (bam_ma, goi_y, tao_boi, tao_luc, het_han) VALUES (?, ?, ?, ?, ?)").run(
      sha256(ma),
      ma.slice(-2),
      req.nguoiDung!.id,
      bay,
      bay + HAN_MA_MOI,
    );
    ghiNhatKy(req.nguoiDung!.id, "tao_ma_moi", `…${ma.slice(-2)}`, diaChi(req));
    res.json({ ma: `${ma.slice(0, 4)}-${ma.slice(4)}`, hetHan: bay + HAN_MA_MOI });
  });

  app.get("/api/ma-moi", chiQuanTri, (_req, res) => {
    const ds = db
      .prepare(
        `SELECT m.goi_y, m.tao_luc, m.het_han, m.dung_luc, n.ho_ten AS dung_boi
         FROM ma_moi m LEFT JOIN nguoi_dung n ON n.id = m.dung_boi ORDER BY m.tao_luc DESC LIMIT 20`,
      )
      .all();
    const nguoi = db
      .prepare("SELECT id, email, ho_ten, vai, tao_luc, dang_nhap_cuoi FROM nguoi_dung ORDER BY id")
      .all();
    res.json({ maMoi: ds, nguoiDung: nguoi });
  });
}
