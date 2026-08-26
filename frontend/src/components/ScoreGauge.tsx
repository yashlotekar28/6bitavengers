import React from 'react';
import { ShieldCheck, ShieldAlert, AlertTriangle } from 'lucide-react';
import { ComplianceScore } from '../types';

interface ScoreGaugeProps {
  complianceScore?: ComplianceScore;
}

export const ScoreGauge: React.FC<ScoreGaugeProps> = ({ complianceScore }) => {
  if (!complianceScore) return null;

  const score = complianceScore.score;
  const risk = complianceScore.risk_level;

  let strokeColor = "#10B981"; // emerald
  let textColor = "text-emerald-400";
  let bgGradient = "from-emerald-950/30 to-slate-900";
  let riskBadge = "bg-emerald-500/20 text-emerald-300 border-emerald-500/40";
  let RiskIcon = ShieldCheck;

  if (risk === 'MEDIUM' || risk === 'HIGH') {
    strokeColor = "#F59E0B"; // amber
    textColor = "text-amber-400";
    bgGradient = "from-amber-950/30 to-slate-900";
    riskBadge = "bg-amber-500/20 text-amber-300 border-amber-500/40";
    RiskIcon = AlertTriangle;
  } else if (risk === 'CRITICAL') {
    strokeColor = "#F43F5E"; // rose
    textColor = "text-rose-400";
    bgGradient = "from-rose-950/30 to-slate-900";
    riskBadge = "bg-rose-500/20 text-rose-300 border-rose-500/40";
    RiskIcon = ShieldAlert;
  }

  // SVG circle calculation
  const radius = 46;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className={`bg-gradient-to-b ${bgGradient} border border-slate-800 rounded-2xl p-5 flex flex-col items-center justify-center relative overflow-hidden shadow-lg`}>
      <div className="flex items-center justify-between w-full mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Compliance Index</span>
        <div className={`flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-bold border ${riskBadge}`}>
          <RiskIcon className="w-3.5 h-3.5 mr-1" />
          <span>{risk} RISK</span>
        </div>
      </div>

      <div className="relative flex items-center justify-center my-2">
        <svg className="w-32 h-32 transform -rotate-90">
          <circle
            cx="64"
            cy="64"
            r={radius}
            stroke="currentColor"
            strokeWidth="8"
            className="text-slate-800"
            fill="transparent"
          />
          <circle
            cx="64"
            cy="64"
            r={radius}
            stroke={strokeColor}
            strokeWidth="8"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
            className="transition-all duration-1000 ease-out"
          />
        </svg>

        <div className="absolute flex flex-col items-center justify-center text-center">
          <span className={`text-3xl font-extrabold ${textColor} font-mono tracking-tight`}>
            {score}
          </span>
          <span className="text-[10px] text-slate-400 font-medium uppercase tracking-wider">/ 100</span>
        </div>
      </div>

      <div className="w-full grid grid-cols-2 gap-2 mt-2 pt-3 border-t border-slate-800/80 text-center text-xs">
        <div className="bg-slate-950/60 p-2 rounded-lg border border-slate-800/60">
          <p className="text-[10px] text-slate-400 uppercase">Hard Gates</p>
          <p className={`font-bold font-mono ${complianceScore.hard_blocks_triggered === 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
            {complianceScore.hard_blocks_triggered === 0 ? '0 Blocks' : `${complianceScore.hard_blocks_triggered} FAILED`}
          </p>
        </div>
        <div className="bg-slate-950/60 p-2 rounded-lg border border-slate-800/60">
          <p className="text-[10px] text-slate-400 uppercase">Mandatory Rules</p>
          <p className="font-bold font-mono text-slate-200">
            {complianceScore.mandatory_rules_passed}/{complianceScore.mandatory_rules_total}
          </p>
        </div>
      </div>
    </div>
  );
};
