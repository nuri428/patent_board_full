import React, { useState } from 'react';
import {
  Search,
  Network,
  Cpu,
  BarChart3,
  Loader2,
  AlertTriangle,
  Info,
  RefreshCw
} from 'lucide-react';
import api from '../api/axios';
import SemanticSearchTab from '../components/AnalysisWorkbench/SemanticSearchTab';
import NetworkAnalysisTab from '../components/AnalysisWorkbench/NetworkAnalysisTab';
import TechMappingTab from '../components/AnalysisWorkbench/TechMappingTab';
import AnalysisResults from '../components/AnalysisWorkbench/AnalysisResults';

const AnalysisWorkbench = () => {
  const [activeTab, setActiveTab] = useState('semantic');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const handleAnalysis = async (type, params) => {
    setLoading(true);
    setError(null);

    // 분석 타입별 전용 엔드포인트 매핑
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
      setError(err.response?.data?.detail || "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <header className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-600 to-blue-600">
          AI Analysis Workbench
        </h1>
        <p className="text-gray-500">
          Advanced patent analysis powered by MCP server capabilities
        </p>
      </header>

      <div className="flex bg-gray-100 p-1 rounded-xl w-fit border border-gray-200">
        {[
          { id: 'semantic', label: 'Semantic Search', icon: Search },
          { id: 'network', label: 'Network Analysis', icon: Network },
          { id: 'tech', label: 'Tech Mapping', icon: Cpu },
          { id: 'charts', label: 'Data Charts', icon: BarChart3 }
        ].map(tab => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === tab.id
                ? 'bg-white shadow-sm text-purple-600'
                : 'text-gray-500 hover:text-gray-700'
                }`}
              onClick={() => setActiveTab(tab.id)}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      <div className="bg-white p-8 rounded-3xl shadow-sm border border-gray-100">
        {activeTab === 'semantic' && (
          <SemanticSearchTab
            onSearch={handleAnalysis}
            loading={loading}
          />
        )}
        {activeTab === 'network' && (
          <NetworkAnalysisTab
            onAnalyze={handleAnalysis}
            loading={loading}
          />
        )}
        {activeTab === 'tech' && (
          <TechMappingTab
            onMapping={handleAnalysis}
            loading={loading}
          />
        )}
        {activeTab === 'charts' && (
          <div className="text-center py-12">
            <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">Data visualization charts coming soon</p>
          </div>
        )}
      </div>

      {results && (
        <AnalysisResults results={results} />
      )}

      {error && (
        <div className="p-4 bg-red-50 text-red-700 rounded-2xl border border-red-200">
          <AlertTriangle className="w-5 h-5 inline mr-2" />
          {error}
        </div>
      )}
    </div>
  );
};

export default AnalysisWorkbench;