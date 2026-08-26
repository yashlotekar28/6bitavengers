import React from 'react';
import { ShieldCheck, RefreshCw, FileText, Activity, AlertTriangle, CheckCircle2, XCircle } from 'lucide-react';
import { Bidder } from '../types';

interface NavbarProps {
  bidders: Bidder[];
  selectedBidderId: string;
  onSelectBidder: (id: string) => void;
  onResetDemo: () => void;
  onOpenAudit: () => void;
  isLoading: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  bidders,
  selectedBidderId,
  onSelectBidder,
  onResetDemo,
  onOpenAudit,
  isLoading
}) => {
  return (
    <header className="bg-slate-900 border-b border-slate-800 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Logo & Branding */}
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-600/20 border border-blue-500/30 rounded-lg text-blue-400">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-lg text-white tracking-tight">ProcureShield<span className="text-blue-400">AI</span></span>
                <span className="px-2 py-0.5 text-[10px] font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 rounded">
                  GeM VERIFIED
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono">Tender #GEM/2026/B/89420 • MeitY Cloud Infra</p>
            </div>
          </div>

          {/* 1-Click Demo Scenarios Switcher */}
          <div className="hidden md:flex items-center bg-slate-950 p-1 rounded-lg border border-slate-800 space-x-1">
            <span className="text-[11px] font-medium text-slate-400 px-2 uppercase tracking-wider">Scenarios:</span>
            {bidders.map((b) => {
              const isSelected = b.bidder_id === selectedBidderId;
              let badgeColor = "text-emerald-400 hover:bg-emerald-950/40";
              let icon = <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 inline mr-1" />;
              
              if (b.compliance_score?.risk_level === 'MEDIUM' || b.compliance_score?.risk_level === 'HIGH') {
                badgeColor = "text-amber-400 hover:bg-amber-950/40";
                icon = <AlertTriangle className="w-3.5 h-3.5 text-amber-400 inline mr-1" />;
              } else if (b.compliance_score?.risk_level === 'CRITICAL') {
                badgeColor = "text-rose-400 hover:bg-rose-950/40";
                icon = <XCircle className="w-3.5 h-3.5 text-rose-400 inline mr-1" />;
              }

              return (
                <button
                  key={b.bidder_id}
                  onClick={() => onSelectBidder(b.bidder_id)}
                  className={`px-3 py-1 text-xs font-medium rounded-md transition-all flex items-center ${
                    isSelected
                      ? 'bg-blue-600 text-white shadow-sm'
                      : `text-slate-300 ${badgeColor}`
                  }`}
                >
                  {icon}
                  {b.company_name.split(' ')[0]}
                </button>
              );
            })}
          </div>

          {/* Quick Actions */}
          <div className="flex items-center space-x-2">
            <button
              onClick={onOpenAudit}
              className="flex items-center space-x-1.5 px-3 py-1.5 text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg border border-slate-700 transition"
              title="View full system audit logs"
            >
              <Activity className="w-3.5 h-3.5 text-blue-400" />
              <span>Audit Trail</span>
            </button>

            <button
              onClick={onResetDemo}
              disabled={isLoading}
              className="flex items-center space-x-1.5 px-3 py-1.5 text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg border border-slate-700 transition disabled:opacity-50"
              title="Reset sample data and re-run verification"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-blue-400' : ''}`} />
              <span className="hidden sm:inline">Reset Demo</span>
            </button>
          </div>

        </div>
      </div>
    </header>
  );
};
