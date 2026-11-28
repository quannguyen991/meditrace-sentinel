# Truy nguồn commit theo công cụ AI

Commit `chua_xac_dinh` là commit không ghi công cụ; không đoán. Tác giả xác nhận dần vào `docs/minh-bach/truy-nguon-ghi-de.json`.

Sinh bằng `python -m tools.truy_nguon_commit`. Thứ tự xác định công cụ: tệp ghi đè → trailer `Cong-cu-AI:` → dòng `Co-Authored-By: Claude` → `chua_xac_dinh`.

## Đếm theo công cụ

| Công cụ | Số commit |
|---|---|
| claude_code | 47 |
| chua_xac_dinh | 34 |
| **Tổng** | **81** |

## Từng commit

| Ngày | Commit | Tóm tắt | Công cụ | Số tệp | Chạm test |
|---|---|---|---|---|---|
| 2026-11-28 | `f406b81` | docs: implementation plan for BTC brief 1 (health data protection, AI transparency), 10 tasks for 6-hour hackathon | claude_code | 1 | không |
| 2026-11-28 | `bfdb58b` | docs: plan for BTC improvement brief 1 (health data), 6-hour hackathon schedule, drop clinical-team claim | claude_code | 8 | không |
| 2026-11-28 | `13cd479` | docs: cap nhat Q&A Ban Giam khao ro cau truc du an va so lieu da kiem chung | chua_xac_dinh | 3 | không |
| 2026-11-27 | `0d94d03` | docs: sync all handbooks/reports to 6-package layout + 2fc4eba & fix HTTP error socket reset | chua_xac_dinh | 11 | không |
| 2026-11-27 | `586945d` | docs: sync project explanation files with verified v2.6/Policy D metrics & 6-package structure | chua_xac_dinh | 2 | không |
| 2026-11-27 | `2fc4eba` | fix: stop eyelid mi -> may, non-dose numbers triggering DOSE_MISMATCH, flag dev-set 11.8% | claude_code | 6 | có |
| 2026-11-27 | `8120ce4` | fix: harden dialect clinical guards, fix 158-drug loader, tighten Policy D & honest benchmarks | chua_xac_dinh | 13 | có |
| 2026-11-27 | `bffaa3c` | feat: expand 3-region dialects, G2P drugs, 5-dataset benchmark & Policy D safety | chua_xac_dinh | 20 | có |
| 2026-11-27 | `1878711` | refactor: organize src into 6 domain packages with BAN_DO_MA_NGUON (1965 pytest + 96 web tests pass) | chua_xac_dinh | 481 | có |
| 2026-11-27 | `680688c` | docs: embed 6 architecture/flow/UI diagrams and M1-M4/A1-A3 source map into handbook | chua_xac_dinh | 2 | không |
| 2026-11-27 | `580c84b` | feat: drop Policy D dangerous leakage to 24.1% and add step-by-step error propagation audit | chua_xac_dinh | 6 | không |
| 2026-11-27 | `d52a182` | fix: A1-A3 core accuracy - drop dangerous leakage 42.9% to 31.8% and 0% train/dev verbatim overlap | chua_xac_dinh | 6 | có |
| 2026-11-26 | `7b3a635` | docs(readme): nhat ky nang cap 15-26/11/2026 (du lieu v2, v3, 8 tinh nang, lop canh bao, DPO, ra soat, Boost/M1-M4, giao dien, trien khai) | claude_code | 1 | không |
| 2026-11-26 | `4b9ed2f` | docs: README cap nhat 26/11 (ngan duyet, Nghe lai theo menh de, menu Cong cu, so phep thu moi, cap nhat duong ham tu dong) + bao cao cai tien BGK (PDF/HTML) | claude_code | 2 | không |
| 2026-11-26 | `39142ee` | feat(web): nut Nghe tren tung luot thoai cho ca chi co chu (doc to bang giong tieng Viet cua may, toc do 1.3) | claude_code | 1 | không |
| 2026-11-26 | `dc8326f` | fix(web): gon thanh nut (bo In PDF trung, nhan tab trung, nut lam moi, chon loa; In/Luu PDF vao menu Sao chep; tro ly canh gioi thu gon san); nut Nghe lai tren tung menh de; ca tai tep am thanh cung nghe lai duoc | claude_code | 6 | không |
| 2026-11-26 | `10b6205` | fix(web): bam vao mot dong trong ban nhap thi mo lai ngan duyet ben canh (dong san khi mo ca); nut xanh van sang man hinh duyet chinh | claude_code | 1 | không |
| 2026-11-26 | `d9b5f49` | fix(web): nut 'Them vao ban nhap' cho muc bo sot Tang 4.5 o man hinh Duyet tung menh de (thay ngan duyet nho da bo) | claude_code | 2 | không |
| 2026-11-26 | `79a5be0` | fix(web): gop 8 nut cong cu vao menu Cong cu; index.html khong cache va tu tai lai khi tep build cu khong con | claude_code | 3 | không |
| 2026-11-26 | `c391b61` | fix(web): thanh nut ban nhap xuong dong khi hep thay vi bi cat duoi khung phai | claude_code | 1 | không |
| 2026-11-26 | `e66edb3` | fix(web): bo ngan duyet nho - bam Duyet hoac bam vao menh de la chuyen thang sang man hinh Duyet tung menh de | claude_code | 1 | không |
| 2026-11-26 | `ac254bb` | fix(web): giao dien gon cho bac si - mo ca thi thu gon danh sach va khung tra cuu, bo nut doc chinh ta da tat, an dong ho khi chua ghi am, chi gach chan menh de can xem | claude_code | 3 | không |
| 2026-11-26 | `319fc02` | fix(web): gon trang dang nhap - bo khung tieng Anh, bot chu | claude_code | 1 | không |
| 2026-11-26 | `1b72691` | feat: MediTrace Sentinel M1-M4 breakthrough clinical safety, BHYT XML1-5 audit, QR portal and LIS HL7 integration | chua_xac_dinh | 43 | có |
| 2026-11-26 | `3d8a91b` | docs: ket qua DPO tren cap loi kho (v3 vs v3+DPO, 140 cap) | claude_code | 2 | không |
| 2026-11-26 | `c21dac1` | feat(boost): trien khai tron bo 12 tinh nang MediTrace Boost chong burnout bac si (Python + BFF + React) | chua_xac_dinh | 41 | có |
| 2026-11-26 | `58a659f` | feat(trien-khai): Worker nhan link duong ham moi qua duong rieng co mat ma chung (secret KHOA_CAP_NHAT); HoaiDuc tu gui khi link doi - khong can khoa API Cloudflare | claude_code | 2 | không |
| 2026-11-26 | `bd30695` | feat(train): --chi-cap-co-ref de train DPO rut gon tren cap da tinh ref; script canh duong ham ghi link vao KV Cloudflare | claude_code | 2 | không |
| 2026-11-26 | `fe6bdc6` | chore(trien-khai): chuyen ban chay thu tu Vercel sang Cloudflare Worker (meditrace-sentinel.meditrace.workers.dev), bo vercel.json | claude_code | 8 | không |
| 2026-11-26 | `2286ee0` | docs(readme): sua loi an toan sau ra soat 26/11, bien moi truong bat buoc, so phep thu 1900/76; so do lop canh bao khong doi | claude_code | 1 | không |
| 2026-11-26 | `5030475` | Merge branch 'worktree-agent-a5d515703487a42ec' | chua_xac_dinh | 0 | không |
| 2026-11-26 | `2db18a8` | Merge branch 'worktree-agent-a16f490e216f542d7' | chua_xac_dinh | 0 | không |
| 2026-11-26 | `0368872` | fix(may-chu): loi 500 tai khoan khong lo chi tiet; OCR/BHYT chi chay Python tai cho khi dich vu tat (khong khi sai khoa); npm test chay ca kiem thu may-chu; .env.example ghi bien moi | claude_code | 4 | không |
| 2026-11-26 | `f462c16` | fix(may-chu): chuoi WORM dung HMAC co khoa (MEDITRACE_WORM_KEY), neo ky HMAC, mat neo khong tu neo lai, neo cham 1 ban ghi tu lanh | claude_code | 3 | có |
| 2026-11-26 | `4c57e89` | fix(may-chu): moi loi goi mo hinh ngoai qua mot cong: cong tac quan tri, han muc theo nguoi dung, che dinh danh tieng Viet va tu choi neu con sot | claude_code | 7 | có |
| 2026-11-26 | `05e36d2` | feat(train): danh gia DPO ghi do chenh log-prob theo loai va tung cap - v3 da chon dung 280/280 nen ti le dung kich tran | claude_code | 1 | không |
| 2026-11-26 | `770dae2` | fix(fhir,bhyt): di ung "không rõ" thanh AllergyIntolerance unconfirmed thay vi bo; trang thai/nguoi noi la khong ngam dinh con hieu luc/benh nhan | claude_code | 3 | có |
| 2026-11-26 | `7d00a2a` | fix(dich-vu): may xa fail-closed khi khu dinh danh con sot, tinh lai lam_sang_nang_cao tai cho (khong gui thong tin benh nhan), khoa noi bo bat buoc cho moi /api tru suc-khoe (tu sinh tep khi chua dat), hmac.compare_digest, kiem Host, Content-Length chat, user_id chi la khai bao; bo except TypeError, sua fake trong test | claude_code | 5 | có |
| 2026-11-26 | `d95b6e8` | fix(may-chu): gan phien ASR voi nguoi tao, assign-roles/generate-note tu choi sessionId cua nguoi khac; loi viec ban nhap 5xx khong lo chi tiet | claude_code | 3 | có |
| 2026-11-26 | `75f5d53` | fix(may-chu): ky duyet tinh so lieu va bam tu ca da luu (ca phai ton tai, dung chu); luu tabId da bam; dong bo ca khong xoa ngam, co khoa lac quan va gop khi 409 | claude_code | 12 | có |
| 2026-11-26 | `d0d5965` | fix(khu-dinh-danh): che SDT tach nhom/+84/doc tung so va chuoi so 9-15 chu so, ten viet thuong theo tien to, ten rieng + danh xung khi biet ho ten, dung bat ten o tu dau cau, bo ti_le_an_toan_bao_mat gia, them kiem_tra_con_sot | claude_code | 2 | có |
| 2026-11-26 | `e415790` | fix(cong): ep kieu an toan thong tin benh nhan/xet nghiem o bien vao /api/ho-so (chuoi so -> so, rac -> thieu), cong rui ro khong con TypeError; /api/ocr khong mac dinh tuoi 50 | claude_code | 5 | có |
| 2026-11-26 | `b6cefc4` | fix(may-chu): che do dev chi nghe 127.0.0.1, bo allowedHosts=true, chan phuc vu data/ db/ may-chu/ server.* .env* *.db* | claude_code | 4 | có |
| 2026-11-26 | `d1a6cb6` | fix(lieu): quy tac than khai bao CrCl/eGFR (dabigatran, enoxaparin dung CrCl), thieu tuoi khong mac dinh 50, gioi tinh theo tu, doxycycline tach tetracycline, benh gan nen la co khong bia AST/ALT + xu ly phu dinh | claude_code | 4 | có |
| 2026-11-26 | `9550ac4` | fix(may-chu): luon gui khoa noi bo X-MediTrace-Internal-Token, thieu thi dung ro rang; loi 5xx khong lo chi tiet | claude_code | 4 | có |
| 2026-11-26 | `f14a490` | fix(khoa): K6 khop lieu thuoc theo ranh gioi so - bo kiem chuoi con tho (5 mg khop nham 2.5/25 mg, 1 vien khop 11 vien) | claude_code | 2 | có |
| 2026-11-26 | `56384ea` | fix(train): DPO tat dropout khi train, luu bam token trong ref, tu kiem ghep lo dung han neu lech | claude_code | 2 | có |
| 2026-11-26 | `b77af1e` | feat: chot chan ky duyet khi con muc can xac nhan, neo WORM, 3 ca mau da nguoi noi, bao cao cai tien chang 1 (Antigravity) | claude_code | 27 | có |
| 2026-11-26 | `8162873` | perf(train): DPO ghep lo theo nguong do dai tu hoc - tran bo nho thi ha nguong, cap dai hon chay lan luot ngay | claude_code | 2 | có |
| 2026-11-26 | `82e8175` | fix(train): DPO lan truyen nguoc tung chuoi theo he so (mot do thi moi luc) - het tran bo nho o 0,70; do bo sot v3 14,1% vs v1 11,8% | claude_code | 4 | có |
| 2026-11-26 | `dad18a4` | perf(train): DPO chay ban dung + ban sai trong mot lo 2 chuoi; tran bo nho thi quay ve chay lan luot | claude_code | 2 | có |
| 2026-11-26 | `fbf987e` | feat(train): DPO tren cap loi kho tu adapter v3 (ref tinh truoc, NLL ban dung, 1.200 cap chia deu 14 loai) | claude_code | 2 | có |
| 2026-11-26 | `eef14d2` | feat(giao-dien): ErrorBoundary, phat am thanh theo luot, bien dich ghi chu hieu luc, sua App/NoteEditor (Antigravity) | claude_code | 27 | có |
| 2026-11-26 | `d83d225` | feat(may-chu): tach module tra cuu, nap env som, WORM, tai khoan, an danh tro ly (Antigravity) | claude_code | 28 | có |
| 2026-11-26 | `e9a1866` | feat(python): kiem toan tang Python cua Antigravity - khu dinh danh, BHYT, FHIR, can lam sang, trie ASR, suc khoe dich vu | claude_code | 23 | có |
| 2026-11-26 | `7781d94` | chore: go file Word/PDF/Office khoi kho ma, giu ban tren may; bo qua qua .gitignore | claude_code | 46 | không |
| 2026-11-26 | `80624ef` | docs(readme): them lop canh bao, tro ly nhieu tac tu, 8 tinh nang ho tro bac si, ket qua do cay loi va so phep thu moi | claude_code | 1 | không |
| 2026-11-26 | `e2bca62` | docs: sua ty le lot D vong 6 (42,9%) | claude_code | 1 | không |
| 2026-11-26 | `397ddbb` | feat(canh-bao): vong 6 va 4 diem mu loi kho - ben, muc do, qua khu/hien tai, dinh chinh nguoc | claude_code | 8 | có |
| 2026-11-26 | `4b55f71` | chore: them tri thuc thuoc, van tay du lieu, tap dieu chinh cay loi va thi nghiem ASR; bo qua CSDL chay va du lieu ngoai | claude_code | 27 | không |
| 2026-11-25 | `3424284` | feat: hoan thien bo du lieu v2 657 khuon, 8 tinh nang lam sang/BHYT va tai cau truc web/WORM | chua_xac_dinh | 358 | có |
| 2026-10-18 | `8e77a0d` | feat: enhance clinical note print and PDF export with A4 pagination, medical header, and signature block | chua_xac_dinh | 5 | không |
| 2026-10-18 | `f0df56a` | refactor: relocate external model banner from document editor to header, prompt bar, and settings | chua_xac_dinh | 3 | không |
| 2026-10-18 | `e269b1b` | feat(ui): chuyen thang sang man hinh Bang chung hoi thoai tong quat khi bam Duyet tung menh de | chua_xac_dinh | 1 | không |
| 2026-10-18 | `f5d05e2` | fix(ui): luon giu ban dinh dang benh an chuan, tro can cu T1 T2 vao dung cau thoai goc de kiem chung | chua_xac_dinh | 3 | không |
| 2026-10-18 | `68bd30d` | fix(ui): loai bo chu BOI DO CAN BAC SI DUYET thua trong ho so benh an | chua_xac_dinh | 2 | không |
| 2026-10-18 | `ce56dc3` | fix(ui): tinh gon header ho so benh an, bo hop thong tin thua va toi uu dinh dang chu dam | chua_xac_dinh | 3 | không |
| 2026-10-18 | `9ad4b85` | fix(ui): highlight unconfirmed propositions in red, parse markdown bold in notes, and connect dialogue turns with verification lines | chua_xac_dinh | 4 | không |
| 2026-10-18 | `0fab56d` | feat: cap nhat bo 3 ca mau do kho cao chua nhieu bay lam sang cho BGK | chua_xac_dinh | 1 | không |
| 2026-10-18 | `c7e8ef4` | feat: nap 3 ca mau lam sang tieu chuan cho tai khoan BGK va khoi dong dich vu dich_vu 8765 | chua_xac_dinh | 2 | không |
| 2026-10-18 | `9d61385` | fix(deploy): cap nhat duong ham Cloudflare tunnel cho Vercel production | chua_xac_dinh | 1 | không |
| 2026-10-18 | `26b50cb` | docs: chuan hoa ngon ngu ky thuat y te, loai bo an du hoan du va cap nhat 7 flow diagram | chua_xac_dinh | 13 | không |
| 2026-10-18 | `8226a6c` | docs: xuat file Word (.docx) bo so do Flow kien truc va quy trinh lam sang day du hinh anh 4K va bang thuyet minh | chua_xac_dinh | 3 | không |
| 2026-10-17 | `d4c2fc7` | docs: tap ho so 6 bang thuc nghiem khoa hoc va doi chung chi tiet (Word va Markdown) | chua_xac_dinh | 5 | không |
| 2026-10-17 | `35e9355` | docs: ho so minh chung nang cap he thong va nhat ky thuc thi lenh (Word va Markdown) | chua_xac_dinh | 5 | không |
| 2026-10-17 | `73b5a3b` | fix(auth): cho phep origin tu Vercel va Cloudflare tunnel trong middleware bao ve CSRF | chua_xac_dinh | 1 | không |
| 2026-10-17 | `ce886d5` | feat: bo anh 7 master flow diagrams, duong ong 1.330 automated tests, ASR phonetic drug quarantine va ha tang lam sang toan dien | chua_xac_dinh | 101 | có |
| 2026-10-01 | `7acd457` | README tiếng Việt cho ban giám khảo; bản xuất không gồm công cụ chấm mù và tên tệp khoá | chua_xac_dinh | 28 | có |
| 2026-09-30 | `147557a` | Web: home page with sample-case shortcut, live audio bar while recording, working record button, processing-source labels, English guide on sign-in, trimmed template list | chua_xac_dinh | 18 | không |
| 2026-09-27 | `1f099a6` | Web: login screen label; allow a forwarding domain (MEDITRACE_NGUON_DUOC_PHEP) for write requests | chua_xac_dinh | 2 | không |
| 2026-09-27 | `370390d` | MediTrace Sentinel: evidence-traced clinical note drafts from Vietnamese consultations (Python pipeline + web app) | chua_xac_dinh | 320 | có |
