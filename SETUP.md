# 🧠 Kenjaku Setup & Architecture Guide

This document explains exactly how to deploy the key-rotation infrastructure for Kenjaku and documents critical rules learned from past deep-analysis builds.

## ⚠️ Critical Domain Rules (From `multi_key_analyze.py`)
1. **Gemini Daily Quotas (429s)**: Google ruthlessly rate limits standard free tier keys to 1,500 requests per day and 15 requests per minute. Kenjaku solves this by dynamically loading an infinite number of keys from `.env` and round-robining them upon any `429` error.
2. **Vision Modality Limitations**: Groq's API is insanely fast and free, but `llama-3.2-vision` strictly supports images (Grids). It fails on raw audio chunks. Kenjaku solves this by mapping image grids to Groq/Gemini, and forcing raw video/audio chunks exclusively through the Gemini multi-modal engine.
3. **yt-dlp Constraints**: Downloading full 10-hour VODs or massive videos is inefficient. Kenjaku strictly uses the `--download-sections` flag to rip precise timestamps (e.g., the first 60 seconds) instantly.

## 💸 The Free Tier Advantage
This architecture is designed to be ridiculously cheap, if not entirely free:
- **Google AI Studio**: By logging into multiple Google accounts, you can generate endless free `GEMINI_API_KEY`s.
- **OpenRouter & Groq**: Kenjaku supports OpenRouter's `google/gemini-flash-1.5-8b:free` tier and Groq's `llama-3.2-90b-vision-preview` endpoint to offset Gemini token limits.
- **Local Compute**: Unlike `rika` and `cursed-speech` which require RunPod Serverless GPUs for audio models, Kenjaku runs 100% locally on your machine and offloads the heavy lifting to the APIs.

## 🚀 Environment Configuration

Create a `.env` file in your working directory containing your API keys. Kenjaku uses wildcard key extraction, meaning you can add as many keys as you want as long as they follow the naming convention:

```env
# Gemini Keys (Will be round-robined automatically)
GEMINI_API_KEY=AQ.Ab8RN6LnCI...
GEMINI_API_KEY_2=AQ.Ab8RN6JZHs...
GEMINI_API_KEY_3=AQ.Ab8RN6I6lB...

# OpenRouter Fallback Keys
OPENROUTER_API_KEY=sk-or-v1-37c4424...

# Groq Vision Key
GROQ_API_KEY=gsk_ieP54GBl4...
```

Once the `.env` is loaded, run `kj init` and let the Brain Hopping begin.
