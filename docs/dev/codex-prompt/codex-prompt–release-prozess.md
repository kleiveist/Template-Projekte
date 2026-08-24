<!-- AUTO-GENERATED:backlink START -->
[← Back](codex-prompt.md)
<!-- AUTO-GENERATED:backlink END -->
# Codex-Prompt – Universeller versionsunabhängiger Release-Prozess

## Aufgabe

Führe den vollständigen Release-Prozess dieses Repositorys nach den vorhandenen Projekt-, Versions-, Qualitäts-, CI/CD- und Release-Richtlinien durch bzw. bereite ihn kontrolliert vor.

Dieser Prompt ist **versionsunabhängig und dauerhaft wiederverwendbar**.

Es ist ausdrücklich verboten, eine Version wie `1.0.0`, einen Tag wie `v1.0.0`, eine GitHub-Actions-Run-ID oder eine Commit-SHA ungeprüft fest anzunehmen.

Alle versions-, commit- und runabhängigen Werte müssen vor Beginn des Release-Prozesses aus dem aktuellen Repository-Zustand ermittelt werden.

---

# Grundprinzip

Der Ablauf bleibt bei jedem Release identisch:

```text
Repository analysieren
        ↓
aktuelle Version ermitteln
        ↓
Versionsrichtlinien prüfen
        ↓
Zielversion bestimmen
        ↓
Release-Variablen setzen
        ↓
Qualitäts- und Release-Gates
        ↓
finalen Commit bestimmen
        ↓
annotierten Release-Tag erzeugen
        ↓
Tag pushen
        ↓
tag-basierte Release Validation
        ↓
Run automatisch ermitteln
        ↓
Artefakte herunterladen
        ↓
plattformbezogen paketieren
        ↓
Checksums erzeugen
        ↓
Draft Release
        ↓
Release verifizieren
        ↓
Publish
```

---

# 1. Obligatorischer Release-Preflight

Bevor irgendein Release-Befehl ausgeführt wird, analysiere den aktuellen Repository-Zustand.

Ermittle mindestens:

```text
Repository
Default Branch
aktueller Branch
Working-Tree-Status
HEAD Commit
Remote HEAD
aktuelle Produkt-/Template-Version
vorhandene Git-Tags
letzten veröffentlichten Release
Versionsrichtlinien
Release-Richtlinien
Release-Workflow
Artefakt-Namen
unterstützte Plattformen
Signierungsstatus
```

Verwende dazu nach Möglichkeit unter anderem:

```bash
git status --short
git branch --show-current
git rev-parse HEAD
git remote -v
git fetch --tags --prune
git tag --sort=-version:refname
gh repo view
gh release list
gh run list --limit 20
```

Prüfe außerdem die im Repository vorhandenen Versionsquellen.

Beispiele:

```text
VERSION
pyproject.toml
package.json
Cargo.toml
tauri.conf.json
release manifest
Release-Dokumentation
Projekt-Governance
```

Die tatsächlich vorhandenen Dateien haben Vorrang.

---

# 2. Aktuelle Version automatisch feststellen

Suche die kanonische Versionsquelle des Repositorys.

Wenn beispielsweise eine Datei

```text
VERSION
```

vorhanden und laut Repository-Konvention maßgeblich ist:

```bash
CURRENT_VERSION=$(cat VERSION)
```

Danach:

```bash
echo "$CURRENT_VERSION"
```

Beispiel:

```text
1.0.0
```

Dieser Wert ist nur ein Beispiel.

Die Version darf nicht aus diesem Prompt übernommen werden.

---

# 3. Vorhandenen Release-Stand feststellen

Ermittle:

```bash
git tag --sort=-version:refname
```

und:

```bash
gh release list
```

Bestimme daraus mindestens:

```text
CURRENT_VERSION
LAST_TAG
LAST_RELEASE
```

Beispielvariablen:

```bash
CURRENT_VERSION="..."
LAST_TAG="..."
LAST_RELEASE="..."
```

Keine dieser Variablen darf fest codiert werden.

---

# 4. Versionsrichtlinien lesen

Prüfe die im Repository dokumentierten Versionsrichtlinien.

Falls Semantic Versioning verwendet wird, gelten grundsätzlich:

```text
PATCH
x.y.z → x.y.(z+1)

Bugfixes und vollständig kompatible Korrekturen
```

```text
MINOR
x.y.z → x.(y+1).0

neue rückwärtskompatible Funktionen
```

