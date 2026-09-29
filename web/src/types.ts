import type { NoteMeta, Quyet } from "./components/VerificationView";

/** Kết quả bác sĩ duyệt mệnh đề của MỘT bản nháp. `khoa` tính từ nội dung bản nháp: tạo lại bản
 *  nháp thì khoá đổi, kết quả cũ không áp vào mệnh đề mới. */
export interface KetQuaDuyet {
  khoa: string;
  quyet: Record<number, Quyet>;
  banSua: Record<number, string>;
}

export type ViewMode = "home" | "scribe" | "evidence" | "tasks" | "patients" | "templates" | "verification" | "library" | "settings";

export interface Session {
  id: string;
  patientIdentifier: string;
  patientSubtitle: string;
  date: string;
  time: string;
  language: string;
  durationSeconds: number;
  isRecording: boolean;
  transcript: string;
  tabs: DocumentTabItem[];
  activeTabId: string;
  contextNotes?: string;
  audioUrl?: string;
  /** Bản nháp gần nhất của CA NÀY (mệnh đề, câu hỏi làm rõ, nhãn nguồn). Lưu cùng ca. */
  note?: NoteMeta | null;
  /** Hỏi đáp ở ngăn phải của ca này. */
  evidenceChat?: ClinicalChatMessage[];
  /** Kết quả duyệt mệnh đề (giữ/sửa/bỏ) — lưu cùng ca để F5 không mất. */
  duyet?: KetQuaDuyet;
}

export interface DocumentTabItem {
  id: string;
  title: string;
  type: "transcript" | "context" | "soap" | "leaflet" | "custom";
  content: string;
  templateStyle?: "Goldilocks" | "Free" | "Comprehensive" | "Concise";
  badgeIcon?: string;
  isClosable?: boolean;
}

export interface ClinicalSource {
  name: string;
  domain: string;
  url?: string;
  /** Số thứ tự nguồn mô hình dùng trong câu trả lời, dạng [1]. */
  so?: number;
  /** Câu trả lời có trích tài liệu này không (server tìm được nhưng mô hình có thể không dùng). */
  cited?: boolean;
  /** Nhãn ngắn hiện trên thẻ nguồn cạnh từng ý ("Bộ Y tế · QĐ 2760", "MSD Manual", "NICE"). */
  nhan?: string;
  /** Nhóm nguồn (kcb, msd, fda, nice, who, cdc, medlineplus, pubmed) — dùng cho "Tra nguồn khác". */
  nhom?: string;
}

/** Câu trả lời tra cứu có cấu trúc (server trả kèm bản markdown). Số trong `nguon` là số tài liệu. */
export interface CauTrucTraLoi {
  ca_kham: string;
  tom_tat: string;
  /** `lech`: số trong ý mà máy không thấy trong tài liệu được trích (kiểm bằng máy, không phải kết luận sai). */
  phuong_an: Array<{ ten: string; noi_dung: string; nguon: number[]; lech?: string[] }>;
  luu_y_ca: string[];
  an_toan: Array<{ noi_dung: string; nguon: number[]; lech?: string[] }>;
  khac_nhau: string;
  khong_du: string;
  hoi_tiep: string[];
}

export interface ClinicalChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  thoughtTime?: string;
  sourcesCount?: number;
  sources?: ClinicalSource[];
  safetyNotes?: string[];
  timestamp: string;
  /** Chế độ hỏi ở ngăn phải: hỏi về ca khám hay tra nguồn chính thống. */
  mode?: "ca_kham" | "tra_cuu";
  /** Cảnh báo của server khi tra cứu (link bị bỏ, không có nguồn kiểm chứng được). */
  warning?: string | null;
  /** Số link mô hình đưa ra mà server đã bỏ (không mở được hoặc không chính thống). */
  removedSources?: number;
  /** Dòng nhỏ cuối câu trả lời: mô hình nào, mất bao lâu. */
  meta?: string;
  /** Câu trả lời có cấu trúc (thẻ nguồn cạnh từng ý, lưu ý an toàn, hỏi tiếp). */
  cauTruc?: CauTrucTraLoi | null;
  /** Câu hỏi gốc — để "Tra nguồn khác" hỏi lại. */
  question?: string;
}

export interface TemplateItem {
  id: string;
  title: string;
  category: "session" | "thu_vien";
  iconType: "sparkle" | "pen";
  isPro?: boolean;
  promptDescription?: string;
}

export interface Patient {
  id: string;
  name: string;
  identifier: string;
  dob?: string;
  gender?: string;
  phone?: string;
  lastConsultation?: string;
  chiefComplaint?: string;
}

export interface ClinicalTask {
  id: string;
  title: string;
  sessionId?: string;
  patientName?: string;
  dueDate: string;
  completed: boolean;
  priority: "high" | "medium" | "low";
}
