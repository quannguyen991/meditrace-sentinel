/**
 * Phần thuần của giao diện trợ lý nhiều tác tử (thử được bằng `tsx`, xem troLy.test.ts).
 * Máy chủ: POST /api/tro-ly → 200 (xong) hoặc 202 (còn chạy, hỏi lại GET /api/tro-ly/:id).
 */
import type { ClinicalChatMessage } from "../types";

export type BuocHienThi = { ten: string; trangThai: "cho" | "dang" | "xong" | "bo_qua" | "loi"; ghiChu?: string };
export type TheTienDo = {
  keHoach: Array<{ tacTu: string; nhiemVu: string }>;
  keHoachTuMoHinh: boolean;
  nhom: Array<{ tacTu: string; ten: string; buoc: BuocHienThi[] }>;
  xemTruoc: string | null;
};

export const TEN_TAC_TU: Record<string, string> = {
  dieu_phoi: "Điều phối",
  tim_kiem: "Tìm kiếm",
  tra_loi: "Trả lời",
  doi_chieu: "Đối chiếu",
  chu_de_can_ban: "Chủ đề cần bàn",
  doi_chieu_thuoc: "Đối chiếu thuốc và dị ứng",
};
const tenTacTu = (ma: string) => TEN_TAC_TU[ma] || ma;

/** Gom bước theo tác tử, giữ thứ tự xuất hiện; tác tử có trong kế hoạch mà chưa có bước vẫn hiện tên. */
export function taoTheTienDo(tt: { keHoach?: any[]; keHoachTuMoHinh?: boolean; buoc?: any[]; xemTruoc?: string | null } | null | undefined): TheTienDo {
  const keHoach = (tt?.keHoach ?? []).map((m) => ({ tacTu: String(m.tacTu), nhiemVu: String(m.nhiemVu ?? "") }));
  const nhom: TheTienDo["nhom"] = [];
  const them = (tacTu: string) => {
    let n = nhom.find((x) => x.tacTu === tacTu);
    if (!n) nhom.push((n = { tacTu, ten: tenTacTu(tacTu), buoc: [] }));
    return n;
  };
  for (const m of keHoach) them(m.tacTu);
  // Thứ tự nhóm theo bước (đã xếp theo kế hoạch lúc tạo); kế hoạch chưa có bước thì theo kế hoạch.
  const theoBuoc: string[] = [];
  for (const b of tt?.buoc ?? []) if (!theoBuoc.includes(b.tacTu)) theoBuoc.push(b.tacTu);
  if (theoBuoc.length) nhom.sort((a, b) => (theoBuoc.indexOf(a.tacTu) + 1 || 99) - (theoBuoc.indexOf(b.tacTu) + 1 || 99));
  for (const b of tt?.buoc ?? []) {
    them(String(b.tacTu)).buoc.push({
      ten: String(b.ten ?? ""),
      trangThai: b.trangThai,
      ...(b.ghiChu ? { ghiChu: String(b.ghiChu) } : {}),
    });
  }
  return { keHoach, keHoachTuMoHinh: !!tt?.keHoachTuMoHinh, nhom, xemTruoc: tt?.xemTruoc ?? null };
}

/** Chỉ giữ trường máy chủ cần; không gửi trích dẫn, lượt thoại, thời điểm. */
export function gonMenhDeGui(ds: any[] | null | undefined) {
  return (Array.isArray(ds) ? ds : []).map((m) => ({
    text: String(m?.text ?? ""),
    section: String(m?.section ?? ""),
    subject: m?.subject ?? null,
    negated: m?.negated === true,
    certainty: m?.certainty ?? null,
    drug: m?.drug ?? null,
  }));
}

export type KetQuaHoi =
  | { ketQua: any; tienTrinh?: any; source?: string; model?: string }
  | { loi: string; code?: string; lyDo?: string };

