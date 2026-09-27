import React, { useMemo, useRef, useState } from "react";
import Markdown from "react-markdown";
import { MediTraceLogo } from "./MediTraceLogo";
import { ThuVienYKhoa } from "./ThuVienYKhoa";
import { MayTinhLamSang } from "./MayTinhLamSang";
import { ClinicalChatMessage } from "../types";
import { useKho } from "../lib/useKho";
import { TraLoiCoNguon } from "./TraLoiCoNguon";
import {
  Plus, Search, BookOpen, Calculator, Award, Mic, ArrowUp, FileText, FilePlus, ArrowRight, ListChecks,
  Stethoscope, Pencil, Check, Copy, RefreshCw, ChevronDown, ChevronUp, ShieldAlert, ExternalLink,
  MessageSquare, Pill, ClipboardList, PenLine, FileSignature, Square, Trash2, Lock, Library,
} from "lucide-react";

/**
 * Màn "Hỏi về ca khám" (trước là màn tra cứu của AI Studio, toàn dữ liệu viết sẵn). Nay mọi nút
 * đều chạy thật:
 *  - Hỏi về ca khám: trả lời chỉ từ lời thoại + bản nháp của ca đang mở (mô hình ngoài).
 *  - Tra tài liệu: server tự tìm Bộ Y tế (phác đồ + kcb.vn), MSD Manual, nhãn thuốc FDA (DailyMed), NICE, WHO, CDC, PubMed, MedlinePlus; mô hình chỉ tóm tắt (xem server.ts).
 *  - Thư viện y khoa, Máy tính lâm sàng: không qua AI.
 *  - Lịch sử hỏi đáp lưu ở kho "tra-cuu" (trình duyệt + server).
 */
export type CheDoHoiDap = "ca_kham" | "tra_cuu" | "de_xuat";
export type NguonTraCuu = { pubmed: boolean; medlineplus: boolean; fda: boolean; kcb: boolean;
  msd: boolean; nice: boolean; who: boolean; cdc: boolean; statpearls: boolean; aafp: boolean; chiBangChungCao: boolean };

export interface TraLoiHoiDap {
  content: string;
  sources?: ClinicalChatMessage["sources"];
  warning?: string | null;
  removedSources?: number;
  meta?: string;
  cauTruc?: ClinicalChatMessage["cauTruc"];
  question?: string;
}

interface Props {
  caTen: string;
  coLoiThoai: boolean;
  allowExternal: boolean;
  onToggleExternal: (bat: boolean) => void;
  hoi: (cheDo: CheDoHoiDap, cauHoi: string, tuyChon: { kemNguCanh: boolean; nguon: NguonTraCuu }) => Promise<TraLoiHoiDap | null>;
  onNavigate: (view: "scribe" | "templates") => void;
  onOpenCreate: () => void;
  onSaveToContext: (text: string) => void;
}

type HoiThoai = { id: string; tieuDe: string; caTen: string; tinNhan: ClinicalChatMessage[]; capNhat: number };
type Man = "hoi" | "thu_vien" | "may_tinh" | "tai_lieu";

const gio = () => new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

