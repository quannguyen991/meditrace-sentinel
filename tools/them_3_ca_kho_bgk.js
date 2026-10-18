// -*- coding: utf-8 -*-
/**
 * Bộ 3 Ca Mẫu Lâm Sàng Độ Khó Cao (High-Difficulty / Complex Ambiguities & Clinical Traps)
 * Được thiết kế chuyên biệt để trình diễn trước Ban Giám Khảo (BGK):
 * 
 * 1. Ca 1: Bác Đặng Đình Phúc (62 tuổi)
 *    - Tình huống: Sau đặt Stent mạch vành, Tăng huyết áp, Đau dạ dày, Đau khớp.
 *    - Bẫy lâm sàng:
 *      + Nhầm lẫn tên thuốc âm thanh tương đồng (LASA): "la-xích / pla-vích" (Lasix vs Plavix) & "co-va-xin / co-ve-xin" (Coveram vs Coversyl).
 *      + Tương tác thuốc chết người cấp 1 (DDI Black-box): Tự uống Omeprazole ức chế CYP2C19 triệt tiêu tác dụng của Plavix (nguy cơ tắc Stent tử vong).
 *      + Đính chính liều 3 tầng (Multi-turn self-contradiction): Tự ý thay đổi liều Coversyl từ 1v x 2l -> 0.5v -> 1v x 2l trong 3 ngày qua.
 *      + Dấu hiệu báo động xuất huyết: Đi cầu phân đen như bã cà phê do uống kèm thuốc giảm đau trên nền kháng kết tập tiểu cầu.
 * 
 * 2. Ca 2: Cô Vũ Thị Bích Thủy (49 tuổi)
 *    - Tình huống: Hen phế quản bậc 3, Thoái hóa khớp gối, Rối loạn lo âu.
 *    - Bẫy lâm sàng:
 *      + Chống chỉ định tử vong trong Hen phế quản: Xin kê Aspirin / Ibuprofen (nguy cơ co thắt phế quản ác tính Hội chứng Widal tử vong trong vài phút).
 *      + Bẫy đại từ người nhà cực kỳ lộn xộn (Bước K3): Con gái nói dồn dập về mẹ, bố sụt 4 cân, đường huyết bố 11.5 -> Lọc sạch thông tin của bố.
 *      + Bẫy phủ định kép phức tạp: "Không phải là không dùng ống xịt, nhưng không phải ngày nào cũng không thở được".
 *      + Lọc câu điều kiện lồng ghép (Bước K4): Kế hoạch cấp cứu gọi 115 khi tím tái đưa vào Plan, không ghi thành bệnh nhân đang bị tím tái.
 * 
 * 3. Ca 3: Cụ Bùi Văn Thành (72 tuổi)
 *    - Tình huống: COPD nhóm E, Đợt mất bù suy tim mạn, Phì đại tiền liệt tuyến (BPH).
 *    - Bẫy lâm sàng:
 *      + Tác dụng phụ kháng Cholinergic nguy hiểm: Tự uống Clorpheniramin gây bí tiểu cấp trên nền BPH và làm quánh đặc đờm COPD.
 *      + Mâu thuẫn lâm sàng nội tại (Self-Contradiction Gate): Câu trước bảo không sốt, câu sau khai rét run sốt gần 39°C.
 *      + Số liệu nói tắt & Tiếng lóng: "mười sáu chín" (160/90 mmHg), tăng 2.5 kg ứ dịch, chân phù ấn lõm sâu hoắm.
 */

const { DatabaseSync } = require("node:sqlite");
const path = require("path");

const dbPath = path.join(__dirname, "..", "web", "data", "meditrace.db");
const db = new DatabaseSync(dbPath);

// ==============================================================================
// CA KHÓ 1: BÁC ĐẶNG ĐÌNH PHÚC (62 TUỔI)
// ==============================================================================
const transcript1 = `Bác sĩ: Chào bác Phúc, mời bác ngồi. Hôm nay bác đến khám lại bệnh mạch vành đúng không?
Bệnh nhân: Vâng chào bác sĩ, tôi đặt stent mạch vành được sáu tháng nay rồi. Dạo này ở nhà thấy tức nặng ngực trái âm ỉ, không phải là đau dữ dội, nhưng không lúc nào thấy ngực nhẹ nhõm hẳn.
Bác sĩ: Bác kể kỹ cho tôi nghe hiện tại bác đang uống những thuốc gì mỗi ngày?
Bệnh nhân: Tôi đang uống viên thuốc chống đông gì tên la-xích... à không, nhớ nhầm, viên pla-vích 75 miligram một viên, với lại một viên huyết áp tên co-va-xin hay co-ve-xin năm mi-li-gam.
Bác sĩ: Về viên thuốc huyết áp đó, bác đang uống liều thế nào?
Bệnh nhân: Đợt trước bác sĩ kê uống một viên sáng, một viên tối. Nhưng tháng trước tôi đo thấy tụt còn chín mươi lăm trên sáu mươi nên bác sĩ trạm bảo giảm còn nửa viên buổi sáng thôi. Nhưng mà ba hôm nay ở nhà đo thấy nó lại vọt lên một trăm năm mươi lăm trên chín mươi, nên tôi tự uống lại một viên sáng một viên tối từ hôm kia đến giờ.
Bác sĩ: Bác có đang tự mua thêm thuốc gì bên ngoài uống kèm không?
Bệnh nhân: Có bác sĩ, cái bao tử dạo này cứ ợ chua cồn cào, tôi ra tiệm thuốc tây gần nhà người ta bán cho vỉ ô-mê-pờ-ra-zôn 20 miligram, dặn uống một viên trước ăn sáng, tôi uống được gần hai tuần nay rồi. Lại thêm dạo này hai khớp gối đau nhức quá nên tiệm thuốc họ đưa thêm mấy viên giảm đau màu hồng bảo uống cho đỡ nhức.
Bác sĩ: Bác có để ý tính chất phân mấy ngày nay thế nào không? Có đi cầu phân đen không?
Bệnh nhân: Đúng rồi bác sĩ, hai ngày nay tôi đi cầu thấy phân sẫm màu hẳn, đen sệt như bã cà phê, người thấy hơi chóng mặt lúc đứng dậy.
Người nhà: Bác sĩ ơi, mẹ tôi ở nhà thì bảo đợt này bà ấy sụt mất ba cân, hay bị tê bì chân tay, bác sĩ xem có cần mua thêm sữa tiểu đường cho bà ấy uống không?
Bác sĩ: Chị người nhà để bác sĩ giải quyết ca cấp này của bác Phúc trước nhé. Bác Phúc nghe tôi dặn thật kỹ: Bác đang gặp HAI NGUY CƠ RẤT NGUY HIỂM. Thứ nhất, thuốc dạ dày Omeprazole bác tự uống sẽ ức chế men gan CYP2C19, làm mất tác dụng chống đông của Plavix, nguy cơ gây tắc huyết khối tái phát trong lòng Stent mạch vành có thể đột tử! Bắt buộc phải ngừng ngay Omeprazole, chuyển sang dùng Pantoprazole 40mg. Thứ hai, bác đang có dấu hiệu xuất huyết tiêu hóa do thuốc giảm đau phối hợp với thuốc chống kết tập tiểu cầu, phân đen như bã cà phê là báo động đỏ!
Bác sĩ: Khám thực thể: Huyết áp hiện tại 145/88 mmHg, mạch 84 lần/phút, da niêm mạc nhợt nhẹ, ấn đau tức nhẹ vùng thượng vị, không có phản ứng thành bụng.
Bác sĩ: Xử trí khẩn: Ngưng ngay lập tức Omeprazole và các thuốc giảm đau khớp tự mua. Chỉ định nội soi dạ dày thực quản cấp cứu để tìm điểm xuất huyết. Duy trì Plavix 75mg sau khi hội chẩn chuyên khoa tiêu hóa, đổi thuốc bảo vệ dạ dày sang Pantoprazole 40mg tiêm tĩnh mạch. Huyết áp tạm dùng Coversyl 5mg 1 viên sáng, không tự ý tăng gấp đôi liều. Bác phải nhập viện theo dõi ngay hôm nay!`;

