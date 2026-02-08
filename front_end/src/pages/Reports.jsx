import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import {
    FileText,
    Loader2,
    Plus,
    RefreshCw,
    CheckCircle,
    XCircle,
    Clock,
    AlertCircle,
    Download,
    Trash2
} from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || '';

const Reports = () => {
    const { user } = useAuth();
    const [reports, setReports] = useState([]);
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState(false);
    const [error, setError] = useState(null);
    const [showGenerateModal, setShowGenerateModal] = useState(false);
    const [newReport, setNewReport] = useState({
        topic: '',
        report_type: 'comprehensive',
        patent_ids: ''
    });

    // Status badge colors
    const statusConfig = {
        pending: { color: 'bg-yellow-100 text-yellow-700 border-yellow-200', icon: Clock, label: 'Pending' },
        processing: { color: 'bg-blue-100 text-blue-700 border-blue-200', icon: Loader2, label: 'Processing' },
        completed: { color: 'bg-green-100 text-green-700 border-green-200', icon: CheckCircle, label: 'Completed' },
        failed: { color: 'bg-red-100 text-red-700 border-red-200', icon: XCircle, label: 'Failed' }
    };

    const fetchReports = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);

            const token = localStorage.getItem('token');
            const response = await fetch(`${API_URL}/api/v1/reports/`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Failed to fetch reports');
            }

            const data = await response.json();
            setReports(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, []);

    // Poll for status updates on pending/processing reports
    useEffect(() => {
        fetchReports();

        // Set up polling interval
        const interval = setInterval(() => {
            const hasActiveReports = reports.some(r =>
                r.status === 'pending' || r.status === 'processing'
            );
            if (hasActiveReports) {
                fetchReports();
            }
        }, 3000);

        return () => clearInterval(interval);
    }, [fetchReports, reports]);

    const handleGenerateReport = async (e) => {
        e.preventDefault();

        try {
            setGenerating(true);
            setError(null);

            const token = localStorage.getItem('token');
            const patentIds = newReport.patent_ids
                .split(',')
                .map(id => parseInt(id.trim()))
                .filter(id => !isNaN(id));

            const response = await fetch(`${API_URL}/api/v1/reports/generate`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    topic: newReport.topic,
                    report_type: newReport.report_type,
                    patent_ids: patentIds,
                    priority: 'normal'
                })
            });

            if (!response.ok) {
                throw new Error('Failed to generate report');
            }

            const data = await response.json();

            // Close modal and refresh reports
            setShowGenerateModal(false);
            setNewReport({ topic: '', report_type: 'comprehensive', patent_ids: '' });

            // Add the new report to the list immediately
            const newReportObj = {
                id: data.report_id,
                title: `Report: ${newReport.topic}`,
                topic: newReport.topic,
                status: 'pending',
                report_type: newReport.report_type,
                created_at: new Date().toISOString(),
                owner_id: user?.id
            };

            setReports(prev => [newReportObj, ...prev]);

        } catch (err) {
            setError(err.message);
        } finally {
            setGenerating(false);
        }
    };

    const handleDeleteReport = async (reportId) => {
        if (!confirm('Are you sure you want to delete this report?')) {
            return;
        }

        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_URL}/api/v1/reports/${reportId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                setReports(prev => prev.filter(r => r.id !== reportId));
            }
        } catch (err) {
            console.error('Failed to delete report:', err);
        }
    };

    const formatDate = (dateString) => {
        if (!dateString) return '-';
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const getReportTypeLabel = (type) => {
        const labels = {
            comprehensive: 'Comprehensive Analysis',
            technical: 'Technical Review',
            market: 'Market Landscape',
            strategic: 'Strategic Insights'
        };
        return labels[type] || type;
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600">
                        Reports
                    </h1>
                    <p className="text-gray-500 mt-1">
                        Generate and manage patent analysis reports
                    </p>
                </div>
                <div className="flex gap-3">
                    <button
                        onClick={fetchReports}
                        disabled={loading}
                        className="flex items-center gap-2 px-4 py-2 rounded-xl border border-gray-200 hover:bg-gray-50 transition-colors disabled:opacity-50"
                    >
                        <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                        Refresh
                    </button>
                    <button
                        onClick={() => setShowGenerateModal(true)}
                        className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors"
                    >
                        <Plus className="w-4 h-4" />
                        Generate Report
                    </button>
                </div>
            </div>

            {/* Error Alert */}
            {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl flex items-center gap-2">
                    <AlertCircle className="w-5 h-5" />
                    {error}
                </div>
            )}

            {/* Reports List */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                {loading && reports.length === 0 ? (
                    <div className="p-12 flex flex-col items-center justify-center text-gray-400">
                        <Loader2 className="w-8 h-8 animate-spin mb-4" />
                        <p>Loading reports...</p>
                    </div>
                ) : reports.length === 0 ? (
                    <div className="p-12 flex flex-col items-center justify-center text-gray-400">
                        <FileText className="w-16 h-16 mb-4 opacity-20" />
                        <p className="text-lg font-medium">No reports yet</p>
                        <p className="text-sm mt-1">Generate your first report to get started</p>
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="border-b border-gray-100 text-sm text-gray-500 bg-gray-50/30">
                                    <th className="p-4 font-medium">Title</th>
                                    <th className="p-4 font-medium">Type</th>
                                    <th className="p-4 font-medium">Status</th>
                                    <th className="p-4 font-medium">Created</th>
                                    <th className="p-4 font-medium">Completed</th>
                                    <th className="p-4 font-medium text-right">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="text-sm divide-y divide-gray-50">
                                {reports.map((report) => {
                                    const status = statusConfig[report.status] || statusConfig.pending;
                                    const StatusIcon = status.icon;

                                    return (
                                        <tr key={report.id} className="hover:bg-gray-50/50 transition-colors">
                                            <td className="p-4">
                                                <div className="font-medium text-gray-900">
                                                    {report.title}
                                                </div>
                                                <div className="text-xs text-gray-500 mt-0.5">
                                                    Topic: {report.topic}
                                                </div>
                                            </td>
                                            <td className="p-4">
                                                <span className="inline-flex px-2.5 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700">
                                                    {getReportTypeLabel(report.report_type)}
                                                </span>
                                            </td>
                                            <td className="p-4">
                                                <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${status.color}`}>
                                                    <StatusIcon className={`w-3.5 h-3.5 ${report.status === 'processing' ? 'animate-spin' : ''}`} />
                                                    {status.label}
                                                </span>
                                            </td>
                                            <td className="p-4 text-gray-600">
                                                {formatDate(report.created_at)}
                                            </td>
                                            <td className="p-4 text-gray-600">
                                                {report.generated_at ? formatDate(report.generated_at) : '-'}
                                            </td>
                                            <td className="p-4 text-right">
                                                <div className="flex items-center justify-end gap-2">
                                                    {report.status === 'completed' && (
                                                        <button
                                                            className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                                                            title="Download Report"
                                                        >
                                                            <Download className="w-4 h-4" />
                                                        </button>
                                                    )}
                                                    <button
                                                        onClick={() => handleDeleteReport(report.id)}
                                                        className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                                                        title="Delete Report"
                                                    >
                                                        <Trash2 className="w-4 h-4" />
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {/* Generate Report Modal */}
            {showGenerateModal && (
                <div
                    className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
                    onClick={() => !generating && setShowGenerateModal(false)}
                >
                    <div
                        className="bg-white rounded-2xl shadow-2xl max-w-lg w-full"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <div className="p-6 border-b border-gray-100">
                            <h2 className="text-xl font-bold text-gray-900">Generate New Report</h2>
                            <p className="text-sm text-gray-500 mt-1">
                                Create a patent analysis report on a specific topic
                            </p>
                        </div>

                        <form onSubmit={handleGenerateReport} className="p-6 space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Topic *
                                </label>
                                <input
                                    type="text"
                                    required
                                    placeholder="e.g., Machine Learning in Healthcare"
                                    value={newReport.topic}
                                    onChange={(e) => setNewReport(prev => ({ ...prev, topic: e.target.value }))}
                                    className="w-full px-4 py-2 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 transition-all outline-none"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Report Type
                                </label>
                                <select
                                    value={newReport.report_type}
                                    onChange={(e) => setNewReport(prev => ({ ...prev, report_type: e.target.value }))}
                                    className="w-full px-4 py-2 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 transition-all outline-none bg-white"
                                >
                                    <option value="comprehensive">Comprehensive Analysis</option>
                                    <option value="technical">Technical Review</option>
                                    <option value="market">Market Landscape</option>
                                    <option value="strategic">Strategic Insights</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Patent IDs (optional)
                                </label>
                                <input
                                    type="text"
                                    placeholder="e.g., 12345, 67890, 11111"
                                    value={newReport.patent_ids}
                                    onChange={(e) => setNewReport(prev => ({ ...prev, patent_ids: e.target.value }))}
                                    className="w-full px-4 py-2 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 transition-all outline-none"
                                />
                                <p className="text-xs text-gray-500 mt-1">
                                    Comma-separated list of patent IDs to include
                                </p>
                            </div>

                            <div className="flex gap-3 pt-4">
                                <button
                                    type="button"
                                    onClick={() => setShowGenerateModal(false)}
                                    disabled={generating}
                                    className="flex-1 px-4 py-2 border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors disabled:opacity-50"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    disabled={generating || !newReport.topic.trim()}
                                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                                >
                                    {generating ? (
                                        <>
                                            <Loader2 className="w-4 h-4 animate-spin" />
                                            Generating...
                                        </>
                                    ) : (
                                        'Generate Report'
                                    )}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Reports;
