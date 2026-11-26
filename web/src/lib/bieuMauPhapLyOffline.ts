/**
 * Bộ Biên dịch Biểu mẫu Pháp lý & Chuyên khoa 100% Tại chỗ (Boost 7 & Boost 12).
 *
 * Nguyên tắc bất biến an toàn lâm sàng:
 * 1. 100% luật tất định chạy tại chỗ (< 10 ms), KHÔNG gọi mô hình ngoài, 0 byte rời máy.
 * 2. CHỈ dùng mệnh đề còn hiệu lực (`quyet !== "bo"`), áp dụng bản sửa của bác sĩ (`quyet === "sua"`).
 * 3. Tách bạch chủ thể: chỉ mệnh đề của người bệnh (`chu_the_id === 0` / `subject` thuộc bệnh nhân)
 *    mới đi vào các mục lâm sàng của người bệnh; thông tin người nhà tách sang mục riêng.
 * 4. Mọi nhận định đều gắn dẫn nguồn `[T_i]`; thông tin chưa có trong nguồn luôn ghi `[cần bổ sung]`;
 *    mệnh đề còn ở trạng thái `Cần bác sĩ xác nhận` (chưa bấm Giữ/Sửa) được gom riêng ở cuối phiếu.
 */
import type { Session } from "../types";
import type { NoteMeta, Proposition, Quyet } from "../components/VerificationView";
import { canXacNhan } from "./compileEffectiveNote";
import { xayNguCanhChoTaoHoSo } from "./nguCanhTroLy";

export const DANH_SACH_MAU_BIEN_DICH_TAI_CHO = [
  "phieu-chuyen-co-so-kcb-tt01-2025",
  "phieu-chuyen-cls-tt01-2025",
  "giay-nghi-bhxh-tt25-2025",
  "tom-tat-hsba-ra-vien-tt32",
  "bien-ban-hoi-chan-tt32",
  "khuon-nhi-khoa",
  "khuon-san-phu-khoa",
  "khuon-cap-cuu-chan-thuong",
] as const;

export type MaBieuMauTaiCho = (typeof DANH_SACH_MAU_BIEN_DICH_TAI_CHO)[number];

export function laMauBienDichTaiCho(mauId?: string | null): mauId is MaBieuMauTaiCho {
  return Boolean(mauId && (DANH_SACH_MAU_BIEN_DICH_TAI_CHO as readonly string[]).includes(mauId));
}

const TAP_CHU_THE_BENH_NHAN = new Set([
  "",
  "bệnh nhân",
  "người bệnh",
  "tôi",
  "tui",
  "em",
  "mình",
  "bản thân",
  "patient",
  "self",
  "trẻ",
  "bé",
  "em bé",
  "trẻ nhỏ",
  "bệnh nhi",
  "cháu",
  "cháu bé",
  "bé nhà em",
  "bé nhà tôi",
  "cháu nhà em",
  "cháu nhà tôi",
  "thai phụ",
  "sản phụ",
  "bác sĩ",
  "bác sỹ",
  "điều dưỡng",
]);

type MenhDeMoRong = Proposition & { chu_the_id?: number | null };

export function laChuTheBenhNhan(p: MenhDeMoRong): boolean {
  const sec = (p.section || "").toUpperCase();
  if (sec.includes("GIA ĐÌNH")) return false;
  if (p.chu_the_id !== undefined && p.chu_the_id !== null) {
    return Number(p.chu_the_id) === 0;
  }
  const subj = (p.subject || "").trim().toLowerCase();
  return TAP_CHU_THE_BENH_NHAN.has(subj);
}

interface MenhDeDaChuan {
  id: number;
  section: string;
  text: string;
  textKemNguon: string;
  negated: boolean;
  drug?: string | null;
  turns: number[];
  laBenhNhan: boolean;
  conCanXacNhan: boolean;
}

function dinhDangKemNguon(text: string, turns?: number[]): string {
  const sach = text.trim().replace(/\s*\[T\d+(?:,\s*T\d+)*\]\s*$/, "").trim();
  const dsLuot = Array.isArray(turns) ? turns.filter((n) => Number.isFinite(n) && n > 0) : [];
  if (dsLuot.length === 0) return sach;
  return `${sach} [T${dsLuot.join(", T")}]`;
}

function chuanBiMenhDe(
  note?: NoteMeta | null,
  quyetDuyet?: Record<number, Quyet>,
  banSuaDuyet?: Record<number, string>
): {
  bnDaDuyet: MenhDeDaChuan[];
  giaDinhDaDuyet: MenhDeDaChuan[];
  choXacNhan: MenhDeDaChuan[];
} {
  const raw = Array.isArray(note?.propositions) ? (note!.propositions as MenhDeMoRong[]) : [];
  const quyet = quyetDuyet || {};
  const banSua = banSuaDuyet || {};

  const bnDaDuyet: MenhDeDaChuan[] = [];
  const giaDinhDaDuyet: MenhDeDaChuan[] = [];
  const choXacNhan: MenhDeDaChuan[] = [];

  for (const p of raw) {
    const q = quyet[p.id];
    if (q === "bo") continue;

    const chuHieuLuc = (q === "sua" && banSua[p.id]?.trim() ? banSua[p.id].trim() : p.text || "").trim();
    if (!chuHieuLuc) continue;

    const chuaChotCanXacNhan = canXacNhan(p) && q !== "giu" && q !== "sua";
    const laBn = laChuTheBenhNhan(p);
    const item: MenhDeDaChuan = {
      id: p.id,
      section: (p.section || "").toUpperCase(),
      text: chuHieuLuc,
      textKemNguon: dinhDangKemNguon(chuHieuLuc, p.evidenceTurns),
      negated: Boolean(p.negated),
      drug: p.drug,
      turns: p.evidenceTurns || [],
      laBenhNhan: laBn,
      conCanXacNhan: chuaChotCanXacNhan,
    };

    if (chuaChotCanXacNhan) {
      choXacNhan.push(item);
    } else if (laBn) {
      bnDaDuyet.push(item);
    } else {
      giaDinhDaDuyet.push(item);
    }
  }

  return { bnDaDuyet, giaDinhDaDuyet, choXacNhan };
}

function ghepDanhSach(ds: MenhDeDaChuan[], macDinh = "[cần bổ sung]"): string {
  if (ds.length === 0) return `- ${macDinh}`;
  return ds.map((m) => `- ${m.textKemNguon}`).join("\n");
}

