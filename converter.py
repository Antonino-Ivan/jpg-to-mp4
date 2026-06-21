import os
import sys
import glob
from pathlib import Path

import numpy as np
from PIL import Image


DEFAULT_FPS = 24
DEFAULT_TOTAL_DURATION = 30
EXTENSIONS = ("*.jpg", "*.jpeg", "*.JPG", "*.JPEG")


def find_images(input_dir):
    images = []
    for ext in EXTENSIONS:
        images.extend(glob.glob(os.path.join(input_dir, ext)))
    return sorted(images)


def load_and_resize(image_paths, on_resize=None):
    sizes = {}
    for path in image_paths:
        with Image.open(path) as img:
            sz = img.size
            sizes[sz] = sizes.get(sz, 0) + 1
    target = max(sizes, key=sizes.get)

    frames = []
    for path in image_paths:
        with Image.open(path) as img:
            if img.size != target:
                if on_resize:
                    on_resize(path, img.size, target)
                img = img.resize(target, Image.LANCZOS)
            frames.append(np.array(img.convert("RGB")))
    return frames, target


def convert_images_to_video(
    input_dir,
    output_file,
    fps=DEFAULT_FPS,
    total_duration=DEFAULT_TOTAL_DURATION,
    progress_callback=None,
    log_callback=None,
):
    log = log_callback or print
    progress = progress_callback or (lambda p: None)

    try:
        from moviepy import ImageSequenceClip
    except ImportError:
        log("Errore: moviepy non è installato. Installa con: pip install moviepy")
        return False

    if not os.path.isdir(input_dir):
        log(f"Errore: la cartella '{input_dir}' non esiste.")
        return False

    log("Ricerca immagini in corso...")
    progress(0.05)
    images = find_images(input_dir)

    if not images:
        log(f"Errore: nessuna immagine JPG/JPEG trovata in '{input_dir}'.")
        return False

    log(f"Trovate {len(images)} immagini. Ordinamento completato.")
    progress(0.1)

    dur_per_image = total_duration / len(images)
    log(f"FPS: {fps} | Durata totale: {total_duration}s | Per immagine: {dur_per_image:.2f}s")
    progress(0.15)

    def on_resize(path, old_size, new_size):
        log(f"  Ridimensionamento: {os.path.basename(path)} ({old_size[0]}x{old_size[1]} → {new_size[0]}x{new_size[1]})")

    frames, target_size = load_and_resize(images, on_resize=on_resize)
    log(f"Dimensioni video: {target_size[0]}x{target_size[1]}")
    progress(0.4)

    log("Creazione clip video...")
    clip = ImageSequenceClip(
        sequence=frames,
        durations=[dur_per_image] * len(frames),
    )
    progress(0.5)

    log(f"Scrittura {output_file}... (codec: libx264)")
    clip.write_videofile(output_file, codec="libx264", fps=fps, logger=None)
    progress(1.0)
    log(f"Video creato con successo: {output_file}")
    return True


def main():
    input_dir = sys.argv[1] if len(sys.argv) > 1 else "immagini"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "output.mp4"

    success = convert_images_to_video(input_dir, output_file)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
