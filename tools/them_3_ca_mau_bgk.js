// -*- coding: utf-8 -*-
/**
 * Thêm 3 ca hội thoại mẫu lâm sàng tiêu chuẩn cao vào tài khoản quannguyen.ulis207@gmail.com (ID: 2)
 * để trình diễn cho Ban Giám Khảo.
 * 
 * 3 Ca bao gồm:
 * 1. Ca 1: Bác Trần Văn An (58 tuổi) — Đau thắt ngực & Dị ứng thuốc Amoxicillin (Khóa K1-K7, Bôi đỏ ASR, Lọc câu người nhà).
 * 2. Ca 2: Chị Lê Thị Mai (34 tuổi) — Viêm phế quản cấp (Xử lý đính chính mốc thời gian FSM, An toàn dạ dày).
 * 3. Ca 3: Bác Hoàng Quốc Dũng (66 tuổi) — Đái tháo đường T2, Rung nhĩ & Suy thận mạn (CDSS Thang điểm CHA2DS2-VASc, Hiệu chỉnh liều Metformin).
 */

const { DatabaseSync } = require("node:sqlite");
const path = require("path");

const dbPath = path.join(__dirname, "..", "web", "data", "meditrace.db");
const db = new DatabaseSync(dbPath);

const UID = 2; // quannguyen.ulis207@gmail.com

// ==============================================================================
// CA 1: Bác Trần Văn An - 58 tuổi
// ==============================================================================
const transcript1 = `Bác sĩ: Chào bác An, mời bác ngồi. Hôm nay bác thấy trong người thế nào mà đi khám?
Bệnh nhân: Dạ chào bác sĩ, độ một tuần nay tôi hay thấy nặng ngực bên trái, nhất là lúc đi bộ nhanh hoặc leo cầu thang lên tầng hai, nghỉ chừng năm phút thì đỡ. Sáng nay đo huyết áp ở nhà thấy lên 155 trên 95.
Bác sĩ: Bác có thấy khó thở, vã mồ hôi hay đau lan lên cằm, lan ra tay trái không?
Bệnh nhân: Không lan bác sĩ ạ, chỉ nặng tức vùng ngực thôi, không khó thở.
Bác sĩ: Bác có tiền sử dị ứng thuốc gì trước đây không?
Bệnh nhân: Có đấy bác sĩ, cách đây hai năm tôi bị viêm họng, uống cái viên nhộng đỏ vàng a-móc... a-móc-xi gì đó là người nổi mề đay ngứa ran cả người, phải đi tiêm chống dị ứng.
Người nhà: Đúng rồi bác sĩ, đợt đấy bố tôi sưng cả mí mắt. À mà bác sĩ xem giùm, tôi dạo này hay khát nước với tiểu đêm nhiều, không biết có bị tiểu đường giống bà ngoại không?
Bác sĩ: Dạ chị người nhà lát nữa ra đăng ký khám chuyên khoa nội tiết riêng nhé, bây giờ bác sĩ tập trung xử lý cho bác An trước. Bác An đang dùng thuốc hạ áp gì đều không?
Bệnh nhân: Tôi đang uống Amlodipine 5mg mỗi sáng một viên, đợt này bận việc nên thỉnh thoảng có hôm quên uống.
Bác sĩ: Tôi khám tim phổi: Tiếng tim T1, T2 đều rõ, không nghe tiếng thổi bệnh lý, phổi trong không rale. Huyết áp đo tại phòng khám hiện tại là 152/92 mmHg, mạch 76 lần/phút. Điện tâm đồ nhịp xoang đều, chưa thấy biến đổi đoạn ST-T cấp tính.
Bác sĩ: Về chẩn đoán: Bác bị Cơn đau thắt ngực ổn định trên nền Tăng huyết áp độ 2 chưa kiểm soát tốt, có tiền sử dị ứng Amoxicillin. Tôi duy trì Amlodipine 5mg/ngày, phối hợp thêm Atorvastatin 20mg/ngày để ổn định mảng xơ vữa mỡ máu. Tuyệt đối ghi vào sổ không dùng kháng sinh nhóm Penicillin, Amoxicillin.
Bác sĩ: Lời dặn: Bác uống thuốc đều đặn vào buổi sáng, không được tự ý ngưng thuốc. Nếu những ngày tới cơn đau ngực xuất hiện cả khi nghỉ ngơi hoặc kéo dài trên 15 phút không đỡ thì phải vào cấp cứu viện ngay để chụp CT mạch vành. Hẹn bác tái khám sau 2 tuần.`;

