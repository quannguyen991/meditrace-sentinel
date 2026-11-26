import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { chuanSo, soLech } from "./kiem-dinh-so";
import { datLaiBoDemWHO, docBoDemWHO, timWHO, vanIRIS } from "./nguon-ngoai";

test("chuanSo: giu nguyen so thap phan tieng Anh 0.125 mg va 1.250 g, chi bo dau cham nghin kieu Viet", () => {
  assert.equal(chuanSo("Digoxin 0.125 mg once daily"), "digoxin 0.125 mg once daily");
  assert.equal(chuanSo("Vancomycin 1.250 g IV"), "vancomycin 1.250 g iv");
  assert.equal(chuanSo("Digoxin 0,125 mg uống"), "digoxin 0.125 mg uống");
  assert.equal(chuanSo("tiểu cầu dưới 100.000"), "tiểu cầu <100000");
  assert.equal(chuanSo("liều 1.000.000 IU"), "liều 1000000 iu");
  assert.equal(chuanSo("tối đa 4.000 mg/ngày"), "≤4000 mg/ngày");
  assert.equal(chuanSo("metformin tối đa 1.500 mg/ngày"), "metformin ≤1500 mg/ngày");
  assert.equal(chuanSo("ibuprofen 2.400 mg/ngày"), "ibuprofen 2400 mg/ngày");
  assert.equal(chuanSo("at most 4,000 mg daily"), "≤4000 mg daily");
});

test("soLech: quy doi dung bac don vi (1 g = 1000 mg = 1_000_000 mcg, 1 l = 1000 ml, toc do truyen)", () => {
  assert.deepEqual(soLech("Dùng paracetamol 1 g mỗi lần", "Recommended dose: acetaminophen 1000 mg orally"), []);
  assert.deepEqual(soLech("Liều 1.000.000 mcg", "Dose: 1 g IV"), []);
  assert.deepEqual(soLech("Digoxin 0,125 mg/ngày", "Usual maintenance dose is 0.125 mg daily"), []);
  assert.deepEqual(soLech("Digoxin 125 mcg uống", "Maintenance dose: 0.125 mg orally"), []);
  assert.deepEqual(soLech("Vancomycin 1250 mg truyền tĩnh mạch", "Administer vancomycin 1.250 g IV"), []);
  assert.deepEqual(soLech("Metformin tối đa 1.500 mg/ngày", "Maximum metformin dose 1500 mg daily"), []);
  assert.deepEqual(soLech("Bù 0,5 lít dịch", "Infuse 500 ml crystalloid"), []);
  assert.deepEqual(soLech("Liều từ 50 đến 100 mg", "Dosage: 50–100 mg every 6 hours"), []);
  assert.deepEqual(soLech("Liều 10 mg/kg hoặc 15 mg/kg", "Pediatric dose: 10-15 mg/kg per dose"), []);
  assert.deepEqual(soLech("Truyền noradrenaline 1 mcg/kg/phút", "Infusion rate: 60 mcg/kg/hour"), []);
});

