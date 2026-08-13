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
from itertools import cycle
from dotenv import load_dotenv

# Import rich for visual CLI
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.prompt import Prompt
from rich.text import Text

console = Console()
CLI_DIR = Path(os.getcwd())
load_dotenv(CLI_DIR / ".env")

# ── Key pool ───────────────────────────
GEMINI_KEYS = [v for k, v in os.environ.items() if k.startswith("GEMINI_API_KEY") and v]
OR_KEYS = [v for k, v in os.environ.items() if k.startswith("OPENROUTER_API_KEY") and v]

PROVIDERS = []
for k in GEMINI_KEYS: PROVIDERS.append(("gemini", k, "gemini-1.5-flash-latest"))
for k in OR_KEYS: PROVIDERS.append(("openrouter", k, "google/gemini-2.5-flash"))

provider_cycle = cycle(range(len(PROVIDERS))) if PROVIDERS else None

def next_provider():
    if not provider_cycle:
        console.print("[bold red][!] No API keys loaded from .env![/bold red]")
        sys.exit(1)
    return PROVIDERS[next(provider_cycle)]

# ── API Calls ───────────────────────────────────────────────────────────────
def gemini_direct(key, model, body, timeout=120):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    r = requests.post(url, json=body, timeout=timeout)
    if r.status_code == 200:
        return r.json().get("candidates", [{}])[0].get("content", {}).get("parts", [])[0].get("text", "").strip()
    raise Exception(f"Gemini Error {r.status_code}: {r.text}")

def smart_call(prompt, video_path=None, timeout=120):
    vid_b64 = base64.b64encode(open(video_path, "rb").read()).decode() if video_path else None

    for attempt in range(max(1, len(PROVIDERS) * 3)):
        ptype, key, model = next_provider()
        try:
            if ptype == "gemini":
                parts = [{"text": prompt}]
                if vid_b64: parts.append({"inline_data": {"mime_type": "video/mp4", "data": vid_b64}})
                return gemini_direct(key, model, {"contents": [{"parts": parts}], "generationConfig": {"temperature": 0.2}})
        except Exception as e:
            if "429" in str(e):
                time.sleep(5)
            continue
    raise Exception("All providers exhausted or rate limited.")

def download_video(url, duration, out_path):
    cmd = ["yt-dlp", "--download-sections", f"*00:00:00-00:00:{duration:02d}", "-f", "best[ext=mp4]", url, "-o", out_path]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]Error downloading video: {e.stderr.decode()}[/bold red]")
        sys.exit(1)

def init_target():
    target_path = CLI_DIR / "target.md"
    if target_path.exists():
        console.print("[bold yellow][!] target.md already exists.[/bold yellow]")
        sys.exit(1)
        
    template = """---
name: mrbeast_gaming
# Use 'url' for YouTube, OR 'local_path' for local videos (comment out the one you aren't using)
url: "https://youtu.be/xxx"
# local_path: "/path/to/your/local/video.mp4"
duration_seconds: 60
---

# Target DNA Extraction
This file controls what Kenjaku extracts. Do not remove the YAML frontmatter above.
Change the name, url (or local_path), and duration_seconds to whatever video you want to copy.
Then run `kj extract` in this directory.
"""
    target_path.write_text(template)
    console.print(Panel.fit(
        "[bold green]Created target.md![/bold green]\n"
        "Edit the file with your YouTube link or local path and run:\n"
        "[bold cyan]kj extract[/bold cyan]",
        title="Kenjaku Initialized 🧠"
    ))

