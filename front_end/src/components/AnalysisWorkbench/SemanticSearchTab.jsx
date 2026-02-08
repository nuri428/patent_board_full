import React, { useState } from 'react';
import { Search, Loader2 } from 'lucide-react';

const SemanticSearchTab = ({ onSearch, loading }) => {
  const [query, setQuery] = useState('');
  const [limit, setLimit] = useState(10);
  const [threshold, setThreshold] = useState(0.7);

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    onSearch('semantic', {
      query: query.trim(),
      limit,
      similarity_threshold: threshold
    });
  };

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <div className="text-center">
        <h2 className="text-xl font-bold text-gray-800 mb-2">Semantic Patent Search</h2>
        <p className="text-gray-500 text-sm mb-6">
          Find patents using AI-powered semantic similarity search
        </p>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Search Query
          </label>
          <textarea
            className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:border-purple-500 focus:ring-4 focus:ring-purple-50 outline-none transition-all"
            placeholder="Enter your search query (e.g., 'machine learning algorithms for medical imaging')"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            rows={3}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Results Limit
            </label>
            <select
              className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:border-purple-500 outline-none transition-all"
              value={limit}
              onChange={(e) => setLimit(parseInt(e.target.value))}
            >
              {[5, 10, 20, 30, 50].map(num => (
                <option key={num} value={num}>{num}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Similarity Threshold
            </label>
            <input
              type="range"
              min="0.0"
              max="1.0"
              step="0.1"
              value={threshold}
              onChange={(e) => setThreshold(parseFloat(e.target.value))}
              className="w-full"
            />
            <div className="text-center text-sm text-gray-600 mt-1">
              {threshold.toFixed(1)}
            </div>
          </div>
        </div>

        <button
          onClick={handleSearch}
          disabled={loading || !query.trim()}
          className="w-full px-6 py-3 bg-purple-600 text-white rounded-xl hover:bg-purple-700 shadow-lg shadow-purple-200 flex items-center justify-center gap-2 disabled:opacity-50 transition-all"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Searching...
            </>
          ) : (
            <>
              <Search className="w-4 h-4" />
              Search Patents
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default SemanticSearchTab;