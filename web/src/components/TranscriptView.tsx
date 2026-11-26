import React, { useState, useRef, useEffect, useMemo, useCallback } from "react";
import {
  Copy,
  Trash2,
  ThumbsUp,
  ThumbsDown,
  Check,
  Mic,
  Upload,
  Play,
  Sparkles,
  Loader2,
  FileAudio,
  Download,
  Edit3,
  AlertTriangle,
  Fingerprint,
  Volume2,
  Square,
} from "lucide-react";
import { motion } from "motion/react";
import { realAudioService } from "../services/realAudioService";
import {
  apDungVaiGoiY,
  cacNguoiNoiChuaGan,
  dongTuDoan,
  ganVaiNguoiNoi,
  goiYVaiTuDoan,
  goiYVaiTuVanBanLuot,
  moTaTach,
  soNguoiNoiLonNhat,
  type VaiChuan,
} from "../lib/nguoiNoi";
import { quetRadarCoDo } from "../lib/radarCoDo";

const KHOA_MAU_GIONG_BS = "meditrace_doctor_voiceprint_v1";

interface MauGiongBacSiCucBo {
  version: 1;
  enrolledAt: string;
  f0Hz: number;
  spectralBands: number[];
  sampleSeconds: number;
}

function docMauGiongCucBo(): MauGiongBacSiCucBo | null {
  try {
    const raw = localStorage.getItem(KHOA_MAU_GIONG_BS);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (parsed && parsed.version === 1 && typeof parsed.f0Hz === "number") {
      return parsed as MauGiongBacSiCucBo;
    }
  } catch {}
  return null;
}

/** Ước lượng tần số cơ bản F0 (Hz) bằng tự tương quan miền thời gian ngay trong RAM trình duyệt. */
function uocLuongPitchTuKhung(buf: Float32Array, sampleRate: number): number | null {
  let rms = 0;
  for (let i = 0; i < buf.length; i++) rms += buf[i] * buf[i];
  rms = Math.sqrt(rms / buf.length);
  if (rms < 0.012) return null;

  const minLag = Math.floor(sampleRate / 340);
  const maxLag = Math.min(buf.length - 1, Math.floor(sampleRate / 75));
  let bestLag = -1;
  let bestCorr = 0;

  for (let lag = minLag; lag <= maxLag; lag++) {
    let corr = 0;
    for (let i = 0; i < buf.length - lag; i++) {
      corr += buf[i] * buf[i + lag];
    }
    corr /= buf.length - lag;
    if (corr > bestCorr) {
      bestCorr = corr;
      bestLag = lag;
    }
  }

  if (bestLag <= 0 || bestCorr < 0.0002) return null;
  const hz = sampleRate / bestLag;
  return hz >= 75 && hz <= 340 ? hz : null;
}

interface TranscriptViewProps {
  transcript: string;
  gioiTinh?: string;
  onUpdateTranscript: (newText: string) => void;
  onUpdateSegments?: (newSegments: import("../types").TranscriptSegment[]) => void;
  isRecording?: boolean;
  onStartRecording?: () => void;
  onOpenTemplates?: () => void;
  /** Nạp một ca đã chạy trước từ dịch vụ tại chỗ (dùng khi GPU đang bận). */
  onLoadSample?: () => void;
  audioUrl?: string;
  /** Tệp âm thanh vừa tải lên: giữ lại để nghe lại từng lượt / từng mệnh đề. */
  onDatAmThanh?: (url: string) => void;
}

