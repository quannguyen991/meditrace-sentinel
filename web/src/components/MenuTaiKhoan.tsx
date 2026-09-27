import React, { useEffect, useRef, useState } from "react";
import { LogOut, Ticket, Copy, Check, Loader2 } from "lucide-react";
import { taoMaMoi, type NguoiDung } from "../lib/taiKhoan";

type Props = {
  nguoiDung: NguoiDung;
  onDangXuat: () => Promise<void> | void;
  /** Thanh trên: menu mở xuống, canh phải. Thanh trái: menu mở sang phải, canh đáy. */
  huong: "top" | "left";
};

const chuCai = (ten: string) => (ten.trim().split(/\s+/).pop() || "?").charAt(0).toUpperCase();

/** Nút tròn có chữ cái đầu của tên; bấm mở thông tin tài khoản, mã mời (quản trị) và đăng xuất. */
export function MenuTaiKhoan({ nguoiDung, onDangXuat, huong }: Props) {
  const [mo, setMo] = useState(false);
  const [ma, setMa] = useState<{ ma: string; hetHan: number } | null>(null);
  const [dangTao, setDangTao] = useState(false);
  const [daChep, setDaChep] = useState(false);
  const [dangRa, setDangRa] = useState(false);
  const [loi, setLoi] = useState<string | null>(null);
  const goc = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!mo) return;
    const ngoai = (e: MouseEvent) => goc.current && !goc.current.contains(e.target as Node) && setMo(false);
    const phim = (e: KeyboardEvent) => e.key === "Escape" && setMo(false);
    document.addEventListener("mousedown", ngoai);
    document.addEventListener("keydown", phim);
    return () => {
      document.removeEventListener("mousedown", ngoai);
      document.removeEventListener("keydown", phim);
    };
  }, [mo]);

  const tao = async () => {
    setDangTao(true);
    setLoi(null);
    setDaChep(false);
    try {
      setMa(await taoMaMoi());
    } catch (e: any) {
      setLoi(e?.message || String(e));
    } finally {
      setDangTao(false);
    }
  };
  const chep = async () => {
    if (!ma) return;
    try {
      await navigator.clipboard.writeText(ma.ma);
      setDaChep(true);
    } catch {}
  };
  const ra = async () => {
    setDangRa(true);
    await onDangXuat();
  };

  const lon = huong === "left" ? "w-8 h-8 mt-1" : "w-7 h-7 ml-0.5 sm:ml-1";
  const viTri = huong === "left" ? "left-full bottom-0 ml-3" : "right-0 top-full mt-2";

  return (
    <div ref={goc} className="relative flex-shrink-0">
      <button
        id="btn-nav-user-profile"
        onClick={() => setMo((v) => !v)}
        aria-haspopup="dialog"
        aria-expanded={mo}
        className={`${lon} rounded-full bg-[#0284C7] text-white font-semibold text-xs flex items-center justify-center hover:bg-[#0369A1] transition-colors shadow-[0_2px_8px_rgba(2,132,199,0.35)] ring-2 ring-[#BAE6FD]`}
        title={`${nguoiDung.hoTen} · ${nguoiDung.email}`}
      >
        {chuCai(nguoiDung.hoTen)}
      </button>

      {mo && (
        <div
          role="dialog"
          aria-label="Tài khoản"
          className={`absolute ${viTri} z-50 w-72 rounded-2xl border border-[#CCE3F0] bg-white p-3 text-left shadow-[0_18px_40px_-12px_rgba(12,74,110,0.35)]`}
        >
          <div className="px-1.5 pb-3 border-b border-[#E2E8F0]">
            <div className="font-semibold text-[#0F172A] text-[14px] truncate">{nguoiDung.hoTen}</div>
            <div className="text-[12.5px] text-[#64748B] truncate">{nguoiDung.email}</div>
            <span
              className={`mt-1.5 inline-block rounded-full px-2 py-0.5 text-[11px] font-semibold ${
                nguoiDung.vai === "quan_tri" ? "bg-[#E0F2FE] text-[#0369A1]" : "bg-[#F1F5F9] text-[#475569]"
              }`}
            >
              {nguoiDung.vai === "quan_tri" ? "Quản trị" : "Bác sĩ"}
            </span>
          </div>

          {nguoiDung.vai === "quan_tri" && (
            <div className="py-3 border-b border-[#E2E8F0]">
              <button
                onClick={tao}
                disabled={dangTao}
                className="w-full flex items-center gap-2 rounded-lg px-1.5 py-1.5 text-[13.5px] font-medium text-[#0F172A] hover:bg-[#F0F7FA] disabled:opacity-60"
              >
                {dangTao ? <Loader2 size={15} className="animate-spin" /> : <Ticket size={15} className="text-[#0284C7]" />}
                Tạo mã mời
              </button>
              {ma && (
                <div className="mt-2 rounded-xl bg-[#F0F7FA] px-3 py-2.5">
                  <div className="flex items-center justify-between gap-2">
                    <code className="font-mono text-[17px] font-semibold tracking-[0.14em] text-[#0C4A6E]">{ma.ma}</code>
                    <button
                      onClick={chep}
                      className="rounded-md p-1.5 text-[#0369A1] hover:bg-white"
                      aria-label="Chép mã mời"
                      title="Chép"
                    >
                      {daChep ? <Check size={15} /> : <Copy size={15} />}
                    </button>
                  </div>
                  <p className="mt-1 text-[11.5px] leading-snug text-[#475569]">
                    Dùng một lần, hết hạn {new Date(ma.hetHan).toLocaleDateString("vi-VN")}. Mã chỉ hiện lúc này — chép
                    lại gửi cho người cần tạo tài khoản.
                  </p>
                </div>
              )}
              {loi && <p className="mt-2 text-[12.5px] text-[#B91C1C]">{loi}</p>}
            </div>
          )}

          <button
            onClick={ra}
            disabled={dangRa}
            className="mt-2 w-full flex items-center gap-2 rounded-lg px-1.5 py-1.5 text-[13.5px] font-medium text-[#B91C1C] hover:bg-[#FEF2F2] disabled:opacity-60"
          >
            {dangRa ? <Loader2 size={15} className="animate-spin" /> : <LogOut size={15} />}
            Đăng xuất
          </button>
          <p className="px-1.5 mt-1 text-[11.5px] leading-snug text-[#64748B]">
            Lưu nốt thay đổi lên máy chủ rồi xoá bản sao ca khám trong trình duyệt này.
          </p>
        </div>
      )}
    </div>
  );
}
