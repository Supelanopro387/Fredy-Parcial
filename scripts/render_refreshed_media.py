"""Create the two redesigned animated explainers with original moving graphics."""

from __future__ import annotations

import math
import re
import struct
import subprocess
import tempfile
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

try:
    import imageio_ffmpeg

    FFMPEG = Path(imageio_ffmpeg.get_ffmpeg_exe())
except ImportError:
    FFMPEG = Path(r"C:\ffmpeg\ffmpeg.exe")

ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / "web" / "media"
REGULAR = Path(r"C:\Windows\Fonts\segoeui.ttf")
BOLD = Path(r"C:\Windows\Fonts\segoeuib.ttf")
WIDTH, HEIGHT = 1280, 720
FPS = 15

NAVY = (17, 40, 63)
BLUE = (28, 82, 135)
ORANGE = (237, 103, 56)
TEAL = (18, 139, 130)
PAPER = (247, 246, 241)
WHITE = (255, 255, 255)
MUTED = (91, 108, 119)
LINE = (214, 222, 222)
PURPLE = (112, 76, 158)
LILAC = (232, 225, 243)
MINT = (212, 238, 225)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = BOLD if bold else REGULAR
    if path.exists():
        return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def rounded(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill: tuple[int, int, int],
            outline: tuple[int, int, int] | None = None, radius: int = 20, width: int = 2) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def text_center(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str,
                face: ImageFont.ImageFont, fill: tuple[int, int, int]) -> None:
    draw.text(xy, text, font=face, fill=fill, anchor="mm")


def brand_header(draw: ImageDraw.ImageDraw, area: str, accent: tuple[int, int, int]) -> None:
    rounded(draw, (58, 38, 151, 79), WHITE, LINE, 12, 2)
    draw.text((77, 47), "FESNA", font=font(18, True), fill=NAVY)
    draw.text((170, 49), "FUNDACIÓN DE EDUCACIÓN SUPERIOR NUEVA AMÉRICA",
              font=font(13, True), fill=NAVY)
    draw.line((58, 91, 1222, 91), fill=LINE, width=2)
    draw.text((59, 106), area.upper(), font=font(12, True), fill=accent)


def progress_footer(draw: ImageDraw.ImageDraw, scene: int, phase: float, total: int,
                    accent: tuple[int, int, int], note: str = "") -> None:
    x0, x1, y = 60, 1220, 685
    draw.rounded_rectangle((x0, y, x1, y + 7), radius=3, fill=(220, 225, 222))
    portion = (scene + phase) / total
    draw.rounded_rectangle((x0, y, int(x0 + (x1 - x0) * portion), y + 7), radius=3, fill=accent)
    draw.text((60, 653), note, font=font(11), fill=MUTED)
    draw.text((1172, 111), f"{scene + 1:02d} / {total:02d}", font=font(14, True), fill=accent)


def draw_admin_person(draw: ImageDraw.ImageDraw, cx: int, cy: int, color: tuple[int, int, int],
                      scale: float = 1.0) -> None:
    r = int(17 * scale)
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 223, 189), outline=color, width=max(2, int(3 * scale)))
    draw.rounded_rectangle((cx - int(28 * scale), cy + r, cx + int(28 * scale), cy + int(84 * scale)),
                           radius=int(18 * scale), fill=color)


