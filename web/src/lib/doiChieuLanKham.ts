import type { Session } from "../types";
import type { Proposition } from "../components/VerificationView";

export interface CanhBaoMauThuanLanKham {
  id: string;
  mucDo: "khan_cap" | "canh_bao";
  loai: "di_ung" | "benh_nen_thuoc";
  tieuDe: string;
  chiTiet: string;
  ngayKhamTruoc: string;
  trichDanCu: string;
  trichDanMoi: string;
}

const THUOC_VA_BENH_QUAN_TRONG = [
  "amoxicillin", "penicillin", "augmentin", "cefixim", "aspirin", "nsaid",
  "đái tháo đường", "tiểu đường", "tăng huyết áp", "cao huyết áp", "hen phế quản",
  "suy thận", "suy tim", "metformin", "insulin", "amlodipin", "losartan", "warfarin",
];

/**
 * Phát hiện mâu thuẫn xuyên lần khám giữa ca hiện tại và các ca trước của cùng bệnh nhân.
 * Tập trung vào 2 nhóm nguy hiểm cao: (1) Phủ định dị ứng đã ghi nhận trước đó,
 * (2) Phủ định bệnh nền / thuốc mạn tính đang điều trị trước đó.
 */
export function phatHienMauThuanXuyenLanKham(
  caHienTai: Pick<Session, "id" | "patientIdentifier" | "note">,
  tatCaCacCa: Session[]
): CanhBaoMauThuanLanKham[] {
  const maBn = (caHienTai.patientIdentifier || "").trim().toLowerCase();
  const mdMoi = caHienTai.note?.propositions || [];
  if (!maBn || mdMoi.length === 0) return [];

  const cacCaTruoc = tatCaCacCa.filter(
    (s) =>
      s.id !== caHienTai.id &&
      (s.patientIdentifier || "").trim().toLowerCase() === maBn &&
      (s.note?.propositions?.length || 0) > 0
  );
  if (cacCaTruoc.length === 0) return [];

  const locHieuLuc = (ca: Session): Proposition[] => {
    const q = ca.duyet?.quyet || {};
    const bs = ca.duyet?.banSua || {};
    return (ca.note?.propositions || [])
      .filter((p) => q[p.id] !== "bo")
      .map((p) => ({
        ...p,
        text: q[p.id] === "sua" && bs[p.id] ? bs[p.id] : p.text,
      }));
  };

  const canhBao: CanhBaoMauThuanLanKham[] = [];
  const daCoId = new Set<string>();
  const PHU_DINH_DI_UNG_RE = /(?<![\p{L}\p{N}_])(không|chưa\s+từng|không\s+có\s+tiền\s+sử)\s+dị\s+ứng(?![\p{L}\p{N}_])/iu;

  // 1. Kiểm tra mâu thuẫn Dị ứng: Lần trước khẳng định dị ứng (và không có đính chính phủ định sau đó), lần này phủ định
  const mdPhuDinhDiUngMoi = mdMoi.find(
    (p) =>
      p.negated &&
      ((p.section || "").toUpperCase().includes("DỊ ỨNG") || /\bdị ứng\b/i.test(p.text || ""))
  );
  if (mdPhuDinhDiUngMoi) {
    for (const caCu of cacCaTruoc) {
      const dsCu = locHieuLuc(caCu).filter(
        (p) => (p.section || "").toUpperCase().includes("DỊ ỨNG") || /\bdị ứng\b/i.test(p.text || "")
      );
      if (dsCu.length === 0) continue;
      // Nếu mệnh đề dị ứng cuối cùng trong ca cũ đã đính chính là không dị ứng -> bỏ qua
      const cuoiCu = dsCu[dsCu.length - 1];
      if (cuoiCu.negated || PHU_DINH_DI_UNG_RE.test(cuoiCu.text || "")) continue;
      const mdDiUngCu = dsCu.find(
        (p) => !p.negated && !PHU_DINH_DI_UNG_RE.test(p.text || "")
      );
      if (mdDiUngCu) {
        const key = `di_ung_${caCu.id}_${mdDiUngCu.id}`;
        if (!daCoId.has(key)) {
          daCoId.add(key);
          canhBao.push({
            id: key,
            mucDo: "khan_cap",
            loai: "di_ung",
            tieuDe: "Mâu thuẫn DỊ ỨNG so với lần khám trước",
            chiTiet: `Hồ sơ ngày ${caCu.date} từng ghi nhận dị ứng, nhưng hôm nay người bệnh nói không dị ứng.`,
            ngayKhamTruoc: caCu.date,
            trichDanCu: mdDiUngCu.quotes?.[0] || mdDiUngCu.text,
            trichDanMoi: mdPhuDinhDiUngMoi.quotes?.[0] || mdPhuDinhDiUngMoi.text,
          });
        }
      }
    }
  }

  // 2. Kiểm tra mâu thuẫn Bệnh nền / Thuốc mạn tính: Lần trước khẳng định, lần này phủ định cùng từ khóa
  const mdPhuDinhMoi: Proposition[] = mdMoi.filter((p) => p.negated);
  for (const pMoi of mdPhuDinhMoi) {
    const chuMoi = (pMoi.text || "").toLowerCase();
    for (const kw of THUOC_VA_BENH_QUAN_TRONG) {
      if (!chuMoi.includes(kw)) continue;
      for (const caCu of cacCaTruoc) {
        const pCu = locHieuLuc(caCu).find(
          (x) => !x.negated && (x.text || "").toLowerCase().includes(kw)
        );
        if (pCu) {
          const key = `benh_${kw}_${caCu.id}`;
          if (!daCoId.has(key)) {
            daCoId.add(key);
            canhBao.push({
              id: key,
              mucDo: "canh_bao",
              loai: "benh_nen_thuoc",
              tieuDe: `Mâu thuẫn tiền sử/thuốc "${kw}"`,
              chiTiet: `Lần khám ${caCu.date} có ghi nhận "${kw}", nhưng lần này phủ định.`,
              ngayKhamTruoc: caCu.date,
              trichDanCu: pCu.quotes?.[0] || pCu.text,
              trichDanMoi: pMoi.quotes?.[0] || pMoi.text,
            });
          }
        }
      }
    }
  }

  return canhBao;
}
