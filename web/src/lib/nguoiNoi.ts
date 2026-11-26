/**
 * Bản chép có tách người nói -> các dòng "Người nói N: …", và gán vai theo người nói.
 *
 * Máy tách người nói theo GIỌNG (pyannote chạy tại chỗ), không biết ai là bác sĩ. Mỗi người nói
 * chỉ mang số thứ tự ("Người nói 1" là người cất tiếng trước). Vai Bác sĩ / Bệnh nhân / Người nhà
 * do người dùng gán; còn dòng "Người nói N" thì App chặn tạo bản nháp, như với "Chưa rõ vai".
 *
 * Boost 1 bổ sung lớp gợi ý vai tất định (`goiYVaiTuDoan`, `goiYVaiTuVanBanLuot`, `apDungVaiGoiY`)
 * để bác sĩ chỉ cần 1 cú bấm áp dụng gợi ý cho các lượt chưa gán rồi đọc kiểm lại ngoại lệ,
 * tuyệt đối KHÔNG tự ý ghi đè các dòng đã gán Bác sĩ / Bệnh nhân / Người nhà.
 */

export type VaiChuan = "Bác sĩ" | "Bệnh nhân" | "Người nhà";

export type DoanChep = {
  speaker_id?: string | null;
  text_original?: string | null;
  suggested_role?: string | null;
  suggested_role_reason?: string | null;
};

export type ThongTinTach = {
  phuong_phap?: string;
  tach_that?: boolean;
  so_nguoi_noi?: number;
  loi?: string;
  lui_ve?: boolean;
  bo_qua?: boolean;
};

const NHAN_RE = /^\s*người nói\s+(\d+)\s*:/i;
const DONG_CHUA_GAN_RE = /^\s*(chưa rõ vai|người nói\s+\d+|speaker_\d+)\s*:/i;
const DONG_DA_GAN_RE = /^\s*(bác sĩ|bác sỹ|doctor|bs|bệnh nhân|patient|bn|người nhà)\s*:/i;

/** Chuẩn hoá chuỗi vai gợi ý về 3 vai chuẩn hoặc null nếu không chắc. */
export function chuanHoaVaiGoiY(vai?: string | null): VaiChuan | null {
  if (!vai) return null;
  const t = vai.trim().toLowerCase();
  if (t === "bác sĩ" || t === "bác sỹ" || t === "doctor" || t === "bs" || t === "bac_si") {
    return "Bác sĩ";
  }
  if (t === "bệnh nhân" || t === "người bệnh" || t === "patient" || t === "bn" || t === "benh_nhan") {
    return "Bệnh nhân";
  }
  if (t === "người nhà" || t === "thân nhân" || t === "family" || t === "caregiver" || t === "nguoi_nha") {
    return "Người nhà";
  }
  return null;
}

/** Số của nhãn "Người nói N" ở đầu dòng; null nếu dòng không mang nhãn đó. */
export function soCuaDong(dong: string): number | null {
  const m = dong.match(NHAN_RE);
  return m ? Number(m[1]) : null;
}

/** Số lớn nhất của nhãn "Người nói N" đang có (0 nếu chưa có). */
export function soNguoiNoiLonNhat(transcript: string): number {
  let lon = 0;
  for (const d of (transcript || "").split("\n")) {
    const n = soCuaDong(d);
    if (n !== null && n > lon) lon = n;
  }
  return lon;
}

/**
 * Đoạn chép -> các dòng lời thoại.
 * - Máy đã tách thật: "Người nói N: …". `batDau` cộng vào N để tệp ghi âm thứ hai không trùng
 *   số với tệp đầu (hai "Người nói 1" của hai tệp có thể là hai người khác nhau).
 * - Chưa tách: "Chưa rõ vai: …" như trước.
 */
export function dongTuDoan(doan: DoanChep[], tach?: ThongTinTach | null, batDau = 0): string[] {
  return doan
    .map((d) => ({ chu: (d.text_original || "").trim(), m: /^speaker_(\d+)$/.exec(d.speaker_id || "") }))
    .filter((x) => x.chu)
    .map(({ chu, m }) =>
      tach?.tach_that && m ? `Người nói ${Number(m[1]) + batDau}: ${chu}` : `Chưa rõ vai: ${chu}`
    );
}

export type NguoiNoiChuaGan = { so: number; nhan: string; soLuot: number; viDu: string };

