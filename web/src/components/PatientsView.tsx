import React, { useState } from "react";
import { BangDuLieuMinhHoa } from "./BangDuLieuMinhHoa";
import { Patient } from "../types";
import { samplePatients } from "../data/mockData";
import {
  Upload,
  Plus,
  Search,
  SlidersHorizontal,
  Users,
  X,
} from "lucide-react";

interface PatientsViewProps {
  onStartSessionWithPatient?: (patient: Patient) => void;
}

export const PatientsView: React.FC<PatientsViewProps> = ({
  onStartSessionWithPatient,
}) => {
  const [patients, setPatients] = useState<Patient[]>(samplePatients);
  const [searchQuery, setSearchQuery] = useState("");
  const [showAddModal, setShowAddModal] = useState(false);

  // Form thêm bệnh nhân
  const [newName, setNewName] = useState("");
  const [newIdentifier, setNewIdentifier] = useState("");
  const [newDob, setNewDob] = useState("");
  const [newPhone, setNewPhone] = useState("");
  const [newComplaint, setNewComplaint] = useState("");

  const filteredPatients = patients.filter(
    (p) =>
      p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.identifier.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleAddPatient = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName.trim()) return;

    const created: Patient = {
      id: `pat-${Date.now()}`,
      name: newName.trim(),
      identifier: newIdentifier.trim() || newName.trim(),
      dob: newDob.trim() || "Chưa xác định",
      phone: newPhone.trim() || "Chưa xác định",
      lastConsultation: "Hôm nay",
      chiefComplaint: newComplaint.trim() || "Khám nội khoa tổng quát",
    };

    setPatients([created, ...patients]);
    setShowAddModal(false);
    setNewName("");
    setNewIdentifier("");
    setNewDob("");
    setNewPhone("");
    setNewComplaint("");
  };

  return (
    <div id="patients-view" className="flex-1 flex flex-col h-full bg-gradient-to-b from-[#F0F7FA] via-[#F8FBFC] to-[#EEF6FB] select-none overflow-y-auto">
      <BangDuLieuMinhHoa />
      {/* Header */}
      <div className="p-6 border-b border-[#CCE3F0] flex items-center justify-between bg-white/90 backdrop-blur-xs shadow-[0_1px_3px_rgba(2,132,199,0.04)]">
        <div>
          <h1 className="font-serif text-2xl font-bold text-[#0F172A] tracking-tight">
            Quản lý Bệnh nhân
          </h1>
          <div className="flex items-center gap-2 mt-2">
            <span className="text-xs px-2.5 py-1 rounded-full bg-[#E0F2FE] text-[#0369A1] border border-[#BAE6FD] font-semibold shadow-tactile-doctor-pill">
              Tất cả bệnh nhân ({patients.length})
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => alert("Chức năng nhập danh sách bệnh nhân từ file CSV hoặc hệ thống HIS/EHR")}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-[#BAE6FD] bg-white text-xs font-semibold text-[#0C4A6E] hover:bg-[#E0F2FE] transition-colors shadow-tactile-doctor-pill"
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
                  <th className="py-3 px-4">Định danh / Triệu chứng</th>
                  <th className="py-3 px-4">Ngày sinh</th>
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
                          <div className="font-bold text-[#0F172A]">{patient.name}</div>
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
                      {onStartSessionWithPatient && (
                        <button
                          onClick={() => onStartSessionWithPatient(patient)}
                          className="px-3 py-1.5 rounded-xl bg-[#0284C7] text-white text-xs font-semibold hover:bg-[#0369A1] transition-all shadow-tactile-doctor active:translate-y-0.5"
                        >
                          Khám bệnh (Scribe)
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
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
