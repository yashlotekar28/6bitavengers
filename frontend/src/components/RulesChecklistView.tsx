import React from 'react';
import { CheckCircle2, XCircle, AlertCircle, ShieldAlert, FileCode2 } from 'lucide-react';
import { RuleEvaluationResult } from '../types';

interface RulesChecklistProps {
  rules: RuleEvaluationResult[];
}

export const RulesChecklistView: React.FC<RulesChecklistProps> = ({ rules }) => {
  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-lg">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <FileCode2 className="w-5 h-5 text-blue-400" />
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">
            Deterministic Rules Engine (Pass / Fail)
          </h3>
        </div>
        <span className="text-xs bg-slate-800 text-slate-300 px-2.5 py-1 rounded-md border border-slate-700 font-mono">
          YAML Rule Evaluator
        </span>
      </div>

      <div className="space-y-2.5">
        {rules.map((rule) => {
          const isPassed = rule.passed;
          const isHardBlock = rule.is_hard_block;

          return (
            <div
              key={rule.rule_id}
              className={`p-3 rounded-xl border transition-all ${
                isPassed
                  ? 'bg-slate-950/40 border-slate-800/80 hover:border-emerald-500/30'
                  : isHardBlock
                  ? 'bg-rose-950/20 border-rose-500/40 shadow-sm'
                  : 'bg-amber-950/20 border-amber-500/40'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3">
                  <div className="mt-0.5">
                    {isPassed ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    ) : isHardBlock ? (
                      <XCircle className="w-4 h-4 text-rose-400" />
                    ) : (
                      <AlertCircle className="w-4 h-4 text-amber-400" />
                    )}
                  </div>

                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-semibold text-white">{rule.rule_name}</span>
                      <span className="text-[10px] px-1.5 py-0.2 bg-slate-800 text-slate-400 rounded border border-slate-700 font-mono">
                        {rule.category}
                      </span>
                      {isHardBlock && (
                        <span className="text-[9px] px-1.5 py-0.2 bg-rose-500/20 text-rose-300 rounded font-bold uppercase tracking-wider">
                          Hard Gate
                        </span>
                      )}
                    </div>

                    <div className="mt-1 flex items-center space-x-3 text-[11px] text-slate-400 font-mono">
                      <span>Condition: <span className="text-slate-300">{rule.expected_condition}</span></span>
                      <span>•</span>
                      <span>Evaluated: <span className={isPassed ? "text-emerald-400" : "text-rose-400"}>{String(rule.actual_value)}</span></span>
                    </div>

                    {!isPassed && rule.failure_reason && (
                      <p className="mt-1.5 text-xs text-rose-300 bg-rose-950/40 p-1.5 rounded border border-rose-900/50">
                        ⚠️ {rule.failure_reason}
                      </p>
                    )}
                  </div>
                </div>

                <div className="ml-2">
                  <span
                    className={`px-2 py-0.5 text-[10px] font-bold rounded uppercase ${
                      isPassed
                        ? 'bg-emerald-500/20 text-emerald-300'
                        : isHardBlock
                        ? 'bg-rose-500/20 text-rose-300'
                        : 'bg-amber-500/20 text-amber-300'
                    }`}
                  >
                    {isPassed ? 'PASS' : isHardBlock ? 'HARD FAIL' : 'WARN'}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
