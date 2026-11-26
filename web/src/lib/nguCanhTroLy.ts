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

  // 1. Tuổi (hỗ trợ cả trẻ nhũ nhi/trẻ nhỏ tính theo tháng tuổi)
  if (params.patient?.dob) {
    const mNam = params.patient.dob.match(/(19\d{2}|20\d{2})/);
    if (mNam) {
      const tuoi = namHienTai - Number(mNam[1]);
      if (tuoi >= 0 && tuoi <= 120) kq.tuoi = tuoi;
    }
  }
  if (kq.tuoi === undefined) {
    const gop = `${params.patientSubtitle || ""} ${params.contextNotes || ""}`;
    const mThang = gop.match(/(?<![\p{L}\p{N}_])(\d{1,2})\s*tháng\s*tuổi(?![\p{L}\p{N}_])/iu);
    const mTuoi = gop.match(/\b(\d{1,3})\s*tuổi\b/i);
    if (mThang && Number(mThang[1]) >= 0 && Number(mThang[1]) < 72) {
      kq.tuoi = Math.floor(Number(mThang[1]) / 12);
    } else if (mTuoi) {
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
  if (/(?<![\p{L}\p{N}_])(nữ|female|bé\s*gái)(?![\p{L}\p{N}_])/iu.test(gText)) kq.gioi = "nữ";
  else if (/(?<![\p{L}\p{N}_])(nam|male|bé\s*trai)(?![\p{L}\p{N}_])/iu.test(gText)) kq.gioi = "nam";

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
 * Boost 9B: Bóc tách đầy đủ 14 chỉ số xét nghiệm trọng yếu (Kali, Na, Troponin, WBC, Hb, PLT, Urea,
 * AST, ALT, CRP, INR, Creatinine, eGFR, HbA1c, Glucose) + tháng tuổi & chiều cao Nhi khoa.
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
  const canNang = laySoFloat(/(?:cân\s*nặng|cn|weight)?\s*[:=]?\s*(\d{1,3}(?:[.,]\d+)?)\s*kg\b/iu, gop);
  const chieuCao = laySoFloat(/(?<![\p{L}\p{N}_])(?:chiều\s*cao|cao)\s*[:=]?\s*(\d{2,3}(?:[.,]\d+)?)\s*cm\b/iu, gop);
  const mThangTuoi = gop.match(/(?<![\p{L}\p{N}_])(\d{1,2})\s*tháng\s*tuổi(?![\p{L}\p{N}_])/iu);
  const thangTuoi = mThangTuoi ? Number(mThangTuoi[1]) : undefined;

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

  const egfr = laySoFloat(/(?<![\p{L}\p{N}_])(?:egfr|mlct)(?![\p{L}\p{N}_])\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)/iu, gop);
  if (egfr !== undefined) duLieuXn.egfr = egfr;

  const hba1c = laySoFloat(/(?<![\p{L}\p{N}_])hba1c(?![\p{L}\p{N}_])\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)/iu, gop);
  if (hba1c !== undefined) duLieuXn.hba1c = hba1c;

  const glu = laySoFloat(/(?<![\p{L}\p{N}_])(?:glucose|đường\s*huyết)(?:_mmol_l)?(?![\p{L}\p{N}_])\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)/iu, gop);
  if (glu !== undefined) duLieuXn.glucose_mmol_l = glu;

  const kali = laySoFloat(/(?<![\p{L}\p{N}_])(?:kali(?![\p{L}\p{N}_])|k\+)\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)/iu, gop);
  if (kali !== undefined) duLieuXn.kali = kali;

  const na = laySoFloat(/(?<![\p{L}\p{N}_])(?:natri(?![\p{L}\p{N}_])|na\+|na(?![\p{L}\p{N}_]))\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)/iu, gop);
  if (na !== undefined) duLieuXn.na = na;

  const troponin = laySoFloat(/(?<![\p{L}\p{N}_])troponin(?:\s*[ti])?(?![\p{L}\p{N}_])\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)/iu, gop);
  if (troponin !== undefined) duLieuXn.troponin = troponin;

  const wbc = laySoFloat(/(?<![\p{L}\p{N}_])(?:wbc|bạch\s*cầu)(?![\p{L}\p{N}_])\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)/iu, gop);
  if (wbc !== undefined) duLieuXn.wbc = wbc;

  const hb = laySoFloat(/(?<![\p{L}\p{N}_])(?:hb|hgb|hemoglobin|huyết\s*sắc\s*tố)(?![\p{L}\p{N}_])\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)/iu, gop);
  if (hb !== undefined) duLieuXn.hb = hb;

  const plt = laySoFloat(/(?<![\p{L}\p{N}_])(?:plt|tiểu\s*cầu)(?![\p{L}\p{N}_])\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)/iu, gop);
  if (plt !== undefined) duLieuXn.plt = plt;

  const urea = laySoFloat(/(?<![\p{L}\p{N}_])(?:urea|ure|bun)(?![\p{L}\p{N}_])\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)/iu, gop);
  if (urea !== undefined) duLieuXn.urea = urea;

  const ast = laySoFloat(/(?<![\p{L}\p{N}_])(?:ast|got)(?![\p{L}\p{N}_])\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)/iu, gop);
  if (ast !== undefined) duLieuXn.ast = ast;

  const alt = laySoFloat(/(?<![\p{L}\p{N}_])(?:alt|gpt)(?![\p{L}\p{N}_])\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)/iu, gop);
  if (alt !== undefined) duLieuXn.alt = alt;

  const crp = laySoFloat(/(?<![\p{L}\p{N}_])crp(?![\p{L}\p{N}_])\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)/iu, gop);
  if (crp !== undefined) duLieuXn.crp = crp;

  const inr = laySoFloat(/(?<![\p{L}\p{N}_])inr(?![\p{L}\p{N}_])\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)/iu, gop);
  if (inr !== undefined) duLieuXn.inr = inr;

  const ten = (params.patientIdentifier || "").trim();
  const coTenThat = Boolean(ten && !/^thêm\s+(?:tên\s+)?định\s+danh/i.test(ten));

  const ttBn: Record<string, unknown> = {};
  if (params.sessionId) ttBn.id = params.sessionId;
  if (coTenThat) {
    ttBn.ho_ten = ten;
    ttBn.ten = ten;
  }
  if (nc.tuoi !== undefined) ttBn.tuoi = nc.tuoi;
  if (thangTuoi !== undefined && Number.isFinite(thangTuoi) && thangTuoi >= 0) {
    ttBn.thang_tuoi = thangTuoi;
    if (thangTuoi < 72) {
      ttBn.tuoi = Math.floor(thangTuoi / 12);
    }
  }
  if (nc.gioi !== undefined) {
    ttBn.gioi_tinh = nc.gioi;
    ttBn.la_nu = nc.gioi === "nữ";
  }
  if (nc.coThai) ttBn.co_thai = true;
  if (canNang !== undefined && canNang > 0 && canNang <= 300) ttBn.can_nang_kg = canNang;
  if (chieuCao !== undefined && chieuCao > 0 && chieuCao <= 260) ttBn.chieu_cao_cm = chieuCao;
  if (contextText) ttBn.ngu_canh = contextText;
  if (subtitle && subtitle !== "Ca khám bệnh mới") ttBn.mo_ta_ca = subtitle;

  const kq: NguCanhTaoHoSoPayload = {};
  if (contextText) kq.context = contextText;
  if (Object.keys(ttBn).length > 0) kq.thong_tin_benh_nhan = ttBn;
  if (Object.keys(duLieuXn).length > 0) kq.du_lieu_xet_nghiem = duLieuXn;
  return kq;
}
