import React from "react";

export interface QrMatrixResult {
  size: number;
  version: number;
  modules: boolean[][];
}

interface VersionSpec {
  version: number;
  totalCodewords: number;
  dataCodewords: number;
  ecPerBlock: number;
  groups: ReadonlyArray<{ blocks: number; dataPerBlock: number }>;
  remainderBits: number;
  alignmentCenters: ReadonlyArray<number>;
}

// ISO/IEC 18004 Table 9 & Table E.1 (Versions 1..10, Error Correction Level L)
const VERSION_SPECS: ReadonlyArray<VersionSpec> = [
  { version: 1, totalCodewords: 26, dataCodewords: 19, ecPerBlock: 7, groups: [{ blocks: 1, dataPerBlock: 19 }], remainderBits: 0, alignmentCenters: [] },
  { version: 2, totalCodewords: 44, dataCodewords: 34, ecPerBlock: 10, groups: [{ blocks: 1, dataPerBlock: 34 }], remainderBits: 7, alignmentCenters: [6, 18] },
  { version: 3, totalCodewords: 70, dataCodewords: 55, ecPerBlock: 15, groups: [{ blocks: 1, dataPerBlock: 55 }], remainderBits: 7, alignmentCenters: [6, 22] },
  { version: 4, totalCodewords: 100, dataCodewords: 80, ecPerBlock: 20, groups: [{ blocks: 1, dataPerBlock: 80 }], remainderBits: 7, alignmentCenters: [6, 26] },
  { version: 5, totalCodewords: 134, dataCodewords: 108, ecPerBlock: 26, groups: [{ blocks: 1, dataPerBlock: 108 }], remainderBits: 7, alignmentCenters: [6, 30] },
  { version: 6, totalCodewords: 172, dataCodewords: 136, ecPerBlock: 18, groups: [{ blocks: 2, dataPerBlock: 68 }], remainderBits: 7, alignmentCenters: [6, 34] },
  { version: 7, totalCodewords: 196, dataCodewords: 156, ecPerBlock: 20, groups: [{ blocks: 2, dataPerBlock: 78 }], remainderBits: 0, alignmentCenters: [6, 22, 38] },
  { version: 8, totalCodewords: 242, dataCodewords: 194, ecPerBlock: 24, groups: [{ blocks: 2, dataPerBlock: 97 }], remainderBits: 0, alignmentCenters: [6, 24, 42] },
  { version: 9, totalCodewords: 292, dataCodewords: 232, ecPerBlock: 30, groups: [{ blocks: 2, dataPerBlock: 116 }], remainderBits: 0, alignmentCenters: [6, 26, 46] },
  { version: 10, totalCodewords: 346, dataCodewords: 274, ecPerBlock: 18, groups: [{ blocks: 2, dataPerBlock: 68 }, { blocks: 2, dataPerBlock: 69 }], remainderBits: 0, alignmentCenters: [6, 28, 50] },
];

// GF(256) with primitive polynomial 0x11d (x^8 + x^4 + x^3 + x^2 + 1)
const GF_EXP = new Uint8Array(512);
const GF_LOG = new Uint8Array(256);
(() => {
  let x = 1;
  for (let i = 0; i < 255; i++) {
    GF_EXP[i] = x;
    GF_LOG[x] = i;
    x <<= 1;
    if (x & 0x100) x ^= 0x11d;
  }
  for (let i = 255; i < 512; i++) {
    GF_EXP[i] = GF_EXP[i - 255];
  }
})();

function gfMul(a: number, b: number): number {
  if (a === 0 || b === 0) return 0;
  return GF_EXP[GF_LOG[a] + GF_LOG[b]];
}

function rsGeneratorPoly(degree: number): Uint8Array {
  let poly = new Uint8Array([1]);
  for (let i = 0; i < degree; i++) {
    const next = new Uint8Array(poly.length + 1);
    const root = GF_EXP[i];
    for (let j = 0; j < poly.length; j++) {
      next[j] ^= poly[j];
      next[j + 1] ^= gfMul(poly[j], root);
    }
    poly = next;
  }
  return poly;
}

function rsComputeRemainder(data: Uint8Array, ecCount: number): Uint8Array {
  const gen = rsGeneratorPoly(ecCount);
  const work = new Uint8Array(data.length + ecCount);
  work.set(data, 0);
  for (let i = 0; i < data.length; i++) {
    const factor = work[i];
    if (factor !== 0) {
      for (let j = 0; j < gen.length; j++) {
        work[i + j] ^= gfMul(gen[j], factor);
      }
    }
  }
  return work.slice(data.length);
}

function selectVersion(byteLen: number): VersionSpec {
  for (const spec of VERSION_SPECS) {
    const countBits = spec.version >= 10 ? 16 : 8;
    const neededBits = 4 + countBits + byteLen * 8;
    if (neededBits <= spec.dataCodewords * 8) {
      return spec;
    }
  }
  throw new Error(`Dữ liệu quá dài cho QR Version 1-10 (${byteLen} bytes > 271 bytes)`);
}

