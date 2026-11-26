import React, { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  Check,
  CheckCircle2,
  Copy,
  FileHeart,
  Pill,
  Plus,
  ShieldAlert,
  Trash2,
  X,
} from "lucide-react";
import type { NoteMeta, Proposition, Quyet } from "./VerificationView";
import type { Thuoc } from "./ToDanDoBenhNhanModal";

export type QuyetDoiSoatThuocNha = "chua_chon" | "tiep_tuc" | "doi_lieu" | "tam_ngung";

export interface DongThuocTaiNha {
  id: string;
  tenThuoc: string;
  chiTietGoc: string;
  luot: number[];
  quyetDinh: QuyetDoiSoatThuocNha;
  ghiChuBacSi: string;
}

export interface DongDonThuocTt26 {
  id: string;
  hoatChatBietDuoc: string;
  hamLuong: string;
  sang: string;
  trua: string;
  chieu: string;
  toi: string;
  soNgay: string;
  tongSoLuong: string;
  duongDungLoiDan: string;
  canCuLuot: string;
}

interface BangDoiSoatThuocVaDonQuocGiaModalProps {
  open: boolean;
  onClose: () => void;
  patientName?: string;
  patientInfo?: Record<string, unknown>;
  transcript?: string;
  noteMeta?: NoteMeta | null;
  quyetDuyet?: Record<number, Quyet>;
  banSuaDuyet?: Record<number, string>;
  onInsertReconciliationToNote?: (summaryBlock: string) => void;
  onSyncToLeaflet?: (thuocDonMoi: Thuoc[]) => void;
}

const CAN_BO_SUNG = "[cần bổ sung]";

// Thang điểm kháng Cholinergic ACB (Anticholinergic Cognitive Burden) chuẩn lão khoa quốc tế (khớp cả chính tả Dược thư VN & INN quốc tế có -e)
const BANG_DIEM_ACB: Array<{ goc: RegExp; diem: 1 | 2 | 3; ten: string }> = [
  {
    goc: /\b(?:amitriptyline?|amitriptyline?|chlorpheniramine?|clorpheniramine?|promethazine?|diphenhydramine?|hydroxyzine?|atropine?|oxybutynine?|olanzapine?|quetiapine?)\b/i,
    diem: 3,
    ten: "ACB bậc 3 (Kháng cholinergic mạnh)",
  },
  {
    goc: /\b(?:carbamazepine?|oxcarbazepine?|cyclobenzaprine?|cyproheptadine?|loperamide?)\b/i,
    diem: 2,
    ten: "ACB bậc 2 (Kháng cholinergic vừa)",
  },
  {
    goc: /\b(?:cetirizine?|loratadine?|desloratadine?|fexofenadine?|furosemide?|lasix|digoxine?|nifedipine?|isosorbide?|warfarine?|codeine?|tramadol|prednisolone?|methylprednisolone?|ranitidine?|alprazolam|diazepam)\b/i,
    diem: 1,
    ten: "ACB bậc 1 (Kháng cholinergic nhẹ)",
  },
];

export function tinhDiemAcbThamKhao(danhSachChuoiThuoc: string[]): {
  tongDiem: number;
  chiTiet: Array<{ thuoc: string; diem: number }>;
} {
  const daTinh = new Set<string>();
  const chiTiet: Array<{ thuoc: string; diem: number }> = [];
  let tongDiem = 0;
  for (const chuoi of danhSachChuoiThuoc) {
    for (const muc of BANG_DIEM_ACB) {
      const m = chuoi.match(muc.goc);
      if (m) {
        const khoa = m[0].toLowerCase();
        if (!daTinh.has(khoa)) {
          daTinh.add(khoa);
          tongDiem += muc.diem;
          chiTiet.push({ thuoc: m[0], diem: muc.diem });
        }
      }
    }
  }
  return { tongDiem, chiTiet };
}

const RE_KHONG_PHAI_THUOC = /\b(?:tái khám|nghỉ ngơi|ăn nhạt|kiêng|theo dõi|nhập viện|chụp|siêu âm|xét nghiệm|nội soi|điện tim)\b/i;
const RE_DAU_HIEU_THUOC = /\b(?:\d+\s*(?:mg|mcg|g|ml|viên|ống|gói|nhát|giọt)|uống|tiêm|xịt|bôi|nhỏ|sáng|trưa|chiều|tối|ngày\s+\d+\s*lần)\b/i;

/**
 * Phân tích tất định một dòng y lệnh thành cấu trúc chuẩn Thông tư 26/2025/TT-BYT.
 * TUYỆT ĐỐI KHÔNG tự bịa hàm lượng, buổi uống, số ngày hay tổng số lượng nếu lời thoại chưa nêu rõ!
 */
