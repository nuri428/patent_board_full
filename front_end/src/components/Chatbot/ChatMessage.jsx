import React from 'react';
import PropTypes from 'prop-types';
import PatentLink from '../PatentLink';

function ChatMessage({ message }) {
    const { content, role, timestamp, pending = false, error = false, sources = [], metadata = {}, patent_urls = [] } = message;

    const formatTime = (timestampString) => {
        if (!timestampString) return '';
        const date = new Date(timestampString);
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    const isUser = role === 'user';
    const isAssistant = role === 'assistant';

    const getSourceBadge = (source) => {
        if (!source) return null;
        
        const getIcon = (type) => {
            switch (type) {
                case 'patent': return '📄';
                case 'document': return '📄';
                case 'analysis': return '🔍';
                default: return '📚';
            }
        };

        return (
            <span 
                className="badge bg-light text-dark me-1 mb-1"
                style={{ fontSize: '0.75rem' }}
                title={source.title || source.name}
            >
                {getIcon(source.type)} {source.title?.substring(0, 20)}{source.title?.length > 20 ? '...' : ''}
            </span>
        );
    };

    const renderContent = () => {
        if (error) {
            return (
                <div className="text-danger">
                    <i className="bi bi-exclamation-triangle-fill me-2"></i>
                    {content}
                </div>
            );
        }

        return (
            <div className="chat-message-content">
                <p className="mb-0">{content}</p>
                
                {patent_urls && patent_urls.length > 0 && (
                    <div className="patent-urls-container mt-3 mb-2">
                        <div className="d-flex align-items-center mb-2">
                            <i className="bi bi-file-earmark-text text-primary me-2"></i>
                            <small className="text-muted fw-bold">
                                Related Patent Links ({patent_urls.length}):
                            </small>
                        </div>
                        <div className="patent-links">
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
                                    className="mb-2"
                                />
                            ))}
                        </div>
                    </div>
                )}
                
                {/* Sources section */}
                {sources && sources.length > 0 && (
                    <div className="sources-container mt-2">
                        <small className="text-muted">
                            <i className="bi bi-info-circle me-1"></i>
                            Sources:
                        </small>
                        <div className="sources-badges mt-1">
                            {sources.map((source, index) => (
                                <React.Fragment key={index}>
                                    {getSourceBadge(source)}
                                </React.Fragment>
                            ))}
                        </div>
                    </div>
                )}

                {/* Metadata section */}
                {Object.keys(metadata).length > 0 && (
                    <div className="metadata-container mt-2">
                        <small className="text-muted">Metadata:</small>
                        <pre className="small bg-light p-2 rounded mt-1">
                            {JSON.stringify(metadata, null, 2)}
                        </pre>
                    </div>
                )}
            </div>
        );
    };

    return (
        <div className={`chat-message ${isUser ? 'user-message' : 'assistant-message'} ${pending ? 'pending' : ''} ${error ? 'error' : ''}`}>
            <div className="message-container">
                <div className="message-header">
                    <div className="d-flex justify-content-between align-items-center">
                        <div className="message-role">
                            {isUser ? (
                                <span className="badge bg-primary">
                                    <i className="bi bi-person me-1"></i>You
                                </span>
                            ) : (
                                <span className="badge bg-success">
                                    <i className="bi bi-robot me-1"></i>Assistant
                                </span>
                            )}
                        </div>
                        <div className="message-timestamp">
                            <small className="text-muted">{formatTime(timestamp)}</small>
                        </div>
                    </div>
                </div>
                
                <div className="message-body">
                    {renderContent()}
                    
                    {pending && (
                        <div className="message-pending">
                            <div className="typing-indicator">
                                <span className="dot"></span>
                                <span className="dot"></span>
                                <span className="dot"></span>
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
    }).isRequired
};

export default ChatMessage;