```text
MAJOR
x.y.z → (x+1).0.0

Breaking Changes bzw. inkompatible Änderungen
```

Die Repository-eigenen Regeln haben jedoch Vorrang.

---

# 5. Zielversion bestimmen

Bestimme anhand von:

```text
aktueller Version
Änderungsumfang
Commit-Historie
Release Notes
Versionsrichtlinien
Breaking Changes
Feature-Änderungen
Bugfixes
```

die korrekte Zielversion.

Speichere sie als:

```bash
TARGET_VERSION="X.Y.Z"
```

Danach:

```bash
TAG="v${TARGET_VERSION}"
```

Beispiel:

```text
CURRENT_VERSION = 1.0.0
TARGET_VERSION  = 1.0.1
TAG             = v1.0.1
```

Das Beispiel darf niemals ungeprüft übernommen werden.

---

# 6. Konsistenzprüfung der Version

Prüfe sämtliche relevanten Versionsquellen.

Beispielsweise:

```bash
grep -R "version" \
  VERSION \
  Cargo.toml \
  package.json \
  pyproject.toml \
  2>/dev/null
```

Stelle fest, ob alle Dateien entsprechend der Repository-Konvention konsistent sind.

Bei unterschiedlichen Produktversionen muss zwischen ihnen unterschieden werden.

Beispielsweise:

```text
Template-Version
Produktversion
Frontend-Version
Backend-Version
Desktop-App-Version
API-Version
```

Versionen dürfen nicht automatisch gleichgesetzt werden, wenn das Repository getrennte Versionierungsmodelle definiert.

---

# 7. Zentrale Release-Variablen setzen

Nach erfolgreicher Prüfung werden ausschließlich dynamische Variablen verwendet.

```bash
PROJECT_NAME="Template-Projekte"
CURRENT_VERSION="..."
TARGET_VERSION="..."
TAG="v${TARGET_VERSION}"
HEAD_SHA=$(git rev-parse HEAD)
```

Später zusätzlich:

```bash
RELEASE_RUN_ID="..."
```

Damit dürfen spätere Befehle nicht mehr enthalten:

```text
v1.0.0
1.0.0
feste Commit-SHA
feste Run-ID
```

sondern ausschließlich:

```text
${TARGET_VERSION}
${TAG}
${HEAD_SHA}
${RELEASE_RUN_ID}
```

---

# 8. Repository-Zustand prüfen

Vor dem Release:

```bash
git status --short
```

Es dürfen keine unbeabsichtigten Änderungen vorhanden sein.

Prüfe anschließend:

```bash
git branch --show-current
```

und den Upstream-Stand.

Beispielsweise:

```bash
git fetch origin
git status
```

Der Release darf nur vom laut Repository-Richtlinie freigegebenen Branch erfolgen.

In der Regel:

```text
main
```

aber dies muss geprüft und nicht vorausgesetzt werden.

---

# 9. Qualitäts-Gates ausführen

Ermittle die im Repository definierten Quality-, Test- und Release-Kommandos.

Beispiele können sein:

```bash
python tools/control.py docs check
python tools/control.py quality
python tools/control.py test --suite tools
python tools/control.py test --suite all
git diff --check
```

Führe nicht blind Beispielbefehle aus.

Prüfe zunächst, welche Befehle dieses Repository tatsächlich definiert.

Alle obligatorischen Gates müssen erfolgreich sein.

Ergebnis dokumentieren als:

```text
QUALITY = PASS
TESTS = PASS
DOCS = PASS
RELEASE_VALIDATION = PASS
```

Falls ein verpflichtendes Gate fehlschlägt:

```text
STOP
```

Keinen Release veröffentlichen.

---

# 10. Finalen Release-Commit bestimmen

Nach allen erforderlichen Änderungen:

```bash
HEAD_SHA=$(git rev-parse HEAD)
```

Ausgeben:

```bash
echo "$HEAD_SHA"
```

Prüfen, dass dieser Commit:

```text
alle Release-Änderungen enthält
alle erforderlichen Tests bestanden hat
mit der Zielversion übereinstimmt
für den Release vorgesehen ist
```

---

# 11. Vorhandenen Tag prüfen

Bevor ein Tag erzeugt wird:

```bash
git tag -l "$TAG"
```

und gegebenenfalls:

```bash
gh release view "$TAG"
```

Falls der Tag bereits existiert:

```text
NICHT überschreiben.
NICHT löschen.
NICHT force-pushen.
```

Zuerst analysieren, warum er existiert.

---

# 12. Annotierten Release-Tag erzeugen

Nur wenn alle vorherigen Prüfungen erfolgreich sind:

```bash
git tag -a "$TAG" \
  -m "${PROJECT_NAME} ${TAG}"
```

Kontrollieren:

```bash
git show "$TAG" --no-patch
```

Commitvergleich:

```bash
git rev-parse HEAD
git rev-list -n 1 "$TAG"
```

Die Commit-SHAs müssen übereinstimmen.

---

# 13. Release-Tag pushen

```bash
git push origin "$TAG"
```

Danach prüfen, ob der erwartete Release-Workflow gestartet wurde.

---

# 14. Tag-basierten Workflow automatisch finden

Keine feste Run-ID verwenden.

Ermittle den aktuellen Workflow-Run für:

```text
TAG=${TAG}
HEAD=${HEAD_SHA}
```

Beispielsweise über:

```bash
gh run list \
  --workflow release.yml \
  --limit 20
```

Wenn möglich, verwende strukturierte JSON-Ausgabe:

```bash
gh run list \
  --workflow release.yml \
  --limit 20 \
  --json databaseId,headSha,headBranch,status,conclusion,url
```

Identifiziere ausschließlich den Run, der zum aktuellen:

```text
TAG
HEAD_SHA
```

gehört.

Speichere:

```bash
RELEASE_RUN_ID="..."
```

---

# 15. Release Validation prüfen

```bash
gh run watch "$RELEASE_RUN_ID" --exit-status
```

Danach:

```bash
gh run view "$RELEASE_RUN_ID"
```

Zusätzlich:

```bash
gh run view "$RELEASE_RUN_ID" \
  --json conclusion,headSha,url
```

Verifiziere:

```text
conclusion == success
headSha == HEAD_SHA
```

Nur dann darf fortgefahren werden.

---

# 16. Release-Arbeitsverzeichnis erstellen

Verwende eine saubere temporäre bzw. ignorierte Release-Struktur:

```bash
mkdir -p release-assets/raw
mkdir -p release-assets/packages
```

Die Verzeichnisse dürfen nicht unbeabsichtigt Bestandteil des Repository-Commits werden.

---

# 17. Tatsächliche Workflow-Artefakte feststellen

Nicht einfach davon ausgehen, dass bestimmte Artefakt-Namen existieren.

Prüfe zuerst den Workflow bzw. die Run-Artefakte.

Erwartet werden bei diesem Repository derzeit möglicherweise:

```text
desktop-linux-unsigned
desktop-macos-unsigned
desktop-windows-unsigned
web-release-candidate
```

Diese Namen müssen jedoch vor jedem Release mit dem aktuellen Workflow verglichen werden.

---

# 18. Artefakte herunterladen

Mit der dynamisch ermittelten Run-ID:

```bash
gh run download "$RELEASE_RUN_ID" \
  -n desktop-linux-unsigned \
  -n desktop-macos-unsigned \
  -n desktop-windows-unsigned \
  -n web-release-candidate
```

Nur Artefakte des erfolgreich geprüften Release-Runs verwenden.

---

# 19. Artefakte prüfen

Für jede Plattform:

```bash
find desktop-linux-unsigned -type f | sort
find desktop-macos-unsigned -type f | sort
find desktop-windows-unsigned -type f | sort
```

Web:

```bash
find web-release-candidate -type f | sort
```

Prüfe:

```text
Dateitypen
Dateigrößen
Buildstruktur
Architektur
Installer-/Bundle-Typ
Signierungsstatus
```

---

# 20. Dynamische Release-Dateinamen verwenden

Release-Dateien werden anhand von:

```text
PROJECT_NAME
TARGET_VERSION
PLATFORM
SIGNING_STATUS
```

benannt.

Beispiel:

```bash
"${PROJECT_NAME}-v${TARGET_VERSION}-linux-unsigned.zip"
"${PROJECT_NAME}-v${TARGET_VERSION}-macos-unsigned.zip"
"${PROJECT_NAME}-v${TARGET_VERSION}-windows-unsigned.zip"
"${PROJECT_NAME}-v${TARGET_VERSION}-web.zip"
```

Damit wird aus:

```text
TARGET_VERSION=1.0.1
```

automatisch:

```text
Template-Projekte-v1.0.1-linux-unsigned.zip
Template-Projekte-v1.0.1-macos-unsigned.zip
Template-Projekte-v1.0.1-windows-unsigned.zip
Template-Projekte-v1.0.1-web.zip
```

Und aus:

```text
TARGET_VERSION=1.2.0
```

automatisch:

```text
Template-Projekte-v1.2.0-linux-unsigned.zip
Template-Projekte-v1.2.0-macos-unsigned.zip
Template-Projekte-v1.2.0-windows-unsigned.zip
Template-Projekte-v1.2.0-web.zip
```

Der Ablauf selbst verändert sich nicht.

---

# 21. Linux paketieren

```bash
(
  cd desktop-linux-unsigned
  zip -r \
    "../../packages/${PROJECT_NAME}-v${TARGET_VERSION}-linux-unsigned.zip" \
    .
)
```

---

# 22. macOS paketieren

```bash
(
  cd desktop-macos-unsigned
  zip -r \
    "../../packages/${PROJECT_NAME}-v${TARGET_VERSION}-macos-unsigned.zip" \
    .
)
```

---

# 23. Windows paketieren

```bash
(
  cd desktop-windows-unsigned
  zip -r \
    "../../packages/${PROJECT_NAME}-v${TARGET_VERSION}-windows-unsigned.zip" \
    .
)
```

---

# 24. Web-Paket behandeln

Prüfe zunächst den tatsächlichen Inhalt.

Falls bereits eine fertige ZIP vorhanden ist:

```bash
cp <GEPRÜFTE_WEB_ZIP> \
  "../packages/${PROJECT_NAME}-v${TARGET_VERSION}-web.zip"
```

Keine unnötigen ZIP-in-ZIP-Strukturen erzeugen.

---

# 25. Release-Pakete prüfen

```bash
cd ../packages
ls -lh
```

Erwartete Struktur dynamisch:

```text
${PROJECT_NAME}-v${TARGET_VERSION}-linux-unsigned.zip
${PROJECT_NAME}-v${TARGET_VERSION}-macos-unsigned.zip
${PROJECT_NAME}-v${TARGET_VERSION}-windows-unsigned.zip
${PROJECT_NAME}-v${TARGET_VERSION}-web.zip
```

---

# 26. SHA-256-Prüfsummen erzeugen

Auf Linux:

```bash
sha256sum *.zip > SHA256SUMS.txt
```

Danach:

```bash
cat SHA256SUMS.txt
```

Prüfen:

```bash
sha256sum -c SHA256SUMS.txt
```

Alle Dateien müssen:

```text
OK
```

melden.

---

# 27. Draft Release erstellen

Der Release wird zuerst ausschließlich als Draft erzeugt.

```bash
gh release create "$TAG" \
  ./*.zip \
  SHA256SUMS.txt \
  --verify-tag \
  --title "${PROJECT_NAME} ${TAG}" \
  --generate-notes \
  --draft
```

Keine Veröffentlichung vor der abschließenden Kontrolle.

---

# 28. Draft Release validieren

```bash
gh release view "$TAG"
```

Strukturiert:

```bash
gh release view "$TAG" \
  --json tagName,name,isDraft,isPrerelease,assets
```

Prüfe:

```text
tagName == TAG
name enthält TARGET_VERSION
isDraft == true
richtige Artefakte vorhanden
richtige Plattformen vorhanden
SHA256SUMS.txt vorhanden
keine falsche Version in Dateinamen
```

---

# 29. Release Notes prüfen

Prüfe automatisch erzeugte Release Notes auf:

```text
korrekte Version
korrekten Änderungsumfang
keine veralteten Versionsnummern
keine veralteten Commit-SHAs
keine falschen Plattformangaben
```

Bei unsigned Builds muss dies ausdrücklich angegeben werden.

Beispielsweise:

```text
Desktop artifacts are unsigned verification builds.

Linux:
- unsigned

macOS:
- unsigned / not notarized

Windows:
- unsigned
```

Wenn der Workflow zukünftig signierte Artefakte erzeugt, darf dieser Hinweis nicht blind übernommen werden.

Der tatsächliche Signierungsstatus muss vorher geprüft werden.

---

# 30. Finale Konsistenzprüfung

Vor dem Publish müssen mindestens folgende Beziehungen stimmen:

