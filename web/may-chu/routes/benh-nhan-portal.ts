import crypto from "node:crypto";
import type { DatabaseSync } from "node:sqlite";
import express from "express";
import { db as defaultDb } from "../csdl";
import { chanNeuChuaKy } from "../kiem-ky-may-chu";

export interface NguoiDungReq {
  id: number;
  email?: string;
  hoTen?: string;
  vai?: string;
}

export interface TaoRouterBenhNhanPortalCtx {
  db?: DatabaseSync;
  secret?: string;
}

interface ThuocVao {
  ten?: string;
  ten_thuoc?: string;
  sang?: string;
  trua?: string;
  chieu?: string;
  toi?: string;
  loiDan?: string;
  loi_dan?: string;
}

export interface LichMuc {
  ten_thuoc: string;
  cach_dung: string;
}

export interface GoiCongBenhNhan {
  phien_ban: string;
  ma_ho_so: string;
  tenBenhNhan: string;
  chanDoan: string;
  lichUongThuoc: {
    sang: LichMuc[];
    trua: LichMuc[];
    chieu: LichMuc[];
    toi: LichMuc[];
    truoc_ngu: LichMuc[];
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

const RED_FLAG_KEYWORDS = [
  "khó thở",
  "đau ngực",
  "tức ngực",
  "phát ban",
  "phân đen",
  "nôn ra máu",
  "sốt > 39",
  "sốt trên 39",
  "sốt cao",
  "yếu liệt",
  "méo mặt",
  "nói ngọng",
  "co giật",
  "ngất",
  "sưng môi",
  "phù mặt",
  "chóng mặt dữ dội",
];

const FOOD_DRUG_RULES: Array<{ keywords: string[]; mucDo: string; noiDung: string }> = [
  {
    keywords: ["warfarin", "sintrom", "acenocoumarol"],
    mucDo: "canh_bao",
    noiDung: "Thuốc chống đông: Giữ lượng rau xanh đậm ổn định hàng ngày và tránh rượu bia.",
  },
  {
    keywords: ["metformin", "glucophage"],
    mucDo: "luu_y",
    noiDung: "Metformin: Uống trong hoặc ngay sau ăn để giảm khó chịu dạ dày; kiêng rượu bia.",
  },
  {
    keywords: ["atorvastatin", "simvastatin", "lovastatin", "statin"],
    mucDo: "canh_bao",
    noiDung: "Statin: Tránh nước ép bưởi chùm; nên uống vào buổi tối.",
  },
  {
    keywords: ["ciprofloxacin", "levofloxacin", "moxifloxacin", "tetracycline", "doxycycline"],
    mucDo: "canh_bao",
    noiDung: "Kháng sinh Quinolon/Tetracyclin: Uống cách sữa, canxi, sắt ít nhất 2 giờ.",
  },
  {
    keywords: ["ibuprofen", "diclofenac", "naproxen", "meloxicam", "celecoxib", "aspirin"],
    mucDo: "canh_bao",
    noiDung: "Thuốc giảm đau NSAID/Aspirin: Luôn uống sau ăn no; thận trọng nếu đau dạ dày hoặc bệnh thận.",
  },
  {
    keywords: ["perindopril", "enalapril", "lisinopril", "coversyl", "losartan", "valsartan"],
    mucDo: "luu_y",
    noiDung: "Thuốc huyết áp ƯCMC/ARB: Tránh tự ý dùng muối kali hoặc thực phẩm bổ sung kali.",
  },
];

function laTrongHoacMoHo(val: unknown): boolean {
  const s = String(val ?? "").trim();
  return !s || s === "—" || s === "-" || s === "0" || /^chưa/i.test(s);
}

function phanBoThuocAnToan(dsThuoc: Array<string | ThuocVao>) {
  const lich: GoiCongBenhNhan["lichUongThuoc"] = {
    sang: [],
    trua: [],
    chieu: [],
    toi: [],
    truoc_ngu: [],
  };
  const moHo: GoiCongBenhNhan["thuocMoHoLich"] = [];
  const tenGhep: string[] = [];

  for (const item of dsThuoc) {
    if (typeof item === "string") {
      const s = item.trim();
      if (!s) continue;
      tenGhep.push(s.toLowerCase());
      const low = s.toLowerCase();
      let daGan = false;
      const cachDung = low.includes("trước ăn") || low.includes("trước khi ăn")
        ? "Uống TRƯỚC khi ăn 30 phút"
        : low.includes("trong bữa")
          ? "Uống trong bữa ăn"
          : "Uống sau khi ăn no";

      if (low.includes("sáng")) { lich.sang.push({ ten_thuoc: s, cach_dung: cachDung }); daGan = true; }
      if (low.includes("trưa")) { lich.trua.push({ ten_thuoc: s, cach_dung: cachDung }); daGan = true; }
      if (low.includes("chiều")) { lich.chieu.push({ ten_thuoc: s, cach_dung: cachDung }); daGan = true; }
      if (low.includes("tối")) { lich.toi.push({ ten_thuoc: s, cach_dung: cachDung }); daGan = true; }
      if (low.includes("trước ngủ") || low.includes("đi ngủ")) {
        lich.truoc_ngu.push({ ten_thuoc: s, cach_dung: "Uống trước khi đi ngủ 30 phút" });
        daGan = true;
      }
      if (!daGan) {
        if (low.includes("2 lần/ngày") || low.includes("ngày 2 lần")) {
          lich.sang.push({ ten_thuoc: s, cach_dung: `${cachDung} (Liều 1)` });
          lich.toi.push({ ten_thuoc: s, cach_dung: `${cachDung} (Liều 2)` });
        } else if (low.includes("3 lần/ngày") || low.includes("ngày 3 lần")) {
          lich.sang.push({ ten_thuoc: s, cach_dung: `${cachDung} (Liều 1)` });
          lich.trua.push({ ten_thuoc: s, cach_dung: `${cachDung} (Liều 2)` });
          lich.toi.push({ ten_thuoc: s, cach_dung: `${cachDung} (Liều 3)` });
        } else if (low.includes("statin") || low.includes("atorvastatin") || low.includes("rosuvastatin")) {
          lich.toi.push({ ten_thuoc: s, cach_dung: "Uống vào buổi tối sau ăn" });
        } else {
          moHo.push({
            ten_thuoc: s,
            cach_dung: "Cần bác sĩ/dược sĩ xác nhận giờ uống cụ thể",
            ly_do: "Chưa ghi rõ khung giờ hoặc tần suất uống trong ngày",
          });
        }
      }
    } else if (item && typeof item === "object") {
      const ten = String(item.ten || item.ten_thuoc || "").trim();
      if (!ten) continue;
      tenGhep.push(ten.toLowerCase());
      const loiDan = String(item.loiDan || item.loi_dan || "Theo chỉ định của bác sĩ").trim();
      let daGan = false;
      if (!laTrongHoacMoHo(item.sang)) { lich.sang.push({ ten_thuoc: `${ten} (${item.sang})`, cach_dung: loiDan }); daGan = true; }
      if (!laTrongHoacMoHo(item.trua)) { lich.trua.push({ ten_thuoc: `${ten} (${item.trua})`, cach_dung: loiDan }); daGan = true; }
      if (!laTrongHoacMoHo(item.chieu)) { lich.chieu.push({ ten_thuoc: `${ten} (${item.chieu})`, cach_dung: loiDan }); daGan = true; }
      if (!laTrongHoacMoHo(item.toi)) { lich.toi.push({ ten_thuoc: `${ten} (${item.toi})`, cach_dung: loiDan }); daGan = true; }
      if (!daGan) {
        moHo.push({
          ten_thuoc: ten,
          cach_dung: "Cần bác sĩ/dược sĩ xác nhận giờ uống cụ thể",
          ly_do: "Đơn thuốc chưa ghi rõ liều theo buổi Sáng/Trưa/Chiều/Tối",
        });
      }
    }
  }

  return { lich, moHo, tenGhep: tenGhep.join(" | ") };
}

function damBaoBangCongBenhNhan(targetDb: DatabaseSync) {
  targetDb.exec(`
    CREATE TABLE IF NOT EXISTS cong_benh_nhan (
      token TEXT PRIMARY KEY,
      nguoi_dung_id INTEGER NOT NULL,
      session_id TEXT,
      goi_json TEXT NOT NULL,
      tao_luc INTEGER NOT NULL,
      het_han INTEGER NOT NULL
    );
    CREATE TABLE IF NOT EXISTS bao_cao_benh_nhan (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      token TEXT NOT NULL,
      moc_theo_doi TEXT NOT NULL,
      da_uong_du_thuoc INTEGER NOT NULL,
      trieu_chung_moi TEXT NOT NULL,
      muc_do_met INTEGER NOT NULL,
      co_dau_hieu_do INTEGER NOT NULL,
      dau_hieu_do_json TEXT NOT NULL,
      tao_luc INTEGER NOT NULL
    );
  `);
}

export function danhGiaDauHieuDo(body: Record<string, unknown>): {
  redFlagDetected: boolean;
  matchedKeywords: string[];
} {
  const coDauHieuDo = body.co_dau_hieu_do === true;
  const dsChon = Array.isArray(body.dau_hieu_do_chon)
    ? body.dau_hieu_do_chon.map((x) => String(x || "").trim()).filter(Boolean)
    : [];
  const trieuChung = String(body.trieu_chung_moi || "").toLowerCase();

  const matchedKeywords = RED_FLAG_KEYWORDS.filter((kw) => trieuChung.includes(kw));
  const redFlagDetected = coDauHieuDo || dsChon.length > 0 || matchedKeywords.length > 0;
  return { redFlagDetected, matchedKeywords };
}

export function taoRouterBenhNhanPortal(ctx?: TaoRouterBenhNhanPortalCtx): express.Router {
  const targetDb = ctx?.db ?? defaultDb;
  const secret = (ctx?.secret || process.env.MEDITRACE_PORTAL_SECRET || "meditrace-patient-portal-default-key").trim();
  damBaoBangCongBenhNhan(targetDb);

  const router = express.Router();

  // 1. Bác sĩ tạo mã QR & gói theo dõi an toàn (đã lọc bỏ ghi chú nội bộ)
  router.post("/api/benh-nhan-portal/tao-ma", (req, res) => {
    const uid = (req as express.Request & { nguoiDung?: NguoiDungReq }).nguoiDung?.id;
    if (typeof uid !== "number") {
      return res.status(401).json({ error: "Chưa đăng nhập" });
    }

    const body = req.body && typeof req.body === "object" ? req.body : {};
    const tenBenhNhan = String(body.tenBenhNhan || body.ten_benh_nhan || body.patientIdentifier || "Quý khách / Người bệnh").trim();
    const chanDoan = String(body.chanDoan || body.chan_doan || "").trim();
    const sessionId = body.sessionId ? String(body.sessionId).trim() : null;
    // Cổng/QR đưa hồ sơ ra ngoài phần mềm: chỉ khi bác sĩ đã ký và chưa sửa sau khi ký (kiểm trên máy chủ).
    if (chanNeuChuaKy(req, res, sessionId || "")) return;

    const dsThuoc = Array.isArray(body.thuoc)
      ? body.thuoc
      : Array.isArray(body.danh_sach_thuoc)
        ? body.danh_sach_thuoc
        : [];

    const { lich, moHo, tenGhep } = phanBoThuocAnToan(dsThuoc);

    const tuongTacThucAn: GoiCongBenhNhan["tuongTacThucAn"] = [];
    const seen = new Set<string>();
    for (const rule of FOOD_DRUG_RULES) {
      if (rule.keywords.some((kw) => tenGhep.includes(kw)) && !seen.has(rule.noiDung)) {
        seen.add(rule.noiDung);
        tuongTacThucAn.push({ nguon: "tuong_tac_thuc_an", muc_do: rule.mucDo, noi_dung: rule.noiDung });
      }
    }
    if (Array.isArray(body.tuongTacThucAn)) {
      for (const tt of body.tuongTacThucAn) {
        const msg = typeof tt === "string" ? tt.trim() : String(tt?.noi_dung || "").trim();
        if (msg && !seen.has(msg)) {
          seen.add(msg);
          tuongTacThucAn.push({ nguon: "bac_si", muc_do: "luu_y", noi_dung: msg });
        }
      }
    }

    const dauHieuBaoDong: string[] = Array.isArray(body.dauHieu)
      ? body.dauHieu.map((d: unknown) => (typeof d === "string" ? d : String((d as any)?.noiDung || ""))).filter(Boolean)
      : Array.isArray(body.dauHieuBaoDong)
        ? body.dauHieuBaoDong.map((d: unknown) => String(d || "")).filter(Boolean)
        : [
            "Khó thở, thở hụt hơi hoặc tức nặng ngực.",
            "Sốt cao liên tục trên 39.0°C không hạ sau 2 giờ uống thuốc hạ sốt.",
            "Phát ban mẩn đỏ toàn thân, sưng môi/mí mắt sau khi uống thuốc.",
            "Nôn ra máu hoặc đi ngoài phân đen.",
          ];

    const nenAn = Array.isArray(body.cheDoSinhHoat?.nenAn)
      ? body.cheDoSinhHoat.nenAn.map(String)
      : Array.isArray(body.anUong)
        ? body.anUong.map((a: any) => String(a?.noiDung || a || "")).filter(Boolean)
        : ["Ăn đủ bữa, tăng rau xanh, uống đủ nước lọc mỗi ngày."];
    const kiengCu = Array.isArray(body.cheDoSinhHoat?.kiengCu)
      ? body.cheDoSinhHoat.kiengCu.map(String)
      : ["Kiêng rượu bia, thuốc lá, hạn chế đồ ăn quá mặn hoặc nhiều dầu mỡ."];
    const loiDan = Array.isArray(body.cheDoSinhHoat?.loiDan)
      ? body.cheDoSinhHoat.loiDan.map(String)
      : ["Uống thuốc đúng giờ với nước lọc, không tự ý ngừng thuốc khi chưa hỏi bác sĩ."];

    const token = crypto.randomBytes(12).toString("base64url");
    const now = Date.now();
    const ttlDays = Math.min(90, Math.max(1, Number(body.ttlDays) || 14));
    const expiresAt = now + ttlDays * 86_400_000;

    const goiKhongKy: Omit<GoiCongBenhNhan, "chuKyHmac"> = {
      phien_ban: "1.0",
      ma_ho_so: token,
      tenBenhNhan,
      chanDoan,
      lichUongThuoc: lich,
      thuocMoHoLich: moHo,
      tuongTacThucAn,
      dauHieuBaoDong,
      cheDoSinhHoat: { nenAn, kiengCu, loiDan },
      ngayTaiKham: String(body.ngayTaiKham || "Sau 5 - 7 ngày hoặc khi hết thuốc").trim(),
      diaDiemTaiKham: String(body.diaDiemTaiKham || "Phòng khám / Cơ sở điều trị").trim(),
    };

    const canonical = JSON.stringify(goiKhongKy);
    const chuKyHmac = crypto.createHmac("sha256", secret).update(canonical, "utf-8").digest("hex");
    const goi: GoiCongBenhNhan = { ...goiKhongKy, chuKyHmac };

    targetDb
      .prepare(
        `INSERT INTO cong_benh_nhan (token, nguoi_dung_id, session_id, goi_json, tao_luc, het_han)
         VALUES (?, ?, ?, ?, ?, ?)`
      )
      .run(token, uid, sessionId, JSON.stringify(goi), now, expiresAt);

    return res.status(201).json({
      ok: true,
      token,
      url: `?portal=${token}`,
      expiresAt,
      chuKyHmac,
      goi,
    });
  });

  // 2. Cổng công khai cho người bệnh quét QR xem lịch uống thuốc & cảnh báo
  router.get("/api/benh-nhan-portal/:token", (req, res) => {
    const token = String(req.params.token || "").trim();
    const row = targetDb
      .prepare("SELECT token, session_id, goi_json, tao_luc, het_han FROM cong_benh_nhan WHERE token = ?")
      .get(token) as
      | { token: string; session_id: string | null; goi_json: string; tao_luc: number; het_han: number }
      | undefined;

    if (!row) {
      return res.status(404).json({ error: "Không tìm thấy hồ sơ cổng người bệnh" });
    }
    if (row.het_han < Date.now()) {
      return res.status(410).json({ error: "Liên kết cổng theo dõi đã hết hạn" });
    }

    const goi = JSON.parse(row.goi_json) as GoiCongBenhNhan;
    return res.set("Cache-Control", "no-store").json({
      ok: true,
      token: row.token,
      createdAt: row.tao_luc,
      expiresAt: row.het_han,
      ...goi,
    });
  });

  // 3. Người bệnh / thân nhân gửi báo cáo theo dõi 48h / 7 ngày -> tự động tạo task ưu tiên cao nếu có dấu hiệu đỏ
  router.post("/api/benh-nhan-portal/:token/bao-cao", (req, res) => {
    const token = String(req.params.token || "").trim();
    const row = targetDb
      .prepare("SELECT token, nguoi_dung_id, session_id, goi_json, het_han FROM cong_benh_nhan WHERE token = ?")
      .get(token) as
      | { token: string; nguoi_dung_id: number; session_id: string | null; goi_json: string; het_han: number }
      | undefined;

    if (!row) {
      return res.status(404).json({ error: "Không tìm thấy hồ sơ cổng người bệnh" });
    }
    if (row.het_han < Date.now()) {
      return res.status(410).json({ error: "Liên kết cổng theo dõi đã hết hạn" });
    }

    const body = req.body && typeof req.body === "object" ? (req.body as Record<string, unknown>) : {};
    const mocTheoDoi = body.moc_theo_doi === "7d" ? "7d" : "48h";
    const daUongDu = Boolean(body.da_uong_du_thuoc);
    const trieuChungMoi = String(body.trieu_chung_moi || "").trim();
    const mucDoMet = Math.min(10, Math.max(0, Number(body.muc_do_met) || 0));
    const dsChon = Array.isArray(body.dau_hieu_do_chon)
      ? body.dau_hieu_do_chon.map((x) => String(x || "").trim()).filter(Boolean)
      : [];

    const { redFlagDetected, matchedKeywords } = danhGiaDauHieuDo(body);
    const now = Date.now();

    targetDb
      .prepare(
        `INSERT INTO bao_cao_benh_nhan
         (token, moc_theo_doi, da_uong_du_thuoc, trieu_chung_moi, muc_do_met, co_dau_hieu_do, dau_hieu_do_json, tao_luc)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?)`
      )
      .run(
        token,
        mocTheoDoi,
        daUongDu ? 1 : 0,
        trieuChungMoi,
        mucDoMet,
        redFlagDetected ? 1 : 0,
        JSON.stringify(dsChon),
        now
      );

    let taskCreated = false;
    let taskId: string | undefined;

    if (redFlagDetected) {
      const goi = JSON.parse(row.goi_json) as GoiCongBenhNhan;
      const chiTiet = [...dsChon, ...matchedKeywords, trieuChungMoi]
        .filter(Boolean)
        .slice(0, 3)
        .join("; ");
      taskId = `portal-rf-${token}-${now}`;
      const newTask = {
        id: taskId,
        title: `[CẢNH BÁO ĐỎ ${mocTheoDoi}] ${goi.tenBenhNhan}: ${chiTiet || "Báo cáo dấu hiệu nguy hiểm"}`,
        patientName: goi.tenBenhNhan,
        dueDate: "Ngay hôm nay (Khẩn)",
        completed: false,
        priority: "high" as const,
        ...(row.session_id ? { sessionId: row.session_id } : {}),
      };

      const nextRow = targetDb
        .prepare("SELECT COALESCE(MAX(thu_tu), -1) + 1 AS next_tt FROM muc_kho WHERE nguoi_dung_id = ? AND kho = 'nhiem-vu'")
        .get(row.nguoi_dung_id) as { next_tt: number } | undefined;
      const nextThuTu = nextRow?.next_tt ?? 0;

      targetDb
        .prepare("INSERT INTO muc_kho (nguoi_dung_id, kho, thu_tu, du_lieu) VALUES (?, 'nhiem-vu', ?, ?)")
        .run(row.nguoi_dung_id, nextThuTu, JSON.stringify(newTask));

      taskCreated = true;
    }

    return res.json({
      ok: true,
      moc_theo_doi: mocTheoDoi,
      redFlagDetected,
      matchedKeywords,
      taskCreated,
      ...(taskId ? { taskId } : {}),
    });
  });

  return router;
}