const soap1 = `# BỆNH ÁN LÂM SÀNG (SOAP) — MEDITRACE SENTINEL (CẢNH BÁO BẬC CAO)
**Bệnh nhân:** Đặng Đình Phúc | **Tuổi:** 62 | **Giới:** Nam
**Ngày khám:** Hôm nay | **Bác sĩ phụ trách:** BS. Quan Nguyen

---

### S — SUBJECTIVE (BỆNH SỬ & BẪY THÔNG TIN CÓ CĂN CỨ)
- **Lý do khám:** Tức nặng ngực trái âm ỉ, mệt, chóng mặt khi đứng dậy [T2, T10].
- **Tiền sử tim mạch:** Đặt Stent động mạch vành 6 tháng nay [T2].
- **Bẫy âm vị tên thuốc LASA & Tự ý đổi liều (K1, K7):**
  - ⚠️ **[BÔI ĐỎ — CẦN BÁC SĨ DUYỆT]:** Phát âm nhầm "la-xích... pla-vích" -> Nhận diện hoạt chất: **Plavix (Clopidogrel 75mg)** [T4].
  - ⚠️ **[BÔI ĐỎ — CẦN BÁC SĨ DUYỆT]:** Tên thuốc huyết áp "co-va-xin / co-ve-xin" -> Xác nhận: **Coversyl (Perindopril 5mg)** [T4].
  - ⚠️ **[BÔI ĐỎ — ĐÍNH CHÍNH LIỀU 3 TẦNG]:** Bệnh nhân tự ý đổi liều Coversyl (kê ban đầu 1v x 2l -> giảm 0.5v/sáng -> 3 ngày nay tự ý uống lại 1v x 2l/ngày) [T6].
- **Báo động tương tác thuốc nguy hiểm & Xuất huyết tiêu hóa:**
  - 🚨 **[BÔI ĐỎ KHẨN CẤP — TƯƠNG TÁC ĐỘ 1 BLACK-BOX]:** Tự mua **Omeprazole 20mg/ngày** uống cùng **Plavix (Clopidogrel)** 2 tuần nay -> Omeprazole ức chế CYP2C19 làm mất tác dụng chống đông của Clopidogrel -> NGUY CƠ TẮC HUYẾT KHỐI TRONG STENT TỬ VONG! [T8, T12].
  - 🚨 **[BÔI ĐỎ BÁO ĐỘNG ĐỎ]:** Đi cầu phân đen như bã cà phê 2 ngày nay + chóng mặt tư thế -> Dấu hiệu **Xuất huyết tiêu hóa trên** do phối hợp thuốc chống đông với thuốc giảm đau NSAID tự mua ngoài tiệm [T8, T10, T12].
- *(Ghi chú phân định người nói K3: Hệ thống loại bỏ hoàn toàn thông tin người nhà kể về mẹ sụt 3 cân, tê bì chân tay tại [T11]).*

### O — OBJECTIVE (THỰC THỂ & CẬN LÂM SÀNG)
- **Sinh hiệu:** Huyết áp 145/88 mmHg, Mạch 84 lần/phút [T13].
- **Khám lâm sàng:** Da niêm mạc nhợt nhẹ, ấn đau tức nhẹ vùng thượng vị, không đề kháng thành bụng [T13].
- **Chỉ định cận lâm sàng cấp cứu:**
  - Nội soi thực quản - dạ dày - tá tràng cấp cứu tìm ổ loét xuất huyết [T14].
  - Công thức máu (kiểm tra tụt HGB/HCT), Đông máu toàn bộ, Điện tâm đồ, Troponin I [T14].

### A — ASSESSMENT (CHẨN ĐOÁN LÂM SÀNG CẤP BÁCH)
- **Chẩn đoán chính:** Xuất huyết tiêu hóa trên nghi do loét dạ dày - tá tràng theo dõi biến chứng dùng thuốc (K92.2).
- **Bệnh kèm theo:** Hậu can thiệp đặt Stent mạch vành (Z95.5) — Cơn đau thắt ngực (I20) — Tăng huyết áp (I10).
- **Đánh giá nguy cơ:** Nguy cơ kép cực kỳ phức tạp: Vừa có nguy cơ chảy máu tiến triển, vừa có nguy cơ huyết khối tắc Stent mạch vành nếu ngưng thuốc chống đông không đúng cách.

### P — PLAN (XỬ TRÍ CẤP CỨU & HIỆU CHỈNH ĐƠN THUỐC)
1. **Xử trí khẩn cấp:**
   - ⛔ **NGƯNG NGAY LẬP TỨC:** Omeprazole 20mg và các thuốc giảm đau khớp không rõ loại [T14].
   - **Nhập viện theo dõi tại khoa Cấp cứu / Tim mạch can thiệp** [T14].
   - **Nội soi dạ dày cấp cứu** can thiệp cầm máu nếu có ổ loét đang rỉ máu [T14].
2. **Hiệu chỉnh dược lý an toàn (CDSS):**
   - Đổi thuốc ức chế bơm proton sang **Pantoprazole 40mg tĩnh mạch** (Pantoprazole không ức chế CYP2C19, an toàn khi dùng cùng Clopidogrel) [T12, T14].
   - Duy trì **Clopidogrel 75mg** dưới sự theo dõi sát của bác sĩ tim mạch và tiêu hóa [T14].
   - Huyết áp: Dùng **Coversyl 5mg** đúng 1 viên sáng, tuyệt đối không tự ý uống gấp đôi liều [T14].`;

const leaflet1 = `# HƯỚNG DẪN CẤP CỨU & CẢNH BÁO NGUY HIỂM TÍNH MẠNG
**Người bệnh:** Bác Đặng Đình Phúc | **Mã hồ sơ:** MT-PHUC-62

---

### 🚨 CẢNH BÁO KHẨN CẤP TỪ BÁC SĨ:
1. **DỪNG NGAY VIÊN DẠ DÀY OMEPRAZOLE:** Thuốc này làm mất tác dụng của thuốc chống đông Plavix, có thể gây đông máu nghẽn tắc Stent tim đột tử!
2. **DỪNG TẤT CẢ THUỐC GIẢM ĐAU KHỚP MÀU HỒNG:** Các thuốc giảm đau tự mua gây viêm loét chảy máu dạ dày dẫn đến tình trạng đi cầu phân đen!

### 🏥 BÁC CẦN NHẬP VIỆN THEO DÕI NGAY HÔM NAY:
- Bác sĩ đã chỉ định làm nội soi dạ dày cấp cứu để kiểm tra và xử lý điểm chảy máu trong bao tử.
- Tuyệt đối không tự ý uống thêm bất kỳ viên thuốc nào khác ngoài y lệnh của bác sĩ tại bệnh viện.`;

