import React from 'react';
import {
  LayoutDashboard,
  Users,
  Sliders,
  TrendingUp,
  Package,
  FileBarChart2,
  Settings,
  HelpCircle,
  Bell,
  Sparkles,
  LogOut,
} from 'lucide-react';
import { ViewMode } from '../types';

interface SidebarProps {
  currentView: ViewMode;
  onNavigate: (view: ViewMode) => void;
  activeAlertsCount: number;
  unreadAlertsCount?: number;
  onOpenTrackModal?: () => void;
  onOpenUpgradeModal: () => void;
  isOpenMobile?: boolean;
  onCloseMobile?: () => void;
  onLogout?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentView,
  onNavigate,
  activeAlertsCount,
  unreadAlertsCount,
  onOpenTrackModal,
  onOpenUpgradeModal,
  isOpenMobile = false,
  onCloseMobile,
  onLogout,
}) => {
  const alertsCount = unreadAlertsCount ?? activeAlertsCount;
  const navItems = [
    {
      id: 'dashboard' as ViewMode,
      label: 'Dashboard',
      icon: LayoutDashboard,
    },
    {
      id: 'competitors' as ViewMode,
      label: 'Competitors',
      icon: Users,
    },
    {
      id: 'price-rules' as ViewMode,
      label: 'Price Rules',
      icon: Sliders,
    },
    {
      id: 'market-grid' as ViewMode,
      label: 'Market Trends',
      icon: TrendingUp,
    },
    {
      id: 'inventory' as ViewMode,
      label: 'Inventory',
      icon: Package,
    },
    {
      id: 'alerts' as ViewMode,
      label: 'Alerts Inbox',
      icon: Bell,
      badge: alertsCount,
    },
    {
      id: 'reports' as ViewMode,
      label: 'Reports',
      icon: FileBarChart2,
    },
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpenMobile && (
        <div
          onClick={onCloseMobile}
          className="fixed inset-0 bg-black/60 backdrop-blur-xs z-40 md:hidden"
        />
      )}

      <nav
        id="main-sidebar"
        className={`bg-[#000000] text-white fixed left-0 top-0 h-screen w-[240px] border-r border-[#1e293b] flex flex-col py-6 z-50 select-none shadow-2xl transition-transform duration-300 ${
          isOpenMobile ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
      {/* Brand Header */}
      <div
        className="px-6 mb-6 flex items-center gap-3 cursor-pointer group"
        onClick={() => onNavigate('dashboard')}
      >
        <img
          alt="Priceloop AI Logo"
          className="w-8 h-8 rounded-sm object-cover group-hover:scale-105 transition-transform"
          src="https://lh3.googleusercontent.com/aida/AEtjO1WQeqo6ixOTLdiEF8WsqcpSE05ALFPy_50Qf7a7m4nLgudZXyVHq3vBpIYIBNIjPeXbr27D0kplf29DB2KNZLVyrjXL5ees3VfuoXCH5NljZeCDv7qbM5H0oP3ziEXMRCGVckOP2max54Vt391XrDr3pHVZUq5rCz-bIvcI95arFOo4tkbFhZldYDRZujo5rc-y02hTJw-PcbMLAoqJ55dOGJdnhPZg11YFNF9fUwJNAq4fi0o5Drl4PQ4"
        />
        <div>
          <h1 className="font-bold text-white text-[19px] leading-tight tracking-tight">
            Priceloop AI
          </h1>
          <p className="text-[#94a3b8] text-[11px] font-medium tracking-wide">
            Intelligence Platform
          </p>
        </div>
      </div>

      {/* Nav List */}
      <div className="flex-1 overflow-y-auto px-2 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive =
            currentView === item.id ||
            (item.id === 'market-grid' && currentView === 'product-detail');

          return (
            <button
              key={item.id}
              id={`nav-${item.id}`}
              onClick={() => onNavigate(item.id)}
              className={`w-full text-left px-4 py-3 rounded-r-md flex items-center justify-between text-sm transition-all duration-150 cursor-pointer ${
                isActive
                  ? 'border-l-4 border-[#0051d5] bg-[#316bf3]/15 text-white font-bold'
                  : 'text-[#94a3b8] hover:text-white hover:bg-white/5 font-normal'
              }`}
            >
              <div className="flex items-center gap-3.5">
                <Icon
                  className={`w-[18px] h-[18px] ${
                    isActive ? 'text-[#3b82f6]' : 'text-[#94a3b8]'
                  }`}
                />
                <span>{item.label}</span>
              </div>
              {item.badge !== undefined && item.badge > 0 && (
                <span className="bg-[#ba1a1a] text-white text-[10px] font-mono font-bold px-1.5 py-0.5 rounded-full">
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Bottom Upgrade and Utility */}
      <div className="mt-auto px-4 pt-4 border-t border-[#1e293b]/60">
        <button
          id="sidebar-upgrade-button"
          onClick={onOpenUpgradeModal}
          className="w-full bg-[#0051d5] hover:bg-[#0042b0] active:scale-[0.98] text-white font-semibold py-2.5 px-3 rounded-lg transition-colors mb-4 text-xs flex items-center justify-center gap-2 shadow-md cursor-pointer"
        >
          <Sparkles className="w-4 h-4 text-sky-200" />
          <span>Upgrade Plan</span>
        </button>

        <div className="space-y-1">
          <button
            id="nav-settings"
            onClick={() => onNavigate('settings')}
            className={`w-full text-left px-3 py-2 rounded flex items-center gap-3 text-xs transition-colors cursor-pointer ${
              currentView === 'settings'
                ? 'text-white font-bold bg-white/10'
                : 'text-[#94a3b8] hover:text-white hover:bg-white/5'
            }`}
          >
            <Settings className="w-4 h-4 text-[#94a3b8]" />
            <span>Settings</span>
          </button>
          <button
            id="nav-support"
            onClick={() => onNavigate('settings')}
            className="w-full text-left px-3 py-2 rounded flex items-center gap-3 text-xs text-[#94a3b8] hover:text-white hover:bg-white/5 transition-colors cursor-pointer"
          >
            <HelpCircle className="w-4 h-4 text-[#94a3b8]" />
            <span>Support</span>
          </button>
          {onLogout && (
            <button
              id="nav-logout"
              onClick={onLogout}
              className="w-full text-left px-3 py-2 rounded flex items-center gap-3 text-xs text-[#94a3b8] hover:text-white hover:bg-white/5 transition-colors cursor-pointer"
            >
              <LogOut className="w-4 h-4 text-[#94a3b8]" />
              <span>Log out</span>
            </button>
          )}
        </div>
      </div>
    </nav>
    </>
  );
};
