import React from 'react';
import PropTypes from 'prop-types';
import { motion } from 'framer-motion';

function LandingPage({ onGetStarted }) {
    return (
        <div className="min-h-screen bg-slate-50 text-slate-900 selection:bg-indigo-100 selection:text-indigo-900">
            {/* Navigation */}
            <nav className="fixed top-0 w-full z-50 glass-morphism py-4">
                <div className="max-w-7xl mx-auto px-4 flex justify-between items-center">
                    <div className="flex items-center gap-2">
                        <div className="bg-indigo-600 p-2 rounded-lg">
                            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                        </div>
                        <span className="text-xl font-bold tracking-tight text-slate-900">Patent Board</span>
                    </div>
                    <div className="hidden md:flex items-center gap-8">
                        <a href="#features" className="text-sm font-medium text-slate-600 hover:text-indigo-600 transition-colors">Features</a>
                        <a href="#how-it-works" className="text-sm font-medium text-slate-600 hover:text-indigo-600 transition-colors">How it works</a>
                        <button onClick={onGetStarted} className="premium-button-primary text-sm">Get Started</button>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <section className="relative pt-32 pb-20 lg:pt-48 lg:pb-32 overflow-hidden">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
                    <div className="text-center">
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.5 }}
                        >
                            <span className="inline-flex items-center px-4 py-1.5 rounded-full text-sm font-medium bg-indigo-50 text-indigo-700 border border-indigo-100 mb-6">
                                <span className="flex h-2 w-2 rounded-full bg-indigo-600 mr-2 animate-pulse"></span>
                                AI-Powered Patent Intelligence
                            </span>
                        </motion.div>

                        <motion.h1
                            className="text-5xl md:text-7xl font-bold text-slate-900 mb-8 tracking-tight"
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.5, delay: 0.1 }}
                        >
                            The Next Era of <br />
                            <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-violet-600">Patent Analysis</span>
                        </motion.h1>

                        <motion.p
                            className="text-xl md:text-2xl text-slate-600 mb-10 max-w-3xl mx-auto leading-relaxed"
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.5, delay: 0.2 }}
                        >
                            Elevate your intellectual property strategy with our multi-agent AI system.
                            From intelligent chat to node-network analysis, all in one premium workspace.
                        </motion.p>

                        <motion.div
                            className="flex flex-col sm:flex-row gap-4 justify-center"
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.5, delay: 0.3 }}
                        >
                            <button
                                onClick={onGetStarted}
                                className="premium-button-primary text-lg px-10 py-4"
                            >
                                Start Analysis Free
                            </button>
                            <button
                                onClick={() => window.scrollTo({ top: document.getElementById('features')?.offsetTop || 0, behavior: 'smooth' })}
                                className="bg-white text-slate-900 border border-slate-200 px-10 py-4 rounded-xl text-lg font-semibold hover:bg-slate-50 transition-all duration-200 shadow-sm"
                            >
                                Explorer Features
                            </button>
                        </motion.div>
                    </div>
                </div>

                {/* Background Blobs */}
                <div className="absolute top-0 inset-x-0 h-full -z-10">
                    <div className="absolute top-1/4 -right-20 w-96 h-96 bg-indigo-200/30 rounded-full blur-3xl animate-blob"></div>
                    <div className="absolute bottom-1/4 -left-20 w-96 h-96 bg-purple-200/30 rounded-full blur-3xl animate-blob animation-delay-2000"></div>
                </div>
            </section>

            {/* Features Section */}
            <section id="features" className="py-24 bg-white">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="text-center mb-20">
                        <h2 className="text-3xl md:text-5xl font-bold text-slate-900 mb-6">
                            Professional Features for Experts
                        </h2>
                        <div className="w-20 h-1.5 bg-indigo-600 mx-auto rounded-full mb-6"></div>
                        <p className="text-xl text-slate-600 max-w-3xl mx-auto">
                            Advanced AI tools designed to simplify the most complex patent research tasks.
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                        <FeatureCard
                            icon={<ChatIcon />}
                            title="Contextual AI Chat"
                            description="Engage with a specialized AI agent that understands patent law and technical hierarchies, providing cited references from global databases."
                        />
                        <FeatureCard
                            icon={<GraphIcon />}
                            title="Graph Network Analysis"
                            description="Visualize competitor landscapes and patent citations through interactive node-network graphs powered by Neo4j."
                        />
                        <FeatureCard
                            icon={<ReportIcon />}
                            title="Automated Reporting"
                            description="Generate comprehensive professional reports with technical assessment, market trends, and risk analysis in seconds."
                        />
                        <FeatureCard
                            icon={<AgentIcon />}
                            title="Multi-Agent Workflows"
                            description="Leverage LangGraph to orchestrate multiple specialized agents working in parallel to verify data and refine insights."
                        />
                        <FeatureCard
                            icon={<DbIcon />}
                            title="Unified Data Hub"
                            description="Direct access to synchronized MariaDB, OpenSearch, and Neo4j architectures for unmatched search speed and depth."
                        />
                        <FeatureCard
                            icon={<RealtimeIcon />}
                            title="Real-time Insights"
                            description="Experience lightning-fast processing with intelligent caching and asynchronous AI execution for instant decision support."
                        />
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="py-24 bg-slate-900 overflow-hidden relative">
                <div className="max-w-4xl mx-auto px-4 text-center relative z-10">
                    <h2 className="text-4xl md:text-5xl font-bold text-white mb-8">
                        Transform Your Research Workflow Today.
                    </h2>
                    <p className="text-xl text-slate-400 mb-12 max-w-2xl mx-auto">
                        Join patent attorneys and R&D managers who use Patent Board to stay ahead of the curve.
                    </p>

                    <button
                        onClick={onGetStarted}
                        className="bg-white text-slate-900 px-10 py-5 rounded-2xl text-xl font-bold shadow-2xl hover:bg-slate-50 transform hover:scale-105 transition-all duration-200"
                    >
                        Create Your Free Account
                    </button>
                </div>
                {/* Visual decoration for CTA */}
                <div className="absolute top-0 right-0 -mr-20 -mt-20 w-80 h-80 bg-indigo-500/10 rounded-full blur-3xl"></div>
                <div className="absolute bottom-0 left-0 -ml-20 -mb-20 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl"></div>
            </section>

            {/* Footer */}
            <footer className="py-12 bg-slate-50 border-t border-slate-200">
                <div className="max-w-7xl mx-auto px-4 flex flex-col md:row justify-between items-center gap-6">
                    <div className="flex items-center gap-2">
                        <span className="text-xl font-bold text-slate-900">Patent Board</span>
                    </div>
                    <p className="text-slate-500 text-sm italic">
                        © 2026 Patent Board AI. Precision. Speed. Intelligence.
                    </p>
                </div>
            </footer>
        </div>
    );
}

