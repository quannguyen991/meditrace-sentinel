/**
 * Tóm tắt Dọc Trước Khám (Pre-Visit Longitudinal Brief — Boost 2B) &
 * Trích xuất Nhiệm vụ Lâm sàng Hậu khám Tất định (Boost 11).
 *
 * 100% hàm thuần túy tất định (0 token LLM, chạy tức thời trên trình duyệt/Node).
 */
import type { ClinicalTask, Session } from "../types";
import type { Proposition } from "../components/VerificationView";
import { laChuTheBenhNhan } from "./bieuMauPhapLyOffline";

export interface DaiTomTatTruocKham {
  coDuLieuCu: boolean;
  soLanKhamTruoc: number;
  diUngDaXacNhan: string[];
  thuocManTinh: string[];
  bienThienSinhHieuXn: string[];
  viecHenTonDong: string[];
}

const TEN_GIA_DINH_MAC_DINH_RE = /^thêm\s+(?:tên\s+)?định\s+danh/iu;

const TU_KHOA_NHIEM_VU_RE =
  /(?:tái\s*khám|thử\s*lại|xét\s*nghiệm\s*lại|kiểm\s*tra\s*lại|đo\s*lại|siêu\s*âm\s*lại|chụp\s*lại|cấy\s*máu|cấy\s*đờm|cấy\s*nước\s*tiểu|hẹn\s*(?:tái\s*khám|khám\s*lại|lại|sau|\d)|chuyển\s*tuyến|chuyển\s*viện|chuyển\s*cơ\s*sở|hội\s*chẩn)/iu;

export function laDinhDanhBenhNhanThat(ten?: string | null): boolean {
  const t = (ten || "").trim();
  if (!t) return false;
  return !TEN_GIA_DINH_MAC_DINH_RE.test(t);
}

function parseNgayPhien(s: Session): number | null {
  const d = (s.date || "").trim();
  if (d) {
    const mDmy = d.match(/^(\d{1,2})[\/.\-](\d{1,2})[\/.\-](\d{4})/);
    if (mDmy) {
      return new Date(Number(mDmy[3]), Number(mDmy[2]) - 1, Number(mDmy[1])).getTime();
    }
    const mIso = d.match(/^(\d{4})-(\d{1,2})-(\d{1,2})/);
    if (mIso) {
      return new Date(Number(mIso[1]), Number(mIso[2]) - 1, Number(mIso[3])).getTime();
    }
    const mTh = d.match(/(\d{1,2})\s*th(?:áng)?\s*0?(\d{1,2})\s*(\d{4})/iu);
    if (mTh) {
      return new Date(Number(mTh[3]), Number(mTh[2]) - 1, Number(mTh[1])).getTime();
    }
    const mLan = d.match(/lần\s*(\d+)/iu);
    if (mLan) {
      return Number(mLan[1]);
    }
    if (/^hôm\s*nay$/iu.test(d)) {
      return Date.now();
    }
  }
  const mId = (s.id || "").match(/(\d{12,15})/);
  if (mId) return Number(mId[1]);
  return null;
}

function sapXepCaTuCuDenMoi(cacCa: Session[], currentId: string, allSessions: Session[]): Session[] {
  const coMoc = cacCa.map((s, idx) => ({ s, idx, moc: parseNgayPhien(s) }));
  if (coMoc.every((x) => x.moc !== null)) {
    return coMoc.sort((a, b) => (a.moc as number) - (b.moc as number) || a.idx - b.idx).map((x) => x.s);
  }
  // Trong App.tsx, ca mới nhất nằm ở đầu mảng (index 0). Nếu currentSession ở đầu mảng thì đảo ngược để cũ -> mới.
  const viTriCurrent = allSessions.findIndex((x) => x.id === currentId);
  if (viTriCurrent === 0) {
    return [...cacCa].reverse();
  }
  return cacCa;
}

function layMenhDeHieuLucBenhNhan(ca: Session): Proposition[] {
  const quyet = ca.duyet?.quyet || {};
  const banSua = ca.duyet?.banSua || {};
  const raw = ca.note?.propositions || [];
  return raw
    .filter((p) => quyet[p.id] !== "bo" && laChuTheBenhNhan(p))
    .map((p) => ({
      ...p,
      text: (quyet[p.id] === "sua" && banSua[p.id]?.trim() ? banSua[p.id].trim() : p.text || "").trim(),
    }))
    .filter((p) => p.text.length > 0);
}

function gomVanBanPhien(ca: Session): string {
  const mdText = layMenhDeHieuLucBenhNhan(ca).map((p) => p.text).join("\n");
  const tabText = (ca.tabs || [])
    .filter((t) => t.type !== "leaflet")
    .map((t) => t.content || "")
    .join("\n");
  return [mdText, ca.contextNotes || "", tabText, ca.transcript || ""].filter(Boolean).join("\n");
}

