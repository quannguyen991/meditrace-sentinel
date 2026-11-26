import React, { Suspense, useState, useEffect, useMemo, useRef } from "react";
import { ViewMode, Session, DocumentTabItem, ClinicalChatMessage, TemplateItem, Patient } from "./types";
import { chuyenKetQuaThanhTin, gonMenhDeGui, hoiTroLy } from "./lib/troLy";
import { RefreshCw, Sparkles, Bell, CheckCircle2, Loader2 } from "lucide-react";
import { NavigationRail } from "./components/NavigationRail";
import { MenuTaiKhoan } from "./components/MenuTaiKhoan";
import { HomeDashboard } from "./components/HomeDashboard";
import { SessionsSidebar } from "./components/SessionsSidebar";
import { ScribeHeader } from "./components/ScribeHeader";
import { DocumentTabs } from "./components/DocumentTabs";
import { TranscriptView } from "./components/TranscriptView";
import { NoteEditorView } from "./components/NoteEditorView";
import type { HoSoDD } from "./components/ToDanDoBenhNhanModal";
import { ContextView } from "./components/ContextView";
import { BottomPromptBar } from "./components/BottomPromptBar";
import { ClinicalEvidenceDrawer, CheDoHoi, NguonBat } from "./components/ClinicalEvidenceDrawer";
import { TaoVanBanModal } from "./components/TaoVanBanModal";
import type { MauVanBan } from "./lib/mauVanBan";
import type { CheDoHoiDap, NguonTraCuu, TraLoiHoiDap } from "./components/EvidenceView";
import type { NoteMeta, Quyet } from "./components/VerificationView";
import { DuyetBenCanh, trangThaiMD } from "./components/DuyetBenCanh";
import { TinhTrangHeThong } from "./components/TinhTrangHeThong";
import { ErrorBoundary } from "./components/ErrorBoundary";
import type { NguoiDung } from "./lib/taiKhoan";
import { cacNguoiNoiChuaGan } from "./lib/nguoiNoi";
import { trichNguCanhChoTroLy, xayNguCanhChoTaoHoSo } from "./lib/nguCanhTroLy";
import { phatHienMauThuanXuyenLanKham } from "./lib/doiChieuLanKham";
import { computeNoteSignOffHash, kiemTraDieuKienKyDuyet } from "./lib/compileEffectiveNote";
import { chonTabBenhAnDeBam, khoaDuyetCuaNote } from "./lib/kyDuyet";
import { bienDichBieuMauPhapLyTaiCho } from "./lib/bieuMauPhapLyOffline";
import { taoDaiTomTatTruocKham } from "./lib/trichNhiemVuVaTomTat";
import { useSessionsStore } from "./hooks/useSessionsStore";

const VerificationView = React.lazy(() =>
  import("./components/VerificationView").then((m) => ({ default: m.VerificationView })),
);
const EvidenceView = React.lazy(() =>
  import("./components/EvidenceView").then((m) => ({ default: m.EvidenceView })),
);
const PatientsView = React.lazy(() =>
  import("./components/PatientsView").then((m) => ({ default: m.PatientsView })),
);
const TasksView = React.lazy(() =>
  import("./components/TasksView").then((m) => ({ default: m.TasksView })),
);
const TemplatesView = React.lazy(() =>
  import("./components/TemplatesView").then((m) => ({ default: m.TemplatesView })),
);
const ThuVienYKhoa = React.lazy(() =>
  import("./components/ThuVienYKhoa").then((m) => ({ default: m.ThuVienYKhoa })),
);
const HospitalCommandCenterView = React.lazy(() =>
  import("./components/HospitalCommandCenterView").then((m) => ({ default: m.HospitalCommandCenterView })),
);

const KhungDangTaiManHinh: React.FC = () => (
  <div
    className="flex-1 flex items-center justify-center bg-[#F8FBFC] text-[#0369A1] gap-2 text-xs font-semibold"
    aria-label="Đang tải màn hình"
  >
    <Loader2 size={16} className="animate-spin text-[#0284C7]" />
    <span>Đang mở phân hệ lâm sàng…</span>
  </div>
);

type AppProps = { nguoiDung: NguoiDung; onDangXuat: () => Promise<void> };

