import React, { useState, useMemo } from 'react';
import { graphAPI } from '../api/mcp';
import { Network, Search, Cpu, GitMerge, Info, AlertTriangle, ChevronDown, ChevronUp, Loader2 } from 'lucide-react';
import GraphVisualizer from '../components/AnalysisWorkbench/GraphVisualizer';

// Transform API result data into graph format for visualization
const transformResultToGraph = (data, tabType) => {
    if (!data || !Array.isArray(data) || data.length === 0) return null;

    const nodes = [];
    const edges = [];
    const nodeIds = new Set();

    if (tabType === 'competitor') {
        // Competitor data: [{company, competitor, strength}]
        data.forEach((item, idx) => {
            if (item.company && !nodeIds.has(item.company)) {
                nodes.push({ id: item.company, label: item.company, group: 'Corporation' });
                nodeIds.add(item.company);
            }
            if (item.competitor && !nodeIds.has(item.competitor)) {
                nodes.push({ id: item.competitor, label: item.competitor, group: 'Corporation' });
                nodeIds.add(item.competitor);
            }
            if (item.company && item.competitor) {
                edges.push({ id: `e${idx}`, from: item.company, to: item.competitor });
            }
        });
    } else if (tabType === 'problem') {
        // Problem data: [{problem, solution, patent_number, title}]
        data.forEach((item, idx) => {
            const patentId = item.patent_number || `patent_${idx}`;
            if (!nodeIds.has(patentId)) {
                nodes.push({ id: patentId, label: item.title || patentId, group: 'Patent' });
                nodeIds.add(patentId);
            }
            if (item.problem) {
                const problemId = `problem_${idx}`;
                nodes.push({ id: problemId, label: item.problem.substring(0, 40) + '...', group: 'Default' });
                edges.push({ id: `e_prob_${idx}`, from: patentId, to: problemId });
            }
            if (item.solution) {
                const solutionId = `solution_${idx}`;
                nodes.push({ id: solutionId, label: item.solution.substring(0, 40) + '...', group: 'Technology' });
                edges.push({ id: `e_sol_${idx}`, from: patentId, to: solutionId });
            }
        });
    } else if (tabType === 'cluster') {
        // Cluster data: [{technology_code, technology_level, patent_count, top_patents}]
        data.forEach((item, idx) => {
            const techId = item.technology_code || `tech_${idx}`;
            if (!nodeIds.has(techId)) {
                nodes.push({ id: techId, label: `${techId} (${item.patent_count})`, group: 'Technology' });
                nodeIds.add(techId);
            }
            (item.top_patents || []).forEach((patentTitle, pIdx) => {
                const patentId = `${techId}_patent_${pIdx}`;
                nodes.push({ id: patentId, label: patentTitle?.substring(0, 30) + '...' || patentId, group: 'Patent' });
                edges.push({ id: `e_${techId}_${pIdx}`, from: techId, to: patentId });
            });
        });
    } else if (tabType === 'path') {
        // Path data: [{path_nodes, distance}]
        data.forEach((item, idx) => {
            const pathNodes = item.path_nodes || [];
            pathNodes.forEach((nodeLabel, nIdx) => {
                const nodeId = `path${idx}_node${nIdx}`;
                if (!nodeIds.has(nodeLabel)) {
                    nodes.push({ id: nodeLabel, label: nodeLabel, group: 'Default' });
                    nodeIds.add(nodeLabel);
                }
                if (nIdx > 0) {
                    edges.push({ id: `path${idx}_e${nIdx}`, from: pathNodes[nIdx - 1], to: nodeLabel });
                }
            });
        });
    }

    return nodes.length > 0 ? { nodes, edges } : null;
};

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

    // IPC Classification States
    const [ipcSection, setIpcSection] = useState('');
    const [ipcClass, setIpcClass] = useState('');
    const [ipcSubclass, setIpcSubclass] = useState('');
    const [ipcGroup, setIpcGroup] = useState('');

    // IPC Sections Data (A-H)
    const IPC_SECTIONS = [
        { code: 'A', name: 'Human Necessities (생활필수품)' },
        { code: 'B', name: 'Operations, Transport (처리조작, 운수)' },
        { code: 'C', name: 'Chemistry, Metallurgy (화학, 야금)' },
        { code: 'D', name: 'Textiles, Paper (섬유, 제지)' },
        { code: 'E', name: 'Fixed Constructions (고정구조물)' },
        { code: 'F', name: 'Mechanical Engineering (기계공학)' },
        { code: 'G', name: 'Physics (물리학)' },
        { code: 'H', name: 'Electricity (전기)' },
    ];

    // IPC Main Classes (simplified - user can type or select)
    const getIpcClasses = (section) => {
        if (!section) return [];
        // Common main classes per section
        const classMap = {
            'A': ['01', '21', '23', '41', '43', '45', '47', '61', '62', '63'],
            'B': ['01', '02', '03', '04', '05', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '41', '60', '62', '63', '64', '65', '66', '67'],
            'C': ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '21', '22', '23', '25', '30', '40'],
            'D': ['01', '02', '03', '04', '05', '06', '07', '21'],
            'E': ['01', '02', '03', '04', '05', '06', '21'],
            'F': ['01', '02', '03', '04', '15', '16', '17', '21', '22', '23', '24', '25', '26', '27', '28', '41', '42'],
            'G': ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '16', '21'],
            'H': ['01', '02', '03', '04', '05', '10'],
        };
        return classMap[section] || [];
    };

    // IPC Subclasses per Class
    const getIpcSubclasses = (section, classCode) => {
        if (!section || !classCode) return [];
        // Common subclass letters per class
        const subclassMap = {
            // Section A
            'A01': ['B', 'C', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P'],
            'A23': ['B', 'C', 'D', 'F', 'G', 'J', 'K', 'L', 'N', 'P'],
            'A61': ['B', 'C', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q'],
            // Section B  
            'B01': ['D', 'F', 'J', 'L'],
            'B21': ['B', 'C', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            'B29': ['B', 'C', 'D', 'K', 'L'],
            'B60': ['B', 'C', 'D', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'W'],
            'B65': ['B', 'C', 'D', 'F', 'G', 'H'],
            // Section C
            'C01': ['B', 'C', 'D', 'F', 'G'],
            'C07': ['B', 'C', 'D', 'F', 'G', 'H', 'J', 'K'],
            'C08': ['B', 'C', 'F', 'G', 'H', 'J', 'K', 'L'],
            'C12': ['C', 'G', 'H', 'J', 'L', 'M', 'N', 'P', 'Q', 'R', 'S'],
            // Section G
            'G01': ['B', 'C', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'R', 'S', 'T', 'V', 'W'],
            'G02': ['B', 'C', 'F'],
            'G03': ['B', 'C', 'D', 'F', 'G', 'H'],
            'G06': ['C', 'D', 'E', 'F', 'G', 'J', 'K', 'N', 'Q', 'T', 'V'],
            'G09': ['B', 'C', 'D', 'F', 'G'],
            'G11': ['B', 'C'],
            // Section H
            'H01': ['B', 'C', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'P', 'Q', 'R', 'S', 'T'],
            'H02': ['B', 'G', 'H', 'J', 'K', 'M', 'N', 'P', 'S'],
            'H03': ['B', 'C', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'M'],
            'H04': ['B', 'H', 'J', 'K', 'L', 'M', 'N', 'Q', 'R', 'S', 'W'],
            'H05': ['B', 'C', 'F', 'G', 'H', 'K'],
            'H10': ['B', 'K', 'N'],
        };
        const key = section + classCode;
        return subclassMap[key] || ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T'];
    };

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

    // Transform result data to graph format
    const graphData = useMemo(() => {
        if (!result || !result.data) return null;
        return transformResultToGraph(result.data, activeTab);
    }, [result, activeTab]);

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
                    { id: 'cluster', label: 'IPC Classification', icon: Cpu },
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
                        <h2 className="text-xl font-bold text-gray-800">IPC Classification Search</h2>
                        <p className="text-gray-500 text-sm">Search patents by IPC (International Patent Classification) code hierarchy.</p>

                        {/* Cascading IPC Dropdowns */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-left">
                            {/* Section Select */}
                            <div>
                                <label className="block text-xs font-bold text-gray-500 mb-1 uppercase tracking-wider">Section</label>
                                <select
                                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:border-purple-500 focus:ring-4 focus:ring-purple-50 outline-none transition-all bg-white"
                                    value={ipcSection}
                                    onChange={(e) => {
                                        setIpcSection(e.target.value);
                                        setIpcClass('');
                                        setIpcSubclass('');
                                        setTechKeyword(e.target.value);
                                    }}
                                >
                                    <option value="">-- Select Section --</option>
                                    {IPC_SECTIONS.map(s => (
                                        <option key={s.code} value={s.code}>{s.code} - {s.name}</option>
                                    ))}
                                </select>
                            </div>

                            {/* Class Select */}
                            <div>
                                <label className="block text-xs font-bold text-gray-500 mb-1 uppercase tracking-wider">Class</label>
                                <select
                                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:border-purple-500 focus:ring-4 focus:ring-purple-50 outline-none transition-all bg-white disabled:bg-gray-100"
                                    value={ipcClass}
                                    onChange={(e) => {
                                        setIpcClass(e.target.value);
                                        setIpcSubclass('');
                                        setIpcGroup('');
                                        setTechKeyword(ipcSection + e.target.value);
                                    }}
                                    disabled={!ipcSection}
                                >
                                    <option value="">-- All Classes --</option>
                                    {getIpcClasses(ipcSection).map(c => (
                                        <option key={c} value={c}>{ipcSection}{c}</option>
                                    ))}
                                </select>
                            </div>

                            {/* Subclass Select */}
                            <div>
                                <label className="block text-xs font-bold text-gray-500 mb-1 uppercase tracking-wider">Subclass</label>
                                <select
                                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:border-purple-500 focus:ring-4 focus:ring-purple-50 outline-none transition-all bg-white disabled:bg-gray-100"
                                    value={ipcSubclass}
                                    onChange={(e) => {
                                        setIpcSubclass(e.target.value);
                                        setIpcGroup('');
                                        setTechKeyword(ipcSection + ipcClass + e.target.value);
                                    }}
                                    disabled={!ipcClass}
                                >
                                    <option value="">-- All Subclasses --</option>
                                    {getIpcSubclasses(ipcSection, ipcClass).map(s => (
                                        <option key={s} value={s}>{ipcSection}{ipcClass}{s}</option>
                                    ))}
                                </select>
                            </div>
                        </div>

                        {/* Group Input (Optional) */}
                        <div className="max-w-xs mx-auto">
                            <label className="block text-xs font-bold text-gray-500 mb-1 uppercase tracking-wider text-left">Group (Optional)</label>
                            <input
                                type="text"
                                className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:border-purple-500 focus:ring-4 focus:ring-purple-50 outline-none transition-all disabled:bg-gray-100"
                                placeholder="e.g., 1/00, 7/004"
                                value={ipcGroup}
                                onChange={(e) => {
                                    setIpcGroup(e.target.value);
                                    const fullCode = ipcSection + ipcClass + ipcSubclass + (e.target.value ? ' ' + e.target.value : '');
                                    setTechKeyword(fullCode);
                                }}
                                disabled={!ipcSubclass}
                            />
                        </div>

                        {/* Selected IPC Code Display */}
                        {ipcSection && (
                            <div className="bg-purple-50 border border-purple-100 rounded-xl px-4 py-2 inline-block">
                                <span className="text-xs text-purple-500 font-medium">Selected IPC: </span>
                                <span className="text-purple-700 font-bold">{techKeyword || ipcSection}</span>
                            </div>
                        )}

                        <button
                            onClick={() => handleSearch('cluster')}
                            disabled={loading || !ipcSection}
                            className="px-6 py-3 bg-purple-600 text-white rounded-xl hover:bg-purple-700 shadow-lg shadow-purple-200 flex items-center gap-2 disabled:opacity-50 transition-all mx-auto"
                        >
                            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Cpu className="w-4 h-4" />}
                            Search IPC
                        </button>
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

                                {/* Graph Visualization */}
                                {graphData && graphData.nodes && graphData.nodes.length > 0 && (
                                    <div className="p-6 border-b border-gray-100">
                                        <h3 className="font-bold mb-4 text-gray-700 flex items-center gap-2">
                                            <Network className="w-4 h-4 text-purple-500" />
                                            Interactive Graph View:
                                        </h3>
                                        <div className="h-[600px] bg-gray-50 rounded-2xl border border-gray-200 overflow-hidden">
                                            <GraphVisualizer data={graphData} />
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
