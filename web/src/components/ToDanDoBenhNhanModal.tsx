import React, { useEffect, useRef, useState } from "react";
import {
  AlertTriangle,
  Calendar,
  Check,
  Clock,
  FileHeart,
  HeartPulse,
  Info,
  Pencil,
  Plus,
  Printer,
  RotateCcw,
  ShieldCheck,
  Square,
  Trash2,
  Volume2,
  X,
} from "lucide-react";

export interface Thuoc {
  id: number;
  ten: string;
  loai: string;
  nhan: string;
  mau: string;
  sang: string;
  trua: string;
  chieu: string;
  toi: string;
  loiDan: string;
}

export interface MucDan {
  id: number;
  tieuDe: string;
  noiDung: string;
}

export interface HoSoDD {
  coSo: string;
  khoa: string;
  diaChi: string;
  hotline: string;
  maMau: string;
  soHoSo: string;
  ngayIn: string;
  soDon: string;
  tuoiGioi: string;
  maBhyt: string;
  bacSi: string;
  chanDoan: string;
  thuoc: Thuoc[];
  anUong: MucDan[];
  theoDoi: MucDan[];
  dauHieu: MucDan[];
  ngayTaiKham: string;
  diaDiemTaiKham: string;
  ngayKy: string;
  cchn: string;
}

/**
 * Nội dung mẫu khi chưa ai sửa. Ngoặc vuông là chỗ điền: hiện thành nhãn nét đứt.
 * Bác sĩ thay bằng chữ thật thì không còn ngoặc. Bảng thuốc là ca mẫu để minh hoạ bố cục.
 */
export const HO_SO_MAU: HoSoDD = {
  coSo: "[Tên cơ sở khám bệnh]",
  khoa: "[Khoa / phòng khám]",
  diaChi: "[Địa chỉ]",
  hotline: "[Số hotline]",
  maMau: "[mã mẫu]",
  soHoSo: "[số hồ sơ]",
  ngayIn: "[ngày in]",
  soDon: "[số đơn]",
  tuoiGioi: "[tuổi / giới]",
  maBhyt: "[mã BHYT]",
  bacSi: "[tên bác sĩ điều trị]",
  chanDoan: "[chẩn đoán xuất viện]",
  thuoc: [
    {
      id: 1,
      ten: "Plavix (Clopidogrel) 75mg",
      loai: "Thuốc chống kết tập tiểu cầu (bảo vệ Stent)",
      nhan: "BẮT BUỘC",
      mau: "bg-red-50 text-red-700 border-red-200",
      sang: "1 viên",
      trua: "—",
      chieu: "—",
      toi: "—",
      loiDan: "Uống sau ăn sáng no 15 phút. Tuyệt đối KHÔNG tự ý ngừng thuốc vì có nguy cơ hình thành cục máu đông gây tắc Stent tử vong!",
    },
    {
      id: 2,
      ten: "Coversyl (Perindopril) 5mg",
      loai: "Thuốc hạ huyết áp & bảo vệ tim",
      nhan: "ĐÍNH CHÍNH LIỀU",
      mau: "bg-emerald-50 text-emerald-700 border-emerald-200",
      sang: "1 viên",
      trua: "—",
      chieu: "—",
      toi: "—",
      loiDan: "Uống 1 viên vào buổi sáng cùng 1 cốc nước ấm đầy. (Chốt an toàn K4 đã loại trừ câu nói nhầm 2 viên của người bệnh).",
    },
    {
      id: 3,
      ten: "Nexium (Esomeprazole) 40mg",
      loai: "Thuốc giảm tiết acid bảo vệ dạ dày",
      nhan: "AN TOÀN DDI",
      mau: "bg-sky-50 text-sky-700 border-sky-200",
      sang: "1 viên",
      trua: "—",
      chieu: "—",
      toi: "—",
      loiDan: "Uống trước khi ăn sáng 30-60 phút. (Đã thay thế Omeprazole nhằm ngăn triệt để tương tác dược lý DDI làm mất tác dụng của Plavix).",
    },
    {
      id: 4,
      ten: "Atorvastatin (Lipitor) 20mg",
      loai: "Thuốc hạ mỡ máu & ổn định mảng xơ vữa",
      nhan: "DUY TRÌ",
      mau: "bg-indigo-50 text-indigo-700 border-indigo-200",
      sang: "—",
      trua: "—",
      chieu: "—",
      toi: "1 viên",
      loiDan: "Uống buổi tối trước khi đi ngủ. Duy trì màng nội mạc mạch máu ổn định và chống tái hẹp lòng mạch.",
    },
  ],
  anUong: [
    { id: 1, tieuDe: "Ăn giảm muối", noiDung: "dưới 5g/ngày (khoảng 1 thìa cà phê gạt ngang). Hạn chế cá khô, dưa muối, đồ hộp." },
    { id: 2, tieuDe: "Hạn chế mỡ động vật", noiDung: "dùng dầu thực vật, ưu tiên cá, thịt nạc luộc, nhiều rau xanh và củ quả." },
    { id: 3, tieuDe: "Không hút thuốc, không uống bia rượu", noiDung: "khói thuốc làm co thắt mạch vành và tăng nguy cơ đông máu." },
    { id: 4, tieuDe: "Vận động", noiDung: "đi bộ chậm rãi 20–30 phút/ngày, không mang vác vật nặng quá [giới hạn do bác sĩ ghi]." },
  ],
  theoDoi: [
    { id: 1, tieuDe: "Đo huyết áp", noiDung: "vào hai khung giờ cố định theo dặn dò của bác sĩ. Ghi vào sổ nhật ký huyết áp." },
    { id: 2, tieuDe: "Mục tiêu", noiDung: "[khoảng huyết áp mục tiêu]. Nếu thấp hơn [ngưỡng thấp] hoặc cao hơn [ngưỡng cao] kèm chóng mặt, gọi bác sĩ ngay." },
    { id: 3, tieuDe: "Uống nước", noiDung: "[lượng nước do bác sĩ dặn], chia đều trong ngày, không uống nhiều ngay trước giờ ngủ." },
  ],
  dauHieu: [
    { id: 1, tieuDe: "", noiDung: "Đau thắt ngực dữ dội, kéo dài không đỡ khi nghỉ, lan lên hàm hoặc cánh tay trái." },
    { id: 2, tieuDe: "", noiDung: "Khó thở dồn dập, vã mồ hôi lạnh, hoa mắt, chóng mặt hoặc ngất đột ngột." },
    { id: 3, tieuDe: "", noiDung: "Dấu hiệu chảy máu: phân đen như hắc ín, nôn ra máu hoặc dịch nâu đỏ, ho ra máu, chảy máu răng khó cầm." },
    { id: 4, tieuDe: "", noiDung: "Huyết áp đo nhiều lần liên tiếp vượt [ngưỡng cao] hoặc tụt dưới [ngưỡng thấp] kèm li bì." },
  ],
  ngayTaiKham: "[ngày tái khám]",
  diaDiemTaiKham: "[địa điểm tái khám]",
  ngayKy: "[ngày tháng năm]",
  cchn: "[số chứng chỉ hành nghề]",
};

