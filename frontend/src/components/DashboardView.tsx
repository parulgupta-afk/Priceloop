import React from 'react';
import {
  Package,
  AlertTriangle,
  BarChart3,
  Plus,
  ArrowUpRight,
  ArrowDownRight,
  Minus,
  Zap,
  Info,
  CheckCircle,
  Headphones,
  Mouse,
  Keyboard,
  Monitor,
  Armchair,
  Coffee,
  Thermometer,
  ArrowRight,
  MoreVertical,
} from 'lucide-react';
import { Product, MarketPositionStats } from '../types';

interface DashboardViewProps {
  products: Product[];
  marketStats?: MarketPositionStats;
  stats?: MarketPositionStats;
  activeAlertsCount?: number;
  onOpenAddProductModal?: () => void;
  onSelectProduct: (product: Product) => void;
  onViewAllDynamics?: () => void;
  onNavigate?: (view: any) => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  products,
  marketStats,
  stats,
  activeAlertsCount = 2,
  onOpenAddProductModal,
  onSelectProduct,
  onViewAllDynamics,
  onNavigate,
}) => {
  const currentStats = marketStats || stats || {
    cheapestCount: 6394,
    cheapestPercent: 45,
    midTierCount: 4973,
    midTierPercent: 35,
    premiumCount: 2842,
    premiumPercent: 20,
    totalProducts: 14209,
  };

  const handleOpenAdd = () => {
    if (onOpenAddProductModal) {
      onOpenAddProductModal();
    } else if (onNavigate) {
      onNavigate('market-grid');
    }
  };

  const handleViewAll = () => {
    if (onViewAllDynamics) {
      onViewAllDynamics();
    } else if (onNavigate) {
      onNavigate('market-grid');
    }
  };
  // Helper to render representative product category icon
  const getProductIcon = (name: string, category: string) => {
    const lower = (name + ' ' + category).toLowerCase();
    if (lower.includes('headphone') || lower.includes('audio') || lower.includes('wh-1000')) {
      return <Headphones className="w-4 h-4 text-[#0051d5]" />;
    }
    if (lower.includes('mouse') || lower.includes('mx master')) {
      return <Mouse className="w-4 h-4 text-[#0051d5]" />;
    }
    if (lower.includes('keyboard') || lower.includes('keychron')) {
      return <Keyboard className="w-4 h-4 text-[#0051d5]" />;
    }
    if (lower.includes('monitor') || lower.includes('display')) {
      return <Monitor className="w-4 h-4 text-[#0051d5]" />;
    }
    if (lower.includes('chair') || lower.includes('furniture')) {
      return <Armchair className="w-4 h-4 text-[#0051d5]" />;
    }
    if (lower.includes('barista') || lower.includes('coffee') || lower.includes('breville')) {
      return <Coffee className="w-4 h-4 text-[#0051d5]" />;
    }
    if (lower.includes('thermostat') || lower.includes('nest')) {
      return <Thermometer className="w-4 h-4 text-[#0051d5]" />;
    }
    return <Package className="w-4 h-4 text-[#0051d5]" />;
  };

  const getInsightBadge = (product: Product) => {
    const { type, title } = product.aiInsight;
    if (type === 'flash_sale') {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#ffdad6]/60 text-[#ba1a1a] text-[11px] font-medium border border-[#ffdad6]">
          <Zap className="w-3 h-3 text-[#ba1a1a]" />
          <span>{title}</span>
        </span>
      );
    }
    if (type === 'optimal_price') {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#eff4ff] text-[#0051d5] text-[11px] font-medium border border-[#d3e4fe]">
          <Info className="w-3 h-3 text-[#0051d5]" />
          <span>{title}</span>
        </span>
      );
    }
    if (type === 'margin_warning') {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-amber-50 text-amber-800 text-[11px] font-medium border border-amber-200">
          <AlertTriangle className="w-3 h-3 text-amber-600" />
          <span>{title}</span>
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-emerald-50 text-emerald-800 text-[11px] font-medium border border-emerald-200">
        <CheckCircle className="w-3 h-3 text-emerald-600" />
        <span>{title}</span>
      </span>
    );
  };

  return (
    <div id="dashboard-view" className="space-y-8 animate-in fade-in duration-200">
      {/* Dashboard Title & CTA */}
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <h2 className="text-2xl sm:text-3xl lg:text-[32px] font-bold text-[#0b1c30] tracking-tight leading-tight">
            Optimize the intelligence,
          </h2>
          <h2 className="text-2xl sm:text-3xl lg:text-[32px] font-bold text-[#76777d] tracking-tight leading-tight opacity-75">
            Maximize profitability
          </h2>
        </div>
        <button
          id="dashboard-add-product-btn"
          onClick={handleOpenAdd}
          className="bg-[#000000] hover:bg-[#1f2937] active:scale-[0.98] text-white font-semibold px-6 py-2.5 rounded-lg transition-all flex items-center justify-center gap-2 shadow-sm cursor-pointer shrink-0"
        >
          <Plus className="w-4 h-4" />
          <span>Add Product</span>
        </button>
      </div>

      {/* 3 Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Metric 1: Products Tracked */}
        <div className="bg-white border border-[#e2e8f0] rounded-xl p-6 flex flex-col gap-2 hover:border-[#316bf3]/50 transition-colors shadow-sm">
          <div className="flex justify-between items-center text-[#76777d]">
            <span className="text-sm font-medium text-[#45464d]">
              Products Tracked
            </span>
            <Package className="w-5 h-5 text-[#76777d]" />
          </div>
          <div className="flex items-baseline gap-2.5 mt-1">
            <span className="text-3xl font-bold text-[#0b1c30] font-mono tracking-tight">
              {currentStats.totalProducts.toLocaleString()}
            </span>
            <span className="text-[#009668] text-xs font-mono font-semibold flex items-center gap-0.5">
              <ArrowUpRight className="w-3.5 h-3.5" /> +2.4%
            </span>
          </div>
        </div>

        {/* Metric 2: Active Alerts */}
        <div className="bg-white border border-[#e2e8f0] rounded-xl p-6 flex flex-col gap-2 hover:border-[#316bf3]/50 transition-colors shadow-sm relative overflow-hidden">
          <div className="absolute right-0 top-0 w-20 h-20 bg-[#ffdad6]/30 rounded-bl-full pointer-events-none" />
          <div className="flex justify-between items-center text-[#45464d] relative z-10">
            <span className="text-sm font-medium">Active Alerts</span>
            <AlertTriangle className="w-5 h-5 text-[#ba1a1a]" />
          </div>
          <div className="flex items-baseline gap-3 mt-1 relative z-10">
            <span className="text-3xl font-bold text-[#0b1c30] font-mono tracking-tight">
              {activeAlertsCount}
            </span>
            <span className="text-[#ba1a1a] text-xs font-medium bg-[#ffdad6] px-2.5 py-0.5 rounded-full border border-[#ffdad6]">
              High Severity
            </span>
          </div>
        </div>

        {/* Metric 3: Avg Market Position */}
        <div className="bg-white border border-[#e2e8f0] rounded-xl p-6 flex flex-col gap-2 hover:border-[#316bf3]/50 transition-colors shadow-sm">
          <div className="flex justify-between items-center text-[#76777d]">
            <span className="text-sm font-medium text-[#45464d]">
              Avg Market Position
            </span>
            <BarChart3 className="w-5 h-5 text-[#76777d]" />
          </div>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-3xl font-bold text-[#0b1c30] font-mono tracking-tight">
              #2.4
            </span>
            <span className="text-[#76777d] text-xs font-medium">
              Out of top 10
            </span>
          </div>
        </div>
      </div>

      {/* Data Table & Donut Chart Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Table Area (2 Cols) */}
        <div className="lg:col-span-2 bg-white border border-[#e2e8f0] rounded-xl flex flex-col overflow-hidden shadow-sm">
          <div className="p-4 px-6 border-b border-[#e2e8f0] bg-[#f8f9ff] flex justify-between items-center">
            <h3 className="font-semibold text-base text-[#0b1c30]">
              Recent Market Dynamics
            </h3>
            <button
              onClick={handleViewAll}
              className="text-[#0051d5] hover:text-[#003ea8] text-xs font-semibold flex items-center gap-1 cursor-pointer transition-colors"
            >
              <span>View All</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse min-w-[550px]">
              <thead>
                <tr className="border-b border-[#e2e8f0] bg-[#f8f9ff]/60 text-[#76777d] font-mono text-[10px] uppercase tracking-wider">
                  <th className="py-3 px-6 font-semibold">Product</th>
                  <th className="py-3 px-4 font-semibold">SKU</th>
                  <th className="py-3 px-4 font-semibold">Price Change</th>
                  <th className="py-3 px-6 font-semibold">AI Insight</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#e2e8f0]/60 text-sm">
                {products.slice(0, 5).map((product) => (
                  <tr
                    key={product.id}
                    onClick={() => onSelectProduct(product)}
                    className="hover:bg-[#eff4ff]/70 transition-colors group cursor-pointer"
                  >
                    {/* Product */}
                    <td className="py-3.5 px-6">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded bg-[#eff4ff] border border-[#d3e4fe] flex items-center justify-center shrink-0">
                          {getProductIcon(product.name, product.category)}
                        </div>
                        <span className="font-semibold text-[#0b1c30] group-hover:text-[#0051d5] transition-colors">
                          {product.name}
                        </span>
                      </div>
                    </td>

                    {/* SKU */}
                    <td className="py-3.5 px-4 font-mono text-xs text-[#76777d]">
                      {product.sku}
                    </td>

                    {/* Price Change */}
                    <td className="py-3.5 px-4">
                      <div className="flex items-center gap-1.5">
                        {product.priceChangeDirection === 'up' && (
                          <>
                            <span className="font-mono text-xs font-semibold text-emerald-600 flex items-center">
                              <ArrowUpRight className="w-3.5 h-3.5" />
                              ${Math.abs(product.priceDeltaAmount).toFixed(2)}
                            </span>
                            <span className="text-[11px] text-[#76777d]">
                              (+{product.priceDeltaPercent}%)
                            </span>
                          </>
                        )}
                        {product.priceChangeDirection === 'down' && (
                          <>
                            <span className="font-mono text-xs font-semibold text-[#ba1a1a] flex items-center">
                              <ArrowDownRight className="w-3.5 h-3.5" />
                              ${Math.abs(product.priceDeltaAmount).toFixed(2)}
                            </span>
                            <span className="text-[11px] text-[#76777d]">
                              ({product.priceDeltaPercent}%)
                            </span>
                          </>
                        )}
                        {product.priceChangeDirection === 'neutral' && (
                          <>
                            <span className="font-mono text-xs font-semibold text-[#76777d] flex items-center">
                              <Minus className="w-3.5 h-3.5" />
                              $0.00
                            </span>
                            <span className="text-[11px] text-[#76777d]">
                              (0.0%)
                            </span>
                          </>
                        )}
                      </div>
                    </td>

                    {/* AI Insight */}
                    <td className="py-3.5 px-6">
                      {getInsightBadge(product)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Chart Area (1 Col) */}
        <div className="bg-white border border-[#e2e8f0] rounded-xl flex flex-col p-6 shadow-sm">
          <div className="flex justify-between items-center mb-6">
            <h3 className="font-semibold text-base text-[#0b1c30]">
              Market Position
            </h3>
            <button className="text-[#76777d] hover:text-[#0b1c30] p-1 rounded">
              <MoreVertical className="w-4 h-4" />
            </button>
          </div>

          {/* Clean Vector CSS Donut Chart */}
          <div className="flex-1 flex flex-col justify-center items-center relative py-4">
            <div
              className="relative w-44 h-44 rounded-full flex items-center justify-center transition-transform hover:scale-105 duration-300"
              style={{
                background:
                  'conic-gradient(#10b981 0% 45%, #3b82f6 45% 80%, #64748b 80% 100%)',
              }}
            >
              {/* Inner cutout */}
              <div className="w-32 h-32 bg-white rounded-full flex flex-col items-center justify-center shadow-inner">
                <span className="text-3xl font-bold font-mono text-[#0b1c30]">
                  45%
                </span>
                <span className="text-[11px] text-[#76777d] font-medium tracking-wide uppercase">
                  Cheapest
                </span>
              </div>
            </div>
          </div>

          {/* Donut Legend */}
          <div className="mt-6 pt-4 border-t border-[#e2e8f0] space-y-2.5 text-xs">
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-[#10b981]" />
                <span className="text-[#0b1c30] font-medium">Cheapest</span>
              </div>
              <span className="font-mono font-semibold text-[#0b1c30]">
                {currentStats.cheapestCount.toLocaleString()}
              </span>
            </div>

            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-[#3b82f6]" />
                <span className="text-[#0b1c30] font-medium">Mid-tier</span>
              </div>
              <span className="font-mono font-semibold text-[#0b1c30]">
                {currentStats.midTierCount.toLocaleString()}
              </span>
            </div>

            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-[#64748b]" />
                <span className="text-[#0b1c30] font-medium">Premium</span>
              </div>
              <span className="font-mono font-semibold text-[#0b1c30]">
                {currentStats.premiumCount.toLocaleString()}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
