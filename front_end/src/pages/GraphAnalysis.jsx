import React, { useState } from 'react';
import { graphAPI } from '../api/mcp';

const GraphAnalysis = () => {
    const [activeTab, setActiveTab] = useState('competitor');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    // Form States
    const [companyName, setCompanyName] = useState('');
    const [problemKeyword, setProblemKeyword] = useState('');
    const [techKeyword, setTechKeyword] = useState('');
    const [pathStart, setPathStart] = useState('');
    const [pathEnd, setPathEnd] = useState('');

    const handleSearch = async (type) => {
        setLoading(true);
        setError(null);
        setResult(null);
        try {
            let data;
            switch (type) {
                case 'competitor':
                    data = await graphAPI.getCompetitors(companyName);
                    break;
                case 'problem':
                    data = await graphAPI.searchByProblem(problemKeyword);
                    break;
                case 'cluster':
                    data = await graphAPI.getTechCluster(techKeyword);
                    break;
                case 'path':
                    data = await graphAPI.findPath(pathStart, pathEnd);
                    break;
            }
            setResult(data);
        } catch (err) {
            setError(err.response?.data?.detail || "An error occurred");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="p-6">
            <h1 className="text-2xl font-bold mb-6">Graph Analysis (Neo4j)</h1>

            {/* Tabs */}
            <div className="flex border-b border-gray-200 mb-6">
                {[
                    { id: 'competitor', label: 'Competitor Analysis' },
                    { id: 'problem', label: 'Problem Search' },
                    { id: 'cluster', label: 'Tech Cluster' },
                    { id: 'path', label: 'Path Finder' }
                ].map(tab => (
                    <button
                        key={tab.id}
                        className={`px-4 py-2 border-b-2 font-medium text-sm transition-colors ${activeTab === tab.id
                                ? 'border-blue-600 text-blue-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }`}
                        onClick={() => { setActiveTab(tab.id); setResult(null); setError(null); }}
                    >
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* Content Areas */}
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">

                {/* Competitor Analysis Tab */}
                {activeTab === 'competitor' && (
                    <div className="space-y-4">
                        <p className="text-gray-600">Analyze direct competitors based on graph relationships.</p>
                        <div className="flex gap-2">
                            <input
                                type="text"
                                className="flex-1 p-2 border border-gray-300 rounded"
                                placeholder="Enter Company Name (e.g., Samsung)"
                                value={companyName}
                                onChange={(e) => setCompanyName(e.target.value)}
                            />
                            <button
                                onClick={() => handleSearch('competitor')}
                                disabled={loading}
                                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                            >
                                {loading ? 'Analyzing...' : 'Analyze'}
                            </button>
                        </div>
                    </div>
                )}

                {/* Problem Search Tab */}
                {activeTab === 'problem' && (
                    <div className="space-y-4">
                        <p className="text-gray-600">Find technology solving specific problems (Semantic Search).</p>
                        <div className="flex gap-2">
                            <input
                                type="text"
                                className="flex-1 p-2 border border-gray-300 rounded"
                                placeholder="Enter Problem Keyword (e.g., data loss)"
                                value={problemKeyword}
                                onChange={(e) => setProblemKeyword(e.target.value)}
                            />
                            <button
                                onClick={() => handleSearch('problem')}
                                disabled={loading}
                                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                            >
                                {loading ? 'Search...' : 'Search'}
                            </button>
                        </div>
                    </div>
                )}

                {/* Tech Cluster Tab */}
                {activeTab === 'cluster' && (
                    <div className="space-y-4">
                        <p className="text-gray-600">Identify major technology clusters.</p>
                        <div className="flex gap-2">
                            <input
                                type="text"
                                className="flex-1 p-2 border border-gray-300 rounded"
                                placeholder="Enter Tech Keyword (e.g., AI, Battery)"
                                value={techKeyword}
                                onChange={(e) => setTechKeyword(e.target.value)}
                            />
                            <button
                                onClick={() => handleSearch('cluster')}
                                disabled={loading}
                                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                            >
                                {loading ? 'Identify...' : 'Identify'}
                            </button>
                        </div>
                    </div>
                )}

                {/* Path Finder Tab */}
                {activeTab === 'path' && (
                    <div className="space-y-4">
                        <p className="text-gray-600">Find the shortest connection path between two entities.</p>
                        <div className="flex gap-2">
                            <input
                                type="text"
                                className="flex-1 p-2 border border-gray-300 rounded"
                                placeholder="Start Entity (e.g., Google)"
                                value={pathStart}
                                onChange={(e) => setPathStart(e.target.value)}
                            />
                            <input
                                type="text"
                                className="flex-1 p-2 border border-gray-300 rounded"
                                placeholder="End Entity (e.g., Microsoft)"
                                value={pathEnd}
                                onChange={(e) => setPathEnd(e.target.value)}
                            />
                            <button
                                onClick={() => handleSearch('path')}
                                disabled={loading}
                                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                            >
                                {loading ? 'Trace...' : 'Trace'}
                            </button>
                        </div>
                    </div>
                )}
            </div>

            {/* Results Display */}
            {(result || error) && (
                <div className="mt-6">
                    {error ? (
                        <div className="p-4 bg-red-50 text-red-700 rounded border border-red-200">
                            <strong>Error:</strong> {error}
                        </div>
                    ) : (
                        <div className="p-4 bg-gray-50 rounded border border-gray-200">
                            <h3 className="font-semibold mb-2 text-gray-700">Analysis Result:</h3>
                            <pre className="whitespace-pre-wrap text-sm text-gray-800 overflow-auto max-h-96">
                                {JSON.stringify(result, null, 2)}
                            </pre>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default GraphAnalysis;
