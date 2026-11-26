// Link co dinh cua MediTrace tren Cloudflare Workers (thay Vercel tu 26/11/2026).
//
// May chu that chay tren HoaiDuc (cong 3100) va ra ngoai qua duong ham tam
// `*.trycloudflare.com`, dia chi DOI moi lan HoaiDuc khoi dong lai. Worker nay giu mot
// dia chi co dinh va chuyen tiep moi yeu cau toi duong ham hien tai, doc tu KV
// (`CAU_HINH`, khoa `dich`). Doi duong ham thi chi ghi lai khoa do:
//
//   npx wrangler kv key put --binding CAU_HINH dich https://<moi>.trycloudflare.com --remote
//
// Khong luu, khong doc noi dung yeu cau/phan hoi — chi chuyen tiep.

const KHONG_CHUYEN = ["host", "cf-connecting-ip", "cf-ipcountry", "cf-ray", "cf-visitor", "x-forwarded-proto", "x-real-ip"];

const DUONG_CAP_NHAT = "/__meditrace/cap-nhat-dich";
const MAU_DICH = /^https:\/\/[a-z0-9-]+\.trycloudflare\.com$/;

function bangNhau(a, b) {
  // so sanh thoi gian khong doi de khong lo do dai/tien to mat ma
  if (typeof a !== "string" || typeof b !== "string" || a.length !== b.length) return false;
  let d = 0;
  for (let i = 0; i < a.length; i++) d |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return d === 0;
}

// HoaiDuc goi duong nay khi duong ham doi link (xem cap-nhat-kv.ps1). Chi nhan link
// *.trycloudflare.com va chi khi kem dung mat ma chung (secret KHOA_CAP_NHAT cua Worker).
async function capNhatDich(req, env) {
  if (req.method !== "POST" || !env.KHOA_CAP_NHAT) return new Response("not found", { status: 404 });
  if (!bangNhau(req.headers.get("x-meditrace-khoa") || "", env.KHOA_CAP_NHAT)) {
    return new Response("forbidden", { status: 403 });
  }
  const dich = (await req.text()).trim();
  if (!MAU_DICH.test(dich)) return new Response("link khong hop le", { status: 400 });
  await env.CAU_HINH.put("dich", dich);
  return new Response("ok", { status: 200 });
}

export default {
  async fetch(req, env) {
    if (new URL(req.url).pathname === DUONG_CAP_NHAT) return capNhatDich(req, env);
    const dich = (await env.CAU_HINH.get("dich")) || "";
    if (!MAU_DICH.test(dich)) {
      return new Response("MediTrace đang bảo trì, vui lòng thử lại sau ít phút.", {
        status: 503,
        headers: { "content-type": "text/plain; charset=utf-8", "retry-after": "60" },
      });
    }
    const vao = new URL(req.url);
    const ra = new URL(vao.pathname + vao.search, dich);
    const h = new Headers(req.headers);
    for (const k of KHONG_CHUYEN) h.delete(k);
    h.set("x-forwarded-host", vao.host);

    let tl;
    try {
      tl = await fetch(ra, {
        method: req.method,
        headers: h,
        body: req.method === "GET" || req.method === "HEAD" ? undefined : req.body,
        redirect: "manual",
      });
    } catch {
      return new Response("Không kết nối được máy chủ MediTrace.", {
        status: 502,
        headers: { "content-type": "text/plain; charset=utf-8" },
      });
    }
    // Chuyen huong tuyet doi ve duong ham -> doi ve dia chi co dinh
    const vi_tri = tl.headers.get("location");
    if (vi_tri && vi_tri.startsWith(dich)) {
      const h2 = new Headers(tl.headers);
      h2.set("location", vao.origin + vi_tri.slice(dich.length));
      return new Response(tl.body, { status: tl.status, statusText: tl.statusText, headers: h2 });
    }
    return tl;
  },
};
