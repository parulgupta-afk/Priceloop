import React, { useState } from 'react';
import {
  ArrowLeft,
  Bookmark,
  BookmarkCheck,
  MoreVertical,
  ArrowDown,
  Sparkles,
  Maximize2,
  Minimize2,
  Store,
  Truck,
  Building2,
  Bell,
  SlidersHorizontal,
  ArrowUpRight,
  ArrowDownRight,
  TrendingDown,
  CheckCircle2,
} from 'lucide-react';
import { Product } from '../types';

interface ProductDetailViewProps {
  product: Product;
  onBack: () => void;
  onOpenAlertModal: (product: Product) => void;
  onOpenStrategyModal: (product: Product) => void;
  onToggleBookmark: (productId: string) => void;
}

export const ProductDetailView: React.FC<ProductDetailViewProps> = ({
  product,
  onBack,
  onOpenAlertModal,
  onOpenStrategyModal,
  onToggleBookmark,
}) => {
  const [activeRange, setActiveRange] = useState<'7D' | '30D' | '90D' | '1Y'>('30D');
  const [hoveredPoint, setHoveredPoint] = useState<{
    date: string;
    target: number;
    avg: number;
    x: number;
    y: number;
  } | null>(null);
  const [isChartExpanded, setIsChartExpanded] = useState(false);

  // SVG Chart calculation
  const history = product.priceHistory;
  const minVal = Math.min(...history.map((h) => Math.min(h.targetPrice, h.marketAvg))) - 15;
  const maxVal = Math.max(...history.map((h) => Math.max(h.targetPrice, h.marketAvg))) + 15;
  const range = maxVal - minVal || 1;

  // Convert points to SVG coordinates (viewBox 0 0 100 60)
  const targetPoints = history.map((item, idx) => {
    const x = (idx / (history.length - 1)) * 90 + 5;
    const y = 55 - ((item.targetPrice - minVal) / range) * 45;
    return { x, y, date: item.date, target: item.targetPrice, avg: item.marketAvg };
  });

  const avgPoints = history.map((item, idx) => {
    const x = (idx / (history.length - 1)) * 90 + 5;
    const y = 55 - ((item.marketAvg - minVal) / range) * 45;
    return { x, y, date: item.date, target: item.targetPrice, avg: item.marketAvg };
  });

  const targetPath = targetPoints
    .map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`)
    .join(' ');

  const avgPath = avgPoints
    .map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`)
    .join(' ');

  return (
    <div
      id="product-detail-view"
      className="max-w-[640px] mx-auto pb-24 space-y-6 animate-in fade-in duration-200"
    >
      {/* Top Mobile/Subpage Header */}
      <div className="bg-white border border-[#e2e8f0] rounded-xl px-4 py-3 flex items-center justify-between shadow-sm sticky top-20 z-30">
        <button
          id="product-back-btn"
          onClick={onBack}
          className="w-9 h-9 flex items-center justify-center rounded-full hover:bg-[#eff4ff] text-[#0b1c30] transition-colors cursor-pointer"
          aria-label="Back"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2">
          <img
            alt="Priceloop Logo"
            className="w-6 h-6 rounded object-contain"
            src="https://lh3.googleusercontent.com/aida/AEtjO1WQeqo6ixOTLdiEF8WsqcpSE05ALFPy_50Qf7a7m4nLgudZXyVHq3vBpIYIBNIjPeXbr27D0kplf29DB2KNZLVyrjXL5ees3VfuoXCH5NljZeCDv7qbM5H0oP3ziEXMRCGVckOP2max54Vt391XrDr3pHVZUq5rCz-bIvcI95arFOo4tkbFhZldYDRZujo5rc-y02hTJw-PcbMLAoqJ55dOGJdnhPZg11YFNF9fUwJNAq4fi0o5Drl4PQ4"
          />
          <span className="font-extrabold text-sm tracking-widest text-[#0b1c30]">
            PRICELOOP
          </span>
        </div>

        <button
          className="w-9 h-9 flex items-center justify-center rounded-full hover:bg-[#eff4ff] text-[#0b1c30] transition-colors cursor-pointer"
          aria-label="More"
        >
          <MoreVertical className="w-5 h-5" />
        </button>
      </div>

      {/* Hero Section */}
      <section className="bg-white rounded-xl p-6 border border-[#e2e8f0] shadow-sm relative overflow-hidden">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h1 className="text-xl sm:text-2xl font-bold text-[#0b1c30] tracking-tight">
              {product.name}
            </h1>
            <p className="text-xs sm:text-sm text-[#76777d] mt-0.5">
              {product.subtitle}
            </p>
          </div>
          <button
            onClick={() => onToggleBookmark(product.id)}
            className={`w-9 h-9 rounded-full flex items-center justify-center transition-colors cursor-pointer ${
              product.isBookmarked
                ? 'bg-[#d3e4fe] text-[#0051d5]'
                : 'bg-[#eff4ff] text-[#76777d] hover:text-[#0051d5]'
            }`}
            title={product.isBookmarked ? 'Bookmarked' : 'Bookmark product'}
          >
            {product.isBookmarked ? (
              <BookmarkCheck className="w-4 h-4 fill-current" />
            ) : (
              <Bookmark className="w-4 h-4" />
            )}
          </button>
        </div>

        {/* Product Studio Image */}
        <div className="flex justify-center my-6">
          <div className="relative group">
            <img
              src={product.imageUrl}
              alt={product.name}
              className="w-48 h-48 object-contain drop-shadow-xl transition-transform duration-300 group-hover:scale-105"
            />
          </div>
        </div>

        {/* Price Row */}
        <div className="flex items-end justify-between border-t border-[#e2e8f0] pt-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="font-mono text-[11px] font-semibold text-[#76777d] uppercase tracking-wider">
                Target Price
              </span>
              <span className="inline-flex items-center gap-0.5 bg-emerald-50 text-emerald-700 border border-emerald-200 px-1.5 py-0.5 rounded text-[10px] font-mono font-bold">
                <ArrowDown className="w-3 h-3" /> 2.4%
              </span>
            </div>
            <div className="text-3xl sm:text-4xl font-extrabold text-[#0b1c30] font-mono tracking-tight">
              ${product.targetPrice.toFixed(2)}
            </div>
          </div>

          <div className="text-right pb-1">
            <div className="font-mono text-[11px] font-semibold text-[#76777d] uppercase tracking-wider mb-1">
              Market Avg
            </div>
            <div className="text-lg font-semibold text-[#94a3b8] line-through font-mono">
              ${product.marketAvg.toFixed(2)}
            </div>
          </div>
        </div>

        {/* AI Insight Badge inside Hero */}
        <div className="mt-4 bg-[#eff4ff] border border-[#d3e4fe] rounded-lg p-3.5 flex items-start gap-3">
          <Sparkles className="w-5 h-5 text-[#0051d5] shrink-0 mt-0.5" />
          <div>
            <span className="text-xs font-bold text-[#0051d5] block mb-0.5">
              AI Insight
            </span>
            <p className="text-xs text-[#45464d] leading-relaxed">
              {product.aiInsight.description}
            </p>
          </div>
        </div>
      </section>

      {/* 30-Day Price History Chart Section */}
      <section className="bg-white rounded-xl p-5 border border-[#e2e8f0] shadow-sm">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h2 className="font-bold text-base text-[#0b1c30]">
              {activeRange} Price History
            </h2>
            <div className="flex items-center gap-1.5 mt-1">
              {(['7D', '30D', '90D', '1Y'] as const).map((r) => (
                <button
                  key={r}
                  onClick={() => setActiveRange(r)}
                  className={`text-[10px] font-mono px-2 py-0.5 rounded transition-colors cursor-pointer ${
                    activeRange === r
                      ? 'bg-[#0051d5] text-white font-bold'
                      : 'text-gray-500 hover:bg-gray-100'
                  }`}
                >
                  {r}
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={() => setIsChartExpanded(!isChartExpanded)}
            className="font-mono text-xs text-[#0051d5] hover:bg-[#eff4ff] px-2.5 py-1 rounded transition-colors flex items-center gap-1 cursor-pointer"
          >
            <span>{isChartExpanded ? 'Collapse' : 'Expand'}</span>
            {isChartExpanded ? (
              <Minimize2 className="w-3.5 h-3.5" />
            ) : (
              <Maximize2 className="w-3.5 h-3.5" />
            )}
          </button>
        </div>

        {/* Interactive SVG Chart Canvas */}
        <div
          className={`w-full relative transition-all duration-300 ${
            isChartExpanded ? 'h-72' : 'h-48'
          }`}
        >
          {/* Y Axis Grid lines */}
          <div className="absolute left-0 top-0 bottom-6 flex flex-col justify-between text-[10px] font-mono text-[#94a3b8] select-none">
            <span>${Math.round(maxVal)}</span>
            <span>${Math.round((maxVal + minVal) / 2)}</span>
            <span>${Math.round(minVal)}</span>
          </div>

          {/* X Axis Grid labels */}
          <div className="absolute left-10 right-2 bottom-0 flex justify-between text-[10px] font-mono text-[#94a3b8] border-t border-gray-200 pt-1 select-none">
            <span>{history[0]?.date || 'Jul 1'}</span>
            <span>{history[Math.floor(history.length / 2)]?.date || 'Jul 15'}</span>
            <span>{history[history.length - 1]?.date || 'Jul 30'}</span>
          </div>

          {/* SVG Canvas */}
          <svg
            className="w-[calc(100%-40px)] h-[calc(100%-24px)] absolute left-10 top-0 overflow-visible"
            viewBox="0 0 100 60"
            preserveAspectRatio="none"
          >
            {/* Grid Line */}
            <line
              x1="0"
              y1="30"
              x2="100"
              y2="30"
              stroke="#f1f5f9"
              strokeWidth="0.5"
            />

            {/* Market Avg Dashed Line */}
            <path
              d={avgPath}
              fill="none"
              stroke="#94a3b8"
              strokeWidth="1.5"
              strokeDasharray="2 2"
            />

            {/* Target Price Solid Line */}
            <path
              d={targetPath}
              fill="none"
              stroke="#0051d5"
              strokeWidth="2.5"
              strokeLinejoin="round"
              strokeLinecap="round"
            />

            {/* Interactive Points */}
            {targetPoints.map((pt, idx) => (
              <g key={idx}>
                <circle
                  cx={pt.x}
                  cy={pt.y}
                  r={idx === targetPoints.length - 1 ? '2.5' : '1.8'}
                  fill="#0051d5"
                  stroke="#ffffff"
                  strokeWidth="0.8"
                  className="cursor-pointer hover:r-3 transition-all"
                  onMouseEnter={() => setHoveredPoint(pt)}
                />
              </g>
            ))}
          </svg>

          {/* Tooltip on hover */}
          {hoveredPoint && (
            <div
              className="absolute bg-[#0b1c30] text-white text-[11px] font-mono py-1 px-2.5 rounded shadow-lg pointer-events-none z-20 border border-gray-700"
              style={{
                left: `clamp(10px, ${hoveredPoint.x}%, calc(100% - 110px))`,
                top: `${Math.max(5, hoveredPoint.y - 15)}px`,
              }}
            >
              <div className="font-bold text-sky-300">{hoveredPoint.date}</div>
              <div>Target: ${hoveredPoint.target.toFixed(2)}</div>
              <div className="text-gray-400">Avg: ${hoveredPoint.avg.toFixed(2)}</div>
            </div>
          )}
        </div>

        {/* Chart Legend */}
        <div className="flex justify-center gap-6 mt-4 pt-2 border-t border-gray-100">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[#0051d5]" />
            <span className="font-mono text-[11px] text-[#45464d] uppercase">
              Target Price
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full border border-[#94a3b8] border-dashed" />
            <span className="font-mono text-[11px] text-[#45464d] uppercase">
              Market Avg
            </span>
          </div>
        </div>
      </section>

      {/* Competitor Intelligence List */}
      <section className="space-y-3">
        <h2 className="font-bold text-base text-[#0b1c30] flex items-center gap-2">
          <Store className="w-4 h-4 text-[#0051d5]" />
          <span>Competitor Intelligence</span>
        </h2>

        <div className="space-y-2.5">
          {product.competitors.map((comp) => (
            <div
              key={comp.id}
              className="bg-white border border-[#e2e8f0] rounded-xl p-3.5 flex items-center justify-between hover:border-[#0051d5]/40 transition-colors shadow-sm"
            >
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-[#eff4ff] border border-[#d3e4fe] rounded-lg flex items-center justify-center font-bold text-xs text-[#0051d5]">
                  {comp.shortCode}
                </div>
                <div>
                  <div className="font-semibold text-sm text-[#0b1c30]">
                    {comp.name}
                  </div>
                  <div className="flex items-center gap-2 mt-0.5 text-[10px] font-mono">
                    <span
                      className={`px-1.5 py-0.5 rounded font-semibold ${
                        comp.stockStatus === 'In Stock'
                          ? 'bg-emerald-50 text-emerald-700'
                          : comp.stockStatus === 'Low Stock'
                          ? 'bg-amber-50 text-amber-700'
                          : 'bg-red-50 text-red-700'
                      }`}
                    >
                      {comp.stockStatus}
                    </span>
                    <span className="text-[#76777d] flex items-center gap-0.5">
                      <Truck className="w-3 h-3" /> {comp.shipping}
                    </span>
                  </div>
                </div>
              </div>

              <div className="text-right">
                <div className="font-mono font-bold text-sm text-[#0b1c30]">
                  ${comp.price.toFixed(2)}
                </div>
                <div
                  className={`text-[11px] font-mono mt-0.5 ${
                    comp.isMatch
                      ? 'text-[#76777d]'
                      : comp.price > product.targetPrice
                      ? 'text-[#ba1a1a] font-semibold'
                      : 'text-emerald-600 font-semibold'
                  }`}
                >
                  {comp.deltaText}
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Bottom Sticky Action Bar */}
      <div className="fixed bottom-0 left-0 right-0 md:left-[240px] bg-white border-t border-[#e2e8f0] p-3 px-6 flex gap-3 z-40 shadow-xl">
        <div className="max-w-[640px] w-full mx-auto flex gap-3">
          <button
            id="detail-alert-btn"
            onClick={() => onOpenAlertModal(product)}
            className="flex-1 py-3 border border-[#e2e8f0] rounded-lg font-semibold text-xs text-[#0b1c30] flex items-center justify-center gap-2 hover:bg-[#eff4ff] active:scale-[0.98] transition-all cursor-pointer"
          >
            <Bell className="w-4 h-4 text-[#0051d5]" />
            <span>Alert</span>
          </button>

          <button
            id="detail-strategy-btn"
            onClick={() => onOpenStrategyModal(product)}
            className="flex-[2] py-3 bg-[#000000] text-white rounded-lg font-semibold text-xs flex items-center justify-center gap-2 hover:bg-[#1f2937] active:scale-[0.98] transition-all shadow-sm cursor-pointer"
          >
            <SlidersHorizontal className="w-4 h-4 text-sky-300" />
            <span>Adjust Strategy</span>
          </button>
        </div>
      </div>
    </div>
  );
};
