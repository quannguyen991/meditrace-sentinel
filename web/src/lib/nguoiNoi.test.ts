/**
 * Kiểm dòng lời thoại từ bản chép có tách người nói. Chạy: npx tsx src/lib/nguoiNoi.test.ts
 */
import assert from "node:assert/strict";
import {
  cacNguoiNoiChuaGan,
  dongTuDoan,
  ganVaiNguoiNoi,
  moTaTach,
  soNguoiNoiLonNhat,
} from "./nguoiNoi";

const doan = [
  { speaker_id: "speaker_1", text_original: "Chị ho bao lâu rồi?" },
  { speaker_id: "speaker_2", text_original: "Mười ngày. À không, hai tuần rồi ạ." },
  { speaker_id: "speaker_1", text_original: "  " },
  { speaker_id: "speaker_1", text_original: "Có sốt không?" },
];

// 1. Đã tách thật: nhãn "Người nói N", bỏ đoạn rỗng; chưa tách: "Chưa rõ vai".
assert.deepEqual(dongTuDoan(doan, { tach_that: true, so_nguoi_noi: 2 }), [
  "Người nói 1: Chị ho bao lâu rồi?",
  "Người nói 2: Mười ngày. À không, hai tuần rồi ạ.",
  "Người nói 1: Có sốt không?",
]);
assert.deepEqual(dongTuDoan(doan, { tach_that: false, lui_ve: true, loi: "mo_hinh_khong_nap_duoc" }), [
  "Chưa rõ vai: Chị ho bao lâu rồi?",
  "Chưa rõ vai: Mười ngày. À không, hai tuần rồi ạ.",
  "Chưa rõ vai: Có sốt không?",
]);
assert.deepEqual(dongTuDoan(doan, null).length, 3);

// 2. Tệp ghi âm thứ hai: đánh số tiếp, không trùng "Người nói 1" của tệp đầu.
const tepDau = dongTuDoan(doan, { tach_that: true }).join("\n");
assert.equal(soNguoiNoiLonNhat(tepDau), 2);
assert.equal(dongTuDoan([{ speaker_id: "speaker_1", text_original: "Dạ." }], { tach_that: true }, 2)[0], "Người nói 3: Dạ.");
assert.equal(soNguoiNoiLonNhat("Bác sĩ: chào\nChưa rõ vai: ừ"), 0);

// 3. Danh sách người nói chưa gán: đếm lượt, câu đầu làm ví dụ, số 12 không lẫn với số 1.
const loiThoai = tepDau + "\nNgười nói 12: Tôi là người nhà.";
assert.deepEqual(
  cacNguoiNoiChuaGan(loiThoai).map((x) => [x.so, x.soLuot, x.viDu]),
  [
    [1, 2, "Chị ho bao lâu rồi?"],
    [2, 1, "Mười ngày. À không, hai tuần rồi ạ."],
    [12, 1, "Tôi là người nhà."],
  ]
);

// 4. Gán vai theo người nói: mọi dòng của người đó, không đụng người 12 hay dòng đã gán.
const daGan = ganVaiNguoiNoi(loiThoai + "\n\nBệnh nhân: Vâng.", 1, "Bác sĩ");
assert.equal(
  daGan,
  "Bác sĩ: Chị ho bao lâu rồi?\nNgười nói 2: Mười ngày. À không, hai tuần rồi ạ.\nBác sĩ: Có sốt không?\n" +
    "Người nói 12: Tôi là người nhà.\n\nBệnh nhân: Vâng."
);
assert.deepEqual(cacNguoiNoiChuaGan(daGan).map((x) => x.so), [2, 12]);

// 5. Câu báo: nói rõ máy không biết ai là bác sĩ; mã lỗi đổi sang lời thường.
assert.match(moTaTach({ tach_that: true, so_nguoi_noi: 2 }), /không biết ai là bác sĩ/);
assert.match(moTaTach({ lui_ve: true, loi: "pyannote_vuot_tran_ram" }), /quá trần RAM/);
assert.match(moTaTach({ lui_ve: true, loi: "ma_la" }), /ma_la/);
assert.match(moTaTach(undefined), /^Chưa bật tách người nói/);

console.log("nguoiNoi: ổn");
