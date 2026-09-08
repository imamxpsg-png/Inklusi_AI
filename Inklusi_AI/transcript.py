import numpy as np
import scipy.io.wavfile as wav
import tempfile
import os
from google.genai import types

def record_live_voice_segment(audio_data, fs=16000):
    """
    Mengonversi data buffer suara mentah dari mikrofon menjadi berkas .wav sementara 
    yang siap dikirim ke Gemini Cloud untuk transkripsi instan.
    """
    temp_dir = tempfile.gettempdir()
    temp_filename = os.path.join(temp_dir, "live_stream_mic.wav")
    
    # Simpan array numpy audio ke dalam format berkas WAV standard
    wav.write(temp_filename, fs, audio_data)
    return temp_filename

def transcribe_live_audio(client, file_path):
    """Mengirim berkas suara segmen langsung ke Gemini Multimodal Cloud"""
    if not os.path.exists(file_path) or not client:
        return ""
    try:
        with open(file_path, "rb") as f:
            audio_bytes = f.read()
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                types.Part.from_bytes(data=audio_bytes, mime_type='audio/wav'),
                "Salin suara bahasa Indonesia dari audio ini ke teks teks pendek bersih tanpa komentar."
            ]
        )
        return response.text.strip()
    except:
        return ""
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
