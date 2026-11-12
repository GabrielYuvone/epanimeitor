#!/usr/bin/env python3
"""Genera epanimeitor.html — app completa en un solo archivo."""
import json
import os

# Read base64 logos
with open('/tmp/logos_b64.json') as f:
    logos = json.load(f)
LOGO_MAIN_B64 = logos['main']
LOGO_FOOTER_B64 = logos['footer']

# Read gifenc source
with open('/tmp/gifenc.js') as f:
    gifenc_src = f.read()

# The ESM source ends with: export{ct as GIFEncoder, nt as applyPalette, ...}
# Inside a module, `export {x as Y}` makes Y an export name but NOT a local binding.
# The rest of our script references GIFEncoder/quantize/applyPalette as locals.
# Fix: replace the export statement with local const declarations.
gifenc_src = gifenc_src.replace(
    'export{ct as GIFEncoder,nt as applyPalette,Bt as default,ot as nearestColor,W as nearestColorIndex,N as nearestColorIndexWithDistance,et as prequantize,H as quantize,rt as snapColorsToPalette};',
    'const GIFEncoder=ct;const applyPalette=nt;const quantize=H;const prequantize=et;const nearestColor=ot;const nearestColorIndex=W;const nearestColorIndexWithDistance=N;const snapColorsToPalette=rt;'
)

