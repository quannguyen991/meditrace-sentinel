// Real-time audio recording, speech recognition (STT), and audio visualizer service

export interface AudioDevice {
  deviceId: string;
  label: string;
  kind: "audioinput" | "audiooutput";
}

export interface RealAudioServiceCallbacks {
  onTranscriptChunk?: (chunk: string, isFinal: boolean) => void;
  onAudioLevel?: (volume: number, frequencies: number[]) => void;
  onError?: (error: string) => void;
  onAudioReady?: (blob: Blob, url: string) => void;
}

export class RealAudioService {
  private mediaStream: MediaStream | null = null;
  private mediaRecorder: MediaRecorder | null = null;
  private audioChunks: Blob[] = [];
  private recognition: any = null;
  private audioContext: AudioContext | null = null;
  private analyser: AnalyserNode | null = null;
  private animationFrameId: number | null = null;
  private callbacks: RealAudioServiceCallbacks = {};
  private language: string = "vi-VN"; // Default Vietnamese
  private isListening: boolean = false;
  private currentAudioUrl: string | null = null;
  private speakerRole: "Bác sĩ" | "Bệnh nhân" | "Tự động" = "Tự động";

  constructor(callbacks: RealAudioServiceCallbacks = {}) {
    this.callbacks = callbacks;
  }

  public setCallbacks(callbacks: RealAudioServiceCallbacks) {
    this.callbacks = { ...this.callbacks, ...callbacks };
  }

  public setLanguage(lang: string) {
    this.language = lang.startsWith("en") ? "en-US" : "vi-VN";
    if (this.recognition) {
      this.recognition.lang = this.language;
    }
  }

  public setSpeakerRole(role: "Bác sĩ" | "Bệnh nhân" | "Tự động") {
    this.speakerRole = role;
  }

  public static isSpeechRecognitionSupported(): boolean {
    return typeof window !== "undefined" && Boolean(
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    );
  }

