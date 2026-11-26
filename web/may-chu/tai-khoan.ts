/**
 * ĐĂNG KÝ / ĐĂNG NHẬP.
 *
 * - Mật khẩu băm bằng scrypt (giới hạn semaphore tối đa 4 tác vụ scrypt chạy song song).
 * - Phiên: token ngẫu nhiên 32 byte trong cookie HttpOnly + SameSite=Lax (+ Secure khi chạy https);
 *   cơ sở dữ liệu chỉ giữ mã băm của token.
 * - Đăng ký phải có MÃ MỜI do quản trị tạo, trừ tài khoản đầu tiên — tài khoản đầu tiên thành
 *   quản trị và CHỈ tạo được từ chính máy chạy server (không qua đường hầm/mạng ngoài).
 * - Mọi đường /api/* khác đều phải đăng nhập.
 * - Sai mật khẩu quá nhiều lần thì khoá tạm theo địa chỉ + email (LAN_THU giới hạn <= 5.000 mục).
 */
import crypto from "crypto";
import type express from "express";
import { chuyenJsonCu, db, giaoDich, ghiNhatKy } from "./csdl";

const COOKIE = "mt_phien";
const HAN_PHIEN = 14 * 24 * 3600_000; // 14 ngày
const HAN_MA_MOI = 7 * 24 * 3600_000;
const TOI_DA_SCRYPT_DONG_THOI = 4;
const TOI_DA_CHO_SCRYPT = 64;
export const TOI_DA_MUC_LAN_THU = 5_000;

export type NguoiDung = { id: number; email: string; hoTen: string; vai: "quan_tri" | "bac_si" };
declare global {
  namespace Express {
    interface Request {
      nguoiDung?: NguoiDung;
    }
  }
}

// ------------------------------------------------------------------ Semaphore scrypt (tối đa 4 song song)
let scryptDangChay = 0;
const hangChoScrypt: Array<() => void> = [];

function xinLuotScrypt(): Promise<() => void> {
  return new Promise((resolve, reject) => {
    const capPhat = () => {
      scryptDangChay++;
      let daNha = false;
      resolve(() => {
        if (daNha) return;
        daNha = true;
        scryptDangChay--;
        const tiep = hangChoScrypt.shift();
        if (tiep) tiep();
      });
    };
    if (scryptDangChay < TOI_DA_SCRYPT_DONG_THOI) {
      capPhat();
      return;
    }
    if (hangChoScrypt.length >= TOI_DA_CHO_SCRYPT) {
      reject(Object.assign(new Error("Hệ thống xác thực đang quá tải, vui lòng thử lại sau giây lát."), { ma: 503 }));
      return;
    }
    hangChoScrypt.push(capPhat);
  });
}

// ------------------------------------------------------------------ băm mật khẩu
const THAM_SO = { N: 16384, r: 8, p: 1 };
async function scrypt(matKhau: string, muoi: Buffer, N: number, r: number, p: number): Promise<Buffer> {
  const nhaLuot = await xinLuotScrypt();
  try {
    return await new Promise<Buffer>((ok, loi) =>
      crypto.scrypt(matKhau, muoi, 64, { N, r, p, maxmem: 64 * 1024 * 1024 }, (e, k) => (e ? loi(e) : ok(k))),
    );
  } finally {
    nhaLuot();
  }
}

async function bamMatKhau(matKhau: string): Promise<string> {
  const muoi = crypto.randomBytes(16);
  const k = await scrypt(matKhau, muoi, THAM_SO.N, THAM_SO.r, THAM_SO.p);
  return `scrypt$${THAM_SO.N}$${THAM_SO.r}$${THAM_SO.p}$${muoi.toString("base64")}$${k.toString("base64")}`;
}

async function khopMatKhau(matKhau: string, luu: string): Promise<boolean> {
  const [ten, N, r, p, muoi, bam] = String(luu || "").split("$");
  const nNum = Number(N);
  const rNum = Number(r);
  const pNum = Number(p);
  if (ten !== "scrypt" || !Number.isInteger(nNum) || !Number.isInteger(rNum) || !Number.isInteger(pNum) || !muoi || !bam) {
    return false;
  }
  const k = await scrypt(matKhau, Buffer.from(muoi, "base64"), nNum, rNum, pNum);
  const goc = Buffer.from(bam, "base64");
  return goc.length === k.length && crypto.timingSafeEqual(goc, k);
}

