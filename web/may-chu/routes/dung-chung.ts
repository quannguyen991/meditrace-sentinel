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

/** Gọi dịch vụ tại chỗ; lỗi mạng trả về thông điệp nói rõ phải bật dịch vụ nào. */
export async function goiDichVu(duong: string, tuyChon?: RequestInit) {
  let res: Response;
  const internalToken = (process.env.MEDITRACE_INTERNAL_TOKEN || "").trim();
  const baseHeaders = (tuyChon?.headers || {}) as Record<string, string>;
  const headers = internalToken ? { ...baseHeaders, "X-MediTrace-Internal-Token": internalToken } : baseHeaders;
  try {
    res = await fetch(`${API}${duong}`, { ...(tuyChon || {}), headers, dispatcher: choLau } as any);
  } catch (err: any) {
    const e: any = new Error(
      `Không kết nối được dịch vụ MediTrace ở ${API}. Chạy: python -m src.dich_vu --cong 8765 ` +
        `trong thư mục D:\\Claude\\meditrace-core (${err?.message || err}).`,
    );
    e.status = 503;
    throw e;
  }
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const e: any = new Error(data?.thong_diep || `Dịch vụ trả mã ${res.status}`);
    e.status = res.status;
    e.code = data?.loi;
    throw e;
  }
  return data;
}

export function traLoi(res: express.Response, err: any) {
  if (res.headersSent) return;
  const raw = Number(err?.status || err?.statusCode || err?.ma);
  const status = Number.isInteger(raw) && raw >= 100 && raw <= 599 ? raw : 500;
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
          if (code !== 0) return reject(new Error(err || `Python exited with ${code}`));
          try {
            resolve(JSON.parse(out.trim()));
          } catch {
            reject(new Error(`JSON không hợp lệ từ ${moduleName}: ${out.slice(0, 200)}`));
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
