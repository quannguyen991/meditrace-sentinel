/**
 * Bật mô hình ngoài (cổng AIBOX, dịch vụ bên thứ ba) một cách nhất quán giữa trình duyệt và máy chủ.
 * Máy chủ chỉ gửi ra ngoài khi có khoá VÀ quản trị đã bật; trước đây công tắc ở giao diện chỉ đổi cờ
 * trong trình duyệt nên bấm bật xong mọi lệnh vẫn bị từ chối.
 */
export type KetQuaBatNgoai = { duoc: true } | { duoc: false; lyDo: string };

type TrangThaiNgoai = { configured?: boolean; enabled?: boolean; reachable?: boolean; model?: string };

export const HOI_XAC_NHAN_BAT_NGOAI =
  "Bật mô hình ngoài cho máy chủ này?\n\n" +
  "AIBOX là dịch vụ của bên thứ ba. Chỉ văn bản đã che tên, số điện thoại, địa chỉ… mới được gửi đi; " +
  "bản nháp chính vẫn do Qwen3-4B tại chỗ viết. Việc bật được ghi vào nhật ký quản trị.";

export async function kiemVaBatMoHinhNgoai(
  xacNhan: (cau: string) => boolean,
  goi: typeof fetch = (...a) => fetch(...a),
): Promise<KetQuaBatNgoai> {
  let st: TrangThaiNgoai | null = null;
  try {
    st = (await (await goi("/api/external/status")).json()) as TrangThaiNgoai;
  } catch {
    return { duoc: false, lyDo: "Không hỏi được máy chủ về mô hình ngoài. Kiểm tra kết nối rồi thử lại." };
  }
  if (!st?.configured) {
    return { duoc: false, lyDo: "Máy chủ chưa cấu hình khoá mô hình ngoài — hệ thống chỉ dùng Qwen3-4B tại chỗ." };
  }
  if (!st.enabled) {
    if (!xacNhan(HOI_XAC_NHAN_BAT_NGOAI)) return { duoc: false, lyDo: "Đã giữ tắt mô hình ngoài." };
    let r: Response;
    try {
      r = await goi("/api/tro-ly/cai-dat/ngoai", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ bat: true }),
      });
    } catch {
      return { duoc: false, lyDo: "Không gửi được lệnh bật tới máy chủ." };
    }
    if (r.status === 403) {
      return { duoc: false, lyDo: "Chỉ quản trị mới bật được mô hình ngoài cho máy chủ. Nhờ quản trị bật trong khung Trợ lý." };
    }
    const d = (await r.json().catch(() => ({}))) as { ngoaiBat?: boolean; error?: string };
    if (!r.ok) return { duoc: false, lyDo: d.error || `Máy chủ trả mã ${r.status} khi bật mô hình ngoài.` };
    if (!d.ngoaiBat) {
      return { duoc: false, lyDo: "Máy chủ đang khoá tắt mô hình ngoài bằng biến môi trường (MEDITRACE_TRO_LY_NGOAI=tat)." };
    }
  }
  if (st.reachable === false) {
    return { duoc: false, lyDo: "Đã bật nhưng hiện không tới được cổng mô hình ngoài. Thử lại sau." };
  }
  return { duoc: true };
}
