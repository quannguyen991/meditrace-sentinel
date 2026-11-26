import { useCallback, useEffect, useRef, useState } from "react";
import type { TranscriptSegment } from "../types";
import { khoangPhatLaiLuot } from "../lib/asrHighlight";

/**
 * Hook dùng chung cho phát lại đoạn âm thanh gốc (~3s) theo lượt hội thoại [T_i]
 * ở cả `DuyetBenCanh` và `VerificationView`, tự động dọn sạch `HTMLAudioElement` khi đổi ca / đóng màn.
 */
export function useTurnAudioPlayer(audioUrl?: string, segments?: TranscriptSegment[]) {
  const [dangPhatLuot, setDangPhatLuot] = useState<number | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const ketThucPhatRef = useRef<number | null>(null);

  const dungPhat = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.ontimeupdate = null;
      audioRef.current.onended = null;
      audioRef.current.onloadedmetadata = null;
      audioRef.current = null;
    }
    ketThucPhatRef.current = null;
    setDangPhatLuot(null);
  }, []);

  useEffect(() => {
    setDangPhatLuot(null);
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.ontimeupdate = null;
        audioRef.current.onended = null;
        audioRef.current.onloadedmetadata = null;
        audioRef.current = null;
      }
      ketThucPhatRef.current = null;
    };
  }, [audioUrl]);

  const phatDoanLuot = useCallback(
    (so: number) => {
      if (!audioUrl) return;
      if (dangPhatLuot === so && audioRef.current) {
        audioRef.current.pause();
        setDangPhatLuot(null);
        return;
      }
      const khoang = khoangPhatLaiLuot(so, segments);
      if (!khoang) return;

      if (!audioRef.current) {
        audioRef.current = new Audio(audioUrl);
      } else if (audioRef.current.src !== audioUrl) {
        audioRef.current.src = audioUrl;
      }
      const au = audioRef.current;
      ketThucPhatRef.current = khoang.end_s;
      au.ontimeupdate = () => {
        if (ketThucPhatRef.current !== null && au.currentTime >= ketThucPhatRef.current) {
          au.pause();
          setDangPhatLuot(null);
        }
      };
      au.onended = () => setDangPhatLuot(null);

      const batDauPhat = () => {
        au.currentTime = khoang.start_s;
        au.play()
          .then(() => setDangPhatLuot(so))
          .catch(() => setDangPhatLuot(null));
      };
      if (au.readyState >= 1) {
        batDauPhat();
      } else {
        au.onloadedmetadata = batDauPhat;
      }
    },
    [audioUrl, segments, dangPhatLuot],
  );

  return { dangPhatLuot, phatDoanLuot, dungPhat };
}