function buildDataCodewords(bytes: Uint8Array, spec: VersionSpec): Uint8Array {
  const bits: number[] = [];
  const pushBits = (val: number, len: number) => {
    for (let i = len - 1; i >= 0; i--) {
      bits.push((val >>> i) & 1);
    }
  };

  // Byte mode = 0100
  pushBits(0b0100, 4);
  pushBits(bytes.length, spec.version >= 10 ? 16 : 8);
  for (let i = 0; i < bytes.length; i++) {
    pushBits(bytes[i], 8);
  }

  const maxBits = spec.dataCodewords * 8;
  const terminatorLen = Math.min(4, maxBits - bits.length);
  for (let i = 0; i < terminatorLen; i++) bits.push(0);
  while (bits.length % 8 !== 0) bits.push(0);

  const codewords = new Uint8Array(spec.dataCodewords);
  let idx = 0;
  for (let i = 0; i < bits.length; i += 8) {
    let b = 0;
    for (let j = 0; j < 8; j++) b = (b << 1) | bits[i + j];
    codewords[idx++] = b;
  }

  let padToggle = 0;
  while (idx < spec.dataCodewords) {
    codewords[idx++] = padToggle === 0 ? 0xec : 0x11;
    padToggle ^= 1;
  }
  return codewords;
}

function interleaveCodewords(data: Uint8Array, spec: VersionSpec): number[] {
  const dataBlocks: Uint8Array[] = [];
  const ecBlocks: Uint8Array[] = [];
  let offset = 0;
  let maxDataLen = 0;

  for (const group of spec.groups) {
    for (let b = 0; b < group.blocks; b++) {
      const slice = data.slice(offset, offset + group.dataPerBlock);
      offset += group.dataPerBlock;
      dataBlocks.push(slice);
      ecBlocks.push(rsComputeRemainder(slice, spec.ecPerBlock));
      if (group.dataPerBlock > maxDataLen) maxDataLen = group.dataPerBlock;
    }
  }

  const allBytes: number[] = [];
  for (let i = 0; i < maxDataLen; i++) {
    for (const blk of dataBlocks) {
      if (i < blk.length) allBytes.push(blk[i]);
    }
  }
  for (let i = 0; i < spec.ecPerBlock; i++) {
    for (const ec of ecBlocks) {
      allBytes.push(ec[i]);
    }
  }

  const allBits: number[] = [];
  for (const byte of allBytes) {
    for (let b = 7; b >= 0; b--) {
      allBits.push((byte >>> b) & 1);
    }
  }
  for (let i = 0; i < spec.remainderBits; i++) {
    allBits.push(0);
  }
  return allBits;
}

function setModule(
  modules: boolean[][],
  isFunc: boolean[][],
  r: number,
  c: number,
  val: boolean
) {
  modules[r][c] = val;
  isFunc[r][c] = true;
}

function drawFinderWithSeparator(
  modules: boolean[][],
  isFunc: boolean[][],
  top: number,
  left: number,
  size: number
) {
  for (let dr = -1; dr <= 7; dr++) {
    for (let dc = -1; dc <= 7; dc++) {
      const r = top + dr;
      const c = left + dc;
      if (r < 0 || r >= size || c < 0 || c >= size) continue;
      const on =
        dr >= 0 &&
        dr <= 6 &&
        dc >= 0 &&
        dc <= 6 &&
        (dr === 0 || dr === 6 || dc === 0 || dc === 6 || (dr >= 2 && dr <= 4 && dc >= 2 && dc <= 4));
      setModule(modules, isFunc, r, c, on);
    }
  }
}

function drawAlignmentPattern(
  modules: boolean[][],
  isFunc: boolean[][],
  centerR: number,
  centerC: number
) {
  for (let dr = -2; dr <= 2; dr++) {
    for (let dc = -2; dc <= 2; dc++) {
      const dist = Math.max(Math.abs(dr), Math.abs(dc));
      setModule(modules, isFunc, centerR + dr, centerC + dc, dist !== 1);
    }
  }
}

function computeFormatBits(maskPattern: number): number {
  // Error correction level L = 01
  const data = (0b01 << 3) | maskPattern;
  let rem = data << 10;
  const gen = 0x537;
  for (let i = 14; i >= 10; i--) {
    if ((rem >>> i) & 1) {
      rem ^= gen << (i - 10);
    }
  }
  return ((data << 10) | rem) ^ 0x5412;
}

function computeVersionBits(version: number): number {
  let rem = version << 12;
  const gen = 0x1f25;
  for (let i = 17; i >= 12; i--) {
    if ((rem >>> i) & 1) {
      rem ^= gen << (i - 12);
    }
  }
  return (version << 12) | rem;
}

