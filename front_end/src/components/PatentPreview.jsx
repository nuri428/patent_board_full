import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';

function PatentPreview({ patent, onClose }) {
    const [loading, setLoading] = useState(false);
    const [patentDetails, setPatentDetails] = useState(null);
    const [error, setError] = useState(null);
    
    const { url, title, country, patent_id } = patent;
    
    useEffect(() => {
        // Fetch patent details when component mounts
        const fetchPatentDetails = async () => {
            try {
                setLoading(true);
                setError(null);
                
                // This would typically call your API to get patent details
                // For now, we'll simulate with a timeout
                await new Promise(resolve => setTimeout(resolve, 1000));
                
                // Mock patent details - in real implementation, fetch from API
                setPatentDetails({
                    title: title || `Patent ${country}-${patent_id}`,
                    abstract: 'This is a sample abstract for the patent. In a real implementation, this would be fetched from the patent database.',
                    inventors: ['John Doe', 'Jane Smith'],
                    assignee: 'Example Corp',
                    filing_date: '2023-01-15',
                    grant_date: '2024-06-20',
                    claims_count: 15,
                    ipc_classes: ['G06F 16/9535', 'G06F 40/30']
                });
                
            } catch (err) {
                setError('Failed to load patent details');
                console.error('Error fetching patent details:', err);
            } finally {
                setLoading(false);
            }
        };
        
        fetchPatentDetails();
    }, [country, patent_id, title]);
    
    const getCountryFlag = (countryCode) => {
        const countryFlags = {
            'US': '🇺🇸',
            'KR': '🇰🇷',
            'WO': '🌐',
            'EP': '🇪🇺',
            'JP': '🇯🇵',
            'CN': '🇨🇳',
            'default': '📄'
        };
        return countryFlags[countryCode?.toUpperCase()] || countryFlags.default;
    };

    if (loading) {
        return (
            <div className="patent-preview modal" style={{ display: 'block' }}>
                <div className="modal-dialog modal-lg">
                    <div className="modal-content">
                        <div className="modal-header">
                            <h5 className="modal-title">
                                <span className="me-2">{getCountryFlag(country)}</span>
                                {country}-{patent_id} Preview
                            </h5>
                            <button type="button" className="btn-close" onClick={onClose}></button>
                        </div>
                        <div className="modal-body text-center">
                            <div className="spinner-border text-primary" role="status">
                                <span className="visually-hidden">Loading...</span>
                            </div>
                            <p className="mt-3 text-muted">Loading patent details...</p>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="patent-preview modal" style={{ display: 'block' }}>
                <div className="modal-dialog modal-lg">
                    <div className="modal-content">
                        <div className="modal-header">
                            <h5 className="modal-title">
                                <span className="me-2">{getCountryFlag(country)}</span>
                                {country}-{patent_id} Preview
                            </h5>
                            <button type="button" className="btn-close" onClick={onClose}></button>
                        </div>
                        <div className="modal-body text-center">
                            <i className="bi bi-exclamation-triangle text-warning" style={{ fontSize: '2rem' }}></i>
                            <p className="mt-3 text-muted">{error}</p>
                            <button type="button" className="btn btn-primary" onClick={onClose}>
                                Close
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="patent-preview modal" style={{ display: 'block' }}>
            <div className="modal-dialog modal-lg">
                <div className="modal-content">
                    <div className="modal-header">
                        <h5 className="modal-title">
                            <span className="me-2">{getCountryFlag(country)}</span>
                            {country}-{patent_id} Preview
                        </h5>
                        <button type="button" className="btn-close" onClick={onClose}></button>
                    </div>
                    <div className="modal-body">
                        <div className="patent-preview-header">
                            <div className="d-flex justify-content-between align-items-start mb-3">
                                <div>
                                    <h6 className="mb-1">Patent Details</h6>
                                    <div className="text-muted small">
                                        {patentDetails?.assignee && (
                                            <span>Assignee: {patentDetails.assignee}</span>
                                        )}
                                    </div>
                                </div>
                                <div className="patent-actions">
                                    <a 
                                        href={url} 
                                        target="_blank" 
                                        rel="noopener noreferrer"
                                        className="btn btn-sm btn-outline-primary"
                                        title="View full patent in new tab"
                                    >
                                        <i className="bi bi-box-arrow-up-right me-1"></i>
                                        Full Patent
                                    </a>
                                </div>
                            </div>
                            
                            <div className="row mb-3">
                                <div className="col-md-6">
                                    <table className="table table-sm">
                                        <tbody>
                                            <tr>
                                                <td><strong>Inventors:</strong></td>
                                                <td>{patentDetails?.inventors?.join(', ') || 'N/A'}</td>
                                            </tr>
                                            <tr>
                                                <td><strong>Filing Date:</strong></td>
                                                <td>{patentDetails?.filing_date || 'N/A'}</td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                                <div className="col-md-6">
                                    <table className="table table-sm">
                                        <tbody>
                                            <tr>
                                                <td><strong>Grant Date:</strong></td>
                                                <td>{patentDetails?.grant_date || 'N/A'}</td>
                                            </tr>
                                            <tr>
                                                <td><strong>Claims:</strong></td>
                                                <td>{patentDetails?.claims_count || 'N/A'}</td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                            
                            {patentDetails?.ipc_classes && patentDetails.ipc_classes.length > 0 && (
                                <div className="mb-3">
                                    <strong className="text-muted small">IPC Classes:</strong>
                                    <div className="d-flex flex-wrap gap-1 mt-1">
                                        {patentDetails.ipc_classes.map((ipc, index) => (
                                            <span key={index} className="badge bg-light text-dark border">
                                                {ipc}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                        
                        <div className="patent-preview-content">
                            <h6 className="mb-2">Abstract</h6>
                            <div className="abstract-content bg-light p-3 rounded mb-3">
                                {patentDetails?.abstract || 'No abstract available.'}
                            </div>
                            
                            <h6 className="mb-2">Title</h6>
                            <div className="title-content bg-light p-3 rounded">
                                {patentDetails?.title || `Patent ${country}-${patent_id}`}
                            </div>
                        </div>
                    </div>
                    <div className="modal-footer">
                        <button type="button" className="btn btn-secondary" onClick={onClose}>
                            Close Preview
                        </button>
                        <a 
                            href={url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="btn btn-primary"
                        >
                            <i className="bi bi-box-arrow-up-right me-1"></i>
                            View Full Patent
                        </a>
                    </div>
                </div>
            </div>
        </div>
    );
}

PatentPreview.propTypes = {
    patent: PropTypes.shape({
        url: PropTypes.string.isRequired,
        title: PropTypes.string,
        country: PropTypes.string,
        patent_id: PropTypes.string.isRequired
    }).isRequired,
    onClose: PropTypes.func.isRequired
};

// Add backdrop styling
const style = document.createElement('style');
style.textContent = `
    .patent-preview {
        position: fixed;
        z-index: 1050;
        inset: 0;
        background-color: rgba(0, 0, 0, 0.5);
    }
    
    .patent-preview .modal-dialog {
        margin: 5% auto;
    }
    
    .patent-preview-header {
        border-bottom: 1px solid #dee2e6;
        padding-bottom: 1rem;
        margin-bottom: 1rem;
    }
    
    .patent-actions {
        text-align: right;
    }
    
    .abstract-content, .title-content {
        font-size: 0.95rem;
        line-height: 1.5;
    }
    
    .patent-preview-content h6 {
        color: #495057;
        font-weight: 600;
    }
`;
document.head.appendChild(style);

export default PatentPreview;