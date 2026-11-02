// Tipos compartidos para el editor de animación

export type ToolId =
  | "pencil"
  | "brush"
  | "eraser"
  | "line"
  | "rectangle"
  | "circle"
  | "fill";

export interface Tool {
  id: ToolId;
  label: string;
  icon: string; // nombre del icono lucide
  hint: string;
}

export interface Frame {
  id: string;
  /** dataURL del canvas (PNG) */
  data: string;
  /** duración del frame en milisegundos (cuando se reproduce frame a frame) */
  duration: number;
}

export interface AnimationProject {
  name: string;
  width: number;
  height: number;
  bgColor: string;
  fps: number;
  onionSkin: boolean;
  frames: Frame[];
}

export const DEFAULT_PALETTE: string[] = [
  "#1a1a1a",
  "#FFFFFF",
  "#888888",
  "#FF6B6B",
  "#FFA94D",
  "#FFD93D",
  "#6BCB77",
  "#4D96FF",
  "#9B59B6",
  "#FF6FB5",
  "#FFB6C1",
  "#87CEEB",
  "#98FB98",
  "#DDA0DD",
  "#F5DEB3",
  "#2C2C2C",
];

export const BG_PRESETS: string[] = [
  "#FFFFFF",
  "#FFF8E7",
  "#E0F7FA",
  "#FCE4EC",
  "#F1F8E9",
  "#FFF3E0",
  "#EDE7F6",
  "#ECEFF1",
  "#1a1a1a",
];

export const CANVAS_W = 600;
export const CANVAS_H = 450;
