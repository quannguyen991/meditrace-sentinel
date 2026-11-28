/**
 * Che định danh trước khi ghi log tiến trình (Đề cải tiến 1: không đưa dữ liệu nhận dạng vào log).
 * Che trước, rồi cắt ngắn; dùng cùng bộ che với cổng ra mô hình ngoài. Bộ che từ chối (còn định danh
 * không che được) thì chỉ ghi độ dài.
 */
import { anDanhChoNgoai } from "./an-danh-ngoai";

export function cheLog(giaTri: unknown, toiDa = 300): string {
  let s: string;
  if (typeof giaTri === "string") s = giaTri;
  else if (giaTri instanceof Error) s = giaTri.stack || giaTri.message;
  else {
    try {
      s = JSON.stringify(giaTri) ?? String(giaTri);
    } catch {
      s = String(giaTri);
    }
  }
  // Che TRƯỚC rồi mới cắt: cắt trước có thể chặt đôi một số điện thoại / tên khiến bộ che không nhận ra.
  // Giới hạn đầu vào ở 8.000 ký tự để log khổng lồ không làm chậm máy chủ.
  const kq = anDanhChoNgoai(s.length > 8000 ? s.slice(0, 8000) : s);
  if (!kq.ok) return `[đã ẩn ${s.length} ký tự: còn định danh]`;
  return kq.van.length > toiDa ? kq.van.slice(0, toiDa) : kq.van;
}
