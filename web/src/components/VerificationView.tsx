/**
 * Màn Duyệt — chỗ thể hiện điểm riêng của MediTrace.
 *
 * Mỗi dòng trong bản nháp là một MỆNH ĐỀ, kèm: nói về ai, mức chắc chắn, và LƯỢT HỘI THOẠI
 * làm căn cứ. Bố cục hai cột: lời thoại bên trái, mệnh đề bên phải, DÂY NỐI từ lượt làm căn cứ
 * sang mệnh đề — bác sĩ lần theo dây để đối chiếu. Dây đỏ = máy đưa sang "cần xác nhận".
 * Dữ liệu lấy từ `/api/generate-note` (nhánh C_khoa của dự án), không có gì gán cứng ở đây.
 *
 * Nhãn `source` phải luôn hiện: mô hình vừa chạy, hay lấy từ bộ đệm, hay bản chạy trước.
 */
import React, { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import {
  ArrowLeft, Check, ChevronDown, ChevronUp, FileText, HelpCircle, Pencil, ShieldAlert, Trash2, Undo2,
  MessageSquare, ListTree, AlertTriangle, CheckCircle2, Users, Sparkles, Pill, Clock, CalendarClock,
  GitCompare, SearchX, Quote, EyeOff, Copy, Link2, Mic, Eye, EyeOff as BoQua, Info,
} from "lucide-react";

export interface Proposition {
  id: number;
  text: string;
  section: string;
  status: "than" | "can_xac_nhan";
  gateReason?: string | null;
  subject?: string | null;
  negated?: boolean;
  certainty?: string | null;
  situation?: string | null;
  time?: string | null;
  drug?: string | null;
  evidenceTurns: number[];
  quotes: string[];
  /** Lop canh bao: canh bao chinh, toi da 2 canh bao khac nhom, trang thai theo chinh sach D. */
  warning?: CanhBaoUI | null;
  otherWarnings?: CanhBaoUI[];
  warningTags?: string[];
  stateD?: string | null;
  stateDReason?: string | null;
}

export interface CanhBaoUI {
  code: string;
  group: string;
  groupName: string;
  title: string;
  explanation: string;
  reason: string;
  turns: number[];
  quotes: string[];
  severity: "cao" | "trung" | "thap";
  uncertainty: "cao" | "trung" | "thap";
  kind: "loi_phat_hien" | "nghi_rui_ro" | "can_xem";
  reliability: string;
  affectsState: boolean;
  tags?: string[];
  tagTitles?: string[];
}

export interface NoteMeta {
  content: string;
  propositions: Proposition[];
  questions: string[];
  needsConfirmCount: number;
  caseId?: string;
  branch?: string;
  policy?: string;
  source?: "mo_hinh" | "bo_dem" | "chay_truoc" | string;
  seconds?: number;
  transcript?: string;
  caseWarnings?: CanhBaoUI[];
  warningPolicy?: string | null;
}

export interface CauHoiNgoai {
  hoi: string;
  /** Cách hỏi hoặc thang đo, ngắn. */
  goi_y?: string;
  nhom?: string;
  vi_sao?: string;
  luot?: number[];
}

export type Quyet = "cho" | "giu" | "sua" | "bo";

const NHAN_NGUON: Record<string, { chu: string; mau: string }> = {
  mo_hinh: { chu: "Mô hình vừa chạy", mau: "bg-[#E6F4F1] text-[#0D9488] border-[#BCE3DB]" },
  bo_dem: { chu: "Khâu trích lấy từ bộ đệm đã chạy trước", mau: "bg-[#FEF6E0] text-[#A16207] border-[#F2DFA8]" },
  chay_truoc: { chu: "Bản ghi đã chạy từ trước, không tính lại", mau: "bg-[#FDE8E8] text-[#B4232C] border-[#F5C2C2]" },
};

// Màu dây và thẻ. Xanh = máy không cảnh báo; đỏ = máy đưa sang cần xác nhận; xám = bác sĩ đã bỏ.
const MAU = { ok: "#34B889", canh: "#E86A6A", bo: "#CBD5E1", mo: "#E2E8F0" };

/** Tách bản nháp thành các mục theo dòng tiêu đề viết hoa. */
function tachMuc(van: string) {
  const ra: Array<{ ten: string; dong: string[] }> = [];
  for (const dong of (van || "").split("\n")) {
    const d = dong.trim();
    if (!d) continue;
    const laTieuDe = d === d.toLocaleUpperCase("vi") && /\p{L}/u.test(d) && d.length < 60;
    if (laTieuDe) ra.push({ ten: d, dong: [] });
    else if (ra.length) ra[ra.length - 1].dong.push(d);
    else ra.push({ ten: "BẢN NHÁP", dong: [d] });
  }
  return ra;
}

type Luot = { so: number; vai: string; chu: string };

/** Lời thoại → từng lượt (đánh số từ 1, như máy dẫn), tách vai ở đầu dòng. */
export function tachLuot(transcript?: string): Luot[] {
  return (transcript || "")
    .split("\n")
    .filter((x) => x.trim())
    .map((d, i) => {
      const m = d.trim().match(/^([^:]{2,20}):\s*(.*)$/);
      return { so: i + 1, vai: m ? m[1].trim() : "", chu: m ? m[2] : d.trim() };
    });
}

const MAU_VAI = (vai: string) => {
  const v = vai.toLowerCase();
  if (v.startsWith("bác sĩ")) return { nen: "bg-[#F1F5F9]", vien: "border-[#E2E8F0]", chu: "text-[#475569]" };
  if (v.startsWith("bệnh nhân")) return { nen: "bg-[#E0F2FE]", vien: "border-[#BAE6FD]", chu: "text-[#0369A1]" };
  if (v.startsWith("người nhà")) return { nen: "bg-[#FEF3E2]", vien: "border-[#F8DDB0]", chu: "text-[#9A5B00]" };
  return { nen: "bg-white", vien: "border-[#E2E8F0]", chu: "text-[#64748B]" };
};

const MUC_DO: Record<string, string> = { cao: "nghiêm trọng nếu sai", trung: "vừa", thap: "nhẹ" };
const CAN_CU: Record<string, string> = { thap: "căn cứ rõ", trung: "căn cứ vừa", cao: "căn cứ còn mơ hồ" };
const KET_LUAN: Record<string, string> = {
  loi_phat_hien: "Có dấu hiệu sai",
  nghi_rui_ro: "Nghi ngờ",
  can_xem: "Lưu ý",
};
const ICON_NHOM: Record<string, React.ElementType> = {
  SUBJECT_ATTRIBUTION: Users,
  NEGATION_ASSERTION: AlertTriangle,
  ENTITY_VALUE: Pill,
  TEMPORAL: Clock,
  PLAN_FACT_CONDITIONAL: CalendarClock,
  STATE_UPDATE: GitCompare,
  UNSUPPORTED: SearchX,
  EVIDENCE_PROVENANCE: Quote,
  OMISSION: EyeOff,
  QUALITY: Copy,
  RELATION_CAUSALITY: Link2,
  ASR_UPSTREAM: Mic,
};

/** Trang thai hien thi: theo chinh sach D neu co, khong thi theo muc cua ban nhap (C). */
export function canXacNhan(p: Proposition) {
  return p.stateD ? p.stateD === "cần xác nhận" : p.status === "can_xac_nhan";
}

interface Props {
  note: NoteMeta | null;
  onBack: () => void;
  patientIdentifier?: string;
  /** Có bật mô hình ngoài không — chỉ khi bật mới hiện nút gợi ý câu hỏi. */
  allowExternal?: boolean;
  /** Gọi mô hình ngoài đặt câu hỏi; trả null nếu lỗi (lỗi đã hiện ở thanh báo). */
  onAskExternalQuestions?: () => Promise<{ questions: CauHoiNgoai[]; model: string } | null>;
  /** Quyết định giữ/sửa/bỏ do App giữ — dùng chung với ngăn duyệt cạnh bản nháp. Không truyền thì tự giữ. */
  quyetChung?: Record<number, Quyet>;
  setQuyetChung?: React.Dispatch<React.SetStateAction<Record<number, Quyet>>>;
  banSuaChung?: Record<number, string>;
  setBanSuaChung?: React.Dispatch<React.SetStateAction<Record<number, string>>>;
}

type Chon = { loai: "p"; id: number } | { loai: "t"; so: number } | null;
type Day = { d: string; mau: string; sang: boolean; x1: number; y1: number; x2: number; y2: number; key: string };

export const VerificationView: React.FC<Props> = ({
  note,
  onBack,
  patientIdentifier,
  allowExternal,
  onAskExternalQuestions,
  quyetChung,
  setQuyetChung,
  banSuaChung,
  setBanSuaChung,
}) => {
  const [cauHoiNgoai, setCauHoiNgoai] = useState<{ questions: CauHoiNgoai[]; model: string } | null>(null);
  const [dangHoi, setDangHoi] = useState(false);
  const [quyetRieng, setQuyetRieng] = useState<Record<number, Quyet>>({});
  const quyet = quyetChung ?? quyetRieng;
  const setQuyet = setQuyetChung ?? setQuyetRieng;
  const [suaId, setSuaId] = useState<number | null>(null);
  const [chuSua, setChuSua] = useState("");
  const [banSuaRieng, setBanSuaRieng] = useState<Record<number, string>>({});
  const banSua = banSuaChung ?? banSuaRieng;
  const setBanSua = setBanSuaChung ?? setBanSuaRieng;
  const [moBanNhap, setMoBanNhap] = useState(false);
  const [xep, setXep] = useState<"luot" | "muc">("luot");
  const [chon, setChon] = useState<Chon>(null);
  const [ghim, setGhim] = useState<Chon>(null);
  const [day, setDay] = useState<Day[]>([]);
  const [khung, setKhung] = useState({ w: 0, h: 0 });
  const [rong, setRong] = useState(false);

  const khungRef = useRef<HTMLDivElement>(null);
  const luotRef = useRef(new Map<number, HTMLDivElement>());
  const mdRef = useRef(new Map<number, HTMLDivElement>());

  useEffect(() => {
    // Trạng thái dùng chung do App đặt lại khi đổi ca / tạo lại bản nháp.
    if (!setQuyetChung) setQuyetRieng({});
    if (!setBanSuaChung) setBanSuaRieng({});
    setSuaId(null);
    setCauHoiNgoai(null);
    setGhim(null);
    setBoQua({});
  }, [note?.caseId, note?.content]);

  const luot = useMemo(() => tachLuot(note?.transcript), [note?.transcript]);
  const muc = useMemo(() => tachMuc(note?.content || ""), [note?.content]);
  const ds = useMemo(() => {
    const goc = note?.propositions || [];
    if (xep === "muc") return goc;
    const dau = (p: Proposition) => (p.evidenceTurns.length ? Math.min(...p.evidenceTurns) : 1e9);
    return [...goc].sort((a, b) => dau(a) - dau(b) || a.id - b.id);
  }, [note?.propositions, xep]);

  // Lượt nào được mệnh đề nào dẫn — để bấm vào lượt thì sáng các mệnh đề liên quan.
  const menhDeCuaLuot = useMemo(() => {
    const m = new Map<number, number[]>();
    for (const p of ds) for (const t of p.evidenceTurns) m.set(t, [...(m.get(t) || []), p.id]);
    return m;
  }, [ds]);

  const dangChon = chon || ghim;
  const pSang = (p: Proposition) =>
    !dangChon || (dangChon.loai === "p" ? dangChon.id === p.id : p.evidenceTurns.includes(dangChon.so));
  const tSang = (so: number) =>
    !dangChon || (dangChon.loai === "t" ? dangChon.so === so : !!ds.find((p) => p.id === dangChon.id)?.evidenceTurns.includes(so));

  const mauMD = (p: Proposition) => {
    const q = quyet[p.id] || "cho";
    if (q === "bo") return MAU.bo;
    return canXacNhan(p) && q !== "giu" && q !== "sua" ? MAU.canh : MAU.ok;
  };
  const [boQua, setBoQua] = useState<Record<number, boolean>>({});
  const [moKhac, setMoKhac] = useState<Record<number, boolean>>({});
  // Luot bi bo sot (canh bao toan ca) -> danh dau o cot hoi thoai
  const luotBoSot = useMemo(() => {
    const m = new Map<number, CanhBaoUI>();
    for (const c of note?.caseWarnings || []) for (const t of c.turns) if (!m.has(t)) m.set(t, c);
    return m;
  }, [note?.caseWarnings]);
  const xemLuot = (so: number) => {
    setGhim({ loai: "t", so });
    luotRef.current.get(so)?.scrollIntoView({ behavior: "smooth", block: "center" });
  };

  // Vẽ dây: đo vị trí thật của từng lượt và từng thẻ mệnh đề trong khung chung.
  const ve = useCallback(() => {
    const k = khungRef.current;
    if (!k) return;
    const laRong = window.matchMedia("(min-width: 1024px)").matches;
    setRong(laRong);
    if (!laRong) {
      setDay([]);
      return;
    }
    const gk = k.getBoundingClientRect();
    setKhung({ w: gk.width, h: gk.height });
    const ra: Day[] = [];
    for (const p of ds) {
      const the = mdRef.current.get(p.id);
      if (!the) continue;
      const r2 = the.getBoundingClientRect();
      const x2 = r2.left - gk.left;
      const y2 = r2.top - gk.top + 26;
      for (const t of p.evidenceTurns) {
        const o = luotRef.current.get(t);
        if (!o) continue;
        const r1 = o.getBoundingClientRect();
        const x1 = r1.right - gk.left;
        const y1 = r1.top - gk.top + Math.min(r1.height / 2, 26);
        const dx = Math.max(24, (x2 - x1) / 2);
        const sang = pSang(p) && tSang(t);
        ra.push({
          key: `${t}-${p.id}`, x1, y1, x2, y2, sang, mau: mauMD(p),
          d: `M ${x1} ${y1} C ${x1 + dx} ${y1}, ${x2 - dx} ${y2}, ${x2} ${y2}`,
        });
      }
    }
    // Dây đang sáng vẽ sau cùng để nằm trên.
    ra.sort((a, b) => Number(a.sang) - Number(b.sang));
    setDay(ra);
  }, [ds, quyet, chon, ghim]);

  useLayoutEffect(() => {
    ve();
  }, [ve, luot, banSua, suaId, moBanNhap]);

  useEffect(() => {
    const k = khungRef.current;
    if (!k) return;
    const ro = new ResizeObserver(() => ve());
    ro.observe(k);
    window.addEventListener("resize", ve);
    return () => {
      ro.disconnect();
      window.removeEventListener("resize", ve);
    };
  }, [ve]);

  if (!note) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center gap-3 bg-[#F0F7FA] text-center px-8">
        <ShieldAlert size={30} className="text-[#0284C7]" />
        <h1 className="text-xl font-bold text-[#0F172A]">Chưa có bản nháp nào để duyệt</h1>
        <p className="text-sm text-[#475569] max-w-md">
          Tạo bản nháp từ một ca khám trước: mở tab Lời thoại, rồi bấm tạo hồ sơ. Khi có bản nháp,
          từng mệnh đề sẽ hiện ở đây, nối với lượt hội thoại làm căn cứ.
        </p>
        <button onClick={onBack} className="mt-2 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[#CCE3F0] bg-white text-xs font-semibold text-[#0C4A6E]">
          <ArrowLeft size={14} /> Quay lại ca khám
        </button>
      </div>
    );
  }

  const daQuyet = ds.filter((p) => quyet[p.id] && quyet[p.id] !== "cho").length;
  const phanTram = ds.length ? Math.round((daQuyet / ds.length) * 100) : 0;
  const nguon = NHAN_NGUON[note.source || ""] || { chu: note.source || "không rõ nguồn", mau: "bg-[#EEE] text-[#444] border-[#DDD]" };
  const dem = (q: Quyet) => Object.values(quyet).filter((x) => x === q).length;
  const dat = (id: number, q: Quyet) => setQuyet((p) => ({ ...p, [id]: q }));
  const bamChon = (c: Chon) =>
    setGhim((g) => (g && c && g.loai === c.loai && (g.loai === "p" ? g.id === (c as any).id : g.so === (c as any).so) ? null : c));

  return (
    <div className="flex-1 flex flex-col h-full bg-[#F0F7FA] overflow-y-auto">
      {/* Đầu trang */}
      <div className="px-4 sm:px-8 pt-5 pb-3 max-w-[1400px] mx-auto w-full flex flex-col gap-3">
        <div>
          <button onClick={onBack} className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[#CCE3F0] bg-white text-xs font-semibold text-[#0C4A6E] hover:bg-[#E0F2FE]">
            <ArrowLeft size={14} /> Quay lại
          </button>
        </div>
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-serif font-bold text-[#0C2340]">Duyệt từng mệnh đề</h1>
            <p className="text-[13px] text-[#475569] mt-1">
              Lần theo dây nối để đối chiếu từng mệnh đề với lượt hội thoại làm căn cứ, rồi giữ, sửa hoặc bỏ.
            </p>
            <div className="flex flex-wrap items-center gap-2 mt-2 text-[11px]">
              <span className={`px-2 py-0.5 rounded-full border font-semibold ${nguon.mau}`}>{nguon.chu}</span>
              {note.branch && <span className="px-2 py-0.5 rounded-full border border-[#CCE3F0] bg-white text-[#475569]">nhánh {note.branch}</span>}
              {note.policy && <span className="px-2 py-0.5 rounded-full border border-[#CCE3F0] bg-white text-[#475569]">cổng {note.policy}</span>}
              {note.seconds !== undefined && <span className="px-2 py-0.5 rounded-full border border-[#CCE3F0] bg-white text-[#475569] font-mono">{note.seconds}s</span>}
              {note.caseId && <span className="px-2 py-0.5 rounded-full border border-[#CCE3F0] bg-white text-[#475569] font-mono">{note.caseId}</span>}
              {note.warningPolicy && (
                <span className="px-2 py-0.5 rounded-full border border-[#CCE3F0] bg-white text-[#475569]" title="Trạng thái xác nhận trên màn này theo lớp cảnh báo mới; bản nháp chữ vẫn theo chính sách đã đo">
                  lớp cảnh báo {note.warningPolicy}
                </span>
              )}
            </div>
          </div>
          <div className="flex items-center gap-3 bg-[#E0F2FE] border border-[#BAE6FD] rounded-2xl px-4 py-3 min-w-[260px]">
            <Users size={22} className="text-[#0284C7] flex-shrink-0" />
            <div className="flex-1">
              <div className="flex items-center justify-between text-xs font-semibold text-[#0C4A6E]">
                <span><strong className="text-sm tabular-nums">{daQuyet}/{ds.length}</strong> mệnh đề đã duyệt</span>
                <span className="font-mono text-[11px]">{phanTram}%</span>
              </div>
              <div className="w-full h-1.5 rounded-full bg-white overflow-hidden mt-1.5">
                <div className="h-full bg-[#0284C7] rounded-full transition-all" style={{ width: `${phanTram}%` }} />
              </div>
              <div className="text-[10.5px] text-[#0369A1] mt-1">Công cụ hỗ trợ — không thay thế đánh giá của bác sĩ</div>
            </div>
          </div>
        </div>

        {/* Dải số liệu */}
        <div className="flex flex-wrap gap-2 text-[11.5px]">
          {[
            ["Tổng mệnh đề", ds.length, "text-[#0C4A6E]"],
            ["Máy đưa sang cần xác nhận", note.needsConfirmCount, "text-[#B4232C]"],
            ["Đã giữ", dem("giu"), "text-[#0D7A5C]"],
            ["Đã sửa", dem("sua"), "text-[#A16207]"],
            ["Đã bỏ", dem("bo"), "text-[#64748B]"],
          ].map(([ten, so, mau]) => (
            <span key={String(ten)} className="px-3 py-1.5 rounded-xl bg-white border border-[#CCE3F0] text-[#475569]">
              {ten} <strong className={`ml-1 tabular-nums ${mau}`}>{so}</strong>
            </span>
          ))}
        </div>
      </div>

      {(note.caseWarnings?.length || 0) > 0 && (
        <div className="px-4 sm:px-8 pb-4 max-w-[1400px] mx-auto w-full">
          <div className="rounded-2xl border border-[#F2DFA8] bg-[#FFFBEB] p-4">
            <h2 className="text-sm font-bold text-[#92400E] flex items-center gap-1.5">
              <EyeOff size={15} /> Có thể bỏ sót ({note.caseWarnings!.length})
            </h2>
            <p className="text-[11.5px] text-[#92400E]/80 mt-0.5">
              Đoạn hội thoại có thông tin quan trọng mà không dòng nào trong bản nháp dẫn tới. Máy không tự thêm vào bản nháp.
            </p>
            <ul className="mt-2 grid grid-cols-1 md:grid-cols-2 gap-2">
              {note.caseWarnings!.map((c, i) => (
                <li key={i} className="bg-white rounded-xl border border-[#F2DFA8] px-3 py-2 text-[12px] flex items-start justify-between gap-2">
                  <span className="min-w-0">
                    <strong className="text-[#92400E]">{c.title}</strong>
                    <span className="block text-[#334155] italic">“{c.quotes[0]}”</span>
                  </span>
                  {c.turns[0] && (
                    <button onClick={() => xemLuot(c.turns[0])} className="flex-shrink-0 px-2 py-0.5 rounded-lg border border-[#F2DFA8] text-[11px] font-semibold text-[#92400E] hover:bg-[#FEF3C7]">
                      lượt {c.turns[0]}
                    </button>
                  )}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Hai cột + dây nối */}
      <div className="px-4 sm:px-8 pb-6 max-w-[1400px] mx-auto w-full">
        <div ref={khungRef} className="relative grid grid-cols-1 lg:grid-cols-[minmax(0,5fr)_minmax(0,7fr)] gap-5 lg:gap-x-20">
          {rong && (
            <svg className="absolute inset-0 pointer-events-none z-10" width={khung.w} height={khung.h} aria-hidden="true">
              {day.map((d) => (
                <g key={d.key} opacity={d.sang ? 1 : 0.18}>
                  <path d={d.d} fill="none" stroke={d.mau} strokeWidth={d.sang && dangChon ? 2.5 : 1.75} />
                  <circle cx={d.x1} cy={d.y1} r={4} fill={d.mau} />
                  <circle cx={d.x2} cy={d.y2} r={4} fill={d.mau} />
                </g>
              ))}
            </svg>
          )}

          {/* Cột trái — hội thoại */}
          <section className="bg-white rounded-3xl border border-[#E2ECF3] p-4 sm:p-5 self-start">
            <div className="flex items-center justify-between mb-4">
              <h2 className="flex items-center gap-2 text-base font-bold text-[#0C2340]">
                <MessageSquare size={18} className="text-[#0C4A6E]" /> Hội thoại
              </h2>
              <span className="text-[12px] text-[#64748B]">{luot.length} lượt</span>
            </div>
            {luot.length === 0 && <p className="text-[12px] text-[#64748B]">Bản nháp này không kèm lời thoại.</p>}
            <ol className="relative flex flex-col gap-1.5">
              <span className="absolute left-[15px] top-3 bottom-3 w-px bg-[#E2E8F0]" aria-hidden="true" />
              {luot.map((l) => {
                const soMD = menhDeCuaLuot.get(l.so)?.length || 0;
                const mv = MAU_VAI(l.vai);
                const sang = tSang(l.so);
                const coCanh = (menhDeCuaLuot.get(l.so) || []).some((id) => {
                  const p = ds.find((x) => x.id === id);
                  return p && mauMD(p) === MAU.canh;
                });
                return (
                  <li
                    key={l.so}
                    className={`relative flex items-start gap-3 transition-opacity ${sang ? "" : "opacity-35"}`}
                    onMouseEnter={() => soMD && setChon({ loai: "t", so: l.so })}
                    onMouseLeave={() => setChon(null)}
                    onClick={() => soMD && bamChon({ loai: "t", so: l.so })}
                  >
                    <span
                      className={`relative z-[1] ${soMD ? "w-8 h-8 text-[12px]" : "w-6 h-6 ml-1 text-[10.5px]"} rounded-full flex items-center justify-center font-semibold flex-shrink-0 border ${
                        soMD ? (coCanh ? "bg-[#FDECEC] border-[#F5C2C2] text-[#B4232C]" : "bg-[#E7F7F0] border-[#BCE8D5] text-[#0D7A5C]") : "bg-[#F8FAFC] border-[#E2E8F0] text-[#94A3B8]"
                      }`}
                    >
                      {l.so}
                    </span>
                    <div
                      ref={(el) => {
                        if (el) luotRef.current.set(l.so, el);
                        else luotRef.current.delete(l.so);
                      }}
                      title={soMD ? `${soMD} mệnh đề dẫn lượt này` : "Không mệnh đề nào dẫn lượt này"}
                      className={`flex-1 min-w-0 rounded-2xl border ${
                        soMD ? `px-3.5 py-2.5 ${mv.nen} ${mv.vien} cursor-pointer` : "px-3 py-1 bg-transparent border-transparent"
                      }`}
                    >
                      {luotBoSot.has(l.so) && (
                        <div className="text-[10.5px] font-semibold text-[#B45309] flex items-center gap-1" title={luotBoSot.get(l.so)!.reason}>
                          <EyeOff size={11} /> {luotBoSot.get(l.so)!.title}
                        </div>
                      )}
                      {soMD ? (
                        <>
                          {l.vai && <div className={`text-[10.5px] font-semibold uppercase tracking-wide ${mv.chu}`}>{l.vai}</div>}
                          <p className="text-[13px] text-[#1E293B] leading-snug select-text">{l.chu}</p>
                        </>
                      ) : (
                        // Lượt không được mệnh đề nào dẫn (thường là câu hỏi của bác sĩ): thu gọn một dòng.
                        <p className="text-[12px] text-[#64748B] leading-snug truncate select-text">
                          <span className="font-semibold">{l.vai ? `${l.vai}: ` : ""}</span>{l.chu}
                        </p>
                      )}
                    </div>
                  </li>
                );
              })}
            </ol>
          </section>

          {/* Cột phải — mệnh đề */}
          <section className="bg-white rounded-3xl border border-[#E2ECF3] p-4 sm:p-5 self-start">
            <div className="flex flex-wrap items-center justify-between gap-2 mb-4">
              <h2 className="flex items-center gap-2 text-base font-bold text-[#0C2340]">
                <FileText size={18} className="text-[#0C4A6E]" /> Các mệnh đề được trích xuất
              </h2>
              <div className="flex items-center gap-2">
                <span className="text-[12px] text-[#64748B]">{ds.length} mệnh đề</span>
                <div className="grid grid-cols-2 gap-0.5 p-0.5 rounded-lg bg-[#F1F5F9] border border-[#E2E8F0] text-[11px]">
                  {([["luot", "Theo lượt"], ["muc", "Theo mục"]] as const).map(([id, chu]) => (
                    <button key={id} onClick={() => setXep(id)} className={`px-2 py-0.5 rounded-md font-semibold ${xep === id ? "bg-white text-[#0369A1] shadow-sm" : "text-[#64748B]"}`}>
                      {chu}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex flex-col gap-3">
              {ds.map((p) => {
                const q = quyet[p.id] || "cho";
                const chu = banSua[p.id] || p.text;
                const mau = mauMD(p);
                const canh = mau === MAU.canh;
                const bo = q === "bo";
                const cbGoc = boQua[p.id] ? null : p.warning || null;
                // Loai "luu y" (chat luong, ghi lap): chi mot dong ghi chu xam, khong to mau the.
                const ghiChu = cbGoc && cbGoc.kind === "can_xem" && !canh ? cbGoc : null;
                const cb = ghiChu ? null : cbGoc;
                const coLuuY = !canh && !!cb;
                const IconCb = (cb && ICON_NHOM[cb.group]) || AlertTriangle;
                return (
                  <div
                    key={p.id}
                    ref={(el) => {
                      if (el) mdRef.current.set(p.id, el);
                      else mdRef.current.delete(p.id);
                    }}
                    onMouseEnter={() => setChon({ loai: "p", id: p.id })}
                    onMouseLeave={() => setChon(null)}
                    onClick={(e) => {
                      if ((e.target as HTMLElement).closest("button,input")) return;
                      bamChon({ loai: "p", id: p.id });
                    }}
                    className={`rounded-2xl border p-3.5 transition-opacity cursor-pointer ${pSang(p) ? "" : "opacity-40"} ${
                      bo ? "bg-[#F8FAFC] border-[#E2E8F0]" : canh ? "bg-[#FFF5F5] border-[#F5C2C2]" : coLuuY ? "bg-[#FFFBEB] border-[#F5E1A4]" : "bg-[#F3FBF7] border-[#CDEBDD]"
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div className="flex flex-col gap-1 flex-shrink-0">
                        {(p.evidenceTurns.length ? p.evidenceTurns : [0]).map((t) => (
                          <span
                            key={t}
                            className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-xl text-[11.5px] font-semibold whitespace-nowrap ${
                              t === 0 ? "bg-[#FDE8E8] text-[#B4232C]" : canh ? "bg-[#FDE2E2] text-[#9B2C2C]" : "bg-[#DDF3E9] text-[#0D6B50]"
                            }`}
                          >
                            <MessageSquare size={12} /> {t === 0 ? "Không dẫn lượt" : `Từ lượt ${t}`}
                          </span>
                        ))}
                      </div>
                      <div className="flex-1 min-w-0">
                        {suaId === p.id ? (
                          <input
                            value={chuSua}
                            onChange={(e) => setChuSua(e.target.value)}
                            onKeyDown={(e) => {
                              if (e.key === "Enter") {
                                setBanSua((b) => ({ ...b, [p.id]: chuSua }));
                                dat(p.id, "sua");
                                setSuaId(null);
                              }
                            }}
                            className="w-full text-[14px] border border-[#BAE6FD] rounded-lg px-2 py-1 bg-white"
                            autoFocus
                          />
                        ) : (
                          <p className={`text-[14px] font-semibold text-[#0C2340] leading-snug ${bo ? "line-through text-[#94A3B8]" : ""}`}>{chu}</p>
                        )}
                        {banSua[p.id] && <p className="text-[11px] text-[#A16207] mt-0.5">Máy viết: “{p.text}”</p>}
                        <div className="flex flex-wrap gap-1.5 mt-2 text-[11px]">
                          <span className="px-2 py-0.5 rounded-lg bg-[#E0EDFF] text-[#1E4E9C]">nói về: {p.subject || "chưa rõ"}</span>
                          {p.negated && <span className="px-2 py-0.5 rounded-lg bg-[#FEE2E2] text-[#991B1B] font-bold">phủ định</span>}
                          {p.certainty && p.certainty !== "chắc chắn" && <span className="px-2 py-0.5 rounded-lg bg-[#FEF3C7] text-[#92400E]">{p.certainty}</span>}
                          {p.situation && p.situation !== "thực tế" && <span className="px-2 py-0.5 rounded-lg bg-[#FEF3C7] text-[#92400E]">{p.situation}</span>}
                          {p.time && <span className="px-2 py-0.5 rounded-lg bg-[#E0F2FE] text-[#0369A1]">{p.time}</span>}
                          {p.drug && <span className="px-2 py-0.5 rounded-lg bg-[#EDE9FE] text-[#5B21B6]">{p.drug}</span>}
                          <span className="px-2 py-0.5 rounded-lg bg-[#F1F5F9] text-[#475569]">{p.section}</span>
                        </div>
                      </div>
                      <div className="flex flex-col items-end gap-1 flex-shrink-0">
                        <span
                          className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11.5px] font-semibold ${
                            bo ? "bg-[#F1F5F9] text-[#64748B]" : q === "giu" ? "bg-[#D1F2E3] text-[#0D6B50]" : q === "sua" ? "bg-[#FEF3C7] text-[#92400E]" : canh ? "bg-[#FDE2E2] text-[#B4232C]" : coLuuY ? "bg-[#FEF3C7] text-[#92400E]" : "bg-[#DDF3E9] text-[#0D6B50]"
                          }`}
                        >
                          {bo ? <><Trash2 size={13} /> Đã bỏ</>
                            : q === "giu" ? <><CheckCircle2 size={13} /> Đã giữ</>
                              : q === "sua" ? <><Pencil size={12} /> Đã sửa</>
                                : canh ? <><IconCb size={13} /> Cần bác sĩ xác nhận</>
                                  : coLuuY ? <><Info size={13} /> Có lưu ý</>
                                    : <><CheckCircle2 size={13} /> Máy không cảnh báo</>}
                        </span>
                        <span className="text-[10px] font-mono text-[#94A3B8]">#{p.id}</span>
                      </div>
                    </div>

                    {cb && (
                      <div
                        className={`mt-3 rounded-xl border px-3 py-2.5 ${
                          canh ? "bg-[#FDECEC] border-[#F7CFCF]" : "bg-[#FEF6DD] border-[#F2DFA8]"
                        }`}
                      >
                        <div className="flex items-start gap-2.5">
                          <IconCb size={18} className={`flex-shrink-0 mt-0.5 ${canh ? "text-[#C53030]" : "text-[#B45309]"}`} />
                          <div className="flex-1 min-w-0">
                            <div className={`text-[13px] font-bold ${canh ? "text-[#B4232C]" : "text-[#92400E]"}`}>
                              {cb.title}
                              {cb.reliability !== "on_dinh" && (
                                <span className="ml-1.5 px-1.5 py-0.5 rounded bg-white/70 text-[10px] font-semibold text-[#64748B] align-middle">thử nghiệm</span>
                              )}
                            </div>
                            <div className="text-[12px] text-[#3F2A1D] leading-snug mt-0.5">{cb.reason}</div>
                            {cb.quotes.length > 0 && (
                              <div className="mt-1.5 text-[12px] text-[#334155] italic border-l-2 border-current/30 pl-2 opacity-90">
                                “{cb.quotes[0]}”
                              </div>
                            )}
                            <div className="flex flex-wrap gap-1.5 mt-2 text-[10.5px]">
                              <span className="px-1.5 py-0.5 rounded-md bg-white/80 text-[#475569]">{KET_LUAN[cb.kind]}</span>
                              <span className="px-1.5 py-0.5 rounded-md bg-white/80 text-[#475569]">Mức độ: {MUC_DO[cb.severity]}</span>
                              <span className="px-1.5 py-0.5 rounded-md bg-white/80 text-[#475569]">{CAN_CU[cb.uncertainty]}</span>
                              {(p.otherWarnings?.length || 0) + (cb.tagTitles?.length || 0) > 0 && (
                                <button
                                  onClick={() => setMoKhac((m2) => ({ ...m2, [p.id]: !m2[p.id] }))}
                                  className="px-1.5 py-0.5 rounded-md bg-white/80 text-[#0369A1] font-semibold"
                                >
                                  +{(p.otherWarnings?.length || 0) + (cb.tagTitles?.length || 0)} dấu hiệu khác
                                </button>
                              )}
                            </div>
                            {moKhac[p.id] && (
                              <ul className="mt-2 space-y-1 text-[11.5px] text-[#3F2A1D]">
                                {(p.otherWarnings || []).map((o, i) => (
                                  <li key={i}><strong>{o.title}</strong> — {o.reason}</li>
                                ))}
                                {(cb.tagTitles || []).map((t, i) => <li key={`t${i}`} className="text-[#64748B]">cùng nguyên nhân: {t}</li>)}
                              </ul>
                            )}
                            <div className="flex flex-wrap gap-1.5 mt-2.5">
                              {cb.turns.length > 0 && (
                                <button onClick={() => xemLuot(cb.turns[0])} className="inline-flex items-center gap-1 px-2 py-1 rounded-lg bg-white border border-[#E2E8F0] text-[11.5px] font-semibold text-[#0C2340] hover:border-[#0284C7]">
                                  <Eye size={12} /> Xem câu gốc (lượt {cb.turns.join(", ")})
                                </button>
                              )}
                              <button onClick={() => dat(p.id, "giu")} className="inline-flex items-center gap-1 px-2 py-1 rounded-lg bg-white border border-[#E2E8F0] text-[11.5px] font-semibold text-[#0D6B50] hover:border-[#0D9488]">
                                <Check size={12} /> Xác nhận đúng
                              </button>
                              <button onClick={() => { setSuaId(p.id); setChuSua(chu); }} className="inline-flex items-center gap-1 px-2 py-1 rounded-lg bg-white border border-[#E2E8F0] text-[11.5px] font-semibold text-[#0C2340] hover:border-[#0284C7]">
                                <Pencil size={12} /> Sửa
                              </button>
                              <button onClick={() => setBoQua((b2) => ({ ...b2, [p.id]: true }))} className="inline-flex items-center gap-1 px-2 py-1 rounded-lg bg-white border border-[#E2E8F0] text-[11.5px] text-[#64748B] hover:border-[#94A3B8]">
                                <BoQua size={12} /> Bỏ qua cảnh báo
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                    {ghiChu && (
                      <p className="mt-2 text-[11.5px] text-[#64748B] flex items-start gap-1.5">
                        <Info size={12} className="mt-0.5 flex-shrink-0" /> Ghi chú: {ghiChu.title} — {ghiChu.reason}
                      </p>
                    )}
                    {boQua[p.id] && p.warning && (
                      <button onClick={() => setBoQua((b2) => ({ ...b2, [p.id]: false }))} className="mt-2 text-[11px] text-[#64748B] underline">
                        Đã bỏ qua cảnh báo “{p.warning.title}” — hiện lại
                      </button>
                    )}

                    {/* Màn hẹp: không có dây, hiện luôn câu thoại làm căn cứ */}
                    {!rong && p.evidenceTurns.length > 0 && (
                      <div className="mt-2.5 rounded-xl bg-white/70 border border-[#E2E8F0] p-2 text-[11.5px] text-[#334155] space-y-1">
                        {p.evidenceTurns.map((t) => {
                          const l = luot.find((x) => x.so === t);
                          return (
                            <p key={t}>
                              <span className="font-mono text-[#0369A1]">lượt {t}</span> · {l ? `${l.vai ? `${l.vai}: ` : ""}${l.chu}` : "(không có trong bản chép)"}
                            </p>
                          );
                        })}
                      </div>
                    )}

                    <div className="flex flex-wrap items-center gap-2 mt-3">
                      {suaId === p.id ? (
                        <>
                          <button
                            onClick={() => {
                              setBanSua((b) => ({ ...b, [p.id]: chuSua }));
                              dat(p.id, "sua");
                              setSuaId(null);
                            }}
                            className="px-3 py-1.5 rounded-xl bg-[#0284C7] text-white text-xs font-semibold"
                          >
                            Lưu sửa
                          </button>
                          <button onClick={() => setSuaId(null)} className="px-3 py-1.5 rounded-xl border border-[#CCE3F0] bg-white text-xs">Huỷ</button>
                        </>
                      ) : (
                        <>
                          <button
                            onClick={() => dat(p.id, "giu")}
                            className={`inline-flex items-center gap-1 px-3 py-1.5 rounded-xl text-xs font-semibold border ${q === "giu" ? "bg-[#0D9488] text-white border-[#0D9488]" : "bg-white border-[#CCE3F0] text-[#0C2340] hover:border-[#0D9488]"}`}
                          >
                            <Check size={13} /> {canh ? "Đã xác nhận, giữ" : "Giữ"}
                          </button>
                          <button
                            onClick={() => {
                              setSuaId(p.id);
                              setChuSua(chu);
                            }}
                            className={`inline-flex items-center gap-1 px-3 py-1.5 rounded-xl text-xs font-semibold border ${q === "sua" ? "bg-[#FEF6E0] border-[#F2DFA8] text-[#A16207]" : "bg-white border-[#CCE3F0] text-[#0C2340] hover:border-[#0284C7]"}`}
                          >
                            <Pencil size={13} /> Sửa mệnh đề
                          </button>
                          <button
                            onClick={() => dat(p.id, "bo")}
                            className={`inline-flex items-center gap-1 px-3 py-1.5 rounded-xl text-xs font-semibold border ${bo ? "bg-[#FDE8E8] border-[#F5C2C2] text-[#B4232C]" : "bg-white border-[#CCE3F0] text-[#0C2340] hover:border-[#E86A6A]"}`}
                          >
                            <Trash2 size={13} /> Bỏ
                          </button>
                          {q !== "cho" && (
                            <button onClick={() => dat(p.id, "cho")} className="inline-flex items-center gap-1 px-2 py-1 rounded-lg text-xs text-[#64748B]">
                              <Undo2 size={12} /> bỏ đánh dấu
                            </button>
                          )}
                        </>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </section>
        </div>
        {rong && (
          <p className="text-[11px] text-[#64748B] mt-3">
            Di chuột vào một mệnh đề hoặc một lượt để làm sáng dây nối; bấm để ghim. Dây xanh: không cần xác nhận · dây đỏ: cần bác sĩ xác nhận · dây xám: đã bỏ. Thẻ vàng: có lưu ý nhưng không bắt buộc xác nhận.
          </p>
        )}
      </div>

      {/* Phần phụ */}
      <div className="px-4 sm:px-8 pb-16 max-w-[1400px] mx-auto w-full grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="bg-white rounded-2xl border border-[#E2ECF3] p-4">
          <h2 className="text-sm font-bold text-[#0C2340] mb-2 flex items-center gap-1.5"><HelpCircle size={15} className="text-[#0284C7]" /> Câu hỏi làm rõ</h2>
          {note.questions?.length ? (
            <ul className="text-[12.5px] text-[#334155] list-decimal pl-4 space-y-1">
              {note.questions.map((q2, i) => <li key={i}>{q2}</li>)}
            </ul>
          ) : (
            <p className="text-[12px] text-[#64748B]">Luật không thấy chỗ nào cần hỏi lại.</p>
          )}
          <p className="text-[10.5px] text-[#64748B] mt-2">Sinh từ chính hội thoại, không lấy từ nguồn ngoài.</p>
        </div>

        <div className="bg-white rounded-2xl border border-[#E2ECF3] p-4">
          <h2 className="text-sm font-bold text-[#0C2340] mb-2 flex items-center gap-1.5"><Sparkles size={15} className="text-[#0284C7]" /> Gợi ý câu hỏi thêm</h2>
          {allowExternal && onAskExternalQuestions ? (
            <>
              <button
                disabled={dangHoi}
                onClick={async () => {
                  setDangHoi(true);
                  try {
                    setCauHoiNgoai(await onAskExternalQuestions());
                  } finally {
                    setDangHoi(false);
                  }
                }}
                className="w-full px-2.5 py-1.5 rounded-xl border border-[#F5C2C2] bg-[#FDF2F2] text-[#8C1D26] text-xs font-semibold disabled:opacity-60"
              >
                {dangHoi ? "Đang hỏi mô hình ngoài…" : cauHoiNgoai ? "Gợi ý lại" : "Gợi ý bằng mô hình ngoài"}
              </button>
              {cauHoiNgoai && (
                <>
                  <ul className="text-[12.5px] text-[#334155] list-decimal pl-4 space-y-1.5 mt-2">
                    {cauHoiNgoai.questions.map((q, i) => (
                      <li key={i}>
                        <span className="font-semibold">{q.hoi}</span>
                        {q.vi_sao && <span className="block text-[11px] text-[#64748B]">{q.vi_sao}</span>}
                        {q.luot && q.luot.length > 0 && <span className="text-[10px] font-mono text-[#0369A1]">lượt {q.luot.join(", ")}</span>}
                      </li>
                    ))}
                  </ul>
                  <p className="text-[10px] text-[#8C1D26] mt-2">Mô hình ngoài · {cauHoiNgoai.model}. Chỉ là gợi ý.</p>
                </>
              )}
            </>
          ) : (
            <p className="text-[12px] text-[#64748B]">Bật “Mô hình ngoài” ở màn soạn để dùng.</p>
          )}
        </div>

        <div className="bg-white rounded-2xl border border-[#E2ECF3] p-4">
          <button onClick={() => setMoBanNhap(!moBanNhap)} className="w-full flex items-center justify-between text-sm font-bold text-[#0C2340]">
            <span className="flex items-center gap-1.5"><ListTree size={15} className="text-[#0284C7]" /> Bản nháp theo mục{patientIdentifier ? ` — ${patientIdentifier}` : ""}</span>
            {moBanNhap ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          </button>
          {moBanNhap ? (
            <div className="mt-2 flex flex-col gap-2">
              {muc.map((m) => (
                <div key={m.ten}>
                  <div className="text-[11px] font-bold text-[#0C4A6E]">{m.ten}</div>
                  <ul className="text-[12px] text-[#334155] list-disc pl-4">
                    {m.dong.map((d, i) => <li key={i}>{d}</li>)}
                  </ul>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-[12px] text-[#64748B] mt-2">{muc.length} mục. Bấm để xem bản nháp như máy viết.</p>
          )}
          <p className="text-[10.5px] text-[#64748B] mt-3 leading-snug">
            Bản nháp hồ sơ lâm sàng có cấu trúc. Bác sĩ xem xét, chỉnh sửa và chịu trách nhiệm cuối cùng. Hệ thống không chẩn đoán và không đưa ra chỉ định điều trị.
          </p>
        </div>
      </div>
    </div>
  );
};
