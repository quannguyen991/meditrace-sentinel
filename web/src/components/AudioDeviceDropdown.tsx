import React, { useEffect, useState } from "react";
import { Check, Volume2, Mic, RefreshCw } from "lucide-react";
import { MediTraceLogo } from "./MediTraceLogo";
import { RealAudioService, AudioDevice } from "../services/realAudioService";

interface AudioDeviceDropdownProps {
  isOpen: boolean;
  onClose: () => void;
  selectedSpeaker: string;
  onSelectSpeaker: (speaker: string) => void;
  selectedMic: string;
  onSelectMic: (mic: string) => void;
  mode: "speaker" | "mic";
}

export const AudioDeviceDropdown: React.FC<AudioDeviceDropdownProps> = ({
  isOpen,
  onClose,
  selectedSpeaker,
  onSelectSpeaker,
  selectedMic,
  onSelectMic,
  mode,
}) => {
  const [realMics, setRealMics] = useState<AudioDevice[]>([]);
  const [realSpeakers, setRealSpeakers] = useState<AudioDevice[]>([]);
  const [isScanning, setIsScanning] = useState(false);

  useEffect(() => {
    if (isOpen) {
      scanDevices();
    }
  }, [isOpen]);

  const scanDevices = async () => {
    setIsScanning(true);
    try {
      const res = await RealAudioService.getAvailableDevices();
      if (res.mics.length > 0) {
        setRealMics(res.mics);
      }
      if (res.speakers.length > 0) {
        setRealSpeakers(res.speakers);
      }
    } catch (e) {
      console.warn(e);
    } finally {
      setIsScanning(false);
    }
  };

  if (!isOpen) return null;

  const defaultSpeakers = [
    "Mặc định - Loa máy tính (System Audio)",
    "Loa ngoài Bluetooth (Wireless Speaker/Headphones)",
  ];

  const defaultMics = [
    "Mặc định - Micrô hệ thống (System Microphone)",
    "Micrô khử ồn chuyên dụng (Noise-canceling Mic)",
  ];

  const speakersList = realSpeakers.length > 0
    ? realSpeakers.map((s) => s.label)
    : defaultSpeakers;

  const micsList = realMics.length > 0
    ? realMics.map((m) => m.label)
    : defaultMics;

  const appsList = [
    { name: "Ứng dụng phòng khám", icon: <MediTraceLogo size={15} /> },
    {
      name: "Microsoft Teams / Zoom",
      icon: (
        <div className="w-3.5 h-3.5 rounded-full bg-blue-500 flex items-center justify-center text-[8px] text-white font-bold">
          T
        </div>
      ),
    },
  ];

  return (
    <>
      {/* Nền bấm để đóng */}
      <div className="fixed inset-0 z-40" onClick={onClose} />

      {/* Hộp thoại Popover */}
      <div
        id="audio-device-dropdown"
        className="absolute right-0 top-full mt-2 w-80 bg-white rounded-2xl shadow-xl border border-[#E8E4DD] p-3 z-50 animate-in fade-in zoom-in-95 duration-100 select-none text-left"
      >
        <div className="text-[11px] font-medium text-[#7C756F] uppercase tracking-wider px-2 py-1">
          {mode === "speaker" ? "Thiết bị phát âm thanh" : "Micrô thu âm ca khám"}
        </div>

        <div className="px-2.5 py-2 mb-1.5 bg-[#F9F8F5] rounded-xl border border-[#EFECE6]">
          <p className="text-xs font-semibold text-[#2C2420]">
            {mode === "speaker" ? "Âm thanh hệ thống" : "Micrô phòng khám xung quanh (Ambient)"}
          </p>
          <p className="text-[11px] text-[#7C756F] mt-0.5">
            {mode === "speaker"
              ? "Thu nhận toàn bộ âm thanh và hội thoại trực tuyến trên máy tính"
              : "Thu âm trực tiếp cuộc trò chuyện giữa Bác sĩ và Bệnh nhân với khử nhiễu AI"}
          </p>
        </div>

        <div className="flex flex-col gap-0.5">
          {(mode === "speaker" ? speakersList : micsList).map((device) => {
            const isSelected =
              mode === "speaker"
                ? selectedSpeaker === device
                : selectedMic === device;
            return (
              <button
                key={device}
                onClick={() => {
                  if (mode === "speaker") onSelectSpeaker(device);
                  else onSelectMic(device);
                  onClose();
                }}
                className={`flex items-center justify-between px-2.5 py-2 rounded-xl text-xs transition-colors ${
                  isSelected
                    ? "bg-[#F3EFEA] text-[#2B1B22] font-medium"
                    : "text-[#4A423D] hover:bg-[#F9F8F5]"
                }`}
              >
                <div className="flex items-center gap-2 truncate pr-2">
                  {mode === "speaker" ? (
                    <Volume2 size={14} className="text-[#7C756F] flex-shrink-0" />
                  ) : (
                    <Mic size={14} className="text-[#7C756F] flex-shrink-0" />
                  )}
                  <span className="truncate">{device}</span>
                </div>
                {isSelected && (
                  <Check size={14} className="text-[#2B1B22] stroke-[2.5] flex-shrink-0" />
                )}
              </button>
            );
          })}
        </div>

        {/* Danh sách ứng dụng */}
        {mode === "speaker" && (
          <div className="mt-3 pt-2.5 border-t border-[#EFECE6]">
            <div className="text-[11px] font-medium text-[#7C756F] uppercase tracking-wider px-2 mb-1.5">
              Ứng dụng đang phát âm thanh
            </div>
            <div className="flex flex-col gap-1">
              {appsList.map((app) => (
                <div
                  key={app.name}
                  className="flex items-center gap-2.5 px-2.5 py-1.5 rounded-lg text-xs text-[#4A423D] hover:bg-[#F9F8F5]"
                >
                  <span className="flex-shrink-0">{app.icon}</span>
                  <span className="truncate">{app.name}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </>
  );
};
