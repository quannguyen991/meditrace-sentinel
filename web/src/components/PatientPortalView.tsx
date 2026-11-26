import React, { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  Calendar,
  CheckCircle2,
  Clock,
  HeartPulse,
  Moon,
  Pill,
  ShieldCheck,
  Sun,
  Sunrise,
  Sunset,
  Utensils,
} from "lucide-react";

interface LichMuc {
  ten_thuoc: string;
  cach_dung: string;
}

interface PortalData {
  token: string;
  tenBenhNhan: string;
  chanDoan: string;
  lichUongThuoc: {
    sang: LichMuc[];
    trua: LichMuc[];
    chieu: LichMuc[];
    toi: LichMuc[];
    truoc_ngu?: LichMuc[];
  };
  thuocMoHoLich: Array<{ ten_thuoc: string; cach_dung: string; ly_do: string }>;
  tuongTacThucAn: Array<{ nguon: string; muc_do: string; noi_dung: string }>;
  dauHieuBaoDong: string[];
  cheDoSinhHoat: {
    nenAn: string[];
    kiengCu: string[];
    loiDan: string[];
  };
  ngayTaiKham: string;
  diaDiemTaiKham: string;
  chuKyHmac: string;
}

export interface PatientPortalViewProps {
  token?: string;
}

const DAU_HIEU_DO_NHANH = [
  "Khó thở / thở hụt hơi",
  "Đau tức ngực",
  "Sốt cao > 39°C không hạ",
  "Phát ban, sưng môi hoặc mí mắt",
  "Nôn ra máu hoặc đi ngoài phân đen",
  "Chóng mặt dữ dội / yếu liệt tay chân",
];

function layTokenTuUrl(propToken?: string): string {
  if (propToken && propToken.trim()) return propToken.trim();
  if (typeof window === "undefined") return "";
  const params = new URLSearchParams(window.location.search);
  const q = params.get("portal");
  if (q && q.trim()) return q.trim();
  const match = window.location.pathname.match(/\/benh-nhan\/([^/]+)/);
  return match ? decodeURIComponent(match[1]) : "";
}

