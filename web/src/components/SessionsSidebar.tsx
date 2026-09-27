import React, { useState } from "react";
import { Session } from "../types";
import {
  Search,
  SlidersHorizontal,
  Plus,
  ChevronDown,
  ChevronsLeft,
  ChevronsRight,
  Maximize2,
  Trash2,
  BookOpen,
  Calculator,
  GraduationCap,
} from "lucide-react";

interface SessionsSidebarProps {
  sessions: Session[];
  activeSessionId: string;
  onSelectSession: (id: string) => void;
  onCreateSession: () => void;
  onDeleteSession?: (id: string) => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

export const SessionsSidebar: React.FC<SessionsSidebarProps> = ({
  sessions,
  activeSessionId,
  onSelectSession,
  onCreateSession,
  onDeleteSession,
  isCollapsed,
  onToggleCollapse,
}) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [filterMode, setFilterMode] = useState<"my" | "all">("my");
  const [showSearchInput, setShowSearchInput] = useState(false);

  const filteredSessions = sessions.filter((s) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      s.patientIdentifier.toLowerCase().includes(q) ||
      s.patientSubtitle.toLowerCase().includes(q) ||
      s.transcript.toLowerCase().includes(q)
    );
  });

  if (isCollapsed) {
    return (
      <div
        id="sessions-sidebar-collapsed"
        className="w-10 flex-shrink-0 bg-[#F0F7FA] border-r border-[#CCE3F0] flex flex-col items-center py-3 select-none gap-2"
      >
        <button
          onClick={onToggleCollapse}
          className="p-1.5 rounded-lg text-[#0369A1] hover:bg-[#E0F2FE] hover:text-[#0284C7] transition-colors"
          title="Mở rộng danh sách ca khám"
        >
          <ChevronsRight size={18} />
        </button>

        <button
          onClick={onCreateSession}
          className="p-1.5 rounded-lg bg-[#0284C7] text-white hover:bg-[#0369A1] transition-colors shadow-tactile-doctor"
          title="Tạo ca khám mới"
        >
          <Plus size={15} />
        </button>
      </div>
    );
  }

  return (
    <>
    <div className="fixed inset-0 bg-black/25 z-30 md:hidden" onClick={onToggleCollapse} />
    <div
      id="sessions-sidebar"
      className="w-[min(18rem,85vw)] md:w-64 flex-shrink-0 bg-[#F0F7FA] border-r border-[#CCE3F0] shadow-[2px_0_10px_rgba(2,132,199,0.04)] flex flex-col h-full select-none fixed md:relative left-0 top-0 bottom-0 z-40 md:z-auto"
    >
      {/* Top Header */}
      <div className="p-3 border-b border-[#D0E2ED] flex flex-col gap-2.5">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-[#0F172A] tracking-tight">Danh sách Ca khám</h2>
          <div className="flex items-center gap-1 text-[#64748B]">
            <button
              onClick={onToggleCollapse}
              className="p-1 rounded-md hover:bg-[#E0F2FE] hover:text-[#0284C7] transition-colors"
              title="Thu gọn danh sách"
            >
              <ChevronsLeft size={14} />
            </button>
          </div>
        </div>

        {/* Action Controls Bar */}
        <div className="flex items-center justify-between gap-1.5">
          <button
            onClick={() => setFilterMode(filterMode === "my" ? "all" : "my")}
            className="text-xs px-2.5 py-1 rounded-full bg-white border border-[#BAE6FD] text-[#0C4A6E] font-semibold hover:bg-[#F0F9FF] shadow-tactile-doctor-pill transition-all"
          >
            {filterMode === "my" ? "Ca của tôi" : "Tất cả ca khám"}
          </button>

          <div className="flex items-center gap-1">
            <button
              onClick={() => setShowSearchInput(!showSearchInput)}
              className="p-1.5 rounded-lg text-[#0369A1] hover:bg-white hover:text-[#0284C7] hover:shadow-2xs transition-all"
              title="Tìm kiếm ca khám"
            >
              <Search size={14} />
            </button>
            <button
              className="p-1.5 rounded-lg text-[#0369A1] hover:bg-white hover:text-[#0284C7] hover:shadow-2xs transition-all"
              title="Bộ lọc & Sắp xếp"
            >
              <SlidersHorizontal size={14} />
            </button>
            <button
              onClick={onCreateSession}
              className="p-1.5 rounded-lg bg-[#0284C7] text-white hover:bg-[#0369A1] transition-all shadow-tactile-doctor active:translate-y-0.5"
              title="Tạo ca khám mới"
            >
              <Plus size={14} />
            </button>
          </div>
        </div>

        {/* Search input if toggled */}
        {showSearchInput && (
          <div className="mt-1">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Tìm kiếm theo tên hoặc triệu chứng..."
              className="w-full text-xs px-2.5 py-1.5 rounded-lg border border-[#BAE6FD] bg-white shadow-[inset_0_1px_2.5px_rgba(2,132,199,0.06)] focus:outline-none focus:border-[#0284C7] focus:ring-1 focus:ring-[#BAE6FD]"
              autoFocus
            />
          </div>
        )}
      </div>

      {/* Sessions List */}
      <div className="flex-1 overflow-y-auto px-2 py-3">
        {/* Date Group: Today */}
        <div className="mb-2">
          <div className="flex items-center gap-1.5 px-2 py-1 text-xs font-semibold text-[#0369A1]">
            <ChevronDown size={14} className="text-[#0284C7]" />
            <span>Hôm nay</span>
          </div>

          <div className="flex flex-col gap-1.5 mt-1">
            {filteredSessions.map((session) => {
              const isSelected = session.id === activeSessionId;
              return (
                <div
                  key={session.id}
                  onClick={() => onSelectSession(session.id)}
                  className={`group relative flex items-start gap-2.5 p-2.5 rounded-xl cursor-pointer transition-all border ${
                    isSelected
                      ? "bg-white text-[#0C4A6E] border-[#BAE6FD] shadow-[0_4px_14px_-2px_rgba(2,132,199,0.12)] ring-1 ring-[#BAE6FD]"
                      : "text-[#334155] border-transparent hover:bg-white/80 hover:border-[#BAE6FD]/60 hover:shadow-2xs"
                  }`}
                >
                  {/* Circular recording/session status icon */}
                  <div className={`mt-0.5 w-5 h-5 rounded-full border border-dashed flex items-center justify-center flex-shrink-0 ${isSelected ? "border-[#0284C7] bg-[#E0F2FE]" : "border-[#94A3B8]"}`}>
                    <span className={`w-1.5 h-1.5 rounded-full ${isSelected ? "bg-[#0284C7]" : "bg-[#94A3B8]"}`} />
                  </div>

                  <div className="flex-1 min-w-0 pr-1">
                    <div className="flex items-center justify-between">
                      <p className="text-xs font-semibold truncate text-[#0F172A]">
                        {session.patientIdentifier.length > 18
                          ? `${session.patientIdentifier.slice(0, 18)}...`
                          : session.patientIdentifier}
                      </p>
                      <span className="text-[10px] text-[#64748B] flex-shrink-0 ml-1">
                        {session.time}
                      </span>
                    </div>

                    <div className="flex items-center justify-between mt-0.5">
                      <p className="text-[11px] text-[#475569] truncate">
                        {session.patientSubtitle}
                      </p>
                    </div>
                  </div>

                  {/* Delete button on hover */}
                  {onDeleteSession && sessions.length > 1 && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onDeleteSession(session.id);
                      }}
                      className="opacity-0 group-hover:opacity-100 p-1 text-[#94A3B8] hover:text-red-600 transition-opacity"
                      title="Xóa ca khám"
                    >
                      <Trash2 size={12} />
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        </div>

      </div>
    </div>
    </>
  );
};