export function phanTichDongDonTt26TuMenhDe(
  vanBan: string,
  tenThuocGoiY?: string | null,
  evidenceTurns: number[] = [],
  id = "1",
): DongDonThuocTt26 {
  const txt = (vanBan || "").trim();
  const mHamLuong = txt.match(/\b(\d+(?:[.,]\d+)?\s*(?:mg|mcg|g|ml|iu|ui)(?:\s*\/\s*\d+(?:[.,]\d+)?\s*(?:mg|ml))?)\b/i);
  const hamLuong = mHamLuong ? mHamLuong[1].trim() : CAN_BO_SUNG;

  // Tên hoạt chất / biệt dược: ưu tiên p.drug (bỏ phần liều nếu trùng), hoặc phần đầu câu trước hàm lượng/cách dùng
  let hoatChat = (tenThuocGoiY || "").trim();
  if (!hoatChat) {
    const catTruoc = txt.split(/\b(?:uống|tiêm|ngày|sáng|trưa|chiều|tối|lần|,|—|-)\b/i)[0]?.trim() || txt;
    hoatChat = catTruoc.replace(/\b\d+(?:[.,]\d+)?\s*(?:mg|mcg|g|ml)\b/gi, "").trim() || txt.slice(0, 45);
  }

  const timBuoi = (buoiRe: RegExp): string => {
    const m1 = txt.match(new RegExp(`${buoiRe.source}\\s*(\\d+(?:[.,/]\\d+)?\\s*(?:viên|gói|ống|ml|nhát|giọt)?)`, "i"));
    if (m1?.[1]) return m1[1].trim();
    const m2 = txt.match(new RegExp(`(\\d+(?:[.,/]\\d+)?\\s*(?:viên|gói|ống|ml))\\s*(?:vào\\s*)?${buoiRe.source}`, "i"));
    if (m2?.[1]) return m2[1].trim();
    return "—";
  };

  let sang = timBuoi(/\bbuổi\s+sáng|\bsáng\b/);
  let trua = timBuoi(/\bbuổi\s+trưa|\btrưa\b/);
  let chieu = timBuoi(/\bbuổi\s+chiều|\bchiều\b/);
  let toi = timBuoi(/\bbuổi\s+tối|\btối\b|\btrước\s+(?:khi\s+)?ngủ\b/);

  // Nếu cả 4 buổi đều chưa tách rõ, đánh dấu [cần bổ sung] ở cột Sáng để bác sĩ điền rõ (không đoán!)
  if (sang === "—" && trua === "—" && chieu === "—" && toi === "—") {
    sang = CAN_BO_SUNG;
  }

  const mSoNgay = txt.match(/\b(?:trong\s*)?(\d+)\s*ngày\b/i);
  const soNgay = mSoNgay ? `${mSoNgay[1]} ngày` : CAN_BO_SUNG;

  const mTongSl = txt.match(/\btổng\s*(?:cộng|số)?\s*(\d+\s*(?:viên|gói|ống|lọ|hộp|chai))\b/i);
  const tongSoLuong = mTongSl ? mTongSl[1].trim() : CAN_BO_SUNG;

  const duongParts: string[] = [];
  if (/\buống\b/i.test(txt)) duongParts.push("Đường uống");
  else if (/\btiêm\b/i.test(txt)) duongParts.push("Đường tiêm");
  else if (/\bxịt\b|\bhít\b/i.test(txt)) duongParts.push("Xịt / Hít");
  else if (/\bbôi\b/i.test(txt)) duongParts.push("Bôi ngoài da");

  if (/\btrước\s*(?:khi\s*)?ăn\b/i.test(txt)) duongParts.push("uống trước ăn 30 phút");
  else if (/\bsau\s*(?:khi\s*)?ăn\b/i.test(txt)) duongParts.push("uống sau ăn");
  else if (/\btrong\s*bữa\s*ăn\b|\bcùng\s*bữa\s*ăn\b/i.test(txt)) duongParts.push("uống ngay trong bữa ăn");

  const duongDungLoiDan = duongParts.length > 0 ? duongParts.join(" · ") : CAN_BO_SUNG;
  const canCuLuot = evidenceTurns.length > 0 ? `[T${evidenceTurns.join(", T")}]` : CAN_BO_SUNG;

  return {
    id,
    hoatChatBietDuoc: hoatChat || CAN_BO_SUNG,
    hamLuong,
    sang,
    trua,
    chieu,
    toi,
    soNgay,
    tongSoLuong,
    duongDungLoiDan,
    canCuLuot,
  };
}

/**
 * Tách rạch ròi Thuốc đang dùng ở nhà (Bảng 1) và Đơn thuốc kê mới (Bảng 2):
 * - Tuyệt đối KHÔNG trộn thuốc ở nhà chưa xác nhận vào đơn thuốc mới.
 * - Mệnh đề `can_xac_nhan` chỉ được đưa vào đơn mới khi bác sĩ đã bấm `"giu"` hoặc `"sua"`.
 */
