import React, { useMemo } from 'react';
import { Network, ShieldAlert, ShieldCheck } from 'lucide-react';
import { EntityGraph, EntityGraphNode } from '../types';

interface EntityGraphPanelProps {
  graph: EntityGraph | null;
  isLoading: boolean;
}

const nodeColor = (node: EntityGraphNode) => {
  if (node.risk_level === 'CRITICAL' || node.risk_level === 'HIGH') return { fill: '#F43F5E', text: '#FDA4AF' };
  if (node.risk_level === 'MEDIUM') return { fill: '#F59E0B', text: '#FCD34D' };
  if (node.type === 'BIDDER') return { fill: '#3B82F6', text: '#93C5FD' };
  return { fill: '#64748B', text: '#CBD5E1' };
};

export const EntityGraphPanel: React.FC<EntityGraphPanelProps> = ({ graph, isLoading }) => {
  const layout = useMemo(() => {
    if (!graph || graph.nodes.length === 0) return { positions: {}, width: 600, height: 320 };
    const width = 600;
    const height = 320;
    const cx = width / 2;
    const cy = height / 2;
    const radius = Math.min(width, height) / 2 - 60;
    const positions: Record<string, { x: number; y: number }> = {};
    graph.nodes.forEach((node, i) => {
      const angle = (2 * Math.PI * i) / graph.nodes.length - Math.PI / 2;
      positions[node.id] = { x: cx + radius * Math.cos(angle), y: cy + radius * Math.sin(angle) };
    });
    return { positions, width, height };
  }, [graph]);

  if (isLoading) {
    return (
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 text-sm text-slate-400">
        Loading entity linkage graph...
      </div>
    );
  }

  if (!graph || graph.nodes.length === 0) {
    return (
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 text-sm text-slate-400">
        No entity graph data available for this tender.
      </div>
    );
  }

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-blue-600/20 border border-blue-500/30 text-blue-400 rounded-xl">
            <Network className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white">Graph-based entity linkage</h3>
            <p className="text-xs text-slate-400">Director, address &amp; bank-account relationship network</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <span className={`flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-bold border ${
            graph.debarment_links_found > 0
              ? 'bg-rose-500/20 text-rose-300 border-rose-500/40'
              : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
          }`}>
            {graph.debarment_links_found > 0 ? <ShieldAlert className="w-3.5 h-3.5" /> : <ShieldCheck className="w-3.5 h-3.5" />}
            <span>{graph.debarment_links_found} debarment link{graph.debarment_links_found === 1 ? '' : 's'}</span>
          </span>
        </div>
      </div>

      <svg viewBox={`0 0 ${layout.width} ${layout.height}`} className="w-full h-72 bg-slate-950/60 border border-slate-800/80 rounded-xl">
        {graph.edges.map((edge, i) => {
          const src = layout.positions[edge.source];
          const tgt = layout.positions[edge.target];
          if (!src || !tgt) return null;
          return (
            <g key={i}>
              <line
                x1={src.x} y1={src.y} x2={tgt.x} y2={tgt.y}
                stroke={edge.is_conflict ? '#F43F5E' : '#475569'}
                strokeWidth={edge.is_conflict ? 2 : 1}
                strokeDasharray={edge.is_conflict ? '4 3' : undefined}
              />
              <text
                x={(src.x + tgt.x) / 2} y={(src.y + tgt.y) / 2 - 4}
                fontSize="9" textAnchor="middle"
                fill={edge.is_conflict ? '#FDA4AF' : '#64748B'}
              >
                {edge.relationship.replace(/_/g, ' ')}
              </text>
            </g>
          );
        })}
        {graph.nodes.map((node) => {
          const pos = layout.positions[node.id];
          const color = nodeColor(node);
          if (!pos) return null;
          return (
            <g key={node.id}>
              <circle cx={pos.x} cy={pos.y} r={22} fill="#0F172A" stroke={color.fill} strokeWidth="2" />
              <text x={pos.x} y={pos.y + 3} fontSize="9" textAnchor="middle" fill={color.text} fontWeight="600">
                {node.type.slice(0, 3)}
              </text>
              <text x={pos.x} y={pos.y + 36} fontSize="10" textAnchor="middle" fill="#CBD5E1">
                {node.label.length > 18 ? `${node.label.slice(0, 16)}...` : node.label}
              </text>
            </g>
          );
        })}
      </svg>

      {graph.edges.filter((e) => e.is_conflict).length > 0 && (
        <div className="space-y-2">
          {graph.edges.filter((e) => e.is_conflict).map((edge, i) => (
            <div key={i} className="flex items-start space-x-2 bg-rose-950/30 border border-rose-500/30 rounded-xl p-3 text-xs">
              <ShieldAlert className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
              <div>
                <p className="text-rose-300 font-semibold">
                  {edge.relationship.replace(/_/g, ' ')} &middot; confidence {(edge.confidence * 100).toFixed(0)}%
                </p>
                {edge.explanation && <p className="text-slate-400 mt-0.5">{edge.explanation}</p>}
              </div>
            </div>
          ))}
        </div>
      )}

      <p className="text-xs text-slate-400 border-t border-slate-800 pt-3">{graph.risk_summary}</p>
    </div>
  );
};
