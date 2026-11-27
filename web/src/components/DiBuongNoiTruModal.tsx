import React, { useCallback, useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  Check,
  CheckCircle2,
  Clock,
  Copy,
  FileText,
  Plus,
  Printer,
  RefreshCw,
  Stethoscope,
  Users,
  X,
} from "lucide-react";
import type { Session } from "../types";
import type { NoteMeta, Proposition, Quyet } from "./VerificationView";
import { taoPhieuSbar } from "../lib/sbar";

export interface KetQuaDienBienNoiTru {
  ngayGio: string;
  trieuChungDoHet: string[];
  trieuChungMoiHoacNangLen: string[];
  sinhHieuVaKham: string[];
  yLenhDuyTri: string[];
  yLenhMoiHoacDoi: string[];
  cheDoChamSocDinhDuong: string[];
}

export interface MucBanGiaoCaTruc {
  sessionId: string;
  tenBenhNhan: string;
  thoiGian: string;
  mucUuTien: "NGUY_KICH" | "CAN_THEO_DOI" | "ON_DINH";
  diemRuiRo: number;
  lyDoRuiRo: string[];
  situation: string;
  background: string;
  assessment: string;
  recommendation: string;
}

interface DiBuongNoiTruModalProps {
  open: boolean;
  onClose: () => void;
  currentSession?: Session | null;
  allSessions?: Session[];
  noteMeta?: NoteMeta | null;
  quyetDuyet?: Record<number, Quyet>;
  banSuaDuyet?: Record<number, string>;
  onCreateTab?: (title: string, content: string) => void;
}

function trichTuKhoaCotLoi(vanBan: string): string[] {
  const dsTuKhoa = [
    "đau ngực",
    "đau bụng",
    "đau đầu",
    "đau lưng",
    "khó thở",
    "sốt",
    "ho",
    "nôn",
    "buồn nôn",
    "chóng mặt",
    "tiêu chảy",
    "mệt",
    "phù",
    "hồi hộp",
    "ợ chua",
    "tiểu buốt",
  ];
  const v = (vanBan || "").toLowerCase();
  return dsTuKhoa.filter((tk) => v.includes(tk));
}

function trichSinhHieuTuVanBan(vanBan: string): Record<string, string> {
  const kq: Record<string, string> = {};
  const mHa = vanBan.match(/\b(?:huyết áp|ha)\s*[:=]?\s*(\d{2,3}\s*\/\s*\d{2,3}(?:\s*mmhg)?)/i);
  if (mHa) kq["HA"] = mHa[1].trim();
  const mMach = vanBan.match(/\bmạch\s*[:=]?\s*(\d{2,3}(?:\s*l\/p|\s*lần\/phút)?)/i);
  if (mMach) kq["Mạch"] = mMach[1].trim();
  const mNhiet = vanBan.match(/\b(?:nhiệt độ|sốt)\s*[:=]?\s*(3[6-9](?:[.,]\d)?|4[01](?:[.,]\d)?)\s*(?:°c|độ)?/i);
  if (mNhiet) kq["Nhiệt độ"] = `${mNhiet[1]}°C`;
  const mSpo2 = vanBan.match(/\bspo2\s*[:=]?\s*(\d{2,3}\s*%?)/i);
  if (mSpo2) kq["SpO2"] = mSpo2[1].includes("%") ? mSpo2[1].trim() : `${mSpo2[1].trim()}%`;
  return kq;
}

function layMenhDeHieuLuc(
  propositions: Proposition[] | undefined,
  quyet: Record<number, Quyet> = {},
  banSua: Record<number, string> = {},
): Array<Proposition & { effectiveText: string; turnTag: string }> {
  return (propositions || [])
    .filter((p) => quyet[p.id] !== "bo")
    .map((p) => {
      const effectiveText = (quyet[p.id] === "sua" && banSua[p.id]?.trim() ? banSua[p.id].trim() : p.text || "").trim();
      const turnTag = p.evidenceTurns?.length ? `[T${p.evidenceTurns.join(", T")}]` : "";
      return { ...p, effectiveText, turnTag };
    })
    .filter((p) => p.effectiveText.length > 0);
}

/**
 * Động cơ tất định đối chiếu diễn biến đi buồng nội trú giữa ca trước và ca hiện tại
 * (hoặc hợp nhất dữ liệu từ `POST /api/inpatient/ward-round-diff` nếu máy chủ trả về).
 */