def admin_frame(scene: int, phase: float) -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), PAPER)
    draw = ImageDraw.Draw(image)
    accent = ORANGE if scene in (0, 3) else TEAL
    brand_header(draw, "Administración de Empresas · Motion graphics", accent)
    progress_footer(draw, scene, phase, 4, accent,
                    "Propuesta conceptual · esquemas ilustrativos, no datos estadísticos de FESNA")

    headings = [
        ("UNA IDEA SE CONVIERTE EN ACCIÓN", "Identifica una oportunidad antes de decidir."),
        ("LIDERAZGO QUE CONECTA", "Alinea personas, información y decisiones."),
        ("PLAN DE NEGOCIO", "Organiza mercado, operación y recursos."),
        ("SEGUIMIENTO CON PROPÓSITO", "Mide avances y considera a las personas y el entorno."),
    ]
    title, subtitle = headings[scene]
    draw.text((62, 143), title, font=font(31, True), fill=NAVY)
    draw.text((62, 190), subtitle, font=font(18), fill=MUTED)

    if scene == 0:
        # An opportunity marker travels through a process path.
        rounded(draw, (68, 268, 1210, 599), WHITE, LINE, 28, 2)
        labels = [("OBSERVA", 190), ("PREGUNTA", 490), ("DECIDE", 800), ("ACTÚA", 1080)]
        draw.line((190, 420, 1080, 420), fill=(220, 225, 222), width=14)
        for index, (label, cx) in enumerate(labels):
            draw.ellipse((cx - 45, 375, cx + 45, 465), fill=WHITE,
                         outline=TEAL if index < 3 else ORANGE, width=6)
            text_center(draw, (cx, 420), f"0{index + 1}", font(22, True), NAVY)
            text_center(draw, (cx, 500), label, font(13, True), NAVY)
        marker_x = int(190 + phase * 890)
        draw.ellipse((marker_x - 13, 407, marker_x + 13, 433), fill=ORANGE)
        draw.ellipse((marker_x - 22, 398, marker_x + 22, 442), outline=ORANGE, width=2)
        rounded(draw, (745, 292, 1168, 353), MINT, None, 15)
        draw.text((772, 311), "ANÁLISIS · PROPÓSITO · ACCIÓN", font=font(15, True), fill=NAVY)

    elif scene == 1:
        # A team network assembles around a shared decision.
        rounded(draw, (68, 258, 1210, 599), WHITE, LINE, 28, 2)
        cx, cy = 639, 433
        orbit = 218
        nodes = []
        for index in range(4):
            angle = (index / 4) * math.tau - math.pi / 2 + phase * 0.12
            nodes.append((int(cx + math.cos(angle) * orbit), int(cy + math.sin(angle) * orbit * .62)))
        for x, y in nodes:
            draw.line((cx, cy, x, y), fill=LINE, width=5)
        draw.ellipse((cx - 78, cy - 78, cx + 78, cy + 78), fill=(243, 235, 215), outline=ORANGE, width=5)
        text_center(draw, (cx, cy - 8), "VISIÓN", font(17, True), NAVY)
        text_center(draw, (cx, cy + 22), "COMÚN", font(14, True), ORANGE)
        labels = ["EQUIPO", "CLIENTES", "OPERACIÓN", "ENTORNO"]
        for (x, y), label in zip(nodes, labels):
            draw_admin_person(draw, x, y - 5, BLUE if label in ("EQUIPO", "OPERACIÓN") else TEAL, .72)
            rounded(draw, (x - 77, y + 73, x + 77, y + 111), (239, 244, 241), None, 10)
            text_center(draw, (x, y + 92), label, font(12, True), NAVY)
        pulse = int(8 + 10 * abs(math.sin(phase * math.pi * 3)))
        draw.ellipse((cx - 78 - pulse, cy - 78 - pulse, cx + 78 + pulse, cy + 78 + pulse), outline=(244, 204, 169), width=2)

    elif scene == 2:
        # Bars grow as the planning categories appear; no institutional figures are used.
        rounded(draw, (68, 255, 1210, 599), WHITE, LINE, 28, 2)
        draw.line((180, 530, 1110, 530), fill=NAVY, width=3)
        draw.line((180, 310, 180, 530), fill=NAVY, width=3)
        bars = [(350, .68, BLUE, "MERCADO"), (640, .86, TEAL, "OPERACIÓN"), (930, .52, ORANGE, "RECURSOS")]
        for x, height, color, label in bars:
            h = int((160 + 70 * phase) * height)
            rounded(draw, (x - 60, 530 - h, x + 60, 530), color, None, 13)
            text_center(draw, (x, 566), label, font(13, True), NAVY)
            draw.ellipse((x - 7, 530 - h - 9, x + 7, 530 - h + 5), fill=WHITE)
        draw.text((222, 295), "PLANEA · PRUEBA · AJUSTA", font=font(16, True), fill=TEAL)
        draw.text((222, 320), "Relaciones ilustrativas", font=font(12), fill=MUTED)

    else:
        # The closing frame turns three considerations into a review loop.
        rounded(draw, (68, 257, 1210, 599), WHITE, LINE, 28, 2)
        centers = [(340, 421), (640, 421), (940, 421)]
        colors = [TEAL, ORANGE, BLUE]
        labels = [("PERSONAS", "Liderazgo"), ("ENTORNO", "Responsabilidad"), ("AVANCES", "Seguimiento")]
        draw.line((340, 421, 940, 421), fill=LINE, width=8)
        for index, (center, color, label_pair) in enumerate(zip(centers, colors, labels)):
            x, y = center
            pulse = int(2 + 8 * abs(math.sin(phase * math.pi * 2 + index)))
            draw.ellipse((x - 75 - pulse, y - 75 - pulse, x + 75 + pulse, y + 75 + pulse),
                         fill=WHITE, outline=color, width=5)
            text_center(draw, (x, y - 10), label_pair[0], font(15, True), color)
            text_center(draw, (x, y + 20), label_pair[1], font(12), NAVY)
        draw.text((730, 554), "Administración de Empresas · SNIES 111357 presencial · 111750 virtual",
                  font=font(13, True), fill=NAVY)

    return image


