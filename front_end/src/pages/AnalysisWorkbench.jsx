import React, { useState } from 'react';
import {
  Search,
  Network,
  Cpu,
  BarChart3,
  Loader2,
  AlertTriangle,
  Info,
  RefreshCw,
  Sparkles
} from 'lucide-react';
import api from '../api/axios';
import SemanticSearchTab from '../components/AnalysisWorkbench/SemanticSearchTab';
import NetworkAnalysisTab from '../components/AnalysisWorkbench/NetworkAnalysisTab';
import TechMappingTab from '../components/AnalysisWorkbench/TechMappingTab';
import AnalysisResults from '../components/AnalysisWorkbench/AnalysisResults';
import { motion, AnimatePresence } from 'framer-motion';

const AnalysisWorkbench = () => {
  const [activeTab, setActiveTab] = useState('semantic');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const handleAnalysis = async (type, params) => {
    setLoading(true);
    setError(null);

    let endpoint = 'mcp/proxy';
    let data = {
      tool_name: `${type}_analysis_tool_name`,
      arguments: params
    };

    if (type === 'semantic') {
      endpoint = 'mcp/proxy/semantic-search';
      data = params;
    } else if (type === 'network') {
      endpoint = 'mcp/proxy/network-analysis';
      data = params;
    } else if (type === 'tech') {
      endpoint = 'mcp/proxy/technology-mapping';
      data = params;
    }

    try {
      const response = await api.post(endpoint, data);
      setResults(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || "An error occurred during analysis pulse.");
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'semantic', label: 'Semantic Search', icon: Search, color: 'text-indigo-600', bg: 'bg-indigo-50' },
    { id: 'network', label: 'Network Matrix', icon: Network, color: 'text-emerald-600', bg: 'bg-emerald-50' },
    { id: 'tech', label: 'Tech Mapping', icon: Cpu, color: 'text-purple-600', bg: 'bg-purple-50' },
    { id: 'charts', label: 'Visual Analytics', icon: BarChart3, color: 'text-amber-600', bg: 'bg-amber-50' }
  ];

  return (
    <div className="max-w-7xl mx-auto space-y-10 p-4 pb-20">
      <header className="flex flex-col md:row justify-between items-start md:items-center gap-6">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-indigo-600" />
            <span className="text-xs font-bold uppercase tracking-widest text-indigo-600/80">Expert Workspace</span>
          </div>
          <h1 className="text-4xl font-black text-slate-900 tracking-tight">
            Analysis Workbench
          </h1>
          <p className="text-slate-500 font-medium max-w-2xl">
            Execute deep-dive patent investigations using multi-vector semantic models and citation graph analysis.
          </p>
        </div>
        <button
          onClick={() => { setResults(null); setError(null); }}
          className="flex items-center gap-2 px-4 py-2 text-sm font-bold text-slate-500 hover:text-indigo-600 transition-colors border border-slate-200 rounded-xl bg-white"
        >
          <RefreshCw className="w-4 h-4" /> Reset Workspace
        </button>
      </header>

      {/* Tab Navigation */}
      <nav className="flex p-1.5 bg-slate-100 rounded-2xl w-full md:w-fit border border-slate-200/60 shadow-inner overflow-x-auto no-scrollbar">
        {tabs.map(tab => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              className={`relative flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-bold transition-all whitespace-nowrap ${isActive ? 'text-slate-950 translate-y-0 shadow-sm' : 'text-slate-500 hover:text-slate-700'
                }`}
              onClick={() => setActiveTab(tab.id)}
            >
              {isActive && (
                <motion.div
                  layoutId="activeTab"
                  className="absolute inset-0 bg-white rounded-xl -z-10"
                  transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                />
              )}
              <Icon className={`w-4 h-4 ${isActive ? tab.color : ''}`} />
              {tab.label}
            </button>
          );
        })}
      </nav>

      <main className="grid grid-cols-1 xl:grid-cols-12 gap-10">
        {/* Input Panel */}
        <div className="xl:col-span-4">
          <section className="premium-card p-8 sticky top-24">
            <h2 className="text-lg font-bold text-slate-900 mb-6 flex items-center gap-2">
              Configuration
            </h2>
            <div className="space-y-6">
              <AnimatePresence mode="wait">
                <motion.div
                  key={activeTab}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 10 }}
                  transition={{ duration: 0.2 }}
                >
                  {activeTab === 'semantic' && (
                    <SemanticSearchTab onSearch={handleAnalysis} loading={loading} />
                  )}
                  {activeTab === 'network' && (
                    <NetworkAnalysisTab onAnalyze={handleAnalysis} loading={loading} />
                  )}
                  {activeTab === 'tech' && (
                    <TechMappingTab onMapping={handleAnalysis} loading={loading} />
                  )}
                  {activeTab === 'charts' && (
                    <div className="text-center py-10 space-y-4">
                      <div className="w-16 h-16 bg-amber-50 rounded-full flex items-center justify-center mx-auto text-amber-600">
                        <BarChart3 className="w-8 h-8" />
                      </div>
                      <p className="text-slate-500 text-sm font-medium">Visualization layer is currently initializing.</p>
                    </div>
                  )}
                </motion.div>
              </AnimatePresence>
            </div>
          </section>
        </div>

        {/* Results Panel */}
        <div className="xl:col-span-8">
          <AnimatePresence mode="wait">
            {loading ? (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex flex-col items-center justify-center p-20 bg-slate-50 rounded-3xl border border-dashed border-slate-300"
              >
                <div className="relative">
                  <Loader2 className="w-12 h-12 text-indigo-600 animate-spin" />
                  <div className="absolute inset-0 blur-xl bg-indigo-500/10 animate-pulse"></div>
                </div>
                <p className="mt-6 text-slate-900 font-bold">Scanning Global Databases...</p>
                <p className="text-slate-500 text-sm mt-1">AI Agents are verifying claims and metadata.</p>
              </motion.div>
            ) : results ? (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-6"
              >
                <AnalysisResults results={results} />
              </motion.div>
            ) : error ? (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="p-8 bg-rose-50 rounded-3xl border border-rose-100 flex items-start gap-4"
              >
                <div className="p-3 bg-rose-100 rounded-xl text-rose-600">
                  <AlertTriangle className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-rose-900 font-bold mb-1">Analysis Interrupted</h3>
                  <p className="text-rose-700 text-sm">{error}</p>
                </div>
              </motion.div>
            ) : (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex flex-col items-center justify-center p-20 bg-white rounded-3xl border border-slate-200 border-dashed"
              >
                <div className="p-6 bg-slate-50 rounded-full mb-6">
                  <Info className="w-10 h-10 text-slate-300" />
                </div>
                <h3 className="text-slate-900 font-bold text-lg mb-2">Ready for Investigation</h3>
                <p className="text-slate-500 text-center max-w-sm">
                  Configure your analysis parameters on the left to begin searching our high-fidelity patent cluster.
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
};

export default AnalysisWorkbench;

export default AnalysisWorkbench;