export function soSanhDienBienNoiTruDeterministic(params: {
  prevProps: Proposition[];
  prevQuyet?: Record<number, Quyet>;
  prevBanSua?: Record<number, string>;
  prevTranscript?: string;
  currProps: Proposition[];
  currQuyet?: Record<number, Quyet>;
  currBanSua?: Record<number, string>;
  currTranscript?: string;
  serverDiff?: any;
}): KetQuaDienBienNoiTru {
  const {
    prevProps,
    prevQuyet = {},
    prevBanSua = {},
    prevTranscript = "",
    currProps,
    currQuyet = {},
    currBanSua = {},
    currTranscript = "",
    serverDiff,
  } = params;

  const ngayGio = new Date().toLocaleString("vi-VN", {
    hour: "2-digit",
    minute: "2-digit",
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });

  if (serverDiff && typeof serverDiff === "object") {
    // 1. Hỗ trợ định dạng chính thức từ `src/cong_cu_lam_sang/di_buong_noi_tru.py`
    if (
      Array.isArray(serverDiff.trieu_chung_giam_hoac_het) ||
      Array.isArray(serverDiff.trieu_chung_moi_phat_sinh) ||
      Array.isArray(serverDiff.y_lenh_duy_tri) ||
      Array.isArray(serverDiff.y_lenh_thay_doi)
    ) {
      const fmtTc = (arr: any[]) =>
        (arr || []).map((tc: any) => {
          const bc = Array.isArray(tc?.bang_chung) ? tc.bang_chung.join(" ") : "";
          return `${tc?.noi_dung || ""} ${bc}`.trim();
        });
      const fmtSh = (arr: any[]) =>
        (arr || []).map((s: any) => {
          const bc = Array.isArray(s?.bang_chung) ? s.bang_chung.join(" ") : "";
          if (s?.hom_qua && s?.hom_nay) {
            return `${s.chi_so}: ${s.hom_qua} → ${s.hom_nay}${s.xu_huong ? ` (${s.xu_huong})` : ""} ${bc}`.trim();
          }
          if (s?.hom_nay) return `${s.chi_so}: ${s.hom_nay} ${bc}`.trim();
          return `${s?.chi_so || "Sinh hiệu"}: [cần bổ sung số đo hôm nay; hôm qua ${s?.hom_qua || "chưa rõ"}]`;
        });
      const fmtYl = (arr: any[]) =>
        (arr || []).map((yl: any) => {
          const bc = Array.isArray(yl?.bang_chung) ? yl.bang_chung.join(" ") : "";
          return `${yl?.mo_ta || yl?.ten_thuoc || ""} ${bc}`.trim();
        });

      return {
        ngayGio: String(serverDiff.ngay_gio || ngayGio),
        trieuChungDoHet: fmtTc(serverDiff.trieu_chung_giam_hoac_het),
        trieuChungMoiHoacNangLen: [
          ...fmtTc(serverDiff.trieu_chung_moi_phat_sinh).map((x) => `[Mới phát sinh] ${x}`),
          ...fmtTc(serverDiff.trieu_chung_con_ton_tai),
        ],
        sinhHieuVaKham: fmtSh(serverDiff.bien_thien_sinh_hieu),
        yLenhDuyTri: fmtYl(serverDiff.y_lenh_duy_tri),
        yLenhMoiHoacDoi: fmtYl(serverDiff.y_lenh_thay_doi),
        cheDoChamSocDinhDuong: ["Chế độ chăm sóc & dinh dưỡng: [cần bổ sung cấp chăm sóc & chế độ ăn]"],
      };
    }

    // 2. Hỗ trợ định dạng rút gọn nếu có
    const db = serverDiff.dien_bien || serverDiff;
    const yl = serverDiff.y_lenh || serverDiff;
    const coDuLieuBe =
      Array.isArray(db.trieu_chung_do_het) ||
      Array.isArray(db.trieu_chung_moi) ||
      Array.isArray(yl.thuoc_duy_tri) ||
      Array.isArray(yl.thuoc_doi_moi);
    if (coDuLieuBe) {
      return {
        ngayGio: String(serverDiff.ngay_gio || ngayGio),
        trieuChungDoHet: Array.isArray(db.trieu_chung_do_het) ? db.trieu_chung_do_het.map(String) : [],
        trieuChungMoiHoacNangLen: Array.isArray(db.trieu_chung_moi) ? db.trieu_chung_moi.map(String) : [],
        sinhHieuVaKham: Array.isArray(db.sinh_hieu_doi) ? db.sinh_hieu_doi.map(String) : [],
        yLenhDuyTri: Array.isArray(yl.thuoc_duy_tri) ? yl.thuoc_duy_tri.map(String) : [],
        yLenhMoiHoacDoi: Array.isArray(yl.thuoc_doi_moi) ? yl.thuoc_doi_moi.map(String) : [],
        cheDoChamSocDinhDuong: Array.isArray(yl.cham_soc)
          ? yl.cham_soc.map(String)
          : ["Chế độ chăm sóc & dinh dưỡng: [cần bổ sung cấp chăm sóc ĐD]"],
      };
    }
  }

  const cu = layMenhDeHieuLuc(prevProps, prevQuyet, prevBanSua);
  const moi = layMenhDeHieuLuc(currProps, currQuyet, currBanSua);

  const trieuChungCuDuongTinh = new Set<string>();
  for (const p of cu) {
    if (!p.negated && !/THUỐC|KẾ HOẠCH|CHẨN ĐOÁN/i.test(p.section || "")) {
      for (const tk of trichTuKhoaCotLoi(p.effectiveText)) {
        trieuChungCuDuongTinh.add(tk);
      }
    }
  }

  const trieuChungDoHet: string[] = [];
  const trieuChungMoiHoacNangLen: string[] = [];
  const sinhHieuVaKham: string[] = [];

  for (const p of moi) {
    const sec = (p.section || "").toUpperCase();
    if (/THUỐC|KẾ HOẠCH|ĐƠN THUỐC|DẶN DÒ/i.test(sec)) continue;

    if (/KHÁM|SINH HIỆU|CẬN LÂM SÀNG/i.test(sec)) {
      sinhHieuVaKham.push(`${p.effectiveText} ${p.turnTag}`.trim());
      continue;
    }

    const tks = trichTuKhoaCotLoi(p.effectiveText);
    const laDoHet =
      p.negated ||
      /\b(?:đỡ|giảm|hết|bớt|không còn|cải thiện|ổn định)\b/i.test(p.effectiveText);

    if (laDoHet) {
      trieuChungDoHet.push(`${p.effectiveText} ${p.turnTag}`.trim());
    } else {
      const moiXuatHien = tks.length === 0 || tks.some((tk) => !trieuChungCuDuongTinh.has(tk));
      const nhan = cu.length > 0 && moiXuatHien ? "[Mới ghi nhận] " : "";
      trieuChungMoiHoacNangLen.push(`${nhan}${p.effectiveText} ${p.turnTag}`.trim());
    }
  }

  // So sánh sinh hiệu giữa 2 phiên
  const shCu = trichSinhHieuTuVanBan(`${prevTranscript} ${cu.map((x) => x.effectiveText).join(" ")}`);
  const shMoi = trichSinhHieuTuVanBan(`${currTranscript} ${moi.map((x) => x.effectiveText).join(" ")}`);
  for (const k of Object.keys(shMoi)) {
    if (shCu[k] && shCu[k] !== shMoi[k]) {
      sinhHieuVaKham.unshift(`Biến thiên ${k}: ${shCu[k]} → ${shMoi[k]}`);
    } else if (!shCu[k]) {
      sinhHieuVaKham.unshift(`${k} hôm nay: ${shMoi[k]}`);
    }
  }

  // So sánh thuốc duy trì vs. thuốc mới/đổi liều
  const thuocCuMap = new Map<string, string>();
  for (const p of cu) {
    if (p.negated) continue;
    if (p.drug || /THUỐC|KẾ HOẠCH|ĐƠN THUỐC/i.test(p.section || "")) {
      const khoa = (p.drug || p.effectiveText.split(/\s+/).slice(0, 2).join(" ")).toLowerCase();
      thuocCuMap.set(khoa, p.effectiveText);
    }
  }

  const yLenhDuyTri: string[] = [];
  const yLenhMoiHoacDoi: string[] = [];
  const cheDoChamSocDinhDuong: string[] = [];

  for (const p of moi) {
    if (p.negated) continue;
    const sec = (p.section || "").toUpperCase();
    const daDuyetHoacThan = p.status === "than" || currQuyet[p.id] === "giu" || currQuyet[p.id] === "sua";
    if (!daDuyetHoacThan) continue;

    if (/DẶN DÒ|CHẾ ĐỘ ĂN|CHĂM SÓC/i.test(sec)) {
      cheDoChamSocDinhDuong.push(`${p.effectiveText} ${p.turnTag}`.trim());
      continue;
    }

    if (p.drug || /THUỐC|KẾ HOẠCH|ĐƠN THUỐC/i.test(sec)) {
      const khoa = (p.drug || p.effectiveText.split(/\s+/).slice(0, 2).join(" ")).toLowerCase();
      const dongCu = thuocCuMap.get(khoa);
      if (dongCu && dongCu.toLowerCase() === p.effectiveText.toLowerCase()) {
        yLenhDuyTri.push(`Duy trì: ${p.effectiveText} ${p.turnTag}`.trim());
      } else if (dongCu) {
        yLenhMoiHoacDoi.push(`Đổi y lệnh: ${p.effectiveText} (trước đó: ${dongCu}) ${p.turnTag}`.trim());
      } else {
        yLenhMoiHoacDoi.push(`${cu.length > 0 ? "Bổ sung/Kê mới: " : ""}${p.effectiveText} ${p.turnTag}`.trim());
      }
    }
  }

  if (cheDoChamSocDinhDuong.length === 0) {
    cheDoChamSocDinhDuong.push("Chế độ chăm sóc & dinh dưỡng: [cần bổ sung cấp chăm sóc & chế độ ăn]");
  }

  return {
    ngayGio,
    trieuChungDoHet,
    trieuChungMoiHoacNangLen,
    sinhHieuVaKham,
    yLenhDuyTri,
    yLenhMoiHoacDoi,
    cheDoChamSocDinhDuong,
  };
}

