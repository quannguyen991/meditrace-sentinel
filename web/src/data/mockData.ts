import { Session, ClinicalChatMessage, TemplateItem, Patient, ClinicalTask } from "../types";

/**
 * Phien khoi tao: MOT ca TRONG.
 *
 * Ban do AI Studio dung san co hai ca kham viet san (bong gan co chan, cum sot) kem gio
 * gio phut va ma luot thoai. Da bo: nguoi xem demo khong phan biet duoc ca viet san voi
 * ca may vua chay. Muon co du lieu de xem thi bam "Nap mot ca da chay truoc" o tab Loi
 * thoai — ca do lay tu bo du lieu tong hop cua du an va co nhan nguon ro rang.
 */
export const initialSessions: Session[] = [
  {
    id: "session-moi",
    patientIdentifier: "Thêm tên định danh bệnh nhân",
    patientSubtitle: "Ca khám mới",
    date: "Hôm nay",
    time: "",
    language: "Tiếng Việt",
    durationSeconds: 0,
    isRecording: false,
    transcript: "",
    activeTabId: "tab-transcript",
    tabs: [
      { id: "tab-transcript", title: "Lời thoại ca khám", type: "transcript", content: "", isClosable: false },
      { id: "tab-context", title: "Ngữ cảnh", type: "context", content: "", isClosable: false },
    ],
  },
];

export const initialEvidenceChat: ClinicalChatMessage[] = [
  {
    id: "msg-1",
    role: "user",
    content: "Dựa trên cuộc thăm khám từ đầu đến giờ, tôi nên hỏi thêm bệnh nhân những câu hỏi lâm sàng nào?",
    timestamp: "10:24",
  },
  {
    id: "msg-2",
    role: "assistant",
    thoughtTime: "1s",
    sourcesCount: 13,
    timestamp: "10:24",
    content: `Dựa trên diễn biến thăm khám lâm sàng hiện tại, dưới đây là các câu hỏi mục tiêu giúp làm rõ bệnh sử, định hướng chẩn đoán và phác đồ điều trị:

### 1. Làm rõ cơ chế chấn thương
- **Bàn chân tiếp đất như thế nào / lật theo hướng nào?** (Lật sáp trong là điển hình của bong gân ngoài; lật ngoài hoặc gập mu chân gợi ý tổn thương dây chằng chày mác dưới, thời gian lành lâu hơn) [Hiệp hội Bác sĩ Gia đình Hoa Kỳ (AAFP)]
- **Khớp gối có bị vặn xoắn hoặc nghe tiếng động lạ ở cẳng chân không?** (Loại trừ gãy Maisonneuve – gãy đoạn gần xương mác kèm rách màng gian cốt) [Medscape Reference]

### 2. Tiêu chuẩn Ottawa / Đánh giá khả năng tỳ đè
- **Bệnh nhân có thể đi được 4 bước liên tục ngay sau chấn thương không?** (Tiêu chuẩn Ottawa dương tính bắt buộc chụp X-quang loại trừ gãy xương) [Pediatric Education]
- **Hiện tại ở phòng khám bệnh nhân có tự bước được 4 bước không?** (Đánh giá lại tại thời điểm khám) [Pediatric Education]

### 3. Sàng lọc tổn thương mạch máu & thần kinh phối hợp
- **Có cảm giác tê bì, kim châm hoặc đầu ngón chân lạnh, nhợt nhạt không?** (Kiểm tra thần kinh - mạch máu loại trừ tổn thương thần kinh mác) [PubMed Central (PMC)]
- **Có cảm giác đứt giật ở vùng gót chân phía sau không?** (Sàng lọc đứt gân gót Achilles / làm nghiệm pháp Thompson) [AAFP]

### 4. Đánh giá chức năng & công việc
- **Nhu cầu chơi thể thao / vận động cường độ cao?** (Định hướng phục hồi chức năng và lựa chọn nẹp cổ chân) [PubMed Central (PMC)]
- **Mức độ đau hiện tại theo thang điểm VAS (0-10), ảnh hưởng thế nào đến giấc ngủ và đi lại?**
- **Nghề nghiệp có đòi hỏi đứng nhiều, lái xe hay giữ thăng bằng không?**`,
    safetyNotes: [
      "Kiểm tra cụ thể khả năng chịu lực 4 bước ngay sau chấn thương và tại phòng khám — tiêu chuẩn Ottawa dương tính bắt buộc chụp X-quang [Pediatric Education]",
      "Hỏi về điểm đau đoạn gần xương cẳng chân và cơ chế vặn xoắn — cảnh giác gãy Maisonneuve cần xử trí chuyên khoa [Medscape Reference]",
      "Hỏi về tiền sử lật cổ chân trước đây — nguy cơ tái phát từ 12–47% và dễ dẫn đến mất vững cổ chân mạn tính [EJCRIM]",
    ],
    sources: [
      { name: "Hiệp hội Bác sĩ Gia đình Hoa Kỳ (AAFP)", domain: "aafp.org" },
      { name: "Medscape Reference (Medscape)", domain: "medscape.com" },
      { name: "Pediatric Education Guidelines", domain: "pediatriceducation.org" },
      { name: "PubMed Central (PMC)", domain: "ncbi.nlm.nih.gov" },
      { name: "European Journal of Case Reports (EJCRIM)", domain: "ejcrim.com" },
      { name: "UpToDate Clinical Guidelines", domain: "uptodate.com" },
      { name: "Tổ chức Y tế Thế giới (WHO)", domain: "who.int" },
    ],
  },
];

