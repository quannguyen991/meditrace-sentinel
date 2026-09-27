import React, { useEffect, useMemo, useRef, useState } from "react";
import { Search, Sparkles, PenLine, Plus, X, Trash2, Lock, Cpu, Check } from "lucide-react";
import type { Session } from "../types";
import type { NoteMeta } from "./VerificationView";
import { MAU_BAN_NHAP, MAU_CO_SAN, MauVanBan, NhomMau, TEN_NHOM, goiYTheoCa } from "../lib/mauVanBan";
import { useKho } from "../lib/useKho";

/**
 * Nút "Tạo" (kiểu Heidi): gõ để tìm mẫu, hoặc gõ yêu cầu bất kỳ rồi Enter để AI soạn.
 * - "Bản nháp hồ sơ lâm sàng" do Qwen3-4B của dự án sinh tại chỗ, không gửi ra ngoài.
 * - Mọi mục khác do mô hình ngoài soạn từ lời thoại + bản nháp + tab Ngữ cảnh; cần bật công tắc.
 * Không có nhãn "Pro", không có mẫu viết sẵn cho một bệnh cụ thể: gợi ý lấy lý do khám của chính ca.
 */
interface Props {
  isOpen: boolean;
  onClose: () => void;
  session?: Session;
  note?: NoteMeta | null;
  allowExternal: boolean;
  onEnableExternal: () => void;
  /** yeuCau: yêu cầu tự do (khi bác sĩ gõ rồi Enter). */
  onCreate: (mau: MauVanBan, yeuCau?: string) => void;
}

type Loc = "tat_ca" | NhomMau | "cua_toi";