/**
 * Tổng hợp Sổ Bàn giao Ca trực Toàn khoa (Multi-Patient SBAR) sắp xếp theo mức độ nguy cơ lâm sàng.
 */
export function tongHopSoBanGiaoCaTruc(
  sessions: Session[],
  chiLayHomNay = false,
): MucBanGiaoCaTruc[] {
  const homNay = new Date().toLocaleDateString("vi-VN");
  const homNayIso = new Date().toISOString().slice(0, 10);

  const dsLoc = (sessions || []).filter((s) => {
    const coNoiDung = Boolean(s.transcript?.trim() || s.note?.propositions?.length || s.tabs?.some((t) => t.content?.trim()));
    if (!coNoiDung) return false;
    if (!chiLayHomNay) return true;
    const d = (s.date || "").trim();
    return d === homNay || d.includes(homNayIso) || /hôm nay|today/i.test(d);
  });

  const ketQua: MucBanGiaoCaTruc[] = dsLoc.map((s) => {
    const props = s.note?.propositions || [];
    const quyet = s.duyet?.quyet || {};
    const banSua = s.duyet?.banSua || {};
    const sbar = taoPhieuSbar(props, quyet, banSua, s.patientIdentifier);

    const cs = s.note?.clinicalSafety;
    let diemRuiRo = 0;
    const lyDoRuiRo: string[] = [];

    if (cs?.doi_soat_can_lam_sang?.co_gia_tri_nguy_kich) {
      diemRuiRo += 100;
      lyDoRuiRo.push("Giá trị CLS nguy kịch");
    }
    const soDdi = Array.isArray(cs?.duoc_ly_ddi?.canh_bao_ddi) ? cs.duoc_ly_ddi.canh_bao_ddi.length : 0;
    if (soDdi > 0) {
      diemRuiRo += 40 * soDdi;
      lyDoRuiRo.push(`${soDdi} tương tác thuốc DDI`);
    }
    const soCanXacNhan = props.filter(
      (p) => p.status === "can_xac_nhan" && (!quyet[p.id] || quyet[p.id] === "cho"),
    ).length;
    if (soCanXacNhan > 0) {
      diemRuiRo += 15 * soCanXacNhan;
      lyDoRuiRo.push(`${soCanXacNhan} mệnh đề chờ xác nhận`);
    }
    const cbCao = Array.isArray(cs?.thang_diem_nguy_co?.canh_bao_nguy_co_cao)
      ? cs.thang_diem_nguy_co.canh_bao_nguy_co_cao.length
      : 0;
    if (cbCao > 0) {
      diemRuiRo += 50;
      lyDoRuiRo.push("Thang điểm nguy cơ cao");
    }

    const mucUuTien: MucBanGiaoCaTruc["mucUuTien"] =
      diemRuiRo >= 80 ? "NGUY_KICH" : diemRuiRo >= 15 ? "CAN_THEO_DOI" : "ON_DINH";

    const tenSach = (s.patientIdentifier || "").trim();
    const tenBenhNhan =
      tenSach && !/^thêm\s+(?:tên\s+)?định\s+danh/i.test(tenSach) ? tenSach : `Ca #${s.id.slice(0, 6)}`;

    return {
      sessionId: s.id,
      tenBenhNhan,
      thoiGian: `${s.date || ""} ${s.time || ""}`.trim(),
      mucUuTien,
      diemRuiRo,
      lyDoRuiRo,
      situation: sbar.situation.join("; ") || "(Chưa ghi nhận diễn biến)",
      background: sbar.background.join("; ") || "(Chưa ghi nhận tiền sử/dị ứng)",
      assessment: sbar.assessment.join("; ") || "(Chưa ghi nhận chẩn đoán)",
      recommendation: sbar.recommendation.join("; ") || "(Theo dõi tiếp theo phác đồ)",
    };
  });

  return ketQua.sort((a, b) => b.diemRuiRo - a.diemRuiRo);
}

