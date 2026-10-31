"""Render the FESNA final-exam assets: Ingeniería de Sistemas and Marketing y Publicidad."""

from __future__ import annotations

import math
import re
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

try:
    import imageio_ffmpeg

    FFMPEG = Path(imageio_ffmpeg.get_ffmpeg_exe())
except ImportError:
    FFMPEG = Path(r"C:\ffmpeg\ffmpeg.exe")

ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / "web" / "media"
FONT_REGULAR = Path(r"C:\Windows\Fonts\segoeui.ttf")
FONT_BOLD = Path(r"C:\Windows\Fonts\segoeuib.ttf")
FONT_MONO = Path(r"C:\Windows\Fonts\consolab.ttf")

INK = (7, 16, 21)
PANEL = (15, 31, 39)
PANEL_LIGHT = (20, 45, 51)
WHITE = (240, 248, 246)
MUTED = (169, 190, 190)
CYAN = (64, 199, 255)
CORAL = (255, 122, 89)
YELLOW = (255, 209, 102)

# ============ shared helpers (kept in sync with scripts/render_media.py) ============


def font(size: int, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_MONO if mono and FONT_MONO.exists() else FONT_BOLD if bold and FONT_BOLD.exists() else FONT_REGULAR
    if path.exists():
        return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def wrap_text(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.ImageFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if current and draw.textbbox((0, 0), candidate, font=face)[2] > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def draw_lines(draw: ImageDraw.ImageDraw, lines: list[str], xy: tuple[int, int], face: ImageFont.ImageFont,
               fill: tuple[int, int, int], spacing: int = 10) -> int:
    x, y = xy
    for line in lines:
        draw.text((x, y), line, font=face, fill=fill)
        y += face.size + spacing
    return y


def rounded(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill: tuple[int, int, int],
            outline: tuple[int, int, int] | None = None, radius: int = 20, width: int = 2) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def audio_duration(path: Path) -> float:
    result = subprocess.run([str(FFMPEG), "-i", str(path)], capture_output=True, text=True, check=False)
    match = re.search(r"Duration: (\d+):(\d+):(\d+(?:\.\d+)?)", result.stderr or "")
    if not match:
        return 0.0
    return int(match.group(1)) * 3600 + int(match.group(2)) * 60 + float(match.group(3))


def render_slide(path: Path, size: tuple[int, int], accent: tuple[int, int, int],
                 title: str, body: str, label: str, visual: str,
                 footer: str, step: int, total: int, program: str) -> None:
    width, height = size
    image = Image.new("RGB", size, INK)
    draw = ImageDraw.Draw(image)
    for y in range(height):
        ratio = y / max(1, height - 1)
        col = tuple(int(INK[i] * (1 - ratio * .22) + PANEL[i] * ratio * .22) for i in range(3))
        draw.line((0, y, width, y), fill=col)
    margin = int(width * .07)
    draw.rectangle((0, 0, 12, height), fill=accent)
    for x in range(margin, width, 54):
        draw.line((x, 0, x, height), fill=(11, 27, 32), width=1)
    for y in range(0, height, 54):
        draw.line((0, y, width, y), fill=(11, 27, 32), width=1)
    vertical = height > width
    draw.text((margin, int(height * .075)), "FESNA  ·  FUNDACIÓN DE EDUCACIÓN SUPERIOR NUEVA AMÉRICA",
              font=font(18 if not vertical else 16, True), fill=accent)
    draw.text((margin, int(height * .13)), program.upper(), font=font(13 if not vertical else 12), fill=MUTED)
    draw.text((width - margin - 110, int(height * .13)), f"{step:02d} / {total:02d}", font=font(14, True), fill=accent)

    title_face = font(45 if not vertical else 42, True)
    title_lines = wrap_text(draw, title, title_face, width - margin * 2)
    title_y = int(height * .21)
    title_y = draw_lines(draw, title_lines[:3], (margin, title_y), title_face, WHITE, 8)
    label_y = title_y + 10
    draw.text((margin, label_y), label.upper(), font=font(13 if not vertical else 12, True), fill=accent)
    body_lines = wrap_text(draw, body, font(23 if not vertical else 21), width - margin * 2)
    body_y = label_y + 42
    draw_lines(draw, body_lines[:5 if not vertical else 7], (margin, body_y), font(23 if not vertical else 21), MUTED, 10)

    visual_top = int(height * (.68 if not vertical else .55))
    visual_box = (margin, visual_top, width - margin, int(height * .91))
    draw_visual(draw, visual_box, visual, accent)

    footer_y = height - int(height * .055)
    draw.text((margin, footer_y), footer, font=font(11 if not vertical else 10), fill=(137, 163, 163))
    bar_y = height - 8
    bar_left, bar_right = margin, width - margin
    draw.rounded_rectangle((bar_left, bar_y, bar_right, bar_y + 3), radius=2, fill=(43, 66, 68))
    progress_right = bar_left + int((bar_right - bar_left) * step / total)
    draw.rounded_rectangle((bar_left, bar_y, progress_right, bar_y + 3), radius=2, fill=accent)
    image.save(path, format="PNG", optimize=True)


def render_video(filename: str, program: str, accent: tuple[int, int, int],
                 scenes: list[tuple[str, str, str, str]], orientation: str = "landscape",
                 narration: Path | None = None, minimum_duration: float = 18.0) -> Path:
    width, height = (720, 1280) if orientation == "vertical" else (1280, 720)
    output = MEDIA / "video" / filename
    output.parent.mkdir(parents=True, exist_ok=True)
    voice_length = audio_duration(narration) if narration and narration.exists() else 0.0
    total_duration = max(minimum_duration, voice_length + 1.0)
    fps = 24
    scene_duration = total_duration / len(scenes)

    with tempfile.TemporaryDirectory(prefix="fesna-final-render-") as temp_dir:
        temp = Path(temp_dir)
        playlist_path = temp / "scenes.txt"
        clip_paths: list[Path] = []
        for index, scene in enumerate(scenes, start=1):
            frame = temp / f"scene-{index:02d}.png"
            clip = temp / f"clip-{index:02d}.mp4"
            title, body, label, visual = scene
            render_slide(frame, (width, height), accent, title, body, label, visual,
                         "Verifica los datos institucionales antes de publicar.",
                         index, len(scenes), program)
            zoom_filter = (
                f"zoompan=z='min(zoom+0.0006,1.045)':x='iw/2-(iw/zoom/2)':"
                f"y='ih/2-(ih/zoom/2)':d=1:s={width}x{height}:fps={fps},format=yuv420p"
            )
            clip_command = [str(FFMPEG), "-y", "-hide_banner", "-loglevel", "error",
                            "-loop", "1", "-framerate", str(fps), "-t", f"{scene_duration:.3f}",
                            "-i", str(frame), "-vf", zoom_filter, "-an", "-c:v", "libx264",
                            "-preset", "veryfast", "-crf", "27", "-pix_fmt", "yuv420p",
                            "-movflags", "+faststart", str(clip)]
            subprocess.run(clip_command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            clip_paths.append(clip)

        with playlist_path.open("w", encoding="utf-8") as playlist:
            for clip in clip_paths:
                safe_path = clip.resolve().as_posix().replace("'", "'\\''")
                playlist.write(f"file '{safe_path}'\n")

        command = [str(FFMPEG), "-y", "-hide_banner", "-loglevel", "error",
                   "-f", "concat", "-safe", "0", "-i", str(playlist_path)]
        if narration and narration.exists():
            command += ["-i", str(narration), "-map", "0:v:0", "-map", "1:a:0", "-shortest",
                        "-c:a", "aac", "-b:a", "96k"]
        else:
            command += ["-map", "0:v:0", "-an"]
        command += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "27",
                    "-movflags", "+faststart", str(output)]
        result = subprocess.run(command, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        if result.returncode:
            raise RuntimeError(f"FFmpeg failed to render {filename}: {result.stderr}")
    return output


def text_center(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str,
                face: ImageFont.ImageFont, fill: tuple[int, int, int]) -> None:
    draw.text(xy, text, font=face, fill=fill, anchor="mm")


def chip(draw: ImageDraw.ImageDraw, x: int, y: int, label: str, accent: tuple[int, int, int],
         mono: bool = False, size: int = 13, dark: bool = True) -> int:
    face = font(size, True, mono=mono)
    w = draw.textbbox((0, 0), label, font=face)[2] + 22
    if dark:
        rounded(draw, (x, y, x + w, y + size + 14), (9, 25, 31), accent, 9, 2)
        draw.text((x + 11, y + 6), label, font=face, fill=WHITE if dark else INK)
    else:
        rounded(draw, (x, y, x + w, y + size + 14), (240, 244, 246), accent, 9, 2)
        draw.text((x + 11, y + 6), label, font=face, fill=INK)
    return w


def draw_visual(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], kind: str, accent: tuple[int, int, int]) -> None:
    x1, y1, x2, y2 = box
    rounded(draw, box, PANEL_LIGHT, outline=(48, 82, 84), radius=22)
    w, h = x2 - x1, y2 - y1

    if kind == "code":
        draw.text((x1 + 20, y1 + 14), "editor.py · ejemplo didáctico", font=font(12, mono=True), fill=MUTED)
        draw.line((x1 + 18, y1 + 40, x2 - 18, y1 + 40), fill=(48, 82, 84), width=2)
        rows = [("edad = 16", CYAN), ("nombre = \"Ana\"", YELLOW),
                ("si edad >= 18:", WHITE), ("    print(f\"{nombre}, mayor de edad\")", MUTED),
                ("y_reportado = False", YELLOW)]
        y = y1 + 56
        for text, color in rows:
            draw.line((x1 + 26, y + 4, x1 + 26, y + 18), fill=(48, 82, 84), width=1)
            draw.text((x1 + 44, y), text, font=font(15, mono=True), fill=color)
            y += 27
        chip(draw, x1 + 20, y2 - 34, "VARIABLES · IDENTIFICADORES · CONDICIONAL", accent, mono=True, size=12)
    elif kind == "sdlc":
        cx, cy = x1 + w // 2, y1 + h // 2 - 6
        r = min(w, h) // 3
        steps = 5
        labels = ["PLANEA", "DISEÑA", "CONSTRUYE", "PRUEBA", "MANTIENE"]
        for i in range(steps):
            angle = -math.tau * .25 + math.tau * i / steps + math.tau * .055
            px, py = int(cx + math.cos(angle) * r), int(cy + math.sin(angle) * r)
            draw.line((cx, cy, px, py), fill=(48, 82, 84), width=2)
            draw.ellipse((px - 9, py - 9, px + 9, py + 9), fill=INK, outline=accent, width=3)
        draw.arc((cx - r, cy - r, cx + r, cy + r), 0, 360, fill=accent, width=5)
        head_angle = -math.tau * .25 + math.tau * .055 + math.tau * .04
        hx, hy = cx + math.cos(head_angle + .28) * r, cy + math.sin(head_angle + .28) * r
        arrow = [(hx, hy - 11), (hx - 10, hy + 7), (hx + 10, hy + 7)]
        draw.polygon(arrow, fill=accent)
        draw.text((cx - 21, cy - 9), "SDLC", font=font(15, True), fill=accent)
        for i, label in enumerate(labels):
            angle = -math.tau * .25 + math.tau * i / steps + math.tau * .055
            lx, ly = int(cx + math.cos(angle) * (r + 44)), int(cy + math.sin(angle) * (r + 30))
            text_center(draw, (lx, ly), label, font(12, True), WHITE)
        draw.text((x1 + 20, y2 - 34), "CICLO DE VIDA DEL SOFTWARE · ILUSTRATIVO", font=font(11), fill=MUTED)
    elif kind == "db":
        tables = [("ESTUDIANTE", ["id", "nombre", "correo"], x1 + 26), ("CURSO", ["id", "título"], x1 + w // 2 + 30),
                  ("INSCRIPCIÓN", ["estudiante_id", "curso_id"], x1 + w // 2 - 110)]
        for name, cols, tx in tables:
            tw, ty = 210, y1 + 48
            rounded(draw, (tx, ty, tx + tw, ty + 34), (9, 25, 31), accent, 10, 2)
            draw.text((tx + 12, ty + 7), name, font=font(13, True), fill=accent)
            for j, col in enumerate(cols):
                y_ = ty + 50 + j * 27
                rounded(draw, (tx, y_, tx + tw, y_ + 24), (13, 35, 41), None, 7)
                draw.text((tx + 12, y_ + 4), col, font=font(12, mono=True), fill=WHITE)
        draw.line((x1 + 236, y1 + 106, x1 + w // 2 + 16, y1 + 106), fill=accent, width=3)
        draw.line((x1 + w // 2 + 90, y1 + 118, x1 + w // 2 + 90, y1 + 96), fill=accent, width=3)
        chip(draw, x1 + 20, y2 - 36, "ENTIDADES · LLAVES · RELACIONES (ESQUEMA EJEMPLO)", accent, size=12)
    elif kind == "idea":
        labels = ["PROBLEMA", "ALTERNATIVAS", "PROTOTIPO", "EVIDENCIA"]
        gap = 10
        item_w = (w - 48 - gap * 3) // 4
        cy = y1 + h // 2
        for i, label in enumerate(labels):
            left = x1 + 24 + i * (item_w + gap)
            rounded(draw, (left, y1 + 30, left + item_w, y2 - 30), (10, 26, 32), accent, 15, 2)
            draw.ellipse((left + item_w // 2 - 20, cy - 39, left + item_w // 2 + 20, cy + 1), fill=(24, 64, 65))
            draw.text((left + item_w // 2 - 12, cy - 30), f"{i + 1:02d}", font=font(13, True), fill=accent)
            ltw = draw.textbbox((0, 0), label, font=font(13, True))[2]
            draw.text((left + (item_w - ltw) // 2, cy + 31), label, font=font(13, True), fill=WHITE)
            if i < len(labels) - 1:
                draw.line((left + item_w, cy, left + item_w + gap, cy), fill=accent, width=3)
        draw.text((x1 + 22, y2 - 22), "MÉTODO: CRITERIO HUMANO + APOYO DE IA", font=font(12), fill=MUTED)
    elif kind == "pieces":
        cards = [(x1 + 20, y1 + 24, "RUTA 01", "APRENDE A COMUNICAR", "Ciclos propedéuticos"),
                 (x1 + w // 2 - 64, y1 + 24, "PIEZA 02", "VENTA CON PROPÓSITO", "Fases de la venta"),
                 (x1 + 20, y1 + h // 2 + 2, "PIEZA 03", "ATENCIÓN QUE RESPONDE", "Protocolo"),
                 (x1 + w // 2 - 64, y1 + h // 2 + 2, "PIEZA 04", "TU MENSAJE, AL PUNTO", "Copy claro")]
        card_w, card_h = (w - 84) // 2, h // 2 - 46
        for cx1, cy1, kicker, headline, sub in cards:
            rounded(draw, (cx1, cy1, cx1 + card_w, cy1 + card_h), (14, 34, 40), accent, 14, 2)
            draw.text((cx1 + 14, cy1 + 12), kicker, font=font(10, True), fill=accent)
            ty = cy1 + 34
            for line in wrap_text(draw, headline, font(15, True), card_w - 28)[:2]:
                draw.text((cx1 + 14, ty), line, font=font(15, True), fill=WHITE)
                ty += 20
            draw.text((cx1 + 14, cy1 + card_h - 30), sub, font=font(10), fill=MUTED)
            rounded(draw, (cx1 + 14, cy1 + card_h - 52, cx1 + 96, cy1 + card_h - 34), accent, None, 8)
            draw.text((cx1 + 22, cy1 + card_h - 49), "FESNA", font=font(11, True), fill=INK)
        draw.text((x1 + 20, y2 - 22), "PIEZAS DEMOSTRATIVAS · SIN PROMESAS", font=font(11), fill=MUTED)
    elif kind == "persona":
        px, py = x1 + 50, y1 + (h - 120) // 2 + 14
        draw.ellipse((px - 40, py - 40, px + 40, py + 40), fill=(28, 72, 73), outline=accent, width=4)
        draw.ellipse((px - 30, py - 33, px + 30, py + 32), fill=(236, 194, 160))
        draw.pieslice((px - 35, py - 40, px + 35, py + 16), 180, 360, fill=(55, 42, 48))
        draw.ellipse((px - 15, py - 7, px - 6, py + 2), fill=INK)
        draw.ellipse((px + 6, py - 7, px + 15, py + 2), fill=INK)
        draw.arc((px - 12, py + 9, px + 12, py + 25), 0, 180, fill=(117, 57, 61), width=2)
        draw.text((x1 + 116, y1 + 26), "PERSONA FICTICIA · EJEMPLO DE USO", font=font(11, True), fill=accent)
        draw.text((x1 + 116, y1 + 48), "Andrea · 26 años", font=font(21, True), fill=WHITE)
        draw.text((x1 + 116, y1 + 76), "Aspirante interesada en marketing digital", font=font(13), fill=MUTED)
        traits = [("Objetivo", 80), ("Canal favorito", 62), ("Estilo de compra", 48)]
        ty = y1 + 118
        for label, pct in traits:
            draw.text((x1 + 26, ty), label, font=font(12, True), fill=WHITE)
            bw = (w - 120) * pct / 100
            rounded(draw, (x1 + 160, ty + 2, x1 + 160 + bw, ty + 14), accent, None, 6)
            rounded(draw, (x1 + 160, ty + 2, x1 + 160 + (w - 120), ty + 14), (16, 36, 42), None, 6)
            ty += 32
        draw.text((x1 + 26, y2 - 30), "PERFIL DEMOSTRATIVO PARA EJEMPLO ACADÉMICO", font=font(10), fill=MUTED)
    elif kind == "kpi":
        levels = [("IMPRESIONES", .96), ("CLICS", .62), ("REGISTROS", .30)]
        ly = y1 + 30
        for label, ratio in levels:
            lw = int((w - 160) * ratio)
            rounded(draw, (x1 + 60, ly, x1 + 60 + lw, ly + 44), (10, 26, 32), accent, 12, 2)
            lw2 = draw.textbbox((0, 0), label, font=font(12, True))[2]
            draw.text((x1 + 60 + (lw - lw2) // 2, ly + 13), label, font=font(12, True), fill=WHITE)
            ly += 58
        chips = ["CTR", "CPC", "CPA", "ROAS"]
        cx = x1 + 26
        for label in chips:
            cx += chip(draw, cx, y2 - 40, label, accent) + 10
        draw.text((x1 + w - 132, y1 + 24), "SIMULACIÓN", font=font(12, True), fill=accent)
        draw.text((x1 + 26, y1 + h - 76), "CONVERSIÓN POR ETAPA · EJEMPLO", font=font(11), fill=MUTED)
    elif kind == "trends":
        pts_x = 110
        baseline = y2 - 62
        draw.line((x1 + pts_x - 24, baseline - 210, x1 + pts_x - 24, baseline), fill=(48, 82, 84), width=2)
        draw.line((x1 + pts_x - 24, baseline, x1 + w - 26, baseline), fill=(48, 82, 84), width=2)
        series = [("IA EN PAUTA", accent, [.2, .34, .5, .66, .85]),
                  ("COMERCIO SOCIAL", (91, 190, 209), [.16, .22, .34, .42, .52]),
                  ("PERSONALIZACIÓN", YELLOW, [.3, .38, .42, .5, .58])]
        span_x = (w - pts_x - 70)
        for label, color, vals in series:
            coords = []
            for i, v in enumerate(vals):
                cx_ = x1 + pts_x + int(span_x * i / (len(vals) - 1))
                cy_ = baseline - int(v * 230)
                coords.append((cx_, cy_))
            draw.line(coords, fill=color, width=4, joint="curve")
            for cx_, cy_ in coords:
                draw.ellipse((cx_ - 5, cy_ - 5, cx_ + 5, cy_ + 5), fill=INK, outline=color, width=2)
        for i, (label, color, _vals) in enumerate(series):
            draw.line((x1 + 26, y1 + 22 + i * 20, x1 + 52, y1 + 22 + i * 20), fill=color, width=4)
            draw.text((x1 + 60, y1 + 16 + i * 20), label, font=font(11, True), fill=WHITE)
        draw.text((x1 + pts_x - 24, y2 - 34), "SIN CIFRAS REALES · CURVAS ILUSTRATIVAS", font=font(10), fill=MUTED)
    elif kind == "deck":
        draw.text((x1 + 26, y1 + 22), "PITCH DECK · MARCA FICTICIA", font=font(11, True), fill=accent)
        draw.text((x1 + 26, y1 + 48), "AURORA · CAFÉ DE ORIGEN", font=font(24, True), fill=WHITE)
        draw.text((x1 + 26, y1 + 84), "Lanzamiento internacional — presentación demostrativa", font=font(13), fill=MUTED)
        slide_labels = ["PROBLEMA", "SOLUCIÓN", "MERCADO", "MODELO", "HOJA DE RUTA"]
        gap = 10
        item_w = (w - 52 - gap * (len(slide_labels) - 1)) // len(slide_labels)
        for i, label in enumerate(slide_labels):
            left = x1 + 26 + i * (item_w + gap)
            rounded(draw, (left, y1 + 128, left + item_w, y1 + 168), (10, 26, 32), accent if i == 0 else (48, 82, 84), 10, 2)
            ltw = draw.textbbox((0, 0), label, font=font(10, True))[2]
            draw.text((left + (item_w - ltw) // 2, y1 + 139), label, font=font(10, True), fill=WHITE)
        draw.rounded_rectangle((x1 + 26, y2 - 44, x1 + 26 + int((w - 52) * .2), y2 - 38), radius=3, fill=accent)
        draw.rounded_rectangle((x1 + 26, y2 - 44, x1 + w - 26, y2 - 38), radius=3, fill=(43, 66, 68))
        draw.text((x1 + 26, y2 - 28), "NARRATIVA INTERACTIVA EN EL SITIO WEB", font=font(10), fill=MUTED)
    elif kind == "cycle":
        labels = ["RECEPCIÓN", "REGISTRO", "CLASIFICACIÓN", "RESPUESTA", "SEGUIMIENTO"]
        for i, label in enumerate(labels):
            left = x1 + 20 + i * ((w - 44) // len(labels))
            top = y1 + h // 2 - 34 + (6 if i % 2 else -6)
            rounded(draw, (left, top, left + (w - 44) // len(labels) - 8, top + 68), (9, 25, 31), accent, 12, 2)
            tl = wrap_text(draw, label, font(12, True), (w - 44) // len(labels) - 22)
            ty = top + 12 - 4 * (len(tl) - 1)
            for line in tl:
                draw.text((left + 10, ty), line, font=font(12, True), fill=WHITE)
                ty += 17
            if i < len(labels) - 1:
                draw.line((left + (w - 44) // len(labels) - 8, top + 34, left + (w - 44) // len(labels), top + 34), fill=accent, width=3)
        draw.text((x1 + 22, y2 - 26), "PANEL SIMULADO · FLUJO DE UNA SOLICITUD ACADÉMICA", font=font(11), fill=MUTED)
    else:
        labels = ["IDEA", "PLAN", "GESTIÓN", "REVISIÓN"]
        gap = 10
        item_w = (w - 48 - gap * 3) // 4
        cy = y1 + h // 2
        for i, label in enumerate(labels):
            left = x1 + 24 + i * (item_w + gap)
            rounded(draw, (left, y1 + 28, left + item_w, y2 - 28), (10, 26, 32), accent, 15, 2)
            draw.ellipse((left + item_w // 2 - 20, cy - 29, left + item_w // 2 + 20, cy + 11), fill=(24, 64, 65))
            draw.text((left + item_w // 2 - 13, cy - 20), f"{i + 1:02d}", font=font(12, True), fill=accent)
            label_width = draw.textbbox((0, 0), label, font=font(13, True))[2]
            draw.text((left + (item_w - label_width) // 2, cy + 29), label, font=font(13, True), fill=WHITE)
            if i < len(labels) - 1:
                draw.line((left + item_w, cy, left + item_w + gap, cy), fill=accent, width=3)
        draw.text((x1 + 22, y2 - 22), "FESNA · FORMACIÓN POR CICLOS PROPEDÉUTICOS", font=font(12), fill=MUTED)
def main() -> None:
    if not FFMPEG.exists():
        raise FileNotFoundError(f"FFmpeg not found at {FFMPEG}")

    assets = [
        render_is_infography(),
        render_mkt_pieces(),
        render_mkt_buyer(),
        render_mkt_plan(),
        render_mkt_pitch_cover(),
    ]
    for asset in assets:
        print(f"Rendered {asset.relative_to(ROOT)} ({asset.stat().st_size // 1024} KB)")

    render_supply_videos()

VOICE = MEDIA / "audio" / "voz"


def render_supply_videos() -> None:
    if not FFMPEG.exists():
        raise FileNotFoundError(f"FFmpeg not found at {FFMPEG}")
    (MEDIA / "video").mkdir(parents=True, exist_ok=True)

    products = [
        ("isn-tp-serie-reels-programacion.mp4", "T.P. en Procesos de Programación de Software", CYAN, "vertical",
         VOICE / "isn-tp-reels-narracion.mp3", 18,
         [("Variables y tipos de datos", "Una variable guarda un valor; los tipos comunes son número, texto y valor lógico.", "REEL 1 · FUNDAMENTOS", "code"),
          ("Condicionales", "El programa decide caminos: si la condición se cumple ejecuta un bloque; si no, otro.", "REEL 2 · DECISIONES", "code"),
          ("Ciclos y funciones", "Los ciclos repiten tareas y las funciones empaquetan pasos que se reutilizan.", "REEL 3 · ESTRUCTURAS", "flow"),
          ("Algoritmos: orden antes del código", "Un algoritmo organiza los pasos de la solución; practica la lógica antes de escribir código.", "SERIE EDUCATIVA · SNIES 111395", "code")]),
        ("isn-tec-video-explicativo-sistemas.mp4", "Tecnología en Gestión de Software y Sistemas", CYAN, "landscape",
         VOICE / "isn-tec-video-narracion.mp3", 18,
         [("El software sigue un ciclo de vida", "Del requisito al mantenimiento: cada fase tiene entradas, salidas y criterios de calidad.", "REQUISITOS", "sdlc"),
          ("Metodologías ágiles", "Sprints cortos con entrega continua y revisión de avance con el equipo.", "ITERACIÓN", "flow"),
          ("Bases de datos y sistemas de información", "Entidades, llaves y relaciones organizan los datos que las aplicaciones consultan.", "DATOS", "db"),
          ("Arquitectura y gestión de proyectos", "Componentes, alcance, tiempo y calidad se planifican con evidencia.", "CIERRE", "idea")]),
        ("isn-pro-solucion-tecnologica.mp4", "Ingeniería de Sistemas", CYAN, "landscape",
         VOICE / "isn-pro-solucion-narracion.mp3", 18,
         [("Una problemática real: trazabilidad", "Gestionar solicitudes académicas de forma ordenada cuesta tiempo y seguimiento.", "CONTEXTO", "cycle"),
          ("Idear con criterio propio", "Alternativas comparadas: automatización de consultas, panel de seguimiento y respuestas asistidas por IA.", "ANÁLISIS", "idea"),
          ("Prototipo y demostración", "Un prototipo web simula el flujo de una solicitud y permite medir su utilidad antes de construir el producto.", "IMPLEMENTACIÓN", "code"),
          ("IA con criterio humano", "La IA apoya el análisis; el ingeniero revisa, edita y decide la solución.", "CIERRE", "idea")]),
    ]
    for filename, program, accent, orientation, voice, minimum, scenes in products:
        output = render_video(filename, program, accent, scenes, orientation, voice, minimum)
        size = output.stat().st_size // 1024
        print(f"Rendered {output.relative_to(ROOT)} ({size} KB)")


# == PNG SHEETS ==


def _sheet_head(draw: ImageDraw.ImageDraw, size, accent, kicker: str, title: str, subtitle: str) -> None:
    draw.rectangle((0, 0, size[0], 18), fill=accent)
    draw.text((70, 66), f"FESNA · {kicker.upper()}", font=font(18, True), fill=accent)
    draw.text((70, 112), title, font=font(48, True), fill=(16, 37, 56))
    draw_lines(draw, wrap_text(draw, subtitle, font(22), size[0] - 140), (70, 178), font(22), (71, 91, 104), 6)


def _sheet_note(draw: ImageDraw.ImageDraw, box, text: str, accent=None, border=True) -> None:
    if border:
        rounded(draw, box, (231, 240, 245), outline=accent or (214, 222, 222), radius=14, width=2)
    else:
        rounded(draw, box, (231, 240, 245), radius=14)
    draw_lines(draw, wrap_text(draw, text, font(16, True), box[2] - box[0] - 54), (box[0] + 27, box[1] + 26),
               font(16, True), (16, 37, 56), 7)


def render_is_infography() -> Path:
    output = MEDIA / "infografias" / "isn-tp-fundamentos-programacion.png"
    size = (1500, 1700)
    accent = (10, 132, 177)
    dark = (16, 37, 56)
    muted = (71, 91, 104)
    image = Image.new("RGB", size, (246, 249, 248))
    draw = ImageDraw.Draw(image)
    _sheet_head(draw, size, accent, "TP en Procesos de Programación de Software",
                "Fundamentos de programación",
                "Serie de recursos didácticos para explicar variables, condicionales, ciclos, funciones y algoritmos en lenguaje sencillo.")

    blocks = [
        ("01 · VARIABLE", "Un espacio con nombre donde el programa guarda un dato, como la edad de una persona."),
        ("02 · TIPOS DE DATOS", "Número (16), texto (\"Ana\") y valores lógicos (verdadero/falso). Cada tipo define qué se puede hacer."),
        ("03 · CONDICIONAL", "El programa compara una condición y decide entre dos caminos posibles."),
        ("04 · CICLO", "Repite una acción mientras se cumpla una condición, por ejemplo recorrer una lista."),
        ("05 · FUNCIÓN", "Empaqueta pasos con nombre; puede recibir datos (parámetros) y devolver un resultado."),
        ("06 · ALGORITMO", "La secuencia ordenada de pasos que resuelve un problema antes de escribir el código."),
    ]
    block_y = 260
    for kicker, text in blocks:
        rounded(draw, (70, block_y, 1430, block_y + 150), (255, 255, 255), outline=(110, 159, 184), radius=13, width=2)
        draw.rounded_rectangle((70, block_y, 96, block_y + 150), radius=13, fill=accent)
        draw.text((118, block_y + 24), kicker, font=font(19, True), fill=accent)
        draw_lines(draw, wrap_text(draw, text, font(17), 1210), (118, block_y + 62), font(17), dark, 5)
        block_y += 176

    _sheet_note(draw, (70, block_y + 6, 1430, block_y + 196),
                "Versión estática de consulta. La infografía interactiva con definiciones desplegables está disponible en el sitio web del portafolio, sección “Productos interactivos”, y funciona en computador y celular.")
    draw.text((70, size[1] - 66), "Ilustración de autoría propia con asistencia de IA (Python/Pillow) para el examen final. Condiciones didácticas; consulta los contenidos oficiales del programa.", font=font(13), fill=muted)
    image.save(output, format="PNG", optimize=True)
    return output


def render_mkt_pieces() -> Path:
    output = MEDIA / "infografias" / "mkt-tp-piezas-graficas-comerciales.png"
    size = (1600, 1720)
    accent = (198, 60, 43)
    dark = (16, 37, 56)
    muted = (71, 91, 104)
    image = Image.new("RGB", size, (246, 249, 248))
    draw = ImageDraw.Draw(image)
    _sheet_head(draw, size, accent, "TP en Procesos de Comercialización y Comunicación Publicitaria",
                "Piezas gráficas comerciales",
                "Cuatro piezas demostrativas generadas con apoyo de IA para ejercitar mensajes persuasivos, protocolo de atención y promoción de ventas.")

    pieces = [
        ("PIEZA 01 · LISTADO COMERCIAL", "“Toda venta empieza en una conversación.”",
         "Promueve la ruta por ciclos propedéuticos y la pregunta como apertura comercial.", (10, 132, 177)),
        ("PIEZA 02 · TÉCNICAS DE VENTA", "“Escucha, registra, resuelve.”",
         "Resume fases de venta directa: contacto, demostración y cierre con registro.", (198, 60, 43)),
        ("PIEZA 03 · ATENCIÓN AL CLIENTE", "“Protocolo: saluda, identifica, actúa.”",
         "Cadena básica de atención al usuario para canales de difusión pública.", (18, 139, 130)),
        ("PIEZA 04 · MENSAJE PERSUASIVO", "“Tu capacidad de comunicar vale oro.”",
         "Copy claro para redes: beneficio en una línea y llamada a la acción mínima.", (112, 76, 158)),
    ]
    card_w, card_h = (1600 - 70 * 2 - 30) // 2, 420
    positions = [(70, 300), (70 + card_w + 30, 300), (70, 300 + card_h + 34), (70 + card_w + 30, 300 + card_h + 34)]
    for (kicker, headline, support, color), (cx, cy) in zip(pieces, positions):
        rounded(draw, (cx, cy, cx + card_w, cy + card_h), (255, 255, 255), outline=(214, 222, 222), radius=16, width=2)
        draw.rectangle((cx, cy, cx + 14, cy + card_h), fill=color)
        draw.text((cx + 40, cy + 26), "FESNA · FUNDACIÓN DE EDUCACIÓN SUPERIOR NUEVA AMÉRICA", font=font(13, True), fill=color)
        draw.text((cx + 40, cy + 62), f"{kicker}", font=font(16, True), fill=muted)
        draw_lines(draw, wrap_text(draw, headline, font(30, True), card_w - 90), (cx + 40, cy + 118), font(30, True), dark, 8)
        draw_lines(draw, wrap_text(draw, support, font(16), card_w - 90), (cx + 40, cy + 244), font(16), muted, 5)
        draw.rounded_rectangle((cx + 40, cy + card_h - 74, cx + 212, cy + card_h - 34), radius=10, fill=color)
        draw.text((cx + 58, cy + card_h - 66), "AGENDAR", font=font(15, True), fill=(255, 255, 255))
        draw.text((cx + 232, cy + card_h - 64), "CTA demostrativa", font=font(13), fill=muted)

    _sheet_note(draw, (70, 1540, 1530, 1636),
                "Piezas de autoría propia con asistencia de IA; sin fotografías de terceros ni logotipo institucional reproducido. Los mensajes son demostrativos: no prometen resultados, ni costos, ni beneficios no suministrados por FESNA.")
    draw.text((70, size[1] - 60), "Revisa ortografía, contraste y legibilidad en móvil y computador antes de publicar.", font=font(13), fill=muted)
    image.save(output, format="PNG", optimize=True)
    return output


def render_mkt_buyer() -> Path:
    output = MEDIA / "infografias" / "mkt-tec-buyer-persona-copys.png"
    size = (1500, 1700)
    accent = (198, 60, 43)
    dark = (16, 37, 56)
    muted = (71, 91, 104)
    image = Image.new("RGB", size, (246, 249, 252))
    draw = ImageDraw.Draw(image)
    _sheet_head(draw, size, accent, "Tecnología en Gestión Comercial y Publicidad",
                "Buyer persona y copys con IA",
                "Optimización de una audiencia objetivo y de sus mensajes publicitarios con IA generativa de textos; revisados y aprobados manualmente.")

    # Persona card
    rounded(draw, (70, 280, 830, 900), (255, 255, 255), outline=(214, 222, 222), radius=16, width=2)
    px, py = 180, 470
    draw.ellipse((px - 62, py - 62, px + 62, py + 62), fill=(232, 225, 243), outline=accent, width=4)
    draw.ellipse((px - 46, py - 51, px + 46, py + 49), fill=(236, 194, 160))
    draw.pieslice((px - 54, py - 62, px + 54, py + 24), 180, 360, fill=(55, 42, 48))
    draw.ellipse((px - 22, py - 11, px - 9, py + 3), fill=dark)
    draw.ellipse((px + 9, py - 11, px + 22, py + 3), fill=dark)
    draw.arc((px - 17, py + 14, px + 17, py + 44), 0, 180, fill=(117, 57, 61), width=3)
    draw.text((280, 330), "PERSONA FICTICIA · EJEMPLO ACADÉMICO", font=font(13, True), fill=accent)
    draw.text((280, 372), "Andrea · 26 años", font=font(32, True), fill=dark)
    draw.text((280, 424), "Aspirante a marketing digital", font=font(18), fill=muted)
    persona_rows = [
        ("Objetivo", "Avanzar por ciclos propedéuticos y aplicar lo aprendido en proyectos reales."),
        ("Dolores", "Mensajes publicitarios confusos y promesas que no pueden verificarse en la fuente."),
        ("Canales", "Redes sociales, buscadores y canales de mensajería de la institución."),
        ("Decisión", "Compara opciones, valida SNIES y modalidades antes de registrarse."),
    ]
    py_row = 560
    for label, text in persona_rows:
        draw.text((120, py_row), label.upper(), font=font(15, True), fill=accent)
        lines = wrap_text(draw, text, font(15), 640)
        draw_lines(draw, lines, (120, py_row + 26), font(15), dark, 4)
        py_row += 62 + (len(lines) - 1) * 22

    # Copys card
    rounded(draw, (860, 280, 1430, 900), (255, 255, 255), outline=(214, 222, 222), radius=16, width=2)
    draw.text((890, 320), "COPYS PUBLICITARIOS REVISADOS", font=font(16, True), fill=accent)
    copys = [
        ("Copy A · Beneficio", "“Describe lo que aprenderás: fundamentos de comunicación comercial y atención al usuario.”"),
        ("Copy B · Pregunta", "“¿Cómo se construye un mensaje que persuade? Teoría y práctica, por ciclos.”"),
        ("Copy C · Acción", "“Consulta la oferta oficial de FESNA y verifica el SNIES antes de decidir.”"),
    ]
    cy_copy = 400
    for kicker, text in copys:
        rounded(draw, (890, cy_copy, 1400, cy_copy + 118), (244, 239, 248), None, 12)
        draw.rounded_rectangle((890, cy_copy, 904, cy_copy + 118), radius=12, fill=accent)
        draw.text((920, cy_copy + 16), kicker, font=font(14, True), fill=accent)
        draw_lines(draw, wrap_text(draw, text, font(15), 460), (920, cy_copy + 44), font(15), dark, 4)
        cy_copy += 134
    draw_lines(draw, wrap_text(draw, "Prueba sugerida: dos variantes por pieza, midiendo clic, respuesta y matrícula consultada.", font(15), 480),
               (890, 806), font(15), muted, 5)

    _sheet_note(draw, (70, 960, 1430, 1180),
                "Uso de IA: se generaron variantes de texto y de perfil con IA generativa; el estudiante seleccionó, reescribió y aprobó cada versión. La persona es ficticia y no representa a un usuario real ni datos personales de nadie.")
    _sheet_note(draw, (70, 1240, 1430, 1460),
                "Los copys evitan promesas de empleo, salario o resultados. Verificables en la fuente: nombre oficial del programa, modalidad (presencial y virtual) y los códigos SNIES publicados institucionalmente.")

    draw.text((70, size[1] - 60), "Elaborado para el examen final con Pillow y apoyo de IA · Ilustración de autoría propia.", font=font(13), fill=muted)
    image.save(output, format="PNG", optimize=True)
    return output


def render_mkt_plan() -> Path:
    output = MEDIA / "infografias" / "mkt-prof-plan-predictivo-macrotendencias.png"
    size = (1500, 1700)
    accent = (144, 74, 178)
    dark = (16, 37, 56)
    muted = (71, 91, 104)
    image = Image.new("RGB", size, (246, 249, 252))
    draw = ImageDraw.Draw(image)
    _sheet_head(draw, size, accent, "Marketing y Publicidad · Nivel Profesional",
                "Plan de marketing predictivo",
                "Análisis de macrotendencias de consumo con enfoque de IA analítica: tendencias observables que orientan decisiones de mercadeo, sin cifras institucionales.")

    trends = [
        ("01 · IA EN PAUTA DIGITAL", "La IA analítica procesa señales de desempeño y creatividad para recomendar ajustes de campaña en tiempo real."),
        ("02 · COMERCIO SOCIAL", "La venta directa integra catálogo, pago y atención dentro de la misma red social."),
        ("03 · PERSONALIZACIÓN", "Las audiencias esperan mensajes por segmento; los modelos de predicción clasifican intereses y afinidades."),
        ("04 · DATOS PROPIOS", "Las marcas priorizan datos recopilados por consentimiento: calidad sobre volumen."),
    ]
    block_y = 300
    for kicker, text in trends:
        rounded(draw, (70, block_y, 1430, block_y + 118), (255, 255, 255), outline=(220, 211, 231), radius=13, width=2)
        draw.rounded_rectangle((70, block_y, 96, block_y + 118), radius=13, fill=accent)
        draw.text((118, block_y + 20), kicker, font=font(18, True), fill=accent)
        draw_lines(draw, wrap_text(draw, text, font(16), 1210), (118, block_y + 58), font(16), dark, 5)
        block_y += 142

    rounded(draw, (70, block_y + 4, 1430, block_y + 322), (255, 255, 255), outline=(220, 211, 231), radius=16, width=2)
    draw.text((100, block_y + 30), "HORIZONTE DE DECISIÓN (ILUSTRATIVO)", font=font(15, True), fill=accent)
    draw.text((100, block_y + 66), "Revisar fuentes de datos · señales cualitativas · vigencia de plataforma", font=font(15), fill=muted)
    pts_x = 320
    baseline = block_y + 280
    draw.line((pts_x - 16, baseline - 170, pts_x - 16, baseline), fill=(214, 222, 222), width=2)
    draw.line((pts_x - 16, baseline, 1400, baseline), fill=(214, 222, 222), width=2)
    series = [("IA en pauta", accent, [.24, .38, .55, .72, .88]),
              ("Comercio social", (18, 139, 130), [.18, .26, .38, .46, .56]),
              ("Personalización", (198, 60, 43), [.3, .4, .46, .55, .64])]
    span_x = 1400 - pts_x - 30
    for label, color, vals in series:
        coords = []
        for i, v in enumerate(vals):
            cx_ = pts_x + int(span_x * i / (len(vals) - 1))
            cy_ = baseline - int(v * 165)
            coords.append((cx_, cy_))
        draw.line(coords, fill=color, width=4, joint="curve")
        for cx_, cy_ in coords:
            draw.ellipse((cx_ - 5, cy_ - 5, cx_ + 5, cy_ + 5), fill=(255, 255, 255), outline=color, width=2)
    for i, (label, color, _vals) in enumerate(series):
        draw.line((100, block_y + 108 + i * 24, 126, block_y + 108 + i * 24), fill=color, width=4)
        draw.text((134, block_y + 102 + i * 24), label, font=font(12, True), fill=dark)
    draw.text((pts_x - 16, baseline + 10), "Curvas ilustrativas: no representan cifras reales de mercado.", font=font(12), fill=muted)

    _sheet_note(draw, (70, block_y + 352, 1430, block_y + 548),
                "El plan predictivo se apoya en la lectura de KPIs (CTR, CPC, CPA, ROAS) y en la vigilancia de macrotendencias. La versión interactiva con controles de escenarios está en el sitio web, sección “Productos interactivos”. No se incluyen datos de mercado de terceros ni cifras de FESNA.")
    draw.text((70, size[1] - 60), "Ilustración de autoría propia con asistencia de IA · Curvas didácticas sin cifras reales.", font=font(13), fill=muted)
    image.save(output, format="PNG", optimize=True)
    return output


def render_mkt_pitch_cover() -> Path:
    output = MEDIA / "infografias" / "mkt-prof-pitch-deck-portada.png"
    size = (1280, 720)
    accent = (255, 194, 77)
    image = Image.new("RGB", size, (24, 28, 46))
    draw = ImageDraw.Draw(image)
    for y in range(size[1]):
        ratio = y / (size[1] - 1)
        col = (int(24 + 14 * ratio), int(28 + 18 * ratio), int(46 + 40 * ratio))
        draw.line((0, y, size[0], y), fill=col)
    draw.rounded_rectangle((70, 246, 1210, 300), radius=12, fill=(36, 42, 66))
    draw.text((94, 262), "PITCH DECK · MARCA FICTICIA · LANZAMIENTO INTERNACIONAL", font=font(15, True), fill=accent)
    draw.text((70, 320), "AURORA · CAFÉ DE ORIGEN", font=font(64, True), fill=(245, 248, 252))
    draw.text((70, 424), "Narrativa interactiva de presentación creada y revisada con apoyo de IA.", font=font(22), fill=(196, 204, 224))
    draw.text((70, 466), "Seis láminas: problema, solución, mercado ilustrativo, modelo, equipo ficticio y hoja de ruta.", font=font(18), fill=(150, 160, 190))
    draw.rounded_rectangle((70, 520, 356, 566), radius=10, outline=accent, width=3)
    draw.text((94, 532), "→ Navegar láminas", font=font(17, True), fill=accent)
    draw.text((380, 538), "Versión navegable en el sitio web del portafolio.", font=font(14), fill=(150, 160, 190))
    draw.text((70, 636), "AURORA es una marca ficticia creada para el examen; no representa una empresa real ni promete productos o precios.", font=font(12), fill=(120, 130, 160))
    image.save(output, format="PNG", optimize=True)
    return output





if __name__ == '__main__':
    main()

