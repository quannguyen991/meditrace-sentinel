import React, { useMemo, useState } from "react";
import { BangDuLieuMinhHoa } from "./BangDuLieuMinhHoa";
import { ClinicalTask, Session } from "../types";
import { sampleTasks } from "../data/mockData";
import { useKho } from "../lib/useKho";
import { trichNhiemVuTuCacCaKham } from "../lib/trichNhiemVuVaTomTat";
import { Plus, Clock, Check, ExternalLink } from "lucide-react";

interface TasksViewProps {
  sessions?: Session[];
  onOpenSession?: (sessionId: string, turn?: number) => void;
}

export const TasksView: React.FC<TasksViewProps> = ({ sessions = [], onOpenSession }) => {
  const [storedTasks, setStoredTasks] = useKho<ClinicalTask>("nhiem-vu", sampleTasks);
  const [newTaskTitle, setNewTaskTitle] = useState("");
  const [newPatientName, setNewPatientName] = useState("");
  const [showAddModal, setShowAddModal] = useState(false);

  const nhiemVuTuCa = useMemo(() => trichNhiemVuTuCacCaKham(sessions), [sessions]);

  const tasks = useMemo(() => {
    const mapStored = new Map(storedTasks.map((t) => [t.id, t]));
    const hopAuto: ClinicalTask[] = nhiemVuTuCa.map((auto) => {
      const daLuu = mapStored.get(auto.id);
      return daLuu ? { ...auto, completed: daLuu.completed } : auto;
    });
    const tapAutoId = new Set(nhiemVuTuCa.map((a) => a.id));
    const conLai = storedTasks.filter((t) => !tapAutoId.has(t.id) && !t.id.startsWith("auto-task-"));
    return [...hopAuto, ...conLai];
  }, [nhiemVuTuCa, storedTasks]);

  const toggleTask = (task: ClinicalTask) => {
    setStoredTasks((prev) => {
      const co = prev.some((t) => t.id === task.id);
      if (co) {
        return prev.map((t) => (t.id === task.id ? { ...t, completed: !t.completed } : t));
      }
      return [{ ...task, completed: !task.completed }, ...prev];
    });
  };

  const handleAddTask = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTaskTitle.trim()) return;

    const created: ClinicalTask = {
      id: `task-${Date.now()}`,
      title: newTaskTitle.trim(),
      patientName: newPatientName.trim() || "Theo dõi ngoại trú",
      dueDate: "Ngày mai",
      completed: false,
      priority: "medium",
    };
    setStoredTasks((prev) => [created, ...prev]);
    setNewTaskTitle("");
    setNewPatientName("");
    setShowAddModal(false);
  };

  return (
    <div id="tasks-view" className="flex-1 flex flex-col h-full bg-gradient-to-b from-[#F0F7FA] via-[#F8FBFC] to-[#EEF6FB] select-none overflow-y-auto">
      {nhiemVuTuCa.length === 0 && <BangDuLieuMinhHoa />}
      <div className="p-6 border-b border-[#CCE3F0] flex items-center justify-between bg-white/90 backdrop-blur-xs shadow-[0_1px_3px_rgba(2,132,199,0.04)]">
        <div>
          <h1 className="font-serif text-2xl font-bold text-[#0F172A] tracking-tight">
            Nhiệm vụ Lâm sàng Hậu khám
          </h1>
          <p className="text-xs text-[#64748B] mt-1">
            Tự động trích xuất tất định các y lệnh tái khám, xét nghiệm kiểm tra lại, cấy máu, hội chẩn &amp; chuyển tuyến từ các ca khám và lưu bền vững SQLite.
          </p>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#0284C7] text-white text-xs font-semibold hover:bg-[#0369A1] transition-all shadow-tactile-doctor active:translate-y-0.5"
        >
          <Plus size={14} className="stroke-[2.5]" />
          <span>Thêm nhiệm vụ mới</span>
        </button>
      </div>

      <div className="flex-1 p-6 max-w-4xl">
        <div className="bg-white rounded-2xl border border-[#BAE6FD] p-5 shadow-tactile-doctor-card">
          <div className="flex flex-col gap-2.5">
            {tasks.map((task) => {
              const tuCaKham = Boolean(task.sessionId);
              return (
                <div
                  key={task.id}
                  onClick={() => toggleTask(task)}
                  className={`flex items-start gap-3.5 p-3.5 rounded-xl border transition-all cursor-pointer ${
                    task.completed
                      ? "bg-[#F0F7FA]/70 border-[#BAE6FD]/40 opacity-70"
                      : "bg-white border-[#BAE6FD] hover:border-[#0284C7] shadow-tactile-doctor-pill hover:shadow-tactile-doctor-card"
                  }`}
                >
                  <div
                    className={`mt-0.5 w-4 h-4 rounded border flex items-center justify-center transition-all flex-shrink-0 ${
                      task.completed
                        ? "bg-[#0284C7] border-[#0284C7] text-white shadow-2xs"
                        : "border-[#94A3B8] bg-white hover:border-[#0284C7]"
                    }`}
                  >
                    {task.completed && <Check size={12} className="stroke-[3]" />}
                  </div>

                  <div className="flex-1 min-w-0 text-xs">
                    <div
                      className={`font-semibold ${
                        task.completed ? "line-through text-[#64748B]" : "text-[#0F172A]"
                      }`}
                    >
                      {task.title}
                    </div>
                    <div className="flex flex-wrap items-center gap-2.5 mt-1.5 text-[11px] text-[#64748B]">
                      {task.patientName && <span className="font-medium">Bệnh nhân: {task.patientName}</span>}
                      <span className="flex items-center gap-1">
                        <Clock size={11} className="text-[#0284C7]" />
                        <span>{task.dueDate}</span>
                      </span>
                      <span
                        className={`px-2 py-0.5 rounded-md text-[10px] uppercase font-bold border ${
                          task.priority === "high"
                            ? "bg-red-50 text-red-700 border-red-200"
                            : task.priority === "medium"
                            ? "bg-amber-50 text-amber-700 border-amber-200"
                            : "bg-slate-50 text-slate-700 border-slate-200"
                        }`}
                      >
                        {task.priority === "high" ? "Ưu tiên cao" : task.priority === "medium" ? "Trung bình" : "Thấp"}
                      </span>
                      {tuCaKham && (
                        <span className="px-2 py-0.5 rounded-md text-[10px] font-semibold bg-[#ECFDF5] text-[#065F46] border border-[#A7F3D0]">
                          Trích tự động từ Kế hoạch
                        </span>
                      )}
                    </div>
                  </div>

                  {task.sessionId && onOpenSession && (
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        onOpenSession(task.sessionId!);
                      }}
                      className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-xl bg-[#F0F9FF] hover:bg-[#E0F2FE] border border-[#BAE6FD] text-[11px] font-semibold text-[#0369A1] flex-shrink-0 cursor-pointer"
                      title="Mở lại hồ sơ ca khám gốc của nhiệm vụ này"
                    >
                      <span>Mở ca khám</span>
                      <ExternalLink size={12} />
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-2xs animate-in fade-in">
          <div className="bg-white w-full max-w-sm rounded-2xl shadow-2xl border border-[#BAE6FD] p-5">
            <h3 className="text-sm font-bold text-[#0F172A] mb-3">Tạo Nhiệm vụ Lâm sàng</h3>
            <form onSubmit={handleAddTask} className="space-y-3 text-xs">
              <input
                type="text"
                value={newTaskTitle}
                onChange={(e) => setNewTaskTitle(e.target.value)}
                placeholder="Ví dụ: Gọi điện hỏi thăm tình trạng hạ sốt của bệnh nhân..."
                className="w-full px-3.5 py-2.5 rounded-xl border border-[#BAE6FD] focus:outline-none focus:border-[#0284C7] focus:ring-2 focus:ring-[#BAE6FD]/50 text-[#0F172A]"
                autoFocus
              />
              <input
                type="text"
                value={newPatientName}
                onChange={(e) => setNewPatientName(e.target.value)}
                placeholder="Tên người bệnh (tuỳ chọn)..."
                className="w-full px-3.5 py-2 rounded-xl border border-[#BAE6FD] focus:outline-none focus:border-[#0284C7] text-[#0F172A]"
              />
              <div className="flex justify-end gap-2 pt-1">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-3.5 py-1.5 rounded-xl border border-[#BAE6FD] hover:bg-[#F0F9FF] text-[#0C4A6E] font-medium transition-colors"
                >
                  Hủy bỏ
                </button>
                <button
                  type="submit"
                  className="px-3.5 py-1.5 rounded-xl bg-[#0284C7] text-white hover:bg-[#0369A1] font-semibold transition-all shadow-tactile-doctor"
                >
                  Tạo mới
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
