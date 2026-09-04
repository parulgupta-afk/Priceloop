import React, { useState } from 'react';
import {
  X,
  ArrowRight,
  Info,
  CheckCircle2,
  Loader2,
  Sparkles,
  Store,
  Sliders,
  DollarSign,
} from 'lucide-react';
import confetti from 'canvas-confetti';
import { Product } from '../types';

interface TrackProductModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAddProduct: (product: Product) => void;
}

export const TrackProductModal: React.FC<TrackProductModalProps> = ({
  isOpen,
  onClose,
  onAddProduct,
}) => {
  const [step, setStep] = useState<1 | 2 | 3>(1);
  const [url, setUrl] = useState(
    'https://www.amazon.com/Sony-WH-1000XM5-Canceling-Headphones-Hands-Free/dp/B09XS7JWHH'
  );
  const [isDetecting, setIsDetecting] = useState(false);

  // Detected product state
  const [detectedData, setDetectedData] = useState<{
    name: string;
    subtitle: string;
    sku: string;
    category: string;
    detectedPrice: number;
    marketAvg: number;
    cogs: number;
    strategy: 'cheapest' | 'margin' | 'match';
    selectedCompetitors: string[];
    imageUrl: string;
  }>({
    name: 'Sony WH-1000XM5',
    subtitle: 'Wireless Noise Canceling Headphones',
    sku: 'SNY-WH-XM5-BLK',
    category: 'Audio',
    detectedPrice: 348.0,
    marketAvg: 356.5,
    cogs: 280.0,
    strategy: 'cheapest',
    selectedCompetitors: ['Amazon', 'Best Buy', 'Walmart', 'Target'],
    imageUrl:
      'https://lh3.googleusercontent.com/aida-public/AB6AXuBODxHXjK6zaDsj2gca4i_ziO3XDScngP-BHs2bma1YXAscGkZp-mnunpNFr_-bcg_BSt6o9axTD-uySCFkRxzg8TRqY-QchJTgElan8Uc2N_evYVUzXdystiJXMtMFnaFiEUhFIwdUXwksfzN4Skx_efWFOPpn3N44xB39kDEboha3M0gIYohVB1pmwn-wfQmo_I7EvSiFCcP6A6Z86WFkkegOLOdEABDwG0SNl4WIJf3Ap_GMyVvyeA',
  });

  if (!isOpen) return null;

  const handleStartAutoDetect = () => {
    setIsDetecting(true);
    // Simulate smart AI web scraper & intelligence resolution
    setTimeout(() => {
      setIsDetecting(false);
      setStep(2);
    }, 1200);
  };

  const handleCompleteTracking = () => {
    const newProduct: Product = {
      id: 'prod-' + Date.now(),
      name: detectedData.name,
      subtitle: detectedData.subtitle,
      sku: detectedData.sku || 'SKU-' + Math.floor(1000 + Math.random() * 9000),
      category: detectedData.category,
      imageUrl: detectedData.imageUrl,
      targetPrice: detectedData.detectedPrice,
      marketAvg: detectedData.marketAvg,
      priceDeltaAmount: detectedData.detectedPrice - detectedData.marketAvg,
      priceDeltaPercent: Number(
        (
          ((detectedData.detectedPrice - detectedData.marketAvg) /
            detectedData.marketAvg) *
          100
        ).toFixed(1)
      ),
      priceChangeDirection:
        detectedData.detectedPrice < detectedData.marketAvg ? 'down' : 'up',
      minPrice: detectedData.detectedPrice * 0.9,
      maxPrice: detectedData.marketAvg * 1.1,
      marketPositionRank: 1,
      marketPositionTotal: 6,
      marketPositionLabel: '#1 Cheapest',
      aiSentiment: 'Bullish',
      aiInsight: {
        type: 'optimal_price',
        title: 'Optimal Price Active',
        description:
          'Newly tracked item is competitively positioned against 4 verified marketplace feeds.',
      },
      cogs: detectedData.cogs,
      marginPercent: Number(
        (
          ((detectedData.detectedPrice - detectedData.cogs) /
            detectedData.detectedPrice) *
          100
        ).toFixed(1)
      ),
      inventoryUnits: 250,
      isBookmarked: true,
      competitors: [
        {
          id: 'c1',
          name: 'Amazon',
          shortCode: 'A',
          inStock: true,
          stockStatus: 'In Stock',
          shipping: 'Free',
          price: detectedData.detectedPrice,
          deltaText: 'Match',
          isMatch: true,
          lastUpdated: 'Just now',
        },
        {
          id: 'c2',
          name: 'Best Buy',
          shortCode: 'BB',
          inStock: true,
          stockStatus: 'In Stock',
          shipping: 'Pickup Avail',
          price: detectedData.detectedPrice + 1.99,
          deltaText: '+$1.99',
          lastUpdated: 'Just now',
        },
        {
          id: 'c3',
          name: 'Walmart',
          shortCode: 'W',
          inStock: true,
          stockStatus: 'Low Stock',
          shipping: '+$5.99',
          price: detectedData.detectedPrice + 7.0,
          deltaText: '+$7.00',
          lastUpdated: 'Just now',
        },
      ],
      priceHistory: [
        {
          date: 'Jul 1',
          targetPrice: detectedData.detectedPrice + 20,
          marketAvg: detectedData.marketAvg + 15,
          competitorMin: detectedData.detectedPrice + 15,
        },
        {
          date: 'Jul 15',
          targetPrice: detectedData.detectedPrice + 10,
          marketAvg: detectedData.marketAvg + 8,
          competitorMin: detectedData.detectedPrice + 5,
        },
        {
          date: 'Jul 30',
          targetPrice: detectedData.detectedPrice,
          marketAvg: detectedData.marketAvg,
          competitorMin: detectedData.detectedPrice,
        },
      ],
    };

    onAddProduct(newProduct);
    setStep(3);

    try {
      confetti({
        particleCount: 80,
        spread: 70,
        origin: { y: 0.6 },
      });
    } catch {
      // safe fallback
    }
  };

  const handleResetAndClose = () => {
    setStep(1);
    onClose();
  };

  return (
    <div
      id="track-product-modal"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200"
    >
      <div className="w-full max-w-3xl bg-white rounded-xl border border-[#e2e8f0] shadow-2xl overflow-hidden flex flex-col md:flex-row relative">
        {/* Close Button Top Right */}
        <button
          onClick={handleResetAndClose}
          className="absolute right-4 top-4 text-[#76777d] hover:text-[#0b1c30] p-1.5 rounded-full hover:bg-gray-100 z-20 cursor-pointer transition-colors"
          aria-label="Close"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Left Side: Branding & Multi-step Progress */}
        <div className="bg-[#eff4ff] p-8 border-b md:border-b-0 md:border-r border-[#e2e8f0] w-full md:w-1/3 flex flex-col">
          <div className="flex items-center gap-3 mb-10">
            <img
              alt="Priceloop Logo"
              className="w-8 h-8 rounded object-contain"
              src="https://lh3.googleusercontent.com/aida/AEtjO1WQeqo6ixOTLdiEF8WsqcpSE05ALFPy_50Qf7a7m4nLgudZXyVHq3vBpIYIBNIjPeXbr27D0kplf29DB2KNZLVyrjXL5ees3VfuoXCH5NljZeCDv7qbM5H0oP3ziEXMRCGVckOP2max54Vt391XrDr3pHVZUq5rCz-bIvcI95arFOo4tkbFhZldYDRZujo5rc-y02hTJw-PcbMLAoqJ55dOGJdnhPZg11YFNF9fUwJNAq4fi0o5Drl4PQ4"
            />
            <span className="font-bold text-sm tracking-tight text-[#0b1c30]">
              PRICEMIND
            </span>
          </div>

          <div className="flex flex-col gap-6 relative">
            {/* Step 1 */}
            <div className="flex items-start gap-4 relative z-10">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center font-mono text-xs font-bold transition-colors ${
                  step >= 1
                    ? 'bg-[#0051d5] text-white'
                    : 'bg-gray-200 text-gray-500'
                }`}
              >
                1
              </div>
              <div className="flex flex-col pt-0.5">
                <span className="text-xs font-bold text-[#0b1c30]">
                  Input Source
                </span>
                <span className="text-[11px] text-[#76777d]">
                  Provide product URL
                </span>
              </div>
            </div>

            {/* Line 1 */}
            <div
              className={`absolute left-4 top-8 bottom-0 w-px h-12 transition-colors ${
                step > 1 ? 'bg-[#0051d5]' : 'bg-[#e2e8f0]'
              }`}
            />

            {/* Step 2 */}
            <div
              className={`flex items-start gap-4 relative z-10 transition-opacity ${
                step >= 2 ? 'opacity-100' : 'opacity-40'
              }`}
            >
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center font-mono text-xs font-bold transition-colors ${
                  step >= 2
                    ? 'bg-[#0051d5] text-white'
                    : 'bg-[#d3e4fe] text-[#0051d5]'
                }`}
              >
                2
              </div>
              <div className="flex flex-col pt-0.5">
                <span className="text-xs font-bold text-[#0b1c30]">
                  Review Matches
                </span>
                <span className="text-[11px] text-[#76777d]">
                  Select variants to track
                </span>
              </div>
            </div>

            {/* Line 2 */}
            <div
              className={`absolute left-4 top-24 bottom-0 w-px h-12 transition-colors ${
                step >= 3 ? 'bg-[#0051d5]' : 'bg-[#e2e8f0]'
              }`}
            />

            {/* Step 3 */}
            <div
              className={`flex items-start gap-4 relative z-10 transition-opacity ${
                step === 3 ? 'opacity-100' : 'opacity-40'
              }`}
            >
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center font-mono text-xs font-bold transition-colors ${
                  step === 3
                    ? 'bg-[#0051d5] text-white'
                    : 'bg-[#d3e4fe] text-[#0051d5]'
                }`}
              >
                3
              </div>
              <div className="flex flex-col pt-0.5">
                <span className="text-xs font-bold text-[#0b1c30]">
                  Confirmation
                </span>
                <span className="text-[11px] text-[#76777d]">
                  Tracking initiated
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Side: Step Contents */}
        <div className="p-8 w-full md:w-2/3 flex flex-col justify-center min-h-[420px]">
          {/* STEP 1: Input URL */}
          {step === 1 && (
            <div className="space-y-6 animate-in fade-in duration-150">
              <div>
                <h1 className="text-2xl font-bold text-[#0b1c30] tracking-tight mb-1">
                  Track New Product
                </h1>
                <p className="text-xs sm:text-sm text-[#76777d] leading-relaxed">
                  Paste a URL from any major marketplace. Our intelligence engine will auto-detect variants and competitive listings.
                </p>
              </div>

              <div className="space-y-4">
                <div className="space-y-1.5">
                  <label
                    htmlFor="track-product-url"
                    className="font-mono text-xs text-[#76777d] uppercase tracking-wider block"
                  >
                    Source URL
                  </label>
                  <input
                    id="track-product-url"
                    type="url"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder="https://amazon.com/dp/..."
                    className="w-full bg-[#eff4ff]/60 border border-[#e2e8f0] focus:border-[#0051d5] focus:ring-1 focus:ring-[#0051d5] rounded-lg px-4 py-3 text-xs md:text-sm text-[#0b1c30] outline-none transition-all font-mono"
                  />
                </div>

                <div className="flex items-center gap-3 bg-[#eff4ff] p-4 rounded-lg border border-[#d3e4fe]">
                  <Info className="w-5 h-5 text-[#0051d5] shrink-0" />
                  <p className="text-xs text-[#45464d] leading-normal">
                    Supported platforms: Amazon, Walmart, Target, BestBuy, and 50+ regional retailers.
                  </p>
                </div>
              </div>

              <div className="pt-4 flex justify-end gap-3 border-t border-gray-100">
                <button
                  type="button"
                  onClick={handleResetAndClose}
                  className="px-5 py-2.5 rounded-lg border border-[#c6c6cd] text-[#45464d] text-xs font-semibold hover:bg-gray-50 transition-colors cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  id="auto-detect-btn"
                  type="button"
                  onClick={handleStartAutoDetect}
                  disabled={isDetecting || !url.trim()}
                  className="px-6 py-2.5 rounded-lg bg-[#000000] text-white text-xs font-semibold flex items-center gap-2 hover:bg-[#1f2937] active:scale-[0.98] transition-all cursor-pointer group shadow-sm disabled:opacity-50"
                >
                  {isDetecting ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin text-sky-300" />
                      <span>Detecting...</span>
                    </>
                  ) : (
                    <>
                      <span>Auto-detect</span>
                      <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                    </>
                  )}
                </button>
              </div>
            </div>
          )}

          {/* STEP 2: Review Matches */}
          {step === 2 && (
            <div className="space-y-5 animate-in fade-in duration-150">
              <div>
                <div className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 text-[10px] font-mono font-bold border border-emerald-200 mb-2">
                  <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                  Listing Scraped Successfully
                </div>
                <h2 className="text-xl font-bold text-[#0b1c30]">
                  Review Detected Product
                </h2>
              </div>

              {/* Scraped Product Preview Card */}
              <div className="bg-[#eff4ff]/60 border border-[#d3e4fe] rounded-xl p-4 flex gap-4 items-center">
                <img
                  src={detectedData.imageUrl}
                  alt={detectedData.name}
                  className="w-16 h-16 rounded-lg object-contain bg-white border border-gray-200 p-1"
                />
                <div className="flex-1 min-w-0">
                  <div className="font-bold text-sm text-[#0b1c30] truncate">
                    {detectedData.name}
                  </div>
                  <div className="text-xs text-gray-500 font-mono">
                    SKU: {detectedData.sku}
                  </div>
                  <div className="flex items-center gap-3 mt-1.5 text-xs">
                    <span className="font-mono font-bold text-[#0051d5]">
                      ${detectedData.detectedPrice.toFixed(2)}
                    </span>
                    <span className="text-gray-400">|</span>
                    <span className="text-gray-600 font-mono">
                      Market Avg: ${detectedData.marketAvg.toFixed(2)}
                    </span>
                  </div>
                </div>
              </div>

              {/* Match Channels */}
              <div className="space-y-2">
                <label className="font-mono text-xs text-[#76777d] uppercase tracking-wider block">
                  Matched Competitor Channels
                </label>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  {['Amazon', 'Best Buy', 'Walmart', 'Target'].map((comp) => (
                    <label
                      key={comp}
                      className="flex items-center gap-2 p-2.5 rounded-lg border border-gray-200 bg-white hover:border-[#0051d5]/40 cursor-pointer"
                    >
                      <input
                        type="checkbox"
                        defaultChecked
                        className="rounded text-[#0051d5] focus:ring-[#0051d5]"
                      />
                      <span className="font-medium text-[#0b1c30]">{comp}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="pt-4 flex justify-between gap-3 border-t border-gray-100">
                <button
                  type="button"
                  onClick={() => setStep(1)}
                  className="px-4 py-2 rounded-lg border border-gray-300 text-xs font-semibold hover:bg-gray-50 transition-colors"
                >
                  Back
                </button>
                <button
                  id="confirm-tracking-btn"
                  type="button"
                  onClick={handleCompleteTracking}
                  className="px-6 py-2.5 rounded-lg bg-[#000000] text-white text-xs font-semibold flex items-center gap-2 hover:bg-[#1f2937] active:scale-[0.98] transition-all cursor-pointer group shadow-sm"
                >
                  <Sparkles className="w-3.5 h-3.5 text-sky-300" />
                  <span>Initiate Tracking</span>
                </button>
              </div>
            </div>
          )}

          {/* STEP 3: Confirmation */}
          {step === 3 && (
            <div className="text-center py-6 space-y-4 animate-in zoom-in-95 duration-200">
              <div className="w-16 h-16 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mx-auto shadow-sm">
                <CheckCircle2 className="w-8 h-8" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-[#0b1c30]">
                  Tracking Active!
                </h2>
                <p className="text-xs sm:text-sm text-[#76777d] mt-1 max-w-sm mx-auto">
                  {detectedData.name} is now being monitored 24/7. Repricing alerts will trigger automatically.
                </p>
              </div>

              <div className="bg-[#eff4ff] p-3 rounded-lg border border-[#d3e4fe] max-w-sm mx-auto text-left text-xs font-mono space-y-1">
                <div className="flex justify-between">
                  <span className="text-gray-500">Scan Frequency:</span>
                  <span className="font-bold text-[#0b1c30]">Every 15 mins</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Repricing Floor:</span>
                  <span className="font-bold text-[#0b1c30]">$310.00</span>
                </div>
              </div>

              <div className="pt-4">
                <button
                  id="close-confirmation-btn"
                  onClick={handleResetAndClose}
                  className="px-8 py-2.5 rounded-lg bg-[#0051d5] text-white text-xs font-semibold hover:bg-[#003ea8] active:scale-[0.98] transition-all shadow-md cursor-pointer"
                >
                  View Product in Dashboard
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
