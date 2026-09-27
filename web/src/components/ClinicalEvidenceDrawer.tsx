import React, { useState, useEffect, useRef } from "react";
import Markdown from "react-markdown";
import { ClinicalChatMessage } from "../types";
import {
  X,
  Plus,
  Maximize2,
  ChevronDown,
  ChevronUp,
  Copy,
  Check,
  Sparkles,
  ArrowUp,
  ShieldAlert,
  RefreshCw,
  User,
  BookOpen,
  MessageSquare,
  ExternalLink,
  Lock,
  Stethoscope,
  ListPlus,
} from "lucide-react";
import { motion } from "motion/react";
import { CauHoiNgoai } from "./VerificationView";
import { TraLoiCoNguon } from "./TraLoiCoNguon";

/** Nguồn bật/tắt khi hỏi lại ("Tra nguồn khác" bỏ các nhóm nguồn đã trích). */
export type NguonBat = Partial<Record<"kcb" | "msd" | "fda" | "nice" | "who" | "cdc" | "medlineplus" | "pubmed" | "statpearls" | "aafp", boolean>>;
const TAT_CA_NHOM = ["kcb", "msd", "fda", "nice", "who", "cdc", "medlineplus", "pubmed", "statpearls", "aafp"] as const;

/** Gợi ý nhanh dưới ô hỏi (kiểu Heidi "Patient questions"). */
const GOI_Y_NHANH = [
  "Nên hỏi thêm bệnh nhân những gì?",
  "Dấu hiệu nguy hiểm cần dặn bệnh nhân?",
  "Xử trí theo phác đồ cho ca này?",
];

/**
 * Ngăn phải của màn soạn.
 *
 * PHƯƠNG ÁN 1 — câu hỏi nên hỏi thêm:
 *   - "Từ hội thoại": câu hỏi làm rõ do nhánh C_khoa_hoi sinh bằng luật (tại chỗ, luôn có sau khi tạo bản nháp).
 *   - "Đề xuất thêm câu hỏi": mô hình ngoài đọc tab Ngữ cảnh + lời thoại (ghi âm hoặc gõ) + mệnh đề
 *     Qwen3-4B đã tách, rồi đề xuất. Nút "+" chép câu vào tab Ngữ cảnh.
 * PHƯƠNG ÁN 2 — MỘT ô hỏi (gộp 24/09): máy đọc ca khám (hội thoại đánh số lượt + bản nháp) rồi
 *   - hỏi thông tin sẵn trong ca -> trả lời từ ca, ghi số lượt, không tra tài liệu;
 *   - cần kiến thức y khoa -> server tự tra Bộ Y tế, MSD, DailyMed, NICE, WHO, CDC, MedlinePlus, PubMed,
 *     trả lời theo phương án có số nguồn, kèm "Lưu ý từ ca khám" (dị ứng, thai, thuốc đang dùng…).
 *   Tin cũ ở chế độ "ca_kham" vẫn hiển thị như trước.
 * Khâu tách mệnh đề không bao giờ đi qua mô hình ngoài.
 */
export type CheDoHoi = "ca_kham" | "tra_cuu";

interface ClinicalEvidenceDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  chatHistory: ClinicalChatMessage[];
  onSendMessage: (query: string, mode: CheDoHoi, nguon?: NguonBat) => void;
  onNewChat: () => void;
  isLoading?: boolean;
  patientContext: string;
  /** Câu hỏi làm rõ sinh bằng luật từ hội thoại (noteMeta.questions). */
  ruleQuestions: string[];
  /** Đã có bản nháp chưa — chưa có thì chưa có câu hỏi làm rõ. */
  hasDraft: boolean;
  /** Công tắc "Mô hình ngoài" đang bật không. */
  allowExternal: boolean;
  /** Có gì để mô hình đọc không (lời thoại hoặc ngữ cảnh). */
  hasMaterial: boolean;
  onSuggestQuestions: () => Promise<{ questions: CauHoiNgoai[]; model: string; seconds?: number } | null>;
  onAddToContext: (text: string) => void;
}

