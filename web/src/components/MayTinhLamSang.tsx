import React, { useState } from "react";
import {
  bmi, bsaMosteller, creatininMgDl, crclCockcroftGault, egfrCkdEpi2021, giaiDoanEgfr,
  huyetApTrungBinh, lieuTheoCanNang, phanLoaiBmiChauA,
} from "../lib/mayTinh";

/**
 * Máy tính lâm sàng. Số do công thức trong src/lib/mayTinh.ts tính (có phép kiểm), không qua AI.
 * Ô trống hoặc sai thì không hiện kết quả — không đoán giá trị thay bác sĩ.
 */
type Loai = "egfr" | "crcl" | "bmi" | "lieu" | "map";

const DS: Array<{ id: Loai; ten: string; mo: string }> = [
  { id: "egfr", ten: "eGFR (CKD-EPI 2021)", mo: "Mức lọc cầu thận ước tính" },
  { id: "crcl", ten: "Độ thanh thải creatinin", mo: "Cockcroft–Gault, dùng chỉnh liều thuốc" },
  { id: "lieu", ten: "Liều theo cân nặng", mo: "mg/kg/ngày chia số lần" },
  { id: "bmi", ten: "BMI và diện tích da", mo: "Ngưỡng châu Á; BSA Mosteller" },
  { id: "map", ten: "Huyết áp trung bình", mo: "MAP từ tâm thu, tâm trương" },
];

const so = (v: string) => {
  const n = Number(String(v).replace(",", "."));
  return v.trim() !== "" && Number.isFinite(n) && n > 0 ? n : null;
};
const lam = (n: number, k = 1) => n.toLocaleString("vi-VN", { maximumFractionDigits: k, minimumFractionDigits: k });

const O: React.FC<{ nhan: string; donVi?: string; v: string; set: (v: string) => void }> = ({ nhan, donVi, v, set }) => (
  <label className="flex flex-col gap-1 text-[12px] text-[#334155]">
    {nhan}
    <span className="flex items-center rounded-xl border border-[#CCE3F0] bg-white focus-within:border-[#0284C7]">
      <input
        inputMode="decimal"
        value={v}
        onChange={(e) => set(e.target.value)}
        className="flex-1 min-w-0 px-3 py-2 bg-transparent text-[14px] tabular-nums focus:outline-none"
      />
      {donVi && <span className="pr-3 text-[11.5px] text-[#64748B]">{donVi}</span>}
    </span>
  </label>
);

const Gioi: React.FC<{ nu: boolean; set: (v: boolean) => void }> = ({ nu, set }) => (
  <div className="flex flex-col gap-1 text-[12px] text-[#334155]">
    Giới
    <div className="grid grid-cols-2 gap-1 p-0.5 rounded-xl bg-[#E0F2FE] border border-[#BAE6FD]">
      {[false, true].map((g) => (
        <button
          key={String(g)}
          type="button"
          onClick={() => set(g)}
          className={`py-1.5 rounded-lg text-[12px] font-semibold ${nu === g ? "bg-white text-[#0369A1] shadow-sm" : "text-[#0C4A6E]/70"}`}
        >
          {g ? "Nữ" : "Nam"}
        </button>
      ))}
    </div>
  </div>
);

const KetQua: React.FC<{ chinh: string | null; phu?: string; nguon: string }> = ({ chinh, phu, nguon }) => (
  <div className="rounded-2xl bg-[#F0F9FF] border border-[#BAE6FD] p-4">
    {chinh ? (
      <>
        <div className="text-[26px] font-semibold text-[#0C4A6E] tabular-nums leading-tight">{chinh}</div>
        {phu && <div className="text-[12.5px] text-[#0369A1] mt-1">{phu}</div>}
      </>
    ) : (
      <div className="text-[12.5px] text-[#64748B]">Điền đủ các ô để tính.</div>
    )}
    <div className="text-[10.5px] text-[#64748B] mt-3 leading-snug">{nguon} Chỉ để tham khảo — bác sĩ quyết định.</div>
  </div>
);

