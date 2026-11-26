/**
 * Dịch vụ miền Tra cứu Y khoa Chính thống:
 *  - `datTuKhoaTraCuu`: phân tích câu hỏi thành từ khóa đa nguồn
 *  - `timTaiLieuTheoTuKhoa`: chạy song song các nguồn y khoa, lọc bài lạc đề
 *  - `soanTraLoiCoNguon`: tổng hợp phương án có trích dẫn kèm kiểm định số liệu `soLech`
 */
import { goiNgoai } from "../routes/llm-ngoai";
import { chuanSo, soLech } from "./kiem-dinh-so";
import {
  datLaiBoDemWHO,
  docBoDemWHO,
  lamDayPMC,
  timAAFP,
  timCDC,
  timFDA,
  timKCBRutDan,
  timMedlinePlus,
  timMSD,
  timNICE,
  timPubMed,
  timStatPearls,
  timWHO,
  vanIRIS,
} from "./nguon-ngoai";
import { gonTenBenh, mucLucPhacDo, soVanBanPhacDo, timPhacDo } from "./phac-do-byt";
import { HOI_CAP, lienQuan, lienQuanChat, MUC_CAP, type TaiLieu, TEN_NGUON, TEN_Y_KHOA } from "./tu-dien";

export {
  type TaiLieu,
  chuanSo,
  soLech,
  timPubMed,
  mucLucPhacDo,
  vanIRIS,
  timWHO,
  docBoDemWHO,
  datLaiBoDemWHO,
};

/** Bước "từ khoá" của tra cứu: một lời gọi mô hình ngoài. Dùng cho route cũ và trợ lý nhiều tác tử. */
export async function datTuKhoaTraCuu(
  cauHoi: string,
  ngucanh: string,
  caKham: string,
  coCa: boolean,
  signal?: AbortSignal,
): Promise<{ tuKhoa: any; b1: { text: string; model: string; usage: any; seconds: number } }> {
  const b1 = await goiNgoai(
    (coCa
      ? "Bác sĩ hỏi trong lúc khám. Nếu câu hỏi CHỈ hỏi thông tin có sẵn trong ca (ai nói gì, bệnh nhân dùng " +
        "thuốc gì, dị ứng gì, khi nào) thì can_tra_cuu=false. Nếu cần kiến thức y khoa (liều, xử trí, " +
        "tương tác, ngưỡng, chẩn đoán phân biệt, nên hỏi/khám thêm gì, dấu hiệu nguy hiểm cần dặn) thì " +
        "can_tra_cuu=true và đặt từ khoá theo bệnh/thuốc của ca. "
      : "") +
      "Chuyển câu hỏi y khoa thành từ khoá tìm kiếm. Trả về DUY NHẤT JSON: " +
      (coCa ? '{"can_tra_cuu":true,' : "{") +
      '"pubmed":"3-6 từ khoá tiếng Anh, thuật ngữ MeSH nếu có","medlineplus":"1-3 từ tiếng Anh, tên bệnh",' +
      '"benh_en":"tên bệnh CHUẨN Y KHOA tiếng Anh 1-3 từ (vd hypertension, asthma, acute sinusitis, dengue), không dùng tên phổ thông",' +
      '"thuoc":["tên hoạt chất theo FDA Hoa Kỳ (vd acetaminophen, albuterol) của thuốc được hỏi, nếu có"],' +
      '"tieng_viet":"MỘT chuỗi 2-4 từ tiếng Việt có dấu: CHỈ tên bệnh hoặc tên thuốc, không kèm cơn/đợt/cấp/mạn (vd: sốt xuất huyết Dengue, hen phế quản)"}',
    `Câu hỏi: ${cauHoi}${ngucanh ? `\nNgữ cảnh: ${String(ngucanh).slice(0, 500)}` : ""}` +
      (coCa ? `\n\nTrích ca khám:\n${caKham.slice(0, 1500)}` : ""),
    200,
    {},
    signal,
  );
  let tuKhoa: any = { pubmed: "", medlineplus: "", thuoc: [], tieng_viet: "" };
  try {
    tuKhoa = { ...tuKhoa, ...JSON.parse(b1.text.match(/\{[\s\S]*\}/)?.[0] || b1.text) };
  } catch {}
  return { tuKhoa, b1 };
}

