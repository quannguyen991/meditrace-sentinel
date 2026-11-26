import type express from "express";
import fs from "fs";
import { AsyncLocalStorage } from "node:async_hooks";
import { anDanhVanBanNgoai, khoiPhucPII } from "../an-danh-ngoai";
import { ngoaiBat } from "../tro-ly/cai-dat-tro-ly";
import { loiCongKhai, traLoi } from "./dung-chung";

function docTep(duong: string) {
  try {
    return fs.readFileSync(duong, "utf-8").trim();
  } catch {
    return "";
  }
}

export const NGOAI = {
  base: (process.env.AIBOX_BASE || docTep(process.env.AIBOX_BASE_FILE || "D:/Claude/.secrets/aibox-home.base"))
    .replace(/\/$/, ""),
  key: process.env.AIBOX_KEY || docTep(process.env.AIBOX_KEY_FILE || "D:/Claude/.secrets/aibox-home.key"),
  model: process.env.AIBOX_MODEL || "qwen3.8-flash",
  // Tự giới thiệu đúng là máy chủ MediTrace, không giả trình duyệt.
  ua: "MediTrace-may-chu/1",
};

/* ------------------------------------------------------------------ cổng kiểm soát chung cho MỌI lời gọi ngoài */

/** Người dùng của lời gọi hiện tại (cho việc nền như trợ lý, nơi không có `req`). */
const nguCanhNguoiDung = new AsyncLocalStorage<{ uid: number | null }>();
export function chayVoiNguoiDung<T>(uid: number | null | undefined, viec: () => T): T {
  return nguCanhNguoiDung.run({ uid: typeof uid === "number" ? uid : null }, viec);
}

/** Công tắc quản trị `tro_ly_ngoai` (hoặc env MEDITRACE_TRO_LY_NGOAI=tat) áp cho mọi đường ra mô hình ngoài. */
async function ngoaiDangBat(): Promise<boolean> {
  const { db } = await import("../csdl");
  return ngoaiBat(db, process.env);
}

function loiNgoaiBiTat(): Error {
  return loiCongKhai(
    "Quản trị viên đã tắt đường gửi ra mô hình ngoài cho toàn hệ thống. Dùng chức năng chạy tại chỗ.",
    403,
    "ngoai_bi_tat",
  );
}

const demNgoai = new Map<string, { moc: number[]; ngay: string; soNgay: number }>();
const soDuong = (v: string | undefined, macDinh: number) => {
  const n = Number(v);
  return Number.isInteger(n) && n > 0 ? n : macDinh;
};

/** Giới hạn mỗi người dùng: MEDITRACE_NGOAI_TOI_DA_PHUT lượt/phút (mặc định 10), MEDITRACE_NGOAI_TOI_DA_NGAY lượt/ngày (mặc định 200). */
export function kiemHanMucNgoai(uid: number | null, bay = Date.now()): void {
  const khoa = uid === null ? "khong_ro" : String(uid);
  const ngay = new Date(bay).toISOString().slice(0, 10);
  const toiDaPhut = soDuong(process.env.MEDITRACE_NGOAI_TOI_DA_PHUT, 10);
  const toiDaNgay = soDuong(process.env.MEDITRACE_NGOAI_TOI_DA_NGAY, 200);
  const dem = demNgoai.get(khoa) ?? { moc: [], ngay, soNgay: 0 };
  if (dem.ngay !== ngay) {
    dem.ngay = ngay;
    dem.soNgay = 0;
  }
  dem.moc = dem.moc.filter((t) => bay - t < 60_000);
  if (dem.moc.length >= toiDaPhut || dem.soNgay >= toiDaNgay) {
    demNgoai.set(khoa, dem);
    throw loiCongKhai(
      dem.soNgay >= toiDaNgay
        ? `Đã dùng hết ${toiDaNgay} lượt gọi mô hình ngoài hôm nay. Thử lại vào ngày mai hoặc dùng chức năng tại chỗ.`
        : `Gọi mô hình ngoài quá ${toiDaPhut} lượt/phút. Chờ một phút rồi thử lại.`,
      429,
      "qua_gioi_han_ngoai",
    );
  }
  dem.moc.push(bay);
  dem.soNgay++;
  demNgoai.set(khoa, dem);
}

