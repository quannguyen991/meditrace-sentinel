import React, { useEffect, useState } from "react";
import { ChevronDown, ChevronUp, ShieldCheck, ShieldAlert } from "lucide-react";
import { TEN_TAC_TU, taoTheTienDo, type BuocHienThi } from "../lib/troLy";

/** Tác tử người dùng bật/tắt được. Điều phối luôn có mặt nên không có công tắc. */
const TAC_TU_BAT_TAT: Array<{ ma: string; ten: string; mota: string; ngoai: boolean }> = [
  { ma: "tim_kiem", ten: "Tìm kiếm", mota: "Tìm tài liệu y khoa (Bộ Y tế, FDA, PubMed…)", ngoai: true },
  { ma: "tra_loi", ten: "Trả lời", mota: "Soạn câu trả lời có nguồn từ tài liệu đã tìm", ngoai: true },
  { ma: "doi_chieu", ten: "Đối chiếu", mota: "Kiểm câu trả lời với tài liệu, sửa tối đa một lần", ngoai: true },
  { ma: "chu_de_can_ban", ten: "Chủ đề cần bàn", mota: "Chỉ ra mục hồ sơ còn thiếu · luật tại chỗ", ngoai: false },
  { ma: "doi_chieu_thuoc", ten: "Đối chiếu thuốc và dị ứng", mota: "Thuốc trùng dị ứng, cùng thuốc khác liều · luật tại chỗ", ngoai: false },
];

type CaiDat = { batTacTu: string[]; ngoaiBat: boolean; ngoaiCoKhoa: boolean };

function CongTac({ bat, onDoi, nhan, mota, tat }: { bat: boolean; onDoi: () => void; nhan: string; mota: string; tat?: boolean }) {
  return (
    <label className={`flex items-start gap-2 py-1.5 ${tat ? "opacity-50" : "cursor-pointer"}`}>
      <input type="checkbox" checked={bat} disabled={tat} onChange={onDoi} className="mt-0.5 accent-[#0284C7]" />
      <span className="min-w-0">
        <span className="block text-[12px] font-semibold text-[#0F172A] leading-snug">{nhan}</span>
        <span className="block text-[10.5px] text-[#64748B] leading-snug">{mota}</span>
      </span>
    </label>
  );
}