```text
VERSION / Zielversion
        =
TARGET_VERSION
        =
Git-Tag ohne "v"
        =
Release-Titel-Version
        =
Asset-Version
        =
Release Notes Version
```

Zusätzlich:

```text
Tag Commit
=
Release HEAD Commit
=
erfolgreicher Workflow HEAD Commit
=
Artefakt-Ursprungscommit
```

Bei Abweichungen:

```text
STOP
```

---

# 31. Release veröffentlichen

Erst nach vollständigem PASS:

```bash
gh release edit "$TAG" --draft=false
```

---

# 32. Veröffentlichung verifizieren

```bash
gh release view "$TAG" \
  --json name,tagName,isDraft,isPrerelease,publishedAt,url,assets
```

Erwartet:

```text
tagName       = ${TAG}
isDraft       = false
isPrerelease  = false
```

---

# 33. Abschlussbericht ausgeben

Nach Abschluss einen strukturierten Bericht erzeugen:

```text
RELEASE REPORT

Project:
<PROJECT_NAME>

Previous version:
<CURRENT_VERSION>

Released version:
<TARGET_VERSION>

Tag:
<TAG>

Release commit:
<HEAD_SHA>

Release workflow:
<RELEASE_RUN_ID>

Workflow result:
PASS / FAIL

Quality:
PASS / FAIL

Tests:
PASS / FAIL

Documentation:
PASS / FAIL

Linux artifact:
<filename>

macOS artifact:
<filename>

Windows artifact:
<filename>

Web artifact:
<filename / not applicable>

Checksums:
PASS / FAIL

GitHub Release:
<URL>

Release status:
PUBLISHED / DRAFT / BLOCKED
```

---

# Sicherheitsregeln für den Release-Prozess

Niemals:

```text
eine alte Run-ID ungeprüft verwenden
eine alte Commit-SHA ungeprüft verwenden
v1.0.0 fest voraussetzen
einen existierenden Tag überschreiben
einen Release-Tag force-pushen
fehlgeschlagene Quality Gates ignorieren
Artefakte aus unterschiedlichen Runs vermischen
Artefakte eines anderen Commits verwenden
eine Version nur anhand dieses Prompts auswählen
einen Draft ungeprüft veröffentlichen
unsigned Builds als signiert darstellen
```

---

# Entscheidende Regel

Jede Stelle, an der früher beispielsweise

```text
1.0.0
v1.0.0
32718517582
a09c0b9...
```

stand, muss zukünftig aus dynamisch ermittelten Variablen entstehen:

```text
CURRENT_VERSION
TARGET_VERSION
TAG
HEAD_SHA
RELEASE_RUN_ID
```

Der Prompt bleibt dadurch für folgende Releases unverändert verwendbar:

```text
1.0.0
1.0.1
1.0.2
1.1.0
1.2.0
2.0.0
2.1.3
...
```

Nur der tatsächliche Zustand des Repositorys bestimmt, welche Version gerade verarbeitet wird.

---

# Kurzform des universellen Release-Modells

```text
READ REPOSITORY
       │
       ▼
DETECT CURRENT VERSION
       │
       ▼
CHECK VERSION POLICY
       │
       ▼
DETERMINE TARGET VERSION
       │
       ▼
TARGET_VERSION=X.Y.Z
TAG=v${TARGET_VERSION}
HEAD_SHA=<current HEAD>
       │
       ▼
QUALITY + TESTS
       │
       ▼
TAG
       │
       ▼
PUSH
       │
       ▼
DETECT RELEASE RUN
       │
       ▼
RELEASE_RUN_ID=<dynamic>
       │
       ▼
VALIDATE
       │
       ▼
DOWNLOAD ARTIFACTS
       │
       ▼
PACKAGE WITH ${TARGET_VERSION}
       │
       ▼
CHECKSUMS
       │
       ▼
DRAFT RELEASE
       │
       ▼
FINAL CONSISTENCY CHECK
       │
       ▼
PUBLISH
```

## Hauptanforderung

Dieser Prompt ist eine **Release-Vorlage und keine Release-v1.0.0-Anweisung**.

Er muss deshalb bei jeder erneuten Verwendung zunächst feststellen:

> Welche Version hat das Repository aktuell, welche Version ist nach den geltenden Versionsrichtlinien als Nächstes zulässig und welche Version soll mit diesem Release tatsächlich veröffentlicht werden?

Erst nach dieser Feststellung darf der eigentliche Release-Prozess beginnen.
