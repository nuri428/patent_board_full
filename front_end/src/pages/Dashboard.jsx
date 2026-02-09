import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { FileText, Database, Activity, Plus, TrendingUp, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import StatCard from '../components/Dashboard/StatCard';
import RecentReports from '../components/Dashboard/RecentReports';
import api from '../api/axios';

const Dashboard = () => {
    const { user } = useAuth();
    const [stats, setStats] = useState({
        totalReports: 0,
        krPatents: 0,
        usPatents: 0,
        credits: 0
    });
    const [recentReports, setRecentReports] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchDashboardData = async () => {
            try {
                // Fetch reports and stats concurrently
                const [reportsRes, statsRes] = await Promise.all([
                    api.get('/reports/?skip=0&limit=5'),
                    api.get('/patents/statistics')
                ]);

                const reports = reportsRes.data;
                const patentStats = statsRes.data;

                setRecentReports(reports);
                setStats({
                    totalReports: reports.length,
                    krPatents: patentStats.kr_total,
                    usPatents: patentStats.us_total,
                    credits: 500
                });

                if (user?.is_admin) {
                    try {
                        const adminStats = await api.get('/admin/statistics');
                        setStats(prev => ({
                            ...prev,
                            // If admin stats are more comprehensive, we can use them
                            // but for now we prioritize the specific KR/US counts
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
            color: 'bg-indigo-50 text-indigo-600',
            trend: 0
        },
        {
            title: 'KR Patents',
            value: stats.krPatents.toLocaleString(),
            icon: Database,
            color: 'bg-emerald-50 text-emerald-600',
            trend: 0
        },
        {
            title: 'US Patents',
            value: stats.usPatents.toLocaleString(),
            icon: Database,
            color: 'bg-blue-50 text-blue-600',
            trend: 0
        },
        {
            title: 'AI Credits',
            value: stats.credits,
            icon: Activity,
            color: 'bg-amber-50 text-amber-600',
            trend: 0
        },
    ];

    if (loading) {
        return (
            <div className="flex h-[60vh] items-center justify-center">
                <div className="text-center">
                    <div className="spinner-border text-indigo-600" role="status">
                        <span className="visually-hidden">Loading...</span>
                    </div>
                    <p className="mt-4 text-slate-500 font-medium">Syncing with patent intelligence...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-[1600px] mx-auto space-y-10 p-2 md:p-6">
            {/* Header */}
            <header className="flex flex-col md:row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-slate-900 tracking-tight">
                        Intel Intelligence Dashboard
                    </h1>
                    <p className="text-slate-500 mt-1 flex items-center gap-2">
                        Welcome back, <span className="font-semibold text-indigo-600">{user?.full_name || user?.username}</span>
                        <span className="h-1 w-1 rounded-full bg-slate-300"></span>
                        Last updated: {new Date().toLocaleDateString()}
                    </p>
                </div>
                <div className="flex items-center gap-3">
                    <Link
                        to="/reports/new"
                        className="premium-button-primary flex items-center gap-2"
                    >
                        <Plus className="w-5 h-5" /> New Analysis
                    </Link>
                </div>
            </header>

            {/* Stats Grid */}
            <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                {statCards.map((stat, index) => (
                    <motion.div
                        key={index}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="premium-card p-6"
                    >
                        <div className="flex justify-between items-start mb-4">
                            <div className={`${stat.color} p-3 rounded-xl`}>
                                <stat.icon className="w-6 h-6" />
                            </div>
                            {stat.trend > 0 && (
                                <span className="flex items-center gap-1 text-xs font-bold text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-100">
                                    <TrendingUp className="w-3 h-3" /> +{stat.trend}%
                                </span>
                            )}
                        </div>
                        <h3 className="text-slate-500 text-sm font-medium mb-1">{stat.title}</h3>
                        <div className="text-3xl font-bold text-slate-900 tracking-tight">{stat.value}</div>
                    </motion.div>
                ))}
            </section>

            {/* Main Content Area */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
                {/* Recent Reports Section */}
                <section className="lg:col-span-8 space-y-6">
                    <div className="flex justify-between items-center">
                        <h2 className="text-xl font-bold text-slate-900">Recent Investigations</h2>
                        <Link to="/reports" className="text-indigo-600 text-sm font-semibold flex items-center gap-1 hover:underline">
                            View All <ArrowRight className="w-4 h-4" />
                        </Link>
                    </div>
                    <div className="premium-card overflow-hidden">
                        <RecentReports reports={recentReports} />
                    </div>
                </section>

                {/* Side Panel */}
                <aside className="lg:col-span-4 space-y-8">
                    {/* Pro Callout */}
                    <div className="bg-slate-900 rounded-3xl p-8 text-white shadow-2xl relative overflow-hidden group">
                        <div className="relative z-10">
                            <h3 className="text-2xl font-bold mb-3 tracking-tight">Expand Your <br />Reach with Pro</h3>
                            <p className="text-slate-400 text-sm mb-6 leading-relaxed">Unlock advanced patent landscaping and real-time competitor tracking alerts.</p>
                            <button className="bg-white text-slate-900 w-full py-4 rounded-xl font-bold hover:bg-slate-50 transition-colors shadow-lg shadow-white/10">
                                Upgrade Workspace
                            </button>
                        </div>
                        <div className="absolute top-[-20%] right-[-10%] opacity-10 blur-3xl w-48 h-48 bg-indigo-500 rounded-full group-hover:bg-indigo-400 transition-colors duration-500"></div>
                    </div>

                    {/* Quick Search Card */}
                    <div className="premium-card p-8">
                        <h3 className="font-bold text-slate-900 text-lg mb-6">Omni-Search</h3>
                        <div className="space-y-4">
                            <div className="relative">
                                <input
                                    type="text"
                                    placeholder="Patent ID, Keyword, or IPC..."
                                    className="w-full pl-4 pr-4 py-4 bg-white border border-slate-200 rounded-2xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none text-sm transition-all text-slate-900"
                                />
                            </div>
                            <button className="w-full bg-slate-950 text-white py-4 rounded-2xl font-bold hover:bg-slate-900 transition-all shadow-xl shadow-slate-200 active:scale-95">
                                Pulse Search
                            </button>
                        </div>
                        <div className="mt-6 flex flex-wrap gap-2">
                            <span className="text-[10px] uppercase tracking-wider font-bold text-slate-400">Trending</span>
                            <span className="text-[10px] font-bold bg-indigo-50 text-indigo-600 px-2 py-1 rounded">Semiconductor</span>
                            <span className="text-[10px] font-bold bg-indigo-50 text-indigo-600 px-2 py-1 rounded">AR/VR</span>
                        </div>
                    </div>
                </aside>
            </div>
        </div>
    );
};

export default Dashboard;