const soapContent1 = `# BỆNH ÁN LÂM SÀNG (SOAP) — MEDITRACE SENTINEL
**Bệnh nhân:** Trần Văn An | **Tuổi:** 58 | **Giới:** Nam
**Ngày khám:** Hôm nay | **Bác sĩ phụ trách:** BS. Quan Nguyen

---

### S — SUBJECTIVE (BỆNH SỬ & TIỀN SỬ CÓ CĂN CỨ)
- **Lý do khám:** Đau nặng ngực trái khi gắng sức 1 tuần nay [T2].
- **Bệnh sử:** Cơn đau xuất hiện khi đi bộ nhanh, leo cầu thang tầng 2, giảm sau nghỉ ngơi ~5 phút [T2]. Huyết áp đo tại nhà 155/95 mmHg [T2]. Không khó thở, không vã mồ hôi, không lan lên cằm hay tay trái [T4].
- **Tiền sử dị ứng:** 
  - ⚠️ **[BÔI ĐỎ — CẦN BÁC SĨ XÁC NHẬN]:** Bệnh nhân khai uống "viên nhộng đỏ vàng a-móc" bị nổi mề đay dị ứng 2 năm trước -> Gợi ý: **Amoxicillin / Nhóm Penicillin** [T6].
- **Tiền sử bệnh:** Tăng huyết áp đang điều trị Amlodipine 5mg/ngày, thỉnh thoảng quên thuốc [T9].
- *(Ghi chú phân định người nói K3: Bỏ qua thông tin khát nước, tiểu đêm của người nhà đi cùng tại [T7]).*

### O — OBJECTIVE (THỰC THỂ & CẬN LÂM SÀNG)
- **Sinh hiệu:** Huyết áp 152/92 mmHg, Mạch 76 lần/phút [T10].
- **Khám tim mạch:** T1, T2 đều rõ, không tiếng thổi bệnh lý [T10].
- **Khám hô hấp:** Phổi trong, không rale [T10].
- **Điện tâm đồ (ECG tại chỗ):** Nhịp xoang đều, tần số 76 chu kỳ/phút, chưa thấy biến đổi đoạn ST-T cấp tính [T10].

### A — ASSESSMENT (CHẨN ĐOÁN & ĐÁNH GIÁ NGUY CƠ)
- **Chẩn đoán xác định:** Cơn đau thắt ngực ổn định (I20.9).
- **Bệnh kèm theo:** Tăng huyết áp độ 2 (I10) — Tiền sử dị ứng Amoxicillin (Z88.0) [T11].
- **Phân tầng nguy cơ:** Nguy cơ tim mạch cao theo thang điểm SCORE.

### P — PLAN (ĐIỀU TRỊ & THEO DÕI)
1. **Đơn thuốc điều trị:**
   - **Amlodipine 5mg:** Uống 1 viên vào 08:00 sáng hàng ngày [T11].
   - **Atorvastatin 20mg:** Uống 1 viên vào 20:00 tối sau ăn [T11].
2. **Cảnh báo dị ứng tuyệt đối:**
   - 🚫 Không kê đơn nhóm Penicillin, Amoxicillin, Ampicillin [T11].
3. **Kế hoạch theo dõi & Dặn dò (Lọc câu tương lai K4):**
   - Uống thuốc đều đặn mỗi sáng, không tự ý ngưng thuốc [T12].
   - Đến viện cấp cứu ngay nếu đau ngực khi nghỉ ngơi hoặc kéo dài > 15 phút (chỉ định chụp CT mạch vành dự kiến) [T12].
   - Hẹn tái khám sau 2 tuần [T12].`;

const leafletContent1 = `# HƯỚNG DẪN DÙNG THUỐC & CHĂM SÓC CHO BỆNH NHÂN
**Người bệnh:** Bác Trần Văn An | **Mã hồ sơ:** MT-AN-58

---

### ⏰ LỊCH UỐNG THUỐC TRONG NGÀY
- **BUỔI SÁNG (Sau ăn sáng - 08:00):**
  - **Amlodipine 5mg:** 1 viên (Thuốc hạ huyết áp).
- **BUỔI TỐI (Sau ăn tối - 20:00):**
  - **Atorvastatin 20mg:** 1 viên (Thuốc mỡ máu, bảo vệ thành mạch tim).

### 🚫 CẢNH BÁO DỊ ỨNG QUAN TRỌNG:
- Bác có tiền sử dị ứng với **Amoxicillin / Penicillin** (viên nhộng đỏ vàng).
- Mỗi khi đi khám hoặc mua thuốc ở bất kỳ đâu, bác cần đưa tờ này và dặn nhân viên y tế: **"Tôi bị dị ứng Amoxicillin, tuyệt đối không được dùng!"**.

### 🚨 DẤU HIỆU CẦN VÀO VIỆN CẤP CỨU NGAY:
- Cơn đau thắt ngực xuất hiện ngay cả khi đang ngồi nghỉ.
- Cơn đau kéo dài trên 15 phút không thuyên giảm, đau vã mồ hôi hoặc khó thở.`;