export const TaoVanBanModal: React.FC<Props> = ({
  isOpen, onClose, session, note, allowExternal, onEnableExternal, onCreate,
}) => {
  const [q, setQ] = useState("");
  const [loc, setLoc] = useState<Loc>("tat_ca");
  const [chon, setChon] = useState(0);
  const [mauRieng, setMauRieng] = useKho<MauVanBan>("mau-van-ban");
  const [dangTao, setDangTao] = useState(false);
  const [moi, setMoi] = useState({ ten: "", chiDan: "", nhom: "ho_so" as NhomMau });
  const oTim = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      setQ("");
      setChon(0);
      setDangTao(false);
      setTimeout(() => oTim.current?.focus(), 30);
    }
  }, [isOpen]);

  const coNguon = !!(session?.transcript?.trim() || note || session?.tabs.some((t) => t.type === "context" && t.content.trim()));
  const goiY = useMemo(() => goiYTheoCa(session, note), [session, note]);

  const khop = (m: MauVanBan) => {
    const s = q.trim().toLowerCase();
    if (s && !m.ten.toLowerCase().includes(s)) return false;
    if (loc === "tat_ca") return true;
    if (loc === "cua_toi") return !!m.tuTao;
    return m.nhom === loc;
  };

  // Danh sách phẳng, theo đúng thứ tự hiện trên màn, để phím lên/xuống chạy đúng.
  const muc: Array<{ nhom: string; mau: MauVanBan; yeuCau?: string }> = [];
  const s = q.trim();
  if (s) muc.push({ nhom: "Tạo bằng AI", mau: { id: "tu-do", ten: s, nhom: "ho_so", chiDan: s }, yeuCau: s });
  if (khop(MAU_BAN_NHAP)) muc.push({ nhom: "Bản nháp của dự án", mau: MAU_BAN_NHAP });
  if (!s && loc === "tat_ca") goiY.forEach((m) => muc.push({ nhom: "Gợi ý cho ca này", mau: m }));
  mauRieng.filter(khop).forEach((m) => muc.push({ nhom: "Mẫu của tôi", mau: m }));
  MAU_CO_SAN.filter(khop).forEach((m) => muc.push({ nhom: "Mẫu", mau: m }));

  if (!isOpen) return null;

  const dung = (i: number) => {
    const x = muc[i];
    if (!x) return;
    if (!x.mau.taiCho && !allowExternal) return;
    onCreate(x.mau, x.yeuCau);
    onClose();
  };

  const phim = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setChon((c) => Math.min(c + 1, muc.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setChon((c) => Math.max(c - 1, 0));
    } else if (e.key === "Enter") {
      e.preventDefault();
      dung(chon);
    } else if (e.key === "Escape") {
      onClose();
    }
  };

  const luuMau = () => {
    if (!moi.ten.trim() || !moi.chiDan.trim()) return;
    setMauRieng((ds) => [{ id: `rieng-${Date.now()}`, ten: moi.ten.trim(), chiDan: moi.chiDan.trim(), nhom: moi.nhom, tuTao: true }, ...ds]);
    setMoi({ ten: "", chiDan: "", nhom: "ho_so" });
    setDangTao(false);
    setLoc("cua_toi");
  };

  const CHIP: Array<[Loc, string]> = [
    ["tat_ca", "Tất cả"],
    ["ho_so", TEN_NHOM.ho_so],
    ["nguoi_benh", TEN_NHOM.nguoi_benh],
    ["hanh_chinh", TEN_NHOM.hanh_chinh],
    ["cua_toi", "Mẫu của tôi"],
  ];

  return (
    <div
      className="fixed inset-0 z-50 bg-[#0C4A6E]/30 backdrop-blur-[2px] flex items-start sm:items-center justify-center p-3 sm:p-6"
      onClick={onClose}
    >
      <div
        role="dialog"
        aria-label="Tạo văn bản"
        onClick={(e) => e.stopPropagation()}
        className="w-full max-w-2xl bg-white rounded-3xl shadow-[0_24px_60px_-12px_rgba(2,132,199,0.35)] border border-[#BAE6FD] flex flex-col max-h-[88vh] overflow-hidden"
      >
        <div className="px-4 sm:px-5 pt-4 pb-3 border-b border-[#E0F2FE]">
          <div className="flex items-center gap-2.5">
            <Search size={17} className="text-[#0284C7] flex-shrink-0" />
            <input
              ref={oTim}
              value={q}
              onChange={(e) => {
                setQ(e.target.value);
                setChon(0);
              }}
              onKeyDown={phim}
              placeholder="Tìm mẫu, hoặc gõ văn bản muốn tạo rồi Enter"
              className="flex-1 min-w-0 text-[15px] text-[#0F172A] placeholder-[#94A3B8] bg-transparent focus:outline-none py-1"
            />
            <button onClick={onClose} className="p-1 rounded-lg text-[#64748B] hover:bg-[#E0F2FE]" title="Đóng (Esc)">
              <X size={16} />
            </button>
          </div>
          <div className="flex flex-wrap gap-1.5 mt-3">
            {CHIP.map(([id, chu]) => (
              <button
                key={id}
                onClick={() => {
                  setLoc(id);
                  setChon(0);
                }}
                className={`px-2.5 py-1 rounded-full text-[11px] font-semibold border transition-colors ${
                  loc === id
                    ? "bg-[#0284C7] text-white border-[#0284C7]"
                    : "bg-white text-[#0C4A6E] border-[#CCE3F0] hover:bg-[#F0F9FF]"
                }`}
              >
                {chu}
              </button>
            ))}
          </div>
        </div>

        {!allowExternal && (
          <div className="px-4 sm:px-5 py-2 bg-[#FEF9E7] border-b border-[#F5E6B8] text-[11.5px] text-[#7A4B00] flex flex-wrap items-center justify-between gap-2">
            <span>Văn bản soạn bằng AI cần bật “Mô hình ngoài”: nội dung ca khám sẽ gửi tới máy chủ ai-box.</span>
            <button onClick={onEnableExternal} className="px-2.5 py-1 rounded-lg bg-white border border-[#F5E6B8] font-semibold">
              Bật mô hình ngoài
            </button>
          </div>
        )}
        {!coNguon && (
          <div className="px-4 sm:px-5 py-2 bg-[#F8FBFC] border-b border-[#E0F2FE] text-[11.5px] text-[#475569]">
            Ca này chưa có lời thoại hay ngữ cảnh — ghi âm, gõ lời thoại hoặc điền tab Ngữ cảnh trước.
          </div>
        )}

        <div className="flex-1 overflow-y-auto px-2 sm:px-3 py-2">
          {muc.length === 0 && <p className="px-3 py-6 text-center text-xs text-[#64748B]">Không có mẫu nào khớp.</p>}
          {muc.map((x, i) => {
            const dauNhom = i === 0 || muc[i - 1].nhom !== x.nhom;
            const khoa = !x.mau.taiCho && !allowExternal;
            return (
              <React.Fragment key={`${x.nhom}-${x.mau.id}`}>
                {dauNhom && (
                  <div className="px-3 pt-3 pb-1 text-[10.5px] font-semibold uppercase tracking-wider text-[#64748B]">
                    {x.nhom}
                  </div>
                )}
                <div
                  onMouseEnter={() => setChon(i)}
                  onClick={() => dung(i)}
                  className={`group flex items-center gap-3 px-3 py-2.5 rounded-xl cursor-pointer ${
                    chon === i ? "bg-[#F0F9FF]" : ""
                  } ${khoa ? "opacity-55 cursor-not-allowed" : ""}`}
                  title={khoa ? "Cần bật “Mô hình ngoài”" : x.mau.chiDan || "Qwen3-4B tạo tại chỗ"}
                >
                  <span className="w-7 h-7 rounded-lg bg-[#E0F2FE] text-[#0284C7] flex items-center justify-center flex-shrink-0">
                    {x.mau.taiCho ? <Cpu size={14} /> : x.yeuCau || x.nhom === "Gợi ý cho ca này" ? <Sparkles size={14} /> : <PenLine size={14} />}
                  </span>
                  <span className="flex-1 min-w-0 text-[13.5px] text-[#0F172A] truncate">
                    {x.yeuCau ? <>Tạo: <strong>{x.yeuCau}</strong></> : x.mau.ten}
                  </span>
                  {x.mau.taiCho && (
                    <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded-md bg-[#E6F4F1] text-[#0D5F57] border border-[#BCE3DB] flex-shrink-0">
                      tại chỗ
                    </span>
                  )}
                  {khoa && <Lock size={13} className="text-[#94A3B8] flex-shrink-0" />}
                  {x.mau.tuTao && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setMauRieng((ds) => ds.filter((m) => m.id !== x.mau.id));
                      }}
                      className="p-1 rounded-md text-[#94A3B8] hover:text-red-600 opacity-0 group-hover:opacity-100"
                      title="Xoá mẫu này"
                    >
                      <Trash2 size={13} />
                    </button>
                  )}
                </div>
              </React.Fragment>
            );
          })}
        </div>

        <div className="border-t border-[#E0F2FE] px-4 sm:px-5 py-3 bg-[#F8FBFC]">
          {dangTao ? (
            <div className="flex flex-col gap-2">
              <input
                value={moi.ten}
                onChange={(e) => setMoi({ ...moi, ten: e.target.value })}
                placeholder="Tên mẫu, VD: Phiếu khám sức khoẻ học sinh"
                className="px-3 py-2 rounded-xl border border-[#CCE3F0] text-[13px] focus:outline-none focus:border-[#0284C7] bg-white"
              />
              <textarea
                value={moi.chiDan}
                onChange={(e) => setMoi({ ...moi, chiDan: e.target.value })}
                placeholder="Mẫu gồm những mục nào, viết cho ai, dài bao nhiêu…"
                rows={3}
                className="px-3 py-2 rounded-xl border border-[#CCE3F0] text-[13px] focus:outline-none focus:border-[#0284C7] bg-white resize-none"
              />
              <div className="flex flex-wrap items-center gap-2">
                <select
                  value={moi.nhom}
                  onChange={(e) => setMoi({ ...moi, nhom: e.target.value as NhomMau })}
                  className="px-2 py-1.5 rounded-lg border border-[#CCE3F0] text-[12px] bg-white"
                >
                  {(Object.keys(TEN_NHOM) as NhomMau[]).map((n) => (
                    <option key={n} value={n}>{TEN_NHOM[n]}</option>
                  ))}
                </select>
                <div className="flex-1" />
                <button onClick={() => setDangTao(false)} className="px-3 py-1.5 rounded-lg text-[12px] text-[#475569] hover:bg-[#E0F2FE]">
                  Huỷ
                </button>
                <button
                  onClick={luuMau}
                  disabled={!moi.ten.trim() || !moi.chiDan.trim()}
                  className="px-3 py-1.5 rounded-lg text-[12px] font-semibold bg-[#0284C7] text-white disabled:opacity-40 flex items-center gap-1"
                >
                  <Check size={13} /> Lưu mẫu
                </button>
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-between gap-2">
              <button onClick={() => setDangTao(true)} className="flex items-center gap-1.5 text-[13px] font-semibold text-[#0C4A6E] hover:text-[#0284C7]">
                <Plus size={15} /> Tạo mẫu mới
              </button>
              <span className="text-[11px] text-[#64748B] hidden sm:inline">↑↓ chọn · Enter tạo · Esc đóng</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
