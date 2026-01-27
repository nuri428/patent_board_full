import React, { useState } from 'react';
import { Cpu, Loader2 } from 'lucide-react';

const TechMappingTab = ({ onMapping, loading }) => {
  const [patentId, setPatentId] = useState('');
  const [technologyId, setTechnologyId] = useState('');
  const [confidence, setConfidence] = useState(0.8);
  const [method, setMethod] = useState('SEMANTIC_MAPPING');
  const [analysisRunId, setAnalysisRunId] = useState('');

  const handleMapping = async () => {
    if (!patentId || !technologyId || !analysisRunId) return;
    
    onMapping('tech', {
      patent_id: patentId,
      technology_id: technologyId,
      confidence,
      method,
      analysis_run_id: analysisRunId
    });
  };

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <div className="text-center">
        <h2 className="text-xl font-bold text-gray-800 mb-2">Technology Mapping</h2>
        <p className="text-gray-500 text-sm mb-6">
          Create technology mappings for patents with confidence scoring
        </p>
      </div>

      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Patent ID
            </label>
            <input
              type="text"
              className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:border-purple-500 focus:ring-4 focus:ring-purple-50 outline-none transition-all"
              placeholder="e.g., KR1020230001234"
              value={patentId}
              onChange={(e) => setPatentId(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Technology ID
            </label>
            <input
              type="text"
              className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:border-purple-500 focus:ring-4 focus:ring-purple-50 outline-none transition-all"
              placeholder="e.g., TECH_AI_001"
              value={technologyId}
              onChange={(e) => setTechnologyId(e.target.value)}
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Confidence Score
            </label>
            <input
              type="number"
              min="0.0"
              max="1.0"
              step="0.1"
              value={confidence}
              onChange={(e) => setConfidence(parseFloat(e.target.value))}
              className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:border-purple-500 outline-none transition-all"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Mapping Method
            </label>
            <select
              className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:border-purple-500 outline-none transition-all"
              value={method}
              onChange={(e) => setMethod(e.target.value)}
            >
              <option value="SEMANTIC_MAPPING">Semantic Mapping</option>
              <option value="IPC_MAPPING">IPC Classification</option>
              <option value="KEYWORD_MATCHING">Keyword Matching</option>
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Analysis Run ID
          </label>
          <input
            type="text"
            className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:border-purple-500 focus:ring-4 focus:ring-purple-50 outline-none transition-all"
            placeholder="e.g., analysis-run-12345"
            value={analysisRunId}
            onChange={(e) => setAnalysisRunId(e.target.value)}
          />
        </div>

        <button
          onClick={handleMapping}
          disabled={loading || !patentId || !technologyId || !analysisRunId}
          className="w-full px-6 py-3 bg-purple-600 text-white rounded-xl hover:bg-purple-700 shadow-lg shadow-purple-200 flex items-center justify-center gap-2 disabled:opacity-50 transition-all"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Creating Mapping...
            </>
          ) : (
            <>
              <Cpu className="w-4 h-4" />
              Create Technology Mapping
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default TechMappingTab;