import axios from 'axios';

// MCP Server URL (Direct access)
const MCP_API_URL = 'http://localhost:8081';

// We reuse the main auth token if needed, or a specific API Key if we implemented that flow.
// For this integration, we will use the same 'Bearer' token if the MCP server accepts it,
// OR we use the X-API-Key we defined.
// The MCP server uses `verify_api_key`.
// In a real app, we'd fetch this key from the backend or user settings.
// For this demo/dev, we'll hardcode the test key or fetch from a hypothetical endpoint.
// Let's assume we use the known TEST KEY for now to facilitate verification.
const API_KEY = "test-key-123456";

const mcpApi = axios.create({
    baseURL: MCP_API_URL,
    headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY,
    },
});

export const graphAPI = {
    getCompetitors: async (companyName) => {
        const response = await mcpApi.post('/tools/graph_get_competitors', {
            company_name: companyName
        });
        return response.data;
    },
    searchByProblem: async (keyword) => {
        const response = await mcpApi.post('/tools/graph_search_by_problem_solution', {
            keyword: keyword
        });
        return response.data;
    },
    getTechCluster: async (keyword) => {
        const response = await mcpApi.post('/tools/graph_get_tech_cluster', {
            keyword: keyword
        });
        return response.data;
    },
    findPath: async (start, end) => {
        const response = await mcpApi.post('/tools/graph_find_path', {
            start_entity: start,
            end_entity: end
        });
        return response.data;
    }
};

export default mcpApi;
