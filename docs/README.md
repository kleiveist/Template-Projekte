# Dokumentationsstandard

Diese Datei ist die verbindliche Anleitung für alle Dokumente im Repository. Dokumentation wird zusammen mit der zugehörigen Codeänderung erstellt oder aktualisiert; sie ist Teil der Definition of Done.

## Ordner und Zuständigkeiten

| Pfad | Inhalt | Zielgruppe |
| --- | --- | --- |
| `README.md` | Produktüberblick, Schnellstart und wichtigste Befehle | Alle |
| `docs/def/` | Stabile Definitionen, Architektur und fachliche Modelle | Entwicklung und Architektur |
| `docs/dev/` | Anforderungen, Implementierungsnotizen und Migrationspläne | Entwicklung |
| `docs/usr/` | Aufgabenorientierte Bedienungsanleitungen | Anwender |
| `docs/tools/` | Betrieb, Build, Release und Werkzeugreferenz | Entwicklung und Betrieb |
| `docs/tools/tauri/` | Plattformspezifische Desktop-Hinweise | Desktop-Entwicklung |
| `docs/atp/` | Abnahmetestpläne und -protokolle | Entwicklung, QA und Abnahme |

Leere Fachordner enthalten nur `.gitkeep`, bis ein echtes Dokument benötigt wird. Beispieldokumente werden nicht als scheinbar gültige Projektdokumentation abgelegt.

## Verbindliche Regeln

1. Ein Dokument beantwortet eine klar benannte Frage und besitzt genau eine primäre Zielgruppe.
2. Dateinamen verwenden englisches `kebab-case`, zum Beispiel `release-process.md`.
3. Jede Seite beginnt mit einem eindeutigen H1-Titel und einer Metadatentabelle mit Status, Owner und letztem Review.
4. Zulässige Statuswerte sind `Draft`, `Active`, `Deprecated` und `Archived`.
5. Aussagen beschreiben den aktuellen Stand. Geplante Änderungen werden als Plan gekennzeichnet und erhalten einen Verweis auf Anforderung oder ATP.
6. Befehle müssen kopierbar sein und aus dem angegebenen Arbeitsverzeichnis funktionieren.
7. Links sind relativ zum aktuellen Dokument. Nach Umbenennungen müssen eingehende und ausgehende Links aktualisiert werden.
8. Diagramme werden bevorzugt als Mermaid im Markdown gepflegt. Ein Diagramm ergänzt den Text, ersetzt ihn aber nicht.
9. Geheimnisse, echte personenbezogene Daten, interne Zugangsdaten und lokale absolute Pfade gehören nicht in die Dokumentation.
10. Architektur- und API-Änderungen aktualisieren im selben Change die betroffenen Tests und ATPs.

## Pflichtaufbau

Für neue Seiten wird [DOCUMENT-TEMPLATE.md](DOCUMENT-TEMPLATE.md) kopiert. Nicht benötigte optionale Abschnitte dürfen entfernt werden; die folgenden Bestandteile bleiben verpflichtend:

- Titel
- Status, Owner und letztes Review
- Purpose
- Scope
- Inhalt oder Vorgehen
- Verification
- Related documents

## Schreibstil

- Kurze, überprüfbare Sätze und konkrete Verben verwenden.
- Fachbegriffe beim ersten Auftreten erklären und danach konsistent verwenden.
- Pro Dokument genau eine Sprache verwenden. Technische Architektur wird in diesem Template auf Englisch geführt; Benutzer- und Prozessdokumente dürfen Deutsch sein.
- Beispiele als Beispiele markieren und Platzhalter in spitze Klammern setzen, etwa `<project-name>`.
- Keine relativen Zeitangaben wie „bald“ oder „aktuell“ ohne Datum verwenden.

## Code, API und Konfiguration

Codeblöcke erhalten immer eine Sprachangabe. API-Dokumentation nennt mindestens Methode, Pfad, Eingabe, Erfolgsausgabe und Fehlerfälle. Konfigurationswerte dokumentieren Namen, Standardwert, erlaubte Werte, Sicherheitswirkung und ein Beispiel.

## Review und Pflege

Der Code-Reviewer prüft bei jeder Änderung:

- Sind Verhalten und Dokumentation konsistent?
- Funktionieren Befehle und Links?
- Ist die Änderung über Tests oder ein ATP nachweisbar?
- Sind ersetzte Aussagen entfernt statt nur ergänzt worden?
- Muss das Datum `Last review` aktualisiert werden?

Ein Dokument wird `Deprecated`, sobald es nicht mehr die bevorzugte Lösung beschreibt. Es wird `Archived`, wenn es nur noch historischen Nachweis liefert. Aktive Seiten dürfen nicht auf archivierte Inhalte als einzige Quelle angewiesen sein.

## Dokumentations-Workflow

1. Zielgruppe und passenden Ordner bestimmen.
2. [DOCUMENT-TEMPLATE.md](DOCUMENT-TEMPLATE.md) kopieren.
3. Anforderung, Architekturentscheidung oder ATP verlinken.
4. Dokument parallel zur Implementierung aktualisieren.
5. Befehle, Links und Beispiele prüfen.
6. Owner und Review-Datum setzen.
7. Mit dem Code gemeinsam reviewen und einchecken.
