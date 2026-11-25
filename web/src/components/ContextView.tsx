import React from "react";
import { DocumentTabItem } from "../types";
import { FileText, Save, Check, ScanText, AlertTriangle, Plus, ImagePlus, X } from "lucide-react";
import { trichNguCanhChoTroLy } from "../lib/nguCanhTroLy";

interface ContextViewProps {
  tab: DocumentTabItem;
  onUpdateContent: (content: string) => void;
  patientSubtitle?: string;
}

export const ContextView: React.FC<ContextViewProps> = ({ tab, onUpdateContent, patientSubtitle }) => {
  const [saved, setSaved] = React.useState(false);
  const [ocrInput, setOcrInput] = React.useState("");
  const [dangQuet, setDangQuet] = React.useState(false);
  const [anhPhieuCu, setAnhPhieuCu] = React.useState<{ url: string; ten: string } | null>(null);
  const [thongBaoAnh, setThongBaoAnh] = React.useState<string | null>(null);
  const oChonAnh = React.useRef<HTMLInputElement>(null);

  const xuLyChonAnh = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (anhPhieuCu?.url) URL.revokeObjectURL(anhPhieuCu.url);
    const url = URL.createObjectURL(file);
    setAnhPhieuCu({ url, ten: file.name });
    setThongBaoAnh(null);

    try {
      const TD = (window as any).TextDetector;
      if (TD) {
        const bitmap = await createImageBitmap(file);
        const detector = new TD();
        const blocks = await detector.detect(bitmap);
        const extracted = (blocks || []).map((b: any) => b.rawValue).filter(Boolean).join("\n");
        if (extracted.trim()) {
          setOcrInput((prev) => (prev.trim() ? `${prev.trim()}\n${extracted}` : extracted));
          setThongBaoAnh("Đã trích chữ cục bộ từ ảnh phiếu. Kiểm tra lại rồi bấm Phân tích chỉ số & thuốc.");
          return;
        }
      }
      setThongBaoAnh("Đã tải ảnh phiếu lên trình duyệt (cục bộ). Trình duyệt chưa hỗ trợ OCR ảnh tự động — vui lòng gõ hoặc dán chỉ số bên dưới để phân tích.");
    } catch {
      setThongBaoAnh("Đã đính kèm ảnh phiếu cục bộ. Nhập nhanh chỉ số thấy trên ảnh vào ô bên dưới để hệ thống tính eGFR.");
    } finally {
      e.target.value = "";
    }
  };
  const [ketQuaOcr, setKetQuaOcr] = React.useState<{
    chi_so?: Record<string, number>;
    thuoc_nhan_dien?: string[];
    hieu_chinh_lieu?: {
      chuc_nang_than?: { egfr_ckd_epi?: number; phan_do?: { phan_do?: string } };
      canh_bao_hieu_chinh_than?: Array<{ thuoc?: string; muc_do?: string; khuyen_cao?: string }>;
      canh_bao_hieu_chinh_gan?: Array<{ thuoc?: string; muc_do?: string; khuyen_cao?: string }>;
    };
  } | null>(null);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const quetPhieuCu = async () => {
    if (!ocrInput.trim()) return;
    setDangQuet(true);
    try {
      const nc = trichNguCanhChoTroLy({ patientSubtitle, contextNotes: tab.content });
      const r = await fetch("/api/ocr/phieu-cu", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: ocrInput,
          tuoi: nc.tuoi ?? 50,
          laNu: nc.gioi === "nữ",
        }),
      });
      if (r.ok) {
        setKetQuaOcr(await r.json());
      }
    } finally {
      setDangQuet(false);
    }
  };

  const chenVaoNguCanh = () => {
    if (!ketQuaOcr) return;
    const cs = ketQuaOcr.chi_so || {};
    const phanChiSo = Object.entries(cs)
      .map(([k, v]) => `${k}: ${v}`)
      .join(", ");
    const phanThuoc = (ketQuaOcr.thuoc_nhan_dien || []).join(", ");
    const dongMoi = [
      phanChiSo && `[Xét nghiệm cũ] ${phanChiSo}`,
      phanThuoc && `[Đơn thuốc cũ] ${phanThuoc}`,
    ]
      .filter(Boolean)
      .join("\n");
    if (dongMoi) {
      onUpdateContent(tab.content.trim() ? `${tab.content.trimEnd()}\n${dongMoi}` : dongMoi);
    }
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
          className="w-full h-56 p-4 rounded-xl border border-[#BAE6FD] bg-[#F0F7FA]/50 text-sm text-[#0F172A] placeholder-[#94A3B8] focus:outline-none focus:border-[#0284C7] focus:ring-2 focus:ring-[#BAE6FD]/50 leading-relaxed resize-none font-sans shadow-tactile-inset"
        />

        {/* Bộ bóc tách Phiếu XN / Đơn thuốc cũ nối thẳng hieu_chinh_lieu.py */}
        <div className="mt-6 pt-5 border-t border-[#CCE3F0] space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <ScanText size={16} className="text-[#0284C7]" />
              <span className="text-sm font-bold text-[#0F172A]">
                Bóc tách Phiếu Xét nghiệm / Đơn thuốc cũ (eGFR & Hiệu chỉnh liều)
              </span>
            </div>
            <div className="flex items-center gap-2">
              <input
                ref={oChonAnh}
                type="file"
                accept="image/*"
                onChange={xuLyChonAnh}
                className="hidden"
                aria-label="Tải ảnh phiếu xét nghiệm hoặc đơn thuốc cũ"
              />
              <button
                type="button"
                onClick={() => oChonAnh.current?.click()}
                className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl border border-[#BAE6FD] bg-white hover:bg-[#F0F9FF] text-[#0C4A6E] text-xs font-semibold transition-all shadow-tactile-doctor-pill cursor-pointer"
              >
                <ImagePlus size={14} className="text-[#0284C7]" />
                <span>Tải ảnh phiếu XN/đơn cũ</span>
              </button>
              <button
                type="button"
                disabled={dangQuet || !ocrInput.trim()}
                onClick={quetPhieuCu}
                className="px-4 py-2 rounded-xl bg-[#0284C7] hover:bg-[#0369A1] disabled:opacity-40 text-white text-xs font-semibold transition-all shadow-tactile-doctor active:translate-y-0.5 cursor-pointer"
              >
                {dangQuet ? "Đang phân tích..." : "Phân tích chỉ số & thuốc"}
              </button>
            </div>
          </div>
          {anhPhieuCu && (
            <div className="flex items-start gap-3 p-3 rounded-xl border border-[#BAE6FD] bg-[#F0F9FF]/60">
              <img
                src={anhPhieuCu.url}
                alt={anhPhieuCu.ten}
                className="w-20 h-20 object-cover rounded-lg border border-[#BAE6FD] flex-shrink-0"
              />
              <div className="flex-1 min-w-0 text-xs">
                <div className="font-semibold text-[#0F172A] truncate">{anhPhieuCu.ten}</div>
                {thongBaoAnh && <p className="text-[#475569] mt-1 leading-relaxed">{thongBaoAnh}</p>}
              </div>
              <button
                type="button"
                onClick={() => {
                  URL.revokeObjectURL(anhPhieuCu.url);
                  setAnhPhieuCu(null);
                  setThongBaoAnh(null);
                }}
                className="p-1 rounded-lg text-[#64748B] hover:bg-white hover:text-[#0F172A]"
                title="Xóa ảnh"
              >
                <X size={14} />
              </button>
            </div>
          )}
          <textarea
            value={ocrInput}
            onChange={(e) => setOcrInput(e.target.value)}
            placeholder="Dán nội dung OCR phiếu XN hoặc đơn thuốc cũ (ví dụ: Creatinin 165 umol/L, HbA1c 7.8%, Metformin 850mg, Allopurinol 300mg)..."
            className="w-full h-24 p-3.5 rounded-xl border border-[#BAE6FD] bg-[#F0F7FA]/50 text-xs text-[#0F172A] placeholder-[#94A3B8] focus:outline-none focus:border-[#0284C7] focus:ring-2 focus:ring-[#BAE6FD]/50 resize-none font-sans shadow-tactile-inset"
          />

          {ketQuaOcr && (
            <div className="rounded-xl border border-[#BAE6FD] bg-[#F0F9FF] p-3.5 text-xs space-y-2 shadow-tactile-doctor-pill">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="font-semibold text-[#0369A1]">
                  Chỉ số nhận diện:{" "}
                  {Object.entries(ketQuaOcr.chi_so || {}).length > 0
                    ? Object.entries(ketQuaOcr.chi_so || {})
                        .map(([k, v]) => `${k}=${v}`)
                        .join(" · ")
                    : "(Chưa thấy chỉ số sinh hóa)"}
                </div>
                <button
                  type="button"
                  onClick={chenVaoNguCanh}
                  className="inline-flex items-center gap-1 px-3 py-1 rounded-xl bg-white border border-[#BAE6FD] text-[#0C4A6E] font-semibold hover:bg-[#F0F9FF] shadow-tactile-doctor-pill cursor-pointer"
                >
                  <Plus size={12} className="text-[#0284C7]" /> Chèn vào Ngữ cảnh
                </button>
              </div>
              {ketQuaOcr.thuoc_nhan_dien && ketQuaOcr.thuoc_nhan_dien.length > 0 && (
                <div className="text-[#0F172A]">
                  <strong>Thuốc đơn cũ:</strong> {ketQuaOcr.thuoc_nhan_dien.join(", ")}
                </div>
              )}
              {(() => {
                const cbs = [
                  ...(ketQuaOcr.hieu_chinh_lieu?.canh_bao_hieu_chinh_than || []),
                  ...(ketQuaOcr.hieu_chinh_lieu?.canh_bao_hieu_chinh_gan || []),
                ];
                if (cbs.length === 0) return null;
                return (
                  <div className="space-y-1.5">
                    {cbs.map((cb, idx) => (
                      <div key={idx} className="flex items-start gap-2 rounded-xl border border-[#F5C2C2] bg-[#FFF5F5] p-2.5 text-[#B4232C]">
                        <AlertTriangle size={13} className="mt-0.5 flex-shrink-0" />
                        <span>
                          <strong>{cb.thuoc}:</strong> {cb.khuyen_cao}
                        </span>
                      </div>
                    ))}
                  </div>
                );
              })()}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
