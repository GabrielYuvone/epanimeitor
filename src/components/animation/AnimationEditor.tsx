"use client";

import { useState, useRef, useCallback, useEffect, ReactNode } from "react";
import {
  Pencil,
  Brush,
  Eraser,
  Slash,
  Square,
  Circle,
  PaintBucket,
  Play,
  Pause,
  SkipBack,
  SkipForward,
  Plus,
  Copy,
  Trash2,
  Undo2,
  Redo2,
  Download,
  Upload,
  FilePlus2,
  Layers,
  HelpCircle,
  ChevronUp,
  ChevronDown,
  Eye,
  EyeOff,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import DrawingCanvas from "./DrawingCanvas";
import {
  DEFAULT_PALETTE,
  BG_PRESETS,
  CANVAS_W,
  CANVAS_H,
  type ToolId,
  type Frame,
  type AnimationProject,
} from "@/lib/animation/types";
import {
  uid,
  emptyFrameData,
  exportGif,
  downloadBlob,
  downloadText,
  loadImage,
  drawFrameToCanvas,
} from "@/lib/animation/utils";

interface ToolDef {
  id: ToolId;
  label: string;
  icon: ReactNode;
  hint: string;
  key: string;
}

const TOOLS: ToolDef[] = [
  { id: "pencil", label: "Lápiz", icon: <Pencil size={20} />, hint: "Trazo fino", key: "1" },
  { id: "brush", label: "Pincel", icon: <Brush size={20} />, hint: "Trazo suave grueso", key: "2" },
  { id: "eraser", label: "Borrador", icon: <Eraser size={20} />, hint: "Borra con el tamaño del pincel", key: "3" },
  { id: "line", label: "Línea", icon: <Slash size={20} />, hint: "Línea recta", key: "4" },
  { id: "rectangle", label: "Rectángulo", icon: <Square size={20} />, hint: "Marco rectangular", key: "5" },
  { id: "circle", label: "Círculo", icon: <Circle size={20} />, hint: "Elipse", key: "6" },
  { id: "fill", label: "Relleno", icon: <PaintBucket size={20} />, hint: "Rellena un área", key: "7" },
];

export default function AnimationEditor() {
  const [frames, setFrames] = useState<Frame[]>(() => [
    { id: uid(), data: emptyFrameData(), duration: 100 },
  ]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [tool, setTool] = useState<ToolId>("pencil");
  const [color, setColor] = useState("#1a1a1a");
  const [brushSize, setBrushSize] = useState(8);
  const [bgColor, setBgColor] = useState("#FFFFFF");
  const [fps, setFps] = useState(8);
  const [onionSkin, setOnionSkin] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [customColor, setCustomColor] = useState("#FF6B6B");
  const [showHelp, setShowHelp] = useState(false);

  // Undo / Redo (snapshots de toda la secuencia)
  const [undoStack, setUndoStack] = useState<Frame[][]>([]);
  const [redoStack, setRedoStack] = useState<Frame[][]>([]);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const playTimerRef = useRef<number | null>(null);

  const currentFrame = frames[currentIdx];
  const prevFrame = currentIdx > 0 ? frames[currentIdx - 1] : undefined;

  // Snapshot para undo
  const pushUndo = useCallback(() => {
    setUndoStack((s) => [...s.slice(-30), frames.map((f) => ({ ...f }))]);
    setRedoStack([]);
  }, [frames]);

  const undo = () => {
    setUndoStack((s) => {
      if (s.length === 0) return s;
      const last = s[s.length - 1];
      setRedoStack((r) => [...r, frames.map((f) => ({ ...f }))]);
      setFrames(last);
      setCurrentIdx((i) => Math.min(i, last.length - 1));
      return s.slice(0, -1);
    });
  };

  const redo = () => {
    setRedoStack((r) => {
      if (r.length === 0) return r;
      const last = r[r.length - 1];
      setUndoStack((s) => [...s.slice(-30), frames.map((f) => ({ ...f }))]);
      setFrames(last);
      setCurrentIdx((i) => Math.min(i, last.length - 1));
      return r.slice(0, -1);
    });
  };

  // Actualizar frame actual cuando el usuario dibuja
  const commitFrame = useCallback(
    (dataUrl: string) => {
      setFrames((fs) =>
        fs.map((f, i) => (i === currentIdx ? { ...f, data: dataUrl } : f))
      );
    },
    [currentIdx]
  );

  // Operaciones de frames
  const addFrame = () => {
    pushUndo();
    const newF: Frame = { id: uid(), data: emptyFrameData(), duration: 100 };
    setFrames((fs) => {
      const newFs = [...fs];
      newFs.splice(currentIdx + 1, 0, newF);
      return newFs;
    });
    setCurrentIdx((i) => i + 1);
  };

  const duplicateFrame = () => {
    pushUndo();
    const cur = frames[currentIdx];
    const newF: Frame = { id: uid(), data: cur.data, duration: cur.duration };
    setFrames((fs) => {
      const newFs = [...fs];
      newFs.splice(currentIdx + 1, 0, newF);
      return newFs;
    });
    setCurrentIdx((i) => i + 1);
  };

  const deleteFrame = () => {
    if (frames.length <= 1) return;
    pushUndo();
    setFrames((fs) => fs.filter((_, i) => i !== currentIdx));
    setCurrentIdx((i) => Math.max(0, Math.min(i, frames.length - 2)));
  };

  const clearFrame = () => {
    pushUndo();
    setFrames((fs) =>
      fs.map((f, i) => (i === currentIdx ? { ...f, data: emptyFrameData() } : f))
    );
  };

  const moveFrame = (dir: -1 | 1) => {
    const target = currentIdx + dir;
    if (target < 0 || target >= frames.length) return;
    pushUndo();
    setFrames((fs) => {
      const newFs = [...fs];
      [newFs[currentIdx], newFs[target]] = [newFs[target], newFs[currentIdx]];
      return newFs;
    });
    setCurrentIdx(target);
  };

  const setAsFirst = () => {
    if (currentIdx === 0) return;
    pushUndo();
    setFrames((fs) => {
      const newFs = [...fs];
      const [f] = newFs.splice(currentIdx, 1);
      newFs.unshift(f);
      return newFs;
    });
    setCurrentIdx(0);
  };

  // Playback
  useEffect(() => {
    if (!isPlaying) {
      if (playTimerRef.current) {
        clearTimeout(playTimerRef.current);
        playTimerRef.current = null;
      }
      return;
    }
    const delay = Math.max(20, Math.round(1000 / fps));
    playTimerRef.current = window.setTimeout(() => {
      setCurrentIdx((i) => (i + 1) % frames.length);
    }, delay);
    return () => {
      if (playTimerRef.current) clearTimeout(playTimerRef.current);
    };
  }, [isPlaying, currentIdx, fps, frames.length]);

  const togglePlay = () => {
    if (frames.length < 2) return;
    setIsPlaying((p) => !p);
  };

  const prevFrameBtn = () => {
    setIsPlaying(false);
    setCurrentIdx((i) => (i - 1 + frames.length) % frames.length);
  };
  const nextFrameBtn = () => {
    setIsPlaying(false);
    setCurrentIdx((i) => (i + 1) % frames.length);
  };

  // File actions
  const newAnimation = () => {
    if (frames.length > 1 || currentFrame.data !== emptyFrameData()) {
      if (!confirm("¿Empezar una animación nueva? Se perderán los cambios sin guardar.")) {
        return;
      }
    }
    setFrames([{ id: uid(), data: emptyFrameData(), duration: 100 }]);
    setCurrentIdx(0);
    setUndoStack([]);
    setRedoStack([]);
    setIsPlaying(false);
  };

  const saveProject = () => {
    const project: AnimationProject = {
      name: "mi-animacion",
      width: CANVAS_W,
      height: CANVAS_H,
      bgColor,
      fps,
      onionSkin,
      frames,
    };
    downloadText(JSON.stringify(project, null, 2), "animacion.json");
  };

  const loadProject = () => {
    fileInputRef.current?.click();
  };

  const handleFileLoad = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const text = await file.text();
      const project = JSON.parse(text) as AnimationProject;
      if (!project.frames || !Array.isArray(project.frames)) {
        throw new Error("Formato inválido");
      }
      setFrames(project.frames);
      setCurrentIdx(0);
      setBgColor(project.bgColor || "#FFFFFF");
      setFps(project.fps || 8);
      setUndoStack([]);
      setRedoStack([]);
      setIsPlaying(false);
    } catch (err) {
      alert("No se pudo cargar el archivo: " + (err as Error).message);
    }
    e.target.value = "";
  };

  const [exporting, setExporting] = useState(false);
  const exportGifFile = async () => {
    setExporting(true);
    try {
      const blob = await exportGif(frames, bgColor, fps);
      downloadBlob(blob, `animacion-${Date.now()}.gif`);
    } catch (err) {
      alert("Error al exportar: " + (err as Error).message);
    } finally {
      setExporting(false);
    }
  };

  // Atajos de teclado
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const tgt = e.target as HTMLElement;
      if (tgt.tagName === "INPUT" || tgt.tagName === "TEXTAREA") return;

      if (e.ctrlKey || e.metaKey) {
        if (e.key === "z" && !e.shiftKey) {
          e.preventDefault();
          undo();
        } else if ((e.key === "z" && e.shiftKey) || e.key === "y") {
          e.preventDefault();
          redo();
        } else if (e.key === "s") {
          e.preventDefault();
          saveProject();
        } else if (e.key === "e") {
          e.preventDefault();
          exportGifFile();
        }
        return;
      }
      if (e.key === " ") {
        e.preventDefault();
        togglePlay();
      } else if (e.key === "n") {
        addFrame();
      } else if (e.key === "d") {
        duplicateFrame();
      } else if (e.key === "o") {
        setOnionSkin((s) => !s);
      } else if (e.key === "j") {
        prevFrameBtn();
      } else if (e.key === "k") {
        nextFrameBtn();
      } else if (/^[1-7]$/.test(e.key)) {
        setTool(TOOLS[parseInt(e.key) - 1].id);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [frames, currentIdx, fps, onionSkin]);

  return (
    <TooltipProvider delayDuration={300}>
      <div className="min-h-screen flex flex-col bg-gradient-to-br from-rose-50 via-amber-50 to-sky-50">
        {/* ====== TOP BAR ====== */}
        <header className="sticky top-0 z-30 backdrop-blur-md bg-white/70 border-b border-black/5 shadow-sm">
          <div className="max-w-[1400px] mx-auto px-4 py-3 flex items-center gap-3 flex-wrap">
            <div className="flex items-center gap-2 mr-2">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-pink-500 via-orange-400 to-yellow-400 flex items-center justify-center shadow-md">
                <Play size={18} className="text-white" fill="white" />
              </div>
              <div className="leading-tight">
                <div className="font-extrabold text-lg text-slate-800 tracking-tight">
                  FrameFiesta
                </div>
                <div className="text-[10px] text-slate-500 -mt-0.5">
                  animador frame a frame
                </div>
              </div>
            </div>

            <div className="flex items-center gap-1.5 ml-auto">
              <ActionBtn onClick={newAnimation} icon={<FilePlus2 size={16} />} label="Nuevo" />
              <ActionBtn onClick={saveProject} icon={<Download size={16} />} label="Guardar" />
              <ActionBtn onClick={loadProject} icon={<Upload size={16} />} label="Cargar" />
              <ActionBtn
                onClick={exportGifFile}
                icon={exporting ? <span className="animate-pulse">…</span> : <Download size={16} />}
                label={exporting ? "Exportando…" : "GIF"}
                primary
              />
              <Dialog open={showHelp} onOpenChange={setShowHelp}>
                <DialogTrigger asChild>
                  <Button variant="ghost" size="sm" className="gap-1.5 text-slate-600">
                    <HelpCircle size={16} /> Ayuda
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-md">
                  <DialogHeader>
                    <DialogTitle>Atajos y tips</DialogTitle>
                  </DialogHeader>
                  <div className="text-sm text-slate-700 space-y-2">
                    <p><b>Espacio</b> – Reproducir / pausar</p>
                    <p><b>N</b> – Nuevo fotograma · <b>D</b> – Duplicar · <b>O</b> – Onion skin</p>
                    <p><b>J / K</b> – Fotograma anterior / siguiente</p>
                    <p><b>1-7</b> – Seleccionar herramienta</p>
                    <p><b>Ctrl/⌘ + Z</b> – Deshacer · <b>Ctrl/⌘ + Shift + Z</b> – Rehacer</p>
                    <p><b>Ctrl/⌘ + S</b> – Guardar · <b>Ctrl/⌘ + E</b> – Exportar GIF</p>
                    <hr className="my-2" />
                    <p className="text-xs text-slate-500">
                      Tip: activa <b>onion skin</b> para ver el fotograma anterior en
                      transparente y animar con más precisión.
                    </p>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
          </div>
        </header>

        {/* ====== MAIN LAYOUT ====== */}
        <main className="flex-1 max-w-[1400px] w-full mx-auto px-3 lg:px-4 py-4">
          <div className="grid grid-cols-1 lg:grid-cols-[auto_1fr_280px] gap-4">
            {/* ----- Left toolbar ----- */}
            <aside className="lg:w-[68px] w-full">
              <ToolRail
                tools={TOOLS}
                active={tool}
                onChange={setTool}
                onUndo={undo}
                onRedo={redo}
                canUndo={undoStack.length > 0}
                canRedo={redoStack.length > 0}
              />
            </aside>

            {/* ----- Canvas area ----- */}
            <section className="flex flex-col gap-3 min-w-0">
              <div className="bg-white rounded-2xl shadow-sm border border-black/5 p-3 lg:p-4">
                <DrawingCanvas
                  frameData={currentFrame.data}
                  bgColor={bgColor}
                  tool={tool}
                  color={color}
                  brushSize={brushSize}
                  onionSkin={onionSkin}
                  prevFrameData={prevFrame?.data}
                  onCommit={(data) => {
                    pushUndo();
                    commitFrame(data);
                  }}
                />
              </div>

              {/* Playback bar */}
              <div className="bg-white rounded-2xl shadow-sm border border-black/5 px-3 py-2 flex items-center gap-2 flex-wrap">
                <Button size="sm" variant="ghost" onClick={prevFrameBtn} className="px-2">
                  <SkipBack size={16} />
                </Button>
                <Button
                  size="sm"
                  onClick={togglePlay}
                  disabled={frames.length < 2}
                  className="px-3 bg-gradient-to-br from-pink-500 to-orange-500 hover:opacity-90 text-white shadow-sm"
                >
                  {isPlaying ? <Pause size={16} /> : <Play size={16} />}
                  {isPlaying ? "Pausar" : "Reproducir"}
                </Button>
                <Button size="sm" variant="ghost" onClick={nextFrameBtn} className="px-2">
                  <SkipForward size={16} />
                </Button>
                <div className="text-sm text-slate-600 ml-2 tabular-nums">
                  Fotograma <b className="text-slate-800">{currentIdx + 1}</b> / {frames.length}
                </div>
                <div className="flex items-center gap-2 ml-auto">
                  <span className="text-xs text-slate-500 uppercase tracking-wide">FPS</span>
                  <Slider
                    value={[fps]}
                    min={1}
                    max={24}
                    step={1}
                    onValueChange={(v) => setFps(v[0])}
                    className="w-24"
                  />
                  <span className="text-sm font-semibold text-slate-700 w-6 tabular-nums">{fps}</span>
                </div>
              </div>

              {/* Timeline */}
              <Timeline
                frames={frames}
                currentIdx={currentIdx}
                bgColor={bgColor}
                onSelect={(i) => {
                  setIsPlaying(false);
                  setCurrentIdx(i);
                }}
                onAdd={addFrame}
                onDuplicate={duplicateFrame}
                onDelete={deleteFrame}
                onClear={clearFrame}
                onMove={moveFrame}
                onSetFirst={setAsFirst}
              />
            </section>

            {/* ----- Right panel ----- */}
            <aside className="w-full lg:w-[280px]">
              <RightPanel
                color={color}
                setColor={setColor}
                customColor={customColor}
                setCustomColor={setCustomColor}
                brushSize={brushSize}
                setBrushSize={setBrushSize}
                bgColor={bgColor}
                setBgColor={setBgColor}
                onionSkin={onionSkin}
                setOnionSkin={setOnionSkin}
                fps={fps}
                setFps={setFps}
              />
            </aside>
          </div>
        </main>

        <input
          ref={fileInputRef}
          type="file"
          accept=".json,application/json"
          className="hidden"
          onChange={handleFileLoad}
        />

        <footer className="border-t border-black/5 bg-white/60 backdrop-blur-sm py-3 mt-4">
          <div className="max-w-[1400px] mx-auto px-4 text-center text-xs text-slate-500">
            FrameFiesta · Hecho con cariño para animar rapidito · Atajos con <kbd className="px-1 bg-slate-100 rounded">?</kbd> en el botón Ayuda
          </div>
        </footer>
      </div>
    </TooltipProvider>
  );
}

