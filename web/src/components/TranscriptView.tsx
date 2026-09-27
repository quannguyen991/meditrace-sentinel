import React, { useState, useRef, useEffect } from "react";
import {
  Copy,
  Trash2,
  ThumbsUp,
  ThumbsDown,
  Check,
  Mic,
  Upload,
  Play,
  Activity,
  User,
  Sparkles,
  Loader2,
  FileAudio,
  Download,
  Edit3,
  ChevronDown,
} from "lucide-react";
import { motion } from "motion/react";
import { realAudioService } from "../services/realAudioService";
import { cacNguoiNoiChuaGan, dongTuDoan, ganVaiNguoiNoi, moTaTach, soNguoiNoiLonNhat } from "../lib/nguoiNoi";

interface TranscriptViewProps {
  transcript: string;
  onUpdateTranscript: (newText: string) => void;
  isRecording?: boolean;
  onStartRecording?: () => void;
  onOpenTemplates?: () => void;
  /** Nạp một ca đã chạy trước từ dịch vụ tại chỗ (dùng khi GPU đang bận). */
  onLoadSample?: () => void;
  audioUrl?: string;
}

const VAI_RE = /^\s*(bác sĩ|bệnh nhân|người nhà|chưa rõ vai|người nói\s+\d+|doctor|patient|bs|bn|speaker_\d+)\s*:/i;
const THU_TU_VAI = ["Bác sĩ", "Bệnh nhân", "Người nhà", "Chưa rõ vai"];
const VAI_GAN = ["Bác sĩ", "Bệnh nhân", "Người nhà"];
const KIEU_VAI: Record<string, { tat: string; mau: string }> = {
  "Bác sĩ": { tat: "BS", mau: "bg-[#E0F2FE] text-[#0369A1] border-[#BAE6FD]" },
  "Bệnh nhân": { tat: "BN", mau: "bg-[#F0FDF4] text-[#15803D] border-[#BBF7D0]" },
  "Người nhà": { tat: "NN", mau: "bg-[#F5F3FF] text-[#6D28D9] border-[#DDD6FE]" },
  "Chưa rõ vai": { tat: "?", mau: "bg-[#FEF6E0] text-[#A16207] border-[#F2DFA8]" },
};
/** "Người nói N" (máy tách theo giọng, chưa gán vai): cùng màu chờ với "Chưa rõ vai". */
function kieuVai(vai: string) {
  const m = vai.match(/^Người nói (\d+)$/);
  if (m) return { tat: `Nói ${m[1]}`, mau: KIEU_VAI["Chưa rõ vai"].mau };
  return KIEU_VAI[vai] || KIEU_VAI["Chưa rõ vai"];
}
function chuanVai(x: string) {
  const t = x.trim().toLowerCase();
  if (t === "bác sĩ" || t === "doctor" || t === "bs") return "Bác sĩ";
  if (t === "bệnh nhân" || t === "patient" || t === "bn") return "Bệnh nhân";
  if (t === "người nhà") return "Người nhà";
  const n = t.match(/^người nói\s+(\d+)$/);
  if (n) return `Người nói ${Number(n[1])}`;
  return "Chưa rõ vai";
}

