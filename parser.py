# parser.py

#!/usr/bin/env python3
"""
Parst ZUGFeRD-/Factur-X-XML aus Bytes und liefert ein Dictionary für den
FreeFinance-Importer mit:
  - invoice_number
  - invoice_date (YYYY-MM-DD)
  - currency
  - lines: Liste von Einzelpositionen mit Beschreibung, Menge, Einzelpreis,
           Zeilenbetrag, Steuersatz, accountId und taxClassEntry
"""

import xmltodict
from datetime import datetime
from typing import Dict, Any, List

# Statische Regeln aus Deinem Blueprint
TAX_RULES = [
    {"country": "AT", "rate": 20, "accountId": "4000", "taxClassEntry": "020"},
    {"country": "EU", "rate": 0,  "accountId": "4111", "taxClassEntry": "---"},
]

def _first(node):
    if isinstance(node, list):
        return node[0]
    return node

def _parse_date_string(date_str: str) -> str:
    try:
        return datetime.strptime(date_str, "%Y%m%d").date().isoformat()
    except ValueError:
        return date_str

def _map_tax_rule(country: str, rate: float, category: str) -> Dict[str, str]:
    """
    Wählt aus TAX_RULES anhand von Käuferland, Steuersatz und CategoryCode
    den passenden accountId und taxClassEntry aus.
    """
    # Reverse charge 0% EU
    if rate == 0 and category == "E":
        rule = next(r for r in TAX_RULES if r["country"] == "EU" and r["rate"] == 0)
    # Standard-VAT Österreich
    elif country == "AT" and rate == 20 and category == "S":
        rule = next(r for r in TAX_RULES if r["country"] == "AT" and r["rate"] == 20)
    else:
        # Fallback: Erstes Matching nach rate
        rule = next(r for r in TAX_RULES if r["rate"] == rate)
    # Stelle sicher, dass taxClassEntry immer dreistellig mit führenden Nullen ist
    tc = rule["taxClassEntry"]
    rule["taxClassEntry"] = tc.zfill(3) if tc.isdigit() else tc
    return rule

def parse_zugferd_xml(xml_bytes: bytes) -> Dict[str, Any]:
    try:
        xml_str = xml_bytes.decode("utf-8")
        doc = xmltodict.parse(xml_str, process_namespaces=False)

        invoice = _first(doc.get("rsm:CrossIndustryInvoice", {}))
        header = invoice.get("rsm:ExchangedDocument") or invoice.get("rsm:ExchangedDocumentContext")
        header = _first(header) if header else {}
        invoice_number = header.get("ram:ID")

        issue = header.get("ram:IssueDateTime") or {}
        issue = _first(issue)
        dt_node = issue.get("udt:DateTimeString") or {}
        dt_node = _first(dt_node)
        raw_date = dt_node.get("#text", dt_node) if isinstance(dt_node, dict) else dt_node
        invoice_date = _parse_date_string(raw_date)

        trade = _first(invoice.get("rsm:SupplyChainTradeTransaction", {}))
        settlement = _first(trade.get("ram:ApplicableHeaderTradeSettlement", {}))
        currency = settlement.get("ram:InvoiceCurrencyCode") or "EUR"

        buyer = _first(trade.get("ram:ApplicableHeaderTradeAgreement", {})) \
            .get("ram:BuyerTradeParty", {})
        customer_number = buyer.get("ram:ID", "").strip()
        if not customer_number:
            raise ValueError("❌ Keine Kundennummer (<ram:BuyerTradeParty><ram:ID>) gefunden.")
        customer_name = buyer.get("ram:Name")
        tax_reg = _first(buyer.get("ram:SpecifiedTaxRegistration", {}))
        id_node = tax_reg.get("ram:ID")
        if isinstance(id_node, dict):
            uid = id_node.get("#text", "")
        else:
            uid = id_node or ""

        
        address = _first(buyer.get("ram:PostalTradeAddress", {}))
        streetName =  address.get("ram:LineOne")
        zipCode =  address.get("ram:PostcodeCode")
        city =  address.get("ram:CityName")
        country = address.get("ram:CountryID", "")

        items = trade.get("ram:IncludedSupplyChainTradeLineItem", [])
        if not isinstance(items, list):
            items = [items]

        lines: List[Dict[str, Any]] = []
        for item in items:
            item = _first(item)
            prod = item.get("ram:SpecifiedTradeProduct", {})
            description = prod.get("ram:Name") or ""

            settlement_line = _first(item.get("ram:SpecifiedLineTradeSettlement", {}))
            qty = settlement_line.get("ram:BilledQuantity")

            unit_price_node = settlement_line.get("ram:NetPriceProductTradePrice", {})
            if isinstance(unit_price_node, dict):
                price_amount = (unit_price_node.get("ram:ChargeAmount")
                                or unit_price_node.get("ram:NetPriceAmount"))
            else:
                price_amount = unit_price_node

            summation = _first(settlement_line.get("ram:SpecifiedTradeSettlementLineMonetarySummation", {}))
            line_total_node = summation.get("ram:LineTotalAmount")
            if isinstance(line_total_node, dict):
                line_total = float(line_total_node.get("#text"))
            else:
                line_total = float(line_total_node)

            trade_tax = _first(settlement_line.get("ram:ApplicableTradeTax", {}))
            rate_node = trade_tax.get("ram:RateApplicablePercent")
            category = trade_tax.get("ram:CategoryCode", "")
            tax_rate = float(rate_node.get("#text")) if isinstance(rate_node, dict) else float(rate_node)

            # Mapping für accountId & taxClassEntry mit führenden Nullen
            rule = _map_tax_rule(country, tax_rate, category)

            lines.append({
                "description":  description,
                "quantity":     float(qty) if qty else None,
                "unit_price":   float(price_amount) if price_amount else None,
                "line_total":   line_total,
                "tax_rate":     tax_rate,
                "accountId":    rule["accountId"],
                "taxClassEntry":rule["taxClassEntry"]
            })

        return {
            "invoice_number": invoice_number,
            "invoice_date":   invoice_date,
            "currency":       currency,
            "customer_number":customer_number,
            "customer_name":  customer_name,
            "streetName":     streetName,
            "zipCode":        zipCode,
            "city":           city,
            "country":        country,
            "customer_uid":   uid,
            "lines":          lines
        }

    except Exception as e:
        print(f"❌ Parsing-Fehler in parse_zugferd_xml: {e}")
        return {}
