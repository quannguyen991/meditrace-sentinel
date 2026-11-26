import React, { useCallback, useEffect, useMemo, useState } from "react";
import { ArrowRight, Check, RotateCcw } from "lucide-react";

interface HisMucItem {
  nhan: string;
  noiDung: string;
}

interface HisSmartCopyPopoverProps {
  open: boolean;
  items: HisMucItem[];
  onClose: () => void;
}

export const HisSmartCopyPopover: React.FC<HisSmartCopyPopoverProps> = ({ open, items, onClose }) => {
  const [daChepHis, setDaChepHis] = useState<string | null>(null);
  const [viTriQueue, setViTriQueue] = useState<number>(0);
  const [daHoanTatChuoi, setDaHoanTatChuoi] = useState(false);

  const cacMucCoNoiDung = useMemo(
    () => items.filter((m) => Boolean(m.noiDung && m.noiDung.trim())),
    [items]
  );

  // Reset con trỏ về Bước 1 mỗi khi mở lại hộp thoại hoặc thay đổi số mục có nội dung
  useEffect(() => {
    if (open) {
      setViTriQueue(0);
      setDaHoanTatChuoi(false);
    }
  }, [open, cacMucCoNoiDung.length]);

  const chepVaChuyenKeTiep = useCallback(() => {
    if (cacMucCoNoiDung.length === 0) return;
    const idxHienTai = daHoanTatChuoi ? 0 : Math.min(viTriQueue, cacMucCoNoiDung.length - 1);
    const muc = cacMucCoNoiDung[idxHienTai];
    if (!muc) return;

    navigator.clipboard?.writeText(muc.noiDung);
    setDaChepHis(muc.nhan);
    setTimeout(() => setDaChepHis((cur) => (cur === muc.nhan ? null : cur)), 1600);

    if (idxHienTai + 1 < cacMucCoNoiDung.length) {
      setViTriQueue(idxHienTai + 1);
      setDaHoanTatChuoi(false);
    } else {
      setDaHoanTatChuoi(true);
    }
  }, [cacMucCoNoiDung, viTriQueue, daHoanTatChuoi]);

  // Phím tắt Alt+N khi bảng đang mở để bác sĩ chép liên hoàn từng ô HIS siêu nhanh
  useEffect(() => {
    if (!open) return;
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.altKey && (e.key === "n" || e.key === "N")) {
        e.preventDefault();
        chepVaChuyenKeTiep();
      } else if (e.key === "Escape") {
        onClose();
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [open, chepVaChuyenKeTiep, onClose]);

  if (!open) return null;

  const mucDangTro =
    !daHoanTatChuoi && cacMucCoNoiDung.length > 0
      ? cacMucCoNoiDung[Math.min(viTriQueue, cacMucCoNoiDung.length - 1)]
      : null;

  return (
    <div className="fixed bottom-4 right-4 z-40 w-88 max-w-[94vw] rounded-2xl border border-[#BAE6FD] bg-white shadow-2xl p-3.5 space-y-2.5 no-print animate-in fade-in duration-150">
      <div className="flex items-center justify-between border-b border-slate-100 pb-2">
        <div>
          <span className="font-serif text-[14px] font-semibold text-[#0F172A]">Chép nhanh sang ô HIS</span>
          <span className="ml-2 text-[10px] font-mono px-1.5 py-0.5 rounded bg-[#E0F2FE] text-[#0369A1] border border-[#BAE6FD]">
            Alt+N
          </span>
        </div>
        <button onClick={onClose} className="text-xs font-semibold text-[#64748B] hover:text-[#0F172A] cursor-pointer">
          Đóng
        </button>
      </div>

      {/* Chuỗi dán liên hoàn (Sequential Paste Queue) */}
      {cacMucCoNoiDung.length > 0 && (
        <div className="rounded-xl border border-[#7DD3FC] bg-gradient-to-r from-[#E0F2FE]/80 to-[#F0F9FF] p-2.5 space-y-2">
          <div className="flex items-center justify-between gap-2 text-[11px]">
            <span className="font-bold text-[#0369A1] truncate">
              {daHoanTatChuoi
                ? `✓ Đã chép đủ ${cacMucCoNoiDung.length}/${cacMucCoNoiDung.length} ô HIS`
                : `Bước ${Math.min(viTriQueue, cacMucCoNoiDung.length - 1) + 1}/${cacMucCoNoiDung.length}: ${mucDangTro?.nhan}`}
            </span>
            <button
              type="button"
              onClick={() => {
                setViTriQueue(0);
                setDaHoanTatChuoi(false);
              }}
              title="Đặt lại chuỗi dán về Bước 1"
              className="p-1 rounded-lg text-[#0369A1] hover:bg-white/80 cursor-pointer flex-shrink-0"
            >
              <RotateCcw size={12} />
            </button>
          </div>
          <button
            type="button"
            onClick={chepVaChuyenKeTiep}
            className="w-full py-1.5 px-3 rounded-xl bg-[#0284C7] hover:bg-[#0369A1] text-white text-xs font-semibold shadow-tactile-doctor active:translate-y-0.5 transition-all flex items-center justify-center gap-1.5 cursor-pointer"
          >
            {daHoanTatChuoi ? (
              <>
                <RotateCcw size={12} />
                <span>Chép lại từ Bước 1 (Alt+N)</span>
              </>
            ) : (
              <>
                <span>Chép &amp; Chuyển ô kế</span>
                <ArrowRight size={13} />
              </>
            )}
          </button>
        </div>
      )}

      <div className="max-h-64 overflow-y-auto space-y-2">
        {items.map((m) => {
          const laMucHienTai = mucDangTro?.nhan === m.nhan;
          const idxTrongQueue = cacMucCoNoiDung.findIndex((x) => x.nhan === m.nhan);
          const daQua = daHoanTatChuoi ? idxTrongQueue >= 0 : idxTrongQueue >= 0 && idxTrongQueue < viTriQueue;

          return (
            <div
              key={m.nhan}
              onClick={() => {
                if (idxTrongQueue >= 0) {
                  setViTriQueue(idxTrongQueue);
                  setDaHoanTatChuoi(false);
                }
              }}
              className={`flex items-start justify-between gap-2 rounded-xl border p-2.5 transition-colors ${
                laMucHienTai
                  ? "border-[#0284C7] bg-[#E0F2FE]/60 ring-1 ring-[#7DD3FC]"
                  : daQua
                  ? "border-[#BBF7D0] bg-[#F0FDF4]/60"
                  : "border-[#CCE3F0] bg-[#F0F7FA]/50"
              } ${idxTrongQueue >= 0 ? "cursor-pointer" : ""}`}
            >
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-1.5 text-[11px] font-semibold text-[#0369A1]">
                  {daQua && <Check size={11} className="text-emerald-600 flex-shrink-0" />}
                  <span className="truncate">{m.nhan}</span>
                </div>
                <div className="text-[11px] text-[#334155] line-clamp-2">{m.noiDung || "(Trống)"}</div>
              </div>
              <button
                type="button"
                disabled={!m.noiDung}
                onClick={(e) => {
                  e.stopPropagation();
                  navigator.clipboard?.writeText(m.noiDung);
                  setDaChepHis(m.nhan);
                  setTimeout(() => setDaChepHis((cur) => (cur === m.nhan ? null : cur)), 1500);
                }}
                className="px-2.5 py-1 rounded-xl bg-white border border-[#BAE6FD] text-[10.5px] font-semibold text-[#0C4A6E] hover:bg-[#F0F9FF] shadow-tactile-doctor-pill disabled:opacity-40 flex-shrink-0 cursor-pointer"
              >
                {daChepHis === m.nhan ? "Đã chép ✓" : "Chép"}
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
};