// ===================== Subcomponentes =====================

function ActionBtn({
  onClick,
  icon,
  label,
  primary,
}: {
  onClick: () => void;
  icon: ReactNode;
  label: string;
  primary?: boolean;
}) {
  return (
    <Button
      size="sm"
      variant={primary ? "default" : "outline"}
      onClick={onClick}
      className={
        primary
          ? "gap-1.5 bg-gradient-to-br from-emerald-500 to-teal-500 text-white hover:opacity-90 shadow-sm"
          : "gap-1.5 bg-white text-slate-700 hover:bg-slate-50"
      }
    >
      {icon}
      <span className="hidden sm:inline">{label}</span>
    </Button>
  );
}

function ToolRail({
  tools,
  active,
  onChange,
  onUndo,
  onRedo,
  canUndo,
  canRedo,
}: {
  tools: ToolDef[];
  active: ToolId;
  onChange: (id: ToolId) => void;
  onUndo: () => void;
  onRedo: () => void;
  canUndo: boolean;
  canRedo: boolean;
}) {
  return (
    <div className="lg:sticky lg:top-[80px] bg-white rounded-2xl shadow-sm border border-black/5 p-2 flex lg:flex-col gap-1.5 overflow-x-auto lg:overflow-visible">
      {tools.map((t) => {
        const isActive = active === t.id;
        return (
          <Tooltip key={t.id}>
            <TooltipTrigger asChild>
              <button
                onClick={() => onChange(t.id)}
                className={`relative shrink-0 w-12 h-12 rounded-xl flex flex-col items-center justify-center transition-all
                ${isActive
                    ? "bg-gradient-to-br from-pink-500 via-orange-400 to-yellow-400 text-white shadow-md scale-105"
                    : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                  }`}
                aria-label={t.label}
              >
                {t.icon}
                <span className="text-[8px] mt-0.5 hidden lg:block leading-none opacity-70">
                  {t.key}
                </span>
              </button>
            </TooltipTrigger>
            <TooltipContent side="right">
              <span className="font-medium">{t.label}</span> · <span className="text-slate-300">{t.hint}</span>
            </TooltipContent>
          </Tooltip>
        );
      })}
      <div className="lg:h-px lg:w-full h-px w-px bg-slate-200 my-1" />
      <Tooltip>
        <TooltipTrigger asChild>
          <button
            onClick={onUndo}
            disabled={!canUndo}
            className="shrink-0 w-12 h-12 rounded-xl flex items-center justify-center text-slate-600 hover:bg-slate-100 disabled:opacity-30"
            aria-label="Deshacer"
          >
            <Undo2 size={20} />
          </button>
        </TooltipTrigger>
        <TooltipContent side="right">Deshacer (Ctrl+Z)</TooltipContent>
      </Tooltip>
      <Tooltip>
        <TooltipTrigger asChild>
          <button
            onClick={onRedo}
            disabled={!canRedo}
            className="shrink-0 w-12 h-12 rounded-xl flex items-center justify-center text-slate-600 hover:bg-slate-100 disabled:opacity-30"
            aria-label="Rehacer"
          >
            <Redo2 size={20} />
          </button>
        </TooltipTrigger>
        <TooltipContent side="right">Rehacer (Ctrl+Shift+Z)</TooltipContent>
      </Tooltip>
    </div>
  );
}

