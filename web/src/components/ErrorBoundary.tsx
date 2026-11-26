import React from "react";
import { AlertTriangle, RotateCcw, EyeOff } from "lucide-react";

interface ErrorBoundaryProps {
  children: React.ReactNode;
  /** Tiêu đề hiển thị khi vùng giao diện gặp sự cố. */
  title?: string;
  /** Mô tả ngắn gọn cho bác sĩ. */
  description?: string;
  /** Tự động khôi phục khi các khoá này thay đổi (ví dụ đổi ca khám hoặc đổi màn hình). */
  resetKeys?: unknown[];
  /** Gọi khi bác sĩ bấm "Thử lại". */
  onRetry?: () => void;
  /** Gọi khi bác sĩ bấm "Bỏ qua phần lỗi" (ví dụ đóng ngăn bên hoặc về khung soạn chính). */
  onDismiss?: () => void;
  /** Cho phép ẩn hẳn phần lỗi ngay tại chỗ nếu không truyền `onDismiss`. */
  allowDismissInline?: boolean;
  /** Giao diện gọn cho ngăn bên / thành phần nhỏ. */
  compact?: boolean;
}

interface ErrorBoundaryState {
  hasError: boolean;
  dismissed: boolean;
  error: Error | null;
}

function cungDanhSachKhoa(a?: unknown[], b?: unknown[]): boolean {
  if (a === b) return true;
  if (!a || !b || a.length !== b.length) return false;
  for (let i = 0; i < a.length; i++) {
    if (!Object.is(a[i], b[i])) return false;
  }
  return true;
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  declare props: Readonly<ErrorBoundaryProps>;
  state: ErrorBoundaryState = {
    hasError: false,
    dismissed: false,
    error: null,
  };

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return { hasError: true, dismissed: false, error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo): void {
    console.error("[MediTrace ErrorBoundary]", error, info?.componentStack);
  }

  componentDidUpdate(prevProps: ErrorBoundaryProps): void {
    if (
      (this.state.hasError || this.state.dismissed) &&
      !cungDanhSachKhoa(prevProps.resetKeys, this.props.resetKeys)
    ) {
      this.setState({ hasError: false, dismissed: false, error: null });
    }
  }

  private handleRetry = () => {
    this.setState({ hasError: false, dismissed: false, error: null });
    this.props.onRetry?.();
  };

  private handleDismiss = () => {
    if (this.props.onDismiss) {
      this.setState({ hasError: false, dismissed: false, error: null });
      this.props.onDismiss();
    } else {
      this.setState({ dismissed: true });
    }
  };

  render(): React.ReactNode {
    if (this.state.dismissed) return null;

    if (!this.state.hasError) {
      return this.props.children;
    }

    const {
      title = "Khung hiển thị gặp sự cố ngoài dự kiến",
      description = "Dữ liệu ca khám, lời thoại và bản ghi âm cục bộ vẫn an toàn. Bác sĩ có thể bấm Thử lại hoặc bỏ qua phần lỗi để tiếp tục làm việc.",
      compact = false,
      onDismiss,
      allowDismissInline = true,
    } = this.props;

    const showDismiss = Boolean(onDismiss || allowDismissInline);

    return (
      <div
        role="alert"
        className={`flex-1 flex items-center justify-center bg-[#F0F7FA] ${
          compact ? "p-3" : "p-6 min-h-[240px]"
        } no-print`}
      >
        <div
          className={`w-full ${
            compact ? "max-w-sm p-4" : "max-w-lg p-6"
          } rounded-2xl border border-[#BAE6FD] bg-white shadow-tactile-doctor-card text-left space-y-3.5`}
        >
          <div className="flex items-start gap-3">
            <div className="w-9 h-9 rounded-xl bg-[#FEF9E7] border border-[#F5E6B8] text-[#B45309] flex items-center justify-center flex-shrink-0">
              <AlertTriangle size={18} />
            </div>
            <div className="min-w-0 flex-1">
              <h2 className="font-serif text-base sm:text-lg font-bold text-[#0F172A] leading-snug">
                {title}
              </h2>
              <p className="mt-1 text-xs leading-relaxed text-[#475569]">{description}</p>
            </div>
          </div>

          {this.state.error?.message && (
            <div className="rounded-xl border border-[#F5C2C2] bg-[#FFF5F5] px-3 py-2 text-[11.5px] font-mono text-[#991B1B] break-words">
              {this.state.error.message}
            </div>
          )}

          <div className="flex flex-wrap items-center gap-2 pt-1">
            <button
              type="button"
              onClick={this.handleRetry}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-[#0284C7] hover:bg-[#0369A1] text-white text-xs font-semibold shadow-tactile-doctor transition-all cursor-pointer"
            >
              <RotateCcw size={13} />
              <span>Thử lại</span>
            </button>

            {showDismiss && (
              <button
                type="button"
                onClick={this.handleDismiss}
                className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl border border-[#BAE6FD] bg-white hover:bg-[#F0F9FF] text-[#0C4A6E] text-xs font-semibold shadow-tactile-doctor-pill transition-all cursor-pointer"
              >
                <EyeOff size={13} className="text-[#0284C7]" />
                <span>Bỏ qua phần lỗi</span>
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }
}
