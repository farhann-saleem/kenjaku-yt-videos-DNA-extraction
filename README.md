<div align="center">
  <img src="kenjaku.png" alt="Kenjaku Brain Hopping Domain Expansion" width="100%">
  <h1 align="center">kenjaku (羂索)</h1>
  <p align="center"><i>Style DNA Extractor & Brain Snatching Domain</i></p>
  
  [![Python](https://img.shields.io/badge/Python-3.9+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
  [![Gemini](https://img.shields.io/badge/Gemini-2.5%20Flash-orange.svg?style=for-the-badge)](https://ai.google.dev)
</div>

---

> *"I will take over this body and its techniques."* — Kenjaku

**kenjaku** is a fully-automated CLI tool that extracts the "DNA" of a viral video's editing style and binds it to a JSON preset for the Kamui renderer. 

It handles automated yt-dlp downloading, Six Eyes Grid Processing, and ultra-fast pacing extraction using a highly redundant key-rotation strategy across Gemini, OpenRouter, and Groq APIs.

---

## Setup & Infrastructure
Read the **[SETUP.md](./SETUP.md)** file for a full guide on configuring your environment, understanding the rate-limit bypassing architecture, and setting up the rotating API keys.

---

## Features

- **Infinite Keys**: Automatically loads any `GEMINI_API_KEY_*`, `OPENROUTER_API_KEY`, or `GROQ_API_KEY` in your `.env` and rotates them dynamically to permanently bypass `429 Quota Exceeded` errors.
- **Six Eyes Processing**: Slices reference videos into 5x5 grids and chunks audio dynamically for multi-modal VLM ingestion.
- **DNA Extraction**: Spits out `_dna.json` containing the mathematically perfect anchor points, font styles, and pacing rules required to clone a video's style.
- **Zero Cost Architecture**: Uses entirely free-tier inference APIs to deep-analyze 100+ videos without spending a single dollar.

---

## Installation

You can install the `kenjaku` CLI globally straight from GitHub:

```bash
pip install git+https://github.com/farhann-saleem/kenjaku.git
```

Once installed, just navigate to an empty folder anywhere on your computer and run:
```bash
kj init
```
This will generate your `target.md` configuration file. You never have to touch the Python code!

---

## Command Reference

| Command | Description |
|---------|-------------|
| `kj init` | Initializes a `target.md` configuration file in your current directory. |
| `kj extract` | **[AUTO]** Reads `target.md`, fetches the video via yt-dlp, performs Six Eyes Grid Analysis, and extracts the JSON DNA. |

---

<div align="center">
  <i>Built for viral style replication. No manual FFmpeg timing. Pure automated brain snatching.</i>
</div>
