# main.py

from config import PDF_INPUT_FOLDER, XML_OUTPUT_FOLDER, DONE_FOLDER, ERROR_FOLDER
from extractor import extract_xml_bulk
from parser import parse_zugferd_xml
from auth_token import get_access_token
from freefinance_api import send_to_freefinance
from pathlib import Path
from shutil import move

DONE_FOLDER.mkdir(parents=True, exist_ok=True)
ERROR_FOLDER.mkdir(parents=True, exist_ok=True)

def main():
    print("📥 Starte XML-Extraktion aus PDF-Rechnungen ...")
    extract_xml_bulk(PDF_INPUT_FOLDER, XML_OUTPUT_FOLDER)

    print("🔐 Authentifiziere über Pairing-Flow ...")
    access_token = get_access_token()

    print("📄 Verarbeite extrahierte XML-Dateien ...")
    for xml_file in Path(XML_OUTPUT_FOLDER).rglob("*.xml"):
        try:
            with open(xml_file, "rb") as f:
                xml_content = f.read()
                
            parsed = parse_zugferd_xml(xml_content)
            if parsed and parsed.get("lines"):
                send_to_freefinance(parsed, access_token)

                target = DONE_FOLDER / xml_file.name
                move(xml_file, target)

                pdf_name = xml_file.stem + ".pdf"
                pdf_path = PDF_INPUT_FOLDER / pdf_name
                if pdf_path.exists():
                    move(pdf_path, DONE_FOLDER / pdf_name)
            else:
                print(f"⚠️ Keine gültige Rechnung in {xml_file.name}")
                move(xml_file, ERROR_FOLDER / xml_file.name)

        except Exception as e:
            print(f"❌ Fehler bei {xml_file.name}: {e}")
            try:
                move(xml_file, ERROR_FOLDER / xml_file.name)
            except Exception as move_err:
                print(f"⚠️ Fehler beim Verschieben in error/: {move_err}")

if __name__ == "__main__":
    main()
