import os
import logging
from docx import Document
import olefile
import zipfile

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="file_recovery.log",
)
logger = logging.getLogger(__name__)

def try_read_docx(docx_path):
    """Tenta di leggere un file .docx utilizzando python-docx."""
    try:
        logger.info(f"Tentativo di lettura del file {docx_path} come .docx...")
        doc = Document(docx_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        logger.error(f"Errore durante la lettura del file .docx: {e}")
        return None

def try_read_doc(doc_path):
    """Tenta di leggere un file .doc (legacy) utilizzando olefile."""
    try:
        logger.info(f"Tentativo di lettura del file {doc_path} come .doc...")
        ole = olefile.OleFileIO(doc_path)
        text = ""
        for stream in ole.listdir():
            if stream[0].startswith('WordDocument'):
                data = ole.openstream(stream).read()
                text += data.decode('utf-8', errors='ignore')
        return text
    except Exception as e:
        logger.error(f"Errore durante la lettura del file .doc: {e}")
        return None

def try_extract_from_corrupted_zip(docx_path):
    """Tenta di estrarre il contenuto di un file .docx corrotto come se fosse un archivio ZIP."""
    try:
        logger.info(f"Tentativo di estrazione del file {docx_path} come archivio ZIP...")
        with zipfile.ZipFile(docx_path, 'r') as zip_ref:
            # Cerca il file `word/document.xml` che contiene il testo
            with zip_ref.open('word/document.xml') as xml_file:
                from xml.etree import ElementTree as ET
                tree = ET.parse(xml_file)
                root = tree.getroot()
                namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
                text = ""
                for paragraph in root.findall('.//w:p', namespaces):
                    for text_elem in paragraph.findall('.//w:t', namespaces):
                        if text_elem.text:
                            text += text_elem.text + "\n"
                return text
    except Exception as e:
        logger.error(f"Errore durante l'estrazione del file come archivio ZIP: {e}")
        return None

def save_recovered_text(text, output_path):
    """Salva il testo recuperato in un file di output."""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        logger.info(f"Testo recuperato salvato in {output_path}")
    except Exception as e:
        logger.error(f"Errore durante il salvataggio del testo recuperato: {e}")

def recover_corrupted_word_file(file_path, output_path):
    """Tenta di recuperare il testo da un file Word corrotto."""
    logger.info(f"Avvio del processo di recupero per il file: {file_path}")

    # Tentativo 1: Leggi come .docx
    recovered_text = try_read_docx(file_path)

    # Tentativo 2: Leggi come .doc (se il file è in formato legacy)
    if not recovered_text and file_path.lower().endswith('.doc'):
        recovered_text = try_read_doc(file_path)

    # Tentativo 3: Estrai come archivio ZIP (per file .docx corrotti)
    if not recovered_text and file_path.lower().endswith('.docx'):
        recovered_text = try_extract_from_corrupted_zip(file_path)

    # Se il testo è stato recuperato, salvalo
    if recovered_text:
        save_recovered_text(recovered_text, output_path)
        logger.info("Recupero completato con successo.")
    else:
        logger.error("Impossibile recuperare il testo dal file corrotto.")

if __name__ == "__main__":
    # Percorso del file Word corrotto
    corrupted_file_path = "file_corrotto.docx"  # Sostituisci con il percorso del tuo file
    # Percorso di output per il testo recuperato
    output_file_path = "testo_recuperato.txt"

    # Avvia il processo di recupero
    recover_corrupted_word_file(corrupted_file_path, output_file_path)