function drawFormatInfo(
  modules: boolean[][],
  isFunc: boolean[][],
  size: number,
  maskPattern: number
) {
  const bits = computeFormatBits(maskPattern);
  for (let i = 0; i < 15; i++) {
    const bit = Boolean((bits >>> i) & 1);
    // Vertical along col 8 (top-left) and bottom-left
    if (i < 6) {
      setModule(modules, isFunc, i, 8, bit);
    } else if (i < 8) {
      setModule(modules, isFunc, i + 1, 8, bit);
    } else {
      setModule(modules, isFunc, size - 15 + i, 8, bit);
    }

    // Horizontal along row 8 (top-right) and top-left
    if (i < 8) {
      setModule(modules, isFunc, 8, size - 1 - i, bit);
    } else if (i < 9) {
      setModule(modules, isFunc, 8, 15 - i, bit);
    } else {
      setModule(modules, isFunc, 8, 14 - i, bit);
    }
  }
}

function drawVersionInfo(
  modules: boolean[][],
  isFunc: boolean[][],
  size: number,
  version: number
) {
  if (version < 7) return;
  const bits = computeVersionBits(version);
  for (let i = 0; i < 18; i++) {
    const bit = Boolean((bits >>> i) & 1);
    const a = Math.floor(i / 3);
    const b = i % 3;
    setModule(modules, isFunc, size - 11 + b, a, bit);
    setModule(modules, isFunc, a, size - 11 + b, bit);
  }
}

function maskCondition(mask: number, r: number, c: number): boolean {
  switch (mask) {
    case 0: return (r + c) % 2 === 0;
    case 1: return r % 2 === 0;
    case 2: return c % 3 === 0;
    case 3: return (r + c) % 3 === 0;
    case 4: return (Math.floor(r / 2) + Math.floor(c / 3)) % 2 === 0;
    case 5: return ((r * c) % 2) + ((r * c) % 3) === 0;
    case 6: return (((r * c) % 2) + ((r * c) % 3)) % 2 === 0;
    case 7: return (((r + c) % 2) + ((r * c) % 3)) % 2 === 0;
    default: return false;
  }
}

function penaltyScore(modules: boolean[][], size: number): number {
  let penalty = 0;

  // Rule 1: 5+ consecutive same-colored modules in row/col
  for (let r = 0; r < size; r++) {
    let runColor = modules[r][0];
    let runLen = 1;
    for (let c = 1; c < size; c++) {
      if (modules[r][c] === runColor) {
        runLen++;
      } else {
        if (runLen >= 5) penalty += 3 + (runLen - 5);
        runColor = modules[r][c];
        runLen = 1;
      }
    }
    if (runLen >= 5) penalty += 3 + (runLen - 5);
  }
  for (let c = 0; c < size; c++) {
    let runColor = modules[0][c];
    let runLen = 1;
    for (let r = 1; r < size; r++) {
      if (modules[r][c] === runColor) {
        runLen++;
      } else {
        if (runLen >= 5) penalty += 3 + (runLen - 5);
        runColor = modules[r][c];
        runLen = 1;
      }
    }
    if (runLen >= 5) penalty += 3 + (runLen - 5);
  }

  // Rule 2: 2x2 blocks of same color
  for (let r = 0; r < size - 1; r++) {
    for (let c = 0; c < size - 1; c++) {
      const v = modules[r][c];
      if (v === modules[r][c + 1] && v === modules[r + 1][c] && v === modules[r + 1][c + 1]) {
        penalty += 3;
      }
    }
  }

  // Rule 3: 1:1:3:1:1 finder-like pattern with 4 light modules on either side
  const checkLine11 = (get: (i: number) => boolean, len: number) => {
    for (let i = 0; i <= len - 11; i++) {
      const p0 = get(i), p1 = get(i + 1), p2 = get(i + 2), p3 = get(i + 3),
        p4 = get(i + 4), p5 = get(i + 5), p6 = get(i + 6), p7 = get(i + 7),
        p8 = get(i + 8), p9 = get(i + 9), p10 = get(i + 10);
      if (
        (!p0 && !p1 && !p2 && !p3 && p4 && !p5 && p6 && p7 && p8 && !p9 && p10) ||
        (p0 && !p1 && p2 && p3 && p4 && !p5 && p6 && !p7 && !p8 && !p9 && !p10)
      ) {
        penalty += 40;
      }
    }
  };
  for (let r = 0; r < size; r++) checkLine11((i) => modules[r][i], size);
  for (let c = 0; c < size; c++) checkLine11((i) => modules[i][c], size);

  // Rule 4: dark/total ratio
  let darkCount = 0;
  for (let r = 0; r < size; r++) {
    for (let c = 0; c < size; c++) {
      if (modules[r][c]) darkCount++;
    }
  }
  const total = size * size;
  const k = Math.floor(Math.abs(darkCount * 20 - total * 10) / total);
  penalty += k * 10;

  return penalty;
}

