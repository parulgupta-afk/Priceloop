import React, { useState, useRef, useEffect } from 'react';
import {
  Search,
  Bell,
  History,
  Menu,
  X,
  Play,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  TrendingUp,
} from 'lucide-react';
import { AlertItem, Product, ViewMode } from '../types';

interface TopBarProps {
  currentView?: ViewMode;
  onNavigate?: (view: ViewMode) => void;
  searchQuery: string;
  onSearchChange: (q: string) => void;
  alerts?: AlertItem[];
  products?: Product[];
  unreadAlertsCount?: number;
  onSelectProduct?: (product: Product) => void;
  onSelectAlert?: (alert: AlertItem) => void;
  onReplayIntro?: () => void;
  onToggleMobileMenu?: () => void;
  isMobileMenuOpen?: boolean;
  onOpenHistoryModal?: () => void;
  onOpenUpgradeModal?: () => void;
}

export const TopBar: React.FC<TopBarProps> = ({
  currentView = 'dashboard',
  onNavigate,
  searchQuery,
  onSearchChange,
  alerts = [],
  products = [],
  unreadAlertsCount,
  onSelectProduct,
  onSelectAlert,
  onReplayIntro,
  onToggleMobileMenu,
  isMobileMenuOpen = false,
  onOpenHistoryModal,
  onOpenUpgradeModal,
}) => {
  const [isAlertsOpen, setIsAlertsOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [isSearchFocused, setIsSearchFocused] = useState(false);

  const alertsRef = useRef<HTMLDivElement>(null);
  const profileRef = useRef<HTMLDivElement>(null);
  const searchRef = useRef<HTMLDivElement>(null);

  // Close dropdowns on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (alertsRef.current && !alertsRef.current.contains(e.target as Node)) {
        setIsAlertsOpen(false);
      }
      if (profileRef.current && !profileRef.current.contains(e.target as Node)) {
        setIsProfileOpen(false);
      }
      if (searchRef.current && !searchRef.current.contains(e.target as Node)) {
        setIsSearchFocused(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const unreadAlerts = alerts.filter((a) => !a.resolved);

  const searchResults = searchQuery.trim()
    ? products.filter(
        (p) =>
          p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          p.sku.toLowerCase().includes(searchQuery.toLowerCase()) ||
          p.category.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : [];

  return (
    <header
      id="app-topbar"
      className="bg-[#f8f9ff] md:bg-white fixed top-0 right-0 w-full md:w-[calc(100%-240px)] z-40 border-b border-[#e2e8f0] flex justify-between items-center h-16 px-4 md:px-8 transition-all"
    >
      {/* Mobile Menu Button & Brand */}
      <div className="flex items-center gap-3 md:hidden">
        <button
          id="mobile-menu-toggle"
          onClick={onToggleMobileMenu}
          className="p-2 text-[#0b1c30] hover:bg-[#eff4ff] rounded-md transition-colors"
          aria-label="Toggle menu"
        >
          {isMobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
        <div className="flex items-center gap-2">
          <img
            alt="Priceloop Logo"
            className="w-7 h-7 rounded object-contain"
            src="https://lh3.googleusercontent.com/aida/AEtjO1WQeqo6ixOTLdiEF8WsqcpSE05ALFPy_50Qf7a7m4nLgudZXyVHq3vBpIYIBNIjPeXbr27D0kplf29DB2KNZLVyrjXL5ees3VfuoXCH5NljZeCDv7qbM5H0oP3ziEXMRCGVckOP2max54Vt391XrDr3pHVZUq5rCz-bIvcI95arFOo4tkbFhZldYDRZujo5rc-y02hTJw-PcbMLAoqJ55dOGJdnhPZg11YFNF9fUwJNAq4fi0o5Drl4PQ4"
          />
          <span className="font-bold text-sm tracking-tight text-[#0b1c30]">
            Priceloop AI
          </span>
        </div>
      </div>

      {/* Search Bar with live autocomplete */}
      <div ref={searchRef} className="relative w-full max-w-md hidden sm:block">
        <div className="relative">
          <Search className="w-4 h-4 text-[#76777d] absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            id="topbar-search-input"
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            onFocus={() => setIsSearchFocused(true)}
            placeholder="Search products, SKUs, rules..."
            className="w-full pl-9 pr-4 py-2 bg-[#ffffff] border border-[#e2e8f0] focus:border-[#0051d5] focus:ring-1 focus:ring-[#0051d5] rounded-lg text-xs md:text-sm text-[#0b1c30] placeholder-[#76777d] transition-all outline-none"
          />
          {searchQuery && (
            <button
              onClick={() => onSearchChange('')}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 p-1"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Live Search Popup */}
        {isSearchFocused && searchQuery.trim().length > 0 && (
          <div className="absolute left-0 right-0 top-full mt-1.5 bg-white border border-[#e2e8f0] rounded-xl shadow-xl z-50 overflow-hidden max-h-80 overflow-y-auto divide-y divide-gray-100">
            <div className="p-2 text-[11px] font-mono font-medium text-gray-400 bg-gray-50 uppercase tracking-wider">
              Matching Products ({searchResults.length})
            </div>
            {searchResults.length > 0 ? (
              searchResults.map((product) => (
                <div
                  key={product.id}
                  onClick={() => {
                    onSelectProduct(product);
                    setIsSearchFocused(false);
                    onSearchChange('');
                  }}
                  className="p-3 hover:bg-[#eff4ff] cursor-pointer flex items-center justify-between transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <img
                      src={product.imageUrl}
                      alt={product.name}
                      className="w-8 h-8 rounded object-cover border border-gray-100"
                    />
                    <div>
                      <div className="text-sm font-semibold text-[#0b1c30]">
                        {product.name}
                      </div>
                      <div className="text-xs text-[#76777d] font-mono">
                        {product.sku}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-mono font-bold text-[#0051d5]">
                      ${product.targetPrice.toFixed(2)}
                    </div>
                    <div className="text-[11px] text-emerald-600 font-medium">
                      {product.marketPositionLabel}
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="p-4 text-center text-xs text-gray-500">
                No matching products found for "{searchQuery}"
              </div>
            )}
          </div>
        )}
      </div>

      {/* Right Action Icons */}
      <div className="flex items-center space-x-2 md:space-x-4">
        {/* Notifications & Active Alerts Popover */}
        <div ref={alertsRef} className="relative">
          <button
            id="notifications-bell-btn"
            onClick={() => setIsAlertsOpen(!isAlertsOpen)}
            className="text-[#45464d] hover:bg-[#eff4ff] p-2.5 rounded-full transition-colors relative cursor-pointer"
            aria-label="Alerts"
          >
            <Bell className="w-5 h-5" />
            {unreadAlerts.length > 0 && (
              <span className="absolute top-1.5 right-1.5 w-2.5 h-2.5 bg-[#ba1a1a] rounded-full ring-2 ring-white" />
            )}
          </button>

          {isAlertsOpen && (
            <div className="absolute right-0 top-full mt-2 w-80 sm:w-96 bg-white rounded-xl shadow-2xl border border-[#e2e8f0] z-50 overflow-hidden animate-in fade-in slide-in-from-top-2 duration-150">
              <div className="p-4 bg-[#f8f9ff] border-b border-[#e2e8f0] flex justify-between items-center">
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-sm text-[#0b1c30]">
                    Pricing Alerts
                  </span>
                  <span className="bg-[#ffdad6] text-[#ba1a1a] text-xs font-mono font-bold px-2 py-0.5 rounded-full">
                    {unreadAlerts.length} Active
                  </span>
                </div>
                <button
                  onClick={() => setIsAlertsOpen(false)}
                  className="text-xs text-[#0051d5] font-semibold hover:underline cursor-pointer"
                >
                  Close
                </button>
              </div>

              <div className="max-h-80 overflow-y-auto divide-y divide-gray-100">
                {alerts.slice(0, 4).map((alert) => (
                  <div
                    key={alert.id}
                    onClick={() => {
                      onSelectAlert(alert);
                      setIsAlertsOpen(false);
                    }}
                    className={`p-3.5 hover:bg-[#eff4ff] cursor-pointer transition-colors ${
                      alert.resolved ? 'opacity-60' : ''
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2 mb-1">
                      <span
                        className={`text-[10px] font-mono uppercase px-1.5 py-0.5 rounded font-bold ${
                          alert.severity === 'critical'
                            ? 'bg-red-100 text-red-700'
                            : alert.severity === 'warning'
                            ? 'bg-amber-100 text-amber-700'
                            : 'bg-blue-100 text-blue-700'
                        }`}
                      >
                        {alert.severity}
                      </span>
                      <span className="text-[11px] text-gray-400 font-mono">
                        {alert.timeAgo}
                      </span>
                    </div>
                    <div className="text-xs font-semibold text-[#0b1c30]">
                      {alert.productName}
                    </div>
                    <p className="text-[11px] text-gray-600 mt-0.5 line-clamp-2">
                      {alert.description}
                    </p>
                  </div>
                ))}
              </div>

              <div className="p-3 bg-gray-50 border-t border-[#e2e8f0] text-center">
                <button
                  onClick={() => {
                    setIsAlertsOpen(false);
                    if (onNavigate) {
                      onNavigate('alerts');
                    }
                  }}
                  className="text-xs text-[#0051d5] font-bold hover:underline inline-flex items-center gap-1 cursor-pointer"
                >
                  View All Alerts in Inbox <ArrowRight className="w-3 h-3" />
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Audit Log / History Button */}
        <button
          id="audit-history-btn"
          onClick={onOpenHistoryModal}
          className="text-[#45464d] hover:bg-[#eff4ff] p-2.5 rounded-full transition-colors cursor-pointer"
          title="Audit Log & History"
        >
          <History className="w-5 h-5" />
        </button>

        {/* Profile Avatar & Menu */}
        <div ref={profileRef} className="relative">
          <button
            id="profile-avatar-btn"
            onClick={() => setIsProfileOpen(!isProfileOpen)}
            className="flex items-center gap-2 p-1 rounded-full hover:ring-2 hover:ring-[#0051d5]/30 transition-all cursor-pointer"
          >
            <img
              alt="Pricing Analyst Profile"
              className="w-8 h-8 rounded-full border border-[#c6c6cd] object-cover"
              src="https://lh3.googleusercontent.com/aida-public/AB6AXuCYB-6U3ISjOSChzqmmy91DL2zQNSA-X5-tbGniQltU-sT8BRpS4NlI5nqi5bAEmb7_KpYa-VrwHZ9Duw02m5vf6kwI-ddCk_mN8DOdHWOFdg4kMN4YYu_gQJDXgOZOAVH04eLrPgEDsa_pbqcA_Hw8td6yLYjjHxTKNd63Gi4hSPLU9zecatoC0p3_nk-JsaiXSs8JvKb2cIatSMTAq1h8ff4moVnrXQwV6soYAuu9epdlIpx_33b-lQ"
            />
          </button>

          {isProfileOpen && (
            <div className="absolute right-0 top-full mt-2 w-64 bg-white rounded-xl shadow-2xl border border-[#e2e8f0] z-50 p-2 divide-y divide-gray-100 animate-in fade-in slide-in-from-top-2 duration-150">
              <div className="p-3">
                <div className="font-bold text-sm text-[#0b1c30]">
                  Parul Mahajan
                </div>
                <div className="text-xs text-gray-500">
                  Lead Pricing Strategist
                </div>
                <div className="mt-2 inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 text-[10px] font-mono font-medium border border-emerald-200">
                  <CheckCircle2 className="w-3 h-3 text-emerald-600" /> Enterprise Live
                </div>
              </div>

              <div className="py-1">
                <button
                  onClick={() => {
                    setIsProfileOpen(false);
                    onReplayIntro();
                  }}
                  className="w-full text-left px-3 py-2 text-xs text-gray-700 hover:bg-[#eff4ff] rounded-md flex items-center gap-2 cursor-pointer"
                >
                  <Play className="w-3.5 h-3.5 text-[#0051d5]" />
                  <span>Replay Intro Animation</span>
                </button>
                <button
                  onClick={() => {
                    setIsProfileOpen(false);
                    onOpenHistoryModal();
                  }}
                  className="w-full text-left px-3 py-2 text-xs text-gray-700 hover:bg-[#eff4ff] rounded-md flex items-center gap-2 cursor-pointer"
                >
                  <History className="w-3.5 h-3.5 text-gray-500" />
                  <span>Repricing Audit Log</span>
                </button>
              </div>

              <div className="p-2 text-[11px] text-gray-400 font-mono text-center">
                Priceloop v4.2.8 Enterprise
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