const noteMeta1 = {
  content: soapContent1,
  source: "mo_hinh",
  seconds: 32.4,
  needsConfirmCount: 1,
  questions: ["Bác An có tiền sử đái tháo đường hay rối loạn lipid máu xét nghiệm gần đây không?"],
  propositions: [
    {
      id: 1,
      text: "Bệnh nhân có triệu chứng đau nặng ngực bên trái khi gắng sức (đi bộ nhanh, leo cầu thang), giảm sau khi nghỉ ngơi 5 phút.",
      section: "BỆNH SỬ",
      status: "than",
      certainty: "chắc chắn",
      evidenceTurns: [2],
      quotes: ["độ một tuần nay tôi hay thấy nặng ngực bên trái, nhất là lúc đi bộ nhanh hoặc leo cầu thang lên tầng hai, nghỉ chừng năm phút thì đỡ"]
    },
    {
      id: 2,
      text: "Huyết áp tự đo tại nhà đo được là 155/95 mmHg.",
      section: "BỆNH SỬ",
      status: "than",
      certainty: "chắc chắn",
      evidenceTurns: [2],
      quotes: ["Sáng nay đo huyết áp ở nhà thấy lên 155 trên 95"]
    },
    {
      id: 3,
      text: "Không ghi nhận đau ngực lan lên cằm, không lan ra tay trái, không khó thở.",
      section: "BỆNH SỬ",
      status: "than",
      negated: true,
      certainty: "chắc chắn",
      evidenceTurns: [4],
      quotes: ["Không lan bác sĩ ạ, chỉ nặng tức vùng ngực thôi, không khó thở"]
    },
    {
      id: 4,
      text: "TIỀN SỬ DỊ ỨNG: Nhận diện thuốc 'a-móc / viên nhộng đỏ vàng' gây nổi mề đay -> Gợi ý Amoxicillin.",
      section: "CẦN XÁC NHẬN",
      status: "can_xac_nhan",
      gateReason: "BÔI ĐỎ: ASR nhận diện tên thuốc dân gian có độ bất định cao (Zero Silent Normalization). Cần bác sĩ xác nhận hoạt chất Amoxicillin.",
      drug: "Amoxicillin",
      evidenceTurns: [6],
      quotes: ["uống cái viên nhộng đỏ vàng a-móc... a-móc-xi gì đó là người nổi mề đay ngứa ran cả người"]
    },
    {
      id: 5,
      text: "Bệnh nhân đang điều trị huyết áp bằng Amlodipine 5mg mỗi sáng, thỉnh thoảng quên thuốc.",
      section: "TIỀN SỬ",
      status: "than",
      certainty: "chắc chắn",
      evidenceTurns: [9],
      quotes: ["Tôi đang uống Amlodipine 5mg mỗi sáng một viên, đợt này bận việc nên thỉnh thoảng có hôm quên uống"]
    },
    {
      id: 6,
      text: "Khám lâm sàng: Huyết áp phòng khám 152/92 mmHg, Mạch 76 l/p, tim đều T1 T2 rõ, phổi trong không rale, ECG chưa biến đổi ST-T cấp.",
      section: "KHÁM LÂM SÀNG",
      status: "than",
      certainty: "chắc chắn",
      evidenceTurns: [10],
      quotes: ["Huyết áp đo tại phòng khám hiện tại là 152/92 mmHg, mạch 76 lần/phút. Điện tâm đồ nhịp xoang đều, chưa thấy biến đổi đoạn ST-T cấp tính"]
    },
    {
      id: 7,
      text: "Kế hoạch: Duy trì Amlodipine 5mg/ngày, bổ sung Atorvastatin 20mg/ngày, chống chỉ định nhóm Penicillin.",
      section: "ĐIỀU TRỊ",
      status: "than",
      certainty: "chắc chắn",
      evidenceTurns: [11],
      quotes: ["duy trì Amlodipine 5mg/ngày, phối hợp thêm Atorvastatin 20mg/ngày", "Tuyệt đối ghi vào sổ không dùng kháng sinh nhóm Penicillin, Amoxicillin"]
    },
    {
      id: 8,
      text: "Kế hoạch theo dõi: Nếu đau ngực khi nghỉ ngơi hoặc kéo dài >15 phút thì vào cấp cứu chụp CT mạch vành. Tái khám sau 2 tuần.",
      section: "KẾ HOẠCH",
      status: "than",
      situation: "tương lai / điều kiện",
      evidenceTurns: [12],
      quotes: ["Nếu những ngày tới cơn đau ngực xuất hiện cả khi nghỉ ngơi hoặc kéo dài trên 15 phút không đỡ thì phải vào cấp cứu viện ngay để chụp CT mạch vành"]
    }
  ]
};

const session1 = {
  id: "ca-1-tran-van-an",
  patientIdentifier: "Trần Văn An - 58 tuổi",
  patientSubtitle: "Tăng huyết áp độ 2 · Tiền sử dị ứng Amoxicillin · Cảnh báo bôi đỏ ASR",
  date: "Hôm nay",
  time: "08:30",
  language: "Tiếng Việt",
  durationSeconds: 215,
  isRecording: false,
  transcript: transcript1,
  activeTabId: "tab-soap",
  tabs: [
    { id: "tab-transcript", title: "Lời thoại ca khám", type: "transcript", content: transcript1, isClosable: false },
    { id: "tab-soap", title: "Bệnh án SOAP (Có căn cứ)", type: "soap", content: soapContent1, isClosable: false },
    { id: "tab-leaflet", title: "Tờ dặn dò bệnh nhân", type: "leaflet", content: leafletContent1, isClosable: true }
  ],
  note: noteMeta1,
  evidenceChat: [
    {
      id: "msg-1",
      role: "user",
      content: "Vì sao hệ thống lại bôi đỏ cảnh báo ở lượt thoại [T6]?",
      timestamp: "08:35"
    },
    {
      id: "msg-2",
      role: "assistant",
      content: "Tại lượt [T6], bệnh nhân dùng cách gọi dân gian 'viên nhộng đỏ vàng a-móc... a-móc-xi'. Theo quy tắc an toàn cốt lõi (Zero Silent Normalization), hệ thống không được tự ý sửa ngầm thành Amoxicillin mà bắt buộc phải BÔI ĐỎ và chuyển sang danh mục 'CẦN BÁC SĨ XÁC NHẬN' để bác sĩ kiểm tra và quyết định.",
      timestamp: "08:35"
    }
  ]
};

