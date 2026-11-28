import React, { useState, useEffect, useRef, useMemo, useCallback } from "react";
import { DocumentTabItem, Session, SignOffRecord } from "../types";
import { ghepMenhDe } from "../lib/ghepMenhDe";
import {
  compileEffectiveNote,
  computeNoteSignOffHashSync,
  isSignOffStale,
  kiemTraDieuKienKyDuyet,
  laTieuDeMuc,
  tachLuot,
  trichChanDoanVaThuocTuSoap,
} from "../lib/compileEffectiveNote";
import { vietHoaCau, vietHoaDauDong } from "../lib/vietHoaCau";
import { taoPhieuSbar, tachMucHis } from "../lib/sbar";
import { choPhepDungHoSo, nhanInHoSo } from "../lib/choPhepDungHoSo";
import { xuatGoiFhirVaBhytHieuLuc } from "../lib/taiBienDichHieuLuc";
import type { CanhBaoMauThuanLanKham } from "../lib/doiChieuLanKham";
import type { Proposition, Quyet } from "./VerificationView";
import {
  FileText,
  Edit2,
  MoreHorizontal,
  Mic,
  MicOff,
  Undo,
  Redo,
  Copy,
  Wrench,
  Check,
  ChevronDown,
  ThumbsUp,
  ThumbsDown,
  Sparkles,
  Clock,
  RefreshCw,
  Download,
  Printer,
  FileCode,
  AlertTriangle,
  AlertCircle,
  ShieldAlert,
  ShieldCheck,
  CheckCircle2,
  User,
  Stethoscope,
  Activity,
  Pill,
  HeartPulse,
  FileHeart,
  Cpu,
  Users,
  Quote,
  ArrowRight,
  X,
} from "lucide-react";
import type { NoteMeta } from "./VerificationView";
import { NhatKyTienTrinhAIModal } from "./NhatKyTienTrinhAIModal";
import { HO_SO_MAU, HoSoDD, MucDan, Thuoc, ToDanDoBenhNhanModal } from "./ToDanDoBenhNhanModal";
import { CrossVisitBanner } from "./CrossVisitBanner";
import { HisSmartCopyPopover } from "./HisSmartCopyPopover";
import { BhytPrecheckModal, type BhytPrecheckResult } from "./BhytPrecheckModal";
import { SbarModal } from "./SbarModal";
import {
  BangDoiSoatThuocVaDonQuocGiaModal,
  phanTichDongDonTt26TuMenhDe,
} from "./BangDoiSoatThuocVaDonQuocGiaModal";
import { CamDoanThuThuatModal } from "./CamDoanThuThuatModal";
import { DiBuongNoiTruModal } from "./DiBuongNoiTruModal";
import { BangDongCoLamSangThucTinh } from "./BangDongCoLamSangThucTinh";

/** Một mệnh đề cần tô trong bản nháp khi ngăn duyệt đang mở. */
export type DanhDauMD = {
  id: number;
  text: string;
  /** Chữ bác sĩ đã sửa ở ngăn duyệt — cũng dùng để tìm câu. */
  textKhac?: string[];
  trangThai: "canh" | "luuy" | "ok" | "giu" | "sua" | "bo";
};

interface NoteEditorViewProps {
  sessionId?: string;
  tab: DocumentTabItem;
  /** Nội dung bệnh án SOAP/Bản nháp gốc của ca khám (không phải tờ dặn dò leaflet) dùng để kiểm tra chữ ký SHA-256 WORM. */
  soapRawContent?: string;
  onUpdateContent: (content: string) => void;
  onRegenerateNote?: (style: string) => void;
  isGenerating?: boolean;
  /** Ngăn duyệt cạnh bản nháp đang mở: tô từng câu theo trạng thái mệnh đề. */
  danhDau?: DanhDauMD[];
  chonId?: number | null;
  onChonMenhDe?: (id: number | null) => void;
  /** Lời thoại ca khám để đối chiếu căn cứ lượt thoại T1, T2... */
  transcript?: string;
  /** Chuyển sang màn hình đối chiếu & đường nối căn cứ toàn màn hình */
  onKiemChungLuot?: (soLuot: number) => void;
  /** Dữ liệu mệnh đề & kiểm duyệt lâm sàng nâng cao từ backend */
  noteMeta?: NoteMeta | null;
  patientIdentifier?: string;
  patientInfo?: Record<string, unknown>;
  currentSession?: Session | null;
  allSessions?: Session[];
  onCreateCustomTab?: (title: string, content: string) => void;
  quyetDuyet?: Record<number, Quyet>;
  banSuaDuyet?: Record<number, string>;
  signOff?: SignOffRecord;
  onSignOff?: () => Promise<void> | void;
  crossVisitAlerts?: CanhBaoMauThuanLanKham[];
  savedLeaflet?: HoSoDD;
  onSaveLeaflet?: (hoSo: HoSoDD) => void;
}

/**
 * Chèn ghi nhận trực tiếp của bác sĩ (PhoWhisper rảnh tay F2, chip SOCRATES, hoặc biện luận CLS)
 * vào đúng mục mục tiêu (mặc định `KHÁM LÂM SÀNG`) với nhãn nguồn minh bạch.
 */
export function chenGhiNhanKhamTrucTiep(
  noiDungHienTai: string,
  vanBanMoi: string,
  nhanNguon = "[Bác sĩ đọc ghi nhận khám trực tiếp]",
  mauTieuDeMuc = /(?:KHÁM\s+LÂM\s+SÀNG|KHÁM\s+THỰC\s+THỂ|O\s*[—–-]\s*OBJECTIVE|THỰC\s+THỂ\s*&\s*CẬN\s+LÂM\s+SÀNG)/iu,
): string {
  const sach = (vanBanMoi || "").trim();
  if (!sach) return noiDungHienTai;
  const dongChen = sach.startsWith("- ") ? sach : `- ${nhanNguon}: ${sach}`;
  const goc = (noiDungHienTai || "").trimEnd();
  if (!goc) return `KHÁM LÂM SÀNG\n${dongChen}`;

  const cacDong = goc.split("\n");
  let viTriMuc = -1;
  for (let i = 0; i < cacDong.length; i++) {
    if (laTieuDeMuc(cacDong[i]) && mauTieuDeMuc.test(cacDong[i])) {
      viTriMuc = i;
      break;
    }
  }

  if (viTriMuc >= 0) {
    let viTriChen = cacDong.length;
    for (let j = viTriMuc + 1; j < cacDong.length; j++) {
      const dj = cacDong[j].trim();
      if ((laTieuDeMuc(cacDong[j]) && !/^#\s+/.test(dj)) || /^---|^___|^\*\*\*$/.test(dj)) {
        viTriChen = j;
        break;
      }
    }
    while (viTriChen > viTriMuc + 1 && !cacDong[viTriChen - 1].trim()) {
      viTriChen--;
    }
    const truoc = cacDong.slice(0, viTriChen);
    const sau = cacDong.slice(viTriChen);
    return [...truoc, dongChen, ...sau].join("\n");
  }

  if (nhanNguon.includes("Bác sĩ đọc ghi nhận khám")) {
    return `${goc}\n\nKHÁM LÂM SÀNG\n${dongChen}`;
  }
  return `${goc}\n${dongChen}`;
}

/**
 * Boost 4C: Biên dịch gói xuất HL7 FHIR R4 & BHYT QĐ 130/4750 (.json) sao cho phản ánh 100%
 * quyết định `Giữ / Sửa / Bỏ` của bác sĩ (loại bỏ triệt để mệnh đề `bo` và cập nhật `banSuaDuyet`).
 */
export function taoGoiFhirBhytHieuLuc(
  noteMeta: NoteMeta | null | undefined,
  fallbackId: string,
  quyetDuyet: Record<number, Quyet> = {},
  banSuaDuyet: Record<number, string> = {},
) {
  const rawProps: Proposition[] = noteMeta?.propositions || [];
  const rejectedIds = new Set<number>();
  const rejectedTexts = new Set<string>();
  const editedById = new Map<number, string>();
  const editedByOldText = new Map<string, string>();

  for (const p of rawProps) {
    const q = quyetDuyet[p.id];
    if (q === "bo") {
      rejectedIds.add(p.id);
      if (p.text?.trim()) rejectedTexts.add(p.text.trim().toLowerCase());
      if (p.drug?.trim()) rejectedTexts.add(p.drug.trim().toLowerCase());
    } else if (q === "sua" && banSuaDuyet[p.id]?.trim()) {
      const moi = banSuaDuyet[p.id].trim();
      editedById.set(p.id, moi);
      if (p.text?.trim()) editedByOldText.set(p.text.trim(), moi);
    }
  }

  const effectivePropositions = rawProps
    .filter((p) => quyetDuyet[p.id] !== "bo")
    .map((p) => {
      const q = quyetDuyet[p.id] || "cho";
      const sua = editedById.get(p.id);
      return sua
        ? { ...p, text: sua, originalText: p.text, doctorDecision: q }
        : { ...p, doctorDecision: q };
    });

  // Lọc và cập nhật HL7 FHIR R4 Bundle
  let fhirOut: any = noteMeta?.clinicalSafety?.fhir_bundle
    ? JSON.parse(JSON.stringify(noteMeta.clinicalSafety.fhir_bundle))
    : null;

  if (fhirOut && Array.isArray(fhirOut.entry)) {
    fhirOut.entry = fhirOut.entry
      .filter((ent: any) => {
        const res = ent?.resource || {};
        const resId = String(res.id || "");
        const mId = resId.match(/(?:^|[-_])(?:prop[-_])?(\d+)$/i);
        if (mId && rejectedIds.has(Number(mId[1]))) return false;

        const textsToCheck = [
          res?.code?.text,
          res?.medicationCodeableConcept?.text,
          res?.valueString,
          ...(Array.isArray(res?.note) ? res.note.map((n: any) => n?.text) : []),
        ]
          .filter((x) => typeof x === "string")
          .map((x: string) => x.trim().toLowerCase());

        if (textsToCheck.some((t) => rejectedTexts.has(t))) return false;
        return true;
      })
      .map((ent: any) => {
        const res = ent?.resource;
        if (!res) return ent;
        const resId = String(res.id || "");
        const mId = resId.match(/(?:^|[-_])(?:prop[-_])?(\d+)$/i);
        const suaTheoId = mId ? editedById.get(Number(mId[1])) : undefined;

        const thayChuoi = (goc: unknown): unknown => {
          if (typeof goc !== "string") return goc;
          if (suaTheoId) return suaTheoId;
          return editedByOldText.get(goc.trim()) || goc;
        };

        if (res.code?.text) res.code.text = thayChuoi(res.code.text);
        if (res.medicationCodeableConcept?.text) {
          res.medicationCodeableConcept.text = thayChuoi(res.medicationCodeableConcept.text);
        }
        if (typeof res.valueString === "string") res.valueString = thayChuoi(res.valueString);
        if (Array.isArray(res.note)) {
          res.note = res.note.map((n: any) => (n?.text ? { ...n, text: thayChuoi(n.text) } : n));
        }
        return ent;
      });

    if (typeof fhirOut.total === "number") {
      fhirOut.total = fhirOut.entry.length;
    }
  }

  // Lọc và cập nhật gói BHYT QĐ 130/4750
  let bhytOut: any = noteMeta?.clinicalSafety?.bhyt_icd10
    ? JSON.parse(JSON.stringify(noteMeta.clinicalSafety.bhyt_icd10))
    : null;

  if (bhytOut?.bang_xml_130_4750) {
    const xml = bhytOut.bang_xml_130_4750;
    if (Array.isArray(xml.XML2_THUOC)) {
      xml.XML2_THUOC = xml.XML2_THUOC.filter((row: any) => {
        const ten = String(row?.TEN_THUOC || "").trim().toLowerCase();
        return !ten || !rejectedTexts.has(ten);
      }).map((row: any, idx: number) => {
        const tenGoc = String(row?.TEN_THUOC || "").trim();
        const sua = editedByOldText.get(tenGoc);
        return { ...row, STT: idx + 1, ...(sua ? { TEN_THUOC: sua } : {}) };
      });
    }
    if (Array.isArray(xml.XML5_DIEN_BIEN_LS)) {
      xml.XML5_DIEN_BIEN_LS = xml.XML5_DIEN_BIEN_LS.filter((row: any) => {
        const db = String(row?.DIEN_BIEN_LS || "").trim().toLowerCase();
        return !db || !rejectedTexts.has(db);
      }).map((row: any, idx: number) => {
        const dbGoc = String(row?.DIEN_BIEN_LS || "").trim();
        const sua = editedByOldText.get(dbGoc);
        return { ...row, STT: idx + 1, ...(sua ? { DIEN_BIEN_LS: sua } : {}) };
      });
    }
  }

  return {
    caseId: noteMeta?.caseId || fallbackId,
    exportedAt: new Date().toISOString(),
    bhyt_qd130_4750: bhytOut,
    stage_45_omission_recovery: noteMeta?.clinicalSafety?.khoi_phuc_bo_sot_tang_45 || [],
    audit_trail_worm: noteMeta?.clinicalSafety?.audit_trail_worm || null,
    hl7_fhir_r4_bundle: fhirOut,
    propositions: effectivePropositions,
  };
}

const MAU_TO: Record<DanhDauMD["trangThai"], string> = {
  canh: "bg-[#FDE2E2] decoration-[#E86A6A]",
  luuy: "bg-[#FEF3C7] decoration-[#D9A441]",
  ok: "bg-transparent decoration-transparent hover:decoration-[#9ED9C0]",
  giu: "bg-[#E3F6EE] decoration-[#34B889]",
  sua: "bg-[#FEF3C7] decoration-[#D9A441]",
  bo: "bg-[#F1F5F9] line-through text-[#94A3B8] decoration-[#94A3B8]",
};

/** Kiểm tra dòng có chứa cảnh báo cần bác sĩ xác nhận hoặc tương tác nguy hiểm để bôi đỏ */
function kiemTraCanXacNhan(dong: string, mdTrongDong?: DanhDauMD[]): {
  laCanhBao: boolean;
  mucDo: "khan_cap" | "xac_nhan";
  nhan: string;
} {
  const t = dong.trim();
  if (!t) return { laCanhBao: false, mucDo: "xac_nhan", nhan: "" };

  if (
    /BÁO ĐỘNG ĐỎ|BLACK-BOX|TƯƠNG TÁC ĐỘ 1|NGƯNG NGAY LẬP TỨC|CHỐNG CHỈ ĐỊNH TỬ VONG/i.test(t) ||
    /^[ \t]*[-*]?[ \t]*[🚨⛔]/.test(t)
  ) {
    return { laCanhBao: true, mucDo: "khan_cap", nhan: "CẢNH BÁO NGUY HIỂM KHẨN CẤP" };
  }

  if (
    /\[BÔI ĐỎ|CẦN BÁC SĨ XÁC NHẬN|CẦN BÁC SĨ DUYỆT|CẦN XÁC NHẬN|ĐÍNH CHÍNH LIỀU/i.test(t) ||
    /^[ \t]*[-*]?[ \t]*⚠️/.test(t) ||
    mdTrongDong?.some((m) => m.trangThai === "canh")
  ) {
    return { laCanhBao: true, mucDo: "xac_nhan", nhan: "CẦN BÁC SĨ XÁC NHẬN" };
  }

  return { laCanhBao: false, mucDo: "xac_nhan", nhan: "" };
}

/** Định dạng văn bản nội tuyến: bỏ dấu **, in đậm, định dạng trích dẫn [T..] và chữ nghiêng */
function renderDinhDangChu(
  vanBan: string,
  isAlert = false,
  onXemLuot?: (so: number) => void,
  banDoLuot?: Map<number, { so: number; vai: string; chu: string }>
): React.ReactNode {
  if (!vanBan) return null;
  // Loại bỏ triệt để các nhãn chỉ dẫn thừa như [BÔI ĐỎ...] vì giao diện đã được bôi đỏ cảnh báo trực quan
  const vanBanSach = vanBan.replace(/\*?\*?\[(?:BÔI ĐỎ[^\]]*|CẦN BÁC SĨ DUYỆT)\]:?\*?\*?[ \t]*/gi, "");
  if (!vanBanSach) return null;
  const regex = /(\*\*[^*]+\*\*|\[T\d+(?:,\s*T\d+)*\]|\*[^*]+\*|\|)/g;
  const parts: React.ReactNode[] = [];
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = regex.exec(vanBanSach)) !== null) {
    if (match.index > lastIndex) {
      const chunk = vanBanSach.slice(lastIndex, match.index).replace(/\*\*/g, "");
      if (chunk) parts.push(chunk);
    }
    const token = match[0];
    if (token === "|") {
      parts.push(
        <span key={match.index} className="mx-2 text-slate-300 font-normal select-none">
          |
        </span>
      );
    } else if (token.startsWith("**") && token.endsWith("**")) {
      const inner = token.slice(2, -2);
      parts.push(
        <strong
          key={match.index}
          className={
            isAlert
              ? "font-bold text-red-950 underline decoration-red-300 underline-offset-2"
              : "font-semibold text-[#0F172A]"
          }
        >
          {inner}
        </strong>
      );
    } else if (token.startsWith("[T") && token.endsWith("]")) {
      // Tách từng số lượt thoại trong [T2, T10] thành các nút căn cứ độc lập
      const turnNumbers = Array.from(token.matchAll(/\d+/g), (m) => parseInt(m[0], 10));
      parts.push(
        <span key={match.index} className="inline-flex items-center gap-1 mx-1 select-none align-baseline">
          {turnNumbers.map((so) => {
            const luotInfo = banDoLuot?.get(so);
            const vai = luotInfo?.vai || "Hội thoại";
            const trichDan = luotInfo?.chu ? `"${luotInfo.chu.slice(0, 65)}..."` : "";
            return (
              <button
                key={so}
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  onXemLuot?.(so);
                }}
                className={`printable inline-flex items-center gap-1 px-1.5 py-0.5 rounded-md font-mono text-[11px] font-semibold border transition-all cursor-pointer shadow-2xs hover:scale-105 active:scale-95 group print:bg-transparent print:border-none print:shadow-none print:p-0 print:text-[10px] print:text-slate-600 ${
                  isAlert
                    ? "bg-red-50 hover:bg-red-600 hover:text-white text-red-800 border-red-300"
                    : "bg-[#F0F9FF] hover:bg-[#0284C7] hover:text-white text-[#0284C7] border-[#BAE6FD]"
                }`}
                title={`[T${so}] ${vai}: ${trichDan} (Bấm để xem câu thoại gốc và kiểm chứng)`}
              >
                <Quote size={10} className="opacity-70 group-hover:opacity-100 print:hidden" />
                <span className="print:font-normal">[T{so}]</span>
              </button>
            );
          })}
        </span>
      );
    } else if (token.startsWith("*") && token.endsWith("*")) {
      const inner = token.slice(1, -1);
      parts.push(
        <em
          key={match.index}
          className={`italic ${isAlert ? "text-red-800 font-medium" : "text-[#475569]"}`}
        >
          {inner}
        </em>
      );
    }
    lastIndex = match.index + token.length;
  }
  if (lastIndex < vanBanSach.length) {
    const chunk = vanBanSach.slice(lastIndex).replace(/\*\*/g, "");
    if (chunk) parts.push(chunk);
  }
  return parts.length ? parts : vanBanSach.replace(/\*\*/g, "");
}