/** Gửi câu hỏi; còn chạy (202) thì hỏi lại mỗi `khoangMs` và gọi `dangCho(tienTrinh)` cho tới khi xong hoặc lỗi. */
export async function hoiTroLy(
  body: unknown,
  dangCho: (tienTrinh: any) => void,
  tuyChon: { fetchFn?: typeof fetch; khoangMs?: number; toiDaMs?: number } = {},
): Promise<KetQuaHoi> {
  const goi = tuyChon.fetchFn ?? fetch;
  const khoang = tuyChon.khoangMs ?? 1500;
  const han = Date.now() + (tuyChon.toiDaMs ?? 5 * 60_000);
  try {
    let res = await goi("/api/tro-ly", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    let d: any = await res.json().catch(() => ({}));
    for (;;) {
      if (res.status === 200) return { ketQua: d.ketQua, tienTrinh: d.tienTrinh, source: d.source, model: d.model };
      if (res.status !== 202) return { loi: d?.error || `Máy chủ trả mã ${res.status}`, code: d?.code, lyDo: d?.lyDo };
      dangCho(d.tienTrinh);
      if (!d.jobId) return { loi: "Máy chủ không trả mã việc" };
      if (Date.now() >= han) return { loi: "Trợ lý chạy quá lâu. Hãy hỏi lại." };
      await new Promise((r) => setTimeout(r, khoang));
      res = await goi(`/api/tro-ly/${d.jobId}`);
      d = await res.json().catch(() => ({}));
    }
  } catch (e: any) {
    return { loi: `Không gọi được trợ lý: ${e?.message || e}` };
  }
}

const TAC_TU_CAN_CANH_BAO_LEN_DAU = new Set(["tim_kiem", "tra_loi", "doi_chieu"]);

/** Kiểm tra thật xem tác tử `doi_chieu` có thực sự chạy xong trong kết quả/tiến trình hay không. */
export function kiemTraDoiChieuDaChay(
  ketQua: any,
  tienTrinh?: any,
): { daQuaDoiChieu: boolean; coLuuYCanCu: boolean } {
  const phan: any[] = Array.isArray(ketQua?.phan) ? ketQua.phan : [];
  const phanDoiChieu = phan.find((p) => p && p.tacTu === "doi_chieu");

  const buocDoiChieu = Array.isArray(tienTrinh?.buoc)
    ? tienTrinh.buoc.filter((b: any) => b && b.tacTu === "doi_chieu")
    : [];
  const buocXong = buocDoiChieu.length > 0 && buocDoiChieu.every((b: any) => b.trangThai === "xong");
  const phanXong = Boolean(
    phanDoiChieu &&
      (phanDoiChieu.traLoi ||
        (typeof phanDoiChieu.noiDung === "string" && phanDoiChieu.noiDung.trim().length > 0)),
  );

  const daQuaDoiChieu = phanXong || buocXong;
  if (!daQuaDoiChieu) {
    return { daQuaDoiChieu: false, coLuuYCanCu: false };
  }

  const tl = phanDoiChieu?.traLoi;
  const coLuuYCanCu = Boolean(
    (Array.isArray(tl?.conThieu) && tl.conThieu.length > 0) ||
      (Array.isArray(tl?.lech) && tl.lech.length > 0) ||
      (typeof phanDoiChieu?.canhBao === "string" && phanDoiChieu.canhBao.trim().length > 0),
  );
  return { daQuaDoiChieu: true, coLuuYCanCu };
}

/** Đổi kết quả của máy chủ thành một tin trợ lý; phần Trả lời đi vào ô câu trả lời có nguồn, phần khác thành khối thêm. */
export function chuyenKetQuaThanhTin(
  ketQua: any,
  cauHoi: string,
  nhan: { source?: string; model?: string; tienTrinh?: any } = {},
): Partial<ClinicalChatMessage> {
  const phan: any[] = Array.isArray(ketQua?.phan) ? ketQua.phan : [];
  const traLoi = phan.find((p) => p.tacTu === "tra_loi" && p.traLoi && typeof p.traLoi === "object" && (p.traLoi as any).answer);
  const phanKhac = phan.filter((p) => p !== traLoi).map((p) => ({
    tacTu: String(p.tacTu),
    ten: String(p.ten || tenTacTu(p.tacTu)),
    noiDung: String(p.noiDung ?? ""),
    ...(p.canhBao ? { canhBao: String(p.canhBao) } : {}),
  }));
  const khoi = (p: { ten: string; noiDung: string; canhBao?: string }) =>
    `### ${p.ten}\n${p.noiDung}${p.canhBao ? `${p.noiDung ? "\n\n" : ""}**Lưu ý:** ${p.canhBao}` : ""}`.trim();
  const noiDung = [traLoi ? String(traLoi.traLoi.answer) : "", ...phanKhac.map(khoi)].filter(Boolean).join("\n\n") ||
    "Trợ lý không có kết quả để hiện.";

  const canhBao = [
    ...new Set(
      [
        traLoi?.traLoi?.warning,
        ...phan.filter((p) => TAC_TU_CAN_CANH_BAO_LEN_DAU.has(p.tacTu)).map((p) => p.canhBao),
      ]
        .filter((x) => typeof x === "string" && x.trim())
        .map((x: string) => x.trim()),
    ),
  ].join(" ");

  const tk = ketQua?.thongKe || {};
  const ngoai = nhan.source === "mo_hinh_ngoai";
  const { daQuaDoiChieu, coLuuYCanCu } = kiemTraDoiChieuDaChay(ketQua, nhan.tienTrinh);
  const nhanCanCu = daQuaDoiChieu
    ? coLuuYCanCu
      ? "đã qua tác tử đối chiếu (có lưu ý căn cứ)"
      : "đã qua tác tử đối chiếu căn cứ"
    : "chưa qua kiểm căn cứ";
  const meta = ngoai
    ? `Mô hình ngoài · ${nhan.model || "qwen3.8-flash"} · ${tk.giay ?? 0}s · ${tk.token ?? 0} token · dữ liệu đã ẩn danh · ${nhanCanCu} · tham khảo, bác sĩ quyết định`
    : `Tại chỗ · hai tác tử luật · không gửi gì ra ngoài · tham khảo, bác sĩ quyết định`;

  return {
    content: noiDung,
    sources: traLoi?.traLoi?.sources || [],
    cauTruc: traLoi?.traLoi?.cauTruc || null,
    removedSources: traLoi?.traLoi?.removedSources || 0,
    warning: canhBao || null,
    meta,
    question: cauHoi,
    troLy: { phanKhac },
  };
}
