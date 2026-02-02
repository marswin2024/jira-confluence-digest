# Google Cloud Run Deployment Guide

Schritt-für-Schritt Anleitung zum Deployment der Jira & Confluence Daily Digest Applikation auf Google Cloud Run.

## Voraussetzungen

1. **Google Cloud Account** erstellen (falls noch nicht vorhanden)
   - Gehe zu https://console.cloud.google.com/
   - Registriere dich (300$ kostenloses Guthaben für neue Nutzer)

2. **Google Cloud SDK installieren**
   - Download: https://cloud.google.com/sdk/docs/install
   - Nach Installation: Terminal/CMD neu starten

## Schritt 1: Google Cloud Projekt erstellen

1. Gehe zu https://console.cloud.google.com/
2. Klicke auf "Projekt auswählen" → "Neues Projekt"
3. Projektname: `jira-confluence-digest`
4. Notiere die Projekt-ID (z.B. `jira-confluence-digest-123456`)

## Schritt 2: APIs aktivieren

Gehe zu https://console.cloud.google.com/apis/library und aktiviere:
- **Cloud Run API**
- **Cloud Build API**
- **Cloud Scheduler API**
- **Container Registry API**

Oder über CLI:
```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

## Schritt 3: Google Cloud SDK konfigurieren

Öffne Terminal/CMD und führe aus:

```bash
# Login in Google Cloud
gcloud auth login

# Projekt setzen (ersetze mit deiner Projekt-ID)
gcloud config set project jira-confluence-digest-123456

# Region setzen
gcloud config set run/region europe-west1
```

## Schritt 4: Docker Image bauen und deployen

Im Projektverzeichnis `jira-confluence-digest`:

```bash
# Projekt-ID setzen (ersetze mit deiner!)
export PROJECT_ID=jira-confluence-digest-123456

# Docker Image bauen und zu Google Container Registry pushen
gcloud builds submit --tag gcr.io/${PROJECT_ID}/jira-confluence-digest

# Setze die Umgebungsvariablen (ersetze mit deinen echten Werten!)
export JIRA_URL="https://your-company.atlassian.net"
export JIRA_USERNAME="your-email@company.com"
export JIRA_API_TOKEN="your-jira-api-token"
export CONFLUENCE_URL="https://your-company.atlassian.net/wiki"
export CONFLUENCE_USERNAME="your-email@company.com"
export CONFLUENCE_API_TOKEN="your-confluence-api-token"
export SMTP_HOST="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USERNAME="your-email@gmail.com"
export SMTP_PASSWORD="your-app-password"
export RECIPIENT_EMAIL="recipient@company.com"

# Zu Cloud Run deployen
gcloud run deploy jira-confluence-digest \
  --image gcr.io/${PROJECT_ID}/jira-confluence-digest \
  --platform managed \
  --region europe-west1 \
  --no-allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --timeout 900 \
  --set-env-vars "JIRA_URL=${JIRA_URL},JIRA_USERNAME=${JIRA_USERNAME},JIRA_API_TOKEN=${JIRA_API_TOKEN},CONFLUENCE_URL=${CONFLUENCE_URL},CONFLUENCE_USERNAME=${CONFLUENCE_USERNAME},CONFLUENCE_API_TOKEN=${CONFLUENCE_API_TOKEN},SMTP_HOST=${SMTP_HOST},SMTP_PORT=${SMTP_PORT},SMTP_USERNAME=${SMTP_USERNAME},SMTP_PASSWORD=${SMTP_PASSWORD},RECIPIENT_EMAIL=${RECIPIENT_EMAIL},TIMEZONE=Europe/Berlin"
```

**Hinweis:** Das Deployment dauert 2-5 Minuten.

## Schritt 5: Service testen

Nach erfolgreichem Deployment erhältst du eine Service-URL wie:
`https://jira-confluence-digest-xxxxx-ew.a.run.app`

Test-E-Mail sofort senden:

```bash
# Service URL aus Deployment kopieren
SERVICE_URL="https://jira-confluence-digest-xxxxx-ew.a.run.app"

# Test-Request senden
curl -X POST ${SERVICE_URL}/run-digest \
  -H "Authorization: Bearer $(gcloud auth print-identity-token)"
```

Du solltest jetzt eine E-Mail erhalten!

## Schritt 6: Cloud Scheduler einrichten (täglich 7:00 Uhr)

### Option A: Über Google Cloud Console (einfacher)