const noteMeta1 = {
  content: soap1,
  transcript: transcript1,
  source: "mo_hinh",
  seconds: 38.6,
  needsConfirmCount: 3,
  questions: ["Bác Phúc đợt đặt stent 6 tháng trước là dùng loại Stent phủ thuốc gì?", "Lần gần nhất xét nghiệm công thức máu HGB là bao nhiêu?"],
  propositions: [
    {
      id: 1,
      text: "Bệnh nhân có tiền sử can thiệp đặt Stent mạch vành 6 tháng nay, hiện tức nặng ngực trái âm ỉ.",
      section: "TIỀN SỬ",
      status: "than",
      certainty: "chắc chắn",
      evidenceTurns: [2],
      quotes: ["tôi đặt stent mạch vành được sáu tháng nay rồi. Dạo này ở nhà thấy tức nặng ngực trái âm ỉ"]
    },
    {
      id: 2,
      text: "NHẬN DIỆN THUỐC LASA: Phát âm 'la-xích... pla-vích' -> Gợi ý Plavix (Clopidogrel 75mg).",
      section: "CẦN XÁC NHẬN",
      status: "can_xac_nhan",
      gateReason: "BÔI ĐỎ (Âm vị LASA): Bệnh nhân nói nhầm Lasix (lợi tiểu) sang Plavix (kháng kết tập tiểu cầu). Yêu cầu bác sĩ duyệt đúng Plavix 75mg.",
      drug: "Plavix (Clopidogrel)",
      evidenceTurns: [4],
      quotes: ["viên thuốc chống đông gì tên la-xích... à không, nhớ nhầm, viên pla-vích 75 miligram một viên"]
    },
    {
      id: 3,
      text: "NHẬN DIỆN THUỐC HUYẾT ÁP: Tên thuốc 'co-va-xin / co-ve-xin 5mg' -> Coversyl (Perindopril 5mg).",
      section: "CẦN XÁC NHẬN",
      status: "can_xac_nhan",
      gateReason: "BÔI ĐỎ (Nhận diện chưa chuẩn): Tránh nhầm lẫn giữa Coversyl (đơn chất) và Coveram (phối hợp Amlodipine). Cần bác sĩ xác nhận.",
      drug: "Coversyl 5mg",
      evidenceTurns: [4],
      quotes: ["viên huyết áp tên co-va-xin hay co-ve-xin năm mi-li-gam"]
    },
    {
      id: 4,
      text: "ĐÍNH CHÍNH LIỀU 3 TẦNG: Bệnh nhân tự ý đổi liều thuốc huyết áp từ 1v x 2l -> 0.5v -> 1v x 2l trong 3 ngày qua.",
      section: "TIỀN SỬ THUỐC",
      status: "than",
      evidenceTurns: [6],
      quotes: ["tháng trước tôi đo thấy tụt... bảo giảm còn nửa viên", "ba hôm nay ở nhà đo thấy nó lại vọt lên... tôi tự uống lại một viên sáng một viên tối"]
    },
    {
      id: 5,
      text: "TƯƠNG TÁC THUỐC ĐỘ 1: Bệnh nhân tự ý uống Omeprazole 20mg cùng Plavix gây ức chế men CYP2C19 mất hoạt tính chống đông.",
      section: "CẦN XÁC NHẬN",
      status: "can_xac_nhan",
      gateReason: "BÔI ĐỎ KHẨN CẤP (DDI Black-box): Tương tác Omeprazole + Clopidogrel làm tăng nguy cơ tắc Stent mạch vành đột tử. Bắt buộc đổi sang Pantoprazole.",
      evidenceTurns: [8, 12],
      quotes: ["tôi ra tiệm thuốc tây gần nhà người ta bán cho vỉ ô-mê-pờ-ra-zôn 20 miligram", "Omeprazole bác tự uống sẽ ức chế men gan CYP2C19, làm mất tác dụng chống đông của Plavix"]
    },
    {
      id: 6,
      text: "DẤU HIỆU BÁO ĐỘNG XUẤT HUYẾT: Đi cầu phân đen sệt như bã cà phê 2 ngày nay, chóng mặt tư thế.",
      section: "BỆNH SỬ",
      status: "than",
      certainty: "chắc chắn",
      evidenceTurns: [10],
      quotes: ["hai ngày nay tôi đi cầu thấy phân sẫm màu hẳn, đen sệt như bã cà phê, người thấy hơi chóng mặt lúc đứng dậy"]
    },
    {
      id: 7,
      text: "Xử trí cấp cứu: Dừng ngay Omeprazole và NSAIDs, chỉ định nội soi dạ dày cấp cứu, nhập viện theo dõi tại khoa Tim mạch.",
      section: "ĐIỀU TRỊ",
      status: "than",
      certainty: "chắc chắn",
      evidenceTurns: [14],
      quotes: ["Ngưng ngay lập tức Omeprazole và các thuốc giảm đau khớp tự mua", "Chỉ định nội soi dạ dày thực quản cấp cứu", "nhập viện theo dõi ngay hôm nay"]
    }
  ]
};

const session1 = {
  id: "ca-kho-1-dang-dinh-phuc",
  patientIdentifier: "Đặng Đình Phúc - 62 tuổi",
  patientSubtitle: "Sau đặt Stent · Tương tác Plavix-Omeprazole · Bẫy LASA & Xuất huyết tiêu hóa",
  date: "Hôm nay",
  time: "08:15",
  language: "Tiếng Việt",
  durationSeconds: 260,
  isRecording: false,
  transcript: transcript1,
  activeTabId: "tab-soap",
  tabs: [
    { id: "tab-transcript", title: "Lời thoại ca khám", type: "transcript", content: transcript1, isClosable: false },
    { id: "tab-soap", title: "Bệnh án SOAP (Có căn cứ)", type: "soap", content: soap1, isClosable: false },
    { id: "tab-leaflet", title: "Tờ dặn dò bệnh nhân", type: "leaflet", content: leaflet1, isClosable: true }
  ],
  note: noteMeta1,
  evidenceChat: [
    {
      id: "chat-1-1",
      role: "user",
      content: "Vì sao hệ thống bôi đỏ cả 2 thuốc Plavix và Omeprazole trong ca này?",
      timestamp: "08:20"
    },
    {
      id: "chat-1-2",
      role: "assistant",
      content: "1. Về Plavix: Bệnh nhân phát âm nhầm giữa Lasix (thuốc lợi tiểu quai) và Plavix (thuốc kháng kết tập tiểu cầu Clopidogrel). Đây là cặp thuốc LASA kinh điển trong y khoa. Nếu mô hình AI thông thường đoán bừa sang Lasix thì bệnh nhân sau đặt Stent sẽ bị ngừng thuốc chống đông, dẫn đến huyết khối cấp tắc Stent mạch vành.\n2. Về Omeprazole: Đây là tương tác thuốc nghiêm trọng độ 1 (FDA Black-box Warning). Omeprazole ức chế mạnh isoenzyme CYP2C19 tại gan, ngăn cản chuyển hóa Clopidogrel thành dạng có hoạt tính. Hệ thống CDSS phát hiện ngay tương tác chết người này và bôi đỏ yêu cầu bác sĩ đổi sang Pantoprazole 40mg.",
      timestamp: "08:20"
    }
  ]
};

