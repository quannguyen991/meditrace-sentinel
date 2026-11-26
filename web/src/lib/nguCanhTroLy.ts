import type { DocumentTabItem, Patient } from "../types";
import type { Proposition } from "../components/VerificationView";

export interface NguCanhAnDanhGuiDi {
  tuoi?: number;
  gioi?: "nam" | "nữ";
  coThai?: boolean;
}

export interface NguCanhTaoHoSoPayload {
  context?: string;
  thong_tin_benh_nhan?: Record<string, unknown>;
  du_lieu_xet_nghiem?: Record<string, number>;
}

/** Trích tuổi, giới và trạng thái thai kỳ có cấu trúc từ hồ sơ bệnh nhân, ngữ cảnh và mệnh đề (không gửi ngày sinh/tên). */
export function trichNguCanhChoTroLy(params: {
  patient?: Patient | null;
  patientSubtitle?: string;
  contextNotes?: string;
  propositions?: Proposition[];
}): NguCanhAnDanhGuiDi {
  const kq: NguCanhAnDanhGuiDi = {};
  const namHienTai = new Date().getFullYear();

  // 1. Tuổi
  if (params.patient?.dob) {
    const mNam = params.patient.dob.match(/(19\d{2}|20\d{2})/);
    if (mNam) {
      const tuoi = namHienTai - Number(mNam[1]);
      if (tuoi >= 0 && tuoi <= 120) kq.tuoi = tuoi;
    }
  }
  if (kq.tuoi === undefined) {
    const gop = `${params.patientSubtitle || ""} ${params.contextNotes || ""}`;
    const mTuoi = gop.match(/\b(\d{1,3})\s*tuổi\b/i);
    if (mTuoi) {
      const t = Number(mTuoi[1]);
      if (t >= 0 && t <= 120) kq.tuoi = t;
    } else {
      const mNamSinhNhan = gop.match(
        /(?:ngày\s*sinh|năm\s*sinh|sinh\s*năm|dob)\s*[:=\-]?\s*(?:\d{1,2}[\/.\-]\d{1,2}[\/.\-])?(19\d{2}|20\d{2})\b/iu,
      );
      const mSubtitleDob = (params.patientSubtitle || "").match(/\b\d{1,2}[\/.\-]\d{1,2}[\/.\-](19\d{2}|20\d{2})\b/);
      const namStr = mNamSinhNhan?.[1] || mSubtitleDob?.[1];
      if (namStr) {
        const t = namHienTai - Number(namStr);
        if (t >= 0 && t <= 120) kq.tuoi = t;
      }
    }
  }

  // 2. Giới tính (dùng ranh giới Unicode tiếng Việt vì \b không nhận chữ có dấu)
  const gText = `${params.patient?.gender || ""} ${params.patientSubtitle || ""} ${params.contextNotes || ""}`.toLowerCase();
  if (/(?<![\p{L}\p{N}_])(nữ|female)(?![\p{L}\p{N}_])/iu.test(gText)) kq.gioi = "nữ";
  else if (/(?<![\p{L}\p{N}_])(nam|male)(?![\p{L}\p{N}_])/iu.test(gText)) kq.gioi = "nam";

  // 3. Có thai (chỉ xác nhận khi không phải nam và có mệnh đề/ngữ cảnh khẳng định, loại trừ phủ định)
  if (kq.gioi !== "nam") {
    const THAI_RE = /(?<![\p{L}\p{N}_])(mang thai|có thai|thai kỳ|đang bầu)(?![\p{L}\p{N}_])/iu;
    const PHU_DINH_THAI_RE = /(?<![\p{L}\p{N}_])(không|chưa\s+từng|ngừng|test\s+thai\s+âm\s+tính)(?![\p{L}\p{N}_])/iu;
    const coThaiTrongMd = params.propositions?.some((p) => {
      const txt = p.text || "";
      return !p.negated && THAI_RE.test(txt) && !PHU_DINH_THAI_RE.test(txt);
    });
    const nc = params.contextNotes || "";
    const coThaiTrongNc = THAI_RE.test(nc) && !PHU_DINH_THAI_RE.test(nc);
    if (coThaiTrongMd || coThaiTrongNc) kq.coThai = true;
  }

  return kq;
}

