/**
 * Kiểm bộ luật ẩn danh cho tra cứu. Chạy: npx tsx may-chu/tro-ly/an-danh.test.ts  (trong thư mục web/)
 */
import assert from "node:assert/strict";
import { MUC_CHO_PHEP, chuoiGuiRa, kiemCauHoi, lamSachDong, nhomTuoi, xayCaAnDanh } from "./an-danh";

// 1. nhóm tuổi và các ranh giới
{
  assert.equal(nhomTuoi(0), "sơ sinh");
  assert.equal(nhomTuoi(1), "trẻ em");
  assert.equal(nhomTuoi(7), "trẻ em");
  assert.equal(nhomTuoi(15), "trẻ em");
  assert.equal(nhomTuoi(16), "người lớn");
  assert.equal(nhomTuoi(40), "người lớn");
  assert.equal(nhomTuoi(64), "người lớn");
  assert.equal(nhomTuoi(65), "cao tuổi");
  assert.equal(nhomTuoi(70), "cao tuổi");
}

// 2. câu hỏi có danh tính phải bị chặn (Review Focus 1)
{
  const chan = [
    "chị Lan đau đầu ba ngày",
    "gọi 0912 345 678",
    "sinh ngày 12/10/1980",
    "khám ngày 12 tháng 10",
    "ở số 5 đường Láng",
    "bệnh nhân Nguyễn Văn A",
    "Nguyễn Văn An bị sốt",
    "email abc@x.vn",
    "CCCD 012345678901",
    "bác sĩ Hoa kê thuốc gì",
    "tên là Minh",
  ];
  for (const c of chan) {
    const r = kiemCauHoi(c);
    assert.equal(r.ok, false, `phải chặn: ${c}`);
  }
  const qua = [
    "đau đầu ba ngày kèm sốt, dùng Augmentin 625 mg có phù hợp không",
    "trẻ 3 tuổi sốt cao co giật nên xử trí thế nào",
    "huyết áp 150/95 ở người cao tuổi nên bắt đầu thuốc nào",
    "liều amoxicillin 500 mg ngày 3 lần cho người lớn",
  ];
  for (const c of qua) {
    const r = kiemCauHoi(c);
    assert.equal(r.ok, true, `phải cho qua: ${c}`);
    if (r.ok) assert.equal(r.cau, c.replace("3 tuổi", "(trẻ em)"), "tuổi chính xác đổi thành nhóm tuổi");
  }
  const rong = kiemCauHoi("   ");
  assert.equal(rong.ok, false);
}

// 3. lamSachDong: bỏ tiền tố chủ thể, giữ nội dung có dấu hai chấm, loại dòng còn danh tính
{
  assert.equal(lamSachDong("bà Hoa: đau đầu (hôm qua)", "bà Hoa"), "đau đầu (hôm qua)");
  assert.equal(lamSachDong("bệnh nhân: ho khan"), "ho khan");
  assert.equal(lamSachDong("huyết áp: 120/80 mmHg"), "huyết áp: 120/80 mmHg", "không cắt nội dung có dấu hai chấm");
  assert.equal(lamSachDong("đau bụng từ 12/10/2026"), "đau bụng từ");
  assert.equal(lamSachDong("bệnh nhân: gọi 0912345678 khi cần"), null);
  assert.equal(lamSachDong("mẹ: chị Lan nói bé sốt"), null);
  assert.equal(lamSachDong("   "), null);
}

// 4. xayCaAnDanh: danh sách cho phép theo mục
{
  assert.equal(MUC_CHO_PHEP.length, 7);
  const ca = xayCaAnDanh(
    [
      { text: "bà Hoa: đau đầu (hôm qua)", section: "BỆNH SỬ HIỆN TẠI", subject: "bà Hoa" },
      { text: "bà: nổi hạch cổ", section: "KHÁM LÂM SÀNG" },
      { text: "bà: nghề giáo viên ở Hà Nội", section: "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI" },
      { text: "bà: tái khám ngày 20/11", section: "KẾ HOẠCH ĐIỀU TRỊ" },
      { text: "bà: không sốt", section: "BỆNH SỬ HIỆN TẠI", negated: true },
      { text: "bà: nghi viêm xoang", section: "CHẨN ĐOÁN", certainty: "nghi ngờ" },
      { text: "bà: amoxicillin 500 mg, uống", section: "THUỐC ĐANG DÙNG", drug: "amoxicillin 500 mg" },
      { text: "bà: dị ứng penicillin", section: "DỊ ỨNG" },
      { text: "  ", section: "LÝ DO KHÁM BỆNH" },
    ],
    { tuoi: 34, gioi: "Nữ", coThai: false },
  );
  assert.deepEqual(ca.dong, [
    "đau đầu (hôm qua)",
    "nổi hạch cổ",
    "KHÔNG CÓ: không sốt",
    "nghi ngờ: nghi viêm xoang",
    "thuốc: amoxicillin 500 mg",
    "dị ứng penicillin",
  ]);
  assert.equal(ca.soBo.muc_khong_cho_phep, 2);
  assert.equal(ca.soBo.rong, 1);
  assert.equal(ca.nhomTuoi, "người lớn");
  assert.equal(ca.gioi, "nữ");
  assert.equal(ca.coThai, false);
}