export function tachThuocNhaVaDonMoi(
  propositions: Proposition[],
  quyetDuyet: Record<number, Quyet>,
  banSuaDuyet: Record<number, string>,
  doiSoatBackend?: any,
): { thuocNha: DongThuocTaiNha[]; donMoi: DongDonThuocTt26[] } {
  const thuocNha: DongThuocTaiNha[] = [];
  const donMoi: DongDonThuocTt26[] = [];
  const daCoNha = new Set<string>();
  const daCoMoi = new Set<string>();

  // 1. Ưu tiên nguồn đối soát từ backend nếu có (nhưng vẫn tôn trọng bác sĩ bấm "bo")
  const tapTextBiBo = new Set(
    (propositions || [])
      .filter((p) => quyetDuyet[p.id] === "bo")
      .flatMap((p) => [p.text?.trim().toLowerCase(), p.drug?.trim().toLowerCase()])
      .filter(Boolean) as string[],
  );

  const trichSoLuot = (rawBc: unknown): number[] => {
    if (!Array.isArray(rawBc)) return [];
    return rawBc
      .map((x) => {
        if (typeof x === "number") return x;
        const m = String(x).match(/\d+/);
        return m ? Number(m[0]) : NaN;
      })
      .filter((n) => Number.isFinite(n) && n > 0);
  };

  const dsNhaBackend = Array.isArray(doiSoatBackend?.thuoc_dang_dung_o_nha)
    ? doiSoatBackend.thuoc_dang_dung_o_nha
    : [];
  for (let i = 0; i < dsNhaBackend.length; i++) {
    const item = dsNhaBackend[i];
    const ten = String(item?.ten_thuoc || item?.ten || item?.noi_dung_goc || item?.noi_dung || "").trim();
    if (!ten) continue;
    const khoa = ten.toLowerCase();
    if (tapTextBiBo.has(khoa) || daCoNha.has(khoa)) continue;
    daCoNha.add(khoa);
    thuocNha.push({
      id: `be_home_${i}`,
      tenThuoc: item?.hoat_chat && item.hoat_chat !== CAN_BO_SUNG ? `${ten} (${item.hoat_chat})` : ten,
      chiTietGoc: String(item?.noi_dung_goc || item?.lieu || item?.lieu_dung || item?.chi_tiet || ten),
      luot: trichSoLuot(item?.luot || item?.bang_chung),
      quyetDinh: "chua_chon",
      ghiChuBacSi: "",
    });
  }

  // 2. Duyệt danh sách mệnh đề ca khám
  for (const p of propositions || []) {
    const q = quyetDuyet[p.id];
    if (q === "bo") continue;
    if (p.negated) continue;
    if (p.subject && !/bệnh nhân|người bệnh|tôi|mình|bé|cháu|trẻ/i.test(p.subject)) continue;

    const sec = (p.section || "").trim().toUpperCase();
    if (sec === "DỊ ỨNG" || sec === "TIỀN SỬ GIA ĐÌNH") continue;

    const vanBanHieuLuc = (q === "sua" && banSuaDuyet[p.id]?.trim() ? banSuaDuyet[p.id].trim() : p.text || "").trim();
    if (!vanBanHieuLuc) continue;
    if (/dị ứng|mẫn cảm|đã ngưng|đã ngừng/i.test(vanBanHieuLuc)) continue;

    const laThuocTaiNha =
      sec === "THUỐC ĐANG DÙNG" ||
      (sec === "CẦN XÁC NHẬN" &&
        (q === "giu" || q === "sua") &&
        /\b(?:đang uống|đang dùng|ở nhà|uống hàng ngày)\b/i.test(vanBanHieuLuc));

    if (laThuocTaiNha) {
      const ten = (p.drug || vanBanHieuLuc).trim();
      const khoa = ten.toLowerCase();
      if (!daCoNha.has(khoa)) {
        daCoNha.add(khoa);
        thuocNha.push({
          id: `prop_home_${p.id}`,
          tenThuoc: p.drug || vanBanHieuLuc,
          chiTietGoc: vanBanHieuLuc,
          luot: p.evidenceTurns || [],
          quyetDinh: "chua_chon",
          ghiChuBacSi: "",
        });
      }
      continue;
    }

    const daDuocBacSiXacNhanHoacThan = p.status === "than" || q === "giu" || q === "sua";
    const laMucDonMoi =
      sec === "KẾ HOẠCH ĐIỀU TRỊ" ||
      sec === "ĐƠN THUỐC" ||
      (sec === "CẦN XÁC NHẬN" &&
        (q === "giu" || q === "sua") &&
        (Boolean(p.drug) || RE_DAU_HIEU_THUOC.test(vanBanHieuLuc)));

    if (daDuocBacSiXacNhanHoacThan && laMucDonMoi) {
      const coThuoc = Boolean(p.drug) || (RE_DAU_HIEU_THUOC.test(vanBanHieuLuc) && !RE_KHONG_PHAI_THUOC.test(vanBanHieuLuc));
      if (!coThuoc) continue;
      const khoa = vanBanHieuLuc.toLowerCase();
      if (daCoMoi.has(khoa)) continue;
      daCoMoi.add(khoa);
      donMoi.push(phanTichDongDonTt26TuMenhDe(vanBanHieuLuc, p.drug, p.evidenceTurns || [], `rx_${p.id}`));
    }
  }

  // Bổ sung đơn thuốc mới từ backend (`don_thuoc_moi_tt26` hoặc `don_thuoc_moi`) nếu chưa có trong mệnh đề
  const dsMoiBackend = Array.isArray(doiSoatBackend?.don_thuoc_moi_tt26)
    ? doiSoatBackend.don_thuoc_moi_tt26
    : Array.isArray(doiSoatBackend?.don_thuoc_moi)
    ? doiSoatBackend.don_thuoc_moi
    : [];
  for (let i = 0; i < dsMoiBackend.length; i++) {
    const m = dsMoiBackend[i];
    const ten = String(m?.hoat_chat_biet_duoc || m?.ten_thuoc || m?.ten || "").trim();
    if (!ten || tapTextBiBo.has(ten.toLowerCase())) continue;
    const khoa = ten.toLowerCase();
    if ([...daCoMoi].some((x) => x.includes(khoa))) continue;
    daCoMoi.add(khoa);
    const luotBe = trichSoLuot(m?.luot || m?.bang_chung);
    const duongDanParts = [m?.duong_dung, m?.loi_dan_an_uong]
      .filter((x) => x && x !== CAN_BO_SUNG)
      .map(String);
    donMoi.push({
      id: `be_rx_${i}`,
      hoatChatBietDuoc:
        m?.hoat_chat && m.hoat_chat !== CAN_BO_SUNG && !ten.toLowerCase().includes(String(m.hoat_chat).toLowerCase())
          ? `${ten} (${m.hoat_chat})`
          : ten,
      hamLuong: String(m?.ham_luong || CAN_BO_SUNG),
      sang: m?.sang !== null && m?.sang !== undefined ? String(m.sang) : CAN_BO_SUNG,
      trua: m?.trua !== null && m?.trua !== undefined ? String(m.trua) : "—",
      chieu: m?.chieu !== null && m?.chieu !== undefined ? String(m.chieu) : "—",
      toi: m?.toi !== null && m?.toi !== undefined ? String(m.toi) : "—",
      soNgay: m?.so_ngay ? `${m.so_ngay} ngày`.replace(/ngày\s+ngày/i, "ngày") : CAN_BO_SUNG,
      tongSoLuong: m?.tong_so_luong ? String(m.tong_so_luong) : CAN_BO_SUNG,
      duongDungLoiDan:
        m?.duong_dung_loi_dan || (duongDanParts.length > 0 ? duongDanParts.join(" · ") : CAN_BO_SUNG),
      canCuLuot: luotBe.length > 0 ? `[T${luotBe.join(", T")}]` : CAN_BO_SUNG,
    });
  }

  return { thuocNha, donMoi };
}