def draw_accounting_frame(scene: int, phase: float) -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), (249, 247, 252))
    draw = ImageDraw.Draw(image)
    brand_header(draw, "Tecnología en Gestión Contable y Financiera · Animación 2D", PURPLE)
    progress_footer(draw, scene, phase, 4, PURPLE,
                    "Ejemplo didáctico con datos ficticios · no representa cifras de FESNA")
    headings = [
        ("¿QUÉ COMPARA LA RAZÓN CORRIENTE?", "Recursos disponibles y obligaciones de corto plazo."),
        ("1 · ACTIVO CORRIENTE", "Ejemplo inventado: recursos de corto plazo = 150."),
        ("2 · PASIVO CORRIENTE", "Ejemplo inventado: obligaciones de corto plazo = 100."),
        ("3 · INTERPRETA CON CONTEXTO", "Razón corriente = activo corriente ÷ pasivo corriente."),
    ]
    title, subtitle = headings[scene]
    draw.text((62, 144), title, font=font(30, True), fill=NAVY)
    draw.text((62, 193), subtitle, font=font(18), fill=MUTED)
    rounded(draw, (70, 258, 1208, 600), WHITE, (224, 218, 234), 26, 2)

    if scene == 0:
        draw.text((110, 298), "EMPRESA FICTICIA", font=font(13, True), fill=PURPLE)
        # An animated ledger book opens into two colorful account columns.
        split = int(635 + 170 * phase)
        rounded(draw, (195, 365, split, 520), (238, 232, 246), None, 19)
        rounded(draw, (1280 - split, 365, 1085, 520), (238, 232, 246), None, 19)
        draw.line((640, 350, 640, 536), fill=PURPLE, width=4)
        draw.text((265, 409), "ACTIVOS", font=font(21, True), fill=TEAL)
        draw.text((265, 454), "¿Qué recursos tiene?", font=font(15), fill=NAVY)
        draw.text((805, 409), "OBLIGACIONES", font=font(19, True), fill=ORANGE)
        draw.text((805, 454), "¿Qué debe a corto plazo?", font=font(15), fill=NAVY)
        for i in range(5):
            x = 435 + i * 23
            offset = int(16 * phase)
            draw.ellipse((x, 485 - offset, x + 24, 509 - offset), fill=(248, 196, 79), outline=ORANGE, width=1)
        for i in range(4):
            y = 480 - int(20 * phase)
            rounded(draw, (905, y - i * 5, 957, y + 10 - i * 5), (255, 239, 221), ORANGE, 3, 1)

    elif scene in (1, 2):
        color = TEAL if scene == 1 else ORANGE
        label = "ACTIVO CORRIENTE" if scene == 1 else "PASIVO CORRIENTE"
        value = 150 if scene == 1 else 100
        draw.text((117, 300), "BALANCE DE UNA EMPRESA FICTICIA", font=font(13, True), fill=PURPLE)
        rounded(draw, (145, 355, 1135, 540), (247, 246, 250), LINE, 20, 2)
        draw.text((190, 385), label, font=font(23, True), fill=NAVY)
        current = max(0, int(value * phase))
        bar_w = int(740 * current / 160)
        rounded(draw, (190, 450, 190 + 740, 486), (230, 228, 235), None, 14)
        if bar_w:
            rounded(draw, (190, 450, 190 + bar_w, 486), color, None, 14)
        draw.text((990, 438), str(current), font=font(36, True), fill=color)
        # Side icon is a moving cluster of coins/invoices, not a reused card motif.
        icon_x = 1030 if scene == 1 else 1025
        for index in range(5):
            rise = int(24 * phase)
            if scene == 1:
                y = 338 - index * 18 - rise
                draw.ellipse((icon_x - 42, y, icon_x + 42, y + 17), fill=(255, 220, 118), outline=ORANGE, width=2)
                draw.rectangle((icon_x - 42, y + 7, icon_x + 42, y + 20), fill=(255, 220, 118))
            else:
                y = 335 + index * 30 - rise
                rounded(draw, (icon_x - 38, y, icon_x + 38, y + 24), (255, 239, 221), ORANGE, 4, 2)
                draw.line((icon_x - 22, y + 12, icon_x + 22, y + 12), fill=ORANGE, width=2)

    else:
        # The fraction and dial animate into view before the caution cards appear.
        draw.text((130, 300), "RAZÓN CORRIENTE", font=font(15, True), fill=PURPLE)
        draw.text((205, 345), "150", font=font(54, True), fill=TEAL)
        draw.line((168, 418, 366, 418), fill=PURPLE, width=5)
        draw.text((205, 431), "100", font=font(54, True), fill=ORANGE)
        draw.text((417, 395), "=", font=font(48, True), fill=MUTED)
        draw.text((495, 375), "1,5", font=font(76, True), fill=NAVY)
        draw.text((525, 466), "INDICADOR", font=font(14, True), fill=PURPLE)
        draw.rounded_rectangle((478, 510, 640, 522), radius=6, fill=(230, 228, 235))
        draw.rounded_rectangle((478, 510, int(478 + 162 * phase), 522), radius=6, fill=TEAL)
        pointer_x = int(478 + 162 * phase)
        draw.ellipse((pointer_x - 9, 501, pointer_x + 9, 519), fill=ORANGE, outline=WHITE, width=2)
        for index, label in enumerate(("COMPOSICIÓN", "VENCIMIENTOS", "FLUJO DE CAJA")):
            x = 712 + index * 145
            card_phase = max(0, min(1, (phase - index * .18) / .72))
            y = int(357 + (1 - card_phase) * 32)
            rounded(draw, (x, y, x + 125, y + 112), (244, 239, 248), (220, 211, 231), 16, 2)
            text_center(draw, (x + 62, y + 45), label, font(10, True), PURPLE)
            draw.line((x + 25, y + 78, x + 100, y + 78), fill=TEAL, width=4)
        draw.text((135, 548), "150 ÷ 100 = 1,5 · DATOS DE EJEMPLO", font=font(14, True), fill=MUTED)

    return image


