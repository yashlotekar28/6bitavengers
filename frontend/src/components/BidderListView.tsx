import React from 'react';
import { ShieldCheck, AlertTriangle, ShieldAlert, ChevronRight, Building, CheckCircle2, XCircle } from 'lucide-react';
import { Bidder } from '../types';

interface BidderListProps {
  bidders: Bidder[];
  selectedBidderId: string;
  onSelectBidder: (id: string) => void;
}

export const BidderListView: React.FC<BidderListProps> = ({
  bidders,
  selectedBidderId,
  onSelectBidder
}) => {
  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl overflow-hidden shadow-lg mb-6">
      <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
        <div>
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">
            Active Tender Bidders Queue
          </h3>
          <p className="text-xs text-slate-400">Tender #GEM/2026/B/89420 • Evaluation Stage</p>
        </div>
        <span className="text-xs bg-blue-500/20 text-blue-300 border border-blue-500/40 px-2.5 py-0.5 rounded-full font-mono">
          {bidders.length} Bidders Enrolled
        </span>
      </div>

      <div className="divide-y divide-slate-800/80">
        {bidders.map((b) => {
          const isSelected = b.bidder_id === selectedBidderId;
          const score = b.compliance_score?.score ?? 0;
          const risk = b.compliance_score?.risk_level ?? 'LOW';
          const officerStatus = b.officer_status;

          let riskBadge = "bg-emerald-500/20 text-emerald-300 border-emerald-500/30";
          let scoreBar = "bg-emerald-500";
          if (risk === 'MEDIUM' || risk === 'HIGH') {
            riskBadge = "bg-amber-500/20 text-amber-300 border-amber-500/30";
            scoreBar = "bg-amber-500";
          } else if (risk === 'CRITICAL') {
            riskBadge = "bg-rose-500/20 text-rose-300 border-rose-500/30";
            scoreBar = "bg-rose-500";
          }

          return (
            <div
              key={b.bidder_id}
              onClick={() => onSelectBidder(b.bidder_id)}
              className={`p-4 transition-all cursor-pointer flex flex-col md:flex-row md:items-center justify-between gap-3 ${
                isSelected
                  ? 'bg-blue-950/30 border-l-4 border-blue-500'
                  : 'hover:bg-slate-850 bg-slate-900/40'
              }`}
            >
              <div className="flex items-start space-x-3">
                <div className="p-2.5 bg-slate-800 text-slate-300 rounded-xl mt-0.5">
                  <Building className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center space-x-2">
                    <h4 className="text-sm font-bold text-white">{b.company_name}</h4>
                    <span className="text-[10px] bg-slate-800 text-slate-400 px-2 py-0.5 rounded font-mono">
                      {b.bidder_id}
                    </span>
                  </div>

                  <div className="flex flex-wrap gap-2 text-xs text-slate-400 mt-1 font-mono">
                    <span>GST: <strong className="text-slate-300">{b.identifiers.gstin}</strong></span>
                    <span>•</span>
                    <span>PAN: <strong className="text-slate-300">{b.identifiers.pan}</strong></span>
                    <span>•</span>
                    <span>State: <strong className="text-slate-300">{b.registered_state}</strong></span>
                  </div>
                </div>
              </div>

              {/* Score & Risk Status */}
              <div className="flex items-center space-x-6 self-end md:self-center">
                <div className="text-right">
                  <div className="flex items-center space-x-2 justify-end">
                    <span className="text-xs text-slate-400">Score:</span>
                    <span className="text-base font-bold font-mono text-white">{score}</span>
                    <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold border ${riskBadge}`}>
                      {risk}
                    </span>
                  </div>
                  <div className="w-24 bg-slate-800 h-1.5 rounded-full mt-1.5 overflow-hidden">
                    <div className={`h-full ${scoreBar}`} style={{ width: `${score}%` }} />
                  </div>
                </div>

                <div className="text-right min-w-[90px]">
                  <span className={`text-[11px] font-bold px-2 py-1 rounded-md ${
                    officerStatus === 'APPROVED' ? 'bg-emerald-500/20 text-emerald-300' :
                    officerStatus === 'REJECTED' ? 'bg-rose-500/20 text-rose-300' :
                    officerStatus === 'OVERRIDDEN' ? 'bg-purple-500/20 text-purple-300' :
                    'bg-slate-800 text-slate-300'
                  }`}>
                    {officerStatus}
                  </span>
                </div>

                <ChevronRight className={`w-5 h-5 ${isSelected ? 'text-blue-400' : 'text-slate-600'}`} />
              </div>

            </div>
          );
        })}
      </div>
    </div>
  );
};
