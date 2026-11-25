import test from "node:test";
import assert from "node:assert/strict";
import { khoangPhatLaiLuot, phanTichVungMoAsr } from "./asrHighlight";
import { taoPhieuSbar, tachMucHis } from "./sbar";
import { trichNguCanhChoTroLy } from "./nguCanhTroLy";
import { quetRadarCoDo } from "./radarCoDo";
import { phatHienMauThuanXuyenLanKham } from "./doiChieuLanKham";
import type { Proposition } from "../components/VerificationView";
import type { Session } from "../types";

const taoProp = (p: Partial<Proposition> & { id: number; text: string; section: string }): Proposition => ({
  status: "than",
  evidenceTurns: [1],
  quotes: [p.text],
  ...p,
});

test("asrHighlight: phat hien so lieu co don vi, phu dinh tieng Viet va khoang phat lai", () => {
  const segs = [
    { luot: 2, start_s: 4.2, end_s: 7.4, lowConf: true },
    { luot: 3, start_s: Number.NaN, end_s: 5.0 },
    { luot: 4, start_s: 5.0, end_s: Number.POSITIVE_INFINITY },
    { luot: 5, start_s: 6.0, end_s: 5.0 },
  ];
  const r = phanTichVungMoAsr(
    { text: "Uống Metformin 500 mg, chưa từng sốt", negated: false, evidenceTurns: [2] },
    segs
  );
  assert.equal(r.coSoLieu, true);
  assert.equal(r.coPhuDinh, true);
  assert.equal(r.doTinCayThap, true);
  assert.ok(r.nhan?.includes("ASR mờ"));

  // Số không phải liều ("típ 2") không bị gắn nhầm số/liều
  const rTip2 = phanTichVungMoAsr({ text: "Đái tháo đường típ 2", negated: false, evidenceTurns: [1] }, segs);
  assert.equal(rTip2.coSoLieu, false);

  assert.deepEqual(khoangPhatLaiLuot(2, segs), { start_s: 3.7, end_s: 7.9 });
  assert.equal(khoangPhatLaiLuot(3, segs), null);
  assert.equal(khoangPhatLaiLuot(4, segs), null);
  assert.equal(khoangPhatLaiLuot(5, segs), null);
  assert.equal(khoangPhatLaiLuot(99, segs), null);
});

test("sbar & HIS: xu ly TOM TAT, CAN LAM SANG, bo menh de va sua/giu", () => {
  const props: Proposition[] = [
    taoProp({ id: 1, section: "LÝ DO KHÁM BỆNH", text: "Đau đầu chóng mặt 2 ngày" }),
    taoProp({ id: 2, section: "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI", text: "Bố tăng huyết áp" }),
    taoProp({ id: 3, section: "TÓM TẮT", text: "Hội chứng tăng huyết áp" }),
    taoProp({ id: 4, section: "CẬN LÂM SÀNG", text: "Creatinin 1.1 mg/dL" }),
    taoProp({ id: 5, section: "ĐƠN THUỐC", text: "Amlodipin 5 mg ngày 1 viên" }),
    taoProp({ id: 6, section: "KHÁM THỰC THỂ", text: "Tim đều 80 l/p" }),
    taoProp({ id: 7, section: "KHÁM LÂM SÀNG", text: "Câu bị bác sĩ bỏ" }),
  ];
  // Mệnh đề 5 từng sửa nhưng bác sĩ bấm lại "giu" -> phải dùng p.text gốc
  const sbar = taoPhieuSbar(
    props,
    { 7: "bo", 5: "giu" },
    { 5: "Amlodipin 10 mg (đã hủy sửa)" },
    "BN-001"
  );
  assert.equal(sbar.situation.length, 1);
  assert.equal(sbar.background.length, 1);
  assert.equal(sbar.assessment.length, 3); // TÓM TẮT + CẬN LÂM SÀNG + KHÁM THỰC THỂ
  assert.equal(sbar.recommendation[0], "Amlodipin 5 mg ngày 1 viên");
  assert.ok(!sbar.vanBan.includes("Câu bị bác sĩ bỏ"));

  const his = tachMucHis(props, { 7: "bo", 5: "giu" }, { 5: "Amlodipin 10 mg" });
  assert.equal(his.find((m) => m.nhan === "Lý do vào viện")?.noiDung, "Đau đầu chóng mặt 2 ngày");
  assert.equal(his.find((m) => m.nhan === "Khám lâm sàng")?.noiDung, "Creatinin 1.1 mg/dL; Tim đều 80 l/p");
  assert.equal(his.find((m) => m.nhan === "Chẩn đoán")?.noiDung, "Hội chứng tăng huyết áp");
  assert.equal(his.find((m) => m.nhan === "Hướng xử trí & Đơn thuốc")?.noiDung, "Amlodipin 5 mg ngày 1 viên");
});

