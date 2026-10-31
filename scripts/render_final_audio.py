"""Concatena los segmentos de voz (TTSMaker) del examen final en los MP3 finales.

Ingeniería de Sistemas · podcasts pendientes de mezcla:
  - web/media/audio/isn-tec-podcast-tecnico.mp3      (8 segmentos)
  - web/media/audio/isn-pro-podcast-prospectivo.mp3  (6 segmentos)

Los segmentos de voz se descargan de TTSMaker siguiendo el manual en
web/entregables/guiones-prototipo.md (sección "Examen final") y se guardan como
web/media/audio/voz/<episodio>-<NN>.mp3 (01, 02, ...). Solo se concatena un
episodio cuando están TODOS sus segmentos; si falta alguno, se informa y se
mantiene el MP3 anterior intacto.

Uso:  python scripts/render_final_audio.py
"""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

try:
    import imageio_ffmpeg

    FFMPEG = Path(imageio_ffmpeg.get_ffmpeg_exe())
except ImportError:
    FFMPEG = Path(r"C:\ffmpeg\ffmpeg.exe")

ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / "web" / "media"
VOICE = MEDIA / "audio" / "voz"

# (prefijo de segmento, número de segmentos, archivo final, slot en media-links.json)
EPISODES = [
    ("isn-tec-podcast", 8, "isn-tec-podcast-tecnico.mp3", "isn-tec-podcast"),
    ("isn-pro-podcast", 6, "isn-pro-podcast-prospectivo.mp3", "isn-pro-podcast"),
]

SITE_BASE = "https://supelanopro387.github.io/Fredy-Parcial/media/audio/"


def audio_duration(path: Path) -> float:
    """Duración (s) del MP3 vía ffprobe de imageio-ffmpeg; 0.0 si falla."""
    if not path.exists():
        return 0.0
    ffprobe = FFMPEG.with_name(FFMPEG.name.replace("ffmpeg", "ffprobe"))
    if not ffprobe.exists():
        return 0.0
    result = subprocess.run(
        [str(ffprobe), "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    try:
        return float(result.stdout.strip())
    except ValueError:
        return 0.0


def segment_name(prefix: str, index: int, suffix: str = ".mp3") -> str:
    return f"{prefix}-{index:02d}{suffix}"


def concat_audio(prefix: str, count: int, filename: str, media_id: str) -> Path | None:
    paths = [VOICE / segment_name(prefix, i) for i in range(1, count + 1)]
    segments = [path for path in paths if path.exists()]
    missing = [path.name for path in paths if not path.exists()]

    if missing:
        print(f"  [EN PRODUCCIÓN] {filename}: faltan {len(missing)}/{count} segmentos "
              f"({', '.join(missing)}). Se conserva la mezcla previa.")
        return None

    output = MEDIA / "audio" / filename
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="fesna-final-audio-") as temp_dir:
        concat_file = Path(temp_dir) / "audio.txt"
        with concat_file.open("w", encoding="utf-8") as playlist:
            for segment in segments:
                path = segment.resolve().as_posix()
                playlist.write(f"file '{path}'\n")
        subprocess.run(
            [str(FFMPEG), "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file),
             "-c:a", "libmp3lame", "-b:a", "96k", str(output)],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
        )
    duration = audio_duration(output)
    print(f"  [OK] {output.name} ← {count} segmentos · {duration:.1f} s")
    publish_link(filename, media_id)
    return output


def publish_link(filename: str, media_id: str) -> None:
    """Activa el enlace del producto en media-links.json (de null a URL publicada)."""
    links_path = ROOT / "web" / "media-links.json"
    try:
        import json

        config = json.loads(links_path.read_text(encoding="utf-8"))
        products = config.setdefault("products", {})
        if products.get(media_id) != SITE_BASE + filename:
            products[media_id] = SITE_BASE + filename
            links_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"  [ENLACE] {media_id} → {SITE_BASE + filename}")
    except (OSError, ValueError) as error:
        print(f"  [AVISO] No se pudo actualizar media-links.json: {error}")


def main() -> None:
    if not FFMPEG.exists():
        raise SystemExit("FFmpeg no disponible: instala imageio-ffmpeg (pip install imageio-ffmpeg).")
    if not VOICE.exists():
        raise SystemExit(f"No existe la carpeta de voces: {VOICE}")

    print("Mezclando podcasts del examen final (Ingeniería de Sistemas)…")
    done = 0
    for prefix, count, filename, media_id in EPISODES:
        if concat_audio(prefix, count, filename, media_id):
            done += 1
    print(f"Listo: {done}/{len(EPISODES)} episodios mezclados. "
          "Después de cargar narraciones, re-ejecuta scripts/render_final_media.py "
          "para incrustar las voces en los videos.")


if __name__ == "__main__":
    main()
