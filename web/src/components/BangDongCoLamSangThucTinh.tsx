import React, { useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  Check,
  ChevronDown,
  ChevronUp,
  HeartPulse,
  HelpCircle,
  Pill,
  Plus,
  ShieldAlert,
} from "lucide-react";
import { tinhDiemAcbThamKhao } from "./BangDoiSoatThuocVaDonQuocGiaModal";

export interface ThangDiemHoatDong {
  ma: string;
  ten: string;
  diemSo: number | string;
  phanTang: string;
  ghiChuThamKhao: string;
  tieuChi: string[];
}

interface BangDongCoLamSangThucTinhProps {
  clinicalSafety?: any;
  onOpenPolypharmacyModal?: () => void;
  onSelectSocratesChip?: (chipText: string, chuDe?: string) => void;
}

const TEN_9_THANG_DIEM: Record<string, string> = {
  curb65: "CURB-65",
  "curb-65": "CURB-65",
  cha2ds2_vasc: "CHA2DS2-VASc",
  "cha2ds2-vasc": "CHA2DS2-VASc",
  wells_pe: "Wells PE",
  "wells pe": "Wells PE",
  glasgow_blatchford: "Glasgow-Blatchford",
  "glasgow-blatchford": "Glasgow-Blatchford",
  qsofa: "qSOFA",
  gcs: "GCS",
  nyha: "NYHA",
  child_pugh: "Child-Pugh",
  "child-pugh": "Child-Pugh",
  bmi: "BMI",
};

/**
 * Trích xuất các thang điểm nguy cơ quốc tế đang hoạt động từ `clinicalSafety.thang_diem_nguy_co`
 * (hỗ trợ cả dạng từ điển khóa `CURB-65` / `curb65` lẫn mảng đối tượng).
 */
export function trichThangDiemHoatDong(thangDiemRaw: any): ThangDiemHoatDong[] {
  if (!thangDiemRaw || typeof thangDiemRaw !== "object") return [];
  const ketQua: ThangDiemHoatDong[] = [];

  const xuLyMuc = (khoa: string, val: any) => {
    if (!val || typeof val !== "object" || Array.isArray(val)) return;
    if (val.diem_so === undefined && val.score === undefined) return;
    const phanTang = String(val.phan_tang_nguy_co || val.risk_tier || "THAP").toUpperCase();
    if (phanTang === "KHONG_XAC_DINH") return;
    const khoaThap = khoa.toLowerCase();
    const tenChuan =
      val.ten_thang_diem ||
      TEN_9_THANG_DIEM[khoaThap] ||
      khoa;

    ketQua.push({
      ma: khoa,
      ten: String(tenChuan),
      diemSo: val.diem_so ?? val.score ?? 0,
      phanTang,
      ghiChuThamKhao: String(val.khuyen_cao_lam_sang || val.ghi_chu || ""),
      tieuChi: Array.isArray(val.chi_tiet_tieu_chi) ? val.chi_tiet_tieu_chi.map(String) : [],
    });
  };

  if (Array.isArray(thangDiemRaw)) {
    thangDiemRaw.forEach((v, idx) => xuLyMuc(`score_${idx}`, v));
  } else {
    for (const [k, v] of Object.entries(thangDiemRaw)) {
      if (k === "canh_bao_nguy_co_cao") continue;
      xuLyMuc(k, v);
    }
  }

  return ketQua;
}

function mauPhanTangThangDiem(phanTang: string): { badge: string; the: string; nhan: string } {
  const pt = phanTang.toUpperCase();
  if (pt.includes("NGUY_KICH") || pt.includes("CRITICAL")) {
    return {
      badge: "bg-red-600 text-white",
      the: "border-[#F5C2C2] bg-[#FFF5F5]",
      nhan: "Nguy kịch",
    };
  }
  if (pt.includes("CAO") || pt.includes("HIGH")) {
    return {
      badge: "bg-rose-100 text-rose-900 border border-rose-300",
      the: "border-rose-200 bg-rose-50/50",
      nhan: "Nguy cơ cao",
    };
  }
  if (pt.includes("TRUNG_BINH") || pt.includes("MODERATE")) {
    return {
      badge: "bg-amber-100 text-amber-900 border border-amber-300",
      the: "border-[#F5E6B8] bg-[#FEF9E7]",
      nhan: "Nguy cơ trung bình",
    };
  }
  return {
    badge: "bg-emerald-100 text-emerald-800 border border-emerald-200",
    the: "border-[#BAE6FD] bg-white",
    nhan: "Nguy cơ thấp",
  };
}

