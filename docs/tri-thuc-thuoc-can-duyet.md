# Tri thức thuốc chờ duyệt (sinh 25/11/2026 từ `data/tri_thuc_thuoc.json`)

Tổng 158 hoạt chất, **tất cả `da_duyet = false`**. Không mục nào được tự đặt `true`: người có chuyên môn
dược/y tra lại tài liệu gốc (Dược thư Quốc gia Việt Nam, số trang), sửa số nếu cần, ghi nguồn cụ thể vào `nguon`,
rồi mới đổi `da_duyet`. Cho tới lúc đó mọi cảnh báo dựa trên các số này chỉ ở mức **cần xem**, không chặn.

Mọi số dưới đây **chép từ mã cũ**, không phải từ sách: các bảng cũ ghi “Dược thư 2022” nhưng không có số trang.

## 1. Cần tra trước — có ghi chú nghi sai hoặc hai bảng trái nhau (6)

- **clopidogrel**: Bảng cũ ghi 300 mg/ngày là liều TỐI ĐA; 300 mg là liều nạp, liều duy trì 75 mg/ngày. Cần tra.
- **co-amoxiclav**: Liều 3000 mg/ngày trong bảng cũ không rõ tính theo amoxicillin hay cả hai thành phần.
- **digoxin**: 0,25 mg/ngày là liều duy trì thường dùng, không phải trần tuyệt đối. Cần tra.
- **omeprazole**: Hai bảng cũ trái nhau: 40 mg/ngày (duoc_ly_lam_sang, guardrails) và 80 mg/ngày (aho_corasick). Đã lấy 40 (thận trọng hơn). Liều điều trị Zollinger-Ellison có thể cao hơn nhiều. liều tối đa người lớn: 80.0 (bảng aho_corasick) vs 40.0 (src/duoc_ly_lam_sang.py LIEU_TOI_DA_NGAY và src/guardrails.py LIEU_TRAN (không ghi nguồn))
- **theophylline**: Bảng cũ ghi aminophylline là biệt dược của theophylline — đã tách thành hoạt chất riêng.
- **warfarin**: Bảng cũ ghi 10 mg/ngày là liều tối đa; warfarin chỉnh theo INR, không có trần cố định. Bảng cũ còn ghi sintrom là biệt dược của warfarin — sai (sintrom là acenocoumarol), đã tách.
- **sintrom**: bảng cũ (`aho_corasick_duoc_thu.py`) xếp là biệt dược của warfarin. Sintrom là **acenocoumarol** — đã tách thành hoạt chất riêng, giữ cờ khoảng điều trị hẹp.
- **aminophylline**: bảng cũ xếp là biệt dược của theophylline; đã tách thành hoạt chất riêng.

## 2. Có ngưỡng liều (38) — ưu tiên duyệt

