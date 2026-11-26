import React, { useMemo, useState } from "react";
import { defaultTemplates } from "../data/mockData";
import { TemplateItem } from "../types";
import { laMauBienDichTaiCho } from "../lib/bieuMauPhapLyOffline";
import { useKho } from "../lib/useKho";
import { Sparkles, Edit3, Plus, Search, ShieldCheck } from "lucide-react";

const MAU_BYT_VA_CHUYEN_KHOA: TemplateItem[] = [
  {
    id: "phieu-chuyen-co-so-kcb-tt01-2025",
    title: "Phiếu chuyển cơ sở KCB BHYT (Phụ lục TT 01/2025/TT-BYT)",
    category: "thu_vien",
    iconType: "pen",
    promptDescription:
      "Biểu mẫu pháp lý chuẩn 3 cấp chuyên môn kỹ thuật (Ban đầu / Cơ bản / Chuyên sâu), tóm tắt lâm sàng, CLS, ICD-10, thuốc đã dùng và tích chọn hiệu lực 1 năm cho bệnh mạn tính.",
  },
  {
    id: "phieu-chuyen-cls-tt01-2025",
    title: "Phiếu chuyển dịch vụ cận lâm sàng (TT 01/2025/TT-BYT)",
    category: "thu_vien",
    iconType: "pen",
    promptDescription:
      "Phiếu chuyển người bệnh hoặc mẫu bệnh phẩm sang cơ sở thực hiện dịch vụ kỹ thuật cận lâm sàng bảo lưu quyền lợi BHYT theo TT 01/2025/TT-BYT.",
  },
  {
    id: "giay-nghi-bhxh-tt25-2025",
    title: "Giấy chứng nhận nghỉ việc hưởng BHXH (TT 25/2025/TT-BYT)",
    category: "thu_vien",
    iconType: "pen",
    promptDescription:
      "Tự động kiểm tra trần tối đa 30 ngày/lần khám ngoại trú và bắt buộc họ tên cha/mẹ khi người bệnh là trẻ em dưới 7 tuổi theo TT 25/2025/TT-BYT.",
  },
  {
    id: "tom-tat-hsba-ra-vien-tt32",
    title: "Bản tóm tắt hồ sơ bệnh án & Giấy ra viện (TT 32/2023/TT-BYT)",
    category: "thu_vien",
    iconType: "pen",
    promptDescription:
      "Biên dịch tại chỗ Bản tóm tắt hồ sơ bệnh án và Giấy ra viện chuẩn biểu mẫu Thông tư 32/2023/TT-BYT có đính kèm dẫn nguồn [T_i].",
  },
  {
    id: "bien-ban-hoi-chan-tt32",
    title: "Biên bản hội chẩn khoa / liên khoa (TT 32/2023/TT-BYT)",
    category: "thu_vien",
    iconType: "pen",
    promptDescription:
      "Biên bản hội chẩn chuyên môn cấp khoa / liên khoa / toàn viện chuẩn Thông tư 32/2023/TT-BYT từ các mệnh đề bác sĩ đã duyệt.",
  },
  {
    id: "khuon-nhi-khoa",
    title: "Bệnh án Nhi khoa chuyên biệt (TT 26/2025 · mg/kg/ngày)",
    category: "session",
    iconType: "pen",
    promptDescription:
      "Bắt buộc cân nặng kê đơn (TT 26/2025/TT-BYT), tháng tuổi, kiểm chiếu liều mg/kg/ngày, tiền sử tiêm chủng & dinh dưỡng, tách riêng lời khai người chăm sóc.",
  },
  {
    id: "khuon-san-phu-khoa",
    title: "Bệnh án Sản - Phụ khoa (PARA · Tuổi thai · Tim thai)",
    category: "session",
    iconType: "pen",
    promptDescription:
      "Cấu trúc chuyên biệt Sản - Phụ khoa: chỉ số PARA, tuổi thai, kinh cuối, thai máy, tim thai, bề cao tử cung và rà soát thuốc an toàn thai kỳ.",
  },
  {
    id: "khuon-cap-cuu-chan-thuong",
    title: "Bệnh án Cấp cứu - Chấn thương (ABCDE + AMPLE + Glasgow)",
    category: "session",
    iconType: "pen",
    promptDescription:
      "Đánh giá sơ cấp ABCDE, thang điểm hôn mê Glasgow (GCS) và khai thác nhanh bệnh sử AMPLE cho ca cấp cứu nội - ngoại chấn thương.",
  },
];

interface TemplatesViewProps {
  onUseTemplate: (tpl: TemplateItem) => void;
}

