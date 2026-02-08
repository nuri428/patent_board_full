import React, { useState, useRef, useEffect } from 'react';
import PropTypes from 'prop-types';
import { Send, X, Keyboard, Sparkles, Lightbulb, BarChart3, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

function ChatInput({ onSendMessage, disabled = false, placeholder = 'Search patent intelligence...' }) {
    const [message, setMessage] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const inputRef = useRef(null);

    useEffect(() => {
        if (inputRef.current && !disabled) {
            inputRef.current.focus();
        }
    }, [disabled]);

    const handleInputChange = (e) => {
        setMessage(e.target.value);
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const handleSend = async () => {
        if (!message.trim() || disabled) return;

        const messageToSend = message.trim();
        setMessage('');
        setIsTyping(true);

        try {
            await onSendMessage(messageToSend);
        } catch (error) {
            console.error('Failed to send message:', error);
        } finally {
            setIsTyping(false);
        }
    };

    const handleClear = () => {
        setMessage('');
        inputRef.current?.focus();
    };

    const isSendDisabled = !message.trim() || disabled || isTyping;

    const quickPrompts = [
        { label: 'Deep Analysis', icon: Sparkles, text: 'Perform a deep analysis of the current patent landscape for Generative AI.' },
        { label: 'Top Competitors', icon: Lightbulb, text: 'Identify the top 5 competitors based on recent patent filings in the EV sector.' },
        { label: 'Technology Gap', icon: BarChart3, text: 'Show me any technology white spaces in the solid-state battery domain.' }
    ];

    return (
        <div className="chat-input-container">
            {/* Quick Prompts Bar */}
            <div className="flex gap-2 overflow-x-auto no-scrollbar pb-4 mb-2">
                {quickPrompts.map((prompt, idx) => (
                    <button
                        key={idx}
                        onClick={() => !disabled && onSendMessage(prompt.text)}
                        disabled={disabled || isTyping}
                        className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-50 border border-slate-200 text-[11px] font-bold text-slate-500 whitespace-nowrap hover:bg-white hover:border-indigo-200 hover:text-indigo-600 transition-all active:scale-95"
                    >
                        <prompt.icon size={12} strokeWidth={2.5} />
                        {prompt.label}
                    </button>
                ))}
            </div>

            <div className="input-wrapper group shadow-sm">
                <input
                    ref={inputRef}
                    type="text"
                    className="form-control"
                    placeholder={placeholder}
                    value={message}
                    onChange={handleInputChange}
                    onKeyDown={handleKeyDown}
                    disabled={disabled || isTyping}
                    aria-label="Chat message input"
                />

                <div className="flex items-center gap-2 pr-2">
                    <AnimatePresence>
                        {message && (
                            <motion.button
                                initial={{ opacity: 0, scale: 0.8 }}
                                animate={{ opacity: 1, scale: 1 }}
                                exit={{ opacity: 0, scale: 0.8 }}
                                onClick={handleClear}
                                className="p-2 text-slate-400 hover:text-slate-600 transition-colors"
                                type="button"
                            >
                                <X size={18} />
                            </motion.button>
                        )}
                    </AnimatePresence>

                    <button
                        className="btn-send disabled:opacity-50 disabled:cursor-not-allowed"
                        type="button"
                        onClick={handleSend}
                        disabled={isSendDisabled}
                    >
                        {isTyping ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
                    </button>
                </div>
            </div>

            <div className="mt-4 flex items-center justify-between">
                <div className="flex items-center gap-1.5 opacity-40">
                    <Keyboard size={12} />
                    <span className="text-[10px] font-bold uppercase tracking-widest">Enter to analyze pulse</span>
                </div>
                <div className="text-[10px] font-bold text-slate-300">
                    Powered by PatentBoard Multi-Agent v2
                </div>
            </div>
        </div>
    );
}

ChatInput.propTypes = {
    onSendMessage: PropTypes.func.isRequired,
    disabled: PropTypes.bool,
    placeholder: PropTypes.string
};

export default ChatInput;