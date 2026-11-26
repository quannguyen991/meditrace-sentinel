/**
 * Express routes cho tra cứu y khoa chính thống:
 *   - GET  /api/pubmed-search
 *   - GET  /api/phac-do/muc-luc
 *   - POST /api/lookup-official
 *
 * Toàn bộ logic miền đã tách sang `../tra-cuu/*` (giữ re-export tương thích ngược).
 */
import type express from "express";
import {
  chuanSo,
  datTuKhoaTraCuu,
  mucLucPhacDo,
  soanTraLoiCoNguon,
  soLech,
  type TaiLieu,
  timPubMed,
  timTaiLieuTheoTuKhoa,
} from "../tra-cuu/dich-vu-tra-cuu";
import { traLoi } from "./dung-chung";
import { chanNeuChuaChoPhep, chayVoiNguoiDung, goiNgoai } from "./llm-ngoai";

export { type TaiLieu, chuanSo, soLech, datTuKhoaTraCuu, timTaiLieuTheoTuKhoa, soanTraLoiCoNguon };

export function dangKyTraCuuRoutes(app: express.Express) {
  app.get("/api/pubmed-search", async (req, res) => {
    const q = String(req.query.q || "").trim();
    if (!q) return res.status(400).json({ error: "Thiếu từ khoá" });
    try {
      const nam = Number(req.query.tuNam);
      const bai = await timPubMed(q, 8, req.query.cao === "1", Number.isInteger(nam) && nam > 1900 ? nam : undefined);
      res.json({
        results: bai.map((b) => ({
          title: b.ten,
          url: b.url,
          year: b.nam,
          type: b.loai,
          journal: b.tapChi,
          abstract: b.noiDung.slice(0, 600),
        })),
      });
    } catch (err: any) {
      console.error("[pubmed]", err?.message || err);
      res.status(502).json({ error: "Không tìm được trên PubMed. Thử lại sau." });
    }
  });

  app.get("/api/phac-do/muc-luc", (_req, res) => {
    res.json({ van_ban: mucLucPhacDo() });
  });

  // Mọi lời gọi ngoài trong route (kể cả trong datTuKhoaTraCuu/soanTraLoiCoNguon) tính hạn mức cho đúng người dùng.
  app.post("/api/lookup-official", (req, res) => chayVoiNguoiDung(req.nguoiDung?.id, async () => {
    try {
      await chanNeuChuaChoPhep(req);
      const { question, context, nguon, transcript, draft } = req.body || {};
      const soLuotCa = String(transcript || "")
        .split("\n")
        .filter((x) => x.trim())
        .map((x, i) => `[lượt ${i + 1}] ${x.trim()}`)
        .join("\n");
      const coCa = !!(soLuotCa || String(draft || "").trim());
      const caKham = coCa
        ? `Hội thoại:\n${soLuotCa.slice(0, 4000) || "(không có)"}\n\nBản nháp bệnh án:\n${String(draft || "").slice(0, 2000) || "(chưa có)"}`
        : "";

      const dungPubMed = nguon?.pubmed !== false;
      const dungMedline = nguon?.medlineplus !== false;
      const dungFDA = nguon?.fda !== false;
      const dungKCB = nguon?.kcb !== false;
      const dungMSD = nguon?.msd !== false;
      const dungNICE = nguon?.nice !== false;
      const dungWHO = nguon?.who !== false;
      const dungCDC = nguon?.cdc !== false;
      const dungSP = nguon?.statpearls !== false;
      const dungAAFP = nguon?.aafp !== false;
      if (
        !dungPubMed &&
        !dungMedline &&
        !dungFDA &&
        !dungKCB &&
        !dungMSD &&
        !dungNICE &&
        !dungWHO &&
        !dungCDC &&
        !dungSP &&
        !dungAAFP
      ) {
        return res.status(400).json({ error: "Chưa chọn nguồn tra cứu nào" });
      }
      if (!question) return res.status(400).json({ error: "Thiếu câu hỏi" });

      const { tuKhoa, b1 } = await datTuKhoaTraCuu(question, context, caKham, coCa);
      if (coCa && (tuKhoa.can_tra_cuu === false || tuKhoa.can_tra_cuu === "false")) {
        const r = await goiNgoai(
          "Bạn trả lời câu hỏi của bác sĩ về MỘT ca khám, CHỈ dựa trên hội thoại và bản nháp được cung cấp. " +
            "Mỗi ý phải ghi số lượt hội thoại làm căn cứ, dạng (lượt 3). Nếu hội thoại không nói thì trả lời " +
            "đúng câu: “Hội thoại không nói điều này.” KHÔNG chẩn đoán, KHÔNG đề xuất thuốc hay điều trị. " +
            "Trả lời ngắn, tiếng Việt.",
          `${caKham}\n\nCâu hỏi: ${question}`,
          700,
        );
        const u = (x: any) => x?.usage || {};
        return res.json({
          answer:
            `${r.text}\n\n**Nguồn:** chỉ hội thoại và bản nháp của ca này — câu hỏi về thông tin trong ca nên không tra tài liệu.` +
            `\n\n> Chỉ để tham khảo — bác sĩ đối chiếu lời thoại gốc và tự quyết định.`,
          sources: [],
          searched: [],
          caseOnly: true,
          model: r.model,
          seconds: Math.round((b1.seconds + r.seconds) * 10) / 10,
          usage: {
            prompt_tokens: (u(b1).prompt_tokens || 0) + (u(r).prompt_tokens || 0),
            completion_tokens: (u(b1).completion_tokens || 0) + (u(r).completion_tokens || 0),
            calls: 2,
          },
        });
      }
      if (!tuKhoa.pubmed) {
        return res.status(502).json({ error: `Mô hình không trả được từ khoá tìm kiếm: ${b1.text.slice(0, 200)}` });
      }
      const { taiLieu, daTra, loiTim, boLacDe, tuKhoaRa, kcb, phacDo } = await timTaiLieuTheoTuKhoa({ cauHoi: question, tuKhoa, nguon });
      const usage = (x: any) => x?.usage || {};
      if (!taiLieu.length) {
        return res.json({
          answer: "Không tìm thấy tài liệu nào ở các nguồn đã chọn cho câu hỏi này.",
          sources: [],
          removedSources: boLacDe,
          searchTerms: tuKhoaRa,
          warning: "KHÔNG có nguồn nào — không có câu trả lời." + (loiTim.length ? ` Lỗi tìm: ${loiTim.join("; ")}` : ""),
          model: b1.model,
          seconds: b1.seconds,
          usage: { prompt_tokens: usage(b1).prompt_tokens, completion_tokens: usage(b1).completion_tokens },
        });
      }

      const b2 = await soanTraLoiCoNguon({ cauHoi: question, caKham, coCa, taiLieu, daTra, boLacDe, loiTim, tuKhoaRa, kcb, phacDo });
      res.json({
        answer: b2.answer,
        sources: b2.sources,
        searched: b2.searched,
        cauTruc: b2.cauTruc,
        removedSources: b2.removedSources,
        warning: b2.warning,
        searchTerms: tuKhoaRa,
        source: "mo_hinh_ngoai",
        model: b2.model,
        seconds: Math.round((b1.seconds + b2.seconds) * 10) / 10,
        usage: {
          prompt_tokens: (b1.usage?.prompt_tokens || 0) + (b2.usage?.prompt_tokens || 0),
          completion_tokens: (b1.usage?.completion_tokens || 0) + (b2.usage?.completion_tokens || 0),
          calls: 2,
        },
      });
    } catch (err) {
      traLoi(res, err);
    }
  }));
}