function RightPanel({
  color,
  setColor,
  customColor,
  setCustomColor,
  brushSize,
  setBrushSize,
  bgColor,
  setBgColor,
  onionSkin,
  setOnionSkin,
  fps,
  setFps,
}: {
  color: string;
  setColor: (c: string) => void;
  customColor: string;
  setCustomColor: (c: string) => void;
  brushSize: number;
  setBrushSize: (n: number) => void;
  bgColor: string;
  setBgColor: (c: string) => void;
  onionSkin: boolean;
  setOnionSkin: (b: boolean) => void;
  fps: number;
  setFps: (n: number) => void;
}) {
  const [showPicker, setShowPicker] = useState(false);

  return (
    <div className="lg:sticky lg:top-[80px] space-y-3">
      {/* Color principal */}
      <Panel title="Color">
        <div className="grid grid-cols-8 gap-1.5">
          {DEFAULT_PALETTE.map((c) => (
            <button
              key={c}
              onClick={() => setColor(c)}
              className={`aspect-square rounded-md ring-1 ring-black/10 transition-all hover:scale-110
              ${color === c ? "ring-2 ring-slate-800 scale-110" : ""}`}
              style={{ background: c }}
              aria-label={`Color ${c}`}
            />
          ))}
        </div>
        <div className="mt-3 flex items-center gap-2">
          <div
            className="w-10 h-10 rounded-lg ring-1 ring-black/10 shrink-0"
            style={{ background: color }}
          />
          <div className="flex-1">
            <div className="text-xs text-slate-500 mb-0.5">Color actual</div>
            <div className="text-sm font-mono text-slate-700 uppercase">{color}</div>
          </div>
        </div>
        <button
          onClick={() => setShowPicker((s) => !s)}
          className="mt-2 w-full text-xs text-slate-600 hover:text-slate-900 flex items-center justify-center gap-1.5 py-1.5 rounded-lg hover:bg-slate-100"
        >
          <PaintBucket size={12} /> Color personalizado
        </button>
        {showPicker && (
          <div className="mt-2 flex items-center gap-2 p-2 bg-slate-50 rounded-lg">
            <input
              type="color"
              value={customColor}
              onChange={(e) => {
                setCustomColor(e.target.value);
                setColor(e.target.value);
              }}
              className="w-10 h-10 rounded-md cursor-pointer border-0 bg-transparent"
            />
            <input
              type="text"
              value={customColor}
              onChange={(e) => {
                setCustomColor(e.target.value);
                setColor(e.target.value);
              }}
              className="flex-1 text-xs font-mono px-2 py-1 border border-slate-200 rounded"
            />
          </div>
        )}
      </Panel>

      {/* Pincel */}
      <Panel title="Pincel">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-lg bg-slate-50 flex items-center justify-center shrink-0 ring-1 ring-black/5">
            <div
              className="rounded-full"
              style={{
                width: Math.min(brushSize, 36),
                height: Math.min(brushSize, 36),
                background: color,
              }}
            />
          </div>
          <div className="flex-1">
            <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
              <span>Tamaño</span>
              <span className="font-semibold text-slate-700 tabular-nums">{brushSize}px</span>
            </div>
            <Slider
              value={[brushSize]}
              min={1}
              max={50}
              step={1}
              onValueChange={(v) => setBrushSize(v[0])}
            />
          </div>
        </div>
      </Panel>

      {/* Fondo */}
      <Panel title="Fondo">
        <div className="grid grid-cols-5 gap-1.5">
          {BG_PRESETS.map((c) => (
            <button
              key={c}
              onClick={() => setBgColor(c)}
              className={`aspect-square rounded-md ring-1 ring-black/10 hover:scale-110 transition-all
              ${bgColor === c ? "ring-2 ring-slate-800 scale-110" : ""}`}
              style={{ background: c }}
              aria-label={`Fondo ${c}`}
            />
          ))}
        </div>
        <div className="mt-2 flex items-center gap-2">
          <input
            type="color"
            value={bgColor}
            onChange={(e) => setBgColor(e.target.value)}
            className="w-8 h-8 rounded-md cursor-pointer border-0 bg-transparent"
          />
          <span className="text-xs font-mono text-slate-600 uppercase">{bgColor}</span>
        </div>
      </Panel>

      {/* Onion skin */}
      <Panel title="Onion Skin">
        <div className="flex items-center gap-3">
          <Switch checked={onionSkin} onCheckedChange={setOnionSkin} id="onion" />
          <label htmlFor="onion" className="text-sm text-slate-700 cursor-pointer flex-1">
            Ver fotograma anterior
          </label>
          {onionSkin ? (
            <Eye size={16} className="text-slate-500" />
          ) : (
            <EyeOff size={16} className="text-slate-300" />
          )}
        </div>
        <p className="text-xs text-slate-500 mt-2 leading-snug">
          Muestra el fotograma previo semitransparente para ayudarte a animar
          con fluidez.
        </p>
      </Panel>
    </div>
  );
}

