# Epanimeitor

Animador de GIFs **frame a frame** que funciona directamente en el navegador.
Simple, colorido y gratuito. Pensado para escuelas, talleres y cualquiera que
quiera contar historias en movimiento sin instalar nada.

> Herramienta de la **Escuela para Animadores Rosario**.

## Stack

- [Next.js 16](https://nextjs.org/) + TypeScript
- Tailwind CSS + shadcn/ui
- [gifenc](https://github.com/mattdesl/gifenc) para la exportación a GIF

## Funcionalidades

- 7 herramientas de dibujo: lápiz, pincel, borrador, línea, rectángulo, círculo y relleno (flood fill)
- Paleta de 16 colores + selector personalizado
- Tamaño de pincel ajustable (1–50 px)
- Color de fondo dinámico (9 presets + color picker)
- Línea de tiempo con añadir / duplicar / borrar / limpiar / reordenar / marcar como primero
- Reproducción con FPS ajustable (1–24) y play/pause
- **Onion skin**: ve el fotograma anterior al 30 % de opacidad
- Undo / Redo con historial de hasta 30 pasos
- Atajos de teclado completos
- Exportar a GIF (formato GIF89a, 600×450)
- Guardar / Cargar proyecto como JSON

## Cómo usarlo

```bash
bun install
bun run dev
```

Abrí http://localhost:3000 en el navegador.

## Cómo distribuirlo

El manual de uso completo está en [`download/Epanimeitor-Manual-de-Uso.pdf`](download/Epanimeitor-Manual-de-Uso.pdf).

## Estructura

```
src/
├── app/
│   ├── layout.tsx           # metadata de la app (título, idioma)
│   └── page.tsx             # wrapper que carga el editor
├── components/
│   └── animation/
│       ├── AnimationEditor.tsx   # editor completo (toolbar, canvas, timeline, panels)
│       └── DrawingCanvas.tsx     # canvas con onion skin
└── lib/
    └── animation/
        ├── types.ts         # tipos y constantes
        ├── utils.ts         # export GIF, helpers de canvas
        └── logos.ts         # logos en base64 (auto-generado)
```

## Atajos principales

| Tecla       | Acción                          |
|-------------|---------------------------------|
| `Espacio`   | Reproducir / pausar             |
| `N`         | Nuevo fotograma                 |
| `D`         | Duplicar fotograma              |
| `O`         | Activar / desactivar onion skin |
| `J` / `K`   | Fotograma anterior / siguiente  |
| `1`–`7`     | Seleccionar herramienta         |
| `Ctrl+Z`    | Deshacer                        |
| `Ctrl+S`    | Guardar proyecto                |
| `Ctrl+E`    | Exportar GIF                    |

## Licencia

MIT — usalo, copialo, enseñalo, mejoralo.

---

Escuela para Animadores · Rosario · Argentina
