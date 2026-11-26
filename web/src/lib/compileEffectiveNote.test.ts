import assert from "node:assert/strict";
import crypto from "node:crypto";
import test from "node:test";
import {
  buildSignOffCanonicalPayload,
  compileEffectiveNote,
  computeNoteSignOffHash,
  computeNoteSignOffHashSync,
  isSignOffStale,
  kiemTraDieuKienKyDuyet,
  layNoiDungBenhAnDeBam,
  sha256Hex,
  sha256HexSync,
  trichChanDoanVaThuocTuSoap,
} from "./compileEffectiveNote";
import { chuyenKetQuaThanhTin, kiemTraDoiChieuDaChay } from "./troLy";
import {
  chonPhuongAnDongBoServer,
  dauVanTayLuuServer,
  gopBroadcastVaoPhienHienTai,
} from "../hooks/useSessionsStore";
import { trichNguCanhChoTroLy, xayNguCanhChoTaoHoSo } from "./nguCanhTroLy";
import {
  RealAudioService,
  buildScopedAudioKey,
  clearAllPersistedAudio,
  getUserScope,
  khoiPhucAudioIDB,
  setUserScope,
} from "../services/realAudioService";
import { donSachKhiHetPhien, nhanMayChoNguoi } from "./taiKhoan";
import type { DocumentTabItem, Session } from "../types";

test("compileEffectiveNote: ap dung Sua, Bo dong don le, Bo mot menh de tren dong nhieu cau va hoan tac Giu", () => {
  const raw = [
    "# BỆNH ÁN SOAP",
    "",
    "BỆNH SỬ HIỆN TẠI",
    "- Bệnh nhân đau đầu âm ỉ 3 ngày [T1].",
    "- Sốt cao 39 độ C kèm rét run [T2].",
    "bà: đau tăng khi cúi [T3]. bà: đau tăng khi cúi chỉ bị lúc sáng sớm [T4].",
    "",
    "KẾ HOẠCH ĐIỀU TRỊ",
    "- Amlodipin 5 mg uống sáng 1 viên [T5].",
    "- Paracetamol 500 mg uống khi sốt [T6].",
    "",
    "CẦN XÁC NHẬN",
    "- bà: amoxicillin 250 mg, uống — đoạn dẫn nói về người nhà [T7].",
  ].join("\n");

  const propositions = [
    { id: 1, text: "Bệnh nhân đau đầu âm ỉ 3 ngày" },
    { id: 2, text: "Sốt cao 39 độ C kèm rét run" },
    { id: 3, text: "bà: đau tăng khi cúi" },
    { id: 4, text: "bà: đau tăng khi cúi chỉ bị lúc sáng sớm" },
    { id: 5, text: "Amlodipin 5 mg uống sáng 1 viên" },
    { id: 6, text: "Paracetamol 500 mg uống khi sốt" },
    { id: 7, text: "bà: amoxicillin 250 mg, uống", gateReason: "đoạn dẫn nói về người nhà" },
  ];

  // 1. Sửa mệnh đề 5, bỏ mệnh đề 2 (cả dòng bullet), bỏ mệnh đề 3 (câu đầu trong dòng 2 câu), bỏ mệnh đề 7 (làm rỗng CẦN XÁC NHẬN)
  const compiled = compileEffectiveNote(
    raw,
    propositions,
    {
      1: "giu",
      2: "bo",
      3: "bo",
      4: "giu",
      5: "sua",
      6: "giu",
      7: "bo",
    },
    {
      1: "Đau đầu dữ dội (bản sửa cũ đã huỷ khi chọn lại Giữ)",
      5: "Amlodipin 10 mg uống sáng 1 viên sau ăn",
    },
  );

  // Giữ nguyên mệnh đề 1 (không lấy bản sửa cũ vì bác sĩ bấm "giu")
  assert.ok(compiled.includes("- Bệnh nhân đau đầu âm ỉ 3 ngày [T1]."));
  assert.equal(compiled.includes("bản sửa cũ"), false);

  // Loại bỏ hoàn toàn mệnh đề 2 khỏi văn bản xuất
  assert.equal(compiled.includes("Sốt cao 39 độ C"), false);
  assert.equal(compiled.includes("[T2]"), false);

  // Trên dòng 2 câu: xoá câu 3 nhưng giữ nguyên câu 4
  assert.equal(compiled.includes("bà: đau tăng khi cúi [T3]"), false);
  assert.ok(compiled.includes("bà: đau tăng khi cúi chỉ bị lúc sáng sớm [T4]."));

  // Mệnh đề 5 được thay bằng câu bác sĩ sửa, vẫn giữ mỏ neo [T5]
  assert.ok(compiled.includes("- Amlodipin 10 mg uống sáng 1 viên sau ăn [T5]."));
  assert.equal(compiled.includes("Amlodipin 5 mg"), false);

  // Mục CẦN XÁC NHẬN bị bỏ hết mệnh đề thì tiêu đề rỗng cũng được dọn sạch
  assert.equal(compiled.includes("amoxicillin 250 mg"), false);
  assert.equal(compiled.includes("CẦN XÁC NHẬN"), false);
});