1. Gehe zu https://console.cloud.google.com/cloudscheduler
2. Klicke "Job erstellen"
3. **Name:** `daily-digest-trigger`
4. **Region:** `europe-west1`
5. **Beschreibung:** `Triggers Jira & Confluence digest daily at 7 AM`
6. **Häufigkeit:** `0 7 * * *` (Cron-Format für täglich 7:00 Uhr)
7. **Zeitzone:** `Europe/Berlin`
8. **Zieltyp:** `HTTP`
9. **URL:** Deine Service-URL + `/run-digest` (z.B. `https://jira-confluence-digest-xxxxx-ew.a.run.app/run-digest`)
10. **HTTP-Methode:** `POST`
11. **Auth-Header:** `Add OIDC token`
12. **Dienstkonto:** Wähle das Standard-Compute-Dienstkonto oder erstelle ein neues
13. **Zielgruppe:** Deine Service-URL (ohne `/run-digest`)
14. Klicke "Erstellen"

### Option B: Über CLI

```bash
# Service URL ermitteln
SERVICE_URL=$(gcloud run services describe jira-confluence-digest \
  --platform managed \
  --region europe-west1 \
  --format 'value(status.url)')

# Cloud Scheduler Job erstellen
gcloud scheduler jobs create http daily-digest-trigger \
  --location=europe-west1 \
  --schedule="0 7 * * *" \
  --time-zone="Europe/Berlin" \
  --uri="${SERVICE_URL}/run-digest" \
  --http-method=POST \
  --oidc-service-account-email=$(gcloud iam service-accounts list --format='value(email)' --filter='displayName:Compute Engine default service account')
```

## Schritt 7: Scheduler testen

Test-Ausführung sofort:

```bash
gcloud scheduler jobs run daily-digest-trigger --location=europe-west1
```

Prüfe ob die E-Mail angekommen ist!

## Schritt 8: Monitoring

**Logs ansehen:**
```bash
gcloud run services logs read jira-confluence-digest \
  --platform managed \
  --region europe-west1 \
  --limit=50
```

**Oder in der Console:**
https://console.cloud.google.com/run → Wähle deinen Service → "Logs"

## Kosten

Mit der aktuellen Konfiguration:
- **Cloud Run:** Kostenlos (Free Tier: 2 Mio. Requests/Monat)
- **Cloud Scheduler:** $0.10/Monat pro Job
- **Cloud Build:** Kostenlos (Free Tier: 120 Build-Minuten/Tag)
- **Container Registry:** Kostenlos (< 500 MB)

**Geschätzte Gesamtkosten: ~$0.10/Monat**

## Troubleshooting

### Deployment schlägt fehl
```bash
# Prüfe ob APIs aktiviert sind
gcloud services list --enabled

# Prüfe Billing-Account
gcloud billing accounts list
```

### E-Mail wird nicht versendet
```bash
# Logs prüfen
gcloud run services logs read jira-confluence-digest \
  --platform managed \
  --region europe-west1 \
  --limit=100 | grep -i error
```

### Scheduler funktioniert nicht
```bash
# Job-Status prüfen
gcloud scheduler jobs describe daily-digest-trigger --location=europe-west1

# Manuell triggern
gcloud scheduler jobs run daily-digest-trigger --location=europe-west1
```

### SMTP-Fehler bei Gmail
- Stelle sicher dass du ein App-Passwort verwendest
- Prüfe ob "Weniger sichere Apps" aktiviert ist (bei alten Accounts)

## Updates deployen

Wenn du die Applikation änderst:

```bash
# Neues Image bauen und deployen
gcloud builds submit --tag gcr.io/${PROJECT_ID}/jira-confluence-digest
gcloud run deploy jira-confluence-digest \
  --image gcr.io/${PROJECT_ID}/jira-confluence-digest \
  --platform managed \
  --region europe-west1
```

## Service löschen (falls nicht mehr benötigt)

```bash
# Cloud Run Service löschen
gcloud run services delete jira-confluence-digest \
  --platform managed \
  --region europe-west1

# Scheduler Job löschen
gcloud scheduler jobs delete daily-digest-trigger --location=europe-west1

# Container Images löschen
gcloud container images delete gcr.io/${PROJECT_ID}/jira-confluence-digest
```

## Fertig!

Die Applikation läuft jetzt in der Cloud und sendet dir jeden Morgen um 7:00 Uhr die Daily Digest E-Mail - auch wenn dein Computer ausgeschaltet ist! 🎉
