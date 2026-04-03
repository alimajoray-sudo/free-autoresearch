---
name: ambient-pipeline
description: Ambient YouTube video production pipeline (Flux/KIE image → window masking → Kling animation → ffmpeg compositing + optional music).
---

# Ambient Video Production Pipeline — Working Reference

> **Status:** ✅ Confirmed working — 2026-02-20  
> **Dashboard:** https://ambient.emaygroup.org (port 8099)  
> **Server:** `~/clawd/youtube-ambient/app-testb/server.py`

---

## The 3-Layer Pipeline

### Layer 1 — Interior Image (Flux-2 Pro via KIE.ai)

**Goal:** Generate a photorealistic interior scene with window glass painted solid cyan (#00FFFF) so stock footage can be composited through the windows.

**Prompt Rules:**
- ✅ Describe the interior warmly: fireplace, candles, furniture, mood
- ✅ Mention windows exist: "large floor-to-ceiling wooden-framed windows on the far wall"
- ❌ DO NOT describe what's visible through the windows (no "aurora flooding in", no "snowfall outside")
- The server appends a CYAN_SUFFIX automatically — it instructs the AI to paint all window glass #00FFFF

**CYAN_SUFFIX (server-appended):**
```
". CRITICAL COMPOSITING INSTRUCTION: Every single window pane and glass surface
MUST be painted with PURE FLAT SOLID BRIGHT CYAN color #00FFFF.
Do NOT show any outdoor scene through the glass.
Do NOT add reflections or gradients to the glass.
Window glass = solid flat #00FFFF cyan block only.
Fireplace, candles, lamps stay as-is. ONLY window glass = #00FFFF cyan."
```

---

### Layer 2 — Window Masking (Dual approach)

The server checks if the AI actually painted cyan (sometimes it doesn't):

**Path A — Cyan detected (>1% cyan pixels):**
```
FFmpeg colorkey: colorkey=0x00FFFF:0.35:0.2
[interior with cyan][stock][colorkey removes cyan → stock shows through]
```

**Path B — No cyan (brightness fallback):**
```
OpenCV brightness mask → maskedmerge
[interior][stock][mask]maskedmerge
White mask = stock visible | Black mask = interior visible
```

**Critical FFmpeg notes:**
- Use `maskedmerge` NOT `alphamerge` (alphamerge logic is inverted)
- Use `format=yuv420p` on mask NOT `format=gray` (gray causes B&W output)
- Compositing order: `[interior_src][stock_loop][mask_path]`

---

### Layer 3 — Kling 2.6 Animation (KIE.ai)

**Goal:** Animate the interior image (fireplace flicker, candle sway, steam rise).

**Image Upload:** Use **litterbox.catbox.moe** — NOT catbox.moe (blocked by Kling)
```python
requests.post(
    'https://litterbox.catbox.moe/resources/internals/api.php',
    data={'reqtype': 'fileupload', 'time': '72h'},
    files={'fileToUpload': image_file}
)
```

**Kling API payload (correct field names):**
```json
{
  "model": "kling-2.6/image-to-video",
  "input": {
    "prompt": "Fireplace flames dancing and crackling...",
    "image_urls": ["https://litter.catbox.moe/xxx.png"],
    "duration": "10",
    "aspect_ratio": "16:9",
    "sound": false
  }
}
```

**Wrong field names that fail silently:**
- ❌ `"image"` → ✅ `"image_urls": [url]` (must be array)
- ❌ `"ratio"` → ✅ `"aspect_ratio"`
- ❌ duration as int → ✅ duration as string `"10"`

**The 10s clip is looped** to the full video duration using FFmpeg concat.

---

## Compositing Flow Summary

```
Stock footage loop (looped to duration)
        ↓
Interior image (Flux-2 Pro, cyan windows)
        ↓
Kling animation (10s loop, if enabled)
        ↓
Cyan detection → colorkey OR brightness mask → maskedmerge
        ↓
[Optional] Suno music merge
        ↓
Final .mp4 → ~/shared-files/Videos/
```

---

## Bugs Fixed (History)

| Bug | Symptom | Fix |
|-----|---------|-----|
| catbox.moe blocked by Kling | Animation silently falls back to static | Use litterbox.catbox.moe |
| Wrong Kling field names | API 500 error, silent fail | image_urls[], aspect_ratio, duration string |
| `format=gray` on mask | B&W output video | Use `format=yuv420p` |
| `alphamerge` backwards | Only stock visible, no interior | Use `maskedmerge [interior][stock][mask]` |
| Threshold `max(p85, 180)` | Tiny/no windows detected on dark images | Use `max(p85, 40)` |
| Conflicting prompt (outdoor scene + cyan) | AI ignores cyan, renders realistic windows | Keep prompts neutral on window views |
| Cyan suffix overridden | Same as above — worked Feb 17, broke Feb 18 | Category prompts updated to not describe outdoor scenes |
| `use_colorkey = False` hardcoded | Cyan detection worked but maskedmerge had YUV range bleed | Restored colorkey path for static+cyan; maskedmerge only for animated |
| Category prompts described outdoor scenes | aurora/winter/space/rain had "aurora light", "snowy forest", "starfield", "rainy street" in prompts | Removed all outdoor scene references — prompts now say "windows on the far wall" only |

---

## Category Animation Prompts

```python
{
  'winter': 'Fireplace flames dancing and crackling with warm orange glow, candle flames flickering softly, steam rising gently from a mug, subtle warm light pulsing, no camera movement',
  'aurora': 'Candlelight flickering softly, fireplace glow pulsing warmly, aurora light shimmering and dancing through dome windows, cozy atmosphere, no camera movement',
  'rain':   'Raindrops sliding slowly down window glass, candle flames flickering gently, steam rising from coffee cup, soft warm interior light glowing, no camera movement',
  'ocean':  'Soft ocean light shimmering through windows, candle flames gently swaying, steam rising slowly, peaceful coastal atmosphere, no camera movement',
  'desert': 'Warm golden sunlight shifting slowly through windows, candle flames swaying gently, heat shimmer effect, soft amber light pulsing, no camera movement',
  'space':  'Starlight shimmering softly through windows, subtle floating dust particles in ambient light, soft cosmic glow pulsing gently, no camera movement',
  'clouds': 'Soft cloud light shifting gently through windows, candle flames flickering peacefully, steam rising slowly, serene daylight atmosphere, no camera movement',
}
```

---

## Quick Production API Call

```bash
curl -X POST http://localhost:8099/api/production/start \
  -H "Content-Type: application/json" \
  -d '{
    "category": "winter",
    "duration": 3600,
    "image_prompt": "Ultra photorealistic cozy mountain cabin interior, very dim warm fireplace glow and soft candlelight, rough wooden beams, fur throws on armchair, steaming coffee mug, large floor-to-ceiling wooden-framed windows on the far wall, 8K sharp details, 16:9",
    "generate_image": true,
    "generate_music": true,
    "animate_interior": true,
    "output_name": "winter-cabin-1hr"
  }'
```

## Server Management

```bash
# Start
cd ~/clawd/youtube-ambient/app-testb
nohup venv/bin/python3 server.py > ~/clawd/youtube-ambient/logs/dashboard-testb.log 2>&1 &

# Stop
kill $(ps aux | grep server.py | grep -v grep | awk '{print $2}')

# Logs
tail -f ~/clawd/youtube-ambient/logs/dashboard-testb.log
```
