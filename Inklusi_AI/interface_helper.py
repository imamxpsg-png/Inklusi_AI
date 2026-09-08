import streamlit as st
from streamlit_mic_recorder import mic_recorder
import modules as mod
import datetime
import docx
import pypdf

def render_top_dashboard_widgets():
    st.markdown("""
        <div style='background: #FFFFFF; padding: 10px; border-radius: 12px; margin-bottom: 10px; border: 1px solid #E2E8F0;'>
            <b style='font-size: 11px; color: #475569;'>📊 HERMES LIVE WIDGET PANEL (STATUS UTAMA GAWAI)</b>
        </div>
    """, unsafe_allow_html=True)
    
    st.metric(label="🔋 Battery Health (Kondisi Fisik)", value="98% Prima", delta="Pengisian Normal")
    waktu_utc = datetime.datetime.utcnow()
    waktu_wib = waktu_utc + datetime.timedelta(hours=7)
    waktu_sekarang = waktu_wib.strftime("%H:%M WIB")
    st.metric(label="⏰ Waktu Jam Digital Sistem", value=waktu_sekarang, delta="Sinkronisasi Server WIB")
    st.metric(label="🌤️ Prediksi Cuaca Salatiga", value="26°C Berawan", delta="Kelembapan 78% Aman")

def render_sidebar_status(active_keys, client, mode="dokumen"):
    if mode == "dokumen":
        st.markdown("""
            <div class='card-dokumen'>
                <h3 style='color: #6B21A8; margin: 0;'>📚 Modul: Pembaca Dokumen & Rangkuman Materi</h3>
                <p style='color: #475569; font-size:12px; margin: 4px 0 14px 0;'>Unggah file berkas materi Anda (PDF, TXT, WORD) untuk diubah langsung menjadi narasi suara verbal otomatis.</p>
        """, unsafe_allow_html=True)
        
        bahasa_bacaan = st.selectbox("Pilih Bahasa Output Dokumen Belajar:", ["Bahasa Indonesia", "English (Inggris)"], key="lang_doc_sidebar")
        uploaded_file = st.file_uploader("Pilih berkas dokumen Anda:", type=["pdf", "txt", "docx"], key="doc_sidebar_uploader")
        
        if uploaded_file is not None:
            extracted_text = ""
            try:
                if uploaded_file.name.endswith(".txt"): extracted_text = uploaded_file.read().decode("utf-8")
                elif uploaded_file.name.endswith(".docx"): extracted_text = "\n".join([p.text for p in docx.Document(uploaded_file).paragraphs])
                elif uploaded_file.name.endswith(".pdf"): extracted_text = "\n".join([page.extract_text() for page in pypdf.PdfReader(uploaded_file).pages if page.extract_text()])
            except Exception as e: st.error(f"Gagal mengekstrak dokumen: {e}")
            
            if extracted_text:
                st.text_area("Pratinjau Isi Dokumen Terbaca:", extracted_text[:400] + "...", height=100)
                if st.button("🔊 MULAI BACAKAN DOKUMEN MATERI INI", use_container_width=True):
                    lang_map = {"Bahasa Indonesia": "id", "English (Inggris)": "en"}
                    st.audio(mod.text_to_speech(extracted_text[:400], f"doc_{lang_map.get(bahasa_bacaan)}.mp3"), autoplay=True)
                    st.success(f"✓ Sukses menyiarkan narasi suara berkas!")
        
        st.write("---")
        st.markdown("<b style='font-size:13px;'>🎙️ Rekam Jalannya Materi Kuliah / Sekolah:</b>", unsafe_allow_html=True)
        audio_materi = mic_recorder(start_prompt="🎙️ REKAM JALANNYA MATERI PANJANG", stop_prompt="🛑 SELESAI & BUAT RANGKUMAN", just_once=False, use_container_width=True, key='mic_materi_sidebar')
        st.markdown("</div>", unsafe_allow_html=True)
        
        # PERANGKUM SUARA MATERI DENGAN MODEL STABIL GEMINI-2.0-FLASH
        if audio_materi and client:
            st.write("---")
            with st.spinner("Gemini AI merangkum materi kuliah panjang..."):
                try:
                    from google.genai import types
                    res = client.models.generate_content(
                        model='gemini-2.0-flash', 
                        contents=[types.Part.from_bytes(data=audio_materi['bytes'], mime_type='audio/wav'), "Buat rangkuman terstruktur bahasa indonesia dengan penanda emosi emoji di setiap poin dari audio kuliah berikut."]
                    )
                    if res.text:
                        st.markdown("##### 📋 Hasil Rangkuman Pintar:")
                        st.write(res.text.strip())
                except Exception as e: st.error(f"Gagal menyusun data: {e}")