// Icons
const ChatIcon = () => (
    <div className="w-12 h-12 bg-indigo-50 rounded-xl flex items-center justify-center text-indigo-600">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-6 h-6"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" /></svg>
    </div>
);
const GraphIcon = () => (
    <div className="w-12 h-12 bg-purple-50 rounded-xl flex items-center justify-center text-purple-600">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-6 h-6"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" /></svg>
    </div>
);
const ReportIcon = () => (
    <div className="w-12 h-12 bg-emerald-50 rounded-xl flex items-center justify-center text-emerald-600">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-6 h-6"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
    </div>
);
const AgentIcon = () => (
    <div className="w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center text-blue-600">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-6 h-6"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.183.319l-3.077 1.913A1 1 0 002.5 19h15a1 1 0 00.992-.883l.936-12a1 1 0 00-1.874-.43L19.428 15.428z" /></svg>
    </div>
);
const DbIcon = () => (
    <div className="w-12 h-12 bg-rose-50 rounded-xl flex items-center justify-center text-rose-600">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-6 h-6"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" /></svg>
    </div>
);
const RealtimeIcon = () => (
    <div className="w-12 h-12 bg-amber-50 rounded-xl flex items-center justify-center text-amber-600">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-6 h-6"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
    </div>
);

// Feature Card Component
function FeatureCard({ icon, title, description }) {
    return (
        <motion.div
            className="premium-card p-10 group"
            whileHover={{ y: -5 }}
        >
            <div className="mb-6 group-hover:scale-110 transition-transform duration-300 origin-left">{icon}</div>
            <h3 className="text-2xl font-bold text-slate-900 mb-4 tracking-tight">{title}</h3>
            <p className="text-slate-600 leading-relaxed text-lg">{description}</p>
        </motion.div>
    );
}

LandingPage.propTypes = {
    onGetStarted: PropTypes.func.isRequired
};

export default LandingPage;