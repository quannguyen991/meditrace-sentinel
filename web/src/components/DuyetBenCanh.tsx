import React, { useEffect, useMemo, useRef, useState } from "react";
import {
  Check,
  CheckCircle2,
  Info,
  Maximize2,
  MessageSquare,
  Pencil,
  Play,
  Plus,
  Sparkles,
  Square,
  Trash2,
  Undo2,
  X,
  AlertTriangle,
} from "lucide-react";
import type { NoteMeta, Proposition, Quyet } from "./VerificationView";
import type { TranscriptSegment } from "../types";
import { canXacNhan, tachLuot } from "../lib/compileEffectiveNote";
import { khoangPhatLaiLuot, phanTichVungMoAsr } from "../lib/asrHighlight";
import { useTurnAudioPlayer } from "../hooks/useTurnAudioPlayer";

/**
 * NGĂN DUYỆT CẠNH BẢN NHÁP (24/09 + Boost 4 Keyboard Triage & Stage 4.5 Omission 1-Tap Recovery).
 * Bác sĩ vừa đọc bản nháp vừa duyệt từng mệnh đề, không phải chuyển màn.
 * Bấm một mệnh đề -> câu đó sáng lên trong bản nháp (NoteEditorView tô theo `danhDau`);
 * bấm một câu trong bản nháp -> ngăn này cuộn tới mệnh đề đó. Giữ / sửa / bỏ dùng chung trạng thái
 * với màn "Duyệt từng mệnh đề" đầy đủ (có dây nối tới lượt hội thoại).
 */

export type TrangThaiMD = "canh" | "luuy" | "ok" | "giu" | "sua" | "bo";

export interface MucKhoiPhucBoSotTang45 {
  luot?: number;
  nguoi_noi?: string;
  loai_thong_tin?: string;
  noi_dung_goi_y?: string;
  trich_dan_nguyen_van?: string;
  muc_do_nghiem_trong?: number;
  ly_do_khoi_phuc?: string;
  [key: string]: unknown;
}

/** Trạng thái hiển thị của một mệnh đề — dùng chung cho ngăn duyệt và màu tô trong bản nháp. */
export function trangThaiMD(p: Proposition, q: Quyet | undefined, boQuaCanhBao = false): TrangThaiMD {
  if (q === "bo") return "bo";
  if (q === "giu") return "giu";
  if (q === "sua") return "sua";
  if (canXacNhan(p)) return "canh";
  if (!boQuaCanhBao && p.warning && p.warning.kind !== "can_xem") return "luuy";
  return "ok";
}

/**
 * Kiểm tra mệnh đề đủ an toàn để "Giữ nhanh mệnh đề xanh":
 * - Phải đang ở trạng thái `"ok"` (chưa duyệt, không thuộc `Cần xác nhận`, không có lưu ý `luuy`)
 * - Tuyệt đối KHÔNG tự duyệt nhanh Dị ứng, Thuốc đang dùng, Kế hoạch điều trị / Đơn thuốc, hoặc mệnh đề có `p.drug`.
 */
export function laMenhDeXanhAnToanGiuNhanh(p: Proposition, q: Quyet | undefined): boolean {
  if (trangThaiMD(p, q) !== "ok") return false;
  if (p.drug) return false;
  const sec = (p.section || "").trim().toUpperCase();
  if (
    sec === "DỊ ỨNG" ||
    sec === "THUỐC ĐANG DÙNG" ||
    sec === "KẾ HOẠCH ĐIỀU TRỊ" ||
    sec === "ĐƠN THUỐC"
  ) {
    return false;
  }
  return true;
}

const NHAN_LOAI_BO_SOT: Record<string, { chu: string; lop: string }> = {
  di_ung: { chu: "Dị ứng bỏ sót", lop: "bg-[#FEE2E2] text-[#991B1B] border-[#FECACA]" },
  thuoc: { chu: "Thuốc bỏ sót", lop: "bg-[#FEF3C7] text-[#92400E] border-[#FDE68A]" },
  thuoc_dong_y_ngam: { chu: "Đông-Tây y ngầm", lop: "bg-[#FFEDD5] text-[#9A3412] border-[#FED7AA]" },
  trieu_chung_am_tinh: { chu: "Triệu chứng âm tính", lop: "bg-[#E0F2FE] text-[#0369A1] border-[#BAE6FD]" },
  sinh_hieu: { chu: "Sinh hiệu", lop: "bg-[#DCFCE7] text-[#166534] border-[#BBF7D0]" },
};

