/**
 * Bản chép có tách người nói -> các dòng "Người nói N: …", và gán vai theo người nói.
 *
 * Máy tách người nói theo GIỌNG (pyannote chạy tại chỗ), không biết ai là bác sĩ. Mỗi người nói
 * chỉ mang số thứ tự ("Người nói 1" là người cất tiếng trước). Vai Bác sĩ / Bệnh nhân / Người nhà
 * do người dùng gán; còn dòng "Người nói N" thì App chặn tạo bản nháp, như với "Chưa rõ vai".
 */

export type DoanChep = { speaker_id?: string | null; text_original?: string | null };
export type ThongTinTach = {
  phuong_phap?: string;
  tach_that?: boolean;
  so_nguoi_noi?: number;
  loi?: string;
  lui_ve?: boolean;
  bo_qua?: boolean;
};

const NHAN_RE = /^\s*người nói\s+(\d+)\s*:/i;

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
