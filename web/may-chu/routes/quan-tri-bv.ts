import express from "express";
import type { DatabaseSync } from "node:sqlite";
import { db as defaultDb, khoWorm } from "../csdl";
import { taoKhoWorm } from "../worm";
import { chayPythonJson, goiDichVu, traLoi } from "./dung-chung";

const WHO_AWARE_RESERVE = [
  "colistin",
  "linezolid",
  "tigecycline",
  "daptomycin",
  "ceftazidime/avibactam",
  "ceftolozane",
  "polymyxin",
  "aztreonam",
];

const WHO_AWARE_WATCH = [
  "meropenem",
  "imipenem",
  "ertapenem",
  "vancomycin",
  "teicoplanin",
  "levofloxacin",
  "ciprofloxacin",
  "moxifloxacin",
  "ceftriaxone",
  "cefotaxime",
  "ceftazidime",
  "cefepime",
  "cefuroxime",
  "cefixime",
  "azithromycin",
  "clarithromycin",
  "erythromycin",
  "piperacillin",
];

const WHO_AWARE_ACCESS = [
  "amoxicillin",
  "ampicillin",
  "augmentin",
  "cephalexin",
  "cefazolin",
  "cefadroxil",
  "doxycycline",
  "metronidazole",
  "clindamycin",
  "gentamicin",
  "cotrimoxazole",
  "trimethoprim",
  "nitrofurantoin",
  "penicillin",
];

function layThuocNhanTuCa(duLieu: Record<string, any>): string[] {
  const ketQua: string[] = [];
  const props = Array.isArray(duLieu.propositions)
    ? duLieu.propositions
    : Array.isArray(duLieu.phat_bieu)
      ? duLieu.phat_bieu
      : [];

  for (const p of props) {
    if (!p || typeof p !== "object") continue;
    if (p.phu_dinh === true) continue;
    if (p.chu_the_id !== undefined && p.chu_the_id !== 0) continue;
    const thuocTen = p.thuoc && typeof p.thuoc === "object" ? p.thuoc.ten : null;
    if (typeof thuocTen === "string" && thuocTen.trim()) ketQua.push(thuocTen.toLowerCase());
    else if (typeof p.noi_dung === "string" && p.noi_dung.trim()) ketQua.push(p.noi_dung.toLowerCase());
    else if (typeof p.text === "string" && p.text.trim()) ketQua.push(p.text.toLowerCase());
  }

  const xml2 = duLieu?.bhyt_icd10?.goi_xml_1_5?.XML2 || duLieu?.bhytPrecheck?.goi_xml_1_5?.XML2;
  if (typeof xml2 === "string" && xml2.trim()) {
    const matches = xml2.matchAll(/<TEN_THUOC>([^<]+)<\/TEN_THUOC>/gi);
    for (const m of matches) {
      if (m[1]?.trim()) ketQua.push(m[1].trim().toLowerCase());
    }
  }

  const keHoach =
    duLieu?.clinicalNote?.["KẾ HOẠCH ĐIỀU TRỊ"] ||
    duLieu?.draft?.["KẾ HOẠCH ĐIỀU TRỊ"] ||
    duLieu?.ban_nhap?.["KẾ HOẠCH ĐIỀU TRỊ"];
  if (typeof keHoach === "string" && keHoach.trim()) ketQua.push(keHoach.toLowerCase());

  return ketQua;
}

function uocTinhNguyCoXuatToanVnd(duLieu: Record<string, any>): number {
  const bhyt = duLieu.bhyt_icd10 || duLieu.bhytPrecheck || duLieu.bhyt || {};
  let tong = 0;

  const dsXuatToan = Array.isArray(bhyt.canh_bao_xuat_toan_bhyt)
    ? bhyt.canh_bao_xuat_toan_bhyt
    : Array.isArray(bhyt.canh_bao_xuat_toan)
      ? bhyt.canh_bao_xuat_toan
      : [];
  for (const item of dsXuatToan) {
    if (item && typeof item === "object" && typeof item.nguy_co_xuat_toan === "number") {
      tong += item.nguy_co_xuat_toan;
    } else if (item && typeof item === "object" && typeof item.so_tien === "number") {
      tong += item.so_tien;
    } else if (item) {
      tong += 250_000;
    }
  }

  const dsCls = Array.isArray(bhyt.bien_luan_chi_dinh_cls)
    ? bhyt.bien_luan_chi_dinh_cls
    : Array.isArray(duLieu.bien_luan_chi_dinh_cls)
      ? duLieu.bien_luan_chi_dinh_cls
      : [];
  for (const cls of dsCls) {
    if (!cls || typeof cls !== "object") continue;
    const hopLe =
      cls.hop_le !== undefined
        ? Boolean(cls.hop_le)
        : cls.dat_yeu_cau !== undefined
          ? Boolean(cls.dat_yeu_cau)
          : cls.trang_thai
            ? !/thieu|canh_bao|xuat_toan/i.test(String(cls.trang_thai))
            : true;
    if (!hopLe) {
      tong += typeof cls.nguy_co_xuat_toan === "number" ? cls.nguy_co_xuat_toan : 500_000;
    }
  }

  return tong;
}

