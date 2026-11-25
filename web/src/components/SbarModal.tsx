import React from "react";
import { Copy, FileText } from "lucide-react";

interface SbarModalProps {
  open: boolean;
  sbarText: string;
  onClose: () => void;
}

export const SbarModal: React.FC<SbarModalProps> = ({ open, sbarText, onClose }) => {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-2xs p-4 no-print animate-in fade-in duration-150">
      <div className="w-full max-w-xl rounded-2xl bg-white border border-[#BAE6FD] shadow-2xl overflow-hidden text-left">
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-slate-100 bg-white">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-sky-100 text-sky-700 flex items-center justify-center flex-shrink-0">
              <FileText size={16} />
            </div>
            <h3 className="font-serif text-[17px] font-semibold text-[#0F172A]">Phiếu Bàn Giao Lâm Sàng (SBAR)</h3>
          </div>
          <button
            onClick={onClose}
            className="px-3 py-1 rounded-xl bg-slate-100 hover:bg-slate-200 text-xs font-semibold text-slate-700 cursor-pointer"
          >
            Đóng
          </button>
        </div>
        <div className="p-5 max-h-[65vh] overflow-y-auto bg-[#F8FBFC]">
          <pre className="whitespace-pre-wrap font-sans text-xs leading-relaxed text-[#0F172A] bg-white p-4 rounded-xl border border-[#BAE6FD] shadow-tactile-doctor-card">
            {sbarText}
          </pre>
        </div>
        <div className="flex items-center justify-end gap-2 px-5 py-3 border-t border-slate-100 bg-[#F8FBFC]">
          <button
            type="button"
            onClick={() => {
              navigator.clipboard.writeText(sbarText);
              onClose();
            }}
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#0284C7] hover:bg-[#0369A1] text-white text-xs font-semibold shadow-tactile-doctor active:scale-95 cursor-pointer"
          >
            <Copy size={13} /> Chép toàn bộ phiếu SBAR
          </button>
        </div>
      </div>
    </div>
  );
};
