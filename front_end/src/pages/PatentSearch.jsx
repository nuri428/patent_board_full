import React, { useState, useEffect } from 'react';
import { patentAPI } from '../api/axios';
import { Search, Filter, Calendar, Building, FileText, ChevronLeft, ChevronRight, Loader2, Info } from 'lucide-react';

const PatentSearch = () => {
    const [searchParams, setSearchParams] = useState({
        title: '',
        abstract: '',
        assignee: '',
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

    const handleSearch = async (e) => {
        if (e) e.preventDefault();
        setLoading(true);
        try {
            // Clean up empty params
            const params = Object.fromEntries(
                Object.entries(searchParams).filter(([_, v]) => v !== '' && v !== null)
            );
            const data = await patentAPI.search(params);
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
            <header className="flex flex-col gap-2">
                <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600">
                    Patent Search
                </h1>
                <p className="text-gray-500">
                    Search and explore the patent database with advanced filters.
                </p>
            </header>

            {/* Search Panel */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 backdrop-blur-xl bg-opacity-80">
                <form onSubmit={handleSearch} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        <div className="col-span-1 md:col-span-2">
                            <label className="block text-sm font-medium text-gray-700 mb-1">Title / Keywords</label>
                            <div className="relative">
                                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                                <input
                                    type="text"
                                    name="title"
                                    placeholder="Search by title..."
                                    value={searchParams.title}
                                    onChange={handleChange}
                                    className="w-full pl-10 pr-4 py-2 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 transition-all outline-none"
                                />
                            </div>
                        </div>
                        <div className="col-span-1 md:col-span-2">
                            <label className="block text-sm font-medium text-gray-700 mb-1">Abstract</label>
                            <div className="relative">
                                <FileText className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                                <input
                                    type="text"
                                    name="abstract"
                                    placeholder="Search in abstract..."
                                    value={searchParams.abstract}
                                    onChange={handleChange}
                                    className="w-full pl-10 pr-4 py-2 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 transition-all outline-none"
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Assignee</label>
                            <div className="relative">
                                <Building className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                                <input
                                    type="text"
                                    name="assignee"
                                    placeholder="Samsung, Apple, etc."
                                    value={searchParams.assignee}
                                    onChange={handleChange}
                                    className="w-full pl-10 pr-4 py-2 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 transition-all outline-none"
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                            <div className="relative">
                                <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                                <select
                                    name="status"
                                    value={searchParams.status}
                                    onChange={handleChange}
                                    className="w-full pl-10 pr-4 py-2 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 transition-all outline-none appearance-none bg-white"
                                >
                                    <option value="">All Statuses</option>
                                    <option value="active">Active</option>
                                    <option value="pending">Pending</option>
                                    <option value="expired">Expired</option>
                                    <option value="abandoned">Abandoned</option>
                                </select>
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
                                    className="w-full pl-10 pr-4 py-2 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 transition-all outline-none"
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
                                    className="w-full pl-10 pr-4 py-2 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 transition-all outline-none"
                                />
                            </div>
                        </div>
                    </div>

                    <div className="flex justify-end pt-2">
                        <button
                            type="submit"
                            disabled={loading}
                            className="px-6 py-2.5 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:shadow-lg hover:shadow-blue-500/25 transition-all flex items-center gap-2 font-medium disabled:opacity-70 disabled:cursor-not-allowed"
                        >
                            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
                            Search Patents
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
                                        <th className="p-4 font-medium text-right">Actions</th> // Placeholder
                                    </tr>
                                </thead>
                                <tbody className="text-sm divide-y divide-gray-50">
                                    {results.map((patent) => (
                                        <tr key={patent.id} className="hover:bg-blue-50/50 transition-colors group">
                                            <td className="p-4 font-medium text-gray-900">{patent.patent_id}</td>
                                            <td className="p-4">
                                                <div className="font-medium text-gray-900 line-clamp-1 group-hover:text-blue-600 transition-colors">
                                                    {patent.title}
                                                </div>
                                                <div className="text-xs text-gray-500 line-clamp-1 mt-0.5">
                                                    {patent.abstract || "No abstract available"}
                                                </div>
                                            </td>
                                            <td className="p-4 text-gray-600">
                                                {patent.assignee || <span className="text-gray-400 italic">Unknown</span>}
                                            </td>
                                            <td className="p-4 text-gray-600">
                                                {patent.filing_date
                                                    ? new Date(patent.filing_date).toLocaleDateString()
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
                                                <button className="text-blue-600 hover:text-blue-700 font-medium text-xs">
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
        </div>
    );
};

export default PatentSearch;
