# 🎬 JPG to MP4 Converter

Turn a folder full of JPG/JPEG pictures into a single MP4 video — no fuss, no command-line knowledge needed.

Just point it at your images, pick how long you want the video to be, and hit convert.

---

## ✨ Features

- **Folder picker** – select any folder with images
- **Smart resize** – images of different sizes get auto-resized to the most common one
- **Live preview** – see your images before you convert
- **Flexible timing** – set FPS and total video duration
- **Progress bar** – know what's happening during conversion
- **Drag & drop ready** – or type the path manually
- **Dark / Light mode** – follows your system theme

---

## 🚀 How to use

1. **Open the app**

```bash
python3 app.py
```

2. **Pick a folder** with your images (JPG or JPEG)
3. Tweak the **settings** if you want:
   - `FPS` — frames per second (default: 24)
   - `Duration (s)` — how long the final video should be (default: 30)
   - `Output` — where to save the MP4
4. Press **Convert**

Your video will be ready in a few seconds.

---

## 📦 Requirements

- Python 3.9+
- `moviepy` ≥ 2.0
- `Pillow` ≥ 10.0
- `numpy` ≥ 1.24
- `customtkinter` ≥ 5.2

Install everything with:

```bash
pip install -r requirements.txt
```

---

## 🧪 Running from the terminal (no GUI)

```bash
python3 converter.py          # uses the 'immagini' folder
python3 converter.py my_photos   # custom folder
python3 converter.py my_photos video.mp4  # custom folder + output
```

---

## 🛠️ Built with

- [MoviePy](https://zulko.github.io/moviepy/) — video editing in Python
- [CustomTkinter](https://customtkinter.tomschimansky.com/) — modern Tkinter widgets
- [Pillow](https://python-pillow.org/) — image processing
