# extractor.py

import subprocess
from pathlib import Path
import shutil

def extract_xml_bulk(pdf_folder: str, output_folder: str):
    pdf_folder = Path(pdf_folder)
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    for pdf_file in pdf_folder.glob("*.pdf"):
        target_dir = output_folder / pdf_file.stem
        target_dir.mkdir(parents=True, exist_ok=True)

        target_file = target_dir / f"{pdf_file.stem}.xml"

        try:
            subprocess.run([
                "pdfdetach",
                "-saveall",
                str(pdf_file),
                "-o",
                str(target_dir)
            ], check=True)

            source = target_dir / "xrechnung.xml"
            if source.exists():
                new_name = output_folder / f"{pdf_file.stem}.xml"
                shutil.move(source, new_name)
                print(f"✅ XML extrahiert: {pdf_file.name} → {new_name.name}")

                try:
                    target_dir.rmdir()
                    print(f"🧹 Ordner entfernt: {target_dir}")
                except OSError:
                    print(f"⚠️ Ordner nicht leer oder nicht löschbar: {target_dir}")
            else:
                print(f"⚠️ Keine eingebettete XML in {pdf_file.name}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Fehler bei {pdf_file.name}: {e}")