/** Người nói máy đã tách mà chưa được gán vai, theo số thứ tự, kèm số lượt và câu đầu tiên. */
export function cacNguoiNoiChuaGan(transcript: string): NguoiNoiChuaGan[] {
  const gom = new Map<number, NguoiNoiChuaGan>();
  for (const d of (transcript || "").split("\n")) {
    const m = d.match(NHAN_RE);
    if (!m) continue;
    const so = Number(m[1]);
    const cu = gom.get(so);
    if (cu) cu.soLuot += 1;
    else {
      const chu = d.slice(m[0].length).trim();
      gom.set(so, { so, nhan: `Người nói ${so}`, soLuot: 1, viDu: chu.length > 70 ? `${chu.slice(0, 69)}…` : chu });
    }
  }
  return [...gom.values()].sort((a, b) => a.so - b.so);
}

/** Gán vai cho MỌI dòng của một người nói. Dòng khác (kể cả dòng trống) giữ nguyên. */
export function ganVaiNguoiNoi(transcript: string, so: number, vai: string): string {
  return (transcript || "")
    .split("\n")
    .map((d) => {
      const m = d.match(NHAN_RE);
      return m && Number(m[1]) === so ? `${vai}: ${d.slice(m[0].length).trim()}` : d;
    })
    .join("\n");
}

const MAU_NGUOI_NHA: Array<[RegExp, string]> = [
  [/(?<![\p{L}\p{N}_])tôi\s+là\s+(?:người\s+nhà|vợ|chồng|con|bố|mẹ|anh|chị|em\s+ruột)(?![\p{L}\p{N}_])/iu, "Xưng danh người nhà"],
  [/(?<![\p{L}\p{N}_])em\s+là\s+(?:người\s+nhà|vợ|chồng|con|mẹ|bố)\s+(?:của\s+)?(?:bệnh\s+nhân|bác|anh|chị|cháu|bé|ông|bà)(?![\p{L}\p{N}_])/iu, "Xưng danh người chăm sóc"],
  [/(?<![\p{L}\p{N}_])(?:cháu|bé|con|ông|bà|bố|mẹ|nhà\s+em|vợ\s+tôi|chồng\s+tôi|chồng\s+em|vợ\s+em)\s+(?:nhà\s+(?:em|tôi|mình)\s+)?(?:ở\s+nhà\s+)?(?:bị|sốt|ho|đau|nôn|quấy|bỏ\s+bú|mệt|khó\s+thở|ngất|lú\s+lẫn)/iu, "Kể triệu chứng người thân"],
  [/(?<![\p{L}\p{N}_])(?:tôi|em|gia\s+đình)\s+đưa\s+(?:cháu|bé|con|bác|ông|bà|bố|mẹ|nhà\s+em|anh\s+ấy|chị\s+ấy)\s+đi\s+khám/iu, "Đưa người thân đi khám"],
];

const MAU_BAC_SI: Array<[RegExp, string]> = [
  [/(?<![\p{L}\p{N}_])(?:khám\s+thấy|nghe\s+phổi|nghe\s+tim|ấn\s+đau|bụng\s+mềm|họng\s+đỏ|huyết\s+áp\s+(?:của\s+(?:bác|anh|chị|ông|bà|cô|chú|em)|đo\s+được))/iu, "Nhận định khám thực thể của bác sĩ"],
  [/(?<![\p{L}\p{N}_])(?:tôi|mình|bác\s+sĩ)\s+(?:sẽ\s+)?(?:kê\s+đơn|kê\s+thuốc|cho\s+làm\s+xét\s+nghiệm|chỉ\s+định|cho\s+chụp|cho\s+siêu\s+âm)/iu, "Ra y lệnh / kê đơn"],
  [/(?<![\p{L}\p{N}_])(?:uống\s+ngày\s+\d+\s*lần|tái\s+khám\s+sau\s+\d+|nhập\s+viện\s+theo\s+dõi|hít\s+sâu\s+nhé|há\s+miệng\s+to|nằm\s+lên\s+giường\s+khám)/iu, "Hướng dẫn khám / dặn dò điều trị"],
  [/(?<![\p{L}\p{N}_])(?:bác|anh|chị|ông|bà|cô|chú|em|cháu)\s+(?:bị\s+)?(?:đau|ho|sốt|khó\s+thở|mệt|chóng\s+mặt|đi\s+ngoài|tiểu\s+buốt)[^?!.]*(?:bao\s+lâu\s+rồi|mấy\s+ngày\s+rồi|từ\s+khi\s+nào|như\s+thế\s+nào)\s*\?/iu, "Câu hỏi khai thác bệnh sử"],
  [/(?<![\p{L}\p{N}_])(?:có\s+sốt\s+không|có\s+khó\s+thở\s+không|có\s+dị\s+ứng\s+(?:thuốc|thức\s+ăn)?\s*(?:gì\s+)?không|trước\s+giờ\s+có\s+(?:tiền\s+sử|bệnh\s+nền)\s+gì\s+không|ở\s+nhà\s+đã\s+uống\s+thuốc\s+gì\s+chưa)\s*\??/iu, "Câu hỏi sàng lọc lâm sàng"],
  [/^\s*chào\s+(?:bác|anh|chị|ông|bà|cô|chú|em)[,!\s]+hôm\s+nay\s+(?:mình|bác|anh|chị|ông|bà|em)\s+(?:đi\s+khám|khó\s+chịu|đau\s+ở\s+đâu)/iu, "Lời mở đầu hỏi bệnh của bác sĩ"],
];

