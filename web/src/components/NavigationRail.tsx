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
  Stethoscope,
  Bell,
  PanelLeft,
  PanelTop,
  Home,
  FileText,
  Library,
  Settings,
  ChevronDown,
} from "lucide-react";

interface NavigationRailProps {
  activeView: ViewMode;
  activeNavigationItem: string;
  onSelectNavigationItem: (item: string) => void;
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
  activeNavigationItem,
  onSelectNavigationItem,
  onSelectView,
  onCreateNewSession,
  position = "top",
  onOpenHelp,
  onTogglePosition,
  nguoiDung,
  onDangXuat,
}) => {
  const [moQuanLy, setMoQuanLy] = React.useState(false);
  React.useEffect(() => {
    if (["templates", "tasks", "patients"].includes(activeNavigationItem)) setMoQuanLy(true);
  }, [activeNavigationItem]);
  const navItems = [
    { id: "evidence" as ViewMode, label: "Hỏi về ca khám", icon: Glasses },
    { id: "scribe" as ViewMode, label: "Ghi chép Lâm sàng", icon: Mic },
    { id: "tasks" as ViewMode, label: "Nhiệm vụ", icon: CheckSquare },
    { id: "patients" as ViewMode, label: "Bệnh nhân", icon: Users },
    { id: "templates" as ViewMode, label: "Mẫu bệnh án", icon: Layers },
  ];
  const leftNavGroups = [
    {
      label: "Không gian làm việc",
      items: [
        { id: "home", view: "home" as ViewMode, label: "Trang chủ", icon: Home },
        { id: "sessions", view: "scribe" as ViewMode, label: "Ca khám", icon: Stethoscope },
        { id: "transcript", view: "scribe" as ViewMode, label: "Ghi âm & ghi chép", icon: Mic },
        { id: "draft", view: "scribe" as ViewMode, label: "Bản nháp hồ sơ", icon: FileText },
        { id: "proof", view: "verification" as ViewMode, label: "Bằng chứng hội thoại", icon: Link2 },
        { id: "questions", view: "evidence" as ViewMode, label: "Hỏi ca khám", icon: Glasses },
        { id: "library", view: "library" as ViewMode, label: "Thư viện y khoa", icon: Library },
        { id: "settings", view: "settings" as ViewMode, label: "Cài đặt", icon: Settings },
      ],
    },
    {
      label: "Quản lý",
      items: [
        { id: "templates", view: "templates" as ViewMode, label: "Mẫu bệnh án", icon: Layers },
        { id: "tasks", view: "tasks" as ViewMode, label: "Nhiệm vụ", icon: CheckSquare },
        { id: "patients", view: "patients" as ViewMode, label: "Bệnh nhân", icon: Users },
      ],
    },
  ];
  const renderLeftNavItem = (item: (typeof leftNavGroups)[number]["items"][number]) => {
    const Icon = item.icon;
    const isActive = activeNavigationItem === item.id;
    return (
      <button
        key={item.id}
        id={`nav-item-${item.id}`}
        onClick={() => onSelectNavigationItem(item.id)}
        title={item.label}
        aria-current={isActive ? "page" : undefined}
        className={`group w-full min-h-11 flex items-center justify-center lg:justify-start gap-0 lg:gap-3 px-0 lg:px-3 rounded-xl text-center lg:text-left transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#38BDF8] focus-visible:ring-offset-2 ${
          isActive
            ? "bg-[#E2F2FF] text-[#0874B9] font-semibold border border-[#C7E4F8] shadow-[0_3px_10px_rgba(18,113,174,0.07)]"
            : "text-[#405B70] hover:bg-[#E9F5FC] hover:text-[#0874B9] border border-transparent"
        }`}
      >
        <Icon size={19} className={`shrink-0 ${isActive ? "stroke-[2.2] text-[#087FC1]" : "stroke-[1.8] group-hover:text-[#0874B9]"}`} />
        <span className="hidden lg:block text-[13px] leading-tight tracking-[0.005em]">
          {item.label}
        </span>
      </button>
    );
  };

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
              onClick={() => onSelectNavigationItem("home")}
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

  // THANH ĐIỀU HƯỚNG BÊN TRÁI
  return (
    <aside
      id="main-navigation-rail"
      className="w-14 sm:w-[4.5rem] lg:w-[16rem] xl:w-[17rem] min-h-0 flex-shrink-0 overflow-y-auto bg-gradient-to-b from-white via-[#F8FCFF] to-[#EDF7FD] border-r border-[#D6EAF4] flex flex-col items-center lg:items-stretch px-2 lg:px-3.5 py-3.5 select-none z-30"
    >
      <div className="mb-3 flex items-center justify-center lg:justify-start">
        <button
          id="btn-trang-chu"
          onClick={() => onSelectNavigationItem("home")}
          className="w-11 h-11 lg:w-full lg:h-auto p-1.5 lg:p-2 rounded-2xl hover:bg-[#EAF6FD] transition-all active:scale-[0.98] flex flex-col lg:flex-row items-center justify-center lg:justify-start gap-0.5 lg:gap-3 group"
          title="Trang chủ MediTrace"
        >
          <MediTraceLogo size={36} />
          <span className="hidden lg:flex flex-col items-start text-left">
            <span className="font-serif font-bold text-[17px] text-[#0C4A6E] tracking-tight leading-none">
              MediTrace
            </span>
            <span className="mt-1 text-[9px] font-semibold uppercase tracking-[0.15em] text-[#0284C7]">
              Lâm sàng AI
            </span>
          </span>
        </button>
      </div>

      <div className="mb-2.5 w-full flex justify-center lg:justify-start">
        <button
          id="btn-nav-create"
          onClick={onCreateNewSession}
          className="w-11 h-11 lg:w-full lg:h-11 rounded-xl bg-[#087FC1] text-white flex items-center justify-center lg:justify-start lg:px-3 gap-2.5 hover:bg-[#066FAE] active:scale-[0.98] transition-all shadow-[0_5px_14px_rgba(2,132,199,0.2)] group focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#38BDF8] focus-visible:ring-offset-2"
          title="Tạo phiên ghi chép ca khám mới"
        >
          <Plus size={18} className="stroke-[2.5] shrink-0" />
          <span className="hidden lg:inline text-[13px] font-semibold">Ca khám mới</span>
        </button>
      </div>

      {leftNavGroups.map((group, index) => index === 0 ? (
        <section key={group.label} className="w-full">
          <div className="hidden lg:block px-2 pt-3 pb-1 text-[9px] font-semibold uppercase tracking-[0.16em] text-[#7A98AA]">
            {group.label}
          </div>
          <nav aria-label={group.label} className="flex flex-col gap-1 w-full mt-1 lg:mt-0">
            {group.items.map(renderLeftNavItem)}
          </nav>
        </section>
      ) : (
        <section key={group.label} className="w-full">
          <button
            onClick={() => setMoQuanLy((value) => !value)}
            aria-expanded={moQuanLy}
            title={group.label}
            className="w-full min-h-11 flex items-center justify-center lg:justify-between gap-2 px-0 lg:px-2 rounded-xl text-[#718A9A] hover:bg-[#E9F5FC] hover:text-[#0874B9] transition-colors"
          >
            <span className="hidden lg:block text-[9px] font-semibold uppercase tracking-[0.16em]">{group.label}</span>
            <span className="lg:hidden"><Layers size={18} /></span>
            <ChevronDown size={14} className={`transition-transform ${moQuanLy ? "rotate-180" : ""}`} />
          </button>
          {moQuanLy && <nav aria-label={group.label} className="flex flex-col gap-1 w-full mt-1">{group.items.map(renderLeftNavItem)}</nav>}
        </section>
      ))}

      <div className="flex-1" />

      <section aria-label="Thông tin về MediTrace" className="hidden lg:block mb-3 rounded-2xl border border-[#D5EAF6] bg-white/80 p-3.5 shadow-[0_8px_22px_rgba(30,111,158,0.06)]">
        <div className="mb-2.5 flex h-9 w-9 items-center justify-center rounded-xl bg-[#E5F4FF] text-[#087FC1]">
          <Stethoscope size={19} strokeWidth={1.8} />
        </div>
        <p className="text-[14px] font-bold leading-snug tracking-tight text-[#0C4A6E]">
          AI hỗ trợ, bác sĩ duyệt
        </p>
        <p className="mt-1 text-[11px] leading-relaxed text-[#648096]">
          Ghi chú có căn cứ từ hội thoại.
        </p>
      </section>

      <div className="w-full border-t border-[#DCECF5] pt-2.5 flex flex-col lg:flex-row items-center lg:justify-between gap-1 text-[#49667B]">
        {onTogglePosition && (
          <button
            onClick={onTogglePosition}
            className="h-9 w-9 lg:w-auto lg:px-2 rounded-lg flex items-center justify-center lg:justify-start gap-2 hover:bg-[#E6F4FC] hover:text-[#0874B9] transition-colors"
            title="Chuyển thanh điều hướng lên trên"
          >
            <PanelTop size={16} />
            <span className="hidden lg:inline text-[11px]">Thanh trên</span>
          </button>
        )}
      </div>
    </aside>
  );
};
