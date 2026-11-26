/**
 * Mẫu văn bản cho nút "Tạo". Mỗi mẫu là một CÂU CHỈ DẪN cấu trúc gửi cho mô hình ngoài, cùng lời
 * thoại + bản nháp + tab Ngữ cảnh của ca; HOẶC là biểu mẫu pháp lý / chuyên khoa biên dịch 100% tại chỗ
 * bằng luật tất định (`bienDichLuatTaiCho: true`, < 10 ms, 0 byte gửi ra ngoài).
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
  /** Chỉ dẫn cấu trúc cho mô hình hoặc mô tả khung pháp lý. */
  chiDan: string;
  /** true: do Qwen3-4B tại chỗ sinh (không gửi ra ngoài). */
  taiCho?: boolean;
  /** true: biên dịch tất định 100% tại chỗ từ mệnh đề đã duyệt theo luật BYT (không gọi mô hình ngoài). */
  bienDichLuatTaiCho?: boolean;
  /** Alias tương thích cho các trình gọi kiểm tra biên dịch tại chỗ. */
  taiChoBienDich?: boolean;
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
    id: "phieu-chuyen-co-so-kcb-tt01-2025",
    ten: "Phiếu chuyển cơ sở KCB BHYT (Phụ lục TT 01/2025/TT-BYT)",
    nhom: "hanh_chinh",
    bienDichLuatTaiCho: true,
    taiChoBienDich: true,
    chiDan:
      "Biên dịch tại chỗ Phiếu chuyển cơ sở KCB BHYT theo Thông tư 01/2025/TT-BYT (3 cấp chuyên môn kỹ thuật: Ban đầu / Cơ bản / Chuyên sâu, tóm tắt lâm sàng, CLS, ICD-10, thuốc đã dùng, giá trị 1 năm bệnh mạn tính).",
  },
  {
    id: "phieu-chuyen-cls-tt01-2025",
    ten: "Phiếu chuyển dịch vụ cận lâm sàng (TT 01/2025/TT-BYT)",
    nhom: "hanh_chinh",
    bienDichLuatTaiCho: true,
    taiChoBienDich: true,
    chiDan:
      "Biên dịch tại chỗ Phiếu chuyển người bệnh/mẫu bệnh phẩm thực hiện dịch vụ cận lâm sàng theo Thông tư 01/2025/TT-BYT.",
  },
  {
    id: "giay-nghi-bhxh-tt25-2025",
    ten: "Giấy chứng nhận nghỉ việc hưởng BHXH (TT 25/2025/TT-BYT)",
    nhom: "hanh_chinh",
    bienDichLuatTaiCho: true,
    taiChoBienDich: true,
    chiDan:
      "Biên dịch tại chỗ Giấy chứng nhận nghỉ việc hưởng BHXH theo Thông tư 25/2025/TT-BYT (kiểm tra trần tối đa 30 ngày/lần ngoại trú và họ tên cha/mẹ khi bệnh nhi < 7 tuổi).",
  },
  {
    id: "tom-tat-hsba-ra-vien-tt32",
    ten: "Bản tóm tắt hồ sơ bệnh án & Giấy ra viện (TT 32/2023/TT-BYT)",
    nhom: "hanh_chinh",
    bienDichLuatTaiCho: true,
    taiChoBienDich: true,
    chiDan:
      "Biên dịch tại chỗ Bản tóm tắt hồ sơ bệnh án & Giấy ra viện đúng biểu mẫu Thông tư 32/2023/TT-BYT từ mệnh đề bác sĩ đã duyệt.",
  },
  {
    id: "bien-ban-hoi-chan-tt32",
    ten: "Biên bản hội chẩn khoa / liên khoa (TT 32/2023/TT-BYT)",
    nhom: "ho_so",
    bienDichLuatTaiCho: true,
    taiChoBienDich: true,
    chiDan:
      "Biên dịch tại chỗ Biên bản hội chẩn khoa / liên khoa theo Thông tư 32/2023/TT-BYT kèm dẫn nguồn [T_i].",
  },
  {
    id: "khuon-nhi-khoa",
    ten: "Bệnh án Nhi khoa chuyên biệt (TT 26/2025 · mg/kg/ngày)",
    nhom: "ho_so",
    bienDichLuatTaiCho: true,
    taiChoBienDich: true,
    chiDan:
      "Biên dịch tại chỗ Bệnh án Nhi khoa: bắt buộc cân nặng (TT 26/2025), tháng tuổi, liều mg/kg/ngày, tiền sử tiêm chủng & dinh dưỡng, tách riêng lời khai người chăm sóc.",
  },
  {
    id: "khuon-san-phu-khoa",
    ten: "Bệnh án Sản - Phụ khoa (PARA · Tuổi thai · Tim thai)",
    nhom: "ho_so",
    bienDichLuatTaiCho: true,
    taiChoBienDich: true,
    chiDan:
      "Biên dịch tại chỗ Bệnh án Sản - Phụ khoa: chỉ số PARA, tuổi thai, kinh cuối, thai máy, tim thai và rà soát thuốc an toàn thai kỳ.",
  },
  {
    id: "khuon-cap-cuu-chan-thuong",
    ten: "Bệnh án Cấp cứu - Chấn thương (ABCDE + AMPLE + Glasgow)",
    nhom: "ho_so",
    bienDichLuatTaiCho: true,
    taiChoBienDich: true,
    chiDan:
      "Biên dịch tại chỗ Bệnh án Cấp cứu - Chấn thương theo khảo sát sơ cấp ABCDE, thang điểm Glasgow (GCS) và bệnh sử AMPLE.",
  },
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
