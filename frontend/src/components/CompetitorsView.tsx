import React from 'react';
import { Store, TrendingDown, TrendingUp, ShieldAlert, CheckCircle, ExternalLink } from 'lucide-react';
import { Product } from '../types';

interface CompetitorsViewProps {
  products: Product[];
  onSelectProduct: (product: Product) => void;
}

export const CompetitorsView: React.FC<CompetitorsViewProps> = ({
  products,
  onSelectProduct,
}) => {
  const competitorStats = [
    {
      name: 'Amazon',
      code: 'AMZ',
      trackedItems: 14209,
      winRate: '68.4%',
      undercutFreq: 'High (42/day)',
      avgPriceDelta: '-$2.40',
      stockMatch: '99.1%',
      status: 'Aggressive',
      color: 'bg-amber-50 text-amber-700 border-amber-200',
    },
    {
      name: 'Best Buy',
      code: 'BBY',
      trackedItems: 8430,
      winRate: '82.1%',
      undercutFreq: 'Moderate (12/day)',
      avgPriceDelta: '+$4.10',
      stockMatch: '94.3%',
      status: 'Stable',
      color: 'bg-blue-50 text-blue-700 border-blue-200',
    },
    {
      name: 'Walmart',
      code: 'WMT',
      trackedItems: 11200,
      winRate: '74.5%',
      undercutFreq: 'High (31/day)',
      avgPriceDelta: '+$1.80',
      stockMatch: '91.8%',
      status: 'Volatile',
      color: 'bg-indigo-50 text-indigo-700 border-indigo-200',
    },
    {
      name: 'Target',
      code: 'TGT',
      trackedItems: 6150,
      winRate: '88.9%',
      undercutFreq: 'Low (4/day)',
      avgPriceDelta: '+$6.50',
      stockMatch: '96.2%',
      status: 'Passive',
      color: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    },
  ];

  return (
    <div id="competitors-view" className="space-y-6 animate-in fade-in duration-200">
      <div>
        <h2 className="text-2xl sm:text-3xl font-bold text-[#0b1c30] tracking-tight">
          Competitor Intelligence
        </h2>
        <p className="text-xs sm:text-sm text-[#76777d] mt-1">
          Deep-dive telemetry across major retail channels and marketplace feeds.
        </p>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {competitorStats.map((comp) => (
          <div
            key={comp.name}
            className="bg-white border border-[#e2e8f0] rounded-xl p-5 shadow-sm hover:border-[#0051d5]/40 transition-colors"
          >
            <div className="flex justify-between items-start mb-3">
              <div>
                <h3 className="font-bold text-base text-[#0b1c30]">{comp.name}</h3>
                <span className="font-mono text-[10px] text-gray-400 uppercase">
                  Feed: {comp.code}
                </span>
              </div>
              <span
                className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border ${comp.color}`}
              >
                {comp.status}
              </span>
            </div>

            <div className="space-y-2 pt-2 border-t border-gray-100 text-xs font-mono">
              <div className="flex justify-between text-gray-600">
                <span>Win Rate:</span>
                <span className="font-bold text-emerald-600">{comp.winRate}</span>
              </div>
              <div className="flex justify-between text-gray-600">
                <span>Avg Delta:</span>
                <span className="font-bold text-[#0b1c30]">{comp.avgPriceDelta}</span>
              </div>
              <div className="flex justify-between text-gray-600">
                <span>Stock Accuracy:</span>
                <span className="font-bold text-sky-600">{comp.stockMatch}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Active Competitor Price Battles */}
      <div className="bg-white rounded-xl border border-[#e2e8f0] p-6 shadow-sm space-y-4">
        <h3 className="font-bold text-base text-[#0b1c30]">
          Active Price Battles by SKU
        </h3>
        <div className="divide-y divide-[#e2e8f0]">
          {products.map((p) => (
            <div
              key={p.id}
              onClick={() => onSelectProduct(p)}
              className="py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-[#eff4ff]/50 px-2 rounded-lg transition-colors cursor-pointer"
            >
              <div className="flex items-center gap-3">
                <img
                  src={p.imageUrl}
                  alt={p.name}
                  className="w-12 h-12 rounded object-contain bg-[#f8f9ff] border p-1"
                />
                <div>
                  <div className="font-bold text-sm text-[#0b1c30]">{p.name}</div>
                  <div className="font-mono text-xs text-gray-500">
                    SKU: {p.sku} | Our Price: ${p.targetPrice.toFixed(2)}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <div className="text-right">
                  <div className="text-xs font-mono font-semibold text-[#0051d5]">
                    {p.competitors.length} Competitors Tracked
                  </div>
                  <div className="text-[11px] text-gray-500 font-mono">
                    Market Avg: ${p.marketAvg.toFixed(2)}
                  </div>
                </div>
                <button className="p-2 text-gray-400 hover:text-[#0051d5] rounded-full">
                  <ExternalLink className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
