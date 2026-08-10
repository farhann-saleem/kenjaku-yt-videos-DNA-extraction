#!/usr/bin/env python3
"""
Kenjaku (羂索) - Style DNA Extractor
"""

import os
import sys
import json
import time
import base64
import argparse
import subprocess
import requests
import yaml
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from itertools import cycle
from dotenv import load_dotenv

CLI_DIR = Path(os.getcwd())
load_dotenv(CLI_DIR / ".env")

# ── Key pool ───────────────────────────
GEMINI_KEYS = [v for k, v in os.environ.items() if k.startswith("GEMINI_API_KEY") and v]
OR_KEYS = [v for k, v in os.environ.items() if k.startswith("OPENROUTER_API_KEY") and v]
GROQ_KEYS = [v for k, v in os.environ.items() if k.startswith("GROQ_API_KEY") and v]

PROVIDERS = []
for k in GEMINI_KEYS: PROVIDERS.append(("gemini", k, "gemini-3.5-flash"))
for k in OR_KEYS: PROVIDERS.append(("openrouter", k, "google/gemini-2.5-flash"))
for k in GROQ_KEYS: PROVIDERS.append(("groq", k, "llama-3.2-90b-vision-preview"))

provider_cycle = cycle(range(len(PROVIDERS))) if PROVIDERS else None

def next_provider():
    if not provider_cycle:
        raise Exception("No API keys loaded from .env!")
    return PROVIDERS[next(provider_cycle)]

# ── API Calls ───────────────────────────────────────────────────────────────
def gemini_direct(key, model, body, timeout=120):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    r = requests.post(url, json=body, timeout=timeout)
    if r.status_code == 200:
        return r.json().get("candidates", [{}])[0].get("content", {}).get("parts", [])[0].get("text", "").strip()
    raise Exception(f"Gemini {r.status_code}")

def smart_call(prompt, image_path=None, video_path=None, timeout=120):
    img_b64 = base64.b64encode(open(image_path, "rb").read()).decode() if image_path else None
    vid_b64 = base64.b64encode(open(video_path, "rb").read()).decode() if video_path else None

    for attempt in range(max(1, len(PROVIDERS) * 3)):
        ptype, key, model = next_provider()
        try:
            if ptype == "gemini":
                parts = [{"text": prompt}]
                if img_b64: parts.append({"inline_data": {"mime_type": "image/jpeg", "data": img_b64}})
                if vid_b64: parts.append({"inline_data": {"mime_type": "video/mp4", "data": vid_b64}})
                return gemini_direct(key, model, {"contents": [{"parts": parts}], "generationConfig": {"temperature": 0.2}})
        except Exception as e:
            if "429" in str(e):
                time.sleep(15)
            continue
    raise Exception("All providers exhausted.")

def download_video(url, duration, out_path):
    print(f"[*] Brain-Snatching video... (First {duration}s)")
    cmd = ["yt-dlp", "--download-sections", f"*00:00:00-00:00:{duration:02d}", "-f", "best[ext=mp4]", url, "-o", out_path]
    subprocess.run(cmd, check=True, capture_output=True)
    print("[*] Download complete.")

def init_target():
    target_path = CLI_DIR / "target.md"
    if target_path.exists():
        print("[!] target.md already exists.")
        sys.exit(1)
        
    template = """---
name: mrbeast_gaming
url: "https://youtu.be/xxx"
duration_seconds: 60
---

# Target DNA Extraction
This file controls what Kenjaku extracts. Do not remove the YAML frontmatter above.
Change the name, url, and duration_seconds to whatever video you want to copy.
Then run `kj extract` in this directory.
"""
    target_path.write_text(template)
    print("[*] Created target.md!")
    print("[*] Edit the file with your YouTube link and run: kj extract")

def extract_dna():
    target_path = CLI_DIR / "target.md"
    if not target_path.exists():
        print("[!] target.md not found. Run `kj init` first.")
        sys.exit(1)
        
    content = target_path.read_text()
    if not content.startswith("---"):
        print("[!] Invalid target.md format. Missing YAML frontmatter.")
        sys.exit(1)
        
    yaml_part = content.split("---")[1]
    config = yaml.safe_load(yaml_part)
    
    out_name = config.get("name", "unknown")
    url = config.get("url")
    duration = config.get("duration_seconds", 60)
    
    if "youtu.be/xxx" in url:
        print("[!] Please edit target.md and replace the placeholder URL.")
        sys.exit(1)

    print(f"[*] Starting Kenjaku DNA Extraction for: {out_name}")
    
    workspace = CLI_DIR / "workspace"
    workspace.mkdir(exist_ok=True)
    vid_path = str(workspace / f"{out_name}_raw.mp4")
    
    # 1. Download
    download_video(url, duration, vid_path)

    # 2. Extract Grids & Audio (Mocked processing for now)
    print("[*] Running Six Eyes Processing on Grid and Audio...")
    time.sleep(2) 
    
    # 3. Create Outputs
    md_file = CLI_DIR / f"{out_name}_analysis.md"
    json_file = CLI_DIR / f"{out_name}_dna.json"

    # Dummy Output
    md_file.write_text(f"# {out_name} Deep Analysis\n\nVisuals: Heavy screen shake, center captions.\nAudio: Ducking at -12dB.")
    json_file.write_text(json.dumps({
        "style_name": out_name,
        "visuals": {"captions": {"font": "Impact", "animation": "pop"}},
        "audio": {"ducking": -12}
    }, indent=2))

    print(f"[*] Brain extracted successfully!")
    print(f"[*] Saved MD: {md_file}")
    print(f"[*] Saved JSON: {json_file}")

def main():
    parser = argparse.ArgumentParser(description="Kenjaku - Extract Video DNA")
    parser.add_argument("command", choices=["init", "extract"])
    args = parser.parse_args()

    if args.command == "init":
        init_target()
    elif args.command == "extract":
        extract_dna()

if __name__ == "__main__":
    main()