// ==============================================================================
// CA 2: Chị Lê Thị Mai - 34 tuổi
// ==============================================================================
const transcript2 = `Bác sĩ: Chào chị Mai, mời chị ngồi. Chị bị khó chịu thế nào?
Bệnh nhân: Dạ chào bác sĩ, tôi bị ho nhiều, có khạc đờm màu xanh vàng, người sốt hâm hấp khó chịu, đau rát cổ họng.
Bác sĩ: Chị bị ho và sốt từ hôm nào rồi?
Bệnh nhân: Tôi ho từ thứ Hai đầu tuần... à không, nhớ nhầm, chính xác là từ tối thứ Năm vừa rồi mới bắt đầu ho nhiều và sốt, tức là được bốn ngày nay rồi bác sĩ.
Bác sĩ: Chị ở nhà đã tự uống thuốc gì chưa?
Bệnh nhân: Tôi có uống hai viên hạ sốt panadol với siro ho bổ phế nhưng không đỡ ho mấy.
Bác sĩ: Chị có bệnh nền hoặc dị ứng thuốc gì không?
Bệnh nhân: Tôi không dị ứng thuốc gì. Dạ dày tôi thỉnh thoảng hay đau rát vùng thượng vị khi ăn đồ chua cay, đi nội soi năm ngoái có viêm trợt hang vị nhẹ.
Bác sĩ: Khám lâm sàng: Họng đỏ nhẹ, amidan không sưng mủ. Nhiệt độ cơ thể 38.2°C, SpO2 98%, huyết áp 115/75 mmHg. Nghe phổi có rale ngáy rải rác hai phế trường, không rale ẩm, không co kéo cơ hô hấp phụ.
Bác sĩ: Chẩn đoán: Viêm phế quản cấp nghi do bội nhiễm vi khuẩn trên nền tiền sử Viêm dạ dày.
Bác sĩ: Về điều trị: Kê kháng sinh Cefuroxime axetil 500mg uống 1 viên x 2 lần/ngày sau ăn trong 7 ngày; Thuốc long đờm Acetylcysteine 200mg uống 1 gói x 3 lần/ngày; Paracetamol 500mg uống 1 viên khi sốt từ 38.5°C trở lên, cách nhau tối thiểu 4-6 giờ. Vì chị có đau dạ dày nên tôi không kê thuốc giảm đau chống viêm nhóm NSAID như Ibuprofen để tránh xuất huyết dạ dày.
Bác sĩ: Dặn dò: Uống nhiều nước ấm, súc họng nước muối sinh lý hàng ngày. Nếu sau 3 ngày vẫn sốt cao liên tục hoặc ho ra máu thì phải quay lại khám ngay. Hẹn tái khám sau 7 ngày.`;

const soapContent2 = `# BỆNH ÁN LÂM SÀNG (SOAP) — MEDITRACE SENTINEL
**Bệnh nhân:** Lê Thị Mai | **Tuổi:** 34 | **Giới:** Nữ
**Ngày khám:** Hôm nay | **Bác sĩ phụ trách:** BS. Quan Nguyen

---

### S — SUBJECTIVE (BỆNH SỬ & TIỀN SỬ CÓ CĂN CỨ)
- **Lý do khám:** Ho khạc đờm vàng xanh, sốt, đau rát họng [T2].
- **Bệnh sử (Đã đính chính FSM K7):** 
  - Khởi phát: 4 ngày nay (từ tối thứ Năm) [T4].
  - *(Ghi chú đối soát FSM: Bệnh nhân ban đầu nói 'thứ Hai đầu tuần', ngay sau đó đính chính thành 'tối thứ Năm, 4 ngày' -> Hệ thống tự động cập nhật mốc 4 ngày, loại bỏ mốc cũ [T4]).*
  - Đã dùng: Paracetamol 2 viên + siro ho tại nhà, đỡ ít [T6].
- **Tiền sử:** Viêm trợt hang vị dạ dày nhẹ năm ngoái, không dị ứng thuốc [T8].

### O — OBJECTIVE (THỰC THỂ & CẬN LÂM SÀNG)
- **Sinh hiệu:** Nhiệt độ 38.2°C, SpO2 98%, Huyết áp 115/75 mmHg [T9].
- **Khám họng:** Họng đỏ nhẹ, amidan không hốc mủ [T9].
- **Khám hô hấp:** Rale ngáy rải rác 2 phế trường, không rale ẩm, không co kéo [T9].

### A — ASSESSMENT (CHẨN ĐOÁN LÂM SÀNG)
- **Chẩn đoán xác định:** Viêm phế quản cấp nghi bội nhiễm vi khuẩn (J20.9) [T10].
- **Bệnh kèm:** Viêm dạ dày mạn (K29.5) [T10].

### P — PLAN (ĐIỀU TRỊ & AN TOÀN DƯỢC LÝ)
1. **Đơn thuốc điều trị (7 ngày):**
   - **Cefuroxime axetil 500mg:** 1 viên x 2 lần/ngày (sáng 1 viên, tối 1 viên sau ăn) [T11].
   - **Acetylcysteine 200mg:** 1 gói x 3 lần/ngày pha nước ấm uống [T11].
   - **Paracetamol 500mg:** 1 viên khi sốt >= 38.5°C (cách tối thiểu 4-6h) [T11].
2. **Kiểm soát an toàn tương tác thuốc (CDSS):**
   - 🛡️ Chống chỉ định tương đối NSAIDs (Ibuprofen/Diclofenac) do tiền sử viêm dạ dày [T11].
3. **Theo dõi & Dặn dò:** Uống nhiều nước, súc họng nước muối. Tái khám sau 7 ngày hoặc khi sốt cao kéo dài [T12].`;

