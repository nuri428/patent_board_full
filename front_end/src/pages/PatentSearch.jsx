import React, { useState, useEffect } from 'react';
import { patentAPI } from '../api/axios';
import { patentMcpAPI } from '../api/mcp';
import { Search, Filter, Calendar, Building, FileText, ChevronLeft, ChevronRight, Loader2, Info, LayoutGrid, Terminal, X } from 'lucide-react';

const PatentSearch = () => {
    const [isAnalystMode, setIsAnalystMode] = useState(false);
    const [searchParams, setSearchParams] = useState({
        title: '',
        abstract: '',
        assignee: '',
        ipc: '',
        inventor: '',
        status: '',
        filing_date_from: '',
        filing_date_to: '',
        limit: 10,
        offset: 0
    });
    const [results, setResults] = useState([]);
    const [total, setTotal] = useState(0);
    const [loading, setLoading] = useState(false);
    const [searched, setSearched] = useState(false);
    const [metadata, setMetadata] = useState({
        confidence: null,
        interpretation: null,
        source: null
    });
    const [selectedPatent, setSelectedPatent] = useState(null);
    const [modalLoading, setModalLoading] = useState(false);

    const handleViewDetail = async (patentId) => {
        setModalLoading(true);
        try {
            const data = await patentAPI.get(patentId);
            setSelectedPatent(data);
        } catch (error) {
            console.error('Failed to fetch patent detail:', error);
        } finally {
            setModalLoading(false);
        }
    };

    const closeModal = () => setSelectedPatent(null);

    const handleSearch = async (e) => {
        if (e) e.preventDefault();
        setLoading(true);
        setMetadata({
            confidence: null,
            interpretation: null,
            source: null
        });
        try {
            // Clean up empty params
            const params = Object.fromEntries(
                Object.entries(searchParams).filter(([_, v]) => v !== '' && v !== null)
            );

            let data;
            if (isAnalystMode) {
                const proxyResponse = await patentMcpAPI.searchKRPatents(params);
                const patentsList = Array.isArray(proxyResponse.data) ? proxyResponse.data : (proxyResponse.data.patents || []);
                data = {
                    patents: patentsList,
                    total: proxyResponse.data.total_count || patentsList.length
                };
                setMetadata({
                    confidence: proxyResponse.confidence,
                    interpretation: proxyResponse.interpretation_note,
                    source: proxyResponse.source
                });
            } else {
                data = await patentAPI.search(params);
            }

            setResults(data.patents);
            setTotal(data.total);
            setSearched(true);
        } catch (error) {
            console.error("Search failed:", error);
        } finally {
            setLoading(false);
        }
    };

    const handlePageChange = (newOffset) => {
        setSearchParams(prev => ({ ...prev, offset: newOffset }));
    };

    useEffect(() => {
        if (searched) {
            handleSearch();
        }
    }, [searchParams.offset]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setSearchParams(prev => ({ ...prev, [name]: value, offset: 0 })); // Reset offset on filter change
    };

    const totalPages = Math.ceil(total / searchParams.limit);
    const currentPage = Math.floor(searchParams.offset / searchParams.limit) + 1;

    return (
        <div className="space-y-6">
            <header className="flex justify-between items-end">
                <div className="flex flex-col gap-2">
                    <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600">
                        Patent Intelligence Workbench
                    </h1>
                    <p className="text-gray-500">
                        {isAnalystMode ? 'Advanced Technical Analysis (KIPRIS Powered)' : 'Quick Search and Discovery'}
                    </p>
                </div>

                {/* Mode Toggle */}
                <div className="flex bg-gray-100 p-1 rounded-xl border border-gray-200">
                    <button
                        onClick={() => setIsAnalystMode(false)}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${!isAnalystMode ? 'bg-white shadow-sm text-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
                    >
                        <LayoutGrid className="w-4 h-4" />
                        Explorer
                    </button>
                    <button
                        onClick={() => setIsAnalystMode(true)}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${isAnalystMode ? 'bg-white shadow-sm text-purple-600' : 'text-gray-500 hover:text-gray-700'}`}
                    >
                        <Terminal className="w-4 h-4" />
                        Analyst
                    </button>
                </div>
            </header>

            {/* Confidence HUD (Analyst Only) */}
            {isAnalystMode && metadata.confidence && (
                <div className="flex items-center justify-between bg-purple-50 border border-purple-100 p-4 rounded-2xl shadow-sm">
                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2 text-purple-700 text-sm font-bold">
                            <Info className="w-4 h-4" />
                            ANALYSIS CONFIDENCE:
                            <span className={`px-3 py-1 rounded-full text-xs font-bold border ${metadata.confidence === 'High' ? 'bg-green-100 text-green-700 border-green-200' :
                                metadata.confidence === 'Medium' ? 'bg-yellow-100 text-yellow-700 border-yellow-200' :
                                    'bg-red-100 text-red-700 border-red-200'
                                }`}>
                                {metadata.confidence}
                            </span>
                        </div>
                        {metadata.interpretation && (
                            <div className="text-xs text-purple-600 font-medium border-l border-purple-200 pl-4 uppercase tracking-tighter">
                                {metadata.interpretation}
                            </div>
                        )}
                    </div>
                    {metadata.source && (
                        <div className="text-[10px] text-purple-300 font-bold uppercase tracking-widest">
                            Source: {metadata.source}
                        </div>
                    )}
                </div>
            )}

            {/* Search Panel */}
            <div className={`bg-white rounded-2xl shadow-sm border p-6 backdrop-blur-xl bg-opacity-80 transition-all ${isAnalystMode ? 'border-purple-200 ring-4 ring-purple-50' : 'border-gray-100'}`}>
                <form onSubmit={handleSearch} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        <div className="col-span-1 md:col-span-2 lg:col-span-4">
                            <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-1">
                                Search Keywords
                                <Info className="w-3 h-3 text-gray-400 cursor-help" title="Keywords are matched against titles and abstracts." />
                            </label>
                            <div className="relative">
                                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                                <input
                                    type="text"
                                    name="title"
                                    placeholder="Enter search keywords or title..."
                                    value={searchParams.title}
                                    onChange={handleChange}
                                    className="w-full pl-10 pr-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 transition-all outline-none text-lg"
                                />
                            </div>
                        </div>

                        {/* Analyst Features */}
                        {isAnalystMode && (
                            <>
                                <div className="col-span-1 md:col-span-2">
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Technical Abstract</label>
                                    <div className="relative">
                                        <FileText className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                                        <input
                                            type="text"
                                            name="abstract"
                                            placeholder="Deep search for technical terms..."
                                            value={searchParams.abstract}
                                            onChange={handleChange}
                                            className="w-full pl-10 pr-4 py-2 rounded-xl border border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-100 transition-all outline-none"
                                        />
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">IPC Code</label>
                                    <div className="relative">
                                        <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                                        <input
                                            type="text"
                                            name="ipc"
                                            placeholder="e.g. H01M"
                                            value={searchParams.ipc}
                                            onChange={handleChange}
                                            className="w-full pl-10 pr-4 py-2 rounded-xl border border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-100 transition-all outline-none"
                                        />
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Assignee / Applicant</label>
                                    <div className="relative">
                                        <Building className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                                        <input
                                            type="text"
                                            name="assignee"
                                            placeholder="Samsung, LG, etc."
                                            value={searchParams.assignee}
                                            onChange={handleChange}
                                            className="w-full pl-10 pr-4 py-2 rounded-xl border border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-100 transition-all outline-none"
                                        />
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Inventor</label>
                                    <div className="relative">
                                        <Building className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                                        <input
                                            type="text"
                                            name="inventor"
                                            placeholder="Inventor name..."
                                            value={searchParams.inventor}
                                            onChange={handleChange}
                                            className="w-full pl-10 pr-4 py-2 rounded-xl border border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-100 transition-all outline-none"
                                        />
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">From Date</label>
                                    <div className="relative">
                                        <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                                        <input
                                            type="date"
                                            name="filing_date_from"
                                            value={searchParams.filing_date_from}
                                            onChange={handleChange}
                                            className="w-full pl-10 pr-4 py-2 rounded-xl border border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-100 transition-all outline-none"
                                        />
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">To Date</label>
                                    <div className="relative">
                                        <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                                        <input
                                            type="date"
                                            name="filing_date_to"
                                            value={searchParams.filing_date_to}
                                            onChange={handleChange}
                                            className="w-full pl-10 pr-4 py-2 rounded-xl border border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-100 transition-all outline-none"
                                        />
                                    </div>
                                </div>
                            </>
                        )}
                    </div>

                    <div className="flex justify-between items-center pt-2">
                        <div className="text-xs text-gray-400 italic">
                            {isAnalystMode ? 'Note: Analyst mode calls specialized KIPRIS search tools via MCP.' : 'Note: Explorer mode searches the indexed database cache.'}
                        </div>
                        <button
                            type="submit"
                            disabled={loading}
                            className={`px-6 py-2.5 text-white rounded-xl transition-all flex items-center gap-2 font-medium disabled:opacity-70 disabled:cursor-not-allowed ${isAnalystMode ? 'bg-purple-600 hover:bg-purple-700 shadow-purple-200' : 'bg-blue-600 hover:bg-blue-700 shadow-blue-200'
                                }`}
                        >
                            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
                            {isAnalystMode ? 'Analyze via MCP' : 'Search Database'}
                        </button>
                    </div>
                </form>
            </div>

            {/* Results Area */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden backdrop-blur-xl bg-opacity-80 flex flex-col min-h-[400px]">
                {!searched && !loading && (
                    <div className="flex-1 flex flex-col items-center justify-center text-gray-400 p-12">
                        <Search className="w-16 h-16 mb-4 opacity-20" />
                        <p className="text-lg font-medium">Enter search criteria to find patents</p>
                    </div>
                )}

                {loading && !results.length && (
                    <div className="flex-1 flex flex-col items-center justify-center text-blue-500 p-12">
                        <Loader2 className="w-12 h-12 mb-4 animate-spin" />
                        <p className="text-lg font-medium">Searching...</p>
                    </div>
                )}

                {searched && (
                    <>
                        <div className="p-4 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
                            <h3 className="font-semibold text-gray-700 flex items-center gap-2">
                                <Info className="w-4 h-4 text-blue-500" />
                                Found {total} results
                            </h3>
                        </div>

                        <div className="overflow-x-auto">
                            <table className="w-full text-left border-collapse">
                                <thead>
                                    <tr className="border-b border-gray-100 text-sm text-gray-500 bg-gray-50/30">
                                        <th className="p-4 font-medium">ID</th>
                                        <th className="p-4 font-medium w-1/3">Title</th>
                                        <th className="p-4 font-medium">Assignee</th>
                                        <th className="p-4 font-medium">Filing Date</th>
                                        <th className="p-4 font-medium">Status</th>
                                        <th className="p-4 font-medium text-right">Actions</th>
                                    </tr>
                                </thead>
                                <tbody className="text-sm divide-y divide-gray-50">
                                    {results.map((patent) => (
                                        <tr key={patent.id} className="hover:bg-blue-50/50 transition-colors group">
                                            <td className="p-4 font-medium text-gray-900">{patent.id}</td>
                                            <td className="p-4">
                                                <div className="font-medium text-gray-900 line-clamp-1 group-hover:text-blue-600 transition-colors">
                                                    {patent.title}
                                                </div>
                                                <div className="text-xs text-gray-500 line-clamp-1 mt-0.5">
                                                    {patent.abstract || "No abstract available"}
                                                </div>
                                            </td>
                                            <td className="p-4 text-gray-600">
                                                {patent.assignee || patent.registrant || <span className="text-gray-400 italic">Unknown</span>}
                                            </td>
                                            <td className="p-4 text-gray-600">
                                                {(patent.date || patent.filing_date)
                                                    ? new Date(patent.date || patent.filing_date).toLocaleDateString()
                                                    : <span className="text-gray-400">-</span>}
                                            </td>
                                            <td className="p-4">
                                                <span className={`inline-flex px-2.5 py-1 rounded-full text-xs font-medium border ${patent.status === 'active'
                                                    ? 'bg-green-50 text-green-700 border-green-100'
                                                    : 'bg-gray-100 text-gray-600 border-gray-200'
                                                    }`}>
                                                    {patent.status || 'Unknown'}
                                                </span>
                                            </td>
                                            <td className="p-4 text-right">
                                                <button
                                                    onClick={() => handleViewDetail(patent.id)}
                                                    className="text-blue-600 hover:text-blue-700 font-medium text-xs"
                                                >
                                                    View Details
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                    {results.length === 0 && !loading && (
                                        <tr>
                                            <td colSpan="6" className="p-12 text-center text-gray-500">
                                                No results found matching your criteria.
                                            </td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>

                        {/* Pagination */}
                        {total > 0 && (
                            <div className="p-4 border-t border-gray-100 flex items-center justify-between bg-gray-50/30">
                                <div className="text-sm text-gray-500">
                                    Page {currentPage} of {totalPages}
                                </div>
                                <div className="flex items-center gap-2">
                                    <button
                                        onClick={() => handlePageChange(searchParams.offset - searchParams.limit)}
                                        disabled={currentPage === 1}
                                        className="p-2 rounded-lg hover:bg-white hover:shadow-sm border border-transparent hover:border-gray-200 disabled:opacity-30 disabled:hover:bg-transparent disabled:hover:shadow-none transition-all"
                                    >
                                        <ChevronLeft className="w-4 h-4" />
                                    </button>
                                    <button
                                        onClick={() => handlePageChange(searchParams.offset + searchParams.limit)}
                                        disabled={currentPage === totalPages}
                                        className="p-2 rounded-lg hover:bg-white hover:shadow-sm border border-transparent hover:border-gray-200 disabled:opacity-30 disabled:hover:bg-transparent disabled:hover:shadow-none transition-all"
                                    >
                                        <ChevronRight className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>
                        )}
                    </>
                )}
            </div>

            {/* Patent Detail Modal */}
            {(selectedPatent || modalLoading) && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={closeModal}>
                    <div
                        className="bg-white rounded-2xl shadow-2xl max-w-3xl w-full max-h-[80vh] overflow-hidden"
                        onClick={(e) => e.stopPropagation()}
                    >
                        {modalLoading ? (
                            <div className="p-12 flex flex-col items-center justify-center">
                                <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
                                <p className="mt-4 text-gray-500">Loading patent details...</p>
                            </div>
                        ) : selectedPatent && (
                            <>
                                <div className="flex items-center justify-between p-6 border-b border-gray-100">
                                    <div className="flex items-center gap-3">
                                        <span className={`px-3 py-1 rounded-full text-xs font-bold ${selectedPatent.country === 'KR'
                                                ? 'bg-blue-100 text-blue-700'
                                                : 'bg-purple-100 text-purple-700'
                                            }`}>
                                            {selectedPatent.country}
                                        </span>
                                        <span className="text-sm text-gray-500 font-mono">{selectedPatent.patent_id}</span>
                                    </div>
                                    <button onClick={closeModal} className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                                        <X className="w-5 h-5 text-gray-500" />
                                    </button>
                                </div>
                                <div className="p-6 overflow-y-auto max-h-[60vh]">
                                    <h2 className="text-xl font-bold text-gray-900 mb-4">{selectedPatent.title}</h2>

                                    <div className="grid grid-cols-2 gap-4 mb-6">
                                        <div className="bg-gray-50 p-4 rounded-xl">
                                            <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Filing Date</p>
                                            <p className="font-medium">{selectedPatent.filing_date || '-'}</p>
                                        </div>
                                        <div className="bg-gray-50 p-4 rounded-xl">
                                            <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Publication Date</p>
                                            <p className="font-medium">{selectedPatent.publication_date || '-'}</p>
                                        </div>
                                        <div className="bg-gray-50 p-4 rounded-xl">
                                            <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Registration Date</p>
                                            <p className="font-medium">{selectedPatent.registration_date || '-'}</p>
                                        </div>
                                        <div className="bg-gray-50 p-4 rounded-xl">
                                            <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Status</p>
                                            <p className="font-medium">{selectedPatent.status || '-'}</p>
                                        </div>
                                    </div>

                                    {selectedPatent.publication_number && (
                                        <div className="mb-4">
                                            <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Publication Number</p>
                                            <p className="font-mono text-sm">{selectedPatent.publication_number}</p>
                                        </div>
                                    )}
                                    {selectedPatent.registration_number && (
                                        <div className="mb-4">
                                            <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Registration Number</p>
                                            <p className="font-mono text-sm">{selectedPatent.registration_number}</p>
                                        </div>
                                    )}

                                    <div className="mt-6">
                                        <p className="text-xs text-gray-500 uppercase tracking-wide mb-2">Abstract</p>
                                        <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
                                            {selectedPatent.abstract || 'No abstract available.'}
                                        </p>
                                    </div>
                                </div>
                            </>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default PatentSearch;