export const TranscriptView: React.FC<TranscriptViewProps> = ({
  transcript,
  onUpdateTranscript,
  isRecording = false,
  onStartRecording,
  onOpenTemplates,
  onLoadSample,
  audioUrl,
}) => {
  const [copied, setCopied] = useState(false);
  const [liked, setLiked] = useState<boolean | null>(null);
  const [isEditing, setIsEditing] = useState(false);

  /** Đổi vai của một lượt: sửa đúng tiền tố "Vai:" của dòng đó trong lời thoại. */
  const doiVai = (idx: number) => {
    const lines = transcript.split("\n").filter((l) => l.trim().length > 0);
    const m = lines[idx].match(VAI_RE);
    const cu = m ? chuanVai(m[1]) : "Chưa rõ vai";
    const moi = THU_TU_VAI[(THU_TU_VAI.indexOf(cu) + 1) % THU_TU_VAI.length];
    const noiDung = m ? lines[idx].slice(m[0].length).trim() : lines[idx].trim();
    lines[idx] = `${moi}: ${noiDung}`;
    onUpdateTranscript(lines.join("\n"));
  };
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  /** Câu báo về tách người nói của lần chép gần nhất (đã tách mấy người, hay vì sao chưa). */
  const [ghiChuTach, setGhiChuTach] = useState<string | null>(null);
  const nguoiNoiChuaGan = cacNguoiNoiChuaGan(transcript);
  const [interimText, setInterimText] = useState<string>("");
  const [liveVolume, setLiveVolume] = useState<number>(0);
  const [liveFreqs, setLiveFreqs] = useState<number[]>([0, 0, 0, 0, 0, 0, 0, 0]);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Subscribe to real audio service updates for live interim transcription and visualizer
  useEffect(() => {
    if (isRecording) {
      realAudioService.setCallbacks({
        onTranscriptChunk: (chunk: string, isFinal: boolean) => {
          if (!isFinal) {
            setInterimText(chunk);
          } else {
            setInterimText("");
          }
        },
        onAudioLevel: (volume: number, frequencies: number[]) => {
          setLiveVolume(volume);
          setLiveFreqs(frequencies);
        },
      });
    } else {
      setInterimText("");
      setLiveVolume(0);
      setLiveFreqs([0, 0, 0, 0, 0, 0, 0, 0]);
    }
  }, [isRecording]);

  const handleCopy = () => {
    navigator.clipboard.writeText(transcript);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleClear = () => {
    if (window.confirm("Bạn có chắc chắn muốn xóa toàn bộ bản ghi lời thoại này không?")) {
      onUpdateTranscript("");
      setInterimText("");
    }
  };

  // Upload tệp âm thanh thực tế và chuyển thể bằng Gemini AI
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Reset input
    e.target.value = "";
    setIsUploading(true);
    setUploadError(null);

    try {
      const reader = new FileReader();
      const base64Promise = new Promise<string>((resolve, reject) => {
        reader.onload = () => {
          const res = reader.result as string;
          const base64Data = res.split(",")[1];
          resolve(base64Data);
        };
        reader.onerror = reject;
      });

      reader.readAsDataURL(file);
      const audioBase64 = await base64Promise;

      const response = await fetch("/api/transcribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          audioBase64,
          mimeType: file.type || "audio/mp3",
          fileName: file.name,
          language: "vi",
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Không thể chuyển thể file âm thanh này");
      }

      const data = await response.json();
      const doan: any[] = data.segments || [];
      if (!doan.length) throw new Error("PhoWhisper không nghe ra câu nào trong tệp này.");
      // Mỗi lượt một dòng. Máy đã tách người nói thì dòng mang nhãn "Người nói N", chưa tách thì
      // "Chưa rõ vai" — vai Bác sĩ / Bệnh nhân / Người nhà luôn do người dùng gán.
      // Không chèn dòng tiêu đề: dòng nào trong lời thoại cũng bị tính là một lượt nói.
      const moi = dongTuDoan(doan, data.diarization, soNguoiNoiLonNhat(transcript)).join("\n");
      onUpdateTranscript(transcript ? `${transcript.trimEnd()}\n${moi}` : moi);
      setGhiChuTach(moTaTach(data.diarization));
    } catch (err: any) {
      console.error(err);
      setUploadError(err.message || "Lỗi khi xử lý tệp âm thanh");
    } finally {
      setIsUploading(false);
    }
  };

  // Trạng thái Chưa ghi nhận cuộc hội thoại (Empty State tinh gọn - ít chữ)
  if (!transcript || transcript.trim().length === 0) {
    return (
      <motion.div
        id="transcript-empty-state"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.25 }}
        className="flex-1 overflow-y-auto p-6 bg-gradient-to-b from-[#F0F7FA] via-[#F8FBFC] to-[#EEF6FB] flex flex-col items-center justify-center text-center select-none"
      >
        <div className="max-w-xs w-full flex flex-col items-center">
          <div className="w-14 h-14 rounded-2xl bg-white border border-[#BAE6FD] flex items-center justify-center text-[#0284C7] mb-3.5 shadow-tactile-doctor-pill">
            <Mic size={24} className="text-[#0284C7]" />
          </div>

          <h2 className="font-serif text-base font-semibold text-[#0F172A] mb-4">
            Chưa có bản ghi âm
          </h2>

          {/* Nút hành động tinh gọn với hiệu ứng nổi khối */}
          <div className="w-full flex flex-col gap-2.5">
            {onStartRecording && (
              <button
                onClick={onStartRecording}
                className="w-full py-2.5 px-4 rounded-xl bg-[#0284C7] text-white hover:bg-[#0369A1] active:translate-y-0.5 transition-all flex items-center justify-center gap-2 text-xs font-semibold shadow-tactile-doctor"
              >
                <Play size={13} className="fill-current text-white" />
                <span>Bắt đầu ghi âm</span>
              </button>
            )}

            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              accept="audio/*,.mp3,.wav,.m4a,.webm,.ogg"
              className="hidden"
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={isUploading}
              className="w-full py-2.5 px-4 rounded-xl bg-white border border-[#BAE6FD] hover:border-[#0284C7] hover:bg-[#F0F9FF] transition-all flex items-center justify-center gap-2 text-xs font-medium text-[#0C4A6E] shadow-tactile-doctor-card"
            >
              {isUploading ? (
                <Loader2 size={13} className="animate-spin text-[#0284C7]" />
              ) : (
                <Upload size={13} className="text-[#0284C7]" />
              )}
              <span>{isUploading ? "Đang xử lý..." : "Tải tệp âm thanh"}</span>
            </button>
          </div>

          {uploadError && (
            <div className="mt-3 p-2 bg-red-50 border border-red-200 rounded-lg text-red-700 text-xs">
              {uploadError}
            </div>
          )}

          {/* Ca đã chạy trước — lấy từ dịch vụ tại chỗ, có nhãn nguồn rõ ràng */}
          {onLoadSample && (
            <div className="mt-6 flex items-center gap-2 text-[11px] text-[#64748B]">
              <button
                onClick={() => onLoadSample()}
                className="hover:text-[#0284C7] hover:underline font-medium"
              >
                Nạp một ca đã chạy trước
              </button>
              <span className="text-[#94A3B8]">(dữ liệu tổng hợp của dự án, không phải người bệnh thật)</span>
            </div>
          )}
        </div>
      </motion.div>
    );
  }

  return (
    <div
      id="transcript-view-container"
      className="flex-1 overflow-y-auto p-6 bg-gradient-to-b from-[#F8FBFC] via-[#F0F7FA] to-[#EEF6FB] relative flex flex-col justify-between select-none"
    >
      <div>
        {/* Thao tác nhanh phía trên */}
        <div className="flex items-center justify-between mb-4 border-b border-[#CCE3F0] pb-2">
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-[#0F172A]">
              Biên bản hội thoại khám bệnh
            </span>
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#E0F2FE] text-[#0369A1] font-medium border border-[#BAE6FD]">
              Chuyển giọng nói sang chữ (STT Thực tế)
            </span>
            {isRecording && (
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-red-100 text-red-700 font-semibold animate-pulse flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-red-600" />
                Đang lắng nghe
              </span>
            )}
          </div>

          <div className="flex items-center gap-2">
            {/* Tải tệp âm thanh bổ sung */}
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              accept="audio/*,.mp3,.wav,.m4a,.webm,.ogg"
              className="hidden"
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={isUploading}
              className="text-xs px-2.5 py-1 rounded-lg bg-[#E0F2FE] text-[#0369A1] hover:bg-[#BAE6FD] transition-colors flex items-center gap-1.5 font-medium disabled:opacity-50"
              title="Tải thêm tệp ghi âm âm thanh (.mp3, .wav)"
            >
              {isUploading ? (
                <Loader2 size={12} className="animate-spin text-[#0284C7]" />
              ) : (
                <Upload size={12} />
              )}
              <span>{isUploading ? "Đang giải mã..." : "Tải tệp âm thanh"}</span>
            </button>

            {/* Bật tắt chế độ sửa tay */}
            <button
              onClick={() => setIsEditing(!isEditing)}
              className={`text-xs px-2.5 py-1 rounded-lg border transition-colors flex items-center gap-1 font-medium ${
                isEditing
                  ? "bg-[#0284C7] text-white border-[#0284C7] shadow-tactile-doctor"
                  : "border-[#CCE3F0] text-[#0C4A6E] hover:bg-[#E0F2FE]"
              }`}
              title="Chỉnh sửa văn bản trực tiếp"
            >
              <Edit3 size={12} />
              <span>{isEditing ? "Xong" : "Sửa tay"}</span>
            </button>

            {/* Sao chép */}
            <button
              onClick={handleCopy}
              className="flex items-center gap-1 text-xs px-2.5 py-1 rounded-lg border border-[#CCE3F0] text-[#0C4A6E] hover:bg-[#E0F2FE] transition-colors shadow-2xs"
            >
              {copied ? (
                <>
                  <Check size={12} className="text-emerald-600" />
                  <span className="text-emerald-700 font-medium">Đã sao chép</span>
                </>
              ) : (
                <>
                  <Copy size={12} />
                  <span>Sao chép</span>
                </>
              )}
            </button>

            {/* Xóa */}
            <button
              onClick={handleClear}
              className="p-1 rounded-lg text-[#94A3B8] hover:text-red-600 hover:bg-red-50 transition-colors"
              title="Xóa toàn bộ lời thoại"
            >
              <Trash2 size={14} />
            </button>
          </div>
        </div>

        {uploadError && (
          <div className="mb-3 p-2.5 bg-red-50 border border-red-200 rounded-xl text-red-700 text-xs">
            {uploadError}
          </div>
        )}

        {ghiChuTach && !nguoiNoiChuaGan.length && (
          <div className="mb-3 p-2.5 bg-[#F0F9FF] border border-[#BAE6FD] rounded-xl text-[#0C4A6E] text-xs">
            {ghiChuTach}
          </div>
        )}

        {/* Gán vai theo người nói: máy tách theo giọng, người dùng chọn ai là bác sĩ. */}
        {!isEditing && nguoiNoiChuaGan.length > 0 && (
          <section
            aria-label="Gán vai theo người nói"
            className="max-w-4xl mb-4 p-3.5 rounded-2xl bg-[#FFFBEB] border border-[#F2DFA8] text-xs text-[#713F12]"
          >
            <div className="font-semibold text-[13px] text-[#0F172A] mb-1">Gán vai theo người nói</div>
            <p className="mb-3 leading-relaxed">
              {ghiChuTach ||
                "Máy đã tách người nói theo giọng, nhưng không biết ai là bác sĩ: chọn vai cho từng người nói, rồi đọc lại từng dòng."}{" "}
              Máy tách có thể nhầm khi hai người nói chen nhau; dòng nào sai vai thì bấm nhãn tròn của dòng đó để sửa.
            </p>
            <div className="flex flex-col gap-2">
              {nguoiNoiChuaGan.map((nn) => (
                <div
                  key={nn.so}
                  className="flex flex-wrap items-center gap-x-3 gap-y-1.5 bg-white rounded-xl border border-[#F2DFA8] px-3 py-2"
                >
                  <div className="min-w-0 flex-1">
                    <span className="font-semibold text-[#0F172A]">{nn.nhan}</span>
                    <span className="text-[#64748B]"> · {nn.soLuot} lượt · câu đầu: </span>
                    <span className="text-[#334155] italic break-words">“{nn.viDu}”</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    {VAI_GAN.map((vai) => (
                      <button
                        key={vai}
                        onClick={() => onUpdateTranscript(ganVaiNguoiNoi(transcript, nn.so, vai))}
                        className={`px-2.5 py-1 rounded-lg border font-semibold text-[11px] hover:brightness-95 focus-visible:outline focus-visible:outline-2 focus-visible:outline-[#0284C7] ${KIEU_VAI[vai].mau}`}
                        title={`Gán vai ${vai} cho mọi lượt của ${nn.nhan}`}
                      >
                        {vai}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Trình phát âm thanh thực tế nếu đã có bản ghi âm */}
        {audioUrl && (
          <div className="mb-4 p-3 rounded-2xl bg-[#F0F9FF] border border-[#BAE6FD] shadow-[0_2px_8px_rgba(2,132,199,0.05)] flex items-center justify-between gap-4">
            <div className="flex items-center gap-2 text-xs font-medium text-[#0F172A]">
              <FileAudio size={16} className="text-[#0284C7]" />
              <span>Tệp âm thanh ca khám đã ghi nhận:</span>
            </div>
            <div className="flex items-center gap-3">
              <audio src={audioUrl} controls className="h-8 max-w-xs" />
              <a
                href={audioUrl}
                download="meditrace-consultation.webm"
                className="p-1.5 rounded-lg border border-[#BAE6FD] text-[#0369A1] hover:bg-white text-xs flex items-center gap-1 shadow-2xs"
                title="Tải file âm thanh về máy tính"
              >
                <Download size={13} />
                <span>Tải về</span>
              </a>
            </div>
          </div>
        )}

        {/* Visualizer sóng âm trực tiếp khi đang ghi âm */}
        {isRecording && (
          <div className="mb-4 p-3 rounded-2xl bg-sky-50 border border-sky-200 text-sky-900 text-xs flex flex-col gap-2 shadow-[0_4px_16px_rgba(2,132,199,0.12)]">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Mic size={14} className="text-[#0284C7] animate-bounce flex-shrink-0" />
                <span className="font-semibold text-[#0369A1]">
                  Đang ghi âm và nhận diện giọng nói thực tế từ Micrô...
                </span>
              </div>
              <span className="text-[11px] text-[#0284C7] font-mono">
                Âm lượng: {liveVolume}%
              </span>
            </div>

            {/* Dynamic frequency equalizer wave */}
            <div className="flex items-center gap-1.5 h-6 px-2 py-1 bg-white/80 rounded-lg shadow-[inset_0_1px_2px_rgba(2,132,199,0.1)]">
              {liveFreqs.map((freq, idx) => (
                <div
                  key={idx}
                  className="flex-1 bg-[#0284C7] rounded-full transition-all duration-75"
                  style={{
                    height: `${Math.max(4, Math.min(22, Math.round((freq / 100) * 22)))}px`,
                  }}
                />
              ))}
            </div>
          </div>
        )}

        {/* Nội dung lời thoại (Chế độ xem hoặc Chế độ sửa tay) với hiệu ứng nổi khối */}
        {isEditing ? (
          <div className="max-w-4xl bg-white rounded-2xl border border-[#E5DFD5] shadow-tactile-card p-4 sm:p-6">
            <textarea
              value={transcript}
              onChange={(e) => onUpdateTranscript(e.target.value)}
              rows={12}
              className="w-full bg-transparent text-sm text-[#2C2420] focus:outline-none leading-relaxed font-sans"
              placeholder="Nhập hoặc chỉnh sửa lời thoại trực tiếp..."
            />
          </div>
        ) : (
          <div className="max-w-4xl flex flex-col gap-3.5">
            {(() => {
              if (!transcript.trim()) {
                return (
                  <div className="bg-white rounded-2xl border border-[#E5DFD5] shadow-tactile-card p-6 text-sm text-[#8C837C] text-center">
                    Chưa có lời thoại. Hãy bấm "Tiếp tục ghi âm" hoặc "Tải lên bản ghi".
                  </div>
                );
              }
              const lines = transcript.split("\n").filter((l) => l.trim().length > 0);
              return lines.map((line, idx) => {
                // Đọc tiền tố vai đúng như người dùng / bản chép ghi. KHÔNG đoán vai khi không
                // có tiền tố (bản cũ xen kẽ BS/BN theo số dòng — đó là bịa).
                const m = line.match(VAI_RE);
                const vai = m ? chuanVai(m[1]) : "Chưa rõ vai";
                const text = m ? line.slice(m[0].length).trim() : line.trim();
                const kieu = kieuVai(vai);
                const daGan = VAI_GAN.includes(vai);
                return (
                  <div key={idx} className="flex items-start gap-3 group">
                    <div className="flex flex-col items-center flex-shrink-0 w-16 pt-1 text-center gap-1">
                      <button
                        onClick={() => doiVai(idx)}
                        title="Bấm để đổi vai: Bác sĩ → Bệnh nhân → Người nhà → Chưa rõ vai"
                        className={`px-1.5 h-7 min-w-[2.25rem] rounded-full flex items-center justify-center font-bold text-[10px] border whitespace-nowrap ${kieu.mau}`}
                      >
                        {kieu.tat}
                      </button>
                      <span className="text-[9px] text-[#64748B] font-mono">lượt {idx + 1}</span>
                    </div>
                    <div className={`flex-1 bg-white rounded-2xl border p-4 flex items-start justify-between gap-3 ${daGan ? "border-[#BAE6FD]" : "border-[#F2DFA8]"}`}>
                      <div className="text-[13px] sm:text-[14px] leading-relaxed text-[#0F172A] font-sans">
                        <span className="text-[11px] font-semibold text-[#64748B] mr-1.5">{vai}:</span>
                        {text}
                      </div>
                    </div>
                  </div>
                );
              });
            })()}

            {/* Interim live speech recognition text */}
            {interimText && (
              <div className="flex items-start gap-3 mt-1">
                <div className="w-12 flex justify-center">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#0284C7] animate-ping mt-3" />
                </div>
                <div className="flex-1 bg-white/90 rounded-2xl border border-[#BAE6FD] p-3 text-xs text-[#0284C7] italic animate-pulse shadow-sm">
                  {interimText}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Đánh giá độ chính xác & Tiêu chuẩn y khoa */}
      <div className="flex items-center justify-between mt-8 pt-4 border-t border-[#F2EEE9] text-xs text-[#8C837C]">
        <div className="flex items-center gap-2">
          <span>Đánh giá chất lượng nhận diện:</span>
          <button
            onClick={() => setLiked(liked === true ? null : true)}
            className={`p-1.5 rounded-lg transition-colors ${
              liked === true
                ? "bg-[#EAE4D9] text-[#2B1B22]"
                : "text-[#9C948D] hover:text-[#2B1B22] hover:bg-[#F7F6F2]"
            }`}
            title="Lời thoại nhận diện chính xác"
          >
            <ThumbsUp size={14} />
          </button>
          <button
            onClick={() => setLiked(liked === false ? null : false)}
            className={`p-1.5 rounded-lg transition-colors ${
              liked === false
                ? "bg-[#EAE4D9] text-[#2B1B22]"
                : "text-[#9C948D] hover:text-[#2B1B22] hover:bg-[#F7F6F2]"
            }`}
            title="Có từ ngữ nhận diện chưa chuẩn"
          >
            <ThumbsDown size={14} />
          </button>
        </div>

        <div className="text-[11px] text-[#9C948D]">
          Chép âm chạy trên máy chủ của dự án. Hệ thống chưa được đánh giá theo chuẩn bảo mật dữ liệu y tế nào.
        </div>
      </div>
    </div>
  );
};
