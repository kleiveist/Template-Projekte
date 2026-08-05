# Full-Stack Project Template

Dieses Repository ist ein schlankes Ausgangsprojekt für Anwendungen mit Vite und TypeScript, FastAPI sowie Tauri 2.

## Enthaltener Stack

| Bereich | Technologie | Aufgabe |
| --- | --- | --- |
| Web-Frontend | Vite 6, TypeScript 5, Vitest | Browser-Oberfläche und Frontend-Tests |
| Backend | FastAPI, Uvicorn, Pytest | HTTP-API und API-Tests |
| Desktop | Tauri 2, Rust | Native Desktop-Shell für das Web-Frontend |
| Tooling | Python | Gemeinsame Installation, Start, Build und Tests |

## Voraussetzungen

- Python 3.11 oder neuer
- Node.js 20 oder neuer mit npm
- Für Desktop-Builds: Rust Stable und die [plattformspezifischen Tauri-Abhängigkeiten](https://v2.tauri.app/start/prerequisites/)

## Schnellstart

Wenn du das Projekt nach längerer Zeit wieder öffnest, starte ohne Argumente. Die CLI zeigt dann den vollständigen Befehlsplan und verändert noch nichts:

```sh
python tools/control.py
```

Der empfohlene Wiedereinstieg ist:

```sh
python tools/control.py doctor
python tools/control.py install
python tools/control.py run
```

Danach sind standardmäßig erreichbar:

- Frontend: `http://127.0.0.1:5173`
- Backend: `http://127.0.0.1:8000`
- API-Health-Check: `http://127.0.0.1:8000/api/health`

Der kombinierte Entwicklungsstart läuft im Vordergrund. Mit `Ctrl+C` werden beide Prozesse beendet.

## Zentrale Befehle

```sh
python tools/control.py doctor
python tools/control.py install
python tools/control.py run
python tools/control.py stop
python tools/control.py test
python tools/control.py build
python tools/control.py tauri
python tools/control.py console
```

`build`, `test` und `tauri` zeigen bei einem Aufruf ohne weitere Auswahl jeweils ihre eigene Hilfekarte. Konkrete Beispiele:

```sh
python tools/control.py test --suite api
python tools/control.py test --suite frontend
python tools/control.py test --suite tools
python tools/control.py test --suite all --report
python tools/control.py build web
python tools/control.py build desktop --dry-run
python tools/control.py tauri doctor
```

Jeder Befehl unterstützt zusätzlich `--help`, zum Beispiel `python tools/control.py tauri build --help`. Die vollständige Referenz steht in der [Tooling-Anleitung](docs/tools/tooling.md).

## Projektstruktur

```text
backend/             FastAPI-Anwendung und API-Tests
docs/                Dokumentationsregeln, Vorlagen, Architektur und ATPs
frontend/            Vite-/TypeScript-Anwendung und Frontend-Tests
shared/              Framework-neutrale Verträge, Beispiele und gemeinsame Assets
src-tauri/           Tauri-Konfiguration, Rust-Einstiegspunkt und App-Icons
tools/control.py     Gemeinsamer Projekt-CLI-Einstiegspunkt
```

## Neues Projekt aus dem Template erstellen

1. Repository kopieren oder als Git-Template verwenden und eine neue Historie anlegen.
2. Nach `template-project`, `project-template`, `Template Project` und `com.example.templateproject` suchen und die Werte projektspezifisch ersetzen.
3. `src-tauri/app-icon.svg` austauschen und mit `npm --prefix frontend run tauri -- icon ../src-tauri/app-icon.svg` neue Icons erzeugen.
4. Produktziel, Verantwortliche und Qualitätskriterien dokumentieren.
5. Für den ersten Funktionsumfang ein ATP aus `docs/atp/ATP-TEMPLATE.md` anlegen.
6. `python tools/control.py test --suite all` ausführen und das erste abgeschlossene ATP einchecken.

## Verbindliche Dokumentation

- [Dokumentationsstandard](docs/README.md)
- [Allgemeine Dokumentvorlage](docs/DOCUMENT-TEMPLATE.md)
- [Framework architecture](docs/def/architecture.md)
- [ATP workflow](docs/atp/README.md)
- [ATP template](docs/atp/ATP-TEMPLATE.md)
- [Tooling-Anleitung](docs/tools/tooling.md)

Neue oder geänderte Funktionen gelten erst dann als abgeschlossen, wenn Code, Tests und die betroffene Dokumentation gemeinsam aktualisiert wurden.