function Panel({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-black/5 p-3">
      <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-2.5 flex items-center gap-1.5">
        <Layers size={11} /> {title}
      </div>
      {children}
    </div>
  );
}

function Timeline({
  frames,
  currentIdx,
  bgColor,
  onSelect,
  onAdd,
  onDuplicate,
  onDelete,
  onClear,
  onMove,
  onSetFirst,
}: {
  frames: Frame[];
  currentIdx: number;
  bgColor: string;
  onSelect: (i: number) => void;
  onAdd: () => void;
  onDuplicate: () => void;
  onDelete: () => void;
  onClear: () => void;
  onMove: (dir: -1 | 1) => void;
  onSetFirst: () => void;
}) {
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-black/5 p-3">
      <div className="flex items-center justify-between mb-2 gap-2 flex-wrap">
        <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
          <Layers size={11} /> Línea de tiempo · {frames.length} fotograma(s)
        </div>
        <div className="flex items-center gap-1">
          <Button size="sm" variant="ghost" onClick={onClear} className="text-xs px-2 h-7">
            Limpiar
          </Button>
          <Button size="sm" variant="ghost" onClick={onSetFirst} className="text-xs px-2 h-7" disabled={currentIdx === 0}>
            1º
          </Button>
          <Button size="sm" variant="ghost" onClick={() => onMove(-1)} className="px-1.5 h-7" disabled={currentIdx === 0}>
            <ChevronUp size={14} />
          </Button>
          <Button size="sm" variant="ghost" onClick={() => onMove(1)} className="px-1.5 h-7" disabled={currentIdx === frames.length - 1}>
            <ChevronDown size={14} />
          </Button>
          <Button size="sm" variant="ghost" onClick={onDelete} className="px-1.5 h-7 text-red-500" disabled={frames.length <= 1}>
            <Trash2 size={14} />
          </Button>
          <Button size="sm" variant="ghost" onClick={onDuplicate} className="px-1.5 h-7">
            <Copy size={14} />
          </Button>
          <Button size="sm" onClick={onAdd} className="px-2 h-7 bg-gradient-to-br from-pink-500 to-orange-500 text-white gap-1">
            <Plus size={14} /> Fotograma
          </Button>
        </div>
      </div>
      <div className="flex gap-2 overflow-x-auto pb-1 min-h-[90px]">
        {frames.map((f, i) => (
          <FrameThumb
            key={f.id}
            frame={f}
            index={i}
            active={i === currentIdx}
            bgColor={bgColor}
            onClick={() => onSelect(i)}
          />
        ))}
        <button
          onClick={onAdd}
          className="shrink-0 w-[68px] h-[68px] rounded-xl border-2 border-dashed border-slate-300 hover:border-pink-400 hover:bg-pink-50 transition-all flex items-center justify-center text-slate-400 hover:text-pink-500"
          aria-label="Añadir fotograma"
        >
          <Plus size={20} />
        </button>
      </div>
    </div>
  );
}

