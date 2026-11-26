import React, { useCallback, useEffect, useState } from "react";
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  FileCode,
  FileSearch,
  Pill,
  RefreshCw,
  ShieldAlert,
  ShieldCheck,
  Upload,
} from "lucide-react";

export interface KetQuaKiemToanXml {
  hop_le: boolean;
  tong_tien_de_nghi: number;
  tong_nguy_co_xuat_toan: number;
  loi_cau_truc: Array<{
    loai?: string;
    ma_loi?: string;
    truong?: string;
    ly_do: string;
    chenh_lech?: number;
  }>;
  vi_pham_tt20: Array<{
    loai?: string;
    nhom?: string;
    ten?: string;
    ma?: string;
    nguy_co_xuat_toan?: number;
    ly_do: string;
  }>;
  thieu_bang_chung_k1_k7: Array<{
    loai?: string;
    ten?: string;
    ma?: string;
    nguy_co_xuat_toan?: number;
    ly_do: string;
  }>;
  tom_tat_theo_nhom?: Record<string, number>;
}

export interface TongQuanQuanTriBv {
  phamVi: "toan_vien" | "ca_nhan";
  tongCaKham: number;
  tongCaDaKyWorm: number;
  tyLeHoanThienHoSo: number;
  tongNguyCoXuatToanVnd: number;
  soCanhBaoDdiVaDiUng: number;
  tyLeKhangSinhAWaRe: {
    access: number;
    watch: number;
    reserve: number;
    tongKhangSinh: number;
    tyLeAccessPct: number;
    tyLeWatchPct: number;
    tyLeReservePct: number;
  };
  ketQuaKiemDinhWorm: {
    hopLe: boolean;
    soBanGhi: number;
    loi?: string;
  };
  theoBacSi: Array<{
    bacSiId: number;
    hoTen: string;
    tongCa: number;
    daKyWorm: number;
    nguyCoXuatToanVnd: number;
    soCanhBaoDdiVaDiUng: number;
  }>;
}

const dinhDangVnd = (so: number) =>
  `${new Intl.NumberFormat("vi-VN").format(Math.round(so || 0))} đ`;

const XML_MAU = {
  XML1: `<?xml version="1.0" encoding="utf-8"?>
<TONG_HOP>
  <MA_LK>LK_SAMPLE_2026</MA_LK>
  <MA_BN>BN_0099</MA_BN>
  <MA_THE>DN4790123456789</MA_THE>
  <MA_DKBD>79001</MA_DKBD>
  <MA_LOAI_KCB>1</MA_LOAI_KCB>
  <MA_BENH>I10</MA_BENH>
  <NGAY_VAO>202611260800</NGAY_VAO>
  <NGAY_RA>202611260930</NGAY_RA>
  <MA_BAC_SI>BS001</MA_BAC_SI>
  <T_TONGCHI>1950000</T_TONGCHI>
  <T_BHTT>1560000</T_BHTT>
  <T_BNTT>390000</T_BNTT>
  <T_BNCCT>0</T_BNCCT>
  <T_NGUONKHAC>0</T_NGUONKHAC>
</TONG_HOP>`,
  XML2: `<CHITIEU_CHITIET_THUOC><DSACH_CHI_TIET_THUOC>
  <CHI_TIET_THUOC>
    <STT>1</STT>
    <TEN_THUOC>Meropenem 1g</TEN_THUOC>
    <THANH_TIEN>450000</THANH_TIEN>
  </CHI_TIET_THUOC>
</DSACH_CHI_TIET_THUOC></CHITIEU_CHITIET_THUOC>`,
  XML3: `<CHITIEU_CHITIET_DVKT_VTYT><DSACH_CHI_TIET_DVKT>
  <CHI_TIET_DVKT>
    <STT>1</STT>
    <MA_DICH_VU>18.0010</MA_DICH_VU>
    <TEN_DICH_VU>Chụp MRI sọ não</TEN_DICH_VU>
    <THANH_TIEN>1500000</THANH_TIEN>
    <NGAY_YL>202611260830</NGAY_YL>
  </CHI_TIET_DVKT>
</DSACH_CHI_TIET_DVKT></CHITIEU_CHITIET_DVKT_VTYT>`,
  XML5: `<CHITIEU_CHITIET_DIEN_BIEN_BENH><DSACH_CHI_TIET_DIEN_BIEN_BENH>
  <CHI_TIET_DIEN_BIEN_BENH>
    <STT>1</STT>
    <DIEN_BIEN>Khám định kỳ tăng huyết áp.</DIEN_BIEN>
  </CHI_TIET_DIEN_BIEN_BENH>
</DSACH_CHI_TIET_DIEN_BIEN_BENH></CHITIEU_CHITIET_DIEN_BIEN_BENH>`,
};

