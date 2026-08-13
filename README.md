<div align="center">
  <img src="kenjaku.png" alt="Kenjaku Brain Hopping Domain Expansion" width="100%">
  <h1 align="center">kenjaku (羂索)</h1>
  <p align="center"><i>Style DNA Extractor & Brain Snatching Domain</i></p>
  
  [![Python](https://img.shields.io/badge/Python-3.9+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
  [![Gemini](https://img.shields.io/badge/Gemini-1.5%20Flash-orange.svg?style=for-the-badge)](https://ai.google.dev)
</div>

---

> *"I will take over this body and its techniques."* — Kenjaku

**kenjaku** is a fully-automated, highly visual CLI tool that acts as the "Brain" for video automation pipelines. It uses Gemini's native multi-modal capabilities (simultaneous vision and audio processing) to extract the "DNA" of a viral video's editing style, or to analyze raw gameplay for automated editing.

## 🌟 New Features

- **Beautiful Rich UI:** Live progress bars, spinning loaders, and elapsed-time tracking right in your terminal.
- **Local & Remote Support:** Feed it a YouTube URL (auto-downloads via `yt-dlp`) or simply point it to a `local_path` on your hard drive.
- **Smart Caching:** Automatically detects if a video has already been analyzed and skips execution to save your API tokens. Use `--no-cache` to force a rerun.
- **Checkpointing:** If the API fails mid-extraction, Kenjaku saves the downloaded video locally and will resume exactly where it left off on the next run.
- **Agent-Safe Error Handling:** Built with strict `try/except` blocks and standard exit codes (`sys.exit(1)`) so other AI coding agents can run it autonomously without getting stuck in loops.

---

## 🛠️ Installation

You can install the `kenjaku` CLI globally straight from GitHub or locally in editable mode:

```bash
# To install locally with editable mode (recommended for developers)
pip install -e . --break-system-packages
```

Once installed, just navigate to an empty folder anywhere on your computer and run:
```bash
kj init
```
This will generate your `target.md` configuration file. You never have to touch the Python code!

---

## 💻 Command Reference

| Command | Description |
|---------|-------------|
| `kj init` | Initializes a `target.md` configuration file. You can insert a YouTube URL or a Local File Path here. |
| `kj extract` | **[AUTO]** Reads `target.md`, fetches/copies the video, runs Multi-Modal Gemini Analysis, and extracts the JSON DNA. |
| `kj extract --no-cache` | Ignores any previous analysis files and forces a brand new API extraction. |

---

<div align="center">
  <i>Built for viral style replication. No manual FFmpeg timing. Pure automated brain snatching.</i>
</div>