// ==============================================================================
// CA KHÓ 2: CÔ VŨ THỊ BÍCH THỦY (49 TUỔI)
// ==============================================================================
const transcript2 = `Bác sĩ: Chào cô Thủy, mời cô ngồi. Đợt này cô thấy khó thở nhiều không mà đi khám?
Bệnh nhân: Chào bác sĩ, tôi không phải là không dùng ống xịt thuốc hàng ngày, nhưng cũng không phải ngày nào cũng không thở được; chỉ là độ ba bốn hôm nay thời tiết trở lạnh thì đêm nào cũng lên cơn khó thở rít lên, phải ngồi dậy thở dốc.
Người nhà: Bác sĩ ơi tôi nói thật, mẹ tôi cứ bảo mẹ tôi không khó thở đâu để đỡ tốn tiền đi khám, chứ đêm nào tôi cũng nghe bà ấy thở khò khè như kéo gỗ. Mà khổ lắm, bố tôi thì cứ mắng bảo bà ấy giả vờ, trong khi bố tôi đợt này tự nhiên ăn không ngon, sụt hẳn bốn cân, người cứ mệt mỏi bần thần, đường huyết lên tới mười một chấm năm. Bác sĩ xem bố tôi bị bệnh gì?
Bác sĩ: Chị người nhà trật tự để bác sĩ khám cho mẹ trước. Bác sĩ chỉ khám và kê đơn cho cô Thủy, còn bố chị bị sụt cân và đường huyết cao thì phải đến đăng ký khám chuyên khoa tiểu đường riêng nhé.
Bác sĩ: Cô Thủy cho tôi hỏi, đợt này cô có bị đau nhức xương khớp hay dùng thuốc gì khác không?
Bệnh nhân: Ôi bác sĩ nhắc mới nhớ, cái khớp gối trái của tôi nó thoái hóa sưng đau buốt mấy tuần nay. Hôm trước tôi đau quá định lấy mấy viên thuốc A-xpi-rin với Ai-bu-pờ-rô-phen của con gái uống cho bớt nhức, nhưng chưa dám uống vì nhớ mang máng bác sĩ cũ dặn gì đó. Nay bác sĩ kê cho tôi luôn mấy viên giảm đau sưng khớp đó được không?
Bác sĩ: May quá cô chưa uống! Bác sĩ cảnh báo cô điều này cực kỳ hệ trọng: Cô bị Hen phế quản, TUYỆT ĐỐI CHỐNG CHỈ ĐỊNH các thuốc giảm đau chống viêm nhóm NSAID như Aspirin, Ibuprofen, Diclofenac! Uống vào có thể kích hoạt cơn co thắt phế quản ác tính, suy hô hấp cấp nghẹt thở và nguy cơ tử vong trong vài phút! Giảm đau khớp tôi chỉ kê Paracetamol liều vừa phải kết hợp bôi gel thảo dược tại chỗ.
Bệnh nhân: May quá bác sĩ dặn, tí nữa thì tôi uống liều. À bác sĩ, tôi có bị viêm amidan sốt cao không mà sao nuốt nước bọt thấy vướng?
Bác sĩ: Tôi khám họng: Họng cô chỉ hơi khô đỏ do thở miệng đêm, amidan hoàn toàn không sưng mủ, không có sốt, nhiệt độ 36.8°C. Khám phổi: Nghe có nhiều tiếng rale rít, rale ngáy cả hai phế trường thì thở ra, nhịp thở 24 lần/phút, SpO2 hiện tại là 94% khí trời.
Bác sĩ: Chẩn đoán: Cơn hen phế quản mức độ trung bình trên nền Hen phế quản bậc 3 chưa kiểm soát tốt, Thoái hóa khớp gối.
Bác sĩ: Phác đồ điều trị: Nâng bậc kiểm soát hen: Symbicort (Budesonide/Formoterol 160/4.5mcg) hít 2 nhát x 2 lần/ngày sáng tối, dùng đều đặn hàng ngày; Kèm Ventolin xịt cắt cơn khi có khó thở cấp. Khớp gối dùng Paracetamol 500mg uống khi đau nhiều, tối đa 3 viên/ngày.
Bác sĩ: Lời dặn dò cấp cứu: Nếu nửa đêm lên cơn khó thở cấp, xịt ngay 2 nhát cắt cơn Ventolin. Sau 20 phút nếu vẫn khó thở thì xịt nhắc lại 2 nhát và gọi ngay xe cấp cứu 115 đến bệnh viện; tuyệt đối nếu thấy đầu ngón tay tím tái hoặc nói không thành câu thì không được chần chừ ở nhà chờ đến sáng! Hẹn cô tái khám sau 10 ngày.`;

const soap2 = `# BỆNH ÁN LÂM SÀNG (SOAP) — MEDITRACE SENTINEL (CHỐNG CHỈ ĐỊNH ACUTE)
**Bệnh nhân:** Vũ Thị Bích Thủy | **Tuổi:** 49 | **Giới:** Nữ
**Ngày khám:** Hôm nay | **Bác sĩ phụ trách:** BS. Quan Nguyen

---

### S — SUBJECTIVE (BỆNH SỬ & BẪY PHỦ ĐỊNH KÉP)
- **Lý do khám:** Khó thở về đêm tăng dần khi trời lạnh 3-4 ngày nay [T2].
- **Bệnh sử (Phân tích phủ định kép K4):**
  - Bệnh nhân dùng ống hít duy trì nhưng không đều; 3-4 hôm nay khó thở rít về đêm, phải ngồi dậy để thở [T2].
  - *(Giải mã phủ định kép: 'không phải là không dùng... không phải ngày nào cũng không thở được' -> Bệnh nhân tuân thủ điều trị kém, bệnh chưa được kiểm soát tốt [T2]).*
- **Bẫy người nhà lẫn lộn đại từ (K3 Guardrail):**
  - 🛡️ **[ĐÃ LỌC BỎ — BƯỚC K3]:** Người nhà tại lượt [T3] khai *"bố sụt 4 cân, đường huyết 11.5 mmol/L"*. Hệ thống nhận diện đại từ chỉ người khác ("bố tôi"), KHÔNG ghi các triệu chứng này vào bệnh án của cô Thủy.
- **Báo động chống chỉ định thuốc tử vong:**
  - 🚨 **[BÔI ĐỎ KHẨN CẤP — CHỐNG CHỈ ĐỊNH TUYỆT ĐỐI]:** Bệnh nhân xin kê **Aspirin / Ibuprofen** để trị đau khớp gối [T6]. Kích hoạt quy tắc an toàn: Chống chỉ định tuyệt đối nhóm NSAID ở bệnh nhân Hen phế quản (Hội chứng Widal / Co thắt phế quản ác tính gây tử vong do ức chế tổng hợp Prostaglandin PGE2) [T7].

### O — OBJECTIVE (THỰC THỂ LÂM SÀNG)
- **Sinh hiệu:** SpO2 94% khí trời, Nhịp thở 24 lần/phút, Nhiệt độ 36.8°C [T9].
- **Khám họng:** Họng khô đỏ nhẹ do thở miệng, amidan không sưng mủ, không sốt [T9].
- **Khám hô hấp:** Lồng ngực di động theo nhịp thở, nghe rale rít, rale ngáy lan tỏa 2 phế trường thì thở ra [T9].
- **Khám cơ xương khớp:** Khớp gối trái sưng nhẹ, hạn chế vận động nhẹ khi gấp duỗi [T6].

### A — ASSESSMENT (CHẨN ĐOÁN LÂM SÀNG)
- **Chẩn đoán chính:** Cơn hen phế quản mức độ trung bình (J45.901).
- **Bệnh nền:** Hen phế quản bậc 3 chưa kiểm soát (J45.4) — Thoái hóa khớp gối (M17).
- **Cảnh báo nguy cơ:** Nguy cơ bùng phát cơn hen ác tính nếu bệnh nhân tự ý dùng NSAID giảm đau khớp ngoài chỉ định.

### P — PLAN (ĐIỀU TRỊ NÂNG BẬC & HƯỚNG DẪN CẤP CỨU)
1. **Phác đồ kiểm soát hen nâng bậc:**
   - **Symbicort 160/4.5mcg (Budesonide/Formoterol):** Hít 2 nhát x 2 lần/ngày (sáng 2 nhát, tối 2 nhát) đều đặn hàng ngày, súc miệng sau hít [T11].
   - **Ventolin 100mcg (Salbutamol):** Xịt 2 nhát khi có cơn khó thở cấp [T11].
2. **Xử trí đau khớp an toàn:**
   - 🚫 **CẤM:** Aspirin, Ibuprofen, Diclofenac, Naproxen, Meloxicam [T7].
   - Dùng **Paracetamol 500mg** 1 viên khi đau nhiều (tối đa 3 viên/ngày) + chườm ấm [T7, T11].
3. **Kế hoạch xử trí cấp cứu tại nhà (Lọc câu giả định tương lai K4):**
   - Nếu nửa đêm lên cơn khó thở: Xịt 2 nhát Ventolin -> sau 20 phút không đỡ xịt thêm 2 nhát và gọi ngay 115 [T12].
   - Nếu tím tái đầu chi hoặc nói ngắt quãng từng từ -> Đến viện cấp cứu ngay lập tức [T12].`;

