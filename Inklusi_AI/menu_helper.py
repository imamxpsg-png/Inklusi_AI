import streamlit as st

def render_dashboard_menu():
    st.markdown("### 📱 Pilih Modul Aksesibilitas Untuk Dibuka:")
    m_col1, m_col2 = st.columns(2)
    
    with m_col1:
        st.markdown("<div class='card-asisten'><h3 style='color: #15803D;'>🤖 Modul 1: Asisten Multimodal AI</h3><p style='color: #374151;'>Perintah suara, ketikan teks bebas, serta analisa cerdas impor dokumen atau gambar foto.</p></div>", unsafe_allow_html=True)
        if st.button("Masuk ke Asisten AI ➡️", use_container_width=True, key="nav_asisten"):
            st.session_state.current_page = "asisten_ai"; st.rerun()

        # Pembaruan Teks Info Modul 4 Baru di Dashboard Utama
        st.markdown("<div class='card-sos'><h3 style='color: #991B1B;'>🚀 Modul 4: Jalan Pintas Pintar (Navigasi)</h3><p style='color: #374151;'>Buka berbagai aplikasi dan tab website baru favorit Anda secara instan via ketikan teks atau suara.</p></div>", unsafe_allow_html=True)
        if st.button("Masuk ke Jalan Pintas Navigasi ➡️", use_container_width=True, key="nav_shortcut_sos"):
            st.session_state.current_page = "modul_sos"; st.rerun()

    with m_col2:
        st.markdown("<div class='card-obrolan'><h3 style='color: #042F2E;'>🧏 Modul 8 & 2: Obrolan & Terjemahan Live</h3><p style='color: #374151;'>Dengar transkrip bahasa asing jadi teks dan balas mengetik balik menjadi audio lantang.</p></div>", unsafe_allow_html=True)
        if st.button("Masuk ke Obrolan & Bicara ➡️", use_container_width=True, key="nav_obrolan"):
            st.session_state.current_page = "terjemahan_live"; st.rerun()

        st.markdown("<div class='card-dokumen'><h3 style='color: #6B21A8;'>🔊 Modul 2 & 3: Pembaca Berkas & Rangkuman</h3><p style='color: #374151;'>Ubah berkas PDF/Word ke suara narasi dan rangkum rekaman suara pelajaran panjang.</p></div>", unsafe_allow_html=True)
        if st.button("Masuk ke Dokumen & Materi ➡️", use_container_width=True, key="nav_dokumen"):
            st.session_state.current_page = "dokumen_materi"; st.rerun()
