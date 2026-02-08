import { render, screen } from '@testing-library/react';
import { NetworkAnalysisTab } from '../NetworkAnalysisTab';
import { vi } from 'vitest';

// Mock lucide-react icons
vi.mock('lucide-react', () => ({
  Network: () => <div data-testid="network-icon" />,
}));

describe('NetworkAnalysisTab', () => {
  const mockOnAnalyze = vi.fn();
  const mockLoading = false;

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders with correct title and description', () => {
    render(<NetworkAnalysisTab onAnalyze={mockOnAnalyze} loading={mockLoading} />);
    
    expect(screen.getByText('Network Patent Analysis')).toBeInTheDocument();
    expect(screen.getByText('Analyze patent relationships and identify key entities')).toBeInTheDocument();
  });

  it('renders node type selection dropdown', () => {
    render(<NetworkAnalysisTab onAnalyze={mockOnAnalyze} loading={mockLoading} />);
    
    expect(screen.getByText('Select Node Type')).toBeInTheDocument();
    
    const select = screen.getByDisplayValue('Company');
    expect(select).toBeInTheDocument();
    
    // Check if all expected options are present
    const options = screen.getAllByRole('option');
    expect(options).toHaveLength(5);
    expect(options[0]).toHaveValue('company');
    expect(options[1]).toHaveValue('inventor');
    expect(options[2]).toHaveValue('technology');
    expect(options[3]).toHaveValue('classification');
    expect(options[4]).toHaveValue('patent');
  });

  it('renders analysis options checkboxes', () => {
    render(<NetworkAnalysisTab onAnalyze={mockOnAnalyze} loading={mockLoading} />);
    
    expect(screen.getByText('Analysis Options')).toBeInTheDocument();
    
    // Check for expected checkboxes
    expect(screen.getByText('Centrality Analysis')).toBeInTheDocument();
    expect(screen.getByText('Community Detection')).toBeInTheDocument();
    expect(screen.getByText('Path Analysis')).toBeInTheDocument();
  });

  it('has submit button with correct label', () => {
    render(<NetworkAnalysisTab onAnalyze={mockOnAnalyze} loading={mockLoading} />);
    
    const button = screen.getByText('Analyze Network');
    expect(button).toBeInTheDocument();
    expect(screen.getByTestId('network-icon')).toBeInTheDocument();
  });

  it('disables submit button when loading', () => {
    render(<NetworkAnalysisTab onAnalyze={mockOnAnalyze} loading={true} />);
    
    const button = screen.getByText('Analyzing...');
    expect(button).toBeDisabled();
  });

  it('has proper accessibility attributes', () => {
    render(<NetworkAnalysisTab onAnalyze={mockOnAnalyze} loading={mockLoading} />);
    
    const select = screen.getByDisplayValue('Company');
    expect(select).toHaveAttribute('aria-label');
    
    const checkboxes = screen.getAllByRole('checkbox');
    checkboxes.forEach(checkbox => {
      expect(checkbox).toHaveAttribute('aria-label');
    });
  });
});