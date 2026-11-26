/**
 * Kiểm bộ luật ẩn danh cho tra cứu. Chạy: npx tsx may-chu/tro-ly/an-danh.test.ts  (trong thư mục web/)
 */
import assert from "node:assert/strict";
import { DANH_SACH_BENH_DANH_Y_KHOA, MUC_CHO_PHEP, chuoiGuiRa, kiemCauHoi, lamSachDong, nhomTuoi, xayCaAnDanh } from "./an-danh";

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

// 4. xayCaAnDanh: danh sách cho phép theo mục kèm tiền tố mục rõ ràng
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
    "[BỆNH SỬ HIỆN TẠI] đau đầu (hôm qua)",
    "[KHÁM LÂM SÀNG] nổi hạch cổ",
    "[BỆNH SỬ HIỆN TẠI] KHÔNG CÓ: không sốt",
    "[CHẨN ĐOÁN] nghi ngờ: nghi viêm xoang",
    "[THUỐC ĐANG DÙNG] amoxicillin 500 mg, uống",
    "[DỊ ỨNG] dị ứng penicillin",
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
  assert.deepEqual(ca.dong, ["[DỊ ỨNG] người nhà: dị ứng penicillin"]);
}

// 9. Vá P0: DỊ ỨNG kèm m.drug KHÔNG BAO GIỜ xóa m.text hay biến thành "thuốc: ..."
{
  const ca = xayCaAnDanh(
    [
      { text: "bệnh nhân: sốc phản vệ độ 3 với penicillin", section: "DỊ ỨNG", drug: "penicillin" },
      { text: "bệnh nhân: nổi mề đay toàn thân, khó thở", section: "DỊ ỨNG", drug: "ceftriaxone" },
      { text: "", section: "DỊ ỨNG", drug: "aspirin" },
      { text: "bệnh nhân: đang dùng amlodipin 5 mg buổi sáng", section: "THUỐC ĐANG DÙNG", drug: "amlodipin 5 mg" },
      { text: "bệnh nhân: uống thuốc", section: "THUỐC ĐANG DÙNG", drug: "metformin 500 mg gọi 0912345678" },
    ],
    { tuoi: 50, gioi: "nam" },
  );
  assert.deepEqual(ca.dong, [
    "[DỊ ỨNG] sốc phản vệ độ 3 với penicillin",
    "[DỊ ỨNG] nổi mề đay toàn thân, khó thở (ceftriaxone)",
    "[DỊ ỨNG] aspirin",
    "[THUỐC ĐANG DÙNG] đang dùng amlodipin 5 mg buổi sáng",
  ]);
  assert.equal(ca.soBo.con_danh_tinh, 1, "PII trong trường drug cũng phải bị chặn");
  const gui = chuoiGuiRa(ca, "chọn kháng sinh thay thế nào");
  assert.ok(!gui.includes("thuốc: penicillin"), "dị ứng không bao giờ biến thành thuốc đang dùng");
  assert.ok(gui.includes("[DỊ ỨNG] sốc phản vệ độ 3 với penicillin"));
  assert.ok(gui.includes("[DỊ ỨNG] nổi mề đay toàn thân, khó thở (ceftriaxone)"));
}

