# MeinAppNest – Container-Build-System (umgebaut von ElfHosted)

Dieses Repo ist der ehemalige **ElfHosted `containers`-Monorepo**, vollständig
de-brandet und auf **MeinAppNest / GitHub-Owner `Action3062`** umgestellt.
Alle Verweise auf ElfHosted wurden ersetzt.

## Ersetzte Parameter

| Bereich              | Vorher (ElfHosted)                         | Nachher (MeinAppNest)                 |
|----------------------|--------------------------------------------|---------------------------------------|
| Image-Registry       | `ghcr.io/elfhosted/…`                       | `ghcr.io/action3062/…` (lowercase)    |
| Build-Repo           | `elfhosted/containers`                      | `Action3062/containers`               |
| Privates Overlay-Repo| `elfhosted/containers-private`             | `Action3062/containers-private`       |
| Reusable Workflows   | `uses: elfhosted/containers/…@main`         | `uses: Action3062/containers/…@main`  |
| Quell-Repos (ci)     | `elfhosted/<x>`, `funkypenguin/<x>`         | `Action3062/<x>`                      |
| Package-API          | `orgs/elfhosted` / `users/elfhosted`        | `users/Action3062`                    |
| Domain / Mail        | `elfhosted.com`, `…@elfhosted.com`          | `example.com` (Platzhalter)           |
| Marken-Text          | `ElfHosted`                                 | `MeinAppNest`                         |
| Runtime-User/Group   | `elfie` (uid/gid 568)                        | `appnest` (uid/gid **568 unverändert**)|
| Greeting / ElfTerm   | „brave elf…", `elfterm`                      | MeinAppNest-Text, `appnest-terminal`  |
| `geek-cookbook`      | GitHub-Org                                   | `Action3062`                          |

## Umbenannte interne Apps (LOTR-Theme → neutral)

Diese 8 Apps sind ElfHosted-**intern** (nur `metadata.json`, Quellcode in privaten
Repos). Verzeichnis = Image-Name. Quell-Verweise zeigen jetzt auf `Action3062/<neuer-name>`.

| Vorher           | Nachher                      |
|------------------|------------------------------|
| `elrond`         | `nest-orchestrator`          |
| `elrond-gitops`  | `nest-orchestrator-gitops`   |
| `elrond-woo`     | `nest-orchestrator-woo`      |
| `elfbot`         | `nest-bot`                   |
| `elf-discord-bot`| `nest-discord-bot`           |
| `gandalf`        | `nest-gatekeeper`  ⚠ Name geraten |
| `balrog`         | `nest-worker`      ⚠ Name geraten |
| `shadowfax`      | `nest-courier`     ⚠ Name geraten |

⚠ = Funktion dieser drei privaten Apps ist unbekannt; Namen frei wählbar anpassen.

## Wichtige technische Änderung: Basis-Image-Digests entfernt

Die 43 Dockerfiles mit `FROM ghcr.io/elfhosted/alpine|ubuntu|alpine-node@sha256:…`
zeigten auf **ElfHosteds** veröffentlichte Layer. Diese Digests existieren in deiner
Registry nicht. Daher wurde der `@sha256:…`-Pin **entfernt** – die Child-Images bauen
jetzt gegen deine frisch gebauten Basis-Tags (`:rolling`, `:3.19.1`, …). Renovate
re-pinnt die Digests automatisch nach dem ersten Build. Fremd-Image-Digests
(z. B. `oven/bun@sha256`, `public.ecr.aws`) blieben unangetastet.

## Manuelle TODOs vor dem ersten Build

1. **GitHub-Repos anlegen** unter `Action3062`:
   - `containers` (dieses Repo, öffentlich)
   - `containers-private` (privat – enthält die ~90 Overlay-Dockerfiles der Apps,
     die hier nur `metadata.json` haben). Falls nicht benötigt: Overlay-Schritt in
     `.github/workflows/action-image-build.yaml` (Zeilen ~59–68) entfernen.
2. **Actions-Secrets setzen:** `ZURG_GH_CREDS`, `PLEX_TOKEN`, `GH_TOKEN_CONTAINERS_PRIVATE`.
3. **Basis-Images zuerst bauen & pushen:** `alpine`, `ubuntu`, `alpine-node` →
   `ghcr.io/action3062/…`, danach die abhängigen Apps.
4. **Interne `nest-*`-Apps:** brauchen Quellcode unter `github.com/Action3062/<name>`
   (+ `ZURG_GH_CREDS`-Zugriff). Nicht benötigte einfach löschen.
5. **Logo-Artwork ersetzen:** `apps/mediaflow-proxy-light/branding/mediafusion-meinappnest-logo.png`
   enthält noch ElfHosted-Grafik (Binärdatei, nicht automatisch ersetzbar).
6. **Platzhalter-Domain `example.com`** durch deine echte Domain ersetzen, wenn vorhanden.
7. **Owner-Typ:** `published.sh`/`.mjs` nutzen `users/Action3062`. Falls `Action3062`
   eine **Organisation** wird, auf `orgs/Action3062` ändern.

## Repo-Name als Parameter

Die Workflow-Referenzen lauten `Action3062/containers`. Wenn du das Repo anders nennst,
in `.github/workflows/release-*.yaml` und `image-rebuild.yaml` (`uses:`) entsprechend anpassen.
