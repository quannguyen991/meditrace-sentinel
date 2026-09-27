import React, { useEffect, useMemo, useRef, useState } from "react";
import {
  Check, CheckCircle2, Info, Maximize2, MessageSquare, Pencil, Trash2, Undo2, X, AlertTriangle,
} from "lucide-react";
import { NoteMeta, Proposition, Quyet, canXacNhan, tachLuot } from "./VerificationView";

/**
 * NGĂN DUYỆT CẠNH BẢN NHÁP (24/09). Bác sĩ vừa đọc bản nháp vừa duyệt từng mệnh đề, không phải
 * chuyển màn. Bấm một mệnh đề -> câu đó sáng lên trong bản nháp (NoteEditorView tô theo `danhDau`);
 * bấm một câu trong bản nháp -> ngăn này cuộn tới mệnh đề đó. Giữ / sửa / bỏ dùng chung trạng thái
 * với màn "Duyệt từng mệnh đề" đầy đủ (có dây nối tới lượt hội thoại).
 */

export type TrangThaiMD = "canh" | "luuy" | "ok" | "giu" | "sua" | "bo";

/** Trạng thái hiển thị của một mệnh đề — dùng chung cho ngăn duyệt và màu tô trong bản nháp. */
export function trangThaiMD(p: Proposition, q: Quyet | undefined, boQuaCanhBao = false): TrangThaiMD {
  if (q === "bo") return "bo";
  if (q === "giu") return "giu";
  if (q === "sua") return "sua";
  if (canXacNhan(p)) return "canh";
  if (!boQuaCanhBao && p.warning && p.warning.kind !== "can_xem") return "luuy";
  return "ok";
}

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
}

