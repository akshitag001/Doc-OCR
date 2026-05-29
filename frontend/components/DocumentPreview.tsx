"use client";

import { useState, useRef, useEffect } from "react";
import { Card } from "./ui/card";

interface OCRBlock {
  text: string;
  confidence: number;
  bbox: [number, number, number, number]; // [x, y, w, h]
}

interface DocumentPreviewProps {
  fileUrl?: string;
  blocks?: OCRBlock[];
}

export default function DocumentPreview({ fileUrl, blocks = [] }: DocumentPreviewProps) {
  const [dimensions, setDimensions] = useState<{
    width: number;
    height: number;
    naturalWidth: number;
    naturalHeight: number;
  } | null>(null);

  const [hoveredBlockIndex, setHoveredBlockIndex] = useState<number | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const imageRef = useRef<HTMLImageElement>(null);

  // Recalculate dimensions on window resize to ensure highlights align
  useEffect(() => {
    const handleResize = () => {
      if (imageRef.current) {
        const img = imageRef.current;
        if (img.complete && img.naturalWidth) {
          setDimensions({
            width: img.clientWidth,
            height: img.clientHeight,
            naturalWidth: img.naturalWidth,
            naturalHeight: img.naturalHeight,
          });
        }
      }
    };

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const handleImageLoad = (e: React.SyntheticEvent<HTMLImageElement>) => {
    const img = e.currentTarget;
    setDimensions({
      width: img.clientWidth,
      height: img.clientHeight,
      naturalWidth: img.naturalWidth,
      naturalHeight: img.naturalHeight,
    });
  };

  const renderOverlays = () => {
    if (!dimensions || !blocks || blocks.length === 0) return null;

    const scaleX = dimensions.width / dimensions.naturalWidth;
    const scaleY = dimensions.height / dimensions.naturalHeight;

    return blocks.map((block, index) => {
      const [x, y, w, h] = block.bbox;

      // Map to scaled display coordinates
      const left = x * scaleX;
      const top = y * scaleY;
      const width = w * scaleX;
      const height = h * scaleY;

      return (
        <div
          key={index}
          className="absolute border border-yellow-400/30 bg-yellow-300/10 hover:bg-yellow-300/30 hover:border-yellow-500/80 rounded-[2px] transition-all cursor-pointer group"
          style={{
            left: `${left}px`,
            top: `${top}px`,
            width: `${width}px`,
            height: `${height}px`,
            zIndex: hoveredBlockIndex === index ? 30 : 10,
          }}
          onMouseEnter={() => setHoveredBlockIndex(index)}
          onMouseLeave={() => setHoveredBlockIndex(null)}
        >
          {/* Tooltip Overlay */}
          <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-1 hidden group-hover:block bg-slate-900 text-white text-xs font-semibold px-2 py-1 rounded shadow-md whitespace-nowrap z-50 pointer-events-none">
            <span className="opacity-90">{block.text}</span>
            <span className="ml-1.5 text-[10px] text-yellow-400 font-mono">({Math.round(block.confidence)}%)</span>
          </div>
        </div>
      );
    });
  };

  return (
    <Card className="p-4 flex flex-col items-center justify-center bg-card shadow-sm border border-border overflow-hidden">
      <div className="w-full flex items-center justify-between mb-3 border-b pb-2">
        <h3 className="font-semibold text-sm text-foreground">Document Source Preview</h3>
        {blocks.length > 0 && (
          <span className="text-[11px] text-muted-foreground bg-accent px-2 py-0.5 rounded-full font-mono">
            {blocks.length} Text Blocks Detected
          </span>
        )}
      </div>

      {fileUrl ? (
        <div 
          ref={containerRef} 
          className="relative max-w-full flex items-center justify-center rounded border bg-slate-50 dark:bg-slate-950/40 p-1"
          style={{ minHeight: "260px" }}
        >
          <img
            ref={imageRef}
            src={fileUrl}
            alt="Processed document preview"
            onLoad={handleImageLoad}
            className="max-h-[500px] object-contain w-auto select-none rounded-[3px]"
            draggable={false}
          />
          {renderOverlays()}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center h-64 text-center p-6 border-2 border-dashed border-muted rounded">
          <span className="text-2xl mb-1">📄</span>
          <div className="text-sm font-medium text-muted-foreground">Original Preview Not Available</div>
          <p className="text-xs text-muted-foreground/75 mt-1 max-w-[200px]">
            Preview will load once processing finishes successfully.
          </p>
        </div>
      )}
      
      {blocks.length > 0 && (
        <p className="text-[10px] text-muted-foreground mt-3 text-center w-full">
          💡 Hover over text regions in the document to see raw OCR OCR extraction confidence.
        </p>
      )}
    </Card>
  );
}
