import React from "react";
import { DocumentTabItem } from "../types";
import { Mic, FileText, Edit3, Sparkles, Plus, X } from "lucide-react";

interface DocumentTabsProps {
  tabs: DocumentTabItem[];
  activeTabId: string;
  onSelectTab: (id: string) => void;
  onCloseTab: (id: string) => void;
  onOpenTemplateModal: () => void;
}

export const DocumentTabs: React.FC<DocumentTabsProps> = ({
  tabs,
  activeTabId,
  onSelectTab,
  onCloseTab,
  onOpenTemplateModal,
}) => {
  const getTabIcon = (tab: DocumentTabItem) => {
    switch (tab.type) {
      case "transcript":
        return <Mic size={14} className="text-[#964B00]" />;
      case "context":
        return <FileText size={14} className="text-[#6D655E]" />;
      case "soap":
        return <Edit3 size={14} className="text-[#6D655E]" />;
      case "leaflet":
      case "custom":
      default:
        return <Sparkles size={14} className="text-[#0284C7]" />;
    }
  };

  return (
    <div
      id="document-tabs-bar"
      className="flex items-center gap-1.5 px-3 sm:px-4 pt-2 border-b border-[#CCE3F0] bg-[#F0F7FA] overflow-x-auto select-none no-scrollbar"
    >
      {tabs.map((tab) => {
        const isActive = tab.id === activeTabId;
        return (
          <div
            key={tab.id}
            onClick={() => onSelectTab(tab.id)}
            className={`group flex items-center gap-2 px-3.5 py-2 rounded-t-xl text-xs font-medium cursor-pointer transition-all border-t border-x ${
              isActive
                ? "bg-white text-[#0C4A6E] border-[#BAE6FD] border-b-white -mb-[1px] shadow-[0_-3px_8px_rgba(2,132,199,0.08),0_1px_2px_rgba(0,0,0,0.02)] font-semibold relative z-10"
                : "text-[#64748B] border-transparent hover:bg-white/70 hover:text-[#0C4A6E]"
            }`}
          >
            <span className="flex-shrink-0">{getTabIcon(tab)}</span>
            <span className="truncate max-w-[220px]">{tab.title}</span>

            {/* Nút đóng tab nếu cho phép */}
            {tab.isClosable && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onCloseTab(tab.id);
                }}
                className="p-0.5 rounded-full hover:bg-[#E0F2FE] text-[#94A3B8] hover:text-[#0284C7] transition-colors ml-1"
                title="Đóng tab này"
              >
                <X size={12} />
              </button>
            )}
          </div>
        );
      })}

      {/* Nút Thêm Tab (+) */}
      <button
        id="btn-add-tab"
        onClick={onOpenTemplateModal}
        className="p-1.5 rounded-lg text-[#0369A1] hover:bg-white hover:text-[#0284C7] hover:shadow-tactile-doctor-pill transition-all ml-1"
        title="Thêm mẫu bệnh án hoặc văn bản mới"
      >
        <Plus size={15} />
      </button>
    </div>
  );
};