export const NoteEditorView: React.FC<NoteEditorViewProps> = ({
  sessionId,
  tab,
  soapRawContent,
  onUpdateContent,
  onRegenerateNote,
  isGenerating = false,
  danhDau,
  chonId = null,
  onChonMenhDe,
  transcript = "",
  onKiemChungLuot,
  noteMeta = null,
  patientIdentifier = "",
  patientInfo,
  currentSession = null,
  allSessions = [],
  onCreateCustomTab,
  quyetDuyet = {},
  banSuaDuyet = {},
  signOff,
  onSignOff,
  crossVisitAlerts = [],
  savedLeaflet,
  onSaveLeaflet,
}) => {
  const [copied, setCopied] = useState(false);
  const [liked, setLiked] = useState<boolean | null>(null);
  const [isStyleMenuOpen, setIsStyleMenuOpen] = useState(false);
  const [isExportMenuOpen, setIsExportMenuOpen] = useState(false);
  const [moCongCu, setMoCongCu] = useState(false);
  const [personalisationOn, setPersonalisationOn] = useState(true);

  // Dictation state (Boost 3: Đọc khám thực thể rảnh tay F2 bằng PhoWhisper cục bộ — 0 byte gửi Google)
  const [isDictating, setIsDictating] = useState(false);
  const [isTranscribingDictation, setIsTranscribingDictation] = useState(false);
  const [dictationNotice, setDictationNotice] = useState<string | null>(null);

  const [dangSua, setDangSua] = useState(false);
  const [moModalTienTrinhAI, setMoModalTienTrinhAI] = useState(false);
  const [moModalDanDo, setMoModalDanDo] = useState(false);
  const [moModalSbar, setMoModalSbar] = useState(false);
  const [moPanelHis, setMoPanelHis] = useState(false);
  const [dangKyDuyet, setDangKyDuyet] = useState(false);
  const [moModalBhyt, setMoModalBhyt] = useState(false);
  const [dangKiemBhyt, setDangKiemBhyt] = useState(false);
  const [kqBhyt, setKqBhyt] = useState<BhytPrecheckResult | null>(null);
  const [moModalThuocTt26, setMoModalThuocTt26] = useState(false);
  const [moModalCamDoanPttt, setMoModalCamDoanPttt] = useState(false);
  const [moModalDiBuong, setMoModalDiBuong] = useState(false);
  // Tờ dặn dò sửa tay của từng ca, theo mã tab, để chuyển tab rồi quay lại vẫn còn.
  const [hoSoDanDo, setHoSoDanDo] = useState<Record<string, HoSoDD>>({});
  const [luotDangXem, setLuotDangXem] = useState<number | null>(null);

  const phieuSbar = useMemo(
    () => taoPhieuSbar(noteMeta?.propositions || [], quyetDuyet, banSuaDuyet, patientIdentifier),
    [noteMeta?.propositions, quyetDuyet, banSuaDuyet, patientIdentifier]
  );
  const cacMucHis = useMemo(
    () => tachMucHis(noteMeta?.propositions || [], quyetDuyet, banSuaDuyet),
    [noteMeta?.propositions, quyetDuyet, banSuaDuyet]
  );

  // Danh sách lượt thoại để đối chiếu căn cứ [T1, T2...]
  const dsLuot = useMemo(() => tachLuot(transcript), [transcript]);
  const banDoLuot = useMemo(() => new Map(dsLuot.map((l) => [l.so, l])), [dsLuot]);

  const giayRef = useRef<HTMLDivElement>(null);
  // Mở ô sửa thì luôn đặt con trỏ vào ô (autoFocus không chắc chạy). Ô chỉ quay về bản định dạng khi
  // MẤT con trỏ; nếu con trỏ chưa từng vào ô thì ô kẹt ở chế độ sửa (gặp 24/09).
  const oSuaRef = useRef<HTMLTextAreaElement>(null);
  useEffect(() => {
    if (!dangSua) return;
    const h = requestAnimationFrame(() => oSuaRef.current?.focus({ preventScroll: true }));
    return () => cancelAnimationFrame(h);
  }, [dangSua]);
  // Ghép mệnh đề với câu: nguyên văn trước, rồi gần đúng (bác sĩ đã sửa chữ trong bản nháp).
  const ghep = danhDau?.length ? ghepMenhDe(tab.content, danhDau, laTieuDeMuc) : null;
  const mdTheoId = new Map((danhDau || []).map((d) => [d.id, d]));
  const catDong = (txt: string, i: number, offset = 0) => {
    const ra: Array<{ chu: string; md?: DanhDauMD; ganDung?: boolean }> = [];
    let vt = 0;
    for (const g of ghep?.get(i) || []) {
      const md = mdTheoId.get(g.id);
      const bd = Math.max(0, g.bd - offset);
      const kt = Math.min(txt.length, g.kt - offset);
      if (!md || kt <= bd || bd < vt) continue;
      if (bd > vt) ra.push({ chu: txt.slice(vt, bd) });
      ra.push({ chu: txt.slice(bd, kt), md, ganDung: g.ganDung });
      vt = kt;
    }
    if (vt < txt.length) ra.push({ chu: txt.slice(vt) });
    return ra;
  };
  useEffect(() => {
    if (chonId === null || chonId === undefined) return;
    const h = requestAnimationFrame(() =>
      giayRef.current?.querySelector(`[data-md="${chonId}"]`)?.scrollIntoView({ block: "center", behavior: "smooth" }));
    return () => cancelAnimationFrame(h);
  }, [chonId]);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const tabContentRef = useRef<string>(tab.content);
  tabContentRef.current = tab.content;

  // Undo / Redo history
  const [history, setHistory] = useState<string[]>([tab.content]);
  const [historyIndex, setHistoryIndex] = useState(0);

  const dungLuotGhiAmTam = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      try {
        mediaRecorderRef.current.stop();
      } catch {}
    }
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((t) => t.stop());
      mediaStreamRef.current = null;
    }
    setIsDictating(false);
  }, []);

  useEffect(() => {
    setHistory([tab.content]);
    setHistoryIndex(0);
    dungLuotGhiAmTam();
  }, [tab.id, dungLuotGhiAmTam]);

  useEffect(() => {
    return () => {
      dungLuotGhiAmTam();
    };
  }, [dungLuotGhiAmTam]);

  // Văn bản hiệu lực đã áp dụng mọi quyết định "Sửa" và loại bỏ mệnh đề "Bỏ"
  const laTabBenhAn =
    tab.type === "soap" ||
    (tab.type === "custom" &&
      (tab.title === "Bản nháp hồ sơ" || (Boolean(noteMeta?.content) && tab.content === noteMeta?.content)));

  const effectiveContent = useMemo(
    () =>
      laTabBenhAn
        ? compileEffectiveNote(tab.content, noteMeta?.propositions, quyetDuyet, banSuaDuyet)
        : tab.content,
    [laTabBenhAn, tab.content, noteMeta?.propositions, quyetDuyet, banSuaDuyet],
  );

  // Kiểm tra chữ ký SHA-256 WORM trên bệnh án SOAP gốc + trạng thái duyệt mệnh đề (không bao giờ băm tab leaflet)
  const currentSignOffHash = useMemo(() => {
    const gocDeBam = soapRawContent ?? (tab.type !== "leaflet" ? tab.content : "");
    return computeNoteSignOffHashSync(gocDeBam, quyetDuyet, banSuaDuyet);
  }, [soapRawContent, tab.type, tab.content, quyetDuyet, banSuaDuyet]);

  const daSuaSauKy = useMemo(
    () => isSignOffStale(signOff, currentSignOffHash),
    [signOff, currentSignOffHash],
  );

  const kiemTraKy = useMemo(
    () => kiemTraDieuKienKyDuyet(noteMeta?.propositions, quyetDuyet, banSuaDuyet),
    [noteMeta?.propositions, quyetDuyet, banSuaDuyet],
  );

  // Đề cải tiến 1: chỉ được đưa hồ sơ ra khỏi phần mềm (chép, in, tải, HIS, SBAR, tờ dặn dò) sau khi ký.
  const dungHoSo = useMemo(
    () => choPhepDungHoSo({ daKy: Boolean(signOff), daSuaSauKy }),
    [signOff, daSuaSauKy],
  );
  const lopNutKhoa = dungHoSo.duoc ? "" : " opacity-40 cursor-not-allowed pointer-events-auto";
  const inHoSo = () => {
    setIsExportMenuOpen(false);
    if (!dungHoSo.duoc) return;
    window.print();
  };

  const handleTextChange = useCallback(
    (newVal: string) => {
      onUpdateContent(newVal);
      setHistory((prevHist) => {
        const sliced = prevHist.slice(0, historyIndex + 1);
        sliced.push(newVal);
        setHistoryIndex(sliced.length - 1);
        return sliced;
      });
    },
    [onUpdateContent, historyIndex],
  );

  const handleUndo = () => {
    if (historyIndex > 0) {
      const prev = historyIndex - 1;
      setHistoryIndex(prev);
      onUpdateContent(history[prev]);
    }
  };

  const handleRedo = () => {
    if (historyIndex < history.length - 1) {
      const next = historyIndex + 1;
      setHistoryIndex(next);
      onUpdateContent(history[next]);
    }
  };

  const handleCopy = () => {
    if (!dungHoSo.duoc) return;
    navigator.clipboard.writeText(vietHoaDauDong(effectiveContent));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Tải file Text (dùng văn bản hiệu lực đã áp dụng Sửa/Bỏ mệnh đề)
  const handleDownloadTxt = () => {
    if (!dungHoSo.duoc) return;
    const blob = new Blob([vietHoaDauDong(effectiveContent)], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${tab.title.replace(/[^a-z0-9\u00C0-\u024F\u1E00-\u1EFF]/gi, "_")}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    setIsExportMenuOpen(false);
  };

  // Tải file Markdown (dùng văn bản hiệu lực đã áp dụng Sửa/Bỏ mệnh đề)
  const handleDownloadMd = () => {
    if (!dungHoSo.duoc) return;
    const blob = new Blob([vietHoaDauDong(effectiveContent)], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${tab.title.replace(/[^a-z0-9\u00C0-\u024F\u1E00-\u1EFF]/gi, "_")}.md`;
    a.click();
    URL.revokeObjectURL(url);
    setIsExportMenuOpen(false);
  };

  // Boost 4C: Tải gói chuẩn liên thông HL7 FHIR R4 & BHYT XML 130/4750 (.json) đã lọc mục Bỏ & áp dụng mục Sửa
  const handleDownloadFhirBhytJson = () => {
    if (!dungHoSo.duoc) return;
    const payload = xuatGoiFhirVaBhytHieuLuc({
      noteMeta,
      quyetDuyet,
      banSuaDuyet,
      caseId: noteMeta?.caseId || tab.id,
      patientIdentifier,
    });
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `MediTrace_FHIR_BHYT_${(noteMeta?.caseId || "ca_kham").replace(/[^a-z0-9_-]/gi, "_")}.json`;
    a.click();
    URL.revokeObjectURL(url);
    setIsExportMenuOpen(false);
  };

  // Boost 4C: Dựng tờ dặn dò động từ dữ liệu ca khám thật — giữ đầy đủ thuốc `can_xac_nhan` đã được bác sĩ Giữ/Sửa,
  // tách rõ "Đơn thuốc kê mới đợt này" và "Thuốc nền đang dùng tại nhà", lấy chế độ ăn & dấu hiệu đỏ từ `ban_dan_do_benh_nhan`!
  const hoSoDanDoTuCa = useMemo<HoSoDD>(() => {
    const icd = noteMeta?.clinicalSafety?.bhyt_icd10?.ma_icd10_chinh;
    const banDanDoBe = noteMeta?.clinicalSafety?.ban_dan_do_benh_nhan;
    const rawProps = noteMeta?.propositions || [];
    const activeProps = rawProps
      .filter((p) => quyetDuyet[p.id] !== "bo")
      .map((p) => ({
        ...p,
        effectiveText: (quyetDuyet[p.id] === "sua" && banSuaDuyet[p.id] ? banSuaDuyet[p.id] : p.text || "").trim(),
      }))
      .filter((p) => p.effectiveText.length > 0);

    const dsThuoc = activeProps.filter((p) => {
      if (p.negated) return false;
      const daXacNhanHoacThan =
        p.status === "than" || quyetDuyet[p.id] === "giu" || quyetDuyet[p.id] === "sua";
      if (!daXacNhanHoacThan) return false;
      const sec = (p.section || "").toUpperCase();
      if (sec === "DỊ ỨNG" || sec === "TIỀN SỬ GIA ĐÌNH") return false;
      if (/dị ứng|mẫn cảm|đã ngưng|đã ngừng/i.test(p.effectiveText)) return false;
      return Boolean(
        p.drug ||
          sec === "THUỐC ĐANG DÙNG" ||
          sec === "ĐƠN THUỐC" ||
          sec === "KẾ HOẠCH ĐIỀU TRỊ" ||
          (sec === "CẦN XÁC NHẬN" && /\b(?:\d+\s*(?:mg|g|ml|viên)|uống|tiêm|xịt)\b/i.test(p.effectiveText)),
      );
    });

    const propChanDoan = activeProps.find(
      (p) => !p.negated && (p.section === "CHẨN ĐOÁN" || p.section === "ĐÁNH GIÁ" || p.section === "TÓM TẮT"),
    );
    const thuCong = trichChanDoanVaThuocTuSoap(effectiveContent);

    if (
      !icd &&
      !propChanDoan &&
      dsThuoc.length === 0 &&
      activeProps.length === 0 &&
      !thuCong.chanDoan &&
      thuCong.thuoc.length === 0
    ) {
      return HO_SO_MAU;
    }

    const chanDoanCa = icd
      ? `${icd.ten_benh_byt} [ICD-10: ${icd.ma_icd10}]`
      : propChanDoan?.effectiveText || thuCong.chanDoan || "[chẩn đoán xác định do bác sĩ ghi]";

    // Sắp xếp Đơn thuốc kê mới lên trước, Thuốc nền đang dùng tại nhà ở sau
    const dsThuocSapXep = [...dsThuoc].sort((a, b) => {
      const aNha =
        a.section === "THUỐC ĐANG DÙNG" || /\bđang uống|đang dùng|ở nhà\b/i.test(a.effectiveText) ? 1 : 0;
      const bNha =
        b.section === "THUỐC ĐANG DÙNG" || /\bđang uống|đang dùng|ở nhà\b/i.test(b.effectiveText) ? 1 : 0;
      return aNha - bNha;
    });

    const thuocCa: Thuoc[] =
      dsThuocSapXep.length > 0
        ? dsThuocSapXep.slice(0, 10).map((p, idx) => {
            const laThuocNha =
              p.section === "THUỐC ĐANG DÙNG" || /\bđang uống|đang dùng|ở nhà\b/i.test(p.effectiveText);
            const pt = phanTichDongDonTt26TuMenhDe(p.effectiveText, p.drug, p.evidenceTurns || [], String(idx + 1));
            const daSua = quyetDuyet[p.id] === "sua";
            return {
              id: idx + 1,
              ten: p.drug || p.effectiveText,
              loai: laThuocNha
                ? "Thuốc nền đang dùng tại nhà — theo đối soát bác sĩ"
                : "Đơn thuốc kê mới đợt này",
              nhan: p.warning
                ? "LƯU Ý"
                : laThuocNha
                ? "THUỐC NỀN TẠI NHÀ"
                : daSua
                ? "ĐÃ HIỆU CHỈNH"
                : "ĐƠN KÊ MỚI",
              mau: p.warning
                ? "bg-amber-50 text-amber-800 border-amber-200"
                : laThuocNha
                ? "bg-sky-50 text-sky-700 border-sky-200"
                : "bg-emerald-50 text-emerald-700 border-emerald-200",
              sang: pt.sang,
              trua: pt.trua,
              chieu: pt.chieu,
              toi: pt.toi,
              loiDan: `${p.effectiveText} (Căn cứ lượt thoại T${(p.evidenceTurns || []).join(", T") || "1"})`,
            };
          })
        : thuCong.thuoc.length > 0
        ? thuCong.thuoc.slice(0, 8).map((dongThuoc, idx) => {
            const pt = phanTichDongDonTt26TuMenhDe(dongThuoc, null, [], String(idx + 1));
            return {
              id: idx + 1,
              ten: dongThuoc,
              loai: "Đơn thuốc kê mới đợt này (do bác sĩ ghi nhận)",
              nhan: "BÁC SĨ CHỈ ĐỊNH",
              mau: "bg-emerald-50 text-emerald-700 border-emerald-200",
              sang: pt.sang,
              trua: pt.trua,
              chieu: pt.chieu,
              toi: pt.toi,
              loiDan: dongThuoc,
            };
          })
        : [
            {
              id: 1,
              ten: "[tên thuốc, hàm lượng theo đơn bác sĩ]",
              loai: "[nhóm thuốc / công dụng]",
              nhan: "",
              mau: "bg-sky-50 text-sky-700 border-sky-200",
              sang: "",
              trua: "",
              chieu: "",
              toi: "",
              loiDan: "[hướng dẫn dùng thuốc do bác sĩ chỉ định]",
            },
          ];

    const dsDanDo = activeProps.filter((p) =>
      /DẶN\s*DÒ|HƯỚNG\s*DẪN|CHẾ\s*ĐỘ\s*ĂN|SINH\s*HOẠT/iu.test(p.section || ""),
    );

    const anUongTuBe: MucDan[] = [];
    if (banDanDoBe?.che_do_an_uong) {
      const nenAn: string[] = Array.isArray(banDanDoBe.che_do_an_uong.nen_an)
        ? banDanDoBe.che_do_an_uong.nen_an
        : [];
      const kiengCu: string[] = Array.isArray(banDanDoBe.che_do_an_uong.kieng_cu)
        ? banDanDoBe.che_do_an_uong.kieng_cu
        : [];
      if (nenAn.length > 0) {
        anUongTuBe.push({ id: 1, tieuDe: "Thực phẩm nên dùng", noiDung: nenAn.join("; ") });
      }
      if (kiengCu.length > 0) {
        anUongTuBe.push({ id: 2, tieuDe: "Thực phẩm & thói quen cần kiêng", noiDung: kiengCu.join("; ") });
      }
    }

    const anUong: MucDan[] =
      dsDanDo.length > 0
        ? [
            ...dsDanDo.map((d, idx) => ({ id: idx + 1, tieuDe: "Dặn dò bác sĩ", noiDung: d.effectiveText })),
            ...anUongTuBe.map((m, idx) => ({ ...m, id: dsDanDo.length + idx + 1 })),
          ]
        : anUongTuBe.length > 0
        ? anUongTuBe
        : [
            {
              id: 1,
              tieuDe: "Chế độ ăn & sinh hoạt",
              noiDung: "[hướng dẫn ăn uống, nghỉ ngơi phù hợp chẩn đoán của ca khám]",
            },
          ];

    const loiDanAnToanBe: string[] = Array.isArray(banDanDoBe?.loi_dan_uong_thuoc_an_toan)
      ? banDanDoBe.loi_dan_uong_thuoc_an_toan
      : [];
    const theoDoi: MucDan[] =
      loiDanAnToanBe.length > 0
        ? loiDanAnToanBe.map((nd, idx) => ({
            id: idx + 1,
            tieuDe: idx === 0 ? "Nguyên tắc dùng thuốc an toàn" : "Lưu ý theo dõi",
            noiDung: String(nd),
          }))
        : [
            {
              id: 1,
              tieuDe: "Theo dõi tại nhà",
              noiDung: "[triệu chứng và chỉ số sinh tồn cần theo dõi theo dặn dò bác sĩ]",
            },
          ];

    const dauHieuDoBe: string[] = Array.isArray(banDanDoBe?.dau_hieu_do_can_cap_cuu)
      ? banDanDoBe.dau_hieu_do_can_cap_cuu
      : [];
    const dauHieu: MucDan[] =
      dauHieuDoBe.length > 0
        ? dauHieuDoBe.slice(0, 5).map((rf, idx) => ({
            id: idx + 1,
            tieuDe: "",
            noiDung: String(rf),
          }))
        : [
            {
              id: 1,
              tieuDe: "",
              noiDung: "[dấu hiệu bất thường cần tái khám sớm hoặc đến phòng cấp cứu gần nhất ngay]",
            },
          ];

    return {
      coSo: "[Tên cơ sở khám bệnh]",
      khoa: "[Khoa / phòng khám]",
      diaChi: "[Địa chỉ]",
      hotline: "[Số hotline]",
      maMau: "[mã mẫu]",
      soHoSo: noteMeta?.caseId || sessionId || "[số hồ sơ]",
      ngayIn: new Date().toLocaleDateString("vi-VN"),
      soDon: "[số đơn]",
      tuoiGioi: "[tuổi / giới]",
      maBhyt: "[mã BHYT]",
      bacSi: "[tên bác sĩ điều trị]",
      chanDoan: chanDoanCa,
      thuoc: thuocCa,
      anUong,
      theoDoi,
      dauHieu,
      ngayTaiKham:
        typeof banDanDoBe?.hen_tai_kham === "string" && banDanDoBe.hen_tai_kham.trim()
          ? banDanDoBe.hen_tai_kham.trim()
          : "[ngày tái khám]",
      diaDiemTaiKham: "[địa điểm tái khám]",
      ngayKy: new Date().toLocaleDateString("vi-VN"),
      cchn: "[số chứng chỉ hành nghề]",
    };
  }, [noteMeta, quyetDuyet, banSuaDuyet, sessionId, effectiveContent]);

  // Boost 3: Đọc khám thực thể rảnh tay (F2) bằng MediaRecorder + PhoWhisper chạy 100% tại chỗ (0 byte lên Google)
  const toggleDictation = useCallback(async () => {
    if (isTranscribingDictation) return;

    if (isDictating) {
      dungLuotGhiAmTam();
      return;
    }

    if (typeof navigator === "undefined" || !navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === "undefined") {
      setDictationNotice("Trình duyệt không hỗ trợ thu âm MediaRecorder cho PhoWhisper cục bộ.");
      return;
    }

    try {
      setDictationNotice(null);
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;
      audioChunksRef.current = [];

      const mimeUuTien = [
        "audio/webm;codecs=opus",
        "audio/webm",
        "audio/ogg;codecs=opus",
        "audio/mp4",
      ].find((m) => MediaRecorder.isTypeSupported?.(m));

      const recorder = mimeUuTien ? new MediaRecorder(stream, { mimeType: mimeUuTien }) : new MediaRecorder(stream);
      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (ev: BlobEvent) => {
        if (ev.data && ev.data.size > 0) {
          audioChunksRef.current.push(ev.data);
        }
      };

      recorder.onstop = async () => {
        if (mediaStreamRef.current) {
          mediaStreamRef.current.getTracks().forEach((t) => t.stop());
          mediaStreamRef.current = null;
        }
        setIsDictating(false);

        const blob = new Blob(audioChunksRef.current, { type: recorder.mimeType || "audio/webm" });
        audioChunksRef.current = [];
        if (blob.size < 256) return;

        setIsTranscribingDictation(true);
        try {
          const audioBase64 = await new Promise<string>((resolve, reject) => {
            const reader = new FileReader();
            reader.onloadend = () => {
              const res = String(reader.result || "");
              const idx = res.indexOf(",");
              resolve(idx >= 0 ? res.slice(idx + 1) : res);
            };
            reader.onerror = () => reject(new Error("Không đọc được luồng âm thanh"));
            reader.readAsDataURL(blob);
          });

          const r = await fetch("/api/transcribe", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              audioBase64,
              fileName: "kham-thuc-the.webm",
              diarize: false,
            }),
          });

          if (!r.ok) {
            const errJson = await r.json().catch(() => ({}));
            throw new Error(errJson?.error || `Lỗi chép âm PhoWhisper (${r.status})`);
          }

          const d = await r.json();
          const tuSegments = Array.isArray(d?.segments)
            ? d.segments
                .map((s: any) => String(s?.text_original || "").trim())
                .filter(Boolean)
                .join(" ")
            : "";
          const tuTranscript = String(d?.transcript || "")
            .replace(/^[^:\n]{1,20}:\s*/gm, "")
            .replace(/\s+/g, " ")
            .trim();

          const vanBanDoc = (tuSegments || tuTranscript).trim();
          if (vanBanDoc) {
            const capNhat = chenGhiNhanKhamTrucTiep(
              tabContentRef.current,
              vanBanDoc,
              "[Bác sĩ đọc ghi nhận khám trực tiếp]",
            );
            handleTextChange(capNhat);
            setDictationNotice("Đã chèn ghi nhận khám trực tiếp bằng PhoWhisper tại chỗ.");
            setTimeout(() => setDictationNotice((cur) => (cur?.startsWith("Đã chèn") ? null : cur)), 3000);
          } else {
            setDictationNotice("PhoWhisper không nhận diện được tiếng nói rõ ràng trong đoạn vừa thu.");
          }
        } catch (err: any) {
          setDictationNotice(err?.message || "Không kết nối được dịch vụ PhoWhisper tại chỗ.");
        } finally {
          setIsTranscribingDictation(false);
        }
      };

      recorder.start();
      setIsDictating(true);
    } catch (err: any) {
      console.error("Lỗi mở mic PhoWhisper:", err);
      setDictationNotice("Không thể truy cập micro. Vui lòng cấp quyền micro trên trình duyệt.");
      setIsDictating(false);
    }
  }, [isDictating, isTranscribingDictation, dungLuotGhiAmTam, handleTextChange]);

  // Phím tắt F2 bật/tắt đọc khám thực thể rảnh tay khi đang khám cho bệnh nhân
  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === "F2") {
        if (document.querySelector('[role="dialog"]')) return;
        e.preventDefault();
        void toggleDictation();
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [toggleDictation]);

  // Du an chi co MOT cach viet ho so (nhanh C_khoa). Khong co "phong cach" theo loi nhac:
  // de nut do lai thi nguoi xem tuong doi phong cach la doi cach sinh.
  const styleOptions = [{ id: "Goldilocks", label: "Dựng lại bản nháp" }];

  // Tính số từ và ký tự theo văn bản hiệu lực
  const wordsCount = effectiveContent.trim() ? effectiveContent.trim().split(/\s+/).length : 0;
  const charsCount = effectiveContent.length;
  const tenSach = (patientIdentifier || "").trim();
  const tenBenhNhanHienThi =
    tenSach && !/^thêm\s+(?:tên\s+)?định\s+danh/i.test(tenSach) ? tenSach : "Người bệnh";
  const khoaHoSoDanDo = sessionId || tab.id;

  const renderNoiDungBenhAn = (noiDung: string, choPhepTuongTacMenhDe: boolean) =>
    noiDung.split("\n").map((dongGoc, i) => {
      const dong = vietHoaCau(dongGoc);
      const dongTrim = dong.trim();
      if (!dongTrim) {
        return <div key={i} className="h-2.5" />;
      }

      if (/^---|^___|^\*\*\*$/.test(dongTrim)) {
        return <hr key={i} className="my-4 border-[#CCE3F0]" />;
      }

      if (/^#+\s+(?:BỆNH ÁN|HỒ SƠ BỆNH ÁN|SOAP)/i.test(dongTrim)) {
        return (
          <div key={i} className="border-b border-[#E2E8F0] pb-2.5 mb-3">
            <h1 className="text-xl sm:text-2xl font-bold text-[#0F172A] tracking-tight">
              {dongTrim.replace(/^#+\s*/, "")}
            </h1>
          </div>
        );
      }

      if (
        dongTrim.includes("Bệnh nhân:") &&
        (dongTrim.includes("Tuổi:") || dongTrim.includes("Cân nặng:") || dongTrim.includes("Giới:"))
      ) {
        return (
          <div
            key={i}
            className="flex flex-wrap items-center gap-x-2 text-[14px] text-slate-700 py-1 mb-2 font-normal"
          >
            {renderDinhDangChu(dongTrim, false, setLuotDangXem, banDoLuot)}
          </div>
        );
      }

      if (dongTrim.includes("Ngày khám:") && dongTrim.includes("Bác sĩ")) {
        return null;
      }

      if (/S\s*[—–-]\s*SUBJECTIVE|BỆNH SỬ\s*&\s*TIỀN SỬ/i.test(dongTrim)) {
        return (
          <div
            key={i}
            className="flex items-center gap-2 mt-6 mb-2.5 px-3.5 py-2 rounded-xl bg-gradient-to-r from-[#E0F2FE] to-[#F0F9FF] border-l-4 border-[#0284C7] font-bold text-[#0369A1] text-[15px] shadow-2xs"
          >
            <Activity size={17} className="text-[#0284C7]" />
            <span>{dongTrim.replace(/^#{1,4}\s*/, "").trim()}</span>
          </div>
        );
      }

      if (/O\s*[—–-]\s*OBJECTIVE|THỰC THỂ\s*&\s*CẬN LÂM SÀNG/i.test(dongTrim)) {
        return (
          <div
            key={i}
            className="flex items-center gap-2 mt-6 mb-2.5 px-3.5 py-2 rounded-xl bg-gradient-to-r from-[#E6F4F1] to-[#F0FDF4] border-l-4 border-[#0D9488] font-bold text-[#0D9488] text-[15px] shadow-2xs"
          >
            <Stethoscope size={17} className="text-[#0D9488]" />
            <span>{dongTrim.replace(/^#{1,4}\s*/, "").trim()}</span>
          </div>
        );
      }

      if (/A\s*[—–-]\s*ASSESSMENT|CHẨN ĐOÁN/i.test(dongTrim)) {
        return (
          <div
            key={i}
            className="flex items-center gap-2 mt-6 mb-2.5 px-3.5 py-2 rounded-xl bg-gradient-to-r from-[#FEF3C7] to-[#FFFBEB] border-l-4 border-[#D97706] font-bold text-[#92400E] text-[15px] shadow-2xs"
          >
            <AlertTriangle size={17} className="text-[#D97706]" />
            <span>{dongTrim.replace(/^#{1,4}\s*/, "").trim()}</span>
          </div>
        );
      }

      if (/P\s*[—–-]\s*PLAN|KẾ HOẠCH|XỬ TRÍ/i.test(dongTrim)) {
        return (
          <div
            key={i}
            className="flex items-center gap-2 mt-6 mb-2.5 px-3.5 py-2 rounded-xl bg-gradient-to-r from-[#DCFCE7] to-[#F0FDF4] border-l-4 border-[#16A34A] font-bold text-[#15803D] text-[15px] shadow-2xs"
          >
            <Pill size={17} className="text-[#16A34A]" />
            <span>{dongTrim.replace(/^#{1,4}\s*/, "").trim()}</span>
          </div>
        );
      }

      if (laTieuDeMuc(dong)) {
        return (
          <div
            key={i}
            className="font-bold text-[#0C4A6E] tracking-wide mt-5 first:mt-0 mb-1.5 text-[15px] border-b border-[#E2ECF3] pb-1"
          >
            {dongTrim.replace(/^#{1,4}\s*/, "").trim()}
          </div>
        );
      }

      if (/\(Ghi chú phân định người nói/i.test(dongTrim)) {
        return (
          <div
            key={i}
            className="my-2.5 p-2.5 rounded-xl bg-slate-50 border border-slate-200 text-[12.5px] text-[#475569] flex items-center gap-2 italic"
          >
            <span className="p-1 rounded-md bg-slate-200 text-slate-600 flex-shrink-0">
              <Users size={14} />
            </span>
            <span>{renderDinhDangChu(dongTrim.replace(/^\s*[-*]\s*/, ""))}</span>
          </div>
        );
      }

      const mdTrongDong = choPhepTuongTacMenhDe
        ? ((ghep?.get(i) || []).map((g) => mdTheoId.get(g.id)).filter(Boolean) as DanhDauMD[])
        : undefined;
      const canhBao = kiemTraCanXacNhan(dongTrim, mdTrongDong);

      const renderDongText = (txt: string, isCanhBao: boolean, offset = 0) => {
        if (choPhepTuongTacMenhDe && ghep) {
          const doan = catDong(txt, i, offset);
          return doan.map((d, j) => {
            if (!d.md) {
              return <span key={j}>{renderDinhDangChu(d.chu, isCanhBao, setLuotDangXem, banDoLuot)}</span>;
            }
            let chuHienThi = d.chu;
            if (quyetDuyet[d.md.id] === "sua" && banSuaDuyet[d.md.id]?.trim()) {
              const moi = banSuaDuyet[d.md.id].trim();
              const mDuoiT = d.chu.match(/\s*(?:\[T\d+(?:,\s*T\d+)*\])+$/);
              chuHienThi = mDuoiT && !/\[T\d+/.test(moi) ? `${moi}${mDuoiT[0]}` : moi;
            }
            return (
              <span
                key={j}
                data-md={d.md.id}
                onClick={(e) => {
                  e.stopPropagation();
                  onChonMenhDe?.(chonId === d.md!.id ? null : d.md!.id);
                }}
                title={
                  d.ganDung || (quyetDuyet[d.md.id] === "sua" && banSuaDuyet[d.md.id])
                    ? `Câu đã được sửa so với chữ máy trích: “${d.md.text}” — bấm để xem mệnh đề ở ngăn duyệt`
                    : "Bấm để xem mệnh đề này ở ngăn duyệt"
                }
                className={`rounded px-1 -mx-0.5 underline decoration-2 underline-offset-4 cursor-pointer transition-shadow ${
                  d.ganDung ? "decoration-dotted" : ""
                } ${MAU_TO[d.md.trangThai]} ${
                  chonId === d.md.id
                    ? "ring-2 ring-[#0284C7] bg-[#E0F2FE]"
                    : "hover:ring-1 hover:ring-[#93C5FD]"
                }`}
              >
                {renderDinhDangChu(chuHienThi, isCanhBao, setLuotDangXem, banDoLuot)}
              </span>
            );
          });
        }
        return renderDinhDangChu(txt, isCanhBao, setLuotDangXem, banDoLuot);
      };

      if (canhBao.laCanhBao) {
        const mDauCanhBao = dong.match(
          /^[ \t]*(?:[-*][ \t]*)?(?:[⚠️🚨⛔][ \t]*)?(?:\*?\*?\[(?:BÔI ĐỎ[^\]]*|CẦN BÁC SĨ DUYỆT)\]:?\*?\*?[ \t]*)?/i,
        );
        const offsetCanhBao = mDauCanhBao ? mDauCanhBao[0].length : 0;
        return (
          <div
            key={i}
            className="alert-box my-3 p-3.5 rounded-xl border border-red-300 bg-gradient-to-r from-red-50/95 via-rose-50/80 to-red-50/40 border-l-4 border-l-red-500 shadow-xs text-red-950 flex items-start gap-2.5 transition-all hover:shadow-md print:bg-red-50 print:border-red-500 break-inside-avoid page-break-inside-avoid"
          >
            <div className="flex-shrink-0 mt-0.5 p-1 rounded-lg bg-red-100 text-red-600">
              <AlertTriangle size={17} className="animate-pulse print:animate-none" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1.5">
                <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold uppercase tracking-wider bg-red-600 text-white shadow-2xs">
                  {canhBao.nhan}
                </span>
              </div>
              <div className="text-[14.5px] leading-relaxed">
                {renderDongText(dong.slice(offsetCanhBao).trimEnd(), true, offsetCanhBao)}
              </div>
            </div>
          </div>
        );
      }

      if (/^[ \t]{2,}[-*]\s*/.test(dong)) {
        const mSub = dong.match(/^[ \t]{2,}[-*]\s*/)![0];
        return (
          <div key={i} className="flex items-start gap-2 my-1 pl-6 leading-relaxed text-[14px]">
            <span className="w-1.5 h-1.5 rounded-sm bg-slate-400 mt-2 flex-shrink-0" />
            <div className="flex-1 min-w-0">
              {renderDongText(dong.slice(mSub.length), false, mSub.length)}
            </div>
          </div>
        );
      }

      if (/^[ \t]*[-*]\s*/.test(dong)) {
        const mBul = dong.match(/^[ \t]*[-*]\s*/)![0];
        return (
          <div key={i} className="flex items-start gap-2.5 my-1.5 pl-1 leading-relaxed text-[14.5px]">
            <span className="w-1.5 h-1.5 rounded-full bg-[#0284C7] mt-2 flex-shrink-0" />
            <div className="flex-1 min-w-0">
              {renderDongText(dong.slice(mBul.length), false, mBul.length)}
            </div>
          </div>
        );
      }

      if (/^[ \t]*\d+\.\s*/.test(dong)) {
        const mSo = dong.match(/^[ \t]*\d+\./);
        const mSoFull = dong.match(/^[ \t]*\d+\.\s*/)![0];
        return (
          <div key={i} className="flex items-start gap-2.5 my-1.5 pl-1 leading-relaxed text-[14.5px]">
            <span className="font-bold text-[#0284C7] min-w-[20px] flex-shrink-0">
              {mSo ? mSo[0].trim() : "•"}
            </span>
            <div className="flex-1 min-w-0">
              {renderDongText(dong.slice(mSoFull.length), false, mSoFull.length)}
            </div>
          </div>
        );
      }

      return (
        <div key={i} className="my-1.5 text-[14.5px] leading-relaxed text-[#0F172A]">
          {renderDongText(dong, false, 0)}
        </div>
      );
    });

  return (
    <div
      id="note-editor-view"
      className="flex-1 flex flex-col bg-[#F8FBFC] overflow-hidden select-none"
    >
      {/* Subheader Toolbar */}
      <div className="flex items-center justify-between px-2.5 sm:px-5 py-2 border-b border-[#CCE3F0] bg-[#F8FBFC] shadow-[0_1px_4px_rgba(2,132,199,0.04)] gap-x-2 gap-y-1.5 flex-wrap no-print">
        {/* Trái: Nhãn tài liệu & Chọn định dạng phong cách */}
        <div className="flex items-center gap-1.5 sm:gap-2 flex-shrink-0">
          {/* Chọn phong cách: Cân bằng / Tự do */}
          <div className="relative flex-shrink-0">
            <button
              onClick={() => setIsStyleMenuOpen(!isStyleMenuOpen)}
              className="flex items-center gap-1 px-2 sm:px-2.5 py-1 rounded-xl border border-[#BAE6FD] bg-white text-xs text-[#0C4A6E] hover:bg-[#F0F9FF] shadow-tactile-doctor-pill transition-all whitespace-nowrap"
            >
              <Edit2 size={12} className="text-[#0284C7]" />
              <span className="hidden sm:inline font-medium">
                {styleOptions.find((s) => s.id === (tab.templateStyle || "Goldilocks"))?.label ||
                  tab.templateStyle ||
                  "Cân bằng"}
              </span>
              <span className="inline sm:hidden font-medium">
                {tab.templateStyle === "Concise"
                  ? "Ngắn gọn"
                  : tab.templateStyle === "Free"
                  ? "Tự do"
                  : "Cân bằng"}
              </span>
              <ChevronDown size={11} className="text-[#0369A1]" />
            </button>

            {isStyleMenuOpen && (
              <>
                <div
                  className="fixed inset-0 z-30"
                  onClick={() => setIsStyleMenuOpen(false)}
                />
                <div className="absolute left-0 top-full mt-1.5 w-52 bg-white rounded-xl shadow-[0_8px_24px_rgba(2,132,199,0.16)] border border-[#BAE6FD] py-1.5 z-40 animate-in fade-in">
                  <div className="px-3 py-1 text-[10px] font-semibold text-[#0369A1] uppercase tracking-wider">
                    Định dạng đầu ra
                  </div>
                  {styleOptions.map((opt) => (
                    <button
                      key={opt.id}
                      onClick={() => {
                        setIsStyleMenuOpen(false);
                        if (onRegenerateNote) {
                          onRegenerateNote(opt.id);
                        }
                      }}
                      className={`w-full flex items-center justify-between px-3 py-1.5 text-xs text-left hover:bg-[#E0F2FE] transition-colors ${
                        (tab.templateStyle || "Goldilocks") === opt.id
                          ? "font-semibold text-[#0284C7] bg-[#F0F9FF]"
                          : "text-[#334155]"
                      }`}
                    >
                      <span>{opt.label}</span>
                      {(tab.templateStyle || "Goldilocks") === opt.id && (
                        <Check size={12} className="text-[#0284C7]" />
                      )}
                    </button>
                  ))}
                </div>
              </>
            )}
          </div>
        </div>

        {/* Phải: Đọc chính tả PhoWhisper (F2), Hoàn tác, Làm lại, Các công cụ lâm sàng & Xuất */}
        <div className="flex flex-wrap items-center justify-end gap-1 sm:gap-1.5 min-w-0 flex-1">
          {/* Nút Đọc khám thực thể rảnh tay bằng PhoWhisper cục bộ (F2) */}
          <button
            type="button"
            onClick={() => void toggleDictation()}
            disabled={isTranscribingDictation}
            className={`flex items-center gap-1 sm:gap-1.5 px-2.5 sm:px-3 py-1 text-xs border rounded-xl transition-all shadow-tactile-doctor-pill whitespace-nowrap flex-shrink-0 cursor-pointer ${
              isDictating
                ? "bg-red-50 border-red-300 text-red-700 font-semibold animate-pulse"
                : isTranscribingDictation
                ? "bg-[#E0F2FE] border-[#0284C7] text-[#0369A1] font-semibold"
                : "text-[#0C4A6E] hover:bg-[#F0F9FF] border-[#BAE6FD] bg-white"
            }`}
            title={
              isDictating
                ? "Đang thu âm cục bộ — Bấm hoặc nhấn F2 để dừng và chép bằng PhoWhisper tại chỗ"
                : "Đọc kết quả khám lâm sàng rảnh tay bằng PhoWhisper tại chỗ (Phím tắt F2 — 0 byte gửi Google)"
            }
          >
            {isDictating ? (
              <>
                <span className="w-1.5 h-1.5 rounded-full bg-red-600 animate-ping" />
                <MicOff size={13} />
                <span>Dừng đọc (F2)</span>
              </>
            ) : isTranscribingDictation ? (
              <>
                <RefreshCw size={13} className="animate-spin text-[#0284C7]" />
                <span>PhoWhisper...</span>
              </>
            ) : (
              <>
                <Mic size={13} className="text-[#0284C7]" />
                <span className="text-[11px] hidden sm:inline font-medium">Đọc khám (F2)</span>
                <span className="text-[11px] inline sm:hidden font-medium">F2</span>
              </>
            )}
          </button>

          <button
            onClick={handleUndo}
            disabled={historyIndex <= 0}
            className="p-1 sm:p-1.5 text-[#0369A1] hover:text-[#0284C7] hover:bg-[#E0F2FE] rounded-lg disabled:opacity-30 transition-colors flex-shrink-0"
            title="Hoàn tác (Undo)"
          >
            <Undo size={13} />
          </button>

          <button
            onClick={handleRedo}
            disabled={historyIndex >= history.length - 1}
            className="p-1 sm:p-1.5 text-[#0369A1] hover:text-[#0284C7] hover:bg-[#E0F2FE] rounded-lg disabled:opacity-30 transition-colors flex-shrink-0"
            title="Làm lại (Redo)"
          >
            <Redo size={13} />
          </button>

          {/* Nút bật/tắt chế độ sửa văn bản thô thủ công (Chỉ mở khi bác sĩ chủ động bấm) */}
          <button
            type="button"
            onClick={() => setDangSua(!dangSua)}
            className={`flex items-center gap-1 sm:gap-1.5 px-2.5 sm:px-3 py-1 text-xs border rounded-xl transition-all shadow-tactile-doctor-pill whitespace-nowrap flex-shrink-0 ${
              dangSua
                ? "bg-amber-50 border-amber-300 text-amber-800 font-semibold"
                : "text-[#0C4A6E] hover:bg-[#F0F9FF] border-[#BAE6FD] bg-white font-medium"
            }`}
            title={dangSua ? "Bấm để quay về bản xem định dạng chuẩn" : "Bấm để chỉnh sửa văn bản thô (Markdown)"}
          >
            <Edit2 size={12} className="text-[#0284C7]" />
            <span className="text-[11px] hidden sm:inline">{dangSua ? "Xem định dạng" : "Sửa văn bản"}</span>
          </button>

          {/* Công cụ lâm sàng gộp vào một menu để thanh nút gọn */}
          <div className="relative flex-shrink-0">
            <button
              type="button"
              onClick={() => setMoCongCu((v) => !v)}
              className={`flex items-center gap-1.5 px-3 py-1 text-xs border rounded-xl transition-all shadow-tactile-doctor-pill whitespace-nowrap font-semibold ${
                moCongCu ? "border-[#0284C7] bg-[#E0F2FE] text-[#0369A1]" : "border-[#BAE6FD] bg-white text-[#0C4A6E] hover:bg-[#F0F9FF]"
              }`}
              aria-expanded={moCongCu}
              title="Tiến trình AI, BHYT/ICD-10, đơn thuốc, cam đoan, đi buồng, SBAR, chép HIS, tờ dặn dò"
            >
              <Wrench size={12} className="text-[#0284C7]" />
              <span className="text-[11px]">Công cụ</span>
              <ChevronDown size={11} className={moCongCu ? "rotate-180 transition-transform" : "transition-transform"} />
            </button>
            {moCongCu && (
              <>
                <div className="fixed inset-0 z-30" onClick={() => setMoCongCu(false)} />
                <div
                  className="absolute right-0 top-full mt-1.5 z-40 w-64 bg-white rounded-xl border border-[#BAE6FD] shadow-[0_8px_24px_rgba(2,132,199,0.16)] p-1.5 flex flex-col gap-1 [&>button]:w-full [&>button]:justify-start [&>button]:border-transparent [&>button]:shadow-none [&>button]:py-2 [&_span]:!inline"
                  onClickCapture={() => setTimeout(() => setMoCongCu(false), 0)}
                >
          {/* Nút mở nhật ký tiến trình AI và 8 chốt */}
          <button
            type="button"
            onClick={() => setMoModalTienTrinhAI(true)}
            className="flex items-center gap-1 sm:gap-1.5 px-2.5 sm:px-3 py-1 text-xs border rounded-xl transition-all shadow-tactile-doctor-pill whitespace-nowrap flex-shrink-0 text-[#0C4A6E] hover:bg-[#F0F9FF] border-[#BAE6FD] bg-white font-medium"
            title="Xem quá trình Qwen3-4B bóc tách và 8 chốt an toàn"
          >
            <Cpu size={12} className="text-[#0284C7]" />
            <span className="text-[11px] hidden sm:inline">Tiến trình AI</span>
          </button>

          {/* Boost 5: Nút Tiền kiểm BHYT & ICD-10 (truyền đầy đủ thong_tin_benh_nhan + mệnh đề đã sửa/lọc) */}
          <button
            type="button"
            disabled={dangKiemBhyt || !dungHoSo.duoc}
            onClick={async () => {
              if (!dungHoSo.duoc) return;
              setMoModalBhyt(true);
              setDangKiemBhyt(true);
              try {
                const r = await fetch("/api/bhyt/precheck", {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({
                    propositions: (noteMeta?.propositions || [])
                      .filter((p) => quyetDuyet[p.id] !== "bo")
                      .map((p) =>
                        quyetDuyet[p.id] === "sua" && banSuaDuyet[p.id]?.trim()
                          ? { ...p, text: banSuaDuyet[p.id].trim() }
                          : p,
                      ),
                    transcript,
                    thong_tin_benh_nhan: patientInfo || null,
                    sessionId,
                  }),
                });
                if (r.ok) setKqBhyt(await r.json());
              } finally {
                setDangKiemBhyt(false);
              }
            }}
            className={`flex items-center gap-1 sm:gap-1.5 px-2.5 sm:px-3 py-1 text-xs border border-[#F5E6B8] bg-[#FEF9E7] hover:bg-[#FEF3C7] text-[#7A4B00] rounded-xl font-semibold shadow-tactile-doctor-pill transition-all active:scale-95 whitespace-nowrap cursor-pointer flex-shrink-0${lopNutKhoa}`}
            title={dungHoSo.lyDo ?? "Tiền kiểm mã ICD-10 (4 ký tự), Biện luận CLS XML3/4 ↔ XML5 & Xuất gói XML1–XML5 QĐ 130/4750"}
          >
            <ShieldAlert size={12} className="text-[#B45309]" />
            <span className="text-[11px] hidden lg:inline">{dangKiemBhyt ? "Đang kiểm..." : "BHYT / ICD-10"}</span>
          </button>

          {/* Boost 6: Nút Đối soát Đa thuốc & Đơn thuốc Quốc gia TT 26/2025 */}
          <button
            type="button"
            disabled={!dungHoSo.duoc}
            onClick={() => dungHoSo.duoc && setMoModalThuocTt26(true)}
            className={`flex items-center gap-1 sm:gap-1.5 px-2.5 sm:px-3 py-1 text-xs border border-[#BAE6FD] bg-white hover:bg-[#F0F9FF] text-[#0C4A6E] rounded-xl font-medium shadow-tactile-doctor-pill transition-all active:scale-95 whitespace-nowrap cursor-pointer flex-shrink-0${lopNutKhoa}`}
            title={dungHoSo.lyDo ?? "Đối soát Đa thuốc ở nhà (DDI/ATC/ACB) & Lập nháp Đơn thuốc Quốc gia Thông tư 26/2025/TT-BYT"}
          >
            <Pill size={12} className="text-[#0284C7]" />
            <span className="text-[11px] hidden xl:inline">Đơn thuốc TT26 / DDI</span>
            <span className="text-[11px] hidden md:inline xl:hidden">TT26</span>
          </button>

          {/* Boost 8: Nút Cam đoan Thủ thuật / Phẫu thuật WORM (Luật KBCB 2023) */}
          <button
            type="button"
            disabled={!dungHoSo.duoc}
            onClick={() => dungHoSo.duoc && setMoModalCamDoanPttt(true)}
            className={`flex items-center gap-1 sm:gap-1.5 px-2.5 sm:px-3 py-1 text-xs border border-[#BAE6FD] bg-white hover:bg-[#F0F9FF] text-[#0C4A6E] rounded-xl font-medium shadow-tactile-doctor-pill transition-all active:scale-95 whitespace-nowrap cursor-pointer flex-shrink-0${lopNutKhoa}`}
            title={dungHoSo.lyDo ?? "Kiểm định 6 trụ cột Điều 10 & 63 Luật KBCB 2023 & Xuất Phiếu Cam Đoan PTTT đóng dấu WORM"}
          >
            <ShieldCheck size={12} className="text-[#0D9488]" />
            <span className="text-[11px] hidden xl:inline">Cam đoan PTTT</span>
          </button>

          {/* Boost 10: Nút Đi buồng Nội trú TT 32/2023 & Sổ Bàn giao Ca trực */}
          <button
            type="button"
            disabled={!dungHoSo.duoc}
            onClick={() => dungHoSo.duoc && setMoModalDiBuong(true)}
            className={`flex items-center gap-1 sm:gap-1.5 px-2.5 sm:px-3 py-1 text-xs border border-[#BAE6FD] bg-white hover:bg-[#F0F9FF] text-[#0C4A6E] rounded-xl font-medium shadow-tactile-doctor-pill transition-all active:scale-95 whitespace-nowrap cursor-pointer flex-shrink-0${lopNutKhoa}`}
            title={dungHoSo.lyDo ?? "Tờ điều trị Nội trú Mẫu BV-01/BV2 (Thông tư 32/2023) & Sổ Bàn giao Ca trực Toàn khoa"}
          >
            <Stethoscope size={12} className="text-[#0284C7]" />
            <span className="text-[11px] hidden xl:inline">Đi buồng / Trực</span>
          </button>

          {/* Nút Tạo phiếu bàn giao SBAR */}
          <button
            type="button"
            disabled={!dungHoSo.duoc}
            onClick={() => dungHoSo.duoc && setMoModalSbar(true)}
            className={`flex items-center gap-1 sm:gap-1.5 px-2.5 sm:px-3 py-1 text-xs border border-[#BAE6FD] bg-white hover:bg-[#F0F9FF] text-[#0C4A6E] rounded-xl font-medium shadow-tactile-doctor-pill transition-all active:scale-95 whitespace-nowrap cursor-pointer flex-shrink-0${lopNutKhoa}`}
            title={dungHoSo.lyDo ?? "Tạo phiếu bàn giao SBAR nhanh cho ca trực / khoa nội trú"}
          >
            <FileText size={12} className="text-[#0284C7]" />
            <span className="text-[11px] hidden md:inline">SBAR</span>
          </button>

          {/* Nút Chép nhanh sang HIS */}
          <button
            type="button"
            disabled={!dungHoSo.duoc}
            onClick={() => dungHoSo.duoc && setMoPanelHis((v) => !v)}
            className={`flex items-center gap-1 sm:gap-1.5 px-2.5 sm:px-3 py-1 text-xs border rounded-xl shadow-tactile-doctor-pill transition-all active:scale-95 whitespace-nowrap cursor-pointer flex-shrink-0 ${
              moPanelHis ? "border-[#0284C7] bg-[#E0F2FE] text-[#0369A1] font-semibold" : "border-[#BAE6FD] bg-white hover:bg-[#F0F9FF] text-[#0C4A6E] font-medium"
            }${lopNutKhoa}`}
            title={dungHoSo.lyDo ?? "Chép nhanh từng ô sang phần mềm HIS (VNPT-HIS, Viettel HIS, FPT.eHospital)"}
          >
            <Copy size={12} className="text-[#0284C7]" />
            <span className="text-[11px] hidden md:inline">Chép HIS</span>
          </button>

          {/* Nút mở tờ dặn dò người bệnh */}
          <button
            type="button"
            disabled={!dungHoSo.duoc}
            onClick={() => dungHoSo.duoc && setMoModalDanDo(true)}
            className={`flex items-center gap-1 sm:gap-1.5 px-2.5 sm:px-3 py-1 text-xs border rounded-xl transition-all shadow-tactile-doctor-pill whitespace-nowrap flex-shrink-0 text-[#0C4A6E] hover:bg-[#F0F9FF] border-[#BAE6FD] bg-white font-medium${lopNutKhoa}`}
            title={dungHoSo.lyDo ?? "Xem và in tờ dặn dò trao tay người bệnh"}
          >
            <FileHeart size={12} className="text-[#0284C7]" />
            <span className="text-[11px] hidden sm:inline">Tờ dặn dò</span>
          </button>
                </div>
              </>
            )}
          </div>

          {/* Nút Ký duyệt pháp lý WORM (Chốt cứng: không hoàn tất hồ sơ khi thiếu căn cứ / còn mục Cần xác nhận) */}
          {onSignOff && tab.type !== "leaflet" && (
            <button
              type="button"
              disabled={dangKyDuyet}
              onClick={async () => {
                setDangKyDuyet(true);
                try { await onSignOff(); } finally { setDangKyDuyet(false); }
              }}
              className={`flex items-center gap-1 sm:gap-1.5 px-2.5 sm:px-3 py-1 text-xs border rounded-xl font-semibold transition-all active:scale-95 whitespace-nowrap cursor-pointer flex-shrink-0 ${
                !kiemTraKy.duDieuKien
                  ? "border-[#F5E6B8] bg-[#FEF9E7] hover:bg-[#FEF3C7] text-[#92400E] shadow-tactile-doctor-pill"
                  : signOff
                  ? daSuaSauKy
                    ? "border-[#F5E6B8] bg-[#FEF9E7] hover:bg-[#FEF3C7] text-[#92400E] shadow-tactile-doctor-pill"
                    : "border-[#0D9488] bg-[#F0FDF4] hover:bg-[#DCFCE7] text-[#0D9488] shadow-tactile-doctor-pill"
                  : "border-[#0284C7] bg-[#0284C7] hover:bg-[#0369A1] text-white shadow-tactile-doctor"
              }`}
              title={
                !kiemTraKy.duDieuKien
                  ? kiemTraKy.thongDiep
                  : signOff
                  ? daSuaSauKy
                    ? `Nội dung bệnh án hoặc quyết định duyệt đã thay đổi sau lần ký #${signOff.wormSeq ?? "WORM"} — bấm để ký lại`
                    : `Đã ký duyệt lúc ${new Date(signOff.signedAt).toLocaleString("vi-VN")} (WORM #${signOff.wormSeq ?? ""})`
                  : "Chốt & Ký duyệt pháp lý WORM (SHA-256)"
              }
            >
              {!kiemTraKy.duDieuKien || (signOff && daSuaSauKy) ? (
                <AlertTriangle size={12} className="text-[#D97706]" />
              ) : (
                <CheckCircle2 size={12} />
              )}
              <span className="text-[11px]">
                {dangKyDuyet
                  ? "Đang ký..."
                  : !kiemTraKy.duDieuKien
                  ? kiemTraKy.soCanXacNhanChuaDuyet > 0
                    ? `Cần xác nhận (${kiemTraKy.soCanXacNhanChuaDuyet})`
                    : "Chưa đủ căn cứ"
                  : signOff
                  ? daSuaSauKy
                    ? "Đã sửa · Ký lại"
                    : `Đã ký #${signOff.wormSeq ?? "WORM"}`
                  : "Ký duyệt"}
              </span>
            </button>
          )}

          {/* Nút Sao chép & Menu Xuất file */}
          <div className="relative flex-shrink-0">
            <div className="flex items-center bg-[#0284C7] text-white rounded-xl overflow-hidden shadow-tactile-doctor hover:bg-[#0369A1] transition-all whitespace-nowrap">
              <button
                onClick={handleCopy}
                disabled={!dungHoSo.duoc}
                title={dungHoSo.lyDo ?? "Sao chép bản đã duyệt"}
                className={`flex items-center gap-1 sm:gap-1.5 px-2.5 sm:px-3 py-1 text-xs font-semibold whitespace-nowrap hover:bg-[#0369A1]${lopNutKhoa}`}
              >
                {copied ? (
                  <>
                    <Check size={12} className="text-white" />
                    <span>Đã chép</span>
                  </>
                ) : (
                  <>
                    <Copy size={12} />
                    <span>Sao chép</span>
                  </>
                )}
              </button>
              <button
                onClick={() => setIsExportMenuOpen(!isExportMenuOpen)}
                className="flex items-center gap-1 px-2.5 py-1 border-l border-white/30 text-xs font-semibold whitespace-nowrap hover:bg-[#0369A1]"
                title="Xuất hồ sơ: In / Lưu PDF, tải tệp .txt, .md, FHIR"
                aria-haspopup="menu"
                aria-expanded={isExportMenuOpen}
              >
                <Download size={12} />
                <span>Xuất</span>
                <ChevronDown size={11} />
              </button>
            </div>

            {isExportMenuOpen && (
              <>
                <div
                  className="fixed inset-0 z-30"
                  onClick={() => setIsExportMenuOpen(false)}
                />
                <div className="absolute right-0 top-full mt-1.5 w-56 bg-white rounded-xl shadow-[0_8px_24px_rgba(2,132,199,0.16)] border border-[#BAE6FD] py-1 z-40 text-left animate-in fade-in">
                  {!dungHoSo.duoc && (
                    <p className="px-3 py-1.5 text-[13px] leading-snug text-[#92400E] bg-[#FEF9E7] border-b border-[#F5E6B8]">
                      {dungHoSo.lyDo}
                    </p>
                  )}
                  <button
                    disabled={!dungHoSo.duoc}
                    onClick={() => {
                      handleCopy();
                      setIsExportMenuOpen(false);
                    }}
                    className={`w-full flex items-center gap-2 px-3 py-1.5 text-xs text-[#0C4A6E] hover:bg-[#E0F2FE]${lopNutKhoa}`}
                  >
                    <Copy size={13} className="text-[#0284C7]" />
                    <span>Sao chép vào Clipboard</span>
                  </button>
                  <button
                    disabled={!dungHoSo.duoc}
                    onClick={inHoSo}
                    className={`w-full flex items-center gap-2 px-3 py-1.5 text-xs text-[#0C4A6E] hover:bg-[#E0F2FE]${lopNutKhoa}`}
                  >
                    <Printer size={13} className="text-[#0D9488]" />
                    <span>In / Lưu PDF</span>
                  </button>
                  <button
                    disabled={!dungHoSo.duoc}
                    onClick={handleDownloadTxt}
                    className={`w-full flex items-center gap-2 px-3 py-1.5 text-xs text-[#0C4A6E] hover:bg-[#E0F2FE]${lopNutKhoa}`}
                  >
                    <Download size={13} className="text-[#0284C7]" />
                    <span>Tải tệp văn bản (.txt)</span>
                  </button>
                  <button
                    disabled={!dungHoSo.duoc}
                    onClick={handleDownloadMd}
                    className={`w-full flex items-center gap-2 px-3 py-1.5 text-xs text-[#0C4A6E] hover:bg-[#E0F2FE]${lopNutKhoa}`}
                  >
                    <FileCode size={13} className="text-[#0284C7]" />
                    <span>Tải tệp Markdown (.md)</span>
                  </button>
                  <button
                    disabled={!dungHoSo.duoc}
                    onClick={handleDownloadFhirBhytJson}
                    className={`w-full flex items-center gap-2 px-3 py-1.5 text-xs text-[#0C4A6E] hover:bg-[#E0F2FE]${lopNutKhoa}`}
                  >
                    <FileCode size={13} className="text-[#0D9488]" />
                    <span>Tải HL7 FHIR & BHYT (.json)</span>
                  </button>
                  <button
                    disabled={!dungHoSo.duoc}
                    onClick={inHoSo}
                    className={`w-full flex items-center gap-2 px-3 py-1.5 text-xs text-[#0C4A6E] hover:bg-[#E0F2FE] border-t border-[#CCE3F0] font-semibold${lopNutKhoa}`}
                  >
                    <Printer size={13} className="text-[#0D9488]" />
                    <span>In / Lưu PDF (Ctrl+P)</span>
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Editor Main Content Area: Giấy bệnh án nổi khối */}
      <div className="flex-1 overflow-y-auto p-3 sm:p-6 lg:p-8 relative bg-gradient-to-b from-[#F0F7FA] via-[#F8FBFC] to-[#EEF6FB]">
        {nhanInHoSo(dungHoSo.duoc) && (
          <div className="chi-hien-khi-in" role="note">
            {nhanInHoSo(dungHoSo.duoc)}
          </div>
        )}
        {dictationNotice && (
          <div className="max-w-3xl mx-auto mb-3 px-3.5 py-2 rounded-xl border border-[#BAE6FD] bg-[#F0F9FF] text-[#0369A1] text-xs font-medium flex items-center justify-between gap-2 no-print print:hidden">
            <span>{dictationNotice}</span>
            <button
              type="button"
              onClick={() => setDictationNotice(null)}
              className="p-0.5 rounded hover:bg-[#E0F2FE] text-[#0284C7] cursor-pointer"
            >
              <X size={13} />
            </button>
          </div>
        )}

        <BangDongCoLamSangThucTinh
          clinicalSafety={noteMeta?.clinicalSafety}
          onOpenPolypharmacyModal={() => dungHoSo.duoc && setMoModalThuocTt26(true)}
          onSelectSocratesChip={(chip) => {
            const capNhat = chenGhiNhanKhamTrucTiep(
              tabContentRef.current,
              chip,
              "[Bác sĩ xác nhận trực tiếp tại bàn khám]",
              /(?:BỆNH\s+SỬ|S\s*[—–-]\s*SUBJECTIVE|KHÁM\s+LÂM\s+SÀNG)/iu,
            );
            handleTextChange(capNhat);
          }}
        />

        <CrossVisitBanner alerts={crossVisitAlerts} />
        {isGenerating && (
          <div className="absolute inset-0 bg-white/80 backdrop-blur-2xs flex items-center justify-center z-10">
            <div className="flex items-center gap-2.5 px-5 py-3 bg-white rounded-2xl shadow-[0_8px_30px_rgba(2,132,199,0.12)] border border-[#BAE6FD] text-xs text-[#0F172A]">
              <RefreshCw size={15} className="animate-spin text-[#0284C7]" />
              <span className="font-semibold text-[#0369A1]">MediTrace Sentinel AI đang tổng hợp bệnh án theo tiêu chuẩn...</span>
            </div>
          </div>
        )}

        <div
          className={`max-w-3xl mx-auto bg-white rounded-2xl border border-[#BAE6FD] shadow-tactile-doctor-card p-6 sm:p-10 min-h-[500px] ${
            moModalDanDo ? "no-print print:hidden" : "printable-clinical-note"
          } print:border-none print:shadow-none print:p-0 print:max-w-none print:m-0`}
        >
          {/* Tiêu đề y tế chính quy khi in / xuất PDF */}
          <div className="hidden print:block mb-6 pb-4 border-b-2 border-slate-900 break-inside-avoid">
            <div className="flex justify-between items-start text-xs text-slate-800 leading-normal">
              <div>
                <div className="font-bold uppercase tracking-wider text-slate-950">CƠ SỞ KHÁM BỆNH: ______________________________</div>
                <div className="font-semibold text-slate-700">HỆ THỐNG TRỢ LÝ Y KHOA MEDITRACE SENTINEL</div>
                <div className="text-[10px] text-slate-500">
                  Mã ca khám: MT-{(sessionId || tab.id).slice(0, 12).toUpperCase()} • Người bệnh: {tenBenhNhanHienThi}
                </div>
              </div>
              <div className="text-right">
                <div className="font-bold text-slate-950">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</div>
                <div className="font-semibold text-slate-700">Độc lập - Tự do - Hạnh phúc</div>
                <div className="text-[10px] text-slate-500 italic mt-0.5">---o0o---</div>
              </div>
            </div>
            <div className="text-center mt-5">
              <h1 className="text-xl font-bold uppercase tracking-wider text-slate-950 font-serif">
                HỒ SƠ BỆNH ÁN KHÁM BỆNH LÂM SÀNG
              </h1>
              <p className="text-[11px] text-slate-600 mt-1">
                Thời gian lập: {new Date().toLocaleDateString("vi-VN", { day: "2-digit", month: "2-digit", year: "numeric" })} lúc {new Date().toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" })}
              </p>
            </div>
          </div>

          {/* Trên màn hình: hỗ trợ sửa thô hoặc đối chiếu mệnh đề tương tác */}
          <div className="no-print print:hidden">
            {dangSua ? (
              <div className="space-y-3">
                <div className="flex items-center justify-between pb-2.5 border-b border-slate-200">
                  <span className="text-xs font-semibold text-slate-600 flex items-center gap-1.5">
                    <Edit2 size={13} className="text-[#0284C7]" />
                    <span>Đang ở chế độ chỉnh sửa văn bản (Markdown)</span>
                  </span>
                  <button
                    type="button"
                    onClick={() => setDangSua(false)}
                    className="px-3 py-1 bg-[#0284C7] text-white rounded-lg text-xs font-semibold hover:bg-[#0369A1] shadow-tactile-doctor transition-all"
                  >
                    Xong (Xem định dạng đẹp)
                  </button>
                </div>
                <textarea
                  ref={oSuaRef}
                  value={tab.content}
                  onChange={(e) => handleTextChange(e.target.value)}
                  placeholder="Nhập hoặc chỉnh sửa chi tiết hồ sơ bệnh án lâm sàng tại đây..."
                  className="w-full h-full min-h-[460px] bg-transparent resize-none border-none focus:outline-none text-[15px] leading-relaxed text-[#0F172A] font-sans selection:bg-[#BAE6FD]/40"
                  spellCheck={false}
                />
              </div>
            ) : (
              <div
                ref={giayRef}
                className="min-h-[460px] text-[15px] leading-relaxed text-[#0F172A] font-sans focus:outline-none rounded-lg cursor-default select-text"
              >
                {renderNoiDungBenhAn(tab.content, true)}
              </div>
            )}
          </div>

          {/* Khi in A4 / xuất PDF: luôn xuất văn bản hiệu lực đã áp dụng Sửa & loại bỏ mệnh đề Bỏ */}
          <div className="hidden print:block text-[15px] leading-relaxed text-[#0F172A] font-sans">
            {renderNoiDungBenhAn(effectiveContent, false)}
          </div>

          {/* Khối chữ ký Bác sĩ điều trị khi in / xuất PDF */}
          <div className="hidden print:block mt-8 pt-4 border-t border-slate-300 page-break-inside-avoid break-inside-avoid">
            <div className="flex justify-between items-start text-xs text-slate-800">
              <div className="text-[10.5px] text-slate-500 italic max-w-xs leading-relaxed">
                * Bệnh án lâm sàng được tổng hợp từ hội thoại thực tế với sự hỗ trợ của hệ thống MediTrace Sentinel AI. Bác sĩ điều trị đã đối chiếu, kiểm chứng từng mệnh đề căn cứ và chịu trách nhiệm chuyên môn.
              </div>
              <div className="text-center min-w-[220px]">
                <p className="italic text-slate-600 text-[11px]">
                  Ngày {new Date().getDate()} tháng {new Date().getMonth() + 1} năm {new Date().getFullYear()}
                </p>
                <p className="font-bold uppercase text-slate-900 mt-1">BÁC SĨ ĐIỀU TRỊ</p>
                <p className="text-[10px] text-slate-500 italic">(Ký và ghi rõ họ tên)</p>
                <div className="h-16" />
                <p className="font-semibold text-slate-800 text-xs">Họ tên và mã người hành nghề: __________________</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Dưới cùng: Đánh giá chất lượng & Trạng thái thống kê */}
      <div className="flex flex-wrap items-center justify-between px-3 sm:px-6 py-2.5 border-t border-[#BAE6FD] bg-gradient-to-b from-[#F8FBFC] to-[#F0F9FF] shadow-[0_-2px_12px_rgba(2,132,199,0.06)] text-xs text-[#0369A1] gap-2 no-print">
        <div className="flex items-center gap-2 sm:gap-3 flex-shrink-0">
          <div className="flex items-center gap-1 sm:gap-1.5">
            <button
              onClick={() => setLiked(liked === true ? null : true)}
              className={`p-1.5 rounded-lg border border-[#BAE6FD] transition-all ${
                liked === true
                  ? "bg-[#0284C7] text-white shadow-tactile-doctor"
                  : "bg-white text-[#64748B] hover:text-[#0284C7] hover:bg-[#E0F2FE] shadow-tactile-doctor-pill"
              }`}
              title="Bệnh án đạt yêu cầu"
            >
              <ThumbsUp size={13} className={liked === true ? "fill-current" : ""} />
            </button>
            <button
              onClick={() => setLiked(liked === false ? null : false)}
              className={`p-1.5 rounded-lg border border-[#BAE6FD] transition-all ${
                liked === false
                  ? "bg-red-500 text-white shadow-sm"
                  : "bg-white text-[#64748B] hover:text-red-600 hover:bg-red-50 shadow-tactile-doctor-pill"
              }`}
              title="Cần cải thiện chất lượng"
            >
              <ThumbsDown size={13} className={liked === false ? "fill-current" : ""} />
            </button>
          </div>

          <span className="text-[11px] text-[#0369A1] font-medium whitespace-nowrap">
            {wordsCount} từ • {charsCount} ký tự
          </span>
        </div>


        <div className="hidden md:flex items-center gap-1.5 text-[11px] text-[#0369A1]/80 font-medium whitespace-nowrap">
          <Clock size={12} className="text-[#0284C7]" />
          <span>Bản nháp — bác sĩ duyệt rồi mới dùng</span>
        </div>
      </div>

      {/* Modal / Popover hiển thị chi tiết câu thoại gốc tương ứng khi bấm vào [T...] */}
      {luotDangXem !== null && (() => {
        const l = banDoLuot.get(luotDangXem);
        return (
          <div
            className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-2xs flex items-center justify-center p-4 animate-in fade-in duration-150 no-print"
            onClick={() => setLuotDangXem(null)}
          >
            <div
              className="bg-white rounded-2xl border border-[#BAE6FD] shadow-2xl max-w-lg w-full p-5 text-left transform transition-all animate-in zoom-in-95 duration-150"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Header */}
              <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-3">
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-xl bg-sky-100 text-sky-700 flex items-center justify-center font-bold font-mono text-xs shadow-2xs">
                    T{luotDangXem}
                  </div>
                  <div>
                    <h3 className="font-bold text-slate-900 text-sm flex items-center gap-1.5">
                      <Quote size={14} className="text-[#0284C7]" />
                      <span>Căn cứ lời thoại gốc trong cuộc hội thoại</span>
                    </h3>
                    <p className="text-[11.5px] text-slate-500">
                      Bằng chứng đối chiếu trực tiếp từ lời nói thực tế của ca khám
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => setLuotDangXem(null)}
                  className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
                  title="Đóng"
                >
                  <X size={16} />
                </button>
              </div>

              {/* Speaker & Content */}
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 mb-4">
                <div className="flex items-center gap-2 mb-2">
                  <span
                    className={`px-2.5 py-0.5 rounded-md text-[11px] font-bold ${
                      l?.vai?.toLowerCase().includes("bác sĩ")
                        ? "bg-slate-200 text-slate-700"
                        : l?.vai?.toLowerCase().includes("người nhà")
                        ? "bg-amber-100 text-amber-800"
                        : "bg-sky-100 text-sky-800"
                    }`}
                  >
                    {l?.vai || `Lượt thoại [T${luotDangXem}]`}
                  </span>
                  <span className="text-[11px] text-slate-400 font-mono">
                    Lượt #{luotDangXem}
                  </span>
                </div>
                <p className="text-[14.5px] leading-relaxed text-slate-800 font-sans italic">
                  “{l?.chu || "Không tìm thấy nội dung của lượt thoại này trong bản chép."}”
                </p>
              </div>

              {/* Actions */}
              <div className="flex items-center justify-between gap-2 pt-2 border-t border-slate-100">
                <span className="text-[11px] text-slate-400">
                  Đối chiếu căn cứ lâm sàng MediTrace
                </span>
                <div className="flex items-center gap-2">
                  {onKiemChungLuot && (
                    <button
                      type="button"
                      onClick={() => {
                        const so = luotDangXem;
                        setLuotDangXem(null);
                        onKiemChungLuot(so);
                      }}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-[#0284C7] hover:bg-[#0369A1] text-white rounded-xl text-xs font-semibold shadow-tactile-doctor transition-all"
                      title="Mở màn hình kiểm chứng với sơ đồ đường nối căn cứ"
                    >
                      <span>Mở đối chiếu toàn màn hình</span>
                      <ArrowRight size={13} />
                    </button>
                  )}
                  <button
                    type="button"
                    onClick={() => setLuotDangXem(null)}
                    className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-semibold transition-colors"
                  >
                    Đóng
                  </button>
                </div>
              </div>
            </div>
          </div>
        );
      })()}

      {/* Modal Tiến Trình AI & 8 Chốt Phòng Vệ */}
      <NhatKyTienTrinhAIModal
        isOpen={moModalTienTrinhAI}
        onClose={() => setMoModalTienTrinhAI(false)}
        patientName={tenBenhNhanHienThi}
        transcript={transcript}
        noteContent={effectiveContent}
        clinicalSafety={noteMeta?.clinicalSafety}
        propositions={noteMeta?.propositions}
      />

      {/* Modal Tờ Dặn Dò Người Bệnh Bình Dân */}
      <ToDanDoBenhNhanModal
        isOpen={moModalDanDo}
        onClose={() => setMoModalDanDo(false)}
        patientName={tenBenhNhanHienThi}
        noteContent={effectiveContent}
        hoSo={savedLeaflet ?? hoSoDanDo[khoaHoSoDanDo] ?? hoSoDanDoTuCa}
        sessionId={sessionId}
        onDoiHoSo={(hoSo) => {
          setHoSoDanDo((cu) => ({ ...cu, [khoaHoSoDanDo]: hoSo }));
          onSaveLeaflet?.(hoSo);
        }}
      />

      <HisSmartCopyPopover
        open={moPanelHis}
        items={cacMucHis}
        onClose={() => setMoPanelHis(false)}
      />

      <BhytPrecheckModal
        open={moModalBhyt}
        loading={dangKiemBhyt}
        result={kqBhyt}
        onClose={() => setMoModalBhyt(false)}
        onInsertJustification={(cauBienLuan) => {
          const capNhat = chenGhiNhanKhamTrucTiep(
            tabContentRef.current,
            cauBienLuan,
            "[Bổ sung biện luận chỉ định CLS]",
          );
          handleTextChange(capNhat);
        }}
      />

      <BangDoiSoatThuocVaDonQuocGiaModal
        open={moModalThuocTt26}
        onClose={() => setMoModalThuocTt26(false)}
        patientName={tenBenhNhanHienThi}
        patientInfo={patientInfo}
        transcript={transcript}
        noteMeta={noteMeta}
        quyetDuyet={quyetDuyet}
        banSuaDuyet={banSuaDuyet}
        onInsertReconciliationToNote={(summaryBlock) => {
          const capNhat = chenGhiNhanKhamTrucTiep(
            tabContentRef.current,
            summaryBlock,
            "[Đối soát thuốc nền tại nhà]",
            /(?:THUỐC\s+ĐANG\s+DÙNG|TIỀN\s+SỬ|KẾ\s+HOẠCH\s+ĐIỀU\s+TRỊ|P\s*[—–-]\s*PLAN)/iu,
          );
          handleTextChange(capNhat);
        }}
        onSyncToLeaflet={(thuocDonMoi) => {
          const goc = savedLeaflet ?? hoSoDanDo[khoaHoSoDanDo] ?? hoSoDanDoTuCa;
          const giuThuocNha = (goc.thuoc || []).filter((t) =>
            /thuốc nền đang dùng tại nhà/i.test(t.loai || ""),
          );
          const moi: HoSoDD = {
            ...goc,
            thuoc: [
              ...thuocDonMoi,
              ...giuThuocNha.map((t, idx) => ({ ...t, id: thuocDonMoi.length + idx + 1 })),
            ],
          };
          setHoSoDanDo((cu) => ({ ...cu, [khoaHoSoDanDo]: moi }));
          onSaveLeaflet?.(moi);
        }}
      />

      <CamDoanThuThuatModal
        open={moModalCamDoanPttt}
        onClose={() => setMoModalCamDoanPttt(false)}
        sessionId={sessionId || tab.id}
        patientName={tenBenhNhanHienThi}
        patientInfo={patientInfo}
        transcript={transcript}
        noteMeta={noteMeta}
        quyetDuyet={quyetDuyet}
        banSuaDuyet={banSuaDuyet}
        onCreateConsentTab={onCreateCustomTab}
      />

      <DiBuongNoiTruModal
        open={moModalDiBuong}
        onClose={() => setMoModalDiBuong(false)}
        currentSession={currentSession}
        allSessions={allSessions}
        noteMeta={noteMeta}
        quyetDuyet={quyetDuyet}
        banSuaDuyet={banSuaDuyet}
        onCreateTab={onCreateCustomTab}
      />

      <SbarModal
        open={moModalSbar}
        sbarText={phieuSbar.vanBan}
        onClose={() => setMoModalSbar(false)}
      />
    </div>
  );
};
