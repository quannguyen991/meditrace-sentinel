import React, { useState, useEffect, useRef } from "react";
import { ViewMode, Session, DocumentTabItem, ClinicalChatMessage, TemplateItem, Patient } from "./types";
import { initialSessions, initialEvidenceChat } from "./data/mockData";
import { RefreshCw, Sparkles, Bell } from "lucide-react";
import { NavigationRail } from "./components/NavigationRail";
import { MenuTaiKhoan } from "./components/MenuTaiKhoan";
import { HomeDashboard } from "./components/HomeDashboard";
import { SessionsSidebar } from "./components/SessionsSidebar";
import { ScribeHeader } from "./components/ScribeHeader";
import { DocumentTabs } from "./components/DocumentTabs";
import { TranscriptView } from "./components/TranscriptView";
import { NoteEditorView } from "./components/NoteEditorView";
import { ContextView } from "./components/ContextView";
import { BottomPromptBar } from "./components/BottomPromptBar";
import { ClinicalEvidenceDrawer, CheDoHoi, NguonBat } from "./components/ClinicalEvidenceDrawer";
import { TaoVanBanModal } from "./components/TaoVanBanModal";
import { lyDoKham, type MauVanBan } from "./lib/mauVanBan";
import { EvidenceView, CheDoHoiDap, NguonTraCuu, TraLoiHoiDap } from "./components/EvidenceView";
import { PatientsView } from "./components/PatientsView";
import { TasksView } from "./components/TasksView";
import { TemplatesView } from "./components/TemplatesView";
import { ThuVienYKhoa } from "./components/ThuVienYKhoa";
import { VerificationView, NoteMeta, Quyet } from "./components/VerificationView";
import { DuyetBenCanh, trangThaiMD } from "./components/DuyetBenCanh";
import { TinhTrangHeThong } from "./components/TinhTrangHeThong";
import type { NguoiDung } from "./lib/taiKhoan";
import { cacNguoiNoiChuaGan } from "./lib/nguoiNoi";

