import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { FileText, Database, Activity, Plus } from 'lucide-react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import StatCard from '../components/Dashboard/StatCard';
import RecentReports from '../components/Dashboard/RecentReports';
import api from '../api/axios';

const Dashboard = () => {
    const { user } = useAuth();
    const [stats, setStats] = useState({
        totalReports: 0,
        totalPatents: 0,
        credits: 0
    });
    const [recentReports, setRecentReports] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchDashboardData = async () => {
            try {
                // Fetch reports
                const reportsRes = await api.get('/reports/?skip=0&limit=5');
                const reports = reportsRes.data;
                setRecentReports(reports);

                // Fetch Stats (Mock for now or derive from reports/user)
                // If admin, we could fetch /admin/statistics
                // For now, let's derive from available data
                setStats({
                    totalReports: reports.length, // This should ideally be a count endpoint
                    totalPatents: 12503, // Mock global stat
                    credits: 500 // Mock credits
                });

                // If user is admin, try fetching real stats
                if (user?.is_admin) {
                    try {
                        const adminStats = await api.get('/admin/statistics');
                        setStats(prev => ({
                            ...prev,
                            totalPatents: adminStats.data.total_patents,
                            totalReports: adminStats.data.total_reports
                        }));
                    } catch (err) {
                        console.warn("Failed to fetch admin stats", err);
                    }
                }

            } catch (error) {
                console.error("Failed to fetch dashboard data", error);
            } finally {
                setLoading(false);
            }
        };

        if (user) {
            fetchDashboardData();
        }
    }, [user]);

    const statCards = [
        {
            title: 'Active Reports',
            value: stats.totalReports,
            icon: FileText,
            color: 'bg-blue-100',
            trend: 12
        },
        {
            title: 'Analyzed Patents',
            value: stats.totalPatents.toLocaleString(),
            icon: Database,
            color: 'bg-purple-100',
            trend: 5
        },
        {
            title: 'AI Credits',
            value: stats.credits,
            icon: Activity,
            color: 'bg-green-100',
            trend: 0
        },
    ];

    if (loading) {
        return <div className="flex h-screen items-center justify-center">Loading...</div>;
    }

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-gray-800">
                        Welcome back, {user?.full_name || user?.username}
                    </h1>
                    <p className="text-gray-500 mt-1">Here's what's happening with your projects today.</p>
                </div>
                <Link
                    to="/reports/new"
                    className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-2 rounded-lg font-medium shadow-md hover:shadow-lg transition-all flex items-center gap-2"
                >
                    <Plus className="w-5 h-5" /> New Report
                </Link>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {statCards.map((stat, index) => (
                    <motion.div
                        key={index}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                    >
                        <StatCard {...stat} />
                    </motion.div>
                ))}
            </div>

            {/* Main Content Area */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Recent Reports Section */}
                <div className="lg:col-span-2">
                    <RecentReports reports={recentReports} />
                </div>

                {/* Quick Actions / Side Panel */}
                <div className="space-y-6">
                    <div className="bg-gradient-to-br from-indigo-600 to-purple-700 rounded-xl p-6 text-white shadow-lg relative overflow-hidden">
                        <div className="relative z-10">
                            <h3 className="text-lg font-bold mb-2">Upgrade to Pro</h3>
                            <p className="text-indigo-100 text-sm mb-4">Get access to advanced patent analytics and unlimited reports.</p>
                            <button className="bg-white text-indigo-600 px-4 py-2 rounded-lg text-sm font-semibold hover:bg-gray-50 transition-colors">
                                Upgrade Plan
                            </button>
                        </div>
                        <div className="absolute right-[-20px] bottom-[-20px] opacity-20">
                            <Activity className="w-32 h-32" />
                        </div>
                    </div>

                    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                        <h3 className="font-semibold text-gray-800 mb-4">Quick Search</h3>
                        <div className="space-y-3">
                            <input
                                type="text"
                                placeholder="Search by patent ID or keyword..."
                                className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-sm"
                            />
                            <button className="w-full bg-gray-900 text-white py-2 rounded-lg text-sm font-medium hover:bg-gray-800 transition-colors">
                                Search
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
