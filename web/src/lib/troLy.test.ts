/**
 * Kiểm phần thuần của giao diện trợ lý. Chạy: npx tsx src/lib/troLy.test.ts  (trong thư mục web/)
 */
import assert from "node:assert/strict";
import { chuyenKetQuaThanhTin, gonMenhDeGui, hoiTroLy, taoTheTienDo } from "./troLy";

// 1. taoTheTienDo: nhóm theo tác tử, giữ thứ tự, tên tiếng Việt, ghi chú bước bỏ qua
{
  const the = taoTheTienDo({
    keHoach: [
      { tacTu: "tim_kiem", nhiemVu: "tìm", phuThuoc: [] },
      { tacTu: "doi_chieu_thuoc", nhiemVu: "thuốc", phuThuoc: [] },
    ],
    keHoachTuMoHinh: true,
    xemTruoc: "Bối cảnh: người lớn.",
    buoc: [
      { ma: "0.tim_kiem.dat_tu_khoa", tacTu: "tim_kiem", ten: "Đặt từ khoá tìm", trangThai: "xong" },
      { ma: "0.tim_kiem.tim_tai_lieu", tacTu: "tim_kiem", ten: "Tìm tài liệu ở các nguồn", trangThai: "dang" },
      { ma: "1.doi_chieu_thuoc.doi_chieu_thuoc", tacTu: "doi_chieu_thuoc", ten: "Đối chiếu", trangThai: "bo_qua", ghiChu: "chưa bật mô hình ngoài" },
    ],
  });
  assert.deepEqual(the.nhom.map((n) => n.ten), ["Tìm kiếm", "Đối chiếu thuốc và dị ứng"]);
  assert.deepEqual(the.nhom[0].buoc.map((b) => b.trangThai), ["xong", "dang"]);
  assert.equal(the.nhom[1].buoc[0].ghiChu, "chưa bật mô hình ngoài");
  assert.equal(the.keHoachTuMoHinh, true);
  assert.equal(the.xemTruoc, "Bối cảnh: người lớn.");
  assert.equal(the.keHoach.length, 2);
}

// 2. kế hoạch đã có nhưng chưa có bước nào: vẫn hiện tên tác tử
{
  const the = taoTheTienDo({ keHoach: [{ tacTu: "tra_loi", nhiemVu: "x", phuThuoc: [] }], keHoachTuMoHinh: false, buoc: [], xemTruoc: null });
  assert.equal(the.nhom.length, 1);
  assert.equal(the.nhom[0].ten, "Trả lời");
  assert.deepEqual(the.nhom[0].buoc, []);
  const rong = taoTheTienDo(null as any);
  assert.deepEqual(rong.nhom, []);
}

// 3. chuyenKetQuaThanhTin có phần tra_loi
{
  const tin = chuyenKetQuaThanhTin(
    {
      phan: [
        { tacTu: "chu_de_can_ban", ten: "Chủ đề cần bàn", noiDung: "Hồ sơ chưa có mệnh đề ở: Dị ứng." },
        {
          tacTu: "tra_loi",
          ten: "Trả lời có nguồn",
          noiDung: "gợi ý [1]",
          traLoi: { answer: "gợi ý [1]", sources: [{ so: 1, name: "T" }], cauTruc: { phuong_an: [], an_toan: [] }, warning: "cảnh báo X" },
        },
        { tacTu: "doi_chieu_thuoc", ten: "Đối chiếu thuốc và dị ứng", noiDung: "Thuốc: a", canhBao: "a trùng dị ứng" },
      ],
      thongKe: { token: 100, giay: 12.5, loiGoi: 0 },
    },
    "câu hỏi gốc",
    { source: "mo_hinh_ngoai", model: "qwen3.8-flash" },
  );
  assert.ok(tin.content?.startsWith("gợi ý [1]"));
  assert.ok(tin.content?.includes("### Chủ đề cần bàn"));
  assert.ok(tin.content?.includes("a trùng dị ứng"));
  assert.equal(tin.sources?.length, 1);
  assert.ok(tin.cauTruc);
  assert.ok(tin.warning?.includes("cảnh báo X"));
  assert.ok(tin.meta?.includes("qwen3.8-flash") && tin.meta.includes("đã ẩn danh"), tin.meta);
  assert.equal(tin.question, "câu hỏi gốc");
  assert.equal(tin.troLy?.phanKhac.length, 2, "hai phần tại chỗ nằm ở phanKhac");
}

