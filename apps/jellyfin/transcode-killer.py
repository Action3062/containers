#!/usr/bin/env python3
"""Enforce per-plan transcode limits on a Jellyfin server.

One container per customer: the customer's plan is configured through
environment variables.

  JELLYFIN_ALLOW_4K           "true"/"false"  allow 4K *transcoding* (default: true)
  JELLYFIN_MAX_HD_TRANSCODES  int             max simultaneous HD transcodes (unset = unlimited)
  JELLYFIN_MAX_4K_TRANSCODES  int             max simultaneous 4K transcodes (unset = unlimited)
  JELLYFIN_URL                base URL        (default: http://localhost:8096)
  JELLYFIN_API_KEY            Jellyfin API key (needed for detection + graceful stop)
  TRANSCODE_KILLER_INTERVAL   poll seconds    (default: 5)

Enforcement is "API + fallback ffmpeg": an offending session first gets an
on-screen message and a graceful stop via the Jellyfin API; if that is not
possible (no API key, API error, or the session keeps transcoding) the most
recently started jellyfin-ffmpeg process is killed as a fallback.

Only 4K *transcoding* is restricted — 4K direct play / direct stream is never
touched (a 4K source whose video is not being re-encoded is ignored).
"""

import json
import os
import signal
import time
import urllib.error
import urllib.request

UHD_MIN_HEIGHT = 2160
UHD_MIN_WIDTH = 3800
LOG_PREFIX = "[transcode-killer]"


def log(msg):
    print(f"{LOG_PREFIX} {msg}", flush=True)


def env_bool(name, default):
    val = os.environ.get(name)
    if val is None or val.strip() == "":
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


def env_int(name):
    val = os.environ.get(name)
    if val is None or val.strip() == "":
        return None
    try:
        return int(val)
    except ValueError:
        log(f"WARN {name}={val!r} is not an integer, ignoring")
        return None


