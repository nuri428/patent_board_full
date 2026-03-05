import { useCallback } from 'react';

export const usePDFExport = () => {
  const exportToPDF = useCallback(async ({ targetRef, fileName, onError }) => {
    if (!targetRef?.current) return;

    try {
      const [{ default: html2canvas }, { jsPDF }] = await Promise.all([
        import('html2canvas'),
        import('jspdf'),
      ]);

      // C2: DOM 면적에 따라 scale 자동 조절 (메모리 안전화)
      // 1,000,000 px²(약 1000×1000) 초과 시 고해상도 렌더링 생략
      const HIGH_RES_AREA_THRESHOLD = 1_000_000;
      const el = targetRef.current;
      const area = el.offsetWidth * el.offsetHeight;
      const scale = area > HIGH_RES_AREA_THRESHOLD ? 1 : 2;

      const canvas = await html2canvas(el, {
        scale,
        useCORS: true,
        backgroundColor: '#f8fafc',
        logging: false,
      });

      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' });

      const pageWidth = pdf.internal.pageSize.getWidth();
      const pageHeight = pdf.internal.pageSize.getHeight();
      const imgRatio = canvas.height / canvas.width;
      const imgHeight = pageWidth * imgRatio;

      pdf.addImage(imgData, 'PNG', 0, 0, pageWidth, Math.min(imgHeight, pageHeight - 16));

      pdf.setFontSize(7);
      pdf.setTextColor(160);
      pdf.text(
        'This system provides observational signals with evidence. It does not prescribe investment or strategic actions.',
        10,
        pageHeight - 6
      );

      pdf.save(fileName);
    } catch (err) {
      console.error('[PDFExporter] Export failed:', err);
      onError?.(err);
    }
  }, []);

  return { exportToPDF };
};