export const HospitalCommandCenterView: React.FC = () => {
  const [tongQuan, setTongQuan] = useState<TongQuanQuanTriBv | null>(null);
  const [loadingKpi, setLoadingKpi] = useState(false);
  const [loiKpi, setLoiKpi] = useState<string | null>(null);

  const [xmlTab, setXmlTab] = useState<"XML1" | "XML2" | "XML3" | "XML5" | "GIAMDINHHS">("XML1");
  const [xmlInputs, setXmlInputs] = useState<Record<string, string>>({
    XML1: "",
    XML2: "",
    XML3: "",
    XML5: "",
    GIAMDINHHS: "",
  });
  const [dangKiemToan, setDangKiemToan] = useState(false);
  const [loiKiemToan, setLoiKiemToan] = useState<string | null>(null);
  const [ketQuaXml, setKetQuaXml] = useState<KetQuaKiemToanXml | null>(null);

  const taiTongQuan = useCallback(async () => {
    setLoadingKpi(true);
    setLoiKpi(null);
    try {
      const res = await fetch("/api/quan-tri-bv/tong-quan", { credentials: "include" });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.error || `Lỗi ${res.status}`);
      setTongQuan(data as TongQuanQuanTriBv);
    } catch (err: any) {
      setLoiKpi(err?.message || "Không tải được số liệu KHTH / QLCL.");
    } finally {
      setLoadingKpi(false);
    }
  }, []);

  useEffect(() => {
    void taiTongQuan();
  }, [taiTongQuan]);

  const chayKiemToanXml = async () => {
    setDangKiemToan(true);
    setLoiKiemToan(null);
    try {
      const xmlFiles: Record<string, string> = {};
      for (const [k, v] of Object.entries(xmlInputs)) {
        if (v.trim()) xmlFiles[k] = v.trim();
      }
      const res = await fetch("/api/quan-tri-bv/kiem-toan-xml", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ xml_files: xmlFiles }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.error || `Lỗi ${res.status}`);
      setKetQuaXml(data as KetQuaKiemToanXml);
    } catch (err: any) {
      setLoiKiemToan(err?.message || "Kiểm toán gói XML thất bại.");
    } finally {
      setDangKiemToan(false);
    }
  };

  const docTepXml = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      const text = typeof reader.result === "string" ? reader.result : "";
      if (text.includes("<GIAMDINHHS") || text.includes("<FILEHOSO")) {
        setXmlTab("GIAMDINHHS");
        setXmlInputs((prev) => ({ ...prev, GIAMDINHHS: text }));
      } else {
        setXmlInputs((prev) => ({ ...prev, [xmlTab]: text }));
      }
    };
    reader.readAsText(file, "utf-8");
    e.target.value = "";
  };

  const aware = tongQuan?.tyLeKhangSinhAWaRe;

  return (
    <div className="space-y-5 text-left">
      {/* Tiêu đề Command Center */}
      <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-[#BAE6FD] bg-white p-4 shadow-tactile-doctor-card">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-[#E0F2FE] border border-[#BAE6FD] text-[#0369A1] flex items-center justify-center">
            <Activity size={20} />
          </div>
          <div>
            <h2 className="font-serif text-lg font-semibold text-[#0F172A]">
              Trung tâm Điều hành KHTH / QLCL & Quản lý Kháng sinh
            </h2>
            <p className="text-xs text-[#64748B]">
              Giám sát rủi ro xuất toán BHYT (TT 20/2022 & QĐ 130), WHO AWaRe Stewardship và chuỗi kiểm toán WORM
            </p>
          </div>
        </div>
        <button
          type="button"
          onClick={() => void taiTongQuan()}
          disabled={loadingKpi}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#F0F9FF] hover:bg-[#E0F2FE] border border-[#BAE6FD] text-[#0369A1] text-xs font-semibold cursor-pointer disabled:opacity-50"
        >
          <RefreshCw size={13} className={loadingKpi ? "animate-spin" : ""} />
          <span>Làm mới số liệu</span>
        </button>
      </div>

      {loiKpi && (
        <div className="rounded-xl border border-[#F5C2C2] bg-[#FFF5F5] p-3 text-xs text-[#B4232C] flex items-center gap-2">
          <AlertTriangle size={14} />
          <span>{loiKpi}</span>
        </div>
      )}

      {/* 4 Thẻ KPI cốt lõi */}
      {tongQuan && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
          <div className="rounded-2xl border border-[#BAE6FD] bg-white p-4 space-y-1 shadow-2xs">
            <div className="text-[11px] font-semibold text-[#64748B]">Hồ sơ đã ký duyệt WORM</div>
            <div className="text-2xl font-bold text-[#0F172A]">
              {tongQuan.tongCaDaKyWorm} / {tongQuan.tongCaKham}
            </div>
            <div className="text-[11px] font-semibold text-[#0284C7]">
              Hoàn thiện {tongQuan.tyLeHoanThienHoSo}%
            </div>
          </div>

          <div className="rounded-2xl border border-[#F5C2C2] bg-[#FFF5F5] p-4 space-y-1 shadow-2xs">
            <div className="text-[11px] font-semibold text-[#991B1B]">Nguy cơ xuất toán BHYT ước tính</div>
            <div className="text-2xl font-bold text-[#B4232C]">
              {dinhDangVnd(tongQuan.tongNguyCoXuatToanVnd)}
            </div>
            <div className="text-[11px] text-[#7F1D1D]">Cần biện luận XML5 / đối chiếu ICD-10</div>
          </div>

          <div className="rounded-2xl border border-[#F5E6B8] bg-[#FEF9E7] p-4 space-y-1 shadow-2xs">
            <div className="text-[11px] font-semibold text-[#7A4B00]">Cảnh báo DDI & Dị ứng ngăn chặn</div>
            <div className="text-2xl font-bold text-[#92400E]">{tongQuan.soCanhBaoDdiVaDiUng}</div>
            <div className="text-[11px] text-[#7A4B00]">Near-miss an toàn người bệnh</div>
          </div>

          <div
            className={`rounded-2xl border p-4 space-y-1 shadow-2xs ${
              tongQuan.ketQuaKiemDinhWorm.hopLe
                ? "border-[#A7E3C9] bg-[#F3FBF7]"
                : "border-[#F5C2C2] bg-[#FFF5F5]"
            }`}
          >
            <div className="text-[11px] font-semibold text-[#64748B]">Chuỗi kiểm toán WORM (TT 46)</div>
            <div className="flex items-center gap-1.5 text-lg font-bold">
              {tongQuan.ketQuaKiemDinhWorm.hopLe ? (
                <>
                  <ShieldCheck size={18} className="text-[#0D6B50]" />
                  <span className="text-[#0D6B50]">Toàn vẹn 100%</span>
                </>
              ) : (
                <>
                  <ShieldAlert size={18} className="text-[#B4232C]" />
                  <span className="text-[#B4232C]">Phát hiện sai lệch</span>
                </>
              )}
            </div>
            <div className="text-[11px] text-[#475569]">
              {tongQuan.ketQuaKiemDinhWorm.soBanGhi} bản ghi niêm phong SHA-256
            </div>
          </div>
        </div>
      )}

      {/* Thanh WHO AWaRe Antibiotic Stewardship */}
      {aware && (
        <div className="rounded-2xl border border-[#BAE6FD] bg-white p-4 space-y-3 shadow-2xs">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <Pill size={16} className="text-[#0284C7]" />
              <span className="font-semibold text-sm text-[#0F172A]">
                Giám sát sử dụng Kháng sinh theo phân loại WHO AWaRe
              </span>
            </div>
            <span className="text-xs text-[#64748B]">Tổng lượt kháng sinh ghi nhận: {aware.tongKhangSinh}</span>
          </div>

          <div className="h-3 w-full rounded-full bg-slate-100 overflow-hidden flex">
            {aware.tongKhangSinh > 0 ? (
              <>
                <div
                  style={{ width: `${aware.tyLeAccessPct}%` }}
                  className="bg-emerald-500 h-full"
                  title={`Access: ${aware.access} (${aware.tyLeAccessPct}%)`}
                />
                <div
                  style={{ width: `${aware.tyLeWatchPct}%` }}
                  className="bg-amber-500 h-full"
                  title={`Watch: ${aware.watch} (${aware.tyLeWatchPct}%)`}
                />
                <div
                  style={{ width: `${aware.tyLeReservePct}%` }}
                  className="bg-rose-600 h-full"
                  title={`Reserve: ${aware.reserve} (${aware.tyLeReservePct}%)`}
                />
              </>
            ) : (
              <div className="w-full h-full bg-slate-200" />
            )}
          </div>

          <div className="flex flex-wrap gap-4 text-xs">
            <span className="inline-flex items-center gap-1.5 font-semibold text-emerald-700">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
              Access: {aware.access} ({aware.tyLeAccessPct}%)
            </span>
            <span className="inline-flex items-center gap-1.5 font-semibold text-amber-700">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-500" />
              Watch: {aware.watch} ({aware.tyLeWatchPct}%)
            </span>
            <span className="inline-flex items-center gap-1.5 font-semibold text-rose-700">
              <span className="w-2.5 h-2.5 rounded-full bg-rose-600" />
              Reserve: {aware.reserve} ({aware.tyLeReservePct}%)
            </span>
          </div>
        </div>
      )}

      {/* Bảng theo bác sĩ (ẩn danh PHI bệnh nhân) */}
      {tongQuan && tongQuan.theoBacSi.length > 0 && (
        <div className="rounded-2xl border border-[#BAE6FD] bg-white p-4 space-y-2.5 shadow-2xs overflow-x-auto">
          <div className="font-semibold text-sm text-[#0F172A]">
            Tổng hợp chất lượng hồ sơ theo Bác sĩ ({tongQuan.phamVi === "toan_vien" ? "Toàn viện" : "Cá nhân"})
          </div>
          <table className="w-full text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-200 text-[#64748B] text-left">
                <th className="py-2 pr-3">Bác sĩ</th>
                <th className="py-2 px-3">Số ca</th>
                <th className="py-2 px-3">Đã ký WORM</th>
                <th className="py-2 px-3">Nguy cơ xuất toán</th>
                <th className="py-2 pl-3">Cảnh báo DDI/Dị ứng</th>
              </tr>
            </thead>
            <tbody>
              {tongQuan.theoBacSi.map((bs) => (
                <tr key={bs.bacSiId} className="border-b border-slate-100 last:border-0">
                  <td className="py-2 pr-3 font-semibold text-[#0F172A]">{bs.hoTen}</td>
                  <td className="py-2 px-3">{bs.tongCa}</td>
                  <td className="py-2 px-3">{bs.daKyWorm}</td>
                  <td className="py-2 px-3 font-mono text-[#B4232C]">{dinhDangVnd(bs.nguyCoXuatToanVnd)}</td>
                  <td className="py-2 pl-3">{bs.soCanhBaoDdiVaDiUng}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Bộ kiểm toán gói XML1–XML5 đầu vào (QĐ 130/4210 & TT 20/2022) */}
      <div className="rounded-2xl border border-[#BAE6FD] bg-white p-4 space-y-3 shadow-tactile-doctor-card">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <FileSearch size={17} className="text-[#0284C7]" />
            <div>
              <h3 className="font-semibold text-sm text-[#0F172A]">
                Kiểm toán gói XML1–XML5 trước khi gửi BHXH (QĐ 130/4210 & TT 20/2022)
              </h3>
              <p className="text-[11px] text-[#64748B]">
                Dán nội dung từng bảng XML1/2/3/5 hoặc tải tệp XML gộp &lt;GIAMDINHHS&gt; để phát hiện nguy cơ xuất toán
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <label className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-xs font-semibold text-slate-700 cursor-pointer">
              <Upload size={13} />
              <span>Nạp tệp .xml</span>
              <input type="file" accept=".xml,text/xml,application/xml" onChange={docTepXml} className="hidden" />
            </label>
            <button
              type="button"
              onClick={() => setXmlInputs((prev) => ({ ...prev, ...XML_MAU }))}
              className="px-2.5 py-1.5 rounded-xl bg-[#F0F9FF] hover:bg-[#E0F2FE] border border-[#BAE6FD] text-[#0369A1] text-xs font-semibold cursor-pointer"
            >
              Nạp mẫu XML
            </button>
          </div>
        </div>

        <div className="flex flex-wrap gap-1.5">
          {(["XML1", "XML2", "XML3", "XML5", "GIAMDINHHS"] as const).map((tab) => (
            <button
              key={tab}
              type="button"
              onClick={() => setXmlTab(tab)}
              className={`px-3 py-1 rounded-lg text-xs font-semibold cursor-pointer transition-colors ${
                xmlTab === tab
                  ? "bg-[#0284C7] text-white"
                  : "bg-slate-100 text-slate-700 hover:bg-slate-200"
              }`}
            >
              {tab}
              {xmlInputs[tab]?.trim() ? " •" : ""}
            </button>
          ))}
        </div>

        <textarea
          value={xmlInputs[xmlTab] || ""}
          onChange={(e) => setXmlInputs((prev) => ({ ...prev, [xmlTab]: e.target.value }))}
          rows={6}
          placeholder={`Dán nội dung ${xmlTab} tại đây...`}
          className="w-full rounded-xl border border-slate-200 bg-[#F8FBFC] p-3 font-mono text-[11.5px] text-slate-800 focus:outline-none focus:border-[#0284C7]"
        />

        <div className="flex items-center justify-end">
          <button
            type="button"
            disabled={dangKiemToan}
            onClick={() => void chayKiemToanXml()}
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#0284C7] hover:bg-[#0369A1] disabled:opacity-50 text-white text-xs font-semibold cursor-pointer"
          >
            <FileCode size={14} />
            <span>{dangKiemToan ? "Đang kiểm toán..." : "Chạy kiểm toán QĐ 130 & TT 20/2022"}</span>
          </button>
        </div>

        {loiKiemToan && (
          <div className="rounded-xl border border-[#F5C2C2] bg-[#FFF5F5] p-3 text-xs text-[#B4232C]">
            {loiKiemToan}
          </div>
        )}

        {ketQuaXml && (
          <div className="space-y-3 pt-2 border-t border-slate-100 text-xs">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div className="flex items-center gap-2 font-bold">
                {ketQuaXml.hop_le ? (
                  <span className="inline-flex items-center gap-1.5 text-[#0D6B50]">
                    <CheckCircle2 size={15} /> Hồ sơ đạt chuẩn gửi Cổng Giám định BHYT
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1.5 text-[#B4232C]">
                    <AlertTriangle size={15} /> Phát hiện rủi ro xuất toán / sai cấu trúc
                  </span>
                )}
              </div>
              <div className="flex items-center gap-3 font-mono">
                <span>Đề nghị: <strong>{dinhDangVnd(ketQuaXml.tong_tien_de_nghi)}</strong></span>
                <span className="text-[#B4232C]">
                  Nguy cơ xuất toán: <strong>{dinhDangVnd(ketQuaXml.tong_nguy_co_xuat_toan)}</strong>
                </span>
              </div>
            </div>

            {ketQuaXml.loi_cau_truc.length > 0 && (
              <div className="rounded-xl border border-[#F5C2C2] bg-[#FFF5F5] p-3 space-y-1">
                <div className="font-bold text-[#B4232C]">Lỗi cấu trúc & tài chính QĐ 130/4210:</div>
                {ketQuaXml.loi_cau_truc.map((l, i) => (
                  <div key={i} className="text-[#7F1D1D]">• [{l.loai}/{l.truong}] {l.ly_do}</div>
                ))}
              </div>
            )}

            {ketQuaXml.vi_pham_tt20.length > 0 && (
              <div className="rounded-xl border border-[#F5E6B8] bg-[#FEF9E7] p-3 space-y-1">
                <div className="font-bold text-[#7A4B00]">Cảnh báo quy tắc TT 20/2022/TT-BYT:</div>
                {ketQuaXml.vi_pham_tt20.map((v, i) => (
                  <div key={i} className="text-[#92400E]">
                    • [{v.loai}] {v.ly_do}{" "}
                    {typeof v.nguy_co_xuat_toan === "number" && v.nguy_co_xuat_toan > 0
                      ? `(${dinhDangVnd(v.nguy_co_xuat_toan)})`
                      : ""}
                  </div>
                ))}
              </div>
            )}

            {ketQuaXml.thieu_bang_chung_k1_k7.length > 0 && (
              <div className="rounded-xl border border-[#BAE6FD] bg-[#F0F9FF] p-3 space-y-1">
                <div className="font-bold text-[#0369A1]">Thiếu chứng cứ lâm sàng K1–K7:</div>
                {ketQuaXml.thieu_bang_chung_k1_k7.map((t, i) => (
                  <div key={i} className="text-[#0C4A6E]">• [{t.loai}] {t.ly_do}</div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
