/**
 * Kiểm bộ điều phối. Chạy: npx tsx may-chu/tro-ly/dieu-phoi.test.ts  (trong thư mục web/)
 */
import assert from "node:assert/strict";
import { xayCaAnDanh } from "./an-danh";
import { type Phu, chayKePhach, kePhachDuPhong, kiemKePhach, lapKePhach, maBuoc } from "./dieu-phoi";
import type { MucKePhach, TacTuMa, TienTrinh, YeuCauTroLy } from "./kieu";

const TAT_CA: TacTuMa[] = ["tim_kiem", "tra_loi", "doi_chieu", "chu_de_can_ban", "doi_chieu_thuoc"];
const bat = new Set<TacTuMa>(TAT_CA);

const yeuCau = (): YeuCauTroLy => ({
  cauHoi: "đau đầu kéo dài kèm sốt nên làm gì",
  menhDe: [
    { text: "bà: đau đầu ba ngày", section: "BỆNH SỬ HIỆN TẠI" },
    { text: "bà: penicillin V 500 mg", section: "THUỐC ĐANG DÙNG", drug: "penicillin V 500 mg" },
    { text: "bà: dị ứng penicillin", section: "DỊ ỨNG" },
  ],
  nguCanh: { tuoi: 34, gioi: "nữ" },
  batTacTu: TAT_CA,
});

const chuoiTT = (): TienTrinh => ({ keHoach: [], keHoachTuMoHinh: false, xemTruoc: null, buoc: [] });
const KH_DAY_DU: MucKePhach[] = [
  { tacTu: "tim_kiem", nhiemVu: "tìm", phuThuoc: [] },
  { tacTu: "tra_loi", nhiemVu: "trả lời", phuThuoc: [0] },
  { tacTu: "doi_chieu", nhiemVu: "đối chiếu", phuThuoc: [1] },
  { tacTu: "chu_de_can_ban", nhiemVu: "chủ đề", phuThuoc: [] },
  { tacTu: "doi_chieu_thuoc", nhiemVu: "thuốc", phuThuoc: [] },
];

type Nhat = { goi: string[]; goiNgoai: Array<{ he: string; nguoi: string }> };
function phuGia(tuyChon: Partial<{ ngoaiMo: boolean; xetThieu: boolean; timLoi: boolean; goiNgoaiText: string }> = {}) {
  const nhat: Nhat = { goi: [], goiNgoai: [] };
  const o = { ngoaiMo: true, xetThieu: false, timLoi: false, goiNgoaiText: "", ...tuyChon };
  let tick = 0;
  let soSoan = 0;
  const phu: Phu = {
    async goiNgoai(he, nguoi) {
      nhat.goi.push("goiNgoai");
      nhat.goiNgoai.push({ he, nguoi });
      const text = o.goiNgoaiText || JSON.stringify({ thieu_can_cu: o.xetThieu ? [{ y: 1, ly_do: "không có trong tài liệu" }] : [] });
      return { text, model: "gia", usage: { prompt_tokens: 10, completion_tokens: 5 }, seconds: 1 };
    },
    async datTuKhoa() {
      nhat.goi.push("datTuKhoa");
      return { tuKhoa: { pubmed: "x" }, token: 3, giay: 1 };
    },
    async timTaiLieu() {
      nhat.goi.push("timTaiLieu");
      if (o.timLoi) throw new Error("nguồn tìm lỗi");
      return { taiLieu: [{ so: 1, ten: "T1", noiDung: "nội dung 1" }], daTra: [{ nguon: "PubMed", so: 1 }], loiTim: [], boLacDe: 0, tuKhoaRa: {} };
    },
    async soanTraLoi() {
      nhat.goi.push("soanTraLoi");
      soSoan++;
      return {
        traLoi: { answer: `trả lời lần ${soSoan}`, warning: null, cauTruc: { phuong_an: [{ ten: "pa", noi_dung: "nd", nguon: [1], lech: [] }], an_toan: [] } },
        token: 7,
        giay: 2,
      };
    },
    ngoaiMo: () => o.ngoaiMo,
    bay: () => ++tick,
  };
  return { phu, nhat, soSoan: () => soSoan };
}

