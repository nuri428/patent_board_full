import React, { useState } from 'react';
import { Network, Loader2 } from 'lucide-react';

const NetworkAnalysisTab = ({ onAnalyze, loading }) => {
  const [nodeTypes, setNodeTypes] = useState(['Corporation', 'Technology', 'Patent']);
  const [includeCentrality, setIncludeCentrality] = useState(true);
  const [includeCommunities, setIncludeCommunities] = useState(true);
  const [includeLinkPrediction, setIncludeLinkPrediction] = useState(true);

  const handleAnalyze = async () => {
    onAnalyze('network', {
      node_types: nodeTypes,
      include_centrality: includeCentrality,
      include_communities: includeCommunities,
      include_link_prediction: includeLinkPrediction
    });
  };

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <div className="text-center">
        <h2 className="text-xl font-bold text-gray-800 mb-2">Network Analysis</h2>
        <p className="text-gray-500 text-sm mb-6">
          Analyze patent relationships and network structure using Neo4j GDS
        </p>
      </div>

      <div className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Node Types to Analyze
          </label>
          <div className="space-y-2">
            {['Corporation', 'Technology', 'Patent'].map(type => (
              <label key={type} className="flex items-center">
                <input
                  type="checkbox"
                  checked={nodeTypes.includes(type)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setNodeTypes([...nodeTypes, type]);
                    } else {
                      setNodeTypes(nodeTypes.filter(t => t !== type));
                    }
                  }}
                  className="mr-3 text-purple-600 rounded focus:ring-purple-500"
                />
                <span className="text-gray-700">{type}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="space-y-4">
          <h3 className="text-sm font-medium text-gray-700">Analysis Options</h3>
          <div className="space-y-3">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={includeCentrality}
                onChange={(e) => setIncludeCentrality(e.target.checked)}
                className="mr-3 text-purple-600 rounded focus:ring-purple-500"
              />
              <span className="text-gray-700">Include Centrality Metrics</span>
            </label>

            <label className="flex items-center">
              <input
                type="checkbox"
                checked={includeCommunities}
                onChange={(e) => setIncludeCommunities(e.target.checked)}
                className="mr-3 text-purple-600 rounded focus:ring-purple-500"
              />
              <span className="text-gray-700">Include Community Detection</span>
            </label>

            <label className="flex items-center">
              <input
                type="checkbox"
                checked={includeLinkPrediction}
                onChange={(e) => setIncludeLinkPrediction(e.target.checked)}
                className="mr-3 text-purple-600 rounded focus:ring-purple-500"
              />
              <span className="text-gray-700">Include Link Prediction</span>
            </label>
          </div>
        </div>

        <button
          onClick={handleAnalyze}
          disabled={loading || nodeTypes.length === 0}
          className="w-full px-6 py-3 bg-purple-600 text-white rounded-xl hover:bg-purple-700 shadow-lg shadow-purple-200 flex items-center justify-center gap-2 disabled:opacity-50 transition-all"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Analyzing...
            </>
          ) : (
            <>
              <Network className="w-4 h-4" />
              Run Network Analysis
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default NetworkAnalysisTab;