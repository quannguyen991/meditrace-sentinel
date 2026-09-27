import { useEffect, useState } from "react";

/**
 * Một danh sách lưu ở hai nơi: trình duyệt (có ngay khi F5) và kho server /api/kho/<tên>
 * (còn khi xoá dữ liệu trình duyệt, mở được từ máy khác). Lúc mở trang, bản nào mới hơn thì dùng.
 * Chưa đọc xong kho server thì chưa ghi lên, để không đè bản mới bằng bản cũ.
 * Cùng cách làm với danh sách ca khám trong App.tsx.
 */
export function useKho<T>(ten: string, macDinh: T[] = []) {
  const khoaDs = `meditrace_kho_${ten}`;
  const khoaLuc = `meditrace_kho_${ten}_luc`;
  const [ds, setDs] = useState<T[]>(() => {
    try {
      const v = localStorage.getItem(khoaDs);
      if (v) return JSON.parse(v);
    } catch {}
    return macDinh;
  });
  // Mốc của bản trong trình duyệt, đọc MỘT LẦN trước mọi lần ghi.
  const [mocTrinhDuyet] = useState<number>(() => {
    try {
      return localStorage.getItem(khoaDs) ? Number(localStorage.getItem(khoaLuc) || 0) : 0;
    } catch {
      return 0;
    }
  });
  const [sanSang, setSanSang] = useState(false);

  useEffect(() => {
    let huy = false;
    fetch(`/api/kho/${ten}`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((d) => {
        if (huy) return;
        if (Array.isArray(d.sessions) && d.sessions.length && (d.savedAt || 0) > mocTrinhDuyet) setDs(d.sessions);
        setSanSang(true);
      })
      .catch(() => {});
    return () => {
      huy = true;
    };
  }, [ten]);

  useEffect(() => {
    const luc = Date.now();
    try {
      localStorage.setItem(khoaDs, JSON.stringify(ds));
      localStorage.setItem(khoaLuc, String(luc));
    } catch {}
    if (!sanSang) return;
    const hen = setTimeout(() => {
      fetch(`/api/kho/${ten}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sessions: ds, savedAt: luc }),
      }).catch(() => {});
    }, 800);
    return () => clearTimeout(hen);
  }, [ds, sanSang]);

  return [ds, setDs] as const;
}
