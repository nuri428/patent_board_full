#!/usr/bin/env node

/**
 * Frontend Integration Test Script for LangGraph Chatbot
 * 
 * This script tests the integration between the React frontend and the LangGraph backend.
 * It verifies that all components are properly connected and API calls work correctly.
 * 
 * Usage: npm run test:chatbot
 */

import axios from 'axios';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// __dirname equivalent for ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class ChatbotIntegrationTester {
    constructor() {
        this.langgraphAPI = 'http://localhost:8003';
        this.frontendURL = 'http://localhost:3000';
        this.testResults = {
            backend: { healthy: false, endpoints: [] },
            frontend: { accessible: false, components: [] },
            integration: { connected: false, scenarios: [] }
        };
        this.errors = [];
    }

    log(message, type = 'info') {
        const timestamp = new Date().toISOString();
        const prefix = {
            info: '[INFO]',
            warn: '[WARN]',
            error: '[ERROR]',
            success: '[SUCCESS]'
        }[type];
        
        console.log(`${timestamp} ${prefix} ${message}`);
        
        if (type === 'error') {
            this.errors.push(message);
        }
    }

    async sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    async testBackendHealth() {
        this.log('Testing LangGraph backend health...', 'info');
        
        try {
            const response = await axios.get(`${this.langgraphAPI}/health`, {
                timeout: 5000
            });
            
            if (response.status === 200) {
                this.testResults.backend.healthy = true;
                this.log('✓ LangGraph backend is healthy', 'success');
                
                // Test key endpoints
                await this.testBackendEndpoints();
                return true;
            } else {
                this.log(`✗ Backend returned status: ${response.status}`, 'error');
                return false;
            }
        } catch (error) {
            this.log(`✗ Backend health check failed: ${error.message}`, 'error');
            return false;
        }
    }

    async testBackendEndpoints() {
        const endpoints = [
            { method: 'POST', path: '/chat', description: 'Send chat message' },
            { method: 'POST', path: '/sessions', description: 'Create session' },
            { method: 'GET', path: '/sessions/:id', description: 'Get session' },
            { method: 'GET', path: '/users/:id/sessions', description: 'Get user sessions' },
            { method: 'POST', path: '/users/:id/properties', description: 'Set user properties' },
            { method: 'GET', path: '/users/:id/properties', description: 'Get user properties' }
        ];

        for (const endpoint of endpoints) {
            const testEndpoint = endpoint.path.replace(':id', 'test123');
            const url = `${this.langgraphAPI}${testEndpoint}`;
            
            try {
                let response;
                switch (endpoint.method) {
                    case 'POST':
                        response = await axios.post(url, { test: true }, { timeout: 3000 });
                        break;
                    case 'GET':
                        response = await axios.get(url, { timeout: 3000 });
                        break;
                    default:
                        continue;
                }
                
                this.testResults.backend.endpoints.push({
                    endpoint,
                    status: 'success',
                    statusCode: response.status
                });
                
                this.log(`✓ ${endpoint.method} ${endpoint.path}: ${response.status}`, 'success');
                
            } catch (error) {
                // Some endpoints are expected to fail with invalid test data
                if (error.response) {
                    this.testResults.backend.endpoints.push({
                        endpoint,
                        status: 'failed',
                        statusCode: error.response.status,
                        error: error.response.data.detail || error.response.data.message
                    });
                    this.log(`✗ ${endpoint.method} ${endpoint.path}: ${error.response.status} - ${error.response.data.detail || 'Invalid test data'}`, 'warn');
                } else {
                    this.testResults.backend.endpoints.push({
                        endpoint,
                        status: 'error',
                        error: error.message
                    });
                    this.log(`✗ ${endpoint.method} ${endpoint.path}: Connection error`, 'error');
                }
            }
            
            await this.sleep(100); // Rate limiting
        }
    }

    async testFrontendAccessibility() {
        this.log('Testing frontend accessibility...', 'info');
        
        try {
            // Check if frontend is running by testing the chat page
            const response = await axios.get(`${this.frontendURL}/chat`, {
                timeout: 5000,
                validateStatus: function (status) {
                    // Allow 200-302 (redirects may occur)
                    return status >= 200 && status < 400;
                }
            });
            
            this.testResults.frontend.accessible = true;
            this.log('✓ Frontend is accessible', 'success');
            
            // Check for key components
            await this.testFrontendComponents();
            return true;
            
        } catch (error) {
            if (error.code === 'ECONNREFUSED') {
                this.log('✗ Frontend is not running. Please start the frontend with: npm run dev', 'error');
            } else {
                this.log(`✗ Frontend access failed: ${error.message}`, 'error');
            }
            return false;
        }
    }

    async testFrontendComponents() {
        // Check if key files exist
        const frontendPath = path.join(__dirname, '..', 'front_end', 'src');
        const requiredFiles = [
            'pages/Chat.jsx',
            'context/ChatbotContext.jsx',
            'components/Chatbot/Chatbot.jsx',
            'components/Chatbot/ChatMessage.jsx',
            'components/Chatbot/ChatInput.jsx',
            'components/Chatbot/SessionList.jsx',
            'components/Chatbot/ConversationHistory.jsx',
            'api/chatbot.js',
            'utils/chatbotHooks.js'
        ];

        for (const file of requiredFiles) {
            const filePath = path.join(frontendPath, file);
            if (fs.existsSync(filePath)) {
                this.testResults.frontend.components.push({
                    file,
                    status: 'exists',
                    size: fs.statSync(filePath).size
                });
                this.log(`✓ ${file}: Exists (${fs.statSync(filePath).size} bytes)`, 'success');
            } else {
                this.testResults.frontend.components.push({
                    file,
                    status: 'missing'
                });
                this.log(`✗ ${file}: Missing`, 'error');
            }
        }
    }

    async testIntegration() {
        this.log('Testing frontend-backend integration...', 'info');
        
        if (!this.testResults.backend.healthy) {
            this.log('Skipping integration tests - backend is not healthy', 'warn');
            return false;
        }
        
        if (!this.testResults.frontend.accessible) {
            this.log('Skipping integration tests - frontend is not accessible', 'warn');
            return false;
        }
        
        // Test scenarios
        await this.testChatSessionScenario();
        await this testUserAuthenticationScenario();
        await this testEnvironmentVariables();
        
        return this.testResults.integration.connected;
    }

    async testChatSessionScenario() {
        this.log('Testing chat session scenario...', 'info');
        
        try {
            // Create a user session
            const userId = `test_user_${Date.now()}`;
            const createResponse = await axios.post(`${this.langgraphAPI}/sessions`, {
                user_id: userId
            });
            
            if (createResponse.status === 200 && createResponse.data.id) {
                const sessionId = createResponse.data.id;
                this.log(`✓ Created session: ${sessionId}`, 'success');
                
                // Send a test message
                const chatResponse = await axios.post(`${this.langgraphAPI}/chat`, {
                    message: 'Hello, this is a test message from integration test',
                    session_id: sessionId
                });
                
                if (chatResponse.status === 200) {
                    this.testResults.integration.scenarios.push({
                        name: 'Chat Session',
                        status: 'success',
                        sessionId,
                        messageId: chatResponse.data.message_id
                    });
                    this.log('✓ Chat message sent successfully', 'success');
                } else {
                    this.testResults.integration.scenarios.push({
                        name: 'Chat Session',
                        status: 'failed',
                        statusCode: chatResponse.status
                    });
                    this.log(`✗ Chat message failed: ${chatResponse.status}`, 'error');
                }
                
                // Get user sessions
                const sessionsResponse = await axios.get(`${this.langgraphAPI}/users/${userId}/sessions`);
                if (sessionsResponse.status === 200) {
                    this.log(`✓ Retrieved ${sessionsResponse.data.length} sessions for user`, 'success');
                }
                
            } else {
                this.log('✗ Failed to create session', 'error');
            }
            
        } catch (error) {
            this.testResults.integration.scenarios.push({
                name: 'Chat Session',
                status: 'error',
                error: error.message
            });
            this.log(`✗ Chat session scenario failed: ${error.message}`, 'error');
        }
    }

    async testUserAuthenticationScenario() {
        this.log('Testing user authentication scenario...', 'info');
        
        try {
            const userId = `auth_test_user_${Date.now()}`;
            
            // Set user properties
            const properties = {
                name: 'Test User',
                email: 'test@example.com',
                preferences: {
                    theme: 'light',
                    language: 'en'
                }
            };
            
            const setPropertiesResponse = await axios.post(`${this.langgraphAPI}/users/${userId}/properties`, properties);
            if (setPropertiesResponse.status === 200) {
                this.log('✓ User properties set successfully', 'success');
                
                // Get user properties
                const getPropertiesResponse = await axios.get(`${this.langgraphAPI}/users/${userId}/properties`);
                if (getPropertiesResponse.status === 200) {
                    this.testResults.integration.scenarios.push({
                        name: 'User Authentication',
                        status: 'success'
                    });
                    this.log('✓ User properties retrieved successfully', 'success');
                }
            }
            
        } catch (error) {
            this.testResults.integration.scenarios.push({
                name: 'User Authentication',
                status: 'error',
                error: error.message
            });
            this.log(`✗ User authentication scenario failed: ${error.message}`, 'error');
        }
    }

    async testEnvironmentVariables() {
        this.log('Testing environment variables...', 'info');
        
        try {
            // Check if environment files exist and have chatbot configuration
            const envFiles = [
                path.join(__dirname, '..', '.env'),
                path.join(__dirname, '..', 'front_end', '.env')
            ];
            
            for (const envFile of envFiles) {
                if (fs.existsSync(envFile)) {
                    const content = fs.readFileSync(envFile, 'utf8');
                    if (content.includes('VITE_CHATBOT_API_URL')) {
                        this.log(`✓ ${path.basename(envFile)} contains chatbot API URL configuration`, 'success');
                    } else {
                        this.log(`✗ ${path.basename(envFile)} missing chatbot API URL`, 'warn');
                    }
                } else {
                    this.log(`✗ ${path.basename(envFile)} not found`, 'warn');
                }
            }
            
        } catch (error) {
            this.log(`✗ Environment variables test failed: ${error.message}`, 'error');
        }
    }

    async run() {
        this.log('Starting LangGraph Chatbot Integration Test', 'info');
        this.log('==========================================', 'info');
        
        // Backend tests
        const backendHealthy = await this.testBackendHealth();
        this.log('');
        
        // Frontend tests
        const frontendAccessible = await this.testFrontendAccessibility();
        this.log('');
        
        // Integration tests
        if (backendHealthy && frontendAccessible) {
            await this.testIntegration();
        }
        this.log('');
        
        // Summary
        this.generateReport();
    }

    generateReport() {
        this.log('Integration Test Report', 'info');
        this.log('=====================', 'info');
        
        // Backend summary
        this.log('\nBackend Status:', 'info');
        this.log(`- Healthy: ${this.testResults.backend.healthy ? '✓' : '✗'}`);
        this.log(`- Endpoints tested: ${this.testResults.backend.endpoints.length}`);
        const successfulEndpoints = this.testResults.backend.endpoints.filter(e => e.status === 'success').length;
        this.log(`- Successful endpoints: ${successfulEndpoints}`);
        
        // Frontend summary
        this.log('\nFrontend Status:', 'info');
        this.log(`- Accessible: ${this.testResults.frontend.accessible ? '✓' : '✗'}`);
        this.log(`- Components checked: ${this.testResults.frontend.components.length}`);
        const existingComponents = this.testResults.frontend.components.filter(c => c.status === 'exists').length;
        this.log(`- Existing components: ${existingComponents}`);
        
        // Integration summary
        this.log('\nIntegration Status:', 'info');
        const successfulScenarios = this.testResults.integration.scenarios.filter(s => s.status === 'success').length;
        this.log(`- Scenarios tested: ${this.testResults.integration.scenarios.length}`);
        this.log(`- Successful scenarios: ${successfulScenarios}`);
        
        // Overall result
        const overallSuccess = this.testResults.backend.healthy && 
                              this.testResults.frontend.accessible && 
                              successfulScenarios > 0;
        
        this.log(`\nOverall Result: ${overallSuccess ? '✓ SUCCESS' : '✗ FAILED'}`, overallSuccess ? 'success' : 'error');
        
        if (this.errors.length > 0) {
            this.log('\nErrors encountered:', 'error');
            this.errors.forEach(error => this.log(`- ${error}`, 'error'));
        }
        
        this.log('\nNext steps:', 'info');
        if (!this.testResults.backend.healthy) {
            this.log('- Start LangGraph backend: cd back_end/langgraph && python -m uvicorn main:app --reload --port 8003');
        }
        if (!this.testResults.frontend.accessible) {
            this.log('- Start frontend: cd front_end && npm run dev');
        }
        if (this.testResults.frontend.components.filter(c => c.status === 'missing').length > 0) {
            this.log('- Check frontend component files exist in front_end/src/');
        }
        
        this.log('\nIntegration test completed.', 'info');
    }
}

// Run the test
const tester = new ChatbotIntegrationTester();
tester.run().catch(console.error);

export default ChatbotIntegrationTester;