function FrameThumb({
  frame,
  index,
  active,
  bgColor,
  onClick,
}: {
  frame: Frame;
  index: number;
  active: boolean;
  bgColor: string;
  onClick: () => void;
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const c = canvasRef.current;
    if (!c) return;
    let cancelled = false;
    (async () => {
      const ctx = c.getContext("2d")!;
      ctx.clearRect(0, 0, c.width, c.height);
      if (bgColor !== "transparent") {
        ctx.fillStyle = bgColor;
        ctx.fillRect(0, 0, c.width, c.height);
      }
      if (frame.data) {
        try {
          const img = await loadImage(frame.data);
          if (!cancelled) ctx.drawImage(img, 0, 0, c.width, c.height);
        } catch {
          /* noop */
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [frame.data, bgColor]);

  return (
    <button
      onClick={onClick}
      className={`relative shrink-0 group transition-all
      ${active ? "ring-2 ring-pink-500 ring-offset-2 ring-offset-white rounded-xl" : "ring-1 ring-black/10 rounded-xl hover:ring-slate-400"}`}
    >
      <canvas
        ref={canvasRef}
        width={CANVAS_W}
        height={CANVAS_H}
        className="w-[68px] h-[68px] rounded-xl block bg-white"
      />
      <span className={`absolute -top-1 -left-1 text-[10px] font-bold px-1.5 py-0.5 rounded-full shadow-sm
      ${active ? "bg-pink-500 text-white" : "bg-white text-slate-600 border border-slate-200"}`}>
        {index + 1}
      </span>
    </button>
  );
}
