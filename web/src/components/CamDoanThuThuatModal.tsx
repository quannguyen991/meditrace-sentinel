import React, { useCallback, useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  Check,
  CheckCircle2,
  Copy,
  FileText,
  Lock,
  Printer,
  Quote,
  RefreshCw,
  ShieldCheck,
  X,
} from "lucide-react";
import { sha256HexSync, tachLuot } from "../lib/compileEffectiveNote";
import type { NoteMeta, Proposition, Quyet } from "./VerificationView";

export interface TruCotCamDoan {
  stt: number;
  ma: string;
  tieuDe: string;
  moTaLuat: string;
  daGiaiThich: boolean;
  luot: number[];
  trichDan: string;
  noiDungTomTat: string;
}

interface CamDoanThuThuatModalProps {
  open: boolean;
  onClose: () => void;
  sessionId?: string;
  patientName?: string;
  patientInfo?: Record<string, unknown>;
  transcript?: string;
  noteMeta?: NoteMeta | null;
  quyetDuyet?: Record<number, Quyet>;
  banSuaDuyet?: Record<number, string>;
  onCreateConsentTab?: (title: string, content: string) => void;
}

const SAU_TRU_COT_LUAT_KBCB_2023: Array<{
  stt: number;
  ma: string;
  khoaBackend: string[];
  tieuDe: string;
  moTaLuat: string;
  mauTimLuot: RegExp;
}> = [
  {
    stt: 1,
    ma: "chan_doan_tinh_trang",
    khoaBackend: ["chan_doan", "tinh_trang_benh", "chan_doan_tinh_trang"],
    tieuDe: "1. Chẩn đoán / Tình trạng bệnh cần can thiệp",
    moTaLuat: "Điều 10 & Khoản 1 Điều 63 Luật KBCB 2023: Giải thích rõ chẩn đoán và mức độ bệnh lý cần can thiệp.",
    mauTimLuot: /\b(?:chẩn đoán|tình trạng|bị\s+viêm|tắc|hẹp|sỏi|u\s+|xuất huyết|nhồi máu|cần\s+phải\s+làm|chỉ định)\b/i,
  },
  {
    stt: 2,
    ma: "phuong_phap_pttt",
    khoaBackend: ["phuong_phap_thu_thuat", "phuong_phap", "phuong_phap_pttt", "thu_thuat", "can_thiep"],
    tieuDe: "2. Phương pháp thủ thuật / phẫu thuật / tiêm cản quang",
    moTaLuat: "Giải thích cụ thể phương pháp thực hiện, gây tê/gây mê hoặc tiêm thuốc cản quang tĩnh mạch.",
    mauTimLuot: /\b(?:nội soi|phẫu thuật|mổ|tiểu phẫu|chọc dò|sinh thiết|đặt\s+stent|can thiệp|chụp\s+ct\s+có\s+thuốc|tiêm\s+(?:thuốc\s+)?cản quang|gây tê|gây mê)\b/i,
  },
  {
    stt: 3,
    ma: "nguy_co_tai_bien",
    khoaBackend: ["nguy_co", "nguy_co_tai_bien", "tai_bien", "rui_ro"],
    tieuDe: "3. Nguy cơ, tai biến, phản vệ có thể xảy ra",
    moTaLuat: "Thông báo trung thực tỷ lệ/khả năng tai biến, chảy máu, nhiễm trùng, sốc phản vệ thuốc tê/cản quang.",
    mauTimLuot: /\b(?:tai biến|biến chứng|nguy cơ|phản vệ|sốc phản vệ|dị ứng thuốc cản quang|chảy máu|thủng|tác dụng phụ|rủi ro)\b/i,
  },
  {
    stt: 4,
    ma: "phuong_an_thay_the",
    khoaBackend: ["phuong_an_thay_the", "thay_the", "lua_chon_khac"],
    tieuDe: "4. Phương án điều trị thay thế",
    moTaLuat: "Trình bày các phương pháp điều trị bảo tồn hoặc kỹ thuật thay thế khác kèm ưu/nhược điểm.",
    mauTimLuot: /\b(?:phương án khác|thay thế|điều trị nội khoa|uống thuốc bảo tồn|theo dõi thêm|cách khác|lựa chọn khác)\b/i,
  },
  {
    stt: 5,
    ma: "hau_qua_tu_choi",
    khoaBackend: ["hau_qua_tu_choi", "hau_qua_cham_tre", "neu_khong_lam"],
    tieuDe: "5. Hậu quả nếu từ chối hoặc chậm trễ",
    moTaLuat: "Cảnh báo rõ diễn biến xấu hoặc nguy hiểm tính mạng nếu trì hoãn/từ chối thủ thuật.",
    mauTimLuot: /\b(?:nếu không làm|nếu từ chối|để muộn|chậm trễ|vỡ|hoại tử|nguy hiểm tính mạng|nặng thêm|biến chứng nặng)\b/i,
  },
  {
    stt: 6,
    ma: "xac_nhan_dong_y",
    khoaBackend: ["xac_nhan_dong_y", "dong_y", "benh_nhan_dong_y"],
    tieuDe: "6. Xác nhận hiểu rõ & đồng ý của Người bệnh / Người đại diện",
    moTaLuat: "Người bệnh hoặc người đại diện hợp pháp xác nhận đã hiểu, đặt câu hỏi xong và tự nguyện đồng ý.",
    mauTimLuot: /\b(?:đồng ý làm|nhất trí|chấp nhận làm|hiểu rõ rồi|vâng bác sĩ cho làm|gia đình đồng ý|tôi đồng ý)\b/i,
  },
];

