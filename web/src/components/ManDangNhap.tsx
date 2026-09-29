import React, { useState } from "react";
import { Eye, EyeOff, Loader2, ArrowRight } from "lucide-react";
import { MediTraceLogo } from "./MediTraceLogo";
import { dangKy, dangNhap, type NguoiDung, type TinhTrangToi } from "../lib/taiKhoan";

type Props = { tinhTrang: TinhTrangToi; onVao: (nd: NguoiDung) => void };

/** Màn đăng nhập / đăng ký. Chưa có tài khoản nào thì mở sẵn thẻ đăng ký (người đầu tiên là quản trị). */
export function ManDangNhap({ tinhTrang, onVao }: Props) {
  const chuaCoAi = !tinhTrang.canMaMoi;
  const [the, setThe] = useState<"vao" | "tao">(chuaCoAi ? "tao" : "vao");
  const [hoTen, setHoTen] = useState("");
  const [email, setEmail] = useState("");
  const [matKhau, setMatKhau] = useState("");
  const [maMoi, setMaMoi] = useState("");
  const [hienMK, setHienMK] = useState(false);
  const [dang, setDang] = useState(false);
  const [loi, setLoi] = useState<string | null>(null);

  const khongTaoDuoc = the === "tao" && chuaCoAi && !tinhTrang.taoQuanTriDuocTuDay;

  const gui = async (e: React.FormEvent) => {
    e.preventDefault();
    if (dang || khongTaoDuoc) return;
    setLoi(null);
    setDang(true);
    try {
      const nd =
        the === "vao"
          ? await dangNhap(email, matKhau)
          : await dangKy({ hoTen, email, matKhau, maMoi: chuaCoAi ? undefined : maMoi });
      onVao(nd);
    } catch (err: any) {
      setLoi(err?.message || String(err));
      setDang(false);
    }
  };

  const doiThe = (t: "vao" | "tao") => {
    setThe(t);
    setLoi(null);
  };

  const o =
    "w-full rounded-xl border border-[#CCE3F0] bg-white px-3.5 py-2.5 text-[15px] text-[#0F172A] placeholder:text-[#94A3B8] " +
    "outline-none transition focus:border-[#0284C7] focus:ring-4 focus:ring-[#0284C7]/15";
  const nhan = "block text-[13px] font-semibold text-[#334155] mb-1.5";

  return (
    <div className="min-h-screen bg-[#F0F6FA] flex items-stretch">
      {/* Cột trái: nói rõ công cụ làm gì, bằng đúng một dòng bản nháp có căn cứ */}
      <section className="hidden lg:flex w-[46%] max-w-[640px] flex-col justify-between bg-[#0C4A6E] text-[#E0F2FE] px-12 py-10 relative overflow-hidden">
        <div
          aria-hidden
          className="absolute inset-0 opacity-[0.07]"
          style={{
            backgroundImage:
              "linear-gradient(#E0F2FE 1px, transparent 1px), linear-gradient(90deg, #E0F2FE 1px, transparent 1px)",
            backgroundSize: "28px 28px",
          }}
        />
        <div className="relative flex items-center gap-3">
          <div className="rounded-xl bg-white p-1.5">
            <MediTraceLogo size={30} />
          </div>
          <div>
            <div className="font-semibold text-white tracking-tight">MediTrace Sentinel</div>
            <div className="text-[12px] text-[#7DD3FC]">Bản nháp hồ sơ có truy vết</div>
          </div>
        </div>

        <div className="relative space-y-7">
          <h1 className="font-serif text-[40px] leading-[1.1] text-white [text-wrap:balance]">
            Mỗi dòng trong bản nháp đều chỉ ra câu nói làm căn cứ.
          </h1>
          <p className="text-[15px] leading-relaxed text-[#BAE6FD] max-w-[46ch]">
            Từ hội thoại khám bệnh tiếng Việt, công cụ dựng bản nháp hồ sơ lâm sàng có cấu trúc, rồi đánh dấu
            dòng nào có thể sai người, sai trạng thái hoặc thiếu căn cứ để bác sĩ duyệt.
          </p>

          <figure className="rounded-2xl bg-white text-[#0F172A] p-4 shadow-[0_20px_50px_-20px_rgba(0,0,0,0.5)] max-w-[480px]">
            <div className="text-[11px] font-semibold uppercase tracking-[0.08em] text-[#64748B] mb-2">
              Tiền sử gia đình · ví dụ
            </div>
            <p className="text-[15px] leading-snug">
              <mark className="bg-[#FEF3C7] text-[#78350F] rounded px-1 py-0.5">Mẹ bệnh nhân</mark> đái tháo đường
              típ 2, khoảng 5 năm.
            </p>
            <figcaption className="mt-3 border-t border-[#E2E8F0] pt-3 text-[13px] text-[#475569]">
              <span className="font-mono text-[12px] text-[#0369A1]">Lượt 14 · người nhà</span>
              <span className="block mt-0.5 italic">“Mẹ cháu thì tiểu đường cũng năm năm nay rồi bác ạ.”</span>
              <span className="mt-2 inline-flex items-center gap-1.5 rounded-full bg-[#FEF3C7] px-2 py-0.5 text-[12px] font-medium text-[#92400E]">
                Kiểm lại người: người nói là con bệnh nhân, nên “mẹ cháu” có thể chính là bệnh nhân
              </span>
            </figcaption>
          </figure>
        </div>

        <p className="relative text-[12px] text-[#7DD3FC]">
          Không chẩn đoán, không tư vấn điều trị. Bản nháp chỉ dùng sau khi bác sĩ duyệt.
        </p>
      </section>

      {/* Cột phải: biểu mẫu */}
      <main className="flex-1 flex items-center justify-center px-4 py-10">
        <div className="w-full max-w-[400px]">
          <div className="lg:hidden flex items-center gap-2.5 mb-8">
            <MediTraceLogo size={30} />
            <span className="font-semibold tracking-tight text-[#0C4A6E]">MediTrace Sentinel</span>
          </div>

          <h2 className="font-serif text-[30px] leading-tight text-[#0C4A6E]">
            {the === "vao" ? "Đăng nhập" : chuaCoAi ? "Tạo tài khoản quản trị" : "Tạo tài khoản"}
          </h2>
          <p className="mt-1.5 text-[14px] text-[#475569]">
            {the === "vao"
              ? "Ca khám, bản nháp và kết quả duyệt của bạn nằm trong tài khoản này."
              : chuaCoAi
                ? "Máy chủ chưa có tài khoản nào. Tài khoản đầu tiên là quản trị: tạo mã mời cho người khác."
                : "Cần mã mời từ quản trị của nhóm."}
          </p>

          {!chuaCoAi && (
            <div role="tablist" className="mt-6 grid grid-cols-2 rounded-xl bg-[#E0EEF6] p-1 text-[14px] font-semibold">
              {(["vao", "tao"] as const).map((t) => (
                <button
                  key={t}
                  role="tab"
                  type="button"
                  aria-selected={the === t}
                  onClick={() => doiThe(t)}
                  className={`rounded-lg py-2 transition ${
                    the === t ? "bg-white text-[#0C4A6E] shadow-sm" : "text-[#475569] hover:text-[#0C4A6E]"
                  }`}
                >
                  {t === "vao" ? "Đăng nhập" : "Đăng ký"}
                </button>
              ))}
            </div>
          )}

          <form onSubmit={gui} className="mt-6 flex flex-col gap-4" noValidate>
            {the === "tao" && (
              <div>
                <label className={nhan} htmlFor="ho-ten">
                  Họ và tên
                </label>
                <input
                  id="ho-ten"
                  className={o}
                  value={hoTen}
                  onChange={(e) => setHoTen(e.target.value)}
                  autoComplete="name"
                  placeholder="BS. Nguyễn Văn A"
                  required
                />
              </div>
            )}
            <div>
              <label className={nhan} htmlFor="email">
                Email
              </label>
              <input
                id="email"
                type="email"
                className={o}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
                placeholder="ten@benhvien.vn"
                required
                autoFocus
              />
            </div>
            <div>
              <label className={nhan} htmlFor="mat-khau">
                Mật khẩu
              </label>
              <div className="relative">
                <input
                  id="mat-khau"
                  type={hienMK ? "text" : "password"}
                  className={`${o} pr-11`}
                  value={matKhau}
                  onChange={(e) => setMatKhau(e.target.value)}
                  autoComplete={the === "vao" ? "current-password" : "new-password"}
                  minLength={the === "tao" ? 8 : undefined}
                  required
                />
                <button
                  type="button"
                  onClick={() => setHienMK((v) => !v)}
                  className="absolute right-1.5 top-1/2 -translate-y-1/2 rounded-lg p-2 text-[#64748B] hover:bg-[#F1F5F9] hover:text-[#0C4A6E]"
                  aria-label={hienMK ? "Ẩn mật khẩu" : "Hiện mật khẩu"}
                >
                  {hienMK ? <EyeOff size={17} /> : <Eye size={17} />}
                </button>
              </div>
              {the === "tao" && <p className="mt-1.5 text-[12.5px] text-[#64748B]">Ít nhất 8 ký tự.</p>}
            </div>
            {the === "tao" && !chuaCoAi && (
              <div>
                <label className={nhan} htmlFor="ma-moi">
                  Mã mời
                </label>
                <input
                  id="ma-moi"
                  className={`${o} font-mono tracking-[0.12em] uppercase`}
                  value={maMoi}
                  onChange={(e) => setMaMoi(e.target.value)}
                  placeholder="ABCD-EF23"
                  autoComplete="off"
                  spellCheck={false}
                  required
                />
                <p className="mt-1.5 text-[12.5px] text-[#64748B]">Mỗi mã dùng một lần, hết hạn sau 7 ngày.</p>
              </div>
            )}

            {khongTaoDuoc && (
              <p className="rounded-xl border border-[#FDE68A] bg-[#FFFBEB] px-3.5 py-3 text-[13.5px] text-[#92400E]">
                Tài khoản quản trị đầu tiên chỉ tạo được trên chính máy chạy máy chủ (mở http://localhost). Sau đó
                quản trị tạo mã mời cho người khác.
              </p>
            )}
            {loi && (
              <p role="alert" className="rounded-xl border border-[#FECACA] bg-[#FEF2F2] px-3.5 py-3 text-[13.5px] text-[#991B1B]">
                {loi}
              </p>
            )}

            <button
              type="submit"
              disabled={dang || khongTaoDuoc}
              className="mt-1 inline-flex items-center justify-center gap-2 rounded-xl bg-[#0284C7] px-4 py-3 text-[15px] font-semibold text-white shadow-[0_6px_18px_-6px_rgba(2,132,199,0.6)] transition hover:bg-[#0369A1] focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-[#0284C7]/30 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {dang ? <Loader2 size={18} className="animate-spin" /> : null}
              {the === "vao" ? "Đăng nhập" : "Tạo tài khoản"}
              {!dang && <ArrowRight size={17} />}
            </button>
          </form>

          {/* Hướng dẫn tiếng Anh cho người đánh giá ở nước ngoài; giao diện bên trong là tiếng Việt. */}
          <aside lang="en" className="mt-8 rounded-xl border border-[#BAE6FD] bg-[#F0F9FF] p-4 text-[13px] leading-relaxed text-[#0C4A6E]">
            <p className="font-semibold">For reviewers</p>
            <p className="mt-1">
              MediTrace Sentinel turns a Vietnamese doctor–patient conversation into a clinical note draft in which every
              line links back to the turn it came from. Sign in with the demo account from the submission notes. The
              interface is in Vietnamese.
            </p>
            <ol className="mt-2 list-decimal space-y-0.5 pl-5">
              <li>On the Home page, click <b>“Xem thử với ca mẫu”</b> (try a sample case). It loads a pre-computed synthetic case instantly.</li>
              <li>Open <b>“Duyệt từng mệnh đề”</b> (review each statement) to see who each line is about and the source turn.</li>
              <li>Generating a new draft with the live model takes about 3.5 minutes. All data is synthetic.</li>
            </ol>
          </aside>

          <p className="mt-8 text-[12.5px] leading-relaxed text-[#64748B]">
            Mật khẩu được băm (scrypt) trước khi lưu; máy chủ không giữ mật khẩu gốc. Phiên đăng nhập hết hạn sau 14
            ngày. Đăng xuất trên máy dùng chung để xoá bản sao ca khám trong trình duyệt.
          </p>
        </div>
      </main>
    </div>
  );
}
