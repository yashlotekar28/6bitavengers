import React from 'react';
import { Vault, ShieldCheck, RefreshCw, Clock, AlertTriangle } from 'lucide-react';
import { VendorVault } from '../types';

interface VaultPanelProps {
  vault: VendorVault | null;
  isLoading: boolean;
}

const badgeStyle = (badge: string) => {
  if (badge === 'DIGILOCKER_VERIFIED') return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40';
  if (badge === 'API_SETU_AUTHENTICATED') return 'bg-blue-500/20 text-blue-300 border-blue-500/40';
  return 'bg-amber-500/20 text-amber-300 border-amber-500/40';
};

export const VaultPanel: React.FC<VaultPanelProps> = ({ vault, isLoading }) => {
  if (isLoading) {
    return (
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 text-sm text-slate-400">
        Loading vendor document vault...
      </div>
    );
  }

  if (!vault) {
    return (
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 text-sm text-slate-400">
        No vault data available for this bidder.
      </div>
    );
  }

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-5">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-blue-600/20 border border-blue-500/30 text-blue-400 rounded-xl">
            <Vault className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white">Unified Vendor Document Vault</h3>
            <p className="text-xs text-slate-400">{vault.company_name} &middot; synced {new Date(vault.last_synced).toLocaleDateString()}</p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <div className="text-center px-3 py-1.5 rounded-xl bg-slate-950/60 border border-slate-800">
            <p className="text-[10px] text-slate-400 uppercase">Reused across</p>
            <p className="text-sm font-bold font-mono text-slate-100">{vault.total_reused_tenders} tenders</p>
          </div>
          <span className="flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-bold border bg-emerald-500/20 text-emerald-300 border-emerald-500/40">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>{vault.vault_status}</span>
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {vault.documents.map((doc) => (
          <div key={doc.doc_id} className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-4 space-y-2">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-semibold text-white">{doc.document_name}</p>
                <p className="text-xs text-slate-400">{doc.issuer}</p>
              </div>
              <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${badgeStyle(doc.verification_badge)}`}>
                {doc.verification_badge.replace(/_/g, ' ')}
              </span>
            </div>

            <div className="flex items-center justify-between text-xs pt-2 border-t border-slate-800/80">
              <div className="flex items-center space-x-1 text-slate-400">
                <Clock className="w-3.5 h-3.5" />
                <span>
                  {doc.is_valid ? `${doc.days_to_expiry} days to expiry` : 'Expired'}
                </span>
              </div>
              <div className="flex items-center space-x-1 text-slate-400">
                <RefreshCw className="w-3.5 h-3.5" />
                <span>Reused {doc.reuse_count}x</span>
              </div>
            </div>

            {!doc.is_valid && (
              <div className="flex items-center space-x-1.5 text-xs text-rose-400 pt-1">
                <AlertTriangle className="w-3.5 h-3.5" />
                <span>Needs renewal before reuse on a new bid</span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
