# Bộ che định danh trên PhoNER_COVID19 (mốc 0 và sau khi vá)

Ngày đo: 28/11/2026. Số liệu đầy đủ: `docs/ket-qua/an-danh-phoner.json`.

Hai bộ che:
- **TypeScript** `anDanhChoNgoai` (`web/may-chu/an-danh-ngoai.ts`): chặn trước khi gửi ra mô hình ngoài của bên thứ ba.
- **Python** `ClinicalDeidentifier` (`src/he_thong/khu_dinh_danh.py`): chặn trước khi gửi ra máy xa (`src/he_thong/dich_vu_http.py`).

Lệnh đo (cùng định nghĩa):

```
cd web; npx tsx may-chu/do-an-danh-phoner.ts --tap dev|test
python -m tools.do_an_danh_phoner --tap dev|test
```

- **Bảo vệ**: một nhãn vàng NAME hoặc PATIENT_ID được tính là bảo vệ khi chuỗi của nó không còn trong văn bản đã che (so khớp có ranh giới, để token `[PII_1]` không bị tính là lộ nhãn "1"), hoặc khi cả câu bị từ chối gửi (TS: `ok === false`; Python: `kiem_tra_con_sot` khác rỗng).
- **Che nhầm**: một trong 300 câu hỏi đầu của `ViMedAQA/test_sample_500.json` bị đổi sau khi che, hoặc bị từ chối.
- **Ngưỡng** (đặt trên tập dev): bảo vệ ≥ 0,95 và che nhầm ≤ 0,05.

## Kết quả

| Bộ che | Tập | Bảo vệ NAME+PATIENT_ID, mốc 0 | Bảo vệ, sau khi vá | Câu từ chối, mốc 0 → sau khi vá | Che nhầm ViMedAQA, mốc 0 → sau khi vá |
|---|---|---|---|---|---|
| TypeScript | dev (2.000 câu) | 107/1.464 (7,3%) | **1.427/1.464 (97,5%)** | 0 → 0 | 4/300 (1,3%) → 4/300 (1,3%) |
| TypeScript | test (3.000 câu) | 174/2.323 (7,5%) | **2.183/2.323 (94,0%)** | 0 → 0 | 4/300 (1,3%) → 4/300 (1,3%) |
| Python | dev (2.000 câu) | 22/1.464 (1,5%) | **1.425/1.464 (97,3%)** | 0 → 2 | 1/300 (0,3%) → 2/300 (0,7%) |
| Python | test (3.000 câu) | 19/2.323 (0,8%) | **2.178/2.323 (93,8%)** | 0 → 2 | 1/300 (0,3%) → 2/300 (0,7%) |

Tách theo nhãn trên test sau khi vá: PATIENT_ID 1.888/2.005 (94,2%) ở cả hai bộ; NAME 295/318 (TS) và 290/318 (Python).

**Đánh giá ngưỡng.** Trên dev, cả hai bộ che đạt cả hai ngưỡng. Trên test, che nhầm vẫn đạt, nhưng bảo vệ **không đạt** 0,95: TS được 0,940, Python được 0,938. Luật được vá theo các dạng gặp trong dev, nên trên test rơi khoảng 3,5 điểm. Chúng tôi không xem các ca lọt của test và không vá thêm, vì làm vậy sẽ cần đo test lần thứ ba. Trên dev, phần lọt còn lại chủ yếu là tên một tiếng đứng trơ, không có xưng hô ("Nhung", "Oanh", "Kim"), và vài nhãn vàng thực ra là tuổi, ngày hay chữ "19" trong "COVID-19".

PhoNER là văn bản tin tức về COVID-19, không phải hội thoại khám; ngưỡng đặt trên tập dev, số test đo đúng hai lần (trước và sau).

## Vá thêm sau rà soát độc lập (28/11, sau lần đo test thứ hai)

Rà soát độc lập chỉ ra các ca che nhầm/bỏ sót: "sốt từ thứ 2", "là thứ 3", "viêm gan B.", "nhóm máu A.", "Vitamin B.", "Lý Do Khám", "Thái Lan" bị che nhầm; Python bỏ sót họ tên viết thường ("nguyễn văn an"). Đã vá cả hai bộ che và thêm 8 ca vào bộ ca dùng chung.

**Không đo lại tập test** (đã đo đủ hai lần). Đo lại tập dev: bảo vệ TS 1.427/1.464 (97,5%), Python 1.425/1.464 (97,3%) — không đổi; che nhầm ViMedAQA TS 1,3%, Python 1,3% (Python tăng từ 0,7% do thêm luật tên viết thường, bằng mức của TS).

## Đã vá gì

Thêm hai luật cùng tên vào cả hai bộ che:
- **`MA_CA_BENH`**: "bệnh nhân 416", "BN416", "bệnh nhân số 91", "ca bệnh 950", và danh sách "bệnh nhân 861, 862 và 863". Chỉ che phần số. Bỏ qua khi số đi kèm đơn vị ("bệnh nhân 3 ngày", "BN 2 lần", "bệnh nhân 65 tuổi"). "thứ N" chỉ được tính sau "bệnh nhân", "ca" hoặc "COVID-19", để "thứ 2" chỉ ngày trong tuần không bị che.
- **`TEN_VIET_TAT`**: "bà H.T.P", "ông N.V.A", "anh Q.", "bệnh nhân G", chữ tắt đứng riêng như "T.V.D.", và "T." ở giữa câu. Không che tên thuốc như "Alsiful S.R" hay "A.T Desloratadin".

Riêng bộ Python còn thêm ba luật mà bộ TS đã có: xưng hô + tên viết hoa ("Bà Hoa"), họ + tên viết hoa ("Nguyễn Hồng Nhung"), và mã hồ sơ có từ báo trước ("Mã bệnh nhân 20261125"). `kiem_tra_con_sot` nay báo cả `MA_CA_BENH` và `TEN_VIET_TAT` nếu còn sót.

Bộ ca dùng chung: `tests/fixtures/ro_ri_dinh_danh.json` (37 ca), có test ở `tests/test_ro_ri_dinh_danh_chung.py` và `web/may-chu/an-danh-chung.test.ts`.

## Đối chiếu với số cũ 10/847 (1,2%)

`docs/ket-qua/da-nguon-doc-lap.json` ghi bộ Python che được 10/847 nhãn NAME+PATIENT_ID (1,2%). Số mốc 0 ở đây là 19/2.323 (0,8%). Hai cách đo khác nhau ở bốn điểm:
1. Bản cũ chỉ lấy 1.000 câu đầu của test; bản này lấy cả 3.000 câu.
2. Bản cũ khớp chuỗi con không có ranh giới; bản này khớp có ranh giới.
3. Bản cũ không tính câu bị từ chối gửi là được bảo vệ; bản này có tính.
4. Bản cũ chỉ đo bộ Python; bản này đo cả hai bộ che.

Cả hai cách đo đều cho thấy trước khi vá, bộ Python gần như không che được mã ca bệnh và tên viết tắt.
