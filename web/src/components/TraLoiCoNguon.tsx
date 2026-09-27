import React, { useState } from "react";
import { ClinicalChatMessage, ClinicalSource } from "../types";
import {
  BookOpen, ChevronDown, ChevronUp, ShieldAlert, Lightbulb, ThumbsUp, ThumbsDown, Copy, Check,
  SearchCheck, ListPlus, CornerDownRight, Stethoscope, Scale,
} from "lucide-react";

/**
 * Câu trả lời tra cứu kiểu Heidi (24/09):
 *  - đầu: "N tài liệu đã tra · Xem nguồn" (gập được);
 *  - mỗi ý có THẺ NGUỒN ngay sau (bấm mở văn bản gốc) thay vì số [1];
 *  - hộp cam "Lưu ý an toàn" (từ ca khám + tài liệu), hộp xanh "Điểm chính";
 *  - "Tài liệu tham khảo · N đã trích"; thanh thao tác; "Hỏi tiếp" bấm để hỏi.
 * Không có cấu trúc (tin cũ, mô hình trả sai JSON) thì nơi gọi hiện markdown như trước.
 */

const HUY_HIEU: Record<string, { chu: string; mau: string }> = {
  kcb: { chu: "BYT", mau: "bg-[#B91C1C] text-white" },
  msd: { chu: "MSD", mau: "bg-[#0F766E] text-white" },
  fda: { chu: "FDA", mau: "bg-[#1D4ED8] text-white" },
  nice: { chu: "NICE", mau: "bg-[#4C1D95] text-white" },
  who: { chu: "WHO", mau: "bg-[#0284C7] text-white" },
  cdc: { chu: "CDC", mau: "bg-[#1E3A8A] text-white" },
  medlineplus: { chu: "NLM", mau: "bg-[#15803D] text-white" },
  pubmed: { chu: "PM", mau: "bg-[#334155] text-white" },
  statpearls: { chu: "SP", mau: "bg-[#C2410C] text-white" },
  aafp: { chu: "AFP", mau: "bg-[#9F1239] text-white" },
};

const HuyHieu: React.FC<{ nhom?: string }> = ({ nhom }) => {
  const h = HUY_HIEU[nhom || ""] || { chu: "•", mau: "bg-[#94A3B8] text-white" };
  return (
    <span className={`inline-flex items-center justify-center min-w-[22px] h-[14px] px-0.5 rounded-[3px] text-[7.5px] font-bold tracking-tight leading-none ${h.mau}`}>
      {h.chu}
    </span>
  );
};

/** Nhãn đỏ khi số trong ý không có trong văn bản gốc được trích. */
const SoLech: React.FC<{ lech?: string[] }> = ({ lech }) =>
  lech && lech.length ? (
    <span className="block mt-0.5 text-[10.5px] font-semibold text-[#B91C1C]">
      ⚠ Số chưa thấy trong văn bản gốc: {lech.join(", ")} — mở nguồn kiểm lại
    </span>
  ) : null;

const TheNguon: React.FC<{ so: number[]; nguon: ClinicalSource[] }> = ({ so, nguon }) => (
  <>
    {so.map((n) => {
      const s = nguon.find((x) => x.so === n);
      if (!s) return null;
      return (
        <a
          key={n}
          href={s.url}
          target="_blank"
          rel="noopener noreferrer"
          title={`${s.name} — ${s.domain}`}
          className="inline-flex items-center gap-1 align-middle ml-1 my-0.5 px-1.5 py-[1px] rounded-md bg-[#F1F5F9] border border-[#E2E8F0] text-[10.5px] text-[#475569] hover:bg-[#E0F2FE] hover:text-[#0369A1] hover:border-[#BAE6FD] transition-colors max-w-full"
        >
          <HuyHieu nhom={s.nhom} />
          <span className="truncate">{s.nhan || s.domain}</span>
        </a>
      );
    })}
  </>
);

interface Props {
  msg: ClinicalChatMessage;
  onAsk: (cauHoi: string) => void;
  onCheckOther: (msg: ClinicalChatMessage) => void;
  onAddToContext: (text: string) => void;
}