/** Bước "server tự tìm": chạy song song các nguồn, một nguồn lỗi thì dùng nguồn khác và báo lỗi. */
export async function timTaiLieuTheoTuKhoa(opts: {
  cauHoi: string;
  tuKhoa: any;
  nguon: any;
}): Promise<{
  taiLieu: TaiLieu[];
  daTra: Array<{ nguon: string; so: number; ghiChu?: string }>;
  loiTim: string[];
  boLacDe: number;
  tuKhoaRa: any;
  kcb: any[];
  phacDo: any[];
  thuoc: string[];
  tenAnh: string;
}> {
  const { cauHoi, tuKhoa, nguon } = opts;
  const dungPubMed = nguon?.pubmed !== false;
  const dungMedline = nguon?.medlineplus !== false;
  const dungFDA = nguon?.fda !== false;
  const dungKCB = nguon?.kcb !== false;
  const dungMSD = nguon?.msd !== false;
  const dungNICE = nguon?.nice !== false;
  const dungWHO = nguon?.who !== false;
  const dungCDC = nguon?.cdc !== false;
  const dungSP = nguon?.statpearls !== false;
  const dungAAFP = nguon?.aafp !== false;
  const chiBangChungCao = nguon?.chiBangChungCao === true;
  const thuoc: string[] = Array.isArray(tuKhoa.thuoc) ? tuKhoa.thuoc.filter((x: any) => typeof x === "string") : [];
  const tuVietList: string[] = (Array.isArray(tuKhoa.tieng_viet) ? tuKhoa.tieng_viet : [tuKhoa.tieng_viet]).filter(
    (x: any) => typeof x === "string" && x.trim(),
  );

  const loiTim: string[] = [];
  const bat = (ten: string) => (e: any) => (loiTim.push(`${ten}: ${e?.message || e}`), [] as Omit<TaiLieu, "so">[]);
  const tenPhoThong = String(tuKhoa.medlineplus || tuKhoa.pubmed).split(",")[0].trim();
  const tenAnh = String(tuKhoa.benh_en || "").trim() || TEN_Y_KHOA[tenPhoThong.toLowerCase()] || tenPhoThong;
  const hoiMo = `${cauHoi} ${tuKhoa.pubmed}`;

  const timMSDCaHai = async () => {
    const tenViet = gonTenBenh(tuVietList[0] || "");
    const vi = tenViet ? await timMSD(tenViet, "vi", hoiMo).catch(() => []) : [];
    const coMucCap = (r: any[]) => r.length > 0 && MUC_CAP.test(r[0].noiDung.split("\n").find((d: string) => d.startsWith("## ")) || "");
    if (vi.length && !(HOI_CAP.test(hoiMo) && !coMucCap(vi))) return vi;
    const en = await timMSD(tenAnh, "en", hoiMo).catch(() => []);
    return coMucCap(en) || !vi.length ? en : vi;
  };

  const huaSP = dungSP ? timStatPearls(tenAnh, hoiMo).catch(bat("StatPearls")) : Promise.resolve([]);
  const huaAAFP = dungAAFP ? timAAFP(tenAnh, hoiMo).catch(bat("AAFP")) : Promise.resolve([]);
  const huaQuocTe = Promise.all([
    dungMSD ? timMSDCaHai().catch(bat("MSD")) : Promise.resolve([]),
    dungNICE ? timNICE(tenAnh, hoiMo).catch(bat("NICE")) : Promise.resolve([]),
    dungWHO ? timWHO(tenAnh, hoiMo).catch(bat("WHO")) : Promise.resolve([]),
    dungCDC ? timCDC(tenAnh, hoiMo).catch(bat("CDC")) : Promise.resolve([]),
  ]);
  const [kcb, fda, mp, pmTho] = await Promise.all([
    dungKCB && tuVietList.length ? timKCBRutDan(tuVietList).catch(bat("kcb.vn")) : Promise.resolve([]),
    dungFDA && thuoc.length ? timFDA(thuoc, cauHoi).catch(bat("FDA")) : Promise.resolve([]),
    dungMedline ? timMedlinePlus(tuKhoa.medlineplus || tuKhoa.pubmed).catch(bat("MedlinePlus")) : Promise.resolve([]),
    dungPubMed ? timPubMed(tuKhoa.pubmed, 10, chiBangChungCao).catch(bat("PubMed")) : Promise.resolve([]),
  ]);
  const [msd, nice, who, cdc] = await huaQuocTe;
  const sp = await huaSP;
  const aafp = await huaAAFP;
  const pm = pmTho.filter((t) => lienQuan(t, tuKhoa.pubmed) && lienQuanChat(t, tenAnh, thuoc, cauHoi)).slice(0, 5);
  await lamDayPMC(pm, hoiMo);
  const phacDo = dungKCB ? timPhacDo(cauHoi, tuVietList) : [];
  const boLacDe = pmTho.length - pm.length;
  const kcbGiu = phacDo.length ? kcb.slice(0, 1) : kcb;

  let tong = 0;
  const taiLieu: TaiLieu[] = [...phacDo, ...kcbGiu, ...fda, ...msd, ...sp, ...aafp, ...nice, ...who, ...cdc, ...mp, ...pm].map(
    (t, i) => {
      const noiDung = tong > 28000 ? t.noiDung.slice(0, 500) : t.noiDung;
      tong += noiDung.length;
      return { ...t, noiDung, so: i + 1 };
    },
  );

  const soVbPhacDo = soVanBanPhacDo();
  const daTra = [
    dungKCB && { nguon: `Bộ Y tế — ${soVbPhacDo} phác đồ lưu tại máy`, so: phacDo.length },
    dungKCB && { nguon: "Bộ Y tế — tìm trên kcb.vn", so: kcbGiu.length },
    dungFDA && { nguon: "Nhãn thuốc FDA (DailyMed)", so: fda.length, ghiChu: thuoc.length ? "" : "câu hỏi không nhắc thuốc" },
    dungMSD && { nguon: "MSD Manual Professional (bản tiếng Việt, không có thì bản tiếng Anh)", so: msd.length },
    dungSP && { nguon: "StatPearls (NCBI Bookshelf)", so: sp.length },
    dungAAFP && { nguon: "AAFP — American Family Physician", so: aafp.length },
    dungNICE && { nguon: "NICE — Viện Y tế và Chăm sóc Quốc gia Anh", so: nice.length },
    dungWHO && { nguon: "WHO — Tổ chức Y tế Thế giới", so: who.length },
    dungCDC && { nguon: "CDC — Trung tâm Kiểm soát Bệnh tật Hoa Kỳ", so: cdc.length },
    dungMedline && { nguon: "MedlinePlus (Thư viện Y khoa Quốc gia Hoa Kỳ)", so: mp.length },
    dungPubMed && {
      nguon: "PubMed",
      so: pm.length,
      ghiChu: [
        boLacDe ? `bỏ ${boLacDe} bài lạc đề` : "",
        pm.some((t) => /toàn văn PMC/.test(t.loai || ""))
          ? `${pm.filter((t) => /toàn văn PMC/.test(t.loai || "")).length} bài đọc toàn văn PMC`
          : "",
      ]
        .filter(Boolean)
        .join(", "),
    },
  ].filter(Boolean) as Array<{ nguon: string; so: number; ghiChu?: string }>;
  const tuKhoaRa = { pubmed: tuKhoa.pubmed, medlineplus: tuKhoa.medlineplus, thuoc, tieng_viet: tuVietList };
  return { taiLieu, daTra, loiTim, boLacDe, tuKhoaRa, kcb, phacDo, thuoc, tenAnh };
}

