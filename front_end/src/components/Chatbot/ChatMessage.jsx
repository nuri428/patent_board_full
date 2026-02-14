import React from 'react';
import PropTypes from 'prop-types';
import { motion } from 'framer-motion';
import { User, Bot, Clock, Paperclip, ChevronRight, AlertTriangle, Loader2 } from 'lucide-react';
import PatentLink from '../PatentLink';

function ChatMessage({ message, isStreaming = false }) {
    const { content, role, timestamp, pending = false, error = false, sources = [], metadata = {}, patent_urls = [] } = message;

    const formatTime = (timestampString) => {
        if (!timestampString) return '';
        const date = new Date(timestampString);
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    const isUser = role === 'user';

    const getSourceIcon = (type) => {
        switch (type) {
            case 'patent': return '📄';
            case 'document': return '📄';
            case 'analysis': return '🔍';
            default: return '📚';
        }
    };

    const StreamingCursor = () => (
        <motion.span
            animate={{ opacity: [0.4, 1, 0.4] }}
            transition={{ repeat: Infinity, duration: 1, ease: "easeInOut" }}
            className="inline-block w-0.5 h-4.5 bg-indigo-600 rounded-sm ml-1 align-middle"
            aria-label="AI is typing"
        />
    );

    return (
        <div className={`chat-message ${isUser ? 'user-message' : 'assistant-message'} ${pending ? 'pending' : ''} ${error ? 'error' : ''}`}>
            <div className="message-container group shadow-sm hover:shadow-md transition-shadow duration-300">
                <div className={`message-header flex items-center justify-between px-4 py-2 opacity-50 text-[10px] uppercase font-black tracking-widest border-b ${isUser ? 'border-white/10' : 'border-slate-100'}`}>
                    <div className="flex items-center gap-1.5">
                        {isUser ? <User size={10} strokeWidth={3} /> : <Bot size={10} strokeWidth={3} />}
                        <span>{isUser ? 'Strategy Explorer' : 'AI Analysis Logic'}</span>
                    </div>
                    {timestamp && (
                        <div className="flex items-center gap-1">
                            <Clock size={10} />
                            <span>{formatTime(timestamp)}</span>
                        </div>
                    )}
                </div>

                <div className="message-body p-4 md:p-5">
                    {error ? (
                        <div className="flex items-start gap-2 text-rose-500 font-bold">
                            <AlertTriangle size={16} className="mt-0.5" />
                            <p className="text-sm">{content}</p>
                        </div>
                    ) : (
                        <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: isStreaming ? 0.8 : 1, y: 0 }}
                            transition={{ duration: 0.2 }}
                            className="chat-message-content prose prose-sm max-w-none prose-slate"
                        >
                            <p className="whitespace-pre-wrap leading-relaxed text-[0.9375rem]">
                                {content}
                                {isStreaming && !isUser && <StreamingCursor />}
                            </p>

                            {patent_urls && patent_urls.length > 0 && (
                                <div className="patent-urls-container mt-6 pt-4 border-t border-slate-100">
                                    <div className="flex items-center gap-2 mb-3">
                                        <div className="w-1.5 h-4 bg-indigo-600 rounded-full"></div>
                                        <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Linked Intelligence ({patent_urls.length})</span>
                                    </div>
                                    <div className="grid gap-2">
                                        {patent_urls.map((url_info, index) => (
                                            <PatentLink
                                                key={index}
                                                patent={{
                                                    url: url_info.url,
                                                    title: url_info.title,
                                                    country: url_info.country,
                                                    patent_id: url_info.patent_id
                                                }}
                                                source={url_info.source}
                                                className="hover:scale-[1.01] transition-transform"
                                            />
                                        ))}
                                    </div>
                                </div>
                            )}

                            {sources && sources.length > 0 && (
                                <div className="sources-container mt-4 flex flex-wrap gap-1.5">
                                    {sources.map((source, index) => (
                                        <span
                                            key={index}
                                            className="sources-badges badge flex items-center gap-1.5 px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-[10px] font-bold text-slate-600 hover:bg-white hover:border-indigo-200 transition-all cursor-pointer"
                                            title={source.title || source.name}
                                        >
                                            <span className="opacity-70">{getSourceIcon(source.type)}</span>
                                            {source.title?.substring(0, 15)}{source.title?.length > 15 ? '...' : ''}
                                            <ChevronRight size={10} className="text-slate-300" />
                                        </span>
                                    ))}
                                </div>
                            )}

                            {Object.keys(metadata).length > 0 && (
                                <div className="metadata-container mt-4 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <details className="cursor-pointer">
                                        <summary className="text-[10px] font-black text-indigo-400 uppercase tracking-widest hover:text-indigo-600 list-none flex items-center gap-1">
                                            <ChevronRight size={10} className="transform group-open:rotate-90 transition-transform" />
                                            Technical Metadata
                                        </summary>
                                        <pre className="text-[10px] bg-slate-50 p-3 rounded-xl border border-slate-100 mt-2 font-mono overflow-x-auto text-slate-500">
                                            {JSON.stringify(metadata, null, 2)}
                                        </pre>
                                    </details>
                                </div>
                            )}
                        </div>
                    )}

                    {pending && (
                        <div className="message-pending mt-4">
                            <div className="typing-indicator flex gap-1.5">
                                <motion.span animate={{ y: [0, -4, 0] }} transition={{ repeat: Infinity, duration: 0.6, delay: 0 }} className="w-1.5 h-1.5 bg-indigo-600 rounded-full" />
                                <motion.span animate={{ y: [0, -4, 0] }} transition={{ repeat: Infinity, duration: 0.6, delay: 0.2 }} className="w-1.5 h-1.5 bg-indigo-600 rounded-full" />
                                <motion.span animate={{ y: [0, -4, 0] }} transition={{ repeat: Infinity, duration: 0.6, delay: 0.4 }} className="w-1.5 h-1.5 bg-indigo-600 rounded-full" />
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

ChatMessage.propTypes = {
    message: PropTypes.shape({
        id: PropTypes.string.isRequired,
        content: PropTypes.string.isRequired,
        role: PropTypes.oneOf(['user', 'assistant']).isRequired,
        timestamp: PropTypes.string,
        pending: PropTypes.bool,
        error: PropTypes.bool,
        sources: PropTypes.array,
        metadata: PropTypes.object,
        patent_urls: PropTypes.arrayOf(
            PropTypes.shape({
                url: PropTypes.string.isRequired,
                title: PropTypes.string,
                source: PropTypes.string,
                country: PropTypes.string,
                patent_id: PropTypes.string.isRequired
            })
        )
    }).isRequired,
    isStreaming: PropTypes.bool
};

export default ChatMessage;