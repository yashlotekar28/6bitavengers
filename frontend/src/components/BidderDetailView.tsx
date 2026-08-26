import React, { useState, useEffect } from 'react';
import { Building, RefreshCw, Layers, CheckSquare, FileText, Vault, Award, Network, MessageSquare } from 'lucide-react';
import { Bidder, VendorVault, LongitudinalTrustScore, EntityGraph } from '../types';
import { ScoreGauge } from './ScoreGauge';
import { RulesChecklistView } from './RulesChecklistView';
import { SideBySideDiffViewer } from './SideBySideDiffViewer';
import { AIRecommendationCard } from './AIRecommendationCard';
import { OfficerActionPanel } from './OfficerActionPanel';
import { VaultPanel } from './VaultPanel';
import { TrustScorePanel } from './TrustScorePanel';
import { EntityGraphPanel } from './EntityGraphPanel';
import { OfficerChatPanel } from './OfficerChatPanel';
import { fetchVault, fetchTrustScore, fetchEntityGraph } from '../services/api';

interface BidderDetailProps {
  bidder: Bidder;
  onReverify: () => Promise<void>;
  onDecisionSubmit: (action: string, comments: string, overrideJustification?: string) => Promise<void>;
  isVerifying: boolean;
}

export const BidderDetailView: React.FC<BidderDetailProps> = ({
  bidder,
  onReverify,
  onDecisionSubmit,
  isVerifying
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'rules' | 'diff' | 'ai' | 'vault' | 'trust' | 'graph' | 'chat'>('overview');

  const [vault, setVault] = useState<VendorVault | null>(null);
  const [isVaultLoading, setIsVaultLoading] = useState(false);
  const [trustScore, setTrustScore] = useState<LongitudinalTrustScore | null>(null);
  const [isTrustLoading, setIsTrustLoading] = useState(false);
  const [entityGraph, setEntityGraph] = useState<EntityGraph | null>(null);
  const [isGraphLoading, setIsGraphLoading] = useState(false);

  useEffect(() => {
    setVault(null);
    setTrustScore(null);
    setEntityGraph(null);
  }, [bidder.bidder_id]);

  useEffect(() => {
    if (activeTab === 'vault' && !vault && !isVaultLoading) {
      setIsVaultLoading(true);
      fetchVault(bidder.bidder_id).then(setVault).catch(console.error).finally(() => setIsVaultLoading(false));
    }
    if (activeTab === 'trust' && !trustScore && !isTrustLoading) {
      setIsTrustLoading(true);
      fetchTrustScore(bidder.bidder_id).then(setTrustScore).catch(console.error).finally(() => setIsTrustLoading(false));
    }
    if (activeTab === 'graph' && !entityGraph && !isGraphLoading) {
      setIsGraphLoading(true);
      fetchEntityGraph(bidder.tender_id).then(setEntityGraph).catch(console.error).finally(() => setIsGraphLoading(false));
    }
  }, [activeTab, bidder.bidder_id, bidder.tender_id]);

  const formatCurrency = (val: number) => {
    if (val >= 10000000) return `₹${(val / 10000000).toFixed(2)} Cr`;
    if (val >= 100000) return `₹${(val / 100000).toFixed(2)} Lakh`;
    return `₹${val.toLocaleString('en-IN')}`;
  };

  return (
    <div className="space-y-6">
      {/* Bidder Profile Header Card */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl relative overflow-hidden">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          
          <div className="flex items-start space-x-4">
            <div className="p-3.5 bg-blue-600/20 border border-blue-500/30 text-blue-400 rounded-2xl">
              <Building className="w-8 h-8" />
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <h2 className="text-xl font-extrabold text-white tracking-tight">{bidder.company_name}</h2>
                <span className="text-xs bg-slate-800 text-slate-300 px-2.5 py-0.5 rounded font-mono border border-slate-700">
                  {bidder.bidder_id}
                </span>
                <span className="text-xs bg-blue-500/20 text-blue-300 px-2 py-0.5 rounded border border-blue-500/30 font-semibold">
                  {bidder.legal_structure}
                </span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-4 text-xs font-mono text-slate-300">
                <div className="bg-slate-950/70 p-2 rounded-lg border border-slate-800">
                  <span className="text-[10px] text-slate-500 block uppercase">GSTIN Registration</span>
                  <span className="font-bold text-white">{bidder.identifiers.gstin || 'N/A'}</span>
                </div>
                <div className="bg-slate-950/70 p-2 rounded-lg border border-slate-800">
                  <span className="text-[10px] text-slate-500 block uppercase">PAN Identifier</span>
                  <span className="font-bold text-white">{bidder.identifiers.pan || 'N/A'}</span>
                </div>
                <div className="bg-slate-950/70 p-2 rounded-lg border border-slate-800">
                  <span className="text-[10px] text-slate-500 block uppercase">MSME Udyam Number</span>
                  <span className="font-bold text-white">{bidder.identifiers.udyam_registration_number || 'N/A'}</span>
                </div>
                <div className="bg-slate-950/70 p-2 rounded-lg border border-slate-800">
                  <span className="text-[10px] text-slate-500 block uppercase">Declared Turnover</span>
                  <span className="font-bold text-emerald-400">{formatCurrency(bidder.financials.annual_turnover_inr)}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Re-verify action */}
          <div className="flex flex-col items-end justify-center self-start lg:self-center">
            <button
              onClick={onReverify}
              disabled={isVerifying}
              className="flex items-center space-x-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold rounded-xl transition shadow-lg disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${isVerifying ? 'animate-spin' : ''}`} />
              <span>{isVerifying ? 'Running 10-Step Pipeline...' : 'Re-Run Verification Pipeline'}</span>
            </button>
            <span className="text-[10px] text-slate-400 mt-1 font-mono">
              Last Verified: {new Date().toLocaleDateString()}
            </span>
          </div>

        </div>
      </div>

      {/* Top Grid: Compliance Score Gauge + AI Recommendation Engine */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <ScoreGauge complianceScore={bidder.compliance_score} />
        </div>
        <div className="lg:col-span-2">
          <AIRecommendationCard recommendation={bidder.ai_recommendation} />
        </div>
      </div>

      {/* Primary Verification Workspace: Tabs & Panes */}
      <div className="space-y-4">
        <div className="flex items-center space-x-2 border-b border-slate-800 pb-2">
          <button
            onClick={() => setActiveTab('overview')}
            className={`px-4 py-2 text-xs font-bold rounded-xl transition flex items-center space-x-2 ${
              activeTab === 'overview'
                ? 'bg-blue-600 text-white shadow-md'
                : 'bg-slate-900 text-slate-400 hover:text-white border border-slate-800'
            }`}
          >
            <Layers className="w-4 h-4" />
            <span>Complete Verification Cockpit</span>
          </button>

          <button
            onClick={() => setActiveTab('diff')}
            className={`px-4 py-2 text-xs font-bold rounded-xl transition flex items-center space-x-2 ${
              activeTab === 'diff'
                ? 'bg-blue-600 text-white shadow-md'
                : 'bg-slate-900 text-slate-400 hover:text-white border border-slate-800'
            }`}
          >
            <FileText className="w-4 h-4" />
            <span>Document vs Portal Diff ({bidder.cross_check_mismatches.length} Flags)</span>
          </button>

          <button
            onClick={() => setActiveTab('rules')}
            className={`px-4 py-2 text-xs font-bold rounded-xl transition flex items-center space-x-2 ${
              activeTab === 'rules'
                ? 'bg-blue-600 text-white shadow-md'
                : 'bg-slate-900 text-slate-400 hover:text-white border border-slate-800'
            }`}
          >
            <CheckSquare className="w-4 h-4" />
            <span>Deterministic Rules ({bidder.rule_results.length})</span>
          </button>

          <button
            onClick={() => setActiveTab('vault')}
            className={`px-4 py-2 text-xs font-bold rounded-xl transition flex items-center space-x-2 ${
              activeTab === 'vault'
                ? 'bg-blue-600 text-white shadow-md'
                : 'bg-slate-900 text-slate-400 hover:text-white border border-slate-800'
            }`}
          >
            <Vault className="w-4 h-4" />
            <span>Document Vault</span>
          </button>

          <button
            onClick={() => setActiveTab('trust')}
            className={`px-4 py-2 text-xs font-bold rounded-xl transition flex items-center space-x-2 ${
              activeTab === 'trust'
                ? 'bg-blue-600 text-white shadow-md'
                : 'bg-slate-900 text-slate-400 hover:text-white border border-slate-800'
            }`}
          >
            <Award className="w-4 h-4" />
            <span>Trust Score</span>
          </button>

          <button
            onClick={() => setActiveTab('graph')}
            className={`px-4 py-2 text-xs font-bold rounded-xl transition flex items-center space-x-2 ${
              activeTab === 'graph'
                ? 'bg-blue-600 text-white shadow-md'
                : 'bg-slate-900 text-slate-400 hover:text-white border border-slate-800'
            }`}
          >
            <Network className="w-4 h-4" />
            <span>Entity Graph</span>
          </button>

          <button
            onClick={() => setActiveTab('chat')}
            className={`px-4 py-2 text-xs font-bold rounded-xl transition flex items-center space-x-2 ${
              activeTab === 'chat'
                ? 'bg-blue-600 text-white shadow-md'
                : 'bg-slate-900 text-slate-400 hover:text-white border border-slate-800'
            }`}
          >
            <MessageSquare className="w-4 h-4" />
            <span>Officer Assistant</span>
          </button>
        </div>

        {/* Tab Panes */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <SideBySideDiffViewer
              documents={bidder.documents}
              portalVerifications={bidder.portal_verifications}
              mismatches={bidder.cross_check_mismatches}
            />
            <RulesChecklistView rules={bidder.rule_results} />
          </div>
        )}

        {activeTab === 'diff' && (
          <SideBySideDiffViewer
            documents={bidder.documents}
            portalVerifications={bidder.portal_verifications}
            mismatches={bidder.cross_check_mismatches}
          />
        )}

        {activeTab === 'rules' && (
          <RulesChecklistView rules={bidder.rule_results} />
        )}

        {activeTab === 'vault' && (
          <VaultPanel vault={vault} isLoading={isVaultLoading} />
        )}

        {activeTab === 'trust' && (
          <TrustScorePanel trustScore={trustScore} isLoading={isTrustLoading} />
        )}

        {activeTab === 'graph' && (
          <EntityGraphPanel graph={entityGraph} isLoading={isGraphLoading} />
        )}

        {activeTab === 'chat' && (
          <OfficerChatPanel activeBidderId={bidder.bidder_id} tenderId={bidder.tender_id} />
        )}
      </div>

      {/* Step 9: Human-in-the-loop Officer Decision Workflow */}
      <OfficerActionPanel
        bidderId={bidder.bidder_id}
        currentStatus={bidder.officer_status}
        officerNotes={bidder.officer_notes}
        onDecisionSubmit={onDecisionSubmit}
        isSubmitting={isVerifying}
      />
    </div>
  );
};