function layThongTinHanhChinh(session?: Session, note?: NoteMeta | null) {
  const ncPayload = xayNguCanhChoTaoHoSo({
    sessionId: session?.id,
    patientIdentifier: session?.patientIdentifier,
    patientSubtitle: session?.patientSubtitle,
    tabs: session?.tabs,
    contextNotes: session?.contextNotes,
  });
  const tt = (ncPayload.thong_tin_benh_nhan || {}) as Record<string, any>;
  const xn = ncPayload.du_lieu_xet_nghiem || {};

  const hoTen = (tt.ho_ten as string) || "[cần bổ sung họ và tên người bệnh]";
  const tuoiNam = typeof tt.tuoi === "number" ? tt.tuoi : undefined;
  const thangTuoi = typeof tt.thang_tuoi === "number" ? tt.thang_tuoi : undefined;
  const gioiTinh = tt.gioi_tinh === "nữ" ? "Nữ" : tt.gioi_tinh === "nam" ? "Nam" : "[cần bổ sung]";
  const canNangKg = typeof tt.can_nang_kg === "number" ? tt.can_nang_kg : undefined;
  const chieuCaoCm = typeof tt.chieu_cao_cm === "number" ? tt.chieu_cao_cm : undefined;

  const chuoiTuoi =
    thangTuoi !== undefined
      ? `${thangTuoi} tháng tuổi${tuoiNam !== undefined ? ` (${tuoiNam} tuổi)` : ""}`
      : tuoiNam !== undefined
      ? `${tuoiNam} tuổi`
      : "[cần bổ sung tuổi / ngày sinh]";

  const icdChinh = note?.clinicalSafety?.bhyt_icd10?.ma_icd10_chinh;
  const icdKem: Array<{ ma_icd10: string; ten_benh_byt: string }> =
    note?.clinicalSafety?.bhyt_icd10?.ma_icd10_kem_theo || [];

  const ngayLap = session?.date && session.date !== "Hôm nay" ? session.date : new Date().toLocaleDateString("vi-VN");
  const maHoSo = note?.caseId || session?.id || "[cần bổ sung mã hồ sơ]";

  const chuoiXnNguCanh = Object.entries(xn)
    .map(([k, v]) => `${k}: ${v}`)
    .join("; ");

  return {
    hoTen,
    tuoiNam,
    thangTuoi,
    chuoiTuoi,
    gioiTinh,
    canNangKg,
    chieuCaoCm,
    coThai: Boolean(tt.co_thai),
    icdChinh,
    icdKem,
    ngayLap,
    maHoSo,
    chuoiXnNguCanh,
    contextText: ncPayload.context || "",
  };
}

function khoiCanXacNhanCuoiPhieu(choXacNhan: MenhDeDaChuan[]): string {
  if (choXacNhan.length === 0) return "";
  return (
    "\n\n---\n⚠️ MỤC CHƯA ĐƯA VÀO NỘI DUNG PHÁP LÝ CHÍNH THỨC (CẦN BÁC SĨ XÁC NHẬN TRƯỚC KHI KÝ):\n" +
    choXacNhan
      .map((m) => `- [${m.laBenhNhan ? "Bệnh nhân" : "Người nhà"}] ${m.textKemNguon}`)
      .join("\n")
  );
}

function chanTrangPhapLy(tenThongTu: string): string {
  return (
    `\n\n---\n[Biên dịch tất định 100% tại chỗ · Luật biểu mẫu ${tenThongTu} · 0 byte gửi ra ngoài · ` +
    `Chỉ lấy mệnh đề đã giữ/sửa có dẫn nguồn [T_i], không tự suy diễn. Bác sĩ kiểm tra và điền các mục [cần bổ sung] trước khi ký.]`
  );
}

