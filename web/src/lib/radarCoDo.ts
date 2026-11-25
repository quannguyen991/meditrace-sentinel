export interface GoiYCoDo {
  id: string;
  mucDo: "khan" | "canh_bao";
  cauHoi: string;
  lyDo: string;
  daHoi: boolean;
}

interface QuyTacCoDo {
  id: string;
  mucDo: "khan" | "canh_bao";
  kichHoat: RegExp;
  kiemGioi?: "nu";
  daHoiKhi: RegExp;
  cauHoi: string;
  lyDo: string;
}

const QUY_TAC_CO_DO: QuyTacCoDo[] = [
  {
    id: "thai_ky",
    mucDo: "khan",
    kichHoat: /(?<![\p{L}\p{N}_])(đau bụng dưới|trễ kinh|rong kinh|kháng sinh|nsaid|ibuprofen|tetracyclin|ciprofloxacin|levofloxacin|isotretinoin|statin|losartan|enalapril)(?![\p{L}\p{N}_])/iu,
    kiemGioi: "nu",
    daHoiKhi: /(?<![\p{L}\p{N}_])(mang thai|có thai|kinh cuối|chu kỳ kinh|thử thai|đang bầu|mãn kinh)(?![\p{L}\p{N}_])/iu,
    cauHoi: "Chị có đang mang thai hoặc trễ kinh không?",
    lyDo: "Tránh bỏ sót thai ngoài tử cung hoặc kê thuốc chống chỉ định thai kỳ.",
  },
  {
    id: "loet_da_day_nsaid",
    mucDo: "canh_bao",
    kichHoat: /(?<![\p{L}\p{N}_])(nsaid|ibuprofen|diclofenac|meloxicam|piroxicam|celecoxib|aspirin|corticoid|prednisolon|methylprednisolon|giảm đau khớp)(?![\p{L}\p{N}_])/iu,
    daHoiKhi: /(?<![\p{L}\p{N}_])(dạ dày|bao tử|xuất huyết tiêu hóa|ợ chua|trào ngược)(?![\p{L}\p{N}_])/iu,
    cauHoi: "Bác có tiền sử đau hoặc loét dạ dày không?",
    lyDo: "Thuốc kháng viêm/corticoid làm tăng nguy cơ xuất huyết tiêu hóa.",
  },
  {
    id: "mach_vanh_dau_nguc",
    mucDo: "khan",
    kichHoat: /(?<![\p{L}\p{N}_])(đau ngực|tức ngực|nặng ngực|khó thở|hồi hộp|đánh trống ngực)(?![\p{L}\p{N}_])/iu,
    daHoiKhi: /(?<![\p{L}\p{N}_])(lan|vã mồ hôi|tăng huyết áp|huyết áp|mạch vành|nhồi máu)(?![\p{L}\p{N}_])/iu,
    cauHoi: "Đau ngực có lan lên cổ/tay trái hoặc vã mồ hôi không?",
    lyDo: "Sàng lọc sớm hội chứng mạch vành cấp.",
  },
  {
    id: "di_ung_khang_sinh",
    mucDo: "khan",
    kichHoat: /(?<![\p{L}\p{N}_])(sốt cao|nhiễm khuẩn|viêm phổi|amoxicillin|augmentin|cefixim|ceftriaxon|azithromycin|penicillin|kháng sinh)(?![\p{L}\p{N}_])/iu,
    daHoiKhi: /(?<![\p{L}\p{N}_])(dị ứng|mề đay|sốc phản vệ|phản ứng thuốc)(?![\p{L}\p{N}_])/iu,
    cauHoi: "Trước đây bác có từng bị dị ứng thuốc hay kháng sinh nào không?",
    lyDo: "Phòng ngừa sốc phản vệ trước khi kê đơn.",
  },
  {
    id: "suy_than_thuoc",
    mucDo: "canh_bao",
    kichHoat: /(?<![\p{L}\p{N}_])(metformin|allopurinol|ciprofloxacin|levofloxacin|enoxaparin|spironolacton|tiểu đường|gout)(?![\p{L}\p{N}_])/iu,
    daHoiKhi: /(?<![\p{L}\p{N}_])(suy thận|chức năng thận|creatinin|egfr|phù|tiểu ít)(?![\p{L}\p{N}_])/iu,
    cauHoi: "Gần đây bác có xét nghiệm chức năng thận hoặc bị phù/tiểu ít không?",
    lyDo: "Thuốc thải qua thận cần kiểm tra eGFR để chỉnh liều.",
  },
];

/**
 * Radar Câu hỏi Cờ đỏ theo thời gian thực (0 token, chạy tại chỗ < 10ms).
 * Trả về tối đa 2 gợi ý ưu tiên chưa được hỏi, kèm các mục vừa được đánh dấu ✓ xong.
 */
export function quetRadarCoDo(
  transcript: string,
  gioiTinh?: string | null
): GoiYCoDo[] {
  const chu = (transcript || "").trim();
  if (!chu) return [];
  const laNu = Boolean(gioiTinh && /(?<![\p{L}\p{N}_])(nữ|female)(?![\p{L}\p{N}_])/iu.test(gioiTinh));
  const laNam = !laNu && Boolean(gioiTinh && /(?<![\p{L}\p{N}_])(nam|male)(?![\p{L}\p{N}_])/iu.test(gioiTinh));

  const ketQua: GoiYCoDo[] = [];
  for (const qt of QUY_TAC_CO_DO) {
    if (qt.kiemGioi === "nu" && laNam) continue;
    if (!qt.kichHoat.test(chu)) continue;
    ketQua.push({
      id: qt.id,
      mucDo: qt.mucDo,
      cauHoi: qt.cauHoi,
      lyDo: qt.lyDo,
      daHoi: qt.daHoiKhi.test(chu),
    });
  }

  // Ưu tiên mục chưa hỏi & khẩn cấp lên đầu, giới hạn tối đa 2 mục đang mở + 1 mục vừa ✓
  const chuaHoi = ketQua
    .filter((x) => !x.daHoi)
    .sort((a, b) => (a.mucDo === "khan" ? -1 : 1) - (b.mucDo === "khan" ? -1 : 1))
    .slice(0, 2);
  const daXong = ketQua.filter((x) => x.daHoi).slice(0, 1);
  return [...chuaHoi, ...daXong];
}
