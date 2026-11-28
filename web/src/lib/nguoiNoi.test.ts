/**
 * Kiểm dòng lời thoại từ bản chép có tách người nói & gợi ý vai Boost 1.
 * Chạy: npx tsx --test src/lib/nguoiNoi.test.ts
 */
import test from "node:test";
import assert from "node:assert/strict";
import {
  apDungVaiGoiY,
  cacNguoiNoiChuaGan,
  dongTuDoan,
  ganVaiNguoiNoi,
  goiYVaiTuDoan,
  goiYVaiTuVanBanLuot,
  moTaTach,
  soNguoiNoiLonNhat,
} from "./nguoiNoi";

const doan = [
  { speaker_id: "speaker_1", text_original: "Chị ho bao lâu rồi?" },
  { speaker_id: "speaker_2", text_original: "Mười ngày. À không, hai tuần rồi ạ." },
  { speaker_id: "speaker_1", text_original: "  " },
  { speaker_id: "speaker_1", text_original: "Có sốt không?" },
];

test("nguoiNoi: giữ nguyên toàn bộ hành vi dongTuDoan, cacNguoiNoiChuaGan, ganVaiNguoiNoi, moTaTach", () => {
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
});

test("Boost 1: goiYVaiTuDoan, goiYVaiTuVanBanLuot và apDungVaiGoiY không bao giờ ghi đè vai đã gán", () => {
  const goiY = goiYVaiTuDoan(doan);
  assert.equal(goiY.length, 3);
  assert.equal(goiY[0].vaiGoiY, "Bác sĩ");
  assert.equal(goiY[1].vaiGoiY, "Bệnh nhân");
  assert.equal(goiY[2].vaiGoiY, "Bác sĩ");

  assert.equal(goiYVaiTuVanBanLuot("Chưa rõ vai: Cháu nhà em bị sốt cao hai hôm nay").vaiGoiY, "Người nhà");
  assert.equal(goiYVaiTuVanBanLuot("Bác sĩ: Cháu nhà em bị sốt cao").vaiGoiY, null);

  const banDau = [
    "Bệnh nhân: Dòng này bác sĩ đã gán tay là Bệnh nhân dù có chữ bác sĩ kê đơn",
    "Chưa rõ vai: Chị ho bao lâu rồi?",
    "Người nói 2: Dạ tôi bị đau ngực ba ngày rồi ạ.",
    "Chưa rõ vai: Ừm.",
  ].join("\n");

  const { transcriptMoi, soDongDaGan } = apDungVaiGoiY(banDau);
  assert.equal(soDongDaGan, 2);
  assert.equal(
    transcriptMoi,
    [
      "Bệnh nhân: Dòng này bác sĩ đã gán tay là Bệnh nhân dù có chữ bác sĩ kê đơn",
      "Bác sĩ: Chị ho bao lâu rồi?",
      "Bệnh nhân: Dạ tôi bị đau ngực ba ngày rồi ạ.",
      "Chưa rõ vai: Ừm.",
    ].join("\n")
  );
});

import { goiYVaiXenKe } from "./nguoiNoi";

test("xen_ke_tu_moc_bac_si_khi_chua_tach_giong", () => {
  const ds = [
    { luot: 1, vaiGoiY: "Bác sĩ" as const, lyDo: "chào bác" },
    { luot: 2, vaiGoiY: null, lyDo: null },
    { luot: 3, vaiGoiY: null, lyDo: null },
    { luot: 4, vaiGoiY: null, lyDo: null },
  ];
  const kq = goiYVaiXenKe(ds);
  assert.deepEqual(kq.map((g) => g.vaiGoiY), ["Bác sĩ", "Bệnh nhân", "Bác sĩ", "Bệnh nhân"]);
  assert.equal(kq[0].lyDo, "chào bác");
  assert.match(kq[1].lyDo || "", /xen kẽ/i);
});

test("xen_ke_lui_ve_truoc_moc_dau_tien_va_giu_goi_y_co_san", () => {
  const ds = [
    { luot: 1, vaiGoiY: null, lyDo: null },
    { luot: 2, vaiGoiY: "Bệnh nhân" as const, lyDo: "tôi bị ho" },
    { luot: 3, vaiGoiY: "Người nhà" as const, lyDo: "mẹ tôi" },
    { luot: 4, vaiGoiY: null, lyDo: null },
  ];
  const kq = goiYVaiXenKe(ds);
  assert.deepEqual(kq.map((g) => g.vaiGoiY), ["Bác sĩ", "Bệnh nhân", "Người nhà", "Bác sĩ"]);
});

test("khong_co_moc_nao_thi_khong_doan", () => {
  const ds = [
    { luot: 1, vaiGoiY: null, lyDo: null },
    { luot: 2, vaiGoiY: null, lyDo: null },
  ];
  assert.deepEqual(goiYVaiXenKe(ds).map((g) => g.vaiGoiY), [null, null]);
});