  public static async getAvailableDevices(): Promise<{ mics: AudioDevice[]; speakers: AudioDevice[] }> {
    if (typeof navigator === "undefined" || !navigator.mediaDevices?.enumerateDevices) {
      return { mics: [], speakers: [] };
    }

    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      const mics: AudioDevice[] = [];
      const speakers: AudioDevice[] = [];

      devices.forEach((dev, index) => {
        if (dev.kind === "audioinput") {
          mics.push({
            deviceId: dev.deviceId,
            label: dev.label || `Micrô ${index + 1} (${dev.deviceId.slice(0, 5)}...)`,
            kind: "audioinput",
          });
        } else if (dev.kind === "audiooutput") {
          speakers.push({
            deviceId: dev.deviceId,
            label: dev.label || `Loa ngoài ${index + 1} (${dev.deviceId.slice(0, 5)}...)`,
            kind: "audiooutput",
          });
        }
      });

      return { mics, speakers };
    } catch (err) {
      console.warn("Lỗi khi đọc danh sách thiết bị âm thanh:", err);
      return { mics: [], speakers: [] };
    }
  }

  public async start(deviceId?: string): Promise<boolean> {
    if (this.isListening) return true;

    try {
      // 1. Yêu cầu quyền truy cập micrô thực tế
      const constraints: MediaStreamConstraints = {
        audio: deviceId ? { deviceId: { exact: deviceId } } : true,
      };

      this.mediaStream = await navigator.mediaDevices.getUserMedia(constraints);

      // 2. Khởi tạo AudioContext và Analyser để đo cường độ âm thanh thực tế
      try {
        const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
        if (AudioCtx) {
          this.audioContext = new AudioCtx();
          const source = this.audioContext.createMediaStreamSource(this.mediaStream);
          this.analyser = this.audioContext.createAnalyser();
          this.analyser.fftSize = 64;
          source.connect(this.analyser);
          this.startVisualizer();
        }
      } catch (e) {
        console.warn("Không khởi tạo được AudioContext:", e);
      }

      // 3. Khởi tạo MediaRecorder để ghi file âm thanh thực
      this.audioChunks = [];
      try {
        const mimeType = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
          ? "audio/webm;codecs=opus"
          : MediaRecorder.isTypeSupported("audio/webm")
          ? "audio/webm"
          : "audio/mp4";

        this.mediaRecorder = new MediaRecorder(this.mediaStream, { mimeType });
        this.mediaRecorder.ondataavailable = (event) => {
          if (event.data && event.data.size > 0) {
            this.audioChunks.push(event.data);
          }
        };

        this.mediaRecorder.onstop = () => {
          const blob = new Blob(this.audioChunks, { type: mimeType });
          if (this.currentAudioUrl) {
            URL.revokeObjectURL(this.currentAudioUrl);
          }
          this.currentAudioUrl = URL.createObjectURL(blob);
          if (this.callbacks.onAudioReady) {
            this.callbacks.onAudioReady(blob, this.currentAudioUrl);
          }
        };

        this.mediaRecorder.start(500); // Lưu chunk mỗi 500ms
      } catch (err) {
        console.warn("MediaRecorder không khởi động được:", err);
      }

      // 4. KHÔNG dùng Web Speech API: trên Chrome, `webkitSpeechRecognition` gửi âm thanh lên
      //    máy chủ Google để nhận dạng — trái nguyên tắc chạy tại chỗ của dự án. Bản chép
      //    được làm SAU khi dừng ghi: tệp ghi âm gửi sang /api/transcribe (PhoWhisper tại chỗ).

      this.isListening = true;
      return true;
    } catch (err: any) {
      console.error("Lỗi khi mở Micrô:", err);
      const msg =
        err.name === "NotAllowedError" || err.name === "PermissionDeniedError"
          ? "Vui lòng cho phép quyền truy cập Micrô trên trình duyệt để thu âm ca khám."
          : `Lỗi kết nối Micrô: ${err.message || "Thiết bị không sẵn sàng"}`;
      if (this.callbacks.onError) {
        this.callbacks.onError(msg);
      }
      return false;
    }
  }

  private initSpeechRecognition() {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      console.warn("Trình duyệt không hỗ trợ Web Speech API.");
      return;
    }

    try {
      this.recognition = new SpeechRecognition();
      this.recognition.continuous = true;
      this.recognition.interimResults = true;
      this.recognition.lang = this.language;

      this.recognition.onresult = (event: any) => {
        let interimTranscript = "";
        let finalTranscript = "";

        for (let i = event.resultIndex; i < event.results.length; ++i) {
          const transcriptText = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcriptText;
          } else {
            interimTranscript += transcriptText;
          }
        }

        if (finalTranscript.trim() && this.callbacks.onTranscriptChunk) {
          let formatted = finalTranscript.trim();
          if (this.speakerRole !== "Tự động") {
            formatted = `\n${this.speakerRole}: "${formatted}"`;
          } else {
            formatted = ` ${formatted}`;
          }
          this.callbacks.onTranscriptChunk(formatted, true);
        } else if (interimTranscript.trim() && this.callbacks.onTranscriptChunk) {
          this.callbacks.onTranscriptChunk(interimTranscript.trim(), false);
        }
      };

      this.recognition.onerror = (event: any) => {
        // 'no-speech' is normal when user is silent
        if (event.error !== "no-speech") {
          console.warn("Speech recognition error:", event.error);
        }
      };

      this.recognition.onend = () => {
        // Tự động duy trì nhận diện nếu đang trong trạng thái ghi âm
        if (this.isListening) {
          try {
            this.recognition.start();
          } catch (e) {
            // Already started or busy
          }
        }
      };

      this.recognition.start();
    } catch (err) {
      console.warn("Không khởi tạo được SpeechRecognition:", err);
    }
  }

  private startVisualizer() {
    if (!this.analyser) return;

    const dataArray = new Uint8Array(this.analyser.frequencyBinCount);

    const update = () => {
      if (!this.isListening || !this.analyser) return;

      this.analyser.getByteFrequencyData(dataArray);

      // Tính âm lượng trung bình
      let sum = 0;
      for (let i = 0; i < dataArray.length; i++) {
        sum += dataArray[i];
      }
      const avg = sum / dataArray.length;
      const normalizedVolume = Math.min(100, Math.round((avg / 128) * 100));

      // Lấy 8 dải tần số đặc trưng cho visualizer
      const freqs: number[] = [];
      const step = Math.floor(dataArray.length / 8);
      for (let i = 0; i < 8; i++) {
        freqs.push(Math.round((dataArray[i * step] / 255) * 100));
      }

      if (this.callbacks.onAudioLevel) {
        this.callbacks.onAudioLevel(normalizedVolume, freqs);
      }

      this.animationFrameId = requestAnimationFrame(update);
    };

    update();
  }

  public stop(): void {
    this.isListening = false;

    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
      this.animationFrameId = null;
    }

    if (this.callbacks.onAudioLevel) {
      this.callbacks.onAudioLevel(0, [0, 0, 0, 0, 0, 0, 0, 0]);
    }

    if (this.recognition) {
      try {
        this.recognition.stop();
      } catch (e) {}
      this.recognition = null;
    }

    if (this.mediaRecorder && this.mediaRecorder.state !== "inactive") {
      try {
        this.mediaRecorder.stop();
      } catch (e) {}
    }

    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach((track) => track.stop());
      this.mediaStream = null;
    }

    if (this.audioContext && this.audioContext.state !== "closed") {
      try {
        this.audioContext.close();
      } catch (e) {}
      this.audioContext = null;
    }
  }

  public getCurrentAudioBlob(): Blob | null {
    if (this.audioChunks.length === 0) return null;
    return new Blob(this.audioChunks, { type: "audio/webm" });
  }

  public getCurrentAudioUrl(): string | null {
    return this.currentAudioUrl;
  }
}

// Global Singleton for sharing state between Header and Views
export const realAudioService = new RealAudioService();