test("compileEffectiveNote: an toan voi dau vao rong, khong khop va xoa cau cuoi dong", () => {
  assert.equal(compileEffectiveNote("", [{ id: 1, text: "a" }], { 1: "bo" }, {}), "");

  const multi = "TIỀN SỬ\nbà: nghẹt mũi (gần một tuần) — đã hỏi lại. bà: ho khan về đêm.";
  const props = [
    { id: 10, text: "bà: nghẹt mũi (gần một tuần)", gateReason: "đã hỏi lại" },
    { id: 11, text: "bà: ho khan về đêm" },
    { id: 99, text: "mệnh đề không tồn tại trong văn bản" },
  ];
  const out = compileEffectiveNote(multi, props, { 10: "sua", 11: "bo", 99: "bo" }, { 10: "bà: nghẹt mũi 5 ngày" });
  assert.equal(out, "TIỀN SỬ\nbà: nghẹt mũi 5 ngày.");

  // Khi bác sĩ đã sửa nhẹ văn bản thô (khớp gần đúng Dice >= 0.6) rồi bấm Sửa ở ngăn duyệt -> vẫn giữ dấu gạch đầu dòng và [T5]
  const fuzzyRaw = "ĐƠN THUỐC\n- Amlodipin 5mg sáng 1 viên [T5].";
  const fuzzyOut = compileEffectiveNote(
    fuzzyRaw,
    [{ id: 5, text: "Amlodipin 5 mg uống sáng 1 viên" }],
    { 5: "sua" },
    { 5: "Amlodipin 10 mg uống sáng 1 viên" },
  );
  assert.equal(fuzzyOut, "ĐƠN THUỐC\n- Amlodipin 10 mg uống sáng 1 viên [T5].");
});

test("SHA-256: sha256Hex va fallback thuan TS khop 100% bit-for-bit voi node:crypto tren ASCII, dai va Unicode tieng Viet", async () => {
  const mauThu = [
    "",
    "abc",
    "Bệnh án SOAP — Nguyễn Thị Ánh Tuyết, 68 tuổi, Đái tháo đường típ 2, eGFR 42 mL/phút/1.73m²",
    "MediTrace-WORM-Block-Boundary-56Bytes___________________", // đúng biên padding 56 byte
    "MediTrace-MultiBlock-Payload-".repeat(80),
  ];

  for (const chuoi of mauThu) {
    const kyVong = crypto.createHash("sha256").update(chuoi, "utf8").digest("hex");
    const bamDongBo = sha256HexSync(chuoi);
    const bamWebCrypto = await sha256Hex(chuoi);
    const bamFallback = await sha256Hex(chuoi, null); // ép chạy nhánh không có crypto.subtle

    assert.equal(bamDongBo, kyVong, `sha256HexSync lech cho chuoi do dai ${chuoi.length}`);
    assert.equal(bamWebCrypto, kyVong, `sha256Hex (subtle) lech cho chuoi do dai ${chuoi.length}`);
    assert.equal(bamFallback, kyVong, `sha256Hex (fallback) lech cho chuoi do dai ${chuoi.length}`);
    assert.equal(bamDongBo.length, 64);
  }
});

test("WORM Sign-off: khong bao gio bam nham tab leaflet va phat hien chinh xac trang thai 'Da sua · Ky lai'", async () => {
  const tabs: DocumentTabItem[] = [
    { id: "tab-transcript", title: "Lời thoại", type: "transcript", content: "Bác sĩ: Chào bác" },
    { id: "tab-context", title: "Ngữ cảnh", type: "context", content: "Creatinin 140 umol/L" },
    { id: "tab-soap", title: "Bệnh án SOAP", type: "soap", content: "CHẨN ĐOÁN\n- Tăng huyết áp vô căn" },
    { id: "tab-leaflet", title: "Tờ dặn dò", type: "leaflet", content: "Uống thuốc buổi sáng sau ăn" },
  ];

  // Dù đang đứng ở tab "leaflet", hàm chọn nội dung băm vẫn phải lấy đúng tab SOAP, KHÔNG lấy tờ dặn dò!
  const chosenFromLeaflet = layNoiDungBenhAnDeBam(tabs, "tab-leaflet", null);
  assert.equal(chosenFromLeaflet, "CHẨN ĐOÁN\n- Tăng huyết áp vô căn");

  const hashBanDau = await computeNoteSignOffHash(chosenFromLeaflet, { 1: "giu" }, {});
  const signOff = { hash: "worm-chain-curr-hash", contentHash: hashBanDau };

  assert.equal(isSignOffStale(signOff, hashBanDau), false);

  // Sửa quyết định duyệt (giu -> sua) làm hash đổi -> nút chuyển sang "Đã sửa · Ký lại"
  const hashSauSuaDuyet = computeNoteSignOffHashSync(chosenFromLeaflet, { 1: "sua" }, { 1: "Tăng huyết áp độ 2" });
  assert.notEqual(hashSauSuaDuyet, hashBanDau);
  assert.equal(isSignOffStale(signOff, hashSauSuaDuyet), true);

  // Sửa nội dung bệnh án SOAP cũng làm hash đổi -> stale = true
  const hashSauSuaVanBan = computeNoteSignOffHashSync(`${chosenFromLeaflet}\n- Kèm rối loạn lipid máu`, { 1: "giu" }, {});
  assert.equal(isSignOffStale(signOff, hashSauSuaVanBan), true);

  // Tương thích ngược nếu bản ghi cũ chỉ có trường `hash`
  assert.equal(isSignOffStale({ hash: hashBanDau }, hashBanDau), false);
  assert.equal(isSignOffStale({ hash: hashBanDau }, hashSauSuaVanBan), true);

  // Thứ tự key trong object quyetDuyet không làm đổi canonical payload
  const p1 = buildSignOffCanonicalPayload("SOAP", { 2: "bo", 1: "giu", 3: "cho" }, {});
  const p2 = buildSignOffCanonicalPayload("SOAP", { 1: "giu", 2: "bo" }, {});
  assert.equal(p1, p2);
});

