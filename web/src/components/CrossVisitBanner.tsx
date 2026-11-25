import React from "react";
import { AlertTriangle } from "lucide-react";
import type { CanhBaoMauThuanLanKham } from "../lib/doiChieuLanKham";

interface CrossVisitBannerProps {
  alerts: CanhBaoMauThuanLanKham[];
}

export const CrossVisitBanner: React.FC<CrossVisitBannerProps> = ({ alerts }) => {
  if (alerts.length === 0) return null;
  return (
    <div className="max-w-3xl mx-auto mb-4 space-y-2.5 no-print">
      {alerts.map((cb) => (
        <div
          key={cb.id}
          className={`rounded-2xl border p-4 text-xs shadow-tactile-doctor-card ${
            cb.mucDo === "khan_cap"
              ? "bg-[#FFF5F5] border-[#F5C2C2] text-[#B4232C]"
              : "bg-[#FEF9E7] border-[#F5E6B8] text-[#7A4B00]"
          }`}
        >
          <div className="flex items-center gap-1.5 font-bold">
            <AlertTriangle size={14} />
            <span>{cb.tieuDe}</span>
          </div>
          <p className="mt-1 leading-relaxed">{cb.chiTiet}</p>
          <div className="mt-2 grid sm:grid-cols-2 gap-2 text-[11px]">
            <div className="rounded-xl bg-white/90 border border-black/10 p-2.5">
              <span className="font-semibold">Lần khám {cb.ngayKhamTruoc}:</span> “{cb.trichDanCu}”
            </div>
            <div className="rounded-xl bg-white/90 border border-black/10 p-2.5">
              <span className="font-semibold">Hôm nay:</span> “{cb.trichDanMoi}”
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};