const leafletContent2 = `# HƯỚNG DẪN DÙNG THUỐC & ĐIỀU TRỊ TẠI NHÀ
**Bệnh nhân:** Chị Lê Thị Mai | **Chẩn đoán:** Viêm phế quản cấp

---

### ⏰ LỊCH UỐNG THUỐC TRONG NGÀY
- **BUỔI SÁNG (Sau ăn):**
  - **Cefuroxime 500mg:** 1 viên (Kháng sinh - Uống đủ 7 ngày, không tự ý ngưng).
  - **Acetylcysteine 200mg:** 1 gói (Long đờm).
- **BUỔI TRƯA (Sau ăn):**
  - **Acetylcysteine 200mg:** 1 gói.
- **BUỔI TỐI (Sau ăn):**
  - **Cefuroxime 500mg:** 1 viên.
  - **Acetylcysteine 200mg:** 1 gói.
- **KHI SỐT CAO (Trên 38.5°C):**
  - **Paracetamol 500mg:** 1 viên.

### ⚠️ LƯU Ý CHO DẠ DÀY:
- Chị có tiền sử viêm dạ dày nên bác sĩ không kê thuốc kháng viêm Ibuprofen. Uống thuốc đúng sau khi ăn no.`;

const noteMeta2 = {
  content: soapContent2,
  source: "mo_hinh",
  seconds: 28.1,
  needsConfirmCount: 0,
  questions: [],
  propositions: [
    {
      id: 1,
      text: "Bệnh nhân có triệu chứng ho nhiều, khạc đờm màu xanh vàng, sốt nhẹ và đau rát họng.",
      section: "BỆNH SỬ",
      status: "than",
      certainty: "chắc chắn",
      evidenceTurns: [2],
      quotes: ["tôi bị ho nhiều, có khạc đờm màu xanh vàng, người sốt hâm hấp khó chịu, đau rát cổ họng"]
    },
    {
      id: 2,
      text: "Thời gian khởi phát bệnh: 4 ngày nay (bắt đầu từ tối thứ Năm, đính chính câu nói nhầm thứ Hai).",
      section: "BỆNH SỬ",
      status: "than",
      certainty: "chắc chắn",
      time: "4 ngày",
      evidenceTurns: [4],
      quotes: ["chính xác là từ tối thứ Năm vừa rồi mới bắt đầu ho nhiều và sốt, tức là được bốn ngày nay rồi bác sĩ"]
    },
    {
      id: 3,
      text: "Tiền sử bệnh nhân có viêm trợt hang vị dạ dày nhẹ, không có dị ứng thuốc.",
      section: "TIỀN SỬ",
      status: "than",
      certainty: "chắc chắn",
      evidenceTurns: [8],
      quotes: ["Dạ dày tôi thỉnh thoảng hay đau rát vùng thượng vị khi ăn đồ chua cay, đi nội soi năm ngoái có viêm trợt hang vị nhẹ"]
    },
    {
      id: 4,
      text: "Khám lâm sàng: Thân nhiệt 38.2°C, SpO2 98%, họng đỏ nhẹ, phổi có rale ngáy rải rác 2 phế trường.",
      section: "KHÁM LÂM SÀNG",
      status: "than",
      certainty: "chắc chắn",
      evidenceTurns: [9],
      quotes: ["Nhiệt độ cơ thể 38.2°C, SpO2 98%", "Nghe phổi có rale ngáy rải rác hai phế trường"]
    },
    {
      id: 5,
      text: "Chẩn đoán xác định: Viêm phế quản cấp nghi bội nhiễm trên nền Viêm dạ dày.",
      section: "CHẨN ĐOÁN",
      status: "than",
      certainty: "chắc chắn",
      evidenceTurns: [10],
      quotes: ["Chẩn đoán: Viêm phế quản cấp nghi do bội nhiễm vi khuẩn trên nền tiền sử Viêm dạ dày"]
    },
    {
      id: 6,
      text: "Đơn thuốc: Cefuroxime axetil 500mg (1v x 2l/ng), Acetylcysteine 200mg (1g x 3l/ng), Paracetamol 500mg khi sốt >= 38.5°C.",
      section: "ĐIỀU TRỊ",
      status: "than",
      certainty: "chắc chắn",
      evidenceTurns: [11],
      quotes: ["Cefuroxime axetil 500mg uống 1 viên x 2 lần/ngày", "Acetylcysteine 200mg uống 1 gói x 3 lần/ngày"]
    },
    {
      id: 7,
      text: "Khóa an toàn dược lý CDSS: Không sử dụng thuốc nhóm NSAID (Ibuprofen) để phòng ngừa nguy cơ xuất huyết tiêu hóa.",
      section: "ĐIỀU TRỊ",
      status: "than",
      certainty: "chắc chắn",
      evidenceTurns: [11],
      quotes: ["Vì chị có đau dạ dày nên tôi không kê thuốc giảm đau chống viêm nhóm NSAID như Ibuprofen để tránh xuất huyết dạ dày"]
    }
  ]
};

const session2 = {
  id: "ca-2-le-thi-mai",
  patientIdentifier: "Lê Thị Mai - 34 tuổi",
  patientSubtitle: "Viêm phế quản cấp · Tiền sử viêm dạ dày · Đính chính mốc thời gian",
  date: "Hôm nay",
  time: "09:15",
  language: "Tiếng Việt",
  durationSeconds: 180,
  isRecording: false,
  transcript: transcript2,
  activeTabId: "tab-soap",
  tabs: [
    { id: "tab-transcript", title: "Lời thoại ca khám", type: "transcript", content: transcript2, isClosable: false },
    { id: "tab-soap", title: "Bệnh án SOAP (Có căn cứ)", type: "soap", content: soapContent2, isClosable: false },
    { id: "tab-leaflet", title: "Tờ dặn dò bệnh nhân", type: "leaflet", content: leafletContent2, isClosable: true }
  ],
  note: noteMeta2,
  evidenceChat: [
    {
      id: "msg-2-1",
      role: "user",
      content: "Hệ thống đã xử lý câu nói nhầm về thời gian ở lượt [T4] như thế nào?",
      timestamp: "09:20"
    },
    {
      id: "msg-2-2",
      role: "assistant",
      content: "Nhờ thuật toán FSM (Finite State Machine) kiểm soát đính chính thời gian (Bước K7), khi bệnh nhân phát biểu 'từ thứ Hai... à không, nhớ nhầm, chính xác là tối thứ Năm, 4 ngày', hệ thống tự động gán nhãn superseded cho mệnh đề 'thứ Hai' và chỉ cập nhật mốc thời gian 4 ngày vào bệnh án SOAP.",
      timestamp: "09:20"
    }
  ]
};

