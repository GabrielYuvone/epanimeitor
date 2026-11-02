"use client";

import { useRef, useEffect, useState, useCallback } from "react";
import { loadImage, drawFrameToCanvas } from "@/lib/animation/utils";
import { CANVAS_W, CANVAS_H, type ToolId } from "@/lib/animation/types";

interface DrawingCanvasProps {
  frameData: string;
  bgColor: string;
  tool: ToolId;
  color: string;
  brushSize: number;
  onionSkin: boolean;
  prevFrameData?: string;
  onCommit: (dataUrl: string) => void;
}

export default function DrawingCanvas({
  frameData,
  bgColor,
  tool,
  color,
  brushSize,
  onionSkin,
  prevFrameData,
  onCommit,
}: DrawingCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const previewRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const isDrawing = useRef(false);
  const lastPoint = useRef<{ x: number; y: number } | null>(null);
  const startPoint = useRef<{ x: number; y: number } | null>(null);
  const [scale, setScale] = useState(1);

  // Resize observer para responsive
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    const ro = new ResizeObserver(() => {
      const w = container.clientWidth;
      const s = Math.min(1, w / CANVAS_W);
      setScale(s);
    });
    ro.observe(container);
    return () => ro.disconnect();
  }, []);

  // Cargar frame y fondo
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    let cancelled = false;
    (async () => {
      await drawFrameToCanvas(canvas, frameData, "transparent");
      if (!cancelled) {
        // canvas principal ya tiene el frame
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [frameData]);

  const getPos = (e: React.PointerEvent) => {
    const canvas = canvasRef.current!;
    const rect = canvas.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * CANVAS_W;
    const y = ((e.clientY - rect.top) / rect.height) * CANVAS_H;
    return { x: Math.round(x), y: Math.round(y) };
  };

  // fill (bucket)
  const floodFill = useCallback(
    (ctx: CanvasRenderingContext2D, sx: number, sy: number, fillColor: string) => {
      const imgData = ctx.getImageData(0, 0, CANVAS_W, CANVAS_H);
      const data = imgData.data;
      const w = CANVAS_W;
      const h = CANVAS_H;
      const startIdx = (sy * w + sx) * 4;
      const startR = data[startIdx];
      const startG = data[startIdx + 1];
      const startB = data[startIdx + 2];
      const startA = data[startIdx + 3];

      const fill = hexToRgba(fillColor);
      if (
        startR === fill.r &&
        startG === fill.g &&
        startB === fill.b &&
        startA === fill.a
      )
        return;

      const stack: [number, number][] = [[sx, sy]];
      const tol = 32;
      const match = (idx: number) =>
        Math.abs(data[idx] - startR) <= tol &&
        Math.abs(data[idx + 1] - startG) <= tol &&
        Math.abs(data[idx + 2] - startB) <= tol &&
        Math.abs(data[idx + 3] - startA) <= tol;

      while (stack.length) {
        const [x, y] = stack.pop()!;
        if (x < 0 || y < 0 || x >= w || y >= h) continue;
        const idx = (y * w + x) * 4;
        if (!match(idx)) continue;
        data[idx] = fill.r;
        data[idx + 1] = fill.g;
        data[idx + 2] = fill.b;
        data[idx + 3] = fill.a;
        stack.push([x + 1, y], [x - 1, y], [x, y + 1], [x, y - 1]);
      }
      ctx.putImageData(imgData, 0, 0);
    },
    []
  );

  const startDrawing = (e: React.PointerEvent) => {
    e.preventDefault();
    (e.target as HTMLElement).setPointerCapture(e.pointerId);
    isDrawing.current = true;
    const p = getPos(e);
    lastPoint.current = p;
    startPoint.current = p;
    const ctx = canvasRef.current!.getContext("2d")!;

    if (tool === "fill") {
      floodFill(ctx, p.x, p.y, color);
      isDrawing.current = false;
      onCommit(canvasRef.current!.toDataURL("image/png"));
      return;
    }

    if (tool === "pencil" || tool === "brush" || tool === "eraser") {
      // punto inicial
      drawDot(ctx, p);
    }
    // Para line/rect/circle, el preview se dibuja en previewRef
  };

  const drawDot = (ctx: CanvasRenderingContext2D, p: { x: number; y: number }) => {
    const r = (tool === "eraser" ? brushSize : brushSize) / 2;
    ctx.save();
    if (tool === "eraser") {
      ctx.globalCompositeOperation = "destination-out";
      ctx.fillStyle = "rgba(0,0,0,1)";
    } else {
      ctx.globalCompositeOperation = "source-over";
      ctx.fillStyle = color;
    }
    ctx.beginPath();
    ctx.arc(p.x, p.y, Math.max(0.5, r), 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  };

  const drawLineSegment = (
    ctx: CanvasRenderingContext2D,
    from: { x: number; y: number },
    to: { x: number; y: number }
  ) => {
    ctx.save();
    if (tool === "eraser") {
      ctx.globalCompositeOperation = "destination-out";
      ctx.strokeStyle = "rgba(0,0,0,1)";
    } else {
      ctx.globalCompositeOperation = "source-over";
      ctx.strokeStyle = color;
    }
    ctx.lineWidth = tool === "pencil" ? Math.max(1, brushSize * 0.6) : brushSize;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.beginPath();
    ctx.moveTo(from.x, from.y);
    ctx.lineTo(to.x, to.y);
    ctx.stroke();
    ctx.restore();
  };

  const move = (e: React.PointerEvent) => {
    if (!isDrawing.current) return;
    const p = getPos(e);
    const ctx = canvasRef.current!.getContext("2d")!;
    const previewCanvas = previewRef.current!;
    const pctx = previewCanvas.getContext("2d")!;

    if (tool === "pencil" || tool === "brush" || tool === "eraser") {
      if (lastPoint.current) {
        drawLineSegment(ctx, lastPoint.current, p);
      }
      lastPoint.current = p;
    } else if (tool === "line" || tool === "rectangle" || tool === "circle") {
      // dibujar en preview
      pctx.clearRect(0, 0, CANVAS_W, CANVAS_H);
      pctx.save();
      pctx.strokeStyle = color;
      pctx.lineWidth = brushSize;
      pctx.lineCap = "round";
      pctx.lineJoin = "round";
      const sp = startPoint.current!;
      if (tool === "line") {
        pctx.beginPath();
        pctx.moveTo(sp.x, sp.y);
        pctx.lineTo(p.x, p.y);
        pctx.stroke();
      } else if (tool === "rectangle") {
        pctx.strokeRect(
          Math.min(sp.x, p.x),
          Math.min(sp.y, p.y),
          Math.abs(p.x - sp.x),
          Math.abs(p.y - sp.y)
        );
      } else if (tool === "circle") {
        const cx = (sp.x + p.x) / 2;
        const cy = (sp.y + p.y) / 2;
        const rx = Math.abs(p.x - sp.x) / 2;
        const ry = Math.abs(p.y - sp.y) / 2;
        pctx.beginPath();
        pctx.ellipse(cx, cy, Math.max(1, rx), Math.max(1, ry), 0, 0, Math.PI * 2);
        pctx.stroke();
      }
      pctx.restore();
    }
  };

  const endDrawing = (e: React.PointerEvent) => {
    if (!isDrawing.current) return;
    isDrawing.current = false;
    (e.target as HTMLElement).releasePointerCapture(e.pointerId);
    const ctx = canvasRef.current!.getContext("2d")!;
    const pctx = previewRef.current!.getContext("2d")!;

    if (tool === "line" || tool === "rectangle" || tool === "circle") {
      // mezclar preview al canvas principal
      ctx.drawImage(previewRef.current!, 0, 0);
      pctx.clearRect(0, 0, CANVAS_W, CANVAS_H);
    }

    lastPoint.current = null;
    startPoint.current = null;
    onCommit(canvasRef.current!.toDataURL("image/png"));
  };

  // Dibujar onion skin en preview cuando no se está dibujando
  useEffect(() => {
    if (!onionSkin || !prevFrameData) return;
    const pc = previewRef.current;
    if (!pc) return;
    const pctx = pc.getContext("2d")!;
    pctx.clearRect(0, 0, CANVAS_W, CANVAS_H);
    loadImage(prevFrameData).then((img) => {
      pctx.save();
      pctx.globalAlpha = 0.3;
      pctx.drawImage(img, 0, 0, CANVAS_W, CANVAS_H);
      pctx.restore();
    });
  }, [onionSkin, prevFrameData]);

  // Limpiar onion skin cuando se desactiva
  useEffect(() => {
    if (!onionSkin && previewRef.current && !isDrawing.current) {
      const pctx = previewRef.current.getContext("2d")!;
      pctx.clearRect(0, 0, CANVAS_W, CANVAS_H);
    }
  }, [onionSkin]);

  return (
    <div
      ref={containerRef}
      className="relative w-full select-none"
      style={{ aspectRatio: `${CANVAS_W} / ${CANVAS_H}` }}
    >
      <div
        className="absolute inset-0 rounded-2xl overflow-hidden shadow-inner ring-1 ring-black/10"
        style={{ background: bgColor === "transparent" ? "transparent" : bgColor }}
      >
        {/* Patrón checkerboard si transparente */}
        {bgColor === "transparent" && (
          <div
            className="absolute inset-0"
            style={{
              backgroundImage:
                "linear-gradient(45deg, #e2e8f0 25%, transparent 25%), linear-gradient(-45deg, #e2e8f0 25%, transparent 25%), linear-gradient(45deg, transparent 75%, #e2e8f0 75%), linear-gradient(-45deg, transparent 75%, #e2e8f0 75%)",
              backgroundSize: "20px 20px",
              backgroundPosition: "0 0, 0 10px, 10px -10px, -10px 0",
            }}
          />
        )}
        <canvas
          ref={canvasRef}
          width={CANVAS_W}
          height={CANVAS_H}
          className="absolute inset-0 w-full h-full touch-none"
          style={{ cursor: tool === "fill" ? "crosshair" : "crosshair" }}
          onPointerDown={startDrawing}
          onPointerMove={move}
          onPointerUp={endDrawing}
          onPointerCancel={endDrawing}
        />
        <canvas
          ref={previewRef}
          width={CANVAS_W}
          height={CANVAS_H}
          className="absolute inset-0 w-full h-full pointer-events-none"
        />
      </div>
      <div className="absolute top-2 right-2 text-[10px] uppercase tracking-wider bg-black/50 text-white px-2 py-1 rounded-full pointer-events-none">
        {CANVAS_W}×{CANVAS_H}
      </div>
    </div>
  );
}

function hexToRgba(hex: string) {
  hex = hex.replace("#", "");
  if (hex.length === 3) {
    hex = hex
      .split("")
      .map((c) => c + c)
      .join("");
  }
  const r = parseInt(hex.slice(0, 2), 16) || 0;
  const g = parseInt(hex.slice(2, 4), 16) || 0;
  const b = parseInt(hex.slice(4, 6), 16) || 0;
  return { r, g, b, a: 255 };
}