const VAI_RE = /^\s*(bác sĩ|bệnh nhân|người nhà|chưa rõ vai|người nói\s+\d+|doctor|patient|bs|bn|speaker_\d+)\s*:/i;
const THU_TU_VAI = ["Bác sĩ", "Bệnh nhân", "Người nhà", "Chưa rõ vai"];
const VAI_GAN: VaiChuan[] = ["Bác sĩ", "Bệnh nhân", "Người nhà"];
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
  gioiTinh,
  onUpdateTranscript,
  onUpdateSegments,
  isRecording = false,
  onStartRecording,
  onOpenTemplates,
  onLoadSample,
  audioUrl,
  onDatAmThanh,
}) => {
  const [copied, setCopied] = useState(false);
  const [liked, setLiked] = useState<boolean | null>(null);
  const [isEditing, setIsEditing] = useState(false);

  /** Gợi ý vai từ `/api/transcribe` (ưu tiên) kết hợp heuristic tại chỗ (Boost 1). */
  const [suggestedRolesByTurn, setSuggestedRolesByTurn] = useState<
    Record<number, { vai: VaiChuan; lyDo?: string | null }>
  >({});
  const [thongBaoDaGanNhanh, setThongBaoDaGanNhanh] = useState<string | null>(null);
  const [activeTurnIdx, setActiveTurnIdx] = useState<number | null>(null);

  // Đọc to một lượt bằng giọng tiếng Việt có sẵn trong trình duyệt (chạy tại chỗ, không gửi dữ liệu đi),
  // dùng cho ca chỉ có chữ như ca mẫu. Bác sĩ một giọng, bệnh nhân / người nhà giọng khác nếu máy có.
  const [dangDocLuot, setDangDocLuot] = useState<number | null>(null);
  const docLuot = (idx: number, noiDung: string, vai: string) => {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) return;
    const tts = window.speechSynthesis;
    tts.cancel();
    if (dangDocLuot === idx) {
      setDangDocLuot(null);
      return;
    }
    const giongVi = tts.getVoices().filter((v) => v.lang.toLowerCase().startsWith("vi"));
    const tot = [...giongVi].sort(
      (a, b) => Number(/natural|online|neural/i.test(b.name)) - Number(/natural|online|neural/i.test(a.name)),
    );
    const laBacSi = vai === "Bác sĩ";
    const giong =
      tot.find((v) => (laBacSi ? /nam ?minh|male|nam\b/i : /hoai ?my|female|an\b/i).test(v.name)) || tot[laBacSi ? 0 : Math.min(1, tot.length - 1)];
    const u = new SpeechSynthesisUtterance(noiDung);
    u.lang = "vi-VN";
    if (giong) u.voice = giong;
    u.rate = 1.3;
    u.onend = () => setDangDocLuot((c) => (c === idx ? null : c));
    u.onerror = () => setDangDocLuot((c) => (c === idx ? null : c));
    setDangDocLuot(idx);
    tts.speak(u);
  };
  useEffect(() => () => window.speechSynthesis?.cancel(), []);

  /** Mẫu giọng Bác sĩ lưu 100% cục bộ trong localStorage (`meditrace_doctor_voiceprint_v1`). */
  const [mauGiongBs, setMauGiongBs] = useState<MauGiongBacSiCucBo | null>(() => docMauGiongCucBo());
  const [dangThuMauGiong, setDangThuMauGiong] = useState(false);
  const [demNguocMauGiong, setDemNguocMauGiong] = useState(0);
  const [loiMauGiong, setLoiMauGiong] = useState<string | null>(null);
  const huyThuMauRef = useRef<(() => void) | null>(null);

  useEffect(() => {
    return () => {
      huyThuMauRef.current?.();
    };
  }, []);

  /** Thu mẫu giọng bác sĩ trong 5 giây bằng Web Audio API cục bộ (0 byte gửi ra ngoài). */
  const thuMauGiongBacSi5Giay = async () => {
    if (dangThuMauGiong) {
      huyThuMauRef.current?.();
      return;
    }
    setLoiMauGiong(null);
    if (!navigator.mediaDevices?.getUserMedia) {
      setLoiMauGiong("Trình duyệt không hỗ trợ truy cập micrô cục bộ.");
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      const ctx: AudioContext = new AudioCtx();
      const source = ctx.createMediaStreamSource(stream);
      const analyser = ctx.createAnalyser();
      analyser.fftSize = 2048;
      source.connect(analyser);

      const timeBuf = new Float32Array(analyser.fftSize);
      const freqBuf = new Uint8Array(analyser.frequencyBinCount);
      const dsPitch: number[] = [];
      const tongBands = new Array(8).fill(0);
      let soKhung = 0;

      setDangThuMauGiong(true);
      setDemNguocMauGiong(5);

      const sampleTimer = window.setInterval(() => {
        analyser.getFloatTimeDomainData(timeBuf);
        const f0 = uocLuongPitchTuKhung(timeBuf, ctx.sampleRate);
        if (f0 !== null) dsPitch.push(f0);

        analyser.getByteFrequencyData(freqBuf);
        const kichThuocNhom = Math.max(1, Math.floor(freqBuf.length / 8));
        for (let b = 0; b < 8; b++) {
          let sum = 0;
          for (let j = 0; j < kichThuocNhom; j++) {
            sum += freqBuf[b * kichThuocNhom + j] || 0;
          }
          tongBands[b] += sum / kichThuocNhom;
        }
        soKhung += 1;
      }, 120);

      const countdownTimer = window.setInterval(() => {
        setDemNguocMauGiong((c) => Math.max(0, c - 1));
      }, 1000);

      const donDep = () => {
        window.clearInterval(sampleTimer);
        window.clearInterval(countdownTimer);
        stream.getTracks().forEach((t) => t.stop());
        ctx.close().catch(() => {});
        setDangThuMauGiong(false);
        setDemNguocMauGiong(0);
        huyThuMauRef.current = null;
      };

      const finishTimeout = window.setTimeout(() => {
        donDep();
        const trungViF0 =
          dsPitch.length > 0
            ? Math.round([...dsPitch].sort((a, b) => a - b)[Math.floor(dsPitch.length / 2)])
            : 145;
        const spectralBands = tongBands.map((v) => Math.round((v / Math.max(1, soKhung)) * 10) / 10);
        const hoSoMoi: MauGiongBacSiCucBo = {
          version: 1,
          enrolledAt: new Date().toISOString(),
          f0Hz: trungViF0,
          spectralBands,
          sampleSeconds: 5,
        };
        try {
          localStorage.setItem(KHOA_MAU_GIONG_BS, JSON.stringify(hoSoMoi));
        } catch {}
        setMauGiongBs(hoSoMoi);
      }, 5000);

      huyThuMauRef.current = () => {
        window.clearTimeout(finishTimeout);
        donDep();
      };
    } catch (err: any) {
      setDangThuMauGiong(false);
      setLoiMauGiong(err?.message || "Không mở được micrô để lấy mẫu giọng tại máy.");
    }
  };

  /** Gán trực tiếp một vai cụ thể cho một lượt `idx` (0-based trên các dòng không rỗng). */
  const ganVaiMotDong = useCallback(
    (idx: number, vaiMoi: string) => {
      let dem = -1;
      const cacDong = transcript.split("\n").map((dong) => {
        if (!dong.trim()) return dong;
        dem += 1;
        if (dem !== idx) return dong;
        const m = dong.match(VAI_RE);
        const noiDung = m ? dong.slice(m[0].length).trim() : dong.trim();
        return `${vaiMoi}: ${noiDung}`;
      });
      onUpdateTranscript(cacDong.join("\n"));
    },
    [transcript, onUpdateTranscript]
  );

  /** Đổi vai vòng tròn của một lượt: Bác sĩ → Bệnh nhân → Người nhà → Chưa rõ vai. */
  const doiVai = (idx: number) => {
    const lines = transcript.split("\n").filter((l) => l.trim().length > 0);
    if (!lines[idx]) return;
    const m = lines[idx].match(VAI_RE);
    const cu = m ? chuanVai(m[1]) : "Chưa rõ vai";
    const moi = THU_TU_VAI[(THU_TU_VAI.indexOf(cu) + 1) % THU_TU_VAI.length];
    ganVaiMotDong(idx, moi);
  };

  // Phím tắt 1 (Bác sĩ) / 2 (Bệnh nhân) / 3 (Người nhà) khi trỏ chuột hoặc focus vào một thẻ lượt thoại
  useEffect(() => {
    if (isEditing || activeTurnIdx === null) return;
    const xuLyPhim = (e: KeyboardEvent) => {
      if (e.altKey || e.ctrlKey || e.metaKey) return;
      const el = document.activeElement as HTMLElement | null;
      const tag = el?.tagName?.toUpperCase();
      if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT" || el?.isContentEditable) return;

      if (e.key === "1") {
        e.preventDefault();
        ganVaiMotDong(activeTurnIdx, "Bác sĩ");
      } else if (e.key === "2") {
        e.preventDefault();
        ganVaiMotDong(activeTurnIdx, "Bệnh nhân");
      } else if (e.key === "3") {
        e.preventDefault();
        ganVaiMotDong(activeTurnIdx, "Người nhà");
      }
    };
    window.addEventListener("keydown", xuLyPhim);
    return () => window.removeEventListener("keydown", xuLyPhim);
  }, [activeTurnIdx, isEditing, ganVaiMotDong]);

  // Tổng hợp gợi ý vai khả dụng trên các dòng đang Chưa rõ vai / Người nói N
  const thongKeGoiY = useMemo(() => {
    const lines = (transcript || "").split("\n").filter((l) => l.trim().length > 0);
    const mapTheoLuot: Record<number, VaiChuan> = {};
    const lyDoTheoLuot: Record<number, string> = {};
    let soLuotChuaGan = 0;
    let soGoiYSanCo = 0;

    lines.forEach((line, idx) => {
      const luot = idx + 1;
      const m = line.match(VAI_RE);
      const vai = m ? chuanVai(m[1]) : "Chưa rõ vai";
      if (VAI_GAN.includes(vai as VaiChuan)) return;
      soLuotChuaGan += 1;

      const tuServer = suggestedRolesByTurn[luot];
      if (tuServer?.vai) {
        mapTheoLuot[luot] = tuServer.vai;
        if (tuServer.lyDo) lyDoTheoLuot[luot] = tuServer.lyDo;
        soGoiYSanCo += 1;
        return;
      }
      const tuHeuristic = goiYVaiTuVanBanLuot(line);
      if (tuHeuristic.vaiGoiY) {
        mapTheoLuot[luot] = tuHeuristic.vaiGoiY;
        if (tuHeuristic.lyDo) lyDoTheoLuot[luot] = tuHeuristic.lyDo;
        soGoiYSanCo += 1;
      }
    });

    return { soLuotChuaGan, soGoiYSanCo, mapTheoLuot, lyDoTheoLuot };
  }, [transcript, suggestedRolesByTurn]);

  const handleApDungGoiYMotCham = () => {
    const { transcriptMoi, soDongDaGan } = apDungVaiGoiY(transcript, thongKeGoiY.mapTheoLuot);
    if (soDongDaGan > 0) {
      onUpdateTranscript(transcriptMoi);
      setThongBaoDaGanNhanh(
        `Đã điền nhanh ${soDongDaGan} vai gợi ý. Bác sĩ chỉ cần đọc lướt kiểm lại và bấm BS/BN/NN (hoặc phím 1/2/3) ở dòng ngoại lệ.`
      );
    }
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
      });
    } else {
      setInterimText("");
      setLiveVolume(0);
      setLiveFreqs([0, 0, 0, 0, 0, 0, 0, 0]);
    }
  }, [isRecording]);

  useEffect(() => {
    return realAudioService.theoDoiMucAm((volume, frequencies) => {
      setLiveVolume(volume);
      setLiveFreqs(frequencies);
    });
  }, []);

  const handleCopy = () => {
    navigator.clipboard.writeText(transcript);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleClear = () => {
    if (window.confirm("Bạn có chắc chắn muốn xóa toàn bộ bản ghi lời thoại này không?")) {
      onUpdateTranscript("");
      setSuggestedRolesByTurn({});
      setThongBaoDaGanNhanh(null);
      setInterimText("");
    }
  };

  // Upload tệp âm thanh thực tế và chuyển thể bằng PhoWhisper tại chỗ
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    e.target.value = "";
    setIsUploading(true);
    setUploadError(null);
    setThongBaoDaGanNhanh(null);

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

      const offsetLuot = transcript ? transcript.split("\n").filter((l) => l.trim()).length : 0;
      const dsGoiY = goiYVaiTuDoan(doan);
      setSuggestedRolesByTurn((prev) => {
        const tiep = { ...prev };
        for (const g of dsGoiY) {
          if (g.vaiGoiY) {
            tiep[offsetLuot + g.luot] = { vai: g.vaiGoiY, lyDo: g.lyDo };
          }
        }
        return tiep;
      });

      const moi = dongTuDoan(doan, data.diarization, soNguoiNoiLonNhat(transcript)).join("\n");
      if (onUpdateSegments && Array.isArray(data.transcriptSegments) && data.transcriptSegments.length > 0) {
        onUpdateSegments(
          data.transcriptSegments.map((s: any, idx: number) => ({
            ...s,
            luot: offsetLuot + idx + 1,
          }))
        );
      }
      // Mốc thời gian chỉ khớp với tệp đầu tiên của ca (lượt bắt đầu từ 1).
      if (onDatAmThanh && offsetLuot === 0) onDatAmThanh(URL.createObjectURL(file));
      onUpdateTranscript(transcript ? `${transcript.trimEnd()}\n${moi}` : moi);
      setGhiChuTach(moTaTach(data.diarization));
    } catch (err: any) {
      console.error(err);
      setUploadError(err.message || "Lỗi khi xử lý tệp âm thanh");
    } finally {
      setIsUploading(false);
    }
  };

  // Trạng thái Chưa ghi nhận cuộc hội thoại
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

            <button
              type="button"
              onClick={thuMauGiongBacSi5Giay}
              className={`w-full py-2 px-3 rounded-xl border transition-all flex items-center justify-center gap-1.5 text-[11.5px] font-medium ${
                dangThuMauGiong
                  ? "bg-amber-50 border-amber-300 text-amber-800 animate-pulse"
                  : mauGiongBs
                  ? "bg-[#F0FDF4] border-[#BBF7D0] text-[#15803D]"
                  : "bg-white border-[#CCE3F0] text-[#0C4A6E] hover:bg-[#F0F9FF]"
              }`}
              title="Lưu đặc trưng tần số giọng bác sĩ cục bộ trên trình duyệt (0 byte gửi ra ngoài)"
            >
              <Fingerprint size={13} />
              <span>
                {dangThuMauGiong
                  ? `Đang lấy mẫu giọng tại máy (${demNguocMauGiong}s)...`
                  : mauGiongBs
                  ? `Mẫu giọng Bác sĩ tại máy (F0 ~${mauGiongBs.f0Hz}Hz · Thu lại 5s)`
                  : "Mẫu giọng Bác sĩ tại máy (5s)"}
              </span>
            </button>
          </div>

          {(uploadError || loiMauGiong) && (
            <div className="mt-3 p-2 bg-red-50 border border-red-200 rounded-lg text-red-700 text-xs">
              {uploadError || loiMauGiong}
            </div>
          )}

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
        <div className="flex flex-wrap items-center justify-between gap-2 mb-4 border-b border-[#CCE3F0] pb-2">
          <div className="flex flex-wrap items-center gap-2">
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

          <div className="flex flex-wrap items-center gap-2">
            {/* Mẫu giọng Bác sĩ cục bộ tại máy (5s - 0 byte gửi ra ngoài) */}
            <button
              type="button"
              onClick={thuMauGiongBacSi5Giay}
              className={`text-xs px-2.5 py-1 rounded-lg border transition-colors flex items-center gap-1.5 font-medium cursor-pointer ${
                dangThuMauGiong
                  ? "bg-amber-50 border-amber-300 text-amber-800 animate-pulse"
                  : mauGiongBs
                  ? "bg-[#F0FDF4] border-[#BBF7D0] text-[#15803D] hover:bg-[#DCFCE7]"
                  : "border-[#CCE3F0] bg-white text-[#0C4A6E] hover:bg-[#E0F2FE]"
              }`}
              title="Trích đặc trưng phổ/cao độ giọng Bác sĩ bằng Web Audio API và chỉ lưu trong localStorage trình duyệt (0 byte gửi ra ngoài)"
            >
              <Fingerprint size={12} />
              <span>
                {dangThuMauGiong
                  ? `Đang thu mẫu (${demNguocMauGiong}s)...`
                  : mauGiongBs
                  ? `Mẫu giọng BS (${mauGiongBs.f0Hz}Hz)`
                  : "Mẫu giọng Bác sĩ tại máy (5s)"}
              </span>
            </button>

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

        {(uploadError || loiMauGiong) && (
          <div className="mb-3 p-2.5 bg-red-50 border border-red-200 rounded-xl text-red-700 text-xs">
            {uploadError || loiMauGiong}
          </div>
        )}

        {/* Boost 1: Thanh 1 chạm áp dụng vai gợi ý để bác sĩ kiểm lại thay vì bấm tay từng dòng */}
        {!isEditing && thongKeGoiY.soLuotChuaGan > 0 && thongKeGoiY.soGoiYSanCo > 0 && (
          <div className="max-w-4xl mb-4 p-3.5 rounded-2xl bg-gradient-to-r from-[#E0F2FE] via-[#F0F9FF] to-[#ECFEFF] border border-[#7DD3FC] shadow-tactile-doctor-card flex flex-wrap items-center justify-between gap-3">
            <div className="min-w-0 flex-1 text-xs text-[#0C4A6E]">
              <div className="font-bold text-[#0369A1] flex items-center gap-1.5">
                <Sparkles size={14} className="text-[#0284C7] flex-shrink-0" />
                <span>
                  Có {thongKeGoiY.soGoiYSanCo}/{thongKeGoiY.soLuotChuaGan} lượt chưa gán đã có gợi ý vai tất định tại chỗ
                </span>
              </div>
              <p className="mt-0.5 text-[11.5px] text-[#334155]">
                Bấm một lần để điền vai gợi ý (không ghi đè dòng đã gán), sau đó đọc lướt kiểm lại hoặc dùng phím{" "}
                <kbd className="px-1 py-0.5 rounded bg-white border border-[#BAE6FD] font-mono text-[10px]">1</kbd> BS ·{" "}
                <kbd className="px-1 py-0.5 rounded bg-white border border-[#BAE6FD] font-mono text-[10px]">2</kbd> BN ·{" "}
                <kbd className="px-1 py-0.5 rounded bg-white border border-[#BAE6FD] font-mono text-[10px]">3</kbd> NN khi trỏ vào dòng.
              </p>
            </div>
            <button
              type="button"
              onClick={handleApDungGoiYMotCham}
              className="px-3.5 py-2 rounded-xl bg-[#0284C7] hover:bg-[#0369A1] text-white text-xs font-semibold shadow-tactile-doctor active:translate-y-0.5 transition-all cursor-pointer flex items-center gap-1.5"
            >
              <Check size={14} />
              <span>Áp dụng {thongKeGoiY.soGoiYSanCo} vai gợi ý để bác sĩ kiểm lại</span>
            </button>
          </div>
        )}

        {thongBaoDaGanNhanh && !isEditing && (
          <div className="max-w-4xl mb-3 p-2.5 bg-[#ECFDF5] border border-[#A7F3D0] rounded-xl text-[#065F46] text-xs flex items-center justify-between gap-2">
            <span>{thongBaoDaGanNhanh}</span>
            <button
              type="button"
              onClick={() => setThongBaoDaGanNhanh(null)}
              className="text-[11px] font-semibold underline hover:no-underline cursor-pointer"
            >
              Ẩn
            </button>
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

        {/* Radar Câu hỏi Cờ đỏ theo thời gian thực (0 token, chạy tại chỗ) */}
        {(() => {
          const coDo = quetRadarCoDo(transcript, gioiTinh);
          if (coDo.length === 0) return null;
          return (
            <section className="mb-4 rounded-2xl border border-[#F5E6B8] bg-[#FEF9E7] px-4 py-3 shadow-tactile-doctor-card space-y-2">
              <div className="flex items-center justify-between gap-2">
                <span className="inline-flex items-center gap-1.5 text-xs font-bold text-[#7A4B00]">
                  <AlertTriangle size={14} className="text-[#B45309]" />
                  Radar câu hỏi cờ đỏ (tại chỗ · 0 token)
                </span>
                <span className="text-[10.5px] font-medium text-[#92400E]">Tự đánh dấu ✓ khi bác sĩ đã hỏi</span>
              </div>
              <div className="space-y-1.5">
                {coDo.map((g) => (
                  <div
                    key={g.id}
                    className={`flex items-start justify-between gap-2 rounded-xl px-3 py-2 text-xs border ${
                      g.daHoi
                        ? "bg-[#ECFDF5] border-[#A7F3D0] text-[#065F46] line-through opacity-80"
                        : g.mucDo === "khan"
                        ? "bg-[#FFF5F5] border-[#F5C2C2] text-[#B4232C]"
                        : "bg-white border-[#F5E6B8] text-[#7A4B00]"
                    }`}
                  >
                    <div className="min-w-0">
                      <span className="font-semibold">{g.daHoi ? "✓ Đã hỏi: " : "Gợi ý hỏi: "}</span>
                      <span>{g.cauHoi}</span>
                      <span className="block text-[11px] opacity-85 mt-0.5">{g.lyDo}</span>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          );
        })()}

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

        {/* Nội dung lời thoại (Chế độ xem hoặc Chế độ sửa tay) */}
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
                const luot = idx + 1;
                const m = line.match(VAI_RE);
                const vai = m ? chuanVai(m[1]) : "Chưa rõ vai";
                const text = m ? line.slice(m[0].length).trim() : line.trim();
                const kieu = kieuVai(vai);
                const daGan = VAI_GAN.includes(vai as VaiChuan);
                const goiY = !daGan ? thongKeGoiY.mapTheoLuot[luot] : undefined;
                const lyDoGoiY = !daGan ? thongKeGoiY.lyDoTheoLuot[luot] : undefined;

                return (
                  <div
                    key={idx}
                    tabIndex={0}
                    onMouseEnter={() => setActiveTurnIdx(idx)}
                    onMouseLeave={() => setActiveTurnIdx((cur) => (cur === idx ? null : cur))}
                    onFocus={() => setActiveTurnIdx(idx)}
                    className="flex items-start gap-3 group focus:outline-none"
                  >
                    <div className="flex flex-col items-center flex-shrink-0 w-16 pt-1 text-center gap-1">
                      <button
                        onClick={() => doiVai(idx)}
                        title="Bấm để đổi vai (hoặc trỏ chuột vào dòng rồi nhấn phím 1=BS, 2=BN, 3=NN)"
                        className={`px-1.5 h-7 min-w-[2.25rem] rounded-full flex items-center justify-center font-bold text-[10px] border whitespace-nowrap ${kieu.mau}`}
                      >
                        {kieu.tat}
                      </button>
                      <span className="text-[9px] text-[#64748B] font-mono">lượt {luot}</span>
                    </div>
                    <div
                      className={`flex-1 bg-white rounded-2xl border p-4 flex flex-wrap items-start justify-between gap-3 transition-colors ${
                        activeTurnIdx === idx
                          ? "border-[#0284C7] ring-1 ring-[#BAE6FD]"
                          : daGan
                          ? "border-[#BAE6FD]"
                          : "border-[#F2DFA8]"
                      }`}
                    >
                      <div className="min-w-0 flex-1 text-[13px] sm:text-[14px] leading-relaxed text-[#0F172A] font-sans">
                        <span className="text-[11px] font-semibold text-[#64748B] mr-1.5">{vai}:</span>
                        {text}
                        {goiY && (
                          <span
                            className="ml-2 inline-flex items-center gap-1 text-[10.5px] font-medium px-2 py-0.5 rounded-full bg-[#F0F9FF] text-[#0369A1] border border-[#BAE6FD]"
                            title={lyDoGoiY || "Gợi ý vai tất định"}
                          >
                            Gợi ý: {goiY}
                          </span>
                        )}
                      </div>

                      {/* Nghe lượt này: đọc to lời thoại (ca không có tệp ghi âm) */}
                      {!audioUrl && text && (
                        <button
                          type="button"
                          onClick={() => docLuot(idx, text, vai)}
                          title={dangDocLuot === idx ? "Dừng đọc" : "Nghe lượt này (đọc to bằng giọng tiếng Việt của máy)"}
                          className={`inline-flex items-center gap-1 px-2 py-1 rounded-lg border text-[11px] font-semibold flex-shrink-0 ${
                            dangDocLuot === idx
                              ? "bg-[#0284C7] text-white border-[#0284C7]"
                              : "bg-[#F0F9FF] text-[#0369A1] border-[#BAE6FD] hover:bg-[#E0F2FE]"
                          }`}
                        >
                          {dangDocLuot === idx ? <Square size={11} /> : <Volume2 size={12} />}
                          {dangDocLuot === idx ? "Dừng" : "Nghe"}
                        </button>
                      )}

                      {/* Pill 1-click BS / BN / NN cho dòng chưa gán (hoặc hiện khi hover dòng đã gán để sửa nhanh) */}
                      <div
                        className={`flex items-center gap-1 flex-shrink-0 ${
                          daGan ? "opacity-0 group-hover:opacity-100 group-focus-within:opacity-100 transition-opacity" : ""
                        }`}
                      >
                        {([
                          ["Bác sĩ", "BS", "1"],
                          ["Bệnh nhân", "BN", "2"],
                          ["Người nhà", "NN", "3"],
                        ] as const).map(([tenVai, tat, phimTat]) => (
                          <button
                            key={tenVai}
                            type="button"
                            onClick={() => ganVaiMotDong(idx, tenVai)}
                            title={`Gán ${tenVai} (Phím ${phimTat})`}
                            className={`px-2 py-0.5 rounded-lg border text-[10.5px] font-bold cursor-pointer hover:brightness-95 transition-all ${
                              KIEU_VAI[tenVai].mau
                            } ${goiY === tenVai ? "ring-1 ring-[#0284C7]" : ""}`}
                          >
                            {tat}
                          </button>
                        ))}
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
