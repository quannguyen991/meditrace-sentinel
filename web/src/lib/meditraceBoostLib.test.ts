/**
 * Bộ kiểm thử đơn vị cho MediTrace Boost (Boost 1, 2B, 4C, 7, 9B, 11, 12).
 * Chạy: npx tsx --test src/lib/meditraceBoostLib.test.ts src/lib/nguoiNoi.test.ts
 */
import test from "node:test";
import assert from "node:assert/strict";
import { apDungVaiGoiY, goiYVaiTuDoan, goiYVaiTuVanBanLuot } from "./nguoiNoi";
import { xayNguCanhChoTaoHoSo } from "./nguCanhTroLy";
import { bienDichBieuMauPhapLyTaiCho, DANH_SACH_MAU_BIEN_DICH_TAI_CHO } from "./bieuMauPhapLyOffline";
import { xuatGoiFhirVaBhytHieuLuc } from "./taiBienDichHieuLuc";
import { taoDaiTomTatTruocKham, trichNhiemVuTuCacCaKham } from "./trichNhiemVuVaTomTat";
import type { Session } from "../types";
import type { NoteMeta } from "../components/VerificationView";

test("Boost 1: apDungVaiGoiY chỉ cập nhật Chưa rõ vai / Người nói N và giữ nguyên dòng đã gán vai", () => {
  const doan = [
    {
      speaker_id: "speaker_1",
      text_original: "Bác đau ngực bao lâu rồi?",
      suggested_role: "Bác sĩ",
      suggested_role_reason: "Câu hỏi khai thác triệu chứng",
    },
    {
      speaker_id: "speaker_2",
      text_original: "Dạ tôi bị đau ngực hai ngày rồi ạ.",
    },
    {
      speaker_id: "speaker_3",
      text_original: "Tôi là người nhà đưa bác đi khám.",
    },
  ];

  const goiY = goiYVaiTuDoan(doan);
  assert.equal(goiY[0].vaiGoiY, "Bác sĩ");
  assert.equal(goiY[1].vaiGoiY, "Bệnh nhân");
  assert.equal(goiY[2].vaiGoiY, "Người nhà");

  const mapLuot: Record<number, string> = {};
  for (const g of goiY) {
    if (g.vaiGoiY) mapLuot[g.luot] = g.vaiGoiY;
  }

  const transcriptGoc = [
    "Bệnh nhân: Câu đầu bác sĩ đã gán tay là Bệnh nhân",
    "Người nói 2: Dạ tôi bị đau ngực hai ngày rồi ạ.",
    "Chưa rõ vai: Tôi là người nhà đưa bác đi khám.",
    "Chưa rõ vai: Vâng.",
  ].join("\n");

  const { transcriptMoi, soDongDaGan } = apDungVaiGoiY(transcriptGoc, { 2: "Bệnh nhân", 3: "Người nhà" });
  assert.equal(soDongDaGan, 2);
  const dong = transcriptMoi.split("\n");
  assert.equal(dong[0], "Bệnh nhân: Câu đầu bác sĩ đã gán tay là Bệnh nhân");
  assert.equal(dong[1], "Bệnh nhân: Dạ tôi bị đau ngực hai ngày rồi ạ.");
  assert.equal(dong[2], "Người nhà: Tôi là người nhà đưa bác đi khám.");
  assert.equal(dong[3], "Chưa rõ vai: Vâng.");

  assert.equal(goiYVaiTuVanBanLuot("Người nói 1: Khám thấy phổi có ran ẩm hai đáy").vaiGoiY, "Bác sĩ");
});

