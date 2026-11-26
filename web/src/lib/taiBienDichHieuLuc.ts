/**
 * Bộ Tái Biên dịch Gói Liên thông HL7 FHIR R4 & BHYT XML 1–5 Hậu Duyệt (Boost 4C).
 *
 * Bảo đảm tuyệt đối tính nhất quán giữa quyết định duyệt của bác sĩ (Giữ / Sửa / Bỏ) và gói dữ liệu
 * xuất liên thông HIS/EMR/Cổng Giám định BHYT (QĐ 130/QĐ-BYT & 4750/QĐ-BYT):
 * - Loại bỏ 100% mệnh đề bác sĩ bấm "Bỏ" (`quyet === "bo"`) khỏi `propositions`, `effective_fhir_bundle`
 *   và toàn bộ chuỗi `XML1..XML5`.
 * - Cập nhật tức thời nội dung bác sĩ "Sửa" (`quyet === "sua"`) vào các Resource lâm sàng tương ứng
 *   (`Condition`, `MedicationRequest`, `MedicationStatement`, `AllergyIntolerance`, `Composition`, `Provenance`)
 *   cùng nhãn `reviewDecision`.
 */
import type { NoteMeta, Proposition, Quyet } from "../components/VerificationView";
import { sha256HexSync } from "./compileEffectiveNote";
import { laChuTheBenhNhan } from "./bieuMauPhapLyOffline";

export interface MenhDeHieuLucXuat extends Proposition {
  reviewDecision: Quyet;
  originalText?: string;
}

export interface BangXml15HieuLuc {
  XML1: string;
  XML2: string;
  XML3: string;
  XML4: string;
  XML5: string;
  bang_du_lieu: {
    XML1_TONG_HOP: Record<string, unknown>;
    XML2_THUOC: Array<Record<string, unknown>>;
    XML3_DVKT_VTYT: Array<Record<string, unknown>>;
    XML4_CLS: Array<Record<string, unknown>>;
    XML5_DIEN_BIEN_LS: Array<Record<string, unknown>>;
  };
}

export interface KetQuaTaiBienDichHieuLuc {
  caseId: string;
  patientIdentifier: string;
  exportedAt: string;
  reviewSummary: {
    totalOriginal: number;
    activeCount: number;
    keptCount: number;
    editedCount: number;
    rejectedCount: number;
    pendingCount: number;
  };
  propositions: MenhDeHieuLucXuat[];
  effective_fhir_bundle: Record<string, any>;
  effective_xml_1_5: BangXml15HieuLuc;
  hl7_fhir_r4_bundle: Record<string, any>;
  bhyt_qd130_4750: Record<string, any>;
  stage_45_omission_recovery: unknown[];
  audit_trail_worm: unknown;
}

const DANH_MUC_ICD10_RUT_GON: Array<[string, string, string[]]> = [
  ["I10", "Tăng huyết áp vô căn (nguyên phát)", ["tăng huyết áp", "cao huyết áp", "huyết áp cao"]],
  ["E11.2", "Đái tháo đường típ 2 có biến chứng thận", ["đái tháo đường biến chứng thận", "tiểu đường suy thận"]],
  ["E11.9", "Đái tháo đường típ 2", ["đái tháo đường", "tiểu đường", "đường huyết cao"]],
  ["N18.3", "Bệnh thận mạn giai đoạn 3", ["bệnh thận mạn giai đoạn 3", "suy thận giai đoạn 3", "suy thận độ 2"]],
  ["N18.9", "Bệnh thận mạn", ["suy thận", "bệnh thận mạn", "ckd"]],
  ["E78.5", "Rối loạn chuyển hóa lipoprotein", ["rối loạn mỡ máu", "mỡ máu cao", "tăng cholesterol"]],
  ["I20.9", "Cơn đau thắt ngực / Bệnh tim thiếu máu cục bộ", ["đau thắt ngực", "thiếu máu cơ tim", "mạch vành"]],
  ["I50.9", "Suy tim", ["suy tim", "phù hai chân do tim"]],
  ["J02.9", "Viêm họng cấp", ["viêm họng", "đau rát họng", "viêm amidan"]],
  ["J01.9", "Viêm xoang cấp", ["viêm xoang"]],
  ["J20.9", "Viêm phế quản cấp", ["viêm phế quản", "ran rít", "ran ngáy"]],
  ["J18.9", "Viêm phổi", ["viêm phổi", "đông đặc phổi", "ran ẩm", "ran nổ"]],
  ["J45.9", "Hen phế quản", ["hen phế quản", "hen suyễn", "cơn hen"]],
  ["J44.9", "Bệnh phổi tắc nghẽn mạn tính (COPD)", ["copd", "phổi tắc nghẽn mạn tính"]],
  ["K29.7", "Viêm dạ dày - tá tràng", ["viêm dạ dày", "viêm loét dạ dày", "đau thượng vị"]],
  ["K21.9", "Bệnh trào ngược dạ dày - thực quản (GERD)", ["trào ngược dạ dày", "gerd", "ợ chua"]],
  ["A09", "Tiêu chảy và viêm dạ dày-ruột nhiễm khuẩn", ["tiêu chảy cấp", "viêm ruột", "đi ngoài phân lỏng"]],
  ["N39.0", "Nhiễm khuẩn đường tiết niệu", ["nhiễm khuẩn tiết niệu", "viêm đường tiết niệu", "tiểu buốt"]],
  ["M54.5", "Đau thắt lưng / Thoái hóa cột sống", ["đau thắt lưng", "thoái hóa cột sống"]],
  ["M10.9", "Bệnh Gút (Gout)", ["bệnh gút", "gout", "tăng acid uric"]],
];

