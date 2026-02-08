import api from './axios';

/**
 * MCP Proxy API
 * Calls the backend proxy which handles API key authentication and data processing.
 */
const callMcpProxy = async (toolName, args) => {
    const response = await api.post('/mcp/proxy', {
        tool_name: toolName,
        arguments: args
    });
    return response.data;
};

export const graphAPI = {
    getCompetitors: async (companyName) => {
        return callMcpProxy('graph_get_competitors', {
            company_name: companyName
        });
    },
    searchByProblem: async (keyword) => {
        return callMcpProxy('graph_search_by_problem_solution', {
            keyword: keyword
        });
    },
    getTechCluster: async (keyword) => {
        return callMcpProxy('graph_get_tech_cluster', {
            keyword: keyword
        });
    },
    findPath: async (start, end) => {
        return callMcpProxy('graph_find_path', {
            start_entity: start,
            end_entity: end
        });
    }
};

export const patentMcpAPI = {
    searchKRPatents: async (params) => {
        return callMcpProxy('search_kr_patents', params);
    },
    getPatentDetails: async (patentId) => {
        return callMcpProxy('get_patent_details', {
            patent_id: patentId
        });
    }
};

export const visualizationAPI = {
    getNetworkMap: async (params) => {
        const response = await api.post('/visualization/network-map', params);
        return response.data;
    }
};

export default callMcpProxy;