function themKhongTrung(mang: string[], chuoi: string) {
  const sach = chuoi.trim().replace(/\s*\[T\d+(?:,\s*T\d+)*\]\s*$/, "").trim();
  if (!sach) return;
  const khoa = sach.toLowerCase();
  if (!mang.some((x) => x.toLowerCase() === khoa)) {
    mang.push(sach);
  }
}

function kyHieuChieu(dau: number, cuoi: number, nguong = 0.01): string {
  if (cuoi - dau > nguong) return "↑";
  if (dau - cuoi > nguong) return "↓";
  return "→";
}

/**
 * Quét các ca khám trước của cùng `patientIdentifier` (loại trừ placeholder mặc định)
 * để tạo dải tóm tắt dọc trước khám: dị ứng đã xác nhận, thuốc mạn tính, xu hướng HA/eGFR/HbA1c (↑/↓),
 * và các đầu việc hẹn/cận lâm sàng còn tồn đọng.
 */
export function taoDaiTomTatTruocKham(
  currentSession: Session,
  allSessions: Session[]
): DaiTomTatTruocKham {
  if (!laDinhDanhBenhNhanThat(currentSession?.patientIdentifier)) {
    return {
      coDuLieuCu: false,
      soLanKhamTruoc: 0,
      diUngDaXacNhan: [],
      thuocManTinh: [],
      bienThienSinhHieuXn: [],
      viecHenTonDong: [],
    };
  }

  const maBn = currentSession.patientIdentifier.trim().toLowerCase();
  const thoCacCaTruoc = (allSessions || []).filter(
    (s) => s.id !== currentSession.id && laDinhDanhBenhNhanThat(s.patientIdentifier) && s.patientIdentifier.trim().toLowerCase() === maBn
  );

  if (thoCacCaTruoc.length === 0) {
    return {
      coDuLieuCu: false,
      soLanKhamTruoc: 0,
      diUngDaXacNhan: [],
      thuocManTinh: [],
      bienThienSinhHieuXn: [],
      viecHenTonDong: [],
    };
  }

  const cacCaTruoc = sapXepCaTuCuDenMoi(thoCacCaTruoc, currentSession.id, allSessions);

  const diUngDaXacNhan: string[] = [];
  const thuocManTinh: string[] = [];
  const viecHenTonDong: string[] = [];

  const chuoiHa: Array<{ sys: number; dia: number; ngay: string }> = [];
  const chuoiEgfr: Array<{ val: number; ngay: string }> = [];
  const chuoiHba1c: Array<{ val: number; ngay: string }> = [];

  const PHU_DINH_DI_UNG_RE =
    /(?<![\p{L}\p{N}_])(?:không|ko|chưa(?:\s+từng|\s+ghi\s+nhận|\s+rõ)?)\s+(?:có\s+|bị\s+)?(?:tiền\s+sử\s+)?(?:dị\s+ứng|mẫn\s+cảm)/iu;

  for (const ca of cacCaTruoc) {
    const dsMd = layMenhDeHieuLucBenhNhan(ca);
    for (const p of dsMd) {
      const sec = (p.section || "").toUpperCase();
      const txt = p.text;

      // 1. Dị ứng đã xác nhận
      if (
        !p.negated &&
        (sec.includes("DỊ ỨNG") || /\bdị\s*ứng|mẫn\s*cảm|phản\s*vệ\b/iu.test(txt)) &&
        !PHU_DINH_DI_UNG_RE.test(txt)
      ) {
        themKhongTrung(diUngDaXacNhan, txt);
      }

      // 2. Thuốc mạn tính / thuốc đã dùng
      if (
        !p.negated &&
        (Boolean(p.drug) ||
          sec.includes("THUỐC ĐANG DÙNG") ||
          sec.includes("ĐƠN THUỐC") ||
          (sec.includes("KẾ HOẠCH") && /\b(?:\d+\s*(?:mg|mcg|g|ml|viên)|amlodipin|losartan|metformin|insulin|atorvastatin|rosuvastatin|aspirin|clopidogrel|warfarin|bisoprolol)\b/iu.test(txt)))
      ) {
        themKhongTrung(thuocManTinh, p.drug ? `${p.drug} (${txt})` : txt);
      }

      // 3. Đầu việc hẹn / xét nghiệm tồn đọng từ lần trước
      if (!p.negated && TU_KHOA_NHIEM_VU_RE.test(txt)) {
        themKhongTrung(viecHenTonDong, `${txt}${ca.date ? ` (${ca.date})` : ""}`);
      }
    }

    // 4. Trích chỉ số sinh hiệu & xét nghiệm theo chuỗi thời gian
    const vanBan = gomVanBanPhien(ca);
    const mHa = vanBan.match(/huyết\s*áp\s*[:=\-]?\s*(\d{2,3})\s*\/\s*(\d{2,3})/iu);
    if (mHa) {
      chuoiHa.push({ sys: Number(mHa[1]), dia: Number(mHa[2]), ngay: ca.date || "Lần trước" });
    }
    const mEgfr = vanBan.match(/(?:egfr|mlct)\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)/iu);
    if (mEgfr) {
      chuoiEgfr.push({ val: Number(mEgfr[1].replace(",", ".")), ngay: ca.date || "Lần trước" });
    }
    const mHba1c = vanBan.match(/hba1c\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)/iu);
    if (mHba1c) {
      chuoiHba1c.push({ val: Number(mHba1c[1].replace(",", ".")), ngay: ca.date || "Lần trước" });
    }
  }

  // So sánh cả chỉ số mới vừa nhập ở tab Ngữ cảnh của ca hiện tại (nếu có) để hiện mũi tên ↑/↓ tức thì
  const vbHienTai = gomVanBanPhien(currentSession);
  const mHaMoi = vbHienTai.match(/huyết\s*áp\s*[:=\-]?\s*(\d{2,3})\s*\/\s*(\d{2,3})/iu);
  if (mHaMoi && chuoiHa.length === 1) {
    chuoiHa.push({ sys: Number(mHaMoi[1]), dia: Number(mHaMoi[2]), ngay: "Hôm nay" });
  }
  const mEgfrMoi = vbHienTai.match(/(?:egfr|mlct)\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)/iu);
  if (mEgfrMoi && chuoiEgfr.length === 1) {
    chuoiEgfr.push({ val: Number(mEgfrMoi[1].replace(",", ".")), ngay: "Hôm nay" });
  }
  const mHba1cMoi = vbHienTai.match(/hba1c\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)/iu);
  if (mHba1cMoi && chuoiHba1c.length === 1) {
    chuoiHba1c.push({ val: Number(mHba1cMoi[1].replace(",", ".")), ngay: "Hôm nay" });
  }

  const bienThienSinhHieuXn: string[] = [];
  if (chuoiHa.length >= 2) {
    const dau = chuoiHa[0];
    const cuoi = chuoiHa[chuoiHa.length - 1];
    const chieu = kyHieuChieu(dau.sys, cuoi.sys, 1);
    bienThienSinhHieuXn.push(`HA: ${dau.sys}/${dau.dia} → ${cuoi.sys}/${cuoi.dia} mmHg (${chieu})`);
  } else if (chuoiHa.length === 1) {
    bienThienSinhHieuXn.push(`HA gần nhất: ${chuoiHa[0].sys}/${chuoiHa[0].dia} mmHg`);
  }

  if (chuoiEgfr.length >= 2) {
    const dau = chuoiEgfr[0];
    const cuoi = chuoiEgfr[chuoiEgfr.length - 1];
    const chieu = kyHieuChieu(dau.val, cuoi.val, 0.5);
    bienThienSinhHieuXn.push(`eGFR: ${dau.val} → ${cuoi.val} mL/phút (${chieu})`);
  } else if (chuoiEgfr.length === 1) {
    bienThienSinhHieuXn.push(`eGFR gần nhất: ${chuoiEgfr[0].val} mL/phút`);
  }

  if (chuoiHba1c.length >= 2) {
    const dau = chuoiHba1c[0];
    const cuoi = chuoiHba1c[chuoiHba1c.length - 1];
    const chieu = kyHieuChieu(dau.val, cuoi.val, 0.05);
    bienThienSinhHieuXn.push(`HbA1c: ${dau.val}% → ${cuoi.val}% (${chieu})`);
  } else if (chuoiHba1c.length === 1) {
    bienThienSinhHieuXn.push(`HbA1c gần nhất: ${chuoiHba1c[0].val}%`);
  }

  return {
    coDuLieuCu: true,
    soLanKhamTruoc: cacCaTruoc.length,
    diUngDaXacNhan,
    thuocManTinh,
    bienThienSinhHieuXn,
    viecHenTonDong,
  };
}

