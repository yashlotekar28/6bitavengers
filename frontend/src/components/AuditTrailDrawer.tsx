import React from 'react';
import { X, Activity, Clock, ShieldCheck, Cpu, CheckCircle2, User } from 'lucide-react';
import { AuditLogEntry } from '../types';

interface AuditDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  logs: AuditLogEntry[];
}

export const AuditTrailDrawer: React.FC<AuditDrawerProps> = ({ isOpen, onClose, logs }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-black/70 backdrop-blur-sm flex justify-end transition-opacity">
      <div className="w-full max-w-2xl bg-slate-900 border-l border-slate-800 h-full flex flex-col shadow-2xl">
        
        {/* Drawer Header */}
        <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-950">
          <div className="flex items-center space-x-2">
            <div className="p-2 bg-blue-500/20 text-blue-400 rounded-lg">
              <Activity className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-white uppercase tracking-wider">
                Immutable Compliance Audit Trail
              </h2>
              <p className="text-xs text-slate-400">Step 2 to Step 10 chronological event logs</p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Logs Timeline */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {logs.map((log) => {
            let actorIcon = <Cpu className="w-4 h-4 text-blue-400" />;
            let actorColor = "text-blue-400 bg-blue-500/10 border-blue-500/30";

            if (log.actor === 'OFFICER') {
              actorIcon = <User className="w-4 h-4 text-purple-400" />;
              actorColor = "text-purple-400 bg-purple-500/10 border-purple-500/30";
            } else if (log.actor === 'RULES_ENGINE') {
              actorIcon = <CheckCircle2 className="w-4 h-4 text-emerald-400" />;
              actorColor = "text-emerald-400 bg-emerald-500/10 border-emerald-500/30";
            } else if (log.actor === 'CROSS_CHECK_ENGINE') {
              actorIcon = <ShieldCheck className="w-4 h-4 text-amber-400" />;
              actorColor = "text-amber-400 bg-amber-500/10 border-amber-500/30";
            }

            return (
              <div key={log.log_id} className="relative pl-6 pb-4 border-l-2 border-slate-800 last:border-transparent">
                {/* Timeline bullet */}
                <div className="absolute -left-[9px] top-0 w-4 h-4 rounded-full bg-slate-900 border-2 border-blue-500" />

                <div className="bg-slate-950/80 border border-slate-800/80 rounded-xl p-3.5 space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span className={`px-2 py-0.5 text-[10px] font-bold rounded border flex items-center space-x-1 ${actorColor}`}>
                        {actorIcon}
                        <span>{log.actor}</span>
                      </span>
                      <span className="text-xs font-bold text-white">{log.step}</span>
                    </div>

                    <div className="flex items-center space-x-1 text-[10px] text-slate-500 font-mono">
                      <Clock className="w-3 h-3" />
                      <span>{new Date(log.timestamp).toLocaleTimeString()}</span>
                    </div>
                  </div>

                  <p className="text-xs font-semibold text-slate-300 font-mono">
                    Action: {log.action_type}
                  </p>

                  {log.notes && (
                    <p className="text-xs text-indigo-300 bg-indigo-950/30 p-2 rounded border border-indigo-900/40">
                      📝 {log.notes}
                    </p>
                  )}

                  <div className="bg-slate-900 p-2 rounded-lg border border-slate-800 text-[11px] font-mono text-slate-400 overflow-x-auto">
                    <pre>{JSON.stringify(log.details, null, 2)}</pre>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Drawer Footer */}
        <div className="p-3 border-t border-slate-800 bg-slate-950 text-center text-xs text-slate-500 font-mono">
          Cryptographically hashed • Complies with GFR & CAG Audit Standards
        </div>

      </div>
    </div>
  );
};
