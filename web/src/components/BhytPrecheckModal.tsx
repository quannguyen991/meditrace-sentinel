import React, { useState } from "react";
import {
  AlertTriangle,
  Check,
  CheckCircle2,
  Copy,
  Download,
  FileCode,
  Plus,
  ShieldAlert,
} from "lucide-react";
import type { PyBhytPrecheckResponse } from "../types/api-contract";

export interface MucBienLuanCls {
  dich_vu?: string;
  ten_cls?: string;
  ten_dich_vu?: string;
  ma_cls?: string;
  ma_dvkt?: string;
  hop_le?: boolean;
  dat_yeu_cau?: boolean;
  trang_thai?: string;
  cau_bien_luan?: string;
  bien_luan?: string;
  goi_y_bo_sung?: string;
  ly_do?: string;
  canh_bao?: string;
  luot?: number[];
  luot_can_cu?: number[];
  bang_chung?: number[];
  trich_dan?: string;
  [key: string]: unknown;
}

export interface BhytPrecheckResult extends Omit<Partial<PyBhytPrecheckResponse>, "ma_icd10_chinh" | "icd10_chi_tiet" | "canh_bao_xuat_toan"> {
  ma_icd10_chinh?: string | { ma_icd10?: string; ten_benh_byt?: string; chuyen_khoa?: string } | null;
  icd10_chi_tiet?: Array<{ ma: string; ten: string; khoa: string; trich_dan?: string }>;
  canh_bao_xuat_toan?: Array<{ thuoc: string; ly_do: string; muc_do?: string }>;
  canh_bao_xuat_toan_bhyt?: string[];
  bien_luan_chi_dinh_cls?: MucBienLuanCls[];
  canh_bao_lieu_nhi_khoa?: Array<string | { thuoc?: string; canh_bao?: string; ly_do?: string; muc_do?: string }>;
  canh_bao_da_thuoc_dong_tay_y?: Array<string | { thuoc?: string; canh_bao?: string; ly_do?: string }>;
  goi_xml_1_5?: Record<string, unknown>;
  trang_thai?: string;
}

interface BhytPrecheckModalProps {
  open: boolean;
  loading: boolean;
  result: BhytPrecheckResult | null;
  onClose: () => void;
  onInsertJustification?: (cauBienLuan: string) => void;
}

/**
 * Đóng gói từ điển `goi_xml_1_5` (`XML1`..`XML5`) thành một tệp `.xml` đa phần tử hợp lệ
 * theo cấu trúc bao bì giám định chuẩn Quyết định 130/QĐ-BYT & 4750/QĐ-BYT.
 */