def audio_duration(path: Path) -> float:
    result = subprocess.run([str(FFMPEG), "-i", str(path)], capture_output=True, text=True, check=False)
    match = re.search(r"Duration: (\d+):(\d+):(\d+(?:\.\d+)?)", result.stderr or "")
    if not match:
        raise RuntimeError(f"Could not read audio duration: {path}")
    return int(match.group(1)) * 3600 + int(match.group(2)) * 60 + float(match.group(3))


def write_original_jingle(path: Path, duration: float, theme: str) -> None:
    """Synthesize a short original four-note radio signature; no stock music is used."""
    sample_rate = 44100
    motifs = {
        "admin": (523.25, 659.25, 783.99, 1046.5),
        "conta": (392.0, 493.88, 587.33, 783.99),
    }
    notes = motifs[theme]
    note_length = .28
    total_samples = int(duration * sample_rate)
    frames = bytearray()
    for sample_index in range(total_samples):
        time = sample_index / sample_rate
        step = time % (note_length * len(notes))
        note_index = min(len(notes) - 1, int(step / note_length))
        note_time = step - note_index * note_length
        envelope = min(1.0, note_time / .014) * max(0.0, 1.0 - note_time / note_length)
        melody = math.sin(2 * math.pi * notes[note_index] * note_time) * envelope * .075
        bass = math.sin(2 * math.pi * 130.81 * time) * .012
        fade = min(1.0, max(0.0, (duration - time) / .85))
        sample = max(-1.0, min(1.0, (melody + bass) * fade))
        frames.extend(struct.pack("<h", int(sample * 32767)))
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(frames)


