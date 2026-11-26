import { useEffect, useRef, useState } from "react";
import type { Session } from "../types";
import { initialSessions } from "../data/mockData";

export const KHO_KENH_DONG_BO = "meditrace_sessions_sync";

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

function chuanHoaDeSoVanTay(s: Session, baselineDuration = 0): Session {
  const chuan = truocKhiLuu(s);
  return s.isRecording ? { ...chuan, durationSeconds: baselineDuration } : chuan;
}

/**
 * Tính dấu vân tay dữ liệu thực chất để quyết định có cần gọi `PUT /api/ca-kham` hay không.
 * Khi một ca đang ghi âm (`s.isRecording === true`), `durationSeconds` nhảy mỗi giây (1Hz) được ghim về mốc
 * trước khi bấm ghi để chấm dứt bão 1.200 lệnh PUT trong 20 phút ghi âm (kể cả khi bấm Tiếp tục ghi âm).
 * Ngay khi dừng ghi (`s.isRecording === false`), `durationSeconds` chốt cuối được đưa lại vào dấu vân tay để lưu 1 lần duy nhất.
 */
export function dauVanTayLuuServer(
  sessions: Session[],
  baselineDurations?: ReadonlyMap<string, number>,
): string {
  return JSON.stringify(
    sessions.map((s) => chuanHoaDeSoVanTay(s, baselineDurations?.get(s.id) ?? 0)),
  );
}

export type PhuongAnDongBoServer =
  | { loai: "khong_doi" }
  | { loai: "mot_ca"; session: Session }
  | { loai: "toan_bo"; sessions: Session[] };

/**
 * Xác định phương án đồng bộ tối ưu lên máy chủ:
 * - Không đổi thực chất -> `"khong_doi"`
 * - Chỉ sửa 1 ca sẵn có (thứ tự danh sách giữ nguyên) -> `"mot_ca"` (`PUT /api/ca-kham/:id` kèm fallback `PUT /api/ca-kham`)
 * - Thêm mới / xoá / đổi thứ tự / sửa nhiều ca -> `"toan_bo"` (`PUT /api/ca-kham`)
 */
export function chonPhuongAnDongBoServer(
  prevSyncedSessions: Session[] | null,
  currentSessions: Session[],
): PhuongAnDongBoServer {
  const goiMoi = currentSessions.map(truocKhiLuu);
  if (!prevSyncedSessions || prevSyncedSessions.length !== currentSessions.length) {
    return { loai: "toan_bo", sessions: goiMoi };
  }

  let chiSoDoi = -1;
  for (let i = 0; i < currentSessions.length; i++) {
    const cu = prevSyncedSessions[i];
    const moi = currentSessions[i];
    if (cu.id !== moi.id) {
      return { loai: "toan_bo", sessions: goiMoi };
    }
    const fpCu = JSON.stringify(chuanHoaDeSoVanTay(cu, cu.durationSeconds));
    const fpMoi = JSON.stringify(chuanHoaDeSoVanTay(moi, cu.durationSeconds));
    if (fpCu !== fpMoi) {
      if (chiSoDoi !== -1) {
        return { loai: "toan_bo", sessions: goiMoi };
      }
      chiSoDoi = i;
    }
  }

  if (chiSoDoi === -1) return { loai: "khong_doi" };
  return { loai: "mot_ca", session: goiMoi[chiSoDoi] };
}

/**
 * Hợp nhất danh sách ca khám nhận từ `BroadcastChannel` của tab khác mà KHÔNG làm đứt
 * trạng thái đang ghi âm (`isRecording`, `audioUrl`, nhịp đồng hồ `durationSeconds`) ở tab hiện tại.
 */
export function gopBroadcastVaoPhienHienTai(
  currentSessions: Session[],
  incomingSessions: Session[],
): Session[] {
  const dangGhiTheoId = new Map<string, Session>();
  for (const cur of currentSessions) {
    if (cur.isRecording) dangGhiTheoId.set(cur.id, cur);
  }
  return incomingSessions.map((raw) => {
    const sach = sauKhiNap(raw);
    const dangGhi = dangGhiTheoId.get(sach.id);
    if (!dangGhi) return sach;
    return {
      ...sach,
      isRecording: true,
      audioUrl: dangGhi.audioUrl,
      durationSeconds: Math.max(dangGhi.durationSeconds, sach.durationSeconds),
    };
  });
}

