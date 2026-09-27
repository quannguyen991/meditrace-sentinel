import React, { useState } from "react";
import { ExternalLink, Search, RefreshCw, BookOpen } from "lucide-react";

/**
 * Thư viện y khoa: (1) các cổng tài liệu chính thống, link đã mở thử ngày 23/09/2026;
 * (2) ô tìm thẳng trên PubMed qua /api/pubmed-search — KHÔNG qua mô hình, không tốn tiền,
 * không gửi gì ra ai-box. PubMed hiểu từ khoá tiếng Anh.
 */
const CONG: Array<{ nhom: string; ds: Array<{ ten: string; mo: string; url: string }> }> = [
  {
    nhom: "Việt Nam",
    ds: [
      { ten: "Bộ Y tế", mo: "Văn bản, quyết định ban hành hướng dẫn chuyên môn", url: "https://moh.gov.vn" },
      { ten: "Cục Quản lý Khám, chữa bệnh", mo: "Hướng dẫn chẩn đoán và điều trị theo chuyên khoa", url: "https://kcb.vn" },
      { ten: "Cục Quản lý Dược", mo: "Tra cứu thuốc đã cấp phép, thông tin an toàn thuốc", url: "https://dav.gov.vn" },
      { ten: "Cơ sở dữ liệu văn bản pháp luật", mo: "Toàn văn thông tư, quyết định", url: "https://vbpl.vn" },
    ],
  },
  {
    nhom: "Quốc tế",
    ds: [
      { ten: "WHO Guidelines", mo: "Hướng dẫn của Tổ chức Y tế Thế giới", url: "https://www.who.int/publications/who-guidelines" },
      { ten: "NICE Guidance", mo: "Hướng dẫn lâm sàng của Anh", url: "https://www.nice.org.uk/guidance" },
      { ten: "CDC", mo: "Trung tâm Kiểm soát Dịch bệnh Hoa Kỳ", url: "https://www.cdc.gov" },
      { ten: "Cochrane Library", mo: "Tổng quan hệ thống", url: "https://www.cochranelibrary.com" },
      { ten: "PubMed", mo: "Cơ sở dữ liệu bài báo y sinh", url: "https://pubmed.ncbi.nlm.nih.gov" },
      { ten: "MedlinePlus", mo: "Thông tin bệnh cho người bệnh, của NLM", url: "https://medlineplus.gov" },
      { ten: "NHS Conditions", mo: "Mô tả bệnh bằng lời dễ hiểu", url: "https://www.nhs.uk/conditions/" },
    ],
  },
];

type Bai = { title: string; url: string; year?: string; type?: string; journal?: string; abstract?: string };