// 10. Vá P0: bắt họ tên chữ thường + địa chỉ chữ thường và whitelist bệnh danh viết hoa
{
  const chanChuThuong = [
    "tên là minh bị đau ngực",
    "họ tên nguyễn văn an sốt cao",
    "họ và tên: trần thị bích đau đầu",
    "bệnh nhân nguyễn văn hùng khó thở",
    "ông trần bình ho ra máu",
    "bà lê thị hoa chóng mặt",
    "anh phạm minh đau bụng",
    "chị hoàng lan sốt 3 ngày",
    "cháu vũ nam tiêu chảy",
    "bệnh nhân võ văn kiệt mệt",
    "ông đặng tuấn đau lưng",
    "bà bùi thu hà mất ngủ",
    "anh đỗ nam ho khan",
    "ông hồ tùng mậu sốt",
    "chị ngô phương lan buồn nôn",
    "bệnh nhân dương văn minh đau ngực",
    "bà lý thị mai tiểu buốt",
    "cháu huỳnh phúc sốt phát ban",
    "anh phan anh tuấn đau họng",
    "nguyễn văn nam đau thượng vị",
    "ở số nhà 12 đường giải phóng bị sốt",
    "nhà ở ngõ 68 cầu giấy ho kéo dài",
    "ngõ thái hà có ổ dịch sốt xuất huyết",
    "ngách 15/2 sốt cao",
    "cư trú phường bến nghé bị ho",
    "ở quận cầu giấy đau đầu",
    "ở huyện hoài đức sốt 4 ngày",
    "quê tỉnh nghệ an sốt rét",
    "ở thành phố đà nẵng ho nhiều",
    "ở thành phố hồ chí minh đau họng",
  ];
  for (const c of chanChuThuong) {
    const r = kiemCauHoi(c);
    assert.equal(r.ok, false, `phải chặn họ tên / địa chỉ chữ thường: ${c}`);
  }

  // Whitelist toàn bộ 21+ bệnh danh y khoa viết hoa (kể cả đứng ngay sau "bệnh nhân" / "cháu")
  const benhDanhCanQua = [
    "Parkinson",
    "Basedow",
    "Crohn",
    "Alzheimer",
    "Kawasaki",
    "Cushing",
    "Addison",
    "Marfan",
    "Wilson",
    "Wernicke",
    "Tourette",
    "Bell",
    "Raynaud",
    "Sjögren",
    "Behcet",
    "Graves",
    "Hashimoto",
    "Hodgkin",
    "Dengue",
    "Zika",
    "Whitmore",
  ];
  assert.ok(benhDanhCanQua.every((b) => DANH_SACH_BENH_DANH_Y_KHOA.includes(b)));
  for (const benh of benhDanhCanQua) {
    const cau1 = `bệnh nhân ${benh} cần lưu ý xét nghiệm và điều trị gì`;
    const cau2 = `phác đồ điều trị hội chứng ${benh} ở người lớn`;
    assert.equal(kiemCauHoi(cau1).ok, true, `không được chặn nhầm bệnh danh sau 'bệnh nhân': ${cau1}`);
    assert.equal(kiemCauHoi(cau2).ok, true, `không được chặn nhầm bệnh danh: ${cau2}`);
  }

  // Kiểm tra các từ đồng âm y khoa, chữ viết tắt y khoa và chỉ số có số đi liền không bị chặn nhầm
  const cauLamSangHopLe = [
    "bệnh nhân dương tính với cúm A nên dùng oseltamivir khi nào",
    "bệnh nhân hoàng đảm tắc mật cần siêu âm gì",
    "bệnh nhân tỉnh táo tiếp xúc tốt nhưng huyết áp tụt",
    "tràn dịch ngách sườn hoành hai bên trên X-quang ngực",
    "trạm y tế phường có xử trí ban đầu cơn hen cấp được không",
    "trạm y tế phường theo dõi huyết áp tại nhà bao lâu một lần",
    "bệnh viện huyện chuyển tuyến khi nào trong sốc sốt xuất huyết",
    "bệnh viện huyện thiếu huyết thanh kháng nọc rắn xử trí sao",
    "bệnh viện quận tiếp nhận ca ngộ độc cấp cần làm gì trước",
    "tên thuốc là gì khi cần đối kháng heparin",
    "bệnh nhân COPD đợt cấp nên dùng kháng sinh gì",
    "bệnh nhân STEMI thành trước xử trí tái tưới máu thế nào",
    "bệnh nhân NSTEMI nguy cơ cao chụp mạch vành khi nào",
    "bệnh nhân ARDS thông khí bảo vệ phổi cài đặt PEEP sao",
    "bệnh nhân NYHA III suy tim phân suất tống máu giảm dùng thuốc gì",
    "bệnh nhân HbA1c 9.2% cần phối hợp thuốc hạ đường huyết nào",
    "bệnh nhân SpO2 88% thở oxy kính mũi bao nhiêu lít/phút",
    "bệnh nhân THA kèm ĐTĐ típ 2 mục tiêu huyết áp bao nhiêu",
    "BN CKD giai đoạn 4 chỉnh liều kháng sinh thế nào",
  ];
  for (const c of cauLamSangHopLe) {
    assert.equal(kiemCauHoi(c).ok, true, `không được chặn nhầm câu lâm sàng hợp lệ: ${c}`);
  }

  // Bắt thêm các trường hợp PII chữ hoa toàn bộ, họ đa nghĩa đi sau danh xưng cá nhân, "bệnh nhân tên ...", và thành phố tỉnh lẻ chữ thường
  const chanBoSung = [
    "NGUYỄN MINH TUẤN sốt cao 3 ngày",
    "TRẦN HOÀI NAM đau ngực trái",
    "LÊ THU HÀ khó thở về đêm",
    "bệnh nhân tên minh sốt cao",
    "bệnh nhân tên nguyễn văn a ho kéo dài",
    "ông dương sốt cao",
    "bà lý ho nhiều",
    "anh hoàng đau ngực",
    "chị hồ khó thở",
    "bệnh nhân ở thành phố vinh sốt 3 ngày",
    "cư trú thành phố pleiku đau đầu",
    "ở thành phố mỹ tho tiêu chảy",
  ];
  for (const c of chanBoSung) {
    assert.equal(kiemCauHoi(c).ok, false, `phải chặn PII bổ sung: ${c}`);
  }
}

console.log("an-danh.test.ts: tất cả đều qua");
