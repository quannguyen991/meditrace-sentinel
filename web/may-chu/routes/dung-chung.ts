import express from "express";
import fs from "fs";
import path from "path";
import { spawn } from "child_process";
import { Agent } from "undici";

// Thư mục gốc dự án web. Không dùng import.meta.url: bản build (dist/server.cjs, dạng CommonJS) không có nó.
export const GOC = process.cwd();
export const API = (process.env.MEDITRACE_API || "http://127.0.0.1:8765").replace(/\/$/, "");
/** Giữ kết quả việc hoàn tất trong 30 phút để F5 / đa tab đọc lại không bị 404. */
export const TUOI_VIEC_TOI_DA_MS = 30 * 60_000;

/**
 * `fetch` của Node tự cắt sau 300 giây chờ phản hồi. Khâu tách mệnh đề cho một hội thoại mới
 * chạy lâu hơn thế khi GPU dùng chung (đo 23/09: hơn 5 phút trên HoaiDuc). Cho chờ tới 30 phút.
 */
const choLau = new Agent({ headersTimeout: 30 * 60_000, bodyTimeout: 30 * 60_000 });

/** Tên header mang khoá nội bộ; dịch vụ Python (src/dich_vu.py) đòi header này ở mọi /api. */
export const HEADER_TOKEN_NOI_BO = "X-MediTrace-Internal-Token";

/** Lỗi có thông điệp được phép đưa nguyên văn cho người dùng kể cả khi mã >= 500. */
export function loiCongKhai(thongDiep: string, status: number, code?: string): Error {
  return Object.assign(new Error(thongDiep), { status, congKhai: true, ...(code ? { code } : {}) });
}

/** Gọi dịch vụ tại chỗ; luôn kèm khoá nội bộ từ env MEDITRACE_INTERNAL_TOKEN, thiếu khoá thì dừng ngay. */
export async function goiDichVu(duong: string, tuyChon?: RequestInit) {
  const internalToken = (process.env.MEDITRACE_INTERNAL_TOKEN || "").trim();
  if (!internalToken) {
    console.error("[dich-vu] Thiếu biến môi trường MEDITRACE_INTERNAL_TOKEN — không gọi dịch vụ MediTrace.");
    throw loiCongKhai(
      "Máy chủ web chưa cấu hình MEDITRACE_INTERNAL_TOKEN (khoá nội bộ dùng chung với dịch vụ MediTrace). " +
        "Đặt cùng một giá trị cho cả máy chủ web và dịch vụ Python rồi khởi động lại.",
      503,
      "thieu_token_noi_bo",
    );
  }
  const baseHeaders: Record<string, string> = {};
  for (const [k, v] of Object.entries((tuyChon?.headers || {}) as Record<string, string>)) {
    if (k.toLowerCase() !== HEADER_TOKEN_NOI_BO.toLowerCase()) baseHeaders[k] = v;
  }
  const headers = { ...baseHeaders, [HEADER_TOKEN_NOI_BO]: internalToken };
  let res: Response;
  try {
    res = await fetch(`${API}${duong}`, { ...(tuyChon || {}), headers, dispatcher: choLau } as any);
  } catch (err: any) {
    console.error(`[dich-vu] Không kết nối được ${API}${duong}:`, err?.message || err);
    throw loiCongKhai("Không kết nối được dịch vụ MediTrace chạy tại chỗ. Hãy bật dịch vụ rồi thử lại.", 503, "dich_vu_tat");
  }
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    if (res.status === 401 || res.status === 403) {
      console.error(`[dich-vu] Dịch vụ từ chối khoá nội bộ (${res.status}) tại ${duong}`);
      throw loiCongKhai(
        "Dịch vụ MediTrace từ chối khoá nội bộ — kiểm tra MEDITRACE_INTERNAL_TOKEN hai bên trùng nhau.",
        502,
        "token_noi_bo_sai",
      );
    }
    const e: any = new Error(data?.thong_diep || `Dịch vụ trả mã ${res.status}`);
    e.status = res.status;
    e.code = data?.loi;
    throw e;
  }
  return data;
}

/** Trả lỗi JSON. Mã >= 500 chỉ trả thông điệp chung (chi tiết ghi log máy chủ), trừ lỗi đánh dấu `congKhai`. */
export function traLoi(res: express.Response, err: any) {
  if (res.headersSent) return;
  const raw = Number(err?.status || err?.statusCode || err?.ma);
  const status = Number.isInteger(raw) && raw >= 100 && raw <= 599 ? raw : 500;
  if (status >= 500 && !err?.congKhai) {
    console.error(`[loi ${status}]`, err?.stack || err?.message || err);
    res.status(status).json({
      error: "Lỗi máy chủ nội bộ. Chi tiết đã ghi vào nhật ký máy chủ.",
      ...(err?.code ? { code: err.code } : {}),
    });
    return;
  }
  res.status(status).json({ error: err?.message || "Lỗi không rõ", ...(err?.code ? { code: err.code } : {}) });
}

