import React, { useState } from 'react';
import { X, Check, Sparkles, Zap, Shield, Crown, Loader2 } from 'lucide-react';
import confetti from 'canvas-confetti';
import { api, ApiError } from '../lib/api';

interface UpgradePlanModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const UpgradePlanModal: React.FC<UpgradePlanModalProps> = ({ isOpen, onClose }) => {
  const [submittingPlan, setSubmittingPlan] = useState<string | null>(null);
  const [checkoutError, setCheckoutError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSelectPlan = async (planKey: 'professional' | 'enterprise') => {
    setCheckoutError(null);
    setSubmittingPlan(planKey);
    try {
      const { checkout_url } = await api.createCheckoutSession(planKey);
      try {
        confetti({ particleCount: 70, spread: 60, origin: { y: 0.5 } });
      } catch {}
      // Real redirect to Stripe's hosted checkout page. The plan only
      // actually activates once Stripe confirms payment via webhook --
      // this redirect is not itself a "success," it is the start of paying.
      window.location.href = checkout_url;
    } catch (e) {
      setSubmittingPlan(null);
      if (e instanceof ApiError && e.status === 503) {
        setCheckoutError('Billing is not set up on this server yet (Stripe keys not configured).');
      } else {
        setCheckoutError('Could not start checkout. Please try again.');
      }
    }
  };

  const plans = [
    {
      name: 'Professional',
      planKey: 'professional' as const,
      price: '$149',
      period: '/ month',
      description: 'Ideal for growing brands tracking up to 5,000 SKUs across 10 retail channels.',
      badge: null,
      features: [
        'Up to 5,000 Tracked SKUs',
        'Hourly Price & Stock Scraping',
        'Amazon, Best Buy & Walmart Feeds',
        'Standard Margin Rules',
        'Email & Slack Alerts',
      ],
      cta: 'Choose Professional',
      primary: false,
    },
    {
      name: 'Enterprise Scale',
      planKey: 'enterprise' as const,
      price: '$499',
      period: '/ month',
      description: 'Full AI automated repricing engine for omni-channel high velocity merchants.',
      badge: 'Most Popular',
      features: [
        'Unlimited SKUs & Categories',
        'Real-time 5-minute scraping frequency',
        'All 50+ Global Marketplaces & Direct Sites',
        'Full Algorithmic Repricing Engine',
        'Dedicated Pricing Strategist & SLA',
        'Custom Webhooks & ERP / Shopify Sync',
      ],
      cta: 'Activate Enterprise Scale',
      primary: true,
    },
  ];

  return (
    <div
      id="upgrade-plan-modal"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200"
    >
      <div className="bg-white rounded-xl border border-[#e2e8f0] shadow-2xl p-6 sm:p-8 max-w-2xl w-full space-y-6 relative max-h-[90vh] overflow-y-auto">
        <button
          onClick={onClose}
          className="absolute right-4 top-4 text-gray-400 hover:text-gray-700 p-1.5 rounded-full"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="text-center space-y-1">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-50 text-[#0051d5] text-xs font-mono font-bold border border-blue-200">
            <Crown className="w-3.5 h-3.5" />
            <span>Priceloop AI Subscription Tiers</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-bold text-[#0b1c30]">
            Supercharge Your Pricing Edge
          </h2>
          <p className="text-xs sm:text-sm text-gray-500 max-w-md mx-auto">
            Unlock sub-minute scraping, automated Buy Box algorithms, and omni-channel stock prediction.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {plans.map((plan) => (
            <div
              key={plan.name}
              className={`rounded-xl p-5 border flex flex-col justify-between transition-all ${
                plan.primary
                  ? 'border-[#0051d5] bg-[#eff4ff]/30 ring-2 ring-[#0051d5] shadow-lg'
                  : 'border-gray-200 bg-white hover:border-gray-300'
              }`}
            >
              <div>
                <div className="flex justify-between items-center mb-2">
                  <h3 className="font-bold text-base text-[#0b1c30]">{plan.name}</h3>
                  {plan.badge && (
                    <span className="bg-[#0051d5] text-white text-[10px] font-mono font-bold px-2 py-0.5 rounded-full">
                      {plan.badge}
                    </span>
                  )}
                </div>

                <div className="flex items-baseline gap-1 my-3">
                  <span className="text-3xl font-extrabold font-mono text-[#0b1c30]">
                    {plan.price}
                  </span>
                  <span className="text-xs text-gray-500">{plan.period}</span>
                </div>

                <p className="text-xs text-gray-600 mb-4 leading-normal">
                  {plan.description}
                </p>

                <div className="space-y-2 pt-3 border-t border-gray-100 text-xs">
                  {plan.features.map((f, i) => (
                    <div key={i} className="flex items-start gap-2 text-gray-700">
                      <Check className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                      <span>{f}</span>
                    </div>
                  ))}
                </div>
              </div>

              <button
                onClick={() => handleSelectPlan(plan.planKey)}
                disabled={submittingPlan !== null}
                className={`mt-6 w-full py-2.5 rounded-lg text-xs font-semibold transition-all cursor-pointer shadow-sm disabled:opacity-60 flex items-center justify-center gap-2 ${
                  plan.primary
                    ? 'bg-[#000000] hover:bg-[#1f2937] text-white'
                    : 'bg-white hover:bg-gray-50 text-[#0b1c30] border border-gray-300'
                }`}
              >
                {submittingPlan === plan.planKey && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                {plan.cta}
              </button>
            </div>
          ))}
        </div>

        {checkoutError && (
          <p className="text-xs text-red-600 bg-red-50 border border-red-100 rounded-lg px-3 py-2 text-center">
            {checkoutError}
          </p>
        )}
      </div>
    </div>
  );
};
