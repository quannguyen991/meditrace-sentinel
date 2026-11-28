/**
 * Sinh `docs/minh-bach/so-do-du-lieu.md` từ `LOI_RA_DUOC_PHEP` và `NOI_LUU_DU_LIEU` (Đề cải tiến 1).
 * Chạy: `cd web; npx tsx may-chu/sinh-so-do-du-lieu.ts`. Test `sinh-so-do-du-lieu.test.ts` đỏ khi tệp lệch với mã.
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { LOI_RA_DUOC_PHEP } from "./loi-ra-mang";
import { NOI_LUU_DU_LIEU } from "./noi-luu-du-lieu";

const THU_MUC = path.dirname(fileURLToPath(import.meta.url));
export const TEP_SO_DO = path.resolve(THU_MUC, "../../docs/minh-bach/so-do-du-lieu.md");

const o = (s: string) => s.replace(/\|/g, "\\|");
const nhan = (s: string) => s.replace(/"/g, "'");
const DINH_DANH = { co: "có", khong: "không", da_che: "đã che" } as const;
const MAC_DINH = { bat: "mở", tat: "**tắt**" } as const;

export function sinhSoDoDuLieu(): string {
  const dong: string[] = [];
  dong.push("# Sơ đồ dữ liệu — MediTrace Sentinel", "");
  dong.push(
    "Dữ liệu ca khám đi đâu, lưu ở đâu, và lối nào ra khỏi máy. Tệp này **sinh từ mã**: danh sách lối ra mạng",
    "(`web/may-chu/loi-ra-mang.ts`, có test đếm mọi lời gọi mạng của máy chủ) và danh sách nơi lưu",
    "(`web/may-chu/noi-luu-du-lieu.ts`). Mã thêm lối ra mà không khai báo thì test đỏ.",
    "",
  );
  dong.push("## Luồng chính", "");
  dong.push("```mermaid", "flowchart LR");
  dong.push('  MIC["Micro phòng khám"] --> TD["Trình duyệt của bác sĩ"]');
  dong.push('  TD --> WEB["Máy chủ web MediTrace<br/>(máy của bệnh viện / HoaiĐức)"]');
  dong.push('  WEB --> PY["Dịch vụ Python tại chỗ<br/>PhoWhisper chép lời · Qwen3-4B trích mệnh đề<br/>luật kiểm căn cứ K1–K7"]');
  dong.push('  WEB --> DB[("SQLite tại chỗ<br/>ca khám · sổ ký WORM")]');
  dong.push('  PY --> AU[("Thư mục phiên âm thanh")]');
  dong.push('  BS(["Bác sĩ duyệt và ký"]) --> TD');
  LOI_RA_DUOC_PHEP.forEach((m, i) => {
    if (m.tep.endsWith("dung-chung.ts")) return; // dịch vụ Python tại chỗ đã vẽ ở trên
    dong.push(`  WEB -. "${nhan(m.duLieu.split(";")[0])} · mặc định ${m.macDinh === "tat" ? "TẮT" : "mở"}" .-> R${i}["${nhan(m.dich)}"]`);
  });
  dong.push('  NG(["Người xem bản demo công khai"]) -. "chỉ dữ liệu mô phỏng" .-> CF["Cloudflare Worker + đường hầm<br/>(chỉ chuyển tiếp)"] --> WEB');
  dong.push("```", "");
  dong.push(
    "Bản demo công khai đi qua Cloudflare: mã Worker chỉ chuyển tiếp, không lưu hay đọc nội dung, nhưng Cloudflare",
    "là nơi giải mã TLS nên vẫn thấy lưu lượng. Vì vậy bản demo **chỉ dùng dữ liệu mô phỏng** (màn đăng nhập có ghi).",
    "Bản cho phòng khám chạy hoàn toàn trong mạng của bệnh viện.",
    "",
  );
  dong.push("## Lối ra mạng", "");
  dong.push("| Đích | Để làm gì | Dữ liệu đi ra và cách bảo vệ | Mặc định | Mã |", "|---|---|---|---|---|");
  for (const m of LOI_RA_DUOC_PHEP) {
    dong.push(`| ${o(m.dich)} | ${o(m.mucDich)} | ${o(m.duLieu)} | ${MAC_DINH[m.macDinh]} | \`web/${m.tep}\` |`);
  }
  dong.push(
    "",
    "Dịch vụ Python có đúng một lối ra mạng: gọi máy xa của đội khi chạy với `--mo-hinh-xa` (mặc định không bật);",
    "hội thoại được che định danh và kiểm lại trước khi gửi, còn sót thì từ chối (`src/he_thong/dich_vu_http.py`,",
    "test `tests/test_loi_ra_mang_python.py`).",
    "",
  );
  dong.push("## Nơi lưu dữ liệu", "");
  dong.push("| Nơi | Nội dung | Có định danh | Ai đọc được | Giữ bao lâu | Mã |", "|---|---|---|---|---|---|");
  for (const n of NOI_LUU_DU_LIEU) {
    dong.push(`| ${o(n.noi)} | ${o(n.noiDung)} | ${DINH_DANH[n.coDinhDanh]} | ${o(n.aiDoc)} | ${o(n.giu)} | \`${n.tep}\` |`);
  }
  dong.push("", "## Dữ liệu dùng khi phát triển", "");
  dong.push(
    "Chỉ dữ liệu mô phỏng và bộ dữ liệu công khai (xem `docs/nguon-va-giay-phep.md`).",
    "Chưa từng đưa hồ sơ bệnh nhân thật vào công cụ AI nào (tác giả xác nhận 28/11/2026).",
    "Cổng mô hình ngoài AIBOX là dịch vụ bên thứ ba (tác giả xác nhận 28/11/2026).",
    "",
    "---",
    "Tệp này sinh từ `web/may-chu/sinh-so-do-du-lieu.ts`; sửa danh sách rồi chạy lại, không sửa tay.",
    "",
  );
  return dong.join("\n");
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  fs.mkdirSync(path.dirname(TEP_SO_DO), { recursive: true });
  fs.writeFileSync(TEP_SO_DO, sinhSoDoDuLieu(), "utf-8");
  console.log(`Đã ghi ${TEP_SO_DO}`);
}
