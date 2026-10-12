"""Render the FESNA campaign's original visual assets and MP4 storyboards."""

from __future__ import annotations

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

INK = (7, 16, 21)
PANEL = (15, 31, 39)
PANEL_LIGHT = (20, 45, 51)
WHITE = (240, 248, 246)
MUTED = (169, 190, 190)
MINT = (103, 255, 208)
LIME = (191, 255, 145)
VIOLET = (207, 135, 245)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_BOLD if bold and FONT_BOLD.exists() else FONT_REGULAR
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


def draw_visual(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], kind: str, accent: tuple[int, int, int]) -> None:
    x1, y1, x2, y2 = box
    rounded(draw, box, PANEL_LIGHT, outline=(48, 82, 84), radius=22)
    w, h = x2 - x1, y2 - y1
    if kind == "flow":
        labels = ["RECIBE", "REGISTRA", "CLASIFICA", "RESPONDE", "ARCHIVA"]
        gap = 8
        item_w = (w - 42 - gap * (len(labels) - 1)) // len(labels)
        for i, label in enumerate(labels):
            left = x1 + 20 + i * (item_w + gap)
            rounded(draw, (left, y1 + h // 2 - 31, left + item_w, y1 + h // 2 + 31), (9, 25, 31), accent, 12, 2)
            draw.text((left + 8, y1 + h // 2 - 8), label, font=font(13, True), fill=WHITE)
            if i < len(labels) - 1:
                draw.line((left + item_w, y1 + h // 2, left + item_w + gap, y1 + h // 2), fill=accent, width=3)
        draw.text((x1 + 22, y2 - 54), "FLUJO DOCUMENTAL · EJEMPLO EDUCATIVO", font=font(14), fill=MUTED)
    elif kind == "finance":
        draw.text((x1 + 24, y1 + 15), "RAZÓN CORRIENTE = ACTIVO CORRIENTE ÷ PASIVO CORRIENTE",
                  font=font(13, True), fill=accent)
        draw.text((x1 + 24, y1 + 48), "Activo corriente", font=font(22, True), fill=WHITE)
        draw.line((x1 + 23, y1 + 82, x1 + w - 24, y1 + 82), fill=accent, width=3)
        draw.text((x1 + 24, y1 + 91), "Pasivo corriente", font=font(22, True), fill=WHITE)
        draw.text((x1 + 24, y2 - 19), "DATOS FICTICIOS · INTERPRETA CON CONTEXTO", font=font(10), fill=MUTED)
    elif kind == "avatar":
        cx, cy = x1 + w // 2, y1 + 76
        draw.ellipse((cx - 42, cy - 42, cx + 42, cy + 42), fill=(28, 72, 73), outline=accent, width=4)
        draw.ellipse((cx - 32, cy - 35, cx + 32, cy + 34), fill=(236, 194, 160))
        draw.pieslice((cx - 37, cy - 42, cx + 37, cy + 20), 180, 360, fill=(55, 42, 48))
        draw.ellipse((cx - 18, cy - 8, cx - 9, cy + 1), fill=INK)
        draw.ellipse((cx + 9, cy - 8, cx + 18, cy + 1), fill=INK)
        draw.arc((cx - 15, cy + 7, cx + 15, cy + 24), 0, 180, fill=(117, 57, 61), width=2)
        draw.rounded_rectangle((cx - 55, cy + 48, cx + 55, y2 - 42), 23, fill=(97, 84, 163))
        draw.text((x1 + 18, y2 - 26), "VALERIA · PERSONA FICTICIA · VOZ SINTÉTICA", font=font(11, True), fill=accent)
    elif kind == "network":
        nodes = [(x1 + w * .20, y1 + h * .42), (x1 + w * .50, y1 + h * .26),
                 (x1 + w * .79, y1 + h * .42), (x1 + w * .37, y1 + h * .73),
                 (x1 + w * .68, y1 + h * .73)]
        links = [(0, 1), (1, 2), (0, 3), (1, 3), (1, 4), (2, 4), (3, 4)]
        for a, b in links:
            draw.line((nodes[a][0], nodes[a][1], nodes[b][0], nodes[b][1]), fill=(65, 122, 121), width=4)
        labels = ["IDEA", "ANÁLISIS", "OBJETIVO", "EQUIPO", "SEGUIMIENTO"]
        for (cx, cy), label in zip(nodes, labels):
            draw.ellipse((cx - 38, cy - 38, cx + 38, cy + 38), fill=(9, 25, 31), outline=accent, width=4)
            draw.text((cx - 31, cy - 8), label, font=font(11, True), fill=WHITE)
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


def audio_duration(path: Path) -> float:
    result = subprocess.run([str(FFMPEG), "-i", str(path)], capture_output=True, text=True, check=False)
    match = re.search(r"Duration: (\d+):(\d+):(\d+(?:\.\d+)?)", result.stderr or "")
    if not match:
        return 0.0
    return int(match.group(1)) * 3600 + int(match.group(2)) * 60 + float(match.group(3))


def render_video(filename: str, program: str, accent: tuple[int, int, int],
                 scenes: list[tuple[str, str, str, str]], orientation: str = "landscape",
                 narration: Path | None = None, minimum_duration: float = 16.0) -> Path:
    width, height = (720, 1280) if orientation == "vertical" else (1280, 720)
    output = MEDIA / "video" / filename
    output.parent.mkdir(parents=True, exist_ok=True)
    voice_length = audio_duration(narration) if narration and narration.exists() else 0.0
    total_duration = max(minimum_duration, voice_length + 1.0)
    fps = 24
    scene_duration = total_duration / len(scenes)

    with tempfile.TemporaryDirectory(prefix="fesna-render-") as temp_dir:
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


def concat_audio(parts: list[str], filename: str) -> Path:
    output = MEDIA / "audio" / filename
    with tempfile.TemporaryDirectory(prefix="fesna-audio-") as temp_dir:
        concat_file = Path(temp_dir) / "audio.txt"
        with concat_file.open("w", encoding="utf-8") as playlist:
            for part in parts:
                path = (MEDIA / "audio" / "voz" / part).resolve().as_posix()
                playlist.write(f"file '{path}'\n")
        subprocess.run([str(FFMPEG), "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file),
                        "-c:a", "libmp3lame", "-b:a", "96k", str(output)],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    return output


def render_infographic() -> Path:
    output = MEDIA / "infografias" / "admin-tp-estructura-organizacional-fesna.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    size = (1500, 1650)
    image = Image.new("RGB", size, (246, 249, 248))
    draw = ImageDraw.Draw(image)
    accent = (10, 73, 156)
    orange = (253, 83, 30)
    dark = (16, 37, 56)
    muted = (71, 91, 104)
    draw.rectangle((0, 0, size[0], 18), fill=accent)
    draw.rectangle((0, 18, size[0], 27), fill=orange)
    draw.text((70, 66), "FESNA · CAMPAÑA ACADÉMICA", font=font(18, True), fill=accent)
    draw.text((70, 112), "Estructura organizacional", font=font(48, True), fill=dark)
    draw.text((70, 174), "Versión didáctica resumida del organigrama institucional publicado por FESNA", font=font(22), fill=muted)

    def card(x: int, y: int, w: int, h: int, title: str, subtitle: str = "", fill: tuple[int, int, int] = (255, 255, 255),
             border: tuple[int, int, int] = (10, 73, 156), title_size: int = 16) -> None:
        rounded(draw, (x, y, x + w, y + h), fill, outline=border, radius=13, width=2)
        title_color = dark if sum(fill) > 650 else WHITE
        lines = wrap_text(draw, title, font(title_size, True), w - 24)
        ty = y + 12
        ty = draw_lines(draw, lines[:2], (x + 12, ty), font(title_size, True), title_color, 3)
        if subtitle:
            sub_lines = wrap_text(draw, subtitle, font(12), w - 24)
            draw_lines(draw, sub_lines[:2], (x + 12, min(ty + 4, y + h - 34)), font(12), muted, 2)

    # Governance chain and advisory roles follow the source organigram.
    card(585, 235, 330, 64, "ASAMBLEA GENERAL", fill=(12, 31, 52), border=orange, title_size=18)
    card(585, 335, 330, 64, "CONSEJO SUPERIOR", fill=(12, 31, 52), border=orange, title_size=18)
    card(585, 435, 330, 64, "RECTORÍA", fill=(12, 31, 52), border=orange, title_size=18)
    for y1, y2 in [(299, 335), (399, 435)]:
        draw.line((750, y1, 750, y2), fill=orange, width=4)
        draw.polygon([(742, y2 - 8), (758, y2 - 8), (750, y2)], fill=orange)
    card(92, 348, 260, 58, "REVISORÍA FISCAL", fill=(255, 255, 255), border=orange, title_size=14)
    card(1148, 328, 260, 58, "SECRETARÍA GENERAL", fill=(255, 255, 255), border=orange, title_size=14)
    card(1148, 401, 260, 58, "CONSEJO ACADÉMICO", fill=(255, 255, 255), border=orange, title_size=14)
    draw.line((352, 378, 530, 378), fill=(130, 153, 162), width=2)
    draw.line((915, 366, 1148, 366), fill=(130, 153, 162), width=2)

    # Three reporting branches: academic, units reporting to Rectoría, and administration/finance.
    columns = [(55, 450), (530, 440), (995, 450)]
    centers = [x + w // 2 for x, w in columns]
    draw.line((750, 499, 750, 536), fill=orange, width=4)
    draw.line((centers[0], 536, centers[2], 536), fill=orange, width=4)
    for center in centers:
        draw.line((center, 536, center, 565), fill=orange, width=4)
    card(columns[0][0], 565, columns[0][1], 66, "VICERRECTORÍA ACADÉMICA", fill=(183, 20, 20), border=orange, title_size=16)
    card(columns[1][0], 565, columns[1][1], 66, "UNIDADES QUE REPORTAN A RECTORÍA", fill=(12, 31, 52), border=orange, title_size=15)
    card(columns[2][0], 565, columns[2][1], 66, "VICERRECTORÍA ADMINISTRATIVA Y FINANCIERA", fill=(183, 20, 20), border=orange, title_size=15)

    academic = [
        ("Coordinación Académica", "Docentes · Registro y control"),
        ("Coordinación de Sector Externo", ""),
        ("Coordinación de Registro y Control", ""),
        ("Coordinación de Investigación", ""),
        ("Coordinación de Educación Virtual", ""),
    ]
    rector = [
        ("Dirección Comercial, Mercadeo y Ventas", "Asesor comercial · Convenios"),
        ("Calidad, Planeación y Autoevaluación Institucional", ""),
        ("Tecnologías y Recursos Audiovisuales", "Biblioteca · Laboratorios · Medios didácticos"),
        ("Bienestar Institucional", ""),
        ("Comunicaciones", ""),
        ("Proyectos Especiales y Educación Continuada", ""),
    ]
    admin = [
        ("Dirección Administrativa y de Gestión Humana", "Gestión humana · SST · Servicios generales · Recursos físicos"),
        ("Coordinación de Crédito Educativo", ""),
        ("Coordinación de Gestión Contable", "Auxiliar contable · Auxiliar de tesorería"),
    ]
    for index, (title, subtitle) in enumerate(academic):
        card(55, 650 + index * 118, 450, 96, title, subtitle, border=(110, 159, 184), title_size=15)
    for index, (title, subtitle) in enumerate(rector):
        card(530, 650 + index * 98, 440, 80, title, subtitle, border=(110, 159, 184), title_size=14)
    for index, (title, subtitle) in enumerate(admin):
        card(995, 650 + index * 155, 450, 128, title, subtitle, border=(110, 159, 184), title_size=15)

    note_y = 1300
    rounded(draw, (55, note_y, 1445, 1500), (231, 240, 245), outline=accent, radius=14, width=2)
    note = "Adaptación gráfica creada para el examen con apoyo de IA. Fuente de la estructura: Fundación de Educación Superior Nueva América, “Equipo y Estructura Organizacional” (PDF institucional, 2023). Consulta el documento oficial para ver el organigrama completo."
    draw_lines(draw, wrap_text(draw, note, font(16, True), 1320), (82, note_y + 28), font(16, True), dark, 7)
    draw.text((55, 1570), "No se reprodujo el logotipo institucional ni se inventaron dependencias o cargos.", font=font(13), fill=muted)
    image.save(output, format="PNG", optimize=True)
    return output


def main() -> None:
    if not FFMPEG.exists():
        raise FileNotFoundError(f"FFmpeg not found at {FFMPEG}")
    (MEDIA / "audio").mkdir(parents=True, exist_ok=True)
    admin_voice = MEDIA / "audio" / "voz" / "admin-tp-video-narration.mp3"
    admin_spot_voice = MEDIA / "audio" / "admin-spot-voz-ia.mp3"
    admin_prof_voice = MEDIA / "audio" / "voz" / "admin-prof-video-narration.mp3"
    reels_voice = MEDIA / "audio" / "voz" / "conta-tp-reels-narration.mp3"
    avatar_voice = MEDIA / "audio" / "voz" / "conta-prof-avatar-voice.mp3"

    # The two podcasts are multi-speaker TTSMaker exports; leave these final mixes intact.

    products = [
        ("admin-tp-video-explicativo.mp4", "Técnica Profesional en Procesos Administrativos Empresariales", MINT, "landscape", admin_voice, 18,
         [("Un documento tiene una ruta", "Toda gestión comienza al recibir una solicitud y reconocer el documento.", "RECEPCIÓN", "flow"),
          ("Registro y clasificación", "Se deja constancia de ingreso y se determina el tema y su responsable.", "ORGANIZACIÓN", "flow"),
          ("Trámite y respuesta", "El área asignada revisa la información, prepara respuesta y registra las acciones.", "SEGUIMIENTO", "flow"),
          ("Archivo y consulta", "Los documentos se organizan para consultar y conservar según las reglas vigentes.", "CIERRE", "flow")]),
        ("admin-tec-reel-promocional.mp4", "Tecnología en Gestión Administrativa", LIME, "vertical", admin_spot_voice, 17,
         [("Coordinar para avanzar", "¿Cómo se conectan las tareas en una organización?", "REEL · PROPUESTA", "nodes"),
          ("Supervisión", "Revisar tareas, avances y procesos del equipo.", "GESTIÓN", "nodes"),
          ("Talento humano y logística", "Personas y recursos aparecen conectados en una misma ruta.", "ORGANIZACIÓN", "nodes"),
          ("Conoce el programa", "Tecnología en Gestión Administrativa · SNIES 111385 presencial · 111386 virtual.", "FESNA", "nodes")]),
        ("admin-prof-video-institucional.mp4", "Administración de Empresas", MINT, "landscape", admin_prof_voice, 18,
         [("Una idea puede convertirse en acción", "El primer paso es reconocer una necesidad y pensar en una respuesta.", "VISIÓN DIRECTIVA", "nodes"),
          ("Planificar", "Objetivos, equipo y recursos se organizan para orientar el trabajo.", "PLAN DE NEGOCIO", "flow"),
          ("Liderar con responsabilidad", "Las decisiones consideran a las personas y el entorno.", "RESPONSABILIDAD SOCIAL", "nodes"),
          ("Administración de Empresas", "FESNA · SNIES 111357 presencial · 111750 virtual.", "CONSULTA LA OFERTA", "nodes")]),
        ("conta-tp-serie-reels.mp4", "Técnica Profesional en Procesos Contables", VIOLET, "vertical", reels_voice, 19,
         [("Tip 1 · Asientos contables", "Identifica la operación, revisa el soporte y verifica las cuentas.", "SERIE EDUCATIVA", "flow"),
          ("Tip 2 · Caja menor", "Registra los gastos y conserva los comprobantes.", "CONTROL", "finance"),
          ("Tip 3 · Archivo tributario", "Organiza documentos por periodo y protege la información.", "ARCHIVO", "flow"),
          ("Tip 4 · Nómina básica", "Revisa las novedades y valida el cálculo con reglas vigentes.", "TÉCNICA PROFESIONAL", "finance")]),
        ("conta-prof-testimonio-avatar-ficticio.mp4", "Contaduría Pública", VIOLET, "vertical", avatar_voice, 17,
         [("Testimonio demostrativo", "Avatar vectorial ficticio con voz sintética IA.", "NO REPRESENTA UNA PERSONA REAL", "avatar"),
          ("Valeria · personaje ficticio", "La ética contable requiere estudiar la norma y cuidar la evidencia.", "PERSONAJE DE EJEMPLO", "avatar"),
          ("Auditoría", "Documentación e independencia apoyan conclusiones profesionales responsables.", "TEMA EDUCATIVO", "avatar"),
          ("Revisar antes de concluir", "Consulta estándares vigentes y no atribuyas el testimonio a egresados reales.", "CONTADURÍA PÚBLICA", "avatar")]),
    ]
    for filename, program, accent, orientation, voice, minimum, scenes in products:
        output = render_video(filename, program, accent, scenes, orientation, voice, minimum)
        print(f"Rendered {output.relative_to(ROOT)} ({output.stat().st_size // 1024} KB)")

    infographic = render_infographic()
    print(f"Rendered {infographic.relative_to(ROOT)} ({infographic.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
