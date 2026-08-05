# Tooling-Anleitung

| Feld | Wert |
| --- | --- |
| Status | Active |
| Owner | Projektteam |
| Last review | 2026-08-05 |

## Purpose

Diese Seite erklärt den zentralen Einstiegspunkt für Installation, Entwicklung, Tests und Builds. Sie ist für den Wiedereinstieg gedacht, wenn die letzten Arbeiten am Projekt länger zurückliegen.

## Scope

Die Anleitung gilt für `tools/control.py` und die darüber erreichbaren Web-, API- und Tauri-Abläufe. Alle Befehle werden aus dem Repository-Wurzelverzeichnis ausgeführt.

## Sicherer Wiedereinstieg

Der Aufruf ohne Argumente zeigt nur Hilfe und verändert keine Dateien:

```sh
python tools/control.py
```

Danach empfiehlt sich diese Reihenfolge:

```sh
python tools/control.py doctor
python tools/control.py install
python tools/control.py run
```

`doctor` prüft Laufzeiten, Abhängigkeiten, Projektstruktur und Ports. `install` richtet Frontend und Backend ein; Playwright wird nur installiert, wenn das Projekt E2E-Tests konfiguriert hat. `run` startet Vite und FastAPI gemeinsam. Im Vordergrund beendet `Ctrl+C` beide Prozesse.

Alternativ öffnet dieser Befehl ein nummeriertes Menü:

```sh
python tools/control.py console
```

## Befehlslandkarte

| Befehl | Wirkung | Vertiefende Hilfe |
| --- | --- | --- |
| `doctor` | Entwicklungsumgebung prüfen | `python tools/control.py doctor --help` |
| `install` | Projektabhängigkeiten installieren oder reparieren | `python tools/control.py install --help` |
| `console` | Interaktives Menü öffnen | `python tools/control.py console --help` |
| `run` | Frontend und Backend starten | `python tools/control.py run --help` |
| `stop` | Im Hintergrund gestartete Dienste stoppen | `python tools/control.py stop --help` |
| `test` | Testbereiche und Reports auswählen | `python tools/control.py test` |
| `build` | Web- oder Desktop-Build auswählen | `python tools/control.py build` |
| `tauri` | Tauri-Diagnose, Entwicklung und Artefakte verwalten | `python tools/control.py tauri` |

Ein Gruppenbefehl ohne Unterbefehl zeigt nur seine nächste Hilfestufe. Das gilt insbesondere für:

```sh
python tools/control.py build
python tools/control.py test
python tools/control.py tauri
```

Ein unbekannter Befehl zeigt die passende Hilfe, kennzeichnet den Fehler und nennt den nächsten `--help`-Aufruf.

## Entwicklung starten und stoppen

```sh
# Vordergrund; Ctrl+C stoppt beide Dienste
python tools/control.py run

# Hintergrund; PID- und Logdateien liegen in tools/.runtime
python tools/control.py run --detach

# Hintergrunddienste beenden
python tools/control.py stop
```

Abweichende Ports werden mit `--frontend-port` und `--backend-port` gesetzt. Alle Optionen zeigt `python tools/control.py run --help`.

## Tests und Reports

```sh
python tools/control.py test --suite api
python tools/control.py test --suite frontend
python tools/control.py test --suite tools
python tools/control.py test --suite all
python tools/control.py test --suite all --report
```

Verfügbare Suites:

| Suite | Inhalt |
| --- | --- |
| `api` | FastAPI-Tests |
| `schema` | Gemeinsame JSON-Schemas und Beispiele |
| `frontend` | Vitest-Tests |
| `e2e` | Playwright-Tests, sofern konfiguriert |
| `tools` | Tests der Projekt-CLI und Tauri-Helfer |
| `all` | Alle konfigurierten Suites |

Reports werden unter `.report/` erzeugt. `python tools/control.py test --report done` entfernt ausschließlich diesen Report-Ordner.

## Builds

Der Gruppenaufruf zeigt zunächst die Build-Ziele:

```sh
python tools/control.py build
```

Ein Web-Build erzeugt `frontend/dist/` und das Archiv `.dist/web/template-project-web.zip`:

```sh
python tools/control.py build web
```

Desktop-Builds laufen über Tauri. Vor dem ersten echten Build sollte immer Diagnose und Dry-Run ausgeführt werden:

```sh
python tools/control.py tauri doctor
python tools/control.py build desktop --dry-run
python tools/control.py build desktop
```

Plattformstrategien und Bundle-Optionen stehen unter:

```sh
python tools/control.py build desktop --help
python tools/control.py tauri build --help
```

Tauri kann zusätzlich Abhängigkeiten prüfen, den Entwicklungsmodus starten, AppImages lokal installieren und vorhandene Artefakte sammeln. Die aktuelle Karte liefert `python tools/control.py tauri`.

## Fehlerbehebung

1. Den fehlgeschlagenen Befehl mit `--help` prüfen.
2. `python tools/control.py doctor` ausführen.
3. Mit `python tools/control.py install` fehlende Projektabhängigkeiten reparieren.
4. Bei Desktop-Problemen zusätzlich `python tools/control.py tauri doctor` ausführen.
5. Nur den betroffenen Testbereich erneut starten und danach `--suite all` ausführen.

Fehlende optionale Suites werden bei `test --suite all` als `WARN` übersprungen. Fehlende optionale Beschleuniger wie `uv` beeinträchtigen den Doctor-Status nicht. Ein `FAIL` bezeichnet einen Fehler, der den ausgewählten Ablauf ungültig macht.

## Verification

Nach Änderungen am Tooling werden mindestens diese Befehle geprüft:

```sh
python tools/control.py
python tools/control.py build
python tools/control.py test
python tools/control.py tauri
python tools/control.py test --suite tools
python tools/control.py build desktop --dry-run --no-clean
```

## Related documents

- [Dokumentationsstandard](../README.md)
- [Framework architecture](../def/architecture.md)
- [ATP workflow](../atp/README.md)
