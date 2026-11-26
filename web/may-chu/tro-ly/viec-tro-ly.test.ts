/**
 * Kiểm hàng đợi việc trợ lý. Chạy: npx tsx may-chu/tro-ly/viec-tro-ly.test.ts  (trong thư mục web/)
 */
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { DatabaseSync } from "node:sqlite";
import type { KetQuaTroLy, TienTrinh, YeuCauTroLy } from "./kieu";
import { taoKhoViec } from "./viec-tro-ly";

const moi = () => taoKhoViec(new DatabaseSync(":memory:"));
const yc = (cau = "đau đầu kéo dài"): YeuCauTroLy => ({
  cauHoi: cau,
  menhDe: [{ text: "bệnh nhân: đau đầu", section: "BỆNH SỬ HIỆN TẠI" }],
  nguCanh: {},
  batTacTu: ["tim_kiem", "tra_loi", "doi_chieu", "chu_de_can_ban", "doi_chieu_thuoc"],
});
const tt = (...buoc: Array<[string, string]>): TienTrinh => ({
  keHoach: [],
  keHoachTuMoHinh: false,
  xemTruoc: null,
  buoc: buoc.map(([tacTu, trangThai], i) => ({ ma: `b${i}`, tacTu: tacTu as any, ten: `bước ${i}`, trangThai: trangThai as any })),
});
const kq: KetQuaTroLy = { phan: [{ tacTu: "chu_de_can_ban", ten: "Chủ đề cần bàn", noiDung: "ok" }], thongKe: { token: 10, giay: 1, loiGoi: 0 } };

// 1. thêm hai lần cùng khoá -> cùng id; người khác hoặc khoá khác -> id khác (Review Focus 6)
{
  const k = moi();
  const a = k.them(1, "khoa-A", yc());
  assert.equal(k.them(1, "khoa-A", yc()), a);
  assert.notEqual(k.them(1, "khoa-B", yc()), a);
  assert.notEqual(k.them(2, "khoa-A", yc()), a);
}

// 2. lấy tối đa N việc cùng lúc, hết chỗ thì null; việc xong nhường chỗ
{
  const k = moi();
  const a = k.them(1, "a", yc("a"));
  const b = k.them(1, "b", yc("b"));
  const c = k.them(1, "c", yc("c"));
  const x = k.layViecTiepTheo(2);
  assert.equal(x?.id, a);
  assert.equal(x?.yeuCau.cauHoi, "a");
  assert.equal(x?.tienTrinh, null);
  assert.equal(k.layViecTiepTheo(2)?.id, b);
  assert.equal(k.layViecTiepTheo(2), null, "đã có hai việc đang chạy");
  k.xong(a, kq);
  assert.equal(k.layViecTiepTheo(2)?.id, c, "việc xong nhường chỗ");
  assert.equal(k.trangThai(a, 1)?.trangThai, "xong");
  assert.deepEqual(k.trangThai(a, 1)?.ketQua, kq);
}

// 3. ghi tiến trình rồi khởi động lại: giữ nguyên tiến trình, đưa việc về chờ (Review Focus 4)
{
  const k = moi();
  const id = k.them(1, "a", yc());
  k.layViecTiepTheo(2);
  const t = tt(["chu_de_can_ban", "xong"], ["tim_kiem", "dang"]);
  k.ghiTienTrinh(id, t);
  assert.deepEqual(k.khoiPhuc(), { chayLai: 1, thatBai: 0 });
  const s = k.trangThai(id, 1);
  assert.equal(s?.trangThai, "cho_chay");
  assert.deepEqual(s?.tienTrinh, t);
  const lai = k.layViecTiepTheo(2);
  assert.equal(lai?.id, id);
  assert.deepEqual(lai?.tienTrinh, t, "chạy lại nhận đúng tiến trình đã ghi");
}

// 4. ngưỡng chạy lại: việc có bước tốn tiền (tim_kiem...) tối đa 1 lần chạy lại; việc tại chỗ tối đa 2
{
  const k = moi();
  const dat = k.them(1, "dat", yc("dat"));
  k.layViecTiepTheo(5);
  k.ghiTienTrinh(dat, tt(["tim_kiem", "xong"]));
  assert.deepEqual(k.khoiPhuc(), { chayLai: 1, thatBai: 0 });
  k.layViecTiepTheo(5);
  assert.deepEqual(k.khoiPhuc(), { chayLai: 0, thatBai: 1 });
  const s = k.trangThai(dat, 1);
  assert.equal(s?.trangThai, "that_bai");
  assert.equal(s?.ma, "crash_recovery_exhausted");

  const re = k.them(1, "re", yc("re"));
  for (let i = 0; i < 2; i++) {
    k.layViecTiepTheo(5);
    k.ghiTienTrinh(re, tt(["chu_de_can_ban", "dang"]));
    assert.deepEqual(k.khoiPhuc(), { chayLai: 1, thatBai: 0 }, `lần ${i + 1}`);
  }
  k.layViecTiepTheo(5);
  assert.deepEqual(k.khoiPhuc(), { chayLai: 0, thatBai: 1 });
}

