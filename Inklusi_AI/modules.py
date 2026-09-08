from gtts import gTTS
import requests
from bs4 import BeautifulSoup
import psutil
from pypdf import PdfReader
import docx

def text_to_speech(text, filename="temp_voice.mp3"):
    """Mengonversi respons tulisan teks menjadi suara vokal (gTTS)"""
    tts = gTTS(text=text, lang='id')
    tts.save(filename)
    return filename

def check_vps_status():
    """Membaca persentase penggunaan RAM Cloud VPS"""
    ram_use = psutil.virtual_memory().percent
    return f"Status sistem aman. Penggunaan RAM Cloud VPS saat ini berada di angka {ram_use} persen."

def read_pdf_file(file_bytes):
    """Mengekstrak teks dari berkas PDF secara gratis"""
    try:
        reader = PdfReader(file_bytes)
        extracted_text = ""
        # Ambil teks dari halaman pertama/kedua agar tidak terlalu panjang saat demo suara
        for page in reader.pages[:2]:
            extracted_text += page.extract_text() + "\n"
        return extracted_text.strip()
    except Exception as e:
        return f"Gagal membaca PDF: {str(e)}"

def read_word_file(file_bytes):
    """Mengekstrak teks dari berkas Word (.docx) secara gratis"""
    try:
        doc = docx.Document(file_bytes)
        extracted_text = []
        for para in doc.paragraphs[:10]: # Ambil 10 paragraf awal
            extracted_text.append(para.text)
        return "\n".join(extracted_text).strip()
    except Exception as e:
        return f"Gagal membaca Word: {str(e)}"
