import React, { useState } from 'react';
import { X, Bell, ShieldAlert, Sparkles, Check } from 'lucide-react';
import { Product } from '../types';

interface SetAlertModalProps {
  product: Product | null;
  isOpen: boolean;
  onClose: () => void;
  onSaveAlert: (alertConfig: {
    productId: string;
    thresholdPercent: number;
    notifyOnStockOut: boolean;
    notifyOnCompetitorFlashSale: boolean;
  }) => void;
}

export const SetAlertModal: React.FC<SetAlertModalProps> = ({
  product,
  isOpen,
  onClose,
  onSaveAlert,
}) => {
  if (!isOpen || !product) return null;

  const [threshold, setThreshold] = useState(3.0);
  const [notifyStockOut, setNotifyStockOut] = useState(true);
  const [notifyFlashSale, setNotifyFlashSale] = useState(true);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSaveAlert({
      productId: product.id,
      thresholdPercent: threshold,
      notifyOnStockOut: notifyStockOut,
      notifyOnCompetitorFlashSale: notifyFlashSale,
    });
    onClose();
  };

  return (
    <div
      id="set-alert-modal"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200"
    >
      <div className="bg-white rounded-xl border border-[#e2e8f0] shadow-2xl p-6 max-w-md w-full space-y-4">
        <div className="flex justify-between items-start">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-[#eff4ff] border border-[#d3e4fe] flex items-center justify-center text-[#0051d5]">
              <Bell className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-base text-[#0b1c30]">Configure Alerts</h3>
              <p className="text-xs text-gray-500 font-mono">{product.name}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 text-gray-400 hover:text-gray-700">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          <div>
            <div className="flex justify-between font-mono text-gray-600 mb-1">
              <span>Price Deviation Sensitivity</span>
              <span className="font-bold text-[#0051d5]">{threshold}%</span>
            </div>
            <input
              type="range"
              min="1"
              max="15"
              step="0.5"
              value={threshold}
              onChange={(e) => setThreshold(parseFloat(e.target.value))}
              className="w-full accent-[#0051d5] cursor-pointer"
            />
            <p className="text-[11px] text-gray-400 mt-1">
              Triggers when competitor price deviates by &gt; {threshold}% from our target.
            </p>
          </div>

          <div className="space-y-2.5 pt-2 border-t border-gray-100">
            <label className="flex items-center justify-between p-3 rounded-lg border border-gray-200 bg-gray-50 hover:bg-gray-100 cursor-pointer">
              <div>
                <span className="font-semibold text-gray-800 block">Competitor Flash Sales</span>
                <span className="text-[11px] text-gray-500">Detect temporary lightning deals and promotions</span>
              </div>
              <input
                type="checkbox"
                checked={notifyFlashSale}
                onChange={(e) => setNotifyFlashSale(e.target.checked)}
                className="rounded text-[#0051d5] w-4 h-4"
              />
            </label>

            <label className="flex items-center justify-between p-3 rounded-lg border border-gray-200 bg-gray-50 hover:bg-gray-100 cursor-pointer">
              <div>
                <span className="font-semibold text-gray-800 block">Stock Out Arbitrage</span>
                <span className="text-[11px] text-gray-500">Alert immediately when top rivals go out of stock</span>
              </div>
              <input
                type="checkbox"
                checked={notifyStockOut}
                onChange={(e) => setNotifyStockOut(e.target.checked)}
                className="rounded text-[#0051d5] w-4 h-4"
              />
            </label>
          </div>

          <div className="flex justify-end gap-2 pt-3 border-t border-gray-100">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border rounded-lg text-gray-600 hover:bg-gray-50 font-semibold"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-5 py-2 bg-[#000000] text-white rounded-lg hover:bg-[#1f2937] font-semibold"
            >
              Save Alert Rules
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
