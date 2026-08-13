# 🤖 Kenjaku Agent Playbook

**ATTENTION FELLOW AI AGENTS:** 
If the user assigns you to run or troubleshoot the Kenjaku extraction pipeline, you **MUST** read and follow these rules. This tool costs the user money (API tokens) to run, and your mistakes can rapidly burn through their budget.

---

## 1. The Core Workflow
When the user asks you to extract the DNA of a video or analyze raw gameplay, follow this exact sequence:

1. **Initialize the Environment:**
   Run `kj init` in a fresh directory. This generates the `target.md` file.

2. **Configure the Target:**
   Edit the `target.md` file to contain **EITHER** a YouTube URL **OR** a `local_path` to an `.mp4` file on the hard drive. 
   *Do not leave the placeholder `youtu.be/xxx` url in the file, or the CLI will crash.*

3. **Run Extraction:**
   Run `kj extract`. The CLI will automatically handle video downloading, grid processing, and the Gemini API call.

---

## 2. Token Safety & Caching (CRITICAL)

The CLI is built with a strict caching system to prevent burning tokens unnecessarily. 
*   If `kj extract` sees that `[name]_analysis.md` and `[name]_dna.json` already exist, it will **SKIP** the API call and print a Cache warning. 
*   **DO NOT** delete the JSON or MD files just to force a rerun. 
*   If you *actually* need to run a fresh analysis (e.g. the user changed a prompt or asked for a fresh extraction), you MUST use the `--no-cache` flag:
    ```bash
    kj extract --no-cache
    ```

---

## 3. Checkpointing & Resumability

If the CLI stops mid-way (e.g., the video downloaded successfully but the API crashed), it creates a checkpoint.
*   **DO NOT** delete the `workspace/` folder if a run fails. 
*   The downloaded raw video is stored in `workspace/[name]_raw.mp4`.
*   If you just run `kj extract` again, the CLI will automatically detect the video and skip the yt-dlp download phase, resuming straight at the API call.

---

## 4. Error Handling

Kenjaku is designed to be agent-safe. It uses standard Unix exit codes.
*   If the command returns `Exit Code 0`, it was a perfect success. The output files are ready.
*   If it returns `Exit Code 1`, **STOP**. Do not run it again in a `while` loop. Read the red terminal output to understand what failed.
*   Fix the underlying issue before attempting to run it again.

---

## 5. Known Failures & Troubleshooting (The Graveyard)

Throughout the development of this pipeline, we have encountered several recurring API and system failures. If you encounter these, **do not panic and do not bother the user**. Follow these exact resolution steps:

### A. `400 Bad Request` (Payload Too Large)
*   **The Issue:** Gemini throws a 400 error when the Base64 inline data is too massive for the REST endpoint to handle. 
*   **The Fix:** You are trying to send too much video data inline. Edit the `target.md` file and lower the `duration_seconds` (e.g., from 60 down to 15 or 30). Run `kj extract --no-cache` to force a smaller download and retry.

### B. `429 Quota Exceeded` (All Providers Exhausted)
*   **The Issue:** The script crashed because every single Gemini and OpenRouter API key in the `.env` hit a rate limit.
*   **The Fix:** Do not write a script to blindly retry. The keys need a hard cooldown. Wait at least 1-2 minutes before attempting to run `kj extract` again. The checkpointing system will ensure you don't re-download the video.

### C. `yt-dlp` Download Failures
*   **The Issue:** The YouTube URL is invalid, private, or age-restricted.
*   **The Fix:** Verify the `url` in `target.md`. If it requires authentication, you must ask the user to provide a `local_path` to the raw video instead, bypassing YouTube entirely.

### D. `Missing YAML frontmatter` or Parsing Errors
*   **The Issue:** The `target.md` file was malformed or a placeholder was left in.
*   **The Fix:** Ensure the `target.md` starts exactly with `---` and ends the config block with `---`. Ensure the placeholder `youtu.be/xxx` was actually replaced with a real link.
