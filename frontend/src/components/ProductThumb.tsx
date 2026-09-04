import React, { useState } from 'react';
import { Package } from 'lucide-react';

interface ProductThumbProps {
  src?: string | null;
  alt: string;
  className?: string;
  imgClassName?: string;
  size?: 'sm' | 'md' | 'lg';
}

const sizeMap = {
  sm: 'w-8 h-8',
  md: 'w-12 h-12',
  lg: 'w-20 h-20',
};

/**
 * Product thumbnail with graceful fallback when image is missing or fails to load.
 */
export const ProductThumb: React.FC<ProductThumbProps> = ({
  src,
  alt,
  className = '',
  imgClassName = '',
  size = 'sm',
}) => {
  const [failed, setFailed] = useState(false);
  const box = sizeMap[size];
  const showImg = Boolean(src) && !failed;

  return (
    <div
      className={`${box} rounded-lg bg-[#eff4ff] border border-[#d3e4fe] overflow-hidden flex items-center justify-center shrink-0 ${className}`}
    >
      {showImg ? (
        <img
          src={src as string}
          alt={alt}
          loading="lazy"
          referrerPolicy="no-referrer"
          onError={() => setFailed(true)}
          className={`w-full h-full object-cover ${imgClassName}`}
        />
      ) : (
        <Package
          className={`${size === 'lg' ? 'w-8 h-8' : size === 'md' ? 'w-5 h-5' : 'w-4 h-4'} text-[#0051d5]`}
        />
      )}
    </div>
  );
};