test("troLy.ts: kiem tra that trang thai tac tu doi_chieu thay vi gan cung 'chua qua kiem can cu'", () => {
  // 1. Khi doi_chieu chạy xong và không còn ý thiếu căn cứ
  const kqDaDoiChieu = {
    phan: [
      {
        tacTu: "tra_loi",
        ten: "Trả lời",
        noiDung: "Khuyến cáo A [1]",
        traLoi: { answer: "Khuyến cáo A [1]", sources: [{ so: 1, name: "BYT" }], cauTruc: null },
      },
      {
        tacTu: "doi_chieu",
        ten: "Đối chiếu",
        noiDung: "Máy kiểm: không thấy số liệu lệch. Xét từng ý: mọi ý đều có căn cứ.",
        traLoi: { lech: [], thieu: [], daSua: false, conThieu: [] },
      },
    ],
    thongKe: { giay: 8.2, token: 420 },
  };
  const tin1 = chuyenKetQuaThanhTin(kqDaDoiChieu, "câu hỏi", { source: "mo_hinh_ngoai", model: "qwen3" });
  assert.ok(tin1.meta?.includes("đã qua tác tử đối chiếu căn cứ"), tin1.meta);
  assert.equal(tin1.meta?.includes("chưa qua kiểm căn cứ"), false);

  // 2. Khi doi_chieu chạy xong nhưng còn cảnh báo căn cứ
  const kqCoLech = {
    phan: [
      {
        tacTu: "doi_chieu",
        ten: "Đối chiếu",
        noiDung: "Máy kiểm: 1 ý có số liệu lệch.",
        traLoi: { lech: ["liều 500mg"], thieu: [], daSua: false, conThieu: [] },
        canhBao: "liều 500mg lệch",
      },
    ],
    thongKe: { giay: 5, token: 200 },
  };
  const tin2 = chuyenKetQuaThanhTin(kqCoLech, "câu hỏi", { source: "mo_hinh_ngoai", model: "qwen3" });
  assert.ok(tin2.meta?.includes("đã qua tác tử đối chiếu (có lưu ý căn cứ)"), tin2.meta);

  // 3. Khi doi_chieu bị chặn/lỗi rỗng hoặc không bật -> báo trung thực "chưa qua kiểm căn cứ"
  const kqBiChan = {
    phan: [{ tacTu: "doi_chieu", ten: "Đối chiếu", noiDung: "", canhBao: "chưa bật mô hình ngoài" }],
    thongKe: { giay: 1, token: 10 },
  };
  assert.equal(kiemTraDoiChieuDaChay(kqBiChan).daQuaDoiChieu, false);
  const tin3 = chuyenKetQuaThanhTin(kqBiChan, "câu hỏi", { source: "mo_hinh_ngoai", model: "qwen3" });
  assert.ok(tin3.meta?.includes("chưa qua kiểm căn cứ"), tin3.meta);
});

