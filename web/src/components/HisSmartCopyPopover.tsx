import React, { useState } from "react";

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
  if (!open) return null;

  return (
    <div className="fixed bottom-4 right-4 z-40 w-80 max-w-[92vw] rounded-2xl border border-[#BAE6FD] bg-white shadow-2xl p-3.5 space-y-2.5 no-print animate-in fade-in duration-150">
      <div className="flex items-center justify-between border-b border-slate-100 pb-2">
        <span className="font-serif text-[14px] font-semibold text-[#0F172A]">Chép nhanh sang ô HIS</span>
        <button onClick={onClose} className="text-xs font-semibold text-[#64748B] hover:text-[#0F172A] cursor-pointer">
          Đóng
        </button>
      </div>
      <div className="max-h-72 overflow-y-auto space-y-2">
        {items.map((m) => (
          <div
            key={m.nhan}
            className="flex items-start justify-between gap-2 rounded-xl border border-[#CCE3F0] p-2.5 bg-[#F0F7FA]/50"
          >
            <div className="min-w-0 flex-1">
              <div className="text-[11px] font-semibold text-[#0369A1]">{m.nhan}</div>
              <div className="text-[11px] text-[#334155] line-clamp-2">{m.noiDung || "(Trống)"}</div>
            </div>
            <button
              type="button"
              disabled={!m.noiDung}
              onClick={() => {
                navigator.clipboard.writeText(m.noiDung);
                setDaChepHis(m.nhan);
                setTimeout(() => setDaChepHis(null), 1500);
              }}
              className="px-2.5 py-1 rounded-xl bg-white border border-[#BAE6FD] text-[10.5px] font-semibold text-[#0C4A6E] hover:bg-[#F0F9FF] shadow-tactile-doctor-pill disabled:opacity-40 flex-shrink-0 cursor-pointer"
            >
              {daChepHis === m.nhan ? "Đã chép ✓" : "Chép"}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};