// Mã cho mục thêm mới. Mục mẫu dùng mã 1..n cố định để khoá của React không đổi giữa các lần vẽ.
let maSo = 100;
const taoMa = () => ++maSo;

type KhoaBuoi = "sang" | "trua" | "chieu" | "toi";

// Bốn buổi uống, mỗi buổi một màu nhạt để dễ nhìn khi in.
const BUOI_UONG: ReadonlyArray<{ khoa: KhoaBuoi; nhan: string; mau: string }> = [
  { khoa: "sang", nhan: "Sáng", mau: "bg-amber-100 text-amber-900" },
  { khoa: "trua", nhan: "Trưa", mau: "bg-sky-100 text-sky-900" },
  { khoa: "chieu", nhan: "Chiều", mau: "bg-orange-100 text-orange-900" },
  { khoa: "toi", nhan: "Tối", mau: "bg-indigo-100 text-indigo-900" },
];

// Không gắn chiều rộng ở đây: mỗi ô tự quyết (w-full, w-40, flex-1) để không đè lên nhau trong hàng ngang.
const LOP_O =
  "rounded-md border border-dashed border-amber-400 bg-amber-50/60 px-2 py-1 text-[12.5px] text-slate-900 placeholder:text-slate-400 focus:border-solid focus:border-[#0284C7] focus:bg-white focus:outline-none";

/** Chỗ điền khi nối với ca thật. Giữ ngoặc vuông để vẫn đọc được khi in đen trắng. */
const Cho = ({ children }: { children: React.ReactNode }) => (
  <span className="inline-block px-1.5 rounded bg-amber-50 border border-dashed border-amber-400 text-amber-800 font-medium whitespace-nowrap">
    [{children}]
  </span>
);

/** Đoạn chữ có ngoặc vuông thì hiện các ngoặc đó thành chỗ điền. */
const Chu = ({ text }: { text: string }) => (
  <>
    {text.split(/(\[[^\]]*\])/g).map((doan, i) =>
      /^\[[^\]]*\]$/.test(doan) ? (
        <Cho key={i}>{doan.slice(1, -1)}</Cho>
      ) : (
        <React.Fragment key={i}>{doan}</React.Fragment>
      ),
    )}
  </>
);

/** Chữ khi xem. Ô trống thì hiện nhãn gợi ý để bác sĩ biết cần điền gì. */
const ChuHoacCho = ({ text, goiY }: { text: string; goiY: string }) =>
  text.trim() ? <Chu text={text} /> : <Cho>{goiY}</Cho>;

interface TruongProps {
  gia: string;
  goiY: string;
  sua: boolean;
  onDoi: (v: string) => void;
  nhieuDong?: boolean;
}

