import streamlit as st
from streamlit_mic_recorder import mic_recorder
import modules as mod

def render_live_chat(client):
    # -----------------------------------------------------------------
    # BINGKAI KOTAK UTUH 3: MODUL OBROLAN GABUNGAN (WARNA BACKGROUND HIJAU MINT)
    # -----------------------------------------------------------------
    with st.container(border=False):
        st.markdown("""
            <div class='card-obrolan'>
                <h3 style='color: #0F766E; margin:0;'>🧏 Modul Obrolan & Bicara Mandiri (Terjemahan & TTS)</h3>
                <p style='color: #374151; font-size:12px; margin: 4px 0 14px 0;'>Dengarkan ucapan asing sekitar menjadi teks Bahasa Indonesia, sekaligus ketik kalimat balasan Anda untuk diterjemahkan dan disuarakan ke berbagai bahasa target.</p>
        """, unsafe_allow_html=True)
        
        pilihan_bahasa = st.selectbox(
            "Pilih Bahasa Target Komunikasi:", 
            ["Bahasa Indonesia", "English (Inggris)", "日本語 (Jepang)", "العربية (Arab)", "한국어 (Korea)"], 
            key="lang_shared_obrolan"
        )
        st.write("---")
        
        # 1. Perekam Mikrofon Dengar Suara Orang Sekitar (Suara Asing -> Teks Indonesia)
        st.markdown("<b style='font-size:13px; color:#0F766E;'>1. Dengarkan Orang Lain (Suara Asing ➡️ Teks Indonesia):</b>", unsafe_allow_html=True)
        audio_chat = mic_recorder(
            start_prompt="🎙️ REKAM SUARA SEKITAR / TURIS ASING", 
            stop_prompt="🛑 STOP & TRANSLATE", 
            just_once=False, 
            use_container_width=True, 
            key='mic_chat_gab_last'
        )
        
        if audio_chat and client:
            with st.spinner("AI sedang mendeteksi bahasa dan menerjemahkan ucapan..."):
                try:
                    from google.genai import types
                    # FIX PERBAIKAN UTAMA: Prompt diubah total agar mendeteksi audio secara global (Anti-Salah Dengar)
                    response_chat = client.models.generate_content(
                        model='gemini-3.6-flash',
                        contents=[
                            types.Part.from_bytes(data=audio_chat['bytes'], mime_type='audio/wav'), 
                            "Dengarkan audio ini dengan seksama. Deteksi bahasa aslinya terlebih dahulu secara otomatis (bisa berupa Jepang, Inggris, Arab, Korea, dll). Setelah tahu bahasa aslinya, terjemahkan maknanya secara akurat dan bersih ke dalam Bahasa Indonesia. Tampilkan hanya teks hasil akhir terjemahannya saja tanpa penjelasan apa pun."
                        ]
                    )
                    txt = response_chat.text.strip()
                    if txt:
                        st.info(f"📢 Hasil Dengar (Terjemahan ke Indonesia): \"{txt}\"")
                        st.audio(mod.text_to_speech(txt, "dengar.mp3"), autoplay=True)
                except Exception as e: 
                    st.error(f"Gagal memproses audio: {e}")
        st.write("---")
        
        # 2. Papan Ketik Input Manual Teks-ke-Suara Mengobrol (Bisa Translate Otomatis)
        st.markdown("<b style='font-size:13px; color:#0F766E;'>2. Balas Mengobrol Mandiri (Ketik Teks Indonesia ➡️ Auto Translate ➡️ Suara Target):</b>", unsafe_allow_html=True)
        teks_obrolan = st.text_input(
            "Ketik kalimat balasan Anda (Ketik dalam Bahasa Indonesia):", 
            placeholder="Contoh: Terima kasih, senang bisa membantu Anda.", 
            key="txt_obrolan_gab_last"
        )
        click_bicara = st.button("🔊 TERJEMAHKAN & SUARAKAN BALASAN VIA SPEAKER", use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True) # Penutup bingkai hijau obrolan yang menyatu sempurna
        
        if teks_obrolan and click_bicara:
            lang_map = {
                "Bahasa Indonesia": "id", 
                "English (Inggris)": "en", 
                "日本語 (Jepang)": "ja", 
                "العربية (Arab)": "ar", 
                "한국어 (Korea)": "ko"
            }
            code_lang = lang_map.get(pilihan_bahasa, "id")
            
            teks_final_bacaan = teks_obrolan
            if pilihan_bahasa != "Bahasa Indonesia" and client:
                with st.spinner(f"Menerjemahkan teks ketikan Anda ke {pilihan_bahasa}..."):
                    try:
                        response_text_trans = client.models.generate_content(
                            model='gemini-3.6-flash',
                            contents=[f"Terjemahkan kalimat berikut secara akurat ke dalam {pilihan_bahasa}: '{teks_obrolan}'. Tampilkan hanya teks hasil akhir terjemahannya saja tanpa tanda kutip atau penjelasan."]
                        )
                        teks_final_bacaan = response_text_trans.text.strip()
                        
                        st.markdown(f"""
                            <div style='background: rgba(2, 132, 199, 0.1); padding: 10px 14px; border-radius: 8px; border-left: 4px solid #0284C7; margin-bottom: 10px;'>
                                <span style='font-size:11px; font-weight:bold; color:#0369A1;'>TEKS BALASAN TERTERJEMAH:</span>
                                <p style='font-size:15px; color:#0369A1; font-weight:bold; margin:2px 0 0 0;'>{teks_final_bacaan}</p>
                            </div>
                        """, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Gagal menerjemahkan teks: {e}")
            
            with st.spinner("Mengonversi teks menjadi suara..."):
                try:
                    audio_res = mod.text_to_speech(teks_final_bacaan, f"balas_{code_lang}.mp3")
                    st.audio(audio_res, autoplay=True)
                    st.success(f"✓ Sukses menyiarkan balasan suara dalam versi {pilihan_bahasa}!")
                except Exception as e:
                    st.error(f"Gagal memputar suara: {e}")
