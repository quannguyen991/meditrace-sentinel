import React from "react";
import { DocumentTabItem } from "../types";
import { FileText, Save, Check } from "lucide-react";

interface ContextViewProps {
  tab: DocumentTabItem;
  onUpdateContent: (content: string) => void;
}

export const ContextView: React.FC<ContextViewProps> = ({ tab, onUpdateContent }) => {
  const [saved, setSaved] = React.useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div id="context-view" className="flex-1 p-8 bg-gradient-to-b from-[#F0F7FA] via-[#F8FBFC] to-[#EEF6FB] overflow-y-auto select-none">
      <div className="max-w-3xl mx-auto bg-white rounded-2xl border border-[#BAE6FD] p-6 shadow-tactile-doctor-card">
        <div className="flex items-center justify-between mb-4 pb-3 border-b border-[#CCE3F0]">
          <div className="flex items-center gap-2">
            <FileText size={16} className="text-[#0284C7]" />
            <h3 className="text-sm font-bold text-[#0F172A]">Ngữ cảnh Lâm sàng & Thông tin Bệnh nhân</h3>
          </div>
          <button
            onClick={handleSave}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#0284C7] text-white text-xs font-semibold hover:bg-[#0369A1] transition-all shadow-tactile-doctor active:translate-y-0.5"
          >
            {saved ? <Check size={13} className="text-emerald-300 stroke-[3]" /> : <Save size={13} />}
            <span>{saved ? "Đã lưu thành công" : "Lưu ngữ cảnh"}</span>
          </button>
        </div>

        <p className="text-xs text-[#64748B] mb-4 leading-relaxed">
          Nhập thêm chỉ số sinh tồn ban đầu, tiền sử dị ứng thuốc, bệnh lý mãn tính hoặc kết quả cận lâm sàng trước đó để AI đối chiếu và tạo bệnh án chính xác nhất.
        </p>

        <textarea
          value={tab.content}
          onChange={(e) => onUpdateContent(e.target.value)}
          placeholder="Nhập tiền sử bệnh, dị ứng thuốc, các thuốc đang sử dụng, kết quả xét nghiệm..."
          className="w-full h-80 p-4 rounded-xl border border-[#BAE6FD] bg-[#F0F7FA]/50 text-sm text-[#0F172A] placeholder-[#94A3B8] focus:outline-none focus:border-[#0284C7] focus:ring-2 focus:ring-[#BAE6FD]/50 leading-relaxed resize-none font-sans shadow-tactile-inset"
        />
      </div>
    </div>
  );
};
