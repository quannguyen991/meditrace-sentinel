/**
 * Schema Contract chính thức giữa Python Core API (`src/he_thong/hop_dong_api.py`)
 * và Node/TypeScript BFF + Frontend (`web/server.ts`, `web/may-chu/routes/*`).
 *
 * Mọi thay đổi trường trả về cần cập nhật đồng bộ với `src/he_thong/hop_dong_api.py`.
 */

export interface PyAsrInfo {
  nha_cung_cap: string;
  mo_hinh: string;
}

export interface PyHealthResponse {
  ok: boolean;
  mo_hinh: string;
  adapter_trich: string | null;
  da_nap_mo_hinh: boolean;
  cho_nap_mo_hinh: boolean;
  mo_hinh_xa: string | null;
  thiet_bi: string;
  so_ca_bo_dem: number;
  chinh_sach_cong: string;
  bo_cham: string;
  asr: PyAsrInfo;
  tach_nguoi_noi: string;
}

export interface PySampleCaseItem {
  id?: string;
  bo?: string;
  tieu_de?: string;
  input?: string;
  [key: string]: unknown;
}

export interface PySampleCasesResponse {
  ca: PySampleCaseItem[];
}

export interface PyDoanAsr {
  speaker_id?: string;
  text_original?: string;
  start_time?: number;
  end_time?: number;
  start_s?: number;
  end_s?: number;
  asr_confidence?: number;
  asr_review_required?: boolean;
  [key: string]: unknown;
}

export interface PyTranscribeResponse {
  phien: string;
  doan: PyDoanAsr[];
  giay_xu_ly?: number;
  nguon?: string;
  tach_nguoi_noi?: Record<string, unknown> | null;
  ghi_chu?: string | null;
}

export interface PyAssignRolesResponse {
  phien: string;
  doan: PyDoanAsr[];
}

export interface PyPhatBieu {
  id: number;
  noi_dung?: string;
  ten_chu_the?: string | null;
  chu_the_id?: number | null;
  do_chac_chan?: string;
  phu_dinh?: boolean;
  tinh_huong?: string;
  moc_thoi_gian?: string | null;
  bang_chung?: number[];
  trich_dan?: string[];
  thuoc?: Record<string, string> | null;
}

export interface PyGhiChu {
  id?: number;
  muc?: string;
  van?: string;
  ly_do?: string | null;
}

export interface PyCauHoi {
  van?: string;
  muc?: string;
}

export interface PyCanhBaoItem {
  ma?: string;
  nhom?: string;
  nhom_ten?: string;
  tieu_de?: string;
  giai_thich?: string;
  ly_do?: string;
  luot?: number[];
  trich?: string[];
  muc_do?: string;
  bat_dinh?: string;
  ket_luan?: string;
  tin_cay?: string;
  anh_huong_trang_thai?: boolean;
  phu?: string[];
  phu_tieu_de?: string[];
  bo_phat_hien?: string;
}

export interface PyNoteResponse {
  id: string;
  nhanh: string;
  chinh_sach?: string;
  nguon: string;
  giay_xu_ly?: number;
  input?: string;
  du_doan: string;
  du_doan_khong_muc_phu?: string;
  phat_bieu: PyPhatBieu[];
  ghi_chu: PyGhiChu[];
  cau_hoi?: PyCauHoi[];
  so_can_xac_nhan?: number;
  canh_bao?: {
    theo_phat_bieu?: Record<string, { chinh?: PyCanhBaoItem; khac?: PyCanhBaoItem[]; phu?: string[] }>;
    trang_thai_D?: Record<string, { trang_thai?: string; ly_do?: string }>;
    toan_ca?: PyCanhBaoItem[];
    chinh_sach?: string;
    phien_ban?: string;
  } | null;
  lam_sang_nang_cao?: Record<string, unknown> | null;
  worm_seq?: number | null;
  worm_hash?: string | null;
}

export interface PyBhytPrecheckResponse {
  ma_icd10_chinh: string | null;
  ma_icd10_kem_theo: string[];
  canh_bao_xuat_toan_bhyt: unknown[];
  canh_bao_lieu_nhi_khoa?: unknown[];
  canh_bao_da_thuoc_dong_tay_y?: unknown[];
  bang_xml_130_4750?: Record<string, unknown>;
  dat_chuan_cdss_muc_6_7_tt54?: boolean;
  icd10_chi_tiet: unknown[];
  canh_bao_xuat_toan?: unknown[];
  goi_xml_1_5?: Record<string, unknown>;
  [key: string]: unknown;
}