const MAU_NHOM: Record<string, string> = {
  "Triệu chứng": "bg-amber-50 text-amber-800 border-amber-200",
  "Tiền sử": "bg-blue-50 text-[#0C4A6E] border-blue-200",
  Thuốc: "bg-violet-50 text-violet-800 border-violet-200",
  "Dị ứng": "bg-rose-50 text-rose-800 border-rose-200",
  "Người bị": "bg-orange-50 text-orange-800 border-orange-200",
  "Thời gian": "bg-sky-50 text-[#0369A1] border-[#BAE6FD]",
  Khám: "bg-teal-50 text-teal-800 border-teal-200",
  "Chức năng": "bg-emerald-50 text-emerald-800 border-emerald-200",
  Khác: "bg-slate-50 text-slate-700 border-slate-200",
};

export const ClinicalEvidenceDrawer: React.FC<ClinicalEvidenceDrawerProps> = ({
  isOpen,
  onClose,
  chatHistory,
  onSendMessage,
  onNewChat,
  isLoading = false,
  patientContext,
  ruleQuestions,
  hasDraft,
  allowExternal,
  hasMaterial,
  onSuggestQuestions,
  onAddToContext,
}) => {
  const [inputText, setInputText] = useState("");
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [isExpandedFull, setIsExpandedFull] = useState(false);
  // Có hội thoại rồi thì gập khối câu hỏi làm rõ, để câu trả lời mới không bị đẩy xuống dưới.
  const [moCauHoi, setMoCauHoi] = useState(chatHistory.length === 0);
  const [deXuat, setDeXuat] = useState<{ questions: CauHoiNgoai[]; model: string; seconds?: number } | null>(null);
  const [dangDeXuat, setDangDeXuat] = useState(false);
  const [daThem, setDaThem] = useState<Set<string>>(new Set());
  const [moNguon, setMoNguon] = useState<Record<string, boolean>>({});

  // Tin mới: gập khối câu hỏi, cuộn tới đầu tin cuối (đọc câu trả lời từ đầu, không nhảy xuống đáy).
  const vungCuon = useRef<HTMLDivElement>(null);
  const soTinTruoc = useRef(chatHistory.length);
  useEffect(() => {
    if (chatHistory.length > soTinTruoc.current) {
      setMoCauHoi(false);
      requestAnimationFrame(() => {
        const tin = vungCuon.current?.querySelectorAll("[data-tin]");
        tin?.[tin.length - 1]?.scrollIntoView({ block: "start", behavior: "smooth" });
      });
    }
    soTinTruoc.current = chatHistory.length;
  }, [chatHistory.length]);
  useEffect(() => {
    if (isLoading) requestAnimationFrame(() => vungCuon.current?.scrollTo({ top: vungCuon.current.scrollHeight, behavior: "smooth" }));
  }, [isLoading]);

  // Đếm giây lúc chờ, hiện bước đang làm (đọc ca -> tra nguồn -> tổng hợp).
  const [giayCho, setGiayCho] = useState(0);
  useEffect(() => {
    if (!isLoading) return;
    setGiayCho(0);
    const t = setInterval(() => setGiayCho((g) => g + 1), 1000);
    return () => clearInterval(t);
  }, [isLoading]);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim() || isLoading || !allowExternal) return;
    onSendMessage(inputText.trim(), "tra_cuu");
    setInputText("");
  };

  const handleCopyMessage = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const deXuatThem = async () => {
    setDangDeXuat(true);
    try {
      const d = await onSuggestQuestions();
      if (d) setDeXuat(d);
    } finally {
      setDangDeXuat(false);
    }
  };

  const themVaoNguCanh = (cau: string) => {
    onAddToContext(cau);
    setDaThem((prev) => new Set(prev).add(cau));
  };

  const NutThem = ({ cau }: { cau: string }) =>
    daThem.has(cau) ? (
      <span
        className="w-6 h-6 rounded-lg bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center justify-center flex-shrink-0"
        title="Đã thêm vào tab Ngữ cảnh"
      >
        <Check size={13} />
      </span>
    ) : (
      <button
        onClick={() => themVaoNguCanh(cau)}
        className="w-6 h-6 rounded-lg bg-[#E0F2FE] hover:bg-[#0284C7] hover:text-white text-[#0369A1] border border-[#BAE6FD] flex items-center justify-center transition-all shadow-tactile-doctor-pill flex-shrink-0 active:translate-y-0.5"
        title="Thêm câu này vào tab Ngữ cảnh"
      >
        <Plus size={13} className="stroke-[2.5]" />
      </button>
    );

  const khoiCauHoi = (
    <div className="flex flex-col gap-3 py-1">
      <button
        onClick={() => setMoCauHoi(!moCauHoi)}
        className="flex items-center justify-between text-left"
      >
        <div className="flex items-center gap-1.5">
          <span className="font-bold text-xs sm:text-sm text-[#0F172A]">Câu hỏi cần làm rõ</span>
          <span className="min-w-4 h-4 px-1 rounded-full bg-[#E0F2FE] text-[#0284C7] flex items-center justify-center text-[10px] font-bold border border-[#BAE6FD]">
            {ruleQuestions.length + (deXuat?.questions.length || 0)}
          </span>
        </div>
        {moCauHoi ? <ChevronUp size={14} className="text-[#0284C7]" /> : <ChevronDown size={14} className="text-[#0284C7]" />}
      </button>

      {moCauHoi && (
        <>
          {/* Câu hỏi sinh bằng luật từ chính hội thoại — tại chỗ */}
          <div className="flex flex-col gap-2">
            <p className="text-[11px] text-[#64748B]">
              Từ hội thoại · sinh bằng luật tại chỗ, không gửi ra ngoài
            </p>
            {!hasDraft ? (
              <p className="text-[11px] text-[#475569] bg-white rounded-xl border border-dashed border-[#BAE6FD] p-3">
                Chưa có bản nháp. Tạo bản nháp hồ sơ trước; câu hỏi làm rõ sinh từ hội thoại sẽ hiện ở đây.
              </p>
            ) : ruleQuestions.length === 0 ? (
              <p className="text-[11px] text-[#475569] bg-white rounded-xl border border-dashed border-[#BAE6FD] p-3">
                Luật không thấy chỗ nào cần hỏi lại trong hội thoại này.
              </p>
            ) : (
              ruleQuestions.map((q, i) => (
                <div
                  key={`l-${i}`}
                  className="bg-white rounded-2xl border border-[#BAE6FD] p-3 shadow-tactile-doctor-card flex items-start justify-between gap-2"
                >
                  <p className="text-xs font-semibold text-[#0F172A] leading-snug flex-1">{q}</p>
                  <NutThem cau={q} />
                </div>
              ))
            )}
          </div>

          {/* Phương án 1: mô hình ngoài đề xuất thêm */}
          <div className="flex flex-col gap-2 mt-1">
            <button
              onClick={deXuatThem}
              disabled={!allowExternal || !hasMaterial || dangDeXuat}
              className="flex items-center justify-between p-2.5 rounded-xl border border-[#BAE6FD] bg-white text-xs font-semibold text-[#0C4A6E] hover:bg-[#F0F9FF] shadow-tactile-doctor-pill transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              title={
                !allowExternal
                  ? "Bật công tắc “Mô hình ngoài” ở đầu khung soạn"
                  : !hasMaterial
                    ? "Cần lời thoại hoặc nội dung tab Ngữ cảnh"
                    : "Mô hình ngoài đọc ngữ cảnh, lời thoại và các mệnh đề đã tách"
              }
            >
              <span className="flex items-center gap-1.5">
                {dangDeXuat ? (
                  <RefreshCw size={13} className="animate-spin text-[#0284C7]" />
                ) : (
                  <Sparkles size={13} className="text-[#0284C7]" />
                )}
                {dangDeXuat ? "Đang đọc ca khám…" : deXuat ? "Đề xuất lại" : "Đề xuất thêm câu hỏi"}
              </span>
              {!allowExternal && <Lock size={12} className="text-[#94A3B8]" />}
            </button>
            {!allowExternal && (
              <p className="text-[10.5px] text-[#64748B]">
                Cần bật “Mô hình ngoài”: nội dung ca khám sẽ được gửi tới máy chủ ngoài (ai-box).
              </p>
            )}

            {deXuat && (
              <>
                <p className="text-[11px] text-[#64748B]">
                  Mô hình ngoài · {deXuat.model}
                  {deXuat.seconds ? ` · ${deXuat.seconds}s` : ""} · dựa trên ngữ cảnh, lời thoại và mệnh đề đã tách
                </p>
                {deXuat.questions.length === 0 && (
                  <p className="text-[11px] text-[#475569]">Mô hình không đề xuất câu nào.</p>
                )}
                {deXuat.questions.map((q, i) => (
                  <div
                    key={`n-${i}`}
                    className="bg-white rounded-2xl border border-[#BAE6FD] p-3 shadow-tactile-doctor-card"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <h4 className="text-xs font-bold text-[#0F172A] leading-snug">{q.hoi}</h4>
                        {q.goi_y && <p className="text-[11px] text-[#64748B] mt-0.5">{q.goi_y}</p>}
                      </div>
                      <NutThem cau={q.hoi} />
                    </div>
                    {(q.vi_sao || q.nhom || (q.luot && q.luot.length > 0)) && (
                      <div className="mt-2 flex flex-wrap items-center gap-1.5">
                        {q.nhom && (
                          <span
                            className={`px-2 py-0.5 rounded-md border text-[10px] font-semibold ${
                              MAU_NHOM[q.nhom] || MAU_NHOM["Khác"]
                            }`}
                          >
                            {q.nhom}
                          </span>
                        )}
                        {q.luot && q.luot.length > 0 && (
                          <span className="text-[10px] text-[#64748B] font-mono">lượt {q.luot.join(", ")}</span>
                        )}
                        {q.vi_sao && <span className="text-[10.5px] text-[#475569] w-full">{q.vi_sao}</span>}
                      </div>
                    )}
                  </div>
                ))}
              </>
            )}
          </div>
        </>
      )}
    </div>
  );

  return (
    <>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/25 z-30 2xl:hidden backdrop-blur-2xs transition-opacity"
        onClick={onClose}
      />

      <motion.div
        id="clinical-evidence-drawer"
        initial={{ x: "100%", opacity: 0.9 }}
        animate={{ x: 0, opacity: 1 }}
        exit={{ x: "100%", opacity: 0.9 }}
        transition={{ type: "spring", damping: 28, stiffness: 300 }}
        className={`bg-gradient-to-b from-[#F0F7FA] via-[#F8FBFC] to-[#EEF6FB] border-l border-[#CCE3F0] flex flex-col h-full z-40 2xl:z-20 fixed 2xl:relative right-0 top-0 bottom-0 shadow-2xl 2xl:shadow-none ${
          isExpandedFull
            ? "w-full sm:w-[540px] lg:w-[640px]"
            : "w-full sm:w-[400px] 2xl:w-[420px]"
        }`}
      >
        <div className="p-2.5 sm:p-3 border-b border-[#CCE3F0] flex items-center justify-between bg-white/90 backdrop-blur-xs relative z-30 gap-1 shadow-[0_1px_3px_rgba(2,132,199,0.04)]">
          <span className="text-xs font-semibold text-[#0369A1] bg-[#E0F2FE] border border-[#BAE6FD] px-2.5 py-1 rounded-xl">
            Câu hỏi &amp; tra cứu
          </span>

          <div className="flex items-center gap-1 flex-shrink-0">
            <button
              onClick={() => {
                onNewChat();
                setDeXuat(null);
                setDaThem(new Set());
              }}
              className="flex items-center gap-1 text-xs px-2 py-1 rounded-lg border border-[#CCE3F0] text-[#0C4A6E] hover:bg-[#E0F2FE] transition-colors whitespace-nowrap"
              title="Xoá các câu hỏi đáp trong ngăn này"
            >
              <Plus size={12} />
              <span className="text-[11px] font-medium hidden sm:inline">Hỏi mới</span>
            </button>
            <button
              onClick={() => setIsExpandedFull(!isExpandedFull)}
              className="p-1 rounded-lg text-[#64748B] hover:bg-[#E0F2FE] hover:text-[#0369A1] transition-colors hidden sm:flex"
              title={isExpandedFull ? "Thu nhỏ bảng" : "Mở rộng bảng"}
            >
              <Maximize2 size={13} />
            </button>
            <button
              onClick={onClose}
              className="p-1 rounded-lg text-[#64748B] hover:bg-[#E0F2FE] hover:text-[#0369A1] transition-colors"
              title="Đóng bảng này"
            >
              <X size={15} />
            </button>
          </div>
        </div>

        <div ref={vungCuon} className="flex-1 overflow-y-auto p-4 flex flex-col gap-4 text-left">
          {khoiCauHoi}

          {chatHistory.length > 0 && <div className="border-t border-[#CCE3F0]" />}

          {chatHistory.map((msg) => {
            if (msg.role === "user") {
              return (
                <motion.div
                  key={msg.id}
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2 }}
                  data-tin
                  className="flex flex-col items-end gap-1"
                >
                  <div className="max-w-[90%] bg-[#E0F2FE] text-[#0369A1] text-xs font-semibold px-4 py-2.5 rounded-2xl rounded-tr-xs border border-[#BAE6FD] shadow-tactile-doctor-pill leading-relaxed select-text">
                    {msg.content}
                  </div>
                </motion.div>
              );
            }

            if (msg.cauTruc) {
              return (
                <motion.div key={msg.id} data-tin initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.25 }} className="flex flex-col gap-2">
                  {msg.warning && (
                    <div className="flex items-start gap-1.5 p-2.5 rounded-xl border text-[11px] leading-snug bg-[#FEF9E7] border-[#F5E6B8] text-[#7A4B00]">
                      <ShieldAlert size={13} className="flex-shrink-0 mt-0.5" />
                      <span>{msg.warning}</span>
                    </div>
                  )}
                  <TraLoiCoNguon
                    msg={msg}
                    onAsk={(q) => !isLoading && allowExternal && onSendMessage(q, "tra_cuu")}
                    onCheckOther={(m) => {
                      if (isLoading || !allowExternal || !m.question) return;
                      const daDung = new Set((m.sources || []).filter((x) => x.cited).map((x) => x.nhom));
                      const nguon: NguonBat = Object.fromEntries(TAT_CA_NHOM.map((k) => [k, !daDung.has(k)]));
                      if (!Object.values(nguon).some(Boolean)) return;
                      onSendMessage(`${m.question} (tra nguồn khác)`, "tra_cuu", nguon);
                    }}
                    onAddToContext={onAddToContext}
                  />
                </motion.div>
              );
            }
            const coNguon = (msg.sources?.length ?? 0) > 0;
            const moDs = moNguon[msg.id] ?? true;
            return (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.25 }}
                data-tin
                className="flex flex-col gap-2"
              >
                {msg.warning && (
                  <div
                    className={`flex items-start gap-1.5 p-2.5 rounded-xl border text-[11px] leading-snug ${
                      msg.sources && msg.sources.length
                        ? "bg-[#FEF9E7] border-[#F5E6B8] text-[#7A4B00]"
                        : "bg-[#FDE8E8] border-[#F5C2C2] text-[#8C1D26]"
                    }`}
                  >
                    <ShieldAlert size={13} className="flex-shrink-0 mt-0.5" />
                    <span>{msg.warning}</span>
                  </div>
                )}

                {/* Cùng kiểu với câu trả lời có nguồn (TraLoiCoNguon): dải đầu, thân không khung, thanh thao tác. */}
                <div className="rounded-xl bg-[#F0F9FF] border border-[#CCE3F0]">
                  {coNguon ? (
                    <button
                      onClick={() => setMoNguon((p) => ({ ...p, [msg.id]: !moDs }))}
                      className="w-full flex items-center justify-between px-3 py-2 text-[11.5px] text-[#0C4A6E]"
                    >
                      <span className="flex items-center gap-1.5">
                        <BookOpen size={12} className="text-[#0284C7]" />
                        {msg.sources?.length || 0} tài liệu đã tra{msg.removedSources ? ` · bỏ ${msg.removedSources}` : ""}
                      </span>
                      <span className="flex items-center gap-1 text-[#0369A1]">
                        Xem nguồn {moDs ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                      </span>
                    </button>
                  ) : (
                    <div className="flex items-center gap-1.5 px-3 py-2 text-[11.5px] text-[#0C4A6E]">
                      <Stethoscope size={12} className="text-[#0284C7]" />
                      Trả lời từ hội thoại của ca này · không cần tra tài liệu
                    </div>
                  )}
                  {coNguon && moDs && (
                    <ol className="px-3 pb-2.5 space-y-1.5">
                      {msg.sources!.map((s, idx) => (
                        <li key={idx} className="flex items-start gap-1.5 text-[11px] min-w-0">
                          <span className="font-mono text-[#64748B]">[{s.so ?? idx + 1}]</span>
                          <a href={s.url} target="_blank" rel="noopener noreferrer" className="text-[#0F172A] hover:text-[#0369A1] hover:underline break-words min-w-0">
                            {s.name}<span className="text-[#64748B]"> · {s.domain}</span>
                          </a>
                        </li>
                      ))}
                    </ol>
                  )}
                </div>

                <div className="text-[12.5px] text-[#1E293B] leading-relaxed select-text">
                  <Markdown
                    components={{
                      h3: ({ node, ...props }) => <h3 className="text-[13px] font-bold text-[#0F172A] mt-3 mb-1.5" {...props} />,
                      p: ({ node, ...props }) => <p className="my-1.5 px-0.5 leading-relaxed" {...props} />,
                      ul: ({ node, ...props }) => <ul className="list-disc pl-4 space-y-1.5 my-2" {...props} />,
                      ol: ({ node, ...props }) => <ol className="list-decimal pl-4 space-y-1.5 my-2" {...props} />,
                      strong: ({ node, ...props }) => <strong className="font-semibold text-[#0F172A]" {...props} />,
                      // "(lượt 12)" được đổi thành `lượt 12` ở dưới -> hiện thành thẻ nhỏ, giống thẻ nguồn.
                      code: ({ node, ...props }) => (
                        <span className="inline-flex items-center gap-1 align-middle mx-0.5 px-1.5 py-[1px] rounded-md bg-[#F1F5F9] border border-[#E2E8F0] text-[10.5px] text-[#475569] font-sans" {...props} />
                      ),
                      blockquote: ({ node, ...props }) => (
                        <blockquote className="mt-3 border-l-4 border-[#F2DFA8] bg-[#FFFBEB] px-3 py-1.5 rounded-r-lg text-[11px] text-[#7A4B00] [&_p]:my-0" {...props} />
                      ),
                    }}
                  >
                    {msg.content
                      // dòng "Nguồn: chỉ hội thoại…" đã có ở dải đầu
                      .replace(/\n*\*\*Nguồn:\*\* chỉ hội thoại[^\n]*/g, "")
                      .replace(/\(\s*(lượt\s*[\d,\s–-]+?)\s*\)/gi, " `$1`")}
                  </Markdown>

                  <div className="flex flex-wrap items-center gap-1 mt-2 pt-2 border-t border-[#E2ECF3] text-[#64748B]">
                    <span className="flex-1" />
                    <button
                      onClick={() => handleCopyMessage(msg.id, msg.content)}
                      title="Chép câu trả lời"
                      className="p-1.5 rounded-md hover:bg-[#E0F2FE] hover:text-[#0369A1]"
                    >
                      {copiedId === msg.id ? <Check size={13} className="text-emerald-600" /> : <Copy size={13} />}
                    </button>
                    <button
                      onClick={() => themVaoNguCanh(msg.content)}
                      title="Thêm vào tab Ngữ cảnh"
                      className="p-1.5 rounded-md hover:bg-[#E0F2FE] hover:text-[#0369A1]"
                    >
                      {daThem.has(msg.content) ? <Check size={13} className="text-emerald-600" /> : <ListPlus size={13} />}
                    </button>
                  </div>
                  {msg.meta && <div className="text-[10px] text-[#94A3B8] leading-snug">{msg.meta}</div>}
                </div>
              </motion.div>
            );
          })}

          {isLoading && (
            <div className="bg-white rounded-2xl border border-[#CCE3F0] p-3.5 flex items-start gap-3">
              <RefreshCw size={14} className="animate-spin text-[#0284C7] mt-0.5 flex-shrink-0" />
              <div className="flex-1 min-w-0 text-xs text-[#475569] space-y-1">
                {[
                  ["Đọc ca khám", 0],
                  ["Tra nguồn: Bộ Y tế, MSD, DailyMed, StatPearls, AAFP, NICE, WHO, CDC, PubMed", 3],
                  ["Tổng hợp theo phương án, kiểm số liệu", 14],
                ].map(([chu, tu], i, ds) => {
                  const xong = i < ds.length - 1 && giayCho >= (ds[i + 1][1] as number);
                  const dang = giayCho >= (tu as number) && !xong;
                  return (
                    <div key={i} className={`flex items-start gap-1.5 ${dang ? "text-[#0369A1] font-semibold" : xong ? "text-[#64748B]" : "text-[#94A3B8]"}`}>
                      <span className="w-3 flex-shrink-0">{xong ? "✓" : dang ? "•" : "○"}</span>
                      <span>{chu}</span>
                    </div>
                  );
                })}
                <div className="text-[10.5px] text-[#94A3B8] tabular-nums">{giayCho} giây · thường 15–25 giây</div>
              </div>
            </div>
          )}
        </div>

        <div className="p-3 border-t border-[#BAE6FD] bg-gradient-to-b from-[#F8FBFC] to-[#F0F9FF] shadow-[0_-4px_16px_rgba(2,132,199,0.06)] space-y-1.5">
          {allowExternal && chatHistory.length === 0 && (   // có hội thoại thì dùng "Hỏi tiếp" trong câu trả lời
            <div className="flex flex-wrap gap-1.5">
              {GOI_Y_NHANH.map((g) => (
                <button
                  key={g}
                  type="button"
                  disabled={isLoading}
                  onClick={() => onSendMessage(g, "tra_cuu")}
                  className="px-2.5 py-1 rounded-full border border-[#BAE6FD] bg-white text-[10.5px] text-[#0369A1] hover:bg-[#E0F2FE] disabled:opacity-40 text-left"
                >
                  {g}
                </button>
              ))}
            </div>
          )}

          <form
            onSubmit={handleSubmit}
            className="bg-white rounded-2xl border-[1.5px] border-[#BAE6FD] shadow-tactile-box focus-within:border-[#0284C7] focus-within:ring-2 focus-within:ring-[#BAE6FD]/50 p-2.5 flex flex-col gap-2 transition-all"
          >
            <div className="flex items-center gap-1 px-2.5 py-0.5 rounded-md bg-[#E0F2FE] border border-[#BAE6FD] text-[11px] text-[#0369A1] w-fit max-w-full">
              <User size={11} className="text-[#0284C7] flex-shrink-0" />
              <span className="font-semibold text-[#0C4A6E] truncate">{patientContext || "Ca khám hiện tại"}</span>
            </div>

            <div className="flex items-end gap-2">
              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyDown={(e) => {
                  // Enter gửi luôn (không trông vào gửi ngầm của form); đang gõ dấu (IME) thì bỏ qua.
                  if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) handleSubmit(e);
                }}
                disabled={!allowExternal}
                placeholder={
                  !allowExternal
                    ? "Bật “Mô hình ngoài” để hỏi"
                    : "VD: bệnh nhân này dùng amoxicillin được không? · ai bị dị ứng thuốc?"
                }
                className="flex-1 min-w-0 text-xs text-[#0F172A] placeholder-[#94A3B8] bg-transparent border-none focus:outline-none px-1 py-1 disabled:cursor-not-allowed"
              />
              <button
                type="submit"
                disabled={!inputText.trim() || isLoading || !allowExternal}
                className="w-7 h-7 rounded-full bg-[#0284C7] text-white flex items-center justify-center hover:bg-[#0369A1] disabled:opacity-40 transition-all flex-shrink-0 active:translate-y-0.5"
                title="Gửi câu hỏi"
              >
                <ArrowUp size={13} className="stroke-[2.5]" />
              </button>
            </div>
          </form>

          <p
            className="text-[10px] text-[#0369A1]/80 text-center px-1 leading-snug"
            title="Nguồn: Bộ Y tế (phác đồ + kcb.vn), MSD Manual, DailyMed/FDA, StatPearls, AAFP, NICE, WHO, CDC, MedlinePlus, PubMed/PMC"
          >
            Đọc ca khám + 11 nguồn chính thống · chỉ để tham khảo, bác sĩ quyết định
          </p>
        </div>
      </motion.div>
    </>
  );
};