// 1. kiemKePhach (Review Focus 3)
{
  const ok = [
    { tacTu: "tim_kiem", nhiemVu: "x", phuThuoc: [] },
    { tacTu: "tra_loi", nhiemVu: "y", phuThuoc: [0] },
  ];
  assert.equal(kiemKePhach(ok, bat)?.length, 2);
  assert.equal(kiemKePhach([{ tacTu: "hack", nhiemVu: "x", phuThuoc: [] }], bat), null, "tác tử lạ");
  assert.equal(kiemKePhach([{ tacTu: "dieu_phoi", nhiemVu: "x", phuThuoc: [] }], bat), null, "không tự xếp điều phối vào kế hoạch");
  assert.equal(
    kiemKePhach([{ tacTu: "tim_kiem", nhiemVu: "x", phuThuoc: [1] }, { tacTu: "tra_loi", nhiemVu: "y", phuThuoc: [0] }], bat),
    null,
    "vòng",
  );
  assert.equal(kiemKePhach([{ tacTu: "tim_kiem", nhiemVu: "x", phuThuoc: [0] }], bat), null, "tự phụ thuộc");
  assert.equal(kiemKePhach(Array.from({ length: 7 }, () => ({ tacTu: "chu_de_can_ban", nhiemVu: "x", phuThuoc: [] })), bat), null, "7 mục");
  assert.equal(kiemKePhach([], bat), null, "rỗng");
  assert.equal(kiemKePhach([{ tacTu: "tra_loi", nhiemVu: "y", phuThuoc: [] }], bat), null, "trả lời không có tìm kiếm");
  assert.equal(
    kiemKePhach([{ tacTu: "tim_kiem", nhiemVu: "x", phuThuoc: [] }, { tacTu: "doi_chieu", nhiemVu: "y", phuThuoc: [0] }], bat),
    null,
    "đối chiếu không đứng sau trả lời",
  );
  assert.equal(
    kiemKePhach([{ tacTu: "tim_kiem", nhiemVu: "x", phuThuoc: [] }, { tacTu: "tim_kiem", nhiemVu: "y", phuThuoc: [] }], bat),
    null,
    "trùng tác tử",
  );
  assert.equal(kiemKePhach("không phải mảng", bat), null);
  assert.equal(kiemKePhach([{ tacTu: "tim_kiem", nhiemVu: "x", phuThuoc: [5] }], bat), null, "chỉ số ngoài phạm vi");
  assert.equal(kiemKePhach([{ tacTu: "tim_kiem", nhiemVu: 5, phuThuoc: [] }], bat), null, "nhiemVu không phải chuỗi");
  assert.equal(kiemKePhach([{ tacTu: "tim_kiem", nhiemVu: "x", phuThuoc: [] }], new Set<TacTuMa>(["tra_loi"])), null, "tác tử đang tắt");
}

// 2. kế phác dự phòng theo luật
{
  const day = kePhachDuPhong({ coMenhDe: true, batTacTu: bat });
  assert.deepEqual(day.map((m) => m.tacTu), ["chu_de_can_ban", "doi_chieu_thuoc", "tim_kiem", "tra_loi", "doi_chieu"]);
  assert.deepEqual(day[3].phuThuoc, [2]);
  assert.deepEqual(day[4].phuThuoc, [3]);
  assert.ok(kiemKePhach(day, bat), "dự phòng phải hợp lệ");
  assert.deepEqual(kePhachDuPhong({ coMenhDe: false, batTacTu: bat }).map((m) => m.tacTu), ["tim_kiem", "tra_loi", "doi_chieu"]);
  // mô hình ngoài đóng vẫn có chuỗi ngoài trong kế phác (sẽ hiện "bỏ qua"), nhưng nếu người dùng tắt tác tử thì không có
  assert.deepEqual(
    kePhachDuPhong({ coMenhDe: true, batTacTu: new Set<TacTuMa>(["chu_de_can_ban", "doi_chieu_thuoc"]) }).map((m) => m.tacTu),
    ["chu_de_can_ban", "doi_chieu_thuoc"],
  );
  assert.deepEqual(
    kePhachDuPhong({ coMenhDe: true, batTacTu: new Set<TacTuMa>(["chu_de_can_ban"]) }).map((m) => m.tacTu),
    ["chu_de_can_ban"],
  );
}

