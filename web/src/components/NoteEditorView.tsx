import React, { useState, useEffect, useRef } from "react";
import { DocumentTabItem } from "../types";
import { ghepMenhDe } from "../lib/ghepMenhDe";
import {
  FileText,
  Edit2,
  MoreHorizontal,
  Mic,
  MicOff,
  Undo,
  Redo,
  Copy,
  Check,
  ChevronDown,
  ThumbsUp,
  ThumbsDown,
  Sparkles,
  Clock,
  RefreshCw,
  Download,
  Printer,
  FileCode,
} from "lucide-react";

/** Một mệnh đề cần tô trong bản nháp khi ngăn duyệt đang mở. */
export type DanhDauMD = {
  id: number;
  text: string;
  /** Chữ bác sĩ đã sửa ở ngăn duyệt — cũng dùng để tìm câu. */
  textKhac?: string[];
  trangThai: "canh" | "luuy" | "ok" | "giu" | "sua" | "bo";
};

interface NoteEditorViewProps {
  tab: DocumentTabItem;
  onUpdateContent: (content: string) => void;
  onRegenerateNote?: (style: string) => void;
  isGenerating?: boolean;
  /** Ngăn duyệt cạnh bản nháp đang mở: tô từng câu theo trạng thái mệnh đề. */
  danhDau?: DanhDauMD[];
  chonId?: number | null;
  onChonMenhDe?: (id: number | null) => void;
}

const MAU_TO: Record<DanhDauMD["trangThai"], string> = {
  canh: "bg-[#FDE2E2] decoration-[#E86A6A]",
  luuy: "bg-[#FEF3C7] decoration-[#D9A441]",
  ok: "bg-transparent decoration-[#9ED9C0]",
  giu: "bg-[#E3F6EE] decoration-[#34B889]",
  sua: "bg-[#FEF3C7] decoration-[#D9A441]",
  bo: "bg-[#F1F5F9] line-through text-[#94A3B8] decoration-[#94A3B8]",
};