export function dinhDangVanBanToDieuTriTt32(
  patientName: string,
  dienBien: KetQuaDienBienNoiTru,
): string {
  const cotTrai = [
    ...(dienBien.trieuChungDoHet.length > 0
      ? ["• Triệu chứng đỡ/giảm:", ...dienBien.trieuChungDoHet.map((x) => `  - ${x}`)]
      : []),
    ...(dienBien.trieuChungMoiHoacNangLen.length > 0
      ? ["• Triệu chứng hiện tại / mới xuất hiện:", ...dienBien.trieuChungMoiHoacNangLen.map((x) => `  - ${x}`)]
      : []),
    ...(dienBien.sinhHieuVaKham.length > 0
      ? ["• Sinh hiệu & Khám / CLS:", ...dienBien.sinhHieuVaKham.map((x) => `  - ${x}`)]
      : []),
  ];

  const cotPhai = [
    ...(dienBien.yLenhDuyTri.length > 0
      ? ["• Thuốc duy trì:", ...dienBien.yLenhDuyTri.map((x) => `  - ${x}`)]
      : []),
    ...(dienBien.yLenhMoiHoacDoi.length > 0
      ? ["• Y lệnh thuốc mới / điều chỉnh:", ...dienBien.yLenhMoiHoacDoi.map((x) => `  - ${x}`)]
      : []),
    "• Chăm sóc & Theo dõi:",
    ...dienBien.cheDoChamSocDinhDuong.map((x) => `  - ${x}`),
  ];

  return [
    "# TỜ ĐIỀU TRỊ NỘI TRÚ (Mẫu BV-01/BV2 — Thông tư 32/2023/TT-BYT)",
    `Người bệnh: **${patientName}** | Thời điểm đi buồng: **${dienBien.ngayGio}**`,
    "---",
    "## DIỄN BIẾN BỆNH",
    ...(cotTrai.length > 0 ? cotTrai : ["- [cần bổ sung diễn biến lâm sàng hôm nay]"]),
    "",
    "## Y LỆNH ĐIỀU TRỊ & CHĂM SÓC",
    ...cotPhai,
  ].join("\n");
}

