/**
 * Trả lời "nên hỏi thêm bệnh nhân những gì?" bằng dữ liệu của CA ĐANG MỞ, không qua tra cứu tài liệu.
 *
 * Nguồn (đều thuộc ca đang mở):
 *  - câu hỏi làm rõ do bộ luật sinh khi tạo bản nháp (`noteMeta.questions`);
 *  - gợi ý "Nên hỏi thêm" bám lời thoại (`clinicalSafety.tro_ly_socrates`), kèm số lượt làm căn cứ;
 *  - các mục hồ sơ chưa có mệnh đề nào.
 */

const MAU_HOI_THEM = /(nên|cần|phải)\s+hỏi(\s+thêm)?|hỏi\s+thêm|hỏi\s+gì|câu\s+hỏi\s+(nào|gì)/iu;

export function laCauHoiNenHoiThem(cau: string): boolean {
  return MAU_HOI_THEM.test((cau || "").normalize("NFC"));
}

function chuanHoa(s: string): string {
  return (s || "").normalize("NFC").toLowerCase().replace(/[“”"…]/g, "").replace(/\s+/g, " ").trim();
}

/**
 * Chỉ giữ gợi ý có căn cứ nằm trong lời thoại của CA ĐANG MỞ (hoặc căn cứ là hồ sơ).
 * Gợi ý cũ không có `trich_dan` (bộ gợi ý trước 28/11 dò từ khoá bừa) hay căn cứ không còn
 * trong lời thoại hiện tại đều bị bỏ, để không hiện câu hỏi không liên quan tới ca.
 */
export function locGoiYBamLoiThoai<T>(goiY: T[] | null | undefined, loiThoai: string): T[] {
  const lt = chuanHoa(loiThoai);
  return (goiY || []).filter((g) => {
    const o = (g || {}) as Record<string, unknown>;
    if (o.nguon === "hồ sơ") return true;
    const trich = chuanHoa(typeof o.trich_dan === "string" ? o.trich_dan : "");
    return trich.length > 0 && lt.includes(trich);
  });
}

const MUC_CHINH: ReadonlyArray<[string, string]> = [
  ["LÝ DO KHÁM BỆNH", "Lý do khám"],
  ["BỆNH SỬ HIỆN TẠI", "Bệnh sử hiện tại"],
  ["TIỀN SỬ BỆNH", "Tiền sử bệnh"],
  ["THUỐC ĐANG DÙNG", "Thuốc đang dùng"],
  ["DỊ ỨNG", "Dị ứng"],
  ["TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI", "Tiền sử gia đình và xã hội"],
  ["KHÁM LÂM SÀNG", "Khám lâm sàng"],
];

export interface DuLieuCaNenHoiThem {
  cauHoiLamRo?: unknown[] | null;
  goiYSocrates?: unknown[] | null;
  menhDe?: Array<{ section?: string | null }> | null;
}

export interface KetQuaNenHoiThem {
  noiDung: string;
  soCau: number;
}

function chuoi(x: unknown): string {
  if (typeof x === "string") return x.trim();
  if (x && typeof x === "object") {
    const o = x as Record<string, unknown>;
    return String(o.van ?? o.hoi ?? o.text ?? o.cau_hoi ?? "").trim();
  }
  return "";
}

export function soanCauNenHoiThem(du: DuLieuCaNenHoiThem): KetQuaNenHoiThem {
  const dong: string[] = [];
  const daCo = new Set<string>();
  let soCau = 0;

  const lamRo = (du.cauHoiLamRo || []).map(chuoi).filter(Boolean);
  if (lamRo.length) {
    dong.push("**Làm rõ điều chưa chắc trong bản nháp**");
    for (const c of lamRo) {
      if (daCo.has(c)) continue;
      daCo.add(c);
      dong.push(`${++soCau}. ${c}`);
    }
  }

  const goiY = (du.goiYSocrates || []) as Array<Record<string, unknown>>;
  const dongGoiY: string[] = [];
  for (const g of goiY) {
    const c = chuoi(g?.cau_hoi_goi_y ?? g?.khoang_trong);
    if (!c || daCo.has(c)) continue;
    daCo.add(c);
    const luot = Array.isArray(g?.luot_dan) && g.luot_dan.length ? `T${(g.luot_dan as number[]).join(", T")}` : "";
    const trich = typeof g?.trich_dan === "string" && g.trich_dan ? `“${g.trich_dan}”` : "";
    const canCu = [luot, trich].filter(Boolean).join(" · ");
    dongGoiY.push(`${++soCau}. ${c}${canCu ? ` — _${canCu}_` : ""}`);
  }
  if (dongGoiY.length) {
    if (dong.length) dong.push("");
    dong.push("**Hỏi thêm từ lời bệnh nhân đã kể**", ...dongGoiY);
  }

  const coMuc = new Set((du.menhDe || []).map((m) => String(m?.section ?? "").toUpperCase()));
  const thieu = MUC_CHINH.filter(([ma]) => !coMuc.has(ma)).map(([, ten]) => ten);
  if (thieu.length && (du.menhDe || []).length) {
    if (dong.length) dong.push("");
    dong.push(`**Mục hồ sơ chưa có thông tin:** ${thieu.join(", ")}.`);
  }

  if (!dong.length) {
    dong.push(
      (du.menhDe || []).length
        ? "Ca này chưa thấy chỗ nào cần hỏi thêm."
        : "Ca này chưa có bản nháp. Tạo bản nháp từ lời thoại trước rồi hỏi lại.",
    );
  }
  return { noiDung: dong.join("\n"), soCau };
}