export const TemplatesView: React.FC<TemplatesViewProps> = ({ onUseTemplate }) => {
  const [customTemplates, setCustomTemplates] = useKho<TemplateItem>("mau-benh-an-tuy-chinh", []);
  const [search, setSearch] = useState("");

  const templates = useMemo(() => {
    const chuanKhongPro = defaultTemplates.map(({ isPro: _boPro, ...conLai }) => conLai);
    const daCo = new Set<string>();
    const hop: TemplateItem[] = [];
    for (const item of [...customTemplates, ...MAU_BYT_VA_CHUYEN_KHOA, ...chuanKhongPro]) {
      if (daCo.has(item.id)) continue;
      daCo.add(item.id);
      hop.push(item);
    }
    return hop;
  }, [customTemplates]);

  const filtered = templates.filter(
    (t) =>
      t.title.toLowerCase().includes(search.toLowerCase()) ||
      (t.promptDescription || "").toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div id="templates-view" className="flex-1 flex flex-col h-full bg-gradient-to-b from-[#F0F7FA] via-[#F8FBFC] to-[#EEF6FB] select-none overflow-y-auto">
      <div className="p-6 border-b border-[#CCE3F0] flex items-center justify-between bg-white/90 backdrop-blur-xs shadow-[0_1px_3px_rgba(2,132,199,0.04)]">
        <div>
          <h1 className="font-serif text-2xl font-bold text-[#0F172A] tracking-tight">
            Mẫu Bệnh án &amp; Biểu mẫu Pháp lý Bộ Y tế (2025–2026)
          </h1>
          <p className="text-xs text-[#64748B] mt-1">
            Hỗ trợ đầy đủ Biểu mẫu Pháp lý BYT (TT 01/2025, TT 25/2025, TT 32/2023) và Khuôn Chuyên khoa (Nhi khoa, Sản khoa, Cấp cứu) biên dịch tất định 100% tại chỗ.
          </p>
        </div>

        <button
          onClick={() => {
            const name = prompt("Nhập tiêu đề mẫu bệnh án mới:");
            if (name && name.trim()) {
              setCustomTemplates((prev) => [
                {
                  id: `tpl-${Date.now()}`,
                  title: name.trim(),
                  category: "thu_vien",
                  iconType: "pen",
                  promptDescription: "Mẫu bệnh án tùy chỉnh theo nhu cầu chuyên khoa.",
                },
                ...prev,
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
            placeholder="Tìm mẫu TT 01/2025, TT 25/2025, Nhi khoa, Sản khoa, Cấp cứu..."
            className="w-full pl-9 pr-3.5 py-2 rounded-xl border border-[#BAE6FD] bg-white text-xs text-[#0F172A] focus:outline-none focus:border-[#0284C7] focus:ring-2 focus:ring-[#BAE6FD]/50 shadow-tactile-inset"
          />
        </div>
      </div>

      <div className="flex-1 p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((tpl) => {
          const laBienDichTaiCho = laMauBienDichTaiCho(tpl.id);
          return (
            <div
              key={tpl.id}
              className="bg-white rounded-2xl border border-[#BAE6FD] p-5 flex flex-col justify-between hover:border-[#0284C7] transition-all shadow-tactile-doctor-card hover:shadow-tactile-doctor"
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-3">
                  <div
                    className={`w-9 h-9 rounded-xl border flex items-center justify-center shadow-tactile-doctor-pill ${
                      laBienDichTaiCho
                        ? "bg-[#ECFDF5] border-[#A7F3D0] text-[#059669]"
                        : "bg-[#E0F2FE] border-[#BAE6FD] text-[#0284C7]"
                    }`}
                  >
                    {laBienDichTaiCho ? (
                      <ShieldCheck size={16} />
                    ) : tpl.iconType === "sparkle" ? (
                      <Sparkles size={16} className="text-[#0284C7]" />
                    ) : (
                      <Edit3 size={16} />
                    )}
                  </div>
                  {laBienDichTaiCho && (
                    <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-[#ECFDF5] text-[#065F46] border border-[#A7F3D0]">
                      100% tại chỗ · Luật BYT
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
                  {laBienDichTaiCho
                    ? "Biên dịch tức thời (< 10 ms)"
                    : tpl.category === "session"
                    ? "Thư viện ca khám"
                    : "Thư viện chuẩn MediTrace"}
                </span>
                <button
                  onClick={() => onUseTemplate(tpl)}
                  className="text-xs font-semibold px-3 py-1.5 rounded-xl bg-[#0284C7] text-white hover:bg-[#0369A1] transition-all shadow-tactile-doctor active:translate-y-0.5 cursor-pointer"
                >
                  Dùng trong ca khám
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