function phanTichHanVaMucUuTien(vanBan: string): { dueDate: string; priority: "high" | "medium" | "low" } {
  const t = vanBan.toLowerCase();

  if (/(?:cấp\s*cứu|khẩn\s*cấp|ngay\s*lập\s*tức|chuyển\s*tuyến\s*ngay|chuyển\s*viện\s*ngay)/iu.test(t)) {
    return { dueDate: "Ngay hôm nay (Khẩn)", priority: "high" };
  }

  const mGio = t.match(/(?:sau\s*)?(\d{1,2})\s*(?:giờ|tiếng)/iu);
  if (mGio) {
    return { dueDate: `Sau ${mGio[1]} giờ`, priority: "high" };
  }

  if (/(?:ngày\s*mai|sáng\s*mai|trưa\s*mai|chiều\s*mai)/iu.test(t)) {
    return { dueDate: "Ngày mai", priority: "high" };
  }

  const mNgay = t.match(/(?:sau\s*|hẹn\s*)?(\d{1,2})\s*ngày(?:\s*nữa|\s*sau|\s*tới)?/iu);
  if (mNgay) {
    const n = Number(mNgay[1]);
    return {
      dueDate: `Sau ${n} ngày`,
      priority: n <= 3 || /cấy\s*máu|hội\s*chẩn|chuyển\s*tuyến/iu.test(t) ? "high" : "medium",
    };
  }

  const mTuan = t.match(/(?:sau\s*|hẹn\s*)?(\d{1,2})\s*tuần(?:\s*nữa|\s*sau|\s*tới)?/iu);
  if (mTuan) {
    const w = Number(mTuan[1]);
    return {
      dueDate: `Sau ${w} tuần`,
      priority: w <= 1 && /xét\s*nghiệm\s*lại|thử\s*lại|cấy\s*máu/iu.test(t) ? "high" : "medium",
    };
  }

  const mThang = t.match(/(?:sau\s*|hẹn\s*)?(\d{1,2})\s*tháng(?:\s*nữa|\s*sau|\s*tới)?/iu);
  if (mThang) {
    const th = Number(mThang[1]);
    return {
      dueDate: `Sau ${th} tháng`,
      priority: th >= 3 ? "low" : "medium",
    };
  }

  const mNgayCuThe = vanBan.match(/\b(\d{1,2}[\/.\-]\d{1,2}(?:[\/.\-]\d{2,4})?)\b/);
  if (mNgayCuThe) {
    return {
      dueDate: `Ngày ${mNgayCuThe[1]}`,
      priority: /chuyển\s*tuyến|hội\s*chẩn|cấy\s*máu/iu.test(t) ? "high" : "medium",
    };
  }

  if (/chuyển\s*tuyến|chuyển\s*viện|hội\s*chẩn|cấy\s*máu/iu.test(t)) {
    return { dueDate: "Hôm nay", priority: "high" };
  }

  return { dueDate: "Theo lịch hẹn ca khám", priority: "medium" };
}