function laySoFloat(re: RegExp, vanBan: string): number | undefined {
  const m = vanBan.match(re);
  if (!m) return undefined;
  const n = Number(m[1].replace(",", "."));
  return Number.isFinite(n) ? n : undefined;
}

/**
 * Gom dữ liệu từ `patientIdentifier`, `patientSubtitle` và tab `context` (`ContextView`)
 * để gửi kèm lên `/api/generate-note`. Tuyệt đối KHÔNG bịa tuổi/giới mặc định nếu bác sĩ chưa nhập.
 */
export function xayNguCanhChoTaoHoSo(params: {
  sessionId?: string;
  patientIdentifier?: string;
  patientSubtitle?: string;
  tabs?: DocumentTabItem[];
  contextNotes?: string;
}): NguCanhTaoHoSoPayload {
  const coTabNguCanh = Boolean(params.tabs?.some((t) => t.type === "context"));
  const contextTab = params.tabs?.find((t) => t.type === "context")?.content || "";
  const contextText = coTabNguCanh ? contextTab.trim() : (params.contextNotes || "").trim();
  const subtitle = (params.patientSubtitle || "").trim();
  const nc = trichNguCanhChoTroLy({
    patientSubtitle: subtitle,
    contextNotes: contextText,
  });

  const gop = `${subtitle}\n${contextText}`;
  const canNang = laySoFloat(/(?:cân\s*nặng|cn|weight)?\s*[:=]?\s*(\d{1,3}(?:[.,]\d+)?)\s*kg\b/i, gop);

  const duLieuXn: Record<string, number> = {};
  const mCreat = gop.match(/(?:creatinin[e]?|scr)(?:_umol_l|_mg_dl)?\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)\s*(µmol\/l|umol\/l|mg\/dl)?/i);
  if (mCreat) {
    const val = Number(mCreat[1].replace(",", "."));
    const dv = (mCreat[2] || "").toLowerCase();
    if (Number.isFinite(val) && val > 0) {
      if (dv === "mg/dl" || (!dv && val < 15)) {
        duLieuXn.creatinine_mg_dl = val;
        duLieuXn.creatinine = val;
      } else {
        duLieuXn.creatinine_umol_l = val;
      }
    }
  }
  const egfr = laySoFloat(/(?:egfr|mlct)\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)/i, gop);
  if (egfr !== undefined) duLieuXn.egfr = egfr;
  const hba1c = laySoFloat(/hba1c\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)/i, gop);
  if (hba1c !== undefined) duLieuXn.hba1c = hba1c;
  const glu = laySoFloat(/(?:glucose|đường\s*huyết)(?:_mmol_l)?\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)/i, gop);
  if (glu !== undefined) duLieuXn.glucose_mmol_l = glu;

  const ten = (params.patientIdentifier || "").trim();
  const coTenThat = Boolean(ten && !/^thêm\s+(?:tên\s+)?định\s+danh/i.test(ten));

  const ttBn: Record<string, unknown> = {};
  if (params.sessionId) ttBn.id = params.sessionId;
  if (coTenThat) {
    ttBn.ho_ten = ten;
    ttBn.ten = ten;
  }
  if (nc.tuoi !== undefined) ttBn.tuoi = nc.tuoi;
  if (nc.gioi !== undefined) {
    ttBn.gioi_tinh = nc.gioi;
    ttBn.la_nu = nc.gioi === "nữ";
  }
  if (nc.coThai) ttBn.co_thai = true;
  if (canNang !== undefined && canNang > 0 && canNang <= 300) ttBn.can_nang_kg = canNang;
  if (contextText) ttBn.ngu_canh = contextText;
  if (subtitle && subtitle !== "Ca khám bệnh mới") ttBn.mo_ta_ca = subtitle;

  const kq: NguCanhTaoHoSoPayload = {};
  if (contextText) kq.context = contextText;
  if (Object.keys(ttBn).length > 0) kq.thong_tin_benh_nhan = ttBn;
  if (Object.keys(duLieuXn).length > 0) kq.du_lieu_xet_nghiem = duLieuXn;
  return kq;
}
