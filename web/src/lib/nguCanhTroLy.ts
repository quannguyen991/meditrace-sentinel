import type { Patient } from "../types";
import type { Proposition } from "../components/VerificationView";

export interface NguCanhAnDanhGuiDi {
  tuoi?: number;
  gioi?: "nam" | "nữ";
  coThai?: boolean;
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