/** Bảng bật/tắt tác tử. Quản trị còn có công tắc tắt toàn hệ thống đường ra mô hình ngoài. */
export const BangTacTu: React.FC<{ laQuanTri: boolean }> = ({ laQuanTri }) => {
  const [cai, setCai] = useState<CaiDat | null>(null);
  const [loi, setLoi] = useState<string | null>(null);

  useEffect(() => {
    let huy = false;
    fetch("/api/tro-ly/cai-dat")
      .then((r) => r.json())
      .then((d) => !huy && setCai(d))
      .catch(() => !huy && setLoi("Không đọc được cài đặt tác tử."));
    return () => {
      huy = true;
    };
  }, []);

  const doiTacTu = async (ma: string) => {
    if (!cai) return;
    const moi = cai.batTacTu.includes(ma) ? cai.batTacTu.filter((x) => x !== ma) : [...cai.batTacTu, ma];
    setCai({ ...cai, batTacTu: moi }); // hiện ngay, máy chủ trả lại bản chuẩn
    try {
      const r = await fetch("/api/tro-ly/cai-dat", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ batTacTu: moi }) });
      const d = await r.json();
      if (!r.ok) throw new Error(d?.error || "lỗi");
      setCai((c) => (c ? { ...c, batTacTu: d.batTacTu } : c));
      setLoi(null);
    } catch {
      setLoi("Không lưu được cài đặt.");
    }
  };

  const doiNgoai = async () => {
    if (!cai) return;
    try {
      const r = await fetch("/api/tro-ly/cai-dat/ngoai", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ bat: !cai.ngoaiBat }) });
      const d = await r.json();
      if (!r.ok) throw new Error(d?.error || "lỗi");
      setCai({ ...cai, ngoaiBat: d.ngoaiBat });
      setLoi(null);
    } catch {
      setLoi("Không đổi được công tắc toàn hệ thống.");
    }
  };

  return (
    <div id="bang-tac-tu" className="rounded-2xl border border-[#BAE6FD] bg-white p-3 text-left">
      <div className="text-xs font-bold text-[#0F172A] mb-1">Tác tử của trợ lý</div>
      <p className="text-[10.5px] text-[#64748B] leading-snug mb-1.5">
        Mô hình ngoài chỉ nhận dấu hiệu, tình trạng, thuốc kèm liều, nhóm tuổi, giới và có thai. Không nhận tên, ngày, địa chỉ, số liên lạc, trích dẫn hay lời thoại.
      </p>
      {!cai && !loi && <div className="text-[11px] text-[#64748B]">Đang đọc…</div>}
      {cai &&
        TAC_TU_BAT_TAT.map((t) => (
          <CongTac key={t.ma} bat={cai.batTacTu.includes(t.ma)} onDoi={() => doiTacTu(t.ma)} nhan={t.ten} mota={t.mota} />
        ))}
      {cai && !cai.ngoaiBat && (
        <div className="mt-1.5 flex items-start gap-1.5 rounded-xl border border-[#A7F3D0] bg-[#ECFDF5] p-2 text-[10.5px] text-[#065F46] leading-snug">
          <ShieldCheck size={12} className="mt-0.5 flex-shrink-0" />
          Chế độ Nội bộ 100% Offline (0 byte ra ngoài · Tuân thủ NĐ 13/2023): chỉ hai tác tử luật tại chỗ chạy.
        </div>
      )}
      {cai && !cai.ngoaiCoKhoa && cai.ngoaiBat && (
        <div className="mt-1.5 text-[10.5px] text-[#7A4B00] leading-snug">Máy chủ chưa cấu hình cổng mô hình ngoài; chỉ hai tác tử tại chỗ chạy được.</div>
      )}
      {cai && laQuanTri && (
        <div className="mt-2 pt-2 border-t border-[#E2ECF3]">
          <CongTac
            bat={cai.ngoaiBat}
            onDoi={doiNgoai}
            nhan="Cho phép gửi câu hỏi đã ẩn danh ra mô hình ngoài"
            mota="Công tắc của quản trị, áp cho mọi người dùng. Tắt thì chỉ hai tác tử tại chỗ chạy."
          />
        </div>
      )}
      {loi && <div className="mt-1.5 text-[10.5px] text-[#8C1D26]">{loi}</div>}
    </div>
  );
};

function DauBuoc({ b }: { b: BuocHienThi }) {
  if (b.trangThai === "xong") return <span className="text-emerald-600 font-bold" aria-label="xong">✓</span>;
  if (b.trangThai === "dang") return <span className="inline-block animate-spin text-[#0284C7]" aria-label="đang chạy">◌</span>;
  if (b.trangThai === "loi") return <span className="text-[#B42318] font-bold" aria-label="lỗi">✗</span>;
  if (b.trangThai === "bo_qua") return <span className="text-[#94A3B8]" aria-label="bỏ qua">–</span>;
  return <span className="text-[#CBD5E1]" aria-label="chờ">○</span>;
}