export const TraLoiCoNguon: React.FC<Props> = ({ msg, onAsk, onCheckOther, onAddToContext }) => {
  const ct = msg.cauTruc!;
  const nguon = msg.sources || [];
  const daTrich = nguon.filter((s) => s.cited);
  const [moNguon, setMoNguon] = useState(false);
  const [moThamKhao, setMoThamKhao] = useState(false);
  const [danhGia, setDanhGia] = useState<"tot" | "chua" | null>(null);
  const [daChep, setDaChep] = useState(false);
  const [daThem, setDaThem] = useState(false);

  // Văn bản thuần để chép / thêm vào ngữ cảnh: thay số tài liệu bằng tên nhãn nguồn.
  const tenNguon = (so: number[]) =>
    so.map((n) => nguon.find((x) => x.so === n)?.nhan).filter(Boolean).map((x) => `[${x}]`).join(" ");
  const vanThuan = [
    ct.ca_kham && `Trong ca khám: ${ct.ca_kham}`,
    ct.tom_tat,
    ...ct.phuong_an.map((p) => `- ${p.ten}: ${p.noi_dung} ${tenNguon(p.nguon)}`.trim()),
    ...ct.luu_y_ca.map((x) => `! ${x}`),
    ...ct.an_toan.map((x) => `! ${x.noi_dung} ${tenNguon(x.nguon)}`.trim()),
    ct.khac_nhau && `Trong nước / nước ngoài khác nhau: ${ct.khac_nhau}`,
    "(Tra cứu tham khảo — bác sĩ đối chiếu văn bản gốc.)",
  ].filter(Boolean).join("\n");

  const coLuuY = ct.luu_y_ca.length > 0 || ct.an_toan.length > 0;
  // Mô hình đôi khi vẫn viết "[2]" trong đoạn văn — đổi thành tên nguồn cho bác sĩ đọc được.
  const doiSo = (van: string) =>
    van.replace(/\[(\d+(?:\s*,\s*\d+)*)\]/g, (m, ds: string) => {
      const ten = ds.split(",").map((n) => nguon.find((x) => x.so === Number(n.trim()))?.nhan).filter(Boolean);
      return ten.length ? `(${ten.join(", ")})` : m;
    }).replace(/\)\s*\(/g, "; ");

  return (
    <div className="flex flex-col gap-2.5">
      {/* N tài liệu đã tra */}
      <div className="rounded-xl bg-[#F0F9FF] border border-[#CCE3F0]">
        <button
          onClick={() => setMoNguon(!moNguon)}
          className="w-full flex items-center justify-between px-3 py-2 text-[11.5px] text-[#0C4A6E]"
        >
          <span className="flex items-center gap-1.5">
            <BookOpen size={12} className="text-[#0284C7]" />
            {nguon.length} tài liệu đã tra
          </span>
          <span className="flex items-center gap-1 text-[#0369A1]">
            Xem nguồn {moNguon ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
          </span>
        </button>
        {moNguon && (
          <ul className="px-3 pb-2.5 space-y-1.5">
            {nguon.map((s) => (
              <li key={s.so} className="flex items-center gap-2 text-[11px] min-w-0">
                <HuyHieu nhom={s.nhom} />
                <a href={s.url} target="_blank" rel="noopener noreferrer" className="truncate text-[#0F172A] hover:text-[#0369A1] hover:underline flex-1 min-w-0" title={s.name}>
                  {s.name}
                </a>
                <span className="text-[10px] text-[#64748B] flex-shrink-0">{s.nhan}</span>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Không bọc thêm khung ngoài (ngăn phải chỉ ~390px): các hộp tràn hết bề rộng, cột chữ rộng hơn. */}
      <div className="text-[12.5px] text-[#1E293B] leading-relaxed select-text space-y-3">
        {ct.ca_kham && (
          <div className="flex gap-2 p-2.5 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
            <Stethoscope size={13} className="text-[#0284C7] flex-shrink-0 mt-0.5" />
            <div><span className="font-semibold text-[#0C4A6E]">Trong ca khám: </span>{doiSo(ct.ca_kham)}</div>
          </div>
        )}

        {ct.tom_tat && <p className="px-0.5 text-[13px] text-[#0F172A]">{doiSo(ct.tom_tat)}</p>}

        {ct.phuong_an.length > 0 && (
          <div className="rounded-xl bg-[#EFF6FF] border border-[#DBEAFE] p-3 pr-2.5">
            <div className="flex items-center gap-1.5 text-[13px] font-bold text-[#0C4A6E] mb-1.5">
              <Lightbulb size={13} className="text-[#0284C7]" /> Điểm chính theo tài liệu
            </div>
            <ul className="list-disc pl-4 space-y-2.5 marker:text-[#93C5FD]">
              {ct.phuong_an.map((p, i) => (
                <li key={i}>
                  <span className="font-semibold text-[#0F172A]">{p.ten}</span>
                  {p.noi_dung && <> — {p.noi_dung}</>}
                  <TheNguon so={p.nguon} nguon={nguon} />
                  <SoLech lech={p.lech} />
                </li>
              ))}
            </ul>
          </div>
        )}

        {coLuuY && (
          <div className="rounded-xl bg-[#FFF7ED] border border-[#FED7AA] p-3 pr-2.5">
            <div className="flex items-center gap-1.5 text-[13px] font-bold text-[#9A3412] mb-1.5">
              <ShieldAlert size={13} className="text-[#EA580C]" /> Lưu ý an toàn
            </div>
            <ul className="list-disc pl-4 space-y-1.5 text-[#431407]">
              {ct.luu_y_ca.map((x, i) => (
                <li key={`ca${i}`}><span className="text-[10px] font-semibold text-[#C2410C] mr-1">TỪ CA KHÁM</span>{doiSo(x)}</li>
              ))}
              {ct.an_toan.map((x, i) => (
                <li key={`tl${i}`}>{x.noi_dung}<TheNguon so={x.nguon} nguon={nguon} /><SoLech lech={x.lech} /></li>
              ))}
            </ul>
          </div>
        )}

        {ct.khac_nhau && (
          <div className="flex gap-2 p-2.5 rounded-xl bg-[#F5F3FF] border border-[#DDD6FE] text-[#3B0764]">
            <Scale size={13} className="text-[#7C3AED] flex-shrink-0 mt-0.5" />
            <div><span className="font-semibold">Trong nước và nước ngoài khác nhau: </span>{doiSo(ct.khac_nhau)}</div>
          </div>
        )}

        {ct.khong_du && <p className="text-[11.5px] text-[#64748B]"><span className="font-semibold">Tài liệu chưa trả lời được: </span>{doiSo(ct.khong_du)}</p>}

        <p className="text-[11px] text-[#7A4B00] bg-[#FFFBEB] border-l-4 border-[#F2DFA8] px-3 py-1.5 rounded-r-lg">
          Chỉ để tham khảo — không phải khẳng định, chẩn đoán hay chỉ định điều trị. Bác sĩ đối chiếu văn bản gốc và tự quyết định.
        </p>

        {/* Tài liệu tham khảo */}
        <div className="pt-2 border-t border-[#E2ECF3]">
          <button onClick={() => setMoThamKhao(!moThamKhao)} className="w-full flex items-center justify-between text-[12px] font-semibold text-[#0C4A6E]">
            Tài liệu tham khảo
            <span className="flex items-center gap-1 text-[11px] font-normal text-[#64748B]">
              {daTrich.length} đã trích {moThamKhao ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
            </span>
          </button>
          {moThamKhao && (
            <ol className="mt-2 space-y-1.5">
              {[...daTrich, ...nguon.filter((s) => !s.cited)].map((s) => (
                <li key={s.so} className={`flex items-start gap-1.5 text-[11px] ${s.cited ? "" : "opacity-60"}`}>
                  <HuyHieu nhom={s.nhom} />
                  <a href={s.url} target="_blank" rel="noopener noreferrer" className="text-[#0369A1] hover:underline break-words min-w-0">
                    {s.name}<span className="text-[#64748B]"> · {s.domain}</span>
                  </a>
                  {!s.cited && <span className="text-[10px] text-[#94A3B8] flex-shrink-0">chưa trích</span>}
                </li>
              ))}
            </ol>
          )}
        </div>

        {/* Thanh thao tác */}
        <div className="flex flex-wrap items-center gap-1 pt-2 border-t border-[#E2ECF3] text-[#64748B]">
          <button onClick={() => setDanhGia(danhGia === "tot" ? null : "tot")} title="Trả lời hữu ích"
            className={`p-1.5 rounded-md hover:bg-[#E0F2FE] ${danhGia === "tot" ? "text-[#0284C7]" : ""}`}>
            <ThumbsUp size={13} className={danhGia === "tot" ? "fill-current" : ""} />
          </button>
          <button onClick={() => setDanhGia(danhGia === "chua" ? null : "chua")} title="Trả lời chưa tốt"
            className={`p-1.5 rounded-md hover:bg-[#E0F2FE] ${danhGia === "chua" ? "text-[#B91C1C]" : ""}`}>
            <ThumbsDown size={13} className={danhGia === "chua" ? "fill-current" : ""} />
          </button>
          {msg.question && (
            <button onClick={() => onCheckOther(msg)} title="Hỏi lại, bỏ các nguồn đã trích — xem nguồn khác nói gì"
              className="flex items-center gap-1 px-2 py-1 rounded-md text-[11px] hover:bg-[#E0F2FE] hover:text-[#0369A1]">
              <SearchCheck size={13} /> Tra nguồn khác
            </button>
          )}
          <span className="flex-1" />
          <button
            onClick={() => { navigator.clipboard.writeText(vanThuan); setDaChep(true); setTimeout(() => setDaChep(false), 1500); }}
            title="Chép câu trả lời" className="p-1.5 rounded-md hover:bg-[#E0F2FE] hover:text-[#0369A1]"
          >
            {daChep ? <Check size={13} className="text-emerald-600" /> : <Copy size={13} />}
          </button>
          <button
            onClick={() => { onAddToContext(vanThuan); setDaThem(true); }}
            title="Thêm vào tab Ngữ cảnh" className="p-1.5 rounded-md hover:bg-[#E0F2FE] hover:text-[#0369A1]"
          >
            {daThem ? <Check size={13} className="text-emerald-600" /> : <ListPlus size={13} />}
          </button>
        </div>
        {msg.meta && <div className="text-[10px] text-[#94A3B8] leading-snug">{msg.meta}</div>}
      </div>

      {ct.hoi_tiep.length > 0 && (
        <div className="px-1">
          <div className="text-[12px] font-semibold text-[#0C4A6E] mb-1">Hỏi tiếp</div>
          {ct.hoi_tiep.map((q, i) => (
            <button key={i} onClick={() => onAsk(q)}
              className="w-full flex items-start gap-1.5 text-left text-[11.5px] text-[#475569] py-1 hover:text-[#0369A1]">
              <CornerDownRight size={12} className="flex-shrink-0 mt-0.5 text-[#94A3B8]" /> {q}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};
