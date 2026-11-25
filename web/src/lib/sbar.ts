import type { Proposition, Quyet } from "../components/VerificationView";

export interface PhieuSbar {
  situation: string[];
  background: string[];
  assessment: string[];
  recommendation: string[];
  vanBan: string;
}

export interface MucHis {
  nhan: string;
  noiDung: string;
}

function locMenhDeHieuLuc(
  propositions: Proposition[],
  quyet: Record<number, Quyet>,
  banSua: Record<number, string>
): Array<{ section: string; text: string; negated?: boolean }> {
  return propositions
    .filter((p) => quyet[p.id] !== "bo")
    .map((p) => ({
      section: (p.section || "").toUpperCase(),
      text: (quyet[p.id] === "sua" && banSua[p.id] ? banSua[p.id] : p.text || "").trim(),
      negated: p.negated,
    }))
    .filter((x) => x.text.length > 0);
}

/** Tổng hợp phiếu bàn giao SBAR chuẩn lâm sàng từ các mệnh đề đã duyệt (bỏ qua mục bác sĩ đánh dấu "Bỏ"). */
export function taoPhieuSbar(
  propositions: Proposition[],
  quyet: Record<number, Quyet>,
  banSua: Record<number, string>,
  patientIdentifier = ""
): PhieuSbar {
  const ds = locMenhDeHieuLuc(propositions, quyet, banSua);
  const situation: string[] = [];
  const background: string[] = [];
  const assessment: string[] = [];
  const recommendation: string[] = [];

  for (const m of ds) {
    if (m.section.includes("LÝ DO") || m.section.includes("BỆNH SỬ")) {
      situation.push(m.text);
    } else if (m.section.includes("TIỀN SỬ") || m.section.includes("DỊ ỨNG") || (m.section.includes("THUỐC") && !m.section.includes("ĐƠN THUỐC"))) {
      background.push(m.text);
    } else if (
      m.section.includes("KHÁM") ||
      m.section.includes("CHẨN ĐOÁN") ||
      m.section.includes("CẬN LÂM SÀNG") ||
      m.section.includes("TÓM TẮT")
    ) {
      assessment.push(m.text);
    } else {
      recommendation.push(m.text);
    }
  }

  const dong = (tieuDe: string, muc: string[]) =>
    `${tieuDe}:\n${muc.length > 0 ? muc.map((x) => `- ${x}`).join("\n") : "- (Chưa ghi nhận)"}`;

  const dau = patientIdentifier ? `PHIẾU BÀN GIAO SBAR — ${patientIdentifier}\n` : "PHIẾU BÀN GIAO SBAR\n";
  const vanBan = [
    dau.trimEnd(),
    dong("S - Tình trạng hiện tại (Situation)", situation),
    dong("B - Tiền sử & Thuốc/Dị ứng (Background)", background),
    dong("A - Đánh giá & Chẩn đoán (Assessment)", assessment),
    dong("R - Đề xuất & Kế hoạch (Recommendation)", recommendation),
  ].join("\n\n");

  return { situation, background, assessment, recommendation, vanBan };
}

/** Tách bệnh án thành từng ô chuẩn HIS Việt Nam (VNPT-HIS, Viettel HIS, FPT.eHospital) để dán 1-click. */
export function tachMucHis(
  propositions: Proposition[],
  quyet: Record<number, Quyet>,
  banSua: Record<number, string>
): MucHis[] {
  const ds = locMenhDeHieuLuc(propositions, quyet, banSua);
  const nhom: Array<{ nhan: string; khop: (sec: string) => boolean }> = [
    { nhan: "Lý do vào viện", khop: (s) => s.includes("LÝ DO") },
    { nhan: "Bệnh sử", khop: (s) => s.includes("BỆNH SỬ") },
    { nhan: "Tiền sử & Dị ứng", khop: (s) => s.includes("TIỀN SỬ") || s.includes("DỊ ỨNG") || s.includes("THUỐC ĐANG DÙNG") },
    { nhan: "Khám lâm sàng", khop: (s) => s.includes("KHÁM LÂM SÀNG") || s.includes("KHÁM THỰC THỂ") || s.includes("CẬN LÂM SÀNG") },
    { nhan: "Chẩn đoán", khop: (s) => s.includes("CHẨN ĐOÁN") || s.includes("TÓM TẮT") },
    { nhan: "Hướng xử trí & Đơn thuốc", khop: (s) => s.includes("KẾ HOẠCH") || s.includes("ĐIỀU TRỊ") || s.includes("DẶN") || s.includes("ĐƠN THUỐC") || s.includes("THUỐC") },
  ];

  return nhom.map((n) => {
    const items = ds.filter((m) => n.khop(m.section)).map((m) => m.text);
    return {
      nhan: n.nhan,
      noiDung: items.join("; "),
    };
  });
}
