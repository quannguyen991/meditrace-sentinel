/**
 * Khung "Tình trạng hệ thống" — mở từ nút Trợ giúp. Cho biết thật cái gì đang chạy ở đâu:
 * dịch vụ tại chỗ, máy làm khâu tách mệnh đề, PhoWhisper, cổng mô hình ngoài. Không có số giả.
 */
import React, { useEffect, useState } from "react";
import { X } from "lucide-react";

interface Props {
  onClose: () => void;
}

export const TinhTrangHeThong: React.FC<Props> = ({ onClose }) => {
  const [dv, setDv] = useState<any>(null);
  const [ngoai, setNgoai] = useState<any>(null);
  const [loi, setLoi] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/health")
      .then(async (r) => {
        const d = await r.json();
        if (!r.ok) throw new Error(d?.error || `mã ${r.status}`);
        setDv(d);
      })
      .catch((e) => setLoi(String(e?.message || e)));
    fetch("/api/external/status")
      .then((r) => r.json())
      .then(setNgoai)
      .catch(() => setNgoai({ configured: false }));
  }, []);

  const Dong = ({ ten, gia, tot }: { ten: string; gia: React.ReactNode; tot?: boolean }) => (
    <div className="flex items-start justify-between gap-3 py-1 border-b border-[#EEF2F1] last:border-0">
      <span className="text-[#64748B]">{ten}</span>
      <span className={`text-right font-medium ${tot === false ? "text-[#B4232C]" : "text-[#0F172A]"}`}>{gia}</span>
    </div>
  );

  return (
    <div className="fixed inset-0 z-50 bg-black/20 flex items-start justify-center pt-20 px-4" onClick={onClose}>
      <div className="bg-white rounded-2xl border border-[#E2ECE9] shadow-xl w-full max-w-lg p-5 text-xs" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-base font-bold text-[#0F172A]">Tình trạng hệ thống</h2>
          <button onClick={onClose} className="p-1 rounded hover:bg-[#F1F5F9]" aria-label="Đóng">
            <X size={16} />
          </button>
        </div>

        {loi && (
          <p className="mb-3 p-2 rounded-lg bg-[#FDE8E8] text-[#8C1D26]">
            Dịch vụ MediTrace chưa chạy: {loi}
          </p>
        )}
        {dv && (
          <div className="mb-3">
            <Dong ten="Dịch vụ MediTrace" gia="đang chạy" tot />
            <Dong ten="Mô hình tách mệnh đề" gia={dv.mo_hinh} />
            <Dong
              ten="Máy chạy khâu tách"
              gia={dv.mo_hinh_xa ? `máy xa (${dv.mo_hinh_xa})` : dv.cho_nap_mo_hinh ? dv.thiet_bi : "tắt (chỉ ca có sẵn)"}
              tot={!!(dv.mo_hinh_xa || dv.cho_nap_mo_hinh)}
            />
            <Dong ten="Ca dựng lại nhanh từ bộ đệm" gia={dv.so_ca_bo_dem} />
            <Dong ten="Cổng rủi ro" gia={dv.chinh_sach_cong} />
            <Dong ten="Chép âm" gia={`${dv.asr?.nha_cung_cap === "auto" ? "PhoWhisper (VinAI)" : dv.asr?.nha_cung_cap} · chạy tại chỗ`} />
          </div>
        )}
        {ngoai && (
          <div className="mb-3">
            <Dong
              ten="Mô hình ngoài (thương mại)"
              gia={ngoai.configured ? (ngoai.reachable ? `kết nối được · ${ngoai.model}` : "không tới được") : "chưa cấu hình khoá"}
              tot={!!(ngoai.configured && ngoai.reachable)}
            />
          </div>
        )}

        <h3 className="font-bold text-[#0F172A] mt-2 mb-1">Dùng thế nào</h3>
        <ol className="list-decimal pl-4 space-y-1 text-[#334155]">
          <li>Tab Lời thoại: ghi âm, tải tệp âm thanh, gõ tay, hoặc nạp một ca đã chạy trước.</li>
          <li>Bấm nhãn tròn bên trái mỗi lượt để chọn Bác sĩ / Bệnh nhân / Người nhà. Hệ thống không đoán vai.</li>
          <li>Tạo bản nháp: Qwen3-4B tách mệnh đề, luật + cổng rủi ro dựng hồ sơ.</li>
          <li>Mở “Duyệt từng mệnh đề”: đối chiếu lượt làm căn cứ, rồi giữ / sửa / bỏ.</li>
          <li>Công tắc “Mô hình ngoài” (mặc định tắt) mở thêm: sửa theo lời nhắc, hỏi về ca khám, gợi ý câu hỏi, bản so sánh.</li>
        </ol>
      </div>
    </div>
  );
};
