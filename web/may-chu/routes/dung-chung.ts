import express from "express";
import fs from "fs";
import path from "path";
import { spawn } from "child_process";
import { Agent } from "undici";

// Thư mục gốc dự án web. Không dùng import.meta.url: bản build (dist/server.cjs, dạng CommonJS) không có nó.
export const GOC = process.cwd();
export const API = (process.env.MEDITRACE_API || "http://127.0.0.1:8765").replace(/\/$/, "");
export const TUOI_VIEC_TOI_DA_MS = 60 * 60_000;

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
  const status = err?.status || 500;
  res.status(status).json({ error: err?.message || "Lỗi không rõ", code: err?.code });
}

/** Chạy module Python tại chỗ (truyền JSON qua stdin, nhận JSON qua stdout). */
export function chayPythonJson(moduleName: string, args: string[], inputObj: unknown): Promise<any> {
  return new Promise((resolve, reject) => {
    const repoRoot = path.resolve(GOC, "..");
    const venvPy = "D:\\khkt-venv-lap\\Scripts\\python.exe";
    const pyBin = process.env.PYTHON_BIN || (fs.existsSync(venvPy) ? venvPy : "python");
    const child = spawn(pyBin, ["-m", moduleName, ...args], {
      cwd: repoRoot,
      env: { ...process.env, PYTHONUTF8: "1" },
    });
    let out = "";
    let err = "";
    const timer = setTimeout(() => {
      child.kill();
      reject(new Error(`Timeout khi chạy ${moduleName}`));
    }, 15000);
    child.stdout.on("data", (d) => (out += d.toString("utf8")));
    child.stderr.on("data", (d) => (err += d.toString("utf8")));
    child.on("close", (code) => {
      clearTimeout(timer);
      if (code !== 0) return reject(new Error(err || `Python exited with ${code}`));
      try {
        resolve(JSON.parse(out.trim()));
      } catch {
        reject(new Error(`JSON không hợp lệ từ ${moduleName}: ${out.slice(0, 200)}`));
      }
    });
    child.stdin.write(JSON.stringify(inputObj || {}));
    child.stdin.end();
  });
}