const leaflet2 = `# BẢNG HƯỚNG DẪN DÙNG THUỐC & CẢNH BÁO TỬ VONG CHO BỆNH NHÂN HEN
**Người bệnh:** Cô Vũ Thị Bích Thủy | **Chẩn đoán:** Hen phế quản bậc 3

---

### ⛔ CẢNH BÁO NGUY HIỂM TÍNH MẠNG — TUYỆT ĐỐI CẤM UỐNG:
- **CẤM TUYỆT ĐỐI:** **Aspirin, Ibuprofen, Alaxan, Voltaren, Diclofenac** và các thuốc giảm đau khớp sủi bọt/viên con nhộng không rõ tên.
- **Lý do:** Những thuốc này làm co thắt đường thở dữ dội, gây nghẹt thở suy hô hấp cấp cứu không kịp!
- **Đau khớp chỉ uống:** Paracetamol 500mg (khi đau nhiều, tối đa 3 viên/ngày).

### ⏰ LỊCH DÙNG THUỐC HÀNG NGÀY:
- **SÁNG (08:00):** Hít 2 nhát **Symbicort** -> Súc miệng nhổ nước đi.
- **TỐI (20:00):** Hít 2 nhát **Symbicort** -> Súc miệng nhổ nước đi.
- **KHI LÊN CƠN KHÓ THỞ:** Xịt 2 nhát **Ventolin** (bình màu xanh).

### 🚨 GỌI CẤP CỨU 115 NGAY NẾU:
- Đã xịt 4 nhát Ventolin mà vẫn không thở được.
- Đầu ngón tay hoặc môi tím tái, khó thở đến mức không nói trọn được một câu.`;

const noteMeta2 = {
  content: soap2,
  transcript: transcript2,
  source: "mo_hinh",
  seconds: 34.2,
  needsConfirmCount: 2,
  questions: ["Bệnh nhân Thủy đã từng đo chức năng thông khí phổi (Hô hấp ký) trước đây chưa?"],
  propositions: [
    {
      id: 1,
      text: "Bệnh nhân có triệu chứng khó thở rít về đêm 3-4 ngày nay khi trời lạnh, phải ngồi dậy để thở.",
      section: "BỆNH SỬ",
      status: "than",
      certainty: "chắc chắn",
      evidenceTurns: [2],
      quotes: ["độ ba bốn hôm nay thời tiết trở lạnh thì đêm nào cũng lên cơn khó thở rít lên, phải ngồi dậy thở dốc"]
    },
    {
      id: 2,
      text: "LỌC BỎ THÔNG TIN NGƯỜI NHÀ (K3): Triệu chứng sụt 4 cân, đường huyết 11.5 là của bố bệnh nhân, không ghi vào hồ sơ.",
      section: "PHÂN BIỆT NGƯỜI NÓI",
      status: "than",
      certainty: "chắc chắn",
      evidenceTurns: [3, 4],
      quotes: ["bố tôi đợt này tự nhiên ăn không ngon, sụt hẳn bốn cân... đường huyết lên tới mười một chấm năm"]
    },
    {
      id: 3,
      text: "CẢNH BÁO CHỐNG CHỈ ĐỊNH TỬ VONG: Bệnh nhân hen phế quản xin kê Aspirin / Ibuprofen giảm đau khớp.",
      section: "CẦN XÁC NHẬN",
      status: "can_xac_nhan",
      gateReason: "BÔI ĐỎ KHẨN CẤP (Chống chỉ định tử vong): NSAID / Aspirin gây co thắt phế quản ác tính (Hội chứng Widal) ở bệnh nhân hen. Bác sĩ bắt buộc từ chối kê đơn.",
      drug: "Aspirin, Ibuprofen",
      evidenceTurns: [6, 7],
      quotes: ["định lấy mấy viên thuốc A-xpi-rin với Ai-bu-pờ-rô-phen của con gái uống", "TUYỆT ĐỐI CHỐNG CHỈ ĐỊNH các thuốc giảm đau chống viêm nhóm NSAID"]
    },
    {
      id: 4,
      text: "Khám lâm sàng: SpO2 94%, thở 24 l/p, phổi có nhiều rale rít rale ngáy 2 phế trường, họng không sốt không mủ.",
      section: "KHÁM LÂM SÀNG",
      status: "than",
      certainty: "chắc chắn",
      evidenceTurns: [9],
      quotes: ["Nhiệt độ 36.8°C", "Nghe có nhiều tiếng rale rít, rale ngáy cả hai phế trường thì thở ra, nhịp thở 24 lần/phút, SpO2 hiện tại là 94%"]
    },
    {
      id: 5,
      text: "Điều trị: Nâng bậc kiểm soát Symbicort 160/4.5 hít 2 nhát x 2 lần/ngày, Ventolin cắt cơn, Paracetamol giảm đau khớp.",
      section: "ĐIỀU TRỊ",
      status: "than",
      certainty: "chắc chắn",
      evidenceTurns: [11],
      quotes: ["Symbicort (Budesonide/Formoterol 160/4.5mcg) hít 2 nhát x 2 lần/ngày", "Ventolin xịt cắt cơn", "Paracetamol 500mg uống khi đau nhiều"]
    },
    {
      id: 6,
      text: "Kế hoạch cấp cứu (Lọc câu tương lai K4): Nếu tím tái hoặc khó thở không đỡ sau 4 nhát xịt thì gọi 115.",
      section: "KẾ HOẠCH",
      status: "than",
      situation: "tương lai / cấp cứu",
      evidenceTurns: [12],
      quotes: ["Sau 20 phút nếu vẫn khó thở thì xịt nhắc lại 2 nhát và gọi ngay xe cấp cứu 115", "nếu thấy đầu ngón tay tím tái hoặc nói không thành câu thì không được chần chừ"]
    }
  ]
};