export const DuyetBenCanh: React.FC<Props> = ({
  note, quyet, setQuyet, banSua, setBanSua, chonId, onChon, onMoToanMan, onDong,
}) => {
  const [loc, setLoc] = useState<Loc>("tat_ca");
  const [suaId, setSuaId] = useState<number | null>(null);
  const [chuSua, setChuSua] = useState("");
  const [moLuot, setMoLuot] = useState<Record<number, boolean>>({});
  const theRef = useRef(new Map<number, HTMLDivElement>());

  const luot = useMemo(() => tachLuot(note.transcript), [note.transcript]);
  // Thứ tự như trong bản nháp: mệnh đề cần xác nhận lên trước để bác sĩ xử lý trước.
  const ds = useMemo(() => {
    const goc = note.propositions || [];
    const hang = (p: Proposition) => (canXacNhan(p) ? 0 : p.warning && p.warning.kind !== "can_xem" ? 1 : 2);
    return [...goc].sort((a, b) => hang(a) - hang(b) || a.id - b.id);
  }, [note.propositions]);

  const tt = (p: Proposition) => trangThaiMD(p, quyet[p.id]);
  const hien = ds.filter((p) =>
    loc === "tat_ca" ? true : loc === "can" ? ["canh", "luuy"].includes(tt(p)) : !quyet[p.id] || quyet[p.id] === "cho");
  const daDuyet = ds.filter((p) => quyet[p.id] && quyet[p.id] !== "cho").length;
  const conCan = ds.filter((p) => tt(p) === "canh").length;

  // Được chọn từ bản nháp -> cuộn tới thẻ.
  useEffect(() => {
    if (chonId === null) return;
    const h = requestAnimationFrame(() => {
      const el = theRef.current.get(chonId);
      if (el?.offsetParent) el.scrollIntoView({ block: "nearest", behavior: "smooth" });   // ngăn đang ẩn thì thôi
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

  return (
    <aside className="flex flex-col min-h-0 h-full bg-[#F8FBFC] border-t @4xl:border-t-0 @4xl:border-l border-[#BAE6FD]">
      {/* Đầu ngăn */}
      <div className="px-3 pt-3 pb-2 border-b border-[#E2ECF3] bg-white space-y-2">
        <div className="flex items-center justify-between gap-2">
          <h2 className="text-[13px] font-bold text-[#0C2340]">Duyệt từng mệnh đề</h2>
          <div className="flex items-center gap-0.5">
            <button onClick={onMoToanMan} title="Mở màn duyệt đầy đủ (dây nối tới lượt hội thoại)"
              className="p-1.5 rounded-md text-[#64748B] hover:bg-[#E0F2FE] hover:text-[#0369A1]">
              <Maximize2 size={14} />
            </button>
            <button onClick={onDong} title="Đóng ngăn duyệt" className="p-1.5 rounded-md text-[#64748B] hover:bg-[#E0F2FE] hover:text-[#0369A1]">
              <X size={14} />
            </button>
          </div>
        </div>
        <div>
          <div className="flex items-center justify-between text-[11px] text-[#0C4A6E]">
            <span><strong className="tabular-nums">{daDuyet}/{ds.length}</strong> đã duyệt</span>
            {conCan > 0 && <span className="text-[#B4232C] font-semibold">{conCan} cần xác nhận</span>}
          </div>
          <div className="w-full h-1 rounded-full bg-[#E0F2FE] overflow-hidden mt-1">
            <div className="h-full bg-[#0284C7] rounded-full transition-all" style={{ width: `${ds.length ? (daDuyet / ds.length) * 100 : 0}%` }} />
          </div>
        </div>
        <div className="grid grid-cols-3 gap-0.5 p-0.5 rounded-lg bg-[#F1F5F9] border border-[#E2E8F0] text-[11px]">
          {([["tat_ca", `Tất cả ${ds.length}`], ["can", "Cần xem"], ["chua", "Chưa duyệt"]] as const).map(([id, chu]) => (
            <button key={id} onClick={() => setLoc(id)}
              className={`px-1.5 py-1 rounded-md font-semibold ${loc === id ? "bg-white text-[#0369A1] shadow-sm" : "text-[#64748B]"}`}>
              {chu}
            </button>
          ))}
        </div>
      </div>

      {/* Danh sách */}
      <div className="flex-1 min-h-0 overflow-y-auto p-2.5 space-y-2">
        {hien.length === 0 && <p className="text-[12px] text-[#64748B] text-center py-6">Không còn mệnh đề nào trong mục này.</p>}
        {hien.map((p) => {
          const t = tt(p);
          const nhan = NHAN[t];
          const chu = banSua[p.id] || p.text;
          const chon = chonId === p.id;
          const cb = p.warning && p.warning.kind !== "can_xem" ? p.warning : null;
          return (
            <div
              key={p.id}
              ref={(el) => { if (el) theRef.current.set(p.id, el); else theRef.current.delete(p.id); }}
              onClick={(e) => {
                if ((e.target as HTMLElement).closest("button,input")) return;
                onChon(chon ? null : p.id);
              }}
              className={`rounded-xl border p-2.5 cursor-pointer transition-shadow ${nhan.the} ${chon ? "ring-2 ring-[#0284C7] shadow-md" : "hover:shadow-sm"}`}
            >
              <div className="flex items-start justify-between gap-2">
                <span className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded-md text-[10.5px] font-semibold ${nhan.lop}`}>
                  {t === "canh" ? <AlertTriangle size={11} /> : t === "luuy" ? <Info size={11} /> : t === "bo" ? <Trash2 size={11} /> : <CheckCircle2 size={11} />}
                  {nhan.chu}
                </span>
                <span className="text-[10px] text-[#94A3B8] truncate">{p.section}</span>
              </div>

              {suaId === p.id ? (
                <div className="mt-1.5 flex gap-1">
                  <input
                    autoFocus value={chuSua} onChange={(e) => setChuSua(e.target.value)}
                    onKeyDown={(e) => { if (e.key === "Enter") luuSua(p.id); if (e.key === "Escape") setSuaId(null); }}
                    className="flex-1 min-w-0 text-[13px] border border-[#BAE6FD] rounded-md px-2 py-1 bg-white"
                  />
                  <button onClick={() => luuSua(p.id)} className="px-2 rounded-md bg-[#0284C7] text-white text-[11px] font-semibold">Lưu</button>
                </div>
              ) : (
                <p className={`mt-1.5 text-[13px] font-semibold leading-snug text-[#0C2340] ${t === "bo" ? "line-through text-[#94A3B8]" : ""}`}>{chu}</p>
              )}
              {banSua[p.id] && <p className="text-[10.5px] text-[#A16207] mt-0.5">Máy viết: “{p.text}”</p>}

              {cb && t !== "bo" && (
                <div className={`mt-1.5 text-[11.5px] leading-snug ${t === "canh" ? "text-[#9B2C2C]" : "text-[#7C4A03]"}`}>
                  <strong>{cb.title}</strong> — {cb.reason}
                </div>
              )}

              {/* Căn cứ: lượt hội thoại, bấm để xem nguyên câu */}
              <div className="flex flex-wrap gap-1 mt-1.5">
                {p.evidenceTurns.length === 0 && <span className="px-1.5 py-0.5 rounded-md bg-[#FDE8E8] text-[#B4232C] text-[10.5px] font-semibold">Không dẫn lượt nào</span>}
                {p.evidenceTurns.map((so) => (
                  <button key={so} onClick={() => setMoLuot((m) => ({ ...m, [p.id]: !m[p.id] }))}
                    className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-md bg-white border border-[#E2E8F0] text-[10.5px] text-[#475569] hover:border-[#0284C7]">
                    <MessageSquare size={10} /> lượt {so}
                  </button>
                ))}
                {p.subject && <span className="px-1.5 py-0.5 rounded-md bg-[#E0EDFF] text-[#1E4E9C] text-[10.5px]">nói về: {p.subject}</span>}
                {p.negated && <span className="px-1.5 py-0.5 rounded-md bg-[#FEE2E2] text-[#991B1B] text-[10.5px] font-bold">phủ định</span>}
              </div>
              {moLuot[p.id] && p.evidenceTurns.length > 0 && (
                <div className="mt-1.5 rounded-lg bg-white border border-[#E2E8F0] p-2 text-[11.5px] text-[#334155] space-y-1">
                  {p.evidenceTurns.map((so) => {
                    const l = luot.find((x) => x.so === so);
                    return <p key={so}><span className="font-mono text-[#0369A1]">lượt {so}</span> · {l ? `${l.vai ? `${l.vai}: ` : ""}${l.chu}` : "(không có trong bản chép)"}</p>;
                  })}
                </div>
              )}

              {/* Thao tác */}
              {suaId !== p.id && (
                <div className="flex flex-wrap items-center gap-1 mt-2">
                  <button onClick={() => dat(p.id, "giu")}
                    className={`inline-flex items-center gap-1 px-2 py-1 rounded-lg text-[11px] font-semibold border ${quyet[p.id] === "giu" ? "bg-[#0D9488] text-white border-[#0D9488]" : "bg-white border-[#CCE3F0] text-[#0C2340] hover:border-[#0D9488]"}`}>
                    <Check size={12} /> {t === "canh" ? "Xác nhận" : "Giữ"}
                  </button>
                  <button onClick={() => { setSuaId(p.id); setChuSua(chu); }}
                    className={`inline-flex items-center gap-1 px-2 py-1 rounded-lg text-[11px] font-semibold border ${quyet[p.id] === "sua" ? "bg-[#FEF6E0] border-[#F2DFA8] text-[#A16207]" : "bg-white border-[#CCE3F0] text-[#0C2340] hover:border-[#0284C7]"}`}>
                    <Pencil size={12} /> Sửa
                  </button>
                  <button onClick={() => dat(p.id, "bo")}
                    className={`inline-flex items-center gap-1 px-2 py-1 rounded-lg text-[11px] font-semibold border ${quyet[p.id] === "bo" ? "bg-[#FDE8E8] border-[#F5C2C2] text-[#B4232C]" : "bg-white border-[#CCE3F0] text-[#0C2340] hover:border-[#E86A6A]"}`}>
                    <Trash2 size={12} /> Bỏ
                  </button>
                  {quyet[p.id] && quyet[p.id] !== "cho" && (
                    <button onClick={() => dat(p.id, "cho")} title="Bỏ đánh dấu" className="p-1 rounded-md text-[#64748B] hover:bg-[#F1F5F9]">
                      <Undo2 size={12} />
                    </button>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
      <p className="hidden @4xl:block px-3 py-1.5 text-[10px] text-[#64748B] border-t border-[#E2ECF3] bg-white leading-snug">
        Bấm mệnh đề để thấy câu đó trong bản nháp; bấm câu trong bản nháp để tìm mệnh đề. Đỏ: cần xác nhận · vàng: có lưu ý · xanh: không cảnh báo.
      </p>
    </aside>
  );
};
