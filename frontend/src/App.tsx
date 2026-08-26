import React, { useState, useEffect } from 'react';
import { Bidder, DashboardMetrics, AuditLogEntry } from './types';
import { fetchBidders, fetchMetrics, fetchAuditLogs, triggerVerification, resetDemoScenarios, submitOfficerDecision } from './services/api';
import { Navbar } from './components/Navbar';
import { MetricsOverview } from './components/MetricsOverview';
import { BidderListView } from './components/BidderListView';
import { BidderDetailView } from './components/BidderDetailView';
import { AuditTrailDrawer } from './components/AuditTrailDrawer';
import { ShieldCheck, Loader2 } from 'lucide-react';

export const App: React.FC = () => {
  const [bidders, setBidders] = useState<Bidder[]>([]);
  const [selectedBidderId, setSelectedBidderId] = useState<string>('BID-2026-0891');
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [auditLogs, setAuditLogs] = useState<AuditLogEntry[]>([]);
  const [isAuditOpen, setIsAuditOpen] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isVerifying, setIsVerifying] = useState<boolean>(false);
  const [notification, setNotification] = useState<string | null>(null);

  const showNotification = (msg: string) => {
    setNotification(msg);
    setTimeout(() => setNotification(null), 4000);
  };

  const loadData = async () => {
    try {
      setIsLoading(true);
      const [bList, mData, aLogs] = await Promise.all([
        fetchBidders(),
        fetchMetrics(),
        fetchAuditLogs()
      ]);
      setBidders(bList);
      setMetrics(mData);
      setAuditLogs(aLogs);
      if (bList.length > 0 && !selectedBidderId) {
        setSelectedBidderId(bList[0].bidder_id);
      }
    } catch (err) {
      console.error('Failed to load initial data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleReverify = async () => {
    if (!selectedBidderId) return;
    try {
      setIsVerifying(true);
      const updatedBidder = await triggerVerification(selectedBidderId);
      setBidders(prev => prev.map(b => b.bidder_id === updatedBidder.bidder_id ? updatedBidder : b));
      const [mData, aLogs] = await Promise.all([fetchMetrics(), fetchAuditLogs()]);
      setMetrics(mData);
      setAuditLogs(aLogs);
      showNotification(`Verification successfully re-executed for ${updatedBidder.company_name}!`);
    } catch (err) {
      console.error('Re-verification failed:', err);
      showNotification('Re-verification error occurred.');
    } finally {
      setIsVerifying(false);
    }
  };

  const handleResetDemo = async () => {
    try {
      setIsLoading(true);
      await resetDemoScenarios();
      await loadData();
      showNotification('All 3 demo scenarios reset and fresh verification completed!');
    } catch (err) {
      console.error('Failed to reset demo:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDecisionSubmit = async (action: string, comments: string, overrideJustification?: string) => {
    if (!selectedBidderId) return;
    try {
      setIsVerifying(true);
      await submitOfficerDecision({
        bidder_id: selectedBidderId,
        action,
        officer_id: 'OFFICER-GEM-994',
        officer_name: 'Rajesh Kumar (Senior Procurement Officer)',
        comments,
        override_justification: overrideJustification
      });
      await loadData();
      showNotification(`Officer decision (${action}) recorded and committed to audit trail!`);
    } catch (err) {
      console.error('Decision submission failed:', err);
      showNotification('Failed to record officer decision.');
    } finally {
      setIsVerifying(false);
    }
  };

  const selectedBidder = bidders.find(b => b.bidder_id === selectedBidderId) || bidders[0];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      
      {/* Navigation Header */}
      <Navbar
        bidders={bidders}
        selectedBidderId={selectedBidderId}
        onSelectBidder={setSelectedBidderId}
        onResetDemo={handleResetDemo}
        onOpenAudit={() => setIsAuditOpen(true)}
        isLoading={isLoading}
      />

      {/* Floating Alert Notification */}
      {notification && (
        <div className="fixed top-20 right-6 z-50 bg-blue-600 border border-blue-400 text-white px-4 py-3 rounded-xl shadow-2xl flex items-center space-x-2 text-xs font-semibold animate-bounce">
          <ShieldCheck className="w-4 h-4" />
          <span>{notification}</span>
        </div>
      )}

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {isLoading && bidders.length === 0 ? (
          <div className="h-96 flex flex-col items-center justify-center space-y-3">
            <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
            <p className="text-sm text-slate-400">Loading GeM Verification Engine...</p>
          </div>
        ) : (
          <>
            {/* Top KPI Metrics Row */}
            <MetricsOverview metrics={metrics} />

            {/* Bidders Queue Selector */}
            <BidderListView
              bidders={bidders}
              selectedBidderId={selectedBidderId}
              onSelectBidder={setSelectedBidderId}
            />

            {/* Detailed Verification Workspace */}
            {selectedBidder && (
              <BidderDetailView
                bidder={selectedBidder}
                onReverify={handleReverify}
                onDecisionSubmit={handleDecisionSubmit}
                isVerifying={isVerifying}
              />
            )}
          </>
        )}
      </main>

      {/* Audit Trail Drawer */}
      <AuditTrailDrawer
        isOpen={isAuditOpen}
        onClose={() => setIsAuditOpen(false)}
        logs={auditLogs}
      />

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-4 text-center text-xs text-slate-500 font-mono">
        ProcureShield AI • GeM / CPPP Public Procurement Compliance Engine • 10-Step Deterministic & AI Architecture
      </footer>

    </div>
  );
};
export default App;