// 5. chỉ chủ việc đọc được; xoá đúng chủ
{
  const k = moi();
  const id = k.them(1, "a", yc());
  assert.equal(k.trangThai(id, 2), null);
  assert.equal(k.trangThai(9999, 1), null);
  k.xoa(id, 2);
  assert.ok(k.trangThai(id, 1));
  k.xoa(id, 1);
  assert.equal(k.trangThai(id, 1), null);
}

// 6. lỗi và dọn việc cũ
{
  const k = moi();
  const a = k.them(1, "a", yc());
  const b = k.them(1, "b", yc("b"));
  k.layViecTiepTheo(5);
  k.loi(a, "model_loi");
  assert.equal(k.trangThai(a, 1)?.trangThai, "that_bai");
  assert.equal(k.trangThai(a, 1)?.ma, "model_loi");
  assert.equal(k.donViecCu(60 * 60_000), 0);
  assert.equal(k.donViecCu(-1), 1);
  assert.equal(k.trangThai(b, 1)?.trangThai, "cho_chay", "việc chờ không bị dọn");
}

// 7. còn nguyên sau khi đóng và mở lại tệp CSDL
{
  const tep = path.join(fs.mkdtempSync(path.join(os.tmpdir(), "vtl-")), "t.db");
  const d1 = new DatabaseSync(tep);
  const k1 = taoKhoViec(d1);
  const id = k1.them(7, "a", yc("còn không"));
  k1.layViecTiepTheo(2);
  k1.ghiTienTrinh(id, tt(["tim_kiem", "xong"]));
  d1.close();
  const d2 = new DatabaseSync(tep);
  const k2 = taoKhoViec(d2);
  assert.deepEqual(k2.khoiPhuc(), { chayLai: 1, thatBai: 0 });
  const lai = k2.layViecTiepTheo(2);
  assert.equal(lai?.id, id);
  assert.equal(lai?.yeuCau.cauHoi, "còn không");
  assert.equal(lai?.tienTrinh?.buoc[0].tacTu, "tim_kiem");
  d2.close();
}

// 8. Boolean(tt?.dieuPhoi) được tính là tonTien khi khôi phục + hủy việc chống ghi đè muộn
{
  const k = moi();
  const idDp = k.them(1, "dp", yc("đã gọi điều phối"));
  k.layViecTiepTheo(5);
  k.ghiTienTrinh(idDp, {
    keHoach: [{ tacTu: "tim_kiem", nhiemVu: "tìm", phuThuoc: [] }],
    keHoachTuMoHinh: true,
    buoc: [],
    xemTruoc: "x",
    dieuPhoi: { token: 42, giay: 0.4 },
  });
  // Lần sập 1 -> cho chạy lại 1 lần (ngưỡng ngoài = 1)
  assert.deepEqual(k.khoiPhuc(), { chayLai: 1, thatBai: 0 });
  k.layViecTiepTheo(5);
  // Lần sập 2 -> dừng ngay, KHÔNG cho chạy lại lần 2 như việc tại chỗ!
  assert.deepEqual(k.khoiPhuc(), { chayLai: 0, thatBai: 1 });
  assert.equal(k.trangThai(idDp, 1)?.ma, "crash_recovery_exhausted");

  // Hủy việc: sai chủ -> false; đúng chủ -> da_huy và chặn ghi đè xong/lỗi muộn
  const idHuy = k.them(1, "huy", yc("hủy giữa chừng"));
  k.layViecTiepTheo(5);
  assert.equal(k.huy(idHuy, 2), false, "người khác không hủy được");
  assert.equal(k.huy(idHuy, 1), true);
  assert.equal(k.daHuy(idHuy), true);
  k.xong(idHuy, kq);
  k.loi(idHuy, "muon");
  assert.equal(k.trangThai(idHuy, 1)?.trangThai, "da_huy", "việc đã hủy không bị xong/lỗi muộn ghi đè");
}

console.log("viec-tro-ly.test.ts: tất cả đều qua");
