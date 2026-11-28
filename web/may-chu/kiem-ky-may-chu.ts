/**
 * Chốt "bác sĩ đã ký duyệt và chưa sửa sau khi ký" phía MÁY CHỦ, cho mọi đường đưa hồ sơ ra khỏi phần mềm
 * (cổng người bệnh/QR, gói XML 1–5 BHYT, FHIR...). Giao diện có khoá riêng (choPhepDungHoSo) nhưng không đủ:
 * gọi thẳng API thì phải bị chặn ở đây.
 *
 * Bằng chứng ký chỉ lấy từ dữ liệu MÁY CHỦ ghi:
 *  - lúc ký, route ký duyệt ghi `ban_ky_duyet`: số thứ tự WORM, ĐÚNG tab đã ký, băm, và bản chụp `ca_kham.du_lieu`;
 *  - lúc xuất, lấy bản chụp của lần ký MỚI NHẤT, đối chiếu dòng WORM cùng số thứ tự (cùng bác sĩ, cùng ca, cùng băm),
 *    băm lại bản chụp và băm lại ca hiện tại theo ĐÚNG tab đã ký. `signOff.tabId` do trình duyệt lưu KHÔNG được dùng.
 *  - nội dung xuất được dựng từ CHÍNH bản chụp đó (gói*TuBanKy), không lấy nội dung hồ sơ trình duyệt gửi.
 */
import type express from "express";
import { trichChanDoanVaThuocTuSoap } from "../src/lib/compileEffectiveNote";
import { tinhKyDuyetTuCa } from "../src/lib/kyDuyet";
import { xayNguCanhChoTaoHoSo } from "../src/lib/nguCanhTroLy";
import { db, docMotCaKham } from "./csdl";

export const LOI_CHUA_KY_DUYET = "Bác sĩ chưa ký duyệt hồ sơ này (hoặc đã sửa sau khi ký) — chưa được xuất.";
export const MA_LOI_CHUA_KY_DUYET = "chua_ky_duyet";

/* ------------------------------------------------------------------ bản chụp lúc ký */

db.exec(`
  CREATE TABLE IF NOT EXISTS ban_ky_duyet (
    worm_seq       INTEGER PRIMARY KEY,
    nguoi_dung_id  INTEGER NOT NULL,
    session_id     TEXT    NOT NULL,
    tab_id         TEXT,
    content_hash   TEXT    NOT NULL,
    du_lieu        TEXT    NOT NULL,
    tao_luc        INTEGER NOT NULL
  );
  CREATE INDEX IF NOT EXISTS ix_ban_ky_duyet_ca ON ban_ky_duyet (nguoi_dung_id, session_id, worm_seq);
  CREATE TRIGGER IF NOT EXISTS ban_ky_duyet_khong_sua BEFORE UPDATE ON ban_ky_duyet
    BEGIN SELECT RAISE(ABORT, 'ban_ky_duyet chi ghi them'); END;
  CREATE TRIGGER IF NOT EXISTS ban_ky_duyet_khong_xoa BEFORE DELETE ON ban_ky_duyet
    BEGIN SELECT RAISE(ABORT, 'ban_ky_duyet chi ghi them'); END;
`);

export interface BanKyDuyet {
  wormSeq: number;
  sessionId: string;
  tabId: string | null;
  contentHash: string;
  /** `ca_kham.du_lieu` đúng lúc ký — nguồn duy nhất cho nội dung xuất. */
  duLieu: Record<string, any>;
}

/** Gọi trong route ký duyệt, ngay sau khi ghi dòng WORM. */
export function ghiBanKyDuyet(x: {
  uid: number;
  sessionId: string;
  wormSeq: number;
  tabId: string | null;
  contentHash: string;
  duLieu: unknown;
}) {
  db.prepare(
    `INSERT INTO ban_ky_duyet (worm_seq, nguoi_dung_id, session_id, tab_id, content_hash, du_lieu, tao_luc)
     VALUES (?, ?, ?, ?, ?, ?, ?)`,
  ).run(x.wormSeq, x.uid, x.sessionId, x.tabId, x.contentHash, JSON.stringify(x.duLieu ?? null), Date.now());
}