test("Boost 9B: xayNguCanhChoTaoHoSo bóc tách đầy đủ 14+ xét nghiệm trọng yếu + tháng tuổi & chiều cao Nhi khoa", () => {
  const payload = xayNguCanhChoTaoHoSo({
    sessionId: "ca-nhi-01",
    patientIdentifier: "Bé Nguyễn Minh Khôi",
    patientSubtitle: "Bé trai · 8 tháng tuổi · Cân nặng 8,5 kg · Chiều cao 71 cm",
    tabs: [
      {
        id: "tab-ctx",
        title: "Ngữ cảnh",
        type: "context",
        content: [
          "Creatinin: 62 umol/L, eGFR: 85, HbA1c: 5.4, Đường huyết: 5,2",
          "Kali: 6,3, Na+: 132, Troponin T: 0.45",
          "WBC: 18,5, Hb: 6.8, Tiểu cầu: 95, Ure: 11.2",
          "AST: 120, ALT: 145, CRP: 68.4, INR: 2,6",
        ].join("\n"),
      },
    ],
  });

  const tt = payload.thong_tin_benh_nhan || {};
  assert.equal(tt.ho_ten, "Bé Nguyễn Minh Khôi");
  assert.equal(tt.thang_tuoi, 8);
  assert.equal(tt.tuoi, 0);
  assert.equal(tt.gioi_tinh, "nam");
  assert.equal(tt.can_nang_kg, 8.5);
  assert.equal(tt.chieu_cao_cm, 71);

  const xn = payload.du_lieu_xet_nghiem || {};
  assert.equal(xn.creatinine_umol_l, 62);
  assert.equal(xn.egfr, 85);
  assert.equal(xn.hba1c, 5.4);
  assert.equal(xn.glucose_mmol_l, 5.2);
  assert.equal(xn.kali, 6.3);
  assert.equal(xn.na, 132);
  assert.equal(xn.troponin, 0.45);
  assert.equal(xn.wbc, 18.5);
  assert.equal(xn.hb, 6.8);
  assert.equal(xn.plt, 95);
  assert.equal(xn.urea, 11.2);
  assert.equal(xn.ast, 120);
  assert.equal(xn.alt, 145);
  assert.equal(xn.crp, 68.4);
  assert.equal(xn.inr, 2.6);
});