export function phatHienTreDuoi72ThangThieuCanNang(
  patientInfo?: Record<string, unknown>,
  transcript = "",
  canNangNhapTay = "",
): { laTreDuoi72Thang: boolean; thieuCanNang: boolean; moTaTuoi: string } {
  if (canNangNhapTay.trim() && Number(canNangNhapTay.replace(",", ".")) > 0) {
    return { laTreDuoi72Thang: true, thieuCanNang: false, moTaTuoi: "" };
  }
  const bn = patientInfo || {};
  const coCanNangInfo =
    (bn.can_nang !== undefined && bn.can_nang !== null && String(bn.can_nang).trim() !== "") ||
    (bn.can_nang_kg !== undefined && bn.can_nang_kg !== null && String(bn.can_nang_kg).trim() !== "") ||
    /\b\d+(?:[.,]\d+)?\s*kg\b/i.test(transcript);

  const tuoiThang = bn.tuoi_thang !== undefined ? Number(bn.tuoi_thang) : NaN;
  const tuoiNam = bn.tuoi !== undefined ? Number(bn.tuoi) : NaN;

  if (!Number.isNaN(tuoiThang) && tuoiThang >= 0 && tuoiThang < 72) {
    return { laTreDuoi72Thang: true, thieuCanNang: !coCanNangInfo, moTaTuoi: `${tuoiThang} tháng tuổi` };
  }
  if (!Number.isNaN(tuoiNam) && tuoiNam >= 0 && tuoiNam < 6) {
    return { laTreDuoi72Thang: true, thieuCanNang: !coCanNangInfo, moTaTuoi: `${tuoiNam} tuổi (< 72 tháng)` };
  }

  const mThang = transcript.match(/\b(\d{1,2})\s*tháng\s*tuổi\b/i);
  if (mThang && Number(mThang[1]) < 72) {
    return { laTreDuoi72Thang: true, thieuCanNang: !coCanNangInfo, moTaTuoi: `${mThang[1]} tháng tuổi` };
  }
  const mTuoiNho = transcript.match(/\b(?:bé|cháu|con)\s*(\d)\s*tuổi\b/i);
  if (mTuoiNho && Number(mTuoiNho[1]) < 6) {
    return { laTreDuoi72Thang: true, thieuCanNang: !coCanNangInfo, moTaTuoi: `${mTuoiNho[1]} tuổi (< 72 tháng)` };
  }

  return { laTreDuoi72Thang: false, thieuCanNang: false, moTaTuoi: "" };
}

function laOCanBoSung(val: string): boolean {
  const v = (val || "").trim();
  return !v || v.includes("[cần bổ sung");
}