/* ------------------------------------------------------------------ kiểm */

export function kiemDaKyChoXuat(uid: number, caseId: string): { duoc: boolean; lyDo?: string; banKy?: BanKyDuyet } {
  const id = typeof caseId === "string" ? caseId.trim() : "";
  if (!id) return { duoc: false, lyDo: "Thiếu mã ca khám để đối chiếu chữ ký." };
  if (typeof uid !== "number" || !Number.isFinite(uid)) return { duoc: false, lyDo: "Chưa đăng nhập." };

  const ca = docMotCaKham(uid, id);
  if (!ca) return { duoc: false, lyDo: "Không tìm thấy ca khám này trên máy chủ." };

  const ban = db
    .prepare(
      `SELECT worm_seq, tab_id, content_hash, du_lieu FROM ban_ky_duyet
       WHERE nguoi_dung_id = ? AND session_id = ? ORDER BY worm_seq DESC LIMIT 1`,
    )
    .get(uid, id) as { worm_seq: number; tab_id: string | null; content_hash: string; du_lieu: string } | undefined;
  if (!ban) {
    const coKyCu = db.prepare("SELECT 1 FROM worm_signoff WHERE session_id = ? AND nguoi_dung_id = ? LIMIT 1").get(id, uid);
    return {
      duoc: false,
      lyDo: coKyCu
        ? "Chữ ký của ca này chưa có bản chụp máy chủ (ký trước khi có chốt xuất) — cần ký lại."
        : "Bác sĩ chưa ký duyệt ca này.",
    };
  }

  const dongWorm = db
    .prepare("SELECT session_id, nguoi_dung_id, content_hash FROM worm_signoff WHERE seq = ?")
    .get(ban.worm_seq) as { session_id: string; nguoi_dung_id: number | null; content_hash: string } | undefined;
  if (!dongWorm || dongWorm.session_id !== id || dongWorm.nguoi_dung_id !== uid || dongWorm.content_hash !== ban.content_hash) {
    return { duoc: false, lyDo: "Bản chụp ký không khớp sổ WORM — cần ký lại." };
  }

  let duLieu: Record<string, any>;
  try {
    duLieu = JSON.parse(ban.du_lieu);
  } catch {
    return { duoc: false, lyDo: "Bản chụp ký hỏng — cần ký lại." };
  }
  const tabId = ban.tab_id;
  const kqBan = tinhKyDuyetTuCa(duLieu, tabId);
  if (kqBan.contentHash !== ban.content_hash || kqBan.tabId !== tabId) {
    return { duoc: false, lyDo: "Bản chụp ký không khớp băm đã ký — cần ký lại." };
  }
  const kqHienTai = tinhKyDuyetTuCa(ca.duLieu, tabId);
  if (kqHienTai.tabId !== tabId || kqHienTai.contentHash !== ban.content_hash) {
    return { duoc: false, lyDo: "Hồ sơ đã sửa sau lần ký — cần ký lại." };
  }
  return { duoc: true, banKy: { wormSeq: ban.worm_seq, sessionId: id, tabId, contentHash: ban.content_hash, duLieu } };
}

/* ------------------------------------------------------------------ chặn trong route */

const chuoiKhac = (v: unknown) => (typeof v === "string" ? v.trim() : "");

/**
 * Chốt chung cho route xuất. Trả bản chụp đã ký, hoặc `null` khi đã trả lời lỗi:
 *  - 422 `lech_ma_ca`: `sessionId` và `caseId` cùng gửi mà khác nhau;
 *  - 409 `chua_ky_duyet`: chưa ký / sửa sau ký / chữ ký không kiểm được;
 *  - 422 `lech_tab_da_ky`: xin xuất tab khác tab đã ký.
 */
