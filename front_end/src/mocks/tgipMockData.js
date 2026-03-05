// DEV 환경 전용 — 백엔드 API 미완성 시 사용하는 Mock 데이터
// 이 파일은 프로덕션 번들에 포함되지 않음 (tgipStore.js catch 블록의 DEV 조건부 import)

export const MOCK_EVIDENCE = {
  representativePatents: [
    {
      id: 'KR1020230045231',
      title: '고체 전해질 기반 리튬 이온 배터리 및 제조 방법',
      abstractSnippet: '...전해질 층의 두께를 최소화하여 이온 전도도를 개선하고, 계면 저항을 감소시키는 고체 전해질 구조를 제공한다...',
      ipc: ['H01M 10/0562', 'H01M 10/052', 'H01M 4/131'],
      confidence: 0.91,
    },
    {
      id: 'KR1020220098712',
      title: '황화물계 고체 전해질 합성 방법',
      abstractSnippet: '...황화물계 고체 전해질의 고이온 전도성을 달성하기 위한 합성 방법 및 이를 포함하는 전고체 전지...',
      ipc: ['H01M 10/0562', 'C01B 17/20'],
      confidence: 0.87,
    },
  ],
  ipcSignatures: ['H01M 10/05', 'H01M 4/13', 'C01B 17/00'],
  abstractSnippets: [],
  confidenceScores: { overall: 0.89, coverage: 0.73 },
};

export const MOCK_RESULTS = {
  RTS: {
    score: 0.72,
    stage: 'Bottleneck',
    components: {
      patent_volume: 0.85,
      growth: 0.60,
      classification_conf: 0.78,
      citation_percentile: 0.65,
    },
    solutionOptions: [
      { approach: '황화물계 전해질', patents: 1243, coverage: 0.82, evidence: 'H01M 10/0562' },
      { approach: '산화물계 전해질', patents: 876, coverage: 0.71, evidence: 'H01M 10/052' },
      { approach: '폴리머 복합 전해질', patents: 432, coverage: 0.55, evidence: 'H01M 10/056' },
    ],
  },
  TPI: {
    semanticPropagationScore: 0.78,
    propagationGraph: {
      nodes: [
        { id: 'core', label: 'Solid State Battery', size: 40 },
        { id: 'ev', label: 'Electric Vehicle', size: 30 },
        { id: 'consumer', label: 'Consumer Electronics', size: 22 },
        { id: 'grid', label: 'Grid Storage', size: 18 },
      ],
      edges: [
        { id: 'e1', source: 'core', target: 'ev', weight: 0.85 },
        { id: 'e2', source: 'core', target: 'consumer', weight: 0.71 },
        { id: 'e3', source: 'core', target: 'grid', weight: 0.58 },
      ],
    },
    industryFlow: [
      { industry: 'Automotive EV', score: 0.85, patents: 412 },
      { industry: 'Consumer Electronics', score: 0.71, patents: 287 },
      { industry: 'Grid Storage', score: 0.58, patents: 163 },
      { industry: 'Aerospace', score: 0.34, patents: 89 },
    ],
    burstTimeline: [
      { year: 2017, count: 187, burstScore: 0.2 },
      { year: 2018, count: 234, burstScore: 0.3 },
      { year: 2019, count: 312, burstScore: 0.4 },
      { year: 2020, count: 445, burstScore: 0.55 },
      { year: 2021, count: 623, burstScore: 0.72 },
      { year: 2022, count: 891, burstScore: 0.90 },
      { year: 2023, count: 1043, burstScore: 0.95 },
    ],
  },
  FSS: {
    familyMetrics: { FES: 0.82, GCR: 0.74, MIV: 0.68, averageFamilySize: 4.3 },
    countryCoverage: [
      { iso: 'KR', count: 1243, intensity: 1.0 },
      { iso: 'US', count: 876, intensity: 0.71 },
      { iso: 'CN', count: 734, intensity: 0.59 },
      { iso: 'JP', count: 512, intensity: 0.41 },
      { iso: 'DE', count: 289, intensity: 0.23 },
    ],
    assigneeLeaderboard: [
      { name: 'Samsung SDI', familyCount: 234, gcr: 0.91 },
      { name: 'LG Energy Solution', familyCount: 198, gcr: 0.87 },
      { name: 'CATL', familyCount: 176, gcr: 0.82 },
      { name: 'Panasonic', familyCount: 145, gcr: 0.79 },
      { name: 'SK Innovation', familyCount: 112, gcr: 0.73 },
    ],
  },
  WSD: {
    problemClusters: [
      { id: 'dendrite', label: 'Dendrite Growth', density: 0.87, patents: 312 },
      { id: 'interface', label: 'Interface Resistance', density: 0.74, patents: 267 },
      { id: 'thermal', label: 'Thermal Stability', density: 0.61, patents: 198 },
      { id: 'scalability', label: 'Manufacturing Scale', density: 0.45, patents: 134 },
    ],
    solutionClusters: [
      { id: 'coating', label: 'Interface Coating', density: 0.72, patents: 198 },
      { id: 'composite', label: 'Composite Electrolyte', density: 0.65, patents: 176 },
      { id: 'pressure', label: 'Stack Pressure Control', density: 0.48, patents: 112 },
    ],
    heatmapMatrix: [
      [0.9, 0.3, 0.1],
      [0.7, 0.8, 0.2],
      [0.2, 0.4, 0.6],
      [0.1, 0.1, 0.9],
    ],
    gapCandidates: [
      { id: 'gap-1', problem: 'Thermal Stability at High Temperature', solution: 'Cross-industry Ceramic Tech', gapScore: 0.83, confidence: 0.71 },
      { id: 'gap-2', problem: 'Manufacturing Scale', solution: 'Roll-to-Roll Process', gapScore: 0.76, confidence: 0.65 },
      { id: 'gap-3', problem: 'Dendrite Growth', solution: 'Liquid Metal Interface', gapScore: 0.68, confidence: 0.59 },
    ],
    crossIndustryAnalogs: [
      { sourceIndustry: 'Aerospace', targetProblem: 'Thermal Electrolyte', analogy: 'Ceramic Insulator Tech', similarity: 0.76 },
      { sourceIndustry: 'Fuel Cell', targetProblem: 'Interface Resistance', analogy: 'MEA Fabrication', similarity: 0.68 },
    ],
  },
};