// 3. lapKePhach: không phải JSON -> dự phòng; JSON đúng -> mô hình; điều phối không thấy nội dung ca (Review Focus 2)
(async () => {
  const yc = yeuCau();
  const ca = xayCaAnDanh(yc.menhDe, yc.nguCanh);
  {
    const { phu } = phuGia({ goiNgoaiText: "xin chào" });
    const r = await lapKePhach(phu, yc, ca, yc.cauHoi);
    assert.equal(r.tuMoHinh, false);
    assert.ok(r.keHoach.length >= 1);
  }
  {
    const { phu, nhat } = phuGia({
      goiNgoaiText: JSON.stringify({ keHoach: [{ tacTu: "chu_de_can_ban", nhiemVu: "x", phuThuoc: [] }] }),
    });
    const r = await lapKePhach(phu, yc, ca, yc.cauHoi);
    assert.equal(r.tuMoHinh, true);
    assert.equal(r.keHoach.length, 1);
    const nguoi = nhat.goiNgoai[0].nguoi;
    for (const d of ca.dong) assert.ok(!nguoi.includes(d), `điều phối không được thấy: ${d}`);
    assert.ok(nguoi.includes(yc.cauHoi));
  }
  {
    const { phu, nhat } = phuGia({ ngoaiMo: false });
    const r = await lapKePhach(phu, yc, ca, yc.cauHoi);
    assert.equal(nhat.goi.length, 0, "ngoài đóng thì không gọi điều phối");
    assert.equal(r.tuMoHinh, false);
  }

  // 3b. người dùng tắt hết tác tử cần mô hình ngoài: không gọi điều phối (không gửi câu hỏi đi vô ích)
  {
    const { phu, nhat } = phuGia();
    const yc3 = { ...yeuCau(), batTacTu: ["chu_de_can_ban", "doi_chieu_thuoc"] as TacTuMa[] };
    const r = await lapKePhach(phu, yc3, ca, yc3.cauHoi);
    assert.equal(nhat.goi.length, 0);
    assert.deepEqual(r.keHoach.map((m) => m.tacTu), ["chu_de_can_ban", "doi_chieu_thuoc"]);
  }

  // 4. chạy kế hoạch: thứ tự, tích chỉ sau khi hàm trả về
  {
    const g = phuGia();
    const tt = chuoiTT();
    const trangThai: Record<string, string[]> = {};
    let thayKhiDatTuKhoa = "";
    const goc = g.phu.datTuKhoa;
    g.phu.datTuKhoa = async (q) => {
      thayKhiDatTuKhoa = last?.buoc.find((b) => b.ma === maBuoc(0, "tim_kiem", "dat_tu_khoa"))?.trangThai ?? "";
      return goc(q);
    };
    let last: TienTrinh | undefined;
    const ghi = (t: TienTrinh) => {
      last = t;
      for (const b of t.buoc) {
        const d = (trangThai[b.ma] ||= []);
        if (d[d.length - 1] !== b.trangThai) d.push(b.trangThai);
      }
    };
    const kq = await chayKePhach(g.phu, yeuCau(), KH_DAY_DU, tt, ghi);
    assert.equal(thayKhiDatTuKhoa, "dang", "trước khi hàm trả về, bước còn 'dang'");
    for (const [ma, ds] of Object.entries(trangThai)) assert.deepEqual(ds.filter((x) => x !== "cho"), ["dang", "xong"], ma);
    // thứ tự gọi: tìm -> soạn trước khi xét
    const iDat = g.nhat.goi.indexOf("datTuKhoa");
    const iTim = g.nhat.goi.indexOf("timTaiLieu");
    const iSoan = g.nhat.goi.indexOf("soanTraLoi");
    const iXet = g.nhat.goi.indexOf("goiNgoai");
    assert.ok(iDat < iTim && iTim < iSoan && iSoan < iXet, g.nhat.goi.join(","));
    assert.equal(kq.phan.length, 5);
    assert.ok(kq.phan.filter((p) => p.tacTu !== "doi_chieu_thuoc").every((p) => !p.canhBao), JSON.stringify(kq.phan.map((p) => p.canhBao)));
    assert.equal(kq.phan[1].tacTu, "tra_loi");
    assert.equal(kq.phan[1].noiDung, "trả lời lần 1");
    assert.ok(kq.thongKe.token > 0);
    // phần tại chỗ nhìn thấy mâu thuẫn thuốc–dị ứng
    const thuoc = kq.phan.find((p) => p.tacTu === "doi_chieu_thuoc");
    assert.ok(thuoc?.canhBao?.toLowerCase().includes("penicillin"), "thuốc trùng dị ứng phải được báo: " + thuoc?.canhBao);
  }

  // 5. một bước lỗi không làm hỏng tác tử khác (Review Focus 5)
  {
    const g = phuGia({ timLoi: true });
    const kq = await chayKePhach(g.phu, yeuCau(), KH_DAY_DU, chuoiTT(), () => {});
    assert.equal(kq.phan.length, 5);
    const chuDe = kq.phan.find((p) => p.tacTu === "chu_de_can_ban");
    assert.ok(chuDe && chuDe.noiDung.length > 0 && !chuDe.canhBao);
    const tim = kq.phan.find((p) => p.tacTu === "tim_kiem");
    assert.ok(tim?.canhBao?.includes("nguồn tìm lỗi"));
    assert.ok(kq.phan.find((p) => p.tacTu === "tra_loi")?.canhBao, "phần phụ thuộc cũng báo");
    assert.ok(kq.thongKe.loiGoi >= 1);
  }

  // 6. ngoài đóng: tác tử ngoài bỏ qua, tại chỗ chạy, không gọi lần nào
  {
    const g = phuGia({ ngoaiMo: false });
    const tt = chuoiTT();
    const kq = await chayKePhach(g.phu, yeuCau(), KH_DAY_DU, tt, () => {});
    assert.equal(g.nhat.goi.length, 0);
    const bo = tt.buoc.filter((b) => b.trangThai === "bo_qua");
    assert.ok(bo.length >= 4);
    assert.ok(bo.every((b) => b.ghiChu === "chưa bật mô hình ngoài"));
    assert.equal(tt.buoc.filter((b) => b.trangThai === "xong").length, 2);
    assert.ok(kq.phan.find((p) => p.tacTu === "tim_kiem")?.canhBao?.includes("chưa bật mô hình ngoài"));
  }

  // 7. chạy lại với bước đã xong: không gọi lại (Review Focus 4)
  {
    const g = phuGia();
    const tt = chuoiTT();
    tt.buoc.push({
      ma: maBuoc(0, "tim_kiem", "dat_tu_khoa"),
      tacTu: "tim_kiem",
      ten: "Đặt từ khoá tìm",
      trangThai: "xong",
      dau: { tuKhoa: { pubmed: "đã có" }, token: 3, giay: 1 },
    });
    await chayKePhach(g.phu, yeuCau(), KH_DAY_DU, tt, () => {});
    assert.ok(!g.nhat.goi.includes("datTuKhoa"), "không đặt từ khoá lần hai");
    assert.ok(g.nhat.goi.includes("timTaiLieu"));
  }

  // 8. đối chiếu sửa tối đa một lần
  {
    const g = phuGia({ xetThieu: true });
    const kq = await chayKePhach(g.phu, yeuCau(), KH_DAY_DU, chuoiTT(), () => {});
    assert.equal(g.soSoan(), 2, "soạn đúng hai lần: gốc + một lần sửa");
    assert.ok(kq.phan.find((p) => p.tacTu === "doi_chieu")?.canhBao, "vẫn thiếu căn cứ thì gắn cảnh báo");
    assert.equal(kq.phan.find((p) => p.tacTu === "tra_loi")?.noiDung, "trả lời lần 2", "phần trả lời là bản đã sửa");
  }
  {
    const g = phuGia({ xetThieu: false });
    await chayKePhach(g.phu, yeuCau(), KH_DAY_DU, chuoiTT(), () => {});
    assert.equal(g.soSoan(), 1, "không thiếu thì không sửa");
  }

  // 9. hết giờ một bước thì bước đó lỗi, việc vẫn kết thúc
  {
    const g = phuGia();
    g.phu.timTaiLieu = () => new Promise(() => {});
    const kq = await chayKePhach(g.phu, yeuCau(), KH_DAY_DU, chuoiTT(), () => {}, { hetGioMs: 30 });
    assert.ok(kq.phan.find((p) => p.tacTu === "tim_kiem")?.canhBao?.includes("hết giờ"));
    assert.ok(kq.phan.find((p) => p.tacTu === "chu_de_can_ban"));
  }

  // 10. câu hỏi còn danh tính: tác tử ngoài không gọi
  {
    const g = phuGia();
    const yc2 = yeuCau();
    yc2.cauHoi = "chị Lan đau đầu";
    const kq = await chayKePhach(g.phu, yc2, KH_DAY_DU, chuoiTT(), () => {});
    assert.equal(g.nhat.goi.length, 0);
    assert.ok(kq.phan.find((p) => p.tacTu === "tim_kiem")?.canhBao?.includes("danh tính"));
    assert.ok(kq.phan.find((p) => p.tacTu === "chu_de_can_ban"), "tác tử tại chỗ vẫn chạy");
  }

  console.log("dieu-phoi.test.ts: tất cả đều qua");
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
