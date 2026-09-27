import React, { useState } from "react";
import { BangDuLieuMinhHoa } from "./BangDuLieuMinhHoa";
import { defaultTemplates } from "../data/mockData";
import { TemplateItem } from "../types";
import { Sparkles, Edit3, Plus, Search } from "lucide-react";

interface TemplatesViewProps {
  onUseTemplate: (tpl: TemplateItem) => void;
}

export const TemplatesView: React.FC<TemplatesViewProps> = ({ onUseTemplate }) => {
  const [templates, setTemplates] = useState<TemplateItem[]>(defaultTemplates);
  const [search, setSearch] = useState("");

  const filtered = templates.filter((t) =>
    t.title.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div id="templates-view" className="flex-1 flex flex-col h-full bg-gradient-to-b from-[#F0F7FA] via-[#F8FBFC] to-[#EEF6FB] select-none overflow-y-auto">
      <BangDuLieuMinhHoa />
      <div className="p-6 border-b border-[#CCE3F0] flex items-center justify-between bg-white/90 backdrop-blur-xs shadow-[0_1px_3px_rgba(2,132,199,0.04)]">
        <div>
          <h1 className="font-serif text-2xl font-bold text-[#0F172A] tracking-tight">
            Mẫu Bệnh án Lâm sàng
          </h1>
          <p className="text-xs text-[#64748B] mt-1">
            Chọn từ các mẫu chuẩn y khoa của MediTrace Sentinel hoặc cấu hình mẫu câu lệnh chuyên khoa riêng cho phòng khám của bạn.
          </p>
        </div>

        <button
          onClick={() => {
            const name = prompt("Nhập tiêu đề mẫu bệnh án mới:");
            if (name) {
              setTemplates([
                {
                  id: `tpl-${Date.now()}`,
                  title: name,
                  category: "thu_vien",
                  iconType: "pen",
                  promptDescription: "Mẫu bệnh án tùy chỉnh theo nhu cầu chuyên khoa.",
                },
                ...templates,
              ]);
            }
          }}
          className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#0284C7] text-white text-xs font-semibold hover:bg-[#0369A1] transition-all shadow-tactile-doctor active:translate-y-0.5"
        >
          <Plus size={14} className="stroke-[2.5]" />
          <span>Tạo mẫu mới</span>
        </button>
      </div>

      <div className="px-6 py-3 border-b border-[#CCE3F0] bg-[#F0F7FA]/70 flex items-center">
        <div className="w-full max-w-md relative">
          <Search size={14} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-[#0284C7]" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Tìm kiếm mẫu bệnh án..."
            className="w-full pl-9 pr-3.5 py-2 rounded-xl border border-[#BAE6FD] bg-white text-xs text-[#0F172A] focus:outline-none focus:border-[#0284C7] focus:ring-2 focus:ring-[#BAE6FD]/50 shadow-tactile-inset"
          />
        </div>
      </div>

      <div className="flex-1 p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((tpl) => (
          <div
            key={tpl.id}
            className="bg-white rounded-2xl border border-[#BAE6FD] p-5 flex flex-col justify-between hover:border-[#0284C7] transition-all shadow-tactile-doctor-card hover:shadow-tactile-doctor"
          >
            <div>
              <div className="flex items-center justify-between mb-3">
                <div className="w-9 h-9 rounded-xl bg-[#E0F2FE] border border-[#BAE6FD] flex items-center justify-center text-[#0284C7] shadow-tactile-doctor-pill">
                  {tpl.iconType === "sparkle" ? (
                    <Sparkles size={16} className="text-[#0284C7]" />
                  ) : (
                    <Edit3 size={16} />
                  )}
                </div>
                {tpl.isPro && (
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#E0F2FE] text-[#0369A1] border border-[#BAE6FD] shadow-tactile-doctor-pill">
                    Pro
                  </span>
                )}
              </div>

              <h3 className="text-sm font-bold text-[#0F172A] mb-1.5">{tpl.title}</h3>
              <p className="text-xs text-[#64748B] leading-relaxed">
                {tpl.promptDescription || "Mẫu ghi chú thăm khám lâm sàng chuẩn cấu trúc y khoa."}
              </p>
            </div>

            <div className="mt-5 pt-3.5 border-t border-[#CCE3F0] flex items-center justify-between">
              <span className="text-[11px] text-[#64748B] font-medium">
                {tpl.category === "session" ? "Thư viện ca khám" : "Thư viện chuẩn MediTrace"}
              </span>
              <button
                onClick={() => onUseTemplate(tpl)}
                className="text-xs font-semibold px-3 py-1.5 rounded-xl bg-[#0284C7] text-white hover:bg-[#0369A1] transition-all shadow-tactile-doctor active:translate-y-0.5"
              >
                Dùng trong ca khám
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