/** Dòng tiêu đề mục: viết hoa toàn bộ và ngắn ("LÝ DO KHÁM BỆNH", "CẦN XÁC NHẬN"), hoặc "## …". */
function laTieuDeMuc(dong: string) {
  const t = dong.trim();
  if (!t) return false;
  if (/^#{1,4}\s+\S/.test(t)) return true;
  return t.length <= 60 && /\p{Lu}/u.test(t) && t === t.toLocaleUpperCase("vi") && !/[.;]$/.test(t);
}

export const NoteEditorView: React.FC<NoteEditorViewProps> = ({
  tab,
  onUpdateContent,
  onRegenerateNote,
  isGenerating = false,
  danhDau,
  chonId = null,
  onChonMenhDe,
}) => {
  const [copied, setCopied] = useState(false);
  const [liked, setLiked] = useState<boolean | null>(null);
  const [isStyleMenuOpen, setIsStyleMenuOpen] = useState(false);
  const [isExportMenuOpen, setIsExportMenuOpen] = useState(false);
  const [personalisationOn, setPersonalisationOn] = useState(true);

  // Dictation state (Đọc chính tả trực tiếp bằng giọng nói)
  const [isDictating, setIsDictating] = useState(false);
  const [dangSua, setDangSua] = useState(false);
  const giayRef = useRef<HTMLDivElement>(null);
  // Mở ô sửa thì luôn đặt con trỏ vào ô (autoFocus không chắc chạy). Ô chỉ quay về bản định dạng khi
  // MẤT con trỏ; nếu con trỏ chưa từng vào ô thì ô kẹt ở chế độ sửa (gặp 24/09).
  const oSuaRef = useRef<HTMLTextAreaElement>(null);
  useEffect(() => {
    if (!dangSua) return;
    const h = requestAnimationFrame(() => oSuaRef.current?.focus({ preventScroll: true }));
    return () => cancelAnimationFrame(h);
  }, [dangSua]);
  // Ghép mệnh đề với câu: nguyên văn trước, rồi gần đúng (bác sĩ đã sửa chữ trong bản nháp).
  const ghep = danhDau?.length ? ghepMenhDe(tab.content, danhDau, laTieuDeMuc) : null;
  const mdTheoId = new Map((danhDau || []).map((d) => [d.id, d]));
  const catDong = (dong: string, i: number) => {
    const ra: Array<{ chu: string; md?: DanhDauMD; ganDung?: boolean }> = [];
    let vt = 0;
    for (const g of ghep?.get(i) || []) {
      const md = mdTheoId.get(g.id);
      if (!md || g.bd < vt) continue;
      if (g.bd > vt) ra.push({ chu: dong.slice(vt, g.bd) });
      ra.push({ chu: dong.slice(g.bd, g.kt), md, ganDung: g.ganDung });
      vt = g.kt;
    }
    if (vt < dong.length) ra.push({ chu: dong.slice(vt) });
    return ra;
  };
  useEffect(() => {
    if (chonId === null || chonId === undefined) return;
    // Đợi khung hình sau: màn hẹp vừa chuyển từ ngăn duyệt sang bản nháp (đang ẩn -> hiện), cuộn ngay
    // lúc đó không có tác dụng (thử 24/09).
    const h = requestAnimationFrame(() =>
      giayRef.current?.querySelector(`[data-md="${chonId}"]`)?.scrollIntoView({ block: "center", behavior: "smooth" }));
    return () => cancelAnimationFrame(h);
  }, [chonId]);
  const recognitionRef = useRef<any>(null);

  // Undo / Redo history
  const [history, setHistory] = useState<string[]>([tab.content]);
  const [historyIndex, setHistoryIndex] = useState(0);

  useEffect(() => {
    // Stop dictation if tab changes
    if (isDictating && recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (e) {}
      setIsDictating(false);
    }
  }, [tab.id]);

  const handleTextChange = (newVal: string) => {
    onUpdateContent(newVal);
    const newHist = history.slice(0, historyIndex + 1);
    newHist.push(newVal);
    setHistory(newHist);
    setHistoryIndex(newHist.length - 1);
  };

  const handleUndo = () => {
    if (historyIndex > 0) {
      const prev = historyIndex - 1;
      setHistoryIndex(prev);
      onUpdateContent(history[prev]);
    }
  };

  const handleRedo = () => {
    if (historyIndex < history.length - 1) {
      const next = historyIndex + 1;
      setHistoryIndex(next);
      onUpdateContent(history[next]);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(tab.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Tải file Text
  const handleDownloadTxt = () => {
    const blob = new Blob([tab.content], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${tab.title.replace(/[^a-z0-9\u00C0-\u024F\u1E00-\u1EFF]/gi, "_")}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    setIsExportMenuOpen(false);
  };

  // Tải file Markdown
  const handleDownloadMd = () => {
    const blob = new Blob([tab.content], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${tab.title.replace(/[^a-z0-9\u00C0-\u024F\u1E00-\u1EFF]/gi, "_")}.md`;
    a.click();
    URL.revokeObjectURL(url);
    setIsExportMenuOpen(false);
  };

  // Toggle Đọc chính tả trực tiếp bằng giọng nói
  const toggleDictation = () => {
    // Tắt có chủ đích: Web Speech API trên Chrome gửi âm thanh lên máy chủ Google.
    const SpeechRecognition: any = null;

    if (!SpeechRecognition) {
      alert("Đọc chính tả trực tiếp đã tắt: nhận dạng giọng nói của trình duyệt gửi âm thanh lên máy chủ Google. Dùng nút Ghi âm ở đầu trang — tệp ghi âm được chép bằng PhoWhisper chạy tại chỗ.");
      return;
    }

    if (isDictating) {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (e) {}
      }
      setIsDictating(false);
    } else {
      try {
        const recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = false;
        recognition.lang = "vi-VN";

        recognition.onresult = (event: any) => {
          let dictatedChunk = "";
          for (let i = event.resultIndex; i < event.results.length; ++i) {
            if (event.results[i].isFinal) {
              dictatedChunk += event.results[i][0].transcript;
            }
          }
          if (dictatedChunk.trim()) {
            const updated = tab.content ? `${tab.content.trimEnd()} ${dictatedChunk.trim()}` : dictatedChunk.trim();
            handleTextChange(updated);
          }
        };

        recognition.onerror = (e: any) => {
          if (e.error !== "no-speech") {
            console.warn("Dictation error:", e);
          }
        };

        recognition.onend = () => {
          // If user hasn't explicitly stopped, keep going
          if (isDictating && recognitionRef.current) {
            try {
              recognition.start();
            } catch (err) {}
          } else {
            setIsDictating(false);
          }
        };

        recognition.start();
        recognitionRef.current = recognition;
        setIsDictating(true);
      } catch (err) {
        console.error("Lỗi khi mở đọc chính tả:", err);
        setIsDictating(false);
      }
    }
  };

  // Du an chi co MOT cach viet ho so (nhanh C_khoa). Khong co "phong cach" theo loi nhac:
  // de nut do lai thi nguoi xem tuong doi phong cach la doi cach sinh.
  const styleOptions = [{ id: "Goldilocks", label: "Dựng lại bản nháp" }];

  // Tính số từ và ký tự
  const wordsCount = tab.content.trim() ? tab.content.trim().split(/\s+/).length : 0;
  const charsCount = tab.content.length;

  return (
    <div
      id="note-editor-view"
      className="flex-1 flex flex-col bg-[#F8FBFC] overflow-hidden select-none"
    >
      {/* Subheader Toolbar */}
      <div className="flex items-center justify-between px-2.5 sm:px-5 py-2 border-b border-[#CCE3F0] bg-[#F8FBFC] shadow-[0_1px_4px_rgba(2,132,199,0.04)] gap-2 overflow-x-auto no-scrollbar">
        {/* Trái: Nhãn tài liệu & Chọn định dạng phong cách */}
        <div className="flex items-center gap-1.5 sm:gap-2 flex-shrink-0">
          <div className="flex items-center gap-1.5 px-2.5 sm:px-3 py-1 rounded-xl bg-[#E0F2FE] border border-[#BAE6FD] shadow-tactile-doctor-pill text-xs font-semibold text-[#0369A1] whitespace-nowrap flex-shrink-0">
            <FileText size={13} className="text-[#0284C7]" />
            <span className="truncate max-w-[120px] sm:max-w-[200px]">{tab.title}</span>
          </div>

          {/* Chọn phong cách: Cân bằng / Tự do */}
          <div className="relative flex-shrink-0">
            <button
              onClick={() => setIsStyleMenuOpen(!isStyleMenuOpen)}
              className="flex items-center gap-1 px-2 sm:px-2.5 py-1 rounded-xl border border-[#BAE6FD] bg-white text-xs text-[#0C4A6E] hover:bg-[#F0F9FF] shadow-tactile-doctor-pill transition-all whitespace-nowrap"
            >
              <Edit2 size={12} className="text-[#0284C7]" />
              <span className="hidden sm:inline font-medium">
                {styleOptions.find((s) => s.id === (tab.templateStyle || "Goldilocks"))?.label ||
                  tab.templateStyle ||
                  "Cân bằng"}
              </span>
              <span className="inline sm:hidden font-medium">
                {tab.templateStyle === "Concise"
                  ? "Ngắn gọn"
                  : tab.templateStyle === "Free"
                  ? "Tự do"
                  : "Cân bằng"}
              </span>
              <ChevronDown size={11} className="text-[#0369A1]" />
            </button>

            {isStyleMenuOpen && (
              <>
                <div
                  className="fixed inset-0 z-30"
                  onClick={() => setIsStyleMenuOpen(false)}
                />
                <div className="absolute left-0 top-full mt-1.5 w-52 bg-white rounded-xl shadow-[0_8px_24px_rgba(2,132,199,0.16)] border border-[#BAE6FD] py-1.5 z-40 animate-in fade-in">
                  <div className="px-3 py-1 text-[10px] font-semibold text-[#0369A1] uppercase tracking-wider">
                    Định dạng đầu ra
                  </div>
                  {styleOptions.map((opt) => (
                    <button
                      key={opt.id}
                      onClick={() => {
                        setIsStyleMenuOpen(false);
                        if (onRegenerateNote) {
                          onRegenerateNote(opt.id);
                        }
                      }}
                      className={`w-full flex items-center justify-between px-3 py-1.5 text-xs text-left hover:bg-[#E0F2FE] transition-colors ${
                        (tab.templateStyle || "Goldilocks") === opt.id
                          ? "font-semibold text-[#0284C7] bg-[#F0F9FF]"
                          : "text-[#334155]"
                      }`}
                    >
                      <span>{opt.label}</span>
                      {(tab.templateStyle || "Goldilocks") === opt.id && (
                        <Check size={12} className="text-[#0284C7]" />
                      )}
                    </button>
                  ))}
                </div>
              </>
            )}
          </div>

          <button
            onClick={() => onRegenerateNote && onRegenerateNote(tab.templateStyle || "Goldilocks")}
            disabled={isGenerating}
            className="p-1 rounded-lg text-[#0369A1] hover:text-[#0284C7] hover:bg-[#E0F2FE] transition-colors disabled:opacity-40 flex-shrink-0"
            title="Tạo lại bệnh án bằng Gemini AI"
          >
            <RefreshCw size={13} className={isGenerating ? "animate-spin" : ""} />
          </button>
        </div>

        {/* Phải: Đọc chính tả, Hoàn tác, Làm lại, Sao chép & Xuất */}
        <div className="flex items-center gap-1 sm:gap-1.5 flex-shrink-0">
          {/* Nút Đọc chính tả thực tế */}
          <button
            onClick={toggleDictation}
            className={`flex items-center gap-1 sm:gap-1.5 px-2.5 sm:px-3 py-1 text-xs border rounded-xl transition-all shadow-tactile-doctor-pill whitespace-nowrap flex-shrink-0 ${
              isDictating
                ? "bg-red-50 border-red-300 text-red-700 font-semibold animate-pulse"
                : "text-[#0C4A6E] hover:bg-[#F0F9FF] border-[#BAE6FD] bg-white"
            }`}
            title={isDictating ? "Bấm để dừng đọc chính tả" : "Bấm và nói tiếng Việt để ghi văn bản trực tiếp"}
          >
            {isDictating ? (
              <>
                <span className="w-1.5 h-1.5 rounded-full bg-red-600 animate-ping" />
                <MicOff size={13} />
                <span>Đang đọc...</span>
              </>
            ) : (
              <>
                <Mic size={13} className="text-[#0284C7]" />
                <span className="text-[11px] hidden sm:inline font-medium">Đọc chính tả</span>
                <span className="text-[11px] inline sm:hidden font-medium">Đọc</span>
              </>
            )}
          </button>

          <button
            onClick={handleUndo}
            disabled={historyIndex <= 0}
            className="p-1 sm:p-1.5 text-[#0369A1] hover:text-[#0284C7] hover:bg-[#E0F2FE] rounded-lg disabled:opacity-30 transition-colors flex-shrink-0"
            title="Hoàn tác (Undo)"
          >
            <Undo size={13} />
          </button>

          <button
            onClick={handleRedo}
            disabled={historyIndex >= history.length - 1}
            className="p-1 sm:p-1.5 text-[#0369A1] hover:text-[#0284C7] hover:bg-[#E0F2FE] rounded-lg disabled:opacity-30 transition-colors flex-shrink-0"
            title="Làm lại (Redo)"
          >
            <Redo size={13} />
          </button>

          {/* Nút Sao chép & Menu Xuất file */}
          <div className="relative flex-shrink-0">
            <div className="flex items-center bg-[#0284C7] text-white rounded-xl overflow-hidden shadow-tactile-doctor hover:bg-[#0369A1] transition-all whitespace-nowrap">
              <button
                onClick={handleCopy}
                className="flex items-center gap-1 sm:gap-1.5 px-2.5 sm:px-3 py-1 text-xs font-semibold whitespace-nowrap hover:bg-[#0369A1]"
              >
                {copied ? (
                  <>
                    <Check size={12} className="text-white" />
                    <span>Đã chép</span>
                  </>
                ) : (
                  <>
                    <Copy size={12} />
                    <span>Sao chép</span>
                  </>
                )}
              </button>
              <button
                onClick={() => setIsExportMenuOpen(!isExportMenuOpen)}
                className="px-1.5 py-1 border-l border-white/20 hover:bg-[#0369A1]"
                title="Tùy chọn tải về / In"
              >
                <ChevronDown size={11} />
              </button>
            </div>

            {isExportMenuOpen && (
              <>
                <div
                  className="fixed inset-0 z-30"
                  onClick={() => setIsExportMenuOpen(false)}
                />
                <div className="absolute right-0 top-full mt-1.5 w-48 bg-white rounded-xl shadow-[0_8px_24px_rgba(2,132,199,0.16)] border border-[#BAE6FD] py-1 z-40 text-left animate-in fade-in">
                  <button
                    onClick={() => {
                      handleCopy();
                      setIsExportMenuOpen(false);
                    }}
                    className="w-full flex items-center gap-2 px-3 py-1.5 text-xs text-[#0C4A6E] hover:bg-[#E0F2FE]"
                  >
                    <Copy size={13} className="text-[#0284C7]" />
                    <span>Sao chép vào Clipboard</span>
                  </button>
                  <button
                    onClick={handleDownloadTxt}
                    className="w-full flex items-center gap-2 px-3 py-1.5 text-xs text-[#0C4A6E] hover:bg-[#E0F2FE]"
                  >
                    <Download size={13} className="text-[#0284C7]" />
                    <span>Tải tệp văn bản (.txt)</span>
                  </button>
                  <button
                    onClick={handleDownloadMd}
                    className="w-full flex items-center gap-2 px-3 py-1.5 text-xs text-[#0C4A6E] hover:bg-[#E0F2FE]"
                  >
                    <FileCode size={13} className="text-[#0284C7]" />
                    <span>Tải tệp Markdown (.md)</span>
                  </button>
                  <button
                    onClick={() => {
                      setIsExportMenuOpen(false);
                      window.print();
                    }}
                    className="w-full flex items-center gap-2 px-3 py-1.5 text-xs text-[#0C4A6E] hover:bg-[#E0F2FE] border-t border-[#CCE3F0]"
                  >
                    <Printer size={13} className="text-[#0284C7]" />
                    <span>In hồ sơ bệnh án</span>
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Editor Main Content Area: Giấy bệnh án nổi khối */}
      <div className="flex-1 overflow-y-auto p-3 sm:p-6 lg:p-8 relative bg-gradient-to-b from-[#F0F7FA] via-[#F8FBFC] to-[#EEF6FB]">
        {isGenerating && (
          <div className="absolute inset-0 bg-white/80 backdrop-blur-2xs flex items-center justify-center z-10">
            <div className="flex items-center gap-2.5 px-5 py-3 bg-white rounded-2xl shadow-[0_8px_30px_rgba(2,132,199,0.12)] border border-[#BAE6FD] text-xs text-[#0F172A]">
              <RefreshCw size={15} className="animate-spin text-[#0284C7]" />
              <span className="font-semibold text-[#0369A1]">MediTrace Sentinel AI đang tổng hợp bệnh án theo tiêu chuẩn...</span>
            </div>
          </div>
        )}

        <div className="max-w-3xl mx-auto bg-white rounded-2xl border border-[#BAE6FD] shadow-tactile-doctor-card p-5 sm:p-8 min-h-[500px]">
          {/* Textarea không in đậm được từng dòng: bình thường hiện bản đã định dạng (tiêu đề mục đậm),
              bấm vào là sửa, bấm ra ngoài là về bản định dạng. Chưa có nội dung thì mở sẵn ô sửa. */}
          {dangSua || !tab.content.trim() ? (
            <textarea
              ref={oSuaRef}
              value={tab.content}
              onChange={(e) => handleTextChange(e.target.value)}
              onBlur={() => setDangSua(false)}
              placeholder="Nhập hoặc chỉnh sửa chi tiết hồ sơ bệnh án lâm sàng tại đây..."
              className="w-full h-full min-h-[460px] bg-transparent resize-none border-none focus:outline-none text-[15px] leading-relaxed text-[#0F172A] font-sans selection:bg-[#BAE6FD]/40"
              spellCheck={false}
            />
          ) : (
            <div
              role="textbox"
              tabIndex={0}
              aria-label="Hồ sơ bệnh án — bấm để sửa"
              title="Bấm để sửa"
              onClick={() => setDangSua(true)}
              onKeyDown={(e) => e.key === "Enter" && setDangSua(true)}
              ref={giayRef}
              className="min-h-[460px] cursor-text text-[15px] leading-relaxed text-[#0F172A] font-sans focus:outline-none rounded-lg"
            >
              {tab.content.split("\n").map((dong, i) =>
                laTieuDeMuc(dong) ? (
                  <div key={i} className="font-bold text-[#0C4A6E] tracking-wide mt-5 first:mt-0 mb-0.5">
                    {dong.replace(/^#{1,4}\s*/, "").trim()}
                  </div>
                ) : dong.trim() ? (
                  <div key={i} className="whitespace-pre-wrap break-words">
                    {ghep
                      ? catDong(dong, i).map((d, j) =>
                          d.md ? (
                            <span
                              key={j}
                              data-md={d.md.id}
                              onClick={(e) => {
                                e.stopPropagation();
                                onChonMenhDe?.(chonId === d.md!.id ? null : d.md!.id);
                              }}
                              title={d.ganDung
                                ? `Câu đã được sửa so với chữ máy trích: “${d.md.text}” — bấm để xem mệnh đề ở ngăn duyệt`
                                : "Bấm để xem mệnh đề này ở ngăn duyệt"}
                              className={`rounded px-0.5 -mx-0.5 underline decoration-2 underline-offset-4 cursor-pointer transition-shadow ${
                                d.ganDung ? "decoration-dotted" : ""} ${MAU_TO[d.md.trangThai]} ${
                                chonId === d.md.id ? "ring-2 ring-[#0284C7] bg-[#E0F2FE]" : "hover:ring-1 hover:ring-[#93C5FD]"
                              }`}
                            >
                              {d.chu}
                            </span>
                          ) : (
                            <span key={j}>{d.chu}</span>
                          )
                        )
                      : dong}
                  </div>
                ) : (
                  <div key={i} className="h-3" />
                )
              )}
            </div>
          )}
        </div>
      </div>

      {/* Dưới cùng: Đánh giá chất lượng & Trạng thái thống kê */}
      <div className="flex flex-wrap items-center justify-between px-3 sm:px-6 py-2.5 border-t border-[#BAE6FD] bg-gradient-to-b from-[#F8FBFC] to-[#F0F9FF] shadow-[0_-2px_12px_rgba(2,132,199,0.06)] text-xs text-[#0369A1] gap-2">
        <div className="flex items-center gap-2 sm:gap-3 flex-shrink-0">
          <div className="flex items-center gap-1 sm:gap-1.5">
            <button
              onClick={() => setLiked(liked === true ? null : true)}
              className={`p-1.5 rounded-lg border border-[#BAE6FD] transition-all ${
                liked === true
                  ? "bg-[#0284C7] text-white shadow-tactile-doctor"
                  : "bg-white text-[#64748B] hover:text-[#0284C7] hover:bg-[#E0F2FE] shadow-tactile-doctor-pill"
              }`}
              title="Bệnh án đạt yêu cầu"
            >
              <ThumbsUp size={13} className={liked === true ? "fill-current" : ""} />
            </button>
            <button
              onClick={() => setLiked(liked === false ? null : false)}
              className={`p-1.5 rounded-lg border border-[#BAE6FD] transition-all ${
                liked === false
                  ? "bg-red-500 text-white shadow-sm"
                  : "bg-white text-[#64748B] hover:text-red-600 hover:bg-red-50 shadow-tactile-doctor-pill"
              }`}
              title="Cần cải thiện chất lượng"
            >
              <ThumbsDown size={13} className={liked === false ? "fill-current" : ""} />
            </button>
          </div>

          <span className="text-[11px] text-[#0369A1] font-medium whitespace-nowrap">
            {wordsCount} từ • {charsCount} ký tự
          </span>
        </div>


        <div className="hidden md:flex items-center gap-1.5 text-[11px] text-[#0369A1]/80 font-medium whitespace-nowrap">
          <Clock size={12} className="text-[#0284C7]" />
          <span>Bản nháp — bác sĩ duyệt rồi mới dùng</span>
        </div>
      </div>
    </div>
  );
};