export const BangDoiSoatThuocVaDonQuocGiaModal: React.FC<BangDoiSoatThuocVaDonQuocGiaModalProps> = ({
  open,
  onClose,
  patientName = "Người bệnh",
  patientInfo,
  transcript = "",
  noteMeta,
  quyetDuyet = {},
  banSuaDuyet = {},
  onInsertReconciliationToNote,
  onSyncToLeaflet,
}) => {
  const duocLy = noteMeta?.clinicalSafety?.duoc_ly_ddi;
  const doiSoatBackend = noteMeta?.clinicalSafety?.doi_soat_thuoc_tt26;

  const khoiTao = useMemo(
    () => tachThuocNhaVaDonMoi(noteMeta?.propositions || [], quyetDuyet, banSuaDuyet, doiSoatBackend),
    [noteMeta?.propositions, quyetDuyet, banSuaDuyet, doiSoatBackend],
  );

  const [dsThuocNha, setDsThuocNha] = useState<DongThuocTaiNha[]>(khoiTao.thuocNha);
  const [dsDonMoi, setDsDonMoi] = useState<DongDonThuocTt26[]>(khoiTao.donMoi);
  const [canNangNhiKg, setCanNangNhiKg] = useState<string>(
    String(patientInfo?.can_nang_kg ?? patientInfo?.can_nang ?? ""),
  );
  const [nguoiDaiDienNhi, setNguoiDaiDienNhi] = useState<string>(
    String(patientInfo?.nguoi_dai_dien ?? ""),
  );
  const [daChepDon, setDaChepDon] = useState(false);
  const [daChenDoiSoat, setDaChenDoiSoat] = useState(false);
  const [daDongBoDanDo, setDaDongBoDanDo] = useState(false);

  useEffect(() => {
    setDsThuocNha(khoiTao.thuocNha);
    setDsDonMoi(khoiTao.donMoi);
  }, [khoiTao]);

  const kiemNhi = useMemo(
    () => phatHienTreDuoi72ThangThieuCanNang(patientInfo, transcript, canNangNhiKg),
    [patientInfo, transcript, canNangNhiKg],
  );

  // Tính ACB từ backend hoặc tham khảo tất định tại máy khách
  const acbInfo = useMemo(() => {
    const beAcb =
      duocLy?.ganh_nang_da_thuoc?.diem_acb ??
      duocLy?.ganh_nang_da_thuoc?.acb_score ??
      duocLy?.ganh_nang_da_thuoc?.ganh_nang_khang_cholinergic?.tong_diem;
    const chuoiThuoc = [
      ...dsThuocNha.filter((t) => t.quyetDinh !== "tam_ngung").map((t) => t.tenThuoc),
      ...dsDonMoi.map((d) => d.hoatChatBietDuoc),
    ];
    const localAcb = tinhDiemAcbThamKhao(chuoiThuoc);
    return {
      tongDiem: typeof beAcb === "number" ? beAcb : localAcb.tongDiem,
      chiTiet: localAcb.chiTiet,
      soThuocPhanBiet: duocLy?.ganh_nang_da_thuoc?.so_thuoc_phan_biet ?? chuoiThuoc.length,
      polypharmacy: Boolean(duocLy?.ganh_nang_da_thuoc?.polypharmacy || chuoiThuoc.length >= 5),
    };
  }, [duocLy, dsThuocNha, dsDonMoi]);

  if (!open) return null;

  const dsCanhBaoDdi: any[] = Array.isArray(duocLy?.canh_bao_ddi) ? duocLy.canh_bao_ddi : [];
  const dsTrungHoatChatDaDon: string[] = Array.isArray(doiSoatBackend?.canh_bao_trung_hoat_chat)
    ? doiSoatBackend.canh_bao_trung_hoat_chat.map((x: any) => String(x?.canh_bao || "")).filter(Boolean)
    : [];
  const dsTrungAtc: string[] = [
    ...dsTrungHoatChatDaDon,
    ...(Array.isArray(duocLy?.trung_nhom_atc) ? duocLy.trung_nhom_atc : []),
  ];
  const dsChongChiDinh: string[] = Array.isArray(duocLy?.chong_chi_dinh_co_dia) ? duocLy.chong_chi_dinh_co_dia : [];
  const dsVuotLieuTran: string[] = Array.isArray(duocLy?.vuot_lieu_tran) ? duocLy.vuot_lieu_tran : [];

  const capNhatThuocNha = (id: string, patch: Partial<DongThuocTaiNha>) => {
    setDsThuocNha((ds) => ds.map((d) => (d.id === id ? { ...d, ...patch } : d)));
  };

  const capNhatODonMoi = (id: string, truong: keyof DongDonThuocTt26, giaTri: string) => {
    setDsDonMoi((ds) => ds.map((d) => (d.id === id ? { ...d, [truong]: giaTri } : d)));
  };

  const themDongThuocMoi = () => {
    setDsDonMoi((ds) => [
      ...ds,
      {
        id: `manual_${Date.now()}`,
        hoatChatBietDuoc: CAN_BO_SUNG,
        hamLuong: CAN_BO_SUNG,
        sang: CAN_BO_SUNG,
        trua: "—",
        chieu: "—",
        toi: "—",
        soNgay: CAN_BO_SUNG,
        tongSoLuong: CAN_BO_SUNG,
        duongDungLoiDan: CAN_BO_SUNG,
        canCuLuot: "[Bác sĩ kê trực tiếp]",
      },
    ]);
  };

  const taoVanBanKetLuanDoiSoat = (): string => {
    if (dsThuocNha.length === 0) return "";
    const nhanQd: Record<QuyetDoiSoatThuocNha, string> = {
      chua_chon: "[cần bác sĩ chốt: Tiếp tục / Đổi liều / Tạm ngưng]",
      tiep_tuc: "TIẾP TỤC liều hiện tại",
      doi_lieu: "ĐỔI LIỀU theo y lệnh mới",
      tam_ngung: "TẠM NGƯNG",
    };
    const dong = dsThuocNha.map((t) => {
      const luotStr = t.luot.length > 0 ? ` [T${t.luot.join(", T")}]` : "";
      const ghiChu = t.ghiChuBacSi.trim() ? ` (${t.ghiChuBacSi.trim()})` : "";
      return `- [Đối soát thuốc nền tại nhà]: ${t.chiTietGoc} -> ${nhanQd[t.quyetDinh]}${ghiChu}${luotStr}`;
    });
    return dong.join("\n");
  };

  const taoVanBanDonTt26 = (): string => {
    const header = [
      "ĐƠN THUỐC ĐIỆN TỬ CHUẨN QUỐC GIA (THÔNG TƯ 26/2025/TT-BYT)",
      `Người bệnh: ${patientName}${canNangNhiKg.trim() ? ` | Cân nặng: ${canNangNhiKg.trim()} kg` : kiemNhi.laTreDuoi72Thang ? ` | Cân nặng: ${CAN_BO_SUNG}` : ""}${nguoiDaiDienNhi.trim() ? ` | Người đại diện: ${nguoiDaiDienNhi.trim()}` : ""}`,
      "--------------------------------------------------------------------------------",
    ];
    if (dsDonMoi.length === 0) {
      header.push("(Chưa có thuốc kê mới được xác nhận trong đợt khám này)");
    } else {
      dsDonMoi.forEach((d, idx) => {
        header.push(
          `${idx + 1}. ${d.hoatChatBietDuoc} (${d.hamLuong}) — SL: ${d.tongSoLuong} (${d.soNgay}) ${d.canCuLuot}`,
          `   Cách dùng: Sáng ${d.sang} | Trưa ${d.trua} | Chiều ${d.chieu} | Tối ${d.toi} — ${d.duongDungLoiDan}`,
        );
      });
    }
    return header.join("\n");
  };

  const dongBoSangToDanDo = () => {
    if (!onSyncToLeaflet) return;
    const thuocLeaflet: Thuoc[] = dsDonMoi.map((d, idx) => ({
      id: idx + 1,
      ten: `${d.hoatChatBietDuoc} ${d.hamLuong !== CAN_BO_SUNG ? d.hamLuong : ""}`.trim(),
      loai: "Đơn thuốc kê mới đợt này (Chuẩn TT 26/2025)",
      nhan: "ĐƠN KÊ MỚI",
      mau: "bg-emerald-50 text-emerald-700 border-emerald-200",
      sang: d.sang,
      trua: d.trua,
      chieu: d.chieu,
      toi: d.toi,
      loiDan: `${d.duongDungLoiDan} · Thời gian: ${d.soNgay} · Căn cứ ${d.canCuLuot}`,
    }));
    onSyncToLeaflet(thuocLeaflet);
    setDaDongBoDanDo(true);
    setTimeout(() => setDaDongBoDanDo(false), 2200);
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/45 backdrop-blur-2xs p-3 sm:p-5 no-print animate-in fade-in duration-150"
      onClick={onClose}
    >
      <div
        role="dialog"
        aria-label="Đối soát Đa thuốc & Đơn thuốc Quốc gia TT 26/2025"
        onClick={(e) => e.stopPropagation()}
        className="w-full max-w-6xl max-h-[90vh] rounded-2xl bg-white border border-[#BAE6FD] shadow-2xl flex flex-col overflow-hidden text-left font-sans"
      >
        {/* Đầu modal */}
        <div className="px-5 py-3.5 border-b border-[#BAE6FD] bg-gradient-to-r from-[#F0F9FF] via-white to-[#F8FBFC] flex items-center justify-between gap-3 flex-shrink-0">
          <div className="flex items-center gap-3 min-w-0">
            <div className="w-9 h-9 rounded-xl bg-[#0284C7] text-white flex items-center justify-center shadow-tactile-doctor flex-shrink-0">
              <Pill size={18} />
            </div>
            <div className="min-w-0">
              <h2 className="font-serif text-[18px] font-semibold text-[#0F172A] truncate">
                Đối soát Đa thuốc (Polypharmacy) & Đơn thuốc Quốc gia Thông tư 26/2025/TT-BYT
              </h2>
              <p className="text-[11.5px] text-[#475569]">
                Người bệnh: <strong className="text-[#0369A1]">{patientName}</strong> · Tách biệt hoàn toàn thuốc nền tại nhà và đơn kê mới · Không tự điền liều khuyết
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-600 cursor-pointer"
            title="Đóng"
          >
            <X size={16} />
          </button>
        </div>

        {/* Nội dung cuộn */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-5 space-y-5 bg-[#F8FBFC]">
          {/* Khối cảnh báo DDI, Trùng nhóm ATC & Điểm gánh nặng ACB */}
          {(dsCanhBaoDdi.length > 0 ||
            dsTrungAtc.length > 0 ||
            dsChongChiDinh.length > 0 ||
            dsVuotLieuTran.length > 0 ||
            acbInfo.polypharmacy ||
            acbInfo.tongDiem > 0) && (
            <div className="rounded-2xl border border-[#F5C2C2] bg-[#FFF5F5] p-4 space-y-3 shadow-2xs">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center gap-2 text-[#B4232C] font-bold text-xs uppercase tracking-wider">
                  <ShieldAlert size={15} />
                  <span>Cảnh báo An toàn Dược lý · Tương tác DDI & Gánh nặng Kháng Cholinergic (ACB)</span>
                </div>
                <div className="flex flex-wrap items-center gap-1.5">
                  <span
                    className={`px-2.5 py-0.5 rounded-full text-[11px] font-bold border ${
                      acbInfo.tongDiem >= 3
                        ? "bg-red-600 text-white border-red-700"
                        : acbInfo.tongDiem >= 1
                        ? "bg-[#FEF9E7] text-[#92400E] border-[#F5E6B8]"
                        : "bg-white text-slate-600 border-slate-200"
                    }`}
                  >
                    Điểm gánh nặng ACB: {acbInfo.tongDiem} {acbInfo.tongDiem >= 3 ? "(Nguy cơ lú lẫn/té ngã cao ≥ 3!)" : ""}
                  </span>
                  <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-white border border-[#BAE6FD] text-[#0369A1]">
                    {acbInfo.soThuocPhanBiet} hoạt chất đang xem xét
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
                {dsCanhBaoDdi.map((ddi, idx) => (
                  <div key={`ddi_${idx}`} className="rounded-xl bg-white border border-[#F5C2C2] p-3 space-y-1">
                    <div className="font-bold text-[#B4232C] flex items-center justify-between gap-2">
                      <span>
                        {String(ddi.thuoc_1 || "").toUpperCase()} + {String(ddi.thuoc_2 || "").toUpperCase()}
                      </span>
                      <span className="px-1.5 py-0.5 rounded bg-red-100 text-red-800 text-[10px]">
                        {ddi.muc_do || "Tương tác"}
                      </span>
                    </div>
                    <p className="text-[#0F172A] leading-snug">{ddi.hau_qua}</p>
                    {ddi.khuyen_cao && (
                      <p className="text-[11px] text-[#0369A1] font-medium">Gợi ý dược lâm sàng: {ddi.khuyen_cao}</p>
                    )}
                  </div>
                ))}
                {[...dsTrungAtc, ...dsChongChiDinh, ...dsVuotLieuTran].map((msg, idx) => (
                  <div
                    key={`atc_${idx}`}
                    className="rounded-xl bg-[#FEF9E7] border border-[#F5E6B8] p-3 text-[#7A4B00] font-medium leading-snug"
                  >
                    {msg}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* BẢNG 1: ĐỐI SOÁT THUỐC ĐANG DÙNG Ở NHÀ */}
          <section className="rounded-2xl border border-[#BAE6FD] bg-white shadow-tactile-doctor-card overflow-hidden">
            <div className="px-4 py-3 border-b border-[#E2ECF3] bg-[#F0F9FF] flex flex-wrap items-center justify-between gap-2">
              <div>
                <h3 className="font-serif text-[15.5px] font-semibold text-[#0C2340]">
                  Bảng 1 — Đối soát Thuốc Đang Dùng Ở Nhà (Polypharmacy Reconciliation)
                </h3>
                <p className="text-[11px] text-[#475569]">
                  Bác sĩ xác nhận từng thuốc nền người bệnh đang uống tại nhà trước khi ra toa mới
                </p>
              </div>
              {onInsertReconciliationToNote && dsThuocNha.length > 0 && (
                <button
                  type="button"
                  onClick={() => {
                    const block = taoVanBanKetLuanDoiSoat();
                    if (block) {
                      onInsertReconciliationToNote(block);
                      setDaChenDoiSoat(true);
                      setTimeout(() => setDaChenDoiSoat(false), 2200);
                    }
                  }}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#0284C7] hover:bg-[#0369A1] text-white text-xs font-semibold shadow-tactile-doctor cursor-pointer"
                >
                  {daChenDoiSoat ? <Check size={13} /> : <Plus size={13} />}
                  <span>
                    {daChenDoiSoat
                      ? "Đã chèn vào Bệnh án ✓"
                      : "Chèn kết luận đối soát thuốc vào Bệnh án"}
                  </span>
                </button>
              )}
            </div>

            {dsThuocNha.length === 0 ? (
              <p className="p-5 text-xs text-[#64748B] text-center">
                Chưa ghi nhận thuốc nền đang dùng ở nhà từ mục <strong>THUỐC ĐANG DÙNG</strong> của bệnh nhân.
              </p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-xs border-collapse">
                  <thead>
                    <tr className="bg-[#F8FBFC] text-[#0C4A6E] border-b border-[#E2ECF3] text-left">
                      <th className="py-2.5 px-3 font-bold w-10">STT</th>
                      <th className="py-2.5 px-3 font-bold">Thuốc đang dùng ở nhà & Cách uống bệnh nhân khai</th>
                      <th className="py-2.5 px-3 font-bold w-24">Căn cứ</th>
                      <th className="py-2.5 px-3 font-bold w-72">Quyết định đối soát của Bác sĩ</th>
                      <th className="py-2.5 px-3 font-bold w-60">Ghi chú chỉnh liều / Lý do ngưng</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {dsThuocNha.map((t, idx) => (
                      <tr key={t.id} className="hover:bg-[#F8FBFC]">
                        <td className="py-2.5 px-3 font-mono text-slate-500">{idx + 1}</td>
                        <td className="py-2.5 px-3">
                          <div className="font-bold text-[#0F172A]">{t.tenThuoc}</div>
                          {t.chiTietGoc !== t.tenThuoc && (
                            <div className="text-[11px] text-[#64748B] mt-0.5">{t.chiTietGoc}</div>
                          )}
                        </td>
                        <td className="py-2.5 px-3 font-mono text-[11px] text-[#0284C7] font-semibold">
                          {t.luot.length > 0 ? `[T${t.luot.join(", T")}]` : "—"}
                        </td>
                        <td className="py-2.5 px-3">
                          <div className="inline-flex flex-wrap items-center gap-1">
                            {(
                              [
                                ["tiep_tuc", "Tiếp tục", "bg-[#D1F2E3] text-[#0D6B50] border-[#0D9488]"],
                                ["doi_lieu", "Đổi liều", "bg-[#FEF3C7] text-[#92400E] border-[#D97706]"],
                                ["tam_ngung", "Tạm ngưng", "bg-[#FEE2E2] text-[#B4232C] border-[#E11D48]"],
                              ] as const
                            ).map(([ma, nhan, mauChon]) => {
                              const dangChon = t.quyetDinh === ma;
                              return (
                                <button
                                  key={ma}
                                  type="button"
                                  onClick={() =>
                                    capNhatThuocNha(t.id, {
                                      quyetDinh: dangChon ? "chua_chon" : ma,
                                    })
                                  }
                                  className={`px-2.5 py-1 rounded-lg text-[11px] font-semibold border transition-all cursor-pointer ${
                                    dangChon
                                      ? mauChon
                                      : "bg-white border-[#CCE3F0] text-[#334155] hover:border-[#0284C7]"
                                  }`}
                                >
                                  {nhan}
                                </button>
                              );
                            })}
                          </div>
                        </td>
                        <td className="py-2.5 px-3">
                          <input
                            type="text"
                            value={t.ghiChuBacSi}
                            onChange={(e) => capNhatThuocNha(t.id, { ghiChuBacSi: e.target.value })}
                            placeholder={
                              t.quyetDinh === "doi_lieu"
                                ? "Ghi liều mới..."
                                : t.quyetDinh === "tam_ngung"
                                ? "Lý do tạm ngưng..."
                                : "Ghi chú thêm (tùy chọn)"
                            }
                            className="w-full px-2.5 py-1 rounded-lg border border-[#BAE6FD] bg-white text-xs text-[#0F172A] focus:outline-none focus:ring-1 focus:ring-[#0284C7]"
                          />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          {/* CẢNH BÁO BẮT BUỘC CÂN NẶNG NHI KHOA < 72 THÁNG TUỔI (THÔNG TƯ 26/2025/TT-BYT) */}
          {kiemNhi.laTreDuoi72Thang && (
            <div
              className={`rounded-2xl border p-3.5 flex flex-wrap items-center justify-between gap-3 ${
                kiemNhi.thieuCanNang
                  ? "bg-[#FFF5F5] border-[#F5C2C2] text-[#991B1B]"
                  : "bg-[#FEF9E7] border-[#F5E6B8] text-[#7A4B00]"
              }`}
            >
              <div className="flex items-start gap-2.5 max-w-2xl">
                <AlertTriangle size={18} className="mt-0.5 flex-shrink-0" />
                <div className="text-xs space-y-0.5">
                  <div className="font-bold">
                    BẮT BUỘC THEO THÔNG TƯ 26/2025/TT-BYT — BỆNH NHI DƯỚI 72 THÁNG TUỔI ({kiemNhi.moTaTuoi || "< 72 tháng"})
                  </div>
                  <p className="text-[11.5px] leading-snug">
                    Đơn thuốc trẻ dưới 72 tháng tuổi bắt buộc ghi chính xác <strong>Cân nặng (kg)</strong> và họ tên{" "}
                    <strong>Người đại diện đưa trẻ đến khám</strong>; hệ thống không tự suy đoán cân nặng.
                  </p>
                </div>
              </div>
              <div className="flex flex-wrap items-center gap-2 text-xs">
                <label className="flex items-center gap-1.5 font-semibold">
                  <span>Cân nặng (kg):</span>
                  <input
                    type="text"
                    value={canNangNhiKg}
                    onChange={(e) => setCanNangNhiKg(e.target.value)}
                    placeholder="[cần bổ sung kg]"
                    className={`w-28 px-2.5 py-1 rounded-lg border text-xs font-mono ${
                      !canNangNhiKg.trim()
                        ? "border-dashed border-amber-500 bg-[#FEF9E7] text-amber-900"
                        : "border-[#0D9488] bg-white text-[#0F172A]"
                    }`}
                  />
                </label>
                <label className="flex items-center gap-1.5 font-semibold">
                  <span>Người đại diện:</span>
                  <input
                    type="text"
                    value={nguoiDaiDienNhi}
                    onChange={(e) => setNguoiDaiDienNhi(e.target.value)}
                    placeholder="[họ tên bố/mẹ]"
                    className={`w-40 px-2.5 py-1 rounded-lg border text-xs ${
                      !nguoiDaiDienNhi.trim()
                        ? "border-dashed border-amber-500 bg-[#FEF9E7] text-amber-900"
                        : "border-[#0D9488] bg-white text-[#0F172A]"
                    }`}
                  />
                </label>
              </div>
            </div>
          )}

          {/* BẢNG 2: BẢNG NHÁP ĐƠN THUỐC ĐIỆN TỬ QUỐC GIA (THÔNG TƯ 26/2025/TT-BYT) */}
          <section className="rounded-2xl border border-[#BAE6FD] bg-white shadow-tactile-doctor-card overflow-hidden">
            <div className="px-4 py-3 border-b border-[#E2ECF3] bg-[#FEF9E7]/70 flex flex-wrap items-center justify-between gap-2">
              <div>
                <h3 className="font-serif text-[15.5px] font-semibold text-[#0C2340]">
                  Bảng 2 — Bảng Nháp Đơn Thuốc Điện Tử Quốc Gia (Thông tư 26/2025/TT-BYT)
                </h3>
                <p className="text-[11px] text-[#7A4B00]">
                  Chỉ tổng hợp y lệnh kê mới đã được bác sĩ xác nhận · Các ô viền vàng nét đứt{" "}
                  <code className="font-mono">[cần bổ sung]</code> cần bác sĩ điền trực tiếp
                </p>
              </div>
              <button
                type="button"
                onClick={themDongThuocMoi}
                className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-xl bg-white hover:bg-[#F0F9FF] border border-[#BAE6FD] text-[#0369A1] text-xs font-semibold shadow-tactile-doctor-pill cursor-pointer"
              >
                <Plus size={13} />
                <span>Thêm dòng thuốc mới</span>
              </button>
            </div>

            {dsDonMoi.length === 0 ? (
              <div className="p-6 text-center space-y-2 text-xs text-[#64748B]">
                <p>
                  Chưa có thuốc kê mới nào được xác nhận trong mục <strong>KẾ HOẠCH ĐIỀU TRỊ / ĐƠN THUỐC</strong> (thuốc nền ở nhà không tự động chép sang đơn mới).
                </p>
                <p className="text-[11px]">
                  Nếu có thuốc đang ở khay <em>Cần xác nhận</em>, hãy bấm <strong>Xác nhận (Giữ)</strong> ở ngăn duyệt hoặc bấm <strong>+ Thêm dòng thuốc mới</strong>.
                </p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-xs border-collapse min-w-[980px]">
                  <thead>
                    <tr className="bg-[#F8FBFC] text-[#0C4A6E] border-b border-[#E2ECF3] text-left">
                      <th className="py-2.5 px-2.5 font-bold w-10">STT</th>
                      <th className="py-2.5 px-2.5 font-bold min-w-[180px]">Hoạt chất & Biệt dược</th>
                      <th className="py-2.5 px-2 font-bold w-24">Hàm lượng</th>
                      <th className="py-2.5 px-2 font-bold w-20 text-center">Sáng</th>
                      <th className="py-2.5 px-2 font-bold w-20 text-center">Trưa</th>
                      <th className="py-2.5 px-2 font-bold w-20 text-center">Chiều</th>
                      <th className="py-2.5 px-2 font-bold w-20 text-center">Tối</th>
                      <th className="py-2.5 px-2 font-bold w-24">Số ngày</th>
                      <th className="py-2.5 px-2 font-bold w-24">Tổng SL</th>
                      <th className="py-2.5 px-2.5 font-bold min-w-[190px]">Đường dùng & Lời dặn ăn uống</th>
                      <th className="py-2.5 px-2 font-bold w-24">Căn cứ [T_i]</th>
                      <th className="py-2.5 px-2 w-8" />
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {dsDonMoi.map((d, idx) => {
                      const renderCellInput = (
                        truong: keyof DongDonThuocTt26,
                        alignCenter = false,
                      ) => {
                        const val = d[truong];
                        const thieu = laOCanBoSung(val);
                        return (
                          <input
                            type="text"
                            value={val}
                            onChange={(e) => capNhatODonMoi(d.id, truong, e.target.value)}
                            className={`w-full px-2 py-1 rounded-md text-[11.5px] focus:outline-none focus:ring-1 focus:ring-[#0284C7] ${
                              alignCenter ? "text-center" : ""
                            } ${
                              thieu
                                ? "border border-dashed border-amber-400 bg-[#FEF9E7] text-[#92400E] font-medium"
                                : "border border-slate-200 bg-white text-[#0F172A]"
                            }`}
                          />
                        );
                      };

                      return (
                        <tr key={d.id} className="hover:bg-[#F8FBFC]">
                          <td className="py-2 px-2.5 font-mono text-slate-500">{idx + 1}</td>
                          <td className="py-2 px-2.5">{renderCellInput("hoatChatBietDuoc")}</td>
                          <td className="py-2 px-2">{renderCellInput("hamLuong")}</td>
                          <td className="py-2 px-2">{renderCellInput("sang", true)}</td>
                          <td className="py-2 px-2">{renderCellInput("trua", true)}</td>
                          <td className="py-2 px-2">{renderCellInput("chieu", true)}</td>
                          <td className="py-2 px-2">{renderCellInput("toi", true)}</td>
                          <td className="py-2 px-2">{renderCellInput("soNgay")}</td>
                          <td className="py-2 px-2">{renderCellInput("tongSoLuong")}</td>
                          <td className="py-2 px-2.5">{renderCellInput("duongDungLoiDan")}</td>
                          <td className="py-2 px-2 font-mono text-[11px] font-semibold text-[#0284C7]">
                            {d.canCuLuot}
                          </td>
                          <td className="py-2 px-2">
                            <button
                              type="button"
                              onClick={() => setDsDonMoi((ds) => ds.filter((x) => x.id !== d.id))}
                              title="Xóa dòng thuốc này khỏi nháp đơn"
                              className="p-1 rounded text-slate-400 hover:text-red-600 hover:bg-red-50 cursor-pointer"
                            >
                              <Trash2 size={13} />
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </div>

        {/* Chân modal: Xuất & đồng bộ */}
        <div className="px-5 py-3 border-t border-[#BAE6FD] bg-white flex flex-wrap items-center justify-between gap-2 flex-shrink-0">
          <div className="flex items-center gap-1.5 text-[11px] text-[#64748B]">
            <CheckCircle2 size={13} className="text-[#0D9488]" />
            <span>Nháp đơn thuốc chỉ có giá trị sau khi bác sĩ kiểm tra đầy đủ các trường khuyết và ký duyệt.</span>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            {onSyncToLeaflet && (
              <button
                type="button"
                disabled={dsDonMoi.length === 0}
                onClick={dongBoSangToDanDo}
                className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl border border-[#BAE6FD] bg-[#F0F9FF] hover:bg-[#E0F2FE] disabled:opacity-40 text-[#0369A1] text-xs font-semibold shadow-tactile-doctor-pill cursor-pointer"
              >
                {daDongBoDanDo ? <Check size={13} /> : <FileHeart size={13} />}
                <span>{daDongBoDanDo ? "Đã cập nhật Tờ dặn dò ✓" : "Cập nhật sang Tờ dặn dò"}</span>
              </button>
            )}
            <button
              type="button"
              onClick={() => {
                navigator.clipboard.writeText(taoVanBanDonTt26());
                setDaChepDon(true);
                setTimeout(() => setDaChepDon(false), 2200);
              }}
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-[#0284C7] hover:bg-[#0369A1] text-white text-xs font-semibold shadow-tactile-doctor cursor-pointer"
            >
              {daChepDon ? <Check size={13} /> : <Copy size={13} />}
              <span>{daChepDon ? "Đã chép bảng đơn TT 26/2025 ✓" : "Chép bảng đơn chuẩn TT 26/2025"}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