/** Một trường chữ: khi xem thì hiện như văn bản, khi sửa thì thành ô nhập. */
const Truong = ({ gia, goiY, sua, onDoi, nhieuDong = false }: TruongProps) => {
  if (!sua) return <ChuHoacCho text={gia} goiY={goiY} />;
  return nhieuDong ? (
    <textarea rows={2} value={gia} placeholder={goiY} onChange={(e) => onDoi(e.target.value)} className={`${LOP_O} w-full resize-y`} />
  ) : (
    <input value={gia} placeholder={goiY} onChange={(e) => onDoi(e.target.value)} className={`${LOP_O} w-full`} />
  );
};

interface DanhSachProps {
  ds: MucDan[];
  sua: boolean;
  onDoi: (ds: MucDan[]) => void;
  coTieuDe: boolean;
  dauDo?: boolean;
  nhanThem: string;
}

/** Danh sách mục: khi xem là gạch đầu dòng, khi sửa thì thêm, bớt và sửa từng mục. */
const DanhSachMuc = ({ ds, sua, onDoi, coTieuDe, dauDo = false, nhanThem }: DanhSachProps) => {
  const capNhat = (id: number, phan: Partial<MucDan>) => onDoi(ds.map((m) => (m.id === id ? { ...m, ...phan } : m)));
  const xoa = (id: number) => onDoi(ds.filter((m) => m.id !== id));
  const them = () => onDoi([...ds, { id: taoMa(), tieuDe: "", noiDung: "" }]);

  if (!sua) {
    return (
      <ul
        className={
          dauDo
            ? "grid grid-cols-1 sm:grid-cols-2 gap-2.5 text-[12px] text-red-950 font-medium"
            : "space-y-2 text-slate-700 pl-4 list-disc text-[12px] leading-relaxed marker:text-slate-400"
        }
      >
        {ds.map((m) => (
          <li key={m.id} className={dauDo ? "flex items-start gap-2" : undefined}>
            {dauDo && <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-red-600 flex-shrink-0" />}
            <span>
              {coTieuDe && m.tieuDe.trim() && <strong>{m.tieuDe}: </strong>}
              <Chu text={m.noiDung} />
            </span>
          </li>
        ))}
      </ul>
    );
  }

  return (
    <div className="space-y-2">
      {ds.map((m) => (
        <div key={m.id} className="rounded-xl border border-dashed border-amber-300 bg-white p-2.5 flex items-start gap-2">
          {coTieuDe && (
            <input
              value={m.tieuDe}
              placeholder="Tiêu đề"
              onChange={(e) => capNhat(m.id, { tieuDe: e.target.value })}
              className={`${LOP_O} w-40 flex-shrink-0`}
            />
          )}
          <textarea
            rows={2}
            value={m.noiDung}
            placeholder="Nội dung"
            onChange={(e) => capNhat(m.id, { noiDung: e.target.value })}
            className={`${LOP_O} w-full flex-1 min-w-0 resize-y`}
          />
          <button
            type="button"
            onClick={() => xoa(m.id)}
            title="Xoá mục này"
            className="p-1.5 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 flex-shrink-0"
          >
            <Trash2 size={14} />
          </button>
        </div>
      ))}
      <button type="button" onClick={them} className="inline-flex items-center gap-1.5 text-[12px] font-semibold text-[#0369A1] hover:text-[#0284C7]">
        <Plus size={14} />
        <span>{nhanThem}</span>
      </button>
    </div>
  );
};

interface ToDanDoBenhNhanModalProps {
  isOpen: boolean;
  onClose: () => void;
  patientName: string;
  noteContent?: string;
  /** Nội dung tờ dặn dò của ca này. Trang cha giữ để không mất khi đổi tab. */
  hoSo: HoSoDD;
  onDoiHoSo: (hoSo: HoSoDD) => void;
}

export const ToDanDoBenhNhanModal: React.FC<ToDanDoBenhNhanModalProps> = ({
  isOpen,
  onClose,
  patientName,
  hoSo,
  onDoiHoSo,
}) => {
  const printRef = useRef<HTMLDivElement>(null);
  const [sua, setSua] = useState(false);
  const [dangDoc, setDangDoc] = useState(false);

  useEffect(() => {
    if (!isOpen && typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      setDangDoc(false);
    }
    return () => {
      if (typeof window !== "undefined" && "speechSynthesis" in window) {
        window.speechSynthesis.cancel();
      }
    };
  }, [isOpen]);

  if (!isOpen) return null;

  const docHuongDan = () => {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) return;
    if (dangDoc) {
      window.speechSynthesis.cancel();
      setDangDoc(false);
      return;
    }
    const noiDung = [
      `Hướng dẫn chăm sóc cho bệnh nhân ${patientName}. Chẩn đoán: ${hoSo.chanDoan}.`,
      ...hoSo.thuoc.map(
        (t) =>
          `Thuốc ${t.ten}: buổi sáng ${t.sang || "không"}, trưa ${t.trua || "không"}, chiều ${t.chieu || "không"}, tối ${t.toi || "không"}. ${t.loiDan}.`
      ),
      `Lưu ý quay lại bệnh viện ngay nếu có dấu hiệu: ${hoSo.dauHieu.map((d) => d.noiDung).join("; ")}.`,
    ].join(" ");
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(noiDung);
    u.lang = "vi-VN";
    u.rate = 0.95;
    u.onend = () => setDangDoc(false);
    u.onerror = () => setDangDoc(false);
    setDangDoc(true);
    window.speechSynthesis.speak(u);
  };

  const doi = (phan: Partial<HoSoDD>) => onDoiHoSo({ ...hoSo, ...phan });
  const truong = (khoa: keyof HoSoDD) => (v: string) => doi({ [khoa]: v } as Partial<HoSoDD>);

  const suaThuoc = (id: number, phan: Partial<Thuoc>) =>
    doi({ thuoc: hoSo.thuoc.map((t) => (t.id === id ? { ...t, ...phan } : t)) });
  const xoaThuoc = (id: number) => doi({ thuoc: hoSo.thuoc.filter((t) => t.id !== id) });
  const themThuoc = () =>
    doi({
      thuoc: [
        ...hoSo.thuoc,
        { id: taoMa(), ten: "", loai: "", nhan: "", mau: "bg-sky-50 text-sky-700 border-sky-200", sang: "", trua: "", chieu: "", toi: "", loiDan: "" },
      ],
    });

  const inTo = () => {
    setSua(false);
    // Đợi khung xem được vẽ lại xong rồi mới in, để không in cả ô nhập.
    setTimeout(() => window.print(), 0);
  };

  const dong = () => {
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }
    setDangDoc(false);
    setSua(false);
    onClose();
  };

  const khoiPhuc = () => {
    if (window.confirm("Khôi phục nội dung mẫu? Mọi chỗ đã sửa của ca này sẽ mất.")) onDoiHoSo(HO_SO_MAU);
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-2xs flex items-center justify-center p-3 sm:p-6 animate-in fade-in duration-150">
      <div className="bg-white rounded-2xl border border-[#BAE6FD] shadow-2xl w-full max-w-4xl max-h-[92vh] flex flex-col overflow-hidden text-left">
        {/* Đầu cửa sổ (không in) */}
        <div className="px-4 sm:px-5 py-3 bg-white border-b border-slate-100 flex items-center justify-between gap-3 flex-shrink-0 print:hidden">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-8 h-8 rounded-xl bg-sky-100 text-sky-700 flex items-center justify-center flex-shrink-0">
              <FileHeart size={16} />
            </div>
            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-2">
                <h3 className="font-serif text-[17px] font-semibold text-[#0F172A]">
                  Tờ dặn dò xuất viện & hướng dẫn điều trị ngoại trú
                </h3>
                <span className="px-2 py-0.5 rounded-md text-[10.5px] font-semibold bg-amber-100 text-amber-800 border border-amber-200">
                  Minh hoạ
                </span>
              </div>
              <p className="text-[11.5px] text-slate-500">
                Bản in A4 cho người bệnh và gia đình • {patientName}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 flex-shrink-0">
            <button
              type="button"
              onClick={docHuongDan}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-xl border transition-all whitespace-nowrap cursor-pointer ${
                dangDoc
                  ? "bg-emerald-600 border-emerald-600 text-white font-semibold"
                  : "bg-emerald-50 border-emerald-200 text-emerald-800 hover:bg-emerald-100 font-medium"
              }`}
              title="Đọc to hướng dẫn uống thuốc bằng tiếng Việt cho người cao tuổi/mắt kém"
            >
              {dangDoc ? <Square size={12} /> : <Volume2 size={13} />}
              <span>{dangDoc ? "Dừng đọc" : "Đọc to"}</span>
            </button>
            <button
              type="button"
              onClick={() => setSua(!sua)}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-xl border transition-all whitespace-nowrap ${
                sua
                  ? "bg-amber-50 border-amber-300 text-amber-800 font-semibold"
                  : "bg-white border-[#BAE6FD] text-[#0C4A6E] hover:bg-[#F0F9FF] font-medium"
              }`}
            >
              {sua ? <Check size={13} /> : <Pencil size={13} className="text-[#0284C7]" />}
              <span>{sua ? "Xong sửa" : "Sửa nội dung"}</span>
            </button>
            <button
              onClick={inTo}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-[#0284C7] hover:bg-[#0369A1] text-white font-semibold text-xs rounded-xl shadow-tactile-doctor transition-all active:scale-95 cursor-pointer"
            >
              <Printer size={13} />
              <span>In tờ dặn dò (A4)</span>
            </button>
            <button
              onClick={dong}
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
              title="Đóng"
            >
              <X size={16} />
            </button>
          </div>
        </div>

        {/* Nội dung tờ dặn dò (khổ A4) */}
        <div ref={printRef} className="flex-1 overflow-y-auto bg-white text-slate-900 print:p-0">
          <div className="p-5 sm:p-8 space-y-6">
            {/* Ghi chú minh hoạ: giữ cả khi in */}
            <div className="flex items-start gap-2 rounded-xl bg-amber-50 border border-amber-200 px-3.5 py-2.5 text-[12px] leading-relaxed text-amber-900">
              <Info size={14} className="flex-shrink-0 mt-0.5 text-amber-600" />
              <span>
                <strong>Dữ liệu minh hoạ, không phải hồ sơ thật.</strong> Phần trong ngoặc vuông là chỗ điền.
                Bấm <strong>Sửa nội dung</strong> để thay bằng thông tin của ca, rồi bác sĩ xác nhận trước khi in.
              </span>
            </div>

            {/* Đầu tờ: cơ sở khám và số hồ sơ */}
            <div className="flex items-start justify-between gap-4 pb-4 border-b border-slate-200">
              <div className="flex items-start gap-3 min-w-0 flex-1">
                <div className="w-11 h-11 rounded-xl border border-dashed border-slate-300 text-[9.5px] text-slate-400 flex items-center justify-center flex-shrink-0">
                  Logo
                </div>
                <div className="min-w-0 flex-1 space-y-1.5">
                  <div className="text-[13px] font-bold text-slate-900">
                    <Truong gia={hoSo.coSo} goiY="Tên cơ sở khám bệnh" sua={sua} onDoi={truong("coSo")} />
                  </div>
                  <div className="text-[12px] text-slate-600">
                    <Truong gia={hoSo.khoa} goiY="Khoa / phòng khám" sua={sua} onDoi={truong("khoa")} />
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5 text-[11.5px] text-slate-500">
                    <Truong gia={hoSo.diaChi} goiY="Địa chỉ" sua={sua} onDoi={truong("diaChi")} />
                    <Truong gia={hoSo.hotline} goiY="Số hotline" sua={sua} onDoi={truong("hotline")} />
                  </div>
                </div>
              </div>

              <div className="w-48 sm:w-56 flex-shrink-0 space-y-1.5 text-[11.5px] text-slate-600">
                <div className="flex items-center gap-1.5">
                  <span className="flex-shrink-0">Mẫu:</span>
                  <div className="flex-1 min-w-0 text-right">
                    <Truong gia={hoSo.maMau} goiY="mã mẫu" sua={sua} onDoi={truong("maMau")} />
                  </div>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="flex-shrink-0">Số hồ sơ:</span>
                  <div className="flex-1 min-w-0 text-right">
                    <Truong gia={hoSo.soHoSo} goiY="số hồ sơ" sua={sua} onDoi={truong("soHoSo")} />
                  </div>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="flex-shrink-0">Ngày in:</span>
                  <div className="flex-1 min-w-0 text-right">
                    <Truong gia={hoSo.ngayIn} goiY="ngày in" sua={sua} onDoi={truong("ngayIn")} />
                  </div>
                </div>
              </div>
            </div>

            {/* Tiêu đề */}
            <div className="text-center">
              <h2 className="font-serif text-xl sm:text-2xl font-bold uppercase tracking-wider text-slate-950">
                Hướng dẫn dặn dò người bệnh khi về nhà
              </h2>
              <p className="text-[12px] text-slate-500 mt-1.5 flex flex-wrap items-center justify-center gap-x-1">
                <span>Kèm theo đơn thuốc ngoại trú số</span>
                <span className="inline-block min-w-[6rem]">
                  <Truong gia={hoSo.soDon} goiY="số đơn" sua={sua} onDoi={truong("soDon")} />
                </span>
                <span>· Xin đọc kỹ và mang theo khi tái khám</span>
              </p>
            </div>

            {/* Thông tin người bệnh */}
            <dl className="grid grid-cols-2 sm:grid-cols-4 gap-x-5 gap-y-3 rounded-2xl bg-[#F8FBFC] border border-[#E0F2FE] p-4 text-[12.5px]">
              <div>
                <dt className="text-[10.5px] font-semibold uppercase tracking-wider text-slate-500">Họ và tên</dt>
                <dd className="mt-0.5 font-bold text-slate-900 uppercase">{patientName}</dd>
              </div>
              <div>
                <dt className="text-[10.5px] font-semibold uppercase tracking-wider text-slate-500">Tuổi / giới</dt>
                <dd className="mt-0.5 text-slate-800">
                  <Truong gia={hoSo.tuoiGioi} goiY="tuổi / giới" sua={sua} onDoi={truong("tuoiGioi")} />
                </dd>
              </div>
              <div>
                <dt className="text-[10.5px] font-semibold uppercase tracking-wider text-slate-500">Mã BHYT</dt>
                <dd className="mt-0.5 text-slate-800">
                  <Truong gia={hoSo.maBhyt} goiY="mã BHYT" sua={sua} onDoi={truong("maBhyt")} />
                </dd>
              </div>
              <div>
                <dt className="text-[10.5px] font-semibold uppercase tracking-wider text-slate-500">Bác sĩ phụ trách</dt>
                <dd className="mt-0.5 font-semibold text-slate-800">
                  <Truong gia={hoSo.bacSi} goiY="tên bác sĩ điều trị" sua={sua} onDoi={truong("bacSi")} />
                </dd>
              </div>
              <div className="col-span-2 sm:col-span-4 pt-3 border-t border-[#E0F2FE]">
                <dt className="text-[10.5px] font-semibold uppercase tracking-wider text-slate-500">Chẩn đoán xuất viện</dt>
                <dd className="mt-0.5 text-slate-900 font-semibold">
                  <Truong gia={hoSo.chanDoan} goiY="chẩn đoán xuất viện" sua={sua} onDoi={truong("chanDoan")} nhieuDong />
                </dd>
              </div>
            </dl>

            {/* Mục 1: Lịch uống thuốc theo từng thuốc */}
            <section>
              <h3 className="flex items-center gap-2 font-serif text-base font-semibold text-[#0F172A]">
                <Clock size={15} className="text-[#0284C7]" />
                <span>1. Lịch uống thuốc hàng ngày</span>
              </h3>
              <p className="text-[11.5px] text-slate-500 mt-0.5 mb-3">Uống đúng giờ, không tự ý tăng giảm liều.</p>

              <div className="space-y-3">
                {hoSo.thuoc.map((t) =>
                  sua ? (
                    <div key={t.id} className="rounded-2xl border border-dashed border-amber-300 bg-white p-3 space-y-2.5">
                      <div className="flex items-start gap-2">
                        <input
                          value={t.ten}
                          placeholder="Tên thuốc, hàm lượng"
                          onChange={(e) => suaThuoc(t.id, { ten: e.target.value })}
                          className={`${LOP_O} flex-1 min-w-0`}
                        />
                        <input
                          value={t.nhan}
                          placeholder="Nhãn (VD: BẮT BUỘC)"
                          onChange={(e) => suaThuoc(t.id, { nhan: e.target.value })}
                          className={`${LOP_O} w-40 flex-shrink-0`}
                        />
                        <button
                          type="button"
                          onClick={() => xoaThuoc(t.id)}
                          title="Xoá thuốc này"
                          className="p-1.5 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 flex-shrink-0"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                      <input
                        value={t.loai}
                        placeholder="Nhóm thuốc, công dụng"
                        onChange={(e) => suaThuoc(t.id, { loai: e.target.value })}
                        className={`${LOP_O} w-full`}
                      />
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                        {BUOI_UONG.map((b) => (
                          <label key={b.khoa} className="space-y-1">
                            <span className="block text-[10.5px] font-semibold uppercase tracking-wider text-slate-500">{b.nhan}</span>
                            <input
                              value={t[b.khoa]}
                              placeholder="—"
                              onChange={(e) => suaThuoc(t.id, { [b.khoa]: e.target.value } as Partial<Thuoc>)}
                              className={`${LOP_O} w-full text-center`}
                            />
                          </label>
                        ))}
                      </div>
                      <textarea
                        rows={2}
                        value={t.loiDan}
                        placeholder="Lời dặn của bác sĩ"
                        onChange={(e) => suaThuoc(t.id, { loiDan: e.target.value })}
                        className={`${LOP_O} w-full resize-y`}
                      />
                    </div>
                  ) : (
                    <div key={t.id} className="rounded-2xl border border-[#E0F2FE] overflow-hidden">
                      <div className="flex items-start gap-3 px-4 py-3 bg-[#F8FBFC]">
                        <span className="w-6 h-6 rounded-lg bg-[#0284C7] text-white text-[11px] font-bold flex items-center justify-center flex-shrink-0">
                          {hoSo.thuoc.indexOf(t) + 1}
                        </span>
                        <div className="flex-1 min-w-0">
                          <div className="text-[13px] font-bold text-slate-900">
                            <ChuHoacCho text={t.ten} goiY="tên thuốc" />
                          </div>
                          <div className="text-[11.5px] text-slate-500">
                            <ChuHoacCho text={t.loai} goiY="nhóm thuốc" />
                          </div>
                        </div>
                        {t.nhan.trim() && (
                          <span className={`px-2 py-0.5 rounded-md text-[10.5px] font-bold border whitespace-nowrap flex-shrink-0 ${t.mau}`}>
                            {t.nhan}
                          </span>
                        )}
                      </div>

                      <div className="grid grid-cols-4 divide-x divide-[#E0F2FE] border-t border-[#E0F2FE]">
                        {BUOI_UONG.map((b) => (
                          <div key={b.khoa} className="px-2 py-2.5 text-center">
                            <div className="text-[10.5px] font-semibold uppercase tracking-wider text-slate-500">{b.nhan}</div>
                            <div className="mt-1.5 text-[12.5px] font-bold">
                              {t[b.khoa].trim() ? (
                                <span className={`inline-block whitespace-nowrap rounded-md px-2 py-0.5 ${b.mau}`}>
                                  <Chu text={t[b.khoa]} />
                                </span>
                              ) : (
                                <span className="text-slate-300">—</span>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>

                      {t.loiDan.trim() && (
                        <p className="px-4 py-2.5 text-[12px] leading-relaxed text-slate-700 border-t border-[#E0F2FE]">
                          <Chu text={t.loiDan} />
                        </p>
                      )}
                    </div>
                  ),
                )}
              </div>

              {sua && (
                <button
                  type="button"
                  onClick={themThuoc}
                  className="mt-3 inline-flex items-center gap-1.5 text-[12px] font-semibold text-[#0369A1] hover:text-[#0284C7]"
                >
                  <Plus size={14} />
                  <span>Thêm thuốc</span>
                </button>
              )}
            </section>

            {/* Mục 2: Ăn uống, vận động và theo dõi tại nhà */}
            <section className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="rounded-2xl border border-[#E0F2FE] bg-[#F8FBFC] p-4">
                <h4 className="flex items-center gap-2 font-serif text-[15px] font-semibold text-[#0F172A] mb-2.5">
                  <HeartPulse size={15} className="text-[#0D9488]" />
                  <span>Ăn uống & sinh hoạt</span>
                </h4>
                <DanhSachMuc
                  ds={hoSo.anUong}
                  sua={sua}
                  onDoi={(ds) => doi({ anUong: ds })}
                  coTieuDe
                  nhanThem="Thêm mục"
                />
              </div>

              <div className="rounded-2xl border border-[#E0F2FE] bg-[#F8FBFC] p-4">
                <h4 className="flex items-center gap-2 font-serif text-[15px] font-semibold text-[#0F172A] mb-2.5">
                  <Clock size={15} className="text-[#0284C7]" />
                  <span>Theo dõi huyết áp tại nhà</span>
                </h4>
                <DanhSachMuc
                  ds={hoSo.theoDoi}
                  sua={sua}
                  onDoi={(ds) => doi({ theoDoi: ds })}
                  coTieuDe
                  nhanThem="Thêm mục"
                />
              </div>
            </section>

            {/* Mục 3: Dấu hiệu cảnh báo nguy hiểm */}
            <section className="rounded-2xl border border-red-200 bg-red-50/70 p-4">
              <div className="flex items-center gap-2 text-[12.5px] font-bold text-red-900 uppercase tracking-wide mb-1.5">
                <AlertTriangle size={16} className="text-red-600 flex-shrink-0" />
                <span>Dấu hiệu nguy hiểm — đến ngay phòng cấp cứu gần nhất</span>
              </div>
              <p className="text-[12px] text-red-800 mb-3">
                Nếu có <strong>bất kỳ biểu hiện nào</strong> dưới đây, gọi cấp cứu 115 hoặc đưa người bệnh đến bệnh viện ngay:
              </p>
              <DanhSachMuc
                ds={hoSo.dauHieu}
                sua={sua}
                onDoi={(ds) => doi({ dauHieu: ds })}
                coTieuDe={false}
                dauDo
                nhanThem="Thêm dấu hiệu"
              />
            </section>

            {/* Mục 4: Tái khám, xác thực và ký tên */}
            <section className="pt-5 border-t-2 border-slate-900 grid grid-cols-1 sm:grid-cols-3 gap-5 text-[12px]">
              <div className="space-y-1.5">
                <div className="flex items-center gap-1.5 text-slate-900 font-bold text-[12px]">
                  <Calendar size={14} className="text-[#0284C7]" />
                  <span>Hẹn tái khám</span>
                </div>
                <p className="text-slate-700">
                  Ngày: <Truong gia={hoSo.ngayTaiKham} goiY="ngày tái khám" sua={sua} onDoi={truong("ngayTaiKham")} />
                </p>
                <p className="text-slate-700">
                  Địa điểm: <Truong gia={hoSo.diaDiemTaiKham} goiY="địa điểm tái khám" sua={sua} onDoi={truong("diaDiemTaiKham")} />
                </p>
                <p className="text-slate-500 text-[11.5px] leading-relaxed">
                  Nhớ nhịn ăn sáng để làm xét nghiệm sinh hoá máu, và mang theo đơn thuốc này.
                </p>
              </div>

              <div className="space-y-1.5 sm:border-l sm:border-[#E0F2FE] sm:pl-5">
                <div className="flex items-center gap-1.5 text-slate-900 font-bold text-[12px]">
                  <ShieldCheck size={14} className="text-[#0D9488]" />
                  <span>Mã QR & Xác thực MediTrace</span>
                </div>
                <div className="flex items-start gap-2.5 pt-0.5">
                  <svg
                    viewBox="0 0 21 21"
                    className="w-16 h-16 border border-slate-200 rounded-lg p-1 bg-white flex-shrink-0"
                    aria-label="Mã QR tóm tắt lịch uống thuốc"
                  >
                    {Array.from({ length: 21 * 21 }, (_, idx) => {
                      const r = Math.floor(idx / 21);
                      const c = idx % 21;
                      const inFinder =
                        (r < 7 && c < 7) || (r < 7 && c >= 14) || (r >= 14 && c < 7);
                      let on = false;
                      if (inFinder) {
                        const lr = r >= 14 ? r - 14 : r;
                        const lc = c >= 14 ? c - 14 : c;
                        on =
                          lr === 0 || lr === 6 || lc === 0 || lc === 6 ||
                          (lr >= 2 && lr <= 4 && lc >= 2 && lc <= 4);
                      } else {
                        const seedStr = `${hoSo.chanDoan}|${hoSo.thuoc.map((t) => `${t.ten}:${t.sang}-${t.trua}-${t.chieu}-${t.toi}`).join(";")}`;
                        let h = (r * 31 + c * 17) ^ seedStr.length;
                        for (let i = 0; i < seedStr.length; i++) {
                          h = (h * 33 + seedStr.charCodeAt(i) + idx) & 0xffff;
                        }
                        on = h % 2 === 0;
                      }
                      return on ? <rect key={idx} x={c} y={r} width={1} height={1} fill="#0F172A" /> : null;
                    })}
                  </svg>
                  <div className="space-y-1 min-w-0">
                    <p className="text-slate-500 text-[11px] leading-snug">
                      Quét QR lưu lịch uống thuốc 4 buổi & dấu hiệu đỏ cấp cứu.
                    </p>
                    <button
                      type="button"
                      onClick={() => {
                        const tomTat = [
                          `📋 TỜ DẶN DÒ NGƯỜI BỆNH — ${hoSo.chanDoan}`,
                          ...hoSo.thuoc.map(
                            (t, i) =>
                              `${i + 1}. ${t.ten}: Sáng ${t.sang} | Trưa ${t.trua} | Chiều ${t.chieu} | Tối ${t.toi} (${t.loiDan})`
                          ),
                          `⚠️ Cấp cứu ngay nếu: ${hoSo.dauHieu.map((d) => d.noiDung).join("; ")}`,
                        ].join("\n");
                        void navigator.clipboard?.writeText(tomTat);
                      }}
                      className="print:hidden inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-sky-50 hover:bg-sky-100 text-[#0369A1] border border-sky-200 text-[10.5px] font-semibold cursor-pointer"
                    >
                      Sao chép gửi Zalo
                    </button>
                  </div>
                </div>
              </div>

              <div className="space-y-1.5 text-left sm:text-right sm:border-l sm:border-[#E0F2FE] sm:pl-5">
                <p className="text-slate-600">
                  Hà Nội, <Truong gia={hoSo.ngayKy} goiY="ngày tháng năm" sua={sua} onDoi={truong("ngayKy")} />
                </p>
                <p className="font-bold text-slate-900 uppercase text-[12px]">Bác sĩ điều trị</p>
                <div className="h-12 flex items-center sm:justify-end">
                  <Cho>chữ ký bác sĩ</Cho>
                </div>
                <p className="font-bold text-slate-900">
                  <Truong gia={hoSo.bacSi} goiY="tên bác sĩ" sua={sua} onDoi={truong("bacSi")} />
                </p>
                <p className="text-[11.5px] text-slate-500">
                  CCHN: <Truong gia={hoSo.cchn} goiY="số chứng chỉ hành nghề" sua={sua} onDoi={truong("cchn")} />
                </p>
              </div>
            </section>
          </div>
        </div>

        {/* Chân cửa sổ (không in) */}
        <div className="px-4 sm:px-5 py-3 bg-[#F8FBFC] border-t border-slate-100 flex flex-wrap items-center justify-between gap-3 flex-shrink-0 print:hidden">
          <span className="text-slate-600 text-[11.5px]">
            {sua
              ? "Đang sửa. Bấm Xong sửa trước khi in. Nội dung sửa được giữ cho đến khi tải lại trang."
              : "Minh hoạ giao diện, chưa gắn với hồ sơ thật. Bác sĩ xác nhận nội dung trước khi in và trao tay người bệnh."}
          </span>
          <div className="flex items-center gap-2 flex-shrink-0">
            {sua && (
              <button
                type="button"
                onClick={khoiPhuc}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-200 transition-colors"
              >
                <RotateCcw size={13} />
                <span>Khôi phục mẫu</span>
              </button>
            )}
            <button
              onClick={dong}
              className="px-4 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-semibold transition-colors cursor-pointer"
            >
              Đóng cửa sổ
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
