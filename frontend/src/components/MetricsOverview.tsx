import React from 'react';
import { Users, CheckCircle, AlertTriangle, ShieldAlert, Zap, Clock } from 'lucide-react';
import { DashboardMetrics } from '../types';

interface MetricsProps {
  metrics: DashboardMetrics | null;
}

export const MetricsOverview: React.FC<MetricsProps> = ({ metrics }) => {
  if (!metrics) return null;

  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-6">
      <div className="bg-slate-900/90 border border-slate-800 p-3.5 rounded-xl flex items-center space-x-3">
        <div className="p-2 bg-blue-500/10 text-blue-400 rounded-lg">
          <Users className="w-5 h-5" />
        </div>
        <div>
          <p className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">Total Bidders</p>
          <p className="text-xl font-bold text-white">{metrics.total_bidders}</p>
        </div>
      </div>

      <div className="bg-slate-900/90 border border-slate-800 p-3.5 rounded-xl flex items-center space-x-3">
        <div className="p-2 bg-emerald-500/10 text-emerald-400 rounded-lg">
          <CheckCircle className="w-5 h-5" />
        </div>
        <div>
          <p className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">Fully Compliant</p>
          <p className="text-xl font-bold text-emerald-400">{metrics.compliant_count}</p>
        </div>
      </div>

      <div className="bg-slate-900/90 border border-slate-800 p-3.5 rounded-xl flex items-center space-x-3">
        <div className="p-2 bg-amber-500/10 text-amber-400 rounded-lg">
          <AlertTriangle className="w-5 h-5" />
        </div>
        <div>
          <p className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">Flagged Discrepancies</p>
          <p className="text-xl font-bold text-amber-400">{metrics.flagged_count}</p>
        </div>
      </div>

      <div className="bg-slate-900/90 border border-slate-800 p-3.5 rounded-xl flex items-center space-x-3">
        <div className="p-2 bg-rose-500/10 text-rose-400 rounded-lg">
          <ShieldAlert className="w-5 h-5" />
        </div>
        <div>
          <p className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">Debarred / Blocked</p>
          <p className="text-xl font-bold text-rose-400">{metrics.debarred_count}</p>
        </div>
      </div>

      <div className="col-span-2 md:col-span-1 bg-gradient-to-br from-blue-950/40 to-indigo-950/40 border border-blue-800/40 p-3.5 rounded-xl flex items-center space-x-3">
        <div className="p-2 bg-blue-500/20 text-blue-300 rounded-lg">
          <Zap className="w-5 h-5 text-blue-400" />
        </div>
        <div>
          <div className="flex items-center space-x-1">
            <p className="text-[11px] font-medium text-blue-300 uppercase tracking-wider">Speed</p>
            <span className="text-[10px] px-1 bg-emerald-500/20 text-emerald-300 rounded font-semibold">99.8% Faster</span>
          </div>
          <p className="text-base font-bold text-white font-mono">{metrics.automated_verification_time_sec}s <span className="text-xs font-normal text-slate-400">vs 4.5d</span></p>
        </div>
      </div>
    </div>
  );
};
