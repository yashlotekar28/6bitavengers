import React from 'react';
import { Sparkles, AlertTriangle, ShieldCheck, HelpCircle, CheckCircle, Info } from 'lucide-react';
import { AIRecommendation, RiskLevel } from '../types';

interface AIRecommendationProps {
  recommendation?: AIRecommendation;
}

export const AIRecommendationCard: React.FC<AIRecommendationProps> = ({ recommendation }) => {
  if (!recommendation) return null;

  const action = recommendation.recommended_action;

  let badgeColor = "bg-emerald-500/20 text-emerald-300 border-emerald-500/40";
  let ActionIcon = CheckCircle;
  let actionText = "Recommend Technical Approval";

  if (action === 'RECOMMEND_REJECTION') {
    badgeColor = "bg-rose-500/20 text-rose-300 border-rose-500/40";
    ActionIcon = AlertTriangle;
    actionText = "Recommend Disqualification / Rejection";
  } else if (action === 'FLAG_FOR_OFFICER_REVIEW' || action === 'REQUEST_MORE_INFO') {
    badgeColor = "bg-amber-500/20 text-amber-300 border-amber-500/40";
    ActionIcon = HelpCircle;
    actionText = "Flag for Officer Investigation / Clarification";
  }

  return (
    <div className="bg-gradient-to-br from-indigo-950/40 via-slate-900 to-slate-900 border border-indigo-500/30 rounded-2xl p-5 shadow-lg relative overflow-hidden">
      <div className="flex items-center justify-between pb-3 border-b border-indigo-900/40">
        <div className="flex items-center space-x-2">
          <div className="p-1.5 bg-indigo-500/20 rounded-lg text-indigo-400">
            <Sparkles className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              AI Procurement Officer Assistant
            </h3>
            <p className="text-xs text-indigo-300">Contextual synthesis of rules, discrepancies & telemetry</p>
          </div>
        </div>

        <div className={`flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold border ${badgeColor}`}>
          <ActionIcon className="w-4 h-4" />
          <span>{actionText}</span>
        </div>
      </div>

      {/* Executive Summary */}
      <div className="mt-4 bg-slate-950/70 p-3.5 rounded-xl border border-slate-800/80">
        <div className="flex items-start space-x-2">
          <Info className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
          <p className="text-xs text-slate-200 leading-relaxed font-sans">
            {recommendation.executive_summary}
          </p>
        </div>
      </div>

      {/* Flagged Risk Factors */}
      {recommendation.risk_factors.length > 0 && (
        <div className="mt-4 space-y-2">
          <p className="text-xs font-bold text-slate-300 uppercase tracking-wider">
            Synthesized Risk Observations ({recommendation.risk_factors.length}):
          </p>
          {recommendation.risk_factors.map((rf, idx) => (
            <div
              key={idx}
              className={`p-2.5 rounded-xl border text-xs ${
                rf.severity === 'CRITICAL'
                  ? 'bg-rose-950/30 border-rose-500/40 text-rose-200'
                  : rf.severity === 'HIGH'
                  ? 'bg-amber-950/30 border-amber-500/40 text-amber-200'
                  : 'bg-blue-950/30 border-blue-500/40 text-blue-200'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-semibold text-white">{rf.title}</span>
                <span className="text-[9px] uppercase font-bold px-1.5 py-0.5 rounded bg-black/40">
                  {rf.severity}
                </span>
              </div>
              <p className="mt-1 text-[11px] opacity-90">{rf.explanation}</p>
            </div>
          ))}
        </div>
      )}

      {/* Mitigation / Officer Recommendation */}
      {recommendation.mitigation_notes && (
        <div className="mt-4 p-3 bg-slate-950/80 rounded-xl border border-indigo-900/30 text-xs">
          <span className="font-bold text-indigo-300 uppercase text-[10px] tracking-wider block mb-1">
            Suggested Action for Procurement Committee:
          </span>
          <p className="text-slate-300">{recommendation.mitigation_notes}</p>
        </div>
      )}
    </div>
  );
};
