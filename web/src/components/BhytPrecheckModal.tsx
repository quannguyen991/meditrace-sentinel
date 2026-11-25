import React from "react";
import { ShieldAlert } from "lucide-react";
import type { PyBhytPrecheckResponse } from "../types/api-contract";

export interface BhytPrecheckResult extends Partial<PyBhytPrecheckResponse> {
  ma_icd10_chinh?: string | null;
  icd10_chi_tiet?: Array<{ ma: string; ten: string; khoa: string; trich_dan?: string }>;
  canh_bao_xuat_toan?: Array<{ thuoc: string; ly_do: string; muc_do?: string }>;
  trang_thai?: string;
}

interface BhytPrecheckModalProps {
  open: boolean;
  loading: boolean;
  result: BhytPrecheckResult | null;
  onClose: () => void;
}

export const BhytPrecheckModal: React.FC<BhytPrecheckModalProps> = ({ open, loading, result, onClose }) => {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-2xs p-4 no-print animate-in fade-in duration-150">
      <div className="w-full max-w-xl rounded-2xl bg-white border border-[#BAE6FD] shadow-2xl overflow-hidden text-left">
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-slate-100 bg-white">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-[#FEF9E7] border border-[#F5E6B8] text-[#7A4B00] flex items-center justify-center flex-shrink-0">
              <ShieldAlert size={16} />
            </div>
            <h3 className="font-serif text-[17px] font-semibold text-[#0F172A]">Tiền kiểm Mã ICD-10 & Chống Xuất toán BHYT</h3>
          </div>
          <button
            onClick={onClose}
            className="px-3 py-1 rounded-xl bg-slate-100 hover:bg-slate-200 text-xs font-semibold text-slate-700 cursor-pointer"
          >
            Đóng
          </button>
        </div>
        <div className="p-5 max-h-[65vh] overflow-y-auto space-y-3 text-xs bg-[#F8FBFC]">
          {loading && <p className="text-[#64748B]">Đang chạy BHYTXmlPreChecker tại chỗ...</p>}
          {!loading && result && (
            <>
              <div className="rounded-xl border border-[#BAE6FD] bg-white p-3.5 space-y-2 shadow-tactile-doctor-card">
                <div className="font-bold text-[#0369A1]">Mã ICD-10 gợi ý (4 ký tự)</div>
                {(result.icd10_chi_tiet || []).length === 0 ? (
                  <p className="text-[#64748B]">Chưa nhận diện được mã ICD-10 đặc hiệu từ hội thoại.</p>
                ) : (
                  <ul className="space-y-1.5">
                    {result.icd10_chi_tiet!.map((m) => (
                      <li key={m.ma} className="bg-[#F0F7FA]/60 rounded-xl border border-[#CCE3F0] p-2.5">
                        <span className="font-mono font-bold text-[#0284C7]">{m.ma}</span> —{" "}
                        <span className="font-semibold text-[#0F172A]">{m.ten}</span>{" "}
                        <span className="text-[10.5px] text-[#64748B]">({m.khoa})</span>
                        {m.trich_dan && <p className="text-[11px] text-[#475569] mt-0.5 italic">Trích dẫn: “{m.trich_dan}”</p>}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
              <div className="rounded-xl border border-[#F5C2C2] bg-[#FFF5F5] p-3.5 space-y-2">
                <div className="font-bold text-[#B4232C]">Cảnh báo nguy cơ xuất toán BHYT</div>
                {(result.canh_bao_xuat_toan || []).length === 0 ? (
                  <p className="text-[#0D6B50] font-semibold">✓ Không phát hiện bất tương hợp thuốc — mã ICD-10.</p>
                ) : (
                  <ul className="space-y-1.5">
                    {result.canh_bao_xuat_toan!.map((cb, idx) => (
                      <li key={idx} className="text-[#B4232C] bg-white rounded-xl border border-[#F5C2C2] p-2.5">
                        <strong>{cb.thuoc}:</strong> {cb.ly_do}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};