/**
 * Phân tích tất định 6 trụ cột Điều 10 & 63 Luật KBCB 2023 từ hội thoại + mệnh đề hiệu lực
 * (và hợp nhất kết quả từ backend `/api/clinical/informed-consent` hoặc `clinicalSafety.cam_doan_thu_thuat` nếu có).
 * Tuyệt đối KHÔNG tự bịa sự đồng ý của người bệnh khi hội thoại chưa có!
 */
export function phanTichCamDoanThuThuatDeterministic(
  transcript: string,
  propositions: Proposition[],
  quyetDuyet: Record<number, Quyet>,
  banSuaDuyet: Record<number, string>,
  duLieuBackend?: any,
): TruCotCamDoan[] {
  const dsLuot = tachLuot(transcript);
  const propsHieuLuc = (propositions || [])
    .filter((p) => quyetDuyet[p.id] !== "bo")
    .map((p) => ({
      ...p,
      vanBan: (quyetDuyet[p.id] === "sua" && banSuaDuyet[p.id]?.trim() ? banSuaDuyet[p.id].trim() : p.text || "").trim(),
    }));

  const mangBackend: any[] = Array.isArray(duLieuBackend?.cac_muc_kiem_chung)
    ? duLieuBackend.cac_muc_kiem_chung
    : Array.isArray(duLieuBackend?.cac_tru_cot)
    ? duLieuBackend.cac_tru_cot
    : Array.isArray(duLieuBackend?.pillars)
    ? duLieuBackend.pillars
    : Array.isArray(duLieuBackend?.muc_cam_doan)
    ? duLieuBackend.muc_cam_doan
    : [];

  return SAU_TRU_COT_LUAT_KBCB_2023.map((khung, idx) => {
    // 1. Kiểm tra dữ liệu backend trả về cho trụ cột này
    let mucBe: any =
      mangBackend.find((x) => khung.khoaBackend.includes(String(x?.ma || x?.id || ""))) || mangBackend[idx];
    if (!mucBe && duLieuBackend?.chi_tiet_theo_ma && typeof duLieuBackend.chi_tiet_theo_ma === "object") {
      for (const k of khung.khoaBackend) {
        if (duLieuBackend.chi_tiet_theo_ma[k]) {
          mucBe = duLieuBackend.chi_tiet_theo_ma[k];
          break;
        }
      }
    }
    if (!mucBe && duLieuBackend && typeof duLieuBackend === "object") {
      for (const k of khung.khoaBackend) {
        if (duLieuBackend[k] && typeof duLieuBackend[k] === "object") {
          mucBe = duLieuBackend[k];
          break;
        }
      }
    }

    if (mucBe) {
      const daCo = Boolean(
        mucBe.da_giai_thich ??
          mucBe.verified ??
          mucBe.hop_le ??
          (Array.isArray(mucBe.luot_can_cu) && mucBe.luot_can_cu.length > 0) ??
          (Array.isArray(mucBe.luot) && mucBe.luot.length > 0),
      );
      const luotBe: number[] = Array.isArray(mucBe.luot_can_cu)
        ? mucBe.luot_can_cu
        : Array.isArray(mucBe.luot)
        ? mucBe.luot
        : Array.isArray(mucBe.bang_chung)
        ? mucBe.bang_chung
        : typeof mucBe.luot === "number"
        ? [mucBe.luot]
        : [];
      const chuoiTrichDan = Array.isArray(mucBe.trich_dan)
        ? mucBe.trich_dan.filter(Boolean).join(" | ")
        : String(mucBe.trich_dan || mucBe.quote || mucBe.noi_dung || "");
      if (daCo) {
        return {
          stt: khung.stt,
          ma: khung.ma,
          tieuDe: khung.tieuDe,
          moTaLuat: khung.moTaLuat,
          daGiaiThich: true,
          luot: luotBe,
          trichDan: chuoiTrichDan,
          noiDungTomTat: String(mucBe.noi_dung || mucBe.tom_tat || chuoiTrichDan),
        };
      }
      // Nếu backend đã kiểm tra rõ và khẳng định chưa giải thích (VD: bác sĩ tự nói đồng ý thay BN, hoặc BN từ chối)
      // thì tôn trọng tuyệt đối kết quả chặn an toàn pháp lý của backend!
      if (mucBe.da_giai_thich === false) {
        return {
          stt: khung.stt,
          ma: khung.ma,
          tieuDe: khung.tieuDe,
          moTaLuat: mucBe.canh_bao_thieu ? String(mucBe.canh_bao_thieu) : khung.moTaLuat,
          daGiaiThich: false,
          luot: [],
          trichDan: "",
          noiDungTomTat: "",
        };
      }
    }

    // 2. Đối chiếu tất định trên mệnh đề & lời thoại gốc
    if (khung.stt === 1) {
      const propCd = propsHieuLuc.find((p) => /CHẨN ĐOÁN|ĐÁNH GIÁ/i.test(p.section || "") && !p.negated);
      if (propCd) {
        return {
          stt: khung.stt,
          ma: khung.ma,
          tieuDe: khung.tieuDe,
          moTaLuat: khung.moTaLuat,
          daGiaiThich: true,
          luot: propCd.evidenceTurns || [],
          trichDan: propCd.quotes?.[0] || propCd.vanBan,
          noiDungTomTat: propCd.vanBan,
        };
      }
    }

    // Quét lượt thoại: trụ cột 1..5 ưu tiên lượt Bác sĩ giải thích; trụ cột 6 bắt buộc lượt Bệnh nhân / Người nhà nói!
    const luotKhop = dsLuot.find((l) => {
      const vaiThap = (l.vai || "").toLowerCase();
      if (khung.stt === 6) {
        const laBenhNhanHoacNguoiNha =
          !vaiThap || vaiThap.includes("bệnh nhân") || vaiThap.includes("người nhà") || !vaiThap.includes("bác sĩ");
        return laBenhNhanHoacNguoiNha && khung.mauTimLuot.test(l.chu);
      }
      const laBacSi = !vaiThap || vaiThap.includes("bác sĩ") || vaiThap.includes("bs");
      return laBacSi && khung.mauTimLuot.test(l.chu);
    });

    if (luotKhop) {
      return {
        stt: khung.stt,
        ma: khung.ma,
        tieuDe: khung.tieuDe,
        moTaLuat: khung.moTaLuat,
        daGiaiThich: true,
        luot: [luotKhop.so],
        trichDan: luotKhop.chu,
        noiDungTomTat: luotKhop.chu,
      };
    }

    return {
      stt: khung.stt,
      ma: khung.ma,
      tieuDe: khung.tieuDe,
      moTaLuat: khung.moTaLuat,
      daGiaiThich: false,
      luot: [],
      trichDan: "",
      noiDungTomTat: "",
    };
  });
}

