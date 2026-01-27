import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { SemanticSearchTab } from '../SemanticSearchTab';
import { vi } from 'vitest';

// Mock lucide-react icons
vi.mock('lucide-react', () => ({
  Search: () => <div data-testid="search-icon" />,
  Loader2: () => <div data-testid="loader-icon" />,
}));

describe('SemanticSearchTab', () => {
  const mockOnSearch = vi.fn();
  const mockLoading = false;

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders with correct title and description', () => {
    render(<SemanticSearchTab onSearch={mockOnSearch} loading={mockLoading} />);
    
    expect(screen.getByText('Semantic Patent Search')).toBeInTheDocument();
    expect(screen.getByText('Find patents using AI-powered semantic similarity search')).toBeInTheDocument();
  });

  it('renders search input with placeholder', () => {
    render(<SemanticSearchTab onSearch={mockOnSearch} loading={mockLoading} />);
    
    const textarea = screen.getByPlaceholderText(
      'Enter your search query (e.g., "machine learning algorithms for medical imaging")'
    );
    expect(textarea).toBeInTheDocument();
    expect(textarea).toHaveAttribute('rows', '3');
  });

  it('renders results limit select options', () => {
    render(<SemanticSearchTab onSearch={mockOnSearch} loading={mockLoading} />);
    
    const select = screen.getByDisplayValue('10');
    expect(select).toBeInTheDocument();
    
    // Check if all expected options are present
    const options = screen.getAllByRole('option');
    expect(options).toHaveLength(5);
    expect(options[0]).toHaveValue('5');
    expect(options[1]).toHaveValue('10');
    expect(options[2]).toHaveValue('20');
    expect(options[3]).toHaveValue('30');
    expect(options[4]).toHaveValue('50');
  });

  it('renders similarity threshold slider', () => {
    render(<SemanticSearchTab onSearch={mockOnSearch} loading={mockLoading} />);
    
    const slider = screen.getByRole('slider');
    expect(slider).toBeInTheDocument();
    expect(slider).toHaveAttribute('min', '0.0');
    expect(slider).toHaveAttribute('max', '1.0');
    expect(slider).toHaveAttribute('step', '0.1');
    expect(slider).toHaveValue('0.7');
    
    // Check that the threshold value is displayed
    expect(screen.getByText('0.7')).toBeInTheDocument();
  });

  it('calls onSearch with correct parameters when search button is clicked', () => {
    render(<SemanticSearchTab onSearch={mockOnSearch} loading={mockLoading} />);
    
    // Enter search query
    const textarea = screen.getByPlaceholderText(
      'Enter your search query (e.g., "machine learning algorithms for medical imaging")'
    );
    fireEvent.change(textarea, { target: { value: 'test query' } });
    
    // Change limit
    const select = screen.getByDisplayValue('10');
    fireEvent.change(select, { target: { value: '20' } });
    
    // Change threshold
    const slider = screen.getByRole('slider');
    fireEvent.change(slider, { target: { value: '0.8' } });
    
    // Click search button
    const button = screen.getByText('Search Patents');
    fireEvent.click(button);
    
    expect(mockOnSearch).toHaveBeenCalledWith('semantic', {
      query: 'test query',
      limit: 20,
      similarity_threshold: 0.8
    });
  });

  it('disables search button when loading', () => {
    render(<SemanticSearchTab onSearch={mockOnSearch} loading={true} />);
    
    const button = screen.getByText('Searching...');
    expect(button).toBeDisabled();
    expect(screen.getByTestId('loader-icon')).toBeInTheDocument();
  });

  it('disables search button when query is empty', () => {
    render(<SemanticSearchTab onSearch={mockOnSearch} loading={mockLoading} />);
    
    const textarea = screen.getByPlaceholderText(
      'Enter your search query (e.g., "machine learning algorithms for medical imaging")'
    );
    fireEvent.change(textarea, { target: { value: '' } });
    
    const button = screen.getByText('Search Patents');
    expect(button).toBeDisabled();
  });

  it('enables search button when query has text', () => {
    render(<SemanticSearchTab onSearch={mockOnSearch} loading={mockLoading} />);
    
    const textarea = screen.getByPlaceholderText(
      'Enter your search query (e.g., "machine learning algorithms for medical imaging")'
    );
    fireEvent.change(textarea, { target: { value: 'valid query' } });
    
    const button = screen.getByText('Search Patents');
    expect(button).not.toBeDisabled();
  });

  it('updates threshold value when slider is changed', () => {
    render(<SemanticSearchTab onSearch={mockOnSearch} loading={mockLoading} />);
    
    const slider = screen.getByRole('slider');
    fireEvent.change(slider, { target: { value: '0.9' } });
    
    expect(screen.getByText('0.9')).toBeInTheDocument();
  });

  it('displays search button with search icon when not loading', () => {
    render(<SemanticSearchTab onSearch={mockOnSearch} loading={mockLoading} />);
    
    const button = screen.getByText('Search Patents');
    expect(screen.getByTestId('search-icon')).toBeInTheDocument();
  });

  it('has proper accessibility attributes', () => {
    render(<SemanticSearchTab onSearch={mockOnSearch} loading={mockLoading} />);
    
    const textarea = screen.getByPlaceholderText(
      'Enter your search query (e.g., "machine learning algorithms for medical imaging")'
    );
    expect(textarea).toHaveAttribute('aria-label');
    
    const select = screen.getByDisplayValue('10');
    expect(select).toHaveAttribute('aria-label');
    
    const slider = screen.getByRole('slider');
    expect(slider).toHaveAttribute('aria-label');
  });
});