const NHAN: Record<TrangThaiMD, { chu: string; lop: string; the: string }> = {
  canh: { chu: "Cần xác nhận", lop: "bg-[#FDE2E2] text-[#B4232C]", the: "border-[#F5C2C2] bg-[#FFF5F5]" },
  luuy: { chu: "Có lưu ý", lop: "bg-[#FEF3C7] text-[#92400E]", the: "border-[#F5E1A4] bg-[#FFFBEB]" },
  ok: { chu: "Máy không cảnh báo", lop: "bg-[#DDF3E9] text-[#0D6B50]", the: "border-[#CDEBDD] bg-white" },
  giu: { chu: "Đã giữ", lop: "bg-[#D1F2E3] text-[#0D6B50]", the: "border-[#CDEBDD] bg-[#F3FBF7]" },
  sua: { chu: "Đã sửa", lop: "bg-[#FEF3C7] text-[#92400E]", the: "border-[#F2DFA8] bg-[#FFFBEB]" },
  bo: { chu: "Đã bỏ", lop: "bg-[#F1F5F9] text-[#64748B]", the: "border-[#E2E8F0] bg-[#F8FAFC]" },
};

type Loc = "tat_ca" | "can" | "chua";

interface Props {
  note: NoteMeta;
  quyet: Record<number, Quyet>;
  setQuyet: React.Dispatch<React.SetStateAction<Record<number, Quyet>>>;
  banSua: Record<number, string>;
  setBanSua: React.Dispatch<React.SetStateAction<Record<number, string>>>;
  chonId: number | null;
  onChon: (id: number | null) => void;
  onMoToanMan: () => void;
  onDong: () => void;
  audioUrl?: string;
  segments?: TranscriptSegment[];
  /** Boost 4: Khôi phục 1 chạm mệnh đề bị bỏ sót từ Tầng 4.5 ActiveOmissionRecoveryEngine */
  onKhoiPhucBoSot?: (muc: MucKhoiPhucBoSotTang45) => void;
}

function dangGoTrongO(target: EventTarget | null): boolean {
  const el = target as HTMLElement | null;
  if (!el) return false;
  const tag = el.tagName;
  if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return true;
  if (el.isContentEditable || el.closest?.('[contenteditable="true"]')) return true;
  return false;
}

