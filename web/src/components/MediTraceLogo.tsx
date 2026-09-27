import React from "react";

interface MediTraceLogoProps {
  className?: string;
  size?: number;
}

export const MediTraceLogo: React.FC<MediTraceLogoProps> = ({
  className = "",
  size = 32,
}) => {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={`inline-block select-none flex-shrink-0 ${className}`}
      aria-label="Logo"
    >
      <defs>
        {/* Clip path defining the precise curved shield outline */}
        <clipPath id="meditrace-shield-clip">
          <path
            d="M50 6.5 C53.5 6.5 75 12.5 82.5 19 C84.2 20.5 85.5 22.8 85.5 25.5 V48 C85.5 67.5 69 84 51.5 93 C50.6 93.5 49.4 93.5 48.5 93 C31 84 14.5 67.5 14.5 48 V25.5 C14.5 22.8 15.8 20.5 17.5 19 C25 12.5 46.5 6.5 50 6.5 Z"
          />
        </clipPath>
      </defs>

      {/* Main Shield body clipped to shield boundary */}
      <g clipPath="url(#meditrace-shield-clip)">
        {/* Navy Blue Left & Top Section */}
        <rect width="100" height="100" fill="#0A366F" />

        {/* Teal / Cyan Section on the Right & Bottom Contour */}
        <path
          d="M 68 6 C 76 20 73 37 66 50 C 58 64 47 78 33 87 C 41 91.5 48 93 50 93 C 69 84 85.5 67.5 85.5 48 V 25.5 C 85.5 22.8 84.5 20 82.5 19 C 77 13.5 72 8 68 6 Z"
          fill="#00A7A7"
        />

        {/* Bold White Medical Cross with smooth rounded corners */}
        {/* Horizontal bar: width 48, height 20, rx 5 */}
        <rect
          x="26"
          y="37"
          width="48"
          height="20"
          rx="5"
          fill="#FFFFFF"
        />
        {/* Vertical bar: width 20, height 48, rx 5 */}
        <rect
          x="40"
          y="23"
          width="20"
          height="48"
          rx="5"
          fill="#FFFFFF"
        />
      </g>

      {/* White Connecting Trace Pathway S-Curve */}
      <path
        d="M 33 67 C 39 60, 44 53, 50 47 C 56 41, 61 34, 67 27"
        stroke="#FFFFFF"
        strokeWidth="5"
        strokeLinecap="round"
        fill="none"
      />

      {/* Node 1: Bottom Left Node (White Ring + Mint Fill) */}
      <circle cx="33" cy="67" r="5.8" fill="#5AD8BE" stroke="#FFFFFF" strokeWidth="2.6" />

      {/* Node 2: Center Node in Cross Center (White Ring + Navy Fill) */}
      <circle cx="50" cy="47" r="7.5" fill="#0A366F" stroke="#FFFFFF" strokeWidth="3" />

      {/* Node 3: Top Right Node (White Ring + Mint Fill) */}
      <circle cx="67" cy="27" r="5.8" fill="#5AD8BE" stroke="#FFFFFF" strokeWidth="2.6" />
    </svg>
  );
};


export default MediTraceLogo;
