import { Bidder, DashboardMetrics, AuditLogEntry, VendorVault, LongitudinalTrustScore, EntityGraph, OfficerChatRequest, OfficerChatResponse } from '../types';

const API_BASE = '/api';

export const fetchBidders = async (): Promise<Bidder[]> => {
  const res = await fetch(`${API_BASE}/bidders`);
  if (!res.ok) throw new Error('Failed to fetch bidders');
  return res.json();
};

export const fetchBidderById = async (bidderId: string): Promise<Bidder> => {
  const res = await fetch(`${API_BASE}/bidders/${bidderId}`);
  if (!res.ok) throw new Error('Failed to fetch bidder');
  return res.json();
};

export const triggerVerification = async (bidderId: string): Promise<Bidder> => {
  const res = await fetch(`${API_BASE}/bidders/verify/${bidderId}`, {
    method: 'POST'
  });
  if (!res.ok) throw new Error('Failed to trigger verification');
  return res.json();
};

export const resetDemoScenarios = async (): Promise<any> => {
  const res = await fetch(`${API_BASE}/bidders/reset-demo`, {
    method: 'POST'
  });
  if (!res.ok) throw new Error('Failed to reset demo');
  return res.json();
};

export const submitOfficerDecision = async (payload: {
  bidder_id: string;
  action: string;
  officer_id: string;
  officer_name: string;
  comments: string;
  override_justification?: string;
}): Promise<any> => {
  const res = await fetch(`${API_BASE}/officer/decision`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error('Failed to record decision');
  return res.json();
};

export const fetchAuditLogs = async (bidderId?: string): Promise<AuditLogEntry[]> => {
  const url = bidderId ? `${API_BASE}/audit?bidder_id=${bidderId}` : `${API_BASE}/audit`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch audit logs');
  return res.json();
};

export const fetchMetrics = async (): Promise<DashboardMetrics> => {
  const res = await fetch(`${API_BASE}/metrics`);
  if (!res.ok) throw new Error('Failed to fetch metrics');
  return res.json();
};

export const fetchVault = async (bidderId: string): Promise<VendorVault> => {
  const res = await fetch(`${API_BASE}/vault/${bidderId}`);
  if (!res.ok) throw new Error('Failed to fetch vault');
  return res.json();
};

export const fetchTrustScore = async (bidderId: string): Promise<LongitudinalTrustScore> => {
  const res = await fetch(`${API_BASE}/trust-score/${bidderId}`);
  if (!res.ok) throw new Error('Failed to fetch trust score');
  return res.json();
};

export const fetchEntityGraph = async (tenderId: string): Promise<EntityGraph> => {
  const res = await fetch(`${API_BASE}/graph/tender/${tenderId}`);
  if (!res.ok) throw new Error('Failed to fetch entity graph');
  return res.json();
};

export const sendOfficerChatQuery = async (payload: OfficerChatRequest): Promise<OfficerChatResponse> => {
  const res = await fetch(`${API_BASE}/chat/officer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error('Failed to send chat query');
  return res.json();
};
