import React, { useEffect, useState } from "react";
import { Loader2 } from "lucide-react";
import App from "./App";
import { ManDangNhap } from "./components/ManDangNhap";
import { dangXuat, layToi, nhanMayChoNguoi, type NguoiDung, type TinhTrangToi } from "./lib/taiKhoan";

/**
 * Gốc giao diện: hỏi máy chủ đang đăng nhập với ai. Chưa đăng nhập thì hiện màn đăng nhập;
 * rồi thì dựng App cho đúng người đó (key theo id: đổi người là dựng lại từ đầu).
 * Phiên hết hạn giữa chừng (một lời gọi /api trả 401) thì quay về màn đăng nhập.
 */
export default function Goc() {
  const [tinhTrang, setTinhTrang] = useState<TinhTrangToi | null>(null);
  const [loi, setLoi] = useState<string | null>(null);

  const hoiLai = () =>
    layToi()
      .then((t) => {
        if (t.nguoiDung) nhanMayChoNguoi(t.nguoiDung.id);
        setTinhTrang(t);
        setLoi(null);
      })
      .catch((e) => setLoi(e?.message || String(e)));

  useEffect(() => {
    hoiLai();
    const goc = window.fetch;
    window.fetch = async (...args) => {
      const r = await goc(...args);
      const url = typeof args[0] === "string" ? args[0] : args[0] instanceof Request ? args[0].url : String(args[0]);
      if (r.status === 401 && url.includes("/api/") && !/\/api\/(toi|dang-nhap|dang-ky)/.test(url)) {
        setTinhTrang((t) => (t ? { ...t, nguoiDung: null } : t));
      }
      return r;
    };
    return () => {
      window.fetch = goc;
    };
  }, []);

  const vao = (nd: NguoiDung) => {
    nhanMayChoNguoi(nd.id);
    setTinhTrang((t) => ({ canMaMoi: true, taoQuanTriDuocTuDay: false, ...t, nguoiDung: nd }));
  };
  const ra = async () => {
    await dangXuat();
    setTinhTrang(null);
    await hoiLai();
  };

  if (loi)
    return (
      <div className="min-h-screen grid place-items-center px-4 text-center">
        <div>
          <p className="text-[#991B1B] font-medium">Không kết nối được máy chủ MediTrace: {loi}</p>
          <button onClick={hoiLai} className="mt-3 rounded-lg bg-[#0284C7] px-4 py-2 text-white font-semibold">
            Thử lại
          </button>
        </div>
      </div>
    );
  if (!tinhTrang)
    return (
      <div className="min-h-screen grid place-items-center text-[#0369A1]" aria-label="Đang tải">
        <Loader2 className="animate-spin" />
      </div>
    );
  if (!tinhTrang.nguoiDung) return <ManDangNhap tinhTrang={tinhTrang} onVao={vao} />;
  return <App key={tinhTrang.nguoiDung.id} nguoiDung={tinhTrang.nguoiDung} onDangXuat={ra} />;
}
