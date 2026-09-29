import React from "react";
import { ArrowRight, Cloud, ClipboardList, FileText, Glasses, Mic, Stethoscope, Sun, type LucideIcon } from "lucide-react";
import type { Session } from "../types";

type Task = {
  title: string;
  detail: string;
  icon: LucideIcon;
  tone: string;
  run: () => void;
};

type Props = {
  /** Công tắc "Mô hình ngoài" đang bật hay tắt (mặc định tắt). */
  choPhepNgoai: boolean;
  /** Nạp một ca mẫu đã chạy trước (xem ngay, không phải chờ mô hình). */
  onNapCaMau: () => void;
  doctorName: string;
  sessions: Session[];
  onCreateSession: () => void;
  onOpenTranscript: () => void;
  onOpenDraft: () => void;
  onOpenEvidence: () => void;
  onOpenTemplates: () => void;
  onOpenSession: (id: string) => void;
  onViewAllSessions: () => void;
};

function tenCa(session: Session) {
  const ten = session.patientIdentifier?.trim();
  return !ten || ten.toLowerCase().startsWith("thêm tên định danh") ? "Ca khám mới" : ten;
}

function thoiGianCa(session: Session) {
  if (!session.date) return session.time;
  if (!session.time || session.date.includes(session.time)) return session.date;
  return `${session.date} · ${session.time}`;
}