test("Boost 7 & 12: bienDichBieuMauPhapLyTaiCho biên dịch đủ 8 biểu mẫu offline, tách người nhà, loại bỏ 'bo' và kiểm trần BHXH 30 ngày", () => {
  const noteMau: NoteMeta = {
    content: "Bản nháp",
    needsConfirmCount: 1,
    questions: [],
    caseId: "HS-2026-09",
    clinicalSafety: {
      bhyt_icd10: {
        ma_icd10_chinh: { ma_icd10: "J18.9", ten_benh_byt: "Viêm phổi" },
        ma_icd10_kem_theo: [],
      },
    },
    propositions: [
      {
        id: 1,
        section: "LÝ DO KHÁM BỆNH",
        text: "Sốt cao và ho đờm 4 ngày",
        status: "than",
        subject: "bệnh nhi",
        evidenceTurns: [1, 2],
        quotes: [],
      },
      {
        id: 2,
        section: "TIỀN SỬ GIA ĐÌNH",
        text: "Bố bị hen phế quản mạn tính",
        status: "than",
        subject: "bố",
        evidenceTurns: [3],
        quotes: [],
      },
      {
        id: 3,
        section: "DỊ ỨNG",
        text: "Dị ứng Penicillin nổi mề đay",
        status: "than",
        subject: "bệnh nhân",
        evidenceTurns: [4],
        quotes: [],
      },
      {
        id: 4,
        section: "ĐƠN THUỐC",
        text: "Cefuroxim 250mg uống ngày 2 lần",
        drug: "Cefuroxim",
        status: "than",
        subject: "bệnh nhân",
        evidenceTurns: [6],
        quotes: [],
      },
      {
        id: 5,
        section: "KẾ HOẠCH ĐIỀU TRỊ",
        text: "Cho nghỉ làm 45 ngày tại nhà",
        status: "than",
        subject: "bệnh nhân",
        evidenceTurns: [7],
        quotes: [],
      },
      {
        id: 6,
        section: "ĐƠN THUỐC",
        text: "Aspirin 81mg không phù hợp đã bị bác sĩ bỏ",
        drug: "Aspirin",
        status: "than",
        subject: "bệnh nhân",
        evidenceTurns: [8],
        quotes: [],
      },
      {
        id: 7,
        section: "BỆNH SỬ",
        text: "Nghi có cơn co giật chưa rõ",
        status: "can_xac_nhan",
        subject: "bệnh nhân",
        evidenceTurns: [9],
        quotes: [],
      },
    ],
  };

  const sessionNhi: Session = {
    id: "sess-nhi",
    patientIdentifier: "Bé Trần Gia Bảo",
    patientSubtitle: "Bé trai · 18 tháng tuổi · 11 kg",
    date: "26/11/2026",
    time: "08:30",
    language: "Tiếng Việt",
    durationSeconds: 180,
    isRecording: false,
    transcript: "",
    activeTabId: "tab-1",
    tabs: [{ id: "tab-ctx", title: "Ngữ cảnh", type: "context", content: "Bé trai 18 tháng tuổi, cân nặng 11 kg, PARA 1001, GCS 15/15" }],
    note: noteMau,
  };

  const quyet = { 1: "giu", 2: "giu", 3: "giu", 4: "sua", 5: "giu", 6: "bo", 7: "cho" } as const;
  const banSua = { 4: "Cefuroxim 125mg uống ngày 2 lần" };

  assert.equal(DANH_SACH_MAU_BIEN_DICH_TAI_CHO.length, 8);

  for (const mauId of DANH_SACH_MAU_BIEN_DICH_TAI_CHO) {
    const vanBan = bienDichBieuMauPhapLyTaiCho(mauId, {
      session: sessionNhi,
      note: noteMau,
      quyetDuyet: quyet,
      banSuaDuyet: banSua,
    });
    assert.ok(vanBan && vanBan.length > 150, `Mẫu ${mauId} phải biên dịch ra văn bản đầy đủ`);
    assert.ok(!vanBan!.includes("Aspirin 81mg"), `Mẫu ${mauId} tuyệt đối không được chứa mệnh đề đã bấm Bỏ`);
    assert.ok(vanBan!.includes("[T1, T2]") || vanBan!.includes("[T6]"), `Mẫu ${mauId} phải gắn dẫn nguồn [T_i]`);
    assert.ok(vanBan!.includes("[cần bổ sung"), `Mẫu ${mauId} phải dùng [cần bổ sung] cho thông tin thiếu`);
    assert.ok(
      vanBan!.includes("MỤC CHƯA ĐƯA VÀO NỘI DUNG PHÁP LÝ CHÍNH THỨC"),
      `Mẫu ${mauId} phải gom riêng mệnh đề Cần xác nhận chưa chốt`
    );
  }

  // Kiểm tra riêng Giấy nghỉ BHXH TT 25/2025: cảnh báo vượt trần 30 ngày & cha/mẹ bệnh nhi < 7 tuổi
  const bhxh = bienDichBieuMauPhapLyTaiCho("giay-nghi-bhxh-tt25-2025", {
    session: sessionNhi,
    note: noteMau,
    quyetDuyet: quyet,
    banSuaDuyet: banSua,
  })!;
  assert.match(bhxh, /VƯỢT TRẦN TỐI ĐA 30 NGÀY\/LẦN/);
  assert.match(bhxh, /BẮT BUỘC ĐỐI VỚI BỆNH NHI DƯỚI 7 TUỔI/);

  // Kiểm tra riêng Bệnh án Nhi khoa: có cân nặng 11 kg, liều sửa 125mg (~11.4 mg/kg/lần), tách lời khai bố
  const nhi = bienDichBieuMauPhapLyTaiCho("khuon-nhi-khoa", {
    session: sessionNhi,
    note: noteMau,
    quyetDuyet: quyet,
    banSuaDuyet: banSua,
  })!;
  assert.match(nhi, /11 kg/);
  assert.match(nhi, /Cefuroxim 125mg uống ngày 2 lần \[T6\]/);
  assert.match(nhi, /11\.4 mg\/kg\/lần/);
  assert.match(nhi, /Bố bị hen phế quản mạn tính \[T3\]/);

  // Mẫu không thuộc 8 biểu mẫu luật tại chỗ trả null
  assert.equal(bienDichBieuMauPhapLyTaiCho("soap", { session: sessionNhi }), null);
});

