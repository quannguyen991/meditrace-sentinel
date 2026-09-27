import React from "react";
import { ViewMode } from "../types";
import { MediTraceLogo } from "./MediTraceLogo";
import { MenuTaiKhoan } from "./MenuTaiKhoan";
import type { NguoiDung } from "../lib/taiKhoan";
import {
  Mic,
  Glasses,
  CheckSquare,
  Users,
  Layers,
  Plus,
  Link2,
  Pill,
  Stethoscope,
  HelpCircle,
  Bell,
  Gift,
  PanelLeft,
  PanelTop,
} from "lucide-react";

interface NavigationRailProps {
  activeView: ViewMode;
  onSelectView: (view: ViewMode) => void;
  onCreateNewSession: () => void;
  position?: "top" | "left";
  onTogglePosition?: () => void;
  /** Mở khung Tình trạng hệ thống. */
  onOpenHelp?: () => void;
  nguoiDung: NguoiDung;
  onDangXuat: () => Promise<void> | void;
}

export const NavigationRail: React.FC<NavigationRailProps> = ({
  activeView,
  onSelectView,
  onCreateNewSession,
  position = "top",
  onOpenHelp,
  onTogglePosition,
  nguoiDung,
  onDangXuat,
}) => {
  const navItems = [
    { id: "evidence" as ViewMode, label: "Hỏi về ca khám", icon: Glasses },
    { id: "scribe" as ViewMode, label: "Ghi chép Lâm sàng", icon: Mic },
    { id: "tasks" as ViewMode, label: "Nhiệm vụ", icon: CheckSquare },
    { id: "patients" as ViewMode, label: "Bệnh nhân", icon: Users },
    { id: "templates" as ViewMode, label: "Mẫu bệnh án", icon: Layers },
  ];

  // THANH ĐIỀU HƯỚNG TRÊN ĐẦU (TOP TASKBAR) BO GÓC TRÒN HIỆN ĐẠI
  if (position === "top") {
    return (
      <header
        id="main-top-taskbar"
        className="w-full px-2 sm:px-3.5 pt-2 pb-1 bg-[#F0F7FA] flex-shrink-0 select-none z-30"
      >
        <div className="w-full bg-[#FFFFFF] border border-[#CCE3F0] rounded-2xl shadow-[0_4px_16px_-3px_rgba(2,132,199,0.08),0_1px_3px_rgba(0,0,0,0.03)] px-2.5 sm:px-3.5 py-1.5 sm:py-2 flex items-center justify-between gap-2 sm:gap-3">
          {/* Cụm Trái: Logo dự án + Tên MediTrace & Nút Tạo ca khám */}
          <div className="flex items-center gap-2 sm:gap-3 flex-shrink-0">
            <button
              id="btn-trang-chu"
              onClick={() => onSelectView("evidence")}
              className="p-1 rounded-xl hover:bg-[#E0F2FE] transition-transform active:scale-95 flex items-center gap-2 group"
              title="Trang chủ MediTrace"
            >
              <MediTraceLogo size={32} />
              <div className="hidden sm:flex flex-col text-left">
                <span className="font-serif font-bold text-sm sm:text-base text-[#0C4A6E] tracking-tight leading-none">
                  MediTrace
                </span>
                <span className="text-[9px] font-sans font-semibold text-[#0284C7] tracking-wider uppercase leading-tight mt-0.5">
                  Lâm sàng AI
                </span>
              </div>
            </button>

            <button
              id="btn-nav-create"
              onClick={onCreateNewSession}
              className="px-2.5 sm:px-3.5 py-1.5 rounded-xl bg-[#0284C7] text-white flex items-center gap-1.5 hover:bg-[#0369A1] active:translate-y-0.5 transition-all shadow-tactile-doctor text-xs font-semibold whitespace-nowrap"
              title="Tạo phiên ghi chép ca khám mới"
            >
              <Plus size={14} className="stroke-[2.5]" />
              <span className="hidden sm:inline">Tạo ca khám</span>
            </button>
          </div>

          {/* Cụm Giữa: Các Tab điều hướng bo góc tròn dạng Pill với hiệu ứng nổi khối */}
          <nav className="flex items-center gap-1 min-w-0 bg-[#E0F2FE]/70 p-1 rounded-xl border border-[#BAE6FD] shadow-tactile-inset overflow-x-auto no-scrollbar">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeView === item.id;
              return (
                <button
                  key={item.id}
                  id={`nav-item-${item.id}`}
                  onClick={() => onSelectView(item.id)}
                  title={item.label}
                  className={`group flex items-center h-8 rounded-lg text-xs font-medium whitespace-nowrap transition-all duration-200 ease-out select-none ${
                    isActive
                      ? "bg-white text-[#0369A1] shadow-tactile-pill border border-[#BAE6FD] font-semibold px-3"
                      : "text-[#475569] hover:text-[#0369A1] hover:bg-white/80 px-2 hover:px-2.5"
                  }`}
                >
                  <Icon
                    size={15}
                    className={`flex-shrink-0 transition-colors ${
                      isActive
                        ? "stroke-[2.2] text-[#0284C7]"
                        : "stroke-[1.8] group-hover:text-[#0369A1]"
                    }`}
                  />
                  {/* Chưa di chuột vào: chỉ hiện icon.
                      Đang ở tác vụ nào: hiện sang bên phải như hiện tại.
                      Khi di chuột vào (hover): trượt mở rộng tên tác vụ sang bên phải */}
                  <span
                    className={`whitespace-nowrap transition-all duration-200 ease-out overflow-hidden text-xs ${
                      isActive
                        ? "max-w-[160px] opacity-100 ml-1.5 font-semibold text-[#0369A1]"
                        : "max-w-0 opacity-0 group-hover:max-w-[160px] group-hover:opacity-100 group-hover:ml-1.5 text-[#0F172A]"
                    }`}
                  >
                    {item.label}
                  </span>
                </button>
              );
            })}
          </nav>

          {/* Cụm Phải: Tiện ích lâm sàng và Tài khoản bác sĩ (Tối ưu gọn gàng trên tablet) */}
          <div className="flex items-center gap-1 sm:gap-1.5 text-[#475569] flex-shrink-0">
            {onTogglePosition && (
              <button
                onClick={onTogglePosition}
                className="hidden 2xl:flex items-center gap-1 px-2 py-1 rounded-lg hover:bg-[#E0F2FE] hover:text-[#0369A1] text-[11px] text-[#475569] transition-colors border border-transparent hover:border-[#BAE6FD] whitespace-nowrap shadow-2xs"
                title="Gắn thanh công cụ sang bên trái"
              >
                <PanelLeft size={14} />
                <span>Gắn thanh bên</span>
              </button>
            )}

            <button
              id="btn-nav-notifications"
              onClick={onOpenHelp}
              className="p-1.5 rounded-lg hover:bg-[#E0F2FE] hover:text-[#0369A1] transition-colors relative"
              title="Tình trạng hệ thống"
            >
              <Bell size={15} />
            </button>

            <MenuTaiKhoan nguoiDung={nguoiDung} onDangXuat={onDangXuat} huong="top" />
          </div>
        </div>
      </header>
    );
  }

  // THANH ĐIỀU HƯỚNG BÊN TRÁI (LEFT VERTICAL SIDEBAR)
  return (
    <aside
      id="main-navigation-rail"
      className="w-20 flex-shrink-0 bg-[#F0F7FA] border-r border-[#CCE3F0] flex flex-col items-center py-3 select-none z-30"
    >
      {/* Top Logo & Project Name */}
      <div className="mb-3 flex flex-col items-center justify-center">
        <button
          id="btn-trang-chu"
          onClick={() => onSelectView("evidence")}
          className="p-1 rounded-xl hover:bg-[#E0F2FE] transition-transform active:scale-95 flex flex-col items-center justify-center group"
          title="Trang chủ MediTrace"
        >
          <MediTraceLogo size={34} />
          <span className="font-serif font-bold text-[10px] text-[#0C4A6E] tracking-tight mt-1 leading-none">
            MediTrace
          </span>
        </button>
      </div>

      {/* + Nút Tạo ca khám */}
      <div className="mb-3">
        <button
          id="btn-nav-create"
          onClick={onCreateNewSession}
          className="w-12 h-9 rounded-xl bg-[#0284C7] text-white flex items-center justify-center hover:bg-[#0369A1] transition-colors shadow-tactile-doctor group"
          title="Tạo phiên ghi chép ca khám mới"
        >
          <Plus size={18} className="stroke-[2.5]" />
        </button>
      </div>

      {/* Main Navigation Items */}
      <nav className="flex flex-col gap-1.5 w-full px-1.5">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeView === item.id;
          return (
            <button
              key={item.id}
              id={`nav-item-${item.id}`}
              onClick={() => onSelectView(item.id)}
              title={item.label}
              className={`group flex flex-col items-center justify-center py-2 px-1 rounded-xl text-center transition-all ${
                isActive
                  ? "bg-white text-[#0369A1] font-semibold border border-[#BAE6FD] shadow-tactile-pill"
                  : "text-[#475569] hover:bg-[#E0F2FE]/70 hover:text-[#0369A1]"
              }`}
            >
              <Icon size={19} className={isActive ? "stroke-[2.2] text-[#0284C7]" : "stroke-[1.8] group-hover:text-[#0369A1]"} />
              <span
                className={`text-[10px] leading-tight tracking-tight transition-all duration-200 overflow-hidden ${
                  isActive
                    ? "mt-1 max-h-6 opacity-100 font-semibold text-[#0369A1]"
                    : "max-h-0 opacity-0 group-hover:max-h-6 group-hover:opacity-100 group-hover:mt-1 text-[#0F172A]"
                }`}
              >
                {item.label}
              </span>
            </button>
          );
        })}
      </nav>

      <div className="flex-1" />

      {/* Bottom Utility Icons */}
      <div className="flex flex-col items-center gap-2 text-[#475569]">
        {onTogglePosition && (
          <button
            onClick={onTogglePosition}
            className="p-1.5 rounded-lg hover:bg-[#E0F2FE] hover:text-[#0369A1] transition-colors text-[#475569]"
            title="Gắn thanh công cụ lên trên đầu"
          >
            <PanelTop size={16} />
          </button>
        )}
        <button
          id="btn-nav-help"
          onClick={onOpenHelp}
          className="p-1.5 rounded-lg hover:bg-[#E0F2FE] hover:text-[#0369A1] transition-colors"
          title="Trợ giúp"
        >
          <HelpCircle size={16} />
        </button>
        <button
          id="btn-nav-notifications"
          onClick={onOpenHelp}
          className="p-1.5 rounded-lg hover:bg-[#E0F2FE] hover:text-[#0369A1] transition-colors relative"
          title="Tình trạng hệ thống"
        >
          <Bell size={16} />
        </button>

        <MenuTaiKhoan nguoiDung={nguoiDung} onDangXuat={onDangXuat} huong="left" />
      </div>
    </aside>
  );
};
