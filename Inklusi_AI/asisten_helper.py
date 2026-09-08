import streamlit as st
from streamlit_mic_recorder import mic_recorder
from autopilot import execute_gemini_autopilot
import modules as mod
from PIL import Image

def render_asisten_ai(client, sched, mode="asisten"):
    # -----------------------------------------------------------------
    # BINGKAI KOTAK UTUH 1: ASISTEN PINTAR MULTIMODAL AI (TEMA GEMINI CARD)
    # -----------------------------------------------------------------
    if mode == "asisten":
        st.markdown("""
            <div class='card-asisten'>
                <h3 style='color: #15803D; margin: 0;'>🤖 Modul 1: Asisten Multimodal AI & Kendali Otonom</h3>
                <p style='color: #374151; font-size:12px; margin: 4px 0 20px 0;'>Interaksi pintar dengan gaya Google Gemini. Tekan tombol [+] untuk memunculkan menu lampiran berkas atau tombol mikrofon untuk merekam suara.</p>
        """, unsafe_allow_html=True)

        # --- FIX UTAMA: MENGISOLASI CSS AGAR TIDAK MERUSAK TOMBOL BERANDA ---
        # Menambahkan nama kelas pembungkus spesifik (.gemini-capsule-bar) sebelum div.stButton
        st.markdown("""
            <style>
            /* Wadah Kapsul Hitam Utama */
            .gemini-capsule-bar {
                background-color: #1e1f20 !important;
                border-radius: 28px !important;
                padding: 12px 20px !important;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
                margin-top: 15px;
                margin-bottom: 15px;
            }
            
            /* Menghilangkan gaya dasar text input agar menyatu transparan di dalam kapsul */
            .gemini-capsule-bar div[data-testid="stTextInput"] input {
                background-color: transparent !important;
                color: #e3e2e6 !important;
                border: none !important;
                font-size: 16px !important;
                padding-left: 0px !important;
            }
            .gemini-capsule-bar div[data-testid="stTextInput"] input:focus {
                box-shadow: none !important;
                outline: none !important;
            }
            
            /* FIX: Hanya tombol di dalam kelas .gemini-capsule-bar yang diubah menjadi bulat hitam */
            .gemini-capsule-bar div.stButton > button {
                background-color: #2f3032 !important;
                color: #e3e2e6 !important;
                border: none !important;
                font-size: 18px !important;
                font-weight: bold !important;
                width: 40px !important;
                height: 40px !important;
                border-radius: 50% !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                padding: 0 !important;
                margin: 0 !important;
            }
            .gemini-capsule-bar div.stButton > button:hover {
                background-color: #3d3e42 !important;
                color: #ffffff !important;
            }
            </style>
        """, unsafe_allow_html=True)

        # Inisialisasi status menu ekspansi
        if "uploader_active" not in st.session_state: st.session_state.uploader_active = False
        if "microphone_active" not in st.session_state: st.session_state.microphone_active = False

        # --- KONSTRUKSI BAR HORIZONTAL MANDIRI MENGGUNAKAN COLUMNS ASLI ---
        st.markdown("<div class='gemini-capsule-bar'>", unsafe_allow_html=True)
        
        # Membagi 3 kolom proporsional (Kiri untuk +, Tengah untuk Teks, Kanan untuk Mic)
        bar_col1, bar_col2, bar_col3 = st.columns(3)
        
        with bar_col1:
            if st.button("＋", key="gemini_real_plus"):
                st.session_state.uploader_active = not st.session_state.uploader_active
                st.session_state.microphone_active = False
                st.rerun()
                
        with bar_col2:
            ai_command_text = st.text_input("", placeholder="Tanyakan apa saja ke Gemini...", label_visibility="collapsed", key="gemini_real_text")
            
        with bar_col3:
            if st.button("🎙️", key="gemini_real_mic"):
                st.session_state.microphone_active = not st.session_state.microphone_active
                st.session_state.uploader_active = False
                st.rerun()
                
        st.markdown("</div>", unsafe_allow_html=True) # Penutup wadah gemini-capsule-bar
        # --- PANEL AREA EKSPANSI (MUNCUL AMAN SAAT TOMBOL DIATAS DIKETUK) ---
        uploaded_media = None
        audio_ai = None

        if st.session_state.uploader_active:
            st.markdown("<div style='background: rgba(255,255,255,0.7); padding: 16px; border-radius: 14px; border: 1px dashed #15803D; margin-bottom:15px;'>", unsafe_allow_html=True)
            st.markdown("<b style='font-size:12px; color:#15803D;'>🖼️ MENU TAMBAHKAN GAMBAR / BERKAS FILE:</b>", unsafe_allow_html=True)
            uploaded_media = st.file_uploader("Pilih dokumen berkas atau foto gambar Anda:", type=["png", "jpg", "jpeg", "txt"], key="file_uploader_gemini_pure", label_visibility="collapsed")
            st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state.microphone_active:
            st.markdown("<div style='background: rgba(255,255,255,0.7); padding: 16px; border-radius: 14px; border: 1px dashed #15803D; margin-bottom:15px;'>", unsafe_allow_html=True)
            st.markdown("<b style='font-size:12px; color:#15803D;'>🎙️ MENU INPUT SUARA MIKROFON:</b>", unsafe_allow_html=True)
            audio_ai = mic_recorder(start_prompt="🎙️ MULAI SUARAKAN PERINTAH SEKARANG", stop_prompt="🛑 SELESAI REKAM & PROSES DATA", just_once=False, use_container_width=True, key='mic_recorder_gemini_pure')
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True) # Penutup bingkai luar hijau asisten

        # --- LOGIKA PENANGANAN TRANSKRIPSI AUDIO STT ---
        if audio_ai and client:
            with st.spinner("Mencerna ucapan verbal Anda..."):
                try:
                    from google.genai import types
                    res = client.models.generate_content(model='gemini-3.6-flash', contents=[types.Part.from_bytes(data=audio_ai['bytes'], mime_type='audio/wav'), "Salin ucapan menjadi teks bersih."])
                    ai_command_text = res.text.strip()
                    st.session_state.microphone_active = False # Tutup kembali menu mic setelah selesai rekam
                except: st.error("Gagal memproses gelombang suara.")

        # --- SUBMIT DATA MULTIMODAL KE CLOUD GEMINI ---
        if ai_command_text or uploaded_media:
            st.write("---")
            if client:
                with st.spinner("Google Gemini sedang memproses tanggapan Anda..."):
                    try:
                        from google.genai import types
                        isi_konten = []
                        
                        if uploaded_media is not None:
                            if uploaded_media.name.endswith((".png", ".jpg", ".jpeg")):
                                image = Image.open(uploaded_media)
                                isi_konten.append(image)
                                st.image(image, caption="📸 Gambar Terlampir", width=250)
                            elif uploaded_media.name.endswith(".txt"):
                                isi_konten.append(uploaded_media.read().decode("utf-8"))
                        
                        prompt_final = ai_command_text if ai_command_text else "Analisa berkas lampiran yang saya berikan."
                        st.info(f"💡 Kueri Diproses: \"{prompt_final}\"")
                        
                        isi_konten.append(f"Request: '{prompt_final}'. Tanggapi dalam Bahasa Indonesia.")
                        response = client.models.generate_content(model='gemini-3.6-flash', contents=isi_konten)
                        st.success("🤖 Respons Google Gemini:")
                        st.write(response.text.strip())
                        st.audio(mod.text_to_speech(response.text.strip()[:300], "gemini_response.mp3"), autoplay=True)
                            
                    except Exception as e:
                        st.error(f"Gagal memproses cloud multimodal: {e}")

    # --- KOTAK 2: MODUL 4 — SAFETY SOS VIA EMAIL ---
    elif mode == "sos":
        from sos_helper import render_sos_menu
        render_sos_menu()
