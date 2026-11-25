/**
 * Thử tích hợp đầu cuối với mô hình ngoài GIẢ: nhét tên và số điện thoại vào mệnh đề, khẳng định không
 * lời gọi ra ngoài nào chứa chúng. Chạy: npx tsx may-chu/tro-ly/tich-hop.test.ts  (trong thư mục web/)
 */
import assert from "node:assert/strict";
import { DatabaseSync } from "node:sqlite";
import { xuLyViecTroLy } from "./chay-viec";
import type { Phu } from "./dieu-phoi";
import type { TacTuMa, YeuCauTroLy } from "./kieu";
import { taoKhoViec } from "./viec-tro-ly";

const TAT_CA: TacTuMa[] = ["tim_kiem", "tra_loi", "doi_chieu", "chu_de_can_ban", "doi_chieu_thuoc"];
const BI_MAT = ["Nguyễn Thị Hoa", "Hoa", "0912345678", "Cầu Giấy", "Lan", "12/10/1980", "giáo viên"];

// Tên một chữ ("Hoa", "Lan") dò theo ranh giới từ, kẻo trùng nhầm với "keHoach" trong lời nhắc hệ thống.
const lo = (chuoi: string, bm: string) => (/^\p{Lu}\p{Ll}+$/u.test(bm) ? new RegExp(`(?<![\\p{L}])${bm}(?![\\p{L}])`, "u").test(chuoi) : chuoi.includes(bm));

const yeuCau = (): YeuCauTroLy => ({
  cauHoi: "ho khan kéo dài ở người lớn nên làm gì tiếp",
  menhDe: [
    { text: "bà Nguyễn Thị Hoa: đau đầu ba ngày, gọi 0912345678 khi cần", section: "BỆNH SỬ HIỆN TẠI", subject: "bà Nguyễn Thị Hoa" },
    { text: "bệnh nhân: ho khan ba tuần", section: "BỆNH SỬ HIỆN TẠI", subject: "bệnh nhân", quotes: ["tôi là Hoa ở Cầu Giấy ho mãi"] } as any,
    { text: "bà: nghề giáo viên ở Cầu Giấy", section: "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI" },
    { text: "bà: tái khám ngày 12/10/1980", section: "KẾ HOẠCH ĐIỀU TRỊ" },
    { text: "chị Lan: dị ứng penicillin", section: "DỊ ỨNG" },
    { text: "bà: penicillin V 500 mg", section: "THUỐC ĐANG DÙNG", drug: "penicillin V 500 mg" },
    { text: "bà: huyết áp 120/80", section: "KHÁM LÂM SÀNG" },
  ],
  nguCanh: { tuoi: 34, gioi: "nữ" },
  batTacTu: TAT_CA,
});

function phuGia(ngoaiMo = true) {
  const guiRa: string[] = [];
  const phu: Phu = {
    async goiNgoai(he, nguoi) {
      guiRa.push(he, nguoi);
      return { text: JSON.stringify({ thieu_can_cu: [] }), model: "gia", usage: { prompt_tokens: 1, completion_tokens: 1 }, seconds: 0.1 };
    },
    async datTuKhoa(q) {
      guiRa.push(q);
      return { tuKhoa: { pubmed: "cough" }, token: 2, giay: 0.1 };
    },
    async timTaiLieu(tk, q, nguon) {
      guiRa.push(JSON.stringify([tk, q, nguon]));
      return { taiLieu: [{ so: 1, ten: "Ho kéo dài", noiDung: "nội dung" }], daTra: [], loiTim: [], boLacDe: 0, tuKhoaRa: {} };
    },
    async soanTraLoi(a) {
      guiRa.push(JSON.stringify(a));
      return { traLoi: { answer: "gợi ý có nguồn [1]", warning: null, cauTruc: { phuong_an: [], an_toan: [] } }, token: 3, giay: 0.2 };
    },
    ngoaiMo: () => ngoaiMo,
    bay: () => Date.now(),
  };
  return { phu, guiRa };
}

