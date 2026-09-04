import React, { useState } from 'react';
import { Sliders, Plus, ToggleLeft, ToggleRight, CheckCircle2, ShieldCheck, Play, Pause, Trash2 } from 'lucide-react';
import { PriceRule } from '../types';

interface PriceRulesViewProps {
  rules: PriceRule[];
  onToggleRule: (ruleId: string) => void;
  onAddRule: (rule: PriceRule) => void;
}

export const PriceRulesView: React.FC<PriceRulesViewProps> = ({
  rules,
  onToggleRule,
  onAddRule,
}) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [ruleName, setRuleName] = useState('');
  const [ruleCondition, setRuleCondition] = useState('Competitor == Amazon AND Stock == InStock');
  const [ruleAction, setRuleAction] = useState('Undercut by 1.5%');
  const [ruleCategory, setRuleCategory] = useState('All Categories');

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (!ruleName.trim()) return;

    const newRule: PriceRule = {
      id: 'rule-' + Date.now(),
      name: ruleName,
      description: `Automatically applies ${ruleAction} when ${ruleCondition}`,
      condition: ruleCondition,
      action: ruleAction,
      targetCategory: ruleCategory,
      status: 'active',
      appliedProductsCount: Math.floor(Math.random() * 200) + 15,
      lastTriggered: 'Just now',
    };

    onAddRule(newRule);
    setRuleName('');
    setIsModalOpen(false);
  };

  return (
    <div id="price-rules-view" className="space-y-6 animate-in fade-in duration-200">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl sm:text-3xl font-bold text-[#0b1c30] tracking-tight">
            Automated Price Rules
          </h2>
          <p className="text-xs sm:text-sm text-[#76777d] mt-1">
            Configure algorithmic repricing policies and profit protection guardrails.
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="bg-[#000000] text-white hover:bg-[#1f2937] active:scale-[0.98] px-4 py-2.5 rounded-lg flex items-center gap-2 font-mono text-xs font-semibold cursor-pointer shadow-sm"
        >
          <Plus className="w-4 h-4" />
          <span>New Repricing Rule</span>
        </button>
      </div>

      {/* Rules List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {rules.map((rule) => {
          const isActive = rule.status === 'active';
          return (
            <div
              key={rule.id}
              className={`bg-white border rounded-xl p-6 shadow-sm flex flex-col justify-between transition-all ${
                isActive ? 'border-[#e2e8f0] hover:border-[#0051d5]/40' : 'border-gray-200 opacity-60'
              }`}
            >
              <div>
                <div className="flex justify-between items-start gap-2 mb-2">
                  <h3 className="font-bold text-base text-[#0b1c30]">{rule.name}</h3>
                  <button
                    onClick={() => onToggleRule(rule.id)}
                    className="text-xs font-mono font-bold flex items-center gap-1 cursor-pointer"
                  >
                    {isActive ? (
                      <span className="text-emerald-600 flex items-center gap-1">
                        <ToggleRight className="w-6 h-6 fill-current" /> Active
                      </span>
                    ) : (
                      <span className="text-gray-400 flex items-center gap-1">
                        <ToggleLeft className="w-6 h-6" /> Paused
                      </span>
                    )}
                  </button>
                </div>

                <p className="text-xs text-[#64748b] leading-relaxed mb-4">
                  {rule.description}
                </p>

                <div className="space-y-2 bg-[#f8f9ff] p-3.5 rounded-lg border border-[#e2e8f0] font-mono text-xs">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Condition:</span>
                    <span className="font-semibold text-[#0b1c30] text-right truncate max-w-[200px]">
                      {rule.condition}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Action:</span>
                    <span className="font-semibold text-[#0051d5] text-right truncate max-w-[200px]">
                      {rule.action}
                    </span>
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-gray-100 flex justify-between items-center text-xs font-mono text-gray-500">
                <span>Applied to: {rule.appliedProductsCount} SKUs</span>
                <span>Last run: {rule.lastTriggered}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* New Rule Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-white rounded-xl border border-[#e2e8f0] shadow-2xl p-6 max-w-md w-full space-y-4">
            <h3 className="font-bold text-lg text-[#0b1c30]">
              Create Repricing Rule
            </h3>

            <form onSubmit={handleCreate} className="space-y-4 text-xs">
              <div>
                <label className="font-mono text-gray-600 block mb-1">Rule Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Always beat Amazon by 2%"
                  value={ruleName}
                  onChange={(e) => setRuleName(e.target.value)}
                  className="w-full bg-gray-50 border border-gray-200 rounded-lg p-2.5 outline-none focus:border-[#0051d5]"
                />
              </div>

              <div>
                <label className="font-mono text-gray-600 block mb-1">Target Category</label>
                <select
                  value={ruleCategory}
                  onChange={(e) => setRuleCategory(e.target.value)}
                  className="w-full bg-gray-50 border border-gray-200 rounded-lg p-2.5 outline-none"
                >
                  <option>All Categories</option>
                  <option>Audio</option>
                  <option>Displays</option>
                  <option>Peripherals</option>
                  <option>Furniture</option>
                </select>
              </div>

              <div>
                <label className="font-mono text-gray-600 block mb-1">Condition Trigger</label>
                <input
                  type="text"
                  value={ruleCondition}
                  onChange={(e) => setRuleCondition(e.target.value)}
                  className="w-full bg-gray-50 border border-gray-200 rounded-lg p-2.5 outline-none font-mono"
                />
              </div>

              <div>
                <label className="font-mono text-gray-600 block mb-1">Action</label>
                <input
                  type="text"
                  value={ruleAction}
                  onChange={(e) => setRuleAction(e.target.value)}
                  className="w-full bg-gray-50 border border-gray-200 rounded-lg p-2.5 outline-none font-mono"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 border rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-[#000000] text-white rounded-lg hover:bg-[#1f2937]"
                >
                  Save & Enable Rule
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
