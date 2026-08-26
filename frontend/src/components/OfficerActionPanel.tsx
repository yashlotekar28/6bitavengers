import React, { useState } from 'react';
import { CheckCircle2, XCircle, HelpCircle, ShieldAlert, Send } from 'lucide-react';
import { OfficerStatus } from '../types';

interface OfficerActionProps {
  bidderId: string;
  currentStatus: OfficerStatus;
  officerNotes?: string;
  onDecisionSubmit: (action: string, comments: string, overrideJustification?: string) => Promise<void>;
  isSubmitting: boolean;
}

export const OfficerActionPanel: React.FC<OfficerActionProps> = ({
  bidderId: _bidderId,
  currentStatus,
  officerNotes: _officerNotes,
  onDecisionSubmit,
  isSubmitting
}) => {
  const [selectedAction, setSelectedAction] = useState<string>('APPROVE');
  const [comments, setComments] = useState<string>('');
  const [overrideJustification, setOverrideJustification] = useState<string>('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!comments.trim()) return;
    await onDecisionSubmit(selectedAction, comments, overrideJustification);
    setComments('');
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-lg">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div>
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">
            Procurement Officer Decision Workflow
          </h3>
          <p className="text-xs text-slate-400">
            Final statutory determination (Human-in-the-Loop)
          </p>
        </div>

        <div className="text-right">
          <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Current Status</span>
          <span className={`text-xs font-bold px-2.5 py-0.5 rounded-full border ${
            currentStatus === 'APPROVED' ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' :
            currentStatus === 'REJECTED' ? 'bg-rose-500/20 text-rose-300 border-rose-500/40' :
            currentStatus === 'OVERRIDDEN' ? 'bg-purple-500/20 text-purple-300 border-purple-500/40' :
            currentStatus === 'REQUEST_INFO' ? 'bg-amber-500/20 text-amber-300 border-amber-500/40' :
            'bg-slate-800 text-slate-300 border-slate-700'
          }`}>
            {currentStatus}
          </span>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="mt-4 space-y-4">
        {/* Action Radio Buttons */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          <button
            type="button"
            onClick={() => setSelectedAction('APPROVE')}
            className={`p-3 rounded-xl border flex flex-col items-center justify-center space-y-1 transition-all ${
              selectedAction === 'APPROVE'
                ? 'bg-emerald-600/20 border-emerald-500 text-emerald-300 ring-1 ring-emerald-500'
                : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
            }`}
          >
            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
            <span className="text-xs font-bold">Approve Bid</span>
          </button>

          <button
            type="button"
            onClick={() => setSelectedAction('REJECT')}
            className={`p-3 rounded-xl border flex flex-col items-center justify-center space-y-1 transition-all ${
              selectedAction === 'REJECT'
                ? 'bg-rose-600/20 border-rose-500 text-rose-300 ring-1 ring-rose-500'
                : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
            }`}
          >
            <XCircle className="w-5 h-5 text-rose-400" />
            <span className="text-xs font-bold">Reject Bid</span>
          </button>

          <button
            type="button"
            onClick={() => setSelectedAction('REQUEST_INFO')}
            className={`p-3 rounded-xl border flex flex-col items-center justify-center space-y-1 transition-all ${
              selectedAction === 'REQUEST_INFO'
                ? 'bg-amber-600/20 border-amber-500 text-amber-300 ring-1 ring-amber-500'
                : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
            }`}
          >
            <HelpCircle className="w-5 h-5 text-amber-400" />
            <span className="text-xs font-bold">Request Info</span>
          </button>

          <button
            type="button"
            onClick={() => setSelectedAction('OVERRIDE')}
            className={`p-3 rounded-xl border flex flex-col items-center justify-center space-y-1 transition-all ${
              selectedAction === 'OVERRIDE'
                ? 'bg-purple-600/20 border-purple-500 text-purple-300 ring-1 ring-purple-500'
                : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
            }`}
          >
            <ShieldAlert className="w-5 h-5 text-purple-400" />
            <span className="text-xs font-bold">Override Flags</span>
          </button>
        </div>

        {/* Override Justification Notice */}
        {selectedAction === 'OVERRIDE' && (
          <div className="p-3 bg-purple-950/40 border border-purple-500/40 rounded-xl space-y-1.5 text-xs">
            <span className="font-bold text-purple-300 block">⚠️ Mandatory Committee Justification Required:</span>
            <p className="text-slate-300 text-[11px]">
              Overriding compliance flags will create a permanent, highlighted entry in the CPPP Comptroller & Auditor General (CAG) audit trail.
            </p>
            <input
              type="text"
              required
              placeholder="e.g. Approved under MSME relaxation clause 4.2 via Tender Committee Minute TC-2026/89"
              value={overrideJustification}
              onChange={(e) => setOverrideJustification(e.target.value)}
              className="w-full bg-slate-900 border border-purple-700/60 rounded-lg p-2 text-xs text-white focus:outline-none focus:ring-1 focus:ring-purple-400"
            />
          </div>
        )}

        {/* Officer Comments */}
        <div>
          <label className="text-xs font-medium text-slate-300 block mb-1.5">
            Officer Verification Remarks / Order Reference:
          </label>
          <textarea
            required
            rows={2}
            placeholder="Enter reason for decision or queries to be sent to the bidder..."
            value={comments}
            onChange={(e) => setComments(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none font-sans"
          />
        </div>

        <div className="flex items-center justify-between pt-2">
          <span className="text-[11px] text-slate-500 font-mono">
            Signed by: Rajesh Kumar (Officer ID: GEM-994)
          </span>

          <button
            type="submit"
            disabled={isSubmitting || !comments.trim()}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold rounded-xl transition disabled:opacity-50 shadow-md"
          >
            <Send className="w-3.5 h-3.5" />
            <span>Commit Decision & Append Audit Log</span>
          </button>
        </div>
      </form>
    </div>
  );
};
