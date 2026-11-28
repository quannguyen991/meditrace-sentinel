/** Phân loại tệp người dùng thả/chọn ở khung Lời thoại: âm thanh → PhoWhisper, văn bản → lời thoại gõ sẵn. */
export type LoaiTepDauVao = "am_thanh" | "loi_thoai" | "khong_ho_tro";

const DUOI_AM_THANH = new Set(["mp3", "wav", "m4a", "webm", "ogg", "flac", "aac", "mp4"]);
const DUOI_LOI_THOAI = new Set(["txt", "md", "srt", "vtt"]);

/** Giá trị `accept` cho ô chọn tệp: mọi loại âm thanh và văn bản ở trên. */
export const NHAN_TEP_DAU_VAO = [
  "audio/*",
  ...[...DUOI_AM_THANH, ...DUOI_LOI_THOAI].map((d) => `.${d}`),
  "text/plain",
  "text/markdown",
  "text/vtt",
].join(",");

export function loaiTepDauVao(tep: { name: string; type?: string }): LoaiTepDauVao {
  const duoi = (tep.name.split(".").pop() || "").toLowerCase();
  const kieu = (tep.type || "").toLowerCase();
  if (DUOI_LOI_THOAI.has(duoi) || kieu === "text/plain" || kieu === "text/markdown" || kieu === "text/vtt")
    return "loi_thoai";
  if (DUOI_AM_THANH.has(duoi) || kieu.startsWith("audio/")) return "am_thanh";
  return "khong_ho_tro";
}

/**
 * Đọc chữ của tệp lời thoại. Tệp phụ đề .srt/.vtt: bỏ dòng "WEBVTT", số thứ tự và mốc giờ,
 * giữ lại lời nói. Tệp .txt/.md giữ nguyên.
 */
export function layLoiThoaiTuTep(ten: string, chu: string): string {
  const s = chu.replace(/^﻿/, "").replace(/\r\n?/g, "\n");
  const duoi = (ten.split(".").pop() || "").toLowerCase();
  if (duoi !== "srt" && duoi !== "vtt") return s.trim();
  return s
    .split("\n")
    .filter((d) => {
      const t = d.trim();
      if (!t || t === "WEBVTT" || /^\d+$/.test(t)) return false;
      if (/\d{1,2}:\d{2}(:\d{2})?[.,]\d{3}\s*-->/.test(t)) return false;
      if (/^(NOTE|STYLE|REGION)\b/.test(t)) return false;
      return true;
    })
    .join("\n")
    .trim();
}