test("useSessionsStore: dauVanTayLuuServer chan triet de bao 1.200 PUT 1Hz khi dang ghi am nhung van luu khi dung ghi", () => {
  const baseSession: Session = {
    id: "ca-1",
    patientIdentifier: "Nguyễn Văn Bình",
    patientSubtitle: "Nam, 62 tuổi",
    date: "Hôm nay",
    time: "08:30",
    language: "Tiếng Việt",
    durationSeconds: 0,
    isRecording: true,
    transcript: "",
    activeTabId: "tab-transcript",
    tabs: [{ id: "tab-transcript", title: "Lời thoại", type: "transcript", content: "" }],
  };

  const fpStart = dauVanTayLuuServer([baseSession]);
  // Mô phỏng 1.200 nhịp đồng hồ (20 phút ghi âm liên tục)
  for (const sec of [1, 2, 60, 600, 1200]) {
    const fpTick = dauVanTayLuuServer([{ ...baseSession, durationSeconds: sec, isRecording: true }]);
    assert.equal(fpTick, fpStart, `Tick giay thu ${sec} khong duoc lam doi van tay PUT server`);
  }

  // Khi bác sĩ sửa tên bệnh nhân ngay lúc đang ghi âm -> vân tay ĐỔI để không mất dữ liệu thật
  const fpEditedWhileRec = dauVanTayLuuServer([
    { ...baseSession, durationSeconds: 45, isRecording: true, patientIdentifier: "Nguyễn Văn Bình (VIP)" },
  ]);
  assert.notEqual(fpEditedWhileRec, fpStart);

  // Ngay khi bấm Dừng ghi âm ở giây 1200 -> isRecording=false -> vân tay ĐỔI để chốt durationSeconds=1200 lên server 1 lần
  const fpStopped = dauVanTayLuuServer([{ ...baseSession, durationSeconds: 1200, isRecording: false }]);
  assert.notEqual(fpStopped, fpStart);

  // Kiểm tra chonPhuongAnDongBoServer: sửa 1 ca -> PUT hạt mịn /api/ca-kham/:id; thêm/xoá ca -> PUT /api/ca-kham
  const sA: Session = { ...baseSession, id: "ca-A", isRecording: false, durationSeconds: 30 };
  const sB: Session = { ...baseSession, id: "ca-B", isRecording: false, durationSeconds: 60 };
  assert.equal(chonPhuongAnDongBoServer([sA, sB], [sA, { ...sB, isRecording: true, durationSeconds: 95 }]).loai, "khong_doi");
  const motCa = chonPhuongAnDongBoServer([sA, sB], [sA, { ...sB, transcript: "Bác sĩ: Chào anh" }]);
  assert.equal(motCa.loai, "mot_ca");
  if (motCa.loai === "mot_ca") assert.equal(motCa.session.id, "ca-B");
  assert.equal(chonPhuongAnDongBoServer([sA, sB], [sA]).loai, "toan_bo");
});

test("xayNguCanhChoTaoHoSo: trich dung context, tuoi, gioi, can nang va chi so XN ma khong bia tuoi 50", () => {
  // Trường hợp chưa nhập tuổi/giới -> tuyệt đối KHÔNG tự điền tuổi 50 hay la_nu=false
  const rong = xayNguCanhChoTaoHoSo({
    sessionId: "s-empty",
    patientIdentifier: "Thêm tên định danh bệnh nhân",
    patientSubtitle: "Ca khám bệnh mới",
    tabs: [{ id: "tab-context", title: "Ngữ cảnh", type: "context", content: "" }],
  });
  assert.equal(rong.context, undefined);
  assert.equal(rong.thong_tin_benh_nhan?.tuoi, undefined);
  assert.equal(rong.thong_tin_benh_nhan?.la_nu, undefined);
  assert.equal(rong.thong_tin_benh_nhan?.ho_ten, undefined);

  // Trường hợp bác sĩ đã nhập ngữ cảnh & xét nghiệm cũ
  const dayDu = xayNguCanhChoTaoHoSo({
    sessionId: "s-real",
    patientIdentifier: "Trần Thị Mai",
    patientSubtitle: "Nữ, 71 tuổi · Tái khám thận",
    tabs: [
      {
        id: "tab-context",
        title: "Ngữ cảnh",
        type: "context",
        content: "Cân nặng: 54 kg\n[Xét nghiệm cũ] creatinine_umol_l: 168, egfr: 28.5, hba1c: 7.9",
      },
    ],
  });
  assert.ok(dayDu.context?.includes("creatinine_umol_l: 168"));
  assert.equal(dayDu.thong_tin_benh_nhan?.ho_ten, "Trần Thị Mai");
  assert.equal(dayDu.thong_tin_benh_nhan?.tuoi, 71);
  assert.equal(dayDu.thong_tin_benh_nhan?.gioi_tinh, "nữ");
  assert.equal(dayDu.thong_tin_benh_nhan?.la_nu, true);
  assert.equal(dayDu.thong_tin_benh_nhan?.can_nang_kg, 54);
  assert.equal(dayDu.du_lieu_xet_nghiem?.creatinine_umol_l, 168);
  assert.equal(dayDu.du_lieu_xet_nghiem?.egfr, 28.5);
  assert.equal(dayDu.du_lieu_xet_nghiem?.hba1c, 7.9);
});