export const PatientPortalView: React.FC<PatientPortalViewProps> = ({ token: propToken }) => {
  const token = useMemo(() => layTokenTuUrl(propToken), [propToken]);
  const [data, setData] = useState<PortalData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 48h / 7d check-in form state
  const [mocTheoDoi, setMocTheoDoi] = useState<"48h" | "7d">("48h");
  const [daUongDuThuoc, setDaUongDuThuoc] = useState<boolean>(true);
  const [mucDoMet, setMucDoMet] = useState<number>(2);
  const [dauHieuDoChon, setDauHieuDoChon] = useState<string[]>([]);
  const [trieuChungMoi, setTrieuChungMoi] = useState<string>("");
  const [submitting, setSubmitting] = useState(false);
  const [submitResult, setSubmitResult] = useState<{
    ok: boolean;
    redFlagDetected: boolean;
    taskCreated: boolean;
  } | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) {
      setLoading(false);
      setError("Thiếu mã hồ sơ cổng theo dõi người bệnh.");
      return;
    }
    let cancelled = false;
    setLoading(true);
    setError(null);

    fetch(`/api/benh-nhan-portal/${encodeURIComponent(token)}`)
      .then(async (res) => {
        const body = await res.json().catch(() => ({}));
        if (!res.ok) {
          throw new Error(body?.error || `Không tải được hồ sơ (mã ${res.status})`);
        }
        return body as PortalData;
      })
      .then((portal) => {
        if (!cancelled) setData(portal);
      })
      .catch((err: unknown) => {
        if (!cancelled) setError(err instanceof Error ? err.message : "Lỗi kết nối máy chủ");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [token]);

  const toggleDauHieu = (label: string) => {
    setDauHieuDoChon((prev) =>
      prev.includes(label) ? prev.filter((item) => item !== label) : [...prev, label]
    );
  };

  const handleSubmitBaoCao = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token || submitting) return;
    setSubmitting(true);
    setSubmitError(null);
    try {
      const res = await fetch(`/api/benh-nhan-portal/${encodeURIComponent(token)}/bao-cao`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          moc_theo_doi: mocTheoDoi,
          da_uong_du_thuoc: daUongDuThuoc,
          trieu_chung_moi: trieuChungMoi.trim(),
          muc_do_met: mucDoMet,
          co_dau_hieu_do: dauHieuDoChon.length > 0,
          dau_hieu_do_chon: dauHieuDoChon,
        }),
      });
      const body = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(body?.error || "Không gửi được báo cáo theo dõi");
      }
      setSubmitResult({
        ok: true,
        redFlagDetected: Boolean(body.redFlagDetected),
        taskCreated: Boolean(body.taskCreated),
      });
    } catch (err: unknown) {
      setSubmitError(err instanceof Error ? err.message : "Lỗi gửi báo cáo");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#F0F7FA] flex items-center justify-center p-6">
        <div className="bg-white rounded-2xl border border-sky-100 shadow-sm p-6 max-w-md w-full text-center space-y-2">
          <HeartPulse className="w-8 h-8 text-[#0284C7] mx-auto animate-pulse" />
          <p className="text-sm font-semibold text-slate-700">Đang tải Sổ tay Chăm sóc Người bệnh...</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-[#F0F7FA] flex items-center justify-center p-6">
        <div className="bg-white rounded-2xl border border-red-200 shadow-sm p-6 max-w-md w-full text-center space-y-3">
          <AlertTriangle className="w-9 h-9 text-red-600 mx-auto" />
          <h1 className="text-base font-bold text-slate-900">Không mở được Cổng Người bệnh</h1>
          <p className="text-sm text-slate-600">{error || "Liên kết không hợp lệ hoặc đã hết hạn."}</p>
        </div>
      </div>
    );
  }

  const slots: Array<{
    key: keyof PortalData["lichUongThuoc"];
    label: string;
    time: string;
    icon: React.ReactNode;
    accent: string;
  }> = [
    { key: "sang", label: "Buổi Sáng", time: "7h00 – 8h00", icon: <Sunrise className="w-4 h-4 text-amber-600" />, accent: "border-amber-200 bg-amber-50/60" },
    { key: "trua", label: "Buổi Trưa", time: "11h30 – 12h30", icon: <Sun className="w-4 h-4 text-orange-600" />, accent: "border-orange-200 bg-orange-50/60" },
    { key: "chieu", label: "Buổi Chiều", time: "16h30 – 17h30", icon: <Sunset className="w-4 h-4 text-sky-600" />, accent: "border-sky-200 bg-sky-50/60" },
    { key: "toi", label: "Buổi Tối", time: "19h00 – 20h30", icon: <Moon className="w-4 h-4 text-indigo-600" />, accent: "border-indigo-200 bg-indigo-50/60" },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#F0F9FF] via-white to-[#F8FAFC] text-slate-800 pb-12">
      <div className="max-w-2xl mx-auto px-4 pt-5 space-y-5">
        {/* Header người bệnh */}
        <header className="bg-white rounded-2xl border border-sky-200 shadow-sm p-5 space-y-3">
          <div className="flex items-start justify-between gap-3">
            <div>
              <span className="inline-flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-[#0369A1] bg-sky-50 border border-sky-200 px-2.5 py-0.5 rounded-full">
                <ShieldCheck className="w-3.5 h-3.5" />
                Cổng Đồng hành Người bệnh MediTrace
              </span>
              <h1 className="text-xl font-bold text-slate-900 mt-2">{data.tenBenhNhan}</h1>
              {data.chanDoan && (
                <p className="text-sm text-slate-600 mt-0.5">
                  Chẩn đoán: <span className="font-semibold text-slate-800">{data.chanDoan}</span>
                </p>
              )}
            </div>
            <div className="text-right text-[11px] font-mono text-slate-500 bg-slate-50 border border-slate-200 rounded-lg px-2 py-1">
              HMAC: {data.chuKyHmac.slice(0, 10)}
            </div>
          </div>

          <div className="flex flex-wrap gap-3 pt-2 border-t border-slate-100 text-xs text-slate-600">
            <span className="inline-flex items-center gap-1.5">
              <Calendar className="w-3.5 h-3.5 text-[#0284C7]" />
              Tái khám: <strong className="text-slate-800">{data.ngayTaiKham}</strong>
            </span>
            <span className="inline-flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-[#0284C7]" />
              {data.diaDiemTaiKham}
            </span>
          </div>
        </header>

        {/* Cảnh báo thuốc chưa rõ giờ uống */}
        {data.thuocMoHoLich.length > 0 && (
          <section className="bg-amber-50 border-2 border-amber-300 rounded-2xl p-4 space-y-2">
            <div className="flex items-center gap-2 text-amber-900 font-bold text-sm">
              <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0" />
              <span>Hỏi lại bác sĩ/dược sĩ giờ uống cho các thuốc sau:</span>
            </div>
            <ul className="space-y-1.5 text-sm text-amber-950">
              {data.thuocMoHoLich.map((m, i) => (
                <li key={i} className="bg-white/80 border border-amber-200 rounded-xl px-3 py-2">
                  <div className="font-semibold">{m.ten_thuoc}</div>
                  <div className="text-xs text-amber-800">{m.cach_dung}</div>
                </li>
              ))}
            </ul>
          </section>
        )}

        {/* Lịch uống thuốc 4 buổi */}
        <section className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5 space-y-3">
          <div className="flex items-center gap-2">
            <Pill className="w-5 h-5 text-[#0284C7]" />
            <h2 className="text-base font-bold text-slate-900">Lịch uống thuốc hàng ngày</h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {slots.map((slot) => {
              const items = data.lichUongThuoc[slot.key] || [];
              return (
                <div key={slot.key} className={`rounded-xl border p-3.5 space-y-2 ${slot.accent}`}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1.5 font-bold text-sm text-slate-900">
                      {slot.icon}
                      <span>{slot.label}</span>
                    </div>
                    <span className="text-[11px] font-medium text-slate-500">{slot.time}</span>
                  </div>
                  {items.length === 0 ? (
                    <p className="text-xs text-slate-400 italic">Không có thuốc trong buổi này</p>
                  ) : (
                    <ul className="space-y-1.5">
                      {items.map((t, idx) => (
                        <li key={idx} className="bg-white rounded-lg border border-slate-200/80 px-2.5 py-2 text-xs">
                          <div className="font-semibold text-slate-900">{t.ten_thuoc}</div>
                          <div className="text-slate-600 mt-0.5">{t.cach_dung}</div>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              );
            })}
          </div>
        </section>

        {/* Tương tác thực phẩm & chế độ sinh hoạt */}
        <section className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5 space-y-3">
          <div className="flex items-center gap-2">
            <Utensils className="w-5 h-5 text-emerald-600" />
            <h2 className="text-base font-bold text-slate-900">Lưu ý tương tác thuốc &amp; Dinh dưỡng</h2>
          </div>

          {data.tuongTacThucAn.length > 0 && (
            <div className="space-y-2">
              {data.tuongTacThucAn.map((tt, idx) => (
                <div
                  key={idx}
                  className="rounded-xl bg-sky-50 border border-sky-200 px-3.5 py-2.5 text-xs text-slate-800"
                >
                  <span className="font-bold text-[#0369A1]">Lưu ý an toàn: </span>
                  {tt.noi_dung}
                </div>
              ))}
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
            <div className="rounded-xl bg-emerald-50/60 border border-emerald-200 p-3 space-y-1">
              <div className="font-bold text-emerald-900">Nên ăn / sinh hoạt</div>
              <ul className="list-disc pl-4 space-y-1 text-emerald-950">
                {data.cheDoSinhHoat.nenAn.map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            </div>
            <div className="rounded-xl bg-rose-50/60 border border-rose-200 p-3 space-y-1">
              <div className="font-bold text-rose-900">Cần kiêng / tránh</div>
              <ul className="list-disc pl-4 space-y-1 text-rose-950">
                {data.cheDoSinhHoat.kiengCu.map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            </div>
          </div>
        </section>

        {/* Dấu hiệu báo động */}
        <section className="bg-red-50/80 rounded-2xl border border-red-200 p-5 space-y-2">
          <div className="flex items-center gap-2 text-red-800 font-bold text-sm">
            <AlertTriangle className="w-5 h-5 text-red-600" />
            <span>Dấu hiệu nguy hiểm cần đi khám / cấp cứu ngay</span>
          </div>
          <ul className="list-disc pl-5 space-y-1 text-xs text-red-950">
            {data.dauHieuBaoDong.map((rf, i) => (
              <li key={i}>{rf}</li>
            ))}
          </ul>
        </section>

        {/* Form theo dõi 48h / 7 ngày */}
        <section className="bg-white rounded-2xl border-2 border-sky-200 shadow-sm p-5 space-y-4">
          <div>
            <h2 className="text-base font-bold text-slate-900">Báo cáo theo dõi tại nhà (48 giờ / 7 ngày)</h2>
            <p className="text-xs text-slate-600 mt-0.5">
              Gửi tình trạng hiện tại để bác sĩ theo dõi kịp thời. Nếu có dấu hiệu đỏ, hệ thống sẽ ưu tiên báo ngay cho bác sĩ phụ trách.
            </p>
          </div>

          <form onSubmit={handleSubmitBaoCao} className="space-y-4">
            <div className="flex gap-2">
              {(["48h", "7d"] as const).map((moc) => (
                <button
                  key={moc}
                  type="button"
                  onClick={() => setMocTheoDoi(moc)}
                  className={`flex-1 py-2 rounded-xl text-xs font-bold border cursor-pointer transition-colors ${
                    mocTheoDoi === moc
                      ? "bg-[#0284C7] text-white border-[#0284C7]"
                      : "bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100"
                  }`}
                >
                  {moc === "48h" ? "Kiểm tra sau 48 giờ" : "Kiểm tra sau 7 ngày"}
                </button>
              ))}
            </div>

            <div className="space-y-1.5">
              <span className="text-xs font-semibold text-slate-800 block">Bác đã uống đủ thuốc theo lịch chưa?</span>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => setDaUongDuThuoc(true)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold border cursor-pointer ${
                    daUongDuThuoc ? "bg-emerald-600 text-white border-emerald-600" : "bg-white text-slate-700 border-slate-200"
                  }`}
                >
                  Đã uống đủ
                </button>
                <button
                  type="button"
                  onClick={() => setDaUongDuThuoc(false)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold border cursor-pointer ${
                    !daUongDuThuoc ? "bg-amber-600 text-white border-amber-600" : "bg-white text-slate-700 border-slate-200"
                  }`}
                >
                  Còn quên / chưa đủ
                </button>
              </div>
            </div>

            <div className="space-y-1">
              <div className="flex justify-between text-xs font-semibold text-slate-800">
                <span>Mức độ mệt mỏi (0 = khỏe, 10 = rất mệt)</span>
                <span className="text-[#0284C7] font-bold">{mucDoMet}/10</span>
              </div>
              <input
                type="range"
                min={0}
                max={10}
                value={mucDoMet}
                onChange={(e) => setMucDoMet(Number(e.target.value))}
                className="w-full accent-[#0284C7]"
              />
            </div>

            <div className="space-y-2">
              <span className="text-xs font-semibold text-slate-800 block">
                Chạm nhanh nếu có dấu hiệu bất thường (nếu có):
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {DAU_HIEU_DO_NHANH.map((item) => {
                  const checked = dauHieuDoChon.includes(item);
                  return (
                    <label
                      key={item}
                      className={`flex items-center gap-2 rounded-xl border px-3 py-2 text-xs cursor-pointer transition-colors ${
                        checked ? "bg-red-50 border-red-400 text-red-900 font-semibold" : "bg-slate-50 border-slate-200 text-slate-700"
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={() => toggleDauHieu(item)}
                        className="accent-red-600"
                      />
                      <span>{item}</span>
                    </label>
                  );
                })}
              </div>
            </div>

            <div className="space-y-1">
              <label className="text-xs font-semibold text-slate-800 block">
                Triệu chứng mới hoặc điều muốn nhắn bác sĩ:
              </label>
              <textarea
                rows={3}
                value={trieuChungMoi}
                onChange={(e) => setTrieuChungMoi(e.target.value)}
                placeholder="Ví dụ: Đỡ ho hơn, ngủ ngon, hoặc có mệt/khó thở..."
                className="w-full rounded-xl border border-slate-300 px-3 py-2 text-xs focus:outline-none focus:ring-2 focus:ring-sky-500"
              />
            </div>

            {submitError && (
              <div className="rounded-xl bg-red-50 border border-red-200 px-3 py-2 text-xs text-red-700">
                {submitError}
              </div>
            )}

            {submitResult && (
              <div
                className={`rounded-xl border px-3.5 py-3 text-xs space-y-1 ${
                  submitResult.redFlagDetected
                    ? "bg-red-50 border-red-300 text-red-900"
                    : "bg-emerald-50 border-emerald-300 text-emerald-900"
                }`}
              >
                <div className="flex items-center gap-1.5 font-bold">
                  {submitResult.redFlagDetected ? (
                    <AlertTriangle className="w-4 h-4 text-red-600" />
                  ) : (
                    <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  )}
                  <span>
                    {submitResult.redFlagDetected
                      ? "Đã ghi nhận DẤU HIỆU CẢNH BÁO ĐỎ và chuyển khẩn tới bác sĩ!"
                      : "Đã gửi báo cáo theo dõi thành công!"}
                  </span>
                </div>
                {submitResult.redFlagDetected && (
                  <p>
                    Nếu tình trạng nặng lên (khó thở, đau ngực, sốt cao không hạ), hãy đến cơ sở y tế gần nhất hoặc gọi cấp cứu 115 ngay lập tức.
                  </p>
                )}
              </div>
            )}

            <button
              type="submit"
              disabled={submitting}
              className="w-full py-2.5 rounded-xl bg-[#0284C7] hover:bg-[#0369A1] disabled:opacity-60 text-white text-sm font-bold cursor-pointer transition-colors"
            >
              {submitting ? "Đang gửi báo cáo..." : "Gửi báo cáo theo dõi"}
            </button>
          </form>
        </section>
      </div>
    </div>
  );
};
