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

```sh
python3 tools/control.py install
python3 tools/control.py run
```

Danach sind standardmäßig erreichbar:

- Frontend: `http://127.0.0.1:5173`
- Backend: `http://127.0.0.1:8000`
- API-Health-Check: `http://127.0.0.1:8000/api/health`

Der kombinierte Entwicklungsstart läuft im Vordergrund. Mit `Ctrl+C` werden beide Prozesse beendet.

## Zentrale Befehle

```sh
python3 tools/control.py doctor
python3 tools/control.py install
python3 tools/control.py run
python3 tools/control.py test
python3 tools/control.py build
python3 tools/control.py tauri dev
python3 tools/control.py build --desktop
```

Einzelne Testbereiche lassen sich mit `--suite backend`, `--suite frontend` oder `--suite desktop` ausführen.

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
6. `python3 tools/control.py test` ausführen und das erste abgeschlossene ATP einchecken.

## Verbindliche Dokumentation

- [Dokumentationsstandard](docs/README.md)
- [Allgemeine Dokumentvorlage](docs/DOCUMENT-TEMPLATE.md)
- [Framework architecture](docs/def/architecture.md)
- [ATP workflow](docs/atp/README.md)
- [ATP template](docs/atp/ATP-TEMPLATE.md)

Neue oder geänderte Funktionen gelten erst dann als abgeschlossen, wenn Code, Tests und die betroffene Dokumentation gemeinsam aktualisiert wurden.