function mauChiSoXn(trangThai: string): string {
  const tt = (trangThai || "").toUpperCase();
  if (tt === "NGUY_KICH") return "bg-red-600 text-white border-red-700 font-bold";
  if (tt === "TANG_CAO") return "bg-[#FFF5F5] text-[#B4232C] border-[#F5C2C2] font-semibold";
  if (tt === "GIAM_THAP") return "bg-[#FEF9E7] text-[#92400E] border-[#F5E6B8] font-semibold";
  return "bg-[#F3FBF7] text-[#0D6B50] border-[#CDEBDD]";
}

export const BangDongCoLamSangThucTinh: React.FC<BangDongCoLamSangThucTinhProps> = ({
  clinicalSafety,
  onOpenPolypharmacyModal,
  onSelectSocratesChip,
}) => {
  const [thuGon, setThuGon] = useState(true);
  const [moChiTietXn, setMoChiTietXn] = useState(false);
  const [diemDangMo, setDiemDangMo] = useState<string | null>(null);
  const [chipDaXacNhan, setChipDaXacNhan] = useState<Record<string, boolean>>({});

  const cls = clinicalSafety?.doi_soat_can_lam_sang;
  const hieuChinhLieu = clinicalSafety?.hieu_chinh_lieu;
  const duocLy = clinicalSafety?.duoc_ly_ddi;
  const socrates = clinicalSafety?.tro_ly_socrates;

  const dsChiSoXn: any[] = Array.isArray(cls?.danh_sach_chi_so) ? cls.danh_sach_chi_so : [];
  const baoDongDoCls: string[] = Array.isArray(cls?.bao_dong_do_khan_cap) ? cls.bao_dong_do_khan_cap : [];
  const coGiaTriNguyKich = Boolean(cls?.co_gia_tri_nguy_kich || baoDongDoCls.length > 0);
  const batTuongDongCls: string[] = Array.isArray(cls?.canh_bao_bat_tuong_dong) ? cls.canh_bao_bat_tuong_dong : [];

  const canhBaoThanGan: any[] = [
    ...(Array.isArray(hieuChinhLieu?.canh_bao_hieu_chinh_than) ? hieuChinhLieu.canh_bao_hieu_chinh_than : []),
    ...(Array.isArray(hieuChinhLieu?.canh_bao_hieu_chinh_gan) ? hieuChinhLieu.canh_bao_hieu_chinh_gan : []),
  ];

  const dsDdi: any[] = Array.isArray(duocLy?.canh_bao_ddi) ? duocLy.canh_bao_ddi : [];
  const dsTrungAtc: string[] = Array.isArray(duocLy?.trung_nhom_atc) ? duocLy.trung_nhom_atc : [];
  const dsChongChiDinh: string[] = Array.isArray(duocLy?.chong_chi_dinh_co_dia) ? duocLy.chong_chi_dinh_co_dia : [];
  const dsVuotLieu: string[] = Array.isArray(duocLy?.vuot_lieu_tran) ? duocLy.vuot_lieu_tran : [];
  const acbScore = useMemo(() => {
    const beAcb =
      duocLy?.ganh_nang_da_thuoc?.diem_acb ??
      duocLy?.ganh_nang_da_thuoc?.acb_score ??
      duocLy?.ganh_nang_da_thuoc?.ganh_nang_khang_cholinergic?.tong_diem;
    if (typeof beAcb === "number") return beAcb;
    const giaiTrinh: string[] = Array.isArray(duocLy?.giai_trinh_duoc_ly) ? duocLy.giai_trinh_duoc_ly : [];
    return tinhDiemAcbThamKhao(giaiTrinh).tongDiem;
  }, [duocLy]);

  const coCanhBaoDuocLy =
    dsDdi.length > 0 ||
    dsTrungAtc.length > 0 ||
    dsChongChiDinh.length > 0 ||
    dsVuotLieu.length > 0 ||
    Boolean(duocLy?.ganh_nang_da_thuoc?.polypharmacy) ||
    acbScore >= 3;

  const dsThangDiem = useMemo(
    () => trichThangDiemHoatDong(clinicalSafety?.thang_diem_nguy_co),
    [clinicalSafety?.thang_diem_nguy_co],
  );

  const dsGoiYSocrates: any[] = Array.isArray(socrates?.danh_sach_goi_y) ? socrates.danh_sach_goi_y : [];

  const coBatKyPhatHienNao =
    coGiaTriNguyKich ||
    dsChiSoXn.length > 0 ||
    canhBaoThanGan.length > 0 ||
    coCanhBaoDuocLy ||
    dsThangDiem.length > 0 ||
    dsGoiYSocrates.length > 0;

  if (!clinicalSafety || !coBatKyPhatHienNao) return null;

  return (
    <div className="max-w-3xl mx-auto mb-4 space-y-2.5 no-print print:hidden font-sans">
      {/* 1. BANNER ĐỎ KHẨN CẤP NẾU CÓ GIÁ TRỊ CẬN LÂM SÀNG NGUY KỊCH */}
      {coGiaTriNguyKich && (
        <div className="rounded-2xl border-2 border-red-500 bg-gradient-to-r from-[#FFF5F5] via-red-50 to-[#FFF5F5] p-3.5 shadow-sm text-red-950 flex items-start gap-3">
          <div className="p-1.5 rounded-xl bg-red-600 text-white flex-shrink-0 mt-0.5">
            <AlertTriangle size={16} />
          </div>
          <div className="flex-1 min-w-0 space-y-1">
            <div className="text-xs font-bold uppercase tracking-wider text-red-700">
              Báo động Giá trị Cận lâm sàng Nguy kịch (Panic / Critical Lab Values)
            </div>
            <ul className="space-y-0.5 text-[13px] font-semibold">
              {baoDongDoCls.map((msg, idx) => (
                <li key={idx}>• {msg}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* KHUNG ĐIỀU KHIỂN ĐỘNG CƠ LÂM SÀNG TỰ ĐỘNG */}
      <div className="rounded-2xl border border-[#BAE6FD] bg-white shadow-tactile-doctor-card overflow-hidden">
        <div className="px-4 py-2.5 bg-gradient-to-r from-[#F0F9FF] to-white border-b border-[#E2ECF3] flex flex-wrap items-center justify-between gap-2">
          <div className="flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center gap-1.5 text-xs font-bold text-[#0369A1]">
              <HeartPulse size={14} className="text-[#0284C7]" />
              <span>Trợ lý Cảnh giới Lâm sàng Tức thời</span>
            </span>

            {/* Pill bấm mở nhanh bảng DDI / Đa thuốc TT26 */}
            {coCanhBaoDuocLy && (
              <button
                type="button"
                onClick={onOpenPolypharmacyModal}
                className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-[#FFF5F5] hover:bg-red-100 border border-[#F5C2C2] text-[#B4232C] text-[11px] font-bold transition-colors cursor-pointer"
                title="Bấm để mở Bảng Đối soát Đa thuốc & Đơn thuốc Quốc gia TT 26/2025"
              >
                <Pill size={11} />
                <span>
                  {dsDdi.length > 0
                    ? `${dsDdi.length} tương tác DDI`
                    : acbScore >= 3
                    ? `ACB = ${acbScore}`
                    : "Đa thuốc / Trùng nhóm ATC"}
                </span>
                <ArrowRight size={11} />
              </button>
            )}

            {canhBaoThanGan.length > 0 && (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-[#FEF9E7] border border-[#F5E6B8] text-[#92400E] text-[11px] font-bold">
                <ShieldAlert size={11} />
                <span>{canhBaoThanGan.length} lưu ý chỉnh liều Thận/Gan</span>
              </span>
            )}
          </div>

          <button
            type="button"
            onClick={() => setThuGon((v) => !v)}
            className="inline-flex items-center gap-1 text-[11px] font-semibold text-[#0369A1] hover:text-[#0284C7] cursor-pointer"
          >
            <span>{thuGon ? "Mở rộng" : "Thu gọn"}</span>
            {thuGon ? <ChevronDown size={13} /> : <ChevronUp size={13} />}
          </button>
        </div>

        {!thuGon && (
          <div className="p-3.5 space-y-3 text-xs">
            {/* Chỉ số Cận lâm sàng & Hiệu chỉnh liều Thận/Gan */}
            {(dsChiSoXn.length > 0 || canhBaoThanGan.length > 0 || batTuongDongCls.length > 0) && (
              <div className="space-y-2">
                {dsChiSoXn.length > 0 && (
                  <div className="flex flex-wrap items-center gap-1.5">
                    <span className="text-[11px] font-bold text-[#475569] mr-1">Cận lâm sàng:</span>
                    {dsChiSoXn.map((cs, idx) => (
                      <button
                        key={`${cs.ma_xet_nghiem}_${idx}`}
                        type="button"
                        onClick={() => setMoChiTietXn((v) => !v)}
                        title={cs.y_nghia_lam_sang}
                        className={`px-2 py-0.5 rounded-lg border text-[11px] cursor-pointer ${mauChiSoXn(
                          cs.trang_thai,
                        )}`}
                      >
                        {cs.ma_xet_nghiem}: {cs.gia_tri} {cs.don_vi}
                      </button>
                    ))}
                  </div>
                )}

                {moChiTietXn && dsChiSoXn.length > 0 && (
                  <div className="rounded-xl bg-[#F8FBFC] border border-[#E2ECF3] p-2.5 space-y-1 text-[11.5px] text-[#334155]">
                    {dsChiSoXn.map((cs, idx) => (
                      <div key={idx}>
                        <strong>
                          {cs.ten_chi_so} ({cs.gia_tri} {cs.don_vi} · tham chiếu {cs.khoang_tham_chieu}):
                        </strong>{" "}
                        {cs.y_nghia_lam_sang}
                      </div>
                    ))}
                  </div>
                )}

                {batTuongDongCls.map((msg, idx) => (
                  <div
                    key={`btd_${idx}`}
                    className="rounded-xl bg-[#FEF9E7] border border-[#F5E6B8] px-3 py-2 text-[#7A4B00] text-[11.5px]"
                  >
                    <strong>Đối soát Lâm sàng ↔ CLS:</strong> {msg}
                  </div>
                ))}

                {canhBaoThanGan.map((cb, idx) => (
                  <div
                    key={`tg_${idx}`}
                    className={`rounded-xl border px-3 py-2 text-[11.5px] ${
                      cb.muc_do === "CRITICAL"
                        ? "bg-[#FFF5F5] border-[#F5C2C2] text-[#B4232C]"
                        : "bg-[#FEF9E7] border-[#F5E6B8] text-[#7A4B00]"
                    }`}
                  >
                    <strong>
                      [{cb.muc_do}] {cb.thuoc} ({cb.chi_so_danh_gia}):
                    </strong>{" "}
                    {cb.khuyen_cao} — <em>Gợi ý tham khảo: {cb.lieu_de_xuat}</em>
                  </div>
                ))}
              </div>
            )}

            {/* 9 Thang điểm Nguy cơ Quốc tế Tự động */}
            {dsThangDiem.length > 0 && (
              <div className="space-y-1.5">
                <div className="flex items-center gap-1.5 text-[11px] font-bold text-[#0C4A6E]">
                  <Activity size={13} className="text-[#0284C7]" />
                  <span>Thang điểm Phân tầng Nguy cơ Quốc tế (tham khảo, bác sĩ quyết định):</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {dsThangDiem.map((td) => {
                    const mau = mauPhanTangThangDiem(td.phanTang);
                    const dangMo = diemDangMo === td.ma;
                    return (
                      <div
                        key={td.ma}
                        className={`rounded-xl border px-3 py-2 transition-all ${mau.the} ${
                          dangMo ? "w-full" : "max-w-full"
                        }`}
                      >
                        <button
                          type="button"
                          onClick={() => setDiemDangMo(dangMo ? null : td.ma)}
                          className="flex items-center gap-2 text-left cursor-pointer w-full justify-between"
                        >
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="font-bold text-[#0F172A]">{td.ten}</span>
                            <span className={`px-2 py-0.5 rounded-full text-[10.5px] font-bold ${mau.badge}`}>
                              {td.diemSo} điểm · {mau.nhan}
                            </span>
                          </div>
                          {dangMo ? (
                            <ChevronUp size={13} className="text-slate-500" />
                          ) : (
                            <ChevronDown size={13} className="text-slate-500" />
                          )}
                        </button>

                        {dangMo && (
                          <div className="mt-2 pt-2 border-t border-slate-200/70 space-y-1.5 text-[11.5px] text-[#334155]">
                            {td.tieuChi.length > 0 && (
                              <ul className="list-disc pl-4 space-y-0.5">
                                {td.tieuChi.map((tc, i) => (
                                  <li key={i}>{tc}</li>
                                ))}
                              </ul>
                            )}
                            {td.ghiChuThamKhao && (
                              <p className="text-[#0369A1] font-medium">
                                Lưu ý tham khảo lâm sàng (không thay thế quyết định bác sĩ): {td.ghiChuThamKhao}
                              </p>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Chip Hỏi & Xác nhận Nhanh SOCRATES (Pertinent Negatives / Cái lắc đầu tại bàn khám) */}
            {dsGoiYSocrates.length > 0 && (
              <div className="rounded-xl bg-[#F8FBFC] border border-[#E2ECF3] p-3 space-y-2">
                <div className="flex items-center justify-between gap-2">
                  <span className="inline-flex items-center gap-1.5 text-[11.5px] font-bold text-[#0C4A6E]">
                    <HelpCircle size={13} className="text-[#0284C7]" />
                    <span>Gợi ý hỏi bổ sung SOCRATES & Xác nhận 1 chạm tại bàn khám</span>
                  </span>
                  <span className="text-[10.5px] text-[#64748B]">
                    Bấm chip để ghi nhận trả lời / lắc đầu của người bệnh kèm nhãn nguồn rõ ràng
                  </span>
                </div>

                <div className="space-y-2">
                  {dsGoiYSocrates.map((gy, idx) => {
                    const luaChon: string[] = Array.isArray(gy.cac_lua_chon) ? gy.cac_lua_chon : [];
                    return (
                      <div key={gy.ma_goi_y || idx} className="space-y-1">
                        <div className="text-[11.5px] text-[#334155]">
                          <strong className="text-[#0369A1]">[{gy.chu_de || "BỆNH SỬ"}]</strong>{" "}
                          {gy.cau_hoi_goi_y || gy.khoang_trong}
                        </div>
                        {luaChon.length > 0 && (
                          <div className="flex flex-wrap gap-1.5">
                            {luaChon.map((chip) => {
                              const khoaChip = `${gy.ma_goi_y || idx}::${chip}`;
                              const daChon = Boolean(chipDaXacNhan[khoaChip]);
                              return (
                                <button
                                  key={chip}
                                  type="button"
                                  disabled={daChon}
                                  onClick={() => {
                                    setChipDaXacNhan((cu) => ({ ...cu, [khoaChip]: true }));
                                    onSelectSocratesChip?.(chip, gy.chu_de);
                                  }}
                                  className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-semibold border transition-all ${
                                    daChon
                                      ? "bg-[#D1F2E3] border-[#A7E3C9] text-[#0D6B50] cursor-default"
                                      : "bg-white hover:bg-[#E0F2FE] border-[#BAE6FD] text-[#0369A1] cursor-pointer shadow-2xs"
                                  }`}
                                >
                                  {daChon ? <Check size={11} /> : <Plus size={11} />}
                                  <span>{chip}</span>
                                </button>
                              );
                            })}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
