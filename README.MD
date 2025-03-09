# 🧾 FreeFinance ZUGFeRD / XRechnung Importer

Ein CLI-Tool zum automatisierten Import von Ausgangsrechnungen im ZUGFeRD-Format in die FreeFinance-API (AT).  
Es extrahiert eingebettete XML-Dateien aus PDF-Rechnungen, parst die Inhalte und importiert jede Position korrekt als Ausgangsbeleg.  
Kunden werden automatisch erkannt oder neu angelegt.

---

## ✅ Voraussetzungen

- Python 3.8+
- [`pdfdetach`](https://poppler.freedesktop.org/) (aus dem `poppler-utils`-Paket)

### 🔧 Installation (Linux/Mac)

```bash
sudo apt install poppler-utils
pip install -r requirements.txt
```

### 📦 Installation (Windows)

1. [Poppler für Windows](https://github.com/oschwartz10612/poppler-windows/releases/) herunterladen
2. Entpacken und den `bin/`-Ordner zur `PATH`-Umgebungsvariable hinzufügen
3. In der Konsole prüfen: `pdfdetach --version`
4. Python-Abhängigkeiten installieren:

```bash
pip install -r requirements.txt
```

---

## ⚙️ Konfiguration

1. `config.py.example` nach `config.py` kopieren
2. Zugangsdaten und Pfade eintragen:

```python
from pathlib import Path

USERNAME = "dein-benutzername"
PAIRING_CODE = "dein-pairing-code"
CLIENT_ID = "deine-client-id"
API_URL = "https://app.freefinance.at"

PDF_INPUT_FOLDER = Path("./invoices")
XML_OUTPUT_FOLDER = Path("./output_xml")
DONE_FOLDER = PDF_INPUT_FOLDER / "done"
ERROR_FOLDER = PDF_INPUT_FOLDER / "error"

CUSTOMER_NUMBER_PREFIX = "ext"
```

---

## 📂 Ordnerstruktur

- `invoices/` → Hier legst du deine ZUGFeRD-PDFs ab
- `output_xml/` → Extrahierte XML-Dateien
- `invoices/done/` → Erfolgreich verarbeitete PDFs & XMLs
- `invoices/error/` → Ungültige oder fehlerhafte Dateien

Die Ordner werden bei Bedarf automatisch erstellt.

---

## ▶️ Nutzung

```bash
python3 main.py
```

Ablauf:
1. Alle PDF-Dateien in `invoices/` werden durchsucht
2. Eingebettete XML (`xrechnung.xml`) wird extrahiert
3. Rechnungsdaten werden geparst und an FreeFinance gesendet
4. Nach erfolgreichem Import wird die Datei verschoben (PDF + XML)

---

## 💡 Features

- ✅ Automatische Extraktion von ZUGFeRD-/XRechnung-XMLs
- ✅ Vollständige Verarbeitung von Rechnungspositionen
- ✅ Intelligente Steuer- und Konto-Zuordnung (z. B. 20 %, 0 % Reverse Charge)
- ✅ Kundenprüfung & -anlage anhand von `CUSTOMER_NUMBER_PREFIX` + Kundennummer
- ✅ Schutz vor doppeltem Import
- ✅ Logging für XML, Fehler und FreeFinance-Statusmeldungen

---

## 🛠 Beispiel: Rechnung mit 2 Positionen

- **PDF:** `invoices/RE1234.pdf`
- **XML wird extrahiert als:** `output_xml/RE1234.xml`
- **FreeFinance bekommt:** 1 Ausgangsrechnung mit 2 Positionen
- **Nach dem Import:** PDF & XML → `invoices/done/`

---

## 🧪 Testumgebung & API-Zugang

Um das System mit FreeFinance zu verbinden, benötigst du einen **API-Key** sowie ggf. Zugang zum Testsystem.  
Diesen bekommst du **nicht automatisch**, sondern **nach Kontaktaufnahme mit FreeFinance**.

➡️ Beantrage deinen API-Zugang über das Kontaktformular auf  
🔗 [https://developer.freefinance.at/](https://developer.freefinance.at/)

Nach der Anfrage erhältst du alle weiteren Informationen sowie ggf. Zugang zum Testsystem.

📚 **Offizielle API-Dokumentation:**  
[https://developer.freefinance.at/apidoc-1_1.html](https://developer.freefinance.at/apidoc-1_1.html)

---

## ⚠️ Haftungsausschluss & rechtlicher Hinweis

Dieses Tool wurde unabhängig entwickelt und steht **in keiner Verbindung zur FreeFinance / Manubu GmbH**.  
Es nutzt öffentlich dokumentierte Schnittstellen von FreeFinance **zum automatisierten Import von Ausgangsrechnungen in das FreeFinance-System**.

🛑 **Die Nutzung dieses Tools erfolgt auf eigene Verantwortung.** 🛑


- ⚠️ Für die Nutzung dieses Tools wird **keinerlei Haftung übernommen** – insbesondere **nicht für Datenverluste, Fehlbuchungen, rechtliche Folgen oder sonstige Schäden**, die direkt oder indirekt aus dem Einsatz entstehen.
- 🔒 Vor dem Einsatz in einer **produktiven Umgebung** ist eine **ausführliche Prüfung und Testphase** unbedingt erforderlich.
- 📑 Die Verantwortung für die Richtigkeit der importierten Daten und die Einhaltung gesetzlicher Vorgaben liegt vollständig beim Anwender.

**Verwende dieses Tool nur, wenn dir die Funktionsweise und möglichen Folgen vollständig klar sind.**

