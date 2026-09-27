/**
 * Dải nhắc: màn này chạy bằng dữ liệu minh hoạ, không phải dữ liệu thật và không nối
 * với mô hình của dự án. Bắt buộc có, để người xem demo không nhầm.
 */
import React from "react";
import { Info } from "lucide-react";

export const BangDuLieuMinhHoa: React.FC<{ noi_dung?: string }> = ({ noi_dung }) => (
  <div className="bg-[#FEF6E0] border-b border-[#F2DFA8] px-4 py-2 flex items-start gap-2 text-[11px] text-[#A16207]">
    <Info size={13} className="mt-[1px] shrink-0" />
    <span>
      {noi_dung ||
        "Màn này dùng dữ liệu minh hoạ, không phải bệnh nhân thật và không do mô hình của dự án sinh ra."}
    </span>
  </div>
);