// Khi email không tồn tại vẫn băm một lần để chống lộ email qua timing side-channel.
// Dùng Promise khởi tạo an toàn và luôn `await` trước khi đối sánh.
let huaBamGia: Promise<string> | null = null;
function layBamGia(): Promise<string> {
  if (!huaBamGia) {
    huaBamGia = bamMatKhau(crypto.randomBytes(16).toString("hex")).catch((err) => {
      huaBamGia = null;
      throw err;
    });
  }
  return huaBamGia;
}
void layBamGia().catch(() => {});

const sha256 = (s: string) => crypto.createHash("sha256").update(s).digest("hex");

// ------------------------------------------------------------------ địa chỉ, cookie
function diaChi(req: express.Request) {
  const tuMay = laMayNay(req.socket?.remoteAddress);
  return (tuMay && (req.get("cf-connecting-ip") || req.get("x-forwarded-for")?.split(",")[0].trim())) || req.socket?.remoteAddress || "?";
}
function laMayNay(a?: string) {
  return !!a && (a === "127.0.0.1" || a === "::1" || a === "::ffff:127.0.0.1");
}
function tuChinhMayNay(req: express.Request) {
  return laMayNay(req.socket?.remoteAddress) && !req.get("cf-connecting-ip") && !req.get("x-forwarded-for");
}
const quaHttps = (req: express.Request) => req.secure || req.get("x-forwarded-proto") === "https";

