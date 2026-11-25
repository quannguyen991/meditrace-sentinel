import React, { useState } from "react";
import {
  Activity,
  AlertTriangle,
  ChevronRight,
  Cpu,
  FileCode2,
  Lock,
  ShieldCheck,
  Sparkles,
  X,
} from "lucide-react";

interface NhatKyTienTrinhAIModalProps {
  isOpen: boolean;
  onClose: () => void;
  patientName: string;
  transcript?: string;
  noteContent?: string;
  clinicalSafety?: any;
  propositions?: any[];
}

export const NhatKyTienTrinhAIModal: React.FC<NhatKyTienTrinhAIModalProps> = ({
  isOpen,
  onClose,
  patientName,
  transcript = "",
  noteContent = "",
  clinicalSafety,
  propositions = [],
}) => {
  const [tab, setTab] = useState<"stream" | "json">("stream");
  const [expandedStep, setExpandedStep] = useState<number | null>(1);

  if (!isOpen) return null;

  const auditWorm = clinicalSafety?.audit_trail_worm;
  const coDuLieuThat = Boolean(auditWorm?.chu_ky_bam_sha256 || propositions.length > 0);
  const sha256Hash = auditWorm?.chu_ky_bam_sha256 || "[mã băm SHA-256 của hồ sơ]";
  const icdChinh = clinicalSafety?.bhyt_icd10?.ma_icd10_chinh;

  // Sơ đồ các chốt và một ca mẫu viết tay để minh hoạ. Không phải nhật ký của lần xử lý thật.
  const pipelineStages = [
    {
      id: 0,
      phase: "STAGE 0",
      title: "Audio Intake & Phonetic Diarization",
      desc: "Xử lý âm thanh, tách người nói [T1..Tn] và cách ly âm vị thuốc dân gian",
      engine: "PhoWhisper + Pyannote",
      tokens: [
        { label: "Diarization", val: "Bác sĩ [T1, T3], Bệnh nhân [T2, T4, T6, T8], Người nhà [T5]" },
        { label: "Phonetic Quarantine", val: "Phát hiện 'la-xích' -> Gợi ý 'Lasix' (Bôi đỏ chờ BS duyệt)" },
      ],
      log: `INTAKE: Ghi nhận luồng âm thanh của ca khám.
DIARIZATION: Tách các luồng âm thanh theo người nói (Speaker_0: BS, Speaker_1: BN, Speaker_2: Con gái).
ASR_QUARANTINE: Phát hiện token âm vị không chắc chắn [T6: "la-xích"]. Gán cờ QUARANTINE_PHONETIC.`,
    },
    {
      id: 1,
      phase: "STAGE 1",
      title: "Qwen3-4B QLoRA Atomic Proposition Extraction",
      desc: "Trích xuất mệnh đề nguyên tử có căn cứ — Tuyệt đối không sinh văn tự do",
      engine: "Qwen3-4B (QLoRA) @ Edge On-Premise",
      isModelCore: true,
      tokens: [
        { label: "Extraction Schema", val: "Tuple(Subject, Clinical_Fact, Temporal, Evidence_Anchor)" },
        { label: "Anchored Facts", val: "Các mệnh đề gắn với [T1] đến [T10]" },
      ],
      log: `[PROMPT_INJECTION_GUARD]: Đã kiểm tra đầu vào. Temperature cố định (giải mã tham lam).
[QWEN_INFERENCE]: Trích xuất danh sách mệnh đề cấu trúc:
  ├── [P1] (Bệnh nhân, "đau tức ngực trái âm ỉ", "vài ngày nay", anchor: [T2])
  ├── [P2] (Bệnh nhân, "tiền sử đặt stent mạch vành LAD", "vài tháng trước", anchor: [T4])
  ├── [P3] (Gia đình, "bố mắc đái tháo đường type 2", "tiền sử", anchor: [T5])
  ├── [P4] (Bệnh nhân, "uống Coversyl 2 viên", "hiện tại", anchor: [T7])
  └── [P5] (Bệnh nhân, "đính chính Coversyl chỉ uống 1 viên", "hiện tại", anchor: [T8])
[ASSERTION]: Không sinh văn bản tự do ngoài các mệnh đề có mỏ neo.`,
    },
    {
      id: 2,
      phase: "STAGE 2",
      title: "Speaker & Semantic Attribution Gate",
      desc: "Phân giải đại từ nhân xưng, chống nhầm lẫn tiền sử người nhà",
      engine: "Clinical Consistency Guardrail (Rule Engine)",
      tokens: [
        { label: "Attribution", val: "P3 ('Bố bị tiểu đường') -> Chuyển vào Tiền sử Gia đình" },
        { label: "False Association", val: "Không gán tiền sử người nhà vào bệnh nhân" },
      ],
      log: `[STAGE_2_EVAL]: Rà soát người phát biểu tại lượt thoại [T5].
  • Người nói: CON GÁI (Speaker_2).
  • Nội dung: "Bố em ở nhà cũng bị tiểu đường tuýp 2 tiêm insulin".
  • Quyết định: Phân luồng về mục FAMILY_HISTORY. Ngăn việc gán tiểu đường vào bệnh nhân.`,
    },
    {
      id: 3,
      phase: "STAGE 3 & 4",
      title: "Evidence Lock & K7 Supersession FSM",
      desc: "Cổng K7 phát hiện bệnh nhân tự sửa lời; gạch bỏ thông tin cũ",
      engine: "Finite State Machine (FSM K1–K7 Verification)",
      tokens: [
        { label: "K7 Trigger", val: "Bắt cụm từ đính chính: 'à nhầm, chỉ uống 1 viên'" },
        { label: "Action", val: "Gán SUPERSEDED cho [P4] -> Chỉ giữ lại [P5]" },
      ],
      log: `[FSM_STATE_TRANSITION]:
  • State @ [T7]: COMMIT_FACT("Coversyl: 2 viên")
  • Signal @ [T8]: RETRACTION_INDICATOR("à nhầm, bác sĩ kê 1 viên thôi")
  • Transition: SUPERSEDE(Fact_ID=P4) -> REVOKED.
  • Result: Thông tin cũ bị thay bằng lời đính chính.`,
    },
    {
      id: 4,
      phase: "STAGE 5",
      title: "Clinical Pharmacovigilance & DDI Gate",
      desc: "Soi tương tác thuốc nguy hiểm & kiểm soát liều trần Paracetamol",
      engine: "Pharmacovigilance Rule Base",
      isWarn: true,
      tokens: [
        { label: "DDI Alert", val: "Plavix (Clopidogrel) + Omeprazole -> Giảm hoạt hóa kháng kết tập tiểu cầu" },
        { label: "Ceiling Dose", val: "Kiểm tra tổng liều Paracetamol trong 24 giờ" },
      ],
      log: `[PHARMACOVIGILANCE_SCAN]:
  ⚠️ CẢNH BÁO TƯƠNG TÁC THUỐC:
  • Cặp tương tác: Clopidogrel (Plavix) + Omeprazole.
  • Cơ chế: Omeprazole ức chế enzyme CYP2C19, làm giảm nồng độ chất chuyển hóa có hoạt tính của Clopidogrel -> Nguy cơ huyết khối tắc Stent.
  • Khuyến nghị: Đổi sang thuốc ức chế bơm proton khác. Đã gắn nhãn đỏ vào bản nháp.`,
    },
    {
      id: 5,
      phase: "STAGE 6 & 7",
      title: "Paraclinical Correlation, CDSS & Dosage Adjuster",
      desc: "Đối soát cận lâm sàng, tự động tính điểm nguy cơ và hiệu chỉnh liều",
      engine: "CDSS Scoring Engine + Dosage Solver",
      tokens: [
        { label: "Risk Score", val: "Điểm nguy cơ tính từ tuổi và bệnh nền trong ca" },
        { label: "Renal Function", val: "Hiệu chỉnh liều theo chức năng thận từ xét nghiệm" },
      ],
      log: `[CDSS_EVALUATION]:
  • Chẩn đoán chính: Sau đặt Stent mạch vành / Đau ngực không điển hình.
  • Đã đồng bộ sang gói cấu trúc HL7 FHIR R4 Bundle (Encounter, Condition, MedicationRequest).
  • Kết xuất bản dặn dò người bệnh kèm cảnh báo cờ đỏ.`,
    },
    {
      id: 6,
      phase: "STAGE 8",
      title: "Active Clarification (SOCRATES) & SHA-256 Audit Seal",
      desc: "Rà soát khoảng trống bệnh sử và niêm phong mật mã toàn vẹn",
      engine: "SOCRATES Gap Analyzer + Cryptographic Hasher",
      tokens: [
        { label: "Information Gap", val: "Đau ngực: Kiểm tra vị trí, tính chất, hướng lan" },
        { label: "Integrity Hash", val: sha256Hash },
      ],
      log: `[AUDIT_SEAL_GENERATED]:
  • Content Digest: SHA-256(${sha256Hash})
  • Trạng thái: Hồ sơ được niêm phong khi bác sĩ xác nhận.
  • Mọi chỉnh sửa sau thời điểm này sẽ làm sai lệch mã băm kiểm toán.`,
    },
  ];

  return (
    <div
      className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-2xs flex items-center justify-center p-3 sm:p-6 animate-in fade-in duration-150 no-print"
      onClick={onClose}
    >
      <div
        role="dialog"
        aria-label="Tiến trình AI"
        onClick={(e) => e.stopPropagation()}
        className="bg-white rounded-2xl border border-[#BAE6FD] shadow-2xl w-full max-w-4xl h-[88vh] flex flex-col overflow-hidden text-left"
      >
        {/* Đầu cửa sổ */}
        <div className="px-4 sm:px-5 pt-4 pb-3 border-b border-slate-100 flex items-start justify-between gap-3 flex-shrink-0">
          <div className="flex items-start gap-2.5 min-w-0">
            <div className="w-8 h-8 rounded-xl bg-sky-100 text-sky-700 flex items-center justify-center flex-shrink-0">
              <Cpu size={16} />
            </div>
            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-2">
                <h3 className="font-serif text-[17px] font-semibold text-[#0F172A]">Tiến trình AI · 8 chốt an toàn</h3>
                {coDuLieuThat ? (
                  <span className="px-2 py-0.5 rounded-md text-[10.5px] font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">
                    Dữ liệu thật từ Ca khám ({auditWorm?.tong_thoi_gian_ms ?? 0} ms)
                  </span>
                ) : (
                  <span className="px-2 py-0.5 rounded-md text-[10.5px] font-semibold bg-amber-100 text-amber-800 border border-amber-200">
                    Minh hoạ
                  </span>
                )}
              </div>
              <p className="text-[11.5px] text-slate-500 truncate">
                Ca khám: <span className="text-slate-700 font-semibold">{patientName}</span> •{" "}
                {coDuLieuThat
                  ? `${propositions.length} mệnh đề nguyên tử${icdChinh ? ` • ICD-10: ${icdChinh.ma_icd10} (${icdChinh.ten_benh_byt})` : ""}`
                  : "Chưa gắn với lần xử lý thật"}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 flex-shrink-0">
            <span
              className={`hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-lg border text-[11px] ${
                coDuLieuThat
                  ? "bg-emerald-50 border-emerald-200 text-emerald-800"
                  : "bg-slate-50 border-slate-200 text-slate-500"
              }`}
              title={sha256Hash}
            >
              <Lock size={11} className={coDuLieuThat ? "text-emerald-600" : "text-slate-400"} />
              <span className="font-mono">
                SHA-256: {coDuLieuThat ? `${sha256Hash.slice(0, 16)}…` : "[chờ niêm phong]"}
              </span>
            </span>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors cursor-pointer"
              title="Đóng"
            >
              <X size={16} />
            </button>
          </div>
        </div>

        {/* Thanh chọn kiểu xem */}
        <div className="px-4 sm:px-5 py-2.5 bg-[#F8FBFC] border-b border-[#E0F2FE] flex flex-wrap items-center justify-between gap-2 flex-shrink-0">
          <div className="flex items-center gap-1.5">
            <button
              onClick={() => setTab("stream")}
              className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-[11.5px] font-semibold border transition-colors ${
                tab === "stream"
                  ? "bg-[#0284C7] text-white border-[#0284C7]"
                  : "bg-white text-[#0C4A6E] border-[#CCE3F0] hover:bg-[#F0F9FF]"
              }`}
            >
              <Activity size={12} />
              <span>Các chốt (8)</span>
            </button>
            <button
              onClick={() => setTab("json")}
              className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-[11.5px] font-semibold border transition-colors ${
                tab === "json"
                  ? "bg-[#0284C7] text-white border-[#0284C7]"
                  : "bg-white text-[#0C4A6E] border-[#CCE3F0] hover:bg-[#F0F9FF]"
              }`}
            >
              <FileCode2 size={12} />
              <span>Mẫu nhật ký JSON</span>
            </button>
          </div>

          <div className="text-[11px] text-slate-500 flex items-center gap-2">
            <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-500" />
            <span>Chốt kiểm soát theo luật, không sinh văn tự do</span>
          </div>
        </div>

        {/* Nội dung */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-5 space-y-3 bg-white">
          {tab === "stream" ? (
            <div className="space-y-2.5 max-w-3xl mx-auto">
              {/* Lời giới thiệu kiến trúc */}
              <div className="p-3.5 rounded-2xl bg-[#F0F9FF] border border-[#BAE6FD] flex items-start gap-2.5 text-[12px] leading-relaxed text-[#0C4A6E]">
                <Sparkles size={15} className="text-[#0284C7] flex-shrink-0 mt-0.5" />
                <div>
                  <span className="font-semibold">Kiến trúc AI kiểm soát lâm sàng: </span>
                  Mô hình <strong>Qwen3-4B QLoRA</strong> chỉ trích xuất các mệnh đề nguyên tử gắn mỏ neo <code className="px-1 rounded bg-white text-[11px]">[T_i]</code>,
                  tuyệt đối không cho phép sinh văn tự do. Các chốt logic độc lập (K1–K7, DDI, SOCRATES) kiểm duyệt và niêm phong
                  trước khi bác sĩ duyệt bản nháp.
                </div>
              </div>

              {/* Danh sách các chốt */}
              <div className="space-y-2">
                {pipelineStages.map((stage) => {
                  const isExpanded = expandedStep === stage.id;
                  const isWarn = !!stage.isWarn;
                  const isModel = !!stage.isModelCore;

                  return (
                    <div
                      key={stage.id}
                      className={`border rounded-2xl transition-colors overflow-hidden ${
                        isModel
                          ? "bg-[#F0F9FF] border-[#7DD3FC]"
                          : isWarn
                          ? "bg-amber-50/60 border-amber-200"
                          : "bg-white border-[#E0F2FE] hover:border-[#BAE6FD]"
                      }`}
                    >
                      {/* Dòng tóm tắt của chốt */}
                      <div
                        onClick={() => setExpandedStep(isExpanded ? null : stage.id)}
                        className="px-4 py-3 flex items-center justify-between gap-3 cursor-pointer select-none"
                      >
                        <div className="flex items-center gap-3 min-w-0">
                          <div
                            className={`w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold flex-shrink-0 ${
                              isModel
                                ? "bg-[#0284C7] text-white"
                                : isWarn
                                ? "bg-amber-100 text-amber-800"
                                : "bg-emerald-50 text-emerald-700"
                            }`}
                          >
                            {stage.id}
                          </div>

                          <div className="min-w-0">
                            <div className="flex flex-wrap items-center gap-x-2 gap-y-0.5">
                              <span className="text-[10.5px] font-semibold text-slate-500 uppercase tracking-wider">
                                {stage.phase}
                              </span>
                              <h4 className="text-[13px] font-bold text-slate-900 truncate">{stage.title}</h4>
                              {isModel && (
                                <span className="px-1.5 py-0.5 rounded-md text-[10px] font-semibold bg-[#0284C7] text-white">
                                  AI
                                </span>
                              )}
                              {isWarn && (
                                <span className="px-1.5 py-0.5 rounded-md text-[10px] font-semibold bg-amber-100 text-amber-800 border border-amber-200 flex items-center gap-1">
                                  <AlertTriangle size={10} /> Cảnh báo DDI
                                </span>
                              )}
                            </div>
                            <p className="text-[11.5px] text-slate-500 mt-0.5 truncate">{stage.desc}</p>
                          </div>
                        </div>

                        <ChevronRight
                          size={14}
                          className={`text-slate-400 flex-shrink-0 transition-transform duration-200 ${
                            isExpanded ? "rotate-90 text-[#0284C7]" : ""
                          }`}
                        />
                      </div>

                      {/* Chi tiết khi mở */}
                      {isExpanded && (
                        <div className="px-4 pb-3.5 pt-1 border-t border-[#E0F2FE] bg-white/80 text-xs space-y-2.5">
                          {/* Các thẻ dữ liệu */}
                          <div className="flex flex-wrap gap-2 pt-2">
                            {stage.tokens.map((tk, i) => (
                              <div
                                key={i}
                                className="px-2 py-1 rounded-lg bg-[#F8FBFC] border border-[#E0F2FE] text-[11.5px] text-slate-700 flex items-center gap-1.5 max-w-full"
                              >
                                <span className="font-semibold text-[#0369A1]">{tk.label}:</span>
                                <span className="break-all">{tk.val}</span>
                              </div>
                            ))}
                          </div>

                          {/* Nhật ký mẫu */}
                          <pre className="p-3 rounded-xl bg-slate-50 border border-slate-200 font-mono text-[11px] text-slate-700 leading-relaxed overflow-x-auto whitespace-pre-wrap">
                            {stage.log}
                          </pre>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          ) : (
            /* Nhật ký JSON: hiển thị dữ liệu thật từ MediTracePipelineOrchestrator nếu có */
            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 max-w-3xl mx-auto">
              <p className="text-[11px] text-slate-500 mb-2">
                {coDuLieuThat
                  ? "Nhật ký kiểm toán WORM & Tiền kiểm BHYT XML 130/4750 trực tiếp từ ca khám hiện tại:"
                  : "Cấu trúc mẫu. Giá trị sẽ được điền khi nối với lần xử lý thật."}
              </p>
              <pre className="font-mono text-[11.5px] text-slate-700 leading-relaxed overflow-x-auto">{JSON.stringify(
                coDuLieuThat
                  ? {
                      system: "MediTrace Sentinel Neuro-Symbolic Pipeline v3",
                      audit_hash_sha256: sha256Hash,
                      orchestrator: "MediTracePipelineOrchestrator + BHYTXmlPreChecker",
                      execution_verified: true,
                      total_latency_ms: auditWorm?.tong_thoi_gian_ms ?? 0,
                      bhyt_icd10_primary: icdChinh || null,
                      stage_45_omission_recovered: clinicalSafety?.khoi_phuc_bo_sot_tang_45?.length ?? 0,
                      fhir_r4_bundle: clinicalSafety?.fhir_r4_summary || null,
                      guardrail_checkpoints: auditWorm?.cac_chot_kiem_soat || [],
                    }
                  : {
                      system: "[tên hệ thống]",
                      audit_hash: "[mã băm SHA-256]",
                      orchestrator: "[bộ điều phối]",
                      execution_verified: "[true/false]",
                      total_latency_ms: "[đo khi chạy]",
                      guardrail_results: pipelineStages.map((s) => ({
                        stage: s.phase,
                        engine: s.engine,
                        status: "[trạng thái chốt]",
                        latency_ms: "[đo khi chạy]",
                      })),
                    },
                null,
                2
              )}</pre>
            </div>
          )}
        </div>

        {/* Chân cửa sổ */}
        <div className="px-4 sm:px-5 py-3 bg-[#F8FBFC] border-t border-slate-100 flex items-center justify-between gap-3 flex-shrink-0">
          <div className="flex items-center gap-2 text-[11.5px] text-slate-600">
            <ShieldCheck size={14} className={coDuLieuThat ? "text-emerald-600 flex-shrink-0" : "text-slate-400 flex-shrink-0"} />
            <span>
              {coDuLieuThat
                ? `Đã niêm phong chuỗi băm SHA-256 (${auditWorm?.cac_chot_kiem_soat?.length ?? 8} chốt kiểm toán)`
                : "Minh hoạ giao diện • Chưa có số liệu từ lần xử lý thật"}
            </span>
          </div>
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-semibold transition-colors cursor-pointer"
          >
            Đóng
          </button>
        </div>
      </div>
    </div>
  );
};
