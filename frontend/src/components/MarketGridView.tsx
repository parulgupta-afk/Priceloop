import React, { useState } from 'react';
import {
  Filter,
  Download,
  ArrowUp,
  ArrowDown,
  Minus,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  Check,
  Search,
  SlidersHorizontal,
  X,
} from 'lucide-react';
import { Product } from '../types';

interface MarketGridViewProps {
  products: Product[];
  onSelectProduct: (product: Product) => void;
}

export const MarketGridView: React.FC<MarketGridViewProps> = ({
  products,
  onSelectProduct,
}) => {
  const [filterCategory, setFilterCategory] = useState<string>('All');
  const [filterSentiment, setFilterSentiment] = useState<string>('All');
  const [isFilterOpen, setIsFilterOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const categories = ['All', ...Array.from(new Set(products.map((p) => p.category)))];
  const sentiments = ['All', 'Bullish', 'Bearish', 'Neutral', 'High Risk'];

  const filteredProducts = products.filter((p) => {
    const matchesCategory = filterCategory === 'All' || p.category === filterCategory;
    const matchesSentiment = filterSentiment === 'All' || p.aiSentiment === filterSentiment;
    const matchesSearch =
      searchQuery.trim() === '' ||
      p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.sku.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSentiment && matchesSearch;
  });

  const handleExportCSV = () => {
    const headers = ['Product', 'SKU', 'Category', 'Target Price', 'Market Avg', 'Min Price', 'Max Price', 'Position', 'Sentiment', 'Gross Margin %'];
    const rows = filteredProducts.map((p) => [
      `"${p.name}"`,
      `"${p.sku}"`,
      `"${p.category}"`,
      p.targetPrice.toFixed(2),
      p.marketAvg.toFixed(2),
      p.minPrice.toFixed(2),
      p.maxPrice.toFixed(2),
      `"${p.marketPositionLabel}"`,
      `"${p.aiSentiment}"`,
      `${p.marginPercent.toFixed(1)}%`,
    ]);

    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map((e) => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `Priceloop_Market_Benchmarking_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const getSentimentBadge = (sentiment: Product['aiSentiment']) => {
    if (sentiment === 'Bullish') {
      return (
        <div className="flex items-center gap-1.5 text-emerald-600 font-bold font-mono text-xs">
          <TrendingUp className="w-4 h-4 text-emerald-600" />
          <span className="uppercase tracking-wide">Bullish</span>
        </div>
      );
    }
    if (sentiment === 'Bearish') {
      return (
        <div className="flex items-center gap-1.5 text-[#ba1a1a] font-bold font-mono text-xs">
          <TrendingDown className="w-4 h-4 text-[#ba1a1a]" />
          <span className="uppercase tracking-wide">Bearish</span>
        </div>
      );
    }
    if (sentiment === 'High Risk') {
      return (
        <div className="flex items-center gap-1.5 text-red-600 font-bold font-mono text-xs">
          <AlertTriangle className="w-4 h-4 text-red-600" />
          <span className="uppercase tracking-wide">High Risk</span>
        </div>
      );
    }
    return (
      <div className="flex items-center gap-1.5 text-[#76777d] font-bold font-mono text-xs">
        <Minus className="w-4 h-4 text-[#76777d]" />
        <span className="uppercase tracking-wide">Neutral</span>
      </div>
    );
  };

  const getPositionBadge = (product: Product) => {
    if (product.marketPositionLabel.includes('Cheapest')) {
      return (
        <span className="inline-flex items-center px-2 py-1 rounded bg-emerald-50 text-emerald-800 border border-emerald-200 font-mono text-[11px] font-bold">
          {product.marketPositionLabel}
        </span>
      );
    }
    if (product.marketPositionLabel.includes('Max Price')) {
      return (
        <span className="inline-flex items-center px-2 py-1 rounded border border-[#ffdad6] text-[#ba1a1a] font-mono text-[11px] bg-[#ffdad6]/30 font-bold">
          {product.marketPositionLabel}
        </span>
      );
    }
    return (
      <span className="inline-flex items-center px-2 py-1 rounded bg-[#eff4ff] text-[#0051d5] font-mono text-[11px] font-medium border border-[#d3e4fe]">
        {product.marketPositionLabel}
      </span>
    );
  };

  return (
    <div id="market-grid-view" className="space-y-6 animate-in fade-in duration-200">
      {/* Header & Action Buttons */}
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold text-[#0b1c30] tracking-tight">
            Market Benchmarking
          </h2>
          <p className="text-xs sm:text-sm text-[#76777d] mt-1">
            Real-time competitive analysis across key SKUs.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            id="market-grid-filter-btn"
            onClick={() => setIsFilterOpen(!isFilterOpen)}
            className={`bg-white border rounded-lg px-4 py-2 flex items-center gap-2 transition-colors font-mono text-xs font-semibold cursor-pointer shadow-sm ${
              isFilterOpen || filterCategory !== 'All' || filterSentiment !== 'All'
                ? 'border-[#0051d5] text-[#0051d5] bg-[#eff4ff]'
                : 'border-[#e2e8f0] text-[#0b1c30] hover:bg-gray-50'
            }`}
          >
            <Filter className="w-3.5 h-3.5" />
            <span>FILTER</span>
            {(filterCategory !== 'All' || filterSentiment !== 'All') && (
              <span className="w-2 h-2 rounded-full bg-[#0051d5]" />
            )}
          </button>

          <button
            id="market-grid-export-btn"
            onClick={handleExportCSV}
            className="bg-[#000000] text-white hover:bg-[#1f2937] active:scale-[0.98] px-4 py-2 rounded-lg flex items-center gap-2 transition-all font-mono text-xs font-semibold cursor-pointer shadow-sm"
          >
            <Download className="w-3.5 h-3.5" />
            <span>EXPORT CSV</span>
          </button>
        </div>
      </div>

      {/* Expandable Filter Drawer */}
      {isFilterOpen && (
        <div className="bg-white border border-[#e2e8f0] rounded-xl p-4 shadow-sm space-y-4 animate-in fade-in slide-in-from-top-2 duration-150">
          <div className="flex justify-between items-center pb-2 border-b border-gray-100">
            <span className="font-semibold text-xs uppercase tracking-wider text-[#0b1c30] font-mono">
              Filter Options
            </span>
            <button
              onClick={() => {
                setFilterCategory('All');
                setFilterSentiment('All');
                setSearchQuery('');
              }}
              className="text-xs text-[#0051d5] hover:underline font-medium cursor-pointer"
            >
              Reset Filters
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="text-xs font-mono text-gray-500 uppercase block mb-1">
                Category
              </label>
              <select
                value={filterCategory}
                onChange={(e) => setFilterCategory(e.target.value)}
                className="w-full text-xs bg-gray-50 border border-gray-200 rounded-lg p-2 focus:ring-1 focus:ring-[#0051d5]"
              >
                {categories.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-xs font-mono text-gray-500 uppercase block mb-1">
                AI Sentiment
              </label>
              <select
                value={filterSentiment}
                onChange={(e) => setFilterSentiment(e.target.value)}
                className="w-full text-xs bg-gray-50 border border-gray-200 rounded-lg p-2 focus:ring-1 focus:ring-[#0051d5]"
              >
                {sentiments.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-xs font-mono text-gray-500 uppercase block mb-1">
                Quick Search
              </label>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search SKU or Name..."
                className="w-full text-xs bg-gray-50 border border-gray-200 rounded-lg p-2 focus:ring-1 focus:ring-[#0051d5]"
              />
            </div>
          </div>
        </div>
      )}

      {/* Scrollable Data Table Container */}
      <div className="bg-white rounded-xl border border-[#e2e8f0] overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse min-w-[760px]">
            <thead className="bg-[#f8f9ff] border-b border-[#e2e8f0]">
              <tr className="text-[10px] font-mono text-[#76777d] uppercase tracking-wider">
                <th className="p-4 pl-6 sticky left-0 bg-[#f8f9ff] z-10 w-72 border-r border-[#e2e8f0]">
                  Product / SKU
                </th>
                <th className="p-4">Current Price</th>
                <th className="p-4">Min / Max</th>
                <th className="p-4">Position</th>
                <th className="p-4 pr-6">AI Sentiment</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#e2e8f0] text-sm">
              {filteredProducts.map((product) => (
                <tr
                  key={product.id}
                  onClick={() => onSelectProduct(product)}
                  className="hover:bg-[#eff4ff]/70 transition-colors group cursor-pointer"
                >
                  {/* Sticky Column 1: Product / SKU */}
                  <td className="p-4 pl-6 sticky left-0 bg-white group-hover:bg-[#eff4ff]/70 transition-colors border-r border-[#e2e8f0] z-10">
                    <div className="flex flex-col gap-0.5">
                      <span className="font-semibold text-[#0b1c30] group-hover:text-[#0051d5] transition-colors">
                        {product.name}
                      </span>
                      <span className="font-mono text-[10px] text-[#76777d]">
                        SKU: {product.sku}
                      </span>
                    </div>
                  </td>

                  {/* Current Price */}
                  <td className="p-4">
                    <div className="flex items-center gap-1.5 font-mono font-bold text-[#0b1c30]">
                      <span>${product.targetPrice.toFixed(2)}</span>
                      {product.priceChangeDirection === 'up' && (
                        <ArrowUp className="w-3.5 h-3.5 text-[#ba1a1a]" />
                      )}
                      {product.priceChangeDirection === 'down' && (
                        <ArrowDown className="w-3.5 h-3.5 text-emerald-600" />
                      )}
                      {product.priceChangeDirection === 'neutral' && (
                        <Minus className="w-3.5 h-3.5 text-[#76777d]" />
                      )}
                    </div>
                  </td>

                  {/* Min / Max */}
                  <td className="p-4 font-mono text-xs text-[#76777d]">
                    ${product.minPrice.toFixed(0)} - ${product.maxPrice.toFixed(0)}
                  </td>

                  {/* Position Badge */}
                  <td className="p-4">{getPositionBadge(product)}</td>

                  {/* AI Sentiment */}
                  <td className="p-4 pr-6">{getSentimentBadge(product.aiSentiment)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