export const EvidenceView: React.FC<Props> = ({
  caTen, coLoiThoai, allowExternal, onToggleExternal, hoi, onNavigate, onOpenCreate, onSaveToContext,
}) => {
  const [lichSu, setLichSu] = useKho<HoiThoai>("tra-cuu");
  const [dangMo, setDangMo] = useState<string | null>(null);
  const [man, setMan] = useState<Man>("hoi");
  const [timLS, setTimLS] = useState("");
  const [query, setQuery] = useState("");
  // Một ô hỏi (gộp 24/09): mọi câu đi "tra_cuu"; server đọc ca rồi tự quyết định có tra tài liệu không.
  const cheDo = "tra_cuu" as const;
  const [kemNguCanh, setKemNguCanh] = useState(true);
  const [nguon, setNguon] = useState<NguonTraCuu>({
    pubmed: true, medlineplus: true, fda: true, kcb: true, msd: true, nice: true, who: true, cdc: true, statpearls: true, aafp: true, chiBangChungCao: false });
  const [moNguon, setMoNguon] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [daChep, setDaChep] = useState<string | null>(null);
  const [ghi, setGhi] = useState<"tat" | "dang_ghi" | "dang_chep">("tat");
  const [loiMic, setLoiMic] = useState<string | null>(null);
  const rec = useRef<{ r: MediaRecorder; s: MediaStream; c: Blob[] } | null>(null);
  const oNhap = useRef<HTMLTextAreaElement>(null);

  const hienTai = lichSu.find((h) => h.id === dangMo) || null;
  const tinNhan = hienTai?.tinNhan || [];
  const soNguon = [nguon.kcb, nguon.msd, nguon.fda, nguon.medlineplus, nguon.nice, nguon.who, nguon.cdc, nguon.statpearls, nguon.aafp, nguon.pubmed].filter(Boolean).length;

  // Tài liệu đã trích dẫn: đếm thật từ mọi câu trả lời tra cứu, bỏ trùng theo link.
  const taiLieu = useMemo(() => {
    const m = new Map<string, { name: string; domain: string; url: string; lan: number }>();
    for (const h of lichSu)
      for (const t of h.tinNhan)
        for (const s of t.sources || [])
          if (s.url && (s as any).cited !== false) {
            const cu = m.get(s.url);
            m.set(s.url, { name: s.name, domain: s.domain, url: s.url, lan: (cu?.lan || 0) + 1 });
          }
    return [...m.values()].sort((a, b) => b.lan - a.lan);
  }, [lichSu]);

  const ghiTin = (id: string, tin: ClinicalChatMessage) =>
    setLichSu((ds) => ds.map((h) => (h.id === id ? { ...h, tinNhan: [...h.tinNhan, tin], capNhat: Date.now() } : h)));

  const gui = async (cau: string, che: CheDoHoiDap = cheDo, nguonGhiDe?: NguonTraCuu) => {
    const text = cau.trim();
    if (!text || isLoading || !allowExternal) return;
    setMan("hoi");
    let id = dangMo;
    const tinHoi: ClinicalChatMessage = {
      id: `u-${Date.now()}`, role: "user", content: text, timestamp: gio(),
      mode: che === "tra_cuu" ? "tra_cuu" : "ca_kham",
    };
    if (!id) {
      id = `ht-${Date.now()}`;
      const moi: HoiThoai = { id, tieuDe: text.slice(0, 80), caTen, tinNhan: [tinHoi], capNhat: Date.now() };
      setLichSu((ds) => [moi, ...ds]);
      setDangMo(id);
    } else ghiTin(id, tinHoi);
    setQuery("");
    setIsLoading(true);
    try {
      const d = await hoi(che, text, { kemNguCanh, nguon: nguonGhiDe || nguon });
      if (d)
        ghiTin(id, {
          id: `a-${Date.now()}`, role: "assistant", content: d.content, sources: d.sources || [], warning: d.warning,
          removedSources: d.removedSources, meta: d.meta, mode: che === "tra_cuu" ? "tra_cuu" : "ca_kham", timestamp: gio(),
          cauTruc: d.cauTruc || null, question: d.question,
        });
    } finally {
      setIsLoading(false);
    }
  };

  const soanSan = (chu: string, _che?: "ca_kham" | "tra_cuu") => {
    setMan("hoi");
    setQuery(chu);
    setTimeout(() => {
      oNhap.current?.focus();
      oNhap.current?.setSelectionRange(chu.length, chu.length);
    }, 20);
  };

  // Micro: ghi câu hỏi, chép bằng PhoWhisper tại chỗ (/api/transcribe), nối vào ô hỏi.
  const bamMic = async () => {
    setLoiMic(null);
    if (ghi === "dang_ghi" && rec.current) {
      rec.current.r.stop();
      return;
    }
    if (ghi !== "tat") return;
    try {
      const s = await navigator.mediaDevices.getUserMedia({ audio: true });
      const r = new MediaRecorder(s);
      const c: Blob[] = [];
      r.ondataavailable = (e) => e.data.size && c.push(e.data);
      r.onstop = async () => {
        s.getTracks().forEach((t) => t.stop());
        setGhi("dang_chep");
        try {
          const blob = new Blob(c, { type: r.mimeType || "audio/webm" });
          const b64 = await new Promise<string>((ok, hong) => {
            const f = new FileReader();
            f.onload = () => ok(String(f.result).split(",")[1] || "");
            f.onerror = hong;
            f.readAsDataURL(blob);
          });
          const res = await fetch("/api/transcribe", {
            method: "POST", headers: { "Content-Type": "application/json" },
            // Câu hỏi do một người đọc: không cần tách người nói (đỡ chờ pyannote).
            body: JSON.stringify({ audioBase64: b64, fileName: "cau-hoi.webm", diarize: false }),
          });
          const d = await res.json();
          if (!res.ok) throw new Error(d?.error || `mã ${res.status}`);
          const chu = (d.segments || []).map((x: any) => x.text_original).join(" ").trim();
          if (!chu) throw new Error("Không nghe rõ câu nào.");
          setQuery((q) => (q ? `${q} ${chu}` : chu));
        } catch (err: any) {
          setLoiMic(`Không chép được: ${err?.message || err}`);
        } finally {
          setGhi("tat");
          rec.current = null;
        }
      };
      r.start();
      rec.current = { r, s, c };
      setGhi("dang_ghi");
    } catch {
      setLoiMic("Trình duyệt không cho dùng micrô. Cho phép micrô ở thanh địa chỉ rồi thử lại.");
    }
  };

  const traLoiCuoi = [...tinNhan].reverse().find((t) => t.role === "assistant");

  // 4 thẻ tác vụ và 6 nút nhanh: mỗi cái nối với một việc thật.
  const THE = [
    { ten: "Ghi chép lâm sàng", mo: "Ghi âm hoặc gõ lời thoại, dựng bản nháp hồ sơ có cấu trúc.", icon: FilePlus, lam: () => onNavigate("scribe") },
    {
      ten: "Tóm tắt cuộc khám", mo: `Tóm tắt diễn biến, điều bác sĩ đã kết luận và dặn dò — ${caTen}.`, icon: FileText, canNgoai: true,
      lam: () => gui("Tóm tắt cuộc khám này: lý do khám, diễn biến chính, thuốc, dị ứng, bệnh nền; điều bác sĩ đã kết luận và dặn dò (chỉ những gì có trong hội thoại).", "ca_kham"),
    },
    { ten: "Kiểm tra bằng chứng", mo: "Tra Bộ Y tế, MSD, DailyMed, NICE, WHO, CDC, PubMed.", icon: Search, canNgoai: true, lam: () => soanSan("", "tra_cuu") },
    { ten: "Soạn thảo biểu mẫu", mo: "Tạo SOAP, hướng dẫn ra về, giấy nghỉ… từ ca đang mở.", icon: ListChecks, lam: onOpenCreate },
  ];
  const NUT = [
    { ten: "Tra cứu", icon: Search, lam: () => soanSan("", "tra_cuu") },
    { ten: "Khám thêm", icon: Stethoscope, canNgoai: true, lam: () => gui("Nên hỏi và khám thêm gì cho ca này?") },
    { ten: "Điều trị", icon: Pill, lam: () => soanSan("Khuyến cáo điều trị hiện hành cho ", "tra_cuu") },
    {
      ten: "Chuẩn bị", icon: ClipboardList, canNgoai: true,
      lam: () => gui("Chuẩn bị cho lần tái khám hoặc bàn giao: liệt kê những việc bác sĩ đã hẹn, xét nghiệm đã chỉ định, thuốc đã kê và điều còn bỏ ngỏ trong hội thoại.", "ca_kham"),
    },
    { ten: "Viết", icon: PenLine, lam: onOpenCreate },
    { ten: "Điền mẫu", icon: FileSignature, lam: () => onNavigate("templates") },
  ];
  const HOI_CA = [
    { ten: "Ai bị", cau: "Mỗi triệu chứng và bệnh nền trong ca này là của ai: bệnh nhân hay người nhà?" },
    { ten: "Thuốc", cau: "Bệnh nhân đang dùng thuốc gì, liều và số lần bao nhiêu, có ngừng thuốc nào không?" },
    { ten: "Dị ứng", cau: "Trong hội thoại, ai có dị ứng với thuốc gì?" },
    { ten: "Đính chính", cau: "Có chỗ nào người nói tự sửa lại thông tin đã nói trước đó không?" },
    { ten: "Thời gian", cau: "Các triệu chứng bắt đầu từ khi nào, kéo dài bao lâu?" },
  ];

  const lsLoc = lichSu.filter((h) => !timLS.trim() || `${h.tieuDe} ${h.caTen}`.toLowerCase().includes(timLS.toLowerCase()));

  const oHoi = (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        gui(query);
      }}
      className="w-full bg-gradient-to-b from-white to-[#F8FBFC] rounded-2xl border-[1.5px] border-[#BAE6FD] focus-within:border-[#0284C7] focus-within:ring-2 focus-within:ring-[#BAE6FD]/50 shadow-tactile-box p-3 text-left transition-all relative"
    >
      <div className="flex flex-wrap items-center gap-1.5 mb-1.5">
        {kemNguCanh && (
          <span className="flex items-center gap-1 px-2 py-0.5 rounded-md bg-[#E0F2FE] border border-[#BAE6FD] text-[11px] text-[#0C4A6E] max-w-[16rem]">
            <span className="truncate">Ca: {caTen}</span>
            <button type="button" onClick={() => setKemNguCanh(false)} title="Bỏ ngữ cảnh ca" className="text-[#64748B] hover:text-red-600">×</button>
          </span>
        )}
      </div>
      <textarea
        ref={oNhap}
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            gui(query);
          }
        }}
        disabled={!allowExternal}
        placeholder={
          !allowExternal ? "Bật “Mô hình ngoài” ở trên để hỏi"
            : kemNguCanh ? "VD: bệnh nhân này dùng amoxicillin được không? · ai bị dị ứng thuốc?"
              : "VD: corticoid cho liệt mặt ngoại biên — nên dùng trong bao lâu?"
        }
        className="w-full h-16 sm:h-20 text-[13px] sm:text-sm text-[#0F172A] placeholder-[#94A3B8] bg-transparent resize-none border-none focus:outline-none leading-relaxed disabled:cursor-not-allowed"
      />
      <div className="flex items-center justify-between gap-2 pt-1">
        <div className="flex items-center gap-1.5 relative">
          <button
            type="button" onClick={() => setKemNguCanh(!kemNguCanh)}
            className={`w-7 h-7 rounded-lg border flex items-center justify-center transition-all shadow-tactile-doctor-pill ${kemNguCanh ? "bg-[#0284C7] text-white border-[#0284C7]" : "bg-white text-[#0369A1] border-[#BAE6FD] hover:bg-[#F0F9FF]"}`}
            title={kemNguCanh ? "Đang gắn ngữ cảnh ca đang mở — bấm để bỏ" : "Gắn ngữ cảnh ca đang mở"}
          >
            <Plus size={14} />
          </button>
          <button
            type="button" disabled={!traLoiCuoi}
            onClick={() => {
              if (!traLoiCuoi) return;
              onSaveToContext(traLoiCuoi.content);
              setDaChep(traLoiCuoi.id);
            }}
            className="w-7 h-7 rounded-lg border border-[#BAE6FD] bg-white text-[#0369A1] hover:bg-[#F0F9FF] shadow-tactile-doctor-pill flex items-center justify-center disabled:opacity-40"
            title="Chép câu trả lời gần nhất vào tab Ngữ cảnh của ca"
          >
            {daChep && daChep === traLoiCuoi?.id ? <Check size={12} /> : <Pencil size={12} />}
          </button>
          <button
            type="button" onClick={() => setMoNguon(!moNguon)}
            className="flex items-center gap-1 px-2.5 py-1 rounded-full border border-[#BAE6FD] bg-[#F0F9FF] text-xs font-semibold text-[#0369A1] hover:bg-[#E0F2FE] shadow-tactile-doctor-pill"
            title="Chọn nguồn tra tài liệu"
          >
            Nguồn y khoa {soNguon} <ChevronDown size={11} />
          </button>
          {moNguon && (
            <>
              <div className="fixed inset-0 z-10" onClick={() => setMoNguon(false)} />
              <div className="absolute left-0 bottom-full mb-2 z-20 w-80 max-w-[calc(100vw-2rem)] max-h-[70vh] overflow-y-auto bg-white rounded-xl border border-[#BAE6FD] shadow-[0_8px_24px_rgba(2,132,199,0.16)] p-3 flex flex-col gap-2 text-[12px] text-[#334155]">
                <div className="text-[11px] font-semibold text-[#0369A1]">Nguồn khi cần tra tài liệu</div>
                {([
                  ["Trong nước", [["kcb", "Bộ Y tế — phác đồ lưu tại máy và kcb.vn"], ["msd", "Cẩm nang MSD chuyên gia (bản tiếng Việt)"]]],
                  ["Nước ngoài", [["fda", "DailyMed / nhãn thuốc FDA — liều, tương tác"], ["statpearls", "StatPearls (NCBI) — tổng quan lâm sàng"], ["aafp", "AAFP — American Family Physician"], ["nice", "NICE (Anh) — hướng dẫn lâm sàng"],
                                  ["who", "WHO — tờ thông tin bệnh"], ["cdc", "CDC (Hoa Kỳ) — hướng dẫn cho nhân viên y tế"],
                                  ["medlineplus", "MedlinePlus — thông tin bệnh (NLM)"], ["pubmed", "PubMed / PMC — bài báo (đọc toàn văn nếu mở)"]]],
                ] as const).map(([nhom, ds]) => (
                  <div key={nhom} className="flex flex-col gap-1.5">
                    <div className="text-[10.5px] uppercase tracking-wide text-[#64748B]">{nhom}</div>
                    {ds.map(([k, chu]) => (
                      <label key={k} className="flex items-start gap-2 cursor-pointer leading-snug">
                        <input type="checkbox" className="mt-0.5" checked={nguon[k]} onChange={(e) => setNguon({ ...nguon, [k]: e.target.checked })} /> {chu}
                      </label>
                    ))}
                  </div>
                ))}
                <label className={`flex items-center gap-2 cursor-pointer pl-5 ${nguon.pubmed ? "" : "opacity-40"}`}>
                  <input type="checkbox" disabled={!nguon.pubmed} checked={nguon.chiBangChungCao} onChange={(e) => setNguon({ ...nguon, chiBangChungCao: e.target.checked })} />
                  Chỉ hướng dẫn, tổng quan hệ thống, phân tích gộp
                </label>
                <p className="text-[10.5px] text-[#64748B] leading-snug">Server tự tìm và đọc trang gốc; mô hình chỉ tóm tắt từ đoạn đã lấy, ghi số nguồn cho từng phương án. Chỉ để tham khảo.</p>
              </div>
            </>
          )}
        </div>
        <div className="flex items-center gap-1.5">
          <button
            type="button" onClick={bamMic} disabled={ghi === "dang_chep"}
            className={`w-7 h-7 rounded-lg border flex items-center justify-center shadow-tactile-doctor-pill ${ghi === "dang_ghi" ? "bg-red-50 border-red-300 text-red-600 animate-pulse" : "bg-white border-[#BAE6FD] text-[#0369A1] hover:bg-[#F0F9FF]"}`}
            title={ghi === "dang_ghi" ? "Dừng và chép" : ghi === "dang_chep" ? "Đang chép bằng PhoWhisper…" : "Nói câu hỏi (chép bằng PhoWhisper tại chỗ)"}
          >
            {ghi === "dang_ghi" ? <Square size={11} className="fill-current" /> : ghi === "dang_chep" ? <RefreshCw size={12} className="animate-spin" /> : <Mic size={14} />}
          </button>
          <button
            type="submit" disabled={!query.trim() || isLoading || !allowExternal || (cheDo === "tra_cuu" && soNguon === 0)}
            className="w-7 h-7 rounded-lg bg-[#0284C7] text-white hover:bg-[#0369A1] disabled:opacity-40 shadow-tactile-doctor flex items-center justify-center active:translate-y-0.5"
            title="Gửi"
          >
            <ArrowUp size={14} className="stroke-[2.5]" />
          </button>
        </div>
      </div>
      {loiMic && <p className="text-[11px] text-[#8C1D26] mt-1">{loiMic}</p>}
    </form>
  );

  const thanhCongTac = (
    <div className={`w-full flex flex-wrap items-center justify-between gap-2 px-3 py-2 rounded-xl border text-[11.5px] ${allowExternal ? "bg-[#FDE8E8] border-[#F5C2C2] text-[#8C1D26]" : "bg-white border-[#CCE3F0] text-[#475569]"}`}>
      <span className="flex items-center gap-1.5">
        {!allowExternal && <Lock size={12} />}
        {allowExternal
          ? "Mô hình ngoài đang bật: câu hỏi và nội dung ca gửi tới ai-box."
          : "Hỏi đáp và tra tài liệu cần mô hình ngoài. Thư viện và máy tính lâm sàng dùng được ngay."}
      </span>
      <label className="flex items-center gap-1.5 font-semibold cursor-pointer">
        <input type="checkbox" checked={allowExternal} onChange={(e) => onToggleExternal(e.target.checked)} /> Mô hình ngoài
      </label>
    </div>
  );

  const MUC_BEN: Array<[Man, string, React.ElementType]> = [
    ["thu_vien", "Thư viện y khoa", Library],
    ["may_tinh", "Máy tính lâm sàng", Calculator],
  ];

  return (
    <div id="evidence-view" className="@container flex-1 flex h-full bg-[#F0F7FA] overflow-hidden relative">
      <aside className="hidden md:flex w-64 bg-[#F0F7FA] border-r border-[#CCE3F0] flex-col p-3 flex-shrink-0 gap-3">
        <button
          onClick={() => {
            setDangMo(null);
            setMan("hoi");
          }}
          className="flex items-center gap-1.5 py-2 px-3 rounded-xl bg-white border border-[#BAE6FD] text-xs font-semibold text-[#0C4A6E] shadow-tactile-doctor-pill hover:bg-[#F0F9FF]"
        >
          <Pencil size={13} className="text-[#0284C7]" /> Cuộc trò chuyện mới
        </button>
        <div className="relative">
          <Search size={13} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-[#0284C7]" />
          <input
            value={timLS} onChange={(e) => setTimLS(e.target.value)} placeholder="Tìm trong câu đã hỏi…"
            className="w-full pl-8 pr-2.5 py-1.5 rounded-xl bg-white border border-[#BAE6FD] text-xs focus:outline-none focus:border-[#0284C7]"
          />
        </div>
        <nav className="flex flex-col gap-0.5 text-xs">
          {MUC_BEN.map(([id, chu, I]) => (
            <button
              key={id} onClick={() => setMan(id)}
              className={`flex items-center gap-2 px-2.5 py-1.5 rounded-xl text-left font-medium ${man === id ? "bg-white border border-[#BAE6FD] text-[#0369A1]" : "text-[#0C4A6E] hover:bg-[#E0F2FE]"}`}
            >
              <I size={14} className="text-[#0284C7]" /> {chu}
            </button>
          ))}
        </nav>
        <div className="border-t border-[#CCE3F0] pt-2.5 flex-1 min-h-0 overflow-y-auto no-scrollbar">
          <div className="text-[11px] font-semibold text-[#0369A1] px-2 mb-1.5">Gần đây</div>
          {lsLoc.length === 0 && <p className="px-2 text-[11px] text-[#64748B]">{timLS ? "Không có câu nào khớp." : "Chưa hỏi câu nào."}</p>}
          <div className="flex flex-col gap-0.5">
            {lsLoc.map((h) => (
              <div
                key={h.id}
                onClick={() => {
                  setDangMo(h.id);
                  setMan("hoi");
                }}
                className={`group flex items-start gap-2 px-2.5 py-1.5 rounded-xl text-xs cursor-pointer ${dangMo === h.id && man === "hoi" ? "bg-white border border-[#BAE6FD] text-[#0369A1] font-semibold" : "text-[#475569] hover:bg-[#E0F2FE]/70"}`}
              >
                <span className="mt-1.5 w-1.5 h-1.5 rounded-full border border-[#0284C7] flex-shrink-0" />
                <span className="flex-1 min-w-0">
                  <span className="block truncate">{h.tieuDe}</span>
                  <span className="block truncate text-[10px] font-normal text-[#94A3B8]">{h.caTen}</span>
                </span>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setLichSu((ds) => ds.filter((x) => x.id !== h.id));
                    if (dangMo === h.id) setDangMo(null);
                  }}
                  className="opacity-0 group-hover:opacity-100 text-[#94A3B8] hover:text-red-600"
                  title="Xoá cuộc trò chuyện này"
                >
                  <Trash2 size={11} />
                </button>
              </div>
            ))}
          </div>
        </div>
        <button
          onClick={() => setMan("tai_lieu")}
          className={`rounded-2xl border p-3 text-left bg-gradient-to-b from-white to-[#F0F9FF] shadow-tactile-doctor-card ${man === "tai_lieu" ? "border-[#0284C7]" : "border-[#BAE6FD]"}`}
        >
          <div className="flex items-center gap-1.5 text-xs font-bold text-[#0F172A]"><Award size={13} className="text-[#0284C7]" /> Tài liệu đã tra</div>
          <div className="text-[22px] font-semibold text-[#0C4A6E] tabular-nums leading-tight mt-1">{taiLieu.length}</div>
          <div className="text-[10.5px] text-[#64748B]">tài liệu đã trích dẫn trong các câu trả lời</div>
        </button>
      </aside>

      <div className="flex-1 min-w-0 flex flex-col h-full overflow-y-auto">
        {/* Thanh chọn màn cho màn hẹp (thanh bên ẩn dưới 768px) */}
        <div className="md:hidden flex flex-shrink-0 gap-1.5 px-3 pt-3 pb-1 overflow-x-auto no-scrollbar">
          {([["hoi", "Hỏi đáp"], ["thu_vien", "Thư viện"], ["may_tinh", "Máy tính"], ["tai_lieu", `Tài liệu (${taiLieu.length})`]] as const).map(([id, chu]) => (
            <button key={id} onClick={() => setMan(id)} className={`flex-shrink-0 px-3 py-1 rounded-full text-[11.5px] font-semibold border ${man === id ? "bg-[#0284C7] text-white border-[#0284C7]" : "bg-white border-[#CCE3F0] text-[#0C4A6E]"}`}>
              {chu}
            </button>
          ))}
        </div>

        <div className="flex-1 flex-shrink-0 px-3 sm:px-6 py-6">
          {man === "thu_vien" && <ThuVienYKhoa />}
          {man === "may_tinh" && <MayTinhLamSang />}
          {man === "tai_lieu" && (
            <div className="w-full max-w-3xl mx-auto text-left flex flex-col gap-3">
              <h2 className="font-serif text-2xl font-semibold text-[#0F172A]">Tài liệu đã tra</h2>
              <p className="text-[12.5px] text-[#475569]">Mọi tài liệu từng được trích trong câu trả lời tra cứu, bỏ trùng. Số lần = số câu trả lời đã trích.</p>
              {taiLieu.length === 0 && <p className="text-[12.5px] text-[#64748B] bg-white rounded-xl border border-dashed border-[#BAE6FD] p-4">Chưa có. Hỏi một câu cần kiến thức y khoa (liều, xử trí, ngưỡng…) để có tài liệu ở đây.</p>}
              {taiLieu.map((t) => (
                <a key={t.url} href={t.url} target="_blank" rel="noopener noreferrer" className="bg-white rounded-xl border border-[#CCE3F0] p-3 hover:border-[#0284C7] flex items-start gap-3">
                  <span className="text-[11px] font-semibold text-[#0369A1] tabular-nums w-8 flex-shrink-0">{t.lan}×</span>
                  <span className="min-w-0">
                    <span className="block text-[13px] font-semibold text-[#0C4A6E]">{t.name} <ExternalLink size={10} className="inline -mt-0.5" /></span>
                    <span className="block text-[11px] text-[#64748B]">{t.domain}</span>
                  </span>
                </a>
              ))}
            </div>
          )}

          {man === "hoi" && !hienTai && (
            <div className="w-full max-w-3xl mx-auto flex flex-col items-center text-center gap-4">
              <MediTraceLogo size={48} />
              <h1 className="font-serif text-2xl sm:text-3xl font-semibold text-[#0F172A] tracking-tight text-balance">
                Cần hỏi gì về ca khám hôm nay?
              </h1>
              <p className="text-[12px] text-[#475569] -mt-2">
                Ca đang mở: <strong>{caTen}</strong>{coLoiThoai ? "" : " — chưa có lời thoại"}
              </p>
              {thanhCongTac}
              {oHoi}
              <p className="text-[11px] text-[#0369A1]/80 max-w-xl leading-relaxed">
                Chỉ mang tính tham khảo. Không dùng cho quyết định tự động — bác sĩ đối chiếu tài liệu và quyết định.
              </p>
              <div className="grid grid-cols-1 @xl:grid-cols-2 @4xl:grid-cols-4 gap-3 w-full mt-2">
                {THE.map((t) => {
                  const khoa = t.canNgoai && !allowExternal;
                  return (
                    <button
                      key={t.ten} onClick={t.lam} disabled={khoa}
                      className="bg-gradient-to-b from-white to-[#F0F9FF] rounded-2xl border border-[#BAE6FD] p-4 shadow-tactile-doctor-card hover:border-[#0284C7] hover:-translate-y-0.5 transition-all text-left flex flex-col justify-between gap-3 group disabled:opacity-50 disabled:hover:translate-y-0 disabled:cursor-not-allowed"
                      title={khoa ? "Cần bật “Mô hình ngoài”" : undefined}
                    >
                      <span>
                        <span className="w-9 h-9 rounded-xl bg-[#E0F2FE] border border-[#BAE6FD] text-[#0284C7] flex items-center justify-center mb-2.5"><t.icon size={18} /></span>
                        <span className="block font-serif font-bold text-sm text-[#0F172A] group-hover:text-[#0284C7]">{t.ten}</span>
                        <span className="block text-[11px] text-[#64748B] leading-relaxed mt-1">{t.mo}</span>
                      </span>
                      <span className="self-end w-7 h-7 rounded-full bg-[#0284C7] text-white flex items-center justify-center">
                        {khoa ? <Lock size={12} /> : <ArrowRight size={13} className="stroke-[2.5]" />}
                      </span>
                    </button>
                  );
                })}
              </div>
              <div className="flex flex-wrap items-center justify-center gap-2 mt-1">
                {NUT.map((n) => {
                  const khoa = n.canNgoai && !allowExternal;
                  return (
                    <button
                      key={n.ten} onClick={n.lam} disabled={khoa}
                      className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-white border border-[#BAE6FD] text-xs font-medium text-[#0C4A6E] hover:bg-[#E0F2FE] shadow-tactile-doctor-pill disabled:opacity-45"
                    >
                      <n.icon size={13} className="text-[#0284C7]" /> {n.ten}
                    </button>
                  );
                })}
              </div>
              <div className="flex flex-wrap items-center justify-center gap-1.5 text-[11px]">
                <span className="text-[#64748B] mr-1">Hỏi nhanh về ca:</span>
                {HOI_CA.map((h) => (
                  <button key={h.ten} disabled={!allowExternal} onClick={() => gui(h.cau, "ca_kham")} className="px-2.5 py-1 rounded-full border border-[#CCE3F0] bg-white/70 text-[#0C4A6E] hover:bg-white disabled:opacity-45">
                    {h.ten}
                  </button>
                ))}
              </div>
            </div>
          )}

          {man === "hoi" && hienTai && (
            <div className="w-full max-w-3xl mx-auto flex flex-col gap-4 text-left">
              <div className="text-[11px] text-[#64748B]">Ca: {hienTai.caTen}</div>
              {tinNhan.map((m) =>
                m.role === "user" ? (
                  <div key={m.id} className="flex flex-col items-end gap-1">
                    <span className="text-[10px] text-[#64748B]">{m.timestamp}</span>
                    <div className="max-w-[88%] bg-[#E0F2FE] text-[#0C4A6E] text-[13px] px-4 py-2.5 rounded-2xl rounded-tr-sm border border-[#BAE6FD] select-text">{m.content}</div>
                  </div>
                ) : m.cauTruc ? (
                  <div key={m.id} className="flex flex-col gap-2">
                    {m.warning && (
                      <div className="flex items-start gap-1.5 p-2.5 rounded-xl border text-[11.5px] bg-[#FEF9E7] border-[#F5E6B8] text-[#7A4B00]">
                        <ShieldAlert size={13} className="flex-shrink-0 mt-0.5" /> {m.warning}
                      </div>
                    )}
                    <TraLoiCoNguon
                      msg={m}
                      onAsk={(q) => gui(q)}
                      onCheckOther={(mm) => {
                        if (!mm.question) return;
                        const daDung = new Set((mm.sources || []).filter((x) => x.cited).map((x) => x.nhom));
                        const khac: NguonTraCuu = { ...nguon };
                        for (const k of ["kcb", "msd", "fda", "nice", "who", "cdc", "medlineplus", "pubmed", "statpearls", "aafp"] as const)
                          khac[k] = nguon[k] && !daDung.has(k);
                        if (![khac.kcb, khac.msd, khac.fda, khac.nice, khac.who, khac.cdc, khac.medlineplus, khac.pubmed, khac.statpearls, khac.aafp].some(Boolean)) return;
                        gui(`${mm.question} (tra nguồn khác)`, "tra_cuu", khac);
                      }}
                      onAddToContext={onSaveToContext}
                    />
                  </div>
                ) : (
                  <TraLoi
                    key={m.id} m={m} copied={copiedId === m.id} daChep={daChep === m.id}
                    onCopy={() => {
                      navigator.clipboard.writeText(m.content);
                      setCopiedId(m.id);
                      setTimeout(() => setCopiedId(null), 2000);
                    }}
                    onChep={() => {
                      onSaveToContext(m.content);
                      setDaChep(m.id);
                    }}
                  />
                )
              )}
              {isLoading && (
                <div className="bg-white rounded-2xl border border-[#CCE3F0] p-4 flex items-center gap-3 text-xs text-[#64748B]">
                  <RefreshCw size={14} className="animate-spin text-[#0284C7]" />
                  {kemNguCanh ? "Đang đọc ca khám, tra Bộ Y tế, MSD, DailyMed, StatPearls, AAFP, NICE, WHO, CDC, PubMed nếu cần… (thường 15–25 giây)"
                    : "Đang tra Bộ Y tế, MSD, DailyMed, StatPearls, AAFP, NICE, WHO, CDC, PubMed… (thường 15–25 giây)"}
                </div>
              )}
              {!allowExternal && thanhCongTac}
              <div className="sticky bottom-0 pt-2 pb-1 bg-gradient-to-t from-[#F0F7FA] via-[#F0F7FA] to-transparent">{oHoi}</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const TraLoi: React.FC<{ m: ClinicalChatMessage; copied: boolean; daChep: boolean; onCopy: () => void; onChep: () => void }> = ({
  m, copied, daChep, onCopy, onChep,
}) => {
  const [moNguon, setMoNguon] = useState(true);
  const coNguon = m.mode === "tra_cuu";
  return (
    <div className="flex flex-col gap-2">
      {m.warning && (
        <div className={`flex items-start gap-1.5 p-2.5 rounded-xl border text-[11.5px] ${m.sources?.length ? "bg-[#FEF9E7] border-[#F5E6B8] text-[#7A4B00]" : "bg-[#FDE8E8] border-[#F5C2C2] text-[#8C1D26]"}`}>
          <ShieldAlert size={13} className="flex-shrink-0 mt-0.5" /> {m.warning}
        </div>
      )}
      <div className="bg-white rounded-2xl border border-[#BAE6FD] p-4 shadow-tactile-doctor-card text-[13px] text-[#1E293B] leading-relaxed select-text">
        <Markdown
          components={{
            p: ({ node, ...p }) => <p className="my-1.5" {...p} />,
            ul: ({ node, ...p }) => <ul className="list-disc pl-5 space-y-1 my-2" {...p} />,
            ol: ({ node, ...p }) => <ol className="list-decimal pl-5 space-y-1 my-2" {...p} />,
            h3: ({ node, ...p }) => <h3 className="font-semibold text-[#0F172A] mt-3 mb-1" {...p} />,
            blockquote: ({ node, ...p }) => (
              <blockquote className="mt-3 border-l-4 border-[#F2DFA8] bg-[#FFFBEB] px-3 py-2 rounded-r-lg text-[12px] text-[#7A4B00]" {...p} />
            ),
          }}
        >
          {m.content}
        </Markdown>
        {coNguon && (
          <div className="mt-3 pt-3 border-t border-[#E2ECF3]">
            <button onClick={() => setMoNguon(!moNguon)} className="w-full flex items-center justify-between text-[11.5px] font-semibold text-[#0C4A6E]">
              <span className="flex items-center gap-1.5"><BookOpen size={12} /> {m.sources?.length || 0} tài liệu server đã tìm</span>
              {moNguon ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
            </button>
            {moNguon && (
              <ol className="mt-2 space-y-1.5">
                {(m.sources || []).map((s, i) => (
                  <li key={i} className={`flex items-start gap-1.5 text-[11.5px] ${(s as any).cited === false ? "opacity-55" : ""}`}>
                    <span className="font-mono text-[#64748B]">[{s.so ?? i + 1}]</span>
                    <a href={s.url} target="_blank" rel="noopener noreferrer" className="text-[#0369A1] hover:underline min-w-0">
                      {s.name} <span className="text-[#64748B]">· {s.domain}</span>
                      {(s as any).cited === false && <span className="text-[#64748B]"> · không được trích</span>}
                    </a>
                  </li>
                ))}
              </ol>
            )}
          </div>
        )}
        <div className="mt-3 pt-2.5 border-t border-[#E2ECF3] flex flex-wrap items-center justify-between gap-2 text-[#64748B]">
          <span className="text-[10.5px]">{m.meta}</span>
          <span className="flex items-center gap-1">
            <button onClick={onChep} className="flex items-center gap-1 text-[11px] px-2 py-0.5 rounded-md hover:bg-[#E0F2FE] hover:text-[#0369A1]" title="Chép vào tab Ngữ cảnh của ca">
              {daChep ? <Check size={11} className="text-emerald-600" /> : <FileText size={11} />} {daChep ? "Đã chép" : "Vào Ngữ cảnh"}
            </button>
            <button onClick={onCopy} className="flex items-center gap-1 text-[11px] px-2 py-0.5 rounded-md hover:bg-[#E0F2FE] hover:text-[#0369A1]">
              {copied ? <Check size={11} className="text-emerald-600" /> : <Copy size={11} />} {copied ? "Đã chép" : "Chép"}
            </button>
          </span>
        </div>
      </div>
    </div>
  );
};