export interface PyOcrPhieuCuResponse {
  chi_so: Record<string, unknown>;
  thuoc_nhan_dien: unknown[];
  hieu_chinh_lieu: unknown[];
  [key: string]: unknown;
}

export interface PyErrorAttributionResponse {
  ok: boolean;
  quy_ket: Record<string, unknown>;
}

// ============================================================================
// Node BFF Response Contracts (trả về cho React Frontend)
// ============================================================================

export interface ApiUiWarning {
  code?: string;
  group?: string;
  groupName?: string;
  title?: string;
  explanation?: string;
  reason?: string;
  turns: number[];
  quotes: string[];
  severity?: string;
  uncertainty?: string;
  kind?: string;
  reliability?: string;
  affectsState: boolean;
  tags: string[];
  tagTitles: string[];
  detector?: string;
}

export interface ApiUiProposition {
  id: number;
  text: string;
  section: string;
  status: "can_xac_nhan" | "than";
  gateReason: string | null;
  subject: string | null;
  negated: boolean;
  certainty: string | null;
  situation: string | null;
  time: string | null;
  drug: string | null;
  evidenceTurns: number[];
  quotes: string[];
  warning: ApiUiWarning | null;
  otherWarnings: Array<ApiUiWarning | null>;
  warningTags: string[];
  stateD: string | null;
  stateDReason: string | null;
}

export interface ApiTranscribeResponse {
  transcript: string;
  segments: PyDoanAsr[];
  transcriptSegments: Array<{
    luot: number;
    start_s: number;
    end_s: number;
    lowConf: boolean;
  }>;
  sessionId: string;
  seconds?: number;
  source?: string;
  diarization: Record<string, unknown> | null;
  note?: string | null;
}

export interface ApiAssignRolesResponse {
  sessionId: string;
  segments: PyDoanAsr[];
}

export interface ApiNoteResponse {
  content: string;
  contentWithoutExtras?: string;
  propositions: ApiUiProposition[];
  questions: Array<string | undefined>;
  needsConfirmCount: number;
  caseId: string;
  branch: string;
  policy?: string;
  source: string;
  seconds?: number;
  transcript?: string;
  caseWarnings: Array<ApiUiWarning | null>;
  warningPolicy: string | null;
  warningVersion: string | null;
  clinicalSafety: Record<string, unknown> | null;
}

export interface ApiNoteJobResponse {
  jobId: string;
  queued: number;
  startedAt: number;
}

export interface ApiSignOffResponse {
  ok: boolean;
  signedAt: string;
  tongMenhDe: number;
  soGiu: number;
  soSua: number;
  soBo: number;
  tyLeCoNguon: number;
  hash: string;
  wormSeq: number;
}

export interface ApiSessionStoreResponse {
  sessions: unknown[];
  savedAt: number;
}

export const API_CONTRACT_SCHEMA = {
  PyHealthResponse: [
    "ok",
    "mo_hinh",
    "adapter_trich",
    "da_nap_mo_hinh",
    "cho_nap_mo_hinh",
    "mo_hinh_xa",
    "thiet_bi",
    "so_ca_bo_dem",
    "chinh_sach_cong",
    "bo_cham",
    "asr",
    "tach_nguoi_noi",
  ],
  PySampleCasesResponse: ["ca"],
  PyTranscribeResponse: ["phien", "doan"],
  PyAssignRolesResponse: ["phien", "doan"],
  PyNoteResponse: ["id", "nhanh", "nguon", "du_doan", "phat_bieu", "ghi_chu"],
  PyBhytPrecheckResponse: ["ma_icd10_chinh", "ma_icd10_kem_theo", "canh_bao_xuat_toan_bhyt", "icd10_chi_tiet"],
  PyOcrPhieuCuResponse: ["chi_so", "thuoc_nhan_dien", "hieu_chinh_lieu"],
  PyErrorAttributionResponse: ["ok", "quy_ket"],
} as const;