export function datLaiHanMucNgoai(): void {
  demNgoai.clear();
}

/** Chặn sớm ở đầu route: bác sĩ phải bật công tắc ở giao diện VÀ quản trị chưa tắt đường ngoài. */
export async function chanNeuChuaChoPhep(req: express.Request) {
  if (!(await ngoaiDangBat())) throw loiNgoaiBiTat();
  if (req.body?.allowExternal !== true) {
    const e: any = new Error(
      "Việc này cần mô hình ngoài (mô hình thương mại). Bật công tắc “Cho phép gửi ra mô hình ngoài” trước — " +
        "nội dung ca khám (đã che tên, ngày sinh, địa chỉ, số điện thoại, mã hồ sơ) sẽ được gửi ra dịch vụ mô hình ngoài.",
    );
    e.status = 403;
    e.code = "chua_cho_phep_ngoai";
    throw e;
  }
  if (!NGOAI.key || !NGOAI.base) {
    throw loiCongKhai("Chưa cấu hình cổng mô hình ngoài. Liên hệ quản trị viên.", 503, "chua_cau_hinh_ngoai");
  }
}

/**
 * Một lượt gọi chat completions — lối ra DUY NHẤT tới mô hình ngoài. Trước khi gửi luôn:
 * (a) kiểm công tắc quản trị, (b) giới hạn lượt theo người dùng, (c) che định danh và kiểm lại phần còn sót —
 * còn định danh thì từ chối (422 `con_danh_tinh`). Giới hạn token để không tiêu tiền ngoài ý muốn; hỗ trợ AbortSignal.
 */