export const defaultTemplates: TemplateItem[] = [
  // Tạo cho ca khám này
  {
    id: "tpl-auto",
    title: "Tự động phân tích (Auto)",
    category: "session",
    iconType: "sparkle",
    promptDescription: "Tự động phân tích toàn bộ lời thoại ca khám và tạo hồ sơ bệnh án tiêu chuẩn.",
  },
  {
    id: "tpl-academic",
    title: "Bệnh án Diễn tiến Viện - Trường (Academic Progress Note)",
    category: "session",
    iconType: "sparkle",
    isPro: true,
    promptDescription: "Bệnh án hàn lâm tiêu chuẩn bệnh viện đại học với danh sách vấn đề theo dõi chi tiết.",
  },
  {
    id: "tpl-research",
    title: "Bản tóm tắt Nghiên cứu & Thử nghiệm Lâm sàng",
    category: "session",
    iconType: "sparkle",
    isPro: true,
    promptDescription: "Trích xuất dữ liệu lâm sàng theo đề cương nghiên cứu và tiêu chuẩn thu nhận bệnh nhân.",
  },
  {
    id: "tpl-clinical-summary",
    title: "Tóm tắt Ca khám & Hướng xử trí Lâm sàng",
    category: "session",
    iconType: "sparkle",
    isPro: true,
    promptDescription: "Bản tóm tắt súc tích buổi khám kèm các chỉ định xét nghiệm và giấy chuyển tuyến.",
  },

  // Mẫu tạo bởi MediTrace
  {
    id: "tpl-soap",
    title: "Bệnh án SOAP Chuẩn",
    category: "thu_vien",
    iconType: "pen",
    promptDescription: "Ghi chép lâm sàng 4 phần kinh điển: Chủ quan (S), Khách quan (O), Đánh giá (A), Kế hoạch (P).",
  },
  {
    id: "tpl-hp",
    title: "Biên bản Bệnh sử & Khám Thực thể (H & P)",
    category: "thu_vien",
    iconType: "pen",
    promptDescription: "Hồ sơ toàn diện khám ban đầu phân loại theo từng vấn đề sức khỏe của người bệnh.",
  },
  {
    id: "tpl-patient-letter",
    title: "Thư Hướng dẫn & Dặn dò Người bệnh",
    category: "thu_vien",
    iconType: "pen",
    isPro: true,
    promptDescription: "Thư dặn dò viết bằng ngôn từ dễ hiểu, gần gũi, giải thích cặn kẽ kết quả khám và phác đồ dùng thuốc.",
  },
  {
    id: "tpl-allied-health",
    title: "Biên bản Hội chẩn Đa chuyên khoa",
    category: "thu_vien",
    iconType: "pen",
    promptDescription: "Ghi chép cuộc họp hội đồng điều trị phối hợp bác sĩ, điều dưỡng, dược sĩ lâm sàng và phục hồi chức năng.",
  },
  {
    id: "tpl-board-minutes",
    title: "Biên bản Họp Hội đồng Y khoa",
    category: "thu_vien",
    iconType: "pen",
    promptDescription: "Văn bản quản trị lâm sàng và báo cáo chuyên môn cấp hội đồng bệnh viện.",
  },
];

export const samplePatients: Patient[] = [
  {
    id: "pat-1",
    name: "Nguyễn Văn An",
    identifier: "Nhiễm virus hô hấp, Ho khan, Sốt",
    dob: "14/05/1988 (38 tuổi)",
    gender: "Nam",
    phone: "0912 345 678",
    lastConsultation: "Hôm nay 09:17",
    chiefComplaint: "Ho khan kéo dài, đau đầu, sốt nhẹ 3 ngày nay",
  },
  {
    id: "pat-2",
    name: "Trần Thị Mai",
    identifier: "Tái khám Tăng huyết áp & Đái tháo đường",
    dob: "20/11/1965 (61 tuổi)",
    gender: "Nữ",
    phone: "0988 765 432",
    lastConsultation: "18 Th09 2026",
    chiefComplaint: "Kiểm tra huyết áp định kỳ, xét nghiệm HbA1c",
  },
  {
    id: "pat-3",
    name: "Lê Hoàng Phúc",
    identifier: "Đau thượng vị nghi viêm dạ dày",
    dob: "05/08/1995 (31 tuổi)",
    gender: "Nam",
    phone: "0903 112 233",
    lastConsultation: "15 Th09 2026",
    chiefComplaint: "Đau cồn cào vùng thượng vị lúc đói, ợ hơi ợ chua",
  },
];

export const sampleTasks: ClinicalTask[] = [
  {
    id: "task-1",
    title: "Kiểm tra kết quả xét nghiệm PCR virus đường hô hấp khi phòng lab trả kết quả",
    patientName: "Nguyễn Văn An - Nhiễm virus, Ho, Sốt",
    dueDate: "Trưa mai, 12:00",
    completed: false,
    priority: "high",
  },
  {
    id: "task-2",
    title: "Gọi điện hỏi thăm tình trạng sốt của bệnh nhân sau 3 ngày dùng thuốc",
    patientName: "Nguyễn Văn An - Nhiễm virus, Ho, Sốt",
    dueDate: "25 Th09 2026",
    completed: false,
    priority: "medium",
  },
  {
    id: "task-3",
    title: "Gửi tờ rơi điện tử hướng dẫn chăm sóc bệnh cúm qua Zalo/Email cho bệnh nhân",
    patientName: "Nguyễn Văn An - Nhiễm virus, Ho, Sốt",
    dueDate: "Hôm nay",
    completed: true,
    priority: "low",
  },
  {
    id: "task-4",
    title: "Kê đơn lặp thuốc hạ áp Amlodipine 5mg cho bệnh nhân Trần Thị Mai",
    patientName: "Trần Thị Mai - Tăng huyết áp",
    dueDate: "Thứ Sáu tới",
    completed: false,
    priority: "medium",
  },
];
