/**
 * Xử lý MỘT việc trợ lý đã lấy ra khỏi hàng đợi: ẩn danh → bản xem trước → kế phác → chạy kế phác → ghi kết quả.
 * Tách khỏi server.ts để thử được đầu cuối với mô hình ngoài giả (tich-hop.test.ts). Không bao giờ ném lỗi:
 * việc hỏng thì ghi `loi`, việc xong thì ghi `xong`.
 */
import { chuoiGuiRa, kiemCauHoi, xayCaAnDanh } from "./an-danh";
import { type Phu, chayKePhach, lapKePhach } from "./dieu-phoi";
import type { TienTrinh } from "./kieu";
import type { KhoViec, ViecNhan } from "./viec-tro-ly";

/** Một dòng nhật ký mỗi việc. KHÔNG được chứa chuỗi đã gửi ra ngoài (Global Constraints). */
export type GhiNhatKyViec = (hanhDong: string, chiTiet: string) => void;

export async function xuLyViecTroLy(phu: Phu, kho: KhoViec, viec: ViecNhan, ghiNhatKy: GhiNhatKyViec): Promise<void> {
  const t0 = Date.now();
  const ghiDong = (chiTiet: string) => {
    try {
      ghiNhatKy("tro_ly", chiTiet);
    } catch {
      /* nhật ký hỏng không làm hỏng việc */
    }
  };
  try {
    if (kho.daHuy?.(viec.id)) return;
    const { yeuCau } = viec;
    const kiem = kiemCauHoi(yeuCau.cauHoi);
    const ca = xayCaAnDanh(yeuCau.menhDe, yeuCau.nguCanh);
    const cauHoi = kiem.ok ? kiem.cau : "";
    const chuoiRa = chuoiGuiRa(ca, cauHoi);

    const tt: TienTrinh = viec.tienTrinh ?? { keHoach: [], keHoachTuMoHinh: false, buoc: [], xemTruoc: null };
    if (tt.xemTruoc === null) tt.xemTruoc = chuoiRa; // đúng chuỗi sẽ gửi ra; bác sĩ xem được
    if (!tt.keHoach.length) {
      const r = await lapKePhach(phu, yeuCau, ca, cauHoi);
      tt.keHoach = r.keHoach;
      tt.keHoachTuMoHinh = r.tuMoHinh;
      if (r.tuMoHinh || r.token > 0 || r.giay > 0) {
        tt.dieuPhoi = { token: r.token, giay: r.giay };
      }
      kho.ghiTienTrinh(viec.id, tt); // ghi ngay: khởi động lại thì không lập (và trả tiền) lại
    }
    if (kho.daHuy?.(viec.id)) return;
    const kq = await chayKePhach(phu, yeuCau, tt.keHoach, tt, (t) => kho.ghiTienTrinh(viec.id, t));
    if (kho.daHuy?.(viec.id)) return;
    kq.thongKe.token += tt.dieuPhoi?.token ?? 0;
    kq.thongKe.giay = Math.round((kq.thongKe.giay + (tt.dieuPhoi?.giay ?? 0)) * 10) / 10;
    kho.xong(viec.id, kq);
    ghiDong(
      `tac_tu=${[...new Set(tt.keHoach.map((m) => m.tacTu))].join(",")};ky_tu=${chuoiRa.length};` +
        `menh_de_gui=${ca.dong.length}/${yeuCau.menhDe.length};bo=muc:${ca.soBo.muc_khong_cho_phep},danh_tinh:${ca.soBo.con_danh_tinh},rong:${ca.soBo.rong};` +
        `phat_hien=${kiem.ok ? "ok" : kiem.lyDo};ke_phach=${tt.keHoachTuMoHinh ? "mo_hinh" : "du_phong"};` +
        `loi_goi=${kq.thongKe.loiGoi};token=${kq.thongKe.token};ms=${Date.now() - t0}`,
    );
  } catch (e) {
    if (kho.daHuy?.(viec.id)) return;
    try {
      kho.loi(viec.id, "loi_noi_bo");
    } catch {
      /* CSDL bận: việc sẽ được khôi phục lần khởi động sau */
    }
    ghiDong(`loi=loi_noi_bo;ms=${Date.now() - t0};chi_tiet=${e instanceof Error ? e.name : "?"}`);
  }
}
