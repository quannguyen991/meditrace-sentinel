/**
 * Mọi lối đưa hồ sơ ra khỏi phần mềm (chép, in, tải tệp) phải được biết trước và, nếu xuất HỒ SƠ,
 * phải khóa trước khi bác sĩ ký (Đề cải tiến 1, phát hiện của rà soát độc lập 28/11).
 *
 * 1. Component nào có clipboard / window.print / tải tệp phải nằm trong một trong hai danh sách dưới.
 *    Thêm component xuất mới mà quên phân loại thì test đỏ.
 * 2. Trong NoteEditorView, mọi chỗ mở hộp xuất hồ sơ phải đi qua `dungHoSo.duoc`.
 */
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const THU_MUC = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../components");

/** Hộp xuất HỒ SƠ (dữ liệu từ bản nháp) → setter mở nó trong NoteEditorView. */
const HOP_XUAT_HO_SO: Record<string, string> = {
  "BhytPrecheckModal.tsx": "setMoModalBhyt",
  "BangDoiSoatThuocVaDonQuocGiaModal.tsx": "setMoModalThuocTt26",
  "CamDoanThuThuatModal.tsx": "setMoModalCamDoanPttt",
  "DiBuongNoiTruModal.tsx": "setMoModalDiBuong",
  "SbarModal.tsx": "setMoModalSbar",
  "HisSmartCopyPopover.tsx": "setMoPanelHis",
  "ToDanDoBenhNhanModal.tsx": "setMoModalDanDo",
};

/** Có chép/tải nhưng KHÔNG phải hồ sơ đã soạn, kèm lý do. */
const MIEN: Record<string, string> = {
  "NoteEditorView.tsx": "chính màn bản nháp: các hàm chép/in/tải đều kiểm dungHoSo.duoc (choPhepDungHoSo.test.ts)",
  "TranscriptView.tsx": "chép lời thoại gốc để đối chiếu, không phải hồ sơ đã soạn",
  "EvidenceView.tsx": "chép câu trích căn cứ",
  "ContextView.tsx": "chép ngữ cảnh bác sĩ tự nhập",
  "ClinicalEvidenceDrawer.tsx": "chép trích dẫn tài liệu y khoa",
  "TraLoiCoNguon.tsx": "chép câu trả lời tra cứu tài liệu",
  "MenuTaiKhoan.tsx": "chép mã mời tài khoản",
};

const MAU_XUAT = /navigator\.clipboard|window\.print|createObjectURL|\.download\s*=/;

test("moi_component_xuat_deu_duoc_phan_loai", () => {
  const coXuat = fs
    .readdirSync(THU_MUC)
    .filter((t) => t.endsWith(".tsx") && MAU_XUAT.test(fs.readFileSync(path.join(THU_MUC, t), "utf-8")));
  const chuaPhanLoai = coXuat.filter((t) => !(t in HOP_XUAT_HO_SO) && !(t in MIEN));
  assert.deepEqual(chuaPhanLoai, [], "component có lối chép/in/tải chưa được phân loại");
});

test("moi_cho_mo_hop_xuat_ho_so_deu_kiem_ky", () => {
  const dong = fs.readFileSync(path.join(THU_MUC, "NoteEditorView.tsx"), "utf-8").split("\n");
  for (const setter of Object.values(HOP_XUAT_HO_SO)) {
    const cho = dong
      .map((d, i) => ({ d, i }))
      .filter(({ d }) => new RegExp(`${setter}\\((true|\\(v\\))`).test(d));
    assert.ok(cho.length > 0, `không thấy chỗ mở ${setter}`);
    for (const { i } of cho) {
      const canh = dong.slice(Math.max(0, i - 3), i + 1).join("\n");
      assert.ok(/dungHoSo\.duoc/.test(canh), `${setter} ở dòng ${i + 1} mở được khi chưa ký`);
    }
  }
});
