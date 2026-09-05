import React, { useState, useEffect, useMemo } from 'react';
import { ViewMode, Product, AlertItem, PriceRule } from './types';
import {
  INITIAL_PRODUCTS,
  INITIAL_ALERTS,
  INITIAL_RULES,
  MARKET_STATS,
} from './data/mockData';
import { IntroScreen } from './components/IntroScreen';
import { Sidebar } from './components/Sidebar';
import { TopBar } from './components/TopBar';
import { DashboardView } from './components/DashboardView';
import { MarketGridView } from './components/MarketGridView';
import { ProductDetailView } from './components/ProductDetailView';
import { AlertsInboxView } from './components/AlertsInboxView';
import { CompetitorsView } from './components/CompetitorsView';
import { PriceRulesView } from './components/PriceRulesView';
import { SettingsView } from './components/SettingsView';
import { TrackProductModal } from './components/TrackProductModal';
import { AdjustStrategyModal } from './components/AdjustStrategyModal';
import { SetAlertModal } from './components/SetAlertModal';
import { UpgradePlanModal } from './components/UpgradePlanModal';
import { HistoryModal } from './components/HistoryModal';
import { AuthScreen } from './components/AuthScreen';
import { useAuth } from './context/AuthContext';

export default function App() {
  const { user, isLoading, logout } = useAuth();

  const [currentView, setCurrentView] = useState<ViewMode>('intro');
  const [products, setProducts] = useState<Product[]>(() => {
    const saved = localStorage.getItem('priceloop_products');
    return saved ? JSON.parse(saved) : INITIAL_PRODUCTS;
  });
  const [selectedProduct, setSelectedProduct] = useState<Product>(products[0] || INITIAL_PRODUCTS[0]);
  const [alerts, setAlerts] = useState<AlertItem[]>(() => {
    const saved = localStorage.getItem('priceloop_alerts');
    return saved ? JSON.parse(saved) : INITIAL_ALERTS;
  });
  const [priceRules, setPriceRules] = useState<PriceRule[]>(() => {
    const saved = localStorage.getItem('priceloop_rules');
    return saved ? JSON.parse(saved) : INITIAL_RULES;
  });

  const [searchQuery, setSearchQuery] = useState('');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Modal states
  const [isTrackModalOpen, setIsTrackModalOpen] = useState(false);
  const [isStrategyModalOpen, setIsStrategyModalOpen] = useState(false);
  const [isAlertModalOpen, setIsAlertModalOpen] = useState(false);
  const [isUpgradeModalOpen, setIsUpgradeModalOpen] = useState(false);
  const [isHistoryModalOpen, setIsHistoryModalOpen] = useState(false);

  // Persist data in localStorage
  useEffect(() => {
    localStorage.setItem('priceloop_products', JSON.stringify(products));
  }, [products]);

  useEffect(() => {
    localStorage.setItem('priceloop_alerts', JSON.stringify(alerts));
  }, [alerts]);

  useEffect(() => {
    localStorage.setItem('priceloop_rules', JSON.stringify(priceRules));
  }, [priceRules]);

  // Derived filtered products based on search
  const searchedProducts = useMemo(() => {
    if (!searchQuery.trim()) return products;
    return products.filter(
      (p) =>
        p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        p.sku.toLowerCase().includes(searchQuery.toLowerCase()) ||
        p.category.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [products, searchQuery]);

  // Handle selecting a product to view in detail
  const handleSelectProduct = (product: Product) => {
    setSelectedProduct(product);
    setCurrentView('product-detail');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Handle adding a newly tracked product from modal
  const handleAddProduct = (newProd: Product) => {
    setProducts((prev) => [newProd, ...prev]);
    setSelectedProduct(newProd);
  };

  // Handle bookmark toggle
  const handleToggleBookmark = (productId: string) => {
    setProducts((prev) =>
      prev.map((p) =>
        p.id === productId ? { ...p, isBookmarked: !p.isBookmarked } : p
      )
    );
    if (selectedProduct.id === productId) {
      setSelectedProduct((prev) => ({
        ...prev,
        isBookmarked: !prev.isBookmarked,
      }));
    }
  };

  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const showToast = (message: string) => {
    setToastMessage(message);
    setTimeout(() => {
      setToastMessage((cur) => (cur === message ? null : cur));
    }, 4000);
  };

  // Handle saving adjusted strategy
  const handleSaveStrategy = (
    productId: string,
    newTargetPrice: number,
    strategyName: string
  ) => {
    setProducts((prev) =>
      prev.map((p) => {
        if (p.id === productId) {
          const deltaAmount = newTargetPrice - p.marketAvg;
          const deltaPercent = Number(
            ((deltaAmount / p.marketAvg) * 100).toFixed(1)
          );
          return {
            ...p,
            targetPrice: newTargetPrice,
            priceDeltaAmount: deltaAmount,
            priceDeltaPercent: deltaPercent,
            priceChangeDirection:
              newTargetPrice < p.marketAvg
                ? 'down'
                : newTargetPrice > p.marketAvg
                ? 'up'
                : 'neutral',
            aiInsight: {
              ...p.aiInsight,
              description: `Repriced via ${strategyName}. Target updated to $${newTargetPrice.toFixed(
                2
              )}.`,
            },
          };
        }
        return p;
      })
    );

    if (selectedProduct.id === productId) {
      setSelectedProduct((prev) => ({
        ...prev,
        targetPrice: newTargetPrice,
        priceDeltaAmount: newTargetPrice - prev.marketAvg,
        priceDeltaPercent: Number(
          (((newTargetPrice - prev.marketAvg) / prev.marketAvg) * 100).toFixed(
            1
          )
        ),
      }));
    }
  };

  // Handle resolving an alert
  const handleResolveAlert = (alertId: string, actionName: string) => {
    setAlerts((prev) =>
      prev.map((a) => (a.id === alertId ? { ...a, resolved: true } : a))
    );

    const alert = alerts.find((a) => a.id === alertId);
    if (alert && alert.newPrice && actionName.includes('Match')) {
      handleSaveStrategy(alert.productId, alert.newPrice, 'Alert Quick Match');
    }
  };

  // Handle toggling repricing rule
  const handleToggleRule = (ruleId: string) => {
    setPriceRules((prev) =>
      prev.map((r) =>
        r.id === ruleId
          ? { ...r, status: r.status === 'active' ? 'paused' : 'active' }
          : r
      )
    );
  };

  // Handle adding new repricing rule
  const handleAddRule = (newRule: PriceRule) => {
    setPriceRules((prev) => [newRule, ...prev]);
  };

  // Auth gate: while checking a stored token, show nothing jarring; if
  // there's no valid session, show the real login/signup screen instead of
  // the dashboard. Everything below this point only renders once `user` is set.
  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#f8f9ff] flex items-center justify-center">
        <div className="w-6 h-6 border-2 border-[#0051d5] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!user) {
    return <AuthScreen />;
  }

  // If Intro Screen is active
  if (currentView === 'intro') {
    return (
      <IntroScreen
        onEnterDashboard={() => {
          setCurrentView('dashboard');
          window.scrollTo({ top: 0, behavior: 'instant' });
        }}
      />
    );
  }

  return (
    <div className="min-h-screen bg-[#f8f9ff] text-[#0b1c30] flex flex-col md:flex-row antialiased">
      {/* Navigation Sidebar */}
      <Sidebar
        currentView={currentView}
        onNavigate={(view) => {
          setCurrentView(view);
          setIsMobileMenuOpen(false);
          window.scrollTo({ top: 0, behavior: 'smooth' });
        }}
        unreadAlertsCount={alerts.filter((a) => !a.resolved).length}
        onOpenTrackModal={() => setIsTrackModalOpen(true)}
        onOpenUpgradeModal={() => setIsUpgradeModalOpen(true)}
        isOpenMobile={isMobileMenuOpen}
        onCloseMobile={() => setIsMobileMenuOpen(false)}
        onLogout={logout}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 md:ml-[240px]">
        {/* Top Header Navigation */}
        <TopBar
          currentView={currentView}
          onNavigate={(view) => {
            setCurrentView(view);
            window.scrollTo({ top: 0, behavior: 'smooth' });
          }}
          unreadAlertsCount={alerts.filter((a) => !a.resolved).length}
          alerts={alerts}
          products={products}
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          onSelectProduct={handleSelectProduct}
          onSelectAlert={(alert) => {
            const matchedProd = products.find((p) => p.id === alert.productId);
            if (matchedProd) {
              handleSelectProduct(matchedProd);
            } else {
              setCurrentView('alerts');
            }
          }}
          onToggleMobileMenu={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          onOpenHistoryModal={() => setIsHistoryModalOpen(true)}
          onOpenUpgradeModal={() => setIsUpgradeModalOpen(true)}
          onReplayIntro={() => setCurrentView('intro')}
        />

        {/* Dynamic Main Workspace */}
        <main className="flex-1 mt-16 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto">
          {currentView === 'dashboard' && (
            <DashboardView
              products={searchedProducts}
              marketStats={MARKET_STATS}
              stats={MARKET_STATS}
              activeAlertsCount={alerts.filter((a) => !a.resolved).length}
              onOpenAddProductModal={() => setIsTrackModalOpen(true)}
              onSelectProduct={handleSelectProduct}
              onViewAllDynamics={() => setCurrentView('market-grid')}
              onNavigate={setCurrentView}
            />
          )}

          {currentView === 'market-grid' && (
            <MarketGridView
              products={searchedProducts}
              onSelectProduct={handleSelectProduct}
            />
          )}

          {currentView === 'product-detail' && (
            <ProductDetailView
              product={selectedProduct}
              onBack={() => setCurrentView('dashboard')}
              onOpenAlertModal={() => setIsAlertModalOpen(true)}
              onOpenStrategyModal={() => setIsStrategyModalOpen(true)}
              onToggleBookmark={handleToggleBookmark}
            />
          )}

          {currentView === 'alerts' && (
            <AlertsInboxView
              alerts={alerts}
              products={products}
              onSelectProduct={handleSelectProduct}
              onResolveAlert={handleResolveAlert}
              onOpenNewRuleModal={() => setCurrentView('price-rules')}
            />
          )}

          {currentView === 'competitors' && (
            <CompetitorsView
              products={searchedProducts}
              onSelectProduct={handleSelectProduct}
            />
          )}

          {currentView === 'price-rules' && (
            <PriceRulesView
              rules={priceRules}
              onToggleRule={handleToggleRule}
              onAddRule={handleAddRule}
            />
          )}

          {currentView === 'inventory' && (
            <MarketGridView
              products={searchedProducts}
              onSelectProduct={handleSelectProduct}
            />
          )}

          {currentView === 'reports' && (
            <CompetitorsView
              products={searchedProducts}
              onSelectProduct={handleSelectProduct}
            />
          )}

          {currentView === 'settings' && <SettingsView />}
        </main>
      </div>

      {/* Modals Container */}
      <TrackProductModal
        isOpen={isTrackModalOpen}
        onClose={() => setIsTrackModalOpen(false)}
        onAddProduct={handleAddProduct}
      />

      <AdjustStrategyModal
        product={selectedProduct}
        isOpen={isStrategyModalOpen}
        onClose={() => setIsStrategyModalOpen(false)}
        onSaveStrategy={handleSaveStrategy}
      />

      <SetAlertModal
        product={selectedProduct}
        isOpen={isAlertModalOpen}
        onClose={() => setIsAlertModalOpen(false)}
        onSaveAlert={(config) => {
          showToast(
            `Alert trigger configured: ±${config.thresholdPercent}% threshold enabled for ${selectedProduct.name}.`
          );
        }}
      />

      <UpgradePlanModal
        isOpen={isUpgradeModalOpen}
        onClose={() => setIsUpgradeModalOpen(false)}
      />

      <HistoryModal
        isOpen={isHistoryModalOpen}
        onClose={() => setIsHistoryModalOpen(false)}
      />

      {/* Floating Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 bg-[#0b1c30] text-white px-5 py-3 rounded-xl shadow-2xl border border-gray-700 flex items-center gap-3 animate-in fade-in slide-in-from-bottom-4 duration-200">
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-xs sm:text-sm font-medium">{toastMessage}</span>
          <button
            onClick={() => setToastMessage(null)}
            className="text-gray-400 hover:text-white text-xs ml-2 cursor-pointer font-bold"
          >
            ✕
          </button>
        </div>
      )}
    </div>
  );
}
