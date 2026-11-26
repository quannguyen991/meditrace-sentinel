import assert from "node:assert/strict";
import test from "node:test";
import { encodeQrMatrix } from "./qrEncoder";

function assertFinderPattern(modules: boolean[][], top: number, left: number) {
  for (let r = 0; r < 7; r++) {
    for (let c = 0; c < 7; c++) {
      const expected =
        r === 0 || r === 6 || c === 0 || c === 6 || (r >= 2 && r <= 4 && c >= 2 && c <= 4);
      assert.equal(
        modules[top + r][left + c],
        expected,
        `Finder mismatch at (${top + r}, ${left + c})`
      );
    }
  }
}

test("QR Version 1 (21x21) for short ASCII URL has valid finder, timing, and dark module", () => {
  const qr = encodeQrMatrix("https://mt.vn/p1"); // 16 bytes <= 17 bytes (V1-L)
  assert.equal(qr.version, 1);
  assert.equal(qr.size, 21);
  assert.equal(qr.modules.length, 21);
  assert.equal(qr.modules[0].length, 21);

  assertFinderPattern(qr.modules, 0, 0);
  assertFinderPattern(qr.modules, 0, 14);
  assertFinderPattern(qr.modules, 14, 0);

  // Timing patterns at row 6 and col 6
  for (let i = 8; i < 21 - 8; i++) {
    assert.equal(qr.modules[6][i], i % 2 === 0);
    assert.equal(qr.modules[i][6], i % 2 === 0);
  }

  // Dark module at (4*1 + 9, 8) = (13, 8)
  assert.equal(qr.modules[13][8], true);
});

test("QR Version 2 (25x25) and Version 3 (29x29) include alignment patterns", () => {
  const v2 = encodeQrMatrix("https://mt.vn/?portal=abc123"); // 28 bytes: >17, <=32 (V2-L)
  assert.equal(v2.version, 2);
  assert.equal(v2.size, 25);
  // Alignment pattern centered at (18, 18): center is dark, 3x3 ring around center is light, 5x5 border is dark
  assert.equal(v2.modules[18][18], true);
  assert.equal(v2.modules[17][18], false);
  assert.equal(v2.modules[16][18], true);

  const v3 = encodeQrMatrix("https://mt.vn/?portal=token_42_bytes_v3_qr"); // 42 bytes: >32, <=53 (V3-L)
  assert.equal(v3.version, 3);
  assert.equal(v3.size, 29);
  assert.equal(v3.modules[22][22], true);
  assert.equal(v3.modules[21][22], false);
  assert.equal(v3.modules[20][22], true);
});

test("QR supports UTF-8 Vietnamese URLs up to Version 7-10 and is deterministic", () => {
  const url = "https://meditrace.vn/?portal=bn_nguyen_thi_minh&chan_doan=Suy_tim_độ_II&hen=7_ngay";
  const a = encodeQrMatrix(url);
  const b = encodeQrMatrix(url);
  assert.deepEqual(a, b);
  assert.ok(a.version >= 4 && a.version <= 10);
  assert.equal(a.size, a.version * 4 + 17);

  // Test long ~240-byte payload (Version 9 or 10)
  const longPayload = "https://meditrace.vn/?portal=" + "a".repeat(210);
  const vLong = encodeQrMatrix(longPayload);
  assert.ok(vLong.version >= 9 && vLong.version <= 10);
  assert.equal(vLong.modules[4 * vLong.version + 9][8], true);
});

test("Throws clear error when payload exceeds Version 10 capacity", () => {
  assert.throws(() => encodeQrMatrix("x".repeat(300)), /Version 1-10/);
});