test("soLech: bat buoc phat hien lech khi sai khac don vi hoac gap 60x/1000x lan lieu (125 g vs 125 mcg, 50 mg vs 50 ml, phut vs gio, mEq, mmol/mol)", () => {
  const lech1 = soLech("Dùng digoxin 125 g mỗi ngày", "Maintenance dose: digoxin 125 mcg daily");
  assert.equal(lech1.length, 1);
  assert.match(lech1[0], /125\s*g/);

  const lech2 = soLech("Tiêm 50 mg dung dịch", "Administer 50 ml solution");
  assert.equal(lech2.length, 1);
  assert.match(lech2[0], /50\s*mg/);

  const lech3 = soLech("Digoxin 125 mg uống", "Digoxin 0.125 mg tablets");
  assert.equal(lech3.length, 1);
  assert.match(lech3[0], /125\s*mg/);

  const lech4 = soLech("Vancomycin 1250 g truyền", "Vancomycin 1.250 g IV q12h");
  assert.equal(lech4.length, 1);
  assert.match(lech4[0], /1250\s*g/);

  const lech5 = soLech("Amoxicillin 20 mg/kg", "Adult dose: amoxicillin 20 mg");
  assert.equal(lech5.length, 1);
  assert.match(lech5[0], /20\s*mg\/kg/);

  // Số 1 khi đi kèm đơn vị khối lượng (1 g vs 1 mg) vẫn bắt buộc kiểm tra, không được bỏ qua!
  const lech6 = soLech("Tiêm adrenaline 1 g tiêm bắp", "Epinephrine 0.5 mg or max 1 mg IM");
  assert.equal(lech6.length, 1);
  assert.match(lech6[0], /1\s*g/);

  // Đảo chiều dấu so sánh
  const lech7 = soLech("Liều trên 4000 mg/ngày", "Maximum daily dose is at most 4,000 mg");
  assert.equal(lech7.length, 1);
  assert.match(lech7[0], />4000\s*mg/);

  // Tốc độ truyền vận mạch lệch phút vs giờ (gấp 60 lần liều!)
  const lech8 = soLech("Truyền noradrenaline 0.1 mcg/kg/phút", "Noradrenaline infusion: 0.1 mcg/kg/hour");
  assert.equal(lech8.length, 1);
  assert.match(lech8[0], /0\.1\s*mcg\/kg\/phút/);

  // Điện giải mEq vs ml và HbA1c mmol/mol vs %
  const lech9 = soLech("Bù kali 40 mEq", "Administer 40 ml solution");
  assert.equal(lech9.length, 1);
  assert.match(lech9[0], /40\s*meq/);

  const lech10 = soLech("Mục tiêu HbA1c <7 mmol/mol", "Target HbA1c <7%");
  assert.equal(lech10.length, 1);
  assert.match(lech10[0], /<7\s*mmol\/mol/);
});

test("vanIRIS: chan tuyet doi Path Traversal qua UUID va doc bo dem bat dong bo", async () => {
  const badUuids = [
    "",
    "../package.json",
    "../../etc/passwd",
    "12345",
    "a1b2c3d4-e5f6-7890-abcd-ef1234567890/../../secret",
    "a1b2c3d4-e5f6-7890-abcd-ef1234567890;rm -rf",
  ];
  for (const bad of badUuids) {
    await assert.rejects(() => vanIRIS(bad), /UUID IRIS không hợp lệ/);
  }

  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "meditrace-iris-"));
  try {
    const validUuid = "a1b2c3d4-e5f6-4890-abcd-ef1234567890";
    fs.writeFileSync(path.join(tmp, `${validUuid}.txt`), "WHO clinical guideline cached content", "utf-8");
    const content = await vanIRIS(validUuid, tmp);
    assert.equal(content, "WHO clinical guideline cached content");
  } finally {
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});

test("timWHO: khong cache mang rong WHO_DS suot 24 gio khi tai loi hoac HTML rong", async () => {
  datLaiBoDemWHO();
  await timWHO("dengue", "điều trị sốt xuất huyết", async () => {
    throw new Error("mạng chập chờn");
  });
  assert.equal(docBoDemWHO(), null, "tải lỗi không được gán mảng rỗng vào WHO_DS");

  await timWHO("dengue", "điều trị sốt xuất huyết", async () => "<html><body>Empty maintenance page</body></html>");
  assert.equal(docBoDemWHO(), null, "HTML không có mục nào không được khoá bộ đệm rỗng 24h");

  const kq = await timWHO("dengue", "dengue symptoms", async (url) => {
    if (url.includes("iris.who.int")) return "{}";
    if (url.endsWith("/fact-sheets")) {
      return '<a href="/news-room/fact-sheets/detail/dengue-and-severe-dengue">Dengue</a>';
    }
    return "<title>Dengue and severe dengue - World Health Organization</title><p>Dengue is a viral infection transmitted by mosquitoes to people in tropical regions.</p>";
  });
  assert.ok(docBoDemWHO() && docBoDemWHO()!.ds.length === 1);
  assert.equal(kq.length, 1);
  assert.equal(kq[0].nguon, "WHO");
  datLaiBoDemWHO();
});
