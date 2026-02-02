# Jira & Confluence Daily Digest

Eine Python-Applikation, die täglich um 7:00 Uhr eine HTML-formatierte E-Mail mit Updates aus Jira und Confluence versendet.

## Features

### Jira Updates
- Neue Tickets der letzten 24 Stunden
- Status-Änderungen
- Zuweisungen
- Neue Kommentare
- Gruppierung nach Projekten

### Confluence Updates
- Aktualisierte Seiten der letzten 24 Stunden
- Anzeige von Seitentitel, Space, letztem Bearbeiter und Zeitpunkt
- Direkte Links zu den geänderten Seiten

### E-Mail
- HTML-formatiert mit professionellem Design
- Plain-Text Fallback für maximale Kompatibilität
- Übersichtliche Tabellen und Gruppierungen
- Responsive Design für mobile Geräte

## Technologie-Stack

- **Python 3.11+**
- **Docker** für Container-Deployment
- **APScheduler** für zeitgesteuertes Scheduling
- **Atlassian Python API** für Jira & Confluence Integration
- **Jinja2** für HTML-Templates
- **SMTP** für E-Mail-Versand

## Installation

### Voraussetzungen

1. **Atlassian API Tokens erstellen:**
   - Gehe zu https://id.atlassian.com/manage-profile/security/api-tokens
   - Erstelle API Tokens für Jira und Confluence
   - Notiere Username und API Token

2. **SMTP Zugangsdaten:**
   - Gmail: App-Passwort erstellen (bei aktivierter 2FA)
   - Office365: SMTP mit OAuth oder App-Passwort
   - Eigener Server: Standard SMTP Credentials

### Setup

1. **Repository klonen oder Projekt herunterladen:**
   ```bash
   cd jira-confluence-digest
   ```

2. **Umgebungsvariablen konfigurieren:**
   ```bash
   cp .env.example .env
   ```

3. **.env Datei ausfüllen:**
   ```env
   # Jira Configuration
   JIRA_URL=https://your-company.atlassian.net
   JIRA_USERNAME=your-email@company.com
   JIRA_API_TOKEN=your-jira-api-token

   # Confluence Configuration
   CONFLUENCE_URL=https://your-company.atlassian.net/wiki
   CONFLUENCE_USERNAME=your-email@company.com
   CONFLUENCE_API_TOKEN=your-confluence-api-token

   # Email Configuration
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-smtp-password-or-app-password
   RECIPIENT_EMAIL=recipient@company.com

   # Schedule Configuration
   SCHEDULE_TIME=07:00
   TIMEZONE=Europe/Berlin

   # Optional: Filter specific projects/spaces (comma-separated)
   JIRA_PROJECTS=PROJ1,PROJ2
   CONFLUENCE_SPACES=SPACE1,SPACE2
   ```

## Verwendung

### Mit Docker (empfohlen)

1. **Container bauen und starten:**
   ```bash
   docker-compose up -d
   ```

2. **Logs ansehen:**
   ```bash
   docker-compose logs -f
   ```

3. **Container stoppen:**
   ```bash
   docker-compose down
   ```

4. **Container neu starten:**
   ```bash
   docker-compose restart
   ```

### Lokal (ohne Docker)

1. **Virtuelle Umgebung erstellen:**
   ```bash
   python -m venv venv
   ```

2. **Virtuelle Umgebung aktivieren:**
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

3. **Dependencies installieren:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Anwendung starten:**
   ```bash
   python -m src.main
   ```

### Test-E-Mail sofort senden

Um die Applikation sofort auszuführen (ohne auf 7:00 Uhr zu warten):

**Mit Docker:**
```bash
docker-compose run --rm -e RUN_ONCE=true digest-app
```

**Lokal:**
```bash
RUN_ONCE=true python -m src.main
```

## Konfiguration

### Zeitzone anpassen

Die Zeitzone wird in der `.env` Datei konfiguriert:
```env
TIMEZONE=Europe/Berlin
```

Verfügbare Zeitzonen: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

### Schedule-Zeit ändern

Um die tägliche Ausführungszeit zu ändern:
```env
SCHEDULE_TIME=09:30
```