const MAU_BENH_NHAN: Array<[RegExp, string]> = [
  [/(?<![\p{L}\p{N}_])(?:dạ\s+|vâng\s+)?thưa\s+bác\s+sĩ/iu, "Xưng hô với bác sĩ"],
  [/^\s*(?:dạ|vâng)[,.\s]+(?:tôi|em|cháu|con|mình)\s+(?:bị|đau|ho|sốt|mệt|khó\s+thở|chóng\s+mặt|không|chưa|có|uống)/iu, "Trả lời triệu chứng bản thân"],
  [/(?<![\p{L}\p{N}_])(?:tôi|em|mình)\s+(?:bị\s+)?(?:đau\s+(?:đầu|ngực|bụng|lưng|họng|khớp|thượng\s+vị)|ho\s+(?:khan|có\s+đờm|kéo\s+dài|\d+\s*ngày)|sốt\s+\d+|khó\s+thở|mệt\s+mỏi|mất\s+ngủ|buồn\s+nôn|chóng\s+mặt)/iu, "Mô tả triệu chứng chủ quan"],
  [/(?<![\p{L}\p{N}_])(?:mười\s+ngày|hai\s+tuần|ba\s+ngày|mấy\s+hôm\s+nay|\d+\s*(?:ngày|tuần|tháng))\s+rồi\s+ạ(?![\p{L}\p{N}_])/iu, "Trả lời thời gian bệnh lễ phép"],
  [/^\s*dạ\s+(?:không|chưa|có|đúng\s+rồi|vâng)\s+ạ[.!]?\s*$/iu, "Câu đáp ngắn của người bệnh"],
];

/**
 * Heuristic tiếng Việt tất định gợi ý vai cho một dòng lời thoại đang để "Chưa rõ vai" / "Người nói N"
 * (hoặc câu thoại trần chưa có tiền tố). Trả `vaiGoiY: null` khi câu mơ hồ hoặc dòng đã có vai chuẩn.
 */
export function goiYVaiTuVanBanLuot(dong: string): {
  vaiGoiY: VaiChuan | null;
  lyDo: string | null;
} {
  const tho = (dong || "").trim();
  if (!tho) return { vaiGoiY: null, lyDo: null };
  if (DONG_DA_GAN_RE.test(tho)) return { vaiGoiY: null, lyDo: null };

  const mChuaGan = tho.match(DONG_CHUA_GAN_RE);
  const vanBan = (mChuaGan ? tho.slice(mChuaGan[0].length) : tho).trim();
  if (!vanBan) return { vaiGoiY: null, lyDo: null };

  let diemBs = 0;
  let lyDoBs: string | null = null;
  let diemBn = 0;
  let lyDoBn: string | null = null;
  let diemNn = 0;
  let lyDoNn: string | null = null;

  for (const [re, ld] of MAU_NGUOI_NHA) {
    if (re.test(vanBan)) {
      diemNn += 3;
      if (!lyDoNn) lyDoNn = ld;
    }
  }
  for (const [re, ld] of MAU_BAC_SI) {
    if (re.test(vanBan)) {
      diemBs += 2;
      if (!lyDoBs) lyDoBs = ld;
    }
  }
  for (const [re, ld] of MAU_BENH_NHAN) {
    if (re.test(vanBan)) {
      diemBn += 2;
      if (!lyDoBn) lyDoBn = ld;
    }
  }

  // Nếu vừa xưng "cháu nhà em / vợ tôi" (Người nhà) vừa lễ phép "thưa bác sĩ", ưu tiên Người nhà.
  if (diemNn >= 3 && diemNn >= diemBs) {
    return { vaiGoiY: "Người nhà", lyDo: lyDoNn };
  }
  if (diemBs >= 2 && diemBs > diemBn && diemNn === 0) {
    return { vaiGoiY: "Bác sĩ", lyDo: lyDoBs };
  }
  if (diemBn >= 2 && diemBn > diemBs && diemNn === 0) {
    return { vaiGoiY: "Bệnh nhân", lyDo: lyDoBn };
  }
  return { vaiGoiY: null, lyDo: null };
}

