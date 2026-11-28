/**
 * Đọc thân phản hồi là JSON; trả null nếu không phải JSON (ví dụ trang lỗi HTML của cổng mạng
 * khi máy chủ đang khởi động lại). Tránh lỗi khó hiểu "Unexpected token '<' … is not valid JSON".
 */
export async function docJsonHoacNull(res: Response): Promise<any | null> {
  const chu = await res.text().catch(() => "");
  if (!chu.trim()) return null;
  try {
    return JSON.parse(chu);
  } catch {
    return null;
  }
}
