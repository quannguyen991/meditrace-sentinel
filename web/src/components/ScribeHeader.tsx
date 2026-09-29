import React, { useState, useEffect, useRef } from "react";
import { Session } from "../types";
import {
  User,
  Trash2,
  Calendar,
  Globe,
  Zap,
  Upload,
  Plus,
  Play,
  Pause,
  Clock,
  Mic,
  Volume2,
  ChevronDown,
  Edit2,
  Check,
  PanelRight,
  Sparkles,
  AlertCircle,
  Share2,
  Printer,
} from "lucide-react";
import { ThanhAmThanh } from "./ThanhAmThanh";
import { RealAudioService } from "../services/realAudioService";
import { AudioDeviceDropdown } from "./AudioDeviceDropdown";
import { realAudioService } from "../services/realAudioService";
import { dongTuDoan, moTaTach, soNguoiNoiLonNhat } from "../lib/nguoiNoi";

interface ScribeHeaderProps {
  session: Session;
  onUpdateSession: (updated: Partial<Session>) => void;
  onDeleteSession: () => void;
  onCreateNewDocument: () => void;
  isRightDrawerOpen: boolean;
  onToggleRightDrawer: () => void;
}

export const ScribeHeader: React.FC<ScribeHeaderProps> = ({
  session,
  onUpdateSession,
  onDeleteSession,
  onCreateNewDocument,
  isRightDrawerOpen,
  onToggleRightDrawer,
}) => {
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [titleInput, setTitleInput] = useState(session.patientIdentifier);
  const [isEditingSubtitle, setIsEditingSubtitle] = useState(false);
  const [subtitleInput, setSubtitleInput] = useState(session.patientSubtitle);

  const [selectedSpeaker, setSelectedSpeaker] = useState(
    "Mặc định - Loa máy tính (System Audio)"
  );
  const [selectedMic, setSelectedMic] = useState(
    "Mặc định - Micrô hệ thống (System Microphone)"
  );
  const [audioDropdownMode, setAudioDropdownMode] = useState<"speaker" | "mic" | null>(
    null
  );

  // Real Audio & Recording state
  const [duration, setDuration] = useState(session.durationSeconds);
  const [isRecording, setIsRecording] = useState(session.isRecording);
  const khong = () => new Array(RealAudioService.SO_VACH).fill(0);
  const [audioFreqs, setAudioFreqs] = useState<number[]>(khong);
  const [amLuong, setAmLuong] = useState(0);
  const [imLang, setImLang] = useState(false);
  const lanCuoiCoTieng = useRef(Date.now());
  const [micError, setMicError] = useState<string | null>(null);
  const [isLangMenuOpen, setIsLangMenuOpen] = useState(false);

  useEffect(() => {
    setTitleInput(session.patientIdentifier);
    setSubtitleInput(session.patientSubtitle);
    setDuration(session.durationSeconds);
    setIsRecording(session.isRecording);
  }, [session.id]);

  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (isRecording) {
      timer = setInterval(() => {
        setDuration((prev) => {
          const next = prev + 1;
          onUpdateSession({ durationSeconds: next });
          return next;
        });
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [isRecording]);

  // Đã ghi mà 4 giây liền không có tiếng: báo để người dùng biết micrô có thể không thu được.
  useEffect(() => {
    if (!isRecording) {
      setImLang(false);
      setAmLuong(0);
      return;
    }
    lanCuoiCoTieng.current = Date.now();
    const id = setInterval(() => setImLang(Date.now() - lanCuoiCoTieng.current > 4000), 500);
    return () => clearInterval(id);
  }, [isRecording]);

  // Theo dõi mức âm thanh của micrô để vẽ thanh âm thanh; đăng ký riêng nên không bị thành phần khác ghi đè.
  useEffect(() => {
    return realAudioService.theoDoiMucAm((vol, freqs) => {
      setAudioFreqs(freqs);
      setAmLuong(vol);
      if (vol > 6) lanCuoiCoTieng.current = Date.now();
    });
  }, []);

  // Clean up when unmounting
  useEffect(() => {
    return () => {
      realAudioService.stop();
    };
  }, []);

  const toggleRecording = async () => {
    if (!isRecording) {
      setMicError(null);
      realAudioService.setLanguage(session.language === "English" ? "en-US" : "vi-VN");

      realAudioService.setCallbacks({
        onTranscriptChunk: (chunk: string, isFinal: boolean) => {
          if (isFinal) {
            onUpdateSession({
              transcript: session.transcript ? `${session.transcript.trimEnd()}\n${chunk.trim()}` : chunk.trim(),
            });
          }
        },
        onError: (err: string) => {
          setMicError(err);
          setIsRecording(false);
          onUpdateSession({ isRecording: false });
        },
        onAudioReady: (blob: Blob, url: string) => {
          onUpdateSession({ audioUrl: url });
          chepBangPhoWhisper(blob);
        },
      });

      const started = await realAudioService.start();
      if (started) {
        setIsRecording(true);
        onUpdateSession({ isRecording: true });
      } else {
        // Không mở được micrô: bỏ cờ "đang ghi" mà nút bắt đầu ở giữa màn hình vừa bật.
        onUpdateSession({ isRecording: false });
      }
    } else {
      // Dừng ghi: MediaRecorder trả tệp qua onAudioReady, tệp đó được gửi sang PhoWhisper.
      // Không mở ngay hộp chọn mẫu: bản chép chưa có thì chưa dựng được bản nháp.
      realAudioService.stop();
      setIsRecording(false);
      onUpdateSession({ isRecording: false });
      setAudioFreqs(khong());
    }
  };

  // Nút "Bắt đầu ghi âm" ở giữa màn hình (TranscriptView) chỉ bật cờ session.isRecording.
  // Cờ đó phải thật sự mở micrô, không chỉ đổi giao diện: khi cờ bật mà micrô chưa chạy thì mở.
  const dangKhoiDongMic = React.useRef(false);
  useEffect(() => {
    if (session.isRecording && !isRecording && !dangKhoiDongMic.current) {
      dangKhoiDongMic.current = true;
      toggleRecording().finally(() => {
        dangKhoiDongMic.current = false;
      });
    }
  }, [session.isRecording]);

  const handleFinishAndAnalyze = () => {
    realAudioService.stop();
    setIsRecording(false);
    onUpdateSession({ isRecording: false });
    setAudioFreqs(khong());
  };

  /**
   * Tệp ghi âm -> /api/transcribe -> dịch vụ tại chỗ (PhoWhisper). Vai người nói để
   * "Chưa rõ vai" cho tới khi người dùng sửa thành Bác sĩ / Bệnh nhân / Người nhà:
   * hệ thống KHÔNG đoán vai từ giọng nói.
   */
  const [dangChep, setDangChep] = useState(false);
  const chepBangPhoWhisper = async (blob: Blob) => {
    if (!blob || blob.size === 0) {
      setMicError("Không ghi được âm thanh nào. Kiểm tra micrô rồi thử lại.");
      return;
    }
    setDangChep(true);
    setMicError(null);
    try {
      const b64 = await new Promise<string>((resolve, reject) => {
        const r = new FileReader();
        r.onload = () => resolve(String(r.result).split(",")[1] || "");
        r.onerror = reject;
        r.readAsDataURL(blob);
      });
      const res = await fetch("/api/transcribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ audioBase64: b64, fileName: "ghi-am-micro.webm" }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.error || `Dịch vụ trả mã ${res.status}`);
      const doan: any[] = data.segments || [];
      if (!doan.length) throw new Error("PhoWhisper không nghe ra câu nào trong đoạn ghi âm.");
      const cu = session.transcript || "";
      const moi = dongTuDoan(doan, data.diarization, soNguoiNoiLonNhat(cu)).join("\n");
      onUpdateSession({
        transcript: cu ? `${cu.trimEnd()}\n${moi}` : moi,
      });
      setMicError(
        `Đã chép ${doan.length} lượt bằng ${doan[0]?.asr_model || "PhoWhisper"} (${data.seconds ?? "?"}s). ` +
          moTaTach(data.diarization)
      );
    } catch (err: any) {
      setMicError(err?.message || "Không chép được đoạn ghi âm");
    } finally {
      setDangChep(false);
    }
  };

  const handleSelectLanguage = (lang: string) => {
    setIsLangMenuOpen(false);
    onUpdateSession({ language: lang });
    realAudioService.setLanguage(lang === "English" ? "en-US" : "vi-VN");
  };

  const formatTimer = (totalSeconds: number) => {
    const mins = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    return `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
  };

  const handleSaveTitle = () => {
    setIsEditingTitle(false);
    onUpdateSession({ patientIdentifier: titleInput.trim() || "Thêm định danh bệnh nhân" });
  };

  const handleSaveSubtitle = () => {
    setIsEditingSubtitle(false);
    onUpdateSession({ patientSubtitle: subtitleInput.trim() || "Nhiễm virus, Ho khan, Sốt" });
  };

  return (
    <>
      <header
        id="scribe-header"
        className="bg-[#F8FBFC] border-b border-[#D0E2ED] shadow-[0_2px_8px_rgba(2,132,199,0.03)] px-3 @md:px-4 py-2 @md:py-2.5 flex flex-wrap items-center gap-x-3 gap-y-2 select-none relative z-20"
      >
      {/* Trái: Định danh bệnh nhân & Thông tin ca khám */}
      <div className="flex items-center gap-2 @md:gap-3 min-w-[11rem] flex-1 basis-[14rem]">
        <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-full bg-[#E0F2FE] border border-[#BAE6FD] shadow-[0_2px_6px_rgba(2,132,199,0.12)] flex items-center justify-center text-[#0284C7] flex-shrink-0">
          <User size={16} />
        </div>

        <div className="flex flex-col min-w-0 flex-1">
          <div className="flex items-center gap-1.5 min-w-0">
            {isEditingTitle ? (
              <div className="flex items-center gap-1 min-w-0">
                <input
                  type="text"
                  value={titleInput}
                  onChange={(e) => setTitleInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSaveTitle()}
                  className="text-xs sm:text-sm font-semibold text-[#0F172A] border-b border-[#0284C7] bg-transparent focus:outline-none px-0.5 max-w-[180px]"
                  autoFocus
                />
                <button
                  onClick={handleSaveTitle}
                  className="p-1 text-[#0284C7] hover:bg-[#E0F2FE] rounded flex-shrink-0"
                  title="Lưu định danh"
                >
                  <Check size={13} />
                </button>
              </div>
            ) : (
              <h1
                onClick={() => setIsEditingTitle(true)}
                className="text-xs sm:text-sm font-semibold text-[#0F172A] hover:text-[#0284C7] cursor-pointer flex items-center gap-1 group min-w-0"
                title={`${session.patientIdentifier} (Bấm để sửa)`}
              >
                <span className="truncate whitespace-nowrap block">
                  {session.patientIdentifier}
                </span>
                <Edit2 size={11} className="opacity-0 group-hover:opacity-70 text-[#64748B] flex-shrink-0" />
              </h1>
            )}

            <button
              onClick={onDeleteSession}
              className="text-[#94A3B8] hover:text-red-600 transition-colors p-0.5 flex-shrink-0"
              title="Xóa ca khám này"
            >
              <Trash2 size={12} />
            </button>
          </div>

          {/* Dòng tóm tắt triệu chứng & thời gian */}
          <div className="flex items-center gap-1.5 @md:gap-2.5 mt-0.5 text-xs text-[#64748B] min-w-0">
            {isEditingSubtitle ? (
              <div className="flex items-center gap-1 min-w-0">
                <input
                  type="text"
                  value={subtitleInput}
                  onChange={(e) => setSubtitleInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSaveSubtitle()}
                  className="text-[11px] text-[#64748B] border-b border-[#0284C7] bg-transparent focus:outline-none max-w-[140px]"
                  autoFocus
                />
                <button onClick={handleSaveSubtitle} title="Lưu triệu chứng" className="flex-shrink-0">
                  <Check size={11} />
                </button>
              </div>
            ) : (
              <span
                onClick={() => setIsEditingSubtitle(true)}
                className="text-[11px] text-[#64748B] cursor-pointer hover:underline font-medium truncate min-w-0 whitespace-nowrap block"
                title={`${session.patientSubtitle} (Bấm để sửa)`}
              >
                {session.patientSubtitle}
              </span>
            )}

            <div className="hidden @3xl:flex items-center gap-1 text-[11px] text-[#64748B] whitespace-nowrap flex-shrink-0">
              <Calendar size={11} />
              <span>{session.date}</span>
            </div>

            {/* Bộ chọn ngôn ngữ nhận diện */}
            <div className="relative flex-shrink-0">
              <button
                onClick={() => setIsLangMenuOpen(!isLangMenuOpen)}
                className="flex items-center gap-1 text-[10px] sm:text-[11px] text-[#64748B] hover:text-[#0284C7] transition-colors py-0.5 px-1 rounded-md hover:bg-[#E0F2FE] whitespace-nowrap"
                title="Bấm để đổi ngôn ngữ nhận diện giọng nói"
              >
                <Globe size={11} />
                <span className="font-medium">{session.language}</span>
                <ChevronDown size={10} />
              </button>

              {isLangMenuOpen && (
                <>
                  <div className="fixed inset-0 z-30" onClick={() => setIsLangMenuOpen(false)} />
                  <div className="absolute left-0 top-full mt-1 bg-white border border-[#BAE6FD] shadow-lg rounded-xl p-1 z-40 w-28 text-left animate-in fade-in">
                    <button
                      onClick={() => handleSelectLanguage("Tiếng Việt")}
                      className={`w-full text-left px-2 py-1 text-xs rounded-lg transition-colors ${
                        session.language === "Tiếng Việt"
                          ? "bg-[#E0F2FE] text-[#0369A1] font-semibold"
                          : "text-[#475569] hover:bg-[#F0F9FF]"
                      }`}
                    >
                      Tiếng Việt
                    </button>
                    <button
                      onClick={() => handleSelectLanguage("English")}
                      className={`w-full text-left px-2 py-1 text-xs rounded-lg transition-colors ${
                        session.language === "English"
                          ? "bg-[#E0F2FE] text-[#0369A1] font-semibold"
                          : "text-[#475569] hover:bg-[#F0F9FF]"
                      }`}
                    >
                      English
                    </button>
                  </div>
                </>
              )}
            </div>

          </div>
        </div>
      </div>

      {/* Phải: Thao tác ghi âm, thiết bị âm thanh, tạo tài liệu */}
      <div className="flex flex-wrap items-center justify-end gap-1.5 @md:gap-2 ml-auto">
        {/* Nút In / Xuất file */}
        <button
          onClick={() => window.print()}
          className="p-1.5 text-[#64748B] hover:text-[#0284C7] hover:bg-[#E0F2FE] rounded-lg transition-colors hidden @4xl:flex"
          title="In bệnh án hoặc Lưu tệp PDF (Ctrl+P)"
        >
          <Printer size={15} />
        </button>

        {/* Nút + Tạo tài liệu */}
        <button
          onClick={onCreateNewDocument}
          className="flex items-center gap-1 px-2.5 sm:px-3 py-1.5 rounded-xl bg-[#0284C7] text-white text-xs font-semibold hover:bg-[#0369A1] active:translate-y-0.5 transition-all shadow-tactile-doctor whitespace-nowrap flex-shrink-0"
          title="Tạo thêm mẫu bệnh án hoặc văn bản"
        >
          <Plus size={14} className="stroke-[2.5]" />
          <span className="hidden @2xl:inline">Tạo mẫu</span>
        </button>

        {/* Điều khiển Ghi âm: Tiếp tục / Tạm dừng */}
        <div className="flex items-center gap-1 sm:gap-1.5 flex-shrink-0">
          {isRecording && (
            <button
              onClick={handleFinishAndAnalyze}
              className="flex items-center gap-1 px-2 sm:px-2.5 py-1.5 rounded-xl bg-[#0284C7] hover:bg-[#0369A1] text-white text-xs font-semibold shadow-[0_3px_12px_rgba(2,132,199,0.35)] transition-all animate-pulse whitespace-nowrap flex-shrink-0"
              title="Dừng ghi âm và mở bảng phân tích AI tự động"
            >
              <Sparkles size={12} className="text-amber-200" />
              <span className="hidden @2xl:inline">Phân tích AI</span>
            </button>
          )}

          <div className="flex items-center bg-white border border-[#DDD7CE] rounded-xl overflow-hidden shadow-[0_2px_8px_rgba(43,27,34,0.07),0_1px_2px_rgba(0,0,0,0.04)] ring-1 ring-black/5 flex-shrink-0">
            <button
              onClick={toggleRecording}
              className={`flex items-center gap-1 sm:gap-1.5 px-2.5 sm:px-3 py-1.5 text-xs font-medium transition-colors whitespace-nowrap ${
                isRecording
                  ? "bg-red-50 text-red-700 font-semibold"
                  : "text-[#2C2420] hover:bg-[#F7F6F2]"
              }`}
            >
              {isRecording ? (
                <>
                  <span className="w-1.5 h-1.5 rounded-full bg-red-600 animate-ping" />
                  <Pause size={13} />
                  <span className="hidden @2xl:inline">Dừng ghi âm</span>
                  <span className="inline @2xl:hidden">Dừng</span>
                </>
              ) : (
                <>
                  <Play size={12} className="fill-current text-[#2B1B22]" />
                  <span className="hidden @2xl:inline">Tiếp tục ghi âm</span>
                  <span className="inline @2xl:hidden">Ghi âm</span>
                </>
              )}
            </button>
            <button
              onClick={toggleRecording}
              className="px-1.5 sm:px-2 py-1.5 border-l border-[#DDD7CE] text-[#7C756F] hover:bg-[#F7F6F2]"
              title="Tùy chọn ghi âm"
            >
              <ChevronDown size={11} />
            </button>
          </div>
        </div>

        {/* Đồng hồ bấm giờ ca khám */}
        <div className="flex items-center gap-1 text-[11px] sm:text-xs font-mono text-[#4A423D] px-2 py-1 bg-white border border-[#DDD7CE] rounded-xl shadow-[0_2px_6px_rgba(0,0,0,0.04)] flex-shrink-0">
          <Clock size={12} className="text-[#8C837C]" />
          <span>{formatTimer(duration)}</span>
        </div>

        {/* Micrô & Thước đo tín hiệu âm thanh — cột hẹp thì ẩn, ghi âm dùng micrô mặc định */}
        <div className="relative flex-shrink-0 hidden @xl:block">
          <button
            onClick={() =>
              setAudioDropdownMode(audioDropdownMode === "mic" ? null : "mic")
            }
            className="flex items-center gap-1 px-2 py-1.5 bg-white border border-[#DDD7CE] rounded-xl text-xs text-[#2C2420] hover:bg-[#F9F8F5] shadow-[0_2px_6px_rgba(0,0,0,0.04)] ring-1 ring-black/5"
            title={`Micrô: ${selectedMic}`}
          >
            <Mic size={13} className={isRecording ? "text-red-600 animate-pulse" : "text-[#6D655E]"} />
            {/* Vạch sóng âm thực tế */}
            <div className="flex items-center gap-0.5 h-3">
              {[0, 1, 2, 3, 4].map((idx) => {
                const heightVal = isRecording
                  ? Math.max(3, Math.min(12, Math.round((audioFreqs[idx * 6] || 0) / 8)))
                  : 4;
                return (
                  <span
                    key={idx}
                    style={{ height: `${heightVal}px` }}
                    className={`w-0.5 sm:w-1 rounded-2xs transition-all duration-75 ${
                      isRecording
                        ? audioFreqs[idx * 6] > 30
                          ? "bg-emerald-500"
                          : "bg-emerald-400"
                        : "bg-gray-300"
                    }`}
                  />
                );
              })}
            </div>
            <ChevronDown size={10} className="text-[#8C837C]" />
          </button>

          <AudioDeviceDropdown
            isOpen={audioDropdownMode === "mic"}
            onClose={() => setAudioDropdownMode(null)}
            selectedSpeaker={selectedSpeaker}
            onSelectSpeaker={setSelectedSpeaker}
            selectedMic={selectedMic}
            onSelectMic={(mic) => {
              setSelectedMic(mic);
              // Restart mic with new device if recording
              if (isRecording) {
                toggleRecording();
              }
            }}
            mode="mic"
          />
        </div>

        {/* Loa phát - chỉ hiện trên màn hình rất rộng */}
        <div className="relative hidden @5xl:flex flex-shrink-0">
          <button
            onClick={() =>
              setAudioDropdownMode(audioDropdownMode === "speaker" ? null : "speaker")
            }
            className="flex items-center gap-1 px-2.5 py-1.5 bg-white border border-[#DDD7CE] rounded-xl text-xs text-[#2C2420] hover:bg-[#F9F8F5] shadow-[0_2px_6px_rgba(0,0,0,0.04)] ring-1 ring-black/5"
            title={selectedSpeaker}
          >
            <Volume2 size={13} className="text-[#6D655E]" />
            <span className="max-w-[60px] truncate text-[11px]">Loa ngoài</span>
            <ChevronDown size={11} className="text-[#8C837C]" />
          </button>

          <AudioDeviceDropdown
            isOpen={audioDropdownMode === "speaker"}
            onClose={() => setAudioDropdownMode(null)}
            selectedSpeaker={selectedSpeaker}
            onSelectSpeaker={setSelectedSpeaker}
            selectedMic={selectedMic}
            onSelectMic={setSelectedMic}
            mode="speaker"
          />
        </div>

        {/* Nút bật/tắt bảng Hỏi đáp & Chứng cứ lâm sàng bên phải */}
        <button
          onClick={onToggleRightDrawer}
          className={`p-1.5 rounded-xl border transition-all flex-shrink-0 shadow-[0_2px_6px_rgba(2,132,199,0.08)] active:translate-y-0.5 ${
            isRightDrawerOpen
              ? "bg-[#0284C7] text-white border-[#0284C7] shadow-[0_3px_10px_rgba(2,132,199,0.3)]"
              : "bg-white text-[#475569] border-[#CCE3F0] hover:bg-[#E0F2FE] hover:text-[#0369A1]"
          }`}
          title={isRightDrawerOpen ? "Đóng bảng Chứng cứ Y khoa" : "Mở bảng Chứng cứ Y khoa & Gợi ý câu hỏi"}
        >
          <PanelRight size={15} />
        </button>
      </div>
    </header>

    {isRecording && (
      <ThanhAmThanh cacVach={audioFreqs} amLuong={amLuong} imLang={imLang} thoiGian={formatTimer(duration)} />
    )}

    {dangChep && (
      <div className="bg-[#F0F9FF] border-b border-[#BAE6FD] px-4 py-2 text-xs text-[#0369A1] z-20">
        Đang chép đoạn ghi âm bằng PhoWhisper chạy tại chỗ… (lần đầu phải nạp mô hình, mất khoảng 10–30 giây)
      </div>
    )}

    {micError && (
      <div className="bg-amber-50 border-b border-amber-200 px-4 py-2 flex items-center justify-between text-xs text-amber-900 animate-in fade-in z-20">
        <div className="flex items-center gap-2">
          <AlertCircle size={15} className="text-amber-600 flex-shrink-0" />
          <span>{micError}</span>
        </div>
        <button
          onClick={() => setMicError(null)}
          className="text-amber-800 hover:text-amber-950 font-semibold px-2 py-0.5 rounded hover:bg-amber-100"
        >
          Đóng
        </button>
      </div>
    )}
  </>
  );
};
