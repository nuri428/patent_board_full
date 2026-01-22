import React, { useState } from 'react';
import { graphAPI } from '../api/mcp';
import { Network, Search, Cpu, GitMerge, Info, AlertTriangle, ChevronDown, ChevronUp, Loader2 } from 'lucide-react';

const GraphAnalysis = () => {
    const [activeTab, setActiveTab] = useState('competitor');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const [showAISummary, setShowAISummary] = useState(false);

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
        setShowAISummary(false);
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
        <div className="space-y-6">
            <header className="flex flex-col gap-2">
                <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-600 to-blue-600">
                    AI Graph Intelligence Workbench
                </h1>
                <p className="text-gray-500">
                    Explore technology relationships and competitor landscapes via KIPRIS Knowledge Graph.
                </p>
            </header>

            {/* Interpretation Legend - Tiered HUD */}
            <div className="bg-blue-50 border border-blue-100 p-4 rounded-2xl flex items-start gap-3">
                <Info className="w-5 h-5 text-blue-500 mt-0.5" />
                <div className="text-xs text-blue-700 leading-relaxed">
                    <span className="font-bold">Interpretation Rule:</span> Relationships shown represent technical similarity and citation links extracted from KIPRIS raw data.
                    <br />
                    <span className="text-blue-500">Note: Connection paths do not imply direct legal or historical causation. This is a support tool for expert analysis.</span>
                </div>
            </div>

            {/* Tabs */}
            <div className="flex bg-gray-100 p-1 rounded-xl w-fit border border-gray-200">
                {[
                    { id: 'competitor', label: 'Competitor Map', icon: Network },
                    { id: 'problem', label: 'Problem Discovery', icon: Search },
                    { id: 'cluster', label: 'Tech Clustering', icon: Cpu },
                    { id: 'path', label: 'Path Finder', icon: GitMerge }
                ].map(tab => {
                    const Icon = tab.icon;
                    return (
                        <button
                            key={tab.id}
                            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === tab.id
                                ? 'bg-white shadow-sm text-purple-600'
                                : 'text-gray-500 hover:text-gray-700'
                                }`}
                            onClick={() => { setActiveTab(tab.id); setResult(null); setError(null); }}
                        >
                            <Icon className="w-4 h-4" />
                            {tab.label}
                        </button>
                    );
                })}
            </div>

            {/* Content Areas */}
            <div className="bg-white p-8 rounded-3xl shadow-sm border border-gray-100 backdrop-blur-xl bg-opacity-80">
                {activeTab === 'competitor' && (
                    <div className="space-y-4 max-w-2xl text-center mx-auto">
                        <h2 className="text-xl font-bold text-gray-800">Analyze Competitor Landscape</h2>
                        <p className="text-gray-500 text-sm">Identify direct competitors sharing similar technology nodes in the knowledge graph.</p>
                        <div className="flex gap-2">
                            <input
                                type="text"
                                className="flex-1 px-4 py-3 border border-gray-200 rounded-xl focus:border-purple-500 focus:ring-4 focus:ring-purple-50 outline-none transition-all"
                                placeholder="Enter Company Name (e.g., Samsung)"
                                value={companyName}
                                onChange={(e) => setCompanyName(e.target.value)}
                            />
                            <button
                                onClick={() => handleSearch('competitor')}
                                disabled={loading || !companyName}
                                className="px-6 py-3 bg-purple-600 text-white rounded-xl hover:bg-purple-700 shadow-lg shadow-purple-200 flex items-center gap-2 disabled:opacity-50 transition-all"
                            >
                                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Network className="w-4 h-4" />}
                                Map Nodes
                            </button>
                        </div>
                    </div>
                )}

                {activeTab === 'problem' && (
                    <div className="space-y-4 max-w-2xl text-center mx-auto">
                        <h2 className="text-xl font-bold text-gray-800">Semantic Problem Search</h2>
                        <p className="text-gray-500 text-sm">Find patents solving specific technical challenges using graph-based semantic mapping.</p>
                        <div className="flex gap-2">
                            <input
                                type="text"
                                className="flex-1 px-4 py-3 border border-gray-200 rounded-xl focus:border-purple-500 focus:ring-4 focus:ring-purple-50 outline-none transition-all"
                                placeholder="Enter Problem Keyword (e.g., heat dissipation)"
                                value={problemKeyword}
                                onChange={(e) => setProblemKeyword(e.target.value)}
                            />
                            <button
                                onClick={() => handleSearch('problem')}
                                disabled={loading || !problemKeyword}
                                className="px-6 py-3 bg-purple-600 text-white rounded-xl hover:bg-purple-700 shadow-lg shadow-purple-200 flex items-center gap-2 disabled:opacity-50 transition-all"
                            >
                                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
                                Analyze
                            </button>
                        </div>
                    </div>
                )}

                {activeTab === 'cluster' && (
                    <div className="space-y-4 max-w-2xl text-center mx-auto">
                        <h2 className="text-xl font-bold text-gray-800">Technology Clustering</h2>
                        <p className="text-gray-500 text-sm">Cluster patent nodes by shared IPC codes and keyword high-density zones.</p>
                        <div className="flex gap-2">
                            <input
                                type="text"
                                className="flex-1 px-4 py-3 border border-gray-200 rounded-xl focus:border-purple-500 focus:ring-4 focus:ring-purple-50 outline-none transition-all"
                                placeholder="Enter Tech Keyword (e.g., Battery material)"
                                value={techKeyword}
                                onChange={(e) => setTechKeyword(e.target.value)}
                            />
                            <button
                                onClick={() => handleSearch('cluster')}
                                disabled={loading || !techKeyword}
                                className="px-6 py-3 bg-purple-600 text-white rounded-xl hover:bg-purple-700 shadow-lg shadow-purple-200 flex items-center gap-2 disabled:opacity-50 transition-all"
                            >
                                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Cpu className="w-4 h-4" />}
                                Cluster
                            </button>
                        </div>
                    </div>
                )}

                {activeTab === 'path' && (
                    <div className="space-y-4 max-w-2xl text-center mx-auto">
                        <h2 className="text-xl font-bold text-gray-800">Entity Path Finder</h2>
                        <p className="text-gray-500 text-sm">Find the shortest similarity path between two technical entities in the KIPRIS graph.</p>
                        <div className="grid grid-cols-2 gap-2">
                            <input
                                type="text"
                                className="p-3 border border-gray-200 rounded-xl focus:border-purple-500 outline-none transition-all"
                                placeholder="Start Entity (e.g., Apple)"
                                value={pathStart}
                                onChange={(e) => setPathStart(e.target.value)}
                            />
                            <input
                                type="text"
                                className="p-3 border border-gray-200 rounded-xl focus:border-purple-500 outline-none transition-all"
                                placeholder="End Entity (e.g., Tesla)"
                                value={pathEnd}
                                onChange={(e) => setPathEnd(e.target.value)}
                            />
                        </div>
                        <button
                            onClick={() => handleSearch('path')}
                            disabled={loading || !pathStart || !pathEnd}
                            className="w-full mt-2 px-6 py-3 bg-purple-600 text-white rounded-xl hover:bg-purple-700 shadow-lg shadow-purple-200 flex items-center justify-center gap-2 disabled:opacity-50 transition-all"
                        >
                            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <GitMerge className="w-4 h-4" />}
                            Trace Path
                        </button>
                    </div>
                )}
            </div>

            {/* Results Display */}
            {(result || error) && (
                <div className="mt-8 space-y-4">
                    {error ? (
                        <div className="p-4 bg-red-50 text-red-700 rounded-2xl border border-red-200 flex items-center gap-2">
                            <AlertTriangle className="w-5 h-5" />
                            <strong>Error:</strong> {error}
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {/* Confidence & Sampling HUD */}
                            <div className="flex items-center justify-between bg-white p-4 rounded-2xl border border-gray-100 shadow-sm">
                                <div className="flex items-center gap-6">
                                    <div className="flex items-center gap-2">
                                        <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">Analysis Confidence:</span>
                                        <span className={`px-3 py-1 rounded-full text-xs font-bold border ${result.confidence === 'High' ? 'bg-green-50 text-green-700 border-green-100' :
                                                result.confidence === 'Medium' ? 'bg-yellow-50 text-yellow-700 border-yellow-100' :
                                                    'bg-gray-50 text-gray-600 border-gray-200'
                                            }`}>
                                            {result.confidence || 'General'}
                                        </span>
                                    </div>
                                    {result.interpretation_note && (
                                        <div className="flex items-center gap-2 text-xs text-purple-600 font-medium">
                                            <Info className="w-3.5 h-3.5" />
                                            {result.interpretation_note}
                                        </div>
                                    )}
                                </div>
                                <div className="text-xs text-gray-400 font-medium whitespace-nowrap">
                                    Source: {result.source || 'KIPRIS Knowledge Graph'}
                                </div>
                            </div>

                            {/* View Controls */}
                            <div className="bg-white rounded-3xl border border-gray-100 shadow-sm overflow-hidden">
                                <button
                                    onClick={() => setShowAISummary(!showAISummary)}
                                    className="w-full flex items-center justify-between p-6 bg-purple-50/30 hover:bg-purple-50 transition-colors border-b border-gray-50"
                                >
                                    <div className="flex items-center gap-3">
                                        <Cpu className="w-5 h-5 text-purple-600" />
                                        <span className="font-bold text-gray-800">Generate AI Intelligence Summary</span>
                                    </div>
                                    {showAISummary ? <ChevronUp className="w-5 h-5 text-gray-400" /> : <ChevronDown className="w-5 h-5 text-gray-400" />}
                                </button>

                                {showAISummary && (
                                    <div className="p-6 bg-white animate-in slide-in-from-top-2 duration-300">
                                        <div className="p-6 bg-purple-50 rounded-2xl border border-purple-100">
                                            <p className="text-sm text-purple-800 leading-relaxed">
                                                <span className="font-bold block mb-2 underline decoration-purple-300">AI-Generated Interpretation Notice:</span>
                                                The following summary is generated via LLM based on the graph topology and metadata retrieved from KIPRIS.
                                                It is a probabilistic interpretation intended to suggest exploration paths, not to replace formal IP due diligence.
                                            </p>
                                            <hr className="my-4 border-purple-200" />
                                            <div className="space-y-4">
                                                {/* This would ideally be structured data from the proxy's refined results */}
                                                <div className="text-gray-700 text-sm italic">
                                                    [ 분석 환경 구축 중: MCP 결과 기반 심층 판독 데이터가 곧 여기에 표시됩니다. ]
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                )}

                                <div className="p-6">
                                    <h3 className="font-bold mb-4 text-gray-700 flex items-center gap-2">
                                        <Network className="w-4 h-4 text-gray-400" />
                                        Raw Graph Manifest:
                                    </h3>
                                    <div className="bg-gray-900 rounded-2xl p-6 text-blue-300 font-mono text-xs overflow-auto max-h-[500px] scrollbar-thin scrollbar-thumb-gray-700">
                                        <pre className="whitespace-pre-wrap">
                                            {JSON.stringify(result.data, null, 2)}
                                        </pre>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default GraphAnalysis;