/**
 * Mã hóa chuỗi UTF-8 thành ma trận QR chuẩn ISO/IEC 18004 (Byte mode, ECC Level L, Version 1-10).
 */
export function encodeQrMatrix(text: string): QrMatrixResult {
  const bytes = new TextEncoder().encode(text);
  const spec = selectVersion(bytes.length);
  const size = spec.version * 4 + 17;
  const dataCodewords = buildDataCodewords(bytes, spec);
  const bitStream = interleaveCodewords(dataCodewords, spec);

  const baseModules: boolean[][] = Array.from({ length: size }, () => Array(size).fill(false));
  const isFunc: boolean[][] = Array.from({ length: size }, () => Array(size).fill(false));

  // Finder patterns + separators
  drawFinderWithSeparator(baseModules, isFunc, 0, 0, size);
  drawFinderWithSeparator(baseModules, isFunc, 0, size - 7, size);
  drawFinderWithSeparator(baseModules, isFunc, size - 7, 0, size);

  // Timing patterns
  for (let i = 8; i < size - 8; i++) {
    const dark = i % 2 === 0;
    setModule(baseModules, isFunc, 6, i, dark);
    setModule(baseModules, isFunc, i, 6, dark);
  }

  // Alignment patterns (Version >= 2)
  const centers = spec.alignmentCenters;
  for (let i = 0; i < centers.length; i++) {
    for (let j = 0; j < centers.length; j++) {
      const r = centers[i];
      const c = centers[j];
      if ((r <= 8 && c <= 8) || (r <= 8 && c >= size - 8) || (r >= size - 8 && c <= 8)) {
        continue;
      }
      drawAlignmentPattern(baseModules, isFunc, r, c);
    }
  }

  // Dark module
  setModule(baseModules, isFunc, 4 * spec.version + 9, 8, true);

  // Reserve format & version info cells before data placement
  drawFormatInfo(baseModules, isFunc, size, 0);
  drawVersionInfo(baseModules, isFunc, size, spec.version);

  // Place data bits in zig-zag sweep
  let bitIdx = 0;
  let upward = true;
  for (let right = size - 1; right >= 1; right -= 2) {
    if (right === 6) right = 5;
    for (let step = 0; step < size; step++) {
      const r = upward ? size - 1 - step : step;
      for (let dx = 0; dx < 2; dx++) {
        const c = right - dx;
        if (!isFunc[r][c]) {
          baseModules[r][c] = bitIdx < bitStream.length ? bitStream[bitIdx] === 1 : false;
          bitIdx++;
        }
      }
    }
    upward = !upward;
  }

  // Select optimal mask 0..7 minimizing ISO/IEC 18004 penalty
  let bestMask = 0;
  let bestScore = Number.POSITIVE_INFINITY;
  let bestModules = baseModules;

  for (let mask = 0; mask < 8; mask++) {
    const candidate = baseModules.map((row, r) =>
      row.map((val, c) => (isFunc[r][c] ? val : val !== maskCondition(mask, r, c)))
    );
    drawFormatInfo(candidate, isFunc, size, mask);
    const score = penaltyScore(candidate, size);
    if (score < bestScore) {
      bestScore = score;
      bestMask = mask;
      bestModules = candidate;
    }
  }

  void bestMask;
  return { size, version: spec.version, modules: bestModules };
}

export interface QrCodeSvgProps {
  value: string;
  size?: number;
  className?: string;
  title?: string;
}

export const QrCodeSvg: React.FC<QrCodeSvgProps> = ({
  value,
  size = 128,
  className = "",
  title = "Mã QR Cổng theo dõi người bệnh",
}) => {
  const matrix = encodeQrMatrix(value);
  const quiet = 2;
  const viewSize = matrix.size + quiet * 2;
  const rects: React.ReactElement[] = [];

  for (let r = 0; r < matrix.size; r++) {
    for (let c = 0; c < matrix.size; c++) {
      if (matrix.modules[r][c]) {
        rects.push(
          React.createElement("rect", {
            key: `${r}-${c}`,
            x: c + quiet,
            y: r + quiet,
            width: 1,
            height: 1,
            fill: "#0F172A",
          })
        );
      }
    }
  }

  return React.createElement(
    "svg",
    {
      viewBox: `0 0 ${viewSize} ${viewSize}`,
      width: size,
      height: size,
      className,
      role: "img",
      "aria-label": title,
      shapeRendering: "crispEdges",
    },
    React.createElement("rect", {
      x: 0,
      y: 0,
      width: viewSize,
      height: viewSize,
      fill: "#FFFFFF",
    }),
    ...rects
  );
};
