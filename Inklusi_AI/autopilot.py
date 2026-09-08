import webbrowser
import os

def execute_gemini_autopilot(client, user_speech_text):
    """
    Membaca ucapan bebas user secara otonom menggunakan Gemini API terupdate (3.6-flash).
    Sistem bisa membuka website apa saja dan menjawab pertanyaan apa saja secara bebas.
    """
    if not client:
        return "⚠️ Cloud AI Gemini belum aktif. Hubungkan API Key Anda di terminal."
    
    text_lower = user_speech_text.lower()
    
    # =====================================================================
    # 1. AKSI BEBAS: MEMBUKA WEBSITE APA SAJA TERGANTUNG UCAPAN USER
    # =====================================================================
    if "buka" in text_lower or "open" in text_lower or "situs" in text_lower:
        prompt_web = (
            f"Analisis ucapan user ini: '{user_speech_text}'. "
            "User ingin membuka sebuah situs website. Tebak nama domain atau URL lengkap dari website tersebut "
            "(Contoh: jika user bilang 'buka detik', berikan 'https://detik.com'). "
            "Berikan respon berupa LINK URL UTUHNYA SAJA tanpa tambahan teks atau komentar apa pun."
        )
        
        try:
            # Menggunakan model terbaru gemini-3.6-flash agar tidak 404
            response_web = client.models.generate_content(model='gemini-3.6-flash', contents=prompt_web)
            target_url = response_web.text.strip()
            
            if target_url.startswith("http://") or target_url.startswith("https://"):
                webbrowser.open(target_url)
                return f"🤖 [AUTOPILOT SUCCESS] Perintah buka situs terdeteksi via Gemini. Link berhasil dibuka: {target_url}"
        except Exception as e:
            pass

    # =====================================================================
    # 2. AKSI BEBAS: PENJADWALAN ALARM (MENGINGATKAN)
    # =====================================================================
    if "mengingatkan" in text_lower or "ingatkan" in text_lower or "alarm" in text_lower:
        return "🤖 [ROUTE INTENT] Mendeteksi kata pemicu 'Mengingatkan'. Sistem mengaktifkan alarm otonom 10 detik."

    # =====================================================================
    # 3. AKSI BEBAS: MENJAWAB PERTANYAAN APA SAJA SECARA LIVE (TANYA JAWAB)
    # =====================================================================
    try:
        prompt_qa = f"Berikan jawaban singkat, padat, dan jelas dalam bahasa Indonesia maksimal 35 kata untuk instruksi/pertanyaan disabilitas ini: {user_speech_text}"
        # Menggunakan model terbaru gemini-3.6-flash agar tidak 404
        response_qa = client.models.generate_content(model='gemini-3.6-flash', contents=prompt_qa)
        return f"🤖 [AI GENERATE SUCCESS]: {response_qa.text.strip()}"
    except Exception as e:
        return f"❌ Terjadi kesalahan pada server AI Cloud Gemini: {str(e)}"