test("Phan vung userId & don sach PHI cheo bac si tren may dung chung", async () => {
  setUserScope(42);
  assert.equal(getUserScope(), "42");
  assert.equal(buildScopedAudioKey("session-abc"), "u:42:session-abc");

  setUserScope(99);
  assert.notEqual(buildScopedAudioKey("session-abc"), "u:42:session-abc");
  assert.equal(buildScopedAudioKey("session-abc"), "u:99:session-abc");

  // Giả lập localStorage trên máy dùng chung để kiểm tra nhanMayChoNguoi & donSachKhiHetPhien
  const store = new Map<string, string>([
    ["meditrace_chu", "42"],
    ["meditrace_sessions", '[{"id":"s1","patientIdentifier":"BN của BS 42"}]'],
    ["meditrace_kho_ca-kham", '[{"id":"s1"}]'],
  ]);
  const prevLocalStorage = (globalThis as any).localStorage;
  (globalThis as any).localStorage = {
    getItem: (k: string) => store.get(k) ?? null,
    setItem: (k: string, v: string) => store.set(k, String(v)),
    removeItem: (k: string) => store.delete(k),
  };
  Object.defineProperty((globalThis as any).localStorage, "meditrace_extra", {
    value: "1",
    enumerable: true,
    configurable: true,
  });

  try {
    // Đổi sang bác sĩ 77 -> xoá sạch meditrace_sessions & meditrace_kho_ca-kham của bác sĩ 42
    nhanMayChoNguoi(77);
    assert.equal(store.get("meditrace_sessions"), undefined);
    assert.equal(store.get("meditrace_kho_ca-kham"), undefined);
    assert.equal(store.get("meditrace_chu"), "77");
    assert.equal(getUserScope(), "77");

    // Khi bắt 401 hết phiên -> xóa sạch PHI và reset scope về anon
    store.set("meditrace_sessions", '[{"id":"s2"}]');
    store.set("meditrace_kho_ca-kham", '[{"id":"s2"}]');
    await donSachKhiHetPhien();
    await clearAllPersistedAudio();
    assert.equal(store.get("meditrace_sessions"), undefined);
    assert.equal(store.get("meditrace_kho_ca-kham"), undefined);
    assert.equal(getUserScope(), "anon");
  } finally {
    (globalThis as any).localStorage = prevLocalStorage;
  }
});

test("compileEffectiveNote: dong bo cau nhan ban o LY DO KHAM BENH, don muc rong, dau phay cuoi va so thap phan", () => {
  // 1. sinh_benh_an.py chép câu đầu của BỆNH SỬ HIỆN TẠI lên LÝ DO KHÁM BỆNH dưới cùng 1 ID mệnh đề
  const rawSinhBenhAn = [
    "LÝ DO KHÁM BỆNH",
    "",
    "đau đầu âm ỉ 3 ngày.",
    "",
    "BỆNH SỬ HIỆN TẠI",
    "",
    "đau đầu âm ỉ 3 ngày. sốt cao 38.5 độ C.",
    "",
    "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI",
    "",
    "mẹ: tăng huyết áp.",
    "",
    "## KHÁM LÂM SÀNG",
    "",
    "## KẾ HOẠCH",
  ].join("\n");

  const props = [
    { id: 1, text: "đau đầu âm ỉ 3 ngày" },
    { id: 2, text: "sốt cao 38.5 độ C" },
    { id: 3, text: "mẹ: tăng huyết áp" },
  ];

  // Khi bác sĩ Sửa mệnh đề 1 -> CẢ hai nơi (LÝ DO KHÁM BỆNH & BỆNH SỬ HIỆN TẠI) đều được cập nhật nhất quán
  const suaCaHai = compileEffectiveNote(rawSinhBenhAn, props, { 1: "sua" }, { 1: "đau đầu âm ỉ 5 ngày" });
  assert.equal(suaCaHai.includes("3 ngày"), false);
  assert.equal((suaCaHai.match(/đau đầu âm ỉ 5 ngày/g) || []).length, 2);

  // Khi bác sĩ Bỏ mệnh đề 1 và mệnh đề 3 -> xoá cả 2 bản sao mệnh đề 1, dọn sạch tiêu đề LÝ DO KHÁM BỆNH & TIỀN SỬ GIA ĐÌNH rỗng,
  // nhưng VẪN GIỮ tiêu đề mẫu trống từ đầu (## KHÁM LÂM SÀNG, ## KẾ HOẠCH)
  const boSachMuc = compileEffectiveNote(rawSinhBenhAn, props, { 1: "bo", 2: "giu", 3: "bo" }, {});
  assert.equal(boSachMuc.includes("đau đầu âm ỉ"), false);
  assert.equal(boSachMuc.includes("LÝ DO KHÁM BỆNH"), false);
  assert.equal(boSachMuc.includes("TIỀN SỬ GIA ĐÌNH"), false);
  assert.ok(boSachMuc.includes("sốt cao 38.5 độ C."));
  assert.ok(boSachMuc.includes("## KHÁM LÂM SÀNG"));
  assert.ok(boSachMuc.includes("## KẾ HOẠCH"));

  // 2. Xoá mệnh đề sau dấu phẩy cuối dòng -> tự dọn dấu phẩy thừa và khép dấu chấm câu
  const dongPhay = "TRIỆU CHỨNG\n- Đau đầu âm ỉ [T1], sốt nhẹ về chiều [T2].";
  const kqPhay = compileEffectiveNote(
    dongPhay,
    [
      { id: 1, text: "Đau đầu âm ỉ" },
      { id: 2, text: "sốt nhẹ về chiều" },
    ],
    { 1: "giu", 2: "bo" },
    {},
  );
  assert.equal(kqPhay, "TRIỆU CHỨNG\n- Đau đầu âm ỉ [T1].");

  // 3. Khớp gần đúng trên câu có số thập phân (HbA1c 7.8%, sốt 38.5 độ C) không bị cắt đôi tại dấu chấm thập phân
  const dongThapPhan = "CẬN LÂM SÀNG\n- HbA1c 7.8% cao hơn lần trước [T3].";
  const kqThapPhan = compileEffectiveNote(
    dongThapPhan,
    [{ id: 3, text: "HbA1c 7.8% tăng cao hơn lần khám trước" }],
    { 3: "sua" },
    { 3: "HbA1c 8.1% tăng so với lần trước" },
  );
  assert.equal(kqThapPhan, "CẬN LÂM SÀNG\n- HbA1c 8.1% tăng so với lần trước [T3].");
});

