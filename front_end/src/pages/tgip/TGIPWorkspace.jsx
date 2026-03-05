import { useEffect, useRef, useState } from 'react';
import { useParams } from 'react-router-dom';
import TGIPHeader from '../../components/tgip/Layout/TGIPHeader';
import SidebarViewSelector from '../../components/tgip/Workspace/SidebarViewSelector';
import ObservationCanvas from '../../components/tgip/Workspace/ObservationCanvas';
import EvidenceDrawer from '../../components/tgip/Workspace/EvidenceDrawer';
import DisclaimerBanner from '../../components/tgip/shared/DisclaimerBanner';
import { usePDFExport } from '../../components/tgip/shared/PDFExporter';
import { useTGIPStore } from '../../store/tgipStore';
import { DEMO_TECHS } from '../../constants/tgip';

const TGIPWorkspace = () => {
  const { technology_id } = useParams();
  const { setTechnology, selectedTechnology, selectedView, analysisRunId, results, error } = useTGIPStore();
  const canvasRef = useRef(null);
  const prevTechIdRef = useRef(null);
  const { exportToPDF } = usePDFExport();
  const [exportError, setExportError] = useState(null);

  const canExport = !!results?.[selectedView];

  const handleExport = () => {
    const fileName = `tgip-${selectedTechnology?.id || 'unknown'}-${selectedView}-${analysisRunId || 'draft'}.pdf`;
    exportToPDF({
      targetRef: canvasRef,
      fileName,
      onError: () => {
        setExportError('PDF 내보내기에 실패했습니다. 다시 시도해 주세요.');
        setTimeout(() => setExportError(null), 4000);
      },
    });
  };

  useEffect(() => {
    if (technology_id && prevTechIdRef.current !== technology_id) {
      prevTechIdRef.current = technology_id;
      const tech = DEMO_TECHS[technology_id] ?? {
        id: technology_id,
        name: technology_id.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
        description: '',
        patent_count: null,
      };
      setTechnology(tech);
    }
  }, [technology_id, setTechnology]);

  return (
    <div className="h-screen flex flex-col bg-slate-50 overflow-hidden">
      <TGIPHeader onExport={handleExport} canExport={canExport} />
      <div className="flex flex-1 overflow-hidden">
        <SidebarViewSelector />
        <ObservationCanvas canvasRef={canvasRef} />
      </div>
      <EvidenceDrawer />
      {exportError && (
        <div className="px-6 py-2 bg-amber-50 border-t border-amber-200 text-sm text-amber-700 flex items-center justify-between">
          <span>{exportError}</span>
          <button onClick={() => setExportError(null)} className="ml-4 text-amber-500 hover:text-amber-700">✕</button>
        </div>
      )}
      {error && (
        <div className="px-6 py-2 bg-red-50 border-t border-red-200 text-sm text-red-700">
          {error}
        </div>
      )}
      <div className="px-6 py-2 bg-white border-t border-slate-100">
        <DisclaimerBanner />
      </div>
    </div>
  );
};

export default TGIPWorkspace;
