import assert from "node:assert/strict";
import test from "node:test";
import { anDanhVanBanNgoai } from "../../may-chu/an-danh-ngoai.ts";
import { gonMenhDeGui } from "./troLy.ts";
import { khoiPhucAudioIDB, luuChunkAudioIDB, xoaAudioIDB } from "../services/realAudioService.ts";

test("anDanhVanBanNgoai: che dia chi co dau phay, SDT, CCCD, BHYT va email", () => {
  const bang = new Map<string, string>();
  const raw =
    "Bệnh nhân địa chỉ: 123 Nguyễn Trãi, phường 5, quận 5, TP HCM. " +
    "Liên hệ 0912345678, email test.bn@example.com, CCCD 079090001234, thẻ BHYT GD4791234567890.";
  const masked = anDanhVanBanNgoai(raw, bang) as string;
  assert.equal(masked.includes("Nguyễn Trãi"), false);
  assert.equal(masked.includes("quận 5"), false);
  assert.equal(masked.includes("0912345678"), false);
  assert.equal(masked.includes("test.bn@example.com"), false);
  assert.equal(masked.includes("079090001234"), false);
  assert.equal(masked.includes("GD4791234567890"), false);
  assert.ok(bang.size >= 5);
});

test("RealAudioService IndexedDB helpers: an toan khi khong co indexedDB (SSR/Node)", async () => {
  await luuChunkAudioIDB("s1", new Blob(["abc"]), "audio/webm");
  const rec = await khoiPhucAudioIDB("s1");
  assert.equal(rec, null);
  await xoaAudioIDB("s1");
});

test("gonMenhDeGui: loai bo trich dan va luot thoai truoc khi gui TroLyTacTu", () => {
  const gon = gonMenhDeGui([
    {
      id: 1,
      text: "Tăng huyết áp",
      section: "CHẨN ĐOÁN",
      subject: "bệnh nhân",
      negated: false,
      certainty: "chắc chắn",
      drug: "Amlodipin 5mg",
      quotes: ["Tôi bị cao huyết áp từ 3 năm trước"],
      evidenceTurns: [2],
    },
  ]);
  assert.equal(gon.length, 1);
  assert.equal("quotes" in gon[0], false);
  assert.equal("evidenceTurns" in gon[0], false);
  assert.equal(gon[0].drug, "Amlodipin 5mg");
});
