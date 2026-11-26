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

/** Băm ngắn (djb2) — dùng chung với máy chủ để khoá kết quả duyệt khớp nhau. */
export { bamChuoi } from "../lib/kyDuyet";

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

/** Ca có ở lần đồng bộ trước nhưng nay không còn trong danh sách: bị xoá CÓ CHỦ ĐÍCH ở thiết bị này. */
export function caBiXoaCoChuDich(prevSynced: Session[] | null, current: Session[]): string[] {
  if (!prevSynced) return [];
  const conLai = new Set(current.map((s) => s.id));
  return prevSynced.map((s) => s.id).filter((id) => !conLai.has(id));
}

const vanTayMotCa = (s: Session | undefined) => (s ? JSON.stringify(chuanHoaDeSoVanTay(s, s.durationSeconds)) : "");

/**
 * Gộp khi máy chủ báo xung đột (409): `local` là danh sách ở thiết bị này, `server` vừa đọc lại,
 * `base` là bản đã đồng bộ lần trước. Không ca nào bị mất:
 * - chỉ một bên sửa -> lấy bên đã sửa; hai bên sửa khác nhau -> bản máy chủ giữ id, bản thiết bị này tách thành ca mới;
 * - ca mới ở bất kỳ bên nào được giữ; ca thiết bị này xoá chỉ bị xoá nếu máy chủ không sửa nó sau đó.
 */
