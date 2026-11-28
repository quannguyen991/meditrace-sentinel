/** Phân loại tệp người dùng thả/chọn ở khung Lời thoại: âm thanh → PhoWhisper, văn bản → lời thoại gõ sẵn. */
export type LoaiTepDauVao = "am_thanh" | "loi_thoai" | "khong_ho_tro";

const DUOI_AM_THANH = new Set(["mp3", "wav", "m4a", "webm", "ogg", "flac", "aac", "mp4"]);
const DUOI_LOI_THOAI = new Set(["txt", "md"]);

export function loaiTepDauVao(tep: { name: string; type?: string }): LoaiTepDauVao {
  const duoi = (tep.name.split(".").pop() || "").toLowerCase();
  const kieu = (tep.type || "").toLowerCase();
  if (DUOI_LOI_THOAI.has(duoi) || kieu === "text/plain" || kieu === "text/markdown") return "loi_thoai";
  if (DUOI_AM_THANH.has(duoi) || kieu.startsWith("audio/")) return "am_thanh";
  return "khong_ho_tro";
}