/**
 * Lấy danh sách gợi ý vai theo từng lượt nói không rỗng từ mảng `segments` của `/api/transcribe`.
 * Ưu tiên `suggested_role` do dịch vụ tại chỗ trả về; nếu thiếu thì chạy heuristic tất định tại máy.
 */
export function goiYVaiTuDoan(
  doan: DoanChep[]
): Array<{ luot: number; vaiGoiY: VaiChuan | null; lyDo: string | null }> {
  const hopLe = (doan || []).filter((d) => Boolean((d.text_original || "").trim()));
  return hopLe.map((d, idx) => {
    const luot = idx + 1;
    const tuServer = chuanHoaVaiGoiY(d.suggested_role);
    if (tuServer) {
      return {
        luot,
        vaiGoiY: tuServer,
        lyDo: (d.suggested_role_reason || "").trim() || "Gợi ý từ phân tích giọng & ngữ cảnh tại chỗ",
      };
    }
    const tuLuat = goiYVaiTuVanBanLuot((d.text_original || "").trim());
    return {
      luot,
      vaiGoiY: tuLuat.vaiGoiY,
      lyDo: tuLuat.lyDo,
    };
  });
}

/**
 * Áp dụng vai gợi ý cho các dòng ĐANG MANG NHÃN "Chưa rõ vai:" hoặc "Người nói N:".
 * Tuyệt đối KHÔNG ghi đè dòng đã gán "Bác sĩ:", "Bệnh nhân:", hoặc "Người nhà:".
 */
export function apDungVaiGoiY(
  transcript: string,
  goiYTheoLuot?: Record<number, string>
): { transcriptMoi: string; soDongDaGan: number } {
  if (!transcript) return { transcriptMoi: transcript || "", soDongDaGan: 0 };

  let luot = 0;
  let soDongDaGan = 0;
  const cacDong = transcript.split("\n").map((dong) => {
    if (!dong.trim()) return dong;
    luot += 1;

    // Bảo toàn tuyệt đối mọi dòng đã gán vai
    if (DONG_DA_GAN_RE.test(dong)) return dong;

    const mChuaGan = dong.match(/^\s*(chưa rõ vai|người nói\s+\d+)\s*:/i);
    if (!mChuaGan) return dong;

    const vaiTuMap = chuanHoaVaiGoiY(goiYTheoLuot?.[luot]);
    const vaiHeuristic = vaiTuMap ? null : goiYVaiTuVanBanLuot(dong).vaiGoiY;
    const vaiChon = vaiTuMap || vaiHeuristic;
    if (!vaiChon) return dong;

    const noiDung = dong.slice(mChuaGan[0].length).trim();
    soDongDaGan += 1;
    return `${vaiChon}: ${noiDung}`;
  });

  return {
    transcriptMoi: cacDong.join("\n"),
    soDongDaGan,
  };
}

const LY_DO: Record<string, string> = {
  pyannote_chua_cau_hinh: "dịch vụ chưa được cấu hình tách người nói",
  pyannote_python_khong_co: "không tìm thấy môi trường Python có pyannote",
  pyannote_chua_cai: "môi trường pyannote chưa cài đủ thư viện",
  mo_hinh_khong_nap_duoc: "chưa nạp được mô hình tách người nói (chưa tải về máy hoặc chưa có quyền tải)",
  pyannote_vuot_tran_ram: "tách người nói dùng quá trần RAM nên đã bị dừng",
  pyannote_qua_thoi_gian: "tách người nói chạy quá thời gian cho phép",
  pyannote_khong_thay_ai_noi: "máy tách không nghe ra ai nói",
  pyannote_khong_ra_ket_qua: "máy tách chạy xong nhưng không ghi kết quả",
  tach_nguoi_noi_loi: "máy tách gặp lỗi khi chạy",
};

/** Câu báo cho người dùng: máy đã tách người nói chưa, và vai vẫn phải gán tay. */
export function moTaTach(tach?: ThongTinTach | null): string {
  if (tach?.tach_that) {
    const n = tach.so_nguoi_noi || 1;
    return n >= 2
      ? `Máy đã tách ${n} người nói theo giọng, nhưng không biết ai là bác sĩ: chọn vai cho từng người nói, rồi đọc lại từng dòng.`
      : "Máy chỉ nghe ra một người nói. Nếu cuộc khám có nhiều người, gán vai từng dòng.";
  }
  if (tach?.lui_ve) {
    const lyDo = (tach.loi && LY_DO[tach.loi]) || tach.loi || "không rõ lý do";
    return `Chưa tách được người nói: ${lyDo}. Mỗi đoạn để “Chưa rõ vai”, gán vai từng dòng.`;
  }
  return "Chưa bật tách người nói. Mỗi đoạn để “Chưa rõ vai”, gán vai từng dòng.";
}