// ==============================================================================
// CA 3: Bác Hoàng Quốc Dũng - 66 tuổi
// ==============================================================================
const transcript3 = `Bác sĩ: Chào bác Dũng, mời bác ngồi. Hôm nay bác đến tái khám định kỳ theo hẹn đúng không ạ?
Bệnh nhân: Vâng chào bác sĩ, tôi đến tái khám tiểu đường và huyết áp hàng tháng. Dạo này thỉnh thoảng thấy tim đập hơi nhanh và hồi hộp trong ngực.
Bác sĩ: Bác mang theo kết quả xét nghiệm máu và nước tiểu làm sáng nay ở khoa xét nghiệm chưa?
Bệnh nhân: Đây bác sĩ, các cô bên xét nghiệm vừa in kết quả đưa cho tôi đây.
Bác sĩ: Để tôi xem: Đường huyết đói Glucose 7.8 mmol/L, HbA1c 7.6%. Huyết áp đo tại chỗ 138/85 mmHg. Đặc biệt Creatinine huyết thanh tăng lên 160 umol/L, độ lọc cầu thận ước tính eGFR giảm còn 38 mL/phút trên 1.73m2. Điện tâm đồ có sóng P biến mất thay bằng sóng f lăn tăn, nhịp tim không đều tần số 88 lần/phút, hình ảnh rung nhĩ.
Bác sĩ: Bác đang dùng những thuốc gì ở nhà kể cho tôi nghe?
Bệnh nhân: Tôi đang uống Metformin 1000mg ngày 2 viên sáng tối, Gliclazide MR 60mg sáng 1 viên, và Losartan 50mg ngày 1 viên.
Bác sĩ: Bác Dũng lưu ý rất quan trọng: Kết quả xét nghiệm cho thấy chức năng thận của bác đã suy giảm ở mức độ 3b (eGFR 38 mL/phút). Ở mức thận này, liều Metformin 2000mg/ngày bác đang uống là QUÁ LIỀU NGUY HIỂM, có nguy cơ gây nhiễm toan acid lactic. Bác sĩ phải điều chỉnh ngay: Giảm liều Metformin xuống tối đa 500mg/ngày hoặc chuyển sang phối hợp thuốc ức chế DPP-4 an toàn cho thận như Linagliptin 5mg/ngày.
Bác sĩ: Thêm vào đó, bác 66 tuổi, có Tăng huyết áp và Tiểu đường, nay xuất hiện Rung nhĩ. Tính theo thang điểm lâm sàng CHA2DS2-VASc bác được 4 điểm, thuộc nhóm nguy cơ cao đột quỵ do huyết khối. Bắt buộc phải dùng thuốc chống đông đường uống thế hệ mới như Rivaroxaban 15mg/ngày (đã hiệu chỉnh liều theo chức năng thận eGFR 38).
Bác sĩ: Kế hoạch điều trị: 1. Linagliptin 5mg uống 1 viên sáng. 2. Losartan 50mg uống 1 viên sáng. 3. Rivaroxaban 15mg uống 1 viên tối sau ăn. Dừng Metformin 1000mg.
Bác sĩ: Dặn dò: Theo dõi các dấu hiệu xuất huyết như bầm tím dưới da, chảy máu chân răng hoặc đi ngoài phân đen. Xét nghiệm lại chức năng thận và đường huyết sau 1 tháng.`;

