import assert from "node:assert/strict";
import test from "node:test";
import { anDanhChoNgoai, anDanhVanBanNgoai, khoiPhucPII, LoiConDanhTinh } from "./an-danh-ngoai";
import { lyDoDanhTinh } from "./tro-ly/an-danh";

/** [câu vào, các đoạn tuyệt đối không được còn sau khi che] */
const RO_RI: Array<[string, string[]]> = [
  ["Bà Hoa 67 tuổi đến khám vì đau ngực.", ["Hoa"]],
  ["bà Hoa kể đau ngực từ hôm qua", ["Hoa"]],
  ["Ông Nam bị ho 2 tuần.", ["Nam"]],
  ["Ông Nguyễn Văn Nam, 70 tuổi", ["Nguyễn Văn Nam", "Nam"]],
  ["Chị Lan nói con bị sốt", ["Lan"]],
  ["Anh Tuấn làm thợ xây", ["Tuấn"]],
  ["Bác sĩ Minh hỏi bệnh", ["Minh"]],
  ["67 tuổi, sinh ngày 12/03/1959", ["12/03/1959"]],
  ["sinh năm 1959, ở với con gái", ["1959"]],
  ["ngày sinh 5-7-1980", ["5-7-1980"]],
  ["sinh ngày 12 tháng 3 năm 1959", ["12 tháng 3", "1959"]],
  ["Nhà ở số 12 ngõ 45 Láng Hạ, Đống Đa", ["12", "45", "Láng Hạ", "Đống Đa"]],
  ["địa chỉ: 123 Nguyễn Trãi, phường 5, quận 5, TP HCM", ["123 Nguyễn Trãi", "phường 5", "quận 5"]],
  ["trú tại ngách 3/12 phố Vọng, Hai Bà Trưng", ["3/12", "Vọng", "Hai Bà Trưng"]],
  ["sống ở 45 đường Trần Hưng Đạo, Hoàn Kiếm", ["Trần Hưng Đạo", "Hoàn Kiếm"]],
  ["quê ở xã Yên Sở, huyện Hoàng Mai", ["Yên Sở", "Hoàng Mai"]],
  ["Số điện thoại 0912 345 678 của con trai", ["0912", "345 678"]],
  ["gọi 0912.345.678 khi cần", ["0912.345.678"]],
  ["sđt +84 912 345 678", ["912 345 678"]],
  ["liên hệ 0987654321", ["0987654321"]],
  ["máy bàn 024 3826 1234", ["3826 1234"]],
  ["Mã bệnh nhân 20261125 đã nhập viện", ["20261125"]],
  ["PID: 12345678", ["12345678"]],
  ["số hồ sơ BV-2026-00123", ["BV-2026-00123"]],
  ["CCCD 001203004567", ["001203004567"]],
  ["thẻ BHYT DN 4 01 0123456789", ["0123456789"]],
  ["email hoa.nguyen@gmail.com", ["hoa.nguyen@gmail.com"]],
  ["cháu tên là Minh đang học lớp 3 trường Kim Liên", ["Minh", "Kim Liên"]],
  ["cháu tên là minh, 8 tuổi", ["minh"]],
  ["tên tôi là Trần Thị Hoa", ["Trần Thị Hoa", "Hoa"]],
  ["họ và tên: Lê Văn Tám", ["Lê Văn Tám"]],
  ["bệnh nhân nguyễn văn an vào viện", ["nguyễn văn an"]],
  ["con gái là Ngọc học trường THCS Trưng Vương", ["Trưng Vương"]],
  ["làm ở công ty TNHH Hòa Phát", ["Hòa Phát"]],
  ["cụ 95 tuổi sống một mình", ["95 tuổi"]],
];

/** Câu lâm sàng không được bị đổi. */
const GIU_NGUYEN = [
  "Bệnh nhân đau ngực trái 3 ngày, huyết áp 140/90 mmHg.",
  "Tiền sử đái tháo đường type 2, dùng Metformin 500 mg x 2 lần/ngày.",
  "SpO2 96%, nhịp tim 88 lần/phút, nhiệt độ 37,5 độ.",
  "Nghi hội chứng Kawasaki, theo dõi thêm.",
  "Đường huyết lúc đói 7,8 mmol/L, HbA1c 8,2%.",
  "Đau mức 7/10, uống 1/2 viên Paracetamol.",
  "Mẹ bệnh nhân bị tăng huyết áp, bố mất vì nhồi máu cơ tim.",
  "Bác sĩ khuyên nghỉ ngơi, tái khám sau 1 tuần.",
  "Đường uống, ngày 3 lần sau ăn.",
  "Bà ngoại bị hen phế quản.",
  "BS: Chào bác, bác thấy trong người thế nào?",
  "BN: Tôi đau đầu 2 hôm nay, uống thuốc không đỡ.",
];

test("anDanhChoNgoai: che các định danh từng bị lộ, không còn dấu hiệu danh tính", () => {
  for (const [vao, cam] of RO_RI) {
    const kq = anDanhChoNgoai(vao);
    assert.equal(kq.ok, true, `phải che được: ${vao}`);
    if (!kq.ok) continue;
    for (const c of cam) assert.ok(!kq.van.includes(c), `còn lộ "${c}" trong: ${kq.van} (vào: ${vao})`);
    assert.equal(lyDoDanhTinh(kq.van), null, `còn dấu hiệu danh tính: ${kq.van}`);
    assert.equal(khoiPhucPII(kq.van, kq.bang), vao.normalize("NFC"), "khôi phục đúng nguyên văn");
  }
});

test("anDanhChoNgoai: không đổi câu lâm sàng thường", () => {
  for (const cau of GIU_NGUYEN) {
    const kq = anDanhChoNgoai(cau);
    assert.equal(kq.ok, true);
    if (kq.ok) assert.equal(kq.van, cau, `không được đổi: ${cau}`);
  }
});

test("anDanhChoNgoai: dùng chung một bảng cho nhiều đoạn, token không trùng", () => {
  const bang = new Map<string, string>();
  const a = anDanhChoNgoai("Bà Hoa đau ngực", bang);
  const b = anDanhChoNgoai("gọi 0912 345 678", bang);
  assert.ok(a.ok && b.ok);
  assert.equal(bang.size, 2);
  assert.equal(new Set(bang.keys()).size, 2);
});

test("fail closed: bộ kiểm còn thấy danh tính sau khi che thì từ chối, lỗi 422 rõ ràng", () => {
  const kq = anDanhChoNgoai("nội dung bất kỳ", new Map(), () => "ten_rieng");
  assert.equal(kq.ok, false);
  if (!kq.ok) assert.equal(kq.lyDo, "ten_rieng");
  const loi = new LoiConDanhTinh("ten_rieng");
  assert.equal(loi.status, 422);
  assert.equal(loi.code, "con_danh_tinh");
  assert.match(loi.message, /Không gửi ra mô hình ngoài/);
});

test("anDanhVanBanNgoai giữ tương thích: duyệt đối tượng/mảng lồng nhau", () => {
  const bang = new Map<string, string>();
  const ra = anDanhVanBanNgoai({ a: ["Ông Nam", 3], b: { c: "0912 345 678" } }, bang) as any;
  assert.doesNotMatch(JSON.stringify(ra), /Nam|0912/);
  assert.equal(ra.a[1], 3);
});
