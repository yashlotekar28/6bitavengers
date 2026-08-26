import React from 'react';
import { TrendingUp, Award } from 'lucide-react';
import { LongitudinalTrustScore } from '../types';

interface TrustScorePanelProps {
  trustScore: LongitudinalTrustScore | null;
  isLoading: boolean;
}

const bandStyle = (band: string) => {
  if (band.startsWith('PRIME')) return { text: 'text-emerald-400', badge: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40', stroke: '#10B981' };
  if (band.startsWith('HIGH_RELIABILITY')) return { text: 'text-blue-400', badge: 'bg-blue-500/20 text-blue-300 border-blue-500/40', stroke: '#3B82F6' };
  if (band.startsWith('MODERATE')) return { text: 'text-amber-400', badge: 'bg-amber-500/20 text-amber-300 border-amber-500/40', stroke: '#F59E0B' };
  return { text: 'text-rose-400', badge: 'bg-rose-500/20 text-rose-300 border-rose-500/40', stroke: '#F43F5E' };
};

export const TrustScorePanel: React.FC<TrustScorePanelProps> = ({ trustScore, isLoading }) => {
  if (isLoading) {
    return (
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 text-sm text-slate-400">
        Loading longitudinal trust score...
      </div>
    );
  }

  if (!trustScore) {
    return (
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 text-sm text-slate-400">
        No trust score data available for this bidder.
      </div>
    );
  }

  const style = bandStyle(trustScore.rating_band);
  const radius = 46;
  const circumference = 2 * Math.PI * radius;
  const pct = (trustScore.score - 300) / (900 - 300);
  const strokeDashoffset = circumference - pct * circumference;

  const trend = trustScore.historical_trend_24m;
  const maxTrend = trend.length ? Math.max(...trend.map((t) => t.score)) : 900;
  const minTrend = trend.length ? Math.min(...trend.map((t) => t.score)) : 300;

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-5">
      <div className="flex flex-col lg:flex-row gap-6">
        <div className="flex flex-col items-center justify-center bg-slate-950/60 border border-slate-800 rounded-2xl p-5 lg:w-64 shrink-0">
          <div className="flex items-center space-x-2 mb-2">
            <Award className="w-4 h-4 text-slate-400" />
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Trust score</span>
          </div>
          <div className="relative flex items-center justify-center my-1">
            <svg className="w-32 h-32 transform -rotate-90">
              <circle cx="64" cy="64" r={radius} stroke="currentColor" strokeWidth="8" className="text-slate-800" fill="transparent" />
              <circle
                cx="64" cy="64" r={radius}
                stroke={style.stroke} strokeWidth="8"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                strokeLinecap="round" fill="transparent"
                className="transition-all duration-1000 ease-out"
              />
            </svg>
            <div className="absolute flex flex-col items-center justify-center text-center">
              <span className={`text-3xl font-extrabold ${style.text} font-mono tracking-tight`}>{trustScore.score}</span>
              <span className="text-[10px] text-slate-400 font-medium uppercase tracking-wider">/ 900</span>
            </div>
          </div>
          <span className={`mt-2 px-2.5 py-1 rounded-full text-xs font-bold border ${style.badge}`}>
            {trustScore.rating_band.split('_')[0].replace(/_/g, ' ')}
          </span>
        </div>

        <div className="flex-1 space-y-3">
          {trustScore.dimensions.map((dim) => (
            <div key={dim.name} className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3">
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-xs font-semibold text-slate-200">{dim.name}</span>
                <span className="text-xs font-mono text-slate-400">{dim.weight_percent}% weight &middot; grade {dim.grade}</span>
              </div>
              <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-blue-500 rounded-full" style={{ width: `${dim.score}%` }} />
              </div>
              <p className="text-[11px] text-slate-500 mt-1.5">{dim.details}</p>
            </div>
          ))}
        </div>
      </div>

      {trend.length > 0 && (
        <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-4">
          <div className="flex items-center space-x-2 mb-3">
            <TrendingUp className="w-4 h-4 text-slate-400" />
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">24-month trajectory</span>
          </div>
          <svg viewBox={`0 0 ${trend.length * 40} 80`} className="w-full h-20" preserveAspectRatio="none">
            <polyline
              fill="none"
              stroke={style.stroke}
              strokeWidth="2"
              points={trend.map((t, i) => {
                const x = i * 40 + 20;
                const y = 70 - ((t.score - minTrend) / Math.max(1, maxTrend - minTrend)) * 60;
                return `${x},${y}`;
              }).join(' ')}
            />
          </svg>
          <div className="flex justify-between text-[10px] text-slate-500 font-mono mt-1">
            <span>{trend[0]?.month}</span>
            <span>{trend[trend.length - 1]?.month}</span>
          </div>
        </div>
      )}

      <p className="text-xs text-slate-400 border-t border-slate-800 pt-3">{trustScore.summary}</p>
    </div>
  );
};
