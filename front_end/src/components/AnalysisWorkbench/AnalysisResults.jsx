import React, { useState } from 'react';
import { Network, BarChart3, Cpu, Code, RefreshCw, Search, Info, LayoutTemplate } from 'lucide-react';
import GraphVisualizer from './GraphVisualizer';

const AnalysisResults = ({ results }) => {
  const [showDetails, setShowDetails] = useState(false);
  const [viewMode, setViewMode] = useState('graph'); // 'graph' or 'json'

  const renderResults = () => {
    if (!results.data) return null;

    if (results.data.hits || Array.isArray(results.data)) {
      return (
        <div className="space-y-4">
          <h3 className="font-bold text-gray-700 flex items-center gap-2">
            <Search className="w-4 h-4" />
            Search Results
          </h3>
          <div className="bg-gray-900 rounded-2xl p-6 text-blue-300 font-mono text-sm overflow-auto max-h-96">
            <pre className="whitespace-pre-wrap">
              {JSON.stringify(results.data, null, 2)}
            </pre>
          </div>
        </div>
      );
    }

    if (results.data.nodes || results.data.degree_centrality || results.data.community_edges) {
      return (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-gray-700 flex items-center gap-2">
              <Network className="w-4 h-4 text-purple-600" />
              Network Analysis Results
            </h3>
            {results.data.nodes && (
              <div className="flex bg-gray-100 p-1 rounded-xl border border-gray-200">
                <button
                  onClick={() => setViewMode('graph')}
                  className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${viewMode === 'graph' ? 'bg-white shadow-md text-purple-600' : 'text-gray-500 hover:text-gray-700'}`}
                >
                  Graph Visualization
                </button>
                <button
                  onClick={() => setViewMode('json')}
                  className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${viewMode === 'json' ? 'bg-white shadow-md text-purple-600' : 'text-gray-500 hover:text-gray-700'}`}
                >
                  Raw Data
                </button>
              </div>
            )}
          </div>

          {viewMode === 'graph' && results.data.nodes ? (
            <GraphVisualizer data={results.data} />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {results.data.degree_centrality && (
                <div className="bg-purple-50 p-4 rounded-xl">
                  <h4 className="font-semibold text-purple-800 mb-2">Degree Centrality</h4>
                  <div className="text-sm text-purple-700 font-mono">
                    {JSON.stringify(results.data.degree_centrality.slice(0, 5), null, 2)}
                  </div>
                </div>
              )}
              {results.data.community_edges && (
                <div className="bg-blue-50 p-4 rounded-xl">
                  <h4 className="font-semibold text-blue-800 mb-2">Community Detection</h4>
                  <div className="text-sm text-blue-700 font-mono">
                    {JSON.stringify(results.data.community_edges.slice(0, 5), null, 2)}
                  </div>
                </div>
              )}
              {(!results.data.degree_centrality && !results.data.community_edges) && (
                <div className="col-span-2 bg-gray-900 rounded-2xl p-6 text-blue-300 font-mono text-sm overflow-auto max-h-96">
                  <pre className="whitespace-pre-wrap">
                    {JSON.stringify(results.data, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          )}
        </div>
      );
    }

    if (results.data.patent_id) {
      return (
        <div className="space-y-4">
          <h3 className="font-bold text-gray-700 flex items-center gap-2">
            <Cpu className="w-4 h-4" />
            Technology Mapping Result
          </h3>
          <div className="bg-green-50 p-6 rounded-xl border border-green-200">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="font-medium text-green-800">Patent ID:</span>
                <span className="ml-2 text-green-700">{results.data.patent_id}</span>
              </div>
              <div>
                <span className="font-medium text-green-800">Technology ID:</span>
                <span className="ml-2 text-green-700">{results.data.technology_id}</span>
              </div>
              <div>
                <span className="font-medium text-green-800">Confidence:</span>
                <span className="ml-2 text-green-700">{(results.data.confidence * 100).toFixed(1)}%</span>
              </div>
              <div>
                <span className="font-medium text-green-800">Method:</span>
                <span className="ml-2 text-green-700">{results.data.method}</span>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className="bg-gray-900 rounded-2xl p-6 text-blue-300 font-mono text-sm overflow-auto max-h-96">
        <pre className="whitespace-pre-wrap">
          {JSON.stringify(results.data, null, 2)}
        </pre>
      </div>
    );
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between bg-white p-4 rounded-2xl border border-gray-100 shadow-sm">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">
              Analysis Confidence:
            </span>
            <span className={`px-3 py-1 rounded-full text-xs font-bold border ${results.confidence === 'High' ? 'bg-green-50 text-green-700 border-green-100' :
              results.confidence === 'Medium' ? 'bg-yellow-50 text-yellow-700 border-yellow-100' :
                'bg-gray-50 text-gray-600 border-gray-200'
              }`}>
              {results.confidence || 'General'}
            </span>
          </div>
          {results.interpretation_note && (
            <div className="flex items-center gap-2 text-xs text-purple-600 font-medium bg-purple-50 px-3 py-1 rounded-full border border-purple-100">
              <Info className="w-3.5 h-3.5" />
              {results.interpretation_note}
            </div>
          )}
        </div>
        <div className="text-xs text-gray-400 font-medium whitespace-nowrap">
          Source: {results.source || 'MCP Server'}
        </div>
      </div>

      <div className="bg-white rounded-3xl border border-gray-100 shadow-sm overflow-hidden">
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="w-full flex items-center justify-between p-6 bg-purple-50/30 hover:bg-purple-50 transition-colors border-b border-gray-50"
        >
          <div className="flex items-center gap-3">
            <Code className="w-5 h-5 text-purple-600" />
            <span className="font-bold text-gray-800">Analysis Results</span>
          </div>
          {showDetails ? <RefreshCw className="w-5 h-5 text-gray-400" /> : <BarChart3 className="w-5 h-5 text-gray-400" />}
        </button>

        {showDetails && (
          <div className="p-6 animate-in slide-in-from-top-2 duration-300">
            {renderResults()}
          </div>
        )}
      </div>
    </div>
  );
};

export default AnalysisResults;