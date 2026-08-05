# ATP workflow

| Field | Value |
| --- | --- |
| Status | Active |
| Owner | Project team |
| Last review | 2026-08-05 |
| Audience | Development, QA and acceptance owners |

In diesem Template steht **ATP** für **Abnahmetestplan/-protokoll** beziehungsweise **Acceptance Test Plan/Protocol**. Eine ATP-Datei beschreibt zuerst die geplante Abnahme und wird bei der Durchführung um tatsächliche Ergebnisse und Nachweise ergänzt.

## Struktur

```text
docs/atp/
├── README.md
├── ATP-TEMPLATE.md
├── planned/
├── active/
└── completed/
```

| Ordner | Bedeutung |
| --- | --- |
| `planned/` | Testumfang und erwartete Ergebnisse sind definiert, die Ausführung hat noch nicht begonnen. |
| `active/` | Die Abnahme läuft oder es bestehen offene Abweichungen. |
| `completed/` | Alle Pflichtschritte wurden ausgeführt; Ergebnis und Freigabe sind dokumentiert. |

## Dateiname und ID

Der Dateiname lautet `ATP-<vierstellige-ID>-<kurzer-slug>.md`, zum Beispiel `ATP-0007-user-login.md`. Die ID wird nie wiederverwendet. Beim Statuswechsel wird die Datei verschoben, aber weder ID noch Dateiname werden geändert.

## Workflow

1. `ATP-TEMPLATE.md` nach `planned/ATP-<ID>-<slug>.md` kopieren.
2. Anforderung, Scope, Risiken, Voraussetzungen, Testdaten und erwartete Resultate vor der Implementierungsabnahme festlegen.
3. Prüfen, dass jeder fachliche Akzeptanzpunkt mindestens einem Testschritt zugeordnet ist.
4. Zum Start der Ausführung die Datei nach `active/` verschieben.
5. Ist-Ergebnis, Status und Evidence unmittelbar je Testschritt eintragen.
6. Abweichungen mit Verantwortlichem und Folgemaßnahme dokumentieren. Ein fehlgeschlagener Pflichtschritt verhindert den Status `completed`.
7. Nach erfolgreicher Wiederholungsprüfung Ergebnis und Sign-off ergänzen und die Datei nach `completed/` verschieben.

## Status pro Testschritt

Nur diese Werte verwenden:

- `NOT RUN`: noch nicht ausgeführt
- `PASS`: erwartetes Ergebnis vollständig erreicht
- `FAIL`: erwartetes Ergebnis nicht erreicht
- `BLOCKED`: Ausführung durch eine dokumentierte Abhängigkeit verhindert
- `N/A`: nach Review nachweislich nicht anwendbar; Begründung ist Pflicht

## Evidence

Evidence muss durch einen Reviewer auffindbar und nachvollziehbar sein. Geeignet sind relative Pfade zu Testreports oder Screenshots, CI-Run-IDs, reproduzierbare Befehle, relevante Logauszüge und Versionen externer Systeme. Keine geheimen Werte oder personenbezogenen Echtdaten einfügen.

## Abschlusskriterien

Ein ATP darf nur nach `completed/`, wenn:

- alle Pflichtschritte `PASS` oder begründet `N/A` sind,
- keine offene Abweichung die Abnahme verhindert,
- Umgebung sowie getesteter Commit oder Build eindeutig angegeben sind,
- automatisierte Tests referenziert oder begründete manuelle Prüfungen dokumentiert sind,
- Gesamturteil und Sign-off ausgefüllt sind.

Die Vorlage selbst wird niemals als ausgeführtes ATP verwendet.