test("Boost 4C: xuatGoiFhirVaBhytHieuLuc xoá sạch mệnh đề 'bo' và áp dụng 'sua' trên cả FHIR R4 & XML1–XML5", () => {
  const noteMeta: NoteMeta = {
    content: "Bản nháp",
    needsConfirmCount: 0,
    questions: [],
    caseId: "LK-2026-88",
    clinicalSafety: {
      bhyt_icd10: {
        ma_icd10_chinh: { ma_icd10: "I10", ten_benh_byt: "Tăng huyết áp vô căn" },
        ma_icd10_kem_theo: [],
      },
      fhir_bundle: {
        resourceType: "Bundle",
        entry: [
          {
            fullUrl: "urn:uuid:patient-88",
            resource: { resourceType: "Patient", id: "patient-88", name: [{ text: "Lê Văn Tám" }] },
          },
          {
            fullUrl: "urn:uuid:med-stale",
            resource: {
              resourceType: "MedicationRequest",
              id: "med-stale",
              medicationCodeableConcept: { text: "Ibuprofen 400mg bị bác sĩ loại bỏ" },
            },
          },
        ],
      },
    },
    propositions: [
      {
        id: 10,
        section: "CHẨN ĐOÁN",
        text: "Tăng huyết áp độ 2",
        status: "than",
        subject: "bệnh nhân",
        evidenceTurns: [2],
        quotes: [],
      },
      {
        id: 11,
        section: "DỊ ỨNG",
        text: "Dị ứng NSAID gây phù mạch",
        status: "than",
        subject: "bệnh nhân",
        evidenceTurns: [3],
        quotes: [],
      },
      {
        id: 12,
        section: "KẾ HOẠCH ĐIỀU TRỊ",
        text: "Amlodipin 10mg uống sáng",
        drug: "Amlodipin",
        status: "than",
        subject: "bệnh nhân",
        evidenceTurns: [5],
        quotes: [],
      },
      {
        id: 13,
        section: "KẾ HOẠCH ĐIỀU TRỊ",
        text: "Ibuprofen 400mg bị bác sĩ loại bỏ",
        drug: "Ibuprofen",
        status: "than",
        subject: "bệnh nhân",
        evidenceTurns: [6],
        quotes: [],
      },
    ],
  };

  const goi = xuatGoiFhirVaBhytHieuLuc({
    noteMeta,
    quyetDuyet: { 10: "giu", 11: "giu", 12: "sua", 13: "bo" },
    banSuaDuyet: { 12: "Amlodipin 5mg uống 1 viên buổi sáng" },
    patientIdentifier: "Lê Văn Tám",
  });

  assert.equal(goi.reviewSummary.rejectedCount, 1);
  assert.equal(goi.reviewSummary.editedCount, 1);
  assert.equal(goi.propositions.length, 3);
  assert.ok(!goi.propositions.some((p) => p.text.includes("Ibuprofen")));

  const fhirJson = JSON.stringify(goi.effective_fhir_bundle);
  assert.ok(!fhirJson.includes("Ibuprofen"), "FHIR bundle hậu duyệt không được còn thuốc đã Bỏ");
  assert.ok(fhirJson.includes("Amlodipin 5mg uống 1 viên buổi sáng"), "FHIR bundle phải cập nhật liều bác sĩ đã Sửa");
  assert.ok(fhirJson.includes("Dị ứng NSAID gây phù mạch"));
  assert.ok(fhirJson.includes('"reviewDecision":"sua"'));

  const xmlAll = [
    goi.effective_xml_1_5.XML1,
    goi.effective_xml_1_5.XML2,
    goi.effective_xml_1_5.XML3,
    goi.effective_xml_1_5.XML4,
    goi.effective_xml_1_5.XML5,
  ].join("\n");
  assert.ok(!xmlAll.includes("Ibuprofen"), "XML1–XML5 không được còn mệnh đề đã Bỏ");
  assert.ok(goi.effective_xml_1_5.XML2.includes("Amlodipin 5mg uống 1 viên buổi sáng"));
  assert.ok(goi.effective_xml_1_5.XML1.includes("<MA_BENH_CHINH>I10</MA_BENH_CHINH>"));
});