export function layBanKyDeXuat(req: express.Request, res: express.Response): BanKyDuyet | null {
  const body = req.body && typeof req.body === "object" ? (req.body as Record<string, unknown>) : {};
  const q = (req.query || {}) as Record<string, unknown>;
  const sessionId = chuoiKhac(body.sessionId) || chuoiKhac(q.sessionId);
  const caseId = chuoiKhac(body.caseId) || chuoiKhac(q.caseId);
  if (sessionId && caseId && sessionId !== caseId) {
    res.status(422).json({ error: "sessionId và caseId chỉ hai ca khác nhau — không xuất.", code: "lech_ma_ca" });
    return null;
  }
  const uid = (req as express.Request & { nguoiDung?: { id?: number } }).nguoiDung?.id;
  const kq = kiemDaKyChoXuat(typeof uid === "number" ? uid : NaN, (sessionId || caseId).slice(0, 200));
  if (!kq.duoc || !kq.banKy) {
    res.status(409).json({ error: LOI_CHUA_KY_DUYET, code: MA_LOI_CHUA_KY_DUYET, lyDo: kq.lyDo });
    return null;
  }
  const tabXin = chuoiKhac(body.tabId) || chuoiKhac(q.tabId);
  if (tabXin && tabXin !== kq.banKy.tabId) {
    res.status(422).json({ error: "Tab xin xuất không phải tab bác sĩ đã ký.", code: "lech_tab_da_ky" });
    return null;
  }
  return kq.banKy;
}

/* ------------------------------------------------------------------ dựng nội dung xuất từ bản đã ký */

/** Mệnh đề hiệu lực đúng như giao diện tính: bỏ mệnh đề "bỏ", mệnh đề "sửa" dùng bản sửa. */
function menhDeHieuLuc(ban: BanKyDuyet): Array<Record<string, any>> {
  const { quyet, banSua } = tinhKyDuyetTuCa(ban.duLieu, ban.tabId);
  const ds = Array.isArray(ban.duLieu?.note?.propositions) ? ban.duLieu.note.propositions : [];
  return ds
    .filter((p: any) => p && typeof p === "object" && quyet[Number(p.id)] !== "bo")
    .map((p: any) => {
      const sua = banSua[Number(p.id)];
      return quyet[Number(p.id)] === "sua" && sua?.trim() ? { ...p, text: sua.trim() } : p;
    });
}

/** Gói BHYT/FHIR dựng hoàn toàn từ bản đã ký. */
export function goiBhytTuBanKy(ban: BanKyDuyet) {
  const ca = ban.duLieu || {};
  const nc = xayNguCanhChoTaoHoSo({
    sessionId: ca.id,
    patientIdentifier: ca.patientIdentifier,
    patientSubtitle: ca.patientSubtitle,
    tabs: ca.tabs,
    contextNotes: ca.contextNotes,
  });
  return {
    propositions: menhDeHieuLuc(ban),
    transcript: String(ca.note?.transcript || ca.transcript || ""),
    thong_tin_benh_nhan: (nc.thong_tin_benh_nhan ?? null) as Record<string, unknown> | null,
    du_lieu_xet_nghiem: (nc.du_lieu_xet_nghiem ?? null) as Record<string, number> | null,
    noteSections: null,
  };
}

function chuanHoa(v: unknown): unknown {
  if (Array.isArray(v)) return v.map(chuanHoa);
  if (v && typeof v === "object") {
    const o: Record<string, unknown> = {};
    for (const k of Object.keys(v as object).sort()) {
      const x = (v as Record<string, unknown>)[k];
      if (x !== undefined) o[k] = chuanHoa(x);
    }
    return o;
  }
  return v;
}
const giongNhau = (a: unknown, b: unknown) =>
  JSON.stringify(chuanHoa(JSON.parse(JSON.stringify(a ?? null)))) === JSON.stringify(chuanHoa(JSON.parse(JSON.stringify(b ?? null))));

/**
 * Nội dung hồ sơ trình duyệt gửi kèm (nếu có) phải trùng khít bản đã ký; khác là trộn ca / sửa sau ký -> 422.
 * Trả `true` khi đã trả lời lỗi.
 */