export function sinhVanBanPhieuCamDoanPttt(params: {
  patientName: string;
  sessionId: string;
  truCot: TruCotCamDoan[];
  boSungBacSi: Record<string, string>;
  wormHash: string | null;
  wormSeq: number | string | null;
  stampedAt: string | null;
}): string {
  const { patientName, sessionId, truCot, boSungBacSi, wormHash, wormSeq, stampedAt } = params;
  const ngayHienTai = new Date().toLocaleDateString("vi-VN");
  const dongTruCot = truCot.map((tc) => {
    const luotTag = tc.luot.length > 0 ? ` [T${tc.luot.join(", T")}]` : "";
    const noiDung = tc.daGiaiThich
      ? `${tc.noiDungTomTat}${luotTag}`
      : boSungBacSi[tc.ma]?.trim()
      ? `[Bác sĩ giải thích trực tiếp tại bàn khám]: ${boSungBacSi[tc.ma].trim()}`
      : "[cần bổ sung — bác sĩ giải thích trực tiếp và ghi nhận trước khi ký]";
    return `${tc.tieuDe}\n   - Nội dung ghi nhận: ${noiDung}`;
  });

  return [
    "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM",
    "Độc lập - Tự do - Hạnh phúc",
    "--------------------------------------------------",
    "PHIẾU CAM ĐOAN CHẤP THUẬN PHẪU THUẬT, THỦ THUẬT & CAN THIỆP XÂM LẤN",
    "(Căn cứ Điều 10 & Điều 63 Luật Khám bệnh, chữa bệnh số 15/2023/QH15)",
    "",
    `Họ và tên người bệnh: ${patientName || "[Họ tên người bệnh]"}`,
    `Mã hồ sơ / ca khám: ${sessionId || "[Mã ca khám]"} | Ngày lập: ${ngayHienTai}`,
    "",
    "I. NỘI DUNG TƯ VẤN & GIẢI THÍCH CỦA BÁC SĨ (6 TRỤ CỘT BẮT BUỘC):",
    ...dongTruCot,
    "",
    "II. CAM ĐOAN CỦA NGƯỜI BỆNH / NGƯỜI ĐẠI DIỆN HỢP PHÁP:",
    "Tôi xác nhận đã được Bác sĩ giải thích rõ ràng, dễ hiểu toàn bộ 6 nội dung nêu trên, đã được giải đáp mọi thắc mắc và hoàn toàn tự nguyện đồng ý thực hiện thủ thuật / phẫu thuật / tiêm thuốc cản quang.",
    "",
    `Người bệnh / Đại diện ký tên: ______________________     Bác sĩ tư vấn ký tên: ______________________`,
    ...(wormHash
      ? [
          "",
          `[NIÊM PHONG KIỂM TOÁN WORM SHA-256${wormSeq ? ` #${wormSeq}` : ""}]: ${wormHash}`,
          `Thời điểm đóng dấu: ${stampedAt || new Date().toISOString()}`,
        ]
      : []),
  ].join("\n");
}