Format: `HH:MM` (24-Stunden-Format)

### Projekte/Spaces filtern

Um nur bestimmte Jira-Projekte oder Confluence-Spaces zu überwachen:
```env
JIRA_PROJECTS=PROJ1,PROJ2,PROJ3
CONFLUENCE_SPACES=SPACE1,SPACE2
```

Leer lassen für alle Projekte/Spaces.

## Troubleshooting

### E-Mail wird nicht versendet

1. **SMTP-Verbindung testen:**
   - Prüfe SMTP_HOST und SMTP_PORT
   - Bei Gmail: Nutze `smtp.gmail.com` und Port `587`
   - Bei Office365: Nutze `smtp.office365.com` und Port `587`

2. **Authentifizierung fehlgeschlagen:**
   - Gmail: Erstelle ein App-Passwort (https://myaccount.google.com/apppasswords)
   - Office365: Prüfe ob SMTP AUTH aktiviert ist
   - Prüfe Username/Passwort auf Tippfehler

3. **Logs prüfen:**
   ```bash
   # Docker
   docker-compose logs digest-app

   # Lokal
   cat logs/digest.log
   ```

### Jira/Confluence API-Fehler

1. **API Token prüfen:**
   - Token muss gültig sein
   - Username muss korrekt sein (meist die E-Mail)
   - URL muss korrekt sein (mit https://)

2. **Berechtigungen prüfen:**
   - Der User muss Lesezugriff auf Jira-Projekte haben
   - Der User muss Lesezugriff auf Confluence-Spaces haben

3. **Rate Limiting:**
   - Atlassian API erlaubt 10 Requests/Sekunde
   - Bei vielen Projekten kann dies relevant werden

### Container startet nicht

1. **Logs prüfen:**
   ```bash
   docker-compose logs
   ```

2. **.env Datei prüfen:**
   - Alle Pflichtfelder ausgefüllt?
   - Keine Leerzeichen um die Werte?
   - Keine Anführungszeichen nötig

3. **Container neu bauen:**
   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

## Projektstruktur

```
jira-confluence-digest/
├── src/
│   ├── __init__.py
│   ├── main.py                     # Haupteinstiegspunkt
│   ├── config.py                   # Konfigurationsverwaltung
│   ├── collectors/
│   │   ├── __init__.py
│   │   ├── jira_collector.py       # Jira API Client
│   │   └── confluence_collector.py # Confluence API Client
│   ├── reporters/
│   │   ├── __init__.py
│   │   ├── email_builder.py        # HTML E-Mail Generator
│   │   └── email_sender.py         # SMTP E-Mail Versand
│   └── templates/
│       └── digest_email.html       # HTML E-Mail Template
├── logs/                           # Log-Dateien
├── Dockerfile                      # Docker Container Definition
├── docker-compose.yml              # Docker Compose Konfiguration
├── requirements.txt                # Python Dependencies
├── .env.example                    # Beispiel-Konfiguration
├── .gitignore
└── README.md
```

## Erweiterungsmöglichkeiten

- **Mehrere Empfänger:** Liste von E-Mail-Adressen unterstützen
- **Personalisierung:** Nur eigene zugewiesene Tickets anzeigen
- **Slack/Teams Integration:** Alternative zu E-Mail
- **Web-Dashboard:** Zusätzliche Visualisierung
- **Wochenend-Pause:** Nur an Werktagen versenden
- **Custom-Filter:** Erweiterte JQL/CQL Queries

## Sicherheit

- **.env Datei nie committen** (ist in .gitignore)
- **API Tokens sicher aufbewahren**
- **SMTP Passwörter als App-Passwörter** nutzen
- **Logs regelmäßig prüfen** auf verdächtige Aktivitäten

## Support

Bei Fragen oder Problemen:
1. Logs prüfen (`logs/digest.log`)
2. Troubleshooting-Section in dieser README lesen
3. GitHub Issues erstellen (falls Repository vorhanden)

## Lizenz

Dieses Projekt ist für den privaten und kommerziellen Gebrauch frei verfügbar.
