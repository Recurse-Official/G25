import React, { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';
import { TransformWrapper, TransformComponent } from 'react-zoom-pan-pinch';
import { ZoomIn, ZoomOut, RefreshCw, Download } from 'lucide-react';

const MermaidViewer = ({ diagram }) => {
  const [svgContent, setSvgContent] = useState('');
  const [error, setError] = useState(null);
  const uniqueId = useRef(`mermaid-${Date.now()}`);

  useEffect(() => {
    if (!diagram) {
      setError('No diagram content provided');
      return;
    }

    const renderDiagram = async () => {
      try {
        mermaid.initialize({
          startOnLoad: false,
          theme: 'default',
          securityLevel: 'loose',
          fontSize: 16,
          displayMode: true,
          gantt: { useWidth: 1600 },
          flowchart: {
            htmlLabels: true,
            curve: 'basis',
            diagramPadding: 8
          }
        });

        const cleanDiagram = diagram.trim().replace(/\r\n/g, '\n');
        const { svg } = await mermaid.render(uniqueId.current, cleanDiagram);
        const modifiedSvg = svg.replace(
          '<svg ',
          '<svg style="max-width: 100%; width: 100%; height: 100%;" preserveAspectRatio="xMidYMid meet" '
        );
        setSvgContent(modifiedSvg);
        setError(null);
      } catch (err) {
        console.error('Mermaid rendering error:', err);
        setError(`Error rendering diagram: ${err.message}`);
      }
    };

    renderDiagram();
  }, [diagram]);

  const downloadImage = async (type) => {
    const svgElement = document.querySelector('#container svg');
    if (!svgElement) return;

    if (type === 'svg') {
      // Download as SVG
      const svgData = new XMLSerializer().serializeToString(svgElement);
      const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
      const url = URL.createObjectURL(svgBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'diagram.svg';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } 
  };

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
        <p className="text-red-600">{error}</p>
        <pre className="mt-2 text-sm text-gray-600 overflow-auto">
          {diagram}
        </pre>
      </div>
    );
  }

  return (
    <div className="w-full h-[100%] bg-white p-4">
      <TransformWrapper
        initialScale={0.7}
        minScale={0.1}
        maxScale={10}
        centerOnInit={true}
        smooth={true}
        pinch={{ disabled: true }}
        zoomAnimation={{ disabled: false }}
        alignmentAnimation={{ disabled: false }}
        velocityAnimation={{ disabled: true }}
      >
        {({ zoomIn, zoomOut, resetTransform }) => (
          <>
            <div className="flex justify-between items-center mb-4">
              <div className="flex gap-2">
                <button
                  onClick={() => zoomIn(0.1)}
                  className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
                  title="Zoom In"
                >
                  <ZoomIn className="w-5 h-5" />
                </button>
                <button
                  onClick={() => zoomOut(0.1)}
                  className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
                  title="Zoom Out"
                >
                  <ZoomOut className="w-5 h-5" />
                </button>
                <button
                  onClick={() => resetTransform()}
                  className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
                  title="Reset"
                >
                  <RefreshCw className="w-5 h-5" />
                </button>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => downloadImage('svg')}
                  className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors"
                  title="Download SVG"
                >
                  <Download className="w-4 h-4" />
                  SVG
                </button>
              </div>
            </div>
            <TransformComponent
              wrapperStyle={{
                width: "100%",
                height: "calc(100% - 60px)",
              }}
              contentStyle={{
                width: "100%",
                height: "100%"
              }}
            >
              {svgContent && (
                <div 
                  id='container'
                  className="w-full h-full flex items-center justify-center"
                  dangerouslySetInnerHTML={{ __html: svgContent }}
                />
              )}
            </TransformComponent>
          </>
        )}
      </TransformWrapper>
    </div>
  );
};

export default MermaidViewer;