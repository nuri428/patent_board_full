import axiosInstance from './axios';

export const tgipApi = {
  runAnalysis: (technology_id, options = {}) =>
    axiosInstance.post('/tgip/analysis', { technology_id, ...options }),

  getRunDetail: (run_id) =>
    axiosInstance.get(`/tgip/runs/${run_id}`),

  searchTechnologies: (query) =>
    axiosInstance.get('/tgip/technologies', { params: { q: query } }),

  getLibrary: (options = {}) =>
    axiosInstance.get('/tgip/library', options),
};