def render_radio_spot(narration: Path, output: Path, theme: str) -> None:
    voice_duration = audio_duration(narration)
    bed_duration = voice_duration + 1.5
    with tempfile.TemporaryDirectory(prefix="fesna-radio-") as temp_dir:
        bed = Path(temp_dir) / "original-radio-sting.wav"
        write_original_jingle(bed, bed_duration, theme)
        command = [str(FFMPEG), "-y", "-hide_banner", "-loglevel", "error",
                   "-i", str(bed), "-i", str(narration), "-filter_complex",
                   "[0:a]volume=0.9[bed];[1:a]adelay=650|650[voice];"
                   "[bed][voice]amix=inputs=2:duration=longest:dropout_transition=1,alimiter=limit=0.97[a]",
                   "-map", "[a]", "-c:a", "libmp3lame", "-b:a", "128k", str(output)]
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    print(f"Rendered {output.relative_to(ROOT)} ({output.stat().st_size // 1024} KB)")


def render_animated_video(filename: str, draw_scene, accent: tuple[int, int, int],
                          program: str, narration: Path | None = None,
                          total_duration: float = 22.0) -> Path:
    output = MEDIA / "video" / filename
    output.parent.mkdir(parents=True, exist_ok=True)
    voice_duration = audio_duration(narration) if narration and narration.exists() else 0.0
    duration = max(total_duration, voice_duration + 1.0)
    scene_duration = duration / 4
    frame_count = math.ceil(duration * FPS)
    transition = .35

    with tempfile.TemporaryDirectory(prefix="fesna-animated-") as temp_dir:
        temp = Path(temp_dir)
        for frame_index in range(frame_count):
            timestamp = frame_index / FPS
            scene = min(3, int(timestamp / scene_duration))
            local = timestamp - scene * scene_duration
            phase = max(0.0, min(1.0, local / scene_duration))
            frame = draw_scene(scene, phase)
            if scene < 3 and local >= scene_duration - transition:
                blend = (local - (scene_duration - transition)) / transition
                next_scene = draw_scene(scene + 1, max(0.0, blend))
                frame = Image.blend(frame, next_scene, blend)
            frame.save(temp / f"frame-{frame_index:05d}.jpg", format="JPEG", quality=88, optimize=True)

        command = [str(FFMPEG), "-y", "-hide_banner", "-loglevel", "error",
                   "-framerate", str(FPS), "-i", str(temp / "frame-%05d.jpg")]
        if narration and narration.exists():
            command += ["-i", str(narration), "-filter_complex", "[1:a]apad=pad_dur=1[a]",
                        "-map", "0:v:0", "-map", "[a]", "-t", f"{duration:.3f}",
                        "-c:a", "aac", "-b:a", "128k"]
        else:
            command += ["-map", "0:v:0", "-an"]
        command += ["-vf", "fps=24,format=yuv420p", "-c:v", "libx264", "-preset", "veryfast",
                    "-crf", "24", "-movflags", "+faststart", str(output)]
        result = subprocess.run(command, check=False, stdout=subprocess.DEVNULL,
                                 stderr=subprocess.PIPE, text=True)
        if result.returncode:
            raise RuntimeError(f"FFmpeg failed to render {filename}: {result.stderr}")
    print(f"Rendered {output.relative_to(ROOT)} ({output.stat().st_size // 1024} KB)")
    return output


def main() -> None:
    if not FFMPEG.exists():
        raise FileNotFoundError(f"FFmpeg not found at {FFMPEG}")
    assets = [
        render_animated_video("admin-prof-motion-graphics.mp4", admin_frame, ORANGE,
                             "Administración de Empresas · SNIES 111357 / 111750", None, 24),
        render_animated_video("conta-tec-animacion-2d.mp4", draw_accounting_frame, PURPLE,
                             "Tecnología en Gestión Contable y Financiera", MEDIA / "audio" / "voz" / "conta-tec-animacion.mp3", 24),
    ]
    for path in assets:
        print(f"Available for the existing portfolio link: {path.name}")

    render_radio_spot(MEDIA / "audio" / "voz" / "admin-tec-spot-camila.mp3",
                     MEDIA / "audio" / "admin-spot-voz-ia.mp3", "admin")
    render_radio_spot(MEDIA / "audio" / "voz" / "conta-tp-cuna-camila.mp3",
                     MEDIA / "audio" / "conta-tp-cuna.mp3", "conta")


if __name__ == "__main__":
    main()
