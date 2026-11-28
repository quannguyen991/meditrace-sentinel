import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";

// asr.ts mở CSDL khi nạp: dùng CSDL tạm, không lắng nghe cổng.
const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "meditrace-asr-ngan-sach-"));
process.env.MEDITRACE_DB = path.join(tmpDir, "asr-ngan-sach.db");
process.env.MEDITRACE_KHONG_LISTEN = "1";

const { canhBaoCaGiaoDien, menhDeChoGiaoDien, nganSachMenhDeGiaoDien } = await import("./asr");

const cb = (ma: string, ket_luan = "nghi_rui_ro", muc_do = "trung") => ({
  ma, nhom: "X", nhom_ten: "x", tieu_de: `tiêu đề ${ma}`, giai_thich: "", ly_do: "lý do", luot: [1], trich: ["câu"],
  muc_do, bat_dinh: "trung", ket_luan, tin_cay: "on_dinh", anh_huong_trang_thai: false, phu: [], phu_tieu_de: [],
  bo_phat_hien: "t",
});

const banGhi = (canhBao: any) => ({
  phat_bieu: [{ id: 1, noi_dung: "ho ba ngày", chu_the_id: 0, bang_chung: [2], trich_dan: ["ho ba ngày"] }],
  ghi_chu: [{ id: 1, muc: "BỆNH SỬ", van: "ho ba ngày" }],
  canh_bao: canhBao,
});

test("canh_bao_hien / canh_bao_gap -> warningsShown / warningsFolded", () => {
  const [p] = menhDeChoGiaoDien(banGhi({
    theo_phat_bieu: { "1": {
      chinh: cb("SPEAKER_SUBJECT_MISMATCH"), khac: [], phu: [],
      canh_bao_hien: [cb("NEGATION_FLIP", "loi_phat_hien", "cao")],
      canh_bao_gap: [cb("SPEAKER_SUBJECT_MISMATCH", "nghi_rui_ro", "thap"), cb("DUPLICATE_INFORMATION", "can_xem", "thap")],
    } },
  }));
  assert.equal(p.warning?.code, "SPEAKER_SUBJECT_MISMATCH");        // trường cũ giữ nguyên
  assert.deepEqual(p.warningsShown?.map((w) => w?.code), ["NEGATION_FLIP"]);
  assert.deepEqual(p.warningsFolded?.map((w) => w?.code), ["SPEAKER_SUBJECT_MISMATCH", "DUPLICATE_INFORMATION"]);
  assert.equal(p.warningsShown?.[0]?.title, "tiêu đề NEGATION_FLIP");
});

test("thiếu trường ngân sách: không thêm warningsShown (giao diện dùng cách cũ)", () => {
  const [p] = menhDeChoGiaoDien(banGhi({ theo_phat_bieu: { "1": { chinh: cb("WRONG_SUBJECT"), khac: [], phu: [] } } }));
  assert.equal("warningsShown" in p, false);
  assert.equal("warningsFolded" in p, false);
  assert.deepEqual(nganSachMenhDeGiaoDien(undefined), {});
});

test("toan_ca_ngan_sach -> caseWarningsShown / caseWarningsFolded, caseWarnings như cũ", () => {
  const toan = [cb("OMITTED_MEDICATION", "nghi_rui_ro", "cao"), cb("POSSIBLE_IMPORTANT_OMISSION", "can_xem", "thap")];
  const moi = canhBaoCaGiaoDien({
    toan_ca: toan,
    toan_ca_ngan_sach: { canh_bao_hien: [toan[0]], canh_bao_gap: [toan[1]] },
  });
  assert.deepEqual(moi.caseWarnings.map((w) => w?.code), ["OMITTED_MEDICATION"]);
  assert.deepEqual(moi.caseWarningsShown?.map((w) => w?.code), ["OMITTED_MEDICATION"]);
  assert.deepEqual(moi.caseWarningsFolded?.map((w) => w?.code), ["POSSIBLE_IMPORTANT_OMISSION"]);
  const cu = canhBaoCaGiaoDien({ toan_ca: toan });
  assert.equal("caseWarningsShown" in cu, false);
  assert.deepEqual(canhBaoCaGiaoDien(undefined), { caseWarnings: [] });
});
