/**
 * Cài đặt trợ lý, lưu trong bảng `cai_dat (khoa, gia_tri)` có sẵn:
 *  - `tro_ly:<id người dùng>`: JSON danh sách tác tử người đó bật (mặc định bật cả sáu).
 *  - `tro_ly_ngoai`: "bat" là quản trị đã bật đường ngoài; không có hoặc "tat" thì tắt (env MEDITRACE_TRO_LY_NGOAI=tat|bat thắng).
 */
import type { DatabaseSync } from "node:sqlite";
import type { TacTuMa } from "./kieu";

export const TAT_CA_TAC_TU: readonly TacTuMa[] = ["dieu_phoi", "tim_kiem", "tra_loi", "doi_chieu", "chu_de_can_ban", "doi_chieu_thuoc"];

const hopLe = (x: unknown): x is TacTuMa => typeof x === "string" && (TAT_CA_TAC_TU as readonly string[]).includes(x);

const docKhoa = (db: DatabaseSync, khoa: string): string | null => {
  const r = db.prepare("SELECT gia_tri FROM cai_dat WHERE khoa = ?").get(khoa) as { gia_tri: string | null } | undefined;
  return r?.gia_tri ?? null;
};
const ghiKhoa = (db: DatabaseSync, khoa: string, giaTri: string) =>
  void db.prepare("INSERT INTO cai_dat (khoa, gia_tri) VALUES (?, ?) ON CONFLICT(khoa) DO UPDATE SET gia_tri = excluded.gia_tri").run(khoa, giaTri);

export function docCaiDat(db: DatabaseSync, nguoiDungId: number): { batTacTu: TacTuMa[] } {
  const tho = docKhoa(db, `tro_ly:${nguoiDungId}`);
  if (tho !== null) {
    try {
      const j = JSON.parse(tho);
      if (Array.isArray(j)) return { batTacTu: [...new Set(j.filter(hopLe))] };
    } catch {
      /* dữ liệu hỏng: dùng mặc định */
    }
  }
  return { batTacTu: [...TAT_CA_TAC_TU] };
}

export function ghiCaiDat(db: DatabaseSync, nguoiDungId: number, batTacTu: TacTuMa[]): void {
  ghiKhoa(db, `tro_ly:${nguoiDungId}`, JSON.stringify([...new Set((Array.isArray(batTacTu) ? batTacTu : []).filter(hopLe))]));
}

/**
 * Đường ra mô hình ngoài (AIBOX, dịch vụ bên thứ ba) MẶC ĐỊNH TẮT (Đề cải tiến 1, 28/11/2026):
 * env "tat" luôn tắt; quản trị bấm tắt thì tắt, bấm bật thì mở; chưa ai chọn thì chỉ mở khi env "bat" (máy chủ thử).
 */
export function ngoaiBat(db: DatabaseSync, env: NodeJS.ProcessEnv): boolean {
  if (env.MEDITRACE_TRO_LY_NGOAI === "tat") return false;
  const quanTri = docKhoa(db, "tro_ly_ngoai");
  if (quanTri === "tat") return false; // quản trị đã bấm tắt thì luôn tắt
  if (quanTri === "bat") return true;
  return env.MEDITRACE_TRO_LY_NGOAI === "bat"; // chưa ai chọn: chỉ mở khi máy chủ đặt env bat
}

export function ghiNgoaiBat(db: DatabaseSync, bat: boolean): void {
  ghiKhoa(db, "tro_ly_ngoai", bat ? "bat" : "tat");
}
