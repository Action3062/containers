# jellyfin

Jellyfin media server auf Basis von `ghcr.io/action3062/ubuntu` (jammy), mit
offiziellen Jellyfin-Paketen (`jellyfin-server`, `jellyfin-web`,
`jellyfin-ffmpeg7`), Hardware-Transcoding (Intel VAAPI/QSV + NVIDIA NVENC) und
einem eingebauten **Transcode-Killer**, der pro Container (= pro Kunde/Paket)
die gleichzeitigen Transcodes und die 4K-Nutzung begrenzt.

Kein `s6-overlay`: Jellyfin läuft als Hauptprozess über `tini`, der
Transcode-Killer als überwachter Hintergrund-Daemon (Auto-Restart).

## Tags

| Tag | Beschreibung |
|-----|--------------|
| `ghcr.io/action3062/jellyfin:rolling` | jeweils neuester Build |
| `ghcr.io/action3062/jellyfin:<version>` | gepinnte Jellyfin-Version, z. B. `10.11.11` |

Für unveränderliche Deployments zusätzlich den `sha256`-Digest pinnen.

## Ports & Volume

| Port | Zweck |
|------|-------|
| `8096/tcp` | Web-UI / HTTP-API |
| `8920/tcp` | HTTPS (optional) |
| `7359/udp` | Client-Discovery |
| `1900/udp` | DLNA |

Konfiguration & Datenbank liegen unter `/config` (als Volume mounten).

## Environment-Variablen

### Server

| Variable | Default | Beschreibung |
|----------|---------|--------------|
| `TZ` | `Etc/UTC` | Zeitzone |
| `UMASK` | `0002` | umask für neu erstellte Dateien |

### Transcode-Killer (Paket-Limits)

| Variable | Default | Beschreibung |
|----------|---------|--------------|
| `JELLYFIN_ALLOW_4K` | `true` | `false` sperrt 4K-**Transcoding** (4K Direct Play bleibt erlaubt) |
| `JELLYFIN_MAX_HD_TRANSCODES` | _(leer = unbegrenzt)_ | max. gleichzeitige HD-Transcodes |
| `JELLYFIN_MAX_4K_TRANSCODES` | _(leer = unbegrenzt)_ | max. gleichzeitige 4K-Transcodes |
| `JELLYFIN_API_KEY` | _(leer)_ | Jellyfin-API-Key für sauberes Stoppen + Hinweis-Meldung |
| `JELLYFIN_URL` | `http://localhost:8096` | Basis-URL der lokalen Jellyfin-Instanz |
| `TRANSCODE_KILLER_INTERVAL` | `5` | Poll-Intervall in Sekunden |
| `TRANSCODE_KILLER_ENABLED` | `true` | `false` schaltet den Killer komplett ab |

> Ohne gesetzte Limits (Default) greift der Killer nicht ein – das Image
> verhält sich dann wie ein normaler Jellyfin-Server.

## So funktioniert der Transcode-Killer

1. Pollt die Jellyfin-`/Sessions`-API (alle `TRANSCODE_KILLER_INTERVAL` s).
2. Zählt nur **Video-Transcodes** (Direct Play / Direct Stream wird ignoriert).
   Eine Session gilt als **4K**, wenn die Quell-Videohöhe ≥ 2160 (bzw. Breite
   ≥ 3840) ist – sonst **HD**. HD und 4K werden getrennt gezählt.
3. Verstöße:
   - `JELLYFIN_ALLOW_4K=false` → jeder 4K-Transcode ist ein Verstoß.
   - mehr HD- bzw. 4K-Transcodes als das jeweilige Limit → die überzähligen
     (am wenigsten weit geschauten) Sessions sind Verstöße.
4. Durchsetzung: zuerst **sauber per API** stoppen (mit Hinweis-Meldung an den
   Nutzer); schlägt das fehl oder ist kein API-Key gesetzt, wird als
   **Fallback** der zugehörige `jellyfin-ffmpeg`-Prozess beendet.

### API-Key anlegen

Dashboard → **Administration → API-Schlüssel → +** und den Wert als
`JELLYFIN_API_KEY` setzen. Ohne API-Key läuft nur der grobe ffmpeg-Fallback
(kein per-Klasse-/4K-genaues Enforcement, keine Nutzer-Meldung).

## Beispiel-Pakete

**HD-Paket (kein 4K, max. 2 gleichzeitige Transcodes):**

```yaml
environment:
  JELLYFIN_ALLOW_4K: "false"
  JELLYFIN_MAX_HD_TRANSCODES: "2"
  JELLYFIN_API_KEY: "<key>"
```

**4K-Paket (4K erlaubt, 1×4K + 3×HD gleichzeitig):**

```yaml
environment:
  JELLYFIN_ALLOW_4K: "true"
  JELLYFIN_MAX_HD_TRANSCODES: "3"
  JELLYFIN_MAX_4K_TRANSCODES: "1"
  JELLYFIN_API_KEY: "<key>"
```

**Unbegrenzt (kein Killer):**

```yaml
environment:
  TRANSCODE_KILLER_ENABLED: "false"
```

## Hardware-Transcoding

Die Treiber für **Intel** (VAAPI/QSV) sind im Image enthalten. Für **NVIDIA**
(NVENC) liefert das Image nur `ffmpeg` mit NVENC-Support – die Treiber-Libs
kommen zur Laufzeit vom NVIDIA-Container-Runtime des Hosts.

**docker run (Intel):**

```bash
docker run -d --name jellyfin \
  --device /dev/dri:/dev/dri \
  --group-add "$(getent group render | cut -d: -f3)" \
  -v /srv/jellyfin/config:/config \
  -v /srv/media:/media:ro \
  -p 8096:8096 \
  -e JELLYFIN_ALLOW_4K=false -e JELLYFIN_MAX_HD_TRANSCODES=2 -e JELLYFIN_API_KEY=<key> \
  ghcr.io/action3062/jellyfin:rolling
```

**docker run (NVIDIA):** zusätzlich `--runtime=nvidia --gpus all` (statt
`--device /dev/dri`).

In Jellyfin anschließend unter **Dashboard → Wiedergabe → Hardwarebeschleunigung**
VAAPI/QSV bzw. NVENC aktivieren.
