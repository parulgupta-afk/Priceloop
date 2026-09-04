import React from 'react';
import { X, History, ArrowRight, CheckCircle, Sliders, Shield } from 'lucide-react';

interface HistoryModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const HistoryModal: React.FC<HistoryModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  const logs = [
    {
      time: '10 mins ago',
      product: 'Sony WH-1000XM5',
      action: 'Repriced to $348.00',
      reason: 'Rule matched: Undercut Amazon by 1%',
      user: 'Auto Engine',
      status: 'success',
    },
    {
      time: '45 mins ago',
      product: 'Breville Barista Pro',
      action: 'Price Alert Triggered',
      reason: 'Amazon flash discount -$45.00 detected',
      user: 'Web Scraper Bot #4',
      status: 'warning',
    },
    {
      time: '2 hours ago',
      product: 'Nest Learning Thermostat',
      action: 'Stock Out Verified',
      reason: 'Best Buy inventory dropped to 0 units',
      user: 'Inventory Crawler',
      status: 'info',
    },
    {
      time: '4 hours ago',
      product: 'Logitech MX Master 3S',
      action: 'Strategy Applied',
      reason: 'Manual Buy Box match selected by Parul M.',
      user: 'Parul Mahajan',
      status: 'success',
    },
  ];

  return (
    <div
      id="history-modal"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200"
    >
      <div className="bg-white rounded-xl border border-[#e2e8f0] shadow-2xl p-6 max-w-lg w-full space-y-4">
        <div className="flex justify-between items-center pb-3 border-b border-gray-100">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-gray-100 flex items-center justify-center text-gray-700">
              <History className="w-4 h-4" />
            </div>
            <h3 className="font-bold text-base text-[#0b1c30]">
              Repricing & Telemetry Audit Log
            </h3>
          </div>
          <button onClick={onClose} className="p-1 rounded text-gray-400 hover:text-gray-700">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="max-h-80 overflow-y-auto divide-y divide-gray-100 space-y-1">
          {logs.map((log, i) => (
            <div key={i} className="py-3 text-xs space-y-1">
              <div className="flex justify-between items-center">
                <span className="font-bold text-[#0b1c30]">{log.product}</span>
                <span className="font-mono text-gray-400 text-[11px]">{log.time}</span>
              </div>
              <div className="flex items-center gap-2 font-mono text-[#0051d5] font-semibold">
                <span>{log.action}</span>
              </div>
              <div className="text-gray-500 text-[11px] flex justify-between">
                <span>{log.reason}</span>
                <span className="text-gray-400 italic">{log.user}</span>
              </div>
            </div>
          ))}
        </div>

        <div className="pt-3 border-t border-gray-100 flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 bg-[#000000] text-white rounded-lg text-xs font-semibold hover:bg-[#1f2937]"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
