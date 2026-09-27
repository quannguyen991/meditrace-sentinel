import React, { useState, useRef } from "react";
import {
  Sparkles,
  ArrowUp,
  Mic,
  MicOff,
  Paperclip,
  ThumbsUp,
  ThumbsDown,
  Dna,
  ChevronDown,
  BarChart2,
  Check,
} from "lucide-react";

interface BottomPromptBarProps {
  onSubmitPrompt: (prompt: string) => void;
  isLoading?: boolean;
  onOpenVerification?: () => void;
}

export const BottomPromptBar: React.FC<BottomPromptBarProps> = ({
  onSubmitPrompt,
  isLoading = false,
  onOpenVerification,
}) => {
  const [prompt, setPrompt] = useState("");
  const [isListening, setIsListening] = useState(false);
  const [recognitionVote, setRecognitionVote] = useState<"up" | "down" | null>(null);
  const recognitionRef = useRef<any>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || isLoading) return;
    onSubmitPrompt(prompt.trim());
    setPrompt("");
  };

  const toggleVoiceInput = () => {
    // Tắt có chủ đích: Web Speech API trên Chrome gửi âm thanh lên máy chủ Google.
    const SpeechRecognition: any = null;

    if (!SpeechRecognition) {
      alert("Đọc chính tả trực tiếp đã tắt: nhận dạng giọng nói của trình duyệt gửi âm thanh lên máy chủ Google. Dùng nút Ghi âm ở đầu trang — tệp ghi âm được chép bằng PhoWhisper chạy tại chỗ.");
      return;
    }

    if (isListening) {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (e) {}
      }
      setIsListening(false);
    } else {
      try {
        const recognition = new SpeechRecognition();
        recognition.lang = "vi-VN";
        recognition.continuous = false;
        recognition.interimResults = false;

        recognition.onresult = (event: any) => {
          const text = event.results[0][0].transcript;
          if (text) {
            setPrompt((prev) => (prev ? `${prev} ${text}` : text));
          }
        };

        recognition.onend = () => {
          setIsListening(false);
        };

        recognition.onerror = () => {
          setIsListening(false);
        };

        recognition.start();
        recognitionRef.current = recognition;
        setIsListening(true);
      } catch (err) {
        setIsListening(false);
      }
    }
  };

  return (
    <div
      id="bottom-prompt-bar-container"
      className="bg-gradient-to-b from-[#F8FBFC] to-[#F0F9FF] border-t border-[#BAE6FD] shadow-[0_-4px_20px_rgba(2,132,199,0.06)] px-3 @md:px-5 py-2 @md:py-2.5 flex flex-col items-center select-none w-full"
    >
      {/* 3-Part Bottom Layout matching Image 3 */}
      <div className="w-full flex items-center justify-between gap-3 max-w-6xl">
        {/* Left: Đánh giá chất lượng nhận diện */}
        <div className="hidden @4xl:flex items-center gap-1.5 text-xs text-[#0369A1] flex-shrink-0">
          <BarChart2 size={14} className="text-[#0284C7]" />
          <span className="font-medium text-[11px]">Bản chép nghe có đúng không?</span>
          <div className="flex items-center gap-1 ml-1">
            <button
              onClick={() => setRecognitionVote(recognitionVote === "up" ? null : "up")}
              className={`p-1 rounded-md transition-colors ${
                recognitionVote === "up"
                  ? "bg-emerald-100 text-emerald-700 shadow-2xs"
                  : "hover:bg-[#E0F2FE] text-[#64748B]"
              }`}
              title="Nhận diện tốt"
            >
              <ThumbsUp size={12} className={recognitionVote === "up" ? "fill-current" : ""} />
            </button>
            <button
              onClick={() => setRecognitionVote(recognitionVote === "down" ? null : "down")}
              className={`p-1 rounded-md transition-colors ${
                recognitionVote === "down"
                  ? "bg-red-100 text-red-700 shadow-2xs"
                  : "hover:bg-[#E0F2FE] text-[#64748B]"
              }`}
              title="Nhận diện cần cải thiện"
            >
              <ThumbsDown size={12} className={recognitionVote === "down" ? "fill-current" : ""} />
            </button>
          </div>
        </div>

        {/* Center: Floating Prompt Pill */}
        <form
          onSubmit={handleSubmit}
          className="flex-1 min-w-0 max-w-xl mx-auto bg-white rounded-full border-[1.5px] border-[#BAE6FD] shadow-tactile-box focus-within:border-[#0284C7] focus-within:ring-2 focus-within:ring-[#BAE6FD]/40 px-3 sm:px-4 py-1.5 flex items-center gap-2 transition-all"
        >

          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder={isListening ? "Đang lắng nghe khẩu lệnh..." : "Hỏi, chỉnh sửa hoặc tạo mới..."}
            className="flex-1 bg-transparent border-none text-xs text-[#0F172A] placeholder-[#94A3B8] focus:outline-none min-w-0"
          />

          {/* Model token badge: [M] +7k */}
          <div
            className="hidden @lg:flex items-center gap-1 px-2 py-0.5 rounded-full bg-[#E0F2FE] border border-[#BAE6FD] text-[10px] font-semibold text-[#0369A1] cursor-pointer hover:bg-[#BAE6FD] shadow-tactile-doctor-pill transition-colors flex-shrink-0"
            title="Bản nháp do Qwen3-4B chạy tại chỗ"
          >
            <span className="w-3.5 h-3.5 rounded-full bg-[#0284C7] text-white flex items-center justify-center text-[8px] font-bold shadow-2xs">
              M
            </span>
            <span>Qwen3-4B</span>
          </div>


          {/* Send Button */}
          <button
            type="submit"
            disabled={!prompt.trim() || isLoading}
            className="w-6 h-6 rounded-full bg-[#0284C7] text-white flex items-center justify-center hover:bg-[#0369A1] disabled:opacity-40 transition-all flex-shrink-0 shadow-tactile-doctor active:translate-y-0.5"
            title="Gửi lệnh"
          >
            <ArrowUp size={13} className="stroke-[2.5]" />
          </button>
        </form>

      </div>

      {/* Medical Disclaimer */}
      <p className="hidden @md:block text-[10px] @xl:text-[11px] text-[#0369A1]/70 mt-1 text-center truncate max-w-full px-2">
        Vui lòng xem lại bệnh án trước khi sử dụng để đảm bảo tính chuẩn xác cho ca khám
      </p>
    </div>
  );
};
