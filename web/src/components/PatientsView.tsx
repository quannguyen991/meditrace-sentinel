import React, { useEffect, useMemo, useState } from "react";
import { BangDuLieuMinhHoa } from "./BangDuLieuMinhHoa";
import { Patient, Session } from "../types";
import { samplePatients } from "../data/mockData";
import { useKho } from "../lib/useKho";
import { lyDoKham } from "../lib/mauVanBan";
import { trichNguCanhChoTroLy } from "../lib/nguCanhTroLy";
import { laDinhDanhBenhNhanThat, taoDaiTomTatTruocKham } from "../lib/trichNhiemVuVaTomTat";
import {
  Activity,
  AlertTriangle,
  Pill,
  Plus,
  Search,
  SlidersHorizontal,
  TrendingUp,
  Upload,
  Users,
  X,
} from "lucide-react";

export interface DiemXuHuongKham {
  ngay: string;
  huyetApTamThu?: number;
  huyetApTamTruong?: number;
  nhipTim?: number;
  hba1c?: number;
  egfr?: number;
}

const XU_HUONG_MINH_HOA: DiemXuHuongKham[] = [
  { ngay: "Lần 1 (08/2026)", huyetApTamThu: 152, huyetApTamTruong: 94, nhipTim: 84, hba1c: 8.1, egfr: 68 },
  { ngay: "Lần 2 (09/2026)", huyetApTamThu: 144, huyetApTamTruong: 88, nhipTim: 78, hba1c: 7.6, egfr: 66 },
  { ngay: "Lần 3 (10/2026)", huyetApTamThu: 136, huyetApTamTruong: 84, nhipTim: 74, hba1c: 7.2, egfr: 65 },
  { ngay: "Lần 4 (11/2026)", huyetApTamThu: 128, huyetApTamTruong: 80, nhipTim: 72, hba1c: 6.8, egfr: 67 },
];

function trichXuHuongTuPhien(sessions: Session[], patientName: string): { diem: DiemXuHuongKham[]; laMinhHoa: boolean } {
  const khop = sessions
    .filter((s) => s.patientIdentifier?.trim().toLowerCase() === patientName.trim().toLowerCase())
    .slice(0, 6)
    .reverse();

  const diem: DiemXuHuongKham[] = [];
  for (const s of khop) {
    const gop = [
      s.transcript || "",
      s.contextNotes || "",
      ...(s.tabs || []).map((t) => t.content || ""),
    ].join("\n");
    const ha = gop.match(/huyết\s*áp\s*[:=]?\s*(\d{2,3})\s*\/\s*(\d{2,3})/i);
    const mach = gop.match(/(?:mạch|nhịp\s*tim)\s*[:=]?\s*(\d{2,3})/i);
    const hba1c = gop.match(/hba1c\s*[:=]?\s*(\d+(?:[.,]\d+)?)/i);
    const egfr = gop.match(/(?:egfr|mlct)\s*[:=]?\s*(\d+(?:[.,]\d+)?)/i);
    if (ha || mach || hba1c || egfr) {
      diem.push({
        ngay: s.date || s.time || "Lần khám",
        ...(ha ? { huyetApTamThu: Number(ha[1]), huyetApTamTruong: Number(ha[2]) } : {}),
        ...(mach ? { nhipTim: Number(mach[1]) } : {}),
        ...(hba1c ? { hba1c: Number(hba1c[1].replace(",", ".")) } : {}),
        ...(egfr ? { egfr: Number(egfr[1].replace(",", ".")) } : {}),
      });
    }
  }
  if (diem.length >= 1) return { diem, laMinhHoa: false };
  return { diem: XU_HUONG_MINH_HOA, laMinhHoa: true };
}

function taoChuoiToaDoSVG(values: Array<number | undefined>, width: number, height: number, pad = 16): string {
  const valid = values.filter((v): v is number => typeof v === "number" && !Number.isNaN(v));
  if (valid.length < 2) return "";
  const min = Math.min(...valid);
  const max = Math.max(...valid);
  const span = max - min || 1;
  const pts: string[] = [];
  values.forEach((v, i) => {
    if (typeof v !== "number" || Number.isNaN(v)) return;
    const x = pad + (i / Math.max(1, values.length - 1)) * (width - pad * 2);
    const y = height - pad - ((v - min) / span) * (height - pad * 2);
    pts.push(`${x.toFixed(1)},${y.toFixed(1)}`);
  });
  return pts.join(" ");
}

