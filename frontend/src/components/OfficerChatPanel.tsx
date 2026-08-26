import React, { useState } from 'react';
import { MessageSquare, Send, Loader2 } from 'lucide-react';
import { OfficerChatResponse } from '../types';
import { sendOfficerChatQuery } from '../services/api';

interface OfficerChatPanelProps {
  activeBidderId?: string;
  tenderId: string;
}

interface ChatTurn {
  query: string;
  response: OfficerChatResponse;
}

export const OfficerChatPanel: React.FC<OfficerChatPanelProps> = ({ activeBidderId, tenderId }) => {
  const [input, setInput] = useState('');
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSend = async () => {
    const query = input.trim();
    if (!query) {
      setError('Type a question first');
      return;
    }
    setError(null);
    setIsSending(true);
    try {
      const response = await sendOfficerChatQuery({ query, tender_id: tenderId, active_bidder_id: activeBidderId });
      setTurns((prev) => [...prev, { query, response }]);
      setInput('');
    } catch (err) {
      console.error('Chat query failed:', err);
      setError('Query failed — try again');
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
      <div className="flex items-center space-x-3">
        <div className="p-2.5 bg-blue-600/20 border border-blue-500/30 text-blue-400 rounded-xl">
          <MessageSquare className="w-5 h-5" />
        </div>
        <div>
          <h3 className="text-sm font-bold text-white">Officer assistant</h3>
          <p className="text-xs text-slate-400">Cross-bidder queries, grounded in live compliance data</p>
        </div>
      </div>

      <div className="space-y-3 max-h-72 overflow-y-auto pr-1">
        {turns.length === 0 && (
          <p className="text-xs text-slate-500">
            Try: &quot;compare bidders by risk&quot; or &quot;which bidders have pending GST returns&quot;
          </p>
        )}
        {turns.map((turn, i) => (
          <div key={i} className="space-y-2">
            <div className="flex justify-end">
              <div className="bg-blue-600 text-white text-xs rounded-xl rounded-br-sm px-3 py-2 max-w-[85%]">
                {turn.query}
              </div>
            </div>
            <div className="flex justify-start">
              <div className="bg-slate-950/60 border border-slate-800/80 text-slate-200 text-xs rounded-xl rounded-bl-sm px-3 py-2 max-w-[85%] whitespace-pre-line">
                {turn.response.reply}
                {turn.response.suggested_actions.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-slate-800 flex flex-wrap gap-1.5">
                    {turn.response.suggested_actions.map((action, j) => (
                      <span key={j} className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-slate-800 text-slate-300 border border-slate-700">
                        {action}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {error && <p className="text-xs text-rose-400">{error}</p>}

      <div className="flex items-center space-x-2 pt-2 border-t border-slate-800">
        <input
          type="text"
          value={input}
          onChange={(e) => { setInput(e.target.value); if (error) setError(null); }}
          onKeyDown={(e) => { if (e.key === 'Enter') handleSend(); }}
          placeholder="Ask across bidders in this tender..."
          className="flex-1 bg-slate-950/60 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500/60"
        />
        <button
          onClick={handleSend}
          disabled={isSending}
          className="p-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white rounded-xl transition"
          aria-label="Send"
        >
          {isSending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
        </button>
      </div>
    </div>
  );
};