export function chanNeuNoiDungKhacBanKy(req: express.Request, res: express.Response, goi: ReturnType<typeof goiBhytTuBanKy>) {
  const body = req.body && typeof req.body === "object" ? (req.body as Record<string, unknown>) : {};
  const doiChieu: Array<[string, unknown]> = [
    ["propositions", goi.propositions],
    ["transcript", goi.transcript],
    ["thong_tin_benh_nhan", goi.thong_tin_benh_nhan],
    ["patientInfo", goi.thong_tin_benh_nhan],
    ["du_lieu_xet_nghiem", goi.du_lieu_xet_nghiem],
    ["noteSections", goi.noteSections],
  ];
  const lech = doiChieu.filter(([k, v]) => body[k] !== undefined && body[k] !== null && !giongNhau(body[k], v)).map(([k]) => k);
  if (!lech.length) return false;
  res.status(422).json({
    error: "Nội dung gửi kèm khác bản bác sĩ đã ký (trộn ca hoặc đã sửa sau khi ký) — không xuất.",
    code: "noi_dung_khac_ban_ky",
    truongLech: lech,
  });
  return true;
}

/** Nội dung cổng người bệnh dựng từ bản đã ký: tên, chẩn đoán và thuốc lấy từ đúng tab đã ký. */
export function goiCongTuBanKy(ban: BanKyDuyet): { tenBenhNhan: string; chanDoan: string; thuoc: string[] } {
  const ca = ban.duLieu || {};
  const { soapRaw } = tinhKyDuyetTuCa(ca, ban.tabId);
  const trich = trichChanDoanVaThuocTuSoap(soapRaw);
  const hieuLuc = menhDeHieuLuc(ban).filter((p) => !p.negated && typeof p.text === "string" && p.text.trim());
  const sec = (p: Record<string, any>) => String(p.section || "").toUpperCase();
  const chanDoan =
    trich.chanDoan ||
    hieuLuc.find((p) => ["CHẨN ĐOÁN", "ĐÁNH GIÁ"].includes(sec(p)))?.text ||
    "";
  const thuoc = trich.thuoc.length
    ? trich.thuoc
    : hieuLuc
        .filter((p) => p.drug || ["ĐƠN THUỐC", "THUỐC ĐANG DÙNG", "KẾ HOẠCH ĐIỀU TRỊ"].includes(sec(p)))
        .map((p) => String(p.text).trim());
  const ten = typeof ca.patientIdentifier === "string" ? ca.patientIdentifier.trim() : "";
  return { tenBenhNhan: ten || "Quý khách / Người bệnh", chanDoan: String(chanDoan).trim(), thuoc };
}

/* ------------------------------------------------------------------ giao diện cũ (route khác đang dùng) */

/** Lấy mã ca từ thân yêu cầu hoặc query theo thứ tự trường (mặc định `sessionId`, rồi `caseId`). */
export function layMaCaTuYeuCau(req: express.Request, ...truong: string[]): string {
  const body = req.body && typeof req.body === "object" ? (req.body as Record<string, unknown>) : {};
  const q = (req.query || {}) as Record<string, unknown>;
  for (const k of truong.length ? truong : ["sessionId", "caseId"]) {
    const v = chuoiKhac(body[k]) || chuoiKhac(q[k]);
    if (v) return v.slice(0, 200);
  }
  return "";
}

/**
 * Chỉ kiểm chữ ký (409 khi chưa ký / sửa sau ký); KHÔNG ràng nội dung xuất vào bản đã ký.
 * Route nào xuất nội dung hồ sơ ra ngoài phải dùng `layBanKyDeXuat` + dựng nội dung từ bản chụp.
 */
export function chanNeuChuaKy(req: express.Request, res: express.Response, caseId: string): boolean {
  const uid = (req as express.Request & { nguoiDung?: { id?: number } }).nguoiDung?.id;
  const kq = kiemDaKyChoXuat(typeof uid === "number" ? uid : NaN, caseId);
  if (kq.duoc) return false;
  res.status(409).json({ error: LOI_CHUA_KY_DUYET, code: MA_LOI_CHUA_KY_DUYET, lyDo: kq.lyDo });
  return true;
}