test("RealAudioService: chan chunk mo coi sau 401/clearAllPersistedAudio va chong nhiem ban cheo ca khi dang ghi", async () => {
  // Dựng kho IndexedDB giả lập trong bộ nhớ để kiểm thử thật luồng bất đồng bộ của MediaRecorder.stop()
  type Row = { id: number; sessionKey: string; mimeType: string; chunk: Blob; createdAt: number };
  let autoId = 0;
  let rows: Row[] = [];

  const prevIDB = (globalThis as any).indexedDB;
  const prevNav = (globalThis as any).navigator;
  const prevMR = (globalThis as any).MediaRecorder;

  const makeFakeIDB = () => ({
    open: () => {
      const req: any = { result: null, onupgradeneeded: null, onsuccess: null, onerror: null };
      queueMicrotask(() => {
        const db = {
          objectStoreNames: { contains: () => true },
          createObjectStore: () => ({ createIndex: () => {} }),
          close: () => {},
          transaction: () => {
            const tx: any = { oncomplete: null, onerror: null };
            const finish = () => queueMicrotask(() => tx.oncomplete?.());
            tx.objectStore = () => ({
              add: (item: Omit<Row, "id">) => {
                rows.push({ ...item, id: ++autoId });
                finish();
              },
              clear: () => {
                rows = [];
                finish();
              },
              index: () => ({
                getAll: (key: string) => {
                  const r: any = { result: [], onsuccess: null, onerror: null };
                  queueMicrotask(() => {
                    r.result = rows.filter((x) => x.sessionKey === key);
                    r.onsuccess?.();
                    finish();
                  });
                  return r;
                },
                openCursor: (key: string) => {
                  const r: any = { result: null, onsuccess: null, onerror: null };
                  const matching = rows.filter((x) => x.sessionKey === key);
                  let idx = 0;
                  const step = () => {
                    queueMicrotask(() => {
                      if (idx < matching.length) {
                        const target = matching[idx++];
                        r.result = {
                          delete: () => {
                            rows = rows.filter((x) => x.id !== target.id);
                          },
                          continue: step,
                        };
                      } else {
                        r.result = null;
                        finish();
                      }
                      r.onsuccess?.();
                    });
                  };
                  step();
                  return r;
                },
              }),
            });
            return tx;
          },
        };
        req.result = db;
        req.onsuccess?.();
      });
      return req;
    },
  });

  let activeRecorders: any[] = [];
  class FakeMediaRecorder {
    static isTypeSupported() {
      return true;
    }
    state: "inactive" | "recording" = "inactive";
    mimeType = "audio/webm";
    ondataavailable: ((ev: { data: Blob }) => void) | null = null;
    onstop: (() => void) | null = null;
    onerror: ((ev: unknown) => void) | null = null;
    constructor() {
      activeRecorders.push(this);
    }
    start() {
      this.state = "recording";
    }
    emitChunk(text: string) {
      this.ondataavailable?.({ data: new Blob([text], { type: this.mimeType }) });
    }
    stop() {
      if (this.state === "inactive") return;
      this.state = "inactive";
      // Giống hệt W3C MediaRecorder trên trình duyệt thật: bắn chunk cuối + onstop bất đồng bộ SAU khi stop() trả về
      setTimeout(() => {
        this.ondataavailable?.({ data: new Blob(["final-orphan-chunk"], { type: this.mimeType }) });
        this.onstop?.();
      }, 10);
    }
  }

  Object.defineProperty(globalThis, "indexedDB", { value: makeFakeIDB(), configurable: true, writable: true });
  Object.defineProperty(globalThis, "MediaRecorder", { value: FakeMediaRecorder, configurable: true, writable: true });
  Object.defineProperty(globalThis, "navigator", {
    value: {
      mediaDevices: {
        getUserMedia: async () => ({ getTracks: () => [{ stop: () => {} }] }),
      },
    },
    configurable: true,
    writable: true,
  });

  try {
    // Kịch bản A: Đang ghi Ca A mà đổi setPersistenceKey("ca-B") -> chunk vẫn chỉ được ghi vào ca-A, tuyệt đối không rò sang ca-B!
    const svc = new RealAudioService();
    setUserScope(101);
    svc.setPersistenceKey("ca-A");
    await svc.start();
    const rec1 = activeRecorders[activeRecorders.length - 1];
    svc.setPersistenceKey("ca-B"); // đổi sang ca B giữa chừng
    rec1.emitChunk("chunk-cua-ca-A");
    await new Promise((r) => setTimeout(r, 15));

    assert.equal(await khoiPhucAudioIDB("ca-B"), null, "Chunk cua ca-A khong duoc ro sang ca-B");
    const recA = await khoiPhucAudioIDB("ca-A");
    assert.equal(recA?.count, 1);
    svc.resetMemoryAudio();
    rows = [];

    // Kịch bản B: Đang ghi âm dở dang thì bắt 401 / đăng xuất -> resetMemoryAudio() + clear IDB
    let goiOnAudioReadySau401 = false;
    svc.setCallbacks({
      onAudioReady: () => {
        goiOnAudioReadySau401 = true;
      },
    });
    svc.setPersistenceKey("ca-dang-ghi");
    await svc.start();
    const rec2 = activeRecorders[activeRecorders.length - 1];
    rec2.emitChunk("chunk-truoc-401");
    await new Promise((r) => setTimeout(r, 10));
    assert.equal(rows.length, 1);

    // Giả lập bắt 401 hết phiên ngay lúc đang ghi
    svc.resetMemoryAudio();
    await clearAllPersistedAudio();
    // Chờ thêm 25ms để chắc chắn setTimeout(10ms) của MediaRecorder.stop() đã chạy qua
    await new Promise((r) => setTimeout(r, 25));

    assert.equal(rows.length, 0, "Khong duoc con bat ky chunk mo coi nao trong IndexedDB sau 401");
    assert.equal(svc.getCurrentAudioBlob(), null);
    assert.equal(goiOnAudioReadySau401, false, "Khong duoc goi onAudioReady / transcribe sau khi phien da huy");
  } finally {
    Object.defineProperty(globalThis, "indexedDB", { value: prevIDB, configurable: true, writable: true });
    Object.defineProperty(globalThis, "MediaRecorder", { value: prevMR, configurable: true, writable: true });
    Object.defineProperty(globalThis, "navigator", { value: prevNav, configurable: true, writable: true });
  }
});