function docCookie(req: express.Request, ten: string) {
  for (const phan of (req.get("cookie") || "").split(";")) {
    const i = phan.indexOf("=");
    if (i > 0 && phan.slice(0, i).trim() === ten) {
      try {
        return decodeURIComponent(phan.slice(i + 1).trim());
      } catch {
        return null;
      }
    }
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

// ------------------------------------------------------------------ giới hạn số lần thử (giới hạn <= 5.000 mục)
const LAN_THU = new Map<string, number[]>();
const CUA_SO_TOI_DA_MS = 60 * 60_000;

function donVaGioiHanLanThu(bay: number) {
  if (LAN_THU.size < TOI_DA_MUC_LAN_THU) return;
  for (const [k, ds] of LAN_THU) {
    const con = ds.filter((t) => bay - t < CUA_SO_TOI_DA_MS);
    if (con.length === 0) LAN_THU.delete(k);
    else LAN_THU.set(k, con);
  }
  while (LAN_THU.size >= TOI_DA_MUC_LAN_THU) {
    const dauTien = LAN_THU.keys().next().value;
    if (dauTien === undefined) break;
    LAN_THU.delete(dauTien);
  }
}

/** Trả số phút phải chờ nếu đã vượt `toiDa` lần trong `phut` phút; không thì 0. */
export function conPhaiCho(khoa: string, toiDa: number, phut: number): number {
  const bay = Date.now();
  const hienTai = LAN_THU.get(khoa);
  if (!hienTai || hienTai.length === 0) return 0;
  const ds = hienTai.filter((t) => bay - t < phut * 60_000);
  if (ds.length === 0) {
    LAN_THU.delete(khoa);
    return 0;
  }
  LAN_THU.set(khoa, ds);
  return ds.length >= toiDa ? Math.ceil((ds[0] + phut * 60_000 - bay) / 60_000) : 0;
}

export function ghiLanThu(khoa: string): void {
  const bay = Date.now();
  const cu = (LAN_THU.get(khoa) || []).filter((t) => bay - t < CUA_SO_TOI_DA_MS);
  LAN_THU.delete(khoa);
  donVaGioiHanLanThu(bay);
  cu.push(bay);
  LAN_THU.set(khoa, cu);
}

export function kichThuocLanThu(): number {
  return LAN_THU.size;
}

// ------------------------------------------------------------------ kiểm dữ liệu nhập & Origin
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

function tachTenMay(hostHeader: string): string {
  const h = hostHeader.trim().toLowerCase();
  if (!h) return "";
  if (h.startsWith("[")) {
    const dong = h.indexOf("]");
    return dong >= 0 ? h.slice(0, dong + 1) : h;
  }
  return h.split(":")[0];
}

function docDanhSachNguonDuocPhep(): Set<string> {
  const ds = new Set<string>();
  const raw = process.env.MEDITRACE_NGUON_DUOC_PHEP || "";
  for (const muc of raw.split(",")) {
    const s = muc.trim().toLowerCase().replace(/\/+$/, "");
    if (!s) continue;
    if (s.startsWith("http://") || s.startsWith("https://")) {
      try {
        const u = new URL(s);
        // Giữ nguyên giao thức (https:// vs http://) để chống tấn công hạ cấp giao thức qua Origin
        ds.add(`${u.protocol}//${u.host}`.toLowerCase());
      } catch {
        // Bỏ qua chuỗi URL sai cú pháp
      }
    } else {
      ds.add(s);
    }
  }
  return ds;
}

/** Bọc handler async cho Express 4 để không bao giờ rò rỉ UnhandledPromiseRejection. */
function bocAsync(fn: (req: express.Request, res: express.Response, next: express.NextFunction) => Promise<unknown>): express.RequestHandler {
  return (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch((err: any) => {
      if (res.headersSent) return next(err);
      const raw = Number(err?.ma || err?.status || err?.statusCode);
      const status = Number.isInteger(raw) && raw >= 100 && raw <= 599 ? raw : 500;
      res.status(status).json({ error: err?.message || "Lỗi xử lý tài khoản" });
    });
  };
}

// ------------------------------------------------------------------ các đường
export function lapTaiKhoan(app: express.Express) {
  // Chặn CSRF từ trang khác: KHÔNG cho phép bất kỳ wildcard `.vercel.app` hay `.trycloudflare.com` nào;
  // chỉ cho phép cùng host hoặc khớp chính xác danh sách trong `MEDITRACE_NGUON_DUOC_PHEP`.
  app.use("/api", (req, res, next) => {
    if (req.method === "GET" || req.method === "HEAD" || req.method === "OPTIONS") return next();
    const nguon = req.get("origin");
    if (nguon) {
      try {
        const parsed = new URL(nguon);
        if (parsed.protocol !== "http:" && parsed.protocol !== "https:") {
          return res.status(403).json({ error: "Origin không hợp lệ" });
        }
        const originFull = `${parsed.protocol}//${parsed.host}`.toLowerCase();
        const may = parsed.host.toLowerCase();
        const mayClean = parsed.hostname.toLowerCase();

        const reqHost = (req.get("host") || "").trim().toLowerCase();
        const reqHostClean = tachTenMay(reqHost);
        const tuMay = laMayNay(req.socket?.remoteAddress);
        const fwdHost = tuMay ? (req.get("x-forwarded-host") || "").split(",")[0].trim().toLowerCase() : "";
        const fwdHostClean = tachTenMay(fwdHost);

        const nguonDuocPhep = docDanhSachNguonDuocPhep();
        const cungHost =
          (!!reqHost && (may === reqHost || mayClean === reqHostClean)) ||
          (!!fwdHost && (may === fwdHost || mayClean === fwdHostClean));
        const khopDanhSach = nguonDuocPhep.has(originFull) || nguonDuocPhep.has(may) || nguonDuocPhep.has(mayClean);

        if (!cungHost && !khopDanhSach) {
          return res.status(403).json({ error: "Yêu cầu từ trang khác bị từ chối" });
        }
      } catch {
        return res.status(403).json({ error: "Origin không hợp lệ" });
      }
    }
    const coThan = Number(req.get("content-length") || 0) > 0 || !!req.get("transfer-encoding");
    if (coThan && !req.is("application/json")) return res.status(415).json({ error: "Chỉ nhận JSON" });
    next();
  });

  app.get("/api/toi", (req, res) => {
    try {
      const coNguoi = (db.prepare("SELECT COUNT(*) AS n FROM nguoi_dung").get() as { n: number }).n > 0;
      res.set("Cache-Control", "no-store").json({
        nguoiDung: nguoiDungTuPhien(req),
        canMaMoi: coNguoi,
        taoQuanTriDuocTuDay: !coNguoi && tuChinhMayNay(req),
      });
    } catch (err: any) {
      res.status(500).json({ error: err?.message || "Không kiểm tra được phiên" });
    }
  });

  app.post(
    "/api/dang-ky",
    bocAsync(async (req, res) => {
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
            if (!tuChinhMayNay(req)) {
              throw Object.assign(new Error("Tài khoản quản trị đầu tiên phải tạo trên chính máy chạy máy chủ."), { ma: 403 });
            }
            vai = "quan_tri";
          } else {
            const ma = db.prepare("SELECT dung_boi, het_han FROM ma_moi WHERE bam_ma = ?").get(bamMa) as
              | { dung_boi: number | null; het_han: number }
              | undefined;
            if (!ma || ma.dung_boi || ma.het_han < Date.now()) {
              throw Object.assign(new Error("Mã mời không đúng, đã dùng hoặc đã hết hạn. Hỏi quản trị để lấy mã mới."), { ma: 403 });
            }
          }
          if (db.prepare("SELECT 1 FROM nguoi_dung WHERE email = ?").get(email)) {
            throw Object.assign(new Error("Email này đã có tài khoản. Chuyển sang Đăng nhập."), { ma: 409 });
          }
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
    }),
  );

  app.post(
    "/api/dang-nhap",
    bocAsync(async (req, res) => {
      const ip = diaChi(req);
      const email = typeof req.body?.email === "string" ? req.body.email.trim().toLowerCase() : "";
      const matKhau = typeof req.body?.matKhau === "string" ? req.body.matKhau : "";
      const cho = Math.max(conPhaiCho(`dn|${ip}|${email}`, 5, 15), conPhaiCho(`dn|${ip}`, 20, 15));
      if (cho) return res.status(429).json({ error: `Sai quá nhiều lần. Thử lại sau ${cho} phút.` });

      const r = db.prepare("SELECT id, email, ho_ten, vai, mat_khau_bam FROM nguoi_dung WHERE email = ?").get(email) as
        | { id: number; email: string; ho_ten: string; vai: NguoiDung["vai"]; mat_khau_bam: string }
        | undefined;
      const bamDoiChieu = r?.mat_khau_bam || (await layBamGia());
      const dung = await khopMatKhau(matKhau, bamDoiChieu);
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
    }),
  );

  app.post("/api/dang-xuat", (req, res) => {
    try {
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
    } catch (err: any) {
      res.status(500).json({ error: err?.message || "Không đăng xuất được" });
    }
  });

  // Từ đây trở xuống: mọi /api/* phải đăng nhập.
  app.use("/api", (req, res, next) => {
    try {
      const nd = nguoiDungTuPhien(req);
      if (!nd) return res.status(401).json({ error: "Phiên đăng nhập đã hết. Đăng nhập lại." });
      req.nguoiDung = nd;
      if (req.method === "POST" && req.body?.allowExternal === true) {
        ghiNhatKy(nd.id, "goi_mo_hinh_ngoai", req.path, diaChi(req));
      }
      next();
    } catch (err) {
      next(err);
    }
  });

  const chiQuanTri: express.RequestHandler = (req, res, next) =>
    req.nguoiDung?.vai === "quan_tri" ? next() : res.status(403).json({ error: "Chỉ quản trị làm được việc này" });

  app.post("/api/ma-moi", chiQuanTri, (req, res) => {
    try {
      const BANG = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
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
    } catch (err: any) {
      res.status(500).json({ error: err?.message || "Không tạo được mã mời" });
    }
  });

  app.get("/api/ma-moi", chiQuanTri, (_req, res) => {
    try {
      const ds = db
        .prepare(
          `SELECT m.goi_y, m.tao_luc, m.het_han, m.dung_luc, n.ho_ten AS dung_boi
           FROM ma_moi m LEFT JOIN nguoi_dung n ON n.id = m.dung_boi ORDER BY m.tao_luc DESC LIMIT 20`,
        )
        .all();
      const nguoi = db.prepare("SELECT id, email, ho_ten, vai, tao_luc, dang_nhap_cuoi FROM nguoi_dung ORDER BY id").all();
      res.json({ maMoi: ds, nguoiDung: nguoi });
    } catch (err: any) {
      res.status(500).json({ error: err?.message || "Không đọc được danh sách mã mời" });
    }
  });
}
