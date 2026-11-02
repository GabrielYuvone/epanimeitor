import { GIFEncoder, quantize, applyPalette } from "gifenc";
import { CANVAS_W, CANVAS_H, type Frame } from "./types";

export function uid(): string {
  return Math.random().toString(36).slice(2, 10) + Date.now().toString(36).slice(-4);
}

/** Crea un canvas con data URL vacío (transparente)
 * El fondo se aplica dinámicamente como capa subyacente, no se "hornea"
 * en el frame. Esto permite cambiar el color de fondo en cualquier momento.
 */
export function emptyFrameData(_bgColor?: string): string {
  if (typeof document === "undefined") return "";
  const c = document.createElement("canvas");
  c.width = CANVAS_W;
  c.height = CANVAS_H;
  // canvas transparente - el fondo lo aporta la capa subyacente
  return c.toDataURL("image/png");
}

/** Carga una imagen desde data URL */
export function loadImage(src: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = reject;
    img.src = src;
  });
}

/** Dibuja un frame en un canvas destino */
export async function drawFrameToCanvas(
  canvas: HTMLCanvasElement,
  frameData: string,
  bgColor: string
) {
  const ctx = canvas.getContext("2d")!;
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  // fondo
  if (bgColor !== "transparent") {
    ctx.fillStyle = bgColor;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  }
  if (frameData) {
    const img = await loadImage(frameData);
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
  }
}

/** Genera un GIF a partir de los frames */
export async function exportGif(
  frames: Frame[],
  bgColor: string,
  fps: number
): Promise<Blob> {
  const gif = GIFEncoder();
  const delay = Math.max(20, Math.round(1000 / fps));

  // canvas auxiliar para composición final
  const canvas = document.createElement("canvas");
  canvas.width = CANVAS_W;
  canvas.height = CANVAS_H;
  const ctx = canvas.getContext("2d")!;

  for (const frame of frames) {
    ctx.clearRect(0, 0, CANVAS_W, CANVAS_H);
    if (bgColor !== "transparent") {
      ctx.fillStyle = bgColor;
      ctx.fillRect(0, 0, CANVAS_W, CANVAS_H);
    }
    if (frame.data) {
      const img = await loadImage(frame.data);
      ctx.drawImage(img, 0, 0, CANVAS_W, CANVAS_H);
    }
    const { data } = ctx.getImageData(0, 0, CANVAS_W, CANVAS_H);
    // Orden correcto: quantize genera la paleta, applyPalette mapea los píxeles
    const palette = quantize(data, 256);
    const index = applyPalette(data, palette);
    gif.writeFrame(index, CANVAS_W, CANVAS_H, { palette, delay });
  }
  gif.finish();
  return new Blob([gif.bytes()], { type: "image/gif" });
}

/** Descarga un blob como archivo */
export function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

/** Descarga un texto como archivo */
export function downloadText(text: string, filename: string, type = "application/json") {
  const blob = new Blob([text], { type });
  downloadBlob(blob, filename);
}

/** Genera thumbnail pequeño a partir de data URL */
export async function makeThumbnail(frameData: string, size: number): Promise<string> {
  const img = await loadImage(frameData);
  const c = document.createElement("canvas");
  c.width = size;
  c.height = size;
  const ctx = c.getContext("2d")!;
  // mantener relación de aspecto
  const r = img.width / img.height;
  let w = size;
  let h = size;
  if (r > 1) {
    h = size / r;
  } else {
    w = size * r;
  }
  ctx.drawImage(img, (size - w) / 2, (size - h) / 2, w, h);
  return c.toDataURL("image/png");
}
