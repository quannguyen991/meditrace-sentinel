import React from "react";

type Props = {
  /** Mức của từng vạch, 0–100 (lấy từ bộ phân tích âm thanh của micrô). */
  cacVach: number[];
  /** Âm lượng chung, 0–100. */
  amLuong: number;
  /** true nếu đã nhiều giây liền không nghe thấy tiếng nào. */
  imLang: boolean;
  thoiGian: string;
};

/**
 * Dải "đang ghi âm": các vạch nhảy theo giọng nói để người dùng thấy micrô đang thu.
 * Không nghe thấy gì trong vài giây thì đổi sang cảnh báo (micrô tắt, chọn nhầm thiết bị, hoặc chưa ai nói).
 */
export const ThanhAmThanh: React.FC<Props> = ({ cacVach, amLuong, imLang, thoiGian }) => {
  const mauChinh = imLang ? "#B45309" : "#059669";
  return (
    <div
      role="status"
      aria-live="polite"
      className={`z-20 flex items-center gap-3 border-b px-4 py-2 ${
        imLang ? "border-amber-200 bg-amber-50" : "border-emerald-200 bg-emerald-50"
      }`}
    >
      <span className="flex shrink-0 items-center gap-1.5 text-xs font-semibold" style={{ color: mauChinh }}>
        <span className="relative flex h-2.5 w-2.5">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-red-500 opacity-70" />
          <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-red-600" />
        </span>
        Đang ghi âm · {thoiGian}
      </span>

      <div className="flex h-8 min-w-0 flex-1 items-center justify-center gap-[3px]" aria-hidden="true">
        {cacVach.map((v, i) => (
          <span
            key={i}
            className="w-1 rounded-full transition-[height] duration-75"
            style={{
              height: `${Math.max(3, Math.round((v / 100) * 30))}px`,
              backgroundColor: mauChinh,
              opacity: v > 6 ? 1 : 0.35,
            }}
          />
        ))}
      </div>

      <span className="hidden shrink-0 text-xs sm:block" style={{ color: mauChinh }}>
        {imLang
          ? "Chưa nghe thấy tiếng. Kiểm tra micrô hoặc thử nói."
          : amLuong > 6
          ? "Micrô đang thu"
          : "Micrô sẵn sàng, mời nói"}
      </span>
    </div>
  );
};
