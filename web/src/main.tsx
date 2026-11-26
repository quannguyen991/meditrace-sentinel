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
