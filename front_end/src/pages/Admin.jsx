import React, { useState, useEffect } from 'react';
import {
    Database,
    Plus,
    Save,
    X,
    Trash2,
    Search,
    RefreshCw,
    Download,
    BarChart3,
    PieChart as PieChartIcon,
    Loader2,
    AlertCircle,
    CheckCircle2
} from 'lucide-react';
import api from '../api/axios';

const Admin = () => {
    const [stats, setStats] = useState({
        total_patents: 0,
        status_distribution: {},
        top_assignees: {}
    });
    const [loading, setLoading] = useState(true);
    const [actionLoading, setActionLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const [showAddModal, setShowAddModal] = useState(false);
    const [patents, setPatents] = useState([]);

    const [newPatent, setNewPatent] = useState({
        patent_id: '',
        title: '',
        abstract: '',
        assignee: '',
        status: 'pending',
        inventors: '',
        filing_date: ''
    });

    const fetchStats = async () => {
        try {
            const response = await api.get('/admin/statistics');
            setStats(response.data);
        } catch (err) {
            console.error("Failed to fetch statistics", err);
        }
    };

    const fetchRecentPatents = async () => {
        try {
            // Reusing common search with a high limit for recent ones
            const response = await api.post('/patents/search', { limit: 10, offset: 0 });
            setPatents(response.data.patents || []);
        } catch (err) {
            console.error("Failed to fetch patents", err);
        }
    };

    const loadData = async () => {
        setLoading(true);
        setError(null);
        try {
            await Promise.all([fetchStats(), fetchRecentPatents()]);
        } catch (err) {
            setError("Failed to load admin data");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadData();
    }, []);

    const handleAddPatent = async (e) => {
        e.preventDefault();
        setActionLoading(true);
        setError(null);
        setSuccess(null);

        try {
            const payload = {
                ...newPatent,
                inventors: newPatent.inventors.split(',').map(s => s.trim()).filter(s => s)
            };
            await api.post('/admin/', payload);
            setSuccess("Patent added successfully!");
            setShowAddModal(false);
            setNewPatent({
                patent_id: '',
                title: '',
                abstract: '',
                assignee: '',
                status: 'pending',
                inventors: '',
                filing_date: ''
            });
            loadData();
        } catch (err) {
            setError(err.response?.data?.detail || "Failed to add patent");
        } finally {
            setActionLoading(false);
        }
    };

    const handleDeletePatent = async (patentId) => {
        if (!window.confirm(`Are you sure you want to delete patent ${patentId}?`)) return;

        setActionLoading(true);
        try {
            await api.delete(`/admin/${patentId}`);
            setSuccess("Patent deleted successfully");
            loadData();
        } catch (err) {
            setError("Failed to delete patent");
        } finally {
            setActionLoading(false);
        }
    };

    const handleExportCSV = async () => {
        try {
            const response = await api.get('/admin/export/csv');
            const blob = new Blob([response.data.content], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = response.data.filename;
            a.click();
        } catch (err) {
            setError("Failed to export CSV");
        }
    };

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center h-[60vh] text-slate-500">
                <Loader2 className="w-10 h-10 animate-spin mb-4 text-indigo-600" />
                <p className="font-medium">Loading administrative workspace...</p>
            </div>
        );
    }

    return (
        <div className="space-y-8 max-w-[1400px] mx-auto">
            {/* Header */}
            <div className="flex justify-between items-end">
                <div>
                    <h1 className="text-3xl font-bold text-slate-900 tracking-tight flex items-center gap-3">
                        <Database className="w-8 h-8 text-indigo-600" />
                        Admin Registry
                    </h1>
                    <p className="text-slate-500 mt-1">Manage core patent data and monitor system statistics</p>
                </div>
                <div className="flex gap-3">
                    <button
                        onClick={handleExportCSV}
                        className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 rounded-xl hover:bg-slate-50 transition-colors font-semibold text-slate-700 shadow-sm"
                    >
                        <Download className="w-4 h-4" /> Export CSV
                    </button>
                    <button
                        onClick={() => setShowAddModal(true)}
                        className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-colors font-semibold shadow-lg shadow-indigo-100"
                    >
                        <Plus className="w-4 h-4" /> Add Patent
                    </button>
                </div>
            </div>

            {/* Notifications */}
            {error && (
                <div className="bg-red-50 border border-red-100 text-red-700 p-4 rounded-2xl flex items-center gap-3 animate-in fade-in slide-in-from-top-2">
                    <AlertCircle className="w-5 h-5 flex-shrink-0" />
                    <p className="font-medium">{error}</p>
                    <button onClick={() => setError(null)} className="ml-auto hover:text-red-800"><X className="w-4 h-4" /></button>
                </div>
            )}
            {success && (
                <div className="bg-emerald-50 border border-emerald-100 text-emerald-700 p-4 rounded-2xl flex items-center gap-3 animate-in fade-in slide-in-from-top-2">
                    <CheckCircle2 className="w-5 h-5 flex-shrink-0" />
                    <p className="font-medium">{success}</p>
                    <button onClick={() => setSuccess(null)} className="ml-auto hover:text-emerald-800"><X className="w-4 h-4" /></button>
                </div>
            )}

            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="premium-card p-6 bg-white">
                    <p className="text-slate-500 text-sm font-medium mb-1 uppercase tracking-wider">Total Patents</p>
                    <h2 className="text-3xl font-bold text-slate-900">{stats.total_patents.toLocaleString()}</h2>
                </div>
                {Object.entries(stats.status_distribution).slice(0, 3).map(([status, count]) => (
                    <div key={status} className="premium-card p-6 bg-white">
                        <p className="text-slate-500 text-sm font-medium mb-1 uppercase tracking-wider">{status}</p>
                        <h2 className="text-3xl font-bold text-slate-900">{count}</h2>
                    </div>
                ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Distribution Charts Replicated in simple list/bar form for now */}
                <div className="premium-card p-6 bg-white space-y-6">
                    <h3 className="font-bold text-slate-800 flex items-center gap-2">
                        <PieChartIcon className="w-5 h-5 text-indigo-500" />
                        Status Distribution
                    </h3>
                    <div className="space-y-4">
                        {Object.entries(stats.status_distribution).map(([status, count]) => (
                            <div key={status} className="space-y-1">
                                <div className="flex justify-between text-sm">
                                    <span className="capitalize text-slate-600 font-medium">{status}</span>
                                    <span className="text-slate-900 font-bold">{count}</span>
                                </div>
                                <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-indigo-500 rounded-full transition-all duration-1000"
                                        style={{ width: `${(count / stats.total_patents) * 100}%` }}
                                    ></div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="premium-card p-6 bg-white space-y-6">
                    <h3 className="font-bold text-slate-800 flex items-center gap-2">
                        <BarChart3 className="w-5 h-5 text-emerald-500" />
                        Top Assignees
                    </h3>
                    <div className="space-y-4">
                        {Object.entries(stats.top_assignees).map(([assignee, count]) => (
                            <div key={assignee} className="space-y-1">
                                <div className="flex justify-between text-sm">
                                    <span className="text-slate-600 font-medium truncate pr-4">{assignee}</span>
                                    <span className="text-slate-900 font-bold">{count}</span>
                                </div>
                                <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-emerald-500 rounded-full transition-all duration-1000"
                                        style={{ width: `${(count / stats.total_patents) * 100}%` }}
                                    ></div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Recent Patents Table */}
            <div className="premium-card bg-white overflow-hidden">
                <div className="p-6 border-b border-slate-50 flex justify-between items-center">
                    <h3 className="font-bold text-slate-900">Recent Additions</h3>
                    <button onClick={loadData} className="p-2 hover:bg-slate-50 rounded-lg transition-colors group">
                        <RefreshCw className={`w-4 h-4 text-slate-400 group-hover:text-indigo-600 ${actionLoading ? 'animate-spin' : ''}`} />
                    </button>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead className="bg-slate-50/50 text-[11px] uppercase tracking-widest text-slate-500 font-bold">
                            <tr>
                                <th className="px-6 py-4">ID</th>
                                <th className="px-6 py-4">Title</th>
                                <th className="px-6 py-4">Assignee</th>
                                <th className="px-6 py-4">Status</th>
                                <th className="px-6 py-4 text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-50 text-sm">
                            {patents.map((patent) => (
                                <tr key={patent.id} className="hover:bg-slate-50/50 transition-colors group">
                                    <td className="px-6 py-4 font-mono text-xs text-indigo-600 font-bold">{patent.id}</td>
                                    <td className="px-6 py-4 font-medium text-slate-900">
                                        <div className="line-clamp-1 max-w-sm">{patent.title}</div>
                                    </td>
                                    <td className="px-6 py-4 text-slate-600">{patent.assignee || '-'}</td>
                                    <td className="px-6 py-4">
                                        <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold uppercase transition-all ${patent.status === 'active' || patent.status === 'granted'
                                                ? 'bg-emerald-50 text-emerald-700 border border-emerald-100'
                                                : 'bg-slate-100 text-slate-600 border border-slate-200'
                                            }`}>
                                            {patent.status}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-right">
                                        <button
                                            onClick={() => handleDeletePatent(patent.id)}
                                            className="p-2 text-slate-300 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all opacity-0 group-hover:opacity-100"
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Add Modal */}
            {showAddModal && (
                <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center z-[100] p-4 animate-in fade-in duration-200">
                    <div className="bg-white rounded-3xl shadow-2xl w-full max-w-2xl overflow-hidden animate-in zoom-in-95 duration-200">
                        <div className="p-6 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
                            <h2 className="text-xl font-bold text-slate-900">Add New Patent Record</h2>
                            <button onClick={() => setShowAddModal(false)} className="p-2 hover:bg-white rounded-full transition-all">
                                <X className="w-5 h-5 text-slate-400" />
                            </button>
                        </div>
                        <form onSubmit={handleAddPatent} className="p-8 space-y-6">
                            <div className="grid grid-cols-2 gap-6">
                                <div className="space-y-1.5">
                                    <label className="text-xs font-bold text-slate-500 uppercase">Patent ID / App Number *</label>
                                    <input
                                        required
                                        type="text"
                                        className="premium-input w-full"
                                        placeholder="e.g. 10-2023-..."
                                        value={newPatent.patent_id}
                                        onChange={e => setNewPatent({ ...newPatent, patent_id: e.target.value })}
                                    />
                                </div>
                                <div className="space-y-1.5">
                                    <label className="text-xs font-bold text-slate-500 uppercase">Assignee</label>
                                    <input
                                        type="text"
                                        className="premium-input w-full"
                                        placeholder="Company Name"
                                        value={newPatent.assignee}
                                        onChange={e => setNewPatent({ ...newPatent, assignee: e.target.value })}
                                    />
                                </div>
                                <div className="col-span-2 space-y-1.5">
                                    <label className="text-xs font-bold text-slate-500 uppercase">Patent Title *</label>
                                    <input
                                        required
                                        type="text"
                                        className="premium-input w-full"
                                        placeholder="Full 기술 명칭"
                                        value={newPatent.title}
                                        onChange={e => setNewPatent({ ...newPatent, title: e.target.value })}
                                    />
                                </div>
                                <div className="col-span-2 space-y-1.5">
                                    <label className="text-xs font-bold text-slate-500 uppercase">Abstract Summary *</label>
                                    <textarea
                                        required
                                        rows="4"
                                        className="premium-input w-full resize-none"
                                        placeholder="Detailed technical abstract..."
                                        value={newPatent.abstract}
                                        onChange={e => setNewPatent({ ...newPatent, abstract: e.target.value })}
                                    />
                                </div>
                                <div className="space-y-1.5">
                                    <label className="text-xs font-bold text-slate-500 uppercase">Initial Status</label>
                                    <select
                                        className="premium-input w-full appearance-none"
                                        value={newPatent.status}
                                        onChange={e => setNewPatent({ ...newPatent, status: e.target.value })}
                                    >
                                        <option value="pending">Pending</option>
                                        <option value="granted">Granted</option>
                                        <option value="expired">Expired</option>
                                        <option value="abandoned">Abandoned</option>
                                    </select>
                                </div>
                                <div className="space-y-1.5">
                                    <label className="text-xs font-bold text-slate-500 uppercase">Filing Date</label>
                                    <input
                                        type="date"
                                        className="premium-input w-full"
                                        value={newPatent.filing_date}
                                        onChange={e => setNewPatent({ ...newPatent, filing_date: e.target.value })}
                                    />
                                </div>
                            </div>

                            <div className="flex gap-4 pt-4">
                                <button
                                    type="button"
                                    onClick={() => setShowAddModal(false)}
                                    className="flex-1 py-4 bg-slate-50 text-slate-600 rounded-2xl font-bold hover:bg-slate-100 transition-all border border-slate-200"
                                >
                                    Cancel
                                </button>
                                <button
                                    disabled={actionLoading}
                                    type="submit"
                                    className="flex-1 py-4 bg-indigo-600 text-white rounded-2xl font-bold hover:bg-indigo-700 transition-all shadow-xl shadow-indigo-100 flex items-center justify-center gap-2"
                                >
                                    {actionLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Save className="w-5 h-5" />}
                                    Commit Record
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Admin;
