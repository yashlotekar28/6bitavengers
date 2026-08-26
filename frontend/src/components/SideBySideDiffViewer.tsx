import React, { useState } from 'react';
import { FileSearch, Layers, AlertTriangle, CheckCircle, FileText, Globe } from 'lucide-react';
import { UploadedDocument, PortalVerificationResult, CrossCheckMismatch } from '../types';

interface SideBySideProps {
  documents: UploadedDocument[];
  portalVerifications: Record<string, PortalVerificationResult>;
  mismatches: CrossCheckMismatch[];
}

export const SideBySideDiffViewer: React.FC<SideBySideProps> = ({
  documents,
  portalVerifications,
  mismatches
}) => {
  const [selectedDocIndex, setSelectedDocIndex] = useState<number>(0);

  const activeDoc = documents[selectedDocIndex] || documents[0];
  const gstPortal = portalVerifications['GST_PORTAL'];
  const udyamPortal = portalVerifications['UDYAM_PORTAL'];

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-lg">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-3">
        <div className="flex items-center space-x-2">
          <Layers className="w-5 h-5 text-indigo-400" />
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              Cross-Verification Inspector (OCR vs Portal)
            </h3>
            <p className="text-xs text-slate-400">
              Live reconciliation between submitted PDFs and official Gov Registries
            </p>
          </div>
        </div>

        {/* Document Selector tabs */}
        <div className="flex items-center space-x-1.5 bg-slate-950 p-1 rounded-lg border border-slate-800 overflow-x-auto">
          {documents.map((doc, idx) => (
            <button
              key={doc.doc_id}
              onClick={() => setSelectedDocIndex(idx)}
              className={`px-2.5 py-1 text-xs font-medium rounded-md whitespace-nowrap transition-all flex items-center space-x-1 ${
                selectedDocIndex === idx
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <FileText className="w-3 h-3" />
              <span>{doc.doc_type.replace('_', ' ')}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Discrepancy Alerts Banner */}
      {mismatches.length > 0 ? (
        <div className="mt-4 p-3.5 bg-amber-950/30 border border-amber-500/40 rounded-xl">
          <div className="flex items-center space-x-2 text-amber-300 font-semibold text-xs mb-2">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            <span>{mismatches.length} Cross-Verification Discrepanc{mismatches.length > 1 ? 'ies' : 'y'} Flagged:</span>
          </div>
          <div className="space-y-1.5">
            {mismatches.map((m, i) => (
              <div key={i} className="text-xs bg-slate-950/60 p-2 rounded-lg border border-amber-900/40 text-slate-300">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-white">{m.field_name}</span>
                  <span className={`text-[10px] px-1.5 py-0.5 rounded font-bold uppercase ${
                    m.severity === 'CRITICAL' ? 'bg-rose-500/20 text-rose-300' : 'bg-amber-500/20 text-amber-300'
                  }`}>
                    {m.severity} RISK
                  </span>
                </div>
                <p className="mt-1 text-amber-200">{m.discrepancy_explanation}</p>
                <div className="mt-1 flex flex-wrap gap-2 text-[11px] font-mono text-slate-400">
                  <span className="bg-slate-900 px-1.5 py-0.5 rounded border border-slate-800">
                    Doc: <strong className="text-rose-300">{String(m.source_a_value)}</strong>
                  </span>
                  <span className="bg-slate-900 px-1.5 py-0.5 rounded border border-slate-800">
                    Portal: <strong className="text-emerald-300">{String(m.source_b_value)}</strong>
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="mt-4 p-3 bg-emerald-950/20 border border-emerald-500/30 rounded-xl flex items-center space-x-2 text-emerald-300 text-xs">
          <CheckCircle className="w-4 h-4 text-emerald-400" />
          <span>All document fields reconcile 100% with live government registry databases.</span>
        </div>
      )}

      {/* Side by Side Comparison Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
        
        {/* Left: Uploaded Document (OCR Extraction) */}
        <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between mb-3 pb-2 border-b border-slate-800">
            <div className="flex items-center space-x-2 text-blue-400">
              <FileSearch className="w-4 h-4" />
              <span className="text-xs font-bold uppercase tracking-wider text-slate-300">
                Uploaded Document (OCR Extracted)
              </span>
            </div>
            <span className="text-[10px] bg-slate-800 text-slate-400 px-2 py-0.5 rounded font-mono">
              Conf: {(activeDoc?.confidence * 100).toFixed(0)}%
            </span>
          </div>

          <p className="text-xs font-semibold text-white mb-2 truncate">{activeDoc?.file_name}</p>

          <div className="space-y-2 text-xs font-mono">
            {activeDoc && Object.entries(activeDoc.extracted_fields).map(([key, val]) => (
              <div key={key} className="bg-slate-900/80 p-2 rounded-lg border border-slate-800/80 flex flex-col">
                <span className="text-[10px] text-slate-500 uppercase tracking-wider">{key.replace(/_/g, ' ')}</span>
                <span className="text-slate-200 mt-0.5 font-medium">{typeof val === 'object' ? JSON.stringify(val) : String(val)}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Live Government Portal Telemetry */}
        <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between mb-3 pb-2 border-b border-slate-800">
            <div className="flex items-center space-x-2 text-emerald-400">
              <Globe className="w-4 h-4" />
              <span className="text-xs font-bold uppercase tracking-wider text-slate-300">
                Live Registry Record (API Setu / Portal)
              </span>
            </div>
            <span className="text-[10px] bg-emerald-500/20 text-emerald-300 px-2 py-0.5 rounded font-mono">
              AUTHENTICATED
            </span>
          </div>

          <p className="text-xs font-semibold text-emerald-400 mb-2">
            {activeDoc?.doc_type === 'UDYAM_CERTIFICATE' ? udyamPortal?.source : gstPortal?.source}
          </p>

          <div className="space-y-2 text-xs font-mono">
            {activeDoc?.doc_type === 'UDYAM_CERTIFICATE' && udyamPortal ? (
              Object.entries(udyamPortal.key_fields).map(([key, val]) => (
                <div key={key} className="bg-slate-900/80 p-2 rounded-lg border border-slate-800/80 flex flex-col">
                  <span className="text-[10px] text-slate-500 uppercase tracking-wider">{key.replace(/_/g, ' ')}</span>
                  <span className="text-slate-200 mt-0.5 font-medium">{String(val)}</span>
                </div>
              ))
            ) : gstPortal ? (
              Object.entries(gstPortal.key_fields).map(([key, val]) => (
                <div key={key} className="bg-slate-900/80 p-2 rounded-lg border border-slate-800/80 flex flex-col">
                  <span className="text-[10px] text-slate-500 uppercase tracking-wider">{key.replace(/_/g, ' ')}</span>
                  <span className="text-slate-200 mt-0.5 font-medium">{String(val)}</span>
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-500">No portal record available</p>
            )}
          </div>
        </div>

      </div>
    </div>
  );
};