export const DiBuongNoiTruModal: React.FC<DiBuongNoiTruModalProps> = ({
  open,
  onClose,
  currentSession = null,
  allSessions = [],
  noteMeta = null,
  quyetDuyet = {},
  banSuaDuyet = {},
  onCreateTab,
}) => {
  const [tabCon, setTabCon] = useState<"to_dieu_tri" | "ban_giao_truc">("to_dieu_tri");
  const [phienTruocId, setPhienTruocId] = useState<string>("");
  const [dangTaiDiff, setDangTaiDiff] = useState(false);
  const [serverDiff, setServerDiff] = useState<any>(null);
  const [chiHomNay, setChiHomNay] = useState(false);
  const [daChep, setDaChep] = useState(false);

  const cacPhienKhac = useMemo(() => {
    const curId = currentSession?.id;
    const curName = (currentSession?.patientIdentifier || "").trim().toLowerCase();
    const ds = (allSessions || []).filter((s) => s.id !== curId && (s.note?.propositions?.length || s.transcript?.trim()));
    return [...ds].sort((a, b) => {
      const aCungBn = curName && a.patientIdentifier?.trim().toLowerCase() === curName ? 0 : 1;
      const bCungBn = curName && b.patientIdentifier?.trim().toLowerCase() === curName ? 0 : 1;
      return aCungBn - bCungBn;
    });
  }, [allSessions, currentSession?.id, currentSession?.patientIdentifier]);

  useEffect(() => {
    if (open && !phienTruocId && cacPhienKhac.length > 0) {
      setPhienTruocId(cacPhienKhac[0].id);
    }
  }, [open, phienTruocId, cacPhienKhac]);

  const phienTruoc = useMemo(
    () => cacPhienKhac.find((s) => s.id === phienTruocId) || null,
    [cacPhienKhac, phienTruocId],
  );

  const goiApiWardRoundDiff = useCallback(async () => {
    if (!phienTruoc) {
      setServerDiff(null);
      return;
    }
    setDangTaiDiff(true);
    try {
      const yesterdayProps = (phienTruoc.note?.propositions || [])
        .filter((p) => phienTruoc.duyet?.quyet?.[p.id] !== "bo")
        .map((p) =>
          phienTruoc.duyet?.quyet?.[p.id] === "sua" && phienTruoc.duyet?.banSua?.[p.id]?.trim()
            ? { ...p, text: phienTruoc.duyet.banSua[p.id].trim() }
            : p,
        );
      const todayProps = (noteMeta?.propositions || currentSession?.note?.propositions || [])
        .filter((p) => quyetDuyet[p.id] !== "bo")
        .map((p) =>
          quyetDuyet[p.id] === "sua" && banSuaDuyet[p.id]?.trim()
            ? { ...p, text: banSuaDuyet[p.id].trim() }
            : p,
        );

      const r = await fetch("/api/inpatient/ward-round-diff", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          todayPropositions: todayProps,
          yesterdayPropositions: yesterdayProps,
          todayTranscript: currentSession?.transcript || noteMeta?.transcript || "",
          previousSessionId: phienTruoc.id,
          currentSessionId: currentSession?.id || noteMeta?.caseId || "current",
        }),
      });
      if (r.ok) {
        setServerDiff(await r.json());
      } else {
        setServerDiff(null);
      }
    } catch {
      setServerDiff(null);
    } finally {
      setDangTaiDiff(false);
    }
  }, [phienTruoc, currentSession?.id, currentSession?.transcript, currentSession?.note?.propositions, noteMeta, quyetDuyet, banSuaDuyet]);

  useEffect(() => {
    if (open && tabCon === "to_dieu_tri") {
      void goiApiWardRoundDiff();
    }
  }, [open, tabCon, goiApiWardRoundDiff]);

  const dienBien = useMemo(
    () =>
      soSanhDienBienNoiTruDeterministic({
        prevProps: phienTruoc?.note?.propositions || [],
        prevQuyet: phienTruoc?.duyet?.quyet || {},
        prevBanSua: phienTruoc?.duyet?.banSua || {},
        prevTranscript: phienTruoc?.transcript || "",
        currProps: noteMeta?.propositions || currentSession?.note?.propositions || [],
        currQuyet: quyetDuyet,
        currBanSua: banSuaDuyet,
        currTranscript: currentSession?.transcript || noteMeta?.transcript || "",
        serverDiff,
      }),
    [phienTruoc, noteMeta, currentSession, quyetDuyet, banSuaDuyet, serverDiff],
  );

  const soBanGiao = useMemo(
    () => tongHopSoBanGiaoCaTruc(allSessions, chiHomNay),
    [allSessions, chiHomNay],
  );

  if (!open) return null;

  const tenBn =
    currentSession?.patientIdentifier &&
    !/^thêm\s+(?:tên\s+)?định\s+danh/i.test(currentSession.patientIdentifier)
      ? currentSession.patientIdentifier
      : "Người bệnh nội trú";

  const vanBanToDieuTri = dinhDangVanBanToDieuTriTt32(tenBn, dienBien);

  const vanBanSoBanGiao = [
    `# SỔ BÀN GIAO CA TRỰC TOÀN KHOA (${new Date().toLocaleDateString("vi-VN")})`,
    `Tổng số bệnh nhân bàn giao: ${soBanGiao.length} ca`,
    "---",
    ...soBanGiao.map(
      (m, idx) =>
        `${idx + 1}. [${m.mucUuTien}] ${m.tenBenhNhan} (${m.thoiGian})\n` +
        `   - S (Tình trạng): ${m.situation}\n` +
        `   - B (Tiền sử/Dị ứng): ${m.background}\n` +
        `   - A (Chẩn đoán & Cảnh báo): ${m.assessment}${m.lyDoRuiRo.length ? ` | Lưu ý: ${m.lyDoRuiRo.join(", ")}` : ""}\n` +
        `   - R (Y lệnh theo dõi ca sau): ${m.recommendation}`,
    ),
  ].join("\n\n");

  const saoChepHienTai = () => {
    navigator.clipboard.writeText(tabCon === "to_dieu_tri" ? vanBanToDieuTri : vanBanSoBanGiao);
    setDaChep(true);
    setTimeout(() => setDaChep(false), 2000);
  };

  const inNoiDungHienTai = () => {
    const win = window.open("", "_blank", "width=960,height=900");
    if (!win) return;
    const raw = tabCon === "to_dieu_tri" ? vanBanToDieuTri : vanBanSoBanGiao;
    const esc = raw.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    win.document.write(
      `<!doctype html><html lang="vi"><head><meta charset="utf-8"/><title>${
        tabCon === "to_dieu_tri" ? "Tờ điều trị TT 32/2023" : "Sổ bàn giao ca trực"
      }</title><style>body{font-family:"Times New Roman",serif;padding:32px 44px;line-height:1.55;}pre{white-space:pre-wrap;font-family:inherit;font-size:14px;}</style></head><body><pre>${esc}</pre><script>window.onload=()=>window.print();</script></body></html>`,
    );
    win.document.close();
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/45 backdrop-blur-2xs p-3 sm:p-5 no-print animate-in fade-in duration-150"
      onClick={onClose}
    >
      <div
        role="dialog"
        aria-label="Đi buồng Nội trú TT 32/2023 & Sổ Bàn giao Ca trực"
        onClick={(e) => e.stopPropagation()}
        className="w-full max-w-6xl max-h-[90vh] rounded-2xl bg-white border border-[#BAE6FD] shadow-2xl flex flex-col overflow-hidden text-left font-sans"
      >
        {/* Đầu modal & Chuyển Tab */}
        <div className="px-5 py-3.5 border-b border-[#BAE6FD] bg-gradient-to-r from-[#F0F9FF] via-white to-[#F8FBFC] flex flex-wrap items-center justify-between gap-3 flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-[#0284C7] text-white flex items-center justify-center shadow-tactile-doctor flex-shrink-0">
              <Stethoscope size={18} />
            </div>
            <div>
              <h2 className="font-serif text-[17.5px] font-semibold text-[#0F172A]">
                Đi buồng Nội trú (Thông tư 32/2023/TT-BYT) & Bàn giao Ca trực Toàn khoa
              </h2>
              <p className="text-[11px] text-[#64748B]">
                Đối chiếu diễn biến ngày hôm trước ↔ hôm nay và gom bảng SBAR bàn giao trực theo phân tầng nguy cơ
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <div className="inline-flex p-1 rounded-xl bg-[#E0F2FE]/70 border border-[#BAE6FD] text-xs">
              <button
                type="button"
                onClick={() => setTabCon("to_dieu_tri")}
                className={`px-3 py-1.5 rounded-lg font-semibold transition-all cursor-pointer ${
                  tabCon === "to_dieu_tri"
                    ? "bg-white text-[#0369A1] shadow-sm"
                    : "text-[#475569] hover:text-[#0369A1]"
                }`}
              >
                Tờ điều trị (Mẫu BV-01/BV2)
              </button>
              <button
                type="button"
                onClick={() => setTabCon("ban_giao_truc")}
                className={`px-3 py-1.5 rounded-lg font-semibold transition-all cursor-pointer flex items-center gap-1.5 ${
                  tabCon === "ban_giao_truc"
                    ? "bg-white text-[#0369A1] shadow-sm"
                    : "text-[#475569] hover:text-[#0369A1]"
                }`}
              >
                <Users size={13} />
                <span>Sổ Bàn giao Ca trực ({soBanGiao.length})</span>
              </button>
            </div>
            <button
              type="button"
              onClick={onClose}
              className="p-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-600 cursor-pointer"
            >
              <X size={16} />
            </button>
          </div>
        </div>

        {/* Thân modal */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-5 bg-[#F8FBFC] space-y-4">
          {tabCon === "to_dieu_tri" ? (
            <>
              {/* Thanh chọn phiên khám hôm trước để đối chiếu */}
              <div className="rounded-xl border border-[#BAE6FD] bg-white p-3.5 flex flex-wrap items-center justify-between gap-3 text-xs">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-bold text-[#0C4A6E]">Đối chiếu diễn biến so với phiên trước:</span>
                  <select
                    value={phienTruocId}
                    onChange={(e) => setPhienTruocId(e.target.value)}
                    className="px-3 py-1.5 rounded-xl border border-[#BAE6FD] bg-[#F8FBFC] text-[#0F172A] font-medium focus:outline-none focus:ring-1 focus:ring-[#0284C7]"
                  >
                    <option value="">-- Lần đi buồng đầu tiên (chưa chọn ca trước) --</option>
                    {cacPhienKhac.map((s) => (
                      <option key={s.id} value={s.id}>
                        {s.patientIdentifier || `Ca #${s.id.slice(0, 6)}`} · {s.date} {s.time}
                      </option>
                    ))}
                  </select>
                </div>
                <button
                  type="button"
                  onClick={() => void goiApiWardRoundDiff()}
                  disabled={dangTaiDiff || !phienTruoc}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-[#BAE6FD] bg-[#F0F9FF] hover:bg-[#E0F2FE] disabled:opacity-40 text-[#0369A1] font-semibold cursor-pointer"
                >
                  <RefreshCw size={13} className={dangTaiDiff ? "animate-spin" : ""} />
                  <span>Tính lại diễn biến</span>
                </button>
              </div>

              {/* Tờ điều trị 2 cột chuẩn Mẫu BV-01/BV2 — TT 32/2023/TT-BYT */}
              <div className="rounded-2xl border border-[#BAE6FD] bg-white shadow-tactile-doctor-card overflow-hidden">
                <div className="px-5 py-3 border-b border-slate-200 bg-white text-center">
                  <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                    Biểu mẫu Hồ sơ Bệnh án Nội trú · Thông tư 32/2023/TT-BYT (Mẫu BV-01/BV2)
                  </div>
                  <h3 className="font-serif text-lg font-bold text-[#0F172A] mt-0.5">TỜ ĐIỀU TRỊ</h3>
                  <div className="text-xs text-slate-600 mt-0.5">
                    Họ tên người bệnh: <strong>{tenBn}</strong>
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-xs border-collapse min-w-[760px]">
                    <thead>
                      <tr className="bg-[#F0F9FF] text-[#0C4A6E] border-b-2 border-[#BAE6FD]">
                        <th className="py-2.5 px-3.5 font-bold border-r border-[#BAE6FD] w-40 text-center">
                          NGÀY, GIỜ
                        </th>
                        <th className="py-2.5 px-4 font-bold border-r border-[#BAE6FD] w-[46%] text-left">
                          DIỄN BIẾN BỆNH (Đỡ/Hết · Mới xuất hiện · Sinh hiệu & CLS)
                        </th>
                        <th className="py-2.5 px-4 font-bold text-left">
                          Y LỆNH ĐIỀU TRỊ & CHĂM SÓC (Thuốc duy trì · Thuốc đổi/mới)
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr className="align-top">
                        <td className="p-3.5 border-r border-slate-200 font-mono text-[11.5px] text-slate-700 text-center">
                          <div className="inline-flex items-center gap-1 font-bold text-[#0369A1]">
                            <Clock size={12} />
                            <span>{dienBien.ngayGio}</span>
                          </div>
                        </td>

                        {/* Cột Diễn biến bệnh */}
                        <td className="p-4 border-r border-slate-200 space-y-3 leading-relaxed">
                          {dienBien.trieuChungDoHet.length > 0 && (
                            <div className="space-y-1">
                              <div className="font-bold text-[#0D6B50] flex items-center gap-1">
                                <CheckCircle2 size={13} />
                                <span>Triệu chứng giảm / đỡ / âm tính:</span>
                              </div>
                              <ul className="list-disc pl-4 space-y-0.5 text-[#0F172A]">
                                {dienBien.trieuChungDoHet.map((d, i) => (
                                  <li key={i}>{d}</li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {dienBien.trieuChungMoiHoacNangLen.length > 0 && (
                            <div className="space-y-1">
                              <div className="font-bold text-[#B45309] flex items-center gap-1">
                                <Activity size={13} />
                                <span>Triệu chứng hiện tại / mới xuất hiện:</span>
                              </div>
                              <ul className="list-disc pl-4 space-y-0.5 text-[#0F172A]">
                                {dienBien.trieuChungMoiHoacNangLen.map((d, i) => (
                                  <li key={i}>{d}</li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {dienBien.sinhHieuVaKham.length > 0 && (
                            <div className="space-y-1">
                              <div className="font-bold text-[#0369A1]">Sinh hiệu & Khám thực thể / CLS:</div>
                              <ul className="list-disc pl-4 space-y-0.5 text-[#0F172A]">
                                {dienBien.sinhHieuVaKham.map((d, i) => (
                                  <li key={i}>{d}</li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {dienBien.trieuChungDoHet.length === 0 &&
                            dienBien.trieuChungMoiHoacNangLen.length === 0 &&
                            dienBien.sinhHieuVaKham.length === 0 && (
                              <p className="text-amber-800 bg-[#FEF9E7] border border-dashed border-amber-400 rounded-lg p-2.5">
                                [cần bổ sung diễn biến đi buồng hôm nay]
                              </p>
                            )}
                        </td>

                        {/* Cột Y lệnh điều trị */}
                        <td className="p-4 space-y-3 leading-relaxed">
                          {dienBien.yLenhDuyTri.length > 0 && (
                            <div className="space-y-1">
                              <div className="font-bold text-[#0D6B50]">1. Thuốc duy trì theo phác đồ:</div>
                              <ul className="list-disc pl-4 space-y-0.5 text-[#0F172A]">
                                {dienBien.yLenhDuyTri.map((y, i) => (
                                  <li key={i}>{y}</li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {dienBien.yLenhMoiHoacDoi.length > 0 && (
                            <div className="space-y-1">
                              <div className="font-bold text-[#0284C7]">2. Y lệnh thuốc mới / điều chỉnh liều:</div>
                              <ul className="list-disc pl-4 space-y-0.5 text-[#0F172A]">
                                {dienBien.yLenhMoiHoacDoi.map((y, i) => (
                                  <li key={i}>{y}</li>
                                ))}
                              </ul>
                            </div>
                          )}

                          <div className="space-y-1">
                            <div className="font-bold text-slate-700">3. Chăm sóc & Dinh dưỡng:</div>
                            <ul className="list-disc pl-4 space-y-0.5 text-slate-700">
                              {dienBien.cheDoChamSocDinhDuong.map((c, i) => (
                                <li key={i}>{c}</li>
                              ))}
                            </ul>
                          </div>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          ) : (
            /* TAB 2: SỔ BÀN GIAO CA TRỰC TOÀN KHOA (MULTI-PATIENT SBAR) */
            <div className="space-y-3">
              <div className="rounded-xl border border-[#BAE6FD] bg-white p-3.5 flex flex-wrap items-center justify-between gap-2 text-xs">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-[#0C4A6E]">
                    Danh sách bệnh nhân bàn giao trực (tự động ưu tiên ca có cảnh báo đỏ lên đầu):
                  </span>
                </div>
                <label className="inline-flex items-center gap-1.5 text-xs font-medium text-[#334155] cursor-pointer">
                  <input
                    type="checkbox"
                    checked={chiHomNay}
                    onChange={(e) => setChiHomNay(e.target.checked)}
                    className="rounded border-slate-300 text-[#0284C7]"
                  />
                  <span>Chỉ lọc ca ghi nhận trong ngày hôm nay</span>
                </label>
              </div>

              {soBanGiao.length === 0 ? (
                <div className="rounded-2xl border border-[#BAE6FD] bg-white p-8 text-center text-xs text-slate-500">
                  Không có ca khám nào khớp bộ lọc hiện tại. Bỏ chọn “Chỉ lọc ca ghi nhận trong ngày hôm nay” để xem toàn bộ ca đang theo dõi.
                </div>
              ) : (
                <div className="rounded-2xl border border-[#BAE6FD] bg-white shadow-tactile-doctor-card overflow-hidden">
                  <div className="overflow-x-auto">
                    <table className="w-full text-xs border-collapse min-w-[920px]">
                      <thead>
                        <tr className="bg-[#F0F9FF] text-[#0C4A6E] border-b border-[#BAE6FD] text-left">
                          <th className="py-2.5 px-3 font-bold w-44">Người bệnh & Giờ khám</th>
                          <th className="py-2.5 px-3 font-bold w-36">Phân tầng Trực</th>
                          <th className="py-2.5 px-3 font-bold">S — Diễn biến hiện tại</th>
                          <th className="py-2.5 px-3 font-bold">B — Tiền sử & Dị ứng</th>
                          <th className="py-2.5 px-3 font-bold">A — Chẩn đoán & Cảnh báo</th>
                          <th className="py-2.5 px-3 font-bold">R — Y lệnh ca trực sau</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {soBanGiao.map((m) => (
                          <tr
                            key={m.sessionId}
                            className={
                              m.mucUuTien === "NGUY_KICH"
                                ? "bg-[#FFF5F5]"
                                : m.mucUuTien === "CAN_THEO_DOI"
                                ? "bg-[#FEF9E7]/50"
                                : "bg-white"
                            }
                          >
                            <td className="p-3 align-top">
                              <div className="font-bold text-[#0F172A]">{m.tenBenhNhan}</div>
                              <div className="text-[10.5px] text-slate-500 mt-0.5">{m.thoiGian}</div>
                            </td>
                            <td className="p-3 align-top space-y-1">
                              <span
                                className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold ${
                                  m.mucUuTien === "NGUY_KICH"
                                    ? "bg-red-600 text-white"
                                    : m.mucUuTien === "CAN_THEO_DOI"
                                    ? "bg-amber-100 text-amber-900 border border-amber-300"
                                    : "bg-emerald-100 text-emerald-800"
                                }`}
                              >
                                {m.mucUuTien === "NGUY_KICH" ? (
                                  <>
                                    <AlertTriangle size={10} /> NGUY KỊCH
                                  </>
                                ) : m.mucUuTien === "CAN_THEO_DOI" ? (
                                  "CẦN THEO DÕI"
                                ) : (
                                  "ỔN ĐỊNH"
                                )}
                              </span>
                              {m.lyDoRuiRo.map((ld, idx) => (
                                <div key={idx} className="text-[10.5px] text-[#B4232C] font-medium">
                                  • {ld}
                                </div>
                              ))}
                            </td>
                            <td className="p-3 align-top text-slate-800 leading-snug">{m.situation}</td>
                            <td className="p-3 align-top text-slate-700 leading-snug">{m.background}</td>
                            <td className="p-3 align-top text-slate-800 font-medium leading-snug">{m.assessment}</td>
                            <td className="p-3 align-top text-[#0369A1] font-medium leading-snug">
                              {m.recommendation}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Chân modal */}
        <div className="px-5 py-3 border-t border-[#BAE6FD] bg-white flex flex-wrap items-center justify-between gap-2 flex-shrink-0">
          <span className="text-[11px] text-[#64748B]">
            Mọi mục diễn biến và y lệnh đều trích xuất tất định từ mệnh đề đã loại trừ mục Bỏ — bác sĩ kiểm tra trước khi ký tờ điều trị.
          </span>
          <div className="flex flex-wrap items-center gap-2">
            <button
              type="button"
              onClick={saoChepHienTai}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-[#BAE6FD] bg-white hover:bg-[#F0F9FF] text-[#0C4A6E] text-xs font-semibold cursor-pointer"
            >
              {daChep ? <Check size={13} className="text-[#0D9488]" /> : <Copy size={13} className="text-[#0284C7]" />}
              <span>
                {daChep
                  ? "Đã chép ✓"
                  : tabCon === "to_dieu_tri"
                  ? "Sao chép Tờ điều trị"
                  : "Sao chép Sổ Bàn giao Toàn khoa"}
              </span>
            </button>

            <button
              type="button"
              onClick={inNoiDungHienTai}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-[#0D9488] bg-[#F0FDF4] hover:bg-[#DCFCE7] text-[#0D9488] text-xs font-semibold cursor-pointer"
            >
              <Printer size={13} />
              <span>{tabCon === "to_dieu_tri" ? "In Tờ điều trị" : "In Sổ Bàn giao"}</span>
            </button>

            {onCreateTab && (
              <button
                type="button"
                onClick={() => {
                  if (tabCon === "to_dieu_tri") {
                    onCreateTab("Tờ điều trị TT32", vanBanToDieuTri);
                  } else {
                    onCreateTab("Sổ bàn giao trực", vanBanSoBanGiao);
                  }
                  onClose();
                }}
                className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-[#0284C7] hover:bg-[#0369A1] text-white text-xs font-semibold shadow-tactile-doctor cursor-pointer"
              >
                <Plus size={13} />
                <span>
                  {tabCon === "to_dieu_tri" ? "Đưa sang Tab Tờ điều trị" : "Đưa sang Tab Bàn giao trực"}
                </span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