export const HomeDashboard: React.FC<Props> = ({
  choPhepNgoai,
  onNapCaMau,
  doctorName,
  sessions,
  onCreateSession,
  onOpenTranscript,
  onOpenDraft,
  onOpenEvidence,
  onOpenTemplates,
  onOpenSession,
  onViewAllSessions,
}) => {
  const greetingName = /^BS\./i.test(doctorName.trim()) ? doctorName.trim() : `BS. ${doctorName.trim()}`;
  const tasks: Task[] = [
    { title: "Ghi chép lâm sàng", detail: "Ghi âm hoặc nhập lời thoại.", icon: Mic, tone: "blue", run: onOpenTranscript },
    { title: "Bản nháp hồ sơ", detail: "Xem hoặc tạo bản nháp của ca đang mở.", icon: FileText, tone: "teal", run: onOpenDraft },
    { title: "Kiểm tra bằng chứng", detail: "Xem thông tin gắn với hội thoại.", icon: Glasses, tone: "violet", run: onOpenEvidence },
    { title: "Mẫu bệnh án", detail: "Chọn mẫu hồ sơ cần dùng.", icon: ClipboardList, tone: "orange", run: onOpenTemplates },
  ];

  return (
    <section aria-label="Trang chủ" className="flex-1 min-w-0 overflow-y-auto bg-gradient-to-b from-[#F2FAFE] via-[#F8FBFD] to-[#F3F9FC] px-4 py-4 md:px-6 md:py-5">
      <div className="mx-auto flex w-full max-w-[1280px] flex-col gap-4">
        <section className="home-dashboard-enter relative isolate min-h-[140px] overflow-hidden rounded-[24px] border border-[#D1EAF7] bg-gradient-to-r from-white via-[#F5FBFF] to-[#DFF3FB] px-5 py-5 shadow-[0_10px_28px_rgba(31,117,160,0.08)] sm:min-h-[184px] sm:px-7 sm:py-5">
          <div aria-hidden="true" className="absolute -right-12 -top-20 -z-10 h-64 w-64 rounded-full bg-white/80 blur-3xl" />
          <div aria-hidden="true" className="absolute bottom-0 right-[14%] -z-10 h-36 w-44 rounded-full bg-[#A9E8F1]/35 blur-2xl" />

          <div className="relative z-20 flex min-h-[134px] max-w-full flex-col items-start justify-center sm:min-h-[120px]">
            <div className="flex max-w-full items-center gap-2 text-[19px] font-extrabold leading-tight tracking-[-0.035em] text-[#0D2A62] sm:text-[23px] lg:text-[25px]">
              <span className="truncate">Xin chào, {greetingName}</span>
              <Sun aria-hidden="true" className="shrink-0 text-[#F8B82D]" size={25} strokeWidth={2.5} />
            </div>
            <h2 className="mt-1 text-balance text-[18px] font-medium leading-tight tracking-[-0.025em] text-[#122F68] sm:text-[21px] lg:text-[23px]">
              Hôm nay bạn muốn làm gì?
            </h2>
            <p className="mt-2 max-w-[29rem] text-[11px] leading-relaxed text-[#6D86A4] sm:text-[12px] lg:text-[13px]">
              MediTrace dựng bản nháp hồ sơ từ lời thoại khám bệnh; mỗi dòng dẫn về câu nói gốc để bác sĩ kiểm lại. Không chẩn đoán, không kê đơn.
            </p>
            <button
              onClick={onNapCaMau}
              className="mt-3 inline-flex flex-wrap items-center justify-center gap-x-2 gap-y-0.5 rounded-xl bg-[#0874B9] px-4 py-2 text-[13px] font-semibold text-white shadow-[0_6px_16px_rgba(8,116,185,0.28)] transition hover:bg-[#075F91] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#0874B9] focus-visible:ring-offset-2"
            >
              Xem thử với ca mẫu
              <span className="text-[11px] font-normal opacity-85">Try a sample case</span>
              <ArrowRight size={14} />
            </button>
          </div>

        </section>

        <section aria-label="Tác vụ chính" className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
          {tasks.map((task, index) => {
            const Icon = task.icon;
            const tone = {
              blue: "bg-[#E3F3FF] text-[#087FC1] ring-[#C6E7FB]",
              teal: "bg-[#E0FAF4] text-[#0AA98F] ring-[#B9F0E4]",
              violet: "bg-[#F0E9FF] text-[#8B5CF6] ring-[#DDD0FF]",
              orange: "bg-[#FFF0E2] text-[#EA812C] ring-[#FFD9B6]",
            }[task.tone];

            return (
              <button
                key={task.title}
                onClick={task.run}
                style={{ animationDelay: `${index * 75}ms` }}
                className="home-task-enter group flex min-h-[128px] items-start gap-3 rounded-2xl border border-[#D8EAF4] bg-white/95 p-4 text-left shadow-[0_6px_18px_rgba(34,108,147,0.045)] transition duration-200 hover:-translate-y-1 hover:border-[#9DD6F2] hover:shadow-[0_13px_26px_rgba(26,118,164,0.13)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#38BDF8]"
              >
                <span className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-[14px] ring-1 transition duration-200 group-hover:scale-105 ${tone}`}>
                  <Icon size={20} strokeWidth={1.9} />
                </span>
                <span className="flex min-w-0 flex-1 flex-col pt-0.5">
                  <span className="flex items-center justify-between gap-2 text-[13px] font-bold leading-snug text-[#123E5B]">
                    <span>{task.title}</span>
                    <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-[#EFF8FE] text-[#1684BC] transition duration-200 group-hover:translate-x-0.5 group-hover:bg-[#0785C4] group-hover:text-white">
                      <ArrowRight size={14} />
                    </span>
                  </span>
                  <span className="mt-1.5 text-[11px] leading-relaxed text-[#6C8799]">{task.detail}</span>
                </span>
              </button>
            );
          })}
        </section>

        <section aria-label="Nguồn xử lý" className="rounded-2xl border border-[#D8EAF4] bg-white/90 px-4 py-3 shadow-[0_5px_16px_rgba(34,108,147,0.035)] sm:px-5">
          <h3 className="mb-2 text-[13px] font-bold text-[#153D5A]">Ai xử lý phần nào</h3>
          <ul className="grid gap-2.5 text-[12px] leading-relaxed text-[#3F6076] md:grid-cols-3">
            <li className="flex gap-2.5">
              <Mic size={16} className="mt-0.5 shrink-0 text-[#087FC1]" />
              <span><strong className="text-[#153D5A]">Chép lời:</strong> PhoWhisper, chạy tại chỗ. Âm thanh không rời máy chủ của dự án.</span>
            </li>
            <li className="flex gap-2.5">
              <FileText size={16} className="mt-0.5 shrink-0 text-[#0AA98F]" />
              <span><strong className="text-[#153D5A]">Bản nháp hồ sơ:</strong> Qwen3-4B đã tinh chỉnh, chạy tại chỗ. Mỗi dòng dẫn về câu nói gốc, có bước kiểm căn cứ. Bác sĩ duyệt.</span>
            </li>
            <li className="flex gap-2.5">
              <Cloud size={16} className={`mt-0.5 shrink-0 ${choPhepNgoai ? "text-[#B91C1C]" : "text-[#8B9AA8]"}`} />
              <span>
                <strong className="text-[#153D5A]">Hỏi đáp, sửa theo lời nhắc, soạn mẫu khác:</strong> mô hình ngoài (thương mại).{" "}
                {choPhepNgoai
                  ? <strong className="text-[#B91C1C]">Đang BẬT: nội dung ca khám sẽ gửi ra ngoài.</strong>
                  : <strong>Đang tắt, không có gì gửi ra ngoài.</strong>}{" "}
                Kết quả chưa qua bước kiểm căn cứ.
              </span>
            </li>
          </ul>
        </section>

        <section aria-label="Ca khám gần đây" className="overflow-hidden rounded-2xl border border-[#D8EAF4] bg-white/90 shadow-[0_5px_16px_rgba(34,108,147,0.035)]">
          <div className="flex items-center justify-between gap-3 border-b border-[#E6F0F5] px-4 py-3 sm:px-5">
            <h3 className="text-[13px] font-bold text-[#153D5A]">Ca khám gần đây</h3>
            <button onClick={onViewAllSessions} className="text-[11px] font-semibold text-[#087FC1] transition hover:text-[#075F91]">
              Tất cả ca <ArrowRight size={13} className="ml-0.5 inline" />
            </button>
          </div>
          {sessions.length > 0 ? (
            <div className="divide-y divide-[#EDF3F6]">
              {sessions.slice(0, 3).map((session) => (
                <button
                  key={session.id}
                  onClick={() => onOpenSession(session.id)}
                  className="group flex w-full items-center gap-3 px-4 py-3 text-left transition hover:bg-[#F5FAFD] sm:px-5"
                >
                  <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[#EAF6FD] text-[#1684BC]">
                    <Stethoscope size={15} />
                  </span>
                  <span className="min-w-0 flex-1 truncate text-[12px] font-semibold text-[#244E68]">{tenCa(session)}</span>
                  <span className="shrink-0 text-[10px] text-[#8197A5]">{thoiGianCa(session)}</span>
                  <ArrowRight size={14} className="shrink-0 text-[#9AB8C9] transition group-hover:translate-x-0.5 group-hover:text-[#087FC1]" />
                </button>
              ))}
            </div>
          ) : (
            <div className="flex items-center justify-between gap-3 px-5 py-4 text-[12px] text-[#718B9A]">
              <span>Chưa có ca khám.</span>
              <button onClick={onCreateSession} className="font-semibold text-[#087FC1] hover:text-[#075F91]">Tạo ca khám</button>
            </div>
          )}
        </section>
      </div>
    </section>
  );
};
