import type { TranscriptSegment } from "../types";
import type { Proposition } from "../components/VerificationView";

const SO_LIEU_RE = /\d+(?:[.,]\d+)?\s*(?:mg|ml|mcg|g|kg|ui|%|lần\/ngày|viên|gói|mmhg|l\/p|độ)/i;
const PHU_DINH_RE = /(?<![\p{L}\p{N}_])(không|chưa|ngừng|dừng|chẳng|hết)(?![\p{L}\p{N}_])/iu;

export interface CanhBaoAsr {
  coSoLieu: boolean;
  coPhuDinh: boolean;
  doTinCayThap: boolean;
  nhan: string | null;
}

/** Phát hiện mệnh đề chứa số/liều thuốc, từ phủ định hoặc nằm trên đoạn ASR độ tin cậy thấp. */
export function phanTichVungMoAsr(
  p: Pick<Proposition, "text" | "negated" | "evidenceTurns">,
  segments?: TranscriptSegment[]
): CanhBaoAsr {
  const coSoLieu = SO_LIEU_RE.test(p.text || "");
  const coPhuDinh = Boolean(p.negated) || PHU_DINH_RE.test(p.text || "");
  const doTinCayThap = Boolean(
    segments?.some((s) => p.evidenceTurns.includes(s.luot) && s.lowConf)
  );

  const lyDo: string[] = [];
  if (doTinCayThap) lyDo.push("ASR mờ");
  if (coSoLieu) lyDo.push("số/liều");
  if (coPhuDinh) lyDo.push("phủ định");

  return {
    coSoLieu,
    coPhuDinh,
    doTinCayThap,
    nhan: lyDo.length > 0 ? `Cần nghe kỹ (${lyDo.join(" · ")})` : null,
  };
}

/** Lấy khoảng thời gian phát lại [batDau, ketThuc] (thêm đệm 0.5s mỗi đầu) cho 1 lượt thoại. */
export function khoangPhatLaiLuot(
  luot: number,
  segments?: TranscriptSegment[]
): { start_s: number; end_s: number } | null {
  if (!segments || segments.length === 0) return null;
  const seg = segments.find((s) => s.luot === luot);
  if (!seg || !Number.isFinite(seg.start_s) || !Number.isFinite(seg.end_s)) return null;
  if (seg.end_s <= seg.start_s) return null;
  return {
    start_s: Math.max(0, Number((seg.start_s - 0.5).toFixed(2))),
    end_s: Number((seg.end_s + 0.5).toFixed(2)),
  };
}