// 4. không có phần tra_loi (ngoài tắt): nội dung vẫn không rỗng từ hai tác tử tại chỗ
{
  const tin = chuyenKetQuaThanhTin(
    {
      phan: [
        { tacTu: "tim_kiem", ten: "Tìm kiếm", noiDung: "", canhBao: "chưa bật mô hình ngoài" },
        { tacTu: "chu_de_can_ban", ten: "Chủ đề cần bàn", noiDung: "Hồ sơ chưa có mệnh đề ở: Dị ứng." },
        { tacTu: "doi_chieu_thuoc", ten: "Đối chiếu thuốc và dị ứng", noiDung: "Thuốc ghi nhận: chưa có." },
      ],
      thongKe: { token: 0, giay: 0, loiGoi: 0 },
    },
    "x",
    { source: "tai_cho" },
  );
  assert.ok((tin.content || "").length > 0);
  assert.ok(tin.content!.includes("Hồ sơ chưa có mệnh đề ở"));
  assert.ok(!tin.cauTruc);
  assert.ok(tin.meta?.includes("Tại chỗ"), tin.meta);
  assert.ok(tin.warning?.includes("chưa bật mô hình ngoài"), "cảnh báo của phần bị bỏ qua được báo lên");
}

// 5. gonMenhDeGui: chỉ giữ trường cần, bỏ trích dẫn
{
  const ra = gonMenhDeGui([{ id: "p1", text: "ho", section: "BỆNH SỬ HIỆN TẠI", quotes: ["lời gốc"], evidenceTurns: [1], drug: null }]);
  assert.deepEqual(Object.keys(ra[0]).sort(), ["certainty", "drug", "negated", "section", "subject", "text"]);
  assert.deepEqual(gonMenhDeGui(undefined), []);
}

// 6. hoiTroLy: 202 rồi 200 -> gọi dangCho; 400 danh tính -> trả lỗi có mã; lỗi mạng -> loi
(async () => {
  const phanHoi = (status: number, body: unknown) => ({ status, ok: status >= 200 && status < 300, json: async () => body }) as unknown as Response;
  {
    const goi: string[] = [];
    const dang: any[] = [];
    const chuoi = [
      phanHoi(202, { jobId: "7", tienTrinh: { buoc: [1] } }),
      phanHoi(202, { jobId: "7", tienTrinh: { buoc: [1, 2] } }),
      phanHoi(200, { ketQua: { phan: [], thongKe: {} }, source: "tai_cho" }),
    ];
    const fetchGia = async (url: string) => (goi.push(url), chuoi.shift()!);
    const r = await hoiTroLy({ cauHoi: "x" }, (tt) => dang.push(tt), { fetchFn: fetchGia as any, khoangMs: 1 });
    assert.ok("ketQua" in r);
    assert.deepEqual(goi, ["/api/tro-ly", "/api/tro-ly/7", "/api/tro-ly/7"]);
    assert.equal(dang.length, 2);
  }
  {
    const r = await hoiTroLy({ cauHoi: "chị Lan" }, () => {}, {
      fetchFn: (async () => phanHoi(400, { error: "còn danh tính", code: "cau_hoi_co_danh_tinh", lyDo: "ten_rieng" })) as any,
      khoangMs: 1,
    });
    assert.ok("loi" in r);
    if ("loi" in r) {
      assert.equal(r.code, "cau_hoi_co_danh_tinh");
      assert.equal(r.lyDo, "ten_rieng");
    }
  }
  {
    const r = await hoiTroLy({ cauHoi: "x" }, () => {}, {
      fetchFn: (async () => {
        throw new Error("rớt mạng");
      }) as any,
      khoangMs: 1,
    });
    assert.ok("loi" in r);
  }
  {
    const r = await hoiTroLy({ cauHoi: "x" }, () => {}, {
      fetchFn: (async () => phanHoi(202, { jobId: "1", tienTrinh: null })) as any,
      khoangMs: 1,
      toiDaMs: 20,
    });
    assert.ok("loi" in r, "chờ quá lâu thì thôi");
  }
  console.log("troLy.test.ts: tất cả đều qua");
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