| Hoạt chất | Biệt dược | Người lớn | Trẻ em | NTI | Chép từ |
|---|---|---|---|---|---|
| allopurinol | zyloric, milurit | 800 mg/ngày |  |  | src/aho_corasick_duoc_thu.py (bảng ghi “Dược thư Quốc gia Việt Nam 2022”, không ghi số trang); src/duoc_ly_lam_sang.py LIEU_TOI_DA_NGAY và src/guardrails.py LIEU_TRAN (không ghi nguồn). |
| amiodarone | cordarone | 800 mg/ngày |  | có | src/aho_corasick_duoc_thu.py (bảng ghi “Dược thư Quốc gia Việt Nam 2022”, không ghi số trang); src/cong_rui_ro.py THUOC_KHOANG_DIEU_TRI_HEP (không ghi nguồn). |
| amlodipin | amlor, norvasc | 10 mg/ngày |  |  | src/aho_corasick_duoc_thu.py (bảng ghi “Dược thư Quốc gia Việt Nam 2022”, không ghi số trang); src/duoc_ly_lam_sang.py LIEU_TOI_DA_NGAY và src/guardrails.py LIEU_TRAN (không ghi nguồn). |
| amoxicillin |  |  | 45.0 mg/kg/lần; 90.0 mg/kg/ngày |  | src/kiem_duyet_bhyt_va_bo_sot.py LIEU_TRAN_NHI_KHOA_MG_KG_NGAY (không ghi nguồn). |
| aspirin |  | 3000 mg/ngày |  |  | src/duoc_ly_lam_sang.py LIEU_TOI_DA_NGAY và src/guardrails.py LIEU_TRAN (không ghi nguồn). |
| atorvastatin | lipitor, atorvastad | 80 mg/ngày |  |  | src/aho_corasick_duoc_thu.py (bảng ghi “Dược thư Quốc gia Việt Nam 2022”, không ghi số trang); src/duoc_ly_lam_sang.py LIEU_TOI_DA_NGAY và src/guardrails.py LIEU_TRAN (không ghi nguồn). |
| azathioprine | imuran | 200 mg/ngày |  |  | src/aho_corasick_duoc_thu.py (bảng ghi “Dược thư Quốc gia Việt Nam 2022”, không ghi số trang). |
| azithromycin |  |  | 10.0 mg/kg/lần; 10.0 mg/kg/ngày |  | src/kiem_duyet_bhyt_va_bo_sot.py LIEU_TRAN_NHI_KHOA_MG_KG_NGAY (không ghi nguồn). |
| carbamazepine | tegretol, carbatrol | 1600 mg/ngày |  | có | src/aho_corasick_duoc_thu.py (bảng ghi “Dược thư Quốc gia Việt Nam 2022”, không ghi số trang); src/cong_rui_ro.py THUOC_KHOANG_DIEU_TRI_HEP (không ghi nguồn). |
| cefixim |  |  | 8.0 mg/kg/lần; 8.0 mg/kg/ngày |  | src/kiem_duyet_bhyt_va_bo_sot.py LIEU_TRAN_NHI_KHOA_MG_KG_NGAY (không ghi nguồn). |
| ciprofloxacin | ciprobay, citeran, cipro | 1500 mg/ngày |  |  | src/aho_corasick_duoc_thu.py (bảng ghi “Dược thư Quốc gia Việt Nam 2022”, không ghi số trang). |
| clopidogrel | plavix, clopistad, agrelan | 300 mg/ngày |  |  | src/aho_corasick_duoc_thu.py (bảng ghi “Dược thư Quốc gia Việt Nam 2022”, không ghi số trang). |
| co-amoxiclav | augmentin, klamentin, amoxicillin-clavulanate, amoxicillin-acid clavulanic | 3000 mg/ngày | 45.0 mg/kg/lần; 90.0 mg/kg/ngày |  | src/aho_corasick_duoc_thu.py (bảng ghi “Dược thư Quốc gia Việt Nam 2022”, không ghi số trang); src/kiem_duyet_bhyt_va_bo_sot.py LIEU_TRAN_NHI_KHOA_MG_KG_NGAY (không ghi nguồn). |
| co-trimoxazole | bactrim, biseptol, sulfamethoxazole-trimethoprim | 1920 mg/ngày |  |  | src/aho_corasick_duoc_thu.py (bảng ghi “Dược thư Quốc gia Việt Nam 2022”, không ghi số trang). |
| colchicine | colcrys | 3 mg/ngày |  |  | src/aho_corasick_duoc_thu.py (bảng ghi “Dược thư Quốc gia Việt Nam 2022”, không ghi số trang); src/duoc_ly_lam_sang.py LIEU_TOI_DA_NGAY và src/guardrails.py LIEU_TRAN (không ghi nguồn). |
| digoxin | lanoxin | 0.25 mg/ngày |  | có | src/aho_corasick_duoc_thu.py (bảng ghi “Dược thư Quốc gia Việt Nam 2022”, không ghi số trang); src/duoc_ly_lam_sang.py LIEU_TOI_DA_NGAY và src/guardrails.py LIEU_TRAN (không ghi nguồn); src/cong_rui_ro.py THUOC_KHOANG_DIEU_TRI_HEP (không ghi nguồn). |
| doxycycline | vibramycin | 200 mg/ngày |  |  | src/aho_corasick_duoc_thu.py (bảng ghi “Dược thư Quốc gia Việt Nam 2022”, không ghi số trang). |
| enalapril | renitec, ednyt, vasotec | 40 mg/ngày |  |  | src/aho_corasick_duoc_thu.py (bảng ghi “Dược thư Quốc gia Việt Nam 2022”, không ghi số trang). |
| ethambutol | myambutol, emb | 1600 mg/ngày |  |  | src/aho_corasick_duoc_thu.py (bảng ghi “Dược thư Quốc gia Việt Nam 2022”, không ghi số trang). |
| ibuprofen | advil, brufen, alaxan, motrin | 2400 mg/ngày | 10.0 mg/kg/lần; 40.0 mg/kg/ngày |  | src/aho_corasick_duoc_thu.py (bảng ghi “Dược thư Quốc gia Việt Nam 2022”, không ghi số trang); src/duoc_ly_lam_sang.py LIEU_TOI_DA_NGAY và src/guardrails.py LIEU_TRAN (không ghi nguồn); src/kiem_duyet_bhyt_va_bo_sot.py LIEU_TRAN_NHI_KHOA_MG_KG_NGAY (không ghi nguồn). |
| isoniazid | inh, rimifon | 300 mg/ngày |  |  | src/aho_corasick_duoc_thu.py (bảng ghi “Dược thư Quốc gia Việt Nam 2022”, không ghi số trang). |
| losartan | cozaar, losartan-kali | 100 mg/ngày |  |  | src/aho_corasick_duoc_thu.py (bảng ghi “Dược thư Quốc gia Việt Nam 2022”, không ghi số trang); src/duoc_ly_lam_sang.py LIEU_TOI_DA_NGAY và src/guardrails.py LIEU_TRAN (không ghi nguồn). |
| mesalazine | pentasa, asacol, salofalk | 4000 mg/ngày |  |  | src/aho_corasick_duoc_thu.py (bảng ghi “Dược thư Quốc gia Việt Nam 2022”, không ghi số trang). |
| metformin | glucophage, panfor, diaformin | 2550 mg/ngày |  |  | src/aho_corasick_duoc_thu.py (bảng ghi “Dược thư Quốc gia Việt Nam 2022”, không ghi số trang); src/duoc_ly_lam_sang.py LIEU_TOI_DA_NGAY và src/guardrails.py LIEU_TRAN (không ghi nguồn). |
| methotrexate | trexall | 25 mg/ngày |  | có | src/aho_corasick_duoc_thu.py (bảng ghi “Dược thư Quốc gia Việt Nam 2022”, không ghi số trang); src/cong_rui_ro.py THUOC_KHOANG_DIEU_TRI_HEP (không ghi nguồn). |
| methyldopa | aldomet, dopagyte | 2000 mg/ngày |  |  | src/aho_corasick_duoc_thu.py (bảng ghi “Dược thư Quốc gia Việt Nam 2022”, không ghi số trang); src/duoc_ly_lam_sang.py LIEU_TOI_DA_NGAY và src/guardrails.py LIEU_TRAN (không ghi nguồn). |
| omeprazole | losec, omepral, lomac | 40 mg/ngày |  |  | src/aho_corasick_duoc_thu.py (bảng ghi “Dược thư Quốc gia Việt Nam 2022”, không ghi số trang); src/duoc_ly_lam_sang.py LIEU_TOI_DA_NGAY và src/guardrails.py LIEU_TRAN (không ghi nguồn). |
| paracetamol | panadol, efferalgan, hapacol, tylenol, paracold | 4000 mg/ngày | 15.0 mg/kg/lần; 60.0 mg/kg/ngày |  | src/aho_corasick_duoc_thu.py (bảng ghi “Dược thư Quốc gia Việt Nam 2022”, không ghi số trang); src/duoc_ly_lam_sang.py LIEU_TOI_DA_NGAY và src/guardrails.py LIEU_TRAN (không ghi nguồn); src/kiem_duyet_bhyt_va_bo_sot.py LIEU_TRAN_NHI_KHOA_MG_KG_NGAY (không ghi nguồn). |
| phenytoin | dilantin, epanutin | 500 mg/ngày |  | có | src/aho_corasick_duoc_thu.py (bảng ghi “Dược thư Quốc gia Việt Nam 2022”, không ghi số trang); src/cong_rui_ro.py THUOC_KHOANG_DIEU_TRI_HEP (không ghi nguồn). |
| prednisolon |  |  | 2.0 mg/kg/lần; 2.0 mg/kg/ngày |  | src/kiem_duyet_bhyt_va_bo_sot.py LIEU_TRAN_NHI_KHOA_MG_KG_NGAY (không ghi nguồn). |
| pyrazinamide | pza | 2000 mg/ngày |  |  | src/aho_corasick_duoc_thu.py (bảng ghi “Dược thư Quốc gia Việt Nam 2022”, không ghi số trang). |
| pyridostigmine | mestinon | 720 mg/ngày |  |  | src/aho_corasick_duoc_thu.py (bảng ghi “Dược thư Quốc gia Việt Nam 2022”, không ghi số trang). |
| rifampicin | rifadin, rimactan | 600 mg/ngày |  |  | src/aho_corasick_duoc_thu.py (bảng ghi “Dược thư Quốc gia Việt Nam 2022”, không ghi số trang). |
| salbutamol | ventolin | 16 mg/ngày |  |  | src/duoc_ly_lam_sang.py LIEU_TOI_DA_NGAY và src/guardrails.py LIEU_TRAN (không ghi nguồn). |
| spironolactone | aldactone, verospiron | 100 mg/ngày |  |  | src/aho_corasick_duoc_thu.py (bảng ghi “Dược thư Quốc gia Việt Nam 2022”, không ghi số trang). |
| theophylline | theostat | 900 mg/ngày |  | có | src/aho_corasick_duoc_thu.py (bảng ghi “Dược thư Quốc gia Việt Nam 2022”, không ghi số trang); src/duoc_ly_lam_sang.py LIEU_TOI_DA_NGAY và src/guardrails.py LIEU_TRAN (không ghi nguồn); src/cong_rui_ro.py THUOC_KHOANG_DIEU_TRI_HEP (không ghi nguồn). |
| valproat | depakine, valproic acid, natri valproat | 2500 mg/ngày |  | có | src/aho_corasick_duoc_thu.py (bảng ghi “Dược thư Quốc gia Việt Nam 2022”, không ghi số trang); src/cong_rui_ro.py THUOC_KHOANG_DIEU_TRI_HEP (không ghi nguồn). |
| warfarin | coumadin, marevan | 10 mg/ngày |  | có | src/aho_corasick_duoc_thu.py (bảng ghi “Dược thư Quốc gia Việt Nam 2022”, không ghi số trang); src/cong_rui_ro.py THUOC_KHOANG_DIEU_TRI_HEP (không ghi nguồn). |

