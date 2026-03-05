import { lazy, Suspense, useRef } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { useTGIPStore } from '../../../store/tgipStore';

const RTSView = lazy(() => import('../views/RTSView/RTSView'));
const TPIView = lazy(() => import('../views/TPIView/TPIView'));
const FSSView = lazy(() => import('../views/FSSView/FSSView'));
const WSDView = lazy(() => import('../views/WSDView/WSDView'));

const VIEW_COMPONENTS = {
  RTS: RTSView,
  TPI: TPIView,
  FSS: FSSView,
  WSD: WSDView,
};

const viewVariants = {
  initial: { opacity: 0, y: 6 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.18 } },
  exit:    { opacity: 0, y: -6, transition: { duration: 0.12 } },
};

const ViewLoader = () => (
  <div className="flex items-center justify-center h-full text-slate-400">
    <div className="w-8 h-8 border-2 border-violet-200 border-t-violet-500 rounded-full animate-spin" />
  </div>
);

const LoadingOverlay = () => (
  <div className="flex flex-col items-center justify-center h-full gap-4 text-slate-500">
    <div className="relative w-16 h-16">
      <div className="absolute inset-0 rounded-full border-4 border-slate-200" />
      <div className="absolute inset-0 rounded-full border-4 border-t-violet-500 animate-spin" />
    </div>
    <div className="text-center">
      <p className="font-medium">Running analysis...</p>
      <p className="text-sm text-slate-400 mt-1">Computing RTS · TPI · FSS · WSD signals</p>
    </div>
  </div>
);

const EmptyState = ({ technology }) => (
  <div className="flex flex-col items-center justify-center h-full gap-3 text-slate-400">
    {!technology ? (
      <>
        <p className="text-lg font-medium text-slate-600">Select a technology</p>
        <p className="text-sm">Use the selector above to choose a technology object to observe.</p>
      </>
    ) : (
      <>
        <p className="text-lg font-medium text-slate-600">{technology.name}</p>
        <p className="text-sm">Press <strong>Run Analysis</strong> to generate observational signals.</p>
      </>
    )}
  </div>
);

const ObservationCanvas = ({ canvasRef }) => {
  const { selectedView, results, isRunning, selectedTechnology } = useTGIPStore();
  const innerRef = useRef(null);
  const ref = canvasRef || innerRef;
  const ViewComponent = VIEW_COMPONENTS[selectedView];

  const hasAnyResult = Object.values(results).some(Boolean);

  return (
    <main ref={ref} className="flex-1 overflow-auto bg-slate-50">
      {isRunning ? (
        <LoadingOverlay />
      ) : !hasAnyResult ? (
        <EmptyState technology={selectedTechnology} />
      ) : (
        <div className="p-6 h-full">
          <AnimatePresence mode="wait">
            <motion.div
              key={selectedView}
              variants={viewVariants}
              initial="initial"
              animate="animate"
              exit="exit"
              className="h-full"
            >
              <Suspense fallback={<ViewLoader />}>
                {ViewComponent ? <ViewComponent data={results[selectedView]} /> : null}
              </Suspense>
            </motion.div>
          </AnimatePresence>
        </div>
      )}
    </main>
  );
};

export default ObservationCanvas;