export const ThuVienYKhoa: React.FC = () => {
  const [q, setQ] = useState("");
  const [cao, setCao] = useState(true);
  // Lọc năm xuất bản: 0 = mọi năm; 5/10 = trong 5/10 năm gần đây.
  const [soNam, setSoNam] = useState<0 | 5 | 10>(10);
  const [dang, setDang] = useState(false);
  const [kq, setKq] = useState<Bai[] | null>(null);
  const [loi, setLoi] = useState<string | null>(null);
  const [mo, setMo] = useState<string | null>(null);

  const tim = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!q.trim()) return;
    setDang(true);
    setLoi(null);
    try {
      const tuNam = soNam ? new Date().getFullYear() - soNam : 0;
      const r = await fetch(`/api/pubmed-search?q=${encodeURIComponent(q.trim())}${cao ? "&cao=1" : ""}${tuNam ? `&tuNam=${tuNam}` : ""}`);
      const d = await r.json();
      if (!r.ok) throw new Error(d?.error || `mã ${r.status}`);
      setKq(d.results || []);
    } catch (err: any) {
      setLoi(err?.message || "Không tìm được");
      setKq(null);
    } finally {
      setDang(false);
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto flex flex-col gap-6 text-left">
      <header>
        <h2 className="font-serif text-2xl font-semibold text-[#0F172A]">Thư viện y khoa</h2>
        <p className="text-[12.5px] text-[#475569] mt-1">
          Tìm thẳng trên PubMed — không qua AI, không gửi nội dung ca khám đi đâu.
        </p>
      </header>

      <form onSubmit={tim} className="bg-white rounded-2xl border border-[#BAE6FD] p-3 flex flex-col gap-2 shadow-tactile-doctor-card">
        <div className="flex items-center gap-2">
          <Search size={15} className="text-[#0284C7] flex-shrink-0" />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Từ khoá tiếng Anh, VD: bell palsy prednisolone"
            className="flex-1 min-w-0 text-[13px] bg-transparent focus:outline-none py-1"
          />
          <button
            type="submit"
            disabled={!q.trim() || dang}
            className="px-3 py-1.5 rounded-lg bg-[#0284C7] text-white text-[12px] font-semibold disabled:opacity-40 flex items-center gap-1"
          >
            {dang ? <RefreshCw size={12} className="animate-spin" /> : <Search size={12} />} Tìm
          </button>
        </div>
        <div className="flex flex-wrap items-center gap-x-4 gap-y-1.5">
          <label className="flex items-center gap-1.5 text-[11.5px] text-[#475569] cursor-pointer w-fit">
            <input type="checkbox" checked={cao} onChange={(e) => setCao(e.target.checked)} />
            Chỉ hướng dẫn thực hành, tổng quan hệ thống, phân tích gộp
          </label>
          <div className="flex items-center gap-1.5 text-[11.5px] text-[#475569]">
            <span>Năm xuất bản:</span>
            <div className="grid grid-cols-3 gap-0.5 p-0.5 rounded-lg bg-[#F1F5F9] border border-[#E2E8F0]" role="radiogroup" aria-label="Năm xuất bản">
              {([[5, "5 năm"], [10, "10 năm"], [0, "Mọi năm"]] as const).map(([n, chu]) => (
                <button key={n} type="button" role="radio" aria-checked={soNam === n} onClick={() => setSoNam(n)}
                  className={`px-2 py-0.5 rounded-md font-semibold ${soNam === n ? "bg-white text-[#0369A1] shadow-sm" : "text-[#64748B]"}`}>
                  {chu}
                </button>
              ))}
            </div>
          </div>
        </div>
      </form>

      {loi && <p className="text-[12px] text-[#8C1D26] bg-[#FDE8E8] border border-[#F5C2C2] rounded-xl p-3">{loi}</p>}
      {kq && (
        <section className="flex flex-col gap-2">
          <p className="text-[11.5px] text-[#64748B]">
            {kq.length
              ? `${kq.length} bài${soNam ? ` từ năm ${new Date().getFullYear() - soNam}` : ""}, xếp theo độ liên quan của PubMed. Bài đã bị rút không hiện.`
              : `Không có bài nào. Thử từ khoá tiếng Anh khác, bỏ lọc bằng chứng cao${soNam ? ", hoặc chọn \u201cMọi năm\u201d" : ""}.`}
          </p>
          {kq.map((b) => (
            <article key={b.url} className="bg-white rounded-xl border border-[#CCE3F0] p-3">
              <a href={b.url} target="_blank" rel="noopener noreferrer" className="text-[13px] font-semibold text-[#0C4A6E] hover:underline">
                {b.title} <ExternalLink size={10} className="inline -mt-0.5" />
              </a>
              <div className="text-[11px] text-[#64748B] mt-0.5 flex flex-wrap gap-x-2">
                {b.type && <span className="font-semibold text-[#0369A1]">{b.type}</span>}
                {b.journal && <span>{b.journal}</span>}
                {b.year && <span>{b.year}</span>}
              </div>
              {b.abstract && (
                <>
                  <p className={`text-[12px] text-[#334155] mt-1.5 leading-relaxed ${mo === b.url ? "" : "line-clamp-2"}`}>{b.abstract}</p>
                  <button onClick={() => setMo(mo === b.url ? null : b.url)} className="text-[11px] text-[#0284C7] mt-0.5">
                    {mo === b.url ? "Thu gọn" : "Đọc tóm tắt"}
                  </button>
                </>
              )}
            </article>
          ))}
        </section>
      )}

      {CONG.map((n) => (
        <section key={n.nhom}>
          <h3 className="text-[11px] font-semibold uppercase tracking-wider text-[#64748B] mb-2">{n.nhom}</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {n.ds.map((c) => (
              <a
                key={c.url}
                href={c.url}
                target="_blank"
                rel="noopener noreferrer"
                className="bg-white rounded-xl border border-[#CCE3F0] p-3 hover:border-[#0284C7] transition-colors flex gap-2.5"
              >
                <BookOpen size={15} className="text-[#0284C7] mt-0.5 flex-shrink-0" />
                <span className="min-w-0">
                  <span className="block text-[13px] font-semibold text-[#0F172A]">{c.ten}</span>
                  <span className="block text-[11.5px] text-[#64748B]">{c.mo}</span>
                  <span className="block text-[10.5px] text-[#0369A1] truncate">{c.url.replace(/^https:\/\//, "")}</span>
                </span>
              </a>
            ))}
          </div>
        </section>
      ))}
    </div>
  );
};