## 3. Chỉ có tên, không có ngưỡng (120)

Dùng để nhận ra thuốc trong hội thoại (bỏ sót, sai thuốc). Duyệt nhẹ: tên đúng là thuốc, đúng hoạt chất, cờ NTI đúng.

acenocoumarol (NTI), acyclovir, adalimumab, albendazole, alprazolam, alteplase, aminophylline (NTI), ampicillin, apixaban, aripiprazole, baclofen, benzylpenicillin, betamethasone, bisoprolol, bleomycin, caplacizumab, captopril, cefadroxil, cefazolin, cefdinir, cefepime, cefotaxime, ceftazidime, ceftriaxone, cefuroxime, celecoxib, cephalexin, cilostazol, clarithromycin, clindamycin, clonazepam, clotrimazole, cloxacillin, cyclosporine (NTI), danazol, dapagliflozin, dapsone, denosumab, dexamethasone, diazepam, diclofenac, dornase, dupilumab, enoxaparin (NTI), eperisone, erythromycin, esomeprazol, etoricoxib, fidaxomicin, fluconazole, fludrocortisone, fluticasone, fosfomycin, furosemide, ganciclovir, gentamicin (NTI), heparin (NTI), hydrocortisone, imatinib, infliximab, insulin (NTI), itraconazole, ixekizumab, ketoconazole, ketoprofen, lanadelumab, levofloxacin, lithium (NTI), lorazepam, mepolizumab, methylprednisolone, metoprolol, metronidazole, miconazole, midazolam, minocycline, mometasone, montelukast, moxifloxacin, nadolol, natalizumab, natamycin, nicardipine, nifedipine, nystatin, ocrelizumab, ofloxacin, omalizumab, ondansetron, oxacillin, paromomycin, penicillin, piperacillin, prednisone, propranolol, prostacyclin, rabeprazole, ranibizumab, rituximab, rivaroxaban, rosuvastatin, secukinumab, somatostatin, spiramycin, sumatriptan, tacrolimus (NTI), tetracyclin, thiabendazole, timolol, tinidazole, tobramycin, tocilizumab, tolperisone, triamcinolone, triclabendazole, valacyclovir, valganciclovir, valsartan, vancomycin (NTI), voriconazole