export const DuyetBenCanh: React.FC<Props> = ({
  note,
  quyet,
  setQuyet,
  banSua,
  setBanSua,
  chonId,
  onChon,
  onMoToanMan,
  onDong,
  audioUrl,
  segments,
  onKhoiPhucBoSot,
}) => {
  const [loc, setLoc] = useState<Loc>("tat_ca");
  const [suaId, setSuaId] = useState<number | null>(null);
  const [chuSua, setChuSua] = useState("");
  const [moLuot, setMoLuot] = useState<Record<number, boolean>>({});
  const [daBoSungTang45, setDaBoSungTang45] = useState<Record<string, boolean>>({});
  const { dangPhatLuot, phatDoanLuot } = useTurnAudioPlayer(audioUrl, segments);
  const theRef = useRef(new Map<number, HTMLDivElement>());

  const luot = useMemo(() => tachLuot(note.transcript), [note.transcript]);
  // Thứ tự như trong bản nháp: mệnh đề cần xác nhận lên trước để bác sĩ xử lý trước.
  const ds = useMemo(() => {
    const goc = note.propositions || [];
    const hang = (p: Proposition) => (canXacNhan(p) ? 0 : p.warning && p.warning.kind !== "can_xem" ? 1 : 2);
    return [...goc].sort((a, b) => hang(a) - hang(b) || a.id - b.id);
  }, [note.propositions]);

  const tt = (p: Proposition) => trangThaiMD(p, quyet[p.id]);
  const hien = useMemo(
    () =>
      ds.filter((p) =>
        loc === "tat_ca" ? true : loc === "can" ? ["canh", "luuy"].includes(tt(p)) : !quyet[p.id] || quyet[p.id] === "cho",
      ),
    [ds, loc, quyet],
  );
  const daDuyet = ds.filter((p) => quyet[p.id] && quyet[p.id] !== "cho").length;
  const conCan = ds.filter((p) => tt(p) === "canh").length;

  // Danh sách mệnh đề xanh an toàn có thể duyệt nhanh (không bao gồm Dị ứng, Thuốc, Cần xác nhận, Lưu ý)
  const dsXanhAnToan = useMemo(
    () => ds.filter((p) => laMenhDeXanhAnToanGiuNhanh(p, quyet[p.id])),
    [ds, quyet],
  );

  // Tầng 4.5 Khôi phục bỏ sót chủ động
  const dsBoSotTang45: MucKhoiPhucBoSotTang45[] = useMemo(() => {
    const raw = note.clinicalSafety?.khoi_phuc_bo_sot_tang_45;
    return Array.isArray(raw) ? raw : [];
  }, [note.clinicalSafety]);

  // Được chọn từ bản nháp -> cuộn tới thẻ.
  useEffect(() => {
    if (chonId === null) return;
    const h = requestAnimationFrame(() => {
      const el = theRef.current.get(chonId);
      if (el?.offsetParent) el.scrollIntoView({ block: "nearest", behavior: "smooth" });
    });
    return () => cancelAnimationFrame(h);
  }, [chonId]);

  const dat = (id: number, q: Quyet) => setQuyet((x) => ({ ...x, [id]: q }));
  const luuSua = (id: number) => {
    if (chuSua.trim()) {
      setBanSua((b) => ({ ...b, [id]: chuSua.trim() }));
      dat(id, "sua");
    }
    setSuaId(null);
  };

  const giuNhanhMenhDeXanh = () => {
    if (dsXanhAnToan.length === 0) return;
    setQuyet((truoc) => {
      const moi = { ...truoc };
      for (const p of dsXanhAnToan) {
        moi[p.id] = "giu";
      }
      return moi;
    });
  };

  // Điều hướng bàn phím tốc độ cao (J/K/Enter/E/Backspace/Space) khi ngăn duyệt mở
  useEffect(() => {
    const xuLyPhim = (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey || e.altKey) return;
      if (suaId !== null) return;
      if (dangGoTrongO(e.target) || dangGoTrongO(document.activeElement)) return;
      if (document.querySelector('[role="dialog"]')) return;
      if (hien.length === 0) return;

      const key = e.key;
      const idxHienTai = chonId !== null ? hien.findIndex((p) => p.id === chonId) : -1;
      const dangChon = idxHienTai >= 0 ? hien[idxHienTai] : null;
      const laNutBam = (e.target as HTMLElement | null)?.tagName === "BUTTON";

      if (key === "j" || key === "J" || key === "ArrowDown") {
        e.preventDefault();
        const tiep = idxHienTai < 0 ? 0 : Math.min(hien.length - 1, idxHienTai + 1);
        onChon(hien[tiep].id);
        return;
      }

      if (key === "k" || key === "K" || key === "ArrowUp") {
        e.preventDefault();
        const truoc = idxHienTai < 0 ? hien.length - 1 : Math.max(0, idxHienTai - 1);
        onChon(hien[truoc].id);
        return;
      }

      if (!dangChon) return;

      if (key === "Enter" && !laNutBam) {
        e.preventDefault();
        dat(dangChon.id, "giu");
        return;
      }

      if (key === "e" || key === "E") {
        e.preventDefault();
        setSuaId(dangChon.id);
        setChuSua(banSua[dangChon.id] || dangChon.text);
        return;
      }

      if (key === "Backspace" || key === "Delete") {
        e.preventDefault();
        dat(dangChon.id, "bo");
        return;
      }

      if (key === " " && !laNutBam) {
        const luotDau = dangChon.evidenceTurns[0];
        if (luotDau !== undefined && audioUrl && khoangPhatLaiLuot(luotDau, segments)) {
          e.preventDefault();
          phatDoanLuot(luotDau);
        }
      }
    };

    window.addEventListener("keydown", xuLyPhim);
    return () => window.removeEventListener("keydown", xuLyPhim);
  }, [hien, chonId, suaId, banSua, audioUrl, segments, onChon, phatDoanLuot]);

  return (
    <aside className="flex flex-col min-h-0 h-full bg-[#F8FBFC] border-t @4xl:border-t-0 @4xl:border-l border-[#BAE6FD]">
      {/* Đầu ngăn */}
      <div className="px-3 pt-3 pb-2 border-b border-[#E2ECF3] bg-white space-y-2">
        <div className="flex items-center justify-between gap-2">
          <h2 className="text-[13px] font-bold text-[#0C2340]">Duyệt từng mệnh đề</h2>
          <div className="flex items-center gap-0.5">
            <button
              onClick={onMoToanMan}
              title="Mở màn duyệt đầy đủ (dây nối tới lượt hội thoại)"
              className="p-1.5 rounded-md text-[#64748B] hover:bg-[#E0F2FE] hover:text-[#0369A1]"
            >
              <Maximize2 size={14} />
            </button>
            <button
              onClick={onDong}
              title="Đóng ngăn duyệt"
              className="p-1.5 rounded-md text-[#64748B] hover:bg-[#E0F2FE] hover:text-[#0369A1]"
            >
              <X size={14} />
            </button>
          </div>
        </div>
        <div>
          <div className="flex items-center justify-between text-[11px] text-[#0C4A6E]">
            <span>
              <strong className="tabular-nums">
                {daDuyet}/{ds.length}
              </strong>{" "}
              đã duyệt
            </span>
            {conCan > 0 && <span className="text-[#B4232C] font-semibold">{conCan} cần xác nhận</span>}
          </div>
          <div className="w-full h-1 rounded-full bg-[#E0F2FE] overflow-hidden mt-1">
            <div
              className="h-full bg-[#0284C7] rounded-full transition-all"
              style={{ width: `${ds.length ? (daDuyet / ds.length) * 100 : 0}%` }}
            />
          </div>
        </div>

        {/* Nút Giữ nhanh N mệnh đề xanh (chỉ áp dụng mệnh đề xanh không phải Thuốc / Dị ứng / Cần xác nhận) */}
        {dsXanhAnToan.length > 0 && (
          <button
            type="button"
            onClick={giuNhanhMenhDeXanh}
            title="Chỉ duyệt nhanh các mệnh đề xanh không cảnh báo; tuyệt đối KHÔNG tự duyệt Dị ứng, Thuốc hoặc mục Cần xác nhận"
            className="w-full flex items-center justify-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-[#E6F7F0] hover:bg-[#D1F2E3] border border-[#A7E3C9] text-[#0D6B50] text-[11.5px] font-semibold transition-colors cursor-pointer"
          >
            <CheckCircle2 size={13} className="flex-shrink-0" />
            <span>Giữ nhanh {dsXanhAnToan.length} mệnh đề xanh</span>
          </button>
        )}

        <div className="grid grid-cols-3 gap-0.5 p-0.5 rounded-lg bg-[#F1F5F9] border border-[#E2E8F0] text-[11px]">
          {(
            [
              ["tat_ca", `Tất cả ${ds.length}`],
              ["can", "Cần xem"],
              ["chua", "Chưa duyệt"],
            ] as const
          ).map(([id, chu]) => (
            <button
              key={id}
              onClick={() => setLoc(id)}
              className={`px-1.5 py-1 rounded-md font-semibold ${
                loc === id ? "bg-white text-[#0369A1] shadow-sm" : "text-[#64748B]"
              }`}
            >
              {chu}
            </button>
          ))}
        </div>
      </div>

      {/* Danh sách */}
      <div className="flex-1 min-h-0 overflow-y-auto p-2.5 space-y-2">
        {/* Tầng 4.5 Khôi phục bỏ sót chủ động */}
        {dsBoSotTang45.length > 0 && (
          <div className="rounded-xl border border-[#F5E1A4] bg-[#FEF9E7] p-2.5 space-y-2 shadow-2xs">
            <div className="flex items-center justify-between gap-1.5">
              <span className="inline-flex items-center gap-1 text-[11px] font-bold text-[#92400E]">
                <Sparkles size={12} className="text-[#D97706]" />
                Tầng 4.5 · Khôi phục bỏ sót ({dsBoSotTang45.length})
              </span>
              <span className="text-[10px] text-[#A16207]">Quét từ điển y khoa</span>
            </div>
            <div className="space-y-1.5">
              {dsBoSotTang45.map((muc, idx) => {
                const khoa = `${note.caseId || "ca"}_${idx}_${muc.luot ?? 0}_${muc.noi_dung_goi_y || ""}`;
                const daThem = Boolean(daBoSungTang45[khoa]);
                const loaiKey = String(muc.loai_thong_tin || "").toLowerCase();
                const nhanLoai = NHAN_LOAI_BO_SOT[loaiKey] || {
                  chu: muc.loai_thong_tin || "Thông tin bỏ sót",
                  lop: "bg-[#FEF3C7] text-[#92400E] border-[#FDE68A]",
                };
                return (
                  <div
                    key={khoa}
                    className="rounded-lg bg-white border border-[#F2DFA8] p-2 space-y-1.5 text-left"
                  >
                    <div className="flex items-center justify-between gap-1.5 flex-wrap">
                      <span
                        className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold border ${nhanLoai.lop}`}
                      >
                        {nhanLoai.chu}
                      </span>
                      {muc.luot !== undefined && (
                        <span className="font-mono text-[10.5px] font-semibold px-1.5 py-0.5 rounded bg-[#F0F9FF] text-[#0284C7] border border-[#BAE6FD]">
                          [T{muc.luot}]
                        </span>
                      )}
                    </div>
                    <p className="text-[12px] font-semibold text-[#0C2340] leading-snug">
                      {muc.noi_dung_goi_y || "(Chưa có nội dung gợi ý)"}
                    </p>
                    {muc.trich_dan_nguyen_van && (
                      <p className="text-[11px] text-[#475569] italic leading-snug">
                        “{muc.trich_dan_nguyen_van}”
                      </p>
                    )}
                    <div className="pt-0.5">
                      <button
                        type="button"
                        disabled={daThem}
                        onClick={() => {
                          setDaBoSungTang45((cu) => ({ ...cu, [khoa]: true }));
                          onKhoiPhucBoSot?.(muc);
                        }}
                        className={`inline-flex items-center gap-1 px-2 py-1 rounded-md text-[11px] font-semibold border transition-colors ${
                          daThem
                            ? "bg-[#E6F7F0] border-[#A7E3C9] text-[#0D6B50] cursor-default"
                            : "bg-[#0284C7] hover:bg-[#0369A1] border-[#0284C7] text-white cursor-pointer"
                        }`}
                      >
                        {daThem ? (
                          <>
                            <Check size={11} />
                            <span>Đã bổ sung ✓</span>
                          </>
                        ) : (
                          <>
                            <Plus size={11} />
                            <span>+ Đưa vào bệnh án</span>
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {hien.length === 0 && (
          <p className="text-[12px] text-[#64748B] text-center py-6">Không còn mệnh đề nào trong mục này.</p>
        )}
        {hien.map((p) => {
          const t = tt(p);
          const nhan = NHAN[t];
          const chu = banSua[p.id] || p.text;
          const chon = chonId === p.id;
          const cb = p.warning && p.warning.kind !== "can_xem" ? p.warning : null;
          return (
            <div
              key={p.id}
              ref={(el) => {
                if (el) theRef.current.set(p.id, el);
                else theRef.current.delete(p.id);
              }}
              onClick={(e) => {
                if ((e.target as HTMLElement).closest("button,input")) return;
                onChon(chon ? null : p.id);
              }}
              className={`rounded-xl border p-2.5 cursor-pointer transition-shadow ${nhan.the} ${
                chon ? "ring-2 ring-[#0284C7] shadow-md" : "hover:shadow-sm"
              }`}
            >
              <div className="flex items-start justify-between gap-2">
                <span
                  className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded-md text-[10.5px] font-semibold ${nhan.lop}`}
                >
                  {t === "canh" ? (
                    <AlertTriangle size={11} />
                  ) : t === "luuy" ? (
                    <Info size={11} />
                  ) : t === "bo" ? (
                    <Trash2 size={11} />
                  ) : (
                    <CheckCircle2 size={11} />
                  )}
                  {nhan.chu}
                </span>
                <span className="text-[10px] text-[#94A3B8] truncate">{p.section}</span>
              </div>

              {suaId === p.id ? (
                <div className="mt-1.5 flex gap-1">
                  <input
                    autoFocus
                    value={chuSua}
                    onChange={(e) => setChuSua(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") luuSua(p.id);
                      if (e.key === "Escape") setSuaId(null);
                    }}
                    className="flex-1 min-w-0 text-[13px] border border-[#BAE6FD] rounded-md px-2 py-1 bg-white"
                  />
                  <button
                    onClick={() => luuSua(p.id)}
                    className="px-2 rounded-md bg-[#0284C7] text-white text-[11px] font-semibold"
                  >
                    Lưu
                  </button>
                </div>
              ) : (
                <p
                  className={`mt-1.5 text-[13px] font-semibold leading-snug text-[#0C2340] ${
                    t === "bo" ? "line-through text-[#94A3B8]" : ""
                  }`}
                >
                  {chu}
                </p>
              )}
              {banSua[p.id] && <p className="text-[10.5px] text-[#A16207] mt-0.5">Máy viết: “{p.text}”</p>}

              {cb && t !== "bo" && (
                <div
                  className={`mt-1.5 text-[11.5px] leading-snug ${
                    t === "canh" ? "text-[#9B2C2C]" : "text-[#7C4A03]"
                  }`}
                >
                  <strong>{cb.title}</strong> — {cb.reason}
                </div>
              )}

              {/* Căn cứ: lượt hội thoại, bấm để xem nguyên câu hoặc nghe lại 3s */}
              {(() => {
                const asr = phanTichVungMoAsr(p, segments);
                return (
                  <div className="flex flex-wrap gap-1 mt-1.5">
                    {p.evidenceTurns.length === 0 && (
                      <span className="px-1.5 py-0.5 rounded-md bg-[#FDE8E8] text-[#B4232C] text-[10.5px] font-semibold">
                        Không dẫn lượt nào
                      </span>
                    )}
                    {p.evidenceTurns.map((so) => {
                      const coAmThanh = Boolean(audioUrl && khoangPhatLaiLuot(so, segments));
                      const dangPhat = dangPhatLuot === so;
                      return (
                        <span key={so} className="inline-flex items-center gap-0.5">
                          <button
                            onClick={() => setMoLuot((m) => ({ ...m, [p.id]: !m[p.id] }))}
                            className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-md bg-white border border-[#E2E8F0] text-[10.5px] text-[#475569] hover:border-[#0284C7]"
                          >
                            <MessageSquare size={10} /> lượt {so}
                          </button>
                          {coAmThanh && (
                            <button
                              type="button"
                              onClick={() => phatDoanLuot(so)}
                              title={dangPhat ? "Dừng nghe" : "Nghe lại đoạn ghi âm gốc của lượt này"}
                              className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded-md border text-[10.5px] font-semibold ${
                                dangPhat
                                  ? "bg-[#0284C7] text-white border-[#0284C7]"
                                  : "bg-[#F0F9FF] text-[#0369A1] border-[#BAE6FD] hover:bg-[#E0F2FE]"
                              }`}
                            >
                              {dangPhat ? <Square size={9} /> : <Play size={9} />}
                              {dangPhat ? "Dừng" : "Nghe lại"}
                            </button>
                          )}
                        </span>
                      );
                    })}
                    {asr.nhan && t !== "bo" && (
                      <span className="px-1.5 py-0.5 rounded-md bg-[#FFF7ED] border border-[#FED7AA] text-[#C2410C] text-[10.5px] font-semibold">
                        {asr.nhan}
                      </span>
                    )}
                    {p.subject && (
                      <span className="px-1.5 py-0.5 rounded-md bg-[#E0EDFF] text-[#1E4E9C] text-[10.5px]">
                        nói về: {p.subject}
                      </span>
                    )}
                    {p.negated && (
                      <span className="px-1.5 py-0.5 rounded-md bg-[#FEE2E2] text-[#991B1B] text-[10.5px] font-bold">
                        phủ định
                      </span>
                    )}
                  </div>
                );
              })()}
              {moLuot[p.id] && p.evidenceTurns.length > 0 && (
                <div className="mt-1.5 rounded-lg bg-white border border-[#E2E8F0] p-2 text-[11.5px] text-[#334155] space-y-1">
                  {p.evidenceTurns.map((so) => {
                    const l = luot.find((x) => x.so === so);
                    return (
                      <p key={so}>
                        <span className="font-mono text-[#0369A1]">lượt {so}</span> ·{" "}
                        {l ? `${l.vai ? `${l.vai}: ` : ""}${l.chu}` : "(không có trong bản chép)"}
                      </p>
                    );
                  })}
                </div>
              )}

              {/* Thao tác */}
              {suaId !== p.id && (
                <div className="flex flex-wrap items-center gap-1 mt-2">
                  <button
                    onClick={() => dat(p.id, "giu")}
                    className={`inline-flex items-center gap-1 px-2 py-1 rounded-lg text-[11px] font-semibold border ${
                      quyet[p.id] === "giu"
                        ? "bg-[#0D9488] text-white border-[#0D9488]"
                        : "bg-white border-[#CCE3F0] text-[#0C2340] hover:border-[#0D9488]"
                    }`}
                  >
                    <Check size={12} /> {t === "canh" ? "Xác nhận" : "Giữ"}
                  </button>
                  <button
                    onClick={() => {
                      setSuaId(p.id);
                      setChuSua(chu);
                    }}
                    className={`inline-flex items-center gap-1 px-2 py-1 rounded-lg text-[11px] font-semibold border ${
                      quyet[p.id] === "sua"
                        ? "bg-[#FEF6E0] border-[#F2DFA8] text-[#A16207]"
                        : "bg-white border-[#CCE3F0] text-[#0C2340] hover:border-[#0284C7]"
                    }`}
                  >
                    <Pencil size={12} /> Sửa
                  </button>
                  <button
                    onClick={() => dat(p.id, "bo")}
                    className={`inline-flex items-center gap-1 px-2 py-1 rounded-lg text-[11px] font-semibold border ${
                      quyet[p.id] === "bo"
                        ? "bg-[#FDE8E8] border-[#F5C2C2] text-[#B4232C]"
                        : "bg-white border-[#CCE3F0] text-[#0C2340] hover:border-[#E86A6A]"
                    }`}
                  >
                    <Trash2 size={12} /> Bỏ
                  </button>
                  {quyet[p.id] && quyet[p.id] !== "cho" && (
                    <button
                      onClick={() => dat(p.id, "cho")}
                      title="Bỏ đánh dấu"
                      className="p-1 rounded-md text-[#64748B] hover:bg-[#F1F5F9]"
                    >
                      <Undo2 size={12} />
                    </button>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Chú giải phím tắt nhanh */}
      <div className="px-3 py-1.5 border-t border-[#E2ECF3] bg-white space-y-0.5">
        <p
          className="text-[10.5px] font-mono text-[#0369A1] font-semibold"
          title="Bấm mệnh đề để thấy câu đó trong bản nháp; bấm câu trong bản nháp để tìm mệnh đề. Đỏ: cần xác nhận · vàng: có lưu ý · xanh: không cảnh báo."
        >
          J/K chọn · Enter giữ · E sửa · ⌫ bỏ · Space nghe
        </p>
      </div>
    </aside>
  );
};
