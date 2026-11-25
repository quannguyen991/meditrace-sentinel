import { useEffect, useState } from "react";
import type { Session } from "../types";
import { initialSessions } from "../data/mockData";

/** Trạng thái không còn đúng sau khi tải lại trang: đang ghi âm, đường dẫn blob của bản ghi. */
export function truocKhiLuu(s: Session): Session {
  const { audioUrl, ...con } = s;
  return { ...con, isRecording: false };
}

export function sauKhiNap(s: Session): Session {
  return { ...s, isRecording: false, audioUrl: undefined };
}

/** Băm ngắn (djb2) để làm khoá kết quả duyệt theo nội dung bản nháp. Không dùng cho bảo mật. */
export function bamChuoi(s: string) {
  let h = 5381;
  for (let i = 0; i < s.length; i++) h = ((h << 5) + h + s.charCodeAt(i)) | 0;
  return (h >>> 0).toString(36);
}

export function useSessionsStore() {
  const [sessions, setSessions] = useState<Session[]>(() => {
    try {
      const saved = localStorage.getItem("meditrace_sessions");
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) return parsed.map(sauKhiNap);
      }
    } catch {}
    return initialSessions;
  });

  const [activeSessionId, setActiveSessionId] = useState<string>(() => {
    try {
      const id = localStorage.getItem("meditrace_ca_dang_mo");
      if (id && sessions.some((s) => s.id === id)) return id;
    } catch {}
    return sessions[0]?.id || initialSessions[0].id;
  });

  useEffect(() => {
    try {
      localStorage.setItem("meditrace_ca_dang_mo", activeSessionId);
    } catch {}
  }, [activeSessionId]);

  const [khoServer, setKhoServer] = useState<"dang_doc" | "san_sang" | "loi">("dang_doc");
  const [mocTrinhDuyet] = useState<number>(() => {
    try {
      return localStorage.getItem("meditrace_sessions")
        ? Number(localStorage.getItem("meditrace_sessions_luc") || 0)
        : 0;
    } catch {
      return 0;
    }
  });

  useEffect(() => {
    let huy = false;
    fetch("/api/ca-kham")
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`mã ${r.status}`))))
      .then((d) => {
        if (huy) return;
        if (Array.isArray(d.sessions) && d.sessions.length) {
          const trinhDuyetTrong =
            !mocTrinhDuyet ||
            sessions.length === 0 ||
            (sessions.length === 1 && !sessions[0].transcript && sessions[0].patientIdentifier.includes("Thêm tên"));
          if ((d.savedAt || 0) > mocTrinhDuyet || trinhDuyetTrong) {
            const ds: Session[] = d.sessions.map(sauKhiNap);
            setSessions(ds);
            setActiveSessionId((id) => (ds.some((s) => s.id === id) ? id : ds[0].id));
          }
        }
        setKhoServer("san_sang");
      })
      .catch(() => !huy && setKhoServer("loi"));
    return () => {
      huy = true;
    };
  }, []);

  useEffect(() => {
    const luc = Date.now();
    const goi = sessions.map(truocKhiLuu);
    try {
      localStorage.setItem("meditrace_sessions", JSON.stringify(goi));
      localStorage.setItem("meditrace_sessions_luc", String(luc));
    } catch {}
    if (khoServer !== "san_sang") return;
    const hen = setTimeout(() => {
      fetch("/api/ca-kham", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sessions: goi, savedAt: luc }),
      }).catch(() => {});
    }, 800);
    return () => clearTimeout(hen);
  }, [sessions, khoServer]);

  return {
    sessions,
    setSessions,
    activeSessionId,
    setActiveSessionId,
    khoServer,
  };
}