export default function App({ nguoiDung, onDangXuat }: AppProps) {
  const [activeView, setActiveView] = useState<ViewMode>("scribe");
  const [activeNavigationItem, setActiveNavigationItem] = useState("sessions");
  const [taskbarPosition, setTaskbarPosition] = useState<"top" | "left">(() => {
    try {
      const saved = localStorage.getItem("meditrace_taskbar_position");
      return saved === "top" || saved === "left" ? saved : "left";
    } catch {
      return "left";
    }
  });
  useEffect(() => {
    try {
      localStorage.setItem("meditrace_taskbar_position", taskbarPosition);
    } catch {}
  }, [taskbarPosition]);
  const { sessions, setSessions, activeSessionId, setActiveSessionId, luuMotCaNgay } = useSessionsStore();

  // Quản lý thu gọn thanh bên thông minh theo kích thước màn hình Tablet
  const [isSessionsSidebarCollapsed, setIsSessionsSidebarCollapsed] = useState(() => {
    if (typeof window !== "undefined") {
      return window.innerWidth < 1200;
    }
    return false;
  });

  const [isRightDrawerOpen, setIsRightDrawerOpen] = useState(() => {
    if (typeof window !== "undefined") {
      return window.innerWidth >= 1536;
    }
    return false;
  });

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 1200) {
        setIsSessionsSidebarCollapsed(true);
      }
      if (window.innerWidth < 1024) {
        setIsRightDrawerOpen(false);
      }
    };
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const handleToggleSessionsSidebar = () => {
    const willExpand = isSessionsSidebarCollapsed;
    setIsSessionsSidebarCollapsed(!isSessionsSidebarCollapsed);
    if (willExpand && typeof window !== "undefined" && window.innerWidth < 1100 && isRightDrawerOpen) {
      setIsRightDrawerOpen(false);
    }
  };

  const handleToggleRightDrawer = () => {
    const willOpen = !isRightDrawerOpen;
    setIsRightDrawerOpen(willOpen);
    if (willOpen && typeof window !== "undefined" && window.innerWidth < 1200 && !isSessionsSidebarCollapsed) {
      setIsSessionsSidebarCollapsed(true);
    }
  };

  const [isTemplateModalOpen, setIsTemplateModalOpen] = useState(false);
  const [moTinhTrang, setMoTinhTrang] = useState(false);
  const [promptTraCuuTrangChu, setPromptTraCuuTrangChu] = useState("");
  /** Lưu tờ dặn dò theo `sessionId` ở tầng App để đổi tab (Lời thoại/Ngữ cảnh/SOAP) hoặc chuyển ca không mất bản sửa, vẫn xoá sạch khi đổi người dùng (`<App key={nguoiDung.id}>`). */
  const [hoSoDanDoTheoCa, setHoSoDanDoTheoCa] = useState<Record<string, HoSoDD>>({});

  const [isEvidenceLoading, setIsEvidenceLoading] = useState(false);
  /** Kế hoạch + bước của việc trợ lý đang chạy, để ngăn phải vẽ thẻ tiến độ thật. */
  const [tienDoTroLy, setTienDoTroLy] = useState<any | null>(null);
  /** Gắn theo mã ca đang tạo AI: Ca A đang chạy không khoá trắng Ca B khi bác sĩ chuyển ca! */
  const [generatingSessionId, setGeneratingSessionId] = useState<string | null>(null);
  /** Việc tạo bản nháp đang chạy nền trên máy chủ: lúc bắt đầu, số việc xếp trước. */
  const [tienDoNhap, setTienDoNhap] = useState<{ batDau: number; truoc: number } | null>(null);
  const [, setNhip] = useState(0);
  useEffect(() => {
    if (!tienDoNhap) return;
    const t = setInterval(() => setNhip((n) => n + 1), 1000);
    return () => clearInterval(t);
  }, [tienDoNhap]);

  // Lỗi của dịch vụ hiện thẳng lên giao diện; không nuốt vào console.
  const [apiError, setApiError] = useState<string | null>(null);

  /**
   * Công tắc gửi ra mô hình ngoài (cổng mô hình ngoài). MẶC ĐỊNH TẮT, nhớ theo từng trình duyệt.
   * Bật thì nội dung ca khám được gửi ra máy chủ ngoài cho ba việc phụ: sửa theo lời nhắc,
   * hỏi về ca khám, bản so sánh. Bản nháp chính vẫn luôn do mô hình tại chỗ viết.
   */
  const [choPhepNgoai, setChoPhepNgoai] = useState<boolean>(() => {
    try {
      return localStorage.getItem("meditrace_cho_phep_ngoai") === "1";
    } catch {
      return false;
    }
  });
  useEffect(() => {
    try {
      localStorage.setItem("meditrace_cho_phep_ngoai", choPhepNgoai ? "1" : "0");
    } catch {}
  }, [choPhepNgoai]);

  // Ca khám đang hoạt động
  const currentSession = sessions.find((s) => s.id === activeSessionId) || sessions[0];
  const isCurrentSessionGenerating = Boolean(currentSession && generatingSessionId === currentSession.id);
  const isOtherSessionGenerating = Boolean(generatingSessionId && generatingSessionId !== currentSession?.id);

  // Tab tài liệu đang xem trong ca khám
  const currentTab =
    currentSession?.tabs.find((t) => t.id === currentSession.activeTabId) || currentSession?.tabs[0];

  /** Cập nhật ca khám theo `targetId` bằng updater hàm để chống triệt để stale closure sau `await`. */
  const capNhatCaTheoId = (
    targetId: string,
    capNhat: Partial<Session> | ((ca: Session) => Partial<Session>),
  ) => {
    setSessions((prev) =>
      prev.map((s) => {
        if (s.id !== targetId) return s;
        const thayDoi = typeof capNhat === "function" ? capNhat(s) : capNhat;
        return { ...s, ...thayDoi };
      }),
    );
  };

  // Cập nhật thông tin ca khám (mặc định là ca đang mở, hoặc ca chỉ định rõ `targetSessionId`)
  const handleUpdateSession = (updatedFields: Partial<Session>, targetSessionId?: string) => {
    const id = targetSessionId || currentSession.id;
    capNhatCaTheoId(id, updatedFields);
  };

  /** Gọi một đường cần mô hình ngoài; tự gắn cờ cho phép và báo lỗi lên giao diện. */
  const goiNgoai = async (duong: string, than: Record<string, unknown>) => {
    if (!choPhepNgoai) {
      setApiError("Việc này cần mô hình ngoài. Bật công tắc “Mô hình ngoài” ở đầu khung soạn trước.");
      return null;
    }
    setApiError(null);
    const res = await fetch(duong, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...than, allowExternal: true }),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      setApiError(data?.error || `Cổng ngoài trả mã ${res.status}`);
      return null;
    }
    return data;
  };

  /**
   * Gọi dịch vụ MediTrace chạy tại chỗ để dựng bản nháp.
   * Chụp `targetId` và dữ liệu Ngữ cảnh (`ContextView` + `patientSubtitle`) TRƯỚC `await`
   * để dù chờ 3–4 phút bác sĩ đã chuyển ca khác thì kết quả vẫn vào đúng ca gốc!
   */
  const taoHoSo = async (than: Record<string, unknown>, targetSessionId?: string): Promise<NoteMeta | null> => {
    const targetId = targetSessionId || currentSession.id;
    const caMucTieu = sessions.find((s) => s.id === targetId) || currentSession;

    const loiThoai = typeof than.transcript === "string" ? than.transcript : "";
    if (loiThoai) {
      const dong = loiThoai.split("\n").filter((l) => l.trim());
      const chuaRo = dong.filter((l) => !/^\s*(bác sĩ|bệnh nhân|người nhà)\s*:/i.test(l)).length;
      if (chuaRo) {
        const soNguoiNoi = cacNguoiNoiChuaGan(loiThoai).length;
        setApiError(
          `Còn ${chuaRo} lượt chưa gán vai. ` +
            (soNguoiNoi
              ? `Ở tab Lời thoại, ô “Gán vai theo người nói” còn ${soNguoiNoi} người nói chưa chọn vai; ` +
                "lượt lẻ thì bấm nhãn tròn bên trái lượt đó, rồi tạo bản nháp."
              : "Ở tab Lời thoại, bấm vào nhãn tròn bên trái mỗi lượt để chọn " +
                "Bác sĩ / Bệnh nhân / Người nhà, rồi tạo bản nháp."),
        );
        return null;
      }
    }

    const nguCanhPayload = than.sampleCaseId
      ? {}
      : xayNguCanhChoTaoHoSo({
          sessionId: caMucTieu.id,
          patientIdentifier: caMucTieu.patientIdentifier,
          patientSubtitle: caMucTieu.patientSubtitle,
          tabs: caMucTieu.tabs,
          contextNotes: caMucTieu.contextNotes,
        });

    setGeneratingSessionId(targetId);
    setApiError(null);
    try {
      let res = await fetch("/api/generate-note", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ branch: "C_khoa_hoi", ...nguCanhPayload, ...than }),
      });
      let data = await res.json();
      while (res.status === 202 && data?.jobId) {
        setTienDoNhap({ batDau: data.startedAt || Date.now(), truoc: data.queued || 0 });
        await new Promise((r) => setTimeout(r, 4000));
        res = await fetch(`/api/generate-note/${data.jobId}`);
        data = await res.json();
      }
      if (!res.ok) throw new Error(data?.error || `Dịch vụ trả mã ${res.status}`);
      const meta: NoteMeta = data;
      capNhatCaTheoId(targetId, { note: meta });
      return meta;
    } catch (err: any) {
      setApiError(err?.message || "Không gọi được dịch vụ MediTrace");
      return null;
    } finally {
      setGeneratingSessionId((cur) => (cur === targetId ? null : cur));
      setTienDoNhap(null);
    }
  };

  // Bản nháp và hỏi đáp gắn với TỪNG CA
  const noteMeta: NoteMeta | null = currentSession?.note
    ? {
        ...currentSession.note,
        transcript: currentSession.note.transcript || currentSession.transcript,
      }
    : null;
  const evidenceChat: ClinicalChatMessage[] = currentSession?.evidenceChat || [];

  // Duyệt mệnh đề: lưu cùng ca theo khoá nội dung bản nháp
  const khoaDuyet = noteMeta ? khoaDuyetCuaNote(noteMeta) : "";
  const duyetLuu = currentSession?.duyet?.khoa === khoaDuyet ? currentSession.duyet : undefined;
  const quyetDuyet: Record<number, Quyet> = duyetLuu?.quyet || {};
  const banSuaDuyet: Record<number, string> = duyetLuu?.banSua || {};

  const capNhatDuyet = (phan: "quyet" | "banSua", u: React.SetStateAction<Record<number, any>>) => {
    const idCa = currentSession.id;
    const khoa = khoaDuyet;
    setSessions((prev) =>
      prev.map((s) => {
        if (s.id !== idCa) return s;
        const cu = s.duyet?.khoa === khoa ? s.duyet : { khoa, quyet: {}, banSua: {} };
        const moi = typeof u === "function" ? (u as (x: Record<number, any>) => Record<number, any>)(cu[phan]) : u;
        return { ...s, duyet: { ...cu, [phan]: moi } };
      }),
    );
  };
  const setQuyetDuyet: React.Dispatch<React.SetStateAction<Record<number, Quyet>>> = (u) => capNhatDuyet("quyet", u);
  const setBanSuaDuyet: React.Dispatch<React.SetStateAction<Record<number, string>>> = (u) => capNhatDuyet("banSua", u);
  const [, setMoDuyetBen] = useState(false);
  const [chonMD, setChonMD] = useState<number | null>(null);
  const [moDuyetBenCanh, setMoDuyetBenCanh] = useState(true);
  const [luotKiemChung, setLuotKiemChung] = useState<number | null>(null);
  const chonBanDau = useMemo(
    () =>
      chonMD
        ? { loai: "p" as const, id: chonMD }
        : luotKiemChung
        ? { loai: "t" as const, so: luotKiemChung }
        : undefined,
    [chonMD, luotKiemChung],
  );

  const handleKiemChungLuot = (soLuot: number) => {
    setLuotKiemChung(soLuot);
    handleSelectNavigationItem("proof");
  };
  const vungGiuaRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setChonMD(null);
  }, [currentSession?.id, noteMeta?.content]);

  const capNhatEvidenceChatChoCa = (
    targetId: string,
    u: ClinicalChatMessage[] | ((truoc: ClinicalChatMessage[]) => ClinicalChatMessage[]),
  ) => {
    setSessions((prev) =>
      prev.map((s) =>
        s.id === targetId ? { ...s, evidenceChat: typeof u === "function" ? u(s.evidenceChat || []) : u } : s,
      ),
    );
  };

  // Tạo mới một ca khám
  const handleCreateNewSession = () => {
    const newId = `session-${Date.now()}`;
    const newSession: Session = {
      id: newId,
      patientIdentifier: "Thêm tên định danh bệnh nhân",
      patientSubtitle: "Ca khám bệnh mới",
      date: `Hôm nay ${new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`,
      time: `${new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`,
      language: "Tiếng Việt",
      durationSeconds: 0,
      isRecording: false,
      transcript: "",
      activeTabId: "tab-transcript",
      tabs: [
        {
          id: "tab-transcript",
          title: "Lời thoại",
          type: "transcript",
          content: "",
          isClosable: false,
        },
        {
          id: "tab-context",
          title: "Ngữ cảnh",
          type: "context",
          content: "",
          isClosable: false,
        },
        {
          id: "tab-soap",
          title: "Bệnh án SOAP",
          type: "soap",
          templateStyle: "Goldilocks",
          content: `Lý do vào viện (Chủ quan):\n\nTiền sử bệnh lý & Dị ứng:\n\nKhám lâm sàng (Khách quan):\n\nĐánh giá & Chẩn đoán sơ bộ:\n\nKế hoạch điều trị & Đơn thuốc:`,
          isClosable: false,
        },
      ],
    };

    setSessions((prev) => [newSession, ...prev]);
    setActiveSessionId(newId);
    setActiveView("scribe");
    setActiveNavigationItem("sessions");
  };

  // Xóa ca khám
  const handleDeleteSession = (idToDelete?: string) => {
    const targetId = idToDelete || currentSession.id;
    if (sessions.length <= 1) {
      alert("Cần giữ lại ít nhất một ca khám trong không gian làm việc.");
      return;
    }
    setHoSoDanDoTheoCa((cu) => {
      if (!(targetId in cu)) return cu;
      const { [targetId]: _bo, ...conLai } = cu;
      return conLai;
    });
    setSessions((prev) => {
      if (prev.length <= 1) return prev;
      const remaining = prev.filter((s) => s.id !== targetId);
      if (activeSessionId === targetId && remaining[0]) {
        setActiveSessionId(remaining[0].id);
      }
      return remaining;
    });
  };

  // Chuyển tab trong ca khám
  const handleSelectTab = (tabId: string) => {
    capNhatCaTheoId(currentSession.id, { activeTabId: tabId });
  };

  const handleSelectView = (view: ViewMode) => {
    const mucTheoView: Record<ViewMode, string> = {
      home: "home",
      scribe: "sessions",
      evidence: "questions",
      tasks: "tasks",
      patients: "patients",
      templates: "templates",
      verification: "proof",
      library: "library",
      settings: "settings",
      command_center: "command_center",
    };
    setActiveView(view);
    setActiveNavigationItem(mucTheoView[view]);
  };

  const handleSelectNavigationItem = (item: string) => {
    setActiveNavigationItem(item);
    if (item === "home") {
      setActiveView("home");
    } else if (item === "command_center") {
      setActiveView("command_center");
    } else if (item === "sessions") {
      setActiveView("scribe");
      setMoDuyetBen(false);
    } else if (item === "transcript") {
      setActiveView("scribe");
      setMoDuyetBen(false);
      const tab = currentSession.tabs.find((t) => t.type === "transcript");
      if (tab) handleSelectTab(tab.id);
    } else if (item === "draft") {
      setActiveView("scribe");
      setMoDuyetBen(false);
      const tab =
        [...currentSession.tabs].reverse().find((t) => noteMeta && t.content === noteMeta.content) ||
        [...currentSession.tabs].reverse().find((t) => t.title === "Bản nháp hồ sơ") ||
        currentSession.tabs.find((t) => t.type === "soap");
      const chonTab = tab || currentSession.tabs.find((t) => t.type === "transcript");
      if (chonTab) handleSelectTab(chonTab.id);
    } else if (item === "proof") {
      setActiveView("verification");
    } else if (item === "questions") {
      setActiveView("evidence");
    } else if (item === "library") {
      setActiveView("library");
    } else if (item === "settings") {
      setActiveView("settings");
    } else if (item === "templates") {
      setActiveView("templates");
    } else if (item === "tasks") {
      setActiveView("tasks");
    } else if (item === "patients") {
      setActiveView("patients");
    }
  };

  // Đóng một tab
  const handleCloseTab = (tabId: string) => {
    const targetId = currentSession.id;
    capNhatCaTheoId(targetId, (ca) => {
      const updatedTabs = ca.tabs.filter((t) => t.id !== tabId);
      const nextActive = ca.activeTabId === tabId ? updatedTabs[0]?.id || "tab-transcript" : ca.activeTabId;
      return { tabs: updatedTabs, activeTabId: nextActive };
    });
  };

  // Cập nhật nội dung tab (đồng bộ luôn `contextNotes` nếu đang sửa tab Ngữ cảnh)
  const handleUpdateTabContent = (newContent: string) => {
    const targetId = currentSession.id;
    const targetTabId = currentTab.id;
    const laTabNguCanh = currentTab.type === "context";
    capNhatCaTheoId(targetId, (ca) => ({
      ...(laTabNguCanh ? { contextNotes: newContent } : {}),
      tabs: ca.tabs.map((t) => (t.id === targetTabId ? { ...t, content: newContent } : t)),
    }));
  };

  // In bệnh án A4 từ bất kỳ tab nào (nếu đang đứng ở Lời thoại / Ngữ cảnh thì tự chuyển sang tab Bệnh án trước khi in)
  const handlePrintClinicalNote = () => {
    if (
      currentTab &&
      (currentTab.type === "soap" || currentTab.type === "custom" || currentTab.type === "leaflet")
    ) {
      window.print();
      return;
    }
    const targetId = currentSession.id;
    const tabBenhAn =
      [...currentSession.tabs].reverse().find((t) => noteMeta && t.content === noteMeta.content) ||
      [...currentSession.tabs].reverse().find((t) => t.title === "Bản nháp hồ sơ") ||
      currentSession.tabs.find((t) => t.type === "soap");
    if (tabBenhAn) {
      capNhatCaTheoId(targetId, { activeTabId: tabBenhAn.id });
    } else {
      const soapId = "tab-soap";
      capNhatCaTheoId(targetId, (ca) => ({
        tabs: [
          ...ca.tabs,
          {
            id: soapId,
            title: "Bệnh án SOAP",
            type: "soap",
            templateStyle: "Goldilocks",
            content:
              noteMeta?.content ||
              "Lý do vào viện (Chủ quan):\n\nTiền sử bệnh lý & Dị ứng:\n\nKhám lâm sàng (Khách quan):\n\nĐánh giá & Chẩn đoán sơ bộ:\n\nKế hoạch điều trị & Đơn thuốc:",
            isClosable: false,
          },
        ],
        activeTabId: soapId,
      }));
    }
    setTimeout(() => window.print(), 60);
  };

  // Cập nhật lời thoại
  const handleUpdateTranscript = (newTranscript: string) => {
    const targetId = currentSession.id;
    capNhatCaTheoId(targetId, (ca) => ({
      transcript: newTranscript,
      tabs: ca.tabs.map((t) => (t.type === "transcript" ? { ...t, content: newTranscript } : t)),
    }));
  };

  // Màn "Mẫu bệnh án" → soạn theo mẫu đó
  const handleSelectTemplate = async (template: TemplateItem, _customPrompt?: string) => {
    await taoVanBan({
      id: template.id,
      ten: template.title,
      nhom: "ho_so",
      chiDan: template.promptDescription || `Soạn "${template.title}" cho ca này.`,
    });
  };

  // Dựng lại bản nháp từ lời thoại hiện tại (chống stale closure)
  const handleRegenerateNoteStyle = async (_newStyle: string) => {
    const targetId = currentSession.id;
    const targetTabId = currentTab.id;
    const transcriptSnapshot = currentSession.transcript;
    const meta = await taoHoSo({ transcript: transcriptSnapshot }, targetId);
    if (!meta) return;
    capNhatCaTheoId(targetId, (ca) => ({
      tabs: ca.tabs.map((t) => (t.id === targetTabId ? { ...t, content: meta.content } : t)),
    }));
  };

  /**
   * Thanh lệnh dưới cùng (chụp `targetId` & `targetTabId` trước `await`).
   */
  const handleBottomPrompt = async (promptText: string) => {
    const targetId = currentSession.id;
    const targetTabId = currentTab.id;
    const targetTabType = currentTab.type;
    const currentContentSnapshot = currentTab.content;
    const transcriptSnapshot = currentSession.transcript;

    if (targetTabType === "soap" || targetTabType === "leaflet" || targetTabType === "custom") {
      if (!choPhepNgoai) {
        setApiError(
          "Sửa theo lời nhắc cần mô hình ngoài (bật công tắc “Mô hình ngoài”). Không bật thì sửa " +
            "trực tiếp trong ô soạn thảo, hoặc mở màn Duyệt để giữ, sửa, bỏ từng mệnh đề.",
        );
        return;
      }
      setGeneratingSessionId(targetId);
      try {
        const d = await goiNgoai("/api/edit-note", {
          currentContent: currentContentSnapshot,
          instruction: promptText,
          transcript: transcriptSnapshot,
        });
        if (d?.updatedContent) {
          const noiDungMoi = `${d.updatedContent}\n\n[Đã sửa bằng mô hình ngoài · ${d.model} · chưa qua kiểm căn cứ · theo lời nhắc: ${promptText}]`;
          capNhatCaTheoId(targetId, (ca) => ({
            tabs: ca.tabs.map((t) => (t.id === targetTabId ? { ...t, content: noiDungMoi } : t)),
          }));
        }
      } finally {
        setGeneratingSessionId((cur) => (cur === targetId ? null : cur));
      }
      return;
    }

    const meta = await taoHoSo({ transcript: transcriptSnapshot }, targetId);
    if (!meta) return;
    const newTabId = `tab-doc-${Date.now()}`;
    const newTab: DocumentTabItem = {
      id: newTabId,
      title: promptText || "Bản nháp hồ sơ",
      type: "custom",
      content: meta.content,
      isClosable: true,
    };
    capNhatCaTheoId(targetId, (ca) => ({
      tabs: [...ca.tabs, newTab],
      activeTabId: newTabId,
    }));
  };

  /**
   * Nạp một ca ĐÃ CHẠY TRƯỚC từ dịch vụ tại chỗ (chụp `targetId` trước `await`, xoay vòng qua các ca demo BGK).
   */
  const chiSoCaMauRef = useRef(0);
  const handleLoadSample = async () => {
    const targetId = currentSession.id;
    setApiError(null);
    try {
      const res = await fetch("/api/sample-cases");
      const data = await res.json();
      if (!res.ok) throw new Error(data?.error || `Dich vu tra ma ${res.status}`);
      const ds = data.ca || [];
      if (!ds.length) throw new Error("Dich vu khong co ca nao da chay truoc");
      const uuTienDemo = ds.filter((x: any) => x?.bo === "demo_bgk");
      const nguonChon = uuTienDemo.length > 0 ? uuTienDemo : ds;
      const ca = nguonChon[chiSoCaMauRef.current % nguonChon.length];
      chiSoCaMauRef.current += 1;
      const meta = await taoHoSo({ sampleCaseId: ca.id }, targetId);
      if (!meta) return;
      const tabId = `tab-doc-${Date.now()}`;
      capNhatCaTheoId(targetId, (phien) => ({
        patientIdentifier: ca.ten || `Ca ${ca.id}`,
        patientSubtitle: `Dữ liệu tổng hợp của dự án · bộ ${ca.bo}`,
        transcript: meta.transcript || "",
        duyet: undefined,
        signOff: undefined,
        tabs: [
          ...phien.tabs
            .filter((t) => t.title !== "Bản nháp hồ sơ")
            .map((t) => (t.type === "transcript" ? { ...t, content: meta.transcript || "" } : t)),
          { id: tabId, title: "Bản nháp hồ sơ", type: "custom", content: meta.content, isClosable: true },
        ],
        activeTabId: tabId,
      }));
    } catch (err: any) {
      setApiError(err?.message || "Khong nap duoc ca mau");
    }
  };

  /** Nội dung tab Ngữ cảnh của ca đang mở. */
  const nguCanh = (ca: Session = currentSession) => ca.tabs.find((t) => t.type === "context")?.content || "";

  /** Chép một câu hỏi vào cuối tab Ngữ cảnh (dùng updater hàm). */
  const themVaoNguCanh = (cau: string) => {
    const targetId = currentSession.id;
    capNhatCaTheoId(targetId, (ca) => {
      const cu = nguCanh(ca).trimEnd();
      const moi = cu ? `${cu}\n- ${cau}` : `Câu hỏi cần hỏi thêm:\n- ${cau}`;
      return {
        contextNotes: moi,
        tabs: ca.tabs.map((t) => (t.type === "context" ? { ...t, content: moi } : t)),
      };
    });
  };

  /** Phương án 1: mô hình ngoài đọc ngữ cảnh + lời thoại + mệnh đề đã tách, đề xuất câu hỏi. */
  const deXuatCauHoi = async () => {
    const contextSnapshot = nguCanh();
    const transcriptSnapshot = noteMeta?.transcript || currentSession.transcript;
    const propsSnapshot = noteMeta?.propositions || [];
    const d = await goiNgoai("/api/questions-external", {
      context: contextSnapshot,
      transcript: transcriptSnapshot,
      propositions: propsSnapshot,
    });
    return d ? { questions: d.questions || [], model: d.model, seconds: d.seconds } : null;
  };

  /**
   * Nút "Tạo". Chụp `targetId` và toàn bộ ngữ cảnh ca khám trước `await`.
   */
  const taoVanBan = async (mau: MauVanBan, yeuCau?: string) => {
    const targetId = currentSession.id;
    const transcriptSnapshot = noteMeta?.transcript || currentSession.transcript;
    const draftSnapshot = noteMeta?.content || "";
    const contextSnapshot = nguCanh();

    if (mau.taiCho) {
      const meta = await taoHoSo({ transcript: currentSession.transcript }, targetId);
      if (!meta) return;
      const id = `tab-doc-${Date.now()}`;
      capNhatCaTheoId(targetId, (ca) => ({
        tabs: [
          ...ca.tabs,
          { id, title: "Bản nháp hồ sơ", type: "custom", content: meta.content, isClosable: true },
        ],
        activeTabId: id,
      }));
      return;
    }

    if (mau.bienDichLuatTaiCho) {
      const noiDungOffline = bienDichBieuMauPhapLyTaiCho(mau.id, {
        session: currentSession,
        note: noteMeta,
        quyetDuyet,
        banSuaDuyet,
      });
      if (noiDungOffline) {
        const id = `tab-doc-${Date.now()}`;
        const nhanOffline =
          "\n\n---\n[Biên dịch bằng luật xác định tại chỗ · 100% offline · không gửi dữ liệu ra ngoài · giữ nguyên mỏ neo [T_i] và chỗ trống [cần bổ sung].]";
        capNhatCaTheoId(targetId, (ca) => ({
          tabs: [
            ...ca.tabs,
            {
              id,
              title: mau.ten.slice(0, 60),
              type: "custom",
              content: `${noiDungOffline}${nhanOffline}`,
              isClosable: true,
            },
          ],
          activeTabId: id,
        }));
        return;
      }
    }

    setGeneratingSessionId(targetId);
    try {
      const d = await goiNgoai("/api/generate-document", {
        title: yeuCau ? "" : mau.ten,
        instruction: yeuCau || mau.chiDan,
        transcript: transcriptSnapshot,
        draft: draftSnapshot,
        context: contextSnapshot,
      });
      if (!d?.content) return;
      const id = `tab-doc-${Date.now()}`;
      const nhan =
        `\n\n---\n[Soạn bằng mô hình ngoài · ${d.model} · ${d.seconds}s · chưa qua kiểm căn cứ · từ lời thoại, bản nháp và tab Ngữ cảnh` +
        `${d.missingCount ? ` · còn ${d.missingCount} chỗ [cần bổ sung]` : ""}. Bác sĩ đọc lại trước khi dùng.]`;
      const tab: DocumentTabItem = {
        id,
        title: (yeuCau || mau.ten).slice(0, 60),
        type: "custom",
        content: `${d.content}${nhan}`,
        isClosable: true,
      };
      capNhatCaTheoId(targetId, (ca) => ({
        tabs: [...ca.tabs, tab],
        activeTabId: id,
      }));
    } finally {
      setGeneratingSessionId((cur) => (cur === targetId ? null : cur));
    }
  };

  /** Màn "Hỏi về ca khám": đồng nhất xử lý chặn `cau_hoi_co_danh_tinh` và truyền `tienTrinh` kiểm căn cứ thật. */
  const hoiDap = async (
    cheDo: CheDoHoiDap,
    cauHoi: string,
    tuyChon: { kemNguCanh: boolean; nguon: NguonTraCuu },
  ): Promise<TraLoiHoiDap | null> => {
    const subtitleSnapshot = currentSession.patientSubtitle;
    const contextSnapshot = nguCanh();
    const transcriptSnapshot = currentSession.transcript;
    const draftSnapshot = noteMeta?.content || "";
    const propsSnapshot = noteMeta?.propositions;

    if (cheDo === "de_xuat") {
      const d = await deXuatCauHoi();
      if (!d) return null;
      return {
        content: d.questions.length
          ? d.questions
              .map(
                (q: any, i: number) =>
                  `${i + 1}. **${q.hoi}**${q.goi_y ? ` — ${q.goi_y}` : ""}${q.vi_sao ? `\n   _${q.vi_sao}_` : ""}` +
                  `${q.luot?.length ? ` (lượt ${q.luot.join(", ")})` : ""}`,
              )
              .join("\n")
          : "Mô hình không đề xuất câu nào.",
        meta: `Mô hình ngoài · ${d.model} · ${d.seconds}s · chưa qua kiểm căn cứ · từ ngữ cảnh, lời thoại và mệnh đề đã tách`,
      };
    }
    if (cheDo === "tra_cuu") {
      const cauHoiGoc = cauHoi.replace(/\s*\(tra nguồn khác\)$/, "");
      const nguCanhThat = tuyChon.kemNguCanh
        ? trichNguCanhChoTroLy({
            patientSubtitle: subtitleSnapshot,
            contextNotes: contextSnapshot,
            propositions: propsSnapshot,
          })
        : { tuoi: undefined, gioi: undefined, coThai: undefined };
      const kq = await hoiTroLy(
        {
          cauHoi: cauHoiGoc,
          menhDe: tuyChon.kemNguCanh ? gonMenhDeGui(propsSnapshot) : [],
          nguCanh: nguCanhThat,
          nguon: tuyChon.nguon,
        },
        (tt) => setTienDoTroLy(tt),
      );
      setTienDoTroLy(null);
      if ("loi" in kq) {
        setApiError(kq.loi);
        if (kq.code === "cau_hoi_co_danh_tinh") {
          return { content: "", blockedIdentity: true, errorMessage: kq.loi };
        }
        return null;
      }
      const tin = chuyenKetQuaThanhTin(kq.ketQua, cauHoiGoc, {
        source: kq.source,
        model: kq.model,
        tienTrinh: kq.tienTrinh,
      });
      return {
        content: tin.content || "",
        sources: tin.sources || [],
        warning: tin.warning,
        removedSources: tin.removedSources,
        cauTruc: tin.cauTruc || null,
        question: cauHoiGoc,
        meta: tin.meta || "Trợ lý nhiều tác tử (ẩn danh) · tham khảo, bác sĩ quyết định",
      };
    }
    const d = await goiNgoai("/api/clinical-qa", {
      question: cauHoi,
      transcript: transcriptSnapshot,
      draft: draftSnapshot,
    });
    if (!d) return null;
    return {
      content: d.answer,
      meta: `Mô hình ngoài · ${d.model} · ${d.seconds}s · chưa qua kiểm căn cứ · chỉ dựa trên hội thoại của ca này`,
    };
  };

  /** Hỏi đáp ở ngăn phải (chụp `targetId` trước `await`). */
  const handleSendEvidenceMessage = async (query: string, mode: CheDoHoi, nguon?: NguonBat) => {
    const targetId = currentSession.id;
    const subtitleSnapshot = currentSession.patientSubtitle;
    const contextSnapshot = nguCanh();
    const transcriptSnapshot = currentSession.transcript;
    const draftSnapshot = noteMeta?.content || currentTab?.content || "";
    const propsSnapshot = noteMeta?.propositions;

    const gio = () => new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    const userMsgId = `user-${Date.now()}`;
    capNhatEvidenceChatChoCa(targetId, (prev) => [
      ...prev,
      { id: userMsgId, role: "user", content: query, mode, timestamp: gio() },
    ]);
    setIsEvidenceLoading(true);
    try {
      if (mode === "tra_cuu") {
        const cauHoiGoc = query.replace(/\s*\(tra nguồn khác\)$/, "");
        setApiError(null);
        setTienDoTroLy({ keHoach: [], keHoachTuMoHinh: false, buoc: [], xemTruoc: null });
        const nguCanhThat = trichNguCanhChoTroLy({
          patientSubtitle: subtitleSnapshot,
          contextNotes: contextSnapshot,
          propositions: propsSnapshot,
        });
        const kq = await hoiTroLy(
          {
            cauHoi: cauHoiGoc,
            menhDe: gonMenhDeGui(propsSnapshot),
            nguCanh: nguCanhThat,
            ...(nguon ? { nguon } : {}),
          },
          (tt) => setTienDoTroLy(tt),
        );
        if ("loi" in kq) {
          if (kq.code === "cau_hoi_co_danh_tinh") {
            capNhatEvidenceChatChoCa(targetId, (prev) => prev.filter((m) => m.id !== userMsgId));
          }
          setApiError(kq.loi);
          return;
        }
        capNhatEvidenceChatChoCa(targetId, (prev) => [
          ...prev,
          {
            id: `asst-${Date.now()}`,
            role: "assistant",
            mode,
            timestamp: gio(),
            ...chuyenKetQuaThanhTin(kq.ketQua, cauHoiGoc, {
              source: kq.source,
              model: kq.model,
              tienTrinh: kq.tienTrinh,
            }),
          } as ClinicalChatMessage,
        ]);
        return;
      }
      const d = await goiNgoai("/api/clinical-qa", {
        question: query,
        transcript: transcriptSnapshot,
        draft: draftSnapshot,
      });
      if (d) {
        capNhatEvidenceChatChoCa(targetId, (prev) => [
          ...prev,
          {
            id: `asst-${Date.now()}`,
            role: "assistant",
            mode,
            content: d.answer,
            meta: `Mô hình ngoài · ${d.model} · ${d.seconds}s · chưa qua kiểm căn cứ · chỉ dựa trên hội thoại của ca này`,
            timestamp: gio(),
          },
        ]);
      }
    } finally {
      setIsEvidenceLoading(false);
      setTienDoTroLy(null);
    }
  };

  /** Bản so sánh: mô hình ngoài viết từ cùng lời thoại (chụp `targetId` trước `await`). */
  const taoBanSoSanhNgoai = async () => {
    const targetId = currentSession.id;
    const loiThoai = noteMeta?.transcript || currentSession.transcript;
    if (!loiThoai) {
      setApiError("Chưa có lời thoại để làm bản so sánh.");
      return;
    }
    setGeneratingSessionId(targetId);
    try {
      const d = await goiNgoai("/api/generate-note-external", { transcript: loiThoai });
      if (!d?.content) return;
      const tabId = `tab-doc-${Date.now()}`;
      capNhatCaTheoId(targetId, (ca) => ({
        tabs: [
          ...ca.tabs,
          {
            id: tabId,
            title: `So sánh · ${d.model}`,
            type: "custom",
            content:
              `[BẢN SO SÁNH — mô hình ngoài · ${d.model} · ${d.seconds}s · chưa qua kiểm căn cứ. ` +
              `Không phải bản nháp của dự án: không có mệnh đề, không có lượt làm căn cứ, không qua cổng rủi ro.]\n\n` +
              d.content,
            isClosable: true,
          },
        ],
        activeTabId: tabId,
      }));
    } finally {
      setGeneratingSessionId((cur) => (cur === targetId ? null : cur));
    }
  };

  // Khởi tạo ca khám từ danh sách bệnh nhân: đủ 3 tab (transcript, context, soap), KHÔNG chèn dòng thoại thiếu vai!
  const handleStartSessionWithPatient = (patient: Patient) => {
    const newId = `session-${Date.now()}`;
    const lyDo = patient.chiefComplaint || "Khám sức khỏe tổng quát";
    const dongNguCanh = [
      `Lý do khám ban đầu: ${lyDo}`,
      patient.dob && patient.dob !== "Chưa xác định" ? `Ngày sinh: ${patient.dob}` : "",
      patient.gender ? `Giới tính: ${patient.gender}` : "",
    ]
      .filter(Boolean)
      .join("\n");
    const phuDe = [patient.gender, patient.dob !== "Chưa xác định" ? patient.dob : "", patient.identifier]
      .filter(Boolean)
      .join(" · ");

    const newSession: Session = {
      id: newId,
      patientIdentifier: patient.name,
      patientSubtitle: phuDe || patient.identifier || lyDo,
      date: `Hôm nay ${new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`,
      time: `${new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`,
      language: "Tiếng Việt",
      durationSeconds: 0,
      isRecording: false,
      transcript: "",
      contextNotes: dongNguCanh,
      activeTabId: "tab-transcript",
      tabs: [
        {
          id: "tab-transcript",
          title: "Lời thoại",
          type: "transcript",
          content: "",
          isClosable: false,
        },
        {
          id: "tab-context",
          title: "Ngữ cảnh",
          type: "context",
          content: dongNguCanh,
          isClosable: false,
        },
        {
          id: "tab-soap",
          title: "Bệnh án SOAP",
          type: "soap",
          templateStyle: "Goldilocks",
          content: `Chủ quan (S):\n- Lý do vào viện: ${lyDo}\n\nTiền sử bệnh (PMHx):\n\nKhách quan (O):\n\nĐánh giá (A):\n\nKế hoạch (P):`,
          isClosable: false,
        },
      ],
    };

    setSessions((prev) => [newSession, ...prev]);
    setActiveSessionId(newId);
    setActiveView("scribe");
    setActiveNavigationItem("sessions");
  };

  // Đã ký: luôn băm lại ĐÚNG tab đã ký (không theo tab đang mở). Chưa ký: tab bệnh án đang mở, nếu không thì tab mặc định.
  const tabIdKyDuyet = currentSession?.signOff ? currentSession.signOff.tabId ?? null : currentSession?.activeTabId ?? null;
  const soapRawContentForSignOff = useMemo(
    () => chonTabBenhAnDeBam(currentSession?.tabs, noteMeta?.content, tabIdKyDuyet).noiDung,
    [currentSession?.tabs, tabIdKyDuyet, noteMeta?.content],
  );

  const pageTitle: Record<string, string> = {
    home: "Trang chủ",
    sessions: "Ca khám",
    transcript: "Ghi âm & ghi chép",
    draft: "Bản nháp hồ sơ",
    proof: "Bằng chứng hội thoại",
    questions: "Hỏi ca khám",
    library: "Thư viện y khoa",
    settings: "Cài đặt",
    templates: "Mẫu bệnh án",
    tasks: "Nhiệm vụ",
    patients: "Bệnh nhân",
  };

  return (
    <div
      id="meditrace-app-root"
      className={`h-screen w-screen overflow-hidden bg-gradient-to-br from-[#F0F7FB] via-[#EEF6FB] to-[#E6F2F9] flex ${
        taskbarPosition === "top" ? "flex-col" : "flex-row"
      }`}
    >
      {/* 1. Thanh điều hướng Taskbar */}
      <NavigationRail
        activeView={activeView}
        activeNavigationItem={activeNavigationItem}
        onSelectNavigationItem={handleSelectNavigationItem}
        onSelectView={handleSelectView}
        onCreateNewSession={handleCreateNewSession}
        position={taskbarPosition}
        onTogglePosition={() => setTaskbarPosition((prev) => (prev === "top" ? "left" : "top"))}
        onOpenHelp={() => setMoTinhTrang(true)}
        nguoiDung={nguoiDung}
        onDangXuat={onDangXuat}
      />
      {moTinhTrang && <TinhTrangHeThong onClose={() => setMoTinhTrang(false)} />}

      {/* 2. Khung nhìn chính */}
      <main
        className={`flex-1 flex flex-col overflow-hidden min-h-0 min-w-0 ${
          taskbarPosition === "top"
            ? "mx-2.5 sm:mx-3 mb-2.5 rounded-2xl border border-[#BAE6FD]/70 bg-white shadow-[0_8px_30px_rgba(2,132,199,0.08),0_1px_3px_rgba(0,0,0,0.03)]"
            : ""
        }`}
      >
        {taskbarPosition === "left" && (
          <header className="h-14 shrink-0 flex items-center justify-between gap-3 border-b border-[#D9EAF3] bg-white/85 px-4 sm:px-5 lg:px-6 no-print">
            <h1 className="min-w-0 truncate text-[15px] font-semibold tracking-tight text-[#153D5A]">
              {pageTitle[activeNavigationItem] || "MediTrace"}
            </h1>
            <div className="flex shrink-0 items-center gap-1.5 text-[#49667B]">
              <button
                onClick={() => handleSelectNavigationItem("questions")}
                className="inline-flex h-9 items-center gap-2 rounded-xl border border-[#D5EAF6] bg-[#F1F9FE] px-3 text-[12px] font-semibold text-[#0874B9] transition hover:bg-[#E5F4FD] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#38BDF8]"
                title="Hỏi về ca khám đang mở"
              >
                <Sparkles size={15} />
                <span className="hidden sm:inline">Hỏi ca</span>
              </button>
              <button
                id="btn-nav-notifications"
                onClick={() => setMoTinhTrang(true)}
                className="relative flex h-9 w-9 items-center justify-center rounded-xl transition hover:bg-[#EDF7FC] hover:text-[#0874B9] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#38BDF8]"
                title="Tình trạng hệ thống"
                aria-label="Tình trạng hệ thống"
              >
                <Bell size={17} />
              </button>
              <MenuTaiKhoan nguoiDung={nguoiDung} onDangXuat={onDangXuat} huong="top" />
            </div>
          </header>
        )}

        <div className="flex-1 min-h-0 min-w-0 flex overflow-hidden">
          <ErrorBoundary
            title="Khung làm việc chính gặp sự cố hiển thị"
            description="Dữ liệu các ca khám vẫn được giữ an toàn. Bấm Thử lại hoặc Bỏ qua phần lỗi để quay về màn soạn bệnh án."
            resetKeys={[activeView, currentSession?.id]}
            onDismiss={() => handleSelectView("scribe")}
          >
            {activeView === "home" && (
              <HomeDashboard
                choPhepNgoai={choPhepNgoai}
                onNapCaMau={() => {
                  handleSelectNavigationItem("transcript");
                  void handleLoadSample();
                }}
                doctorName={nguoiDung.hoTen}
                sessions={sessions}
                onCreateSession={handleCreateNewSession}
                onOpenTranscript={() => handleSelectNavigationItem("transcript")}
                onOpenDraft={() => handleSelectNavigationItem("draft")}
                onOpenEvidence={() => handleSelectNavigationItem("proof")}
                onOpenTemplates={() => handleSelectNavigationItem("templates")}
                onOpenSession={(id) => {
                  setActiveSessionId(id);
                  handleSelectNavigationItem("sessions");
                }}
                onViewAllSessions={() => handleSelectNavigationItem("sessions")}
              />
            )}

            {activeView === "scribe" && (
              <div className="print-unclip flex-1 flex overflow-hidden">
                {/* Sidebar danh sách ca khám */}
                <div className="no-print">
                  <SessionsSidebar
                    sessions={sessions}
                    activeSessionId={activeSessionId}
                    onSelectSession={(id) => {
                      setActiveSessionId(id);
                      if (window.innerWidth < 768) setIsSessionsSidebarCollapsed(true);
                    }}
                    onCreateSession={handleCreateNewSession}
                    onDeleteSession={handleDeleteSession}
                    isCollapsed={isSessionsSidebarCollapsed}
                    onToggleCollapse={handleToggleSessionsSidebar}
                  />
                </div>

                {/* Khu vực soạn thảo & ghi âm trung tâm */}
                <div className="print-unclip @container flex-1 flex flex-col min-w-0 bg-[#F0F7FA] h-full overflow-hidden">
                  <div className="no-print">
                    <ScribeHeader
                      session={currentSession}
                      onUpdateSession={handleUpdateSession}
                      onDeleteSession={() => handleDeleteSession()}
                      onCreateNewDocument={() => setIsTemplateModalOpen(true)}
                      onPrintNote={handlePrintClinicalNote}
                      isRightDrawerOpen={isRightDrawerOpen}
                      onToggleRightDrawer={handleToggleRightDrawer}
                      choPhepNgoai={choPhepNgoai}
                      onToggleChoPhepNgoai={setChoPhepNgoai}
                    />

                    {/* Thanh các Tab tài liệu */}
                    <DocumentTabs
                      tabs={currentSession.tabs}
                      activeTabId={currentSession.activeTabId}
                      onSelectTab={handleSelectTab}
                      onCloseTab={handleCloseTab}
                      onOpenTemplateModal={() => setIsTemplateModalOpen(true)}
                    />
                  </div>

                  {/* Banner trạng thái tạo bản nháp: chỉ hiện tiến độ trên ca đang chạy, không khoá trắng các ca khác */}
                  {(isCurrentSessionGenerating || isOtherSessionGenerating) && (
                    <div className="bg-[#F0F9FF] border-b border-[#BAE6FD] px-3 @md:px-4 py-2 flex flex-wrap items-center justify-between gap-x-3 gap-y-1 text-xs text-[#0369A1] animate-in fade-in duration-200 no-print">
                      <div className="flex items-center gap-2">
                        <RefreshCw size={13} className="animate-spin text-[#0284C7]" />
                        <span className="font-medium">
                          {isOtherSessionGenerating
                            ? "Đang tạo bản nháp nền cho một ca khám khác — bác sĩ vẫn soạn thảo và ghi âm ca hiện tại bình thường."
                            : tienDoNhap
                            ? tienDoNhap.truoc > 0
                              ? `Đang chờ ${tienDoNhap.truoc} bản nháp khác tạo xong (máy chủ chỉ có một GPU)…`
                              : `Đang tạo bản nháp · ${Math.floor((Date.now() - tienDoNhap.batDau) / 60000)} phút ${Math.floor(
                                  ((Date.now() - tienDoNhap.batDau) % 60000) / 1000,
                                )} giây (tối ưu hóa VRAM & Prompt Lookup). Có thể chuyển sang ca khác, bản nháp vẫn vào đúng ca này.`
                            : "Đang xử lý tạo hồ sơ... Bác sĩ có thể chuyển sang ca khám khác hoặc bắt đầu ca khám mới."}
                        </span>
                      </div>
                      <span className="text-[11px] text-[#0284C7] font-mono">
                        Qwen3-4B · chạy tại chỗ · không gửi dữ liệu ra ngoài
                      </span>
                    </div>
                  )}

                  {/* Lỗi của dịch vụ */}
                  {apiError && (
                    <div className="bg-[#FDE8E8] border-b border-[#F5C2C2] px-4 py-2 flex items-start justify-between gap-3 text-xs text-[#8C1D26] no-print">
                      <span className="font-medium">{apiError}</span>
                      <button onClick={() => setApiError(null)} className="font-bold shrink-0">
                        đóng
                      </button>
                    </div>
                  )}

                  {/* Có bản nháp thì mời sang màn Duyệt */}
                  {noteMeta && (
                    <div className="bg-[#E6F4F1] border-b border-[#BCE3DB] px-3 @md:px-4 py-2 flex flex-wrap items-center justify-between gap-x-3 gap-y-1.5 text-xs text-[#0D5F57] no-print">
                      <span>
                        Bản nháp có <strong>{noteMeta.propositions.length}</strong> mệnh đề
                        {noteMeta.needsConfirmCount > 0 && (
                          <>
                            , trong đó <strong>{noteMeta.needsConfirmCount}</strong> máy đưa sang mục cần bác sĩ xác nhận
                          </>
                        )}
                        .
                        {noteMeta.source === "chay_truoc" && " Đây là bản ghi đã chạy từ trước."}
                        {noteMeta.source === "bo_dem" && " Khâu trích lấy từ bộ đệm đã chạy trước."}
                        {noteMeta.source !== "chay_truoc" && noteMeta.source !== "bo_dem" && " Qwen3-4B vừa chạy tại chỗ."}
                        <span className="ml-1 font-semibold">Chưa có bác sĩ duyệt.</span>
                      </span>
                      <div className="flex flex-wrap items-center gap-2 ml-auto">
                        {choPhepNgoai && (
                          <button
                            onClick={taoBanSoSanhNgoai}
                            className="px-2.5 py-1 rounded-lg border border-[#F5C2C2] bg-white text-[#8C1D26] font-semibold"
                            title="Mô hình ngoài viết một bản từ cùng lời thoại, để so với bản nháp của dự án"
                          >
                            Bản so sánh (mô hình ngoài)
                          </button>
                        )}
                        <button
                          onClick={() => {
                            setChonMD(null);
                            setLuotKiemChung(null);
                            handleSelectNavigationItem("proof");
                          }}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl font-semibold bg-[#0D9488] hover:bg-[#0B7A6F] text-white shadow-tactile-doctor transition-all cursor-pointer text-xs"
                          title="Chuyển sang trang đối chiếu toàn màn hình: Hội thoại, mệnh đề và đường nối căn cứ"
                        >
                          <CheckCircle2 size={13} />
                          <span>Duyệt từng mệnh đề</span>
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Nội dung tab đang hiển thị — gắn key={currentSession.id} chống nhiễm bẩn PHI chéo bệnh nhân */}
                  <div ref={vungGiuaRef} className="print-unclip flex-1 flex flex-col min-h-0 overflow-hidden">
                    <div className="print-unclip flex-1 flex flex-col min-h-0 min-w-0 bg-[#F8FBFC] overflow-hidden relative">
                      {currentTab?.type === "transcript" && (() => {
                        const tomTatTruocKham = taoDaiTomTatTruocKham(currentSession, sessions);
                        return (
                          <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
                            {tomTatTruocKham.coDuLieuCu && (
                              <div className="no-print px-4 py-2 bg-[#F0F9FF] border-b border-[#BAE6FD] text-[11.5px] text-[#0C4A6E] flex flex-wrap items-center gap-x-3 gap-y-1">
                                <span className="font-bold text-[#0369A1]">
                                  Tóm tắt 10s ({tomTatTruocKham.soLanKhamTruoc} lần khám trước):
                                </span>
                                {tomTatTruocKham.diUngDaXacNhan.length > 0 && (
                                  <span className="px-2 py-0.5 rounded-full bg-[#FFF5F5] border border-[#F5C2C2] text-[#B4232C] font-semibold">
                                    Dị ứng: {tomTatTruocKham.diUngDaXacNhan.join(", ")}
                                  </span>
                                )}
                                {tomTatTruocKham.thuocManTinh.length > 0 && (
                                  <span>Thuốc cũ: {tomTatTruocKham.thuocManTinh.slice(0, 4).join(", ")}</span>
                                )}
                                {tomTatTruocKham.bienThienSinhHieuXn.length > 0 && (
                                  <span className="font-mono text-[#0284C7]">
                                    {tomTatTruocKham.bienThienSinhHieuXn.join(" · ")}
                                  </span>
                                )}
                                {tomTatTruocKham.viecHenTonDong.length > 0 && (
                                  <span className="px-2 py-0.5 rounded-full bg-[#FEF9E7] border border-[#F5E6B8] text-[#7A4B00]">
                                    Hẹn đọc lại: {tomTatTruocKham.viecHenTonDong[0]}
                                  </span>
                                )}
                              </div>
                            )}
                            <TranscriptView
                              key={currentSession.id}
                              transcript={currentSession.transcript}
                              gioiTinh={currentSession.patientSubtitle}
                              onUpdateTranscript={handleUpdateTranscript}
                              onUpdateSegments={(segs) => {
                                const targetId = currentSession.id;
                                capNhatCaTheoId(targetId, (ca) => ({
                                  transcriptSegments: [...(ca.transcriptSegments || []), ...segs],
                                }));
                              }}
                              isRecording={currentSession.isRecording}
                              audioUrl={currentSession.audioUrl}
                              onStartRecording={() => handleUpdateSession({ isRecording: true })}
                              onOpenTemplates={() => setIsTemplateModalOpen(true)}
                              onLoadSample={handleLoadSample}
                            />
                          </div>
                        );
                      })()}

                      {currentTab?.type === "context" && (
                        <ContextView
                          key={currentSession.id}
                          tab={currentTab}
                          onUpdateContent={handleUpdateTabContent}
                          patientSubtitle={currentSession.patientSubtitle}
                        />
                      )}

                      {(currentTab?.type === "soap" ||
                        currentTab?.type === "leaflet" ||
                        currentTab?.type === "custom") && (
                        <div className="print-unclip flex-1 flex flex-col @4xl:flex-row min-h-0 overflow-hidden @container">
                          <div className="print-unclip flex-1 min-w-0 min-h-0 flex flex-col relative">
                            {noteMeta && (noteMeta.propositions?.length || 0) > 0 && !moDuyetBenCanh && (
                              <button
                                type="button"
                                onClick={() => setMoDuyetBenCanh(true)}
                                className="no-print absolute top-3 right-3 z-20 px-3 py-1.5 rounded-xl bg-white border border-[#BAE6FD] text-xs font-semibold text-[#0369A1] shadow-tactile-doctor-pill hover:bg-[#F0F9FF] cursor-pointer"
                              >
                                Mở ngăn duyệt ({noteMeta.propositions.length})
                              </button>
                            )}
                            <NoteEditorView
                              key={currentSession.id}
                              sessionId={currentSession.id}
                              tab={currentTab}
                              soapRawContent={soapRawContentForSignOff}
                              onUpdateContent={handleUpdateTabContent}
                              onRegenerateNote={handleRegenerateNoteStyle}
                              isGenerating={isCurrentSessionGenerating}
                              danhDau={
                                noteMeta?.propositions
                                  ? noteMeta.propositions.map((pp) => ({
                                      id: pp.id,
                                      text: pp.text,
                                      textKhac: banSuaDuyet[pp.id] ? [banSuaDuyet[pp.id]] : undefined,
                                      trangThai: trangThaiMD(pp, quyetDuyet[pp.id]),
                                    }))
                                  : undefined
                              }
                              chonId={chonMD}
                              onChonMenhDe={(id) => {
                                setChonMD(id);
                                if (id !== null) {
                                  setMoDuyetBenCanh(true);
                                }
                              }}
                              transcript={noteMeta?.transcript || currentSession.transcript}
                              onKiemChungLuot={handleKiemChungLuot}
                              noteMeta={noteMeta}
                              patientIdentifier={currentSession.patientIdentifier}
                              patientInfo={
                                xayNguCanhChoTaoHoSo({
                                  sessionId: currentSession.id,
                                  patientIdentifier: currentSession.patientIdentifier,
                                  patientSubtitle: currentSession.patientSubtitle,
                                  tabs: currentSession.tabs,
                                  contextNotes: currentSession.contextNotes,
                                }).thong_tin_benh_nhan
                              }
                              currentSession={currentSession}
                              allSessions={sessions}
                              onCreateCustomTab={(title, content) => {
                                const targetId = currentSession.id;
                                const id = `tab-doc-${Date.now()}`;
                                capNhatCaTheoId(targetId, (ca) => ({
                                  tabs: [
                                    ...ca.tabs,
                                    { id, title: title.slice(0, 60), type: "custom", content, isClosable: true },
                                  ],
                                  activeTabId: id,
                                }));
                              }}
                              quyetDuyet={quyetDuyet}
                              banSuaDuyet={banSuaDuyet}
                              signOff={currentSession.signOff}
                              crossVisitAlerts={phatHienMauThuanXuyenLanKham(currentSession, sessions)}
                              savedLeaflet={hoSoDanDoTheoCa[currentSession.id]}
                              onSaveLeaflet={(hoSo) =>
                                setHoSoDanDoTheoCa((cu) => ({ ...cu, [currentSession.id]: hoSo }))
                              }
                              onSignOff={async () => {
                                const targetId = currentSession.id;
                                const ds = noteMeta?.propositions || [];
                                const qSnap = { ...quyetDuyet };
                                const bSnap = { ...banSuaDuyet };
                                const kiemTra = kiemTraDieuKienKyDuyet(ds, qSnap, bSnap);
                                if (!kiemTra.duDieuKien) {
                                  setApiError(
                                    kiemTra.thongDiep ||
                                      "Chưa đủ căn cứ hoặc còn mục cần xác nhận chưa xử lý — không thể ký duyệt.",
                                  );
                                  if (ds.length > 0) {
                                    setMoDuyetBenCanh(true);
                                    if (kiemTra.chuaXacNhanIds.length > 0) {
                                      setChonMD(kiemTra.chuaXacNhanIds[0]);
                                    }
                                  }
                                  return;
                                }
                                // Máy chủ tính số liệu + băm từ ca ĐÃ LƯU: đẩy bản mới nhất lên trước khi ký.
                                const daLuu = await luuMotCaNgay(currentSession);
                                if (!daLuu) {
                                  setApiError("Chưa lưu được ca khám lên máy chủ — không thể ký duyệt. Thử lại sau giây lát.");
                                  return;
                                }
                                const { tabId, noiDung: soapRaw } = chonTabBenhAnDeBam(
                                  currentSession.tabs,
                                  noteMeta?.content,
                                  currentSession.activeTabId,
                                );
                                // Băm phía trình duyệt chỉ để máy chủ đối chiếu (lệch -> 409), không được dùng làm bằng chứng.
                                const contentHashTrinhDuyet = await computeNoteSignOffHash(soapRaw, qSnap, bSnap);

                                const res = await fetch(`/api/sessions/${encodeURIComponent(targetId)}/sign-off`, {
                                  method: "POST",
                                  headers: { "Content-Type": "application/json" },
                                  body: JSON.stringify({ tabId, contentHash: contentHashTrinhDuyet }),
                                });
                                if (res.ok) {
                                  const data = await res.json();
                                  capNhatCaTheoId(targetId, {
                                    signOff: {
                                      signedAt: data.signedAt,
                                      tongMenhDe: data.tongMenhDe,
                                      soGiu: data.soGiu,
                                      soSua: data.soSua,
                                      soBo: data.soBo,
                                      tyLeCoNguon: data.tyLeCoNguon,
                                      hash: data.hash,
                                      contentHash: data.contentHash,
                                      tabId: data.tabId ?? tabId,
                                      wormSeq: data.wormSeq,
                                    },
                                  });
                                } else {
                                  const d = await res.json().catch(() => ({}));
                                  setApiError(d?.error || `Không ký duyệt được (mã ${res.status})`);
                                }
                              }}
                            />
                          </div>
                          {noteMeta && (noteMeta.propositions?.length || 0) > 0 && moDuyetBenCanh && (
                            <div className="w-full @4xl:w-80 xl:w-96 flex-shrink-0 min-h-0 max-h-[45vh] @4xl:max-h-none no-print">
                              <DuyetBenCanh
                                note={noteMeta}
                                quyet={quyetDuyet}
                                setQuyet={setQuyetDuyet}
                                banSua={banSuaDuyet}
                                setBanSua={setBanSuaDuyet}
                                chonId={chonMD}
                                onChon={setChonMD}
                                onMoToanMan={() => handleSelectNavigationItem("proof")}
                                onDong={() => setMoDuyetBenCanh(false)}
                                audioUrl={currentSession.audioUrl}
                                segments={currentSession.transcriptSegments}
                                onKhoiPhucBoSot={(muc) => {
                                  const targetId = currentSession.id;
                                  const noiDungKhoiPhuc = (muc?.noi_dung_goi_y || muc?.trich_dan_nguyen_van || "").trim();
                                  if (!noiDungKhoiPhuc) return;
                                  const luot = Number(muc?.luot) || 1;
                                  const loai = String(muc?.loai_thong_tin || "");
                                  const section =
                                    loai === "di_ung"
                                      ? "DỊ ỨNG"
                                      : loai === "thuoc" || loai === "thuoc_dong_y_ngam"
                                      ? "THUỐC ĐANG DÙNG"
                                      : loai === "sinh_hieu"
                                      ? "SINH HIỆU"
                                      : "BỆNH SỬ HIỆN TẠI";
                                  const newPropId =
                                    Math.max(0, ...(noteMeta?.propositions || []).map((p) => p.id)) + 1;
                                  const dongMoi = `- ${noiDungKhoiPhuc} [T${luot}] (Khôi phục Tầng 4.5 — Bác sĩ xác nhận)`;
                                  capNhatCaTheoId(targetId, (ca) => {
                                    const updatedTabs = ca.tabs.map((t) =>
                                      t.id === ca.activeTabId || t.type === "soap"
                                        ? {
                                            ...t,
                                            content: t.content
                                              ? `${t.content.trimEnd()}\n${dongMoi}`
                                              : dongMoi,
                                          }
                                        : t,
                                    );
                                    const updatedNote = ca.note
                                      ? {
                                          ...ca.note,
                                          propositions: [
                                            ...(ca.note.propositions || []),
                                            {
                                              id: newPropId,
                                              text: noiDungKhoiPhuc,
                                              section,
                                              status: "than" as const,
                                              subject: "bệnh nhân",
                                              evidenceTurns: [luot],
                                              quotes: muc?.trich_dan_nguyen_van ? [muc.trich_dan_nguyen_van] : [],
                                            },
                                          ],
                                        }
                                      : ca.note;
                                    return { tabs: updatedTabs, note: updatedNote };
                                  });
                                }}
                              />
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Thanh nhập lệnh AI dưới đáy */}
                  <div className="no-print">
                    <BottomPromptBar
                      onSubmitPrompt={handleBottomPrompt}
                      isLoading={isCurrentSessionGenerating}
                      allowExternal={choPhepNgoai}
                      onToggleAllowExternal={setChoPhepNgoai}
                    />
                  </div>
                </div>

                {/* 3. Bảng phụ trợ bên phải bọc ErrorBoundary độc lập */}
                <div className="no-print">
                  <ErrorBoundary
                    compact
                    title="Ngăn Trợ lý & Chứng cứ gặp sự cố"
                    description="Không ảnh hưởng tới bệnh án đang soạn bên trái. Bấm Thử lại hoặc đóng ngăn này."
                    resetKeys={[currentSession.id, isRightDrawerOpen]}
                    onDismiss={() => setIsRightDrawerOpen(false)}
                  >
                    <ClinicalEvidenceDrawer
                      key={currentSession.id}
                      isOpen={isRightDrawerOpen}
                      onClose={() => setIsRightDrawerOpen(false)}
                      chatHistory={evidenceChat}
                      onSendMessage={handleSendEvidenceMessage}
                      onNewChat={() => capNhatEvidenceChatChoCa(currentSession.id, [])}
                      isLoading={isEvidenceLoading}
                      patientContext={currentSession.patientSubtitle}
                      ruleQuestions={noteMeta?.questions || []}
                      hasDraft={!!noteMeta}
                      allowExternal={choPhepNgoai}
                      hasMaterial={!!(currentSession.transcript.trim() || nguCanh().trim())}
                      onSuggestQuestions={deXuatCauHoi}
                      onAddToContext={themVaoNguCanh}
                      tienDoTroLy={tienDoTroLy}
                      laQuanTri={nguoiDung.vai === "quan_tri"}
                    />
                  </ErrorBoundary>
                </div>
              </div>
            )}

            {/* Hỏi về ca khám & Tra cứu chứng cứ — bọc ErrorBoundary riêng + Suspense */}
            {activeView === "evidence" && (
              <ErrorBoundary
                title="Màn Hỏi đáp & Tra cứu gặp sự cố"
                description="Bấm Thử lại để mở lại khung hỏi đáp, hoặc Bỏ qua phần lỗi để quay về Ca khám."
                resetKeys={[currentSession.id]}
                onDismiss={() => handleSelectView("scribe")}
              >
                <Suspense fallback={<KhungDangTaiManHinh />}>
                  <EvidenceView
                    caTen={currentSession.patientIdentifier}
                    coLoiThoai={!!currentSession.transcript.trim()}
                    allowExternal={choPhepNgoai}
                    onToggleExternal={setChoPhepNgoai}
                    hoi={hoiDap}
                    onNavigate={handleSelectView}
                    onOpenCreate={() => {
                      handleSelectNavigationItem("sessions");
                      setIsTemplateModalOpen(true);
                    }}
                    onSaveToContext={themVaoNguCanh}
                    initialPrompt={promptTraCuuTrangChu}
                    onInitialPromptUsed={() => setPromptTraCuuTrangChu("")}
                  />
                </Suspense>
              </ErrorBoundary>
            )}

            {/* Duyệt từng mệnh đề */}
            {activeView === "verification" && (
              <Suspense fallback={<KhungDangTaiManHinh />}>
                <VerificationView
                  note={noteMeta}
                  transcript={currentSession.transcript}
                  onBack={() => handleSelectNavigationItem("draft")}
                  patientIdentifier={currentSession.patientIdentifier}
                  allowExternal={choPhepNgoai}
                  onAskExternalQuestions={deXuatCauHoi}
                  quyetChung={quyetDuyet}
                  setQuyetChung={setQuyetDuyet}
                  banSuaChung={banSuaDuyet}
                  setBanSuaChung={setBanSuaDuyet}
                  chonBanDau={chonBanDau}
                  audioUrl={currentSession.audioUrl}
                  segments={currentSession.transcriptSegments}
                />
              </Suspense>
            )}

            {/* Quản lý Bệnh nhân (nhận trực tiếp `sessions` từ store chính, xoá xung đột 2 store) */}
            {activeView === "patients" && (
              <Suspense fallback={<KhungDangTaiManHinh />}>
                <PatientsView
                  sessions={sessions}
                  onStartSessionWithPatient={handleStartSessionWithPatient}
                />
              </Suspense>
            )}

            {/* Nhiệm vụ Lâm sàng */}
            {activeView === "tasks" && (
              <Suspense fallback={<KhungDangTaiManHinh />}>
                <TasksView
                  sessions={sessions}
                  onOpenSession={(sessionId) => {
                    setActiveSessionId(sessionId);
                    handleSelectNavigationItem("sessions");
                  }}
                />
              </Suspense>
            )}

            {/* Mẫu Bệnh án */}
            {activeView === "templates" && (
              <Suspense fallback={<KhungDangTaiManHinh />}>
                <TemplatesView
                  onUseTemplate={(tpl) => {
                    void handleSelectTemplate(tpl);
                    setActiveView("scribe");
                    setActiveNavigationItem("draft");
                  }}
                />
              </Suspense>
            )}

            {activeView === "command_center" && (
              <section className="flex-1 min-w-0 overflow-y-auto bg-[#F8FBFC]">
                <Suspense fallback={<KhungDangTaiManHinh />}>
                  <HospitalCommandCenterView />
                </Suspense>
              </section>
            )}

            {activeView === "library" && (
              <section className="flex-1 min-w-0 overflow-y-auto bg-[#F8FBFC] px-5 py-6 lg:px-8 lg:py-8">
                <Suspense fallback={<KhungDangTaiManHinh />}>
                  <ThuVienYKhoa />
                </Suspense>
              </section>
            )}

            {activeView === "settings" && (
              <section className="flex-1 min-w-0 overflow-y-auto bg-[#F8FBFC] px-5 py-6 lg:px-8 lg:py-8">
                <div className="mx-auto flex max-w-3xl flex-col gap-4">
                  <section className="rounded-2xl border border-[#D8EAF4] bg-white p-4 sm:p-5">
                    <div>
                      <h2 className="text-[14px] font-semibold text-[#174F70]">Vị trí thanh điều hướng</h2>
                    </div>
                    <div className="mt-4 inline-flex rounded-xl bg-[#EFF7FB] p-1">
                      {(["left", "top"] as const).map((position) => (
                        <button
                          key={position}
                          onClick={() => setTaskbarPosition(position)}
                          aria-pressed={taskbarPosition === position}
                          className={`rounded-lg px-3.5 py-2 text-[12px] font-semibold transition ${
                            taskbarPosition === position
                              ? "bg-white text-[#0874B9] shadow-sm"
                              : "text-[#607C8E] hover:text-[#174F70]"
                          }`}
                        >
                          {position === "left" ? "Bên trái" : "Trên đầu"}
                        </button>
                      ))}
                    </div>
                  </section>

                  <section className="rounded-2xl border border-[#D8EAF4] bg-white p-4 sm:p-5">
                    <div className="flex flex-wrap items-start justify-between gap-4">
                      <div className="max-w-xl">
                        <h2 className="text-[14px] font-semibold text-[#174F70]">
                          Mô hình ngoài (Dịch vụ đám mây / API thương mại)
                        </h2>
                        <p className="mt-1 text-[12px] leading-relaxed text-[#6C8494]">
                          Khi bật, nội dung gửi ra được che một số mẫu định danh trực tiếp mà hệ thống nhận diện được. Đây chỉ là giảm thiểu rủi ro, không bảo đảm ẩn danh hoàn toàn; hãy chỉ gửi dữ liệu phù hợp với chính sách cơ sở. Bản nháp chính vẫn do Qwen3–4B xử lý tại chỗ.
                        </p>
                      </div>
                      <label className="inline-flex cursor-pointer items-center gap-2 rounded-xl bg-[#F3F8FB] px-3.5 py-2 text-[12px] font-semibold text-[#345F79] hover:bg-[#EAF4FA] transition-colors">
                        <input
                          type="checkbox"
                          checked={choPhepNgoai}
                          onChange={(event) => setChoPhepNgoai(event.target.checked)}
                          className="accent-[#087FC1]"
                        />
                        Cho phép mô hình ngoài
                      </label>
                    </div>
                  </section>

                  <button
                    onClick={() => setMoTinhTrang(true)}
                    className="self-start rounded-xl border border-[#CFE4F0] bg-white px-3.5 py-2.5 text-[12px] font-semibold text-[#17628B] transition hover:bg-[#EDF7FC] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#38BDF8]"
                  >
                    Xem tình trạng hệ thống
                  </button>
                </div>
              </section>
            )}
          </ErrorBoundary>
        </div>
      </main>

      {/* Nút "Tạo": tìm mẫu hoặc gõ yêu cầu để AI soạn văn bản từ ca đang mở */}
      <TaoVanBanModal
        isOpen={isTemplateModalOpen}
        onClose={() => setIsTemplateModalOpen(false)}
        session={currentSession}
        note={noteMeta}
        allowExternal={choPhepNgoai}
        onEnableExternal={() => setChoPhepNgoai(true)}
        onCreate={taoVanBan}
      />
    </div>
  );
}