test("Khong nhan doi contextNotes, trich tuoi tu Ngay sinh, bao ve phien dang ghi qua BroadcastChannel va trich SOAP thu cong", () => {
  // 1. Không nhân đôi contextNotes khi cả tab-context và session.contextNotes đều có mặt; ưu tiên nội dung mới của tab-context
  const payload = xayNguCanhChoTaoHoSo({
    sessionId: "s-1",
    patientIdentifier: "Nguyễn Văn An",
    patientSubtitle: "Nam · 14/05/1988 · Nhiễm virus",
    contextNotes: "Dòng cũ đã xoá",
    tabs: [{ id: "tab-context", title: "Ngữ cảnh", type: "context", content: "Ngày sinh: 14/05/1988\nDị ứng: Không" }],
  });
  assert.equal(payload.context, "Ngày sinh: 14/05/1988\nDị ứng: Không");
  assert.equal(payload.context?.includes("Dòng cũ đã xoá"), false);
  assert.equal(payload.thong_tin_benh_nhan?.tuoi, new Date().getFullYear() - 1988);
  assert.equal(payload.thong_tin_benh_nhan?.gioi_tinh, "nam");

  // 2. trichNguCanhChoTroLy trích đúng tuổi từ Ngày sinh DD/MM/YYYY khi không truyền object Patient
  const ncDob = trichNguCanhChoTroLy({
    patientSubtitle: "Nữ · 20/11/1965",
    contextNotes: "Tăng huyết áp",
  });
  assert.equal(ncDob.tuoi, new Date().getFullYear() - 1965);
  assert.equal(ncDob.gioi, "nữ");

  // 3. BroadcastChannel từ Tab 2 sửa tên bệnh nhân không làm đứt trạng thái đang ghi âm ở Tab 1
  const tab1Sessions: Session[] = [
    {
      id: "ca-1",
      patientIdentifier: "BN Cũ",
      patientSubtitle: "Khám nội",
      date: "Hôm nay",
      time: "09:00",
      language: "Tiếng Việt",
      durationSeconds: 48,
      isRecording: true,
      audioUrl: "blob:http://localhost/audio-1",
      transcript: "",
      activeTabId: "tab-transcript",
      tabs: [],
    },
  ];
  const tab2Incoming: Session[] = [
    {
      ...tab1Sessions[0],
      patientIdentifier: "BN Đã Sửa Ở Tab 2",
      durationSeconds: 0,
      isRecording: false,
      audioUrl: undefined,
    },
  ];
  const merged = gopBroadcastVaoPhienHienTai(tab1Sessions, tab2Incoming);
  assert.equal(merged[0].patientIdentifier, "BN Đã Sửa Ở Tab 2");
  assert.equal(merged[0].isRecording, true);
  assert.equal(merged[0].audioUrl, "blob:http://localhost/audio-1");
  assert.equal(merged[0].durationSeconds, 48);

  // 4. Trích SOAP thủ công: mẫu trống trả rỗng, ca đã gõ chẩn đoán/thuốc trả đúng nội dung (chặn chép nhầm HO_SO_MAU)
  const mauTrong = trichChanDoanVaThuocTuSoap(
    "Lý do vào viện (Chủ quan):\n\nTiền sử bệnh lý & Dị ứng:\n\nKhám lâm sàng (Khách quan):\n\nĐánh giá & Chẩn đoán sơ bộ:\n\nKế hoạch điều trị & Đơn thuốc:",
  );
  assert.equal(mauTrong.chanDoan, undefined);
  assert.equal(mauTrong.thuoc.length, 0);

  const soapThuCong = trichChanDoanVaThuocTuSoap(
    "Chủ quan (S):\n- Đau thượng vị\n\nĐánh giá (A):\n- Viêm dạ dày cấp\n\nKế hoạch (P):\n- Esomeprazole 40mg sáng 1 viên trước ăn 30 phút",
  );
  assert.equal(soapThuCong.chanDoan, "Viêm dạ dày cấp");
  assert.deepEqual(soapThuCong.thuoc, ["Esomeprazole 40mg sáng 1 viên trước ăn 30 phút"]);
});

