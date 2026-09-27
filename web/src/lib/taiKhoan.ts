/** Phía giao diện của đăng ký/đăng nhập. Máy chủ: may-chu/tai-khoan.ts. */

export type NguoiDung = { id: number; email: string; hoTen: string; vai: "quan_tri" | "bac_si" };
export type TinhTrangToi = { nguoiDung: NguoiDung | null; canMaMoi: boolean; taoQuanTriDuocTuDay: boolean };

async function goi<T>(duong: string, than?: unknown): Promise<T> {
  const r = await fetch(duong, {
    method: than === undefined ? "GET" : "POST",
    headers: than === undefined ? undefined : { "Content-Type": "application/json" },
    body: than === undefined ? undefined : JSON.stringify(than),
  });
  const d = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(d.error || `Máy chủ trả mã ${r.status}`);
  return d as T;
}

export const layToi = () => goi<TinhTrangToi>("/api/toi");
export const dangNhap = (email: string, matKhau: string) =>
  goi<{ nguoiDung: NguoiDung }>("/api/dang-nhap", { email, matKhau }).then((d) => d.nguoiDung);
export const dangKy = (v: { hoTen: string; email: string; matKhau: string; maMoi?: string }) =>
  goi<{ nguoiDung: NguoiDung }>("/api/dang-ky", v).then((d) => d.nguoiDung);
export const taoMaMoi = () => goi<{ ma: string; hetHan: number }>("/api/ma-moi", {});

// ------------------------------------------------------------------ bản sao trong trình duyệt
// Giao diện giữ một bản ca khám trong localStorage để F5 có ngay. Bản đó thuộc về MỘT người:
// đổi người đăng nhập hay đăng xuất thì xoá, để người sau trên cùng máy không thấy ca của người trước.
const CHU = "meditrace_chu";
const KHO_DONG_BO: [string, string, string][] = [
  ["/api/ca-kham", "meditrace_sessions", "meditrace_sessions_luc"],
  ["/api/kho/tra-cuu", "meditrace_kho_tra-cuu", "meditrace_kho_tra-cuu_luc"],
  ["/api/kho/mau-van-ban", "meditrace_kho_mau-van-ban", "meditrace_kho_mau-van-ban_luc"],
];

function xoaBanSaoMay() {
  try {
    for (const k of Object.keys(localStorage)) if (k.startsWith("meditrace_")) localStorage.removeItem(k);
  } catch {}
}

/** Gọi TRƯỚC khi dựng App cho người `id`: bản sao trên máy là của người khác thì xoá. */
export function nhanMayChoNguoi(id: number) {
  try {
    if (localStorage.getItem(CHU) !== String(id)) {
      xoaBanSaoMay();
      localStorage.setItem(CHU, String(id));
    }
  } catch {}
}

/**
 * Đăng xuất: đẩy nốt thay đổi chưa kịp lưu (giao diện chờ 0,8 giây mới ghi lên máy chủ),
 * rồi mới xoá bản sao trên máy. Chỉ đẩy kho nào bản trên máy mới hơn bản trên máy chủ.
 */
export async function dangXuat() {
  await Promise.all(
    KHO_DONG_BO.map(async ([duong, khoaDs, khoaLuc]) => {
      try {
        const ds = localStorage.getItem(khoaDs);
        const luc = Number(localStorage.getItem(khoaLuc) || 0);
        if (!ds) return;
        const r = await fetch(duong);
        if (!r.ok) return;
        const may = await r.json();
        if (luc > (may.savedAt || 0))
          await fetch(duong, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ sessions: JSON.parse(ds), savedAt: luc }),
          });
      } catch {}
    }),
  );
  await fetch("/api/dang-xuat", { method: "POST" }).catch(() => {});
  xoaBanSaoMay();
}
