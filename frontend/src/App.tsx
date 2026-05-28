import React, { useState } from 'react';
import axios from 'axios';
import { Terminal, Database, RefreshCcw, CheckCircle, AlertTriangle, Send, Loader2, Table2, Clock, Activity } from 'lucide-react';

interface AgentResponse {
  user_query: string;
  generated_sql: string;
  execution_error: string;
  retry_count: number;
  results: any[];
  columns: string[];
  execution_time_ms: number;
  telemetry: string[];
}

function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<AgentResponse[]>([]);
  const [currentStep, setCurrentStep] = useState<string | null>(null);

  const handleExecute = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setCurrentStep('Initializing Autonomous Agent...');

    try {
      const response = await axios.post('http://localhost:8000/api/query', {
        user_query: query
      });

      setHistory([response.data, ...history]);
      setQuery('');
      setCurrentStep(null);
    } catch (error) {
      console.error('Error executing query:', error);
      setCurrentStep('Critical Failure: Network or Agent error.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-gray-100 font-mono flex flex-col md:flex-row">

      {/* Sidebar: Database Schema */}
      <aside className="w-full md:w-64 bg-[#111] border-r border-gray-800 flex-shrink-0">
        <div className="p-4 border-b border-gray-800">
          <div className="flex items-center gap-2 text-blue-500">
            <Database size={20} />
            <h2 className="text-sm font-bold uppercase tracking-wider">System Schema</h2>
          </div>
        </div>
        <div className="p-4">
          <div className="mb-4">
            <h3 className="text-xs font-bold text-gray-400 mb-2 flex items-center gap-2">
              <Table2 size={14}/> TABLE: users
            </h3>
            <ul className="space-y-1">
              {[
                { name: 'id', type: 'SERIAL (PK)' },
                { name: 'name', type: 'VARCHAR' },
                { name: 'email', type: 'VARCHAR (UNIQ)' },
                { name: 'role', type: 'VARCHAR' },
                { name: 'department', type: 'VARCHAR' },
                { name: 'account_status', type: 'VARCHAR' },
                { name: 'signup_date', type: 'DATE' },
                { name: 'last_login', type: 'TIMESTAMP' }
              ].map(col => (
                <li key={col.name} className="flex justify-between items-center text-[10px] bg-[#161616] px-2 py-1 rounded">
                  <span className="text-blue-400">{col.name}</span>
                  <span className="text-gray-600">{col.type}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 p-4 md:p-8 h-screen overflow-y-auto">
        <header className="max-w-4xl mx-auto mb-8 flex items-center justify-between border-b border-gray-800 pb-4">
          <div>
            <h1 className="text-xl font-bold tracking-tight">Neuro-Symbolic DB Operator</h1>
            <p className="text-xs text-gray-500 uppercase tracking-widest">Self-Healing Autonomous System</p>
          </div>
          <div className="flex items-center gap-2 text-xs text-green-500 bg-green-500/10 px-3 py-1 rounded-full border border-green-500/20">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            SYSTEM ONLINE
          </div>
        </header>

        <main className="max-w-4xl mx-auto">
          {/* Input Area */}
          <form onSubmit={handleExecute} className="mb-4">
            <div className="relative group">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <Terminal size={20} className="text-gray-500" />
              </div>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Enter natural language request..."
                className="block w-full bg-[#111] border border-gray-800 rounded-lg py-4 pl-12 pr-12 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all text-gray-200"
                disabled={loading}
              />
              <button
                type="submit"
                disabled={loading || !query.trim()}
                className="absolute inset-y-0 right-0 pr-4 flex items-center text-blue-500 hover:text-blue-400 disabled:text-gray-600 transition-colors"
              >
                {loading ? <Loader2 className="animate-spin" size={24} /> : <Send size={24} />}
              </button>
            </div>
            {currentStep && (
              <p className="mt-2 text-xs text-blue-400 animate-pulse flex items-center gap-2">
                <RefreshCcw size={12} className="animate-spin" /> {currentStep}
              </p>
            )}
          </form>

          {/* Quick Examples */}
          <div className="mb-8 flex flex-wrap gap-2 items-center">
            <span className="text-[10px] uppercase tracking-widest text-gray-600 mr-1">Quick Tests:</span>
            {[
              "Names and emails of users who signed up yesterday",
              "Count active users per department",
              "Newest employee in 'AI Systems' division"
            ].map((example, i) => (
              <button
                key={i}
                type="button"
                onClick={() => setQuery(example)}
                className="text-[10px] bg-[#161616] border border-gray-800 text-gray-400 hover:bg-gray-800 hover:text-blue-400 rounded px-2 py-1 transition-all text-left truncate max-w-[200px] md:max-w-none"
                title={example}
              >
                {example}
              </button>
            ))}
          </div>

          {/* Console / History */}
          <div className="space-y-6">
            {history.length === 0 && !loading && (
              <div className="text-center py-20 border border-dashed border-gray-800 rounded-xl">
                <p className="text-gray-600">No operations executed. Awaiting command signals...</p>
              </div>
            )}

            {history.map((item, index) => (
              <div key={index} className="bg-[#111] border border-gray-800 rounded-lg overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-500">
                {/* Card Header */}
                <div className="px-4 py-3 bg-[#161616] border-b border-gray-800 flex flex-col md:flex-row md:items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-500">ID: {(history.length - index).toString().padStart(3, '0')}</span>
                    <span className="text-xs font-bold text-gray-300 px-2 py-0.5 bg-gray-800 rounded">LOGIC_EXEC</span>
                    {item.execution_time_ms > 0 && (
                      <span className="text-[10px] text-gray-500 flex items-center gap-1">
                        <Clock size={10} /> {item.execution_time_ms}ms
                      </span>
                    )}
                  </div>
                  {item.execution_error ? (
                    <span className="text-[10px] text-red-400 flex items-center gap-1">
                      <AlertTriangle size={12} /> FAILED AFTER {item.retry_count} RETRIES
                    </span>
                  ) : (
                    <span className="text-[10px] text-green-400 flex items-center gap-1">
                      <CheckCircle size={12} /> SUCCESSFUL EXECUTION
                    </span>
                  )}
                </div>

                {/* Card Content */}
                <div className="p-4 space-y-6">

                  {/* Row 1: Request & Telemetry */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h3 className="text-[10px] uppercase text-gray-500 mb-2 tracking-widest">Original Request</h3>
                      <p className="text-sm text-gray-200 mb-4">{item.user_query}</p>

                      <h3 className="text-[10px] uppercase text-gray-500 mb-2 tracking-widest">Generated Artifact (SQL)</h3>
                      <div className="bg-black p-3 rounded border border-gray-800 text-blue-400 text-xs overflow-x-auto">
                        <code>{item.generated_sql || 'No SQL Generated'}</code>
                      </div>
                    </div>

                    {/* Telemetry Timeline */}
                    <div>
                      <h3 className="text-[10px] uppercase text-gray-500 mb-2 tracking-widest flex items-center gap-1"><Activity size={12}/> Agent Telemetry</h3>
                      <div className="space-y-2 border-l border-gray-800 pl-3 ml-2">
                        {item.telemetry?.map((log, i) => (
                          <div key={i} className="relative">
                            <div className={`absolute -left-[17px] top-1.5 w-2 h-2 rounded-full ${log.includes('[FAIL]') ? 'bg-red-500' : log.includes('[WARN]') ? 'bg-yellow-500' : 'bg-green-500'}`}></div>
                            <p className={`text-[10px] ${log.includes('[FAIL]') ? 'text-red-400' : log.includes('[WARN]') ? 'text-yellow-400' : 'text-gray-400'}`}>
                              {log}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Row 2: Results / Errors */}
                  {item.execution_error && (
                    <div className="bg-red-900/10 border border-red-500/20 p-3 rounded">
                      <h3 className="text-[10px] uppercase text-red-500 mb-1 tracking-widest">Final Traceback</h3>
                      <p className="text-xs text-red-400 italic">{item.execution_error}</p>
                    </div>
                  )}

                  {!item.execution_error && item.columns && item.columns.length > 0 && (
                    <div>
                      <h3 className="text-[10px] uppercase text-gray-500 mb-2 tracking-widest flex items-center gap-1"><Table2 size={12}/> Data Output ({item.results?.length || 0} rows)</h3>
                      <div className="overflow-x-auto rounded border border-gray-800">
                        <table className="w-full text-left text-xs">
                          <thead className="bg-[#161616] text-gray-400 uppercase tracking-wider">
                            <tr>
                              {item.columns.map((col, i) => (
                                <th key={i} className="px-4 py-2 border-b border-gray-800 font-medium">{col}</th>
                              ))}
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-gray-800/50 bg-[#0a0a0a]">
                            {item.results?.map((row, rowIndex) => (
                              <tr key={rowIndex} className="hover:bg-gray-900/50 transition-colors">
                                {row.map((cell: any, cellIndex: number) => (
                                  <td key={cellIndex} className="px-4 py-2 whitespace-nowrap text-gray-300">
                                    {cell !== null ? String(cell) : <span className="text-gray-600 italic">null</span>}
                                  </td>
                                ))}
                              </tr>
                            ))}
                            {(!item.results || item.results.length === 0) && (
                              <tr>
                                <td colSpan={item.columns.length} className="px-4 py-4 text-center text-gray-600 italic">No rows matched the query.</td>
                              </tr>
                            )}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}

                  <div className="flex items-center gap-4 pt-2 border-t border-gray-800">
                    <div className="flex items-center gap-1">
                      <RefreshCcw size={12} className="text-gray-500" />
                      <span className="text-[10px] text-gray-500 uppercase">Total Retries: {item.retry_count}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;