/**
 * Trích xuất tất định danh sách Nhiệm vụ Lâm sàng (`ClinicalTask[]`) từ các mệnh đề kế hoạch / dặn dò
 * đã duyệt của tất cả các ca khám (`sessions`).
 */
export function trichNhiemVuTuCacCaKham(sessions: Session[]): ClinicalTask[] {
  const ketQua: ClinicalTask[] = [];
  const daCo = new Set<string>();

  for (const ca of sessions || []) {
    const tenBn = laDinhDanhBenhNhanThat(ca.patientIdentifier)
      ? ca.patientIdentifier.trim()
      : (ca.patientSubtitle || "").trim() && !/^Ca khám mới$/i.test((ca.patientSubtitle || "").trim())
      ? ca.patientSubtitle.trim()
      : "Bệnh nhân ca khám";

    const dsMd = layMenhDeHieuLucBenhNhan(ca);
    for (const p of dsMd) {
      if (p.negated) continue;
      const sec = (p.section || "").toUpperCase();
      const laMucKeHoach =
        sec.includes("KẾ HOẠCH") ||
        sec.includes("XỬ TRÍ") ||
        sec.includes("ĐIỀU TRỊ") ||
        sec.includes("DẶN") ||
        sec.includes("CHẨN ĐOÁN") ||
        sec.includes("CẬN LÂM SÀNG") ||
        (p.situation || "").toLowerCase() === "kế hoạch" ||
        sec === "";

      if (!laMucKeHoach) continue;
      if (!TU_KHOA_NHIEM_VU_RE.test(p.text)) continue;

      const tieuDeSach = p.text.replace(/\s*\[T\d+(?:,\s*T\d+)*\]\s*$/, "").trim();
      if (!tieuDeSach) continue;

      const dedupKey = `${ca.id}::${tieuDeSach.toLowerCase()}`;
      if (daCo.has(dedupKey)) continue;
      daCo.add(dedupKey);

      const { dueDate, priority } = phanTichHanVaMucUuTien(tieuDeSach);
      ketQua.push({
        id: `auto-task-${ca.id}-p${p.id}`,
        title: tieuDeSach,
        sessionId: ca.id,
        patientName: tenBn,
        dueDate,
        completed: false,
        priority,
      });
    }
  }

  return ketQua;
}
