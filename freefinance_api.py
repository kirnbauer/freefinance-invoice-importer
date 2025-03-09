# freefinance_api.py

import requests
import json
from config import API_URL, CUSTOMER_NUMBER_PREFIX

def find_or_create_customer(customer_number: str, customer_name: str, streetName: str, zipCode: str, city: str, country: str, customer_uid: str, access_token: str) -> str:
    """
    Prüft, ob ein Kunde mit Name = 'xxx-{customer_number}' existiert, sonst legt ihn neu an.
    """
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    url = f"{API_URL}/api/1.1/customers"
    customer_ff_id = f"{CUSTOMER_NUMBER_PREFIX}-{customer_number}"


    # Suche nach companyName
    print(f"🔍 Suche nach Kundennummer = {customer_number}")
    resp = requests.get(url, params={"customerNumber": customer_number}, headers=headers)
    resp.raise_for_status()
    result = resp.json()
    if result:
        for r in result:
            if r.get("customerNumber") == customer_ff_id:
                print(f"✅ Gefunden: {customer_name} | {customer_number} | {r['id']}")
                return r["id"]
        print(f"⚠️ Kunde {customer_number} nicht gefunden, wird erstellt...")

    # Neuanlage
    payload = {
        "customerNumber": customer_ff_id,
        "companyName": customer_name,
        "taxNumber": customer_uid,
        "streetName": streetName,
        "zipCode": zipCode,
        "city": city,
        "country": country
    }
    resp = requests.post(url, json=payload, headers=headers)
    resp.raise_for_status()
    try:
        resp.raise_for_status()
        print(f"📤 Kunde erstellt: {customer_name} mit ID {customer_ff_id}")
    except requests.exceptions.HTTPError as e:
        print(f"❌ Fehler beim Erstellen: {customer_name} mit ID {customer_ff_id} | Fehlercode: {resp.status_code} – {resp.text}")
    return resp.json()["id"]

def send_to_freefinance(invoice_data: dict, access_token: str):
    """
    Sendet eine vollständige Ausgangsrechnung an FreeFinance mit allen Positionen.
    Voraussetzung: invoice_data enthält customer_uid + lines mit accountId + taxClassEntry
    """
    url = f"{API_URL}/api/1.1/outgoing_invoices"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    # Kunde prüfen oder anlegen
    customer_id = find_or_create_customer(
        invoice_data["customer_number"],
        invoice_data["customer_name"],
        invoice_data["streetName"],
        invoice_data["zipCode"],
        invoice_data["city"],
        invoice_data["country"],
        invoice_data["customer_uid"],
        access_token
    )

    # Positionen vorbereiten
    ff_lines = []
    for line in invoice_data["lines"]:
        ff_lines.append({
            "account":    line["accountId"],
            "amount":     line["line_total"],
            "amountType": "N",
            "taxEntry":   line["taxClassEntry"],
            "description":line["description"]
        })

    # Rechnungspayload
    payload = {
        "invoiceDate":      invoice_data["invoice_date"],
        "invoiceReference": invoice_data["invoice_number"],
        "description":      "",
        "currency":         invoice_data["currency"],
        "currencyRate":     1,
        "customer":         customer_id,
        "lines":            ff_lines
    }

    # Senden
    print(f"🔗 Kunde {invoice_data['customer_number']} wird verwendet für Rechnung {invoice_data['invoice_number']}")
    resp = requests.post(url, json=payload, headers=headers)
    try:
        resp.raise_for_status()
        print(f"📤 Ausgangsrechnung gesendet: {invoice_data['invoice_number']} mit {len(ff_lines)} Positionen")
    except requests.exceptions.HTTPError as e:
        print(f"❌ Fehler beim Senden: {resp.status_code} – {resp.text}")
