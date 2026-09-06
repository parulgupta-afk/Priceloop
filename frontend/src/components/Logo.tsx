import React from 'react';

interface LogoProps {
  size?: number | string;
  className?: string;
  withText?: boolean;
  subtitle?: string;
  textClassName?: string;
}

export const Logo: React.FC<LogoProps> = ({
  size = 32,
  className = '',
  withText = false,
  subtitle = 'Intelligence Platform',
  textClassName = '',
}) => {
  const icon = (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={`rounded-lg object-contain shadow-sm flex-shrink-0 ${className}`}
      aria-label="Priceloop AI Logo"
    >
      <defs>
        <linearGradient id="pl-grad" x1="0%" y1="100%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#1d4ed8" />
          <stop offset="50%" stopColor="#2563eb" />
          <stop offset="100%" stopColor="#4f46e5" />
        </linearGradient>
        <linearGradient id="pl-line" x1="0%" y1="100%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#93c5fd" />
          <stop offset="100%" stopColor="#ffffff" />
        </linearGradient>
      </defs>

      <rect
        x="4"
        y="4"
        width="92"
        height="92"
        rx="26"
        fill="url(#pl-grad)"
        stroke="rgba(255,255,255,0.25)"
        strokeWidth="2"
      />
      <rect
        x="8"
        y="8"
        width="84"
        height="84"
        rx="22"
        fill="#030712"
        fillOpacity="0.3"
      />

      <path
        d="M26 66 L42 50 L54 60 L74 36"
        stroke="url(#pl-line)"
        strokeWidth="7"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M58 36 H74 V52"
        stroke="url(#pl-line)"
        strokeWidth="7"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <circle cx="54" cy="60" r="3.5" fill="#ffffff" />
      <circle cx="42" cy="50" r="3" fill="#ffffff" opacity="0.9" />
    </svg>
  );

  if (!withText) {
    return icon;
  }

  return (
    <div className="flex items-center gap-3">
      {icon}
      <div>
        <h1 className={`font-bold text-white text-[19px] leading-tight tracking-tight ${textClassName}`}>
          Priceloop AI
        </h1>
        {subtitle && (
          <p className="text-[#94a3b8] text-[11px] font-medium tracking-wide">
            {subtitle}
          </p>
        )}
      </div>
    </div>
  );
};

export default Logo;