// 5. mệnh đề mang trích dẫn, chủ thể cụ thể, số lượt: chữ trong đó không được đi ra (Review Focus 2)
{
  const vao: any = {
    text: "bà: ho kéo dài",
    section: "BỆNH SỬ HIỆN TẠI",
    quotes: ["tôi là Nguyễn Văn An ở Cầu Giấy ho mãi"],
    evidenceTurns: [3],
    subject: "Nguyễn Văn An",
    time: "từ ngày 3/9",
  };
  const ca = xayCaAnDanh([vao], {});
  const s = chuoiGuiRa(ca, "ho kéo dài nên làm gì");
  assert.ok(!s.includes("Nguyễn Văn An"));
  assert.ok(!s.includes("Cầu Giấy"));
  assert.ok(!s.includes("3/9"));
  assert.ok(s.includes("ho kéo dài"));
}

// 6. tên và số điện thoại nhét vào dòng cho phép: dòng bị bỏ, không đi ra
{
  const ca = xayCaAnDanh(
    [
      { text: "bệnh nhân: ho, liên hệ 0912345678", section: "BỆNH SỬ HIỆN TẠI" },
      { text: "bệnh nhân: sốt do chị Lan chăm", section: "BỆNH SỬ HIỆN TẠI" },
      { text: "bệnh nhân: đau họng", section: "BỆNH SỬ HIỆN TẠI" },
    ],
    {},
  );
  assert.equal(ca.soBo.con_danh_tinh, 2);
  const s = chuoiGuiRa(ca, "đau họng kéo dài");
  assert.ok(!s.includes("0912345678"));
  assert.ok(!s.includes("Lan"));
  assert.ok(s.includes("đau họng"));
}

// 7. tuổi chính xác không bao giờ đi ra, chỉ nhóm tuổi
{
  const ca = xayCaAnDanh([{ text: "bệnh nhân: sốt", section: "LÝ DO KHÁM BỆNH" }], { tuoi: 34, gioi: "nam", coThai: null });
  const s = chuoiGuiRa(ca, "sốt");
  assert.ok(s.includes("người lớn"));
  assert.ok(!s.includes("34"));
  assert.ok(s.includes("nam"));
  assert.ok(!s.includes("thai"), "không nói gì về thai khi không biết");
  const ca2 = xayCaAnDanh([], { tuoi: 0, gioi: "female", coThai: true });
  assert.equal(ca2.gioi, "nữ");
  assert.ok(chuoiGuiRa(ca2, "x").includes("có thai"));
  const ca3 = xayCaAnDanh([], { gioi: "khác" });
  assert.equal(ca3.gioi, null);
}

// 8. rà soát độc lập 24/11: kẽ hở danh tính và chặn nhầm câu y khoa
{
  const chan = [
    "sinh năm 1985 bị ho",
    "sinh ngày 12.10.1985",
    "ngày khám 1985-10-12",
    "gọi 0912 - 345 - 678",
    "số (028) 3822 1234",
    "khám ngày 5 tháng 3",
    "ÔNG NGUYỄN VĂN A bị sốt",
    "tên Lan đau đầu",
    "mẹ Lan bị sốt",
    "bệnh nhân Trương Minh ho",
    "BHYT số DN4010123456789",
  ];
  for (const c of chan) assert.equal(kiemCauHoi(c).ok, false, `phải chặn: ${c}`);
  const qua = [
    "đau 7/10 theo thang VAS có nên dùng giảm đau",
    "uống 1/2 viên paracetamol mỗi lần có được không",
    "tiêm đường IV/IM liều bao nhiêu",
    "BHYT có chi trả thuốc này không",
    "bệnh nhân Nữ có thai ho kéo dài",
    "bệnh nhân Covid sốt kéo dài nên theo dõi gì",
    "huyết áp 150/95 ở người cao tuổi",
  ];
  for (const c of qua) assert.equal(kiemCauHoi(c).ok, true, `không được chặn nhầm: ${c}`);
  const t = kiemCauHoi("bé 6 tháng tuổi sốt và người 45 tuổi ho");
  assert.ok(t.ok && !/\d+\s*(tháng )?tuổi/.test(t.cau) && t.cau.includes("(sơ sinh)") && t.cau.includes("(người lớn)"), JSON.stringify(t));
  assert.equal(lamSachDong("uống 1/2 viên mỗi lần"), "uống 1/2 viên mỗi lần", "phân số không bị coi là ngày rồi xoá");
  // người nhà không bị gộp thành người bệnh
  const ca = xayCaAnDanh([{ text: "mẹ: dị ứng penicillin", section: "DỊ ỨNG", subject: "mẹ" }], {});
  assert.deepEqual(ca.dong, ["người nhà: dị ứng penicillin"]);
}

console.log("an-danh.test.ts: tất cả đều qua");