test("Boost 2B & 11: taoDaiTomTatTruocKham và trichNhiemVuTuCacCaKham hoạt động chính xác xuyên ca khám", () => {
  const caLan1: Session = {
    id: "sess-1",
    patientIdentifier: "Trần Thị Mai",
    patientSubtitle: "Khám lần 1",
    date: "01/09/2026",
    time: "08:00",
    language: "Tiếng Việt",
    durationSeconds: 120,
    isRecording: false,
    transcript: "Bác sĩ: Huyết áp 156/94, HbA1c 8.4, eGFR 68",
    activeTabId: "t1",
    tabs: [],
    note: {
      content: "",
      needsConfirmCount: 0,
      questions: [],
      propositions: [
        {
          id: 1,
          section: "DỊ ỨNG",
          text: "Tiền sử dị ứng Penicillin sốc phản vệ độ 2",
          status: "than",
          subject: "bệnh nhân",
          evidenceTurns: [1],
          quotes: [],
        },
        {
          id: 2,
          section: "THUỐC ĐANG DÙNG",
          text: "Metformin 850mg uống ngày 2 lần",
          drug: "Metformin",
          status: "than",
          subject: "bệnh nhân",
          evidenceTurns: [2],
          quotes: [],
        },
      ],
    },
  };

  const caLan2: Session = {
    id: "sess-2",
    patientIdentifier: "Trần Thị Mai",
    patientSubtitle: "Khám lần 2",
    date: "15/10/2026",
    time: "09:00",
    language: "Tiếng Việt",
    durationSeconds: 150,
    isRecording: false,
    transcript: "Bác sĩ: Huyết áp 134/82, HbA1c 7.1, eGFR 61",
    activeTabId: "t1",
    tabs: [],
    note: {
      content: "",
      needsConfirmCount: 0,
      questions: [],
      propositions: [
        {
          id: 1,
          section: "KẾ HOẠCH ĐIỀU TRỊ",
          text: "Hẹn tái khám và xét nghiệm lại chức năng thận sau 2 tuần",
          status: "than",
          subject: "bệnh nhân",
          evidenceTurns: [4],
          quotes: [],
        },
        {
          id: 2,
          section: "KẾ HOẠCH ĐIỀU TRỊ",
          text: "Cấy máu khẩn và hội chẩn tim mạch ngay hôm nay",
          status: "than",
          subject: "bệnh nhân",
          evidenceTurns: [5],
          quotes: [],
        },
      ],
    },
  };

  const caHienTai: Session = {
    id: "sess-3",
    patientIdentifier: "Trần Thị Mai",
    patientSubtitle: "Tái khám hôm nay",
    date: "26/11/2026",
    time: "10:00",
    language: "Tiếng Việt",
    durationSeconds: 0,
    isRecording: false,
    transcript: "",
    activeTabId: "t1",
    tabs: [],
  };

  const caChuaDatTen: Session = {
    ...caHienTai,
    id: "sess-empty",
    patientIdentifier: "Thêm tên định danh bệnh nhân",
  };

  assert.equal(taoDaiTomTatTruocKham(caChuaDatTen, [caChuaDatTen, caLan2, caLan1]).coDuLieuCu, false);

  const tomTat = taoDaiTomTatTruocKham(caHienTai, [caHienTai, caLan2, caLan1]);
  assert.equal(tomTat.coDuLieuCu, true);
  assert.equal(tomTat.soLanKhamTruoc, 2);
  assert.ok(tomTat.diUngDaXacNhan.some((d) => d.includes("Penicillin")));
  assert.ok(tomTat.thuocManTinh.some((m) => m.includes("Metformin")));
  assert.ok(tomTat.bienThienSinhHieuXn.some((x) => x.includes("156/94 → 134/82") && x.includes("↓")));
  assert.ok(tomTat.bienThienSinhHieuXn.some((x) => x.includes("eGFR: 68 → 61") && x.includes("↓")));
  assert.ok(tomTat.bienThienSinhHieuXn.some((x) => x.includes("HbA1c: 8.4% → 7.1%") && x.includes("↓")));
  assert.ok(tomTat.viecHenTonDong.length >= 1);

  const tasks = trichNhiemVuTuCacCaKham([caLan2, caLan1]);
  assert.equal(tasks.length, 2);
  assert.equal(tasks[0].sessionId, "sess-2");
  assert.equal(tasks[0].patientName, "Trần Thị Mai");
  assert.equal(tasks[0].dueDate, "Sau 2 tuần");
  assert.equal(tasks[1].priority, "high");
});