interface BenhNhanHopNhat extends Patient {
  soLanKham?: number;
  tuCaThuc?: boolean;
}

interface PatientsViewProps {
  sessions?: Session[];
  onStartSessionWithPatient?: (patient: Patient) => void;
}

export const PatientsView: React.FC<PatientsViewProps> = ({
  sessions = [],
  onStartSessionWithPatient,
}) => {
  const [storedPatients, setStoredPatients] = useKho<Patient>("benh-nhan", samplePatients);
  const [selectedPatientId, setSelectedPatientId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [showAddModal, setShowAddModal] = useState(false);

  // Tự động tổng hợp bệnh nhân thật từ `sessions` và hợp nhất với danh bạ lưu SQLite (`useKho`)
  const { mergedPatients, coBenhNhanThatTuSessions } = useMemo(() => {
    const gomTheoTen = new Map<string, Session[]>();
    for (const s of sessions || []) {
      if (!laDinhDanhBenhNhanThat(s.patientIdentifier)) continue;
      const key = s.patientIdentifier.trim().toLowerCase();
      const hienCo = gomTheoTen.get(key) || [];
      hienCo.push(s);
      gomTheoTen.set(key, hienCo);
    }

    const daXet = new Set<string>();
    const tuSessions: BenhNhanHopNhat[] = [];

    for (const [key, dsCa] of gomTheoTen.entries()) {
      daXet.add(key);
      const caMoiNhat = dsCa[0];
      const cuTrongKho = storedPatients.find((p) => p.name.trim().toLowerCase() === key);
      const lyDo = lyDoKham(caMoiNhat, caMoiNhat.note) || cuTrongKho?.chiefComplaint || caMoiNhat.patientSubtitle || "Khám lâm sàng";
      const contextText = caMoiNhat.tabs?.find((t) => t.type === "context")?.content || caMoiNhat.contextNotes || "";
      const nc = trichNguCanhChoTroLy({
        patient: cuTrongKho,
        patientSubtitle: caMoiNhat.patientSubtitle,
        contextNotes: contextText,
      });

      const lanKhamCuoi = [caMoiNhat.date, caMoiNhat.time].filter(Boolean).join(" ").trim() || cuTrongKho?.lastConsultation || "Hôm nay";

      tuSessions.push({
        id: cuTrongKho?.id || `pat-sess-${caMoiNhat.id}`,
        name: cuTrongKho?.name || caMoiNhat.patientIdentifier.trim(),
        identifier: lyDo,
        dob:
          cuTrongKho?.dob ||
          (nc.tuoi !== undefined ? `${nc.tuoi} tuổi` : "Chưa ghi ngày sinh"),
        gender: cuTrongKho?.gender || (nc.gioi === "nữ" ? "Nữ" : nc.gioi === "nam" ? "Nam" : undefined),
        phone: cuTrongKho?.phone || "Lưu từ ca khám",
        lastConsultation: lanKhamCuoi,
        chiefComplaint: lyDo,
        soLanKham: dsCa.length,
        tuCaThuc: true,
      });
    }

    const conLaiTrongKho: BenhNhanHopNhat[] = storedPatients
      .filter((p) => !daXet.has(p.name.trim().toLowerCase()))
      .map((p) => ({ ...p }));

    return {
      mergedPatients: [...tuSessions, ...conLaiTrongKho],
      coBenhNhanThatTuSessions: tuSessions.length > 0,
    };
  }, [sessions, storedPatients]);

  const selectedPatient = useMemo(
    () =>
      mergedPatients.find((p) => p.id === selectedPatientId) ||
      mergedPatients[0] ||
      null,
    [mergedPatients, selectedPatientId]
  );

  useEffect(() => {
    if (!selectedPatientId && mergedPatients[0]) {
      setSelectedPatientId(mergedPatients[0].id);
    }
  }, [mergedPatients, selectedPatientId]);

  const xuHuong = useMemo(
    () => (selectedPatient ? trichXuHuongTuPhien(sessions, selectedPatient.name) : null),
    [selectedPatient, sessions],
  );

  const daiTomTat = useMemo(() => {
    if (!selectedPatient) return null;
    const phienAo: Session = {
      id: "__tong_hop_patients_view__",
      patientIdentifier: selectedPatient.name,
      patientSubtitle: "",
      date: "",
      time: "",
      language: "Tiếng Việt",
      durationSeconds: 0,
      isRecording: false,
      transcript: "",
      activeTabId: "",
      tabs: [],
    };
    return taoDaiTomTatTruocKham(phienAo, sessions);
  }, [selectedPatient, sessions]);

  // Form thêm bệnh nhân
  const [newName, setNewName] = useState("");
  const [newIdentifier, setNewIdentifier] = useState("");
  const [newDob, setNewDob] = useState("");
  const [newPhone, setNewPhone] = useState("");
  const [newComplaint, setNewComplaint] = useState("");

  const filteredPatients = mergedPatients.filter(
    (p) =>
      p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.identifier.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (p.chiefComplaint || "").toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleAddPatient = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName.trim()) return;

    const created: Patient = {
      id: `pat-${Date.now()}`,
      name: newName.trim(),
      identifier: newIdentifier.trim() || newComplaint.trim() || "Khám nội khoa tổng quát",
      dob: newDob.trim() || "Chưa xác định",
      phone: newPhone.trim() || "Chưa xác định",
      lastConsultation: "Hôm nay",
      chiefComplaint: newComplaint.trim() || "Khám nội khoa tổng quát",
    };

    setStoredPatients((prev) => [created, ...prev]);
    setSelectedPatientId(created.id);
    setShowAddModal(false);
    setNewName("");
    setNewIdentifier("");
    setNewDob("");
    setNewPhone("");
    setNewComplaint("");
  };

  return (
    <div id="patients-view" className="flex-1 flex flex-col h-full bg-gradient-to-b from-[#F0F7FA] via-[#F8FBFC] to-[#EEF6FB] select-none overflow-y-auto">
      {!coBenhNhanThatTuSessions && <BangDuLieuMinhHoa />}
      {/* Header */}
      <div className="p-6 border-b border-[#CCE3F0] flex items-center justify-between bg-white/90 backdrop-blur-xs shadow-[0_1px_3px_rgba(2,132,199,0.04)]">
        <div>
          <h1 className="font-serif text-2xl font-bold text-[#0F172A] tracking-tight">
            Quản lý Bệnh nhân &amp; Hồ sơ Dọc
          </h1>
          <div className="flex items-center gap-2 mt-2">
            <span className="text-xs px-2.5 py-1 rounded-full bg-[#E0F2FE] text-[#0369A1] border border-[#BAE6FD] font-semibold shadow-tactile-doctor-pill">
              Tất cả bệnh nhân ({mergedPatients.length})
            </span>
            {coBenhNhanThatTuSessions && (
              <span className="text-xs px-2.5 py-1 rounded-full bg-[#ECFDF5] text-[#065F46] border border-[#A7F3D0] font-semibold">
                Đồng bộ tự động từ ca khám &amp; SQLite
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => alert("Chức năng nhập danh sách bệnh nhân từ file CSV hoặc hệ thống HIS/EHR")}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-[#BAE6FD] bg-white text-xs font-semibold text-[#0C4A6E] hover:bg-[#E0F9FF] transition-colors shadow-tactile-doctor-pill"
          >
            <Upload size={14} className="text-[#0284C7]" />
            <span>Nhập tệp</span>
          </button>
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#0284C7] text-white text-xs font-semibold hover:bg-[#0369A1] transition-all shadow-tactile-doctor active:translate-y-0.5"
          >
            <Plus size={14} className="stroke-[2.5]" />
            <span>Thêm bệnh nhân</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="px-6 py-3 border-b border-[#CCE3F0] bg-[#F0F7FA]/70 flex items-center justify-between gap-4">
        <div className="flex-1 max-w-md relative">
          <Search size={14} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-[#0284C7]" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Tìm kiếm bệnh nhân theo tên, mã bệnh án hoặc triệu chứng..."
            className="w-full pl-9 pr-3.5 py-2 rounded-xl border border-[#BAE6FD] bg-white text-xs text-[#0F172A] focus:outline-none focus:border-[#0284C7] focus:ring-2 focus:ring-[#BAE6FD]/50 shadow-tactile-inset"
          />
        </div>

        <button className="p-2 rounded-xl border border-[#BAE6FD] bg-white text-[#0284C7] hover:bg-[#E0F2FE] transition-colors shadow-tactile-doctor-pill">
          <SlidersHorizontal size={14} />
        </button>
      </div>

      {/* Bảng Danh sách Bệnh nhân */}
      <div className="flex-1 p-6">
        {filteredPatients.length === 0 ? (
          <div className="flex flex-col items-center justify-center p-12 text-center max-w-sm mx-auto">
            <div className="w-16 h-16 rounded-full bg-[#E0F2FE] border border-[#BAE6FD] flex items-center justify-center text-[#0284C7] mb-4 shadow-tactile-doctor-pill">
              <Users size={28} />
            </div>
            <h3 className="text-sm font-bold text-[#0F172A] mb-1">Chưa có hồ sơ bệnh nhân</h3>
            <p className="text-xs text-[#64748B] leading-relaxed mb-4">
              Tạo hồ sơ bệnh nhân mới bằng nút bên dưới hoặc tự động lưu trong quá trình ghi chép ca khám.
            </p>
            <button
              onClick={() => setShowAddModal(true)}
              className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#0284C7] text-white text-xs font-semibold hover:bg-[#0369A1] transition-all shadow-tactile-doctor active:translate-y-0.5"
            >
              <Plus size={14} className="stroke-[2.5]" />
              <span>Thêm bệnh nhân</span>
            </button>
          </div>
        ) : (
          <div className="bg-white rounded-2xl border border-[#BAE6FD] overflow-hidden shadow-tactile-doctor-card">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-[#CCE3F0] bg-[#F0F7FA]/80 text-[11px] font-bold text-[#64748B] uppercase tracking-wider">
                  <th className="py-3 px-4">Bệnh nhân</th>
                  <th className="py-3 px-4">Định danh / Lý do khám</th>
                  <th className="py-3 px-4">Ngày sinh / Tuổi</th>
                  <th className="py-3 px-4">Lần khám gần nhất</th>
                  <th className="py-3 px-4 text-right">Thao tác</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E0F2FE] text-xs text-[#0F172A]">
                {filteredPatients.map((patient) => (
                  <tr key={patient.id} className="hover:bg-[#F0F9FF] transition-colors">
                    <td className="py-3.5 px-4">
                      <div className="flex items-center gap-2.5">
                        <div className="w-8 h-8 rounded-full bg-[#E0F2FE] border border-[#BAE6FD] flex items-center justify-center text-[#0284C7] font-bold text-xs shadow-tactile-doctor-pill">
                          {patient.name.charAt(0)}
                        </div>
                        <div>
                          <div className="font-bold text-[#0F172A] flex items-center gap-1.5">
                            <span>{patient.name}</span>
                            {patient.soLanKham !== undefined && patient.soLanKham > 0 && (
                              <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-[#ECFDF5] text-[#065F46] border border-[#A7F3D0] font-semibold">
                                {patient.soLanKham} ca khám
                              </span>
                            )}
                          </div>
                          <div className="text-[11px] text-[#64748B]">{patient.phone}</div>
                        </div>
                      </div>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="px-2.5 py-0.5 rounded-full bg-[#E0F2FE] border border-[#BAE6FD] text-[11px] text-[#0369A1] font-semibold">
                        {patient.identifier}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-[#64748B]">{patient.dob}</td>
                    <td className="py-3.5 px-4 text-[#64748B]">{patient.lastConsultation}</td>
                    <td className="py-3.5 px-4 text-right">
                      <div className="inline-flex items-center gap-1.5">
                        <button
                          type="button"
                          onClick={() => setSelectedPatientId(patient.id)}
                          className={`px-2.5 py-1.5 rounded-xl border text-xs font-semibold transition-colors ${
                            selectedPatient?.id === patient.id
                              ? "border-[#0284C7] bg-[#E0F2FE] text-[#0369A1]"
                              : "border-[#BAE6FD] bg-white text-[#0C4A6E] hover:bg-[#F0F9FF]"
                          }`}
                        >
                          Xu hướng XN
                        </button>
                        {onStartSessionWithPatient && (
                          <button
                            onClick={() => onStartSessionWithPatient(patient)}
                            className="px-3 py-1.5 rounded-xl bg-[#0284C7] text-white text-xs font-semibold hover:bg-[#0369A1] transition-all shadow-tactile-doctor active:translate-y-0.5"
                          >
                            Khám bệnh (Scribe)
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Dải Tóm tắt Dọc Trước khám & Biểu đồ xu hướng Sinh hiệu / Xét nghiệm */}
        {selectedPatient && xuHuong && (
          <div className="mt-6 bg-white rounded-2xl border border-[#BAE6FD] p-5 shadow-tactile-doctor-card space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-[#CCE3F0]">
              <div className="flex items-center gap-2">
                <TrendingUp size={16} className="text-[#0284C7]" />
                <h3 className="font-serif text-base font-bold text-[#0F172A]">
                  Hồ sơ Dọc &amp; Xu hướng Xét nghiệm — {selectedPatient.name}
                </h3>
              </div>
              <span className="text-[11px] px-2.5 py-0.5 rounded-full bg-[#E0F2FE] border border-[#BAE6FD] text-[#0369A1] font-semibold">
                {xuHuong.laMinhHoa ? "Dữ liệu minh họa xuyên lần khám" : `${xuHuong.diem.length} mốc chỉ số thực tế`}
              </span>
            </div>

            {daiTomTat?.coDuLieuCu && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                <div className="rounded-xl border border-red-200 bg-red-50/70 p-3">
                  <div className="font-bold text-red-800 flex items-center gap-1.5 mb-1">
                    <AlertTriangle size={13} /> Dị ứng đã xác nhận
                  </div>
                  <div className="text-red-900">
                    {daiTomTat.diUngDaXacNhan.length > 0
                      ? daiTomTat.diUngDaXacNhan.join("; ")
                      : "Chưa ghi nhận dị ứng thuốc ở các lần trước"}
                  </div>
                </div>
                <div className="rounded-xl border border-[#BAE6FD] bg-[#F0F9FF] p-3">
                  <div className="font-bold text-[#0369A1] flex items-center gap-1.5 mb-1">
                    <Pill size={13} /> Thuốc mạn tính / Đơn trước
                  </div>
                  <div className="text-[#0F172A]">
                    {daiTomTat.thuocManTinh.length > 0
                      ? daiTomTat.thuocManTinh.join("; ")
                      : "Chưa ghi nhận thuốc mạn tính"}
                  </div>
                </div>
                <div className="rounded-xl border border-[#BCE3DB] bg-[#ECFDF5]/70 p-3">
                  <div className="font-bold text-[#065F46] mb-1">Biến thiên &amp; Việc hẹn tồn đọng</div>
                  <div className="text-[#0F172A] space-y-1">
                    {daiTomTat.bienThienSinhHieuXn.length > 0 && (
                      <div>{daiTomTat.bienThienSinhHieuXn.join(" · ")}</div>
                    )}
                    {daiTomTat.viecHenTonDong.length > 0 && (
                      <div className="text-[11px] text-[#065F46]">
                        Hẹn: {daiTomTat.viecHenTonDong.join("; ")}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Huyết áp & Nhịp tim */}
              <div className="rounded-xl border border-[#E0F2FE] bg-[#F8FBFC] p-3.5">
                <div className="flex items-center justify-between text-xs font-semibold text-[#0C4A6E] mb-2">
                  <span className="flex items-center gap-1.5"><Activity size={13} className="text-[#0284C7]" /> Huyết áp (mmHg) &amp; Mạch</span>
                  <span className="text-[11px] text-[#64748B]">Tâm thu / Tâm trương</span>
                </div>
                <svg viewBox="0 0 280 96" className="w-full h-24 overflow-visible">
                  <polyline
                    fill="none"
                    stroke="#0284C7"
                    strokeWidth="2.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    points={taoChuoiToaDoSVG(xuHuong.diem.map((d) => d.huyetApTamThu), 280, 96)}
                  />
                  <polyline
                    fill="none"
                    stroke="#38BDF8"
                    strokeWidth="2"
                    strokeDasharray="4 3"
                    points={taoChuoiToaDoSVG(xuHuong.diem.map((d) => d.huyetApTamTruong), 280, 96)}
                  />
                </svg>
                <div className="flex items-center justify-between text-[11px] text-[#475569] mt-1">
                  {xuHuong.diem.map((d, idx) => (
                    <span key={idx} className="text-center">
                      <strong className="text-[#0F172A]">{d.huyetApTamThu ?? "—"}/{d.huyetApTamTruong ?? "—"}</strong>
                      <span className="block text-[10px] text-[#64748B]">{d.ngay.split(" ")[0]}</span>
                    </span>
                  ))}
                </div>
              </div>

              {/* HbA1c & eGFR */}
              <div className="rounded-xl border border-[#E0F2FE] bg-[#F8FBFC] p-3.5">
                <div className="flex items-center justify-between text-xs font-semibold text-[#0C4A6E] mb-2">
                  <span>HbA1c (%) &amp; eGFR (mL/phút)</span>
                  <span className="text-[11px] text-[#64748B]">Chỉ số chuyển hóa &amp; thận</span>
                </div>
                <svg viewBox="0 0 280 96" className="w-full h-24 overflow-visible">
                  <polyline
                    fill="none"
                    stroke="#D97706"
                    strokeWidth="2.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    points={taoChuoiToaDoSVG(xuHuong.diem.map((d) => d.hba1c), 280, 96)}
                  />
                  <polyline
                    fill="none"
                    stroke="#059669"
                    strokeWidth="2"
                    strokeDasharray="4 3"
                    points={taoChuoiToaDoSVG(xuHuong.diem.map((d) => d.egfr), 280, 96)}
                  />
                </svg>
                <div className="flex items-center justify-between text-[11px] text-[#475569] mt-1">
                  {xuHuong.diem.map((d, idx) => (
                    <span key={idx} className="text-center">
                      <strong className="text-[#B45309]">{d.hba1c ?? "—"}%</strong>
                      <span className="text-[#059669] ml-1">({d.egfr ?? "—"})</span>
                      <span className="block text-[10px] text-[#64748B]">{d.ngay.split(" ")[0]}</span>
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Modal Thêm Bệnh Nhân */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-2xs animate-in fade-in">
          <div className="bg-white w-full max-w-md rounded-2xl shadow-2xl border border-[#BAE6FD] p-6">
            <div className="flex items-center justify-between pb-3 border-b border-[#CCE3F0] mb-4">
              <h3 className="font-serif text-lg font-bold text-[#0F172A]">Thêm Hồ sơ Bệnh nhân mới</h3>
              <button
                onClick={() => setShowAddModal(false)}
                className="p-1.5 rounded-lg text-[#64748B] hover:bg-[#E0F2FE] hover:text-[#0369A1] transition-colors"
              >
                <X size={16} />
              </button>
            </div>

            <form onSubmit={handleAddPatient} className="space-y-3.5 text-xs">
              <div>
                <label className="block text-[#0C4A6E] font-semibold mb-1">Họ và tên *</label>
                <input
                  type="text"
                  required
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  placeholder="Ví dụ: Trần Văn An"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-[#BAE6FD] focus:outline-none focus:border-[#0284C7] focus:ring-2 focus:ring-[#BAE6FD]/50 text-[#0F172A]"
                />
              </div>

              <div>
                <label className="block text-[#0C4A6E] font-semibold mb-1">Mã định danh / Ghi chú ca bệnh</label>
                <input
                  type="text"
                  value={newIdentifier}
                  onChange={(e) => setNewIdentifier(e.target.value)}
                  placeholder="Ví dụ: Tái khám Huyết áp, Ho sốt nhẹ"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-[#BAE6FD] focus:outline-none focus:border-[#0284C7] focus:ring-2 focus:ring-[#BAE6FD]/50 text-[#0F172A]"
                />
              </div>

              <div className="grid grid-cols-2 gap-2.5">
                <div>
                  <label className="block text-[#0C4A6E] font-semibold mb-1">Ngày sinh</label>
                  <input
                    type="text"
                    value={newDob}
                    onChange={(e) => setNewDob(e.target.value)}
                    placeholder="DD/MM/YYYY"
                    className="w-full px-3.5 py-2.5 rounded-xl border border-[#BAE6FD] focus:outline-none focus:border-[#0284C7] focus:ring-2 focus:ring-[#BAE6FD]/50 text-[#0F172A]"
                  />
                </div>
                <div>
                  <label className="block text-[#0C4A6E] font-semibold mb-1">Số điện thoại</label>
                  <input
                    type="text"
                    value={newPhone}
                    onChange={(e) => setNewPhone(e.target.value)}
                    placeholder="0912 345 678"
                    className="w-full px-3.5 py-2.5 rounded-xl border border-[#BAE6FD] focus:outline-none focus:border-[#0284C7] focus:ring-2 focus:ring-[#BAE6FD]/50 text-[#0F172A]"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[#0C4A6E] font-semibold mb-1">Lý do vào khám</label>
                <textarea
                  value={newComplaint}
                  onChange={(e) => setNewComplaint(e.target.value)}
                  placeholder="Mô tả triệu chứng chính của bệnh nhân..."
                  className="w-full px-3.5 py-2.5 rounded-xl border border-[#BAE6FD] focus:outline-none focus:border-[#0284C7] focus:ring-2 focus:ring-[#BAE6FD]/50 text-[#0F172A] h-20 resize-none"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-3 border-t border-[#CCE3F0]">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-3.5 py-1.5 rounded-xl border border-[#BAE6FD] hover:bg-[#F0F9FF] text-[#0C4A6E] font-medium transition-colors"
                >
                  Hủy bỏ
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 rounded-xl bg-[#0284C7] text-white hover:bg-[#0369A1] font-semibold transition-all shadow-tactile-doctor"
                >
                  Lưu bệnh nhân
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