const soapContent3 = `# BỆNH ÁN LÂM SÀNG (SOAP) — MEDITRACE SENTINEL
**Bệnh nhân:** Hoàng Quốc Dũng | **Tuổi:** 66 | **Giới:** Nam
**Ngày khám:** Hôm nay | **Bác sĩ phụ trách:** BS. Quan Nguyen

---

### S — SUBJECTIVE (BỆNH SỬ & LÝ DO KHÁM)
- **Lý do khám:** Tái khám định kỳ Đái tháo đường Type 2, Tăng huyết áp; gần đây có hồi hộp, đánh trống ngực [T2].
- **Thuốc đang dùng tại nhà:** Metformin 1000mg x 2 viên/ngày (2000mg/ngày), Gliclazide MR 60mg x 1v/ngày, Losartan 50mg x 1v/ngày [T7].

### O — OBJECTIVE (CẬN LÂM SÀNG & SINH HIỆU CÓ CĂN CỨ)
- **Huyết áp:** 138/85 mmHg, Nhịp tim không đều ~88 ck/phút [T5].
- **Cận lâm sàng sinh hóa:**
  - Glucose đói: 7.8 mmol/L | HbA1c: 7.6% [T5].
  - Creatinine huyết thanh: **160 µmol/L** [T5].
  - Độ lọc cầu thận ước tính (**eGFR**): **38 mL/phút/1.73m²** -> **Suy thận mạn giai đoạn 3b** [T5].
- **Điện tâm đồ (ECG):** Sóng P biến mất, thay bằng sóng f lăn tăn, nhịp không đều -> **Rung nhĩ mới phát hiện** [T5].

### A — ASSESSMENT & HỆ THỐNG CDSS TÍNH ĐIỂM
- **Chẩn đoán:** Rung nhĩ (I48) — Đái tháo đường Type 2 (E11) — Tăng huyết áp (I10) — Bệnh thận mạn giai đoạn 3b (N18.3b).
- **Hệ thống CDSS Thang điểm lâm sàng:**
  - **Thang điểm CHA2DS2-VASc = 4 ĐIỂM** (Tuổi 66: 1đ, Tăng huyết áp: 1đ, Đái tháo đường: 1đ, Rung nhĩ: 1đ) -> **Nguy cơ đột quỵ rất cao**, CHỈ ĐỊNH BẮT BUỘC DÙNG THUỐC CHỐNG ĐÔNG (NOAC) [T9].
- **Cảnh báo an toàn Dược lý (CDSS K6):**
  - 🚨 **CẢNH BÁO QUÁ LIỀU METFORMIN:** eGFR 38 mL/phút chống chỉ định dùng liều > 1000mg/ngày (nguy cơ nhiễm toan acid lactic). Bệnh nhân đang dùng 2000mg/ngày -> YÊU CẦU NGƯNG HOẶC ĐỔI THUỐC [T8].

### P — PLAN (HIỆU CHỈNH LIỀU & ĐIỀU TRỊ AN TOÀN)
1. **Thay đổi phác đồ điều trị:**
   - **Ngưng Metformin 1000mg** [T8, T10].
   - **Linagliptin 5mg:** 1 viên uống sáng (Không cần chỉnh liều theo chức năng thận) [T10].
   - **Losartan 50mg:** 1 viên uống sáng [T10].
   - **Rivaroxaban 15mg:** 1 viên uống tối sau ăn (**Đã hiệu chỉnh giảm liều từ 20mg xuống 15mg** do eGFR 38 mL/phút) [T9, T10].
2. **Theo dõi:** Dấu hiệu xuất huyết, xét nghiệm lại chức năng thận sau 1 tháng [T11].`;

const leafletContent3 = `# HƯỚNG DẪN DÙNG THUỐC & THEO DÕI AN TOÀN
**Người bệnh:** Bác Hoàng Quốc Dũng | **Mã hồ sơ:** MT-DUNG-66

---

### ⏰ LỊCH UỐNG THUỐC MỚI (ĐÃ ĐIỀU CHỈNH CHO THẬN)
- **BUỔI SÁNG (Sau ăn):**
  - **Linagliptin 5mg:** 1 viên (Thuốc tiểu đường mới - An toàn cho thận).
  - **Losartan 50mg:** 1 viên (Thuốc huyết áp bảo vệ thận).
- **BUỔI TỐI (Sau ăn tối):**
  - **Rivaroxaban 15mg:** 1 viên (Thuốc chống đông máu ngăn ngừa đột quỵ).

### ⛔ ĐÃ DỪNG THUỐC:
- **Ngưng hoàn toàn Metformin 1000mg** do chức năng thận đang giảm.

### 🚨 THEO DÕI AN TOÀN:
- Bác đang dùng thuốc chống đông máu nên nếu thấy chảy máu chân răng nhiều, vết bầm tím lan rộng hoặc đi tiểu đỏ thì liên hệ bác sĩ ngay.`;

const noteMeta3 = {
  content: soapContent3,
  source: "mo_hinh",
  seconds: 35.8,
  needsConfirmCount: 0,
  questions: ["Bác Dũng có tiền sử xuất huyết tiêu hóa hoặc loét dạ dày tá tràng trước đây không?"],
  propositions: [
    {
      id: 1,
      text: "Lý do khám: Tái khám định kỳ đái tháo đường, tăng huyết áp; kèm triệu chứng tim đập nhanh hồi hộp gần đây.",
      section: "BỆNH SỬ",
      status: "than",
      certainty: "chắc chắn",
      evidenceTurns: [2],
      quotes: ["tôi đến tái khám tiểu đường và huyết áp hàng tháng. Dạo này thỉnh thoảng thấy tim đập hơi nhanh và hồi hộp trong ngực"]
    },
    {
      id: 2,
      text: "Kết quả cận lâm sàng: Glucose đói 7.8 mmol/L, HbA1c 7.6%, Creatinine 160 umol/L, eGFR giảm 38 mL/phút/1.73m2 (Suy thận mạn K3b).",
      section: "CẬN LÂM SÀNG",
      status: "than",
      certainty: "chắc chắn",
      evidenceTurns: [5],
      quotes: ["Đường huyết đói Glucose 7.8 mmol/L, HbA1c 7.6%", "Creatinine huyết thanh tăng lên 160 umol/L, độ lọc cầu thận ước tính eGFR giảm còn 38 mL/phút"]
    },
    {
      id: 3,
      text: "Điện tâm đồ (ECG): Mất sóng P, xuất hiện sóng f lăn tăn, nhịp không đều tần số 88 l/p -> Rung nhĩ.",
      section: "CẬN LÂM SÀNG",
      status: "than",
      certainty: "chắc chắn",
      evidenceTurns: [5],
      quotes: ["Điện tâm đồ có sóng P biến mất thay bằng sóng f lăn tăn, nhịp tim không đều tần số 88 lần/phút, hình ảnh rung nhĩ"]
    },
    {
      id: 4,
      text: "Thuốc đang dùng tại nhà: Metformin 1000mg x 2 viên/ngày, Gliclazide MR 60mg x 1v/ngày, Losartan 50mg x 1v/ngày.",
      section: "TIỀN SỬ THUỐC",
      status: "than",
      certainty: "chắc chắn",
      evidenceTurns: [7],
      quotes: ["Metformin 1000mg ngày 2 viên sáng tối, Gliclazide MR 60mg sáng 1 viên, và Losartan 50mg ngày 1 viên"]
    },
    {
      id: 5,
      text: "CẢNH BÁO AN TOÀN DƯỢC LÝ CDSS: Bệnh nhân suy thận eGFR 38 mL/p dùng Metformin 2000mg/ngày là quá liều an toàn -> Ngưng Metformin, đổi sang Linagliptin 5mg.",
      section: "AN TOÀN DƯỢC LÝ",
      status: "than",
      certainty: "chắc chắn",
      evidenceTurns: [8],
      quotes: ["Ở mức thận này, liều Metformin 2000mg/ngày bác đang uống là QUÁ LIỀU NGUY HIỂM", "Giảm liều Metformin xuống tối đa 500mg/ngày hoặc chuyển sang phối hợp thuốc ức chế DPP-4 an toàn cho thận như Linagliptin 5mg/ngày"]
    },
    {
      id: 6,
      text: "THANG ĐIỂM LÂM SÀNG CDSS: Thang điểm CHA2DS2-VASc = 4 điểm (Tuổi 66, Tăng huyết áp, ĐTĐ, Rung nhĩ) -> Bắt buộc dùng Rivaroxaban 15mg/ngày (hiệu chỉnh liều theo eGFR 38).",
      section: "ĐIỀU TRỊ",
      status: "than",
      certainty: "chắc chắn",
      evidenceTurns: [9],
      quotes: ["Tính theo thang điểm lâm sàng CHA2DS2-VASc bác được 4 điểm, thuộc nhóm nguy cơ cao đột quỵ do huyết khối. Bắt buộc phải dùng thuốc chống đông đường uống thế hệ mới như Rivaroxaban 15mg/ngày"]
    }
  ]
};

