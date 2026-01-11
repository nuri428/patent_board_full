import React from 'react';
import { FileText, ArrowRight, Clock } from 'lucide-react';
import { Link } from 'react-router-dom';

const RecentReports = ({ reports }) => {
    const getStatusColor = (status) => {
        switch (status) {
            case 'completed': return 'bg-green-100 text-green-700';
            case 'generating': return 'bg-blue-100 text-blue-700';
            case 'failed': return 'bg-red-100 text-red-700';
            default: return 'bg-gray-100 text-gray-700';
        }
    };

    if (!reports || !Array.isArray(reports) || reports.length === 0) {
        return (
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8 flex flex-col items-center justify-center text-center">
                <div className="bg-gray-50 p-4 rounded-full mb-4">
                    <FileText className="w-8 h-8 text-gray-400" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-1">No reports yet</h3>
                <p className="text-gray-500 mb-6 max-w-sm">Create your first patent analysis report to see it here.</p>
                <Link
                    to="/reports/new"
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
                >
                    Create Report
                </Link>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
                <h3 className="font-semibold text-gray-800">Recent Reports</h3>
                <Link to="/reports" className="text-blue-600 hover:text-blue-700 text-sm font-medium flex items-center gap-1">
                    View all <ArrowRight className="w-4 h-4" />
                </Link>
            </div>
            <div className="divide-y divide-gray-100">
                {reports.map((report) => (
                    <div key={report.id} className="p-4 hover:bg-gray-50 transition-colors group">
                        <div className="flex items-center justify-between">
                            <div className="flex items-start gap-3">
                                <div className={`p-2 rounded-lg ${getStatusColor(report.status)} bg-opacity-20`}>
                                    <FileText className="w-5 h-5" />
                                </div>
                                <div>
                                    <h4 className="font-medium text-gray-900 group-hover:text-blue-600 transition-colors">
                                        {report.title}
                                    </h4>
                                    <div className="flex items-center gap-3 text-xs text-gray-500 mt-1">
                                        <span className="flex items-center gap-1">
                                            <Clock className="w-3 h-3" />
                                            {new Date(report.created_at).toLocaleDateString()}
                                        </span>
                                        <span>•</span>
                                        <span className="capitalize">{report.report_type}</span>
                                    </div>
                                </div>
                            </div>
                            <div className="flex items-center gap-3">
                                <span className={`px-2.5 py-1 rounded-full text-xs font-medium capitalize ${getStatusColor(report.status)}`}>
                                    {report.status}
                                </span>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default RecentReports;