export function gopKhiXungDot(local: Session[], server: Session[], base: Session[] | null): Session[] {
  const baseTheoId = new Map((base || []).map((s) => [s.id, s]));
  const serverTheoId = new Map(server.map((s) => [s.id, sauKhiNap(s)]));
  const localIds = new Set(local.map((s) => s.id));
  const ketQua: Session[] = [];
  const tachRieng: Session[] = [];

  for (const l of local) {
    const s = serverTheoId.get(l.id);
    const b = baseTheoId.get(l.id);
    const localDoi = !b || vanTayMotCa(l) !== vanTayMotCa(b);
    if (!s) {
      // Máy kia đã xoá: chỉ giữ khi thiết bị này có sửa (hoặc ca mới tạo ở đây).
      if (localDoi) ketQua.push(l);
      continue;
    }
    const serverDoi = !b || vanTayMotCa(s) !== vanTayMotCa(b);
    if (!localDoi || vanTayMotCa(l) === vanTayMotCa(s)) {
      ketQua.push(l.isRecording ? { ...s, isRecording: true, audioUrl: l.audioUrl, durationSeconds: l.durationSeconds } : s);
    } else if (!serverDoi) {
      ketQua.push(l);
    } else {
      ketQua.push(s);
      tachRieng.push({
        ...l,
        id: `${l.id}-xung-dot-${Date.now().toString(36)}`,
        patientIdentifier: `${l.patientIdentifier} (bản sửa trên máy này)`,
        signOff: undefined,
        isRecording: false,
      });
    }
  }
  // Ca chỉ có trên máy chủ: mới tạo ở máy kia, hoặc thiết bị này đã xoá nhưng máy kia vừa sửa -> giữ.
  const moiTuMayKhac: Session[] = [];
  for (const s of serverTheoId.values()) {
    if (localIds.has(s.id)) continue;
    const b = baseTheoId.get(s.id);
    if (!b || vanTayMotCa(s) !== vanTayMotCa(b)) moiTuMayKhac.push(s);
  }
  return [...moiTuMayKhac, ...tachRieng, ...ketQua];
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
  /** id -> cap_nhat_luc máy chủ đã xác nhận: gửi lại làm khoá lạc quan (expectedUpdatedAt / baseUpdatedAt). */
  const capNhatLucRef = useRef<Map<string, number>>(new Map());
  const ghiCapNhatLuc = (m: Record<string, number> | undefined | null, thayToanBo = false) => {
    if (thayToanBo) capNhatLucRef.current = new Map();
    for (const [id, luc] of Object.entries(m || {})) if (typeof luc === "number") capNhatLucRef.current.set(id, luc);
  };

  /** Máy chủ báo 409: đọc lại, gộp với bản ở đây (không ghi đè), để vòng lưu kế tiếp đẩy phần chênh lệch lên. */
  const xuLyXungDot = async (base: Session[] | null) => {
    try {
      const r = await fetch("/api/ca-kham", { cache: "no-store" });
      if (!r.ok) throw new Error(`mã ${r.status}`);
      const d = await r.json();
      const dsMayChu: Session[] = (Array.isArray(d.sessions) ? d.sessions : []).map(sauKhiNap);
      ghiCapNhatLuc(d.updatedAt, true);
      const gop = gopKhiXungDot(sessionsRef.current, dsMayChu, base);
      lastSyncedSessionsRef.current = dsMayChu.map(truocKhiLuu);
      lastServerFingerprintRef.current = dauVanTayLuuServer(dsMayChu);
      setSessions(gop);
      setActiveSessionId((id) => (gop.some((s) => s.id === id) ? id : gop[0]?.id ?? id));
    } catch {
      lastServerFingerprintRef.current = "";
    }
  };

  /** Ghi ngay MỘT ca lên máy chủ (vd. trước khi ký duyệt). Trả `true` khi máy chủ đã có đúng bản này. */
  const luuMotCaNgay = async (s: Session): Promise<boolean> => {
    const goi = truocKhiLuu(s);
    const expected = capNhatLucRef.current.get(s.id);
    try {
      const r = await fetch(`/api/ca-kham/${encodeURIComponent(s.id)}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session: goi, savedAt: Date.now(), ...(expected !== undefined ? { expectedUpdatedAt: expected } : {}) }),
      });
      if (r.status === 409) {
        await xuLyXungDot(lastSyncedSessionsRef.current);
        return false;
      }
      if (!r.ok) return false;
      const kq = await r.json().catch(() => ({}));
      if (typeof kq.updatedAt === "number") capNhatLucRef.current.set(s.id, kq.updatedAt);
      // Cập nhật mốc đã đồng bộ cho đúng ca này để vòng lưu nền không gửi lại / không báo xung đột giả.
      const truoc = lastSyncedSessionsRef.current;
      if (truoc) {
        lastSyncedSessionsRef.current = truoc.some((x) => x.id === s.id)
          ? truoc.map((x) => (x.id === s.id ? goi : x))
          : [goi, ...truoc];
      }
      return true;
    } catch {
      return false;
    }
  };

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
        ghiCapNhatLuc(d.updatedAt, true);
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
            // Bản trình duyệt mới hơn bản server: để effect lưu bên dưới đẩy lên 1 lần.
            // Ca chỉ có trên máy chủ (máy khác tạo) được thêm vào đây, KHÔNG bị coi là "đã xoá".
            lastServerFingerprintRef.current = dauVanTayLuuServer(dsMayChu);
            lastSyncedSessionsRef.current = dsMayChu;
            const coTaiCho = new Set(sessionsRef.current.map((s) => s.id));
            const chiTrenMayChu = dsMayChu.filter((s) => !coTaiCho.has(s.id));
            if (chiTrenMayChu.length) setSessions((prev) => [...chiTrenMayChu, ...prev]);
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
      const dongBoTruoc = lastSyncedSessionsRef.current;
      lastServerFingerprintRef.current = vanTayChot;
      lastSyncedSessionsRef.current = goiToanBo;

      // Gửi cả danh sách kèm khoá lạc quan; chỉ xoá những ca thiết bị này đã xoá có chủ đích.
      const luuToanBo = async () => {
        const r = await fetch("/api/ca-kham", {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            sessions: goiToanBo,
            savedAt: lucGhi,
            baseUpdatedAt: Object.fromEntries(capNhatLucRef.current),
            deletedIds: caBiXoaCoChuDich(dongBoTruoc, goiToanBo),
          }),
        });
        if (r.status === 409) return "xung_dot" as const;
        if (!r.ok) throw new Error(`PUT /api/ca-kham trả mã ${r.status}`);
        const kq = await r.json().catch(() => ({}));
        ghiCapNhatLuc(kq.updatedAt, true);
        return "ok" as const;
      };

      try {
        let ketQua: "ok" | "xung_dot";
        if (phuongAn.loai === "mot_ca") {
          const expected = capNhatLucRef.current.get(phuongAn.session.id);
          const r = await fetch(`/api/ca-kham/${encodeURIComponent(phuongAn.session.id)}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              session: phuongAn.session,
              savedAt: lucGhi,
              ...(expected !== undefined ? { expectedUpdatedAt: expected } : {}),
            }),
          });
          if (r.status === 409) ketQua = "xung_dot";
          else if (r.ok) {
            const kq = await r.json().catch(() => ({}));
            if (typeof kq.updatedAt === "number") capNhatLucRef.current.set(phuongAn.session.id, kq.updatedAt);
            ketQua = "ok";
          } else ketQua = await luuToanBo();
        } else {
          ketQua = await luuToanBo();
        }
        // Xung đột: KHÔNG ghi đè — đọc lại, gộp, vòng lưu sau chỉ đẩy phần đã gộp với khoá mới.
        if (ketQua === "xung_dot") await xuLyXungDot(dongBoTruoc);
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
    luuMotCaNgay,
  };
}