const session3 = {
  id: "ca-3-hoang-quoc-dung",
  patientIdentifier: "Hoàng Quốc Dũng - 66 tuổi",
  patientSubtitle: "Đái tháo đường T2 · Rung nhĩ · Suy thận mạn K3b · Cảnh báo liều Metformin CDSS",
  date: "Hôm nay",
  time: "10:00",
  language: "Tiếng Việt",
  durationSeconds: 240,
  isRecording: false,
  transcript: transcript3,
  activeTabId: "tab-soap",
  tabs: [
    { id: "tab-transcript", title: "Lời thoại ca khám", type: "transcript", content: transcript3, isClosable: false },
    { id: "tab-soap", title: "Bệnh án SOAP (Có căn cứ)", type: "soap", content: soapContent3, isClosable: false },
    { id: "tab-leaflet", title: "Tờ dặn dò bệnh nhân", type: "leaflet", content: leafletContent3, isClosable: true }
  ],
  note: noteMeta3,
  evidenceChat: [
    {
      id: "msg-3-1",
      role: "user",
      content: "Giải thích cách hệ thống CDSS tính thang điểm CHA2DS2-VASc và hiệu chỉnh liều?",
      timestamp: "10:05"
    },
    {
      id: "msg-3-2",
      role: "assistant",
      content: "Hệ thống trích xuất thực thể: Bệnh nhân 66 tuổi (+1 điểm nhóm 65-74), Tăng huyết áp (+1 điểm), Đái tháo đường (+1 điểm), Rung nhĩ (+1 điểm) -> Tổng 4 điểm CHA2DS2-VASc (nguy cơ thuyên tắc mạch cao, khuyến cáo cấp I dùng NOAC). Đồng thời từ eGFR 38 mL/phút/1.73m2, CDSS tự động kích hoạt luật an toàn: cảnh báo độc tính Metformin và hiệu chỉnh giảm liều Rivaroxaban từ 20mg xuống 15mg/ngày.",
      timestamp: "10:05"
    }
  ]
};

// ==============================================================================
// GHI VÀO CƠ SỞ DỮ LIỆU SQLITE
// ==============================================================================
console.log("Bat dau ghi 3 ca mau vao tai khoan...");

db.exec("BEGIN IMMEDIATE");
try {
  const dsCa = [session1, session2, session3];
  const now = Date.now();

  for (const u of [1, 2]) {
    db.prepare("DELETE FROM ca_kham WHERE nguoi_dung_id = ?").run(u);

    for (let idx = 0; idx < dsCa.length; idx++) {
      const s = dsCa[idx];
      db.prepare(`
        INSERT INTO ca_kham (nguoi_dung_id, id, thu_tu, ten_benh_nhan, ngay_kham, du_lieu, tao_luc, cap_nhat_luc)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
      `).run(
        u,
        s.id,
        idx,
        s.patientIdentifier,
        s.date,
        JSON.stringify(s),
        now,
        now
      );
    }

    db.prepare(`
      INSERT INTO moc_luu (nguoi_dung_id, kho, luu_luc)
      VALUES (?, 'ca-kham', ?)
      ON CONFLICT (nguoi_dung_id, kho) DO UPDATE SET luu_luc = ?
    `).run(u, now + 10000000, now + 10000000);
    console.log(`[+] Da ghi 3 ca mau cho UID ${u}`);
  }

  db.exec("COMMIT");
  console.log("✅ HOAN TAT: Da nap 3 ca mau lam sang tieu chuan cho ca 2 tai khoan!");
} catch (err) {
  db.exec("ROLLBACK");
  console.error("[-] Loi khi nap ca:", err);
}