function xmlEscape(val: unknown): string {
  return String(val ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

function toBase64Utf8(str: string): string {
  const bytes = new TextEncoder().encode(str);
  if (typeof Buffer !== "undefined") {
    return Buffer.from(bytes).toString("base64");
  }
  let bin = "";
  for (let i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
  return btoa(bin);
}

function laDiUngPhuDinh(text: string, negated?: boolean): boolean {
  if (negated) return true;
  const t = text.trim();
  if (!t) return true;
  if (/^(?:không|chưa|ko)\s+rõ/iu.test(t)) return false;
  return /^(?:[-*•]\s*)?(?:bệnh\s+nhân\s+|người\s+bệnh\s+)?(?:không|ko|chưa(?:\s+từng|\s+ghi\s+nhận)?)\s+(?:có\s+|bị\s+)?(?:tiền\s+sử\s+)?(?:dị\s+ứng|mẫn\s+cảm)/iu.test(
    t
  );
}

function suyMaIcdTuMenhDeHieuLuc(
  bnProps: MenhDeHieuLucXuat[],
  icdCu?: { ma_icd10_chinh?: { ma_icd10: string; ten_benh_byt: string } | null; ma_icd10_kem_theo?: Array<{ ma_icd10: string; ten_benh_byt: string }> } | null,
  coChanDoanBiBo = false
): {
  chinh: { ma_icd10: string; ten_benh_byt: string } | null;
  kemTheo: Array<{ ma_icd10: string; ten_benh_byt: string }>;
} {
  const uuTien = bnProps.filter(
    (p) =>
      !p.negated &&
      ((p.section || "").toUpperCase().includes("CHẨN ĐOÁN") ||
        (p.section || "").toUpperCase().includes("ĐÁNH GIÁ") ||
        (p.section || "").toUpperCase().includes("BỆNH SỬ") ||
        (p.section || "").toUpperCase().includes("TIỀN SỬ"))
  );

  const timThay: Array<{ ma_icd10: string; ten_benh_byt: string }> = [];
  const daCo = new Set<string>();

  // 1. Quét mã ICD-10 tường minh bác sĩ tự gõ khi Sửa (VD: "Viêm phổi thùy (J18.1)")
  for (const p of uuTien) {
    const mMa = p.text.match(/\b([A-Z]\d{2}(?:\.\d{1,2})?)\b/);
    if (mMa && !daCo.has(mMa[1])) {
      daCo.add(mMa[1]);
      timThay.push({ ma_icd10: mMa[1], ten_benh_byt: p.text });
    }
  }

  // 2. Quét từ điển ICD-10 Bộ Y tế trên các mệnh đề còn hiệu lực
  for (const p of uuTien) {
    const low = p.text.toLowerCase();
    for (const [ma, ten, kws] of DANH_MUC_ICD10_RUT_GON) {
      if (daCo.has(ma)) continue;
      if (kws.some((kw) => low.includes(kw))) {
        daCo.add(ma);
        timThay.push({ ma_icd10: ma, ten_benh_byt: ten });
      }
    }
  }

  if (timThay.length > 0) {
    return { chinh: timThay[0], kemTheo: timThay.slice(1) };
  }
  if (!coChanDoanBiBo && icdCu?.ma_icd10_chinh) {
    return {
      chinh: icdCu.ma_icd10_chinh,
      kemTheo: icdCu.ma_icd10_kem_theo || [],
    };
  }
  return { chinh: null, kemTheo: [] };
}

function taoCitationExtension(props: MenhDeHieuLucXuat[]) {
  const turns = Array.from(new Set(props.flatMap((p) => p.evidenceTurns || []))).sort((a, b) => a - b);
  const decisions = Array.from(new Set(props.map((p) => p.reviewDecision)));
  const decisionSummary: Quyet = decisions.includes("sua")
    ? "sua"
    : decisions.includes("giu")
    ? "giu"
    : "cho";

  return {
    decisionSummary,
    extensions: [
      {
        url: "https://meditrace.vn/fhir/StructureDefinition/bidirectional-citation",
        extension: [
          { url: "propositionIds", valueString: props.map((p) => p.id).join(",") },
          { url: "evidenceTurns", valueString: turns.map((t) => `T${t}`).join(",") },
          { url: "reviewDecision", valueCode: decisionSummary },
        ],
      },
    ],
  };
}

export function xuatGoiFhirVaBhytHieuLuc(params: {
  noteMeta?: NoteMeta | null;
  quyetDuyet?: Record<number, Quyet>;
  banSuaDuyet?: Record<number, string>;
  caseId?: string;
  patientIdentifier?: string;
}): KetQuaTaiBienDichHieuLuc {
  const noteMeta = params.noteMeta || null;
  const quyet = params.quyetDuyet || {};
  const banSua = params.banSuaDuyet || {};
  const rawProps = Array.isArray(noteMeta?.propositions) ? noteMeta!.propositions : [];

  const caseId = params.caseId || noteMeta?.caseId || "ca-kham";
  const patientName = (params.patientIdentifier || "").trim() || "Bệnh nhân ẩn danh";
  const nowIso = new Date().toISOString();

  let keptCount = 0;
  let editedCount = 0;
  let rejectedCount = 0;
  let pendingCount = 0;
  let coChanDoanBiBo = false;
  const tapTextBiBo: string[] = [];

  const activeProps: MenhDeHieuLucXuat[] = [];

  for (const p of rawProps) {
    const q: Quyet = quyet[p.id] || "cho";
    if (q === "bo") {
      rejectedCount += 1;
      if (p.text?.trim()) tapTextBiBo.push(p.text.trim().toLowerCase());
      if (/CHẨN\s*ĐOÁN|ĐÁNH\s*GIÁ/iu.test(p.section || "")) coChanDoanBiBo = true;
      continue;
    }

    const daSua = q === "sua" && Boolean(banSua[p.id]?.trim());
    if (daSua) editedCount += 1;
    else if (q === "giu") keptCount += 1;
    else pendingCount += 1;

    const effectiveText = daSua ? banSua[p.id].trim() : (p.text || "").trim();
    if (!effectiveText) continue;

    activeProps.push({
      ...p,
      text: effectiveText,
      reviewDecision: daSua ? "sua" : q,
      ...(daSua ? { originalText: p.text } : {}),
    });
  }

  const bnProps = activeProps.filter((p) => laChuTheBenhNhan(p));
  const gdProps = activeProps.filter((p) => !laChuTheBenhNhan(p));

  const dsChanDoan = bnProps.filter((p) => /CHẨN\s*ĐOÁN|ĐÁNH\s*GIÁ|TÓM\s*TẮT/iu.test(p.section || ""));
  const dsTienSu = bnProps.filter((p) => /TIỀN\s*SỬ/iu.test(p.section || ""));
  const dsDiUng = bnProps.filter(
    (p) => (/DỊ\s*ỨNG/iu.test(p.section || "") || /\bdị\s*ứng\b/iu.test(p.text)) && !laDiUngPhuDinh(p.text, p.negated)
  );
  const dsThuocKeDon = bnProps.filter(
    (p) =>
      !p.negated &&
      (/ĐƠN\s*THUỐC|KẾ\s*HOẠCH|ĐIỀU\s*TRỊ|XỬ\s*TRÍ/iu.test(p.section || "")) &&
      (Boolean(p.drug) || /\b(?:\d+\s*(?:mg|mcg|g|ml|viên|ống|gói)|uống|tiêm|truyền|xịt|nhỏ)\b/iu.test(p.text))
  );
  const dsThuocDangDung = bnProps.filter(
    (p) => !p.negated && /THUỐC\s*ĐANG\s*DÙNG/iu.test(p.section || "")
  );
  const dsBenhSu = bnProps.filter((p) => /LÝ\s*DO|BỆNH\s*SỬ/iu.test(p.section || ""));
  const dsKham = bnProps.filter((p) => /KHÁM|SINH\s*HIỆU|THỰC\s*THỂ/iu.test(p.section || ""));
  const dsCls = bnProps.filter((p) =>
    /CẬN\s*LÂM\s*SÀNG|XÉT\s*NGHIỆM/iu.test(p.section || "") ||
    /(?:xét\s*nghiệm|x-quang|siêu\s*âm|ct|mri|điện\s*tim|ecg|creatinin|egfr|hba1c|troponin|wbc|crp)/iu.test(p.text)
  );
  const dsDvkt = bnProps.filter(
    (p) =>
      !p.negated &&
      (/KẾ\s*HOẠCH|XỬ\s*TRÍ|THỦ\s*THUẬT/iu.test(p.section || "")) &&
      /(?:chụp|siêu\s*âm|nội\s*soi|điện\s*tim|thủ\s*thuật|thở\s*oxy|khí\s*dung|truyền\s*dịch|hội\s*chẩn)/iu.test(p.text)
  );

  const icdHieuLuc = suyMaIcdTuMenhDeHieuLuc(
    bnProps,
    noteMeta?.clinicalSafety?.bhyt_icd10,
    coChanDoanBiBo
  );

  // ===========================================================================
  // 1. TÁI BIÊN DỊCH GÓI HL7 FHIR R4 BUNDLE HẬU DUYỆT
  // ===========================================================================
  const baseBundle = noteMeta?.clinicalSafety?.fhir_bundle;
  const patientId =
    baseBundle?.entry?.find((e: any) => e?.resource?.resourceType === "Patient")?.resource?.id ||
    `patient-${caseId}`;
  const encounterId =
    baseBundle?.entry?.find((e: any) => e?.resource?.resourceType === "Encounter")?.resource?.id ||
    `encounter-${caseId}`;

  const patientEntry =
    baseBundle?.entry?.find((e: any) => e?.resource?.resourceType === "Patient") || {
      fullUrl: `urn:uuid:${patientId}`,
      resource: {
        resourceType: "Patient",
        id: patientId,
        name: [{ use: "official", text: patientName }],
      },
    };

  const encounterEntry =
    baseBundle?.entry?.find((e: any) => e?.resource?.resourceType === "Encounter") || {
      fullUrl: `urn:uuid:${encounterId}`,
      resource: {
        resourceType: "Encounter",
        id: encounterId,
        status: "finished",
        class: {
          system: "http://terminology.hl7.org/CodeSystem/v3-ActCode",
          code: "AMB",
          display: "ambulatory",
        },
        subject: { reference: `urn:uuid:${patientId}` },
        period: { start: nowIso },
      },
    };

  // Giữ lại các Observation cận lâm sàng LOINC từ bundle gốc (trừ khi trùng nội dung mệnh đề đã bị Bỏ)
  const keptLabObservationEntries = (baseBundle?.entry || []).filter((e: any) => {
    const r = e?.resource;
    if (r?.resourceType !== "Observation") return false;
    const isLab = r?.category?.[0]?.coding?.[0]?.code === "laboratory";
    if (!isLab) return false;
    const strVal = String(r?.valueString || r?.code?.text || "").toLowerCase();
    return !tapTextBiBo.some((bo) => bo.length > 4 && strVal.includes(bo));
  });

  const dynamicEntries: Array<Record<string, any>> = [];

  // Condition: Chẩn đoán
  dsChanDoan.forEach((p, idx) => {
    const cid = `condition-dx-${p.id}-${idx + 1}`;
    const cite = taoCitationExtension([p]);
    dynamicEntries.push({
      fullUrl: `urn:uuid:${cid}`,
      resource: {
        resourceType: "Condition",
        id: cid,
        reviewDecision: p.reviewDecision,
        clinicalStatus: {
          coding: [{ system: "http://terminology.hl7.org/CodeSystem/condition-clinical", code: "active" }],
        },
        category: [
          {
            coding: [
              {
                system: "http://terminology.hl7.org/CodeSystem/condition-category",
                code: "encounter-diagnosis",
                display: "Encounter Diagnosis",
              },
            ],
          },
        ],
        code: {
          ...(idx === 0 && icdHieuLuc.chinh
            ? {
                coding: [
                  {
                    system: "http://hl7.org/fhir/sid/icd-10",
                    code: icdHieuLuc.chinh.ma_icd10,
                    display: icdHieuLuc.chinh.ten_benh_byt,
                  },
                ],
              }
            : {}),
          text: p.text,
        },
        subject: { reference: `urn:uuid:${patientId}` },
        encounter: { reference: `urn:uuid:${encounterId}` },
        extension: cite.extensions,
      },
    });
  });

  // Condition: Tiền sử bệnh bản thân
  dsTienSu.forEach((p, idx) => {
    const tid = `condition-history-${p.id}-${idx + 1}`;
    const cite = taoCitationExtension([p]);
    dynamicEntries.push({
      fullUrl: `urn:uuid:${tid}`,
      resource: {
        resourceType: "Condition",
        id: tid,
        reviewDecision: p.reviewDecision,
        category: [
          {
            coding: [
              {
                system: "http://terminology.hl7.org/CodeSystem/condition-category",
                code: "problem-list-item",
                display: "Problem List Item",
              },
            ],
          },
        ],
        code: { text: p.text },
        subject: { reference: `urn:uuid:${patientId}` },
        encounter: { reference: `urn:uuid:${encounterId}` },
        extension: cite.extensions,
      },
    });
  });

  // FamilyMemberHistory: Tiền sử gia đình tách riêng
  gdProps.forEach((p, idx) => {
    const fid = `family-history-${p.id}-${idx + 1}`;
    const cite = taoCitationExtension([p]);
    dynamicEntries.push({
      fullUrl: `urn:uuid:${fid}`,
      resource: {
        resourceType: "FamilyMemberHistory",
        id: fid,
        status: "completed",
        reviewDecision: p.reviewDecision,
        patient: { reference: `urn:uuid:${patientId}` },
        relationship: { text: p.subject || "Người nhà" },
        note: [{ text: p.text }],
        extension: cite.extensions,
      },
    });
  });

  // AllergyIntolerance: Dị ứng
  dsDiUng.forEach((p, idx) => {
    const aid = `allergy-${p.id}-${idx + 1}`;
    const cite = taoCitationExtension([p]);
    dynamicEntries.push({
      fullUrl: `urn:uuid:${aid}`,
      resource: {
        resourceType: "AllergyIntolerance",
        id: aid,
        reviewDecision: p.reviewDecision,
        clinicalStatus: {
          coding: [{ system: "http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical", code: "active" }],
        },
        verificationStatus: {
          coding: [
            {
              system: "http://terminology.hl7.org/CodeSystem/allergyintolerance-verification",
              code: p.reviewDecision === "giu" || p.reviewDecision === "sua" ? "confirmed" : "unconfirmed",
            },
          ],
        },
        type: "allergy",
        criticality: "high",
        code: { text: p.text },
        patient: { reference: `urn:uuid:${patientId}` },
        recordedDate: nowIso,
        extension: cite.extensions,
      },
    });
  });

  // MedicationRequest: Đơn thuốc bác sĩ chỉ định
  dsThuocKeDon.forEach((p, idx) => {
    const mid = `medication-request-${p.id}-${idx + 1}`;
    const cite = taoCitationExtension([p]);
    dynamicEntries.push({
      fullUrl: `urn:uuid:${mid}`,
      resource: {
        resourceType: "MedicationRequest",
        id: mid,
        status: "active",
        intent: "order",
        reviewDecision: p.reviewDecision,
        subject: { reference: `urn:uuid:${patientId}` },
        encounter: { reference: `urn:uuid:${encounterId}` },
        authoredOn: nowIso,
        medicationCodeableConcept: {
          text: p.text,
          coding: [{ system: "https://dav.gov.vn/drug-codes", display: p.drug || p.text }],
        },
        dosageInstruction: [{ text: p.text }],
        extension: cite.extensions,
      },
    });
  });

  // MedicationStatement: Thuốc đang dùng trước khám
  dsThuocDangDung.forEach((p, idx) => {
    const msid = `medication-statement-${p.id}-${idx + 1}`;
    const cite = taoCitationExtension([p]);
    dynamicEntries.push({
      fullUrl: `urn:uuid:${msid}`,
      resource: {
        resourceType: "MedicationStatement",
        id: msid,
        status: "active",
        reviewDecision: p.reviewDecision,
        medicationCodeableConcept: { text: p.text },
        subject: { reference: `urn:uuid:${patientId}` },
        effectiveDateTime: nowIso,
        extension: cite.extensions,
      },
    });
  });

  // Observation: Khám lâm sàng & Sinh hiệu
  if (dsKham.length > 0) {
    const vid = `observation-vitals-${caseId}`;
    const cite = taoCitationExtension(dsKham);
    dynamicEntries.push({
      fullUrl: `urn:uuid:${vid}`,
      resource: {
        resourceType: "Observation",
        id: vid,
        status: "final",
        reviewDecision: cite.decisionSummary,
        category: [
          {
            coding: [
              {
                system: "http://terminology.hl7.org/CodeSystem/observation-category",
                code: "exam",
                display: "Exam",
              },
            ],
          },
        ],
        code: { text: "Khám lâm sàng & Sinh hiệu hậu duyệt" },
        subject: { reference: `urn:uuid:${patientId}` },
        encounter: { reference: `urn:uuid:${encounterId}` },
        valueString: dsKham.map((p) => p.text).join("; "),
        effectiveDateTime: nowIso,
        extension: cite.extensions,
      },
    });
  }

  // DocumentReference & Provenance & Composition hậu duyệt
  const banNhapHieuLucObj = {
    BENH_SU: dsBenhSu.map((p) => p.text),
    TIEN_SU: dsTienSu.map((p) => p.text),
    DI_UNG: dsDiUng.map((p) => p.text),
    THUOC_DANG_DUNG: dsThuocDangDung.map((p) => p.text),
    KHAM_LAM_SANG: dsKham.map((p) => p.text),
    CAN_LAM_SANG: dsCls.map((p) => p.text),
    CHAN_DOAN: dsChanDoan.map((p) => p.text),
    KE_HOACH_DIEU_TRI: dsThuocKeDon.map((p) => p.text),
  };
  const jsonBanNhapHieuLuc = JSON.stringify(banNhapHieuLucObj, null, 2);
  const digestSha256 = sha256HexSync(jsonBanNhapHieuLuc);

  const docRefId = `docref-${caseId}`;
  const docRefEntry = {
    fullUrl: `urn:uuid:${docRefId}`,
    resource: {
      resourceType: "DocumentReference",
      id: docRefId,
      status: "current",
      docStatus: pendingCount === 0 && activeProps.length > 0 ? "final" : "preliminary",
      subject: { reference: `urn:uuid:${patientId}` },
      date: nowIso,
      content: [
        {
          attachment: {
            contentType: "application/json; charset=utf-8",
            title: `Hồ sơ hậu duyệt ca ${caseId}`,
            data: toBase64Utf8(jsonBanNhapHieuLuc),
          },
        },
      ],
    },
  };

  const compositionId = `composition-${caseId}`;
  const compositionEntry = {
    fullUrl: `urn:uuid:${compositionId}`,
    resource: {
      resourceType: "Composition",
      id: compositionId,
      status: pendingCount === 0 && activeProps.length > 0 ? "final" : "preliminary",
      type: {
        coding: [{ system: "http://loinc.org", code: "11488-4", display: "Consultation note" }],
        text: "Hồ sơ bệnh án ngoại trú hậu duyệt MediTrace Sentinel",
      },
      subject: { reference: `urn:uuid:${patientId}` },
      encounter: { reference: `urn:uuid:${encounterId}` },
      date: nowIso,
      title: `Bệnh án điện tử hậu duyệt — ${patientName}`,
      section: [
        {
          title: "Bệnh sử & Lý do khám",
          text: {
            status: "generated",
            div: `<div xmlns="http://www.w3.org/1999/xhtml">${xmlEscape(dsBenhSu.map((p) => p.text).join("; "))}</div>`,
          },
        },
        {
          title: "Tiền sử & Dị ứng",
          text: {
            status: "generated",
            div: `<div xmlns="http://www.w3.org/1999/xhtml">${xmlEscape([...dsTienSu, ...dsDiUng].map((p) => p.text).join("; "))}</div>`,
          },
        },
        {
          title: "Khám lâm sàng & Cận lâm sàng",
          text: {
            status: "generated",
            div: `<div xmlns="http://www.w3.org/1999/xhtml">${xmlEscape([...dsKham, ...dsCls].map((p) => p.text).join("; "))}</div>`,
          },
        },
        {
          title: "Chẩn đoán & Kế hoạch điều trị",
          text: {
            status: "generated",
            div: `<div xmlns="http://www.w3.org/1999/xhtml">${xmlEscape([...dsChanDoan, ...dsThuocKeDon].map((p) => p.text).join("; "))}</div>`,
          },
        },
      ],
    },
  };

  const allTargets = [
    compositionEntry,
    patientEntry,
    encounterEntry,
    ...dynamicEntries,
    ...keptLabObservationEntries,
    docRefEntry,
  ].map((e) => ({ reference: e.fullUrl }));

  const provenanceEntry = {
    fullUrl: `urn:uuid:provenance-${caseId}`,
    resource: {
      resourceType: "Provenance",
      id: `provenance-${caseId}`,
      target: allTargets,
      recorded: nowIso,
      reviewSummary: {
        keptCount,
        editedCount,
        rejectedCount,
        pendingCount,
      },
      signature: [
        {
          when: nowIso,
          who: { display: "MediTrace Post-Review Deterministic Recompiler" },
          data: digestSha256,
        },
      ],
    },
  };

  const effectiveFhirBundle: Record<string, any> = {
    resourceType: "Bundle",
    id: `bundle-effective-${caseId}`,
    type: "document",
    timestamp: nowIso,
    meta: {
      profile: ["http://hl7.org/fhir/StructureDefinition/Bundle"],
      reviewSummary: { keptCount, editedCount, rejectedCount, pendingCount },
    },
    entry: [
      compositionEntry,
      patientEntry,
      encounterEntry,
      ...dynamicEntries,
      ...keptLabObservationEntries,
      docRefEntry,
      provenanceEntry,
    ],
  };

  // ===========================================================================
  // 2. TÁI BIÊN DỊCH BẢNG & CHUỖI BHYT XML 1–5 (QĐ 130/QĐ-BYT & 4750/QĐ-BYT)
  // ===========================================================================
  const tenBenhXml1 =
    dsChanDoan.map((p) => p.text).join("; ") ||
    icdHieuLuc.chinh?.ten_benh_byt ||
    "[Chưa chốt chẩn đoán]";
  const maBenhChinhXml1 = icdHieuLuc.chinh?.ma_icd10 || "";
  const maBenhKtXml1 = icdHieuLuc.kemTheo.map((k) => k.ma_icd10).join(";");

  const xml1Obj = {
    MA_LK: caseId,
    HO_TEN: patientName,
    TEN_BENH: tenBenhXml1,
    MA_BENH_CHINH: maBenhChinhXml1,
    MA_BENH_KT: maBenhKtXml1,
    NGAY_LAP: nowIso.slice(0, 10).replace(/-/g, ""),
  };

  const xml2Arr = dsThuocKeDon.map((p, idx) => ({
    MA_LK: caseId,
    STT: idx + 1,
    TEN_THUOC: p.drug || p.text,
    LIEU_DUNG: p.text,
    LUOT_BANG_CHUNG: (p.evidenceTurns || []).map((t) => `T${t}`).join(","),
    QUYET_DUYET: p.reviewDecision,
  }));

  const xml3Arr = dsDvkt.map((p, idx) => ({
    MA_LK: caseId,
    STT: idx + 1,
    TEN_DICH_VU: p.text,
    LUOT_BANG_CHUNG: (p.evidenceTurns || []).map((t) => `T${t}`).join(","),
    QUYET_DUYET: p.reviewDecision,
  }));

  const xml4Arr = dsCls.map((p, idx) => ({
    MA_LK: caseId,
    STT: idx + 1,
    TEN_CHI_SO: p.text,
    KET_QUA: p.text,
    LUOT_BANG_CHUNG: (p.evidenceTurns || []).map((t) => `T${t}`).join(","),
    QUYET_DUYET: p.reviewDecision,
  }));

  const xml5Arr = bnProps
    .filter((p) => (p.situation || "thực tế").toLowerCase() !== "giả định")
    .map((p, idx) => ({
      MA_LK: caseId,
      STT: idx + 1,
      MUC_BENH_AN: p.section || "DIỄN BIẾN",
      DIEN_BIEN_LS: p.text,
      LUOT_THOAI_GOC: (p.evidenceTurns || []).map((t) => `T${t}`).join(","),
      QUYET_DUYET: p.reviewDecision,
    }));

  const xml1Str = [
    `<?xml version="1.0" encoding="UTF-8"?>`,
    `<TONG_HOP>`,
    `  <MA_LK>${xmlEscape(xml1Obj.MA_LK)}</MA_LK>`,
    `  <HO_TEN>${xmlEscape(xml1Obj.HO_TEN)}</HO_TEN>`,
    `  <TEN_BENH>${xmlEscape(xml1Obj.TEN_BENH)}</TEN_BENH>`,
    `  <MA_BENH_CHINH>${xmlEscape(xml1Obj.MA_BENH_CHINH)}</MA_BENH_CHINH>`,
    `  <MA_BENH_KT>${xmlEscape(xml1Obj.MA_BENH_KT)}</MA_BENH_KT>`,
    `  <NGAY_LAP>${xmlEscape(xml1Obj.NGAY_LAP)}</NGAY_LAP>`,
    `</TONG_HOP>`,
  ].join("\n");

  const xml2Str = [
    `<?xml version="1.0" encoding="UTF-8"?>`,
    `<DSACH_CHI_TIET_THUOC>`,
    ...xml2Arr.map(
      (r) =>
        `  <CHI_TIET_THUOC><MA_LK>${xmlEscape(r.MA_LK)}</MA_LK><STT>${r.STT}</STT><TEN_THUOC>${xmlEscape(
          r.TEN_THUOC
        )}</TEN_THUOC><LIEU_DUNG>${xmlEscape(r.LIEU_DUNG)}</LIEU_DUNG><LUOT_BANG_CHUNG>${xmlEscape(
          r.LUOT_BANG_CHUNG
        )}</LUOT_BANG_CHUNG><QUYET_DUYET>${xmlEscape(r.QUYET_DUYET)}</QUYET_DUYET></CHI_TIET_THUOC>`
    ),
    `</DSACH_CHI_TIET_THUOC>`,
  ].join("\n");

  const xml3Str = [
    `<?xml version="1.0" encoding="UTF-8"?>`,
    `<DSACH_CHI_TIET_DVKT>`,
    ...xml3Arr.map(
      (r) =>
        `  <CHI_TIET_DVKT><MA_LK>${xmlEscape(r.MA_LK)}</MA_LK><STT>${r.STT}</STT><TEN_DICH_VU>${xmlEscape(
          r.TEN_DICH_VU
        )}</TEN_DICH_VU><LUOT_BANG_CHUNG>${xmlEscape(r.LUOT_BANG_CHUNG)}</LUOT_BANG_CHUNG><QUYET_DUYET>${xmlEscape(
          r.QUYET_DUYET
        )}</QUYET_DUYET></CHI_TIET_DVKT>`
    ),
    `</DSACH_CHI_TIET_DVKT>`,
  ].join("\n");

  const xml4Str = [
    `<?xml version="1.0" encoding="UTF-8"?>`,
    `<DSACH_CHI_TIET_CLS>`,
    ...xml4Arr.map(
      (r) =>
        `  <CHI_TIET_CLS><MA_LK>${xmlEscape(r.MA_LK)}</MA_LK><STT>${r.STT}</STT><TEN_CHI_SO>${xmlEscape(
          r.TEN_CHI_SO
        )}</TEN_CHI_SO><KET_QUA>${xmlEscape(r.KET_QUA)}</KET_QUA><LUOT_BANG_CHUNG>${xmlEscape(
          r.LUOT_BANG_CHUNG
        )}</LUOT_BANG_CHUNG><QUYET_DUYET>${xmlEscape(r.QUYET_DUYET)}</QUYET_DUYET></CHI_TIET_CLS>`
    ),
    `</DSACH_CHI_TIET_CLS>`,
  ].join("\n");

  const xml5Str = [
    `<?xml version="1.0" encoding="UTF-8"?>`,
    `<DSACH_CHI_TIET_DIEN_BIEN_BENH>`,
    ...xml5Arr.map(
      (r) =>
        `  <CHI_TIET_DIEN_BIEN_BENH><MA_LK>${xmlEscape(r.MA_LK)}</MA_LK><STT>${r.STT}</STT><MUC_BENH_AN>${xmlEscape(
          r.MUC_BENH_AN
        )}</MUC_BENH_AN><DIEN_BIEN_LS>${xmlEscape(r.DIEN_BIEN_LS)}</DIEN_BIEN_LS><LUOT_THOAI_GOC>${xmlEscape(
          r.LUOT_THOAI_GOC
        )}</LUOT_THOAI_GOC><QUYET_DUYET>${xmlEscape(r.QUYET_DUYET)}</QUYET_DUYET></CHI_TIET_DIEN_BIEN_BENH>`
    ),
    `</DSACH_CHI_TIET_DIEN_BIEN_BENH>`,
  ].join("\n");

  const effectiveXml15: BangXml15HieuLuc = {
    XML1: xml1Str,
    XML2: xml2Str,
    XML3: xml3Str,
    XML4: xml4Str,
    XML5: xml5Str,
    bang_du_lieu: {
      XML1_TONG_HOP: xml1Obj,
      XML2_THUOC: xml2Arr,
      XML3_DVKT_VTYT: xml3Arr,
      XML4_CLS: xml4Arr,
      XML5_DIEN_BIEN_LS: xml5Arr,
    },
  };

  return {
    caseId,
    patientIdentifier: patientName,
    exportedAt: nowIso,
    reviewSummary: {
      totalOriginal: rawProps.length,
      activeCount: activeProps.length,
      keptCount,
      editedCount,
      rejectedCount,
      pendingCount,
    },
    propositions: activeProps,
    effective_fhir_bundle: effectiveFhirBundle,
    effective_xml_1_5: effectiveXml15,
    hl7_fhir_r4_bundle: effectiveFhirBundle,
    bhyt_qd130_4750: {
      ma_icd10_chinh: icdHieuLuc.chinh,
      ma_icd10_kem_theo: icdHieuLuc.kemTheo,
      bang_xml_130_4750: effectiveXml15.bang_du_lieu,
    },
    stage_45_omission_recovery: noteMeta?.clinicalSafety?.khoi_phuc_bo_sot_tang_45 || [],
    audit_trail_worm: noteMeta?.clinicalSafety?.audit_trail_worm || null,
  };
}
