/**
 * Máy tính lâm sàng. Mọi con số do công thức tính, không do mô hình ngôn ngữ. Mỗi công thức ghi
 * nguồn; kết quả chỉ để tham khảo, bác sĩ quyết định. Kiểm bằng `npx tsx src/lib/mayTinh.test.ts`.
 */

/** Creatinin huyết thanh: µmol/L → mg/dL (hệ số 88,4). */
export const creatininMgDl = (umolL: number) => umolL / 88.4;

/**
 * eGFR theo CKD-EPI 2021 (không dùng hệ số chủng tộc). Inker và cs., N Engl J Med 2021;385:1737–49.
 * eGFR = 142 × min(Scr/κ,1)^α × max(Scr/κ,1)^−1,200 × 0,9938^tuổi × 1,012 [nữ]
 * κ = 0,7 (nữ) / 0,9 (nam); α = −0,241 (nữ) / −0,302 (nam). Scr tính bằng mg/dL.
 */
export function egfrCkdEpi2021(scrMgDl: number, tuoi: number, nu: boolean) {
  const k = nu ? 0.7 : 0.9;
  const a = nu ? -0.241 : -0.302;
  const r = scrMgDl / k;
  return 142 * Math.pow(Math.min(r, 1), a) * Math.pow(Math.max(r, 1), -1.2) * Math.pow(0.9938, tuoi) * (nu ? 1.012 : 1);
}

/** Giai đoạn bệnh thận mạn theo eGFR (KDIGO 2012). */
export function giaiDoanEgfr(egfr: number) {
  if (egfr >= 90) return "G1 — bình thường hoặc cao";
  if (egfr >= 60) return "G2 — giảm nhẹ";
  if (egfr >= 45) return "G3a — giảm nhẹ đến vừa";
  if (egfr >= 30) return "G3b — giảm vừa đến nặng";
  if (egfr >= 15) return "G4 — giảm nặng";
  return "G5 — suy thận";
}

/**
 * Độ thanh thải creatinin theo Cockcroft–Gault (1976), mL/phút:
 * (140 − tuổi) × cân nặng (kg) / (72 × Scr mg/dL) × 0,85 [nữ]. Thường dùng để chỉnh liều thuốc.
 */
export function crclCockcroftGault(scrMgDl: number, tuoi: number, canNang: number, nu: boolean) {
  return ((140 - tuoi) * canNang) / (72 * scrMgDl) * (nu ? 0.85 : 1);
}

/** Chỉ số khối cơ thể, kg/m². */
export const bmi = (canNangKg: number, chieuCaoCm: number) => canNangKg / Math.pow(chieuCaoCm / 100, 2);

/**
 * Phân loại BMI cho người trưởng thành châu Á — WHO khu vực Tây Thái Bình Dương (2000),
 * ngưỡng Bộ Y tế Việt Nam đang dùng.
 */
export function phanLoaiBmiChauA(b: number) {
  if (b < 18.5) return "Thiếu cân";
  if (b < 23) return "Bình thường";
  if (b < 25) return "Thừa cân";
  if (b < 30) return "Béo phì độ I";
  return "Béo phì độ II";
}

/** Diện tích da theo Mosteller (1987), m² = √(chiều cao cm × cân nặng kg / 3600). */
export const bsaMosteller = (canNangKg: number, chieuCaoCm: number) => Math.sqrt((chieuCaoCm * canNangKg) / 3600);

/** Huyết áp động mạch trung bình, mmHg = (tâm thu + 2 × tâm trương) / 3. */
export const huyetApTrungBinh = (tamThu: number, tamTruong: number) => (tamThu + 2 * tamTruong) / 3;

/**
 * Liều theo cân nặng: tổng liều/ngày = mg/kg/ngày × kg, chia đều số lần. Có trần liều/ngày thì
 * không vượt trần, và báo là đã chạm trần.
 */
export function lieuTheoCanNang(mgKgNgay: number, canNangKg: number, soLan: number, tranMgNgay?: number) {
  const tinh = mgKgNgay * canNangKg;
  const chamTran = !!tranMgNgay && tinh > tranMgNgay;
  const ngay = chamTran ? tranMgNgay! : tinh;
  return { mgNgay: ngay, mgLan: ngay / soLan, chamTran, mgNgayTheoCongThuc: tinh };
}