# Build the HTML
html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Epanimeitor · Animador de GIFs</title>
<meta name="description" content="Crea animaciones frame a frame y exportalas como GIF. Simple, colorido y gratuito. Escuela para Animadores Rosario.">
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
:root {{
  --bg: #faf7f2;
  --card: #ffffff;
  --border: #e5e1d8;
  --text: #1a1a18;
  --muted: #7d7b73;
  --accent: #FF6B6B;
  --accent-grad: linear-gradient(135deg, #FF6B6B 0%, #FFA94D 50%, #FFD93D 100%);
  --pink: #FF6FB5;
  --shadow: 0 1px 3px rgba(0,0,0,0.05), 0 1px 2px rgba(0,0,0,0.03);
  --radius: 14px;
  --radius-sm: 10px;
}}
html, body {{
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, "Helvetica Neue", Arial, sans-serif;
  background: linear-gradient(135deg, #ffeef0 0%, #fff4e0 50%, #e0f0ff 100%);
  color: var(--text);
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
  font-size: 14px;
  line-height: 1.5;
}}
button {{ font-family: inherit; cursor: pointer; border: none; background: none; color: inherit; }}
input, select {{ font-family: inherit; }}

/* ====== Layout ====== */
.app {{ min-height: 100vh; display: flex; flex-direction: column; }}

header.topbar {{
  position: sticky; top: 0; z-index: 30;
  background: rgba(255,255,255,0.85);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border);
  box-shadow: 0 1px 0 rgba(0,0,0,0.03);
}}
.topbar-inner {{
  max-width: 1400px; margin: 0 auto; padding: 12px 16px;
  display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
}}
.brand {{ display: flex; align-items: center; gap: 8px; margin-right: auto; }}
.brand img {{ height: 36px; width: auto; }}
.topbar-actions {{ display: flex; gap: 6px; align-items: center; flex-wrap: wrap; }}

main {{
  flex: 1; max-width: 1400px; width: 100%; margin: 0 auto; padding: 16px;
  display: grid; grid-template-columns: auto 1fr 280px; gap: 16px;
}}
@media (max-width: 1024px) {{
  main {{ grid-template-columns: 1fr; }}
}}

/* ====== Buttons ====== */
.btn {{
  display: inline-flex; align-items: center; gap: 6px;
  padding: 7px 12px; border-radius: var(--radius-sm);
  background: white; color: var(--text); border: 1px solid var(--border);
  font-size: 13px; font-weight: 500; transition: all 0.15s;
  min-height: 32px;
}}
.btn:hover {{ background: #f7f5f0; }}
.btn:disabled {{ opacity: 0.4; cursor: not-allowed; }}
.btn-primary {{
  background: var(--accent-grad); color: white; border: none;
  box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}}
.btn-primary:hover {{ opacity: 0.9; }}
.btn-success {{
  background: linear-gradient(135deg, #34d399, #14b8a6); color: white; border: none;
  box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}}
.btn-success:hover {{ opacity: 0.9; }}
.btn-ghost {{ background: transparent; border: none; }}
.btn-ghost:hover {{ background: #f0ede5; }}
.btn-sm {{ padding: 4px 8px; min-height: 28px; font-size: 12px; }}
.btn-icon {{ padding: 8px; min-height: 36px; min-width: 36px; justify-content: center; }}

/* ====== Tool rail ====== */
.toolrail {{
  position: sticky; top: 80px; align-self: start;
  background: white; border-radius: var(--radius); padding: 8px;
  display: flex; flex-direction: column; gap: 6px;
  box-shadow: var(--shadow); border: 1px solid var(--border);
  width: 60px;
}}
@media (max-width: 1024px) {{
  .toolrail {{ flex-direction: row; overflow-x: auto; width: 100%; position: static; }}
}}
.tool-btn {{
  width: 44px; height: 44px; border-radius: var(--radius-sm);
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  color: #4a4a4a; transition: all 0.15s; flex-shrink: 0; position: relative;
}}
.tool-btn:hover {{ background: #f0ede5; color: #1a1a18; }}
.tool-btn.active {{
  background: var(--accent-grad); color: white;
  box-shadow: 0 2px 6px rgba(255,107,107,0.3); transform: scale(1.05);
}}
.tool-btn svg {{ width: 20px; height: 20px; }}
.tool-btn .key {{
  position: absolute; bottom: 2px; font-size: 8px; opacity: 0.6; font-weight: 600;
}}
.toolrail-divider {{ height: 1px; background: var(--border); margin: 4px 0; }}
@media (max-width: 1024px) {{ .toolrail-divider {{ width: 1px; height: auto; margin: 0 4px; }} }}

/* ====== Canvas area ====== */
.canvas-area {{ display: flex; flex-direction: column; gap: 12px; min-width: 0; }}
.canvas-card {{
  background: white; border-radius: var(--radius); padding: 16px;
  box-shadow: var(--shadow); border: 1px solid var(--border);
}}
.canvas-wrap {{
  position: relative; width: 100%; aspect-ratio: 4/3;
  border-radius: var(--radius); overflow: hidden;
  box-shadow: inset 0 1px 3px rgba(0,0,0,0.06);
  border: 1px solid rgba(0,0,0,0.08);
}}
.canvas-wrap canvas {{
  position: absolute; inset: 0; width: 100%; height: 100%;
  touch-action: none;
}}
.canvas-wrap canvas.preview {{ pointer-events: none; }}
.canvas-badge {{
  position: absolute; top: 8px; right: 8px;
  background: rgba(0,0,0,0.5); color: white;
  font-size: 10px; padding: 4px 8px; border-radius: 999px;
  text-transform: uppercase; letter-spacing: 0.05em;
  pointer-events: none;
}}

/* Playback bar */
.playback {{
  background: white; border-radius: var(--radius); padding: 8px 12px;
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
  box-shadow: var(--shadow); border: 1px solid var(--border);
}}
.playback .frame-info {{
  font-size: 13px; color: var(--muted); margin-left: 8px;
}}
.playback .frame-info b {{ color: var(--text); }}
.playback .fps-control {{
  margin-left: auto; display: flex; align-items: center; gap: 8px;
}}
.playback .fps-control label {{ font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; }}
.playback .fps-control input[type=range] {{ width: 100px; }}
.playback .fps-val {{ font-weight: 600; width: 24px; text-align: right; font-variant-numeric: tabular-nums; }}

/* Range slider */
input[type=range] {{
  -webkit-appearance: none; appearance: none;
  height: 4px; background: var(--border); border-radius: 999px;
  outline: none;
}}
input[type=range]::-webkit-slider-thumb {{
  -webkit-appearance: none; appearance: none;
  width: 16px; height: 16px; border-radius: 50%;
  background: var(--accent); cursor: pointer;
  box-shadow: 0 1px 2px rgba(0,0,0,0.2);
}}
input[type=range]::-moz-range-thumb {{
  width: 16px; height: 16px; border-radius: 50%; border: none;
  background: var(--accent); cursor: pointer;
}}

/* ====== Timeline ====== */
.timeline {{
  background: white; border-radius: var(--radius); padding: 12px;
  box-shadow: var(--shadow); border: 1px solid var(--border);
}}
.timeline-header {{
  display: flex; justify-content: space-between; align-items: center;
  gap: 8px; flex-wrap: wrap; margin-bottom: 8px;
}}
.timeline-title {{
  font-size: 11px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.08em; color: var(--muted);
}}
.timeline-actions {{ display: flex; gap: 4px; flex-wrap: wrap; }}
.frames-list {{
  display: flex; gap: 8px; overflow-x: auto; padding-bottom: 4px;
  min-height: 90px;
}}
.frame-thumb {{
  position: relative; flex-shrink: 0; cursor: pointer;
  border-radius: var(--radius-sm); transition: all 0.15s;
  border: 1px solid var(--border);
}}
.frame-thumb:hover {{ border-color: #888; }}
.frame-thumb.active {{
  border: 2px solid var(--accent); transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(255,107,107,0.2);
}}
.frame-thumb canvas {{
  width: 68px; height: 68px; display: block; border-radius: 9px; background: white;
}}
.frame-thumb .num {{
  position: absolute; top: -6px; left: -6px;
  font-size: 10px; font-weight: 700; padding: 2px 6px;
  border-radius: 999px; background: white; color: var(--muted);
  border: 1px solid var(--border); box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}}
.frame-thumb.active .num {{ background: var(--accent); color: white; border-color: var(--accent); }}
.add-frame-btn {{
  flex-shrink: 0; width: 68px; height: 68px;
  border: 2px dashed var(--border); border-radius: var(--radius-sm);
  display: flex; align-items: center; justify-content: center;
  color: var(--muted); transition: all 0.15s;
}}
.add-frame-btn:hover {{
  border-color: var(--accent); color: var(--accent); background: #fff5f5;
}}

/* ====== Right panel ====== */
.right-panel {{
  display: flex; flex-direction: column; gap: 12px;
  position: sticky; top: 80px; align-self: start;
}}
@media (max-width: 1024px) {{ .right-panel {{ position: static; }} }}

.panel {{
  background: white; border-radius: var(--radius); padding: 12px;
  box-shadow: var(--shadow); border: 1px solid var(--border);
}}
.panel-title {{
  font-size: 11px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.08em; color: var(--muted); margin-bottom: 10px;
  display: flex; align-items: center; gap: 6px;
}}
.panel-title svg {{ width: 12px; height: 12px; }}

.palette-grid {{ display: grid; grid-template-columns: repeat(8, 1fr); gap: 5px; }}
.palette-swatch {{
  aspect-ratio: 1; border-radius: 6px; cursor: pointer;
  border: 1px solid rgba(0,0,0,0.1); transition: transform 0.1s;
}}
.palette-swatch:hover {{ transform: scale(1.1); }}
.palette-swatch.active {{
  border: 2px solid var(--text); transform: scale(1.1);
  box-shadow: 0 0 0 2px white, 0 0 0 4px var(--text);
}}

.current-color {{
  display: flex; align-items: center; gap: 10px; margin-top: 12px;
}}
.current-color-swatch {{
  width: 40px; height: 40px; border-radius: 8px;
  border: 1px solid rgba(0,0,0,0.1); flex-shrink: 0;
}}
.current-color-info {{ flex: 1; }}
.current-color-info .label {{ font-size: 11px; color: var(--muted); margin-bottom: 2px; }}
.current-color-info .hex {{
  font-size: 13px; font-family: "SF Mono", Monaco, Consolas, monospace;
  color: var(--text); text-transform: uppercase; font-weight: 500;
}}
.color-picker-toggle {{
  width: 100%; margin-top: 8px; padding: 6px;
  font-size: 12px; color: var(--muted);
  display: flex; align-items: center; justify-content: center; gap: 6px;
  border-radius: 8px;
}}
.color-picker-toggle:hover {{ background: #f0ede5; color: var(--text); }}
.color-picker-area {{
  margin-top: 8px; padding: 8px; background: #f7f5f0;
  border-radius: 8px; display: flex; align-items: center; gap: 8px;
}}
.color-picker-area input[type=color] {{
  width: 40px; height: 40px; border: none; background: transparent; cursor: pointer; padding: 0;
}}
.color-picker-area input[type=text] {{
  flex: 1; padding: 4px 8px; border: 1px solid var(--border);
  border-radius: 6px; font-family: monospace; font-size: 12px;
}}

/* Brush */
.brush-row {{ display: flex; align-items: center; gap: 12px; }}
.brush-preview {{
  width: 48px; height: 48px; border-radius: 8px;
  background: #f7f5f0; display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; border: 1px solid rgba(0,0,0,0.05);
}}
.brush-dot {{ border-radius: 50%; }}
.brush-control {{ flex: 1; }}
.brush-control .row {{
  display: flex; justify-content: space-between; font-size: 11px;
  color: var(--muted); margin-bottom: 4px;
}}
.brush-control .row b {{ color: var(--text); font-variant-numeric: tabular-nums; }}
.brush-control input[type=range] {{ width: 100%; }}

/* Background presets */
.bg-presets {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 5px; }}
.bg-swatch {{
  aspect-ratio: 1; border-radius: 6px; cursor: pointer;
  border: 1px solid rgba(0,0,0,0.1); transition: transform 0.1s;
}}
.bg-swatch:hover {{ transform: scale(1.1); }}
.bg-swatch.active {{ border: 2px solid var(--text); transform: scale(1.1); }}
.bg-current-row {{ display: flex; align-items: center; gap: 8px; margin-top: 8px; }}
.bg-current-row input[type=color] {{
  width: 32px; height: 32px; border: none; background: transparent; cursor: pointer; padding: 0;
}}
.bg-current-row .hex {{ font-family: monospace; font-size: 11px; color: var(--muted); text-transform: uppercase; }}

/* Onion skin */
.onion-row {{ display: flex; align-items: center; gap: 12px; }}
.switch {{
  position: relative; display: inline-block; width: 36px; height: 20px;
}}
.switch input {{ opacity: 0; width: 0; height: 0; }}
.switch .slider {{
  position: absolute; cursor: pointer; inset: 0;
  background: #ccc; border-radius: 999px; transition: 0.2s;
}}
.switch .slider::before {{
  content: ''; position: absolute; height: 14px; width: 14px;
  left: 3px; bottom: 3px; background: white; border-radius: 50%; transition: 0.2s;
}}
.switch input:checked + .slider {{ background: var(--accent); }}
.switch input:checked + .slider::before {{ transform: translateX(16px); }}
.onion-label {{ flex: 1; font-size: 13px; cursor: pointer; }}
.onion-desc {{ font-size: 11px; color: var(--muted); margin-top: 8px; line-height: 1.4; }}

/* ====== Footer ====== */
footer {{
  border-top: 1px solid var(--border);
  background: rgba(255,255,255,0.7); backdrop-filter: blur(8px);
  padding: 14px 16px; margin-top: 16px;
}}
.footer-inner {{
  max-width: 1400px; margin: 0 auto;
  display: flex; align-items: center; justify-content: center; gap: 12px; flex-wrap: wrap;
}}
.footer-inner img.footer-logo {{ height: 40px; width: auto; opacity: 0.9; }}
.footer-text {{ font-size: 12px; color: var(--muted); text-align: center; line-height: 1.4; }}
.footer-text b {{ color: var(--text); }}

/* ====== Dialog ====== */
dialog {{
  border: none; border-radius: var(--radius); padding: 0;
  box-shadow: 0 10px 40px rgba(0,0,0,0.15); max-width: 500px; width: 90vw;
}}
dialog::backdrop {{ background: rgba(0,0,0,0.4); }}
.dialog-content {{ padding: 20px; }}
.dialog-header {{
  display: flex; align-items: center; gap: 10px; margin-bottom: 16px;
  padding-bottom: 12px; border-bottom: 1px solid var(--border);
}}
.dialog-header img {{ height: 24px; }}
.dialog-body {{ font-size: 13px; color: var(--text); }}
.dialog-body p {{ margin-bottom: 8px; }}
.dialog-body kbd {{
  background: #f0ede5; padding: 2px 6px; border-radius: 4px;
  font-family: monospace; font-size: 11px;
}}
.dialog-body hr {{ border: none; border-top: 1px solid var(--border); margin: 12px 0; }}
.dialog-body .tip {{ font-size: 12px; color: var(--muted); }}
.dialog-footer-logo {{
  display: flex; align-items: center; gap: 10px;
  padding-top: 12px; margin-top: 12px; border-top: 1px solid var(--border);
}}
.dialog-footer-logo img {{ height: 32px; opacity: 0.8; }}
.dialog-footer-logo span {{ font-size: 10px; color: var(--muted); }}
.dialog-close {{
  position: absolute; top: 12px; right: 12px;
  width: 28px; height: 28px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  color: var(--muted);
}}
.dialog-close:hover {{ background: #f0ede5; color: var(--text); }}

/* ====== Toast ====== */
.toast {{
  position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);
  background: var(--text); color: white; padding: 10px 18px;
  border-radius: var(--radius-sm); font-size: 13px; z-index: 100;
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
  opacity: 0; transition: opacity 0.3s; pointer-events: none;
}}
.toast.show {{ opacity: 1; }}

/* hidden file input */
.hidden-input {{ display: none; }}
</style>
</head>
<body>
<div class="app">
  <!-- ====== TOP BAR ====== -->
  <header class="topbar">
    <div class="topbar-inner">
      <div class="brand">
        <img src="data:image/png;base64,{LOGO_MAIN_B64}" alt="Epanimeitor">
      </div>
      <div class="topbar-actions">
        <button class="btn btn-sm" id="btnNew" title="Nueva animación">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
          <span>Nuevo</span>
        </button>
        <button class="btn btn-sm" id="btnSave" title="Guardar proyecto JSON">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
          <span>Guardar</span>
        </button>
        <button class="btn btn-sm" id="btnLoad" title="Cargar proyecto JSON">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
          <span>Cargar</span>
        </button>
        <button class="btn btn-sm btn-success" id="btnExport" title="Exportar GIF animado">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
          <span>GIF</span>
        </button>
        <button class="btn btn-sm btn-ghost" id="btnHelp" title="Ayuda y atajos">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
          <span>Ayuda</span>
        </button>
      </div>
    </div>
  </header>

  <!-- ====== MAIN ====== -->
  <main>
    <!-- Left tool rail -->
    <aside class="toolrail" id="toolrail"></aside>

    <!-- Canvas + playback + timeline -->
    <section class="canvas-area">
      <div class="canvas-card">
        <div class="canvas-wrap" id="canvasWrap">
          <canvas id="drawCanvas" width="600" height="450"></canvas>
          <canvas id="previewCanvas" width="600" height="450" class="preview"></canvas>
          <div class="canvas-badge">600 × 450</div>
        </div>
      </div>

      <div class="playback">
        <button class="btn btn-icon btn-ghost" id="btnPrev" title="Fotograma anterior (J)">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><polygon points="19 20 9 12 19 4 19 20"/><line x1="5" y1="19" x2="5" y2="5" stroke="currentColor" stroke-width="2"/></svg>
        </button>
        <button class="btn btn-primary" id="btnPlay" disabled>
          <svg id="iconPlay" width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>
          <span id="playLabel">Reproducir</span>
        </button>
        <button class="btn btn-icon btn-ghost" id="btnNext" title="Fotograma siguiente (K)">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 4 15 12 5 20 5 4"/><line x1="19" y1="5" x2="19" y2="19" stroke="currentColor" stroke-width="2"/></svg>
        </button>
        <div class="frame-info">Fotograma <b id="curFrameNum">1</b> / <span id="totalFrames">1</span></div>
        <div class="fps-control">
          <label>FPS</label>
          <input type="range" id="fpsSlider" min="1" max="24" value="8">
          <span class="fps-val" id="fpsVal">8</span>
        </div>
      </div>

      <div class="timeline">
        <div class="timeline-header">
          <div class="timeline-title" id="timelineTitle">Línea de tiempo · 1 fotograma(s)</div>
          <div class="timeline-actions">
            <button class="btn btn-sm btn-ghost" id="btnClear" title="Limpiar fotograma actual">Limpiar</button>
            <button class="btn btn-sm btn-ghost" id="btnFirst" disabled title="Marcar como primero">1º</button>
            <button class="btn btn-sm btn-ghost" id="btnUp" disabled title="Mover izquierda">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="18 15 12 9 6 15"/></svg>
            </button>
            <button class="btn btn-sm btn-ghost" id="btnDown" disabled title="Mover derecha">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
            </button>
            <button class="btn btn-sm btn-ghost" id="btnDelete" disabled title="Borrar fotograma" style="color:#dc2626">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
            </button>
            <button class="btn btn-sm btn-ghost" id="btnDuplicate" title="Duplicar fotograma (D)">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
            </button>
            <button class="btn btn-sm btn-primary" id="btnAdd">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
              <span>Fotograma</span>
            </button>
          </div>
        </div>
        <div class="frames-list" id="framesList"></div>
      </div>
    </section>

    <!-- Right panel -->
    <aside class="right-panel">
      <div class="panel">
        <div class="panel-title">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="13.5" cy="6.5" r=".5"/><circle cx="17.5" cy="10.5" r=".5"/><circle cx="8.5" cy="7.5" r=".5"/><circle cx="6.5" cy="12.5" r=".5"/><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.554C21.965 6.012 17.461 2 12 2z"/></svg>
          Color
        </div>
        <div class="palette-grid" id="paletteGrid"></div>
        <div class="current-color">
          <div class="current-color-swatch" id="currentColorSwatch"></div>
          <div class="current-color-info">
            <div class="label">Color actual</div>
            <div class="hex" id="currentColorHex">#1A1A1A</div>
          </div>
        </div>
        <button class="color-picker-toggle" id="colorPickerToggle">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m19 11-8-8-8.6 8.6a2 2 0 0 0 0 2.8l5.2 5.2c.8.8 2 .8 2.8 0L19 11Z"/><path d="m5 2 5 5"/><path d="m2 13 15 15"/><path d="m3 7 15 15"/></svg>
          Color personalizado
        </button>
        <div class="color-picker-area" id="colorPickerArea" style="display:none">
          <input type="color" id="customColorInput" value="#FF6B6B">
          <input type="text" id="customColorText" value="#FF6B6B">
        </div>
      </div>

      <div class="panel">
        <div class="panel-title">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m9.06 11.9 8.07-8.06a2.85 2.85 0 1 1 4.03 4.03l-8.06 8.08"/><path d="M7.07 14.94c-1.66 0-3 1.35-3 3.02 0 1.33-2.5 1.52-2 2.02 1.08 1.1 2.49 2.02 4 2.02 2.2 0 4-1.8 4-4.04a3.01 3.01 0 0 0-3-3.02z"/></svg>
          Pincel
        </div>
        <div class="brush-row">
          <div class="brush-preview">
            <div class="brush-dot" id="brushDot"></div>
          </div>
          <div class="brush-control">
            <div class="row"><span>Tamaño</span><b><span id="brushVal">8</span>px</b></div>
            <input type="range" id="brushSlider" min="1" max="50" value="8">
          </div>
        </div>
      </div>

      <div class="panel">
        <div class="panel-title">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 21V9"/></svg>
          Fondo
        </div>
        <div class="bg-presets" id="bgPresets"></div>
        <div class="bg-current-row">
          <input type="color" id="bgColorInput" value="#FFFFFF">
          <span class="hex" id="bgColorHex">#FFFFFF</span>
        </div>
      </div>

      <div class="panel">
        <div class="panel-title">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
          Onion Skin
        </div>
        <div class="onion-row">
          <label class="switch">
            <input type="checkbox" id="onionToggle">
            <span class="slider"></span>
          </label>
          <label class="onion-label" for="onionToggle">Ver fotograma anterior</label>
        </div>
        <div class="onion-desc">Muestra el fotograma previo semitransparente para ayudarte a animar con fluidez.</div>
      </div>
    </aside>
  </main>

  <!-- ====== FOOTER ====== -->
  <footer>
    <div class="footer-inner">
      <img src="data:image/png;base64,{LOGO_FOOTER_B64}" alt="Escuela para Animadores Rosario" class="footer-logo">
      <div class="footer-text">
        <div><b>Epanimeitor</b> · animador frame a frame</div>
        <div>Escuela para Animadores · Rosario · Hecho con cariño</div>
      </div>
    </div>
  </footer>
</div>

<!-- ====== HELP DIALOG ====== -->
<dialog id="helpDialog">
  <div class="dialog-content" style="position:relative">
    <button class="dialog-close" id="dialogClose" aria-label="Cerrar">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
    </button>
    <div class="dialog-header">
      <img src="data:image/png;base64,{LOGO_MAIN_B64}" alt="Epanimeitor">
    </div>
    <div class="dialog-body">
      <p><kbd>Espacio</kbd> – Reproducir / pausar</p>
      <p><kbd>N</kbd> – Nuevo fotograma · <kbd>D</kbd> – Duplicar · <kbd>O</kbd> – Onion skin</p>
      <p><kbd>J</kbd> / <kbd>K</kbd> – Fotograma anterior / siguiente</p>
      <p><kbd>1</kbd>–<kbd>7</kbd> – Seleccionar herramienta</p>
      <p><kbd>Ctrl/Cmd + Z</kbd> – Deshacer · <kbd>Ctrl/Cmd + Shift + Z</kbd> – Rehacer</p>
      <p><kbd>Ctrl/Cmd + S</kbd> – Guardar · <kbd>Ctrl/Cmd + E</kbd> – Exportar GIF</p>
      <hr>
      <p class="tip">Tip: activá <b>onion skin</b> para ver el fotograma anterior en transparente y animar con más precisión.</p>
      <div class="dialog-footer-logo">
        <img src="data:image/png;base64,{LOGO_FOOTER_B64}" alt="Escuela para Animadores Rosario">
        <span>Escuela para Animadores · Rosario</span>
      </div>
    </div>
  </div>
</dialog>

<div class="toast" id="toast"></div>
<input type="file" id="fileInput" class="hidden-input" accept=".json,application/json">

<script type="module">
// ====== gifenc inline (ESM) ======
{gifenc_src}

// ====== Epanimeitor app ======
const CANVAS_W = 600;
const CANVAS_H = 450;
const DEFAULT_PALETTE = ['#1a1a1a','#FFFFFF','#888888','#FF6B6B','#FFA94D','#FFD93D','#6BCB77','#4D96FF','#9B59B6','#FF6FB5','#FFB6C1','#87CEEB','#98FB98','#DDA0DD','#F5DEB3','#2C2C2C'];
const BG_PRESETS = ['#FFFFFF','#FFF8E7','#E0F7FA','#FCE4EC','#F1F8E9','#FFF3E0','#EDE7F6','#ECEFF1','#1a1a1a'];

const TOOLS = [
  {{ id:'pencil', label:'Lápiz', key:'1', icon:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 19l7-7 3 3-7 7-3-3z"/><path d="M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z"/><path d="M2 2l7.586 7.586"/><circle cx="11" cy="11" r="2"/></svg>' }},
  {{ id:'brush', label:'Pincel', key:'2', icon:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m9.06 11.9 8.07-8.06a2.85 2.85 0 1 1 4.03 4.03l-8.06 8.08"/><path d="M7.07 14.94c-1.66 0-3 1.35-3 3.02 0 1.33-2.5 1.52-2 2.02 1.08 1.1 2.49 2.02 4 2.02 2.2 0 4-1.8 4-4.04a3.01 3.01 0 0 0-3-3.02z"/></svg>' }},
  {{ id:'eraser', label:'Borrador', key:'3', icon:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m7 21-4.3-4.3c-1-1-1-2.5 0-3.4l9.6-9.6c1-1 2.5-1 3.4 0l5.6 5.6c1 1 1 2.5 0 3.4L13 21"/><path d="M22 21H7"/><path d="m5 11 9 9"/></svg>' }},
  {{ id:'line', label:'Línea', key:'4', icon:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="5" y1="19" x2="19" y2="5"/></svg>' }},
  {{ id:'rectangle', label:'Rectángulo', key:'5', icon:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/></svg>' }},
  {{ id:'circle', label:'Círculo', key:'6', icon:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/></svg>' }},
  {{ id:'fill', label:'Relleno', key:'7', icon:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m19 11-8-8-8.6 8.6a2 2 0 0 0 0 2.8l5.2 5.2c.8.8 2 .8 2.8 0L19 11Z"/><path d="m5 2 5 5"/><path d="m2 13 15 15"/><path d="m3 7 15 15"/></svg>' }},
];

// State
let state = {{
  frames: [{{ id: uid(), data: emptyFrame(), duration: 100 }}],
  currentIdx: 0,
  tool: 'pencil',
  color: '#1a1a1a',
  brushSize: 8,
  bgColor: '#FFFFFF',
  fps: 8,
  onionSkin: false,
  isPlaying: false,
  undoStack: [],
  redoStack: [],
  customColor: '#FF6B6B',
}};

const drawCanvas = document.getElementById('drawCanvas');
const previewCanvas = document.getElementById('previewCanvas');
const drawCtx = drawCanvas.getContext('2d');
const previewCtx = previewCanvas.getContext('2d');

let isDrawing = false;
let lastPoint = null;
let startPoint = null;
let playTimer = null;

function uid() {{
  return Math.random().toString(36).slice(2,10) + Date.now().toString(36).slice(-4);
}}
function emptyFrame() {{
  const c = document.createElement('canvas');
  c.width = CANVAS_W; c.height = CANVAS_H;
  return c.toDataURL('image/png');
}}
function loadImage(src) {{
  return new Promise((resolve,reject) => {{
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = reject;
    img.src = src;
  }});
}}
function showToast(msg) {{
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2000);
}}

// ====== Tool rail ======
function renderToolRail() {{
  const rail = document.getElementById('toolrail');
  rail.innerHTML = '';
  TOOLS.forEach(t => {{
    const btn = document.createElement('button');
    btn.className = 'tool-btn' + (state.tool === t.id ? ' active' : '');
    btn.title = `${{t.label}} (${{t.key}})`;
    btn.innerHTML = t.icon + `<span class="key">${{t.key}}</span>`;
    btn.addEventListener('click', () => {{ state.tool = t.id; renderToolRail(); }});
    rail.appendChild(btn);
  }});
  const div = document.createElement('div');
  div.className = 'toolrail-divider';
  rail.appendChild(div);
  // Undo
  const undoBtn = document.createElement('button');
  undoBtn.className = 'tool-btn';
  undoBtn.title = 'Deshacer (Ctrl+Z)';
  undoBtn.disabled = state.undoStack.length === 0;
  undoBtn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 7v6h6"/><path d="M21 17a9 9 0 0 0-15-6.7L3 13"/></svg>';
  undoBtn.addEventListener('click', undo);
  rail.appendChild(undoBtn);
  // Redo
  const redoBtn = document.createElement('button');
  redoBtn.className = 'tool-btn';
  redoBtn.title = 'Rehacer (Ctrl+Shift+Z)';
  redoBtn.disabled = state.redoStack.length === 0;
  redoBtn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 7v6h-6"/><path d="M3 17a9 9 0 0 1 15-6.7L21 13"/></svg>';
  redoBtn.addEventListener('click', redo);
  rail.appendChild(redoBtn);
}}

// ====== Palette ======
function renderPalette() {{
  const grid = document.getElementById('paletteGrid');
  grid.innerHTML = '';
  DEFAULT_PALETTE.forEach(c => {{
    const sw = document.createElement('div');
    sw.className = 'palette-swatch' + (state.color === c ? ' active' : '');
    sw.style.background = c;
    sw.title = c;
    sw.addEventListener('click', () => {{ state.color = c; renderPalette(); updateColorDisplay(); }});
    grid.appendChild(sw);
  }});
}}
function updateColorDisplay() {{
  document.getElementById('currentColorSwatch').style.background = state.color;
  document.getElementById('currentColorHex').textContent = state.color.toUpperCase();
  document.getElementById('brushDot').style.background = state.color;
}}

// ====== Background presets ======
function renderBgPresets() {{
  const grid = document.getElementById('bgPresets');
  grid.innerHTML = '';
  BG_PRESETS.forEach(c => {{
    const sw = document.createElement('div');
    sw.className = 'bg-swatch' + (state.bgColor === c ? ' active' : '');
    sw.style.background = c;
    sw.title = c;
    sw.addEventListener('click', () => {{ state.bgColor = c; updateBgDisplay(); renderFrames(); loadCurrentFrame(); }});
    grid.appendChild(sw);
  }});
}}
function updateBgDisplay() {{
  document.getElementById('bgColorInput').value = state.bgColor;
  document.getElementById('bgColorHex').textContent = state.bgColor.toUpperCase();
  document.getElementById('canvasWrap').style.background = state.bgColor;
}}

// ====== Canvas drawing ======
function getPos(e) {{
  const rect = drawCanvas.getBoundingClientRect();
  const x = ((e.clientX - rect.left) / rect.width) * CANVAS_W;
  const y = ((e.clientY - rect.top) / rect.height) * CANVAS_H;
  return {{ x: Math.round(x), y: Math.round(y) }};
}}

function hexToRgba(hex) {{
  hex = hex.replace('#','');
  if (hex.length === 3) hex = hex.split('').map(c => c+c).join('');
  return {{
    r: parseInt(hex.slice(0,2),16)||0,
    g: parseInt(hex.slice(2,4),16)||0,
    b: parseInt(hex.slice(4,6),16)||0,
    a: 255,
  }};
}}

function floodFill(ctx, sx, sy, fillColor) {{
  const imgData = ctx.getImageData(0,0,CANVAS_W,CANVAS_H);
  const data = imgData.data;
  const startIdx = (sy * CANVAS_W + sx) * 4;
  const startR = data[startIdx], startG = data[startIdx+1], startB = data[startIdx+2], startA = data[startIdx+3];
  const fill = hexToRgba(fillColor);
  if (startR===fill.r && startG===fill.g && startB===fill.b && startA===fill.a) return;
  const stack = [[sx,sy]];
  const tol = 32;
  while (stack.length) {{
    const [x,y] = stack.pop();
    if (x<0||y<0||x>=CANVAS_W||y>=CANVAS_H) continue;
    const idx = (y*CANVAS_W+x)*4;
    if (Math.abs(data[idx]-startR)>tol || Math.abs(data[idx+1]-startG)>tol || Math.abs(data[idx+2]-startB)>tol || Math.abs(data[idx+3]-startA)>tol) continue;
    data[idx]=fill.r; data[idx+1]=fill.g; data[idx+2]=fill.b; data[idx+3]=fill.a;
    stack.push([x+1,y],[x-1,y],[x,y+1],[x,y-1]);
  }}
  ctx.putImageData(imgData,0,0);
}}

function drawDot(ctx, p) {{
  const r = state.brushSize / 2;
  ctx.save();
  if (state.tool === 'eraser') {{
    ctx.globalCompositeOperation = 'destination-out';
    ctx.fillStyle = 'rgba(0,0,0,1)';
  }} else {{
    ctx.globalCompositeOperation = 'source-over';
    ctx.fillStyle = state.color;
  }}
  ctx.beginPath();
  ctx.arc(p.x, p.y, Math.max(0.5, r), 0, Math.PI*2);
  ctx.fill();
  ctx.restore();
}}

function drawLineSegment(ctx, from, to) {{
  ctx.save();
  if (state.tool === 'eraser') {{
    ctx.globalCompositeOperation = 'destination-out';
    ctx.strokeStyle = 'rgba(0,0,0,1)';
  }} else {{
    ctx.globalCompositeOperation = 'source-over';
    ctx.strokeStyle = state.color;
  }}
  ctx.lineWidth = state.tool === 'pencil' ? Math.max(1, state.brushSize*0.6) : state.brushSize;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  ctx.beginPath();
  ctx.moveTo(from.x, from.y);
  ctx.lineTo(to.x, to.y);
  ctx.stroke();
  ctx.restore();
}}

function onPointerDown(e) {{
  e.preventDefault();
  drawCanvas.setPointerCapture(e.pointerId);
  isDrawing = true;
  const p = getPos(e);
  lastPoint = p; startPoint = p;
  if (state.tool === 'fill') {{
    floodFill(drawCtx, p.x, p.y, state.color);
    isDrawing = false;
    commitFrame();
    return;
  }}
  if (state.tool === 'pencil' || state.tool === 'brush' || state.tool === 'eraser') {{
    drawDot(drawCtx, p);
  }}
}}

function onPointerMove(e) {{
  if (!isDrawing) return;
  const p = getPos(e);
  if (state.tool === 'pencil' || state.tool === 'brush' || state.tool === 'eraser') {{
    if (lastPoint) drawLineSegment(drawCtx, lastPoint, p);
    lastPoint = p;
  }} else {{
    // shape preview on previewCanvas
    previewCtx.clearRect(0,0,CANVAS_W,CANVAS_H);
    if (state.onionSkin && state.currentIdx > 0) drawOnionSkin();
    previewCtx.save();
    previewCtx.strokeStyle = state.color;
    previewCtx.lineWidth = state.brushSize;
    previewCtx.lineCap = 'round';
    previewCtx.lineJoin = 'round';
    const sp = startPoint;
    if (state.tool === 'line') {{
      previewCtx.beginPath();
      previewCtx.moveTo(sp.x, sp.y);
      previewCtx.lineTo(p.x, p.y);
      previewCtx.stroke();
    }} else if (state.tool === 'rectangle') {{
      previewCtx.strokeRect(Math.min(sp.x,p.x), Math.min(sp.y,p.y), Math.abs(p.x-sp.x), Math.abs(p.y-sp.y));
    }} else if (state.tool === 'circle') {{
      const cx = (sp.x+p.x)/2, cy = (sp.y+p.y)/2;
      const rx = Math.abs(p.x-sp.x)/2, ry = Math.abs(p.y-sp.y)/2;
      previewCtx.beginPath();
      previewCtx.ellipse(cx, cy, Math.max(1,rx), Math.max(1,ry), 0, 0, Math.PI*2);
      previewCtx.stroke();
    }}
    previewCtx.restore();
  }}
}}

function onPointerUp(e) {{
  if (!isDrawing) return;
  isDrawing = false;
  try {{ drawCanvas.releasePointerCapture(e.pointerId); }} catch(_) {{}}
  if (state.tool === 'line' || state.tool === 'rectangle' || state.tool === 'circle') {{
    // composite preview onto main canvas
    drawCtx.drawImage(previewCanvas, 0, 0);
    previewCtx.clearRect(0,0,CANVAS_W,CANVAS_H);
    if (state.onionSkin && state.currentIdx > 0) drawOnionSkin();
  }}
  lastPoint = null; startPoint = null;
  commitFrame();
}}

function commitFrame() {{
  const dataUrl = drawCanvas.toDataURL('image/png');
  state.frames[state.currentIdx] = {{ ...state.frames[state.currentIdx], data: dataUrl }};
  renderFrames();
}}

// ====== Load current frame ======
async function loadCurrentFrame() {{
  const f = state.frames[state.currentIdx];
  if (!f) return;
  drawCtx.clearRect(0,0,CANVAS_W,CANVAS_H);
  if (f.data) {{
    try {{
      const img = await loadImage(f.data);
      drawCtx.drawImage(img, 0, 0, CANVAS_W, CANVAS_H);
    }} catch(_) {{}}
  }}
  // redraw onion skin if enabled
  previewCtx.clearRect(0,0,CANVAS_W,CANVAS_H);
  if (state.onionSkin && state.currentIdx > 0) drawOnionSkin();
}}

function drawOnionSkin() {{
  if (state.currentIdx === 0) return;
  const prev = state.frames[state.currentIdx - 1];
  if (!prev || !prev.data) return;
  loadImage(prev.data).then(img => {{
    previewCtx.save();
    previewCtx.globalAlpha = 0.3;
    previewCtx.drawImage(img, 0, 0, CANVAS_W, CANVAS_H);
    previewCtx.restore();
  }});
}}

// ====== Frames ======
function renderFrames() {{
  const list = document.getElementById('framesList');
  list.innerHTML = '';
  state.frames.forEach((f, i) => {{
    const div = document.createElement('div');
    div.className = 'frame-thumb' + (i === state.currentIdx ? ' active' : '');
    const canvas = document.createElement('canvas');
    canvas.width = 68; canvas.height = 68;
    const ctx = canvas.getContext('2d');
    // fill bg
    if (state.bgColor !== 'transparent') {{
      ctx.fillStyle = state.bgColor;
      ctx.fillRect(0,0,68,68);
    }}
    if (f.data) {{
      loadImage(f.data).then(img => {{
        // fit
        const r = img.width / img.height;
        let w = 68, h = 68;
        if (r > 1) h = 68/r; else w = 68*r;
        ctx.drawImage(img, (68-w)/2, (68-h)/2, w, h);
      }});
    }}
    const num = document.createElement('span');
    num.className = 'num';
    num.textContent = i+1;
    div.appendChild(canvas);
    div.appendChild(num);
    div.addEventListener('click', () => {{
      state.isPlaying = false;
      state.currentIdx = i;
      loadCurrentFrame();
      renderFrames();
      updateUI();
    }});
    list.appendChild(div);
  }});
  // add button
  const addBtn = document.createElement('button');
  addBtn.className = 'add-frame-btn';
  addBtn.title = 'Añadir fotograma';
  addBtn.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>';
  addBtn.addEventListener('click', addFrame);
  list.appendChild(addBtn);
  updateUI();
}}

function pushUndo() {{
  state.undoStack.push(state.frames.map(f => ({{...f}})));
  if (state.undoStack.length > 30) state.undoStack.shift();
  state.redoStack = [];
}}
function undo() {{
  if (state.undoStack.length === 0) return;
  state.redoStack.push(state.frames.map(f => ({{...f}})));
  state.frames = state.undoStack.pop();
  state.currentIdx = Math.min(state.currentIdx, state.frames.length-1);
  loadCurrentFrame();
  renderToolRail(); renderFrames();
}}
function redo() {{
  if (state.redoStack.length === 0) return;
  state.undoStack.push(state.frames.map(f => ({{...f}})));
  state.frames = state.redoStack.pop();
  state.currentIdx = Math.min(state.currentIdx, state.frames.length-1);
  loadCurrentFrame();
  renderToolRail(); renderFrames();
}}

function addFrame() {{
  pushUndo();
  const newF = {{ id: uid(), data: emptyFrame(), duration: 100 }};
  state.frames.splice(state.currentIdx+1, 0, newF);
  state.currentIdx++;
  loadCurrentFrame();
  renderFrames();
}}
function duplicateFrame() {{
  pushUndo();
  const cur = state.frames[state.currentIdx];
  const newF = {{ id: uid(), data: cur.data, duration: cur.duration }};
  state.frames.splice(state.currentIdx+1, 0, newF);
  state.currentIdx++;
  loadCurrentFrame();
  renderFrames();
}}
function deleteFrame() {{
  if (state.frames.length <= 1) return;
  pushUndo();
  state.frames.splice(state.currentIdx, 1);
  state.currentIdx = Math.max(0, Math.min(state.currentIdx, state.frames.length-1));
  loadCurrentFrame();
  renderFrames();
}}
function clearFrame() {{
  pushUndo();
  state.frames[state.currentIdx] = {{ ...state.frames[state.currentIdx], data: emptyFrame() }};
  loadCurrentFrame();
  renderFrames();
}}
function moveFrame(dir) {{
  const target = state.currentIdx + dir;
  if (target < 0 || target >= state.frames.length) return;
  pushUndo();
  [state.frames[state.currentIdx], state.frames[target]] = [state.frames[target], state.frames[state.currentIdx]];
  state.currentIdx = target;
  loadCurrentFrame();
  renderFrames();
}}
function setAsFirst() {{
  if (state.currentIdx === 0) return;
  pushUndo();
  const [f] = state.frames.splice(state.currentIdx, 1);
  state.frames.unshift(f);
  state.currentIdx = 0;
  loadCurrentFrame();
  renderFrames();
}}

// ====== Playback ======
function togglePlay() {{
  if (state.frames.length < 2) return;
  state.isPlaying = !state.isPlaying;
  updatePlayButton();
  if (state.isPlaying) scheduleNextFrame();
  else if (playTimer) {{ clearTimeout(playTimer); playTimer = null; }}
}}
function scheduleNextFrame() {{
  if (!state.isPlaying) return;
  const delay = Math.max(20, Math.round(1000 / state.fps));
  playTimer = setTimeout(() => {{
    state.currentIdx = (state.currentIdx + 1) % state.frames.length;
    loadCurrentFrame();
    renderFrames();
    scheduleNextFrame();
  }}, delay);
}}
function updatePlayButton() {{
  const btn = document.getElementById('btnPlay');
  const icon = document.getElementById('iconPlay');
  const label = document.getElementById('playLabel');
  if (state.isPlaying) {{
    icon.innerHTML = '<rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/>';
    label.textContent = 'Pausar';
  }} else {{
    icon.innerHTML = '<polygon points="5 3 19 12 5 21 5 3"/>';
    label.textContent = 'Reproducir';
  }}
}}

// ====== UI updates ======
function updateUI() {{
  document.getElementById('curFrameNum').textContent = state.currentIdx + 1;
  document.getElementById('totalFrames').textContent = state.frames.length;
  document.getElementById('timelineTitle').textContent = `Línea de tiempo · ${{state.frames.length}} fotograma(s)`;
  document.getElementById('btnPlay').disabled = state.frames.length < 2;
  document.getElementById('btnDelete').disabled = state.frames.length <= 1;
  document.getElementById('btnFirst').disabled = state.currentIdx === 0;
  document.getElementById('btnUp').disabled = state.currentIdx === 0;
  document.getElementById('btnDown').disabled = state.currentIdx === state.frames.length - 1;
  document.getElementById('fpsVal').textContent = state.fps;
  document.getElementById('brushVal').textContent = state.brushSize;
  const dot = document.getElementById('brushDot');
  const sz = Math.min(state.brushSize, 36);
  dot.style.width = sz + 'px';
  dot.style.height = sz + 'px';
}}

// ====== Export GIF ======
async function exportGif() {{
  const btn = document.getElementById('btnExport');
  const orig = btn.innerHTML;
  btn.innerHTML = '<span>Exportando…</span>';
  btn.disabled = true;
  try {{
    const gif = GIFEncoder();
    const delay = Math.max(20, Math.round(1000 / state.fps));
    const canvas = document.createElement('canvas');
    canvas.width = CANVAS_W; canvas.height = CANVAS_H;
    const ctx = canvas.getContext('2d');
    for (const frame of state.frames) {{
      ctx.clearRect(0,0,CANVAS_W,CANVAS_H);
      if (state.bgColor !== 'transparent') {{
        ctx.fillStyle = state.bgColor;
        ctx.fillRect(0,0,CANVAS_W,CANVAS_H);
      }}
      if (frame.data) {{
        const img = await loadImage(frame.data);
        ctx.drawImage(img, 0, 0, CANVAS_W, CANVAS_H);
      }}
      const {{ data }} = ctx.getImageData(0,0,CANVAS_W,CANVAS_H);
      const palette = quantize(data, 256);
      const index = applyPalette(data, palette);
      gif.writeFrame(index, CANVAS_W, CANVAS_H, {{ palette, delay }});
    }}
    gif.finish();
    const blob = new Blob([gif.bytes()], {{ type: 'image/gif' }});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `epanimeitor-${{Date.now()}}.gif`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast('GIF exportado');
  }} catch (err) {{
    alert('Error al exportar: ' + err.message);
  }} finally {{
    btn.innerHTML = orig;
    btn.disabled = false;
  }}
}}

// ====== Save / Load ======
function saveProject() {{
  const project = {{
    name: 'epanimeitor',
    width: CANVAS_W, height: CANVAS_H,
    bgColor: state.bgColor, fps: state.fps,
    onionSkin: state.onionSkin, frames: state.frames,
  }};
  const blob = new Blob([JSON.stringify(project, null, 2)], {{ type: 'application/json' }});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'epanimeitor.json';
  document.body.appendChild(a); a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showToast('Proyecto guardado');
}}
function loadProject() {{
  document.getElementById('fileInput').click();
}}
async function handleFileLoad(e) {{
  const file = e.target.files?.[0];
  if (!file) return;
  try {{
    const text = await file.text();
    const project = JSON.parse(text);
    if (!project.frames || !Array.isArray(project.frames)) throw new Error('Formato inválido');
    state.frames = project.frames;
    state.currentIdx = 0;
    state.bgColor = project.bgColor || '#FFFFFF';
    state.fps = project.fps || 8;
    state.undoStack = []; state.redoStack = [];
    state.isPlaying = false;
    loadCurrentFrame();
    renderFrames(); renderBgPresets(); updateBgDisplay();
    document.getElementById('fpsSlider').value = state.fps;
    showToast('Proyecto cargado');
  }} catch (err) {{
    alert('No se pudo cargar: ' + err.message);
  }}
  e.target.value = '';
}}

function newAnimation() {{
  if (state.frames.length > 1 || state.frames[0].data !== emptyFrame()) {{
    if (!confirm('¿Empezar una animación nueva? Se perderán los cambios sin guardar.')) return;
  }}
  state.frames = [{{ id: uid(), data: emptyFrame(), duration: 100 }}];
  state.currentIdx = 0;
  state.undoStack = []; state.redoStack = [];
  state.isPlaying = false;
  loadCurrentFrame();
  renderFrames();
}}

// ====== Wire events ======
drawCanvas.addEventListener('pointerdown', onPointerDown);
drawCanvas.addEventListener('pointermove', onPointerMove);
drawCanvas.addEventListener('pointerup', onPointerUp);
drawCanvas.addEventListener('pointercancel', onPointerUp);

document.getElementById('btnNew').addEventListener('click', newAnimation);
document.getElementById('btnSave').addEventListener('click', saveProject);
document.getElementById('btnLoad').addEventListener('click', loadProject);
document.getElementById('btnExport').addEventListener('click', exportGif);
document.getElementById('btnAdd').addEventListener('click', addFrame);
document.getElementById('btnDuplicate').addEventListener('click', duplicateFrame);
document.getElementById('btnDelete').addEventListener('click', deleteFrame);
document.getElementById('btnClear').addEventListener('click', clearFrame);
document.getElementById('btnFirst').addEventListener('click', setAsFirst);
document.getElementById('btnUp').addEventListener('click', () => moveFrame(-1));
document.getElementById('btnDown').addEventListener('click', () => moveFrame(1));
document.getElementById('btnPlay').addEventListener('click', togglePlay);
document.getElementById('btnPrev').addEventListener('click', () => {{
  state.isPlaying = false; updatePlayButton();
  state.currentIdx = (state.currentIdx - 1 + state.frames.length) % state.frames.length;
  loadCurrentFrame(); renderFrames();
}});
document.getElementById('btnNext').addEventListener('click', () => {{
  state.isPlaying = false; updatePlayButton();
  state.currentIdx = (state.currentIdx + 1) % state.frames.length;
  loadCurrentFrame(); renderFrames();
}});

document.getElementById('btnHelp').addEventListener('click', () => {{
  document.getElementById('helpDialog').showModal();
}});
document.getElementById('dialogClose').addEventListener('click', () => {{
  document.getElementById('helpDialog').close();
}});

document.getElementById('fpsSlider').addEventListener('input', e => {{
  state.fps = parseInt(e.target.value);
  updateUI();
}});
document.getElementById('brushSlider').addEventListener('input', e => {{
  state.brushSize = parseInt(e.target.value);
  updateUI();
}});
document.getElementById('onionToggle').addEventListener('change', e => {{
  state.onionSkin = e.target.checked;
  previewCtx.clearRect(0,0,CANVAS_W,CANVAS_H);
  if (state.onionSkin && state.currentIdx > 0) drawOnionSkin();
}});

// Color picker
document.getElementById('colorPickerToggle').addEventListener('click', () => {{
  const area = document.getElementById('colorPickerArea');
  area.style.display = area.style.display === 'none' ? 'flex' : 'none';
}});
document.getElementById('customColorInput').addEventListener('input', e => {{
  state.color = e.target.value;
  state.customColor = e.target.value;
  document.getElementById('customColorText').value = e.target.value;
  renderPalette(); updateColorDisplay();
}});
document.getElementById('customColorText').addEventListener('input', e => {{
  const v = e.target.value;
  if (/^#[0-9A-Fa-f]{{6}}$/.test(v)) {{
    state.color = v;
    state.customColor = v;
    document.getElementById('customColorInput').value = v;
    renderPalette(); updateColorDisplay();
  }}
}});

// Background picker
document.getElementById('bgColorInput').addEventListener('input', e => {{
  state.bgColor = e.target.value;
  updateBgDisplay();
  renderFrames();
  loadCurrentFrame();
}});

document.getElementById('fileInput').addEventListener('change', handleFileLoad);

// Keyboard shortcuts
window.addEventListener('keydown', e => {{
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
  if (e.ctrlKey || e.metaKey) {{
    if (e.key === 'z' && !e.shiftKey) {{ e.preventDefault(); undo(); }}
    else if ((e.key === 'z' && e.shiftKey) || e.key === 'y') {{ e.preventDefault(); redo(); }}
    else if (e.key === 's') {{ e.preventDefault(); saveProject(); }}
    else if (e.key === 'e') {{ e.preventDefault(); exportGif(); }}
    else if (e.key === 'o') {{ e.preventDefault(); loadProject(); }}
    return;
  }}
  if (e.key === ' ') {{ e.preventDefault(); togglePlay(); }}
  else if (e.key === 'n') addFrame();
  else if (e.key === 'd') duplicateFrame();
  else if (e.key === 'o') {{
    state.onionSkin = !state.onionSkin;
    document.getElementById('onionToggle').checked = state.onionSkin;
    previewCtx.clearRect(0,0,CANVAS_W,CANVAS_H);
    if (state.onionSkin && state.currentIdx > 0) drawOnionSkin();
  }}
  else if (e.key === 'j') {{
    state.isPlaying = false; updatePlayButton();
    state.currentIdx = (state.currentIdx - 1 + state.frames.length) % state.frames.length;
    loadCurrentFrame(); renderFrames();
  }}
  else if (e.key === 'k') {{
    state.isPlaying = false; updatePlayButton();
    state.currentIdx = (state.currentIdx + 1) % state.frames.length;
    loadCurrentFrame(); renderFrames();
  }}
  else if (/^[1-7]$/.test(e.key)) {{
    state.tool = TOOLS[parseInt(e.key)-1].id;
    renderToolRail();
  }}
}});

// Init
renderToolRail();
renderPalette();
renderBgPresets();
updateColorDisplay();
updateBgDisplay();
updateUI();
loadCurrentFrame();
renderFrames();
</script>
</body>
</html>
"""

OUT = '/home/z/my-project/download/epanimeitor.html'
with open(OUT, 'w') as f:
    f.write(html)
size = os.path.getsize(OUT)
print(f'Wrote {OUT}: {size/1024:.1f} KB ({size} bytes)')