type ThongDiepDongBoTab = {
  senderId: string;
  savedAt: number;
  sessions: Session[];
};

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

  const tabSenderIdRef = useRef<string>(`tab-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`);
  const channelRef = useRef<BroadcastChannel | null>(null);
  const sessionsRef = useRef<Session[]>(sessions);
  sessionsRef.current = sessions;
  const lastServerFingerprintRef = useRef<string>("");
  const lastSyncedSessionsRef = useRef<Session[] | null>(null);
  const lastBroadcastFingerprintRef = useRef<string>("");

  // Khởi tạo BroadcastChannel đồng bộ đa tab trình duyệt
  useEffect(() => {
    if (typeof BroadcastChannel === "undefined") return;
    let kenh: BroadcastChannel | null = null;
    try {
      kenh = new BroadcastChannel(KHO_KENH_DONG_BO);
      channelRef.current = kenh;
      kenh.onmessage = (ev: MessageEvent<ThongDiepDongBoTab>) => {
        const msg = ev.data;
        if (!msg || msg.senderId === tabSenderIdRef.current || !Array.isArray(msg.sessions)) return;
        const ds: Session[] = msg.sessions.map(sauKhiNap);
        if (!ds.length) return;
        const fp = dauVanTayLuuServer(ds);
        if (fp === lastBroadcastFingerprintRef.current) return;
        // Đánh dấu đã đồng bộ để tab nhận không bắn ngược PUT hoặc Broadcast gây vòng lặp,
        // đồng thời giữ nguyên phiên đang ghi âm (isRecording/audioUrl/durationSeconds) ở tab hiện tại.
        lastServerFingerprintRef.current = fp;
        lastSyncedSessionsRef.current = ds;
        lastBroadcastFingerprintRef.current = fp;
        setSessions((prev) => gopBroadcastVaoPhienHienTai(prev, msg.sessions));
        setActiveSessionId((id) => (ds.some((s) => s.id === id) ? id : ds[0].id));
      };
    } catch {
      channelRef.current = null;
    }
    return () => {
      try {
        kenh?.close();
      } catch {}
      channelRef.current = null;
    };
  }, []);

  useEffect(() => {
    let huy = false;
    fetch("/api/ca-kham")
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`mã ${r.status}`))))
      .then((d) => {
        if (huy) return;
        if (Array.isArray(d.sessions) && d.sessions.length) {
          const dsMayChu: Session[] = d.sessions.map(sauKhiNap);
          const trinhDuyetTrong =
            !mocTrinhDuyet ||
            sessions.length === 0 ||
            (sessions.length === 1 && !sessions[0].transcript && sessions[0].patientIdentifier.includes("Thêm tên"));
          if ((d.savedAt || 0) > mocTrinhDuyet || trinhDuyetTrong) {
            const fp = dauVanTayLuuServer(dsMayChu);
            lastServerFingerprintRef.current = fp;
            lastSyncedSessionsRef.current = dsMayChu;
            lastBroadcastFingerprintRef.current = fp;
            setSessions(dsMayChu);
            setActiveSessionId((id) => (dsMayChu.some((s) => s.id === id) ? id : dsMayChu[0].id));
          } else {
            // Bản trình duyệt mới hơn bản server: để effect lưu bên dưới đẩy lên 1 lần
            lastServerFingerprintRef.current = dauVanTayLuuServer(dsMayChu);
            lastSyncedSessionsRef.current = dsMayChu;
          }
        } else if (Array.isArray(d.sessions)) {
          lastSyncedSessionsRef.current = [];
          lastServerFingerprintRef.current = dauVanTayLuuServer([]);
        }
        setKhoServer("san_sang");
      })
      .catch(() => !huy && setKhoServer("loi"));
    return () => {
      huy = true;
    };
  }, []);

  const mocDurationCu = new Map<string, number>(
    (lastSyncedSessionsRef.current || []).map((s) => [s.id, s.durationSeconds]),
  );
  const vanTay = dauVanTayLuuServer(sessions, mocDurationCu);

  // Tách hẳn dependency theo `vanTay`: nhịp đồng hồ ghi âm 1Hz không đổi `vanTay` nên KHÔNG bao giờ
  // huỷ bộ hẹn giờ debounce 800ms của các sửa đổi thật diễn ra song song lúc đang ghi âm!
  useEffect(() => {
    const curSessions = sessionsRef.current;
    const duLieuThucChatDoi = vanTay !== lastServerFingerprintRef.current;

    if (duLieuThucChatDoi || vanTay !== lastBroadcastFingerprintRef.current) {
      const luc = Date.now();
      const goi = curSessions.map(truocKhiLuu);
      try {
        localStorage.setItem("meditrace_sessions", JSON.stringify(goi));
        localStorage.setItem("meditrace_sessions_luc", String(luc));
      } catch {}

      if (vanTay !== lastBroadcastFingerprintRef.current) {
        lastBroadcastFingerprintRef.current = vanTay;
        try {
          channelRef.current?.postMessage({
            senderId: tabSenderIdRef.current,
            savedAt: luc,
            sessions: goi,
          } satisfies ThongDiepDongBoTab);
        } catch {}
      }
    }

    if (khoServer !== "san_sang" || !duLieuThucChatDoi) return;

    const hen = setTimeout(async () => {
      const latestSessions = sessionsRef.current;
      const lucGhi = Date.now();
      const phuongAn = chonPhuongAnDongBoServer(lastSyncedSessionsRef.current, latestSessions);
      if (phuongAn.loai === "khong_doi") {
        lastServerFingerprintRef.current = vanTay;
        return;
      }

      const goiToanBo = latestSessions.map(truocKhiLuu);
      const mocSauGhi = new Map<string, number>(goiToanBo.map((s) => [s.id, s.durationSeconds]));
      const vanTayChot = dauVanTayLuuServer(latestSessions, mocSauGhi);
      lastServerFingerprintRef.current = vanTayChot;
      lastSyncedSessionsRef.current = goiToanBo;

      const luuToanBo = async () => {
        const r = await fetch("/api/ca-kham", {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ sessions: goiToanBo, savedAt: lucGhi }),
        });
        if (!r.ok) throw new Error(`PUT /api/ca-kham trả mã ${r.status}`);
      };

      try {
        if (phuongAn.loai === "mot_ca") {
          const r = await fetch(`/api/ca-kham/${encodeURIComponent(phuongAn.session.id)}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session: phuongAn.session, savedAt: lucGhi }),
          });
          if (!r.ok) {
            await luuToanBo();
          }
        } else {
          await luuToanBo();
        }
      } catch {
        // Nếu lỗi mạng thì mở lại khoá vân tay để lần sửa sau thử đồng bộ lại
        if (lastServerFingerprintRef.current === vanTayChot) {
          lastServerFingerprintRef.current = "";
        }
      }
    }, 800);
    return () => clearTimeout(hen);
  }, [vanTay, khoServer]);

  return {
    sessions,
    setSessions,
    activeSessionId,
    setActiveSessionId,
    khoServer,
  };
}
