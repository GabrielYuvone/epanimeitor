#!/usr/bin/env python3
"""Optimize logos and embed as base64 in a TS module."""
import base64
import os
from PIL import Image

UPLOAD = '/home/z/my-project/upload'
OUT = '/home/z/my-project/src/lib/animation/logos.ts'

# Target display widths (in CSS px); render at 2x for retina
LOGO_TARGET_W = 720    # Epanimator banner — displayed ~360px
INTRO_TARGET_W = 240   # logointro badge — displayed ~120px


def optimize(path: str, target_w: int) -> bytes:
    im = Image.open(path)
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    # Resize with LANCZOS
    ratio = target_w / im.width
    new_size = (target_w, int(im.height * ratio))
    im = im.resize(new_size, Image.LANCZOS)
    # Save as optimized PNG
    import io
    buf = io.BytesIO()
    im.save(buf, format='PNG', optimize=True)
    return buf.getvalue()


def main():
    logo_png = optimize(f'{UPLOAD}/EPANIMATOR-logo.png', LOGO_TARGET_W)
    intro_png = optimize(f'{UPLOAD}/logointro.png', INTRO_TARGET_W)

    print(f'Logo optimized: {len(logo_png)} bytes ({len(logo_png)/1024:.1f} KB)')
    print(f'Intro optimized: {len(intro_png)} bytes ({len(intro_png)/1024:.1f} KB)')

    logo_b64 = base64.b64encode(logo_png).decode('ascii')
    intro_b64 = base64.b64encode(intro_png).decode('ascii')

    # Verify dimensions
    from io import BytesIO
    l_im = Image.open(BytesIO(logo_png))
    i_im = Image.open(BytesIO(intro_png))
    print(f'Logo final: {l_im.size}')
    print(f'Intro final: {i_im.size}')

    ts = f'''// Logos de Epanimeitor embebidos como base64 (optimizados)
// Epanimator-logo.png: banner principal con look cinematográfico
// logointro.png: badge circular "Escuela para Animadores ROSARIO"

export const EPANIMATOR_LOGO = "data:image/png;base64,{logo_b64}" as const;
export const LOGO_INTRO = "data:image/png;base64,{intro_b64}" as const;
'''
    with open(OUT, 'w') as f:
        f.write(ts)
    print(f'\nWrote {OUT} ({os.path.getsize(OUT)} bytes)')


if __name__ == '__main__':
    main()