(async () => {
  // 1. đầu cuối: không lời gọi ra ngoài nào chứa tên, số, nơi chốn, ngày, hay chữ ngoài danh sách cho phép
  {
    const kho = taoKhoViec(new DatabaseSync(":memory:"));
    const id = kho.them(1, "k", yeuCau());
    const viec = kho.layViecTiepTheo(2)!;
    const g = phuGia();
    const nhatKy: Array<{ hanhDong: string; chiTiet: string }> = [];
    await xuLyViecTroLy(g.phu, kho, viec, (hanhDong, chiTiet) => nhatKy.push({ hanhDong, chiTiet }));

    assert.ok(g.guiRa.length >= 4, "phải có lời gọi ra ngoài để phép thử có nghĩa");
    for (const chuoi of g.guiRa) {
      for (const bm of BI_MAT) assert.ok(!lo(chuoi, bm), `lộ "${bm}" trong: ${chuoi.slice(0, 200)}`);
    }
    // nội dung được phép thì có đi ra
    assert.ok(g.guiRa.some((c) => c.includes("ho khan ba tuần")));
    assert.ok(g.guiRa.some((c) => c.includes("người lớn")));
    assert.ok(!g.guiRa.some((c) => c.includes("34")), "tuổi chính xác không đi ra");

    const s = kho.trangThai(id, 1)!;
    assert.equal(s.trangThai, "xong");
    assert.ok(s.ketQua && s.ketQua.phan.length >= 4);
    assert.ok(s.tienTrinh?.xemTruoc?.includes("ho khan ba tuần"), "bản xem trước đúng chuỗi sẽ gửi");
    for (const bm of BI_MAT) assert.ok(!lo(s.tienTrinh!.xemTruoc!, bm), `xem trước lộ "${bm}"`);
    // nhật ký: có một dòng, không chứa chuỗi đã gửi
    assert.equal(nhatKy.length, 1);
    assert.ok(!nhatKy[0].chiTiet.includes("ho khan"));
    assert.ok(/ky_tu=\d+/.test(nhatKy[0].chiTiet), nhatKy[0].chiTiet);
  }

  // 2. ngoài đóng: không lời gọi nào ra ngoài, hai tác tử tại chỗ vẫn có kết quả
  {
    const kho = taoKhoViec(new DatabaseSync(":memory:"));
    const id = kho.them(1, "k", yeuCau());
    const g = phuGia(false);
    await xuLyViecTroLy(g.phu, kho, kho.layViecTiepTheo(2)!, () => {});
    assert.equal(g.guiRa.length, 0);
    const kq = kho.trangThai(id, 1)!.ketQua!;
    assert.ok(kq.phan.some((p) => p.tacTu === "chu_de_can_ban" && p.noiDung));
    assert.ok(kq.phan.some((p) => p.tacTu === "tim_kiem" && p.canhBao?.includes("chưa bật mô hình ngoài")), "tác tử ngoài hiện lý do bị bỏ qua");
    assert.ok(kq.phan.some((p) => p.tacTu === "doi_chieu_thuoc" && p.canhBao?.toLowerCase().includes("penicillin")));
  }

  // 3. phu ném lỗi bất ngờ ở lúc lập kế phác: việc vẫn kết thúc (dự phòng), không treo
  {
    const kho = taoKhoViec(new DatabaseSync(":memory:"));
    const id = kho.them(1, "k", yeuCau());
    const g = phuGia();
    g.phu.goiNgoai = async () => {
      throw new Error("mạng chập chờn");
    };
    await xuLyViecTroLy(g.phu, kho, kho.layViecTiepTheo(2)!, () => {});
    assert.equal(kho.trangThai(id, 1)!.trangThai, "xong");
  }

  // 4. chạy lại sau khởi động: kế phác đã ghi được giữ, điều phối không bị gọi lần hai
  {
    const kho = taoKhoViec(new DatabaseSync(":memory:"));
    const id = kho.them(1, "k", yeuCau());
    const g1 = phuGia();
    g1.phu.timTaiLieu = async () => {
      throw new Error("giả lập sập giữa chừng");
    };
    // chạy một phần rồi "sập": ta mô phỏng bằng cách ghi tiến trình sau lần chạy đầu rồi đưa việc về chờ
    const v1 = kho.layViecTiepTheo(2)!;
    await xuLyViecTroLy(g1.phu, kho, v1, () => {});
    const tt = kho.trangThai(id, 1)!.tienTrinh!;
    assert.ok(tt.keHoach.length > 0, "kế phác đã được ghi");
    // việc mới với tiến trình có sẵn: không gọi điều phối lần nữa
    const kho2 = taoKhoViec(new DatabaseSync(":memory:"));
    const id2 = kho2.them(1, "k", yeuCau());
    kho2.layViecTiepTheo(2);
    kho2.ghiTienTrinh(id2, { ...tt, buoc: [] });
    kho2.khoiPhuc();
    const g2 = phuGia();
    let soDieuPhoi = 0;
    const goc = g2.phu.goiNgoai;
    g2.phu.goiNgoai = async (he, nguoi, max) => {
      if (he.includes("bộ điều phối")) soDieuPhoi++;
      return goc(he, nguoi, max);
    };
    await xuLyViecTroLy(g2.phu, kho2, kho2.layViecTiepTheo(2)!, () => {});
    assert.equal(soDieuPhoi, 0, "kế phác đã có thì không gọi điều phối lại");
  }

  console.log("tich-hop.test.ts: tất cả đều qua");
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