const session2 = {
  id: "ca-kho-2-vu-thi-bich-thuy",
  patientIdentifier: "Vũ Thị Bích Thủy - 49 tuổi",
  patientSubtitle: "Hen phế quản bậc 3 · Bẫy đại từ người nhà · Chống chỉ định Aspirin/NSAID & Phủ định kép",
  date: "Hôm nay",
  time: "09:00",
  language: "Tiếng Việt",
  durationSeconds: 240,
  isRecording: false,
  transcript: transcript2,
  activeTabId: "tab-soap",
  tabs: [
    { id: "tab-transcript", title: "Lời thoại ca khám", type: "transcript", content: transcript2, isClosable: false },
    { id: "tab-soap", title: "Bệnh án SOAP (Có căn cứ)", type: "soap", content: soap2, isClosable: false },
    { id: "tab-leaflet", title: "Tờ dặn dò bệnh nhân", type: "leaflet", content: leaflet2, isClosable: true }
  ],
  note: noteMeta2,
  evidenceChat: [
    {
      id: "chat-2-1",
      role: "user",
      content: "Làm thế nào hệ thống không bị nhầm các triệu chứng 'sụt 4 cân' và 'đường huyết 11.5' của người nhà vào bệnh nhân?",
      timestamp: "09:05"
    },
    {
      id: "chat-2-2",
      role: "assistant",
      content: "Ở lượt thoại [T3], người nhà dùng liên tiếp các đại từ chỉ nhiều đối tượng: 'mẹ tôi', 'bà ấy', 'bố tôi'. Nhờ bước K3 (Speaker & Subject Attribution), hệ thống phân tích cây cú pháp đại từ quan hệ và phát hiện thực thể 'sụt 4 cân' và 'đường huyết 11.5' thuộc về chủ thể 'bố tôi' chứ không phải 'cô Thủy'. Hệ thống chủ động loại bỏ thông tin này, không cho phép đưa vào bệnh án SOAP của bệnh nhân.",
      timestamp: "09:05"
    }
  ]
};

// ==============================================================================
// CA KHÓ 3: CỤ BÙI VĂN THÀNH (72 TUỔI)
// ==============================================================================
const transcript3 = `Bác sĩ: Chào cụ Thành, mời cụ ngồi. Hôm nay cụ thấy người mệt thế nào mà người nhà đưa đi khám?
Bệnh nhân: Chào bác sĩ, tôi bị bệnh phổi tắc nghẽn với suy tim mấy năm nay. Dạo này khó thở tăng dần, đêm không nằm đầu bằng được, phải kê ba cái gối mới chợp mắt được một lúc. Hai cái chân bữa nay nặng trịch, ấn vô thấy lún một lỗ sâu hoắm cả buổi không đàn hồi.
Bác sĩ: Cụ có theo dõi huyết áp và cân nặng ở nhà không?
Bệnh nhân: Bữa sớm đo ở trạm y tế xã họ bảo mười sáu chín, còn cân nặng thì tự nhiên tuần này tăng vọt lên hai cân rưỡi dù ăn uống ít đi.
Bác sĩ: Cụ có bị sốt hay ho khạc đờm đặc đờm đổi màu không?
Bệnh nhân: Tôi không thấy sốt đâu... à mà hình như tối qua có rét run đắp hai cái chăn bông, con nó cặp nhiệt độ thấy gần ba mươi chín độ, sáng nay lại thấy bình thường. Đờm thì khạc ra cục đờm màu vàng xanh quánh đặc, khó khạc lắm.
Bác sĩ: Về vấn đề đi tiểu tiện của cụ dạo này thế nào? Cụ có tiền sử phì đại tiền liệt tuyến đúng không?
Bệnh nhân: Đúng rồi bác sĩ, dạo này đêm đi tiểu lắt nhắt năm bảy cữ mà rặn mãi mới ra được tí nước tiểu, rặn buốt rát. Mấy hôm nay tôi bị ngứa dị ứng với sổ mũi, ra hiệu thuốc tư họ bán cho mấy viên thuốc màu vàng tên là Cờ-lo-phe-ni-ra-min bảo uống cho khỏi ngứa và sổ mũi, tôi uống ngày hai viên được ba ngày nay rồi.
Bác sĩ: Bác sĩ yêu cầu cụ NGƯNG NGAY viên Clorpheniramin đó! Cụ bị phì đại tuyến tiền liệt, thuốc Clorpheniramin là kháng Histamin thế hệ 1 có tác dụng phụ kháng cholinergic cực mạnh, làm liệt cơ bàng quang và co thắt cổ bàng quang, uống vào là dẫn thẳng đến BÍ TIỂU CẤP phải đặt ống thông tiểu khẩn cấp! Chưa kể thuốc này làm quánh đặc dịch đờm phế quản, khiến đờm ứ đọng làm cụ khó thở nghẹt đờm nặng thêm trên nền COPD!
Bác sĩ: Khám lâm sàng: Bệnh nhân thở co kéo hõm ức, SpO2 89% khí trời (cần thở oxy kính 2 lít/phút ngay). Huyết áp 160/90 mmHg (khớp với số liệu mười sáu chín trạm y tế đo), nhịp tim nhanh 105 lần/phút, tĩnh mạch cổ nổi 45 độ, phù mềm ấn lõm hai chi dưới. Khám bụng có cầu bàng quang trên xương mu căng nhẹ. Phổi nhiều rale ẩm đáy phổi và rale ngáy rải rác.
Bác sĩ: Chẩn đoán: Đợt cấp Bệnh phổi tắc nghẽn mạn tính (COPD) nghi bội nhiễm / Đợt mất bù suy tim mạn (NYHA III) — Bí tiểu không hoàn toàn do tác dụng phụ Clorpheniramin trên nền U xơ phì đại tiền liệt tuyến (BPH) — Tăng huyết áp.
Bác sĩ: Xử trí khẩn cấp: 1. Thở oxy gọng kính 2 lít/phút duy trì SpO2 90-92%. 2. Khí dung Ventolin 2.5mg + Pulmicort 0.5mg. 3. Tiêm tĩnh mạch Furosemid 20mg 1 ống để rút bớt dịch ứ trệ phù suy tim. 4. Dừng ngay Clorpheniramin; theo dõi sát lượng nước tiểu, nếu sau 2 giờ không tự tiểu được thì đặt sonde tiểu ngắt quãng. 5. Kháng sinh Levofloxacin 500mg/ngày. Chuyển ngay vào khoa Hồi sức cấp cứu để theo dõi liên tục.`;