export async function goiNgoai(
  heThong: string,
  nguoiDung: string,
  maxToken = 1200,
  them: Record<string, unknown> = {},
  signal?: AbortSignal,
  tuyChon: { nguoiDungId?: number | null } = {},
) {
  const t0 = Date.now();
  if (!(await ngoaiDangBat())) throw loiNgoaiBiTat();
  if (!NGOAI.key || !NGOAI.base) {
    throw loiCongKhai("Chưa cấu hình cổng mô hình ngoài. Liên hệ quản trị viên.", 503, "chua_cau_hinh_ngoai");
  }
  const uid = tuyChon.nguoiDungId !== undefined ? tuyChon.nguoiDungId : nguCanhNguoiDung.getStore()?.uid ?? null;
  const bangPII = new Map<string, string>();
  const heThongDaAnDanh = anDanhVanBanNgoai(heThong, bangPII) as string;
  const nguoiDungDaAnDanh = anDanhVanBanNgoai(nguoiDung, bangPII) as string;
  const themDaAnDanh = anDanhVanBanNgoai(them, bangPII) as Record<string, unknown>;
  kiemHanMucNgoai(uid);
  let res: Response;
  try {
    res = await fetch(`${NGOAI.base}/chat/completions`, {
      method: "POST",
      ...(signal ? { signal } : {}),
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${NGOAI.key}`,
        "User-Agent": NGOAI.ua,
      },
      body: JSON.stringify({
        model: NGOAI.model,
        temperature: 0.2,
        max_tokens: maxToken,
        enable_thinking: process.env.AIBOX_THINKING === "1",
        ...themDaAnDanh,
        messages: [
          { role: "system", content: heThongDaAnDanh },
          { role: "user", content: nguoiDungDaAnDanh },
        ],
      }),
    });
  } catch (err: any) {
    if (signal?.aborted || err?.name === "AbortError") {
      const abortErr: any = new Error("Đã hủy gọi mô hình ngoài theo yêu cầu người dùng");
      abortErr.status = 499;
      abortErr.code = "da_huy";
      throw abortErr;
    }
    console.error("[mo-hinh-ngoai] không kết nối được:", err?.message || err);
    throw loiCongKhai("Không kết nối được cổng mô hình ngoài. Thử lại sau.", 502, "ngoai_khong_ket_noi");
  }
  const data: any = await res.json().catch(() => ({}));
  if (!res.ok) {
    console.error(`[mo-hinh-ngoai] trả mã ${res.status}:`, data?.error?.message || data?.message || "");
    throw loiCongKhai(`Cổng mô hình ngoài trả mã ${res.status}.`, 502, "ngoai_loi");
  }
  const noiDung = data?.choices?.[0]?.message?.content || "";
  const sach = khoiPhucPII(noiDung.replace(/<think>[\s\S]*?<\/think>/g, "").trim(), bangPII);
  return {
    text: sach,
    source: "mo_hinh_ngoai",
    model: data?.model || NGOAI.model,
    usage: data?.usage || null,
    seconds: Math.round((Date.now() - t0) / 100) / 10,
  };
}

const NHOM_CAU_HOI = ["Triệu chứng", "Tiền sử", "Thuốc", "Dị ứng", "Người bị", "Thời gian", "Khám", "Chức năng", "Khác"];

export function dangKyLlmNgoaiRoutes(app: express.Express) {
  /** Tình trạng cổng ngoài — gọi /models (không tốn tiền), không gửi nội dung ca khám. */
  app.get("/api/external/status", async (req, res) => {
    const enabled = await ngoaiDangBat().catch(() => false);
    if (!NGOAI.key) return res.json({ configured: false, enabled, model: NGOAI.model });
    // Địa chỉ cổng chỉ cho quản trị xem.
    const laQuanTri = req.nguoiDung?.vai === "quan_tri";
    try {
      const r = await fetch(`${NGOAI.base}/models`, {
        headers: { Authorization: `Bearer ${NGOAI.key}`, "User-Agent": NGOAI.ua },
      });
      const d: any = await r.json().catch(() => ({}));
      const ids: string[] = (d?.data || []).map((m: any) => m.id);
      res.json({
        configured: true,
        enabled,
        reachable: r.ok,
        model: NGOAI.model,
        modelAvailable: ids.includes(NGOAI.model),
        ...(laQuanTri ? { base: NGOAI.base } : {}),
      });
    } catch (err: any) {
      console.error("[mo-hinh-ngoai] /models lỗi:", err?.message || err);
      res.json({ configured: true, enabled, reachable: false, model: NGOAI.model });
    }
  });

  /** Sửa bản nháp theo lời nhắc — chỉ khi đã cho phép mô hình ngoài. */
  app.post("/api/edit-note", async (req, res) => {
    try {
      await chanNeuChuaChoPhep(req);
      const { currentContent, instruction, transcript } = req.body || {};
      if (!currentContent || !instruction) return res.status(400).json({ error: "Thiếu nội dung hoặc lời nhắc" });
      const r = await goiNgoai(
        "Bạn sửa bản nháp hồ sơ lâm sàng tiếng Việt theo đúng lời nhắc của bác sĩ. " +
          "Chỉ sửa đúng chỗ được yêu cầu, giữ nguyên các dòng khác và giữ các tiêu đề mục. " +
          "KHÔNG thêm thông tin không có trong hội thoại hoặc bản nháp. KHÔNG chẩn đoán, KHÔNG đề xuất điều trị. " +
          "Chỉ trả về bản nháp đã sửa, không giải thích.",
        `Lời nhắc của bác sĩ: ${instruction}\n\nHội thoại gốc (để đối chiếu):\n${transcript || "(không có)"}\n\n` +
          `Bản nháp hiện tại:\n${currentContent}`,
        1500,
        {},
        undefined,
        { nguoiDungId: req.nguoiDung?.id ?? null },
      );
      res.json({ updatedContent: r.text, source: r.source, model: r.model, usage: r.usage, seconds: r.seconds });
    } catch (err) {
      traLoi(res, err);
    }
  });

  app.post("/api/clinical-qa", async (req, res) => {
    try {
      await chanNeuChuaChoPhep(req);
      const { question, transcript, draft } = req.body || {};
      if (!question) return res.status(400).json({ error: "Thiếu câu hỏi" });
      const soLuot = (transcript || "")
        .split("\n")
        .filter((x: string) => x.trim())
        .map((x: string, i: number) => `[lượt ${i + 1}] ${x.trim()}`)
        .join("\n");
      const r = await goiNgoai(
        "Bạn trả lời câu hỏi của bác sĩ về MỘT ca khám, CHỈ dựa trên hội thoại và bản nháp được cung cấp. " +
          "Mỗi ý phải ghi số lượt hội thoại làm căn cứ, dạng (lượt 3). Nếu hội thoại không nói thì trả lời " +
          "đúng câu: “Hội thoại không nói điều này.” KHÔNG trích sách, hướng dẫn hay bài báo nào. " +
          "KHÔNG chẩn đoán, KHÔNG đề xuất thuốc hay điều trị. Trả lời ngắn, tiếng Việt.",
        `Hội thoại:\n${soLuot || "(không có)"}\n\nBản nháp:\n${draft || "(chưa có)"}\n\nCâu hỏi: ${question}`,
        700,
        {},
        undefined,
        { nguoiDungId: req.nguoiDung?.id ?? null },
      );
      res.json({ answer: r.text, sources: [], source: r.source, model: r.model, usage: r.usage, seconds: r.seconds });
    } catch (err) {
      traLoi(res, err);
    }
  });

  app.post("/api/questions-external", async (req, res) => {
    try {
      await chanNeuChuaChoPhep(req);
      const { transcript, propositions, context } = req.body || {};
      if (!transcript && !context) return res.status(400).json({ error: "Cần lời thoại hoặc ngữ cảnh" });
      const soLuot = String(transcript || "")
        .split("\n")
        .filter((x: string) => x.trim())
        .map((x: string, i: number) => `[lượt ${i + 1}] ${x.trim()}`)
        .join("\n");
      const menhDe = (propositions || [])
        .map(
          (p: any) =>
            `- #${p.id} [${p.subject || "chưa rõ"}] ${p.text}` +
            (p.status === "can_xac_nhan" ? ` (máy chưa chắc: ${p.gateReason || "cần xác nhận"})` : "") +
            ` — lượt ${(p.evidenceTurns || []).join(", ") || "?"}`,
        )
        .join("\n");
      const r = await goiNgoai(
        "Bạn giúp bác sĩ hỏi bệnh cho đủ trong một ca khám. Đọc ngữ cảnh, hội thoại và danh sách mệnh đề máy đã ghi. " +
          "Đề xuất tối đa 6 câu hỏi NGẮN bác sĩ có thể hỏi ngay: chỗ hội thoại còn mơ hồ (điều này là của bệnh nhân " +
          "hay người nhà, thông tin đã được sửa lại chưa, liều và số lần dùng thuốc, mốc thời gian, dị ứng) và thông tin " +
          "cơ bản còn thiếu so với lý do khám. KHÔNG chẩn đoán, KHÔNG kê thuốc. Mỗi câu gắn một nhóm trong: " +
          NHOM_CAU_HOI.join(", ") +
          ". " +
          'Trả về DUY NHẤT JSON: {"cau_hoi":[{"hoi":"…","goi_y":"…(cách hỏi hoặc thang đo, ngắn)","nhom":"…","vi_sao":"…","luot":[số]}]}',
        `Ngữ cảnh bác sĩ nhập:\n${context || "(không có)"}\n\nHội thoại:\n${soLuot || "(chưa có)"}\n\n` +
          `Mệnh đề máy đã ghi:\n${menhDe || "(chưa có)"}`,
        900,
        {},
        undefined,
        { nguoiDungId: req.nguoiDung?.id ?? null },
      );
      let ds: any[] = [];
      try {
        const m = r.text.match(/\{[\s\S]*\}/);
        ds = JSON.parse(m ? m[0] : r.text).cau_hoi || [];
      } catch {
        ds = [{ hoi: r.text, vi_sao: "(mô hình không trả đúng JSON — hiện nguyên văn)", nhom: "Khác", luot: [] }];
      }
      ds = ds.slice(0, 6).map((q: any) => ({ ...q, nhom: NHOM_CAU_HOI.includes(q.nhom) ? q.nhom : "Khác" }));
      res.json({ questions: ds, source: r.source, model: r.model, usage: r.usage, seconds: r.seconds });
    } catch (err) {
      traLoi(res, err);
    }
  });

  app.post("/api/generate-document", async (req, res) => {
    try {
      await chanNeuChuaChoPhep(req);
      const { title, instruction, transcript, draft, context } = req.body || {};
      if (!instruction && !title) return res.status(400).json({ error: "Thiếu yêu cầu văn bản" });
      if (!transcript && !draft && !context) {
        return res.status(400).json({ error: "Ca này chưa có lời thoại, bản nháp hay ngữ cảnh để soạn văn bản" });
      }
      const soLuot = String(transcript || "")
        .split("\n")
        .filter((x: string) => x.trim())
        .map((x: string, i: number) => `[lượt ${i + 1}] ${x.trim()}`)
        .join("\n");
      const r = await goiNgoai(
        "Bạn soạn văn bản y khoa tiếng Việt cho bác sĩ. CHỈ dùng thông tin có trong lời thoại, bản nháp và ngữ " +
          "cảnh được cung cấp. Thông tin văn bản cần mà nguồn không có thì ghi đúng chữ [cần bổ sung]. KHÔNG tự " +
          "thêm chẩn đoán, thuốc, liều, xét nghiệm, số ngày nghỉ hay lời khuyên mà bác sĩ không nói. Thông tin " +
          "của người nhà phải ghi rõ là của người nhà, không gán cho bệnh nhân. Trình bày bằng tiêu đề ngắn và " +
          'gạch đầu dòng, không dùng bảng. Cuối văn bản thêm một dòng: "Căn cứ: lượt …" liệt kê các lượt đã dùng.',
        `Văn bản cần soạn: ${title || ""}\nYêu cầu: ${instruction || title}\n\n` +
          `Ngữ cảnh bác sĩ nhập:\n${context || "(không có)"}\n\nLời thoại:\n${soLuot || "(không có)"}\n\n` +
          `Bản nháp hồ sơ:\n${draft || "(chưa có)"}`,
        1200,
        {},
        undefined,
        { nguoiDungId: req.nguoiDung?.id ?? null },
      );
      const thieu = (r.text.match(/\[cần bổ sung\]/g) || []).length;
      res.json({ content: r.text, missingCount: thieu, source: r.source, model: r.model, usage: r.usage, seconds: r.seconds });
    } catch (err) {
      traLoi(res, err);
    }
  });

  app.post("/api/generate-note-external", async (req, res) => {
    try {
      await chanNeuChuaChoPhep(req);
      const { transcript } = req.body || {};
      if (!transcript) return res.status(400).json({ error: "Thiếu lời thoại" });
      const r = await goiNgoai(
        "Viết bản nháp hồ sơ lâm sàng tiếng Việt từ hội thoại khám bệnh, chia các mục: LÝ DO KHÁM BỆNH, " +
          "BỆNH SỬ HIỆN TẠI, TIỀN SỬ BỆNH, DỊ ỨNG, THUỐC ĐANG DÙNG, TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI, KHÁM LÂM SÀNG, " +
          "CHẨN ĐOÁN, KẾ HOẠCH ĐIỀU TRỊ. Chỉ ghi điều hội thoại nói. Không thêm gì.",
        transcript,
        1500,
        {},
        undefined,
        { nguoiDungId: req.nguoiDung?.id ?? null },
      );
      res.json({ content: r.text, source: r.source, model: r.model, usage: r.usage, seconds: r.seconds });
    } catch (err) {
      traLoi(res, err);
    }
  });
}