class Jellyfin:
    def __init__(self, base_url, api_key):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def _request(self, method, path, body=None):
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["X-Emby-Token"] = self.api_key
        data = None
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(
            f"{self.base_url}{path}", data=data, headers=headers, method=method
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            payload = resp.read()
            return json.loads(payload) if payload else None

    def sessions(self):
        return self._request("GET", "/Sessions") or []

    def send_message(self, session_id, header, text, timeout_ms=8000):
        self._request(
            "POST",
            f"/Sessions/{session_id}/Message",
            {"Header": header, "Text": text, "TimeoutMs": timeout_ms},
        )

    def stop(self, session_id):
        self._request("POST", f"/Sessions/{session_id}/Playing/Stop")


def source_resolution(now_playing):
    """(width, height) of the source video stream, or (0, 0)."""
    for stream in (now_playing or {}).get("MediaStreams") or []:
        if stream.get("Type") == "Video":
            return int(stream.get("Width") or 0), int(stream.get("Height") or 0)
    return int((now_playing or {}).get("Width") or 0), int((now_playing or {}).get("Height") or 0)


def is_video_transcode(session):
    ti = session.get("TranscodingInfo")
    # TranscodingInfo is only present while transcoding; IsVideoDirect == True
    # means the video is remuxed/direct (cheap) — we only limit re-encodes.
    return bool(ti) and not ti.get("IsVideoDirect", False)


def is_4k(session):
    w, h = source_resolution(session.get("NowPlayingItem"))
    return h >= UHD_MIN_HEIGHT or w >= UHD_MIN_WIDTH


def position_ticks(session):
    return int((session.get("PlayState") or {}).get("PositionTicks") or 0)


# --- ffmpeg fallback -------------------------------------------------------

def ffmpeg_processes():
    """[(pid, start_jiffies)] for running jellyfin-ffmpeg transcodes."""
    procs = []
    for entry in os.listdir("/proc"):
        if not entry.isdigit():
            continue
        pid = int(entry)
        try:
            with open(f"/proc/{pid}/cmdline", "rb") as fh:
                cmd = fh.read().replace(b"\x00", b" ").decode("utf-8", "ignore")
        except (FileNotFoundError, ProcessLookupError, PermissionError):
            continue
        if "ffmpeg" not in cmd:
            continue
        if not ("jellyfin" in cmd or "transcod" in cmd.lower()):
            continue
        try:
            with open(f"/proc/{pid}/stat", "rb") as fh:
                # field 22 (start time) is the 22nd field after "(comm) "
                start = int(fh.read().split(b") ")[-1].split()[19])
        except (FileNotFoundError, ProcessLookupError, PermissionError, IndexError, ValueError):
            start = 0
        procs.append((pid, start))
    return procs


def kill_newest_ffmpeg(count):
    """Kill the `count` most recently started ffmpeg transcodes."""
    if count <= 0:
        return 0
    newest_first = sorted(ffmpeg_processes(), key=lambda p: p[1], reverse=True)
    killed = 0
    for pid, _ in newest_first[:count]:
        try:
            os.kill(pid, signal.SIGKILL)
            log(f"fallback: killed ffmpeg pid {pid}")
            killed += 1
        except (ProcessLookupError, PermissionError) as exc:
            log(f"fallback: could not kill pid {pid}: {exc}")
    return killed


# --- enforcement -----------------------------------------------------------

def enforce(jelly, session, message):
    """Graceful API stop (with message); returns True if stopped via API."""
    sid = session.get("Id")
    user = session.get("UserName") or "?"
    item = (session.get("NowPlayingItem") or {}).get("Name") or "?"
    log(f"violation: user={user!r} item={item!r} -> {message}")
    if not (jelly.api_key and sid):
        return False
    try:
        jelly.send_message(sid, "Wiedergabe gestoppt", message)
    except Exception as exc:  # noqa: BLE001
        log(f"could not message session {sid}: {exc}")
    try:
        jelly.stop(sid)
        log(f"stopped session {sid} via API")
        return True
    except Exception as exc:  # noqa: BLE001
        log(f"API stop failed for session {sid}: {exc}")
        return False


def excess_newest(sessions, limit):
    """Sessions beyond `limit`, dropping the least-watched (newest) first."""
    if limit is None or len(sessions) <= limit:
        return []
    # keep the most-watched (highest position); drop the rest
    by_watched = sorted(sessions, key=position_ticks, reverse=True)
    return by_watched[limit:]


def run_once(jelly, cfg):
    try:
        sessions = jelly.sessions()
    except (urllib.error.URLError, urllib.error.HTTPError) as exc:
        if cfg["api_key"]:
            log(f"cannot reach Jellyfin API: {exc}")
        else:
            degraded_fallback(cfg)
        return
    except Exception as exc:  # noqa: BLE001
        log(f"unexpected error querying sessions: {exc}")
        return

    transcodes = [s for s in sessions if is_video_transcode(s)]
    hd = [s for s in transcodes if not is_4k(s)]
    uhd = [s for s in transcodes if is_4k(s)]

    violations = []  # (session, message)

    if not cfg["allow_4k"]:
        for s in uhd:
            violations.append((s, "4K-Transcoding ist in deinem Paket nicht enthalten."))
    else:
        for s in excess_newest(uhd, cfg["max_4k"]):
            violations.append((s, "Maximale Anzahl gleichzeitiger 4K-Transcodes erreicht."))

    for s in excess_newest(hd, cfg["max_hd"]):
        violations.append((s, "Maximale Anzahl gleichzeitiger HD-Transcodes erreicht."))

    fallback_needed = 0
    for session, message in violations:
        if not enforce(jelly, session, message):
            fallback_needed += 1
    if fallback_needed:
        kill_newest_ffmpeg(fallback_needed)


def degraded_fallback(cfg):
    """No API key: best-effort cap on the total number of transcodes."""
    if cfg["max_hd"] is None and cfg["max_4k"] is None and cfg["allow_4k"]:
        return  # nothing configured to enforce
    cap = (cfg["max_hd"] or 0) + ((cfg["max_4k"] or 0) if cfg["allow_4k"] else 0)
    procs = ffmpeg_processes()
    if len(procs) > cap:
        log(f"degraded mode (no API key): {len(procs)} transcodes > cap {cap}")
        kill_newest_ffmpeg(len(procs) - cap)


def main():
    cfg = {
        "url": os.environ.get("JELLYFIN_URL", "http://localhost:8096"),
        "api_key": os.environ.get("JELLYFIN_API_KEY", "").strip(),
        "allow_4k": env_bool("JELLYFIN_ALLOW_4K", True),
        "max_hd": env_int("JELLYFIN_MAX_HD_TRANSCODES"),
        "max_4k": env_int("JELLYFIN_MAX_4K_TRANSCODES"),
        "interval": env_int("TRANSCODE_KILLER_INTERVAL") or 5,
    }
    jelly = Jellyfin(cfg["url"], cfg["api_key"])
    log(
        "started: url=%s allow_4k=%s max_hd=%s max_4k=%s interval=%ss api_key=%s"
        % (
            cfg["url"],
            cfg["allow_4k"],
            cfg["max_hd"],
            cfg["max_4k"],
            cfg["interval"],
            "set" if cfg["api_key"] else "MISSING (degraded fallback only)",
        )
    )
    while True:
        try:
            run_once(jelly, cfg)
        except Exception as exc:  # noqa: BLE001
            log(f"loop error: {exc}")
        time.sleep(cfg["interval"])


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