/* ------------------------------------------------------------------ Semaphore giới hạn tiến trình Python con */
const TOI_DA_PYTHON_CON = 2;
const TOI_DA_CHO_PYTHON = 32;
let soPythonDangChay = 0;
let dinhPythonDongThoi = 0;
const hangChoPython: Array<() => void> = [];

function xinLuotPython(): Promise<() => void> {
  return new Promise((resolve, reject) => {
    const capPhat = () => {
      soPythonDangChay++;
      if (soPythonDangChay > dinhPythonDongThoi) dinhPythonDongThoi = soPythonDangChay;
      let daTra = false;
      resolve(() => {
        if (daTra) return;
        daTra = true;
        soPythonDangChay--;
        const tiep = hangChoPython.shift();
        if (tiep) tiep();
      });
    };

    if (soPythonDangChay < TOI_DA_PYTHON_CON) {
      capPhat();
      return;
    }
    if (hangChoPython.length >= TOI_DA_CHO_PYTHON) {
      const e: any = new Error("Máy chủ đang xử lý quá nhiều tác vụ Python cục bộ. Vui lòng thử lại sau giây lát.");
      e.status = 503;
      e.code = "python_busy";
      reject(e);
      return;
    }
    hangChoPython.push(capPhat);
  });
}

export function thongKePythonCon() {
  return { dangChay: soPythonDangChay, dangCho: hangChoPython.length, dinhDongThoi: dinhPythonDongThoi };
}

export function datLaiDinhPythonCon() {
  dinhPythonDongThoi = soPythonDangChay;
}

/**
 * Chạy module Python tại chỗ (truyền JSON qua stdin, nhận JSON qua stdout).
 * Giới hạn semaphore tối đa 2 tiến trình Python con đồng thời để chống fork-bomb.
 */
export async function chayPythonJson(moduleName: string, args: string[], inputObj: unknown): Promise<any> {
  const nhaLuot = await xinLuotPython();
  try {
    return await new Promise((resolve, reject) => {
      const repoRoot = path.resolve(GOC, "..");
      const venvPy = "D:\\khkt-venv-lap\\Scripts\\python.exe";
      const pyBin = process.env.PYTHON_BIN || (fs.existsSync(venvPy) ? venvPy : "python");
      const child = spawn(pyBin, ["-m", moduleName, ...args], {
        cwd: repoRoot,
        env: { ...process.env, PYTHONUTF8: "1" },
      });

      let out = "";
      let err = "";
      let daKetThuc = false;
      const hoanTat = (fn: () => void) => {
        if (daKetThuc) return;
        daKetThuc = true;
        clearTimeout(timer);
        fn();
      };

      const timer = setTimeout(() => {
        try {
          child.kill();
        } catch {}
        hoanTat(() => reject(new Error(`Timeout khi chạy ${moduleName}`)));
      }, 15000);

      child.on("error", (spawnErr) => {
        hoanTat(() => reject(new Error(`Không khởi chạy được Python (${moduleName}): ${spawnErr.message}`)));
      });
      child.stdin.on("error", () => {
        // Tiến trình con có thể đóng sớm trước khi ghi hết stdin; sự kiện close sẽ báo mã lỗi chi tiết.
      });
      child.stdout.on("data", (d) => (out += d.toString("utf8")));
      child.stderr.on("data", (d) => (err += d.toString("utf8")));
      child.on("close", (code) => {
        hoanTat(() => {
          if (code !== 0) {
            // stderr của Python có thể chứa đường dẫn máy và traceback: chỉ ghi log, không trả cho người dùng.
            console.error(`[python ${moduleName}] thoát mã ${code}:`, err.slice(-2000));
            return reject(new Error(`Tác vụ Python ${moduleName} thất bại (mã ${code})`));
          }
          try {
            resolve(JSON.parse(out.trim()));
          } catch {
            console.error(`[python ${moduleName}] JSON không hợp lệ:`, out.slice(0, 200));
            reject(new Error(`JSON không hợp lệ từ ${moduleName}`));
          }
        });
      });

      try {
        child.stdin.write(JSON.stringify(inputObj || {}));
        child.stdin.end();
      } catch {}
    });
  } finally {
    nhaLuot();
  }
}
