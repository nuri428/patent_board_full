import { create } from 'zustand';

const INITIAL_RESULTS = { RTS: null, TPI: null, FSS: null, WSD: null };
const INITIAL_EVIDENCE = {
  representativePatents: [],
  ipcSignatures: [],
  abstractSnippets: [],
  confidenceScores: {},
};

export const useTGIPStore = create((set, get) => ({
  // Global
  selectedTechnology: null,
  selectedView: 'RTS',
  analysisRunId: null,

  // Results
  results: { ...INITIAL_RESULTS },

  // Evidence
  evidence: { ...INITIAL_EVIDENCE },

  // UI State
  isRunning: false,
  evidenceDrawerOpen: false,
  loadingView: null,
  error: null,

  // Actions
  setTechnology: (tech) => set({
    selectedTechnology: tech,
    results: { ...INITIAL_RESULTS },
    evidence: { ...INITIAL_EVIDENCE },
    analysisRunId: null,
    error: null,
  }),

  setView: (view) => set({ selectedView: view }),

  toggleEvidenceDrawer: () => set((s) => ({ evidenceDrawerOpen: !s.evidenceDrawerOpen })),

  openEvidenceDrawer: () => set({ evidenceDrawerOpen: true }),

  reset: () => set({
    selectedTechnology: null,
    selectedView: 'RTS',
    analysisRunId: null,
    results: { ...INITIAL_RESULTS },
    evidence: { ...INITIAL_EVIDENCE },
    isRunning: false,
    evidenceDrawerOpen: false,
    loadingView: null,
    error: null,
  }),

  runAnalysis: async (tgipApi) => {
    const { selectedTechnology } = get();
    if (!selectedTechnology) return;

    set({ isRunning: true, error: null });
    try {
      const response = await tgipApi.runAnalysis(selectedTechnology.id);
      const { run_id, results = { ...INITIAL_RESULTS }, evidence = { ...INITIAL_EVIDENCE } } = response.data ?? {};
      set({
        analysisRunId: run_id ?? null,
        results,
        evidence,
        isRunning: false,
        evidenceDrawerOpen: true,
      });
    } catch (err) {
      if (import.meta.env.DEV) {
        // 개발 환경에서만 Mock 데이터로 fallback (프로덕션 번들 제외)
        try {
          const { MOCK_RESULTS, MOCK_EVIDENCE } = await import('../mocks/tgipMockData.js');
          const mockRunId = `mock-run-${Date.now()}`;
          set({
            analysisRunId: mockRunId,
            results: MOCK_RESULTS,
            evidence: MOCK_EVIDENCE,
            isRunning: false,
            evidenceDrawerOpen: true,
            error: null,
          });
        } catch (importErr) {
          console.warn('[tgipStore] Mock data import failed:', importErr);
          set({ isRunning: false, error: null });
        }
      } else {
        // 프로덕션: 에러 상태로 전환
        console.error('[tgipStore] Analysis failed:', err);
        set({
          isRunning: false,
          error: '분석 서버에 연결할 수 없습니다. 잠시 후 다시 시도해 주세요.',
        });
      }
    }
  },
}));
