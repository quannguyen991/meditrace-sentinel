import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { ErrorBoundary } from "./components/ErrorBoundary";
import Goc from "./Goc.tsx";
import "./index.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ErrorBoundary
      title="Không thể khởi tạo giao diện MediTrace"
      description="Đã xảy ra lỗi ngoài dự kiến ở tầng gốc giao diện. Bấm Thử lại để tải lại ứng dụng."
      allowDismissInline={false}
    >
      <Goc />
    </ErrorBoundary>
  </StrictMode>,
);

// Sau khi máy chủ đổi bản build, trang đang mở có thể đòi tệp cũ không còn nữa: tải lại một lần.
window.addEventListener("vite:preloadError", (e) => {
  try {
    const da = sessionStorage.getItem("mt-tai-lai-ban-moi");
    if (da && Date.now() - Number(da) < 30_000) return;
    sessionStorage.setItem("mt-tai-lai-ban-moi", String(Date.now()));
  } catch {}
  e.preventDefault();
  window.location.reload();
});
