/**
 * Mẫu văn bản cho nút "Tạo". Mỗi mẫu là một CÂU CHỈ DẪN cấu trúc gửi cho mô hình ngoài, cùng lời
 * thoại + bản nháp + tab Ngữ cảnh của ca. Mô hình chỉ được dùng thông tin có trong ba nguồn đó;
 * thiếu thì ghi [cần bổ sung] (xem /api/generate-document trong server.ts).
 *
 * Riêng "Bản nháp hồ sơ lâm sàng" do Qwen3-4B của dự án sinh tại chỗ — đó là phần được đo.
 */
import type { Session } from "../types";
import type { NoteMeta } from "../components/VerificationView";

export type NhomMau = "ho_so" | "nguoi_benh" | "hanh_chinh";

export interface MauVanBan {
  id: string;
  ten: string;
  nhom: NhomMau;
  /** Chỉ dẫn cấu trúc cho mô hình. */
  chiDan: string;
  /** true: do Qwen3-4B tại chỗ sinh (không gửi ra ngoài). */
  taiCho?: boolean;
  /** Mẫu do người dùng tạo. */
  tuTao?: boolean;
}

export const TEN_NHOM: Record<NhomMau, string> = {
  ho_so: "Hồ sơ bệnh án",
  nguoi_benh: "Cho người bệnh",
  hanh_chinh: "Hành chính",
};

export const MAU_BAN_NHAP: MauVanBan = {
  id: "ban-nhap-de-tai",
  ten: "Bản nháp hồ sơ lâm sàng (Qwen3-4B, tại chỗ)",
  nhom: "ho_so",
  taiCho: true,
  chiDan: "",
};

export const MAU_CO_SAN: MauVanBan[] = [
  {
    id: "soap",
    ten: "Bệnh án SOAP",
    nhom: "ho_so",
    chiDan:
      "Viết bệnh án theo SOAP: S (chủ quan: lý do khám, bệnh sử, tiền sử, thuốc, dị ứng — ghi rõ thông tin nào " +
      "là của người nhà), O (khách quan: dấu hiệu sinh tồn, khám), A (đánh giá: CHỈ ghi điều bác sĩ đã nói), " +
      "P (kế hoạch: CHỈ ghi điều bác sĩ đã nói).",
  },
  {
    id: "benh-an-noi-khoa",
    ten: "Bệnh án nội khoa (hỏi bệnh – khám – hướng xử trí)",
    nhom: "ho_so",
    chiDan:
      "Viết bệnh án nội khoa theo mục: Lý do vào viện; Bệnh sử; Tiền sử bản thân; Tiền sử gia đình (tách riêng " +
      "thông tin của người nhà); Thuốc đang dùng; Dị ứng; Khám lâm sàng; Tóm tắt bệnh án; Chẩn đoán sơ bộ và " +
      "Hướng xử trí (CHỈ ghi điều bác sĩ đã nói, không tự đề xuất).",
  },
  {
    id: "tom-tat-kham",
    ten: "Tóm tắt cuộc khám để lưu hồ sơ",
    nhom: "ho_so",
    chiDan:
      "Tóm tắt cuộc khám ngắn gọn (tối đa 150 từ) cho hồ sơ: lý do khám, diễn biến chính, thông tin quan trọng " +
      "(thuốc, dị ứng, bệnh nền), những gì bác sĩ đã kết luận và dặn dò.",
  },
  {
    id: "huong-dan-ra-ve",
    ten: "Hướng dẫn ra về cho người bệnh",
    nhom: "nguoi_benh",
    chiDan:
      "Viết hướng dẫn chăm sóc tại nhà cho người bệnh, lời lẽ dễ hiểu, xưng hô lịch sự: cách dùng thuốc bác sĩ " +
      "đã dặn, những việc nên và không nên làm mà bác sĩ đã nói, khi nào cần quay lại khám, lịch tái khám.",
  },
  {
    id: "giay-nghi",
    ten: "Giấy xác nhận đi khám / nghỉ học, nghỉ làm",
    nhom: "hanh_chinh",
    chiDan:
      "Viết giấy xác nhận người bệnh đã đến khám, để nộp cho trường hoặc nơi làm việc. Họ tên, ngày khám, số " +
      "ngày nghỉ: chỉ ghi nếu có trong nguồn, không thì [cần bổ sung]. Không ghi chi tiết bệnh ngoài điều cần thiết.",
  },
  {
    id: "chuyen-tuyen",
    ten: "Giấy chuyển tuyến / thư giới thiệu",
    nhom: "hanh_chinh",
    chiDan:
      "Viết thư giới thiệu chuyển người bệnh: nơi chuyển đến [cần bổ sung], lý do chuyển (theo lời bác sĩ), tóm " +
      "tắt bệnh, thuốc đang dùng, dị ứng, điều đã làm.",
  },
];

/** Lý do khám của ca: lấy từ mục LÝ DO trong bản nháp, không có thì dòng mô tả của ca. */
export function lyDoKham(ca?: Session, note?: NoteMeta | null) {
  const van = note?.content || "";
  const m = van.match(/L[ÝY] DO[^\n]*\n+([^\n]+)/i);
  const tuBanNhap = m?.[1]?.trim().replace(/[.。]\s*$/, "").replace(/\s*\([^)]*\)$/, "");
  if (tuBanNhap) return tuBanNhap;
  const phu = (ca?.patientSubtitle || "").trim();
  if (phu && !/^Dữ liệu tổng hợp|^Ca khám bệnh mới/i.test(phu)) return phu;
  return "";
}