export const CamDoanThuThuatModal: React.FC<CamDoanThuThuatModalProps> = ({
  open,
  onClose,
  sessionId = "",
  patientName = "Người bệnh",
  patientInfo,
  transcript = "",
  noteMeta,
  quyetDuyet = {},
  banSuaDuyet = {},
  onCreateConsentTab,
}) => {
  const [dangTai, setDangTai] = useState(false);
  const [dangDongDauWorm, setDangDongDauWorm] = useState(false);
  const [duLieuServer, setDuLieuServer] = useState<any>(null);
  const [boSungBacSi, setBoSungBacSi] = useState<Record<string, string>>({});
  const [wormStamp, setWormStamp] = useState<{
    hash: string;
    seq: number | string | null;
    stampedAt: string;
  } | null>(null);
  const [daChep, setDaChep] = useState(false);
  const [hienXemTruocPhieu, setHienXemTruocPhieu] = useState(false);

  const activePropositions = useMemo(
    () =>
      (noteMeta?.propositions || [])
        .filter((p) => quyetDuyet[p.id] !== "bo")
        .map((p) =>
          quyetDuyet[p.id] === "sua" && banSuaDuyet[p.id]?.trim()
            ? { ...p, text: banSuaDuyet[p.id].trim() }
            : p,
        ),
    [noteMeta?.propositions, quyetDuyet, banSuaDuyet],
  );

  const lamMoiTuApi = useCallback(async () => {
    setDangTai(true);
    try {
      const r = await fetch("/api/clinical/informed-consent", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sessionId: sessionId || noteMeta?.caseId || "ca_kham",
          propositions: activePropositions,
          transcript,
          thong_tin_benh_nhan: patientInfo || null,
          stampWorm: false,
        }),
      });
      if (r.ok) {
        setDuLieuServer(await r.json());
      }
    } catch {
      // Fallback tất định từ noteMeta.clinicalSafety.cam_doan_thu_thuat & hội thoại tại chỗ
    } finally {
      setDangTai(false);
    }
  }, [sessionId, noteMeta?.caseId, activePropositions, transcript, patientInfo]);

  useEffect(() => {
    if (open) {
      void lamMoiTuApi();
    }
  }, [open, lamMoiTuApi]);

  const truCot = useMemo(
    () =>
      phanTichCamDoanThuThuatDeterministic(
        transcript,
        noteMeta?.propositions || [],
        quyetDuyet,
        banSuaDuyet,
        duLieuServer || noteMeta?.clinicalSafety?.cam_doan_thu_thuat,
      ),
    [transcript, noteMeta?.propositions, quyetDuyet, banSuaDuyet, duLieuServer, noteMeta?.clinicalSafety],
  );

  const soTruCotDat = truCot.filter((t) => t.daGiaiThich || Boolean(boSungBacSi[t.ma]?.trim())).length;

  const vanBanPhieu = useMemo(
    () =>
      sinhVanBanPhieuCamDoanPttt({
        patientName,
        sessionId: sessionId || noteMeta?.caseId || "MT-CONSENT",
        truCot,
        boSungBacSi,
        wormHash: wormStamp?.hash || null,
        wormSeq: wormStamp?.seq ?? null,
        stampedAt: wormStamp?.stampedAt || null,
      }),
    [patientName, sessionId, noteMeta?.caseId, truCot, boSungBacSi, wormStamp],
  );

  if (!open) return null;

  const dongDauWormVaXuatPhieu = async () => {
    setDangDongDauWorm(true);
    try {
      let hashTuServer: string | null = null;
      let seqTuServer: number | string | null = null;
      let thoiGianServer = new Date().toISOString();

      try {
        const r = await fetch("/api/clinical/informed-consent", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            sessionId: sessionId || noteMeta?.caseId || "ca_kham",
            propositions: activePropositions,
            transcript,
            thong_tin_benh_nhan: patientInfo || null,
            doctorNotes: boSungBacSi,
            stampWorm: true,
          }),
        });
        if (r.ok) {
          const kq = await r.json();
          setDuLieuServer(kq);
          hashTuServer = kq.consentHash || kq.worm_hash || kq.wormHash || kq.hash || null;
          seqTuServer = kq.worm_seq ?? kq.wormSeq ?? "WORM-CONSENT";
          if (kq.checkedAt || kq.stampedAt || kq.thoi_gian) {
            thoiGianServer = String(kq.checkedAt || kq.stampedAt || kq.thoi_gian);
          }
        }
      } catch {
        // Offline deterministic SHA-256 WORM fallback
      }

      const bamDuPhong = sha256HexSync(
        JSON.stringify({
          sessionId: sessionId || noteMeta?.caseId || "ca_kham",
          truCot,
          boSungBacSi,
          thoiGianServer,
        }),
      );
      const dauMoi = {
        hash: hashTuServer || bamDuPhong,
        seq: seqTuServer ?? "LOCAL-SHA256",
        stampedAt: thoiGianServer,
      };
      setWormStamp(dauMoi);
      setHienXemTruocPhieu(true);

      const banPhieuCoDau = sinhVanBanPhieuCamDoanPttt({
        patientName,
        sessionId: sessionId || noteMeta?.caseId || "MT-CONSENT",
        truCot,
        boSungBacSi,
        wormHash: dauMoi.hash,
        wormSeq: dauMoi.seq,
        stampedAt: dauMoi.stampedAt,
      });

      if (onCreateConsentTab) {
        onCreateConsentTab("Phiếu Cam đoan PTTT", banPhieuCoDau);
      }
    } finally {
      setDangDongDauWorm(false);
    }
  };

  const inTrucTiepPhieuCamDoan = () => {
    const win = window.open("", "_blank", "width=860,height=920");
    if (!win) return;
    const escaped = vanBanPhieu
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
    win.document.write(
      `<!doctype html><html lang="vi"><head><meta charset="utf-8"/><title>Phiếu Cam Đoan PTTT — ${patientName}</title>` +
        `<style>body{font-family:"Times New Roman",serif;padding:36px 48px;line-height:1.55;color:#0f172a;}pre{white-space:pre-wrap;font-family:inherit;font-size:14px;}</style>` +
        `</head><body><pre>${escaped}</pre><script>window.onload=()=>window.print();</script></body></html>`,
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
        aria-label="Cam đoan Thủ thuật & Phẫu thuật Luật KBCB 2023"
        onClick={(e) => e.stopPropagation()}
        className="w-full max-w-4xl max-h-[90vh] rounded-2xl bg-white border border-[#BAE6FD] shadow-2xl flex flex-col overflow-hidden text-left font-sans"
      >
        {/* Đầu modal */}
        <div className="px-5 py-3.5 border-b border-[#BAE6FD] bg-gradient-to-r from-[#F0F9FF] via-white to-[#F8FBFC] flex items-center justify-between gap-3 flex-shrink-0">
          <div className="flex items-center gap-3 min-w-0">
            <div className="w-9 h-9 rounded-xl bg-[#0D9488] text-white flex items-center justify-center shadow-sm flex-shrink-0">
              <ShieldCheck size={18} />
            </div>
            <div className="min-w-0">
              <h2 className="font-serif text-[17.5px] font-semibold text-[#0F172A] truncate">
                Kiểm định Tư vấn & Cam đoan Thủ thuật / Phẫu thuật (Điều 10 & 63 Luật KBCB 2023)
              </h2>
              <p className="text-[11.5px] text-[#475569]">
                Người bệnh: <strong className="text-[#0369A1]">{patientName}</strong> · Đã có căn cứ:{" "}
                <strong className={soTruCotDat === 6 ? "text-[#0D6B50]" : "text-[#B45309]"}>{soTruCotDat}/6</strong> trụ cột pháp lý bắt buộc
              </p>
            </div>
          </div>
          <div className="flex items-center gap-1.5">
            <button
              type="button"
              onClick={() => void lamMoiTuApi()}
              disabled={dangTai}
              title="Làm mới đối soát từ lời thoại"
              className="p-1.5 rounded-xl border border-[#BAE6FD] bg-white hover:bg-[#F0F9FF] text-[#0284C7] cursor-pointer"
            >
              <RefreshCw size={14} className={dangTai ? "animate-spin" : ""} />
            </button>
            <button
              type="button"
              onClick={onClose}
              className="p-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-600 cursor-pointer"
            >
              <X size={16} />
            </button>
          </div>
        </div>

        {/* Nội dung cuộn */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-5 space-y-3.5 bg-[#F8FBFC]">
          {/* Banner WORM nếu đã đóng dấu */}
          {wormStamp && (
            <div className="rounded-xl border border-[#A7E3C9] bg-[#F3FBF7] p-3 flex flex-wrap items-center justify-between gap-2 text-xs text-[#0D6B50]">
              <div className="flex items-center gap-2 font-semibold">
                <Lock size={14} />
                <span>Đã đóng dấu kiểm toán WORM SHA-256 ({wormStamp.seq}):</span>
                <code className="font-mono text-[11px] bg-white px-2 py-0.5 rounded border border-[#A7E3C9]">
                  {wormStamp.hash.slice(0, 24)}...
                </code>
              </div>
              <button
                type="button"
                onClick={() => setHienXemTruocPhieu((v) => !v)}
                className="underline font-semibold cursor-pointer"
              >
                {hienXemTruocPhieu ? "Ẩn bản xem trước phiếu" : "Xem văn bản phiếu cam đoan"}
              </button>
            </div>
          )}

          {/* 6 trụ cột Điều 10 & 63 Luật KBCB 2023 */}
          <div className="grid grid-cols-1 gap-3">
            {truCot.map((tc) => {
              const daBoSungTay = Boolean(boSungBacSi[tc.ma]?.trim());
              return (
                <div
                  key={tc.ma}
                  className={`rounded-2xl border p-3.5 space-y-2 transition-all ${
                    tc.daGiaiThich
                      ? "bg-white border-[#A7E3C9] shadow-2xs"
                      : daBoSungTay
                      ? "bg-[#F0F9FF] border-[#BAE6FD]"
                      : "bg-[#FEF9E7] border-[#F5E6B8]"
                  }`}
                >
                  <div className="flex items-start justify-between gap-2 flex-wrap">
                    <div>
                      <h3 className="text-[13px] font-bold text-[#0F172A]">{tc.tieuDe}</h3>
                      <p className="text-[11px] text-[#64748B]">{tc.moTaLuat}</p>
                    </div>
                    {tc.daGiaiThich ? (
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10.5px] font-bold bg-[#D1F2E3] text-[#0D6B50]">
                        <CheckCircle2 size={12} />
                        Đã giải thích trong hội thoại{" "}
                        {tc.luot.length > 0 ? `[T${tc.luot.join(", T")}]` : ""}
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10.5px] font-bold bg-[#FEF3C7] text-[#92400E] border border-[#F2DFA8]">
                        <AlertTriangle size={12} />
                        Chưa thấy trong lời thoại · Cần bác sĩ giải thích
                      </span>
                    )}
                  </div>

                  {tc.daGiaiThich ? (
                    <div className="rounded-xl bg-[#F3FBF7] border border-[#CDEBDD] p-2.5 text-xs text-[#0C2340] flex items-start gap-2">
                      <Quote size={13} className="text-[#0D9488] mt-0.5 flex-shrink-0" />
                      <div>
                        <span className="font-mono font-bold text-[#0284C7] mr-1.5">
                          {tc.luot.length > 0 ? `[T${tc.luot.join(", T")}]` : "[Căn cứ]"}
                        </span>
                        <span className="italic">“{tc.trichDan || tc.noiDungTomTat}”</span>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-1">
                      <input
                        type="text"
                        value={boSungBacSi[tc.ma] || ""}
                        onChange={(e) => setBoSungBacSi((cu) => ({ ...cu, [tc.ma]: e.target.value }))}
                        placeholder="[cần bổ sung: bác sĩ giải thích trực tiếp cho người bệnh tại bàn khám và ghi nhận tại đây]"
                        className="w-full px-3 py-1.5 rounded-xl border border-dashed border-amber-400 bg-white text-xs text-[#0F172A] focus:outline-none focus:ring-1 focus:ring-[#0284C7]"
                      />
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Khung xem trước Phiếu Cam Đoan PTTT */}
          {hienXemTruocPhieu && (
            <div className="rounded-2xl border border-[#BAE6FD] bg-white p-4 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-[#0369A1] flex items-center gap-1.5">
                  <FileText size={14} />
                  <span>Bản xem trước Phiếu Cam Đoan PTTT (Chuẩn A4)</span>
                </span>
                <button
                  type="button"
                  onClick={inTrucTiepPhieuCamDoan}
                  className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-[#F0FDF4] border border-[#0D9488] text-[#0D9488] text-[11px] font-semibold cursor-pointer"
                >
                  <Printer size={12} />
                  <span>In A4</span>
                </button>
              </div>
              <pre className="whitespace-pre-wrap font-serif text-[12.5px] leading-relaxed text-[#0F172A] bg-[#F8FBFC] p-3.5 rounded-xl border border-slate-200 max-h-64 overflow-y-auto">
                {vanBanPhieu}
              </pre>
            </div>
          )}
        </div>

        {/* Chân modal */}
        <div className="px-5 py-3 border-t border-[#BAE6FD] bg-white flex flex-wrap items-center justify-between gap-2 flex-shrink-0">
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setHienXemTruocPhieu((v) => !v)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-[#BAE6FD] bg-white hover:bg-[#F0F9FF] text-[#0C4A6E] text-xs font-semibold cursor-pointer"
            >
              <FileText size={13} className="text-[#0284C7]" />
              <span>{hienXemTruocPhieu ? "Ẩn phiếu" : "Xem phiếu in"}</span>
            </button>
            <button
              type="button"
              onClick={() => {
                navigator.clipboard.writeText(vanBanPhieu);
                setDaChep(true);
                setTimeout(() => setDaChep(false), 2000);
              }}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-[#BAE6FD] bg-white hover:bg-[#F0F9FF] text-[#0C4A6E] text-xs font-semibold cursor-pointer"
            >
              {daChep ? <Check size={13} className="text-[#0D9488]" /> : <Copy size={13} className="text-[#0284C7]" />}
              <span>{daChep ? "Đã chép phiếu ✓" : "Sao chép Phiếu Cam Đoan"}</span>
            </button>
            <button
              type="button"
              onClick={inTrucTiepPhieuCamDoan}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-[#0D9488] bg-[#F0FDF4] hover:bg-[#DCFCE7] text-[#0D9488] text-xs font-semibold cursor-pointer"
            >
              <Printer size={13} />
              <span>In Phiếu</span>
            </button>
          </div>

          <button
            type="button"
            disabled={dangDongDauWorm}
            onClick={() => void dongDauWormVaXuatPhieu()}
            className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-xl bg-[#0284C7] hover:bg-[#0369A1] disabled:opacity-50 text-white text-xs font-semibold shadow-tactile-doctor cursor-pointer"
          >
            <Lock size={13} />
            <span>
              {dangDongDauWorm
                ? "Đang niêm phong WORM..."
                : "Đóng dấu WORM SHA-256 & Xuất Phiếu Cam Đoan PTTT"}
            </span>
          </button>
        </div>
      </div>
    </div>
  );
};