/** Bước "mô hình chỉ tóm tắt": một lời gọi mô hình ngoài, rồi server tự ghép nguồn và cảnh báo. */
export async function soanTraLoiCoNguon(opts: {
  cauHoi: string;
  caKham: string;
  coCa: boolean;
  taiLieu: TaiLieu[];
  daTra: Array<{ nguon: string; so: number; ghiChu?: string }>;
  boLacDe: number;
  loiTim: string[];
  tuKhoaRa: any;
  kcb: any[];
  phacDo: any[];
  caAnDanh?: boolean;
  signal?: AbortSignal;
}): Promise<{
  answer: string;
  sources: any[];
  searched: any[];
  cauTruc: any;
  removedSources: number;
  warning: string | null;
  model: string;
  usage: any;
  seconds: number;
}> {
  const { cauHoi, caKham, coCa, taiLieu, daTra, boLacDe, loiTim, tuKhoaRa, kcb, phacDo, caAnDanh = false, signal } = opts;
  void tuKhoaRa;
  if (!taiLieu.length) {
    return {
      answer: "Không tìm thấy tài liệu nào ở các nguồn đã chọn cho câu hỏi này.",
      sources: [],
      searched: daTra,
      cauTruc: null,
      removedSources: boLacDe,
      warning: "KHÔNG có nguồn nào — không có câu trả lời." + (loiTim.length ? ` Lỗi tìm: ${loiTim.join("; ")}` : ""),
      model: "",
      usage: {},
      seconds: 0,
    };
  }
  const b2 = await goiNgoai(
    "Bạn tổng hợp tài liệu y khoa cho bác sĩ, bằng tiếng Việt. CHỈ dùng các tài liệu được cung cấp; không " +
      "thêm kiến thức ngoài, không tự đặt ra phương án. Liệt kê các PHƯƠNG ÁN / lựa chọn mà tài liệu nêu " +
      "(ví dụ các cách xử trí, các mức liều, các ngưỡng), mỗi phương án ghi số tài liệu dạng [1]. Mỗi phương " +
      "án ghi TẤT CẢ tài liệu nói cùng ý, cả trong nước lẫn nước ngoài, không chỉ tài liệu chi tiết nhất. Nếu tài " +
      "liệu Bộ Y tế Việt Nam và tài liệu nước ngoài nói khác nhau hoặc nước ngoài có thêm điểm (thuốc, liều, " +
      "ngưỡng) thì nêu rõ trong khac_nhau, có số tài liệu. Phần câu hỏi mà tài " +
      "liệu không trả lời được thì nói thẳng. Tài liệu không liên quan thì bỏ qua. Không đưa link. Không " +
      "khẳng định, không kết luận thay bác sĩ. Viết gọn: tối đa 6 phương án, mỗi phương án dưới 70 từ; " +
      "khac_nhau dưới 80 từ. " +
      (coCa
        ? "Có kèm THÔNG TIN CA KHÁM. Ghi thêm: ca_kham = thông tin trong ca liên quan câu hỏi (" +
          (caAnDanh ? "ca đã ẩn danh, không có số lượt nên không ghi số lượt" : "mỗi ý ghi (lượt n)") +
          "); " +
          "luu_y_ca = các điểm trong ca có thể làm một phương án không phù hợp hoặc cần chỉnh (dị ứng, thai, tuổi, " +
          "cân nặng, chức năng thận/gan, thuốc đang dùng, bệnh nền), mỗi điểm ghi " +
          (caAnDanh ? "" : "(lượt n) ") +
          "và số tài liệu. " +
          "Không chọn phương án thay bác sĩ, không kê đơn. Ca không nói thì để rỗng, không suy đoán. "
        : "") +
      "Nếu bác sĩ hỏi NÊN HỎI/KHÁM THÊM GÌ thì mỗi phương án là MỘT câu hỏi hoặc việc khám nên làm (ten = câu " +
      "hỏi, noi_dung = vì sao, theo tài liệu). an_toan = tối đa 3 điểm an toàn tài liệu nêu (dấu hiệu nguy hiểm, " +
      "chống chỉ định, khi nào chuyển viện), mỗi điểm có số tài liệu; tài liệu không nêu thì để rỗng. hoi_tiep = 3 " +
      "câu hỏi tiếp ngắn bác sĩ có thể hỏi hệ thống. " +
      "Trả về DUY NHẤT JSON: {" +
      (coCa ? '"ca_kham":"… hoặc rỗng","luu_y_ca":["…"],' : "") +
      '"tom_tat":"1-2 câu","phuong_an":[{"ten":"…","noi_dung":"…","nguon":[số]}],' +
      '"an_toan":[{"noi_dung":"…","nguon":[số]}],"khac_nhau":"… hoặc rỗng","khong_du":"… hoặc rỗng",' +
      '"hoi_tiep":["…","…","…"],"dung":[số các tài liệu thực sự dùng]}',
    `Câu hỏi của bác sĩ: ${cauHoi}\n\n` +
      (coCa ? `THÔNG TIN CA KHÁM:\n${caKham}\n\n` : "") +
      `Tài liệu:\n` +
      taiLieu
        .map((t) => `[${t.so}] ${t.nguon}${t.loai ? ` · ${t.loai}` : ""}${t.nam ? ` · ${t.nam}` : ""} — ${t.ten}\n${t.noiDung}`)
        .join("\n\n"),
    2500,
    {},
    signal,
  );
  let traLoiMH = b2.text;
  let cauTruc: any = null;
  let dung: number[] = [];
  const cuuJSON = (t: string) => {
    const chuoi = (ten: string) => t.match(new RegExp(`"${ten}"\\s*:\\s*"((?:[^"\\\\]|\\\\.)*)"`))?.[1];
    const pa = [
      ...t.matchAll(/\{\s*"ten"\s*:\s*"((?:[^"\\]|\\.)*)"\s*,\s*"noi_dung"\s*:\s*"((?:[^"\\]|\\.)*)"\s*,\s*"nguon"\s*:\s*\[([\d,\s]*)\]/g),
    ].map((m) => ({ ten: m[1], noi_dung: m[2], nguon: m[3].split(",").map(Number).filter(Boolean) }));
    return {
      ca_kham: chuoi("ca_kham"),
      tom_tat: chuoi("tom_tat"),
      phuong_an: pa,
      an_toan: [],
      hoi_tiep: [],
      khac_nhau: chuoi("khac_nhau"),
      khong_du: chuoi("khong_du") || "Câu trả lời của mô hình bị cắt ngang; có thể thiếu phương án cuối.",
      dung: [...new Set(pa.flatMap((x) => x.nguon))],
    };
  };
  try {
    let j: any;
    try {
      j = JSON.parse(b2.text.match(/\{[\s\S]*\}/)?.[0] || b2.text);
    } catch {
      j = cuuJSON(b2.text);
      if (!j.phuong_an.length && !j.tom_tat) throw new Error("không cứu được JSON");
    }
    dung = (Array.isArray(j.dung) ? j.dung : []).map(Number);
    const so = (ds: any) => (Array.isArray(ds) && ds.length ? " " + ds.map((n: any) => `[${n}]`).join("") : "");
    const pa = (Array.isArray(j.phuong_an) ? j.phuong_an : []).map(
      (x: any, i: number) => `${i + 1}. **${x.ten || "Phương án"}** — ${x.noi_dung || ""}${so(x.nguon)}`,
    );
    const luuY = (Array.isArray(j.luu_y_ca) ? j.luu_y_ca : []).filter((x: any) => typeof x === "string" && x.trim());
    const soHop = (ds: any) => (Array.isArray(ds) ? ds.map(Number).filter((n: number) => taiLieu.some((t) => t.so === n)) : []);
    const anToan = (Array.isArray(j.an_toan) ? j.an_toan : [])
      .map((x: any) => (typeof x === "string" ? { noi_dung: x, nguon: [] } : x))
      .filter((x: any) => x?.noi_dung)
      .map((x: any) => ({ noi_dung: String(x.noi_dung), nguon: soHop(x.nguon) }));
    const vanCua = (soDs: number[]) =>
      taiLieu
        .filter((t) => soDs.includes(t.so))
        .map((t) => `${t.ten} ${t.noiDung}`)
        .join("\n");
    const kiem = (y: string, soDs: number[]) => (soDs.length ? soLech(y, vanCua(soDs)) : []);
    cauTruc = {
      ca_kham: j.ca_kham || "",
      tom_tat: j.tom_tat || "",
      phuong_an: (Array.isArray(j.phuong_an) ? j.phuong_an : [])
        .map((x: any) => ({ ten: String(x.ten || ""), noi_dung: String(x.noi_dung || ""), nguon: soHop(x.nguon) }))
        .map((x: any) => ({ ...x, lech: kiem(`${x.ten} ${x.noi_dung}`, x.nguon) })),
      luu_y_ca: luuY,
      an_toan: anToan.map((x: any) => ({ ...x, lech: kiem(x.noi_dung, x.nguon) })),
      khac_nhau: j.khac_nhau || "",
      khong_du: j.khong_du || "",
      hoi_tiep: (Array.isArray(j.hoi_tiep) ? j.hoi_tiep : []).filter((x: any) => typeof x === "string" && x.trim()).slice(0, 3),
    };
    traLoiMH =
      [
        j.ca_kham ? `**Trong ca khám:** ${j.ca_kham}` : "",
        j.tom_tat ? `**Tóm tắt:** ${j.tom_tat}` : "",
        pa.length ? `**Các phương án tài liệu nêu:**\n${pa.join("\n")}` : "",
        luuY.length ? `**Lưu ý từ ca khám:**\n${luuY.map((x: string) => `- ${x}`).join("\n")}` : "",
        anToan.length ? `**Lưu ý an toàn:**\n${anToan.map((x: any) => `- ${x.noi_dung}${so(x.nguon)}`).join("\n")}` : "",
        j.khac_nhau ? `**Nguồn trong nước và nước ngoài khác nhau ở:** ${j.khac_nhau}` : "",
        j.khong_du ? `**Tài liệu chưa trả lời được:** ${j.khong_du}` : "",
      ]
        .filter(Boolean)
        .join("\n\n") || traLoiMH;
  } catch {}

  const soTrongVan = [...traLoiMH.matchAll(/\[(\d+)\]/g)].map((m) => Number(m[1]));
  const soTrich = new Set(dung.length ? dung : soTrongVan);
  const soLa = [...new Set([...dung, ...soTrongVan])].filter((n) => !taiLieu.some((t) => t.so === n));
  const NHOM_NGUON: Record<string, string> = {
    "Phác đồ BYT": "kcb",
    "Bộ Y tế": "kcb",
    MSD: "msd",
    FDA: "fda",
    NICE: "nice",
    WHO: "who",
    CDC: "cdc",
    MedlinePlus: "medlineplus",
    PubMed: "pubmed",
    StatPearls: "statpearls",
    AAFP: "aafp",
  };
  const nhanNgan = (t: TaiLieu) => {
    if (t.nguon === "Phác đồ BYT") return `Bộ Y tế${t.ten.match(/QĐ\s*\d+/)?.[0] ? ` · ${t.ten.match(/QĐ\s*\d+/)![0]}` : ""}`;
    if (t.nguon === "Bộ Y tế") return "Bộ Y tế · kcb.vn";
    if (t.nguon === "FDA") return "DailyMed (FDA)";
    if (t.nguon === "MSD") return "MSD Manual";
    if (t.nguon === "WHO") return /hướng dẫn/.test(t.loai || "") ? `WHO${t.nam ? ` ${t.nam}` : ""}` : "WHO";
    if (t.nguon === "PubMed") return `${/toàn văn PMC/.test(t.loai || "") ? "PMC" : "PubMed"}${t.nam ? ` · ${t.nam}` : ""}`;
    if (t.nguon === "AAFP") return `AAFP${t.nam ? ` · ${t.nam}` : ""}`;
    return t.nguon;
  };
  const sources = taiLieu.map((t) => ({
    nhan: nhanNgan(t),
    nhom: NHOM_NGUON[t.nguon] || "",
    so: t.so,
    name: `${t.ten}${t.nam ? ` (${t.nam})` : ""}`,
    domain: `${TEN_NGUON[t.nguon] || t.nguon}${t.loai ? ` · ${t.loai}` : ""}`,
    url: t.url,
    cited: soTrich.has(t.so),
  }));
  const hoiBoYTe = /bộ y tế|phác đồ|việt nam|byt/i.test(cauHoi);
  const cu = phacDo.filter((t) => t.nam && Number(t.nam) < 2018).map((t) => t.nam);
  const canhBao = [
    soTrich.size === 0 ? "Câu trả lời không trích tài liệu nào — kiểm lại trước khi dùng." : "",
    soLa.length ? `Câu trả lời trích số không có trong danh sách: ${soLa.join(", ")}.` : "",
    hoiBoYTe && !kcb.length && !phacDo.length ? "Không tìm thấy phác đồ Bộ Y tế cho câu hỏi này (thư viện tại máy và kcb.vn)." : "",
    cu.length ? `Phác đồ Bộ Y tế tìm được ban hành năm ${[...new Set(cu)].join(", ")} — có thể đã có bản mới hơn.` : "",
    hoiBoYTe && kcb.length && !phacDo.length
      ? "Nguồn Bộ Y tế tìm được chỉ là trang quyết định, công văn hoặc tin chuyên môn — thư viện tại máy chưa có toàn văn phác đồ này. Mở văn bản gốc để đối chiếu."
      : "",
    loiTim.length ? `Một nguồn tìm bị lỗi: ${loiTim.join("; ")}.` : "",
  ]
    .filter(Boolean)
    .join(" ");
  const muc = daTra.map((d) => `- ${d.nguon}: ${d.so ? `${d.so} tài liệu` : "không tìm thấy"}${d.ghiChu ? ` (${d.ghiChu})` : ""}`);
  traLoiMH +=
    `\n\n**Nguồn đã tra:**\n${muc.join("\n")}` +
    `\n\n> Chỉ để tham khảo — không phải khẳng định, chẩn đoán hay chỉ định điều trị. ` +
    `Bác sĩ đối chiếu văn bản gốc và tự quyết định.`;
  return {
    answer: traLoiMH,
    sources,
    searched: daTra,
    cauTruc,
    removedSources: boLacDe,
    warning: canhBao || null,
    model: b2.model,
    seconds: b2.seconds,
    usage: { prompt_tokens: b2.usage?.prompt_tokens || 0, completion_tokens: b2.usage?.completion_tokens || 0 },
  };
}