/** Trạng thái không còn đúng sau khi tải lại trang: đang ghi âm, đường dẫn blob của bản ghi. */
function truocKhiLuu(s: Session): Session {
  const { audioUrl, ...con } = s;
  return { ...con, isRecording: false };
}
function sauKhiNap(s: Session): Session {
  return { ...s, isRecording: false, audioUrl: undefined };
}
/** Băm ngắn (djb2) để làm khoá kết quả duyệt theo nội dung bản nháp. Không dùng cho bảo mật. */
function bamChuoi(s: string) {
  let h = 5381;
  for (let i = 0; i < s.length; i++) h = ((h << 5) + h + s.charCodeAt(i)) | 0;
  return (h >>> 0).toString(36);
}

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
  const [sessions, setSessions] = useState<Session[]>(() => {
    try {
      const saved = localStorage.getItem("meditrace_sessions");
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) return parsed.map(sauKhiNap);
      }
    } catch (e) {}
    return initialSessions;
  });
  const [activeSessionId, setActiveSessionId] = useState<string>(() => {
    try {
      const id = localStorage.getItem("meditrace_ca_dang_mo");
      if (id && sessions.some((s) => s.id === id)) return id;
    } catch {}
    return sessions[0]?.id || initialSessions[0].id;
  });
  useEffect(() => {
    try {
      localStorage.setItem("meditrace_ca_dang_mo", activeSessionId);
    } catch {}
  }, [activeSessionId]);

  /**
   * Lưu ca khám ở hai nơi: trình duyệt (nhanh, có ngay khi F5) và cơ sở dữ liệu trên server
   * (bảng ca_kham của tài khoản đang đăng nhập — còn khi xoá dữ liệu trình duyệt, mở được từ máy khác).
   * Khi mở trang, bản nào mới hơn (savedAt) thì dùng bản đó. Chưa đọc xong kho server thì
   * chưa ghi lên server, để không đè bản mới hơn bằng bản cũ trong trình duyệt.
   */
  const [khoServer, setKhoServer] = useState<"dang_doc" | "san_sang" | "loi">("dang_doc");
  // Mốc lưu của bản trong trình duyệt, đọc MỘT LẦN lúc mở trang — trước khi effect lưu bên dưới
  // ghi mốc mới. (Đọc trong effect thì ở chế độ dev React chạy effect hai lần, lần hai đọc phải
  // mốc vừa ghi, tưởng bản trình duyệt mới hơn và ghi đè kho server.)
  const [mocTrinhDuyet] = useState<number>(() => {
    try {
      return localStorage.getItem("meditrace_sessions")
        ? Number(localStorage.getItem("meditrace_sessions_luc") || 0)
        : 0;
    } catch {
      return 0;
    }
  });
  useEffect(() => {
    let huy = false;
    fetch("/api/ca-kham")
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`mã ${r.status}`))))
      .then((d) => {
        if (huy) return;
        if (Array.isArray(d.sessions) && d.sessions.length && (d.savedAt || 0) > mocTrinhDuyet) {
          const ds: Session[] = d.sessions.map(sauKhiNap);
          setSessions(ds);
          setActiveSessionId((id) => (ds.some((s) => s.id === id) ? id : ds[0].id));
        }
        setKhoServer("san_sang");
      })
      .catch(() => !huy && setKhoServer("loi"));
    return () => {
      huy = true;
    };
  }, []);

  useEffect(() => {
    const luc = Date.now();
    const goi = sessions.map(truocKhiLuu);
    try {
      localStorage.setItem("meditrace_sessions", JSON.stringify(goi));
      localStorage.setItem("meditrace_sessions_luc", String(luc));
    } catch (e) {}
    if (khoServer !== "san_sang") return;
    const hen = setTimeout(() => {
      fetch("/api/ca-kham", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sessions: goi, savedAt: luc }),
      }).catch(() => {});
    }, 800);
    return () => clearTimeout(hen);
  }, [sessions, khoServer]);

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
    // Nếu trên tablet mở sidebar thì tự đóng drawer để ưu tiên không gian
    if (willExpand && typeof window !== "undefined" && window.innerWidth < 1100 && isRightDrawerOpen) {
      setIsRightDrawerOpen(false);
    }
  };

  const handleToggleRightDrawer = () => {
    const willOpen = !isRightDrawerOpen;
    setIsRightDrawerOpen(willOpen);
    // Nếu trên tablet mở drawer thì tự thu gọn sidebar
    if (willOpen && typeof window !== "undefined" && window.innerWidth < 1200 && !isSessionsSidebarCollapsed) {
      setIsSessionsSidebarCollapsed(true);
    }
  };

  const [isTemplateModalOpen, setIsTemplateModalOpen] = useState(false);
  const [moTinhTrang, setMoTinhTrang] = useState(false);
  const [promptTraCuuTrangChu, setPromptTraCuuTrangChu] = useState("");

  const [isEvidenceLoading, setIsEvidenceLoading] = useState(false);
  const [isGeneratingNote, setIsGeneratingNote] = useState(false);
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
   * `than`: {transcript} | {sessionId} | {sampleCaseId}.
   */
  const taoHoSo = async (than: Record<string, unknown>): Promise<NoteMeta | null> => {
    // Mô hình tách mệnh đề cần biết AI nói từng lượt. Hệ thống không đoán vai từ giọng nói,
    // nên còn lượt "Chưa rõ vai" thì dừng lại và báo, thay vì để mô hình tự gán.
    const loiThoai = typeof than.transcript === "string" ? than.transcript : "";
    if (loiThoai) {
      const dong = loiThoai.split("\n").filter((l) => l.trim());
      const chuaRo = dong.filter((l) => !/^\s*(bác sĩ|bệnh nhân|người nhà)\s*:/i.test(l)).length;
      if (chuaRo) {
        // "Người nói N" là máy tách theo giọng, chưa phải vai: vẫn chặn như "Chưa rõ vai".
        const soNguoiNoi = cacNguoiNoiChuaGan(loiThoai).length;
        setApiError(
          `Còn ${chuaRo} lượt chưa gán vai. ` +
            (soNguoiNoi
              ? `Ở tab Lời thoại, ô “Gán vai theo người nói” còn ${soNguoiNoi} người nói chưa chọn vai; ` +
                "lượt lẻ thì bấm nhãn tròn bên trái lượt đó, rồi tạo bản nháp."
              : "Ở tab Lời thoại, bấm vào nhãn tròn bên trái mỗi lượt để chọn " +
                "Bác sĩ / Bệnh nhân / Người nhà, rồi tạo bản nháp.")
        );
        return null;
      }
    }
    setIsGeneratingNote(true);
    setApiError(null);
    try {
      let res = await fetch("/api/generate-note", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ branch: "C_khoa_hoi", ...than }),
      });
      let data = await res.json();
      // Bản nháp mới mất vài phút: máy chủ trả 202 + mã việc, hỏi lại tới khi xong
      // (không giữ một yêu cầu mở vài phút — đường hầm ra ngoài cắt ở khoảng 100 giây).
      while (res.status === 202 && data?.jobId) {
        setTienDoNhap({ batDau: data.startedAt || Date.now(), truoc: data.queued || 0 });
        await new Promise((r) => setTimeout(r, 4000));
        res = await fetch(`/api/generate-note/${data.jobId}`);
        data = await res.json();
      }
      if (!res.ok) throw new Error(data?.error || `Dịch vụ trả mã ${res.status}`);
      const meta: NoteMeta = data;
      setNoteMeta(meta);
      return meta;
    } catch (err: any) {
      setApiError(err?.message || "Không gọi được dịch vụ MediTrace");
      return null;
    } finally {
      setIsGeneratingNote(false);
      setTienDoNhap(null);
    }
  };

  // Cấu hình tra cứu nguồn web & y văn

  // Ca khám đang hoạt động
  const currentSession =
    sessions.find((s) => s.id === activeSessionId) || sessions[0];

  // Tab tài liệu đang xem trong ca khám
  const currentTab =
    currentSession?.tabs.find((t) => t.id === currentSession.activeTabId) ||
    currentSession?.tabs[0];

  // Cập nhật thông tin ca khám
  const handleUpdateSession = (updatedFields: Partial<Session>) => {
    setSessions((prev) =>
      prev.map((s) => (s.id === currentSession.id ? { ...s, ...updatedFields } : s))
    );
  };

  // Bản nháp và hỏi đáp gắn với TỪNG CA (trước đây là biến chung: F5 là mất, đổi ca vẫn thấy
  // bản nháp của ca trước). Hàm ghi chốt mã ca lúc gọi, nên lời gọi chậm vẫn ghi đúng ca.
  const noteMeta: NoteMeta | null = currentSession?.note ?? null;
  const setNoteMeta = (m: NoteMeta | null) => handleUpdateSession({ note: m });
  const evidenceChat: ClinicalChatMessage[] = currentSession?.evidenceChat || [];

  // Duyệt mệnh đề: giữ/sửa/bỏ dùng chung giữa ngăn cạnh bản nháp và màn duyệt đầy đủ, LƯU CÙNG CA
  // (session.duyet -> kho ca-kham trên máy chủ) nên F5 không mất. Khoá theo nội dung bản nháp:
  // tạo lại bản nháp thì kết quả cũ không còn khớp và bị bỏ qua.
  const khoaDuyet = noteMeta ? `${noteMeta.caseId || ""}#${noteMeta.content.length}#${bamChuoi(noteMeta.content)}` : "";
  const duyetLuu = currentSession?.duyet?.khoa === khoaDuyet ? currentSession.duyet : undefined;
  const quyetDuyet: Record<number, Quyet> = duyetLuu?.quyet || {};
  const banSuaDuyet: Record<number, string> = duyetLuu?.banSua || {};
  /** Cập nhật một phần kết quả duyệt; dùng bản MỚI NHẤT của ca trong setSessions (tránh ghi đè
   *  khi hai lần bấm liên tiếp), và chốt mã ca lúc gọi. */
  const capNhatDuyet = (phan: "quyet" | "banSua", u: React.SetStateAction<Record<number, any>>) => {
    const idCa = currentSession.id;
    const khoa = khoaDuyet;
    setSessions((prev) =>
      prev.map((s) => {
        if (s.id !== idCa) return s;
        const cu = s.duyet?.khoa === khoa ? s.duyet : { khoa, quyet: {}, banSua: {} };
        const moi = typeof u === "function" ? (u as (x: Record<number, any>) => Record<number, any>)(cu[phan]) : u;
        return { ...s, duyet: { ...cu, [phan]: moi } };
      })
    );
  };
  const setQuyetDuyet: React.Dispatch<React.SetStateAction<Record<number, Quyet>>> = (u) => capNhatDuyet("quyet", u);
  const setBanSuaDuyet: React.Dispatch<React.SetStateAction<Record<number, string>>> = (u) => capNhatDuyet("banSua", u);
  const [moDuyetBen, setMoDuyetBen] = useState(false);
  const [chonMD, setChonMD] = useState<number | null>(null);
  // Màn hẹp (< 896px vùng giữa): không đủ chỗ cho hai bên -> chuyển qua lại "Bản nháp | Duyệt".
  const [xemHep, setXemHep] = useState<"nhap" | "duyet">("duyet");
  const vungGiuaRef = useRef<HTMLDivElement>(null);
  const laHep = () => (vungGiuaRef.current?.clientWidth ?? 9999) < 896;
  /** Chọn mệnh đề từ ngăn duyệt: màn hẹp thì chuyển sang bản nháp để thấy câu đó. */
  const chonTuNgan = (id: number | null) => {
    setChonMD(id);
    if (id !== null && laHep()) setXemHep("nhap");
  };
  /** Chọn câu trong bản nháp: màn hẹp thì chuyển sang ngăn duyệt để thấy mệnh đề. */
  const chonTuBanNhap = (id: number | null) => {
    setChonMD(id);
    if (id !== null && laHep()) setXemHep("duyet");
  };
  useEffect(() => {
    setChonMD(null);
  }, [currentSession?.id, noteMeta?.content]);
  /** Mở ngăn duyệt cạnh bản nháp; đang ở tab khác thì chuyển sang tab bản nháp. */
  const moNganDuyet = () => {
    const tabNhap = [...(currentSession?.tabs || [])].reverse().find((t) => t.title === "Bản nháp hồ sơ" || t.content === noteMeta?.content);
    if (tabNhap && currentSession.activeTabId !== tabNhap.id) handleUpdateSession({ activeTabId: tabNhap.id });
    setMoDuyetBen(true);
    setXemHep("duyet");
  };
  const setEvidenceChat = (
    u: ClinicalChatMessage[] | ((truoc: ClinicalChatMessage[]) => ClinicalChatMessage[])
  ) => {
    const id = currentSession.id;
    setSessions((prev) =>
      prev.map((s) =>
        s.id === id ? { ...s, evidenceChat: typeof u === "function" ? u(s.evidenceChat || []) : u } : s
      )
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

    setSessions([newSession, ...sessions]);
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
    const remaining = sessions.filter((s) => s.id !== targetId);
    setSessions(remaining);
    if (activeSessionId === targetId) {
      setActiveSessionId(remaining[0].id);
    }
  };

  // Chuyển tab trong ca khám
  const handleSelectTab = (tabId: string) => {
    handleUpdateSession({ activeTabId: tabId });
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
    };
    setActiveView(view);
    setActiveNavigationItem(mucTheoView[view]);
  };

  const handleSelectNavigationItem = (item: string) => {
    setActiveNavigationItem(item);
    if (item === "home") {
      setActiveView("home");
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
      // Ca chưa có bản nháp: đưa người dùng về tab lời thoại, nơi có nút tạo bản nháp.
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
    const updatedTabs = currentSession.tabs.filter((t) => t.id !== tabId);
    const nextActive =
      currentSession.activeTabId === tabId
        ? updatedTabs[0]?.id || "tab-transcript"
        : currentSession.activeTabId;

    handleUpdateSession({ tabs: updatedTabs, activeTabId: nextActive });
  };

  // Cập nhật nội dung tab
  const handleUpdateTabContent = (newContent: string) => {
    const updatedTabs = currentSession.tabs.map((t) =>
      t.id === currentTab.id ? { ...t, content: newContent } : t
    );
    handleUpdateSession({ tabs: updatedTabs });
  };

  // Cập nhật lời thoại
  const handleUpdateTranscript = (newTranscript: string) => {
    const updatedTabs = currentSession.tabs.map((t) =>
      t.type === "transcript" ? { ...t, content: newTranscript } : t
    );
    handleUpdateSession({ transcript: newTranscript, tabs: updatedTabs });
  };

  // Màn "Mẫu bệnh án" → soạn theo mẫu đó (cùng đường với nút "Tạo"; cần mô hình ngoài).
  const handleSelectTemplate = async (template: TemplateItem, _customPrompt?: string) => {
    await taoVanBan({
      id: template.id,
      ten: template.title,
      nhom: "ho_so",
      chiDan: template.promptDescription || `Soạn "${template.title}" cho ca này.`,
    });
  };

  // Dựng lại bản nháp từ lời thoại hiện tại (không có "phong cách": xem ghi chú ở trên)
  const handleRegenerateNoteStyle = async (_newStyle: string) => {
    const meta = await taoHoSo({ transcript: currentSession.transcript });
    if (!meta) return;
    const updatedTabs = currentSession.tabs.map((t) =>
      t.id === currentTab.id ? { ...t, content: meta.content } : t
    );
    handleUpdateSession({ tabs: updatedTabs });
  };

  /**
   * Thanh lệnh dưới cùng. Bản này KHÔNG sửa hồ sơ bằng mô hình ngôn ngữ: sửa tay trong ô
   * soạn thảo, hoặc dùng màn Duyệt. Ở tab lời thoại thì lệnh có nghĩa là "dựng bản nháp".
   */
  const handleBottomPrompt = async (promptText: string) => {
    if (currentTab.type === "soap" || currentTab.type === "leaflet" || currentTab.type === "custom") {
      // Sửa theo lời nhắc chỉ có khi bật mô hình ngoài. Không bật: sửa tay hoặc dùng màn Duyệt.
      if (!choPhepNgoai) {
        setApiError(
          "Sửa theo lời nhắc cần mô hình ngoài (bật công tắc “Mô hình ngoài”). Không bật thì sửa " +
            "trực tiếp trong ô soạn thảo, hoặc mở màn Duyệt để giữ, sửa, bỏ từng mệnh đề."
        );
        return;
      }
      setIsGeneratingNote(true);
      try {
        const d = await goiNgoai("/api/edit-note", {
          currentContent: currentTab.content,
          instruction: promptText,
          transcript: currentSession.transcript,
        });
        if (d?.updatedContent) {
          handleUpdateTabContent(
            `${d.updatedContent}\n\n[Đã sửa bằng mô hình ngoài · ${d.model} · chưa qua kiểm căn cứ · theo lời nhắc: ${promptText}]`
          );
        }
      } finally {
        setIsGeneratingNote(false);
      }
      return;
    }
    const meta = await taoHoSo({ transcript: currentSession.transcript });
    if (!meta) return;
    const newTabId = `tab-doc-${Date.now()}`;
    const newTab: DocumentTabItem = {
      id: newTabId,
      title: promptText || "Bản nháp hồ sơ",
      type: "custom",
      content: meta.content,
      isClosable: true,
    };
    handleUpdateSession({ tabs: [...currentSession.tabs, newTab], activeTabId: newTabId });
  };

  // Gửi câu hỏi lâm sàng & bằng chứng y văn
  /**
   * Nap mot ca DA CHAY TRUOC tu dich vu tai cho. Dung khi GPU dang ban: ban ghi co san
   * duoc danh nhan `chay_truoc`, khong gia vo la may vua chay.
   */
  const handleLoadSample = async () => {
    setApiError(null);
    try {
      const res = await fetch("/api/sample-cases");
      const data = await res.json();
      if (!res.ok) throw new Error(data?.error || `Dich vu tra ma ${res.status}`);
      const ds = data.ca || [];
      if (!ds.length) throw new Error("Dich vu khong co ca nao da chay truoc");
      const ca = ds[Math.floor(Math.random() * ds.length)];
      const meta = await taoHoSo({ sampleCaseId: ca.id });
      if (!meta) return;
      const tabId = `tab-doc-${Date.now()}`;
      handleUpdateSession({
        patientIdentifier: `Ca ${ca.id}`,
        patientSubtitle: `Dữ liệu tổng hợp của dự án · bộ ${ca.bo}`,
        transcript: meta.transcript || "",
        tabs: [
          ...currentSession.tabs.map((t) =>
            t.type === "transcript" ? { ...t, content: meta.transcript || "" } : t
          ),
          { id: tabId, title: "Bản nháp hồ sơ", type: "custom", content: meta.content, isClosable: true },
        ],
        activeTabId: tabId,
      });
    } catch (err: any) {
      setApiError(err?.message || "Khong nap duoc ca mau");
    }
  };

  /** Nội dung tab Ngữ cảnh của ca đang mở (bác sĩ gõ hoặc thêm câu hỏi từ ngăn phải). */
  const nguCanh = () => currentSession.tabs.find((t) => t.type === "context")?.content || "";

  /** Chép một câu hỏi vào cuối tab Ngữ cảnh. */
  const themVaoNguCanh = (cau: string) => {
    const cu = nguCanh().trimEnd();
    const moi = cu ? `${cu}\n- ${cau}` : `Câu hỏi cần hỏi thêm:\n- ${cau}`;
    handleUpdateSession({
      tabs: currentSession.tabs.map((t) => (t.type === "context" ? { ...t, content: moi } : t)),
    });
  };

  /** Phương án 1: mô hình ngoài đọc ngữ cảnh + lời thoại + mệnh đề đã tách, đề xuất câu hỏi. */
  const deXuatCauHoi = async () => {
    const d = await goiNgoai("/api/questions-external", {
      context: nguCanh(),
      transcript: noteMeta?.transcript || currentSession.transcript,
      propositions: noteMeta?.propositions || [],
    });
    return d ? { questions: d.questions || [], model: d.model, seconds: d.seconds } : null;
  };

  /**
   * Nút "Tạo". Bản nháp hồ sơ: Qwen3-4B tại chỗ (phần được đo). Mọi mẫu khác và yêu cầu tự do:
   * mô hình ngoài soạn từ lời thoại + bản nháp + tab Ngữ cảnh, mở thành tab mới có nhãn nguồn.
   */
  const taoVanBan = async (mau: MauVanBan, yeuCau?: string) => {
    if (mau.taiCho) {
      const meta = await taoHoSo({ transcript: currentSession.transcript });
      if (!meta) return;
      const id = `tab-doc-${Date.now()}`;
      handleUpdateSession({
        tabs: [...currentSession.tabs, { id, title: "Bản nháp hồ sơ", type: "custom", content: meta.content, isClosable: true }],
        activeTabId: id,
      });
      return;
    }
    const idCa = currentSession.id;
    setIsGeneratingNote(true);
    try {
      const d = await goiNgoai("/api/generate-document", {
        title: yeuCau ? "" : mau.ten,
        instruction: yeuCau || mau.chiDan,
        transcript: noteMeta?.transcript || currentSession.transcript,
        draft: noteMeta?.content || "",
        context: nguCanh(),
      });
      if (!d?.content) return;
      const id = `tab-doc-${Date.now()}`;
      const nhan =
        `\n\n---\n[Soạn bằng mô hình ngoài · ${d.model} · ${d.seconds}s · chưa qua kiểm căn cứ · từ lời thoại, bản nháp và tab Ngữ cảnh` +
        `${d.missingCount ? ` · còn ${d.missingCount} chỗ [cần bổ sung]` : ""}. Bác sĩ đọc lại trước khi dùng.]`;
      const tab: DocumentTabItem = {
        id, title: (yeuCau || mau.ten).slice(0, 60), type: "custom", content: `${d.content}${nhan}`, isClosable: true,
      };
      setSessions((prev) =>
        prev.map((c) => (c.id === idCa ? { ...c, tabs: [...c.tabs, tab], activeTabId: id } : c))
      );
    } finally {
      setIsGeneratingNote(false);
    }
  };

  /** Màn "Hỏi về ca khám": ba kiểu hỏi, đều cần mô hình ngoài. */
  const hoiDap = async (
    cheDo: CheDoHoiDap,
    cauHoi: string,
    tuyChon: { kemNguCanh: boolean; nguon: NguonTraCuu }
  ): Promise<TraLoiHoiDap | null> => {
    if (cheDo === "de_xuat") {
      const d = await deXuatCauHoi();
      if (!d) return null;
      return {
        content: d.questions.length
          ? d.questions
              .map((q: any, i: number) =>
                `${i + 1}. **${q.hoi}**${q.goi_y ? ` — ${q.goi_y}` : ""}${q.vi_sao ? `\n   _${q.vi_sao}_` : ""}` +
                `${q.luot?.length ? ` (lượt ${q.luot.join(", ")})` : ""}`)
              .join("\n")
          : "Mô hình không đề xuất câu nào.",
        meta: `Mô hình ngoài · ${d.model} · ${d.seconds}s · chưa qua kiểm căn cứ · từ ngữ cảnh, lời thoại và mệnh đề đã tách`,
      };
    }
    if (cheDo === "tra_cuu") {
      // Một ô hỏi (gộp 24/09, như ngăn phải): gắn ca khám thì gửi cả lời thoại + bản nháp, server tự
      // quyết định trả lời từ ca hay tra tài liệu. Bỏ gắn ca thì chỉ tra tài liệu theo câu hỏi.
      const ly = lyDoKham(currentSession, noteMeta);
      const d = await goiNgoai("/api/lookup-official", {
        question: cauHoi,
        context: tuyChon.kemNguCanh ? [ly && `Lý do khám: ${ly}`, nguCanh()].filter(Boolean).join("\n") : "",
        nguon: tuyChon.nguon,
        ...(tuyChon.kemNguCanh
          ? { transcript: noteMeta?.transcript || currentSession.transcript, draft: noteMeta?.content || "" }
          : {}),
      });
      if (!d) return null;
      return {
        content: d.answer,
        sources: d.sources || [],
        warning: d.warning,
        cauTruc: d.cauTruc || null,
        question: cauHoi.replace(/\s*\(tra nguồn khác\)$/, ""),
        meta: d.caseOnly
          ? `Mô hình ngoài · ${d.model} · ${d.seconds}s · chưa qua kiểm căn cứ · chỉ từ hội thoại và bản nháp của ca này (không cần tra tài liệu)`
          : `Mô hình ngoài · ${d.model} · ${d.seconds}s · chưa qua kiểm căn cứ · ${tuyChon.kemNguCanh ? "ca khám + " : ""}tài liệu server tự tìm` +
            `${d.searchTerms?.pubmed ? ` (từ khoá: ${d.searchTerms.pubmed})` : ""} · tham khảo, bác sĩ quyết định`,
      };
    }
    const d = await goiNgoai("/api/clinical-qa", {
      question: cauHoi,
      transcript: currentSession.transcript,
      draft: noteMeta?.content || "",
    });
    if (!d) return null;
    return { content: d.answer, meta: `Mô hình ngoài · ${d.model} · ${d.seconds}s · chưa qua kiểm căn cứ · chỉ dựa trên hội thoại của ca này` };
  };

  /** Phương án 2 và hỏi về ca khám: cả hai cần mô hình ngoài; ngăn phải khoá ô nhập khi công tắc tắt. */
  const handleSendEvidenceMessage = async (query: string, mode: CheDoHoi, nguon?: NguonBat) => {
    const gio = () => new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    setEvidenceChat((prev) => [
      ...prev,
      { id: `user-${Date.now()}`, role: "user", content: query, mode, timestamp: gio() },
    ]);
    setIsEvidenceLoading(true);
    try {
      if (mode === "tra_cuu") {
        // Một ô hỏi: gửi cả ca khám; server tự quyết định có tra tài liệu không.
        const d = await goiNgoai("/api/lookup-official", {
          question: query,
          context: nguCanh(),
          transcript: noteMeta?.transcript || currentSession.transcript,
          draft: noteMeta?.content || currentTab?.content || "",
          ...(nguon ? { nguon } : {}),
        });
        if (d) {
          setEvidenceChat((prev) => [
            ...prev,
            {
              id: `asst-${Date.now()}`,
              role: "assistant",
              mode,
              content: d.answer,
              sources: d.sources || [],
              cauTruc: d.cauTruc || null,
              question: query.replace(/\s*\(tra nguồn khác\)$/, ""),
              removedSources: d.removedSources || 0,
              warning: d.warning,
              meta: d.caseOnly
                ? `Mô hình ngoài · ${d.model} · ${d.seconds}s · chưa qua kiểm căn cứ · chỉ từ hội thoại và bản nháp của ca này (không cần tra tài liệu)`
                : `Mô hình ngoài · ${d.model} · ${d.seconds}s · chưa qua kiểm căn cứ · ca khám + tài liệu server tự tìm (Bộ Y tế, MSD, DailyMed, NICE, WHO, CDC, MedlinePlus, PubMed) · tham khảo, bác sĩ quyết định`,
              timestamp: gio(),
            },
          ]);
        }
        return;
      }
      const d = await goiNgoai("/api/clinical-qa", {
        question: query,
        transcript: currentSession.transcript,
        draft: noteMeta?.content || currentTab?.content || "",
      });
      if (d) {
        setEvidenceChat((prev) => [
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
    }
  };

  /** Bản so sánh: mô hình ngoài viết từ cùng lời thoại. Không có mệnh đề, không có căn cứ. */
  const taoBanSoSanhNgoai = async () => {
    const loiThoai = noteMeta?.transcript || currentSession.transcript;
    if (!loiThoai) {
      setApiError("Chưa có lời thoại để làm bản so sánh.");
      return;
    }
    setIsGeneratingNote(true);
    try {
      const d = await goiNgoai("/api/generate-note-external", { transcript: loiThoai });
      if (!d?.content) return;
      const tabId = `tab-doc-${Date.now()}`;
      handleUpdateSession({
        tabs: [
          ...currentSession.tabs,
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
      });
    } finally {
      setIsGeneratingNote(false);
    }
  };

  // Khởi tạo ca khám từ danh sách bệnh nhân
  const handleStartSessionWithPatient = (patient: Patient) => {
    const newId = `session-${Date.now()}`;
    const newSession: Session = {
      id: newId,
      patientIdentifier: patient.name,
      patientSubtitle: patient.identifier,
      date: `Hôm nay ${new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`,
      time: `${new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`,
      language: "Tiếng Việt",
      durationSeconds: 0,
      isRecording: false,
      transcript: `Ca khám bệnh nhân ${patient.name}. Lý do khám: ${patient.chiefComplaint || "Khám sức khỏe tổng quát"}.`,
      activeTabId: "tab-soap",
      tabs: [
        {
          id: "tab-transcript",
          title: "Lời thoại",
          type: "transcript",
          content: `Ca khám bệnh nhân ${patient.name}. Lý do khám: ${patient.chiefComplaint || "Khám sức khỏe tổng quát"}.`,
          isClosable: false,
        },
        {
          id: "tab-soap",
          title: "Bệnh án SOAP",
          type: "soap",
          templateStyle: "Goldilocks",
          content: `Chủ quan (S):\n- Lý do vào viện: ${patient.chiefComplaint}\n\nTiền sử bệnh (PMHx):\n- Chưa ghi nhận bất thường đặc biệt\n\nKhách quan (O):\n- Thể trạng bình thường\n\nĐánh giá (A):\n- Theo dõi lâm sàng\n\nKế hoạch (P):\n- Kê đơn và hướng dẫn theo dõi`,
          isClosable: false,
        },
      ],
    };

    setSessions([newSession, ...sessions]);
    setActiveSessionId(newId);
    setActiveView("scribe");
    setActiveNavigationItem("sessions");
  };

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
      {/* 1. Thanh điều hướng Taskbar (Phía trên với góc bo tròn mềm mại hoặc dạng thanh bên trái) */}
      <NavigationRail
        activeView={activeView}
        activeNavigationItem={activeNavigationItem}
        onSelectNavigationItem={handleSelectNavigationItem}
        onSelectView={handleSelectView}
        onCreateNewSession={handleCreateNewSession}
        position={taskbarPosition}
        onTogglePosition={() =>
          setTaskbarPosition((prev) => (prev === "top" ? "left" : "top"))
        }
        onOpenHelp={() => setMoTinhTrang(true)}
        nguoiDung={nguoiDung}
        onDangXuat={onDangXuat}
      />
      {moTinhTrang && <TinhTrangHeThong onClose={() => setMoTinhTrang(false)} />}

      {/* 2. Khung nhìn chính với bo góc tinh tế và đổ bóng nổi khối */}
      <main
        className={`flex-1 flex flex-col overflow-hidden min-h-0 min-w-0 ${
          taskbarPosition === "top"
            ? "mx-2.5 sm:mx-3 mb-2.5 rounded-2xl border border-[#BAE6FD]/70 bg-white shadow-[0_8px_30px_rgba(2,132,199,0.08),0_1px_3px_rgba(0,0,0,0.03)]"
            : ""
        }`}
      >
        {taskbarPosition === "left" && (
          <header className="h-14 shrink-0 flex items-center justify-between gap-3 border-b border-[#D9EAF3] bg-white/85 px-4 sm:px-5 lg:px-6">
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
          <div className="flex-1 flex overflow-hidden">
            {/* Sidebar danh sách ca khám */}
            <SessionsSidebar
              sessions={sessions}
              activeSessionId={activeSessionId}
              onSelectSession={(id) => {
                setActiveSessionId(id);
                // Màn hẹp: danh sách ca đè lên vùng soạn, chọn xong thì thu lại.
                if (window.innerWidth < 768) setIsSessionsSidebarCollapsed(true);
              }}
              onCreateSession={handleCreateNewSession}
              onDeleteSession={handleDeleteSession}
              isCollapsed={isSessionsSidebarCollapsed}
              onToggleCollapse={handleToggleSessionsSidebar}
            />

            {/* Khu vực soạn thảo & ghi âm trung tâm */}
            <div className="@container flex-1 flex flex-col min-w-0 bg-[#F0F7FA] h-full overflow-hidden">
              <ScribeHeader
                session={currentSession}
                onUpdateSession={handleUpdateSession}
                onDeleteSession={() => handleDeleteSession()}
                onCreateNewDocument={() => setIsTemplateModalOpen(true)}
                isRightDrawerOpen={isRightDrawerOpen}
                onToggleRightDrawer={handleToggleRightDrawer}
              />

              {/* Thanh các Tab tài liệu */}
              <DocumentTabs
                tabs={currentSession.tabs}
                activeTabId={currentSession.activeTabId}
                onSelectTab={handleSelectTab}
                onCloseTab={handleCloseTab}
                onOpenTemplateModal={() => setIsTemplateModalOpen(true)}
              />

              {/* Banner trạng thái đang phân tích & sinh văn bản AI (Ảnh 1 & 2) */}
              {isGeneratingNote && (
                <div className="bg-[#F0F9FF] border-b border-[#BAE6FD] px-3 @md:px-4 py-2 flex flex-wrap items-center justify-between gap-x-3 gap-y-1 text-xs text-[#0369A1] animate-in fade-in duration-200">
                  <div className="flex items-center gap-2">
                    <RefreshCw size={13} className="animate-spin text-[#0284C7]" />
                    <span className="font-medium">
                      {tienDoNhap
                        ? tienDoNhap.truoc > 0
                          ? `Đang chờ ${tienDoNhap.truoc} bản nháp khác tạo xong (máy chủ chỉ có một GPU)…`
                          : `Đang tạo bản nháp · ${Math.floor((Date.now() - tienDoNhap.batDau) / 60000)} phút ${Math.floor(
                              ((Date.now() - tienDoNhap.batDau) % 60000) / 1000,
                            )} giây (thường mất 3–4 phút). Có thể chuyển sang ca khác, bản nháp vẫn vào đúng ca này.`
                        : "Đang xử lý tạo hồ sơ... Bác sĩ có thể chuyển sang ca khám khác hoặc bắt đầu ca khám mới."}
                    </span>
                  </div>
                  <span className="text-[11px] text-[#0284C7] font-mono">Qwen3-4B · chạy tại chỗ · không gửi dữ liệu ra ngoài</span>
                </div>
              )}

              {/* Lỗi của dịch vụ: hiện thẳng, không nuốt vào console */}
              {apiError && (
                <div className="bg-[#FDE8E8] border-b border-[#F5C2C2] px-4 py-2 flex items-start justify-between gap-3 text-xs text-[#8C1D26]">
                  <span className="font-medium">{apiError}</span>
                  <button onClick={() => setApiError(null)} className="font-bold shrink-0">đóng</button>
                </div>
              )}

              {/* Có bản nháp thì mời sang màn Duyệt — đó mới là bước bác sĩ phải làm */}
              {noteMeta && (
                <div className="bg-[#E6F4F1] border-b border-[#BCE3DB] px-3 @md:px-4 py-2 flex flex-wrap items-center justify-between gap-x-3 gap-y-1.5 text-xs text-[#0D5F57]">
                  <span>
                    Bản nháp có <strong>{noteMeta.propositions.length}</strong> mệnh đề
                    {noteMeta.needsConfirmCount > 0 && <>, trong đó <strong>{noteMeta.needsConfirmCount}</strong> máy đưa sang mục cần bác sĩ xác nhận</>}.
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
                      onClick={() => (moDuyetBen ? setMoDuyetBen(false) : moNganDuyet())}
                      className={`px-2.5 py-1 rounded-lg font-semibold ${moDuyetBen ? "bg-white text-[#0D9488] border border-[#0D9488]" : "bg-[#0D9488] text-white"}`}
                      title="Duyệt ngay cạnh bản nháp; màn đầy đủ có dây nối mở từ nút trong ngăn duyệt"
                    >
                      {moDuyetBen ? "Đóng ngăn duyệt" : "Duyệt từng mệnh đề"}
                    </button>
                  </div>
                </div>
              )}

              {/* Công tắc mô hình ngoài — mặc định tắt; bật thì cảnh báo rõ dữ liệu đi đâu */}
              <div
                className={`px-3 @md:px-4 py-1.5 border-b flex items-center justify-between gap-3 text-[11px] ${
                  choPhepNgoai ? "bg-[#FDE8E8] border-[#F5C2C2] text-[#8C1D26]" : "bg-[#F8FBFC] border-[#E2ECE9] text-[#64748B]"
                }`}
              >
                <span className="min-w-0 line-clamp-2 @2xl:line-clamp-none">
                  {choPhepNgoai
                    ? "Đang cho phép gửi nội dung ca khám ra máy chủ của dịch vụ mô hình ngoài (mô hình thương mại) để sửa theo lời nhắc, hỏi về ca khám, gợi ý câu hỏi và làm bản so sánh. Khâu tách mệnh đề và bản nháp chính vẫn do Qwen3-4B của dự án làm."
                    : "Mô hình ngoài đang tắt: không có gì rời khỏi máy này. Bản chép dùng PhoWhisper, bản nháp dùng Qwen3-4B tại chỗ."}
                </span>
                <label className="flex items-center gap-1.5 shrink-0 font-semibold cursor-pointer">
                  <input
                    type="checkbox"
                    checked={choPhepNgoai}
                    onChange={(e) => setChoPhepNgoai(e.target.checked)}
                  />
                  Mô hình ngoài
                </label>
              </div>

              {/* Nội dung tab đang hiển thị (+ ngăn duyệt cạnh bản nháp khi mở) */}
              {moDuyetBen && noteMeta && (
                <div className="@4xl:hidden grid grid-cols-2 gap-0.5 p-0.5 mx-3 mt-2 rounded-lg bg-[#E0F2FE] border border-[#BAE6FD] text-[12px]" role="tablist">
                  {([["nhap", "Bản nháp"], ["duyet", `Duyệt${noteMeta.needsConfirmCount ? ` · ${noteMeta.needsConfirmCount} cần xác nhận` : ""}`]] as const).map(([id, chu]) => (
                    <button key={id} role="tab" aria-selected={xemHep === id} onClick={() => setXemHep(id)}
                      className={`py-1.5 rounded-md font-semibold ${xemHep === id ? "bg-white text-[#0369A1] shadow-sm" : "text-[#0C4A6E]/70"}`}>
                      {chu}
                    </button>
                  ))}
                </div>
              )}
              <div ref={vungGiuaRef} className="flex-1 flex flex-col @4xl:flex-row min-h-0 overflow-hidden">
              <div className={`flex-1 flex-col min-h-0 min-w-0 bg-[#F8FBFC] overflow-hidden relative ${
                moDuyetBen && noteMeta && xemHep === "duyet" ? "hidden @4xl:flex" : "flex"}`}>
                {currentTab?.type === "transcript" && (
                  <TranscriptView
                    transcript={currentSession.transcript}
                    onUpdateTranscript={handleUpdateTranscript}
                    isRecording={currentSession.isRecording}
                    audioUrl={currentSession.audioUrl}
                    onStartRecording={() => handleUpdateSession({ isRecording: true })}
                    onOpenTemplates={() => setIsTemplateModalOpen(true)}
                    onLoadSample={handleLoadSample}
                  />
                )}

                {currentTab?.type === "context" && (
                  <ContextView
                    tab={currentTab}
                    onUpdateContent={handleUpdateTabContent}
                  />
                )}

                {(currentTab?.type === "soap" ||
                  currentTab?.type === "leaflet" ||
                  currentTab?.type === "custom") && (
                  <NoteEditorView
                    tab={currentTab}
                    onUpdateContent={handleUpdateTabContent}
                    onRegenerateNote={handleRegenerateNoteStyle}
                    isGenerating={isGeneratingNote}
                    danhDau={
                      moDuyetBen && noteMeta
                        ? noteMeta.propositions.map((pp) => ({
                            id: pp.id,
                            text: pp.text,
                            textKhac: banSuaDuyet[pp.id] ? [banSuaDuyet[pp.id]] : undefined,
                            trangThai: trangThaiMD(pp, quyetDuyet[pp.id]),
                          }))
                        : undefined
                    }
                    chonId={moDuyetBen ? chonMD : null}
                    onChonMenhDe={chonTuBanNhap}
                  />
                )}
              </div>
              {moDuyetBen && noteMeta && (
                <div className={`flex-1 @4xl:flex-none @4xl:w-[380px] @6xl:w-[420px] min-h-0 ${xemHep === "nhap" ? "hidden @4xl:block" : "block"}`}>
                  <DuyetBenCanh
                    note={noteMeta}
                    quyet={quyetDuyet}
                    setQuyet={setQuyetDuyet}
                    banSua={banSuaDuyet}
                    setBanSua={setBanSuaDuyet}
                    chonId={chonMD}
                    onChon={chonTuNgan}
                    onMoToanMan={() => handleSelectNavigationItem("proof")}
                    onDong={() => setMoDuyetBen(false)}
                  />
                </div>
              )}
              </div>

              {/* Thanh nhập lệnh AI dưới đáy */}
              <BottomPromptBar
                onSubmitPrompt={handleBottomPrompt}
                isLoading={isGeneratingNote}
              />
            </div>

            {/* 3. Bảng phụ trợ bên phải: "Câu hỏi cho Người bệnh & Chứng cứ" */}
            <ClinicalEvidenceDrawer
              key={currentSession.id}
              isOpen={isRightDrawerOpen}
              onClose={() => setIsRightDrawerOpen(false)}
              chatHistory={evidenceChat}
              onSendMessage={handleSendEvidenceMessage}
              onNewChat={() => setEvidenceChat([])}
              isLoading={isEvidenceLoading}
              patientContext={currentSession.patientSubtitle}
              ruleQuestions={noteMeta?.questions || []}
              hasDraft={!!noteMeta}
              allowExternal={choPhepNgoai}
              hasMaterial={!!(currentSession.transcript.trim() || nguCanh().trim())}
              onSuggestQuestions={deXuatCauHoi}
              onAddToContext={themVaoNguCanh}
            />
          </div>
        )}

        {/* Câu hỏi làm rõ — sinh từ chính hội thoại, KHÔNG tra cứu y văn ngoài */}
        {activeView === "evidence" && (
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
        )}

        {/* Duyệt từng mệnh đề — dữ liệu thật từ dịch vụ tại chỗ */}
        {activeView === "verification" && (
          <VerificationView
            note={noteMeta}
            onBack={() => handleSelectNavigationItem("draft")}
            patientIdentifier={currentSession.patientIdentifier}
            allowExternal={choPhepNgoai}
            onAskExternalQuestions={deXuatCauHoi}
            quyetChung={quyetDuyet}
            setQuyetChung={setQuyetDuyet}
            banSuaChung={banSuaDuyet}
            setBanSuaChung={setBanSuaDuyet}
          />
        )}

        {/* Quản lý Bệnh nhân */}
        {activeView === "patients" && (
          <PatientsView onStartSessionWithPatient={handleStartSessionWithPatient} />
        )}

        {/* Nhiệm vụ Lâm sàng */}
        {activeView === "tasks" && <TasksView />}

        {/* Mẫu Bệnh án */}
        {activeView === "templates" && (
          <TemplatesView
            onUseTemplate={(tpl) => {
              handleSelectTemplate(tpl);
              setActiveView("scribe");
              setActiveNavigationItem("draft");
            }}
          />
        )}

        {activeView === "library" && (
          <section className="flex-1 min-w-0 overflow-y-auto bg-[#F8FBFC] px-5 py-6 lg:px-8 lg:py-8">
            <ThuVienYKhoa />
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
                        taskbarPosition === position ? "bg-white text-[#0874B9] shadow-sm" : "text-[#607C8E] hover:text-[#174F70]"
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
                    <h2 className="text-[14px] font-semibold text-[#174F70]">Mô hình ngoài</h2>
                    <p className="mt-1 text-[12px] leading-relaxed text-[#6C8494]">Có thể gửi nội dung ca khám tới mô hình ngoài. Bản nháp chính vẫn tạo tại chỗ.</p>
                  </div>
                  <label className="inline-flex cursor-pointer items-center gap-2 rounded-xl bg-[#F3F8FB] px-3 py-2 text-[12px] font-semibold text-[#345F79]">
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