function demCanhBaoDdiVaDiUng(duLieu: Record<string, any>): number {
  let count = 0;
  const dsWarnings = Array.isArray(duLieu.warnings)
    ? duLieu.warnings
    : Array.isArray(duLieu?.canh_bao?.toan_ca)
      ? duLieu.canh_bao.toan_ca
      : [];

  for (const w of dsWarnings) {
    if (!w || typeof w !== "object") continue;
    const tag = `${w.code || w.ma || ""} ${w.group || w.nhom || ""} ${w.title || w.tieu_de || ""}`.toLowerCase();
    if (/ddi|tuong_tac|tương tác|di_ung|dị ứng|allergy|chong_chi_dinh|chống chỉ định/.test(tag)) {
      count += 1;
    }
  }

  if (Array.isArray(duLieu.ddiWarnings)) count += duLieu.ddiWarnings.length;
  if (Array.isArray(duLieu.allergyWarnings)) count += duLieu.allergyWarnings.length;
  const lsn = duLieu.lam_sang_nang_cao;
  if (lsn && typeof lsn === "object") {
    if (Array.isArray(lsn.ddi)) count += lsn.ddi.length;
    if (Array.isArray(lsn.di_ung)) count += lsn.di_ung.length;
  }

  return count;
}

export function taoRouterQuanTriBv(ctx?: { db?: DatabaseSync }): express.Router {
  const router = express.Router();
  const targetDb = ctx?.db ?? defaultDb;
  const worm = ctx?.db ? taoKhoWorm(ctx.db) : khoWorm;

  router.get("/api/quan-tri-bv/tong-quan", (req, res) => {
    try {
      const uid = req.nguoiDung?.id;
      if (typeof uid !== "number") {
        return res.status(401).json({ error: "Chưa đăng nhập" });
      }
      const laQuanTri = req.nguoiDung?.vai === "quan_tri";

      const caRows = targetDb
        .prepare(
          `SELECT c.nguoi_dung_id, c.id, c.du_lieu, u.ho_ten
           FROM ca_kham c
           LEFT JOIN nguoi_dung u ON u.id = c.nguoi_dung_id`,
        )
        .all() as Array<{ nguoi_dung_id: number; id: string; du_lieu: string; ho_ten: string | null }>;

      const wormSet = new Set<string>();
      try {
        const wormRows = targetDb
          .prepare("SELECT DISTINCT nguoi_dung_id, session_id FROM worm_signoff")
          .all() as Array<{ nguoi_dung_id: number; session_id: string }>;
        for (const r of wormRows) {
          wormSet.add(`${r.nguoi_dung_id}:${r.session_id}`);
        }
      } catch {
        // Bỏ qua nếu bảng worm_signoff chưa khởi tạo
      }

      let tongCaKham = 0;
      let tongCaDaKyWorm = 0;
      let tongNguyCoXuatToanVnd = 0;
      let soCanhBaoDdiVaDiUng = 0;
      let accessCount = 0;
      let watchCount = 0;
      let reserveCount = 0;

      const byDoctor = new Map<
        number,
        {
          bacSiId: number;
          hoTen: string;
          tongCa: number;
          daKyWorm: number;
          nguyCoXuatToanVnd: number;
          soCanhBaoDdiVaDiUng: number;
        }
      >();

      for (const row of caRows) {
        tongCaKham += 1;
        let duLieu: Record<string, any> = {};
        try {
          duLieu = JSON.parse(row.du_lieu || "{}");
        } catch {
          duLieu = {};
        }

        const daKy =
          wormSet.has(`${row.nguoi_dung_id}:${row.id}`) ||
          Boolean(duLieu.wormSignOff || duLieu.worm_seq || duLieu.worm_hash);
        if (daKy) tongCaDaKyWorm += 1;

        const nguyCo = uocTinhNguyCoXuatToanVnd(duLieu);
        tongNguyCoXuatToanVnd += nguyCo;

        const ddiCount = demCanhBaoDdiVaDiUng(duLieu);
        soCanhBaoDdiVaDiUng += ddiCount;

        const dsThuoc = layThuocNhanTuCa(duLieu);
        for (const t of dsThuoc) {
          if (WHO_AWARE_RESERVE.some((kw) => t.includes(kw))) {
            reserveCount += 1;
          } else if (WHO_AWARE_WATCH.some((kw) => t.includes(kw))) {
            watchCount += 1;
          } else if (WHO_AWARE_ACCESS.some((kw) => t.includes(kw))) {
            accessCount += 1;
          }
        }

        if (laQuanTri || row.nguoi_dung_id === uid) {
          const cur = byDoctor.get(row.nguoi_dung_id) || {
            bacSiId: row.nguoi_dung_id,
            hoTen: row.ho_ten || `Bác sĩ #${row.nguoi_dung_id}`,
            tongCa: 0,
            daKyWorm: 0,
            nguyCoXuatToanVnd: 0,
            soCanhBaoDdiVaDiUng: 0,
          };
          cur.tongCa += 1;
          if (daKy) cur.daKyWorm += 1;
          cur.nguyCoXuatToanVnd += nguyCo;
          cur.soCanhBaoDdiVaDiUng += ddiCount;
          byDoctor.set(row.nguoi_dung_id, cur);
        }
      }

      const tongKhangSinh = accessCount + watchCount + reserveCount;
      const tyLeHoanThienHoSo =
        tongCaKham > 0 ? Math.round((tongCaDaKyWorm / tongCaKham) * 1000) / 10 : 0;

      const tyLeKhangSinhAWaRe = {
        access: accessCount,
        watch: watchCount,
        reserve: reserveCount,
        tongKhangSinh,
        tyLeAccessPct: tongKhangSinh > 0 ? Math.round((accessCount / tongKhangSinh) * 1000) / 10 : 0,
        tyLeWatchPct: tongKhangSinh > 0 ? Math.round((watchCount / tongKhangSinh) * 1000) / 10 : 0,
        tyLeReservePct: tongKhangSinh > 0 ? Math.round((reserveCount / tongKhangSinh) * 1000) / 10 : 0,
      };

      const ketQuaKiemDinhWorm = worm.xacMinhChuoi();

      return res.json({
        phamVi: laQuanTri ? "toan_vien" : "ca_nhan",
        tongCaKham,
        tongCaDaKyWorm,
        tyLeHoanThienHoSo,
        tongNguyCoXuatToanVnd,
        soCanhBaoDdiVaDiUng,
        tyLeKhangSinhAWaRe,
        ketQuaKiemDinhWorm,
        theoBacSi: Array.from(byDoctor.values()),
      });
    } catch (err) {
      return traLoi(res, err);
    }
  });

  router.post("/api/quan-tri-bv/kiem-toan-xml", async (req, res) => {
    try {
      const uid = req.nguoiDung?.id;
      if (typeof uid !== "number") {
        return res.status(401).json({ error: "Chưa đăng nhập" });
      }
      const body = req.body && typeof req.body === "object" ? req.body : {};
      const xml_files = body.xml_files || body.xmlFiles || {};
      const bang_chung_kham = body.bang_chung_kham || body.clinicalEvidence || undefined;

      const payload = {
        xml_files,
        ...(bang_chung_kham ? { bang_chung_kham } : {}),
      };

      try {
        const kqHttp = await goiDichVu("/api/bhyt/kiem-toan-xml", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        return res.json(kqHttp);
      } catch (err: any) {
        if (err?.code !== "dich_vu_tat" && err?.status !== 404 && err?.code !== "khong_co_duong") {
          throw err;
        }
      }

      const kqPython = await chayPythonJson("src.cong_cu_lam_sang.kiem_toan_xml_bhyt", ["--audit"], payload);
      return res.json(kqPython);
    } catch (err) {
      return traLoi(res, err);
    }
  });

  return router;
}
