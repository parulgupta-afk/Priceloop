import React, { useState } from 'react';
import {
  AlertTriangle,
  AlertOctagon,
  Info,
  Filter,
  Plus,
  ArrowRight,
  MoreVertical,
  CheckCircle2,
  Check,
} from 'lucide-react';
import { AlertItem, Product } from '../types';

interface AlertsInboxViewProps {
  alerts: AlertItem[];
  products: Product[];
  onSelectProduct: (product: Product) => void;
  onResolveAlert: (alertId: string, actionName: string) => void;
  onOpenNewRuleModal: () => void;
}

export const AlertsInboxView: React.FC<AlertsInboxViewProps> = ({
  alerts,
  products,
  onSelectProduct,
  onResolveAlert,
  onOpenNewRuleModal,
}) => {
  const [activeTab, setActiveTab] = useState<'all' | 'critical' | 'price_drops'>('all');
  const [filterSeverity, setFilterSeverity] = useState<string>('all');
  const [actionFeedback, setActionFeedback] = useState<string | null>(null);

  const filteredAlerts = alerts.filter((a) => {
    if (activeTab === 'critical') return a.severity === 'critical';
    if (activeTab === 'price_drops') return a.type === 'price_drop';
    if (filterSeverity !== 'all') return a.severity === filterSeverity;
    return true;
  });

  const criticalCount = alerts.filter((a) => a.severity === 'critical' && !a.resolved).length;
  const totalUnresolved = alerts.filter((a) => !a.resolved).length;

  const handleAction = (alert: AlertItem, actionText: string) => {
    onResolveAlert(alert.id, actionText);
    setActionFeedback(`Action applied: ${actionText} for ${alert.productName}`);
    setTimeout(() => setActionFeedback(null), 3000);
  };

  const getProductForAlert = (alert: AlertItem) => {
    return products.find((p) => p.id === alert.productId) || products[0];
  };

  return (
    <div id="alerts-inbox-view" className="space-y-6 animate-in fade-in duration-200">
      {/* Toast Notification if action triggered */}
      {actionFeedback && (
        <div className="fixed bottom-6 right-6 z-50 bg-[#0b1c30] text-white px-4 py-3 rounded-lg shadow-2xl flex items-center gap-3 border border-emerald-500/50 animate-in slide-in-from-bottom-3 duration-200">
          <CheckCircle2 className="w-5 h-5 text-emerald-400" />
          <span className="text-xs font-mono font-medium">{actionFeedback}</span>
        </div>
      )}

      {/* Page Header & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl sm:text-3xl font-bold text-[#0b1c30] tracking-tight">
            Alerts Inbox
          </h2>
          <p className="text-xs sm:text-sm text-[#76777d] mt-1">
            Manage and respond to critical pricing deviations.
          </p>
        </div>

        <div className="flex gap-2.5">
          <button
            onClick={() => setFilterSeverity(filterSeverity === 'all' ? 'critical' : 'all')}
            className={`flex items-center gap-2 px-4 py-2 bg-white border rounded-lg font-mono text-xs font-semibold hover:bg-gray-50 transition-colors shadow-sm cursor-pointer ${
              filterSeverity !== 'all' ? 'border-[#0051d5] text-[#0051d5]' : 'border-[#e2e8f0] text-[#0b1c30]'
            }`}
          >
            <Filter className="w-3.5 h-3.5" />
            <span>Filter</span>
          </button>

          <button
            onClick={onOpenNewRuleModal}
            className="flex items-center gap-2 px-4 py-2 bg-[#000000] text-white rounded-lg font-mono text-xs font-semibold hover:bg-[#1f2937] active:scale-[0.98] transition-all shadow-sm cursor-pointer"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>New Rule</span>
          </button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="border-b border-[#e2e8f0]">
        <nav className="flex gap-6 sm:gap-8 overflow-x-auto">
          <button
            onClick={() => setActiveTab('all')}
            className={`py-3 px-1 text-xs sm:text-sm font-semibold flex items-center gap-2 border-b-2 transition-all cursor-pointer whitespace-nowrap ${
              activeTab === 'all'
                ? 'border-[#0051d5] text-[#0b1c30]'
                : 'border-transparent text-[#76777d] hover:text-[#0b1c30]'
            }`}
          >
            <span>All Alerts</span>
            <span className="bg-[#eff4ff] text-[#0051d5] font-mono text-xs font-bold py-0.5 px-2 rounded-full">
              {totalUnresolved}
            </span>
          </button>

          <button
            onClick={() => setActiveTab('critical')}
            className={`py-3 px-1 text-xs sm:text-sm font-semibold flex items-center gap-2 border-b-2 transition-all cursor-pointer whitespace-nowrap ${
              activeTab === 'critical'
                ? 'border-[#ba1a1a] text-[#ba1a1a]'
                : 'border-transparent text-[#76777d] hover:text-[#ba1a1a]'
            }`}
          >
            <span>High Severity</span>
            <span className="bg-[#ffdad6] text-[#ba1a1a] font-mono text-xs font-bold py-0.5 px-2 rounded-full">
              {criticalCount}
            </span>
          </button>

          <button
            onClick={() => setActiveTab('price_drops')}
            className={`py-3 px-1 text-xs sm:text-sm font-semibold border-b-2 transition-all cursor-pointer whitespace-nowrap ${
              activeTab === 'price_drops'
                ? 'border-[#0051d5] text-[#0b1c30]'
                : 'border-transparent text-[#76777d] hover:text-[#0b1c30]'
            }`}
          >
            Price Drops
          </button>
        </nav>
      </div>

      {/* Alerts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredAlerts.map((alert) => {
          const product = getProductForAlert(alert);

          return (
            <div
              key={alert.id}
              className={`bg-white border rounded-xl p-6 shadow-sm hover:shadow-md transition-all flex flex-col gap-4 relative overflow-hidden ${
                alert.resolved
                  ? 'border-gray-200 opacity-60 bg-gray-50/50'
                  : alert.severity === 'critical'
                  ? 'border-red-200 hover:border-red-400'
                  : 'border-[#e2e8f0] hover:border-[#0051d5]/40'
              }`}
            >
              {/* Card Header with Severity Tag & Time */}
              <div className="flex justify-between items-start">
                <div className="flex items-center gap-2">
                  {alert.severity === 'critical' && (
                    <span className="bg-[#ffdad6] text-[#ba1a1a] border border-[#ffdad6] px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase tracking-wider flex items-center gap-1">
                      <AlertOctagon className="w-3 h-3" />
                      Critical
                    </span>
                  )}
                  {alert.severity === 'warning' && (
                    <span className="bg-amber-100 text-amber-800 border border-amber-200 px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase tracking-wider flex items-center gap-1">
                      <AlertTriangle className="w-3 h-3" />
                      Warning
                    </span>
                  )}
                  {alert.severity === 'info' && (
                    <span className="bg-[#eff4ff] text-[#0051d5] border border-[#d3e4fe] px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase tracking-wider flex items-center gap-1">
                      <Info className="w-3 h-3" />
                      Info
                    </span>
                  )}

                  <span className="text-[#76777d] text-xs font-mono">
                    {alert.timeAgo}
                  </span>
                </div>

                <button className="text-[#76777d] hover:text-[#0b1c30] p-1 rounded cursor-pointer">
                  <MoreVertical className="w-4 h-4" />
                </button>
              </div>

              {/* Product Info Row */}
              <div
                onClick={() => onSelectProduct(product)}
                className="flex gap-4 items-center cursor-pointer group"
              >
                <div className="w-16 h-16 rounded-lg bg-[#eff4ff] border border-[#e2e8f0] overflow-hidden shrink-0 p-1 flex items-center justify-center">
                  <img
                    src={alert.imageUrl}
                    alt={alert.productName}
                    className="w-full h-full object-contain group-hover:scale-105 transition-transform"
                  />
                </div>
                <div>
                  <h3 className="font-bold text-sm text-[#0b1c30] group-hover:text-[#0051d5] transition-colors leading-snug">
                    {alert.productName}
                  </h3>
                  <p className="font-mono text-[11px] text-[#76777d] mt-0.5">
                    SKU: {alert.sku}
                  </p>
                </div>
              </div>

              {/* Deviation Details Container */}
              <div className="bg-[#f8f9ff] p-3.5 rounded-lg border border-[#e2e8f0] text-xs">
                <div className="flex justify-between items-baseline mb-1.5">
                  <span className="text-[#76777d] font-medium">
                    {alert.metricTitle}
                  </span>
                  <span
                    className={`font-mono font-bold ${
                      alert.severity === 'critical'
                        ? 'text-[#ba1a1a]'
                        : alert.severity === 'warning'
                        ? 'text-amber-700'
                        : 'text-[#0051d5]'
                    }`}
                  >
                    {alert.metricBadge}
                  </span>
                </div>

                {alert.type === 'price_drop' && alert.oldPrice && alert.newPrice ? (
                  <div className="flex items-center gap-2 font-mono text-xs text-[#0b1c30]">
                    <span className="font-semibold">{alert.competitorName || 'Amazon'}</span>
                    <ArrowRight className="w-3.5 h-3.5 text-[#76777d]" />
                    <span className="line-through text-[#76777d]">
                      ${alert.oldPrice.toFixed(2)}
                    </span>
                    <span className="font-bold text-[#ba1a1a]">
                      ${alert.newPrice.toFixed(2)}
                    </span>
                  </div>
                ) : (
                  <div className="text-[#45464d] leading-relaxed">
                    {alert.description}
                  </div>
                )}
              </div>

              {/* Actions Footer */}
              <div className="flex gap-2 mt-auto pt-2">
                {alert.resolved ? (
                  <div className="w-full py-2 bg-emerald-50 text-emerald-700 font-mono text-xs font-bold rounded flex items-center justify-center gap-1.5 border border-emerald-200">
                    <Check className="w-3.5 h-3.5" />
                    <span>Resolved</span>
                  </div>
                ) : (
                  <>
                    {alert.severity === 'critical' && (
                      <button
                        onClick={() => handleAction(alert, 'Match Competitor Price')}
                        className="flex-1 px-3 py-2 bg-[#000000] text-white rounded font-mono text-xs font-semibold hover:bg-[#1f2937] active:scale-[0.98] transition-all cursor-pointer shadow-sm"
                      >
                        Match Price
                      </button>
                    )}

                    {alert.severity === 'warning' && (
                      <button
                        onClick={() => handleAction(alert, 'Adjust Margin Strategy')}
                        className="flex-1 px-3 py-2 bg-white text-[#0b1c30] border border-[#e2e8f0] rounded font-mono text-xs font-semibold hover:bg-gray-50 active:scale-[0.98] transition-all cursor-pointer shadow-sm"
                      >
                        Review Pricing
                      </button>
                    )}

                    {alert.severity === 'info' && (
                      <button
                        onClick={() => handleAction(alert, 'Increase Target Price')}
                        className="flex-1 px-3 py-2 bg-white text-[#0b1c30] border border-[#e2e8f0] rounded font-mono text-xs font-semibold hover:bg-gray-50 active:scale-[0.98] transition-all cursor-pointer shadow-sm"
                      >
                        View Opportunity
                      </button>
                    )}

                    <button
                      onClick={() => handleAction(alert, 'Dismissed')}
                      className="px-3 py-2 bg-transparent text-[#76777d] hover:text-[#0b1c30] hover:bg-gray-100 rounded font-mono text-xs font-medium transition-colors cursor-pointer"
                    >
                      Dismiss
                    </button>
                  </>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
