import React, { useState } from 'react';
import PropTypes from 'prop-types';

function SessionList({ 
    sessions, 
    currentSessionId, 
    onSelectSession, 
    onCreateSession, 
    onRefreshSessions,
    userId,
    isLoading = false 
}) {
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [newSessionTitle, setNewSessionTitle] = useState('');
    const [isCreating, setIsCreating] = useState(false);

    const formatDate = (dateString) => {
        if (!dateString) return 'Unknown date';
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    const handleCreateSession = async () => {
        if (!newSessionTitle.trim() || !userId) return;

        setIsCreating(true);
        try {
            await onCreateSession(userId, newSessionTitle.trim());
            setNewSessionTitle('');
            setShowCreateModal(false);
        } catch (error) {
            console.error('Failed to create session:', error);
        } finally {
            setIsCreating(false);
        }
    };

    const getSessionPreview = (session) => {
        if (!session.last_message) return 'No messages yet';
        
        const maxLength = 50;
        const message = session.last_message;
        const preview = message.length > maxLength 
            ? message.substring(0, maxLength) + '...' 
            : message;
        
        return `${message.role === 'user' ? 'You: ' : 'AI: '}${preview}`;
    };

    const getSessionStats = (session) => {
        const messageCount = session.message_count || 0;
        return `${messageCount} message${messageCount !== 1 ? 's' : ''}`;
    };

    return (
        <div className="session-list-container">
            {/* Header */}
            <div className="session-list-header d-flex justify-content-between align-items-center mb-3">
                <h5 className="mb-0">
                    <i className="bi bi-chat-dots me-2"></i>
                    Chat Sessions
                </h5>
                <div className="header-actions">
                    <button
                        className="btn btn-sm btn-outline-primary"
                        onClick={() => setShowCreateModal(true)}
                        disabled={isLoading}
                        title="Create new session"
                    >
                        <i className="bi bi-plus-circle me-1"></i>
                        New
                    </button>
                    
                    <button
                        className="btn btn-sm btn-outline-secondary ms-1"
                        onClick={onRefreshSessions}
                        disabled={isLoading}
                        title="Refresh sessions"
                    >
                        <i className="bi bi-arrow-clockwise me-1"></i>
                        Refresh
                    </button>
                </div>
            </div>

            {/* Sessions list */}
            <div className="sessions-list">
                {isLoading ? (
                    <div className="text-center py-4">
                        <div className="spinner-border text-primary" role="status">
                            <span className="visually-hidden">Loading...</span>
                        </div>
                        <p className="text-muted mt-2">Loading sessions...</p>
                    </div>
                ) : sessions.length === 0 ? (
                    <div className="text-center py-4">
                        <i className="bi bi-chat-square-text display-1 text-muted"></i>
                        <p className="text-muted mt-3">No chat sessions yet</p>
                        <button
                            className="btn btn-primary"
                            onClick={() => setShowCreateModal(true)}
                            title="Create your first chat session"
                        >
                            <i className="bi bi-plus-circle me-1"></i>
                            Start Chatting
                        </button>
                    </div>
                ) : (
                    <div className="list-group">
                        {sessions.map((session) => (
                            <div
                                key={session.id}
                                className={`list-group-item list-group-item-action ${
                                    session.id === currentSessionId ? 'active' : ''
                                }`}
                                onClick={() => onSelectSession(session.id)}
                            >
                                <div className="d-flex w-100 justify-content-between">
                                    <div className="session-info">
                                        <h6 className="mb-1">
                                            {session.title || `Chat Session ${session.id}`}
                                            {session.id === currentSessionId && (
                                                <span className="badge bg-primary ms-2">Active</span>
                                            )}
                                        </h6>
                                        <p className="mb-1 text-muted small">
                                            {getSessionPreview(session)}
                                        </p>
                                        <small className="text-muted">
                                            <i className="bi bi-calendar me-1"></i>
                                            {formatDate(session.created_at)}
                                            {session.updated_at && session.updated_at !== session.created_at && (
                                                <span className="ms-2">
                                                    <i className="bi bi-clock me-1"></i>
                                                    Updated {formatDate(session.updated_at)}
                                                </span>
                                            )}
                                        </small>
                                    </div>
                                    <div className="session-stats">
                                        <small className="text-muted">
                                            {getSessionStats(session)}
                                        </small>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Create session modal */}
            {showCreateModal && (
                <div className="modal fade show d-block" tabIndex="-1" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
                    <div className="modal-dialog">
                        <div className="modal-content">
                            <div className="modal-header">
                                <h5 className="modal-title">
                                    <i className="bi bi-plus-circle me-2"></i>
                                    New Chat Session
                                </h5>
                                <button
                                    type="button"
                                    className="btn-close"
                                    onClick={() => setShowCreateModal(false)}
                                ></button>
                            </div>
                            <div className="modal-body">
                                <div className="mb-3">
                                    <label htmlFor="sessionTitle" className="form-label">
                                        Session Title (Optional)
                                    </label>
                                    <input
                                        type="text"
                                        className="form-control"
                                        id="sessionTitle"
                                        placeholder="e.g., Patent Analysis - AI in Healthcare"
                                        value={newSessionTitle}
                                        onChange={(e) => setNewSessionTitle(e.target.value)}
                                        maxLength={100}
                                    />
                                    <div className="form-text">
                                        Leave blank for an auto-generated title
                                    </div>
                                </div>
                            </div>
                            <div className="modal-footer">
                                <button
                                    type="button"
                                    className="btn btn-secondary"
                                    onClick={() => setShowCreateModal(false)}
                                >
                                    Cancel
                                </button>
                                <button
                                    type="button"
                                    className="btn btn-primary"
                                    onClick={handleCreateSession}
                                    disabled={isCreating || !userId}
                                >
                                    {isCreating ? (
                                        <>
                                            <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                                            Creating...
                                        </>
                                    ) : (
                                        <>
                                            <i className="bi bi-plus-circle me-1"></i>
                                            Create Session
                                        </>
                                    )}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

SessionList.propTypes = {
    sessions: PropTypes.array.isRequired,
    currentSessionId: PropTypes.string,
    onSelectSession: PropTypes.func.isRequired,
    onCreateSession: PropTypes.func.isRequired,
    onRefreshSessions: PropTypes.func.isRequired,
    userId: PropTypes.string,
    isLoading: PropTypes.bool
};

export default SessionList;