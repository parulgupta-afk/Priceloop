import React, { useState } from 'react';
import { Settings, Bell, DollarSign, Cpu, Database, Save, CheckCircle2 } from 'lucide-react';

export const SettingsView: React.FC = () => {
  const [currency, setCurrency] = useState('USD ($)');
  const [frequency, setFrequency] = useState('15');
  const [aiAggressiveness, setAiAggressiveness] = useState('Balanced');
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  return (
    <div id="settings-view" className="max-w-3xl space-y-6 animate-in fade-in duration-200">
      <div>
        <h2 className="text-2xl sm:text-3xl font-bold text-[#0b1c30] tracking-tight">
          System Settings & Integrations
        </h2>
        <p className="text-xs sm:text-sm text-[#76777d] mt-1">
          Manage your AI repricing engine, web scrapers, and communication webhooks.
        </p>
      </div>

      {saved && (
        <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 px-4 py-3 rounded-xl flex items-center gap-3 text-xs font-semibold">
          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          Settings synchronized across all crawler instances!
        </div>
      )}

      <form onSubmit={handleSave} className="bg-white border border-[#e2e8f0] rounded-xl p-6 shadow-sm space-y-6">
        {/* Scraper Configuration */}
        <div className="space-y-4">
          <h3 className="font-bold text-sm text-[#0b1c30] flex items-center gap-2">
            <Cpu className="w-4 h-4 text-[#0051d5]" />
            <span>Crawler Engine Configuration</span>
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="font-mono text-gray-600 block mb-1">Scrape Frequency</label>
              <select
                value={frequency}
                onChange={(e) => setFrequency(e.target.value)}
                className="w-full bg-gray-50 border border-gray-200 rounded-lg p-2.5 outline-none focus:border-[#0051d5]"
              >
                <option value="5">Every 5 minutes (Real-time Live)</option>
                <option value="15">Every 15 minutes (Standard)</option>
                <option value="60">Every 1 hour</option>
                <option value="360">Every 6 hours</option>
              </select>
            </div>

            <div>
              <label className="font-mono text-gray-600 block mb-1">Base Currency</label>
              <select
                value={currency}
                onChange={(e) => setCurrency(e.target.value)}
                className="w-full bg-gray-50 border border-gray-200 rounded-lg p-2.5 outline-none focus:border-[#0051d5]"
              >
                <option>USD ($)</option>
                <option>EUR (€)</option>
                <option>GBP (£)</option>
                <option>CAD ($)</option>
              </select>
            </div>
          </div>
        </div>

        {/* AI Strategy Mode */}
        <div className="space-y-4 pt-4 border-t border-gray-100">
          <h3 className="font-bold text-sm text-[#0b1c30] flex items-center gap-2">
            <DollarSign className="w-4 h-4 text-[#0051d5]" />
            <span>AI Repricing Behavior</span>
          </h3>

          <div className="grid grid-cols-3 gap-3 text-xs">
            {['Conservative (Margin First)', 'Balanced (Buy Box + Margin)', 'Aggressive (Volume & Velocity)'].map((mode) => (
              <label
                key={mode}
                className={`p-3 rounded-lg border text-center cursor-pointer transition-all ${
                  aiAggressiveness === mode
                    ? 'border-[#0051d5] bg-[#eff4ff] text-[#0051d5] font-bold'
                    : 'border-gray-200 text-gray-600 hover:bg-gray-50'
                }`}
              >
                <input
                  type="radio"
                  name="aggressiveness"
                  value={mode}
                  checked={aiAggressiveness === mode}
                  onChange={() => setAiAggressiveness(mode)}
                  className="sr-only"
                />
                <span>{mode}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Webhooks & Notification Channels */}
        <div className="space-y-4 pt-4 border-t border-gray-100">
          <h3 className="font-bold text-sm text-[#0b1c30] flex items-center gap-2">
            <Bell className="w-4 h-4 text-[#0051d5]" />
            <span>Notification Webhooks</span>
          </h3>

          <div className="space-y-2 text-xs">
            <label className="flex items-center gap-2">
              <input type="checkbox" defaultChecked className="rounded text-[#0051d5]" />
              <span className="text-gray-700">Send Critical Price War alerts via Email</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" defaultChecked className="rounded text-[#0051d5]" />
              <span className="text-gray-700">Slack Webhook channel integration (#pricing-ops)</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" defaultChecked className="rounded text-[#0051d5]" />
              <span className="text-gray-700">Automated Shopify & Amazon Inventory sync</span>
            </label>
          </div>
        </div>

        <div className="pt-4 border-t border-gray-100 flex justify-end">
          <button
            type="submit"
            className="px-6 py-2.5 bg-[#000000] text-white rounded-lg text-xs font-semibold hover:bg-[#1f2937] flex items-center gap-2 shadow-sm cursor-pointer"
          >
            <Save className="w-4 h-4" />
            <span>Save Configuration</span>
          </button>
        </div>
      </form>
    </div>
  );
};
