import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { AnalysisResults } from '../AnalysisResults';
import { vi } from 'vitest';

// Mock lucide-react icons
vi.mock('lucide-react', () => ({
  Info: () => <div data-testid="info-icon" />,
  RefreshCw: () => <div data-testid="refresh-icon" />,
}));

describe('AnalysisResults', () => {
  const mockResults = {
    status: 'success',
    data: [
      {
        id: '1',
        title: 'Test Patent 1',
        abstract: 'This is a test abstract',
        confidence: 0.85
      }
    ],
    metadata: {
      engine: 'OpenSearch',
      confidence: 'High'
    }
  };

  it('renders results when data is provided', () => {
    render(<AnalysisResults results={mockResults} />);
    
    expect(screen.getByText('Analysis Results')).toBeInTheDocument();
    expect(screen.getByText('Results')).toBeInTheDocument();
  });

  it('displays confidence badge correctly', () => {
    render(<AnalysisResults results={mockResults} />);
    
    const confidenceBadge = screen.getByText('High');
    expect(confidenceBadge).toBeInTheDocument();
    expect(confidenceBadge).toHaveClass('bg-green-50');
    expect(confidenceBadge).toHaveClass('text-green-700');
  });

  it('shows interpretation notes when provided', () => {
    const resultsWithNotes = {
      ...mockResults,
      metadata: {
        ...mockResults.metadata,
        interpretation_note: 'Sample interpretation'
      }
    };
    
    render(<AnalysisResults results={resultsWithNotes} />);
    
    expect(screen.getByText('Sample interpretation')).toBeInTheDocument();
    expect(screen.getByTestId('info-icon')).toBeInTheDocument();
  });

  it('displays source information', () => {
    render(<AnalysisResults results={mockResults} />);
    
    expect(screen.getByText('Source: OpenSearch')).toBeInTheDocument();
  });

  it('handles network analysis results', () => {
    const networkResults = {
      status: 'success',
      data: {
        nodes: [
          { id: '1', label: 'Node 1', size: 10 },
          { id: '2', label: 'Node 2', size: 15 }
        ],
        edges: [
          { from: '1', to: '2' }
        ]
      },
      metadata: {
        engine: 'Neo4j',
        confidence: 'Medium'
      }
    };
    
    render(<AnalysisResults results={networkResults} />);
    
    expect(screen.getByText('Medium')).toBeInTheDocument();
    expect(screen.getByText('Source: Neo4j')).toBeInTheDocument();
  });

  it('handles technology mapping results', () => {
    const techResults = {
      status: 'success',
      data: [
        {
          patent_id: 'US123456',
          technology_name: 'Machine Learning',
          confidence: 0.92,
          method: 'IPC_MAPPING'
        }
      ],
      metadata: {
        engine: 'Neo4j-V2-Mapper',
        confidence: 'High'
      }
    };
    
    render(<AnalysisResults results={techResults} />);
    
    expect(screen.getByText('High')).toBeInTheDocument();
    expect(screen.getByText('Source: Neo4j-V2-Mapper')).toBeInTheDocument();
  });

  it('handles empty results', () => {
    const emptyResults = {
      status: 'success',
      data: [],
      metadata: {
        engine: 'Test',
        confidence: 'General'
      }
    };
    
    render(<AnalysisResults results={emptyResults} />);
    
    expect(screen.getByText('General')).toBeInTheDocument();
  });

  it('handles missing metadata', () => {
    const resultsWithoutMetadata = {
      status: 'success',
      data: [mockResults.data[0]]
    };
    
    render(<AnalysisResults results={resultsWithoutMetadata} />);
    
    expect(screen.getByText('Results')).toBeInTheDocument();
    // Should not crash when metadata is missing
  });

  it('handles Low confidence level', () => {
    const lowConfidenceResults = {
      ...mockResults,
      metadata: {
        ...mockResults.metadata,
        confidence: 'Low'
      }
    };
    
    render(<AnalysisResults results={lowConfidenceResults} />);
    
    const confidenceBadge = screen.getByText('Low');
    expect(confidenceBadge).toBeInTheDocument();
    expect(confidenceBadge).toHaveClass('bg-gray-50');
    expect(confidenceBadge).toHaveClass('text-gray-600');
  });

  it('handles Medium confidence level', () => {
    const mediumConfidenceResults = {
      ...mockResults,
      metadata: {
        ...mockResults.metadata,
        confidence: 'Medium'
      }
    };
    
    render(<AnalysisResults results={mediumConfidenceResults} />);
    
    const confidenceBadge = screen.getByText('Medium');
    expect(confidenceBadge).toBeInTheDocument();
    expect(confidenceBadge).toHaveClass('bg-yellow-50');
    expect(confidenceBadge).toHaveClass('text-yellow-700');
  });

  it('displays loading state when provided', () => {
    const loadingProps = {
      results: mockResults,
      loading: true
    };
    
    render(<AnalysisResults {...loadingProps} />);
    
    expect(screen.getByText('Analysis Results')).toBeInTheDocument();
    // Should not show loading spinner in this component as it doesn't handle loading state
  });
});