/** Thẻ kế hoạch + tiến độ. Kế hoạch (mô hình đề xuất) và tiến độ (code ghi) tách riêng. */
export const TheTienDoTroLy: React.FC<{ tt: any | null }> = ({ tt }) => {
  const the = taoTheTienDo(tt);
  const [moXem, setMoXem] = useState(false);
  if (!the.keHoach.length) {
    return (
      <div className="bg-white rounded-2xl border border-[#CCE3F0] p-3.5 text-xs text-[#475569] flex items-center gap-2" data-the-tien-do>
        <span className="inline-block animate-spin text-[#0284C7]">◌</span>
        Điều phối đang lập kế hoạch…
      </div>
    );
  }
  return (
    <div className="bg-white rounded-2xl border border-[#CCE3F0] p-3.5 text-left space-y-2.5" data-the-tien-do>
      <div>
        <div className="flex items-center gap-1.5 mb-1">
          <span className="text-xs font-bold text-[#0F172A]">Kế hoạch</span>
          <span className={`text-[10px] px-1.5 py-[1px] rounded-full border ${the.keHoachTuMoHinh ? "bg-[#E0F2FE] border-[#BAE6FD] text-[#0369A1]" : "bg-[#F1F5F9] border-[#E2E8F0] text-[#475569]"}`}>
            {the.keHoachTuMoHinh ? "do mô hình đề xuất" : "kế hoạch dự phòng theo luật"}
          </span>
        </div>
        <ol className="list-decimal pl-4 space-y-0.5 text-[11.5px] text-[#334155] leading-snug">
          {the.keHoach.map((m, i) => (
            <li key={i}>
              <span className="font-semibold text-[#0C4A6E]">{TEN_TAC_TU[m.tacTu] || m.tacTu}</span>
              {m.nhiemVu ? ` — ${m.nhiemVu}` : ""}
            </li>
          ))}
        </ol>
      </div>

      <div className="space-y-1.5">
        <div className="text-xs font-bold text-[#0F172A]">Tiến độ</div>
        {the.nhom.map((n) => (
          <div key={n.tacTu} className="text-[11.5px]">
            <div className="font-semibold text-[#0C4A6E]">{n.ten}</div>
            {n.buoc.map((b, i) => (
              <div key={i} className={`flex items-start gap-1.5 pl-2 leading-snug ${b.trangThai === "dang" ? "text-[#0369A1] font-semibold" : b.trangThai === "xong" ? "text-[#475569]" : "text-[#94A3B8]"}`}>
                <span className="w-3 flex-shrink-0 text-center"><DauBuoc b={b} /></span>
                <span className="min-w-0">
                  {b.ten}
                  {b.ghiChu ? <span className="text-[#94A3B8] font-normal"> · {b.ghiChu}</span> : null}
                </span>
              </div>
            ))}
          </div>
        ))}
      </div>

      {the.xemTruoc && (
        <div className="border-t border-[#E2ECF3] pt-2">
          <button type="button" onClick={() => setMoXem(!moXem)} className="w-full flex items-center justify-between text-[11px] text-[#0369A1]">
            <span className="flex items-center gap-1.5">
              <ShieldCheck size={12} /> Dữ liệu gửi ra ngoài (đã ẩn danh)
            </span>
            {moXem ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
          </button>
          {moXem && <pre className="mt-1.5 whitespace-pre-wrap break-words rounded-lg bg-[#F8FAFC] border border-[#E2E8F0] p-2 text-[10.5px] leading-snug text-[#334155] font-sans">{the.xemTruoc}</pre>}
        </div>
      )}
    </div>
  );
};

/** Các phần ngoài câu trả lời có nguồn: chủ đề cần bàn, thuốc–dị ứng, đối chiếu, tìm kiếm. */
export const PhanKhacTroLy: React.FC<{ phan: Array<{ tacTu: string; ten: string; noiDung: string; canhBao?: string }> }> = ({ phan }) => {
  if (!phan.length) return null;
  return (
    <div className="flex flex-col gap-1.5" data-phan-khac>
      {phan.map((p, i) => (
        <div key={i} className="rounded-xl border border-[#CCE3F0] bg-white p-2.5 text-left">
          <div className="text-[11.5px] font-bold text-[#0C4A6E]">{p.ten}</div>
          {p.noiDung && <div className="mt-0.5 text-[11.5px] text-[#334155] leading-snug select-text">{p.noiDung}</div>}
          {p.canhBao && (
            <div className="mt-1 flex items-start gap-1.5 rounded-lg border border-[#F5E6B8] bg-[#FEF9E7] p-1.5 text-[10.5px] text-[#7A4B00] leading-snug select-text">
              <ShieldAlert size={11} className="mt-0.5 flex-shrink-0" />
              <span>{p.canhBao}</span>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};
