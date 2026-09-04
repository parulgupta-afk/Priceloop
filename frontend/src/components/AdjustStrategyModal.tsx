import React, { useState } from 'react';
import { X, SlidersHorizontal, Check, Shield, Zap, TrendingUp, DollarSign } from 'lucide-react';
import { Product } from '../types';

interface AdjustStrategyModalProps {
  product: Product | null;
  isOpen: boolean;
  onClose: () => void;
  onSaveStrategy: (productId: string, newTargetPrice: number, strategyName: string) => void;
}

export const AdjustStrategyModal: React.FC<AdjustStrategyModalProps> = ({
  product,
  isOpen,
  onClose,
  onSaveStrategy,
}) => {
  if (!isOpen || !product) return null;

  const [selectedStrategy, setSelectedStrategy] = useState<'undercut' | 'match' | 'margin' | 'custom'>('undercut');
  const [customPrice, setCustomPrice] = useState(product.targetPrice);

  const strategies = [
    {
      id: 'undercut' as const,
      title: 'Aggressive Undercut (Cheapest)',
      description: 'Automatically reprices $1.00 below the lowest in-stock verified competitor.',
      target: product.competitors.length > 0 ? Math.min(...product.competitors.map((c) => c.price)) - 1.0 : product.targetPrice - 2.0,
      icon: Zap,
    },
    {
      id: 'match' as const,
      title: 'Match Top Competitor',
      description: 'Matches Amazon or Best Buy price exactly to share the primary Buy Box.',
      target: product.competitors[0]?.price || product.targetPrice,
      icon: Check,
    },
    {
      id: 'margin' as const,
      title: 'Profit Margin Maximizer (30% Gross)',
      description: 'Locks target price at minimum 30% gross margin above current COGS ($' + product.cogs.toFixed(0) + ').',
      target: product.cogs / 0.7,
      icon: TrendingUp,
    },
    {
      id: 'custom' as const,
      title: 'Manual Custom Price',
      description: 'Set a fixed custom price override for this specific SKU.',
      target: customPrice,
      icon: DollarSign,
    },
  ];

  const handleSave = () => {
    const chosen = strategies.find((s) => s.id === selectedStrategy);
    const finalPrice = selectedStrategy === 'custom' ? Number(customPrice) : Number(chosen?.target.toFixed(2));
    onSaveStrategy(product.id, finalPrice, chosen?.title || 'Custom');
    onClose();
  };

  return (
    <div
      id="adjust-strategy-modal"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200"
    >
      <div className="bg-white rounded-xl border border-[#e2e8f0] shadow-2xl p-6 max-w-lg w-full space-y-5">
        <div className="flex justify-between items-start">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-[#eff4ff] border border-[#d3e4fe] flex items-center justify-center text-[#0051d5]">
              <SlidersHorizontal className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-base text-[#0b1c30]">Adjust Repricing Strategy</h3>
              <p className="text-xs text-gray-500 font-mono">{product.name} ({product.sku})</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 rounded-full text-gray-400 hover:text-gray-700">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Strategy Selection Radio List */}
        <div className="space-y-2.5">
          {strategies.map((strat) => {
            const Icon = strat.icon;
            const isSelected = selectedStrategy === strat.id;

            return (
              <div
                key={strat.id}
                onClick={() => setSelectedStrategy(strat.id)}
                className={`p-3.5 rounded-xl border transition-all cursor-pointer flex items-start gap-3.5 ${
                  isSelected
                    ? 'border-[#0051d5] bg-[#eff4ff]/60 ring-1 ring-[#0051d5]'
                    : 'border-[#e2e8f0] bg-white hover:border-gray-300'
                }`}
              >
                <div
                  className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${
                    isSelected ? 'bg-[#0051d5] text-white' : 'bg-gray-100 text-gray-500'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex justify-between items-center">
                    <span className="font-semibold text-xs text-[#0b1c30]">{strat.title}</span>
                    <span className="font-mono text-xs font-bold text-[#0051d5]">
                      ${strat.target.toFixed(2)}
                    </span>
                  </div>
                  <p className="text-[11px] text-gray-500 mt-0.5 leading-snug">{strat.description}</p>
                </div>
              </div>
            );
          })}
        </div>

        {/* Custom Input when selected */}
        {selectedStrategy === 'custom' && (
          <div className="p-3 bg-gray-50 rounded-lg border border-gray-200">
            <label className="text-xs font-mono text-gray-600 uppercase block mb-1">
              Custom Target Price ($)
            </label>
            <input
              type="number"
              step="0.01"
              value={customPrice}
              onChange={(e) => setCustomPrice(parseFloat(e.target.value) || 0)}
              className="w-full bg-white border border-gray-300 rounded-lg p-2 font-mono text-sm font-bold text-[#0b1c30] outline-none focus:border-[#0051d5]"
            />
          </div>
        )}

        <div className="flex justify-end gap-3 pt-2 border-t border-gray-100">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 border rounded-lg text-xs font-semibold text-gray-600 hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleSave}
            className="px-6 py-2 bg-[#000000] text-white rounded-lg text-xs font-semibold hover:bg-[#1f2937] shadow-sm"
          >
            Apply Repricing Strategy
          </button>
        </div>
      </div>
    </div>
  );
};
