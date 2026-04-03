---
name: tv-player
description: Play videos on TV via Home Assistant. Supports Samsung TV (AirPlay) and Android TV. Manages video streaming server, handles format conversion, and provides playback controls. Use when user wants to play/stream videos on TV, cast to TV, or manage TV video playback.
---

# TV Player Skill

Stream videos to TV through Home Assistant integration with automatic server management and format conversion.

## Quick Start

Play a video on Samsung TV (auto-converts if needed):
```bash
bash scripts/play-on-tv.sh /path/to/video.mp4
```

Play on Android TV (no auto-conversion):
```bash
bash scripts/play-on-tv.sh /path/to/video.mp4 android
```

**Auto-conversion:** The script automatically detects incompatible video formats (H.264 High profile) and converts them to Samsung-compatible format before playing. Converted files are cached for future playback.

## Supported TVs

**Samsung TV** (Primary, via AirPlay):
- Entity: `media_player.tv_samsung_7_series_50`
- Method: AirPlay streaming
- Status: Working reliably
- Best for: Default playback

**Android TV** (Secondary):
- Entity: `media_player.android_tv_jerusalem`
- Method: HTTP streaming
- Status: May require device reconnection
- Use when: Explicitly requested

## Video Requirements

**Samsung TV Compatibility:**
- Format: MP4 container
- Video: H.264 (baseline or main profile, level 3.0)
- Audio: AAC (128kbps recommended)

**Auto-conversion:** The play script automatically detects and converts incompatible formats (H.264 High profile, 10-bit) to Samsung-compatible format. Manual conversion is no longer needed.

**Manual conversion** (optional):
```bash
bash scripts/convert-for-tv.sh input-video.mp4
```

Output will be named `input-video-SAMSUNG-COMPATIBLE.mp4`.

## Video Server Management

The skill automatically manages an HTTP server for streaming:

**Check status:**
```bash
bash scripts/video-server.sh status
```

**Manual control:**
```bash
bash scripts/video-server.sh start
bash scripts/video-server.sh stop
bash scripts/video-server.sh restart
```

Server details:
- Port: 8766
- Directory: `~/shared-files/videos/`
- Access: `http://10.0.0.30:8766/`
- PID file: `/tmp/video-server-8766.pid`

## Workflow

1. **Format check** - Script detects video codec profile (Samsung TV only)
2. **Auto-conversion** - If incompatible (H.264 High profile), converts to baseline/main profile
3. **Server management** - Starts HTTP server if not running
4. **Stream to TV** - Plays via HA API (AirPlay for Samsung, HTTP for Android)
5. **Caching** - Converted files reused on subsequent plays

**Smart behavior:** If a converted version already exists, it's reused immediately without re-converting.

## Playback Controls

The play script outputs control commands. Examples:

**Pause:**
```bash
curl -X POST 'https://jer.emaygroup.org/api/services/media_player/media_pause' \
  -H "Authorization: Bearer $HA_TOKEN" \
  -d '{"entity_id":"media_player.tv_samsung_7_series_50"}'
```

**Resume:**
```bash
curl -X POST 'https://jer.emaygroup.org/api/services/media_player/media_play' \
  -H "Authorization: Bearer $HA_TOKEN" \
  -d '{"entity_id":"media_player.tv_samsung_7_series_50"}'
```

**Stop:**
```bash
curl -X POST 'https://jer.emaygroup.org/api/services/media_player/media_stop' \
  -H "Authorization: Bearer $HA_TOKEN" \
  -d '{"entity_id":"media_player.tv_samsung_7_series_50"}'
```

## Troubleshooting

**"Failed to play video":**
- Check TV is powered on and connected
- Verify `media_player` entity is available in HA
- Try converting video: `bash scripts/convert-for-tv.sh video.mp4`

**"Server not accessible":**
- Confirm M1 Mac IP is `10.0.0.30`
- Check firewall allows port 8766
- Restart server: `bash scripts/video-server.sh restart`

**Android TV not responding:**
- Device may show as unavailable in HA
- Check HA integration status
- Use Samsung TV as fallback

## Configuration

Edit script variables if environment differs:

**Network settings:**
- `M1_IP="10.0.0.30"` - Mac mini local IP
- `SERVER_PORT="8766"` - HTTP server port

**Home Assistant:**
- `HA_URL="https://jer.emaygroup.org"` - HA instance URL
- Token from `~/.openclaw/openclaw.json` → `env.HA_TOKEN`

**Paths:**
- Server directory: `~/shared-files/videos/`
- PID file: `/tmp/video-server-${SERVER_PORT}.pid`

## Common Patterns

**Play latest video:**
```bash
LATEST=$(ls -t ~/shared-files/videos/*.mp4 | head -1)
bash scripts/play-on-tv.sh "$LATEST"
```

**Convert and play:**
```bash
bash scripts/convert-for-tv.sh raw-video.mp4
CONVERTED=$(ls -t ~/shared-files/videos/*-SAMSUNG-COMPATIBLE.mp4 | head -1)
bash scripts/play-on-tv.sh "$CONVERTED"
```

**Batch convert videos:**
```bash
for video in ~/Downloads/*.mp4; do
  bash scripts/convert-for-tv.sh "$video"
done
```

## Integration Notes

- Videos MUST be in `~/shared-files/videos/` for server access
- Server runs persistently until explicitly stopped
- Samsung TV preferred for reliability
- Android TV requires functional HA integration
- Format conversion preserves original files