export function dongGoiXml15ThanhTepXml(
  goiXml15: Record<string, unknown> | null | undefined,
  maLk = "MEDITRACE_LK",
): string {
  const goi = goiXml15 || {};
  const cacPhan = ["XML1", "XML2", "XML3", "XML4", "XML5"];
  const ngayLap = new Date().toISOString().replace(/[-:T]/g, "").slice(0, 12);
  const maAnToan = String(maLk || "MEDITRACE_LK").replace(/[<>&"']/g, "_");

  const dsFileXml = cacPhan
    .filter((loai) => typeof goi[loai] === "string" && String(goi[loai]).trim().length > 0)
    .map((loai) => {
      const noiDungSach = String(goi[loai])
        .replace(/^\s*<\?xml[^>]*\?>\s*/i, "")
        .trim()
        .split("\n")
        .map((dong) => `          ${dong}`)
        .join("\n");
      return `        <FILEHOSO loai="${loai}">\n${noiDungSach}\n        </FILEHOSO>`;
    });

  return [
    '<?xml version="1.0" encoding="utf-8"?>',
    `<GIAMDINHHS chuan="${String(goi.chuan || "QD_130_4750_QD_BYT").replace(/[<>&"']/g, "")}">`,
    "  <THONGTINHOSO>",
    `    <NGAYLAP>${ngayLap}</NGAYLAP>`,
    "    <SOLUONGHOSO>1</SOLUONGHOSO>",
    "    <DANHSACHHOSO>",
    `      <HOSO ma_lk="${maAnToan}">`,
    ...(dsFileXml.length > 0 ? dsFileXml : ['        <FILEHOSO loai="XML1"><TONG_HOP /></FILEHOSO>']),
    "      </HOSO>",
    "    </DANHSACHHOSO>",
    "  </THONGTINHOSO>",
    "</GIAMDINHHS>",
  ].join("\n");
}

function chuanHoaChuoiCanhBao(muc: unknown): string {
  if (typeof muc === "string") return muc;
  if (muc && typeof muc === "object") {
    const o = muc as Record<string, unknown>;
    const thuoc = o.thuoc ? `${String(o.thuoc)}: ` : "";
    return `${thuoc}${String(o.canh_bao || o.ly_do || o.thong_diep || JSON.stringify(o))}`;
  }
  return String(muc ?? "");
}

export const BhytPrecheckModal: React.FC<BhytPrecheckModalProps> = ({
  open,
  loading,
  result,
  onClose,
  onInsertJustification,
}) => {
  const [daChepIdx, setDaChepIdx] = useState<number | null>(null);
  const [daChenIdx, setDaChenIdx] = useState<number | null>(null);

  if (!open) return null;

  const dsIcd = result?.icd10_chi_tiet || [];
  const dsXuatToan =
    result?.canh_bao_xuat_toan && result.canh_bao_xuat_toan.length > 0
      ? result.canh_bao_xuat_toan
      : (result?.canh_bao_xuat_toan_bhyt || []).map((ly_do) => ({ thuoc: "BHYT", ly_do }));
  const dsBienLuanCls: MucBienLuanCls[] = Array.isArray(result?.bien_luan_chi_dinh_cls)
    ? result!.bien_luan_chi_dinh_cls!
    : [];
  const dsNhiKhoa = (result?.canh_bao_lieu_nhi_khoa || []).map(chuanHoaChuoiCanhBao).filter(Boolean);
  const dsDongTayY = (result?.canh_bao_da_thuoc_dong_tay_y || []).map(chuanHoaChuoiCanhBao).filter(Boolean);
  const coGoiXml = Boolean(
    result?.goi_xml_1_5 &&
      ["XML1", "XML2", "XML3", "XML4", "XML5"].some((k) => typeof result.goi_xml_1_5?.[k] === "string"),
  );

  const taiGoiXml15 = () => {
    if (!result?.goi_xml_1_5) return;
    const xmlContent = dongGoiXml15ThanhTepXml(result.goi_xml_1_5, "MEDITRACE_QD130");
    const blob = new Blob([xmlContent], { type: "application/xml;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `MediTrace_BHYT_XML1_XML5_QD130_${new Date().toISOString().slice(0, 10)}.xml`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-2xs p-4 no-print animate-in fade-in duration-150"
      onClick={onClose}
    >
      <div
        role="dialog"
        aria-label="Tiền kiểm BHYT QĐ 130/4750"
        onClick={(e) => e.stopPropagation()}
        className="w-full max-w-2xl rounded-2xl bg-white border border-[#BAE6FD] shadow-2xl overflow-hidden text-left flex flex-col max-h-[86vh]"
      >
        {/* Đầu modal */}
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-slate-100 bg-white flex-shrink-0">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-[#FEF9E7] border border-[#F5E6B8] text-[#7A4B00] flex items-center justify-center flex-shrink-0">
              <ShieldAlert size={16} />
            </div>
            <div>
              <h3 className="font-serif text-[17px] font-semibold text-[#0F172A]">
                Tiền kiểm Mã ICD-10 & Chống Xuất toán BHYT (QĐ 130/4750)
              </h3>
              <p className="text-[11px] text-[#64748B]">
                Đối soát chéo XML1 (Chẩn đoán) ↔ XML2 (Thuốc) ↔ XML3/XML4 (CLS) ↔ XML5 (Diễn biến) & Liều Nhi TT 26/2025
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="px-3 py-1 rounded-xl bg-slate-100 hover:bg-slate-200 text-xs font-semibold text-slate-700 cursor-pointer"
          >
            Đóng
          </button>
        </div>

        {/* Thân modal */}
        <div className="p-5 overflow-y-auto space-y-3.5 text-xs bg-[#F8FBFC] flex-1">
          {loading && <p className="text-[#64748B] py-6 text-center">Đang chạy BHYTXmlPreChecker tại chỗ...</p>}

          {!loading && result && (
            <>
              {/* 1. Mã ICD-10 gợi ý (4 ký tự) */}
              <div className="rounded-xl border border-[#BAE6FD] bg-white p-3.5 space-y-2 shadow-tactile-doctor-card">
                <div className="flex items-center justify-between gap-2">
                  <span className="font-bold text-[#0369A1]">1. Mã ICD-10 gợi ý (4 ký tự — XML1)</span>
                  <span className="text-[10.5px] text-[#64748B]">Gợi ý tham khảo do bác sĩ chốt</span>
                </div>
                {dsIcd.length === 0 ? (
                  <p className="text-[#64748B]">Chưa nhận diện được mã ICD-10 đặc hiệu từ hội thoại.</p>
                ) : (
                  <ul className="space-y-1.5">
                    {dsIcd.map((m, idx) => (
                      <li key={`${m.ma}_${idx}`} className="bg-[#F0F7FA]/70 rounded-xl border border-[#CCE3F0] p-2.5">
                        <div className="flex items-center gap-1.5 flex-wrap">
                          <span className="font-mono font-bold text-[#0284C7] px-1.5 py-0.5 rounded bg-white border border-[#BAE6FD]">
                            {m.ma}
                          </span>
                          <span className="font-semibold text-[#0F172A]">{m.ten}</span>
                          {m.khoa && <span className="text-[10.5px] text-[#64748B]">({m.khoa})</span>}
                        </div>
                        {m.trich_dan && (
                          <p className="text-[11px] text-[#475569] mt-1 italic">Trích dẫn: “{m.trich_dan}”</p>
                        )}
                      </li>
                    ))}
                  </ul>
                )}
              </div>

              {/* 2. Cảnh báo xuất toán Thuốc <-> ICD-10 */}
              <div
                className={`rounded-xl border p-3.5 space-y-2 ${
                  dsXuatToan.length > 0 ? "border-[#F5C2C2] bg-[#FFF5F5]" : "border-[#CDEBDD] bg-[#F3FBF7]"
                }`}
              >
                <div className={`font-bold ${dsXuatToan.length > 0 ? "text-[#B4232C]" : "text-[#0D6B50]"}`}>
                  2. Đối soát Thuốc (XML2) ↔ Chẩn đoán ICD-10 (XML1)
                </div>
                {dsXuatToan.length === 0 ? (
                  <p className="text-[#0D6B50] font-semibold flex items-center gap-1.5">
                    <CheckCircle2 size={14} />
                    <span>Không phát hiện bất tương hợp thuốc — mã ICD-10.</span>
                  </p>
                ) : (
                  <ul className="space-y-1.5">
                    {dsXuatToan.map((cb, idx) => (
                      <li key={idx} className="text-[#B4232C] bg-white rounded-xl border border-[#F5C2C2] p-2.5">
                        <strong>{cb.thuoc}:</strong> {cb.ly_do}
                      </li>
                    ))}
                  </ul>
                )}
              </div>

              {/* 3. Lá chắn Biện luận Chỉ định Cận lâm sàng (XML3/XML4 <-> XML5) */}
              <div className="rounded-xl border border-[#BAE6FD] bg-white p-3.5 space-y-2.5 shadow-2xs">
                <div className="flex items-center justify-between gap-2 flex-wrap">
                  <span className="font-bold text-[#0369A1]">
                    3. Lá chắn Biện luận Chỉ định Cận lâm sàng (XML3/XML4 ↔ XML5)
                  </span>
                  <span className="text-[10.5px] font-semibold text-[#0284C7]">Chống xuất toán DVKT / CLS</span>
                </div>
                {dsBienLuanCls.length === 0 ? (
                  <p className="text-[#64748B]">
                    Chưa ghi nhận chỉ định cận lâm sàng / dịch vụ kỹ thuật cần kiểm tra chéo diễn biến XML5 trong ca này.
                  </p>
                ) : (
                  <div className="space-y-2">
                    {dsBienLuanCls.map((cls, idx) => {
                      const tenDv = cls.dich_vu || cls.ten_cls || cls.ten_dich_vu || `Chỉ định CLS #${idx + 1}`;
                      const hopLe =
                        cls.hop_le !== undefined
                          ? Boolean(cls.hop_le)
                          : cls.dat_yeu_cau !== undefined
                          ? Boolean(cls.dat_yeu_cau)
                          : cls.trang_thai
                          ? !/thieu|canh_bao|xuat_toan/i.test(cls.trang_thai)
                          : Boolean(cls.cau_bien_luan || cls.bien_luan) && !cls.canh_bao;
                      const luotList = cls.luot_can_cu || cls.luot || cls.bang_chung || [];
                      const nhanLuot = luotList.length > 0 ? `[T${luotList.join(", T")}]` : "";
                      const maDvkt = cls.ma_dvkt || cls.ma_cls;
                      const cauBienLuan =
                        cls.cau_bien_luan ||
                        cls.bien_luan ||
                        cls.goi_y_bo_sung ||
                        `${tenDv}: [cần bổ sung triệu chứng / diễn biến lâm sàng làm căn cứ chỉ định CLS]`;

                      return (
                        <div
                          key={idx}
                          className={`rounded-xl border p-3 space-y-2 ${
                            hopLe
                              ? "bg-[#F3FBF7] border-[#A7E3C9] text-[#0C2340]"
                              : "bg-[#FFF5F5] border-[#F5C2C2] text-[#7F1D1D]"
                          }`}
                        >
                          <div className="flex items-start justify-between gap-2 flex-wrap">
                            <div className="flex items-center gap-1.5 flex-wrap">
                              {hopLe ? (
                                <CheckCircle2 size={14} className="text-[#0D6B50] flex-shrink-0" />
                              ) : (
                                <AlertTriangle size={14} className="text-[#B4232C] flex-shrink-0" />
                              )}
                              <span className="font-bold text-[12.5px]">{tenDv}</span>
                              {maDvkt && (
                                <span className="font-mono text-[10.5px] px-1.5 py-0.5 rounded bg-white border border-slate-200 text-slate-600">
                                  {maDvkt}
                                </span>
                              )}
                              {nhanLuot && (
                                <span className="font-mono text-[10.5px] font-semibold px-1.5 py-0.5 rounded bg-[#E0F2FE] text-[#0284C7] border border-[#BAE6FD]">
                                  {nhanLuot}
                                </span>
                              )}
                            </div>
                            <span
                              className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                                hopLe ? "bg-[#D1F2E3] text-[#0D6B50]" : "bg-[#FEE2E2] text-[#B4232C]"
                              }`}
                            >
                              {hopLe ? "Đủ căn cứ XML5" : "Nguy cơ xuất toán CLS"}
                            </span>
                          </div>

                          {!hopLe && (cls.canh_bao || cls.ly_do) && (
                            <p className="text-[11.5px] text-[#B4232C] font-medium leading-snug">
                              {cls.canh_bao || cls.ly_do}
                            </p>
                          )}

                          <div className="rounded-lg bg-white border border-slate-200/80 p-2 text-[11.5px] text-[#0F172A] leading-relaxed">
                            <span className="font-semibold text-[#0369A1]">
                              {hopLe ? "Câu biện luận có căn cứ:" : "Gợi ý ghi chú diễn biến lâm sàng:"}{" "}
                            </span>
                            <span>{cauBienLuan}</span>
                          </div>

                          {cls.trich_dan && (
                            <p className="text-[11px] text-[#475569] italic">Trích dẫn gốc: “{cls.trich_dan}”</p>
                          )}

                          <div className="flex items-center gap-1.5 flex-wrap">
                            <button
                              type="button"
                              onClick={() => {
                                navigator.clipboard.writeText(cauBienLuan);
                                setDaChepIdx(idx);
                                setTimeout(() => setDaChepIdx((cur) => (cur === idx ? null : cur)), 2000);
                              }}
                              className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-white hover:bg-[#F0F9FF] border border-[#BAE6FD] text-[#0369A1] text-[11px] font-semibold cursor-pointer"
                            >
                              {daChepIdx === idx ? <Check size={12} /> : <Copy size={12} />}
                              <span>{daChepIdx === idx ? "Đã chép câu biện luận" : "Chép câu biện luận"}</span>
                            </button>

                            {onInsertJustification && (
                              <button
                                type="button"
                                onClick={() => {
                                  onInsertJustification(cauBienLuan);
                                  setDaChenIdx(idx);
                                  setTimeout(() => setDaChenIdx((cur) => (cur === idx ? null : cur)), 2000);
                                }}
                                className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-[#0284C7] hover:bg-[#0369A1] text-white text-[11px] font-semibold cursor-pointer"
                              >
                                {daChenIdx === idx ? <Check size={12} /> : <Plus size={12} />}
                                <span>{daChenIdx === idx ? "Đã chèn vào bệnh án ✓" : "Chèn vào bệnh án"}</span>
                              </button>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* 4. Cảnh báo Liều Nhi khoa & Bắt buộc Cân nặng TT 26/2025 + Đa thuốc Đông-Tây y */}
              <div
                className={`rounded-xl border p-3.5 space-y-2.5 ${
                  dsNhiKhoa.length > 0 || dsDongTayY.length > 0
                    ? "border-[#F5E6B8] bg-[#FEF9E7]"
                    : "border-[#E2ECF3] bg-white"
                }`}
              >
                <div className="font-bold text-[#7A4B00]">
                  4. An toàn Liều Nhi khoa (TT 26/2025/TT-BYT) & Đa thuốc Đông-Tây y
                </div>

                {dsNhiKhoa.length === 0 && dsDongTayY.length === 0 ? (
                  <p className="text-[#0D6B50] font-semibold flex items-center gap-1.5">
                    <CheckCircle2 size={14} />
                    <span>Không phát hiện vượt trần liều mg/kg nhi khoa hoặc trùng hoạt chất Đông-Tây y.</span>
                  </p>
                ) : (
                  <div className="space-y-2">
                    {dsNhiKhoa.map((cb, idx) => (
                      <div
                        key={`nhi_${idx}`}
                        className="rounded-xl bg-[#FFF5F5] border border-[#F5C2C2] p-2.5 text-[#B4232C] flex items-start gap-2"
                      >
                        <AlertTriangle size={14} className="mt-0.5 flex-shrink-0" />
                        <span className="leading-snug font-medium">{cb}</span>
                      </div>
                    ))}
                    {dsDongTayY.map((cb, idx) => (
                      <div
                        key={`dty_${idx}`}
                        className="rounded-xl bg-white border border-[#F2DFA8] p-2.5 text-[#92400E] flex items-start gap-2"
                      >
                        <AlertTriangle size={14} className="mt-0.5 flex-shrink-0 text-[#D97706]" />
                        <span className="leading-snug font-medium">{cb}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </>
          )}
        </div>

        {/* Chân modal: Xuất gói XML1-XML5 QĐ 130/4750 */}
        <div className="px-5 py-3 border-t border-[#E2ECF3] bg-white flex flex-wrap items-center justify-between gap-2 flex-shrink-0">
          <div className="flex items-center gap-1.5 text-[11px] text-[#64748B]">
            <FileCode size={13} className="text-[#0284C7]" />
            <span>Chuẩn liên thông Cổng Giám định BHYT QĐ 130/2023 & QĐ 4750/QĐ-BYT</span>
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              disabled={!coGoiXml || loading}
              onClick={taiGoiXml15}
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-[#0284C7] hover:bg-[#0369A1] disabled:opacity-40 text-white text-xs font-semibold shadow-tactile-doctor transition-all cursor-pointer"
            >
              <Download size={13} />
              <span>Tải gói XML1–XML5 chuẩn QĐ 130/4750 (.xml)</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