export function bienDichBieuMauPhapLyTaiCho(
  mauId: string,
  params: {
    session?: Session;
    note?: NoteMeta | null;
    quyetDuyet?: Record<number, Quyet>;
    banSuaDuyet?: Record<number, string>;
  }
): string | null {
  if (!laMauBienDichTaiCho(mauId)) return null;

  const session = params.session;
  const note = params.note ?? session?.note ?? null;
  const quyet = params.quyetDuyet ?? session?.duyet?.quyet ?? {};
  const banSua = params.banSuaDuyet ?? session?.duyet?.banSua ?? {};

  const hc = layThongTinHanhChinh(session, note);
  const { bnDaDuyet, giaDinhDaDuyet, choXacNhan } = chuanBiMenhDe(note, quyet, banSua);

  const dsLyDo = bnDaDuyet.filter((m) => m.section.includes("LÝ DO"));
  const dsBenhSu = bnDaDuyet.filter((m) => m.section.includes("BỆNH SỬ"));
  const dsTienSu = bnDaDuyet.filter((m) => m.section.includes("TIỀN SỬ"));
  const dsDiUng = bnDaDuyet.filter((m) => m.section.includes("DỊ ỨNG") || /\bdị\s*ứng\b/iu.test(m.text));
  const dsThuocDangDung = bnDaDuyet.filter((m) => m.section.includes("THUỐC ĐANG DÙNG"));
  const dsKham = bnDaDuyet.filter(
    (m) => m.section.includes("KHÁM") || m.section.includes("SINH HIỆU") || m.section.includes("THỰC THỂ")
  );
  const dsCls = bnDaDuyet.filter(
    (m) =>
      m.section.includes("CẬN LÂM SÀNG") ||
      m.section.includes("XÉT NGHIỆM") ||
      /(?:xét\s*nghiệm|x-quang|siêu\s*âm|ct|mri|điện\s*tim|ecg|creatinin|egfr|hba1c|troponin|bạch\s*cầu|wbc|crp)/iu.test(
        m.text
      )
  );
  const dsChanDoan = bnDaDuyet.filter(
    (m) => m.section.includes("CHẨN ĐOÁN") || m.section.includes("ĐÁNH GIÁ") || m.section.includes("TÓM TẮT")
  );
  const dsKeHoach = bnDaDuyet.filter(
    (m) =>
      m.section.includes("KẾ HOẠCH") ||
      m.section.includes("ĐƠN THUỐC") ||
      m.section.includes("XỬ TRÍ") ||
      m.section.includes("ĐIỀU TRỊ") ||
      m.section.includes("DẶN")
  );
  const dsThuocTatCa = bnDaDuyet.filter(
    (m) =>
      Boolean(m.drug) ||
      m.section.includes("THUỐC") ||
      /(?:\b\d+\s*(?:mg|mcg|g|ml|viên|ống|gói)\b|uống\s+ngày|tiêm|truyền)/iu.test(m.text)
  );

  const chuoiChanDoanIcd =
    dsChanDoan.length > 0
      ? dsChanDoan.map((m) => m.textKemNguon).join("; ") +
        (hc.icdChinh ? ` — Mã ICD-10 chính: ${hc.icdChinh.ma_icd10} (${hc.icdChinh.ten_benh_byt})` : " — Mã ICD-10: [cần bổ sung]")
      : hc.icdChinh
      ? `${hc.icdChinh.ten_benh_byt} [ICD-10: ${hc.icdChinh.ma_icd10}] (cần bác sĩ đối chiếu lâm sàng)`
      : "[cần bổ sung chẩn đoán & mã ICD-10]";

  const chuoiBenhKem =
    hc.icdKem.length > 0
      ? hc.icdKem.map((x) => `${x.ten_benh_byt} (${x.ma_icd10})`).join("; ")
      : "[cần bổ sung nếu có]";

  // ---------------------------------------------------------------------------
  // 1. PHIẾU CHUYỂN CƠ SỞ KCB BHYT (PHỤ LỤC THÔNG TƯ 01/2025/TT-BYT)
  // ---------------------------------------------------------------------------
  if (mauId === "phieu-chuyen-co-so-kcb-tt01-2025") {
    const dsLyDoChuyen = dsKeHoach.filter((m) => /chuyển\s*(?:tuyến|viện|cơ\s*sở|khoa)/iu.test(m.text));
    return (
      [
        "# PHIẾU CHUYỂN CƠ SỞ KHÁM BỆNH, CHỮA BỆNH BẢO HIỂM Y TẾ",
        "*(Theo Phụ lục Thông tư số 01/2025/TT-BYT của Bộ Y tế — 3 cấp chuyên môn kỹ thuật)*",
        "",
        "I. HÀNH CHÍNH & PHÂN CẤP CHUYÊN MÔN KỸ THUẬT",
        `- Cơ sở KCB chuyển đi: [cần bổ sung tên cơ sở KCB] — Cấp chuyên môn kỹ thuật: [ ] Cấp ban đầu  [ ] Cấp cơ bản  [ ] Cấp chuyên sâu`,
        `- Kính chuyển đến cơ sở KCB: [cần bổ sung nơi chuyển đến] — Cấp chuyên môn kỹ thuật: [ ] Cấp ban đầu  [ ] Cấp cơ bản  [ ] Cấp chuyên sâu`,
        `- Số hồ sơ / Mã ca: ${hc.maHoSo} | Ngày lập phiếu: ${hc.ngayLap}`,
        `- Họ và tên người bệnh: ${hc.hoTen} | Tuổi: ${hc.chuoiTuoi} | Giới tính: ${hc.gioiTinh}`,
        `- Mã số thẻ BHYT: [cần bổ sung mã thẻ BHYT] | Hạn sử dụng thẻ: [cần bổ sung]`,
        "",
        "II. TÓM TẮT LÂM SÀNG & QUÁ TRÌNH ĐIỀU TRỊ",
        "1. Dấu hiệu lâm sàng chính (Lý do khám, bệnh sử, khám thực thể):",
        ghepDanhSach([...dsLyDo, ...dsBenhSu, ...dsKham], "[cần bổ sung tóm tắt dấu hiệu lâm sàng]"),
        "",
        "2. Kết quả xét nghiệm, cận lâm sàng đã thực hiện:",
        dsCls.length > 0
          ? ghepDanhSach(dsCls)
          : hc.chuoiXnNguCanh
          ? `- Chỉ số xét nghiệm từ ngữ cảnh hồ sơ: ${hc.chuoiXnNguCanh}`
          : "- [cần bổ sung kết quả xét nghiệm, cận lâm sàng]",
        "",
        "3. Chẩn đoán xác định / Chẩn đoán sơ bộ (kèm mã ICD-10):",
        `- Chẩn đoán chính: ${chuoiChanDoanIcd}`,
        `- Bệnh kèm theo: ${chuoiBenhKem}`,
        `- Tiền sử dị ứng ghi nhận: ${dsDiUng.length > 0 ? dsDiUng.map((d) => d.textKemNguon).join("; ") : "[cần bổ sung]"}`,
        "",
        "4. Phương pháp, thủ thuật, kỹ thuật, thuốc đã sử dụng trong điều trị:",
        ghepDanhSach(dsThuocTatCa, "[cần bổ sung thuốc / kỹ thuật đã xử trí]"),
        "",
        "5. Tình trạng người bệnh lúc chuyển cơ sở KCB:",
        dsKham.length > 0
          ? ghepDanhSach(dsKham)
          : "- Tỉnh táo / Sinh hiệu lúc chuyển: [cần bổ sung Mạch, Huyết áp, SpO2 lúc chuyển]",
        "",
        "6. Lý do chuyển cơ sở KCB & Thời hạn hiệu lực phiếu (TT 01/2025/TT-BYT):",
        dsLyDoChuyen.length > 0
          ? ghepDanhSach(dsLyDoChuyen)
          : "- Lý do chuyển: [ ] Đủ điều kiện chuyển cơ sở KCB theo quy định chuyên môn  [ ] Theo yêu cầu của người bệnh / người đại diện hợp pháp — Chi tiết: [cần bổ sung]",
        "- Hiệu lực sử dụng phiếu chuyển BHYT:",
        "  [ ] Phiếu có giá trị sử dụng trong 01 năm (12 tháng) kể từ ngày ký (áp dụng bệnh mạn tính theo Phụ lục TT 01/2025/TT-BYT)",
        "  [ ] Phiếu có giá trị chuyển 01 đợt khám bệnh, chữa bệnh",
        `- Thời gian chuyển đi: [cần bổ sung giờ/ngày] | Phương tiện vận chuyển & Người hộ tống: [cần bổ sung]`,
      ].join("\n") +
      khoiCanXacNhanCuoiPhieu(choXacNhan) +
      chanTrangPhapLy("Thông tư 01/2025/TT-BYT")
    );
  }

  // ---------------------------------------------------------------------------
  // 2. PHIẾU CHUYỂN DỊCH VỤ CẬN LÂM SÀNG (THÔNG TƯ 01/2025/TT-BYT)
  // ---------------------------------------------------------------------------
  if (mauId === "phieu-chuyen-cls-tt01-2025") {
    const dsChiDinhCls = [...dsCls, ...dsKeHoach].filter((m) =>
      /(?:xét\s*nghiệm|chụp|siêu\s*âm|ct|mri|nội\s*soi|điện\s*tim|sinh\s*thiết|cấy|cận\s*lâm\s*sàng|pcr)/iu.test(m.text)
    );
    return (
      [
        "# PHIẾU CHUYỂN THỰC HIỆN DỊCH VỤ CẬN LÂM SÀNG BHYT",
        "*(Theo Thông tư số 01/2025/TT-BYT của Bộ Y tế)*",
        "",
        "I. THÔNG TIN HÀNH CHÍNH",
        `- Cơ sở KCB chỉ định: [cần bổ sung] | Kính chuyển đến cơ sở thực hiện CLS: [cần bổ sung]`,
        `- Họ và tên người bệnh: ${hc.hoTen} | Tuổi: ${hc.chuoiTuoi} | Giới tính: ${hc.gioiTinh}`,
        `- Mã thẻ BHYT: [cần bổ sung] | Mã hồ sơ: ${hc.maHoSo} | Ngày chỉ định: ${hc.ngayLap}`,
        `- Hình thức chuyển: [ ] Chuyển người bệnh đến cơ sở thực hiện CLS   [ ] Chuyển mẫu bệnh phẩm`,
        "",
        "II. TÓM TẮT LÂM SÀNG & CHẨN ĐOÁN",
        "1. Tóm tắt diễn biến lâm sàng liên quan chỉ định:",
        ghepDanhSach([...dsLyDo, ...dsBenhSu, ...dsKham], "[cần bổ sung triệu chứng lâm sàng liên quan]"),
        `2. Chẩn đoán sơ bộ / xác định: ${chuoiChanDoanIcd}`,
        "",
        "III. DANH MỤC DỊCH VỤ KỸ THUẬT CẬN LÂM SÀNG ĐỀ NGHỊ THỰC HIỆN",
        ghepDanhSach(dsChiDinhCls, "[cần bổ sung tên dịch vụ kỹ thuật cận lâm sàng đề nghị thực hiện]"),
        "",
        "IV. LÝ DO CHUYỂN THỰC HIỆN DỊCH VỤ CẬN LÂM SÀNG",
        "- [ ] Cơ sở KCB hiện tại tạm thời hết hoá chất / vật tư hoặc thiết bị đang bảo trì",
        "- [ ] Dịch vụ kỹ thuật vượt khả năng thực hiện tại chỗ theo phân cấp chuyên môn (TT 01/2025/TT-BYT)",
        "- Ghi chú chuyên môn kèm theo: [cần bổ sung]",
      ].join("\n") +
      khoiCanXacNhanCuoiPhieu(choXacNhan) +
      chanTrangPhapLy("Thông tư 01/2025/TT-BYT")
    );
  }

  // ---------------------------------------------------------------------------
  // 3. GIẤY CHỨNG NHẬN NGHỈ VIỆC HƯỞNG BHXH (THÔNG TƯ 25/2025/TT-BYT)
  // ---------------------------------------------------------------------------
  if (mauId === "giay-nghi-bhxh-tt25-2025") {
    const laTreDuoi7Tuoi =
      (hc.thangTuoi !== undefined && hc.thangTuoi < 84) ||
      (hc.tuoiNam !== undefined && hc.tuoiNam < 7);

    let soNgayNghi: number | null = null;
    for (const m of [...dsKeHoach, ...bnDaDuyet]) {
      const khopNgay = m.text.match(/nghỉ\s*(?:làm|việc|học|ngơi|bhxh)?\s*(\d{1,3})\s*ngày/iu);
      if (khopNgay) {
        soNgayNghi = Number(khopNgay[1]);
        break;
      }
    }

    const canhBaoTran30Ngay =
      soNgayNghi !== null && soNgayNghi > 30
        ? `\n- ⚠️ CẢNH BÁO PHÁP LÝ TT 25/2025/TT-BYT: Số ngày nghỉ ngoại trú ghi nhận (${soNgayNghi} ngày) VƯỢT TRẦN TỐI ĐA 30 NGÀY/LẦN CẤP! Bác sĩ bắt buộc kiểm tra lại, tách đợt khám hoặc hội chẩn theo quy định.`
        : "";

    const dongSoNgayNghi =
      soNgayNghi !== null
        ? `${soNgayNghi} ngày (${soNgayNghi <= 30 ? "Hợp lệ ≤ 30 ngày/lần khám ngoại trú theo TT 25/2025/TT-BYT" : "VƯỢT TRẦN 30 NGÀY/LẦN — CẦN CHỈNH SỬA"}) — Từ ngày: [cần bổ sung] đến hết ngày: [cần bổ sung]`
        : "[cần bổ sung số ngày nghỉ — tối đa 30 ngày cho một lần khám ngoại trú theo TT 25/2025/TT-BYT] — Từ ngày: [cần bổ sung] đến hết ngày: [cần bổ sung]";

    const khoiChaMe = laTreDuoi7Tuoi
      ? [
          "II. THÔNG TIN CHA / MẸ (BẮT BUỘC ĐỐI VỚI BỆNH NHI DƯỚI 7 TUỔI — TT 25/2025/TT-BYT)",
          `- Họ và tên cha hoặc người nuôi dưỡng: [cần bổ sung bắt buộc]`,
          `- Họ và tên mẹ hoặc người chăm sóc hưởng BHXH: [cần bổ sung bắt buộc]`,
          ...(giaDinhDaDuyet.length > 0
            ? [`- Ghi nhận lời khai người chăm sóc đi cùng: ${giaDinhDaDuyet.map((g) => g.textKemNguon).join("; ")}`]
            : []),
        ].join("\n")
      : [
          "II. THÔNG TIN CHA / MẸ (CHỈ GHI NẾU NGƯỜI BỆNH LÀ TRẺ DƯỚI 7 TUỔI)",
          `- Đối tượng hiện tại (${hc.chuoiTuoi}): ${hc.tuoiNam === undefined ? "[cần kiểm tra tuổi: nếu trẻ < 7 tuổi bắt buộc ghi họ tên Cha/Mẹ]" : "Người bệnh ≥ 7 tuổi (không bắt buộc ghi họ tên cha/mẹ)"}`,
        ].join("\n");

    return (
      [
        "# GIẤY CHỨNG NHẬN NGHỈ VIỆC HƯỞNG BẢO HIỂM XÃ HỘI",
        "*(Theo Thông tư số 25/2025/TT-BYT quy định chi tiết thi hành Luật BHXH về lĩnh vực y tế)*",
        "",
        "I. THÔNG TIN NGƯỜI BỆNH",
        `- Số seri / Số hồ sơ khám bệnh: ${hc.maHoSo} | Ngày cấp: ${hc.ngayLap}`,
        `- Họ và tên người bệnh: ${hc.hoTen} | Tuổi / Ngày sinh: ${hc.chuoiTuoi} | Giới tính: ${hc.gioiTinh}`,
        `- Mã số BHXH / Mã số thẻ BHYT: [cần bổ sung mã số BHXH / BHYT]`,
        `- Đơn vị làm việc (tên cơ quan, tổ chức): [cần bổ sung đơn vị làm việc]`,
        "",
        khoiChaMe,
        "",
        "III. CHẨN ĐOÁN VÀ PHƯƠNG PHÁP ĐIỀU TRỊ",
        `- Chẩn đoán xác định và mã bệnh ICD-10: ${chuoiChanDoanIcd}`,
        "- Phương pháp điều trị / Hướng xử trí của bác sĩ:",
        ghepDanhSach(dsKeHoach.length > 0 ? dsKeHoach : dsThuocTatCa, "[cần bổ sung phương pháp điều trị]"),
        "",
        "IV. SỐ NGÀY NGHỈ VIỆC HƯỞNG BHXH (KIỂM TRA TRẦN NGOẠI TRÚ ≤ 30 NGÀY/LẦN)",
        `- Số ngày nghỉ: ${dongSoNgayNghi}${canhBaoTran30Ngay}`,
        `- Xác nhận của Thủ trưởng đơn vị & Bác sĩ KCB (chữ ký số / đóng dấu): [cần bổ sung]`,
      ].join("\n") +
      khoiCanXacNhanCuoiPhieu(choXacNhan) +
      chanTrangPhapLy("Thông tư 25/2025/TT-BYT")
    );
  }

  // ---------------------------------------------------------------------------
  // 4. BẢN TÓM TẮT HỒ SƠ BỆNH ÁN & GIẤY RA VIỆN (THÔNG TƯ 32/2023/TT-BYT)
  // ---------------------------------------------------------------------------
  if (mauId === "tom-tat-hsba-ra-vien-tt32") {
    return (
      [
        "# BẢN TÓM TẮT HỒ SƠ BỆNH ÁN & GIẤY RA VIỆN",
        "*(Theo biểu mẫu quy định tại Thông tư số 32/2023/TT-BYT của Bộ Y tế)*",
        "",
        "I. HÀNH CHÍNH",
        `- Họ và tên người bệnh: ${hc.hoTen} | Tuổi: ${hc.chuoiTuoi} | Giới tính: ${hc.gioiTinh}`,
        `- Mã số hồ sơ / Mã lưu trữ: ${hc.maHoSo} | Mã thẻ BHYT: [cần bổ sung]`,
        `- Khoa điều trị: [cần bổ sung] | Vào viện ngày: [cần bổ sung] | Ra viện ngày: ${hc.ngayLap}`,
        "",
        "II. LÝ DO VÀO VIỆN",
        ghepDanhSach(dsLyDo, "[cần bổ sung lý do vào viện]"),
        "",
        "III. QUÁ TRÌNH BỆNH LÝ VÀ DIỄN BIẾN LÂM SÀNG",
        "1. Bệnh sử & Khám lâm sàng:",
        ghepDanhSach([...dsBenhSu, ...dsKham], "[cần bổ sung quá trình bệnh lý và diễn biến lâm sàng]"),
        "2. Tiền sử bản thân & Dị ứng:",
        ghepDanhSach([...dsTienSu, ...dsDiUng], "[cần bổ sung tiền sử bản thân / dị ứng]"),
        ...(giaDinhDaDuyet.length > 0
          ? ["3. Tiền sử gia đình (tách riêng chủ thể người nhà):", ghepDanhSach(giaDinhDaDuyet)]
          : []),
        "",
        "IV. TÓM TẮT KẾT QUẢ XÉT NGHIỆM CẬN LÂM SÀNG CÓ GIÁ TRỊ CHẨN ĐOÁN",
        dsCls.length > 0
          ? ghepDanhSach(dsCls)
          : hc.chuoiXnNguCanh
          ? `- Xét nghiệm ghi nhận: ${hc.chuoiXnNguCanh}`
          : "- [cần bổ sung tóm tắt kết quả cận lâm sàng có giá trị chẩn đoán]",
        "",
        "V. PHƯƠNG PHÁP ĐIỀU TRỊ",
        ghepDanhSach([...dsThuocTatCa, ...dsKeHoach], "[cần bổ sung phương pháp điều trị nội/ngoại khoa]"),
        "",
        "VI. CHẨN ĐOÁN RA VIỆN",
        `- Bệnh chính (kèm mã ICD-10): ${chuoiChanDoanIcd}`,
        `- Bệnh kèm theo (kèm mã ICD-10): ${chuoiBenhKem}`,
        "",
        "VII. TÌNH TRẠNG NGƯỜI BỆNH RA VIỆN & HƯỚNG ĐIỀU TRỊ TIẾP THEO (GIẤY RA VIỆN)",
        `- Kết quả điều trị: [ ] Khỏi   [ ] Đỡ, giảm   [ ] Không thay đổi   [ ] Nặng hơn   [ ] Chuyển viện`,
        "- Lời dặn của bác sĩ & Lịch hẹn tái khám:",
        ghepDanhSach(dsKeHoach, "[cần bổ sung lời dặn dò và lịch tái khám sau ra viện]"),
      ].join("\n") +
      khoiCanXacNhanCuoiPhieu(choXacNhan) +
      chanTrangPhapLy("Thông tư 32/2023/TT-BYT")
    );
  }

  // ---------------------------------------------------------------------------
  // 5. BIÊN BẢN HỘI CHẨN KHOA / LIÊN KHOA (THÔNG TƯ 32/2023/TT-BYT)
  // ---------------------------------------------------------------------------
  if (mauId === "bien-ban-hoi-chan-tt32") {
    return (
      [
        "# BIÊN BẢN HỘI CHẨN KHOA / LIÊN KHOA",
        "*(Theo biểu mẫu quy định tại Thông tư số 32/2023/TT-BYT của Bộ Y tế)*",
        "",
        "I. THÔNG TIN HÀNH CHÍNH & HỘI ĐỒNG HỘI CHẨN",
        `- Cấp hội chẩn: [ ] Hội chẩn khoa   [ ] Hội chẩn liên khoa   [ ] Hội chẩn toàn viện`,
        `- Thời gian hội chẩn: [cần bổ sung giờ/phút], ngày ${hc.ngayLap} | Tại khoa/phòng: [cần bổ sung]`,
        `- Chủ tọa hội chẩn: [cần bổ sung họ tên, chức danh] | Thư ký: [cần bổ sung họ tên]`,
        `- Thành viên tham gia: [cần bổ sung danh sách bác sĩ chuyên khoa tham dự]`,
        `- Người bệnh: ${hc.hoTen} | Tuổi: ${hc.chuoiTuoi} | Giới tính: ${hc.gioiTinh} | Mã HSBA: ${hc.maHoSo}`,
        "",
        "II. TÓM TẮT QUÁ TRÌNH DIỄN BIẾN BỆNH, KHÁM & ĐIỀU TRỊ ĐÃ THỰC HIỆN",
        "1. Lý do vào viện & Diễn biến lâm sàng:",
        ghepDanhSach([...dsLyDo, ...dsBenhSu, ...dsKham], "[cần bổ sung diễn biến bệnh lý]"),
        "2. Tiền sử, bệnh nền & Dị ứng:",
        ghepDanhSach([...dsTienSu, ...dsDiUng], "[cần bổ sung tiền sử & dị ứng]"),
        "3. Cận lâm sàng đã thực hiện:",
        dsCls.length > 0
          ? ghepDanhSach(dsCls)
          : hc.chuoiXnNguCanh
          ? `- ${hc.chuoiXnNguCanh}`
          : "- [cần bổ sung kết quả xét nghiệm / CĐHA]",
        "4. Chăm sóc và thuốc đã điều trị trước hội chẩn:",
        ghepDanhSach(dsThuocTatCa, "[cần bổ sung thuốc và can thiệp đã thực hiện]"),
        "",
        "III. Ý KIẾN THẢO LUẬN & KẾT LUẬN HỘI CHẨN",
        `- Ý kiến thảo luận các chuyên khoa: [cần bổ sung tóm tắt ý kiến thảo luận hội đồng]`,
        `- Kết luận chẩn đoán sau hội chẩn: ${chuoiChanDoanIcd}`,
        "- Hướng điều trị, xét nghiệm bổ sung và theo dõi tiếp theo:",
        ghepDanhSach(dsKeHoach, "[cần bổ sung kết luận hướng xử trí của chủ tọa hội chẩn]"),
      ].join("\n") +
      khoiCanXacNhanCuoiPhieu(choXacNhan) +
      chanTrangPhapLy("Thông tư 32/2023/TT-BYT")
    );
  }

  // ---------------------------------------------------------------------------
  // 6. BỆNH ÁN NHI KHOA CHUYÊN BIỆT (TT 26/2025/TT-BYT · CÂN NẶNG & MG/KG/NGÀY)
  // ---------------------------------------------------------------------------
  if (mauId === "khuon-nhi-khoa") {
    const dongCanNang =
      hc.canNangKg !== undefined
        ? `${hc.canNangKg} kg (Đạt yêu cầu bắt buộc ghi cân nặng kê đơn Nhi khoa theo TT 26/2025/TT-BYT)`
        : "⚠️ [BẮT BUỘC BỔ SUNG CÂN NẶNG (kg) theo Thông tư 26/2025/TT-BYT trước khi kê đơn thuốc Nhi khoa]";

    const dsTiemChungDinhDuong = bnDaDuyet.filter((m) =>
      /(?:tiêm\s*chủng|vắc\s*xin|vaccine|tcmr|bú\s*mẹ|sữa\s*công\s*thức|ăn\s*dặm|sinh\s*đủ\s*tháng|sinh\s*non)/iu.test(
        m.text
      )
    );

    const dongDonThuocNhi =
      dsThuocTatCa.length > 0
        ? dsThuocTatCa
            .map((m) => {
              const mMg = m.text.match(/(\d+(?:[.,]\d+)?)\s*mg\b/iu);
              const mgVal = mMg ? Number(mMg[1].replace(",", ".")) : null;
              const goiYLieuKg =
                mgVal !== null && hc.canNangKg && hc.canNangKg > 0
                  ? ` → Tương đương ~${(mgVal / hc.canNangKg).toFixed(1)} mg/kg/lần (Bác sĩ kiểm lại tổng liều mg/kg/ngày)`
                  : ` → Liều tính theo cân nặng: [cần bổ sung mg/kg/ngày]`;
              return `- ${m.textKemNguon}${goiYLieuKg}`;
            })
            .join("\n")
        : "- [cần bổ sung y lệnh thuốc tính theo liều mg/kg/ngày]";

    return (
      [
        "# BỆNH ÁN NHI KHOA CHUYÊN BIỆT",
        "*(Chuẩn Nhi khoa Bộ Y tế & Quy định kê đơn bắt buộc cân nặng Thông tư 26/2025/TT-BYT)*",
        "",
        "I. HÀNH CHÍNH & CHỈ SỐ NHÂN TRẮC NHI KHOA",
        `- Họ và tên bệnh nhi: ${hc.hoTen} | Giới tính: ${hc.gioiTinh}`,
        `- Tháng tuổi / Tuổi: ${hc.thangTuoi !== undefined ? `${hc.thangTuoi} tháng tuổi` : hc.chuoiTuoi}`,
        `- Cân nặng hiện tại: ${dongCanNang}`,
        `- Chiều cao / Chiều dài nằm: ${hc.chieuCaoCm !== undefined ? `${hc.chieuCaoCm} cm` : "[cần bổ sung cm]"} | Vòng đầu: [cần bổ sung nếu < 24 tháng]`,
        `- Họ tên cha/mẹ hoặc người trực tiếp chăm sóc: [cần bổ sung] | SĐT liên hệ: [cần bổ sung]`,
        "",
        "II. LÝ DO ĐẾN KHÁM & BỆNH SỬ CỦA TRẺ",
        ghepDanhSach([...dsLyDo, ...dsBenhSu], "[cần bổ sung lý do khám và bệnh sử của trẻ]"),
        "",
        "III. LỜI KHAI NGƯỜI CHĂM SÓC & TIỀN SỬ GIA ĐÌNH (TÁCH RIÊNG CHỦ THỂ)",
        ghepDanhSach(giaDinhDaDuyet, "[chưa ghi nhận thông tin riêng của người chăm sóc / gia đình]"),
        "",
        "IV. TIỀN SỬ BẢN THÂN TRẺ (SẢN KHOA · DINH DƯỠNG · TIÊM CHỦNG · DỊ ỨNG)",
        `- Tiền sử tiêm chủng & Dinh dưỡng: ${dsTiemChungDinhDuong.length > 0 ? dsTiemChungDinhDuong.map((x) => x.textKemNguon).join("; ") : "[cần bổ sung lịch tiêm chủng TCMR và chế độ bú/ăn dặm]"}`,
        `- Tiền sử bệnh lý & Dị ứng của trẻ:`,
        ghepDanhSach([...dsTienSu, ...dsDiUng], "[cần bổ sung tiền sử bệnh và dị ứng của trẻ]"),
        "",
        "V. KHÁM LÂM SÀNG NHI KHOA (SÀNG LỌC DẤU HIỆU NGUY HIỂM TOÀN THÂN)",
        "- Dấu hiệu nguy hiểm toàn thân (Không uống được/bỏ bú, Nôn tất cả mọi thứ, Co giật, Li bì khó đánh thức, Rút lõm lồng ngực):",
        ghepDanhSach(dsKham, "[cần bổ sung khám thực thể, nhịp thở theo tuổi, SpO2, nhiệt độ]"),
        "",
        "VI. CẬN LÂM SÀNG & CHẨN ĐOÁN",
        "- Cận lâm sàng:",
        dsCls.length > 0
          ? ghepDanhSach(dsCls)
          : hc.chuoiXnNguCanh
          ? `- ${hc.chuoiXnNguCanh}`
          : "- [cần bổ sung cận lâm sàng nếu có]",
        `- Chẩn đoán xác định / sơ bộ: ${chuoiChanDoanIcd}`,
        "",
        "VII. ĐIỀU TRỊ & KIỂM TRA LIỀU NHI KHOA (MG/KG/NGÀY)",
        dongDonThuocNhi,
        "- Dặn dò người chăm sóc dấu hiệu cần đưa trẻ khám lại ngay:",
        ghepDanhSach(dsKeHoach, "[cần bổ sung dặn dò theo dõi sốt, nhịp thở, bú/uống và hẹn tái khám]"),
      ].join("\n") +
      khoiCanXacNhanCuoiPhieu(choXacNhan) +
      chanTrangPhapLy("Bệnh án Nhi khoa & TT 26/2025/TT-BYT")
    );
  }

  // ---------------------------------------------------------------------------
  // 7. BỆNH ÁN SẢN - PHỤ KHOA (PARA · TUỔI THAI · KINH CUỐI · TIM THAI · AN TOÀN THAI KỲ)
  // ---------------------------------------------------------------------------
  if (mauId === "khuon-san-phu-khoa") {
    const gopNguonSan = `${hc.contextText}\n${bnDaDuyet.map((m) => m.text).join("\n")}`;
    const mPara = gopNguonSan.match(/\bpara\s*[:=]?\s*(\d{4})\b/iu);
    const mTuanThai = gopNguonSan.match(/\bthai\s+(\d{1,2})\s*tuần(?:\s*(\d)\s*ngày)?/iu);
    const mKinhCuoi = gopNguonSan.match(/(?:kinh\s*cuối|kcc|lmp)\s*[:=]?\s*([^\n.;,]+)/iu);
    const dsThaiMay = bnDaDuyet.filter((m) => /(?:thai\s*máy|cử\s*động\s*thai|gò\s*tử\s*cung|ra\s*huyết|ra\s*nước)/iu.test(m.text));
    const dsTimThai = bnDaDuyet.filter((m) => /(?:tim\s*thai|bề\s*cao\s*tử\s*cung|cổ\s*tử\s*cung|ngôi\s*thai|monitoring)/iu.test(m.text));

    return (
      [
        "# BỆNH ÁN SẢN - PHỤ KHOA",
        "*(Chuẩn chuyên khoa Phụ Sản Bộ Y tế — Kiểm soát thai kỳ & an toàn dùng thuốc)*",
        "",
        "I. HÀNH CHÍNH & TIỀN SỬ SẢN - PHỤ KHOA (PARA)",
        `- Họ và tên người bệnh / sản phụ: ${hc.hoTen} | Tuổi: ${hc.chuoiTuoi} | Mã hồ sơ: ${hc.maHoSo}`,
        `- Chỉ số PARA: ${mPara ? mPara[1] : "[cần bổ sung PARA (Sinh đủ tháng - Sinh non - Sẩy/Nạo - Con hiện sống)]"}`,
        `- Kinh cuối cùng (KCC): ${mKinhCuoi ? mKinhCuoi[1].trim() : "[cần bổ sung ngày đầu kỳ kinh cuối]"} | Dự kiến sinh (DKS): [cần bổ sung]`,
        `- Tuổi thai hiện tại: ${mTuanThai ? `${mTuanThai[1]} tuần${mTuanThai[2] ? ` ${mTuanThai[2]} ngày` : ""}` : hc.coThai ? "[Đang mang thai — cần bổ sung số tuần thai]" : "[cần bổ sung tuổi thai nếu mang thai]"}`,
        "",
        "II. LÝ DO KHÁM & TRIỆU CHỨNG CƠ NĂNG (THAI MÁY · CƠN GÒ · RA DỊCH/HUYẾT)",
        ghepDanhSach([...dsLyDo, ...dsBenhSu], "[cần bổ sung lý do khám và diễn biến]"),
        `- Ghi nhận Thai máy / Cơn gò / Ra huyết âm đạo: ${dsThaiMay.length > 0 ? dsThaiMay.map((m) => m.textKemNguon).join("; ") : "[cần bổ sung tình trạng thai máy, cơn gò tử cung, dịch âm đạo]"}`,
        "",
        "III. TIỀN SỬ BỆNH NỘI NGOẠI KHOA & DỊ ỨNG THUỐC",
        ghepDanhSach([...dsTienSu, ...dsDiUng], "[cần bổ sung tiền sử tiền sản giật, ĐTĐ thai kỳ, mổ lấy thai cũ, dị ứng]"),
        ...(giaDinhDaDuyet.length > 0
          ? ["IV. TIỀN SỬ GIA ĐÌNH (TÁCH RIÊNG):", ghepDanhSach(giaDinhDaDuyet)]
          : []),
        "",
        "V. KHÁM TOÀN THÂN & KHÁM CHUYÊN KHOA SẢN - PHỤ",
        "- Toàn thân & Sinh hiệu (lưu ý tầm soát Huyết áp / Phù / Protein niệu):",
        ghepDanhSach(dsKham, "[cần bổ sung Huyết áp, Mạch, Cân nặng, Phù]"),
        `- Khám Sản / Tim thai / Bề cao tử cung / Cổ tử cung: ${dsTimThai.length > 0 ? dsTimThai.map((m) => m.textKemNguon).join("; ") : "[cần bổ sung tần số tim thai (lần/phút), BCTC, vòng bụng, ngôi thai / khám mỏ vịt]"}`,
        "",
        "VI. CẬN LÂM SÀNG (SIÊU ÂM · MONITORING · XÉT NGHIỆM)",
        dsCls.length > 0
          ? ghepDanhSach(dsCls)
          : hc.chuoiXnNguCanh
          ? `- ${hc.chuoiXnNguCanh}`
          : "- [cần bổ sung kết quả siêu âm thai / phụ khoa, CTG, tổng phân tích nước tiểu]",
        "",
        "VII. CHẨN ĐOÁN & KẾ HOẠCH ĐIỀU TRỊ (RÀ SOÁT THUỐC AN TOÀN THAI KỲ)",
        `- Chẩn đoán: ${chuoiChanDoanIcd}`,
        "- Thuốc & Hướng xử trí (⚠️ Bác sĩ kiểm tra chống chỉ định thai kỳ & cho con bú trước khi ký đơn):",
        ghepDanhSach([...dsThuocTatCa, ...dsKeHoach], "[cần bổ sung phác đồ xử trí & hẹn khám thai định kỳ]"),
      ].join("\n") +
      khoiCanXacNhanCuoiPhieu(choXacNhan) +
      chanTrangPhapLy("Bệnh án Sản - Phụ khoa BYT")
    );
  }

  // ---------------------------------------------------------------------------
  // 8. BỆNH ÁN CẤP CỨU - CHẤN THƯƠNG (ABCDE + AMPLE + GLASGOW)
  // ---------------------------------------------------------------------------
  if (mauId === "khuon-cap-cuu-chan-thuong") {
    const gopCapCuu = `${hc.contextText}\n${bnDaDuyet.map((m) => m.text).join("\n")}`;
    const mGcs = gopCapCuu.match(/(?:gcs|glasgow)\s*[:=]?\s*(\d{1,2})\s*(?:\/\s*15|\s*điểm)?/iu);
    const dsHoHap = dsKham.filter((m) => /(?:thở|spo2|phổi|khó\s*thở|rì\s*rào|đường\s*thở)/iu.test(m.text));
    const dsTuanHoan = dsKham.filter((m) => /(?:mạch|huyết\s*áp|nhịp\s*tim|da\s*niêm|chảy\s*máu|chi\s*lạnh)/iu.test(m.text));
    const dsThanKinh = dsKham.filter((m) => /(?:tỉnh|glasgow|gcs|đồng\s*tử|liệt|tri\s*giác|đau\s*đầu|chóng\s*mặt)/iu.test(m.text));
    const dsBuaAnCuoi = bnDaDuyet.filter((m) => /(?:ăn\s*lúc|bữa\s*ăn\s*cuối|nhịn\s*ăn|mới\s*ăn)/iu.test(m.text));

    return (
      [
        "# BỆNH ÁN CẤP CỨU - CHẤN THƯƠNG (ABCDE + AMPLE + GLASGOW)",
        "*(Chuẩn tiếp nhận Cấp cứu ban đầu — Đánh giá sơ cấp ABCDE & Bệnh sử nhanh AMPLE)*",
        "",
        "I. HÀNH CHÍNH & PHÂN LOẠI CẤP CỨU",
        `- Họ và tên người bệnh: ${hc.hoTen} | Tuổi: ${hc.chuoiTuoi} | Giới tính: ${hc.gioiTinh} | Mã ca: ${hc.maHoSo}`,
        `- Giờ tiếp nhận cấp cứu: ${session?.time || "[cần bổ sung giờ:phút]"} ngày ${hc.ngayLap}`,
        `- Phân loại ưu tiên cấp cứu (Triage): [ ] Cấp I (Tối khẩn)  [ ] Cấp II (Khẩn)  [ ] Cấp III  [ ] Cấp IV`,
        "",
        "II. KHẢO SÁT BAN ĐẦU THEO CHUẨN ABCDE & THANG ĐIỂM GLASGOW (GCS)",
        `- A (Airway — Đường thở & Cột sống cổ): [cần bổ sung tình trạng thông thoáng đường thở & cố định cột sống cổ]`,
        `- B (Breathing — Hô hấp & SpO2): ${dsHoHap.length > 0 ? dsHoHap.map((m) => m.textKemNguon).join("; ") : "[cần bổ sung tần số thở, SpO2, âm phế bào 2 bên]"}`,
        `- C (Circulation — Tuần hoàn & Cầm máu): ${dsTuanHoan.length > 0 ? dsTuanHoan.map((m) => m.textKemNguon).join("; ") : "[cần bổ sung Mạch, Huyết áp, CRT, kiểm soát chảy máu ngoài]"}`,
        `- D (Disability — Thần kinh & Glasgow): GCS = ${mGcs ? `${mGcs[1]}/15 điểm` : "[cần bổ sung E_ V_ M_ = __/15]"}; ${dsThanKinh.length > 0 ? dsThanKinh.map((m) => m.textKemNguon).join("; ") : "Đồng tử 2 bên & dấu thần kinh khu trú: [cần bổ sung]"}`,
        `- E (Exposure — Bộc lộ toàn thân & Thân nhiệt): ${dsKham.length > 0 ? dsKham.map((m) => m.textKemNguon).join("; ") : "[cần bổ sung thân nhiệt và thương tổn phối hợp khi bộc lộ toàn thân]"}`,
        "",
        "III. KHAI THÁC BỆNH SỬ NHANH THEO AMPLE",
        `- A (Allergies — Dị ứng): ${dsDiUng.length > 0 ? dsDiUng.map((m) => m.textKemNguon).join("; ") : "[cần bổ sung tiền sử dị ứng thuốc/thức ăn]"}`,
        `- M (Medications — Thuốc đang dùng, đặc biệt kháng đông/hạ áp/insulin): ${dsThuocDangDung.length > 0 ? dsThuocDangDung.map((m) => m.textKemNguon).join("; ") : "[cần bổ sung thuốc đang dùng]"}`,
        `- P (Past history — Tiền sử bệnh / Phẫu thuật / Thai kỳ): ${dsTienSu.length > 0 ? dsTienSu.map((m) => m.textKemNguon).join("; ") : "[cần bổ sung bệnh nền]"}`,
        `- L (Last meal — Bữa ăn/uống cuối cùng): ${dsBuaAnCuoi.length > 0 ? dsBuaAnCuoi.map((m) => m.textKemNguon).join("; ") : "[cần bổ sung thời điểm ăn/uống cuối phục vụ gây mê nếu cần]"}`,
        `- E (Events / Mechanism — Cơ chế chấn thương / Hoàn cảnh khởi phát):`,
        ghepDanhSach([...dsLyDo, ...dsBenhSu], "[cần bổ sung cơ chế chấn thương / hoàn cảnh khởi phát cấp cứu]"),
        ...(giaDinhDaDuyet.length > 0
          ? ["- Thông tin nhân chứng / người nhà đưa vào viện:", ghepDanhSach(giaDinhDaDuyet)]
          : []),
        "",
        "IV. CẬN LÂM SÀNG CẤP CỨU (eFAST · X-QUANG · CT · XÉT NGHIỆM KHẨN)",
        dsCls.length > 0
          ? ghepDanhSach(dsCls)
          : hc.chuoiXnNguCanh
          ? `- Chỉ số xét nghiệm khẩn: ${hc.chuoiXnNguCanh}`
          : "- [cần bổ sung eFAST, Điện tim, Khí máu, Troponin, Công thức máu, Đông máu]",
        "",
        "V. CHẨN ĐOÁN CẤP CỨU & XỬ TRÍ BAN ĐẦU",
        `- Chẩn đoán cấp cứu: ${chuoiChanDoanIcd}`,
        "- Y lệnh xử trí cấp cứu & Hướng chuyển khoa/mổ/lưu theo dõi:",
        ghepDanhSach([...dsThuocTatCa, ...dsKeHoach], "[cần bổ sung y lệnh xử trí cấp cứu có giờ thực hiện]"),
      ].join("\n") +
      khoiCanXacNhanCuoiPhieu(choXacNhan) +
      chanTrangPhapLy("Bệnh án Cấp cứu ABCDE + AMPLE")
    );
  }

  return null;
}