const soap3 = `# BỆNH ÁN LÂM SÀNG (SOAP) — MEDITRACE SENTINEL (ĐA BỆNH LÝ & BẪY MÂU THUẪN)
**Bệnh nhân:** Bùi Văn Thành | **Tuổi:** 72 | **Giới:** Nam
**Ngày khám:** Hôm nay | **Bác sĩ phụ trách:** BS. Quan Nguyen

---

### S — SUBJECTIVE (BỆNH SỬ & SỐ LIỆU ĐỊA PHƯƠNG)
- **Lý do khám:** Kh khó thở tăng dần, khó thở khi nằm phẳng (phải kê 3 gối), phù 2 chân, tiểu rắt buốt [T2, T8].
- **Số liệu lâm sàng tiếng lóng địa phương (K6):**
  - Huyết áp trạm y tế xã đo: "mười sáu chín" -> **160/90 mmHg** [T4].
  - Cân nặng tăng vọt "hai cân rưỡi" trong 1 tuần -> **Tăng 2.5 kg do ứ dịch suy tim mất bù** [T4].
  - Chân "ấn vô lún một lỗ sâu hoắm" -> **Phù mềm ấn lõm độ 3** hai chi dưới [T2].
- **Mâu thuẫn lâm sàng nội tại (Self-Contradiction Gate):**
  - ⚠️ **[BÔI ĐỎ — CẦN BÁC SĨ THẨM ĐỊNH LẠI]:** Bệnh nhân câu trước nói *"Tôi không thấy sốt đâu"*, ngay câu sau khai *"tối qua rét run đắp hai chăn, cặp nhiệt độ gần ba chín độ"* [T6]. Khạc đờm vàng xanh quánh đặc -> Dấu hiệu đợt cấp bội nhiễm.
- **Báo động tác dụng phụ gây Bí tiểu cấp:**
  - 🚨 **[BÔI ĐỎ KHẨN CẤP — TÁC DỤNG PHỤ KHÁNG CHOLINERGIC]:** Tự mua uống **Clorpheniramin (Chlorpheniramine)** 2 viên/ngày trị ngứa sổ mũi [T8]. Thuốc kháng Histamin H1 thế hệ 1 có hoạt tính kháng Cholinergic mạnh -> Gây liệt cơ bàng quang dẫn đến **Bí tiểu cấp / Cầu bàng quang căng** trên nền U xơ tiền liệt tuyến (BPH), đồng thời làm đặc đờm gây bít tắc đường thở COPD! [T8, T9].

### O — OBJECTIVE (THỰC THỂ & DẤU HIỆU CẤP CỨU)
- **Sinh hiệu cấp cứu:** SpO2 tụt còn **89% khí trời** (suy hô hấp), Nhịp thở 28 l/p co kéo hõm ức, Nhịp tim nhanh 105 l/p, Huyết áp 160/90 mmHg [T10].
- **Khám tim mạch & Phù:** Tĩnh mạch cổ nổi 45 độ, phù mềm ấn lõm 2 cẳng bàn chân rõ [T10].
- **Khám hô hấp:** Phổi nhiều rale ngáy, rale rít rải rác và rale ẩm đáy phổi 2 bên [T10].
- **Khám tiết niệu:** Bụng dưới có **Cầu bàng quang căng nhẹ** trên xương mu [T10].

### A — ASSESSMENT (CHẨN ĐOÁN PHỨC TẠP ĐA BỆNH LÝ)
- **Chẩn đoán đợt cấp:** Đợt cấp Bệnh phổi tắc nghẽn mạn tính (COPD) mức độ nặng có suy hô hấp (J44.1).
- **Hội chứng đi kèm:** Đợt mất bù cấp suy tim mạn phân suất tống máu giảm (I50.9) — Bí tiểu không hoàn toàn do tác dụng phụ Clorpheniramin trên nền U xơ phì đại tiền liệt tuyến (N40.1) — Tăng huyết áp độ 2 (I10).
- **Phân loại độ nặng:** Bệnh nhân rơi vào tình trạng cấp cứu hô hấp - tuần hoàn kết hợp, nguy cơ bí tiểu hoàn toàn vỡ bàng quang nếu không xử trí rút thuốc kịp thời.

### P — PLAN (XỬ TRÍ CẤP CỨU TẠI CHỖ & CHUYỂN HỒI SỨC)
1. **Can thiệp suy hô hấp & Suy tim ứ huyết:**
   - Thở oxy gọng kính 2 lít/phút (duy trì mục tiêu SpO2 88-92% ở bệnh nhân COPD) [T12].
   - Khí dung giãn phế quản: Ventolin 2.5mg + Pulmicort 0.5mg [T12].
   - Tiêm tĩnh mạch Furosemid 20mg (1 ống) rút bớt dịch phù [T12].
2. **Xử trí bí tiểu cấp:**
   - ⛔ **CẤM DÙNG:** Ngưng ngay lập tức Clorpheniramin [T9, T12].
   - Theo dõi lượng nước tiểu trong 2 giờ; nếu không tiểu được -> Đặt sonde tiểu ngắt quãng giải áp bàng quang [T12].
3. **Điều trị nhiễm khuẩn & Nhập viện:**
   - Kháng sinh Levofloxacin 500mg/ngày [T12].
   - Chuyển khoa Cấp cứu / Hồi sức tích cực (ICU) theo dõi liên tục [T12].`;

const leaflet3 = `# HƯỚNG DẪN XỬ TRÍ CẤP CỨU & CẢNH BÁO THUỐC BÍ TIỂU
**Người bệnh:** Cụ Bùi Văn Thành | **Mã hồ sơ:** MT-THANH-72

---

### 🚨 CẢNH BÁO KHẨN CẤP — NGUY CƠ BÍ TIỂU & NGHẸT THỞ:
1. **DỪNG NGAY THUỐC SỔ MŨI / DỊ ỨNG MÀU VÀNG (CLORPHENIRAMIN):**
   - Cụ bị phì đại tiền liệt tuyến, uống thuốc này làm liệt bàng quang không đi tiểu được, gây vỡ bàng quang!
   - Thuốc này còn làm đờm trong phổi đặc quánh lại, làm cụ nghẹt thở không khạc đờm ra được!

### 🏥 BỆNH NHÂN ĐANG ĐƯỢC CHUYỂN CẤP CỨU:
- Đang được thở oxy và tiêm thuốc rút nước phù ở tim và phổi.
- Nhân viên y tế sẽ theo dõi việc đi tiểu, nếu không tự tiểu được sẽ hỗ trợ đặt ống thông tiểu nhẹ nhàng.`;