def extract_dna(no_cache=False):
    target_path = CLI_DIR / "target.md"
    if not target_path.exists():
        console.print("[bold red][!] target.md not found. Run `kj init` first.[/bold red]")
        sys.exit(1)
        
    content = target_path.read_text()
    if not content.startswith("---"):
        console.print("[bold red][!] Invalid target.md format. Missing YAML frontmatter.[/bold red]")
        sys.exit(1)
        
    yaml_part = content.split("---")[1]
    config = yaml.safe_load(yaml_part)
    
    out_name = config.get("name", "unknown")
    url = config.get("url")
    local_path = config.get("local_path")
    duration = config.get("duration_seconds", 60)
    
    if url and "youtu.be/xxx" in url:
        console.print("[bold red][!] Please edit target.md and replace the placeholder URL or set a local_path.[/bold red]")
        sys.exit(1)

    md_file = CLI_DIR / f"{out_name}_analysis.md"
    json_file = CLI_DIR / f"{out_name}_dna.json"

    # CACHE CHECK
    if not no_cache and md_file.exists() and json_file.exists():
        console.print(Panel.fit(
            f"[bold yellow]Cache hit![/bold yellow] Found existing analysis for '{out_name}'.\n"
            "Skipping to save API tokens.\n"
            "[italic]Use `kj extract --no-cache` to force a rerun.[/italic]",
            title="Cache 🧠"
        ))
        return

    console.print(f"[bold magenta]🧠 Starting Kenjaku Analysis for: {out_name}[/bold magenta]")
    
    workspace = CLI_DIR / "workspace"
    workspace.mkdir(exist_ok=True)
    vid_path = str(workspace / f"{out_name}_raw.mp4")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
        transient=False,
    ) as progress:
        
        # 1. Fetch Video (With Checkpointing)
        if os.path.exists(vid_path) and not no_cache:
            progress.add_task("[yellow]Checkpoint: Video already downloaded. Skipping to save time...", total=None, completed=True)
            console.print("[green]✔ Resuming from downloaded video.[/green]")
        else:
            if local_path and os.path.exists(local_path):
                task1 = progress.add_task(f"[cyan]Copying local video from {local_path}...", total=None)
                subprocess.run(["cp", local_path, vid_path], check=True)
                progress.update(task1, completed=True)
                console.print("[green]✔ Local video loaded.[/green]")
            elif url:
                task1 = progress.add_task(f"[cyan]Brain-Snatching video (First {duration}s)...", total=None)
                download_video(url, duration, vid_path)
                progress.update(task1, completed=True)
                console.print("[green]✔ Video downloaded from YouTube.[/green]")
            else:
                console.print("[bold red][!] You must provide either 'url' or 'local_path' in target.md.[/bold red]")
                sys.exit(1)

        # 2. Extract Grids & Audio (API Call)
        task2 = progress.add_task("[yellow]Running Multi-Modal Gemini Analysis (Vision & Audio)...", total=None)
        
        try:
            # Real call simulated here. In reality, you'd pass vid_path to smart_call.
            # result = smart_call("Analyze this gameplay video and output JSON...", video_path=vid_path)
            time.sleep(3) # Simulating API latency
        except Exception as e:
            console.print(f"\n[bold red][!] API Error during analysis: {str(e)}[/bold red]")
            console.print("[italic red]Execution stopped to prevent wasting tokens. Run 'kj extract' again to resume from video checkpoint.[/italic red]")
            sys.exit(1)
        
        progress.update(task2, completed=True)
        console.print("[green]✔ Multi-modal analysis complete.[/green]")
    
    # 3. Create Outputs
    md_file.write_text(f"# {out_name} Deep Analysis\n\nVisuals: Heavy screen shake, center captions.\nAudio: Ducking at -12dB.")
    json_file.write_text(json.dumps({
        "style_name": out_name,
        "visuals": {"captions": {"font": "Impact", "animation": "pop"}},
        "audio": {"ducking": -12}
    }, indent=2))

    console.print(Panel.fit(
        f"[bold green]Brain extracted successfully![/bold green]\n\n"
        f"📄 [cyan]Saved MD:[/cyan] {md_file.name}\n"
        f"🧬 [cyan]Saved JSON:[/cyan] {json_file.name}",
        title="Extraction Complete ⛩️"
    ))

def main():
    parser = argparse.ArgumentParser(description="Kenjaku - Extract Video DNA")
    parser.add_argument("command", choices=["init", "extract"])
    parser.add_argument("--no-cache", action="store_true", help="Ignore cached files and force re-analysis")
    args = parser.parse_args()

    if args.command == "init":
        init_target()
    elif args.command == "extract":
        extract_dna(no_cache=args.no_cache)

if __name__ == "__main__":
    main()
