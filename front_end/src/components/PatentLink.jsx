import React, { useState } from 'react';
import PropTypes from 'prop-types';
import PatentPreview from './PatentPreview';

function PatentLink({ patent, source, className = '' }) {
    const { url, title, country, patent_id } = patent;
    const [showPreview, setShowPreview] = useState(false);
    
    const getSourceIcon = (sourceName) => {
        const sourceIcons = {
            'google': '🔍',
            'uspto': '🇺🇸',
            'kipris': '🇰🇷',
            'wipo': '🌐',
            'patft': '📄',
            'default': '📄'
        };
        return sourceIcons[sourceName?.toLowerCase()] || sourceIcons.default;
    };

    const getSourceName = (sourceName) => {
        const sourceNames = {
            'google': 'Google Patents',
            'uspto': 'USPTO',
            'kipris': 'KIPRIS',
            'wipo': 'WIPO',
            'patft': 'USPTO Patent Database',
            'default': sourceName || 'Patent Database'
        };
        return sourceNames[sourceName?.toLowerCase()] || sourceNames.default;
    };

    const getCountryFlag = (countryCode) => {
        const countryFlags = {
            'US': '🇺🇸',
            'KR': '🇰🇷',
            'WO': '🌐',
            'EP': '🇪🇺',
            'JP': '🇯🇵',
            'CN': '🇨🇳',
            'CA': '🇨🇦',
            'AU': '🇦🇺',
            'DE': '🇩🇪',
            'FR': '🇫🇷',
            'GB': '🇬🇧',
            'IL': '🇮🇱',
            'RU': '🇷🇺',
            'default': '📄'
        };
        return countryFlags[countryCode?.toUpperCase()] || countryFlags.default;
    };

    const handleClick = (e) => {
        if (e) {
            e.preventDefault();
        }
        
        // Toggle preview modal
        setShowPreview(!showPreview);
        
        // Track click (if analytics is available)
        if (typeof window !== 'undefined' && window.gtag) {
            window.gtag('event', 'patent_link_click', {
                'event_category': 'engagement',
                'event_label': `${country}-${patent_id}`,
                'value': 1
            });
        }
    };

    const handleClosePreview = () => {
        setShowPreview(false);
    };

    return (
        <div className={`patent-link-container ${className}`}>
            <a
                href={url}
                onClick={handleClick}
                target="_blank"
                rel="noopener noreferrer"
                className="patent-link d-flex align-items-center p-2 mb-2 rounded hover-bg-light text-decoration-none"
                style={{
                    borderLeft: `4px solid ${getSourceColor(source)}`,
                    background: 'linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%)',
                    transition: 'all 0.2s ease'
                }}
                title={`View ${patent_id} in ${getSourceName(source)}`}
            >
                <div className="patent-link-icon me-3">
                    <span style={{ fontSize: '1.2rem' }}>
                        {getCountryFlag(country)} {getSourceIcon(source)}
                    </span>
                </div>
                
                <div className="patent-link-content flex-grow-1">
                    <div className="d-flex justify-content-between align-items-start">
                        <div>
                            <div className="patent-id fw-bold text-primary">
                                {country}-{patent_id}
                            </div>
                            <div className="patent-source text-muted small">
                                {getSourceName(source)}
                            </div>
                        </div>
                        
                        <div className="patent-link-actions">
                            <i className="bi bi-box-arrow-up-right text-muted ms-2"></i>
                        </div>
                    </div>
                    
                    {title && (
                        <div className="patent-title mt-1 text-muted small">
                            {title.length > 80 ? title.substring(0, 80) + '...' : title}
                        </div>
                    )}
                </div>
            </a>
            
            {/* Patent Preview Modal */}
            {showPreview && (
                <div className="patent-link-modal-overlay">
                    <PatentPreview 
                        patent={patent}
                        onClose={handleClosePreview}
                    />
                </div>
            )}
        </div>
    );
}

function getSourceColor(source) {
    const sourceColors = {
        'google': '#4285f4',
        'uspto': '#dc3912',
        'kipris': '#0066cc',
        'wipo': '#009639',
        'patft': '#ff6600',
        'default': '#6c757d'
    };
    return sourceColors[source?.toLowerCase()] || sourceColors.default;
}

// Add modal styling
const modalStyle = document.createElement('style');
modalStyle.textContent = `
    .patent-link-modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1050;
        padding: 20px;
    }
    
    .patent-link-modal-overlay .modal-content {
        max-width: 800px;
        max-height: 90vh;
        overflow-y: auto;
    }
    
    @media (max-width: 768px) {
        .patent-link-modal-overlay {
            padding: 10px;
        }
        
        .patent-link-modal-overlay .modal-content {
            max-width: 100%;
        }
    }
`;
document.head.appendChild(modalStyle);

PatentLink.propTypes = {
    patent: PropTypes.shape({
        url: PropTypes.string.isRequired,
        title: PropTypes.string,
        country: PropTypes.string,
        patent_id: PropTypes.string.isRequired
    }).isRequired,
    source: PropTypes.string,
    className: PropTypes.string
};

export default PatentLink;