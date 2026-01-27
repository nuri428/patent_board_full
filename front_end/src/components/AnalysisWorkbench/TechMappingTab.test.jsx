import { render, screen } from '@testing-library/react';
import { TechMappingTab } from '../TechMappingTab';
import { vi } from 'vitest';

// Mock lucide-react icons
vi.mock('lucide-react', () => ({
  Cpu: () => <div data-testid="cpu-icon" />,
}));

describe('TechMappingTab', () => {
  const mockOnMapping = vi.fn();
  const mockLoading = false;

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders with correct title and description', () => {
    render(<TechMappingTab onMapping={mockOnMapping} loading={mockLoading} />);
    
    expect(screen.getByText('Technology Patent Mapping')).toBeInTheDocument();
    expect(screen.getByText('Map patents to technology domains with AI classification')).toBeInTheDocument();
  });

  it('renders patent ID input with placeholder', () => {
    render(<TechMappingTab onMapping={mockOnMapping} loading={mockLoading} />);
    
    const input = screen.getByPlaceholderText('Enter patent application number');
    expect(input).toBeInTheDocument();
    expect(input).toHaveAttribute('type', 'text');
  });

  it('renders technology classification dropdown', () => {
    render(<TechMappingTab onMapping={mockOnMapping} loading={mockLoading} />);
    
    expect(screen.getByText('Technology Classification')).toBeInTheDocument();
    
    const select = screen.getByDisplayValue('Machine Learning');
    expect(select).toBeInTheDocument();
    
    // Check if all expected options are present
    const options = screen.getAllByRole('option');
    expect(options.length).toBeGreaterThan(1);
    expect(options[0]).toHaveValue('machine_learning');
  });

  it('renders confidence threshold slider', () => {
    render(<TechMappingTab onMapping={mockOnMapping} loading={mockLoading} />);
    
    expect(screen.getByText('Confidence Threshold')).toBeInTheDocument();
    
    const slider = screen.getByRole('slider');
    expect(slider).toBeInTheDocument();
    expect(slider).toHaveAttribute('min', '0.0');
    expect(slider).toHaveAttribute('max', '1.0');
    expect(slider).toHaveAttribute('step', '0.1');
    expect(slider).toHaveValue('0.7');
    
    // Check that the threshold value is displayed
    expect(screen.getByText('0.7')).toBeInTheDocument();
  });

  it('renders map button with correct icon', () => {
    render(<TechMappingTab onMapping={mockOnMapping} loading={mockLoading} />);
    
    const button = screen.getByText('Map Technology');
    expect(button).toBeInTheDocument();
    expect(screen.getByTestId('cpu-icon')).toBeInTheDocument();
  });

  it('disables map button when loading', () => {
    render(<TechMappingTab onMapping={mockOnMapping} loading={true} />);
    
    const button = screen.getByText('Mapping...');
    expect(button).toBeDisabled();
  });

  it('disables map button when patent ID is empty', () => {
    render(<TechMappingTab onMapping={mockOnMapping} loading={mockLoading} />);
    
    const input = screen.getByPlaceholderText('Enter patent application number');
    fireEvent.change(input, { target: { value: '' } });
    
    const button = screen.getByText('Map Technology');
    expect(button).toBeDisabled();
  });

  it('enables map button when patent ID has text', () => {
    render(<TechMappingTab onMapping={mockOnMapping} loading={mockLoading} />);
    
    const input = screen.getByPlaceholderText('Enter patent application number');
    fireEvent.change(input, { target: { value: 'US123456789' } });
    
    const button = screen.getByText('Map Technology');
    expect(button).not.toBeDisabled();
  });

  it('updates threshold value when slider is changed', () => {
    render(<TechMappingTab onMapping={mockOnMapping} loading={mockLoading} />);
    
    const slider = screen.getByRole('slider');
    fireEvent.change(slider, { target: { value: '0.9' } });
    
    expect(screen.getByText('0.9')).toBeInTheDocument();
  });

  it('has proper accessibility attributes', () => {
    render(<TechMappingTab onMapping={mockOnMapping} loading={mockLoading} />);
    
    const input = screen.getByPlaceholderText('Enter patent application number');
    expect(input).toHaveAttribute('aria-label');
    
    const select = screen.getByDisplayValue('Machine Learning');
    expect(select).toHaveAttribute('aria-label');
    
    const slider = screen.getByRole('slider');
    expect(slider).toHaveAttribute('aria-label');
  });

  it('renders description text', () => {
    render(<TechMappingTab onMapping={mockOnMapping} loading={mockLoading} />);
    
    expect(screen.getByText('AI-powered patent classification into technology domains')).toBeInTheDocument();
  });
});