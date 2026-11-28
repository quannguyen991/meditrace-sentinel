/**
 * Ngân sách cảnh báo (Task 5 plan 27/11, V11 plan 28/11).
 *
 * Dịch vụ Python trả mỗi mệnh đề `canh_bao_hien` (tối đa 2, nhưng cảnh báo mức cao / lỗi phát hiện
 * luôn có mặt) và `canh_bao_gap` (phần gập sau nút "Xem thêm N gợi ý"); cả ca có
 * `toan_ca_ngan_sach`. Lớp BFF đổi sang dạng giao diện thành `warningsShown` / `warningsFolded`
 * và `caseWarningsShown` / `caseWarningsFolded`. Thiếu trường thì giữ nguyên cách hiển thị cũ.
 */

export interface CanhBaoToiThieu {
  code: string;
  severity: "cao" | "trung" | "thap";
  kind: "loi_phat_hien" | "nghi_rui_ro" | "can_xem";
}

export interface MenhDeCoCanhBao<C extends CanhBaoToiThieu> {
  warning?: C | null;
  otherWarnings?: C[];
  warningsShown?: C[];
  warningsFolded?: C[];
}

export interface ChiaCanhBao<C> {
  /** true khi API có trường ngân sách; false = hiển thị theo cách cũ. */
  coNganSach: boolean;
  /** Cảnh báo dựng thành thẻ chính của dòng. */
  chinh: C | null;
  /** Cảnh báo hiện ngay dưới thẻ chính (trong ngân sách). */
  hienThem: C[];
  /** Cảnh báo gập: cách cũ = "dấu hiệu khác", cách mới = "gợi ý". */
  gap: C[];
}

/** Chia cảnh báo của một mệnh đề. Cách cũ: chính = `warning`, gập = `otherWarnings`. */
export function chiaCanhBaoMenhDe<C extends CanhBaoToiThieu>(p: MenhDeCoCanhBao<C>): ChiaCanhBao<C> {
  if (!Array.isArray(p.warningsShown)) {
    return { coNganSach: false, chinh: p.warning || null, hienThem: [], gap: p.otherWarnings || [] };
  }
  const hien = p.warningsShown;
  return { coNganSach: true, chinh: hien[0] || null, hienThem: hien.slice(1), gap: p.warningsFolded || [] };
}

/** Cảnh báo toàn ca (bỏ sót). Cách cũ: hiện hết `caseWarnings`, không gập. */
export function chiaCanhBaoCa<C>(note: {
  caseWarnings?: C[];
  caseWarningsShown?: C[];
  caseWarningsFolded?: C[];
}): { coNganSach: boolean; hien: C[]; gap: C[] } {
  if (!Array.isArray(note.caseWarningsShown)) {
    return { coNganSach: false, hien: note.caseWarnings || [], gap: [] };
  }
  return { coNganSach: true, hien: note.caseWarningsShown, gap: note.caseWarningsFolded || [] };
}

/** Nhãn nút mở phần gập. */
export function nhanXemThem(n: number, dangMo: boolean): string {
  return dangMo ? `Ẩn ${n} gợi ý` : `Xem thêm ${n} gợi ý`;
}
