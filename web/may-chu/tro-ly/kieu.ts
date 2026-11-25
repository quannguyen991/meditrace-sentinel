import type { MenhDeVao, NguCanhVao } from "./an-danh";

export type TacTuMa = "dieu_phoi" | "tim_kiem" | "tra_loi" | "doi_chieu" | "chu_de_can_ban" | "doi_chieu_thuoc";

export type TrangThaiBuoc = "cho" | "dang" | "xong" | "bo_qua" | "loi";

export type Buoc = {
  ma: string;
  tacTu: TacTuMa;
  ten: string;
  trangThai: TrangThaiBuoc;
  ghiChu?: string;
  batDau?: number;
  ketThuc?: number;
  /** Kết quả trung gian của bước đã xong, để chạy lại không lặp. */
  dau?: unknown;
};

export type MucKePhach = { tacTu: TacTuMa; nhiemVu: string; phuThuoc: number[] };

export type YeuCauTroLy = {
  cauHoi: string;
  menhDe: MenhDeVao[];
  nguCanh: NguCanhVao;
  nguon?: Record<string, boolean>;
  batTacTu: TacTuMa[];
};

export type TienTrinh = {
  keHoach: MucKePhach[];
  keHoachTuMoHinh: boolean;
  buoc: Buoc[];
  xemTruoc: string | null;
  /** Token và giây của lời gọi điều phối (lập kế phác), để chạy lại không mất số liệu. */
  dieuPhoi?: { token: number; giay: number };
};

export type KetQuaTroLy = {
  phan: Array<{ tacTu: TacTuMa; ten: string; noiDung: string; traLoi?: unknown; canhBao?: string }>;
  thongKe: { token: number; giay: number; loiGoi: number };
};