test("nguCanhTroLy: Unicode 'đang bầu', phu dinh thai ky, tuoi 0 & >120, khong lo PII", () => {
  const nc1 = trichNguCanhChoTroLy({
    patient: { id: "p1", name: "Nguyen Thi A", identifier: "BN1", dob: "1996-05-10", gender: "Nữ" },
    propositions: [taoProp({ id: 1, section: "BỆNH SỬ HIỆN TẠI", text: "Bệnh nhân đang bầu tuần thứ 12" })],
  });
  assert.equal(nc1.gioi, "nữ");
  assert.equal(nc1.coThai, true);
  assert.equal((nc1 as Record<string, unknown>).name, undefined);
  assert.equal((nc1 as Record<string, unknown>).dob, undefined);

  // Phủ định trong text dù thiếu negated=true
  const nc2 = trichNguCanhChoTroLy({
    contextNotes: "Nữ, 30 tuổi, chưa từng mang thai, test thai âm tính",
    propositions: [taoProp({ id: 2, section: "BỆNH SỬ HIỆN TẠI", text: "Không mang thai", negated: false })],
  });
  assert.equal(nc2.tuoi, 30);
  assert.equal(nc2.coThai, undefined);

  // Tuổi biên 0 (sơ sinh) và > 120 (bị loại)
  const nc0 = trichNguCanhChoTroLy({ contextNotes: "Trẻ 0 tuổi, nam" });
  assert.equal(nc0.tuoi, 0);
  assert.equal(nc0.gioi, "nam");
  const ncOver = trichNguCanhChoTroLy({ contextNotes: "150 tuổi" });
  assert.equal(ncOver.tuoi, undefined);
});

test("radarCoDo: phan biet 'female' vs 'Nam', gioi han 2 goi y va danh dau da hoi", () => {
  // 'female' KHÔNG bị nhận nhầm thành 'male'
  const rFemale = quetRadarCoDo("Đau bụng dưới nhiều, kê ibuprofen giảm đau", "female");
  assert.equal(rFemale.length, 2);
  assert.equal(rFemale[0].id, "thai_ky");
  assert.equal(rFemale[0].daHoi, false);

  // 'Nam' bỏ qua cờ đỏ thai kỳ nhưng vẫn hiện loét dạ dày NSAID
  const rNam = quetRadarCoDo("Đau bụng dưới, kê ibuprofen", "Nam");
  assert.equal(rNam.some((x) => x.id === "thai_ky"), false);
  assert.equal(rNam.some((x) => x.id === "loet_da_day_nsaid"), true);

  // Tự đánh dấu đã hỏi
  const rAsked = quetRadarCoDo("Nữ đau bụng dưới. BS: Chị có đang mang thai không? BN: Không có thai", "Nữ");
  assert.equal(rAsked.find((x) => x.id === "thai_ky")?.daHoi, true);
});

test("doiChieuLanKham: phat hien mau thuan di ung, bo qua menh de da 'bo' va dinh chinh phu dinh", () => {
  const mkSession = (id: string, date: string, props: Proposition[], duyet?: Session["duyet"]): Session => ({
    id,
    patientIdentifier: "BN-999",
    patientSubtitle: "Nữ, 50 tuổi",
    date,
    time: "09:00",
    language: "vi",
    durationSeconds: 120,
    isRecording: false,
    transcript: "",
    tabs: [],
    activeTabId: "",
    duyet,
    note: { content: "", transcript: "", needsConfirmCount: 0, propositions: props, questions: [] },
  });

  // Case 1: Mâu thuẫn thật
  const caCu = mkSession("s1", "10/10/2026", [
    taoProp({ id: 1, section: "DỊ ỨNG", text: "Dị ứng Amoxicillin nổi mề đay", negated: false }),
    taoProp({ id: 2, section: "TIỀN SỬ BỆNH", text: "Đái tháo đường típ 2", negated: false }),
  ]);
  const caMoi = mkSession("s2", "24/11/2026", [
    taoProp({ id: 3, section: "DỊ ỨNG", text: "Không dị ứng thuốc nào", negated: true }),
    taoProp({ id: 4, section: "TIỀN SỬ BỆNH", text: "Không bị đái tháo đường", negated: true }),
  ]);
  const cb1 = phatHienMauThuanXuyenLanKham(caMoi, [caCu, caMoi]);
  assert.equal(cb1.length, 2);
  assert.equal(cb1[0].loai, "di_ung");
  assert.equal(cb1[1].loai, "benh_nen_thuoc");

  // Case 2: Bác sĩ đã bấm "bo" ở ca cũ -> không báo mâu thuẫn giả
  const caCuBo = mkSession(
    "s1_bo",
    "10/10/2026",
    [taoProp({ id: 1, section: "DỊ ỨNG", text: "Dị ứng Amoxicillin", negated: false })],
    { khoa: "k", quyet: { 1: "bo" }, banSua: {} }
  );
  assert.equal(phatHienMauThuanXuyenLanKham(caMoi, [caCuBo, caMoi]).length, 0);

  // Case 3: Ca cũ có 2 mệnh đề dị ứng (sau đính chính phủ định) -> không báo giả
  const caCuDinhChinh = mkSession("s1_dc", "10/10/2026", [
    taoProp({ id: 1, section: "DỊ ỨNG", text: "Dị ứng Amoxicillin", negated: false }),
    taoProp({ id: 2, section: "DỊ ỨNG", text: "Chưa từng dị ứng thuốc", negated: true }),
  ]);
  assert.equal(phatHienMauThuanXuyenLanKham(caMoi, [caCuDinhChinh, caMoi]).length, 0);
});