const noteMeta3 = {
  content: soap3,
  transcript: transcript3,
  source: "mo_hinh",
  seconds: 41.3,
  needsConfirmCount: 3,
  questions: ["Cụ Thành trước đây đã từng bị bí tiểu phải đặt ống thông tiểu lần nào chưa?", "Chỉ số PSA tiền liệt tuyến gần nhất là bao nhiêu?"],
  propositions: [
    {
      id: 1,
      text: "Khó thở tăng dần khi nằm phẳng (phải kê 3 gối), phù 2 chân ấn lõm sâu hoắm, tăng 2.5kg trong 1 tuần.",
      section: "BỆNH SỬ",
      status: "than",
      certainty: "chắc chắn",
      evidenceTurns: [2, 4],
      quotes: ["khó thở tăng dần, đêm không nằm đầu bằng được, phải kê ba cái gối", "chân bữa nay nặng trịch, ấn vô thấy lún một lỗ sâu hoắm", "cân nặng thì tự nhiên tuần này tăng vọt lên hai cân rưỡi"]
    },
    {
      id: 2,
      text: "SỐ LIỆU ĐỊA PHƯƠNG K6: 'Mười sáu chín' giải mã thành Huyết áp 160/90 mmHg.",
      section: "CẬN LÂM SÀNG",
      status: "than",
      certainty: "chắc chắn",
      evidenceTurns: [4, 10],
      quotes: ["Bữa sớm đo ở trạm y tế xã họ bảo mười sáu chín", "Huyết áp 160/90 mmHg (khớp với số liệu mười sáu chín trạm y tế đo)"]
    },
    {
      id: 3,
      text: "MÂU THUẪN NỘI TẠI: Bệnh nhân câu trước nói 'không sốt', câu sau khai 'rét run đắp 2 chăn, cặp nhiệt độ gần 39 độ'.",
      section: "CẦN XÁC NHẬN",
      status: "can_xac_nhan",
      gateReason: "BÔI ĐỎ MÂU THUẪN: Bệnh nhân tự mâu thuẫn về triệu chứng sốt. Cần bác sĩ thẩm định lại thân nhiệt thực tế.",
      evidenceTurns: [6],
      quotes: ["Tôi không thấy sốt đâu... à mà hình như tối qua có rét run đắp hai cái chăn bông, con nó cặp nhiệt độ thấy gần ba mươi chín độ"]
    },
    {
      id: 4,
      text: "TÁC DỤNG PHỤ NGUY HIỂM: Uống Clorpheniramin gây bí tiểu cấp trên nền phì đại tiền liệt tuyến và làm đặc đờm COPD.",
      section: "CẦN XÁC NHẬN",
      status: "can_xac_nhan",
      gateReason: "BÔI ĐỎ KHẨN CẤP: Kháng Histamin H1 thế hệ 1 (Clorpheniramin) gây tác dụng phụ kháng cholinergic làm liệt bàng quang ở bệnh nhân BPH. Yêu cầu ngưng ngay lập tức.",
      drug: "Clorpheniramin",
      evidenceTurns: [8, 9],
      quotes: ["mấy viên thuốc màu vàng tên là Cờ-lo-phe-ni-ra-min bảo uống cho khỏi ngứa và sổ mũi", "thuốc Clorpheniramin là kháng Histamin thế hệ 1 có tác dụng phụ kháng cholinergic cực mạnh, làm liệt cơ bàng quang... dẫn thẳng đến BÍ TIỂU CẤP"]
    },
    {
      id: 5,
      text: "Khám lâm sàng cấp cứu: SpO2 89%, thở co kéo 28 l/p, tim 105 l/p, tĩnh mạch cổ nổi, có cầu bàng quang căng nhẹ.",
      section: "KHÁM LÂM SÀNG",
      status: "than",
      certainty: "chắc chắn",
      evidenceTurns: [10],
      quotes: ["Bệnh nhân thở co kéo hõm ức, SpO2 89% khí trời", "tĩnh mạch cổ nổi 45 độ, phù mềm ấn lõm", "Khám bụng có cầu bàng quang trên xương mu căng nhẹ"]
    },
    {
      id: 6,
      text: "Xử trí khẩn: Thở oxy kính 2 l/p (SpO2 90-92%), khí dung Ventolin + Pulmicort, tiêm tĩnh mạch Furosemid 20mg, ngưng Clorpheniramin, chuyển Hồi sức cấp cứu.",
      section: "ĐIỀU TRỊ",
      status: "than",
      certainty: "chắc chắn",
      evidenceTurns: [12],
      quotes: ["Thở oxy gọng kính 2 lít/phút", "Khí dung Ventolin 2.5mg + Pulmicort 0.5mg", "Tiêm tĩnh mạch Furosemid 20mg 1 ống", "Chuyển ngay vào khoa Hồi sức cấp cứu"]
    }
  ]
};

const session3 = {
  id: "ca-kho-3-bui-van-thanh",
  patientIdentifier: "Bùi Văn Thành - 72 tuổi",
  patientSubtitle: "COPD nhóm E · Suy tim EF giảm · Phì đại tiền liệt tuyến & Bẫy bí tiểu do Clorpheniramin",
  date: "Hôm nay",
  time: "09:45",
  language: "Tiếng Việt",
  durationSeconds: 270,
  isRecording: false,
  transcript: transcript3,
  activeTabId: "tab-soap",
  tabs: [
    { id: "tab-transcript", title: "Lời thoại ca khám", type: "transcript", content: transcript3, isClosable: false },
    { id: "tab-soap", title: "Bệnh án SOAP (Có căn cứ)", type: "soap", content: soap3, isClosable: false },
    { id: "tab-leaflet", title: "Tờ dặn dò bệnh nhân", type: "leaflet", content: leaflet3, isClosable: true }
  ],
  note: noteMeta3,
  evidenceChat: [
    {
      id: "chat-3-1",
      role: "user",
      content: "Giải thích cơ chế hệ thống phát hiện tác dụng phụ kháng cholinergic của Clorpheniramin?",
      timestamp: "09:50"
    },
    {
      id: "chat-3-2",
      role: "assistant",
      content: "Clorpheniramin là thuốc kháng histamin H1 thế hệ 1 có hoạt tính kháng thụ thể muscarinic (anticholinergic) mạnh. Khi dùng trên bệnh nhân phì đại tiền liệt tuyến (BPH), thuốc gây giãn cơ chóp bàng quang và co thắt cơ vòng cổ bàng quang, dẫn đến ứ đọng nước tiểu cấp tính (cầu bàng quang căng trên lâm sàng). Đồng thời, tác dụng kháng cholinergic làm giảm tiết dịch phế quản, khiến đờm đặc quánh gây tắc nghẽn thông khí nghiêm trọng ở bệnh nhân COPD. Hệ thống CDSS kích hoạt cảnh báo bôi đỏ để bác sĩ can thiệp ngưng thuốc và giải áp bàng quang kịp thời.",
      timestamp: "09:50"
    }
  ]
};

// ==============================================================================
// GHI VÀO CƠ SỞ DỮ LIỆU SQLITE CHO CẢ 2 TÀI KHOẢN (UID 1 & UID 2)
// ==============================================================================
console.log("Bat dau ghi 3 ca mau do kho cao vao co so du lieu SQLite...");

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

    // Set luu_luc cuc ky cao de dam bao trinh duyet uu tien nap tu server
    db.prepare(`
      INSERT INTO moc_luu (nguoi_dung_id, kho, luu_luc)
      VALUES (?, 'ca-kham', ?)
      ON CONFLICT (nguoi_dung_id, kho) DO UPDATE SET luu_luc = ?
    `).run(u, now + 100000000, now + 100000000);
    console.log(`[+] Da ghi 3 ca mau do kho cao cho UID ${u}`);
  }

  db.exec("COMMIT");
  console.log("✅ HOAN TAT: Da nap 3 ca mau do kho cao thanh cong vao SQLite!");
} catch (err) {
  db.exec("ROLLBACK");
  console.error("[-] Loi khi nap ca:", err);
}