test("kiemTraDieuKienKyDuyet: chan cung hoan tat ho so khi thieu can cu hoac con muc Can xac nhan chua duyet", () => {
  // 1. Hồ sơ rỗng (0 mệnh đề) -> chặn cứng
  const rRong = kiemTraDieuKienKyDuyet([], {}, {});
  assert.equal(rRong.duDieuKien, false);
  assert.equal(rRong.maLoi, "khong_co_menh_de");

  // 2. Còn mệnh đề trong mục Cần xác nhận chưa được bác sĩ Giữ / Sửa / Bỏ -> chặn cứng
  const props = [
    { id: 1, status: "than", evidenceTurns: [2] },
    { id: 2, status: "can_xac_nhan", evidenceTurns: [5] },
    { id: 3, status: "than", stateD: "cần xác nhận", evidenceTurns: [6] },
  ];
  const rChuaDuyet = kiemTraDieuKienKyDuyet(props, { 1: "giu" }, {});
  assert.equal(rChuaDuyet.duDieuKien, false);
  assert.equal(rChuaDuyet.maLoi, "con_muc_can_xac_nhan");
  assert.equal(rChuaDuyet.soCanXacNhanChuaDuyet, 2);
  assert.deepEqual(rChuaDuyet.chuaXacNhanIds, [2, 3]);

  // 3. Chọn "sua" nhưng nội dung sửa để trống -> vẫn chặn
  const rSuaRong = kiemTraDieuKienKyDuyet(props, { 2: "sua", 3: "bo" }, { 2: "   " });
  assert.equal(rSuaRong.duDieuKien, false);
  assert.equal(rSuaRong.maLoi, "con_muc_can_xac_nhan");
  assert.deepEqual(rSuaRong.chuaXacNhanIds, [2]);

  // 4. Mệnh đề thân không có evidenceTurns và chưa được sửa/bỏ -> chặn vì thiếu căn cứ
  const rThieuLuot = kiemTraDieuKienKyDuyet(
    [
      { id: 1, status: "than", evidenceTurns: [2] },
      { id: 4, status: "than", evidenceTurns: [] },
    ],
    {},
    {},
  );
  assert.equal(rThieuLuot.duDieuKien, false);
  assert.equal(rThieuLuot.maLoi, "thieu_can_cu_luot");
  assert.deepEqual(rThieuLuot.chuaXacNhanIds, [4]);

  // 5. Tất cả mệnh đề đều bị bác sĩ bấm "bo" -> không còn căn cứ hợp lệ để hoàn tất
  const rBoHet = kiemTraDieuKienKyDuyet(props, { 1: "bo", 2: "bo", 3: "bo" }, {});
  assert.equal(rBoHet.duDieuKien, false);
  assert.equal(rBoHet.maLoi, "da_bo_het_menh_de");

  // 6. Khi toàn bộ mục Cần xác nhận đã được bác sĩ Xác nhận ("giu"), Sửa hợp lệ ("sua") hoặc Bỏ ("bo") -> cho phép ký duyệt!
  const rHopLe = kiemTraDieuKienKyDuyet(
    props,
    { 2: "sua", 3: "bo" },
    { 2: "Mẹ bệnh nhân dị ứng Penicillin (tiền sử gia đình)" },
  );
  assert.equal(rHopLe.duDieuKien, true);
  assert.equal(rHopLe.soCanXacNhanChuaDuyet, 0);
});
