import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { API_CONTRACT_SCHEMA } from "./api-contract";

test("api-contract: TypeScript interfaces khop hai chieu voi API_CONTRACT_SCHEMA va src/he_thong/hop_dong_api.py", () => {
  const tsSrc = fs.readFileSync(path.join(import.meta.dirname, "api-contract.ts"), "utf-8");
  const pyPath = path.resolve(import.meta.dirname, "..", "..", "..", "src", "he_thong", "hop_dong_api.py");
  const pySrc = fs.readFileSync(pyPath, "utf-8");

  // Trich xuat CONTRACT_SCHEMA tu Python de doi chieu hai chieu
  const pySchemaMatch = pySrc.match(/CONTRACT_SCHEMA[\s\S]*?=\s*\{([\s\S]*?)\n\}/);
  assert.ok(pySchemaMatch, "Khong tim thay CONTRACT_SCHEMA trong src/he_thong/hop_dong_api.py");
  const pyBlock = pySchemaMatch[1];

  const pyEntries = new Map<string, string[]>();
  const entryRe = /"(Py\w+)":\s*\{\s*"required":\s*\[([\s\S]*?)\]\s*,?\s*\}/g;
  for (const m of pyBlock.matchAll(entryRe)) {
    const fields = [...m[2].matchAll(/"([^"]+)"/g)].map((x) => x[1]);
    pyEntries.set(m[1], fields);
  }

  assert.deepEqual(
    [...pyEntries.keys()].sort(),
    Object.keys(API_CONTRACT_SCHEMA).sort(),
    "Danh sach contract trong Python va TypeScript khong khop",
  );

  for (const [iface, fields] of Object.entries(API_CONTRACT_SCHEMA)) {
    assert.deepEqual(
      [...fields],
      pyEntries.get(iface),
      `Danh sach truong bat buoc cua ${iface} lech giua TS va Python`,
    );

    const ifaceRe = new RegExp(`export\\s+interface\\s+${iface}\\s*\\{([\\s\\S]*?)\\n\\}`);
    const match = tsSrc.match(ifaceRe);
    assert.ok(match, `Thieu interface ${iface} trong api-contract.ts`);
    for (const field of fields) {
      // Truong bat buoc trong contract khong duoc de optional (?:) trong TS
      assert.match(
        match[1],
        new RegExp(`\\b${field}\\s*:`),
        `Truong bat buoc ${field} trong ${iface} thieu hoac bi danh dau optional`,
      );
    }
  }
});
