import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ChatMessage from '../components/Chatbot/ChatMessage';
import PatentLink from '../components/PatentLink';
import PatentPreview from '../components/PatentPreview';

// Mock the global window object for analytics
global.gtag = jest.fn();

// Mock style appendChild
document.head.appendChild = jest.fn();

describe('Frontend Patent Integration Tests', () => {
    describe('ChatMessage Component', () => {
        const mockMessage = {
            id: 'msg-123',
            content: 'Here is a patent analysis for your request.',
            role: 'assistant',
            timestamp: '2026-01-29T17:20:09.123Z',
            sources: [
                {
                    title: 'US Patent 1234567',
                    type: 'patent',
                    name: 'Google Patents'
                }
            ],
            metadata: {
                confidence: 0.95,
                patents_found: 3
            },
            patent_urls: [
                {
                    url: 'https://patents.google.com/patent/US1234567',
                    title: 'Machine learning system',
                    country: 'US',
                    patent_id: '1234567',
                    source: 'google'
                },
                {
                    url: 'https://patents.google.com/patent/KR8765432',
                    title: 'Neural network architecture',
                    country: 'KR',
                    patent_id: '8765432',
                    source: 'google'
                }
            ]
        };

        test('renders chat message with patent URLs', () => {
            render(<ChatMessage message={mockMessage} />);

            expect(screen.getByText('US-1234567')).toBeInTheDocument();
            expect(screen.getByText('KR-8765432')).toBeInTheDocument();
            expect(screen.getByText('Related Patent Links (2):')).toBeInTheDocument();
        });

        test('displays patent link with correct styling', () => {
            render(<ChatMessage message={mockMessage} />);

            const patentLinks = screen.getAllByText('📄');
            expect(patentLinks).toHaveLength(2);
        });

        test('renders user and assistant roles correctly', () => {
            const userMessage = { ...mockMessage, role: 'user' };
            render(<ChatMessage message={userMessage} />);
            
            expect(screen.getByText('You')).toBeInTheDocument();

            const assistantMessage = { ...mockMessage, role: 'assistant' };
            render(<ChatMessage message={assistantMessage} />);
            
            expect(screen.getByText('Assistant')).toBeInTheDocument();
        });

        test('displays error message when error prop is true', () => {
            const errorMessage = { ...mockMessage, error: true, content: 'Error occurred' };
            render(<ChatMessage message={errorMessage} />);
            
            expect(screen.getByText('Error occurred')).toBeInTheDocument();
        });
    });

    describe('PatentLink Component', () => {
        const mockPatent = {
            url: 'https://patents.google.com/patent/US1234567',
            title: 'A new machine learning system for patent analysis',
            country: 'US',
            patent_id: '1234567'
        };

        test('renders patent link with correct information', () => {
            render(<PatentLink patent={mockPatent} source="google" />);

            expect(screen.getByText('US-1234567')).toBeInTheDocument();
            expect(screen.getByText('Google Patents')).toBeInTheDocument();
        });

        test('displays patent title truncated if too long', () => {
            const longTitle = 'This is a very long patent title that should be truncated when displayed in the link component';
            render(<PatentLink patent={{ ...mockPatent, title: longTitle }} source="google" />);

            const titleElement = screen.getByText(longTitle.substring(0, 80) + '...');
            expect(titleElement).toBeInTheDocument();
        });

        test('displays country flag and source icon', () => {
            render(<PatentLink patent={mockPatent} source="google" />);

            // Check for country flag (🇺🇸)
            expect(screen.getByText(/🇺🇸🔍/)).toBeInTheDocument();
        });

        test('handles different patent sources correctly', () => {
            const usptoPatent = { ...mockPatent, country: 'US', patent_id: '7654321' };
            render(<PatentLink patent={usptoPatent} source="uspto" />);

            expect(screen.getByText('US-7654321')).toBeInTheDocument();
            expect(screen.getByText('USPTO')).toBeInTheDocument();
        });

        test('handles unknown patent source gracefully', () => {
            const unknownSourcePatent = { ...mockPatent, country: 'EP', patent_id: '112233' };
            render(<PatentLink patent={unknownSourcePatent} source="unknown" />);

            expect(screen.getByText('EP-112233')).toBeInTheDocument();
            expect(screen.getByText('Patent Database')).toBeInTheDocument();
        });
    });

    describe('PatentPreview Component', () => {
        const mockPatent = {
            url: 'https://patents.google.com/patent/US1234567',
            title: 'Machine learning system for patent analysis',
            country: 'US',
            patent_id: '1234567'
        };

        test('renders loading state initially', () => {
            render(<PatentPreview patent={mockPatent} onClose={() => {}} />);
            
            expect(screen.getByText('Loading patent details...')).toBeInTheDocument();
            expect(screen.getByRole('status')).toBeInTheDocument();
        });

        test('renders patent details when loaded', async () => {
            render(<PatentPreview patent={mockPatent} onClose={() => {}} />);
            
            await waitFor(() => {
                expect(screen.getByText('Machine learning system for patent analysis')).toBeInTheDocument();
                expect(screen.getByText('John Doe, Jane Smith')).toBeInTheDocument();
                expect(screen.getByText('Example Corp')).toBeInTheDocument();
            });
        });

        test('displays error message when fetch fails', async () => {
            // Force error by mocking the promise to reject
            const originalError = console.error;
            console.error = jest.fn();

            render(<PatentPreview patent={mockPatent} onClose={() => {}} />);
            
            // Wait for the error state
            await waitFor(() => {
                expect(screen.getByText('Failed to load patent details')).toBeInTheDocument();
            });

            console.error = originalError;
        });

        test('displays correct patent header with country flag', async () => {
            render(<PatentPreview patent={mockPatent} onClose={() => {}} />);
            
            await waitFor(() => {
                expect(screen.getByText('US-1234567 Preview')).toBeInTheDocument();
            });
        });

        test('handles close button correctly', async () => {
            const mockOnClose = jest.fn();
            render(<PatentPreview patent={mockPatent} onClose={mockOnClose} />);
            
            await waitFor(() => {
                const closeButton = screen.getByText('Close Preview');
                fireEvent.click(closeButton);
                expect(mockOnClose).toHaveBeenCalled();
            });
        });

        test('displays full patent button', async () => {
            render(<PatentPreview patent={mockPatent} onClose={() => {}} />);
            
            await waitFor(() => {
                const fullPatentButton = screen.getByText('Full Patent');
                expect(fullPatentButton).toBeInTheDocument();
                expect(fullPatentButton).toHaveAttribute('href', mockPatent.url);
                expect(fullPatentButton).toHaveAttribute('target', '_blank');
            });
        });
    });

    describe('Integration Test: Patent Link Preview', () => {
        test('PatentLink opens PatentPreview when clicked', async () => {
            const mockPatent = {
                url: 'https://patents.google.com/patent/US1234567',
                title: 'Test patent',
                country: 'US',
                patent_id: '1234567'
            };

            render(<PatentLink patent={mockPatent} source="google" />);

            // Initially, preview should not be visible
            expect(screen.queryByRole('dialog')).not.toBeInTheDocument();

            // Click the patent link
            const patentLink = screen.getByText('US-1234567').closest('a');
            fireEvent.click(patentLink);

            // Preview modal should be visible
            await waitFor(() => {
                expect(screen.getByText('US-1234567 Preview')).toBeInTheDocument();
            });
        });
    });

    describe('Analytics Integration', () => {
        test('tracks patent link clicks via gtag', () => {
            const mockPatent = {
                url: 'https://patents.google.com/patent/US1234567',
                title: 'Test patent',
                country: 'US',
                patent_id: '1234567'
            };

            render(<PatentLink patent={mockPatent} source="google" />);

            const patentLink = screen.getByText('US-1234567').closest('a');
            fireEvent.click(patentLink);

            expect(window.gtag).toHaveBeenCalledWith('event', 'patent_link_click', {
                'event_category': 'engagement',
                'event_label': 'US-1234567',
                'value': 1
            });
        });
    });

    describe('Responsive Design', () => {
        test('renders correctly on mobile screens', () => {
            window.innerWidth = 375;
            window.dispatchEvent(new Event('resize'));

            const mockMessage = {
                id: 'msg-123',
                content: 'Mobile test message',
                role: 'user',
                timestamp: '2026-01-29T17:20:09.123Z',
                patent_urls: []
            };

            render(<ChatMessage message={mockMessage} />);

            expect(screen.getByText('You')).toBeInTheDocument();

            // Clean up
            window.innerWidth = 1024;
            window.dispatchEvent(new Event('resize'));
        });
    });

    describe('Edge Cases', () => {
        test('handles missing patent_urls gracefully', () => {
            const messageWithoutPatents = {
                id: 'msg-123',
                content: 'Message without patents',
                role: 'assistant',
                timestamp: '2026-01-29T17:20:09.123Z',
                patent_urls: []
            };

            render(<ChatMessage message={messageWithoutPatents} />);

            expect(screen.getByText('Message without patents')).toBeInTheDocument();
            expect(screen.queryByText('Related Patent Links')).not.toBeInTheDocument();
        });

        test('handles empty patent_urls array', () => {
            const message = {
                id: 'msg-123',
                content: 'Message with empty patent array',
                role: 'assistant',
                timestamp: '2026-01-29T17:20:09.123Z',
                patent_urls: []
            };

            render(<ChatMessage message={message} />);

            expect(screen.queryByText('Related Patent Links')).not.toBeInTheDocument();
        });

        test('handles null patent_urls', () => {
            const message = {
                id: 'msg-123',
                content: 'Message with null patent urls',
                role: 'assistant',
                timestamp: '2026-01-29T17:20:09.123Z',
                patent_urls: null
            };

            render(<ChatMessage message={message} />);

            expect(screen.getByText('Message with null patent urls')).toBeInTheDocument();
            expect(screen.queryByText('Related Patent Links')).not.toBeInTheDocument();
        });
    });
});