export const MayTinhLamSang: React.FC = () => {
  const [loai, setLoai] = useState<Loai>("egfr");
  const [scr, setScr] = useState("");
  const [donViScr, setDonViScr] = useState<"umol" | "mg">("umol");
  const [tuoi, setTuoi] = useState("");
  const [nu, setNu] = useState(false);
  const [can, setCan] = useState("");
  const [cao, setCao] = useState("");
  const [mgKg, setMgKg] = useState("");
  const [soLan, setSoLan] = useState("");
  const [tran, setTran] = useState("");
  const [tamThu, setTamThu] = useState("");
  const [tamTruong, setTamTruong] = useState("");

  const scrMg = so(scr) ? (donViScr === "umol" ? creatininMgDl(so(scr)!) : so(scr)!) : null;

  const oScr = (
    <div className="flex flex-col gap-1">
      <O nhan="Creatinin huyết thanh" v={scr} set={setScr} />
      <div className="flex gap-1">
        {(["umol", "mg"] as const).map((d) => (
          <button
            key={d}
            type="button"
            onClick={() => setDonViScr(d)}
            className={`px-2 py-0.5 rounded-md text-[11px] border ${donViScr === d ? "bg-[#0284C7] text-white border-[#0284C7]" : "border-[#CCE3F0] text-[#0C4A6E]"}`}
          >
            {d === "umol" ? "µmol/L" : "mg/dL"}
          </button>
        ))}
      </div>
    </div>
  );

  let noiDung: React.ReactNode = null;
  if (loai === "egfr") {
    const g = scrMg && so(tuoi) ? egfrCkdEpi2021(scrMg, so(tuoi)!, nu) : null;
    noiDung = (
      <>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">{oScr}<O nhan="Tuổi" donVi="năm" v={tuoi} set={setTuoi} /><Gioi nu={nu} set={setNu} /></div>
        <KetQua
          chinh={g ? `${lam(g, 0)} mL/phút/1,73 m²` : null}
          phu={g ? `KDIGO ${giaiDoanEgfr(g)}` : undefined}
          nguon="Công thức CKD-EPI 2021 không hệ số chủng tộc (Inker và cs., NEJM 2021). Phân giai đoạn theo KDIGO 2012."
        />
      </>
    );
  } else if (loai === "crcl") {
    const c = scrMg && so(tuoi) && so(can) ? crclCockcroftGault(scrMg, so(tuoi)!, so(can)!, nu) : null;
    noiDung = (
      <>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">{oScr}<O nhan="Tuổi" donVi="năm" v={tuoi} set={setTuoi} /><O nhan="Cân nặng" donVi="kg" v={can} set={setCan} /><Gioi nu={nu} set={setNu} /></div>
        <KetQua chinh={c ? `${lam(c, 0)} mL/phút` : null} nguon="Cockcroft–Gault (1976), dùng cân nặng thực tế." />
      </>
    );
  } else if (loai === "lieu") {
    const l = so(mgKg) && so(can) && so(soLan) ? lieuTheoCanNang(so(mgKg)!, so(can)!, Math.round(so(soLan)!), so(tran) || undefined) : null;
    noiDung = (
      <>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <O nhan="Liều" donVi="mg/kg/ngày" v={mgKg} set={setMgKg} />
          <O nhan="Cân nặng" donVi="kg" v={can} set={setCan} />
          <O nhan="Chia" donVi="lần/ngày" v={soLan} set={setSoLan} />
          <O nhan="Liều tối đa (không bắt buộc)" donVi="mg/ngày" v={tran} set={setTran} />
        </div>
        <KetQua
          chinh={l ? `${lam(l.mgLan)} mg/lần` : null}
          phu={l ? `${lam(l.mgNgay)} mg/ngày${l.chamTran ? ` — đã chạm liều tối đa (công thức ra ${lam(l.mgNgayTheoCongThuc)} mg/ngày)` : ""}` : undefined}
          nguon="Tổng liều/ngày = mg/kg/ngày × cân nặng, chia đều số lần. Liều mg/kg lấy từ tài liệu thuốc, máy không tự điền."
        />
      </>
    );
  } else if (loai === "bmi") {
    const b = so(can) && so(cao) ? bmi(so(can)!, so(cao)!) : null;
    noiDung = (
      <>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3"><O nhan="Cân nặng" donVi="kg" v={can} set={setCan} /><O nhan="Chiều cao" donVi="cm" v={cao} set={setCao} /></div>
        <KetQua
          chinh={b ? `BMI ${lam(b)} kg/m²` : null}
          phu={b ? `${phanLoaiBmiChauA(b)} · Diện tích da ${lam(bsaMosteller(so(can)!, so(cao)!), 2)} m²` : undefined}
          nguon="Ngưỡng BMI người trưởng thành châu Á (WHO Tây Thái Bình Dương 2000). BSA theo Mosteller (1987)."
        />
      </>
    );
  } else {
    const m = so(tamThu) && so(tamTruong) ? huyetApTrungBinh(so(tamThu)!, so(tamTruong)!) : null;
    noiDung = (
      <>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3"><O nhan="Tâm thu" donVi="mmHg" v={tamThu} set={setTamThu} /><O nhan="Tâm trương" donVi="mmHg" v={tamTruong} set={setTamTruong} /></div>
        <KetQua chinh={m ? `${lam(m, 0)} mmHg` : null} nguon="MAP = (tâm thu + 2 × tâm trương) / 3." />
      </>
    );
  }

  return (
    <div className="w-full max-w-3xl mx-auto flex flex-col gap-5 text-left">
      <header>
        <h2 className="font-serif text-2xl font-semibold text-[#0F172A]">Máy tính lâm sàng</h2>
        <p className="text-[12.5px] text-[#475569] mt-1">Tính bằng công thức, không qua AI. Mỗi kết quả ghi nguồn công thức.</p>
      </header>
      <div className="flex gap-1.5 overflow-x-auto no-scrollbar pb-1">
        {DS.map((d) => (
          <button
            key={d.id}
            onClick={() => setLoai(d.id)}
            className={`flex-shrink-0 text-left px-3 py-2 rounded-xl border transition-colors ${
              loai === d.id ? "bg-white border-[#0284C7] shadow-tactile-doctor-pill" : "bg-white/60 border-[#CCE3F0] hover:border-[#BAE6FD]"
            }`}
          >
            <span className="block text-[12.5px] font-semibold text-[#0F172A]">{d.ten}</span>
            <span className="block text-[10.5px] text-[#64748B]">{d.mo}</span>
          </button>
        ))}
      </div>
      <div className="bg-white rounded-2xl border border-[#BAE6FD] p-4 flex flex-col gap-4 shadow-tactile-doctor-card">{noiDung}</div>
    </div>
  );
};
