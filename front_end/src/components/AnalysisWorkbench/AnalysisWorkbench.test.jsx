import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { AnalysisWorkbench } from '../AnalysisWorkbench';
import { vi } from 'vitest';

// Mock the API module
vi.mock('../api/axios');

const mockApi = {
  post: vi.fn()
};

// Mock the tab components
vi.mock('../components/AnalysisWorkbench/SemanticSearchTab', () => ({
  default: ({ onSearch, loading }) => (
    <div data-testid="semantic-search-tab">
      <button onClick={() => onSearch('semantic', { query: 'test' })}>
        Search
      </button>
    </div>
  )
}));

vi.mock('../components/AnalysisWorkbench/NetworkAnalysisTab', () => ({
  default: ({ onAnalyze, loading }) => (
    <div data-testid="network-analysis-tab">
      <button onClick={() => onAnalyze('network', { nodes: [] })}>
        Analyze
      </button>
    </div>
  )
}));

vi.mock('../components/AnalysisWorkbench/TechMappingTab', () => ({
  default: ({ onMapping, loading }) => (
    <div data-testid="tech-mapping-tab">
      <button onClick={() => onMapping('tech', { patent_id: 'test' })}>
        Map
      </button>
    </div>
  )
}));

vi.mock('../components/AnalysisWorkbench/AnalysisResults', () => ({
  default: ({ results }) => (
    <div data-testid="analysis-results">
      Results: {JSON.stringify(results)}
    </div>
  )
}));

describe('AnalysisWorkbench', () => {
  beforeEach(() => {
    // Reset all mocks
    vi.clearAllMocks();
    // Mock the API module
    vi.mocked(mockApi.post).mockResolvedValue({
      data: { status: 'success', results: [] }
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('renders with correct title and description', () => {
    render(<AnalysisWorkbench />);
    
    expect(screen.getByText('AI Analysis Workbench')).toBeInTheDocument();
    expect(screen.getByText('Advanced patent analysis powered by MCP server capabilities')).toBeInTheDocument();
  });

  it('renders all tab buttons', () => {
    render(<AnalysisWorkbench />);
    
    expect(screen.getByText('Semantic Search')).toBeInTheDocument();
    expect(screen.getByText('Network Analysis')).toBeInTheDocument();
    expect(screen.getByText('Tech Mapping')).toBeInTheDocument();
    expect(screen.getByText('Data Charts')).toBeInTheDocument();
  });

  it('switches tabs correctly', () => {
    render(<AnalysisWorkbench />);
    
    // Initially should show semantic tab content
    expect(screen.getByTestId('semantic-search-tab')).toBeInTheDocument();
    
    // Click network analysis tab
    const networkTab = screen.getByText('Network Analysis');
    fireEvent.click(networkTab);
    
    expect(screen.getByTestId('network-analysis-tab')).toBeInTheDocument();
    expect(screen.queryByTestId('semantic-search-tab')).not.toBeInTheDocument();
  });

  it('shows loading state during analysis', async () => {
    render(<AnalysisWorkbench />);
    
    // Click search to trigger analysis
    fireEvent.click(screen.getByText('Search Patents'));
    
    // Check if loading state is handled
    await waitFor(() => {
      // The component should handle loading state internally
      expect(mockApi.post).toHaveBeenCalled();
    });
  });

  it('displays analysis results when available', async () => {
    const mockResults = {
      status: 'success',
      data: [{ id: '1', title: 'Test Patent' }]
    };
    
    vi.mocked(mockApi.post).mockResolvedValueOnce({
      data: mockResults
    });
    
    render(<AnalysisWorkbench />);
    
    // Trigger analysis
    fireEvent.click(screen.getByText('Search Patents'));
    
    await waitFor(() => {
      expect(screen.getByTestId('analysis-results')).toBeInTheDocument();
    });
  });

  it('handles API errors gracefully', async () => {
    vi.mocked(mockApi.post).mockRejectedValueOnce({
      response: { data: { detail: 'API Error' } }
    });
    
    render(<AnalysisWorkbench />);
    
    // Trigger analysis that will fail
    fireEvent.click(screen.getByText('Search Patents'));
    
    await waitFor(() => {
      // Should display error message
      expect(screen.getByText('API Error')).toBeInTheDocument();
    });
  });

  it('shows charts tab placeholder', () => {
    render(<AnalysisWorkbench />);
    
    // Click charts tab
    const chartsTab = screen.getByText('Data Charts');
    fireEvent.click(chartsTab);
    
    expect(screen.getByText('Data visualization charts coming soon')).toBeInTheDocument();
  });

  it('maintains active tab state', () => {
    const { rerender } = render(<AnalysisWorkbench />);
    
    // Initially semantic tab should be active
    const semanticTab = screen.getByText('Semantic Search');
    expect(semanticTab).toHaveClass('bg-white');
    
    // Click tech mapping tab
    const techTab = screen.getByText('Tech Mapping');
    fireEvent.click(techTab);
    
    // Tech tab should be active
    expect(techTab).toHaveClass('bg-white');
    expect(semanticTab).not.toHaveClass('bg-white');
  });

  it('calls API with correct parameters for semantic search', async () => {
    render(<AnalysisWorkbench />);
    
    // The semantic search tab should trigger the API call
    fireEvent.click(screen.getByText('Search Patents'));
    
    await waitFor(() => {
      expect(mockApi.post).toHaveBeenCalledWith('mcp/semantic-search', {
        query: 'test',
      });
    });
  });

  it('calls API with correct parameters for network analysis', async () => {
    render(<AnalysisWorkbench />);
    
    // Switch to network analysis tab
    fireEvent.click(screen.getByText('Network Analysis'));
    
    // The network analysis tab should trigger the API call
    fireEvent.click(screen.getByText('Analyze'));
    
    await waitFor(() => {
      expect(mockApi.post).toHaveBeenCalledWith('mcp/network-analysis', {
        nodes: [],
      });
    });
  });

  it('calls API with correct parameters for technology mapping', async () => {
    render(<AnalysisWorkbench />);
    
    // Switch to tech mapping tab
    fireEvent.click(screen.getByText('Tech Mapping'));
    
    // The tech mapping tab should trigger the API call
    fireEvent.click(screen.getByText('Map'));
    
    await waitFor(() => {
      expect(mockApi.post).toHaveBeenCalledWith('mcp/technology-mapping', {
        patent_id: 'test',
      });
    